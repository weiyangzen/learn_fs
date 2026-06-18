# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-metadata.h

## Purpose
Public interface and limits for metadata space maps.

## Main Definitions
- `DM_SM_METADATA_BLOCK_SIZE`: metadata block size in sectors for 4 KiB metadata blocks.
- `DM_SM_METADATA_MAX_BLOCKS`: maximum metadata blocks supported by the fixed metadata index design.
- `DM_SM_METADATA_MAX_SECTORS`: sector limit derived from max blocks.

## API
- `dm_sm_metadata_init()`: allocates an unbound metadata space-map object.
- `dm_sm_metadata_create()`: creates a fresh metadata space map with a transaction manager, block count, and superblock reservation.
- `dm_sm_metadata_open()`: opens an existing metadata space map from a serialized root.

## Important Note
Like the disk variant, construction is two-phase because metadata space maps and transaction managers depend on each other.
