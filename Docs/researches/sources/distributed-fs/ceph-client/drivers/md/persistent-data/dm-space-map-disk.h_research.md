<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-disk.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-disk.h

## Purpose
Declares constructors for the disk/data `dm_space_map` implementation.

## Important APIs, Types, And Functions
`dm_sm_disk_create(struct dm_transaction_manager *tm, dm_block_t nr_blocks)` creates a new disk space map and initializes it to manage `nr_blocks`. `dm_sm_disk_open(struct dm_transaction_manager *tm, void *root, size_t len)` opens a previously persisted root. The header forward-declares `struct dm_space_map` and `struct dm_transaction_manager`.

## Control Flow
Callers create or open the space map after they have a transaction manager. The returned `struct dm_space_map` is then used through the generic inline wrappers in `dm-space-map.h`.

## State And Persistence
The root buffer passed to open must contain the serialized root produced by `copy_root()` from this implementation. Create performs an initial commit internally so its old/current map snapshots start synchronized.

## Dependencies And Integration Points
The header depends on `dm-block-manager.h` for `dm_block_t` and integrates with transaction-manager-managed metadata users.

## Risks
The file notes two-phase construction pressure caused by the transaction-manager/space-map cycle. Callers must not mix disk-space roots with metadata-space roots unless the surrounding format explicitly permits the same `disk_sm_root` layout and semantics.

## Test Signals
Tests should create/open roots, verify `root_size()` matches expected serialized size, and exercise the returned object only through generic `dm_space_map` operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-disk.h -->
