# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/scoutfs.c

## Scope

Implements ScoutFS data-device and metadata-device probing.

## Behavior

- Reads a fixed 4 KiB ScoutFS superblock block and verifies CRC32C excluding the stored CRC field.
- Exports format version, UUID, FSID, and a wipe range.
- Differentiates `scoutfs_meta` and `scoutfs_data` via magic hint and `SCOUTFS_FLAG_IS_META_BDEV`.
- Sets 64 KiB block size for metadata devices and 4 KiB for data devices.

## Dependencies And Risks

- Both device types use identical magic and layout, so flag validation is required to classify correctly.
- CRC validation must pass before metadata is exported.
