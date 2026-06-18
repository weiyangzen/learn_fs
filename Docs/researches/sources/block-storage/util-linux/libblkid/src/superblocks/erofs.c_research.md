# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/erofs.c

EROFS filesystem detector. It matches the v1 magic at 1024 bytes, validates block-size bits in the 512-byte to 64 KiB range, and if the superblock checksum feature is present, computes CRC32C over the superblock block with the checksum field excluded.

On success it emits label, UUID, filesystem/device block size, and filesystem size from block count times block size. The checksum code guards against underflow by requiring the block size to exceed the superblock offset before computing the checksummed span.
