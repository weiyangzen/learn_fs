# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/hpfs.c

HPFS detector. It matches the primary HPFS superblock magic at 0x2000, then reads the spare superblock at 0x2200 to verify its magic. It also reads the boot block to extract label and serial UUID when the boot signature, `HPFS` marker, and `0x28` serial-label signature are present.

On success it emits version from the HPFS superblock and fixed 512-byte block sizes. Detection depends on both primary and spare superblock validation, with optional boot-block identity fields.
