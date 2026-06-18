# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/zonefs.c

## Scope

Implements zonefs filesystem probing.

## Behavior

- Reads the 4 KiB zonefs superblock at offset 0.
- Verifies CRC32 excluding the stored CRC field.
- Exports label, UUID, filesystem block size, and block size as 4096 bytes.

## Dependencies And Risks

- All superblock fields are little-endian.
- CRC validation is required despite the magic table also matching `SFOZ`.
