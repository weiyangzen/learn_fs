# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/apfs.c

APFS container superblock detector. It recognizes `NXSB` at offset 32, reads the 4096-byte container header subset, validates the APFS Fletcher64 checksum over the object payload area, and requires container object type, subtype zero, zero padding, and a standard 4096-byte block size.

On success it reports filesystem type `apfs`, sets the container UUID, and records filesystem/device block size. The implementation is intentionally strict because APFS documentation is limited in the comment’s context. It does not parse volumes inside the APFS container, labels, feature flags, or container size beyond the minimal validation fields.
