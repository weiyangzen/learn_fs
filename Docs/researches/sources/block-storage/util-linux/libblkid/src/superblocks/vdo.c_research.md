# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/vdo.c

## Scope

Detects VDO metadata.

## Behavior

- Reads a minimal VDO superblock with magic `dmvdo001`.
- Exports the VDO superblock UUID.
- Registers usage as `BLKID_USAGE_OTHER`.

## Dependencies And Risks

- No additional geometry or checksum validation is implemented in this file.
- The structure intentionally models only fields needed by libblkid.
