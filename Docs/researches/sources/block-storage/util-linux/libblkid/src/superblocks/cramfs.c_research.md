# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/cramfs.c

Cramfs detector supporting little- and big-endian magic. It converts fields according to the magic hint, detects v1 versus v2 via the FSID version flag, and validates the v2 checksum by reading the declared filesystem image size and excluding the checksum field from CRC32 calculation.

On success it reports label, filesystem size, version `1` or `2`, and endianness. The checksum path bounds the declared size to a small sane range before reading. Version 1 lacks checksum validation, so detection relies mainly on the magic and extracted fields.
