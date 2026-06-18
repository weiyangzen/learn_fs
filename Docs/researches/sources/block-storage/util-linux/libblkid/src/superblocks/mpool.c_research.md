# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/mpool.c

mpool detector. It matches the ASCII `mpoolDev` magic, reads the superblock descriptor, and validates CRC32C over all descriptor fields preceding the checksum field.

On success it emits pool label and pool UUID. It reports filesystem usage under name `mpool`; the detector is compact and relies on magic plus checksum for false-positive resistance.
