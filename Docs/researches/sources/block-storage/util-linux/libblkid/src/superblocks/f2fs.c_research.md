# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/f2fs.c

F2FS detector. It matches the magic at the primary superblock offset, extracts major/minor version, and treats version 1.0 specially because the current structure layout cannot be assumed. For newer versions it validates the optional superblock checksum at the declared checksum offset using the F2FS seed.

On success it emits UTF-16LE volume name, UUID, version, block sizes, and filesystem size from block count times block size. The code bounds checksum offset alignment and size, and avoids shifts above 16 when computing block size.
