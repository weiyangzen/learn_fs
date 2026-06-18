# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/ubifs.c

## Scope

Implements UBIFS filesystem probing.

## Behavior

- Defines UBIFS common header and superblock node structures.
- Verifies CRC32 over the superblock node starting at `sqnum`, matching UBIFS node checksum rules.
- Exports UUID, version as `w<fmt_version>r<ro_compat_version>`, and filesystem size as `leb_size * leb_cnt`.

## Dependencies And Risks

- Magic is little-endian byte sequence for UBIFS node magic.
- The packed 4 KiB superblock node is read as a complete structure before CRC validation.
