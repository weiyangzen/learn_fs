# sources/distributed-fs/ceph-client/drivers/md/dm-thin-metadata.c

## Purpose
`dm-thin-metadata.c` is the persistent metadata engine for the device-mapper thin provisioning target. It owns the on-disk superblock, metadata and data space maps, the two-level mapping btree `(thin device id, virtual block) -> packed(data block, time)`, and the device-details btree `thin id -> mapped block count / creation / snapshot times`. It is the transactional persistence layer used by `dm-thin.c`; it does not map bios itself.

## Important APIs, Types, And Functions
- `struct thin_disk_superblock` is the packed block-zero disk format. It contains checksum, feature flags, transaction id, held metadata snapshot root, space-map roots, mapping/detail roots, block sizes, and metadata device size.
- `struct dm_pool_metadata` is the in-memory pool metadata handle. Key fields are the block manager, transaction managers, metadata/data space maps, btree descriptors, `root_lock`, current transaction/time fields, in-service/fail flags, metadata reserve, and pre-commit callback.
- `struct dm_thin_device` tracks an opened virtual device, cached details, open count, changed flag, aborted-with-changes flag, and mapped block count.
- Superblock validation is handled by `sb_prepare_for_write()` and `sb_check()` using `dm_bm_checksum()` and `THIN_SUPERBLOCK_MAGIC`.
- `dm_pool_metadata_open()` creates block-manager and persistent-data objects, formats all-zero metadata when permitted, opens the current transaction, and calculates metadata reserve.
- `dm_pool_commit_metadata()` commits changed device details, data space-map roots, transaction-manager state, superblock roots, transaction id, flags, and then begins the next transaction.
- `dm_pool_abort_metadata()` destroys current persistent objects except the block manager, resets the block manager, reopens the last committed transaction, and sets `fail_io` if rollback fails.
- Device APIs include `dm_pool_create_thin()`, `dm_pool_create_snap()`, `dm_pool_delete_thin_device()`, `dm_pool_open_thin_device()`, and `dm_pool_close_thin_device()`.
- Mapping APIs include `dm_thin_find_block()`, `dm_thin_find_mapped_range()`, `dm_pool_alloc_data_block()`, `dm_thin_insert_block()`, and `dm_thin_remove_range()`.

## Control Flow
Opening first creates a `dm_block_manager`, then either formats or opens metadata. Formatting creates transaction manager and space maps, initializes mapping and details btrees, commits the space map, and writes an initial superblock. Opening validates the existing superblock, rejects unsupported feature flags, opens transaction manager and both space maps from roots, creates a non-blocking transaction-manager clone, loads mapping roots, and initializes btree descriptors.

Transactions flow through `__commit_transaction()`: optional pre-commit callback, flush changed `dm_thin_device` details into the details btree, commit data space map, pre-commit the transaction manager, copy both space-map roots into scratch buffers, lock the superblock for write, update time/root/detail-root/trans-id/flags/space-map roots, and commit through `dm_tm_commit()`. `dm_pool_commit_metadata()` wraps this under `root_lock` without marking the pool in-service and calls `__begin_transaction()` afterward.

Thin creation creates an empty bottom-level mapping tree, inserts its root into the top-level tree, then opens a new device details entry. Snapshot creation looks up and increments the origin mapping-root reference, inserts that root under the new device id, increments metadata time, opens the snapshot details, and updates origin/snapshot `snapshotted_time` so lookup can report shared blocks. Deletion removes the details entry and top-level mapping-tree entry after verifying the device is not open more than once.

Lookup uses `dm_btree_lookup()` on the two-level mapping tree and decodes the packed block/time. `shared` is inferred from `td->snapshotted_time > exception_time`, so sharing detection is timestamp based. Range lookup walks contiguous mapped blocks while physical block numbers and maybe-shared state remain adjacent. Insert packs current pool time with the allocated data block and increments mapped count only on new insertion. Range removal temporarily removes and pins the device mapping tree, removes leaves across mapped runs, updates mapped count, then reinserts the updated root.

## State And Persistence Behavior
The file persists all authoritative thin-pool metadata under block-zero superblock roots and persistent-data btrees. `root_lock` serializes metadata mutation and protects readers. The `in_service` flag avoids committing a newly opened pool solely because open/close happened; interfaces that imply live service call `pmd_write_lock()` and set it. `fail_io` is a hard error state after abort rollback failure; most public APIs then return `-EINVAL`, leaving close as the only useful operation.

Metadata snapshots reserve a held superblock copy in `held_root`. Reservation commits first, shadows block zero, increments mapping/detail roots to keep them alive, wipes space-map roots from the copy, and stores the held root in the live superblock. Release clears `held_root`, deletes preserved mapping/detail trees, and decrements the metadata block. The held root is intended for userspace read-only inspection.

Metadata reserve hides up to 4096 blocks or 10 percent of metadata space from free-space reporting, protecting commit overhead. `THIN_METADATA_NEEDS_CHECK_FLAG` is written directly to the superblock by `dm_pool_metadata_set_needs_check()` when repair is required.

## Dependencies And Integration Points
This file depends heavily on `persistent-data/dm-btree`, `dm-space-map`, `dm-space-map-disk`, `dm-transaction-manager`, and block-manager validation. `dm-thin.c` is the primary consumer. It registers a pre-commit callback that flushes the data device before metadata commit, uses metadata thresholds for dm events, calls create/snapshot/delete APIs from target messages, allocates data blocks while provisioning, and switches pool modes based on metadata API errors.

## Risks
- Timestamp-based shared-block detection intentionally overestimates sharing; this can cause extra copy-on-write work.
- Any failure during abort/reopen sets `fail_io`, making the pool effectively unrecoverable in-kernel until external repair.
- Metadata snapshot reservation increases copy-on-write pressure and must be released promptly by userspace.
- `__remove_range()` has multiple intermediate btree operations; failures can leave the active transaction invalid enough that callers must abort and mark needs-check.
- Feature flag support is zero for compat and incompat masks in this file; future metadata features must update these checks carefully.
- Metadata resize refuses shrink and relies on superblock/device-size comparisons in the target frontend.

## Test Signals
Useful tests include format/open/reopen on all-zero and existing metadata, create/open/close/delete thin devices, snapshot creation after quiescing origin, lookup shared/unshared transitions, commit and crash-reopen consistency, abort after injected metadata I/O failures, metadata snapshot reserve/release/get, resize grow-only behavior, low metadata free-space reserve accounting, and `needs_check` preventing return to write mode in `dm-thin.c`.
