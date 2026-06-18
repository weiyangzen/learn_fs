# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/exfs.c

EXFS filesystem detector. It reads a big-endian superblock, converts the fields needed for validation into a temporary CPU-endian structure, and performs extensive sanity checks on sector size, block size, inode size, inodes-per-block log relationship, realtime extent size, allocation-group count, total data blocks, and inode percentage.

On success it emits the filesystem label, UUID, and block sizes. The magic is `EXFS` at the superblock start. False-positive resistance comes mostly from the many geometry and consistency checks rather than a checksum.
