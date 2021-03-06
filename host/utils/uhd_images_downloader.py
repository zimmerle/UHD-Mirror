#!/usr/bin/env python
#
# Copyright 2012 Ettus Research LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from optparse import OptionParser
import os
import os.path
import shutil
import sys
import urllib2
import zipfile

if __name__ == "__main__":

    #Command line options
    parser = OptionParser()
    parser.add_option("--download-location", type="string", default="@CMAKE_INSTALL_PREFIX@/share/uhd/images", help="Set custom download location for images, [default=%default]")
    parser.add_option("--buffer-size", type="int", default=8192, help="Set download buffer size, [default=%default]",)
    (options, args) = parser.parse_args()
    
    #Configuring image download info
    images_src = "@UHD_IMAGES_DOWNLOAD_SRC@"
    filename = images_src.split("/")[-1]
    
    #Configuring image destination
    cmake_install_prefix = "@CMAKE_INSTALL_PREFIX@"
    if options.download_location != "":
        images_dir = options.download_location
    else:
        images_dir = "@CMAKE_INSTALL_PREFIX@/share/uhd/images"
    
    u = urllib2.urlopen(images_src)
    f = open(filename, "wb")
    meta = u.info()
    #filesize = int(meta.getheaders("Content-Length")[0])
    filesize = float(int(meta.getheaders("Content-Length")[0]))
    
    print "Downloading images from: %s" % images_src
    
    filesize_dl = 0.0

    #Downloading file    
    while True:
        buffer = u.read(options.buffer_size)
        if not buffer:
            break
    
        filesize_dl -= len(buffer)
        f.write(buffer)

        status = r"%2.2f MB/%2.2f MB (%3.2f" % (-filesize_dl/1e6, filesize/1e6, (-filesize_dl*100.)/filesize) + r"%)"
        status += chr(8)*(len(status)+1)
        print status,
    
    f.close()

    #Extracting contents of zip file
    if os.path.exists("tempdir"):
        shutil.rmtree("tempdir")
    os.mkdir("tempdir")

    images_zip = zipfile.ZipFile(filename)
    images_zip.extractall("tempdir")

    #Removing images currently in images_dir
    if os.path.exists(images_dir):
        try:
            shutil.rmtree(images_dir)
        except:
            sys.stderr.write("\nMake sure you have write permissions in the images directory.\n")
            sys.exit(0)

    #Copying downloaded images into images_dir
    shutil.copytree("tempdir/%s/share/uhd/images" % filename[:-4],images_dir)

    #Removing tempdir and zip file
    shutil.rmtree("tempdir")
    images_zip.close()
    os.remove(filename)

    print "\nImages successfully installed to: %s" % images_dir
