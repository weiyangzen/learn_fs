# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/jfs.c

JFS detector. It matches `JFS1` at 32 KiB, then validates block-size and physical-block-size logarithms, exact power-of-two relationships, and the logical-to-physical block factor.

On success it emits label, UUID, filesystem block size, and device block size. The geometry checks reduce false positives from the simple four-byte magic. The idinfo declares a 16 MiB minimum size.
