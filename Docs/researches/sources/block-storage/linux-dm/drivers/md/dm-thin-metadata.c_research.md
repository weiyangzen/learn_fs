# File Research: sources/block-storage/linux-dm/drivers/md/dm-thin-metadata.c

## Purpose
Implements the persistent metadata engine for DM thin provisioning. It manages the thin-pool superblock, metadata and data space maps, thin-device details, hierarchical mapping btrees, snapshots, metadata transactions, metadata snapshots for userspace, allocation, resize, and read-only/fail states.

## On-Disk Model
- Superblock at block 0, designed to fit within one 512-byte sector.
- Metadata space map.
- Data space map.
- Device-details btree: `thin_id -> disk_device_details`.
- Two-level mapping btree: `(thin_id, virtual_block) -> block_time`.
- `block_time` packs a data block in the high 40 bits and transaction time in the low 24 bits.
- Superblock stores mapping roots, details root, space-map roots, transaction ID, flags, block sizes, and optional held metadata snapshot root.

## Main Objects
- `struct dm_pool_metadata`: in-core pool state, block manager, space maps, transaction managers, btree descriptors, root lock, roots, transaction ID, thin-device list, reserve, flags, and pre-commit callback.
- `struct dm_thin_device`: open thin-device state, mapped block count, creation/snapshot times, change flags, and open count.
- `struct thin_disk_superblock`: packed on-disk superblock with checksum.
- `struct disk_device_details`: packed on-disk mapped-block and timestamp details.

## Superblock and Opening
- `sb_prepare_for_write()` writes block number and checksum.
- `sb_check()` validates block number, magic, and checksum.
- `dm_pool_metadata_open()` creates the metadata object, opens or formats persistent structures, begins a transaction, and calculates metadata reserve.
- Empty all-zero superblocks are formatted only when `format_device` is true; otherwise open fails with `-EPERM`.
- Unsupported incompat or compat-ro features reject writable access.

## Transactions
- `__begin_transaction()` rereads superblock roots, time, transaction ID, flags, and data block size.
- `__commit_transaction()` writes changed thin-device details, commits data space map, pre-commits transaction manager, saves space-map roots, updates superblock fields, and commits the transaction.
- `dm_pool_commit_metadata()` commits without itself marking the pool in service, then begins the next transaction.
- `dm_pool_abort_metadata()` records which open devices had uncommitted changes, destroys/reopens persistent objects from the last good superblock, and sets `fail_io` if rollback fails.
- Most mutating public APIs take `pmd_write_lock()`, which also marks the pool `in_service`; internal/core-only paths use `pmd_write_lock_in_core()`.

## Thin Devices and Snapshots
- `dm_pool_create_thin()` creates an empty bottom-level mapping tree, inserts it in the top-level tree, and creates device details.
- `dm_pool_create_snap()` clones an origin by incrementing the origin mapping-root reference, inserts the snapshot mapping root, increments pool time, and updates origin/snapshot details.
- Snapshot sharing is inferred by comparing mapping block time with `td->snapshotted_time`.
- `dm_pool_delete_thin_device()` removes device details and mapping root, but refuses deletion when the device has more than one open reference.

## Mapping APIs
- `dm_thin_find_block()` looks up one virtual block, optionally using the non-blocking transaction-manager clone when I/O must not be issued.
- `dm_thin_find_mapped_range()` finds the next contiguous mapped range with same sharing state and contiguous pool blocks.
- `dm_pool_alloc_data_block()` allocates a new data block from the data space map.
- `dm_thin_insert_block()` inserts or replaces a virtual-to-data block mapping and updates mapped-block count on new insert.
- `dm_thin_remove_block()` removes a single mapping.
- `dm_thin_remove_range()` removes mapped leaves over a range by temporarily removing the device’s mapping tree from the top-level btree, editing it, and reinserting the updated root.

## Metadata Snapshots
- `dm_pool_reserve_metadata_snap()` commits current metadata, shadows/copies the superblock, strips space-map roots from the copy, increments preserved btree roots, and records the held root in the live superblock.
- `dm_pool_release_metadata_snap()` clears the held root, deletes preserved mapping/details roots, and decrements the held superblock block.
- `dm_pool_get_metadata_snap()` reads the held root for userspace.

## Queries and Maintenance
- Free/total data and metadata block counts.
- Metadata free count subtracts reserved commit-overhead blocks.
- Highest mapped block and mapped block count.
- Shared-block check through data-space-map reference count.
- Data and metadata resize extend space maps only.
- Read-only/read-write toggles on the block manager.
- Metadata threshold callback registration.
- Immediate `needs_check` flag update in the superblock.
- Transaction-manager prefetch issuance.
- Pre-commit callback registration.

## Dependencies
- Persistent-data block manager, transaction manager, btree, disk space map, and metadata space map.
- Device-mapper block-device types and workqueue headers.
- Kernel locking via rwsem and list management.

## Notable Contract Observations
- The header says opening the same thin device more than once fails with `-EBUSY`, but `__open_device()` increments `open_count` for existing non-create opens. Callers may rely on higher-level single-open discipline.
- The resize comment says shrinking may return `-ENOSPC` if allocated blocks would be lost, but implementation rejects all shrink attempts with `-EINVAL`.
- `fail_io` gates almost all operations after an unrecoverable abort/reopen failure.

## Risk and Test Focus
- Transaction commit ordering is critical: changed details, data space map commit, metadata pre-commit, root copy, superblock update.
- Snapshot creation and metadata snapshots both depend on correct reference-count increments/decrements of shared btree roots.
- `dm_thin_remove_range()` has complex root removal/reinsertion behavior and should be tested across unmapped holes and partial ranges.
- Non-blocking lookup behavior should be verified for `-EWOULDBLOCK`.
- Metadata reserve subtraction can report zero free metadata despite actual reserved blocks.
