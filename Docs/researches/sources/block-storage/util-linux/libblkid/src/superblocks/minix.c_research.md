# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/minix.c

Minix filesystem detector for versions 1, 2, and 3 in native or swapped endianness. It reads the superblock at 1024 bytes, classifies version from magic values, and records whether byte-swapping is needed.

The probe validates state bits for v1/v2, inode and zone bitmap capacity, first data zone bounds, zero zone-size shift, and nonzero sane inode counts. It also reads the ext-family magic location and rejects matches that are actually ext filesystems, because ext metadata can otherwise resemble Minix.

On success it emits version, filesystem/device block size, and endianness. Labels and UUIDs are not part of this detector.
