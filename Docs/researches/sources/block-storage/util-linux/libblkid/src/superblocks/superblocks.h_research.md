# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/superblocks.h

## Scope

Declares superblock idinfo symbols, endianness helpers, and superblock result setter APIs.

## Behavior

- Defines `enum blkid_endianness` and native/other endian macros from compiler byte order.
- Declares all filesystem, RAID, crypto, and other superblock `blkid_idinfo` objects used by `superblocks.c`.
- Declares APIs for setting version, labels, UUIDs, block sizes, filesystem size, last block, and endianness.
- Declares collision helpers `blkid_probe_is_bitlocker()` and `blkid_probe_is_ntfs()`.
- Provides `blkid32_to_cpu()` for value conversion using a runtime endian tag.

## Dependencies And Risks

- Header is shared by all superblock probers, so declarations must stay synchronized with per-format files.
- `blkid32_to_cpu()` aborts on invalid enum values, making caller-controlled endianness validation important.
