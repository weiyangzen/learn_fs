# File Research: sources/block-storage/linux-dm/drivers/md/dm-ima.h

## Role
Declares device-mapper IMA measurement constants, stored metadata structures, and measurement hooks.

## Constants
- Defines buffer sizes for full measurements, device metadata, target metadata, target data, and capacity strings.
- Uses `sha256` as `DM_IMA_TABLE_HASH_ALG`.
- Builds `DM_IMA_VERSION_STR` from `DM_VERSION_MAJOR`, `DM_VERSION_MINOR`, and `DM_VERSION_PATCHLEVEL`.

## Data Structures
- `struct dm_ima_device_table_metadata` stores serialized device metadata, target count, and the hash string for one table state.
- `struct dm_ima_measurements` stores active and inactive table metadata plus cached DM version string length.

## API Surface
When `CONFIG_IMA` is enabled, declares reset, table-load, resume, remove, table-clear, and rename measurement functions. When disabled, all hooks are static no-ops.

## Filesystem/Storage Relevance
The header is the integration point that lets DM core call IMA measurement hooks without making IMA support mandatory.
