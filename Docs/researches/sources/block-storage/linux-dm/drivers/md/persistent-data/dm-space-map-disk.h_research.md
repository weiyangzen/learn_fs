# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-disk.h

## Purpose
Public constructor interface for disk-backed space maps.

## API
- `dm_sm_disk_create(struct dm_transaction_manager *tm, dm_block_t nr_blocks)`: creates a new disk space map.
- `dm_sm_disk_open(struct dm_transaction_manager *tm, void *root, size_t len)`: opens an existing disk space map from a serialized root.

## Important Note
The header documents two-phase construction because the transaction manager and space map refer to each other.
