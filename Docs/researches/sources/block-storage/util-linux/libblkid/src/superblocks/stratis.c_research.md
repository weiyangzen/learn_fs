# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/stratis.c

## Scope

Detects Stratis block device metadata.

## Behavior

- Reads the first 16 sectors and checks two possible superblock copies at sectors 1 and 9.
- Validates CRC32C over the 512-byte superblock sector, excluding the stored CRC.
- Converts hyphenless 32-byte ASCII UUIDs into canonical UUID strings for device UUID and `POOL_UUID`.
- Exports block device sector count and initialization time.

## Dependencies And Risks

- Magic table covers both copy locations, but the probefunc independently validates CRC and chooses the first valid copy.
- UUID formatting assumes Stratis stores ASCII UUID hex without hyphens.
