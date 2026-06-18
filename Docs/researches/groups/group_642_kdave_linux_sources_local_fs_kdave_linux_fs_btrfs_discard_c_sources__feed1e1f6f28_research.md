# Group Research: group_642_kdave_linux_sources_local_fs_kdave_linux_fs_btrfs_discard_c_sources__feed1e1f6f28

Scope: `Docs/research_subset_a.md` / `sources/local-fs/kdave-linux/fs/btrfs/*`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/discard.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/discard.c

## Role

Implements Btrfs asynchronous discard for data-only block groups. It schedules and rate-limits trim work outside transaction commit, tracks block groups on multiple discard queues, advances each block group through extent and bitmap trimming passes, and hands completely free and fully trimmed block groups back to the unused-block-group path.

## Core Model

- `BTRFS_DISCARD_DELAY` gives recently freed space a 120-second reuse window before ordinary async discard work starts.
- `BTRFS_DISCARD_UNUSED_DELAY` gives fully free block groups a shorter 10-second delay before final discard and unused block group processing.
- `discard_minlen[]` defines the three queue filters: unused/full-free queue, large extent filter (`BTRFS_ASYNC_DISCARD_MAX_FILTER`), and smaller extent filter (`BTRFS_ASYNC_DISCARD_MIN_FILTER`).
- `discard_ctl->discard_list[]` stores block groups by discard priority/pass. Each queued block group has a `discard_index`, `discard_state`, `discard_cursor`, and `discard_eligible_time`.
- The code supports data-only block groups and explicitly avoids mixed block groups.
- Empty block-group detection uses `used == 0 && remap_bytes == 0`, or `identity_remap_count == 0` for remapped block groups.

## Queue Management

- `btrfs_run_discard_work()` gates async discard on a writable superblock and `BTRFS_FS_DISCARD_RUNNING`.
- `__add_to_discard_list()` initializes a block group's discard cursor state, eligibility time, and reference, then moves it to the tail of the selected discard list.
- `add_to_discard_list()` filters out non-data-only groups and disabled discard state before queueing.
- `add_to_discard_unused_list()` moves fully empty groups to `BTRFS_DISCARD_INDEX_UNUSED`, using the shorter unused delay and taking a reference if the group was not already queued.
- `remove_from_discard_list()` removes a queued or currently running block group, drops queue references, clears eligibility time, and tells the caller whether it removed the active work item.
- `find_next_block_group()` scans all discard lists for the earliest eligible block group, preferring an already-eligible group when found.
- `peek_discard_list()` chooses a block group for the worker, handles stale unused-list entries that are no longer empty, initializes the state machine, and records the active block group under `discard_ctl->block_group`.

## Worker State Machine

`btrfs_discard_workfn()` performs at most one trim step per work invocation:

- It gets the next eligible block group through `peek_discard_list()`.
- It exits or reschedules if discard has stopped or the selected group is not eligible yet.
- For `BTRFS_DISCARD_EXTENTS`, it calls `btrfs_trim_block_group_extents()` and accumulates `discard_extent_bytes`.
- For `BTRFS_DISCARD_BITMAPS`, it calls `btrfs_trim_block_group_bitmaps()` with the current minimum length and a previous-list maximum length filter, then accumulates `discard_bitmap_bytes`.
- For `BTRFS_DISCARD_FULLY_REMAPPED`, it calls `btrfs_trim_fully_remapped_block_group()`.
- When the block-group cursor reaches the end of the group, the worker either switches from extent pass to bitmap pass or calls `btrfs_finish_discard_pass()`.
- It records `prev_discard` and `prev_discard_time` for rate-limit scheduling before releasing the active block group and scheduling the next work item.

## Scheduling and Rate Limits

- `btrfs_discard_schedule_work()` wraps `__btrfs_discard_schedule_work()` with the discard lock.
- `__btrfs_discard_schedule_work()` respects pending delayed work unless `override` is set, starts from `discard_ctl->delay_ms`, and increases delay to account for:
  - `kbps_limit` derived from the size of the previous discard;
  - block-group eligibility time;
  - elapsed time since the previous discard when overriding an existing timer.
- `btrfs_discard_calc_delay()` derives the base delay from `iops_limit`, clamps it between 0/1 ms and 1000 ms, and defensively corrects negative discardable extent/byte counters.

## Public Operations

- `btrfs_discard_check_filter()` reprioritizes a block group if a newly freed/coalesced range is large enough for an earlier discard filter list.
- `btrfs_discard_cancel_work()` removes a block group and, if it was active, cancels the delayed worker synchronously and reschedules.
- `btrfs_discard_queue_work()` queues a block group on the unused or ordinary discard path and starts the delayed work if needed.
- `btrfs_discard_update_discardable()` propagates per-block-group free-space-cache discardable extent/byte deltas to the global discard controller.
- `btrfs_discard_punt_unused_bgs_list()` moves already marked unused block groups back through async discard when async discard is enabled.
- `btrfs_discard_resume()`, `btrfs_discard_stop()`, `btrfs_discard_init()`, and `btrfs_discard_cleanup()` manage lifecycle and cleanup.

## Concurrency and Lifetime

- `discard_ctl->lock` protects discard queues, active block group pointer, scheduling state, and state transitions.
- Queued block groups hold an extra block-group reference until removed or purged.
- Active worker state holds an additional reference while trimming.
- Cleanup stops discard, cancels the delayed worker, then purges all lists. Purging marks fully free block groups unused when async discard is being disabled.
- The code carefully avoids an infinite loop in `peek_discard_list()` if a group on the unused list is no longer empty and discard was disabled or the group is no longer data-only.

## Dependencies

Uses Btrfs block-group, free-space-cache, filesystem option, unused block-group, and trim helpers. It is invoked by block-group/free-space code when free space changes, by transaction/commit paths for discardable accounting and delay recalculation, and by mount/unmount paths through discard init/resume/cleanup.

## Research Notes

The file's central design is to convert discard from a synchronous transaction-commit cost into a controlled delayed background process. The in-memory free-space cache is the source of discard state, so state is intentionally rebuilt as untrimmed after mount or crash. The implementation accepts some overtrimming, especially for bitmap-backed free space, to get better coalescing and cheaper accounting.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/discard.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/discard.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/discard.h

## Role

Declares the internal Btrfs async-discard interface and the discard filter size constants used by `discard.c` and related free-space/block-group code.

## Key Definitions

- `BTRFS_ASYNC_DISCARD_DEFAULT_MAX_SIZE`: default maximum async discard size, 64 MiB.
- `BTRFS_ASYNC_DISCARD_MAX_FILTER`: large extent filter threshold, 1 MiB.
- `BTRFS_ASYNC_DISCARD_MIN_FILTER`: small extent filter threshold, 32 KiB.
- Forward declarations cover `btrfs_fs_info`, `btrfs_discard_ctl`, and `btrfs_block_group`.

## API Surface

- Queue/list operations: `btrfs_discard_check_filter()`.
- Work operations: `btrfs_discard_cancel_work()`, `btrfs_discard_queue_work()`, `btrfs_discard_schedule_work()`.
- Accounting operations: `btrfs_discard_calc_delay()`, `btrfs_discard_update_discardable()`.
- Setup and lifecycle: `btrfs_discard_punt_unused_bgs_list()`, `btrfs_discard_resume()`, `btrfs_discard_stop()`, `btrfs_discard_init()`, `btrfs_discard_cleanup()`.

## Dependencies

Includes Linux integer and size definitions only. The header intentionally keeps consumers decoupled from the discard controller and block-group structure definitions.

## Research Notes

This is a narrow subsystem header. It exposes enough for mount/unmount, transaction commit, free-space accounting, and block-group lifecycle code to drive async discard while keeping the queueing and worker state machine private to `discard.c`.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/discard.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/disk-io.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/disk-io.c

## Role

Large Btrfs core file for metadata I/O, superblock validation/writes, root allocation and lookup, mount initialization, unmount teardown, transaction cleanup, and metadata dirty throttling. It is the coordination layer that brings together devices, roots, block groups, workqueues, log replay, qgroups, discard, zoned mode, and cleaner/transaction kthreads.

## Metadata Checksum and Tree-Block I/O

- `csum_tree_block()` calculates the checksum for a tree block over all extent-buffer pages or the contiguous buffer mapping.
- `btrfs_buffer_uptodate()` validates an already-cached extent buffer against parent transid and optional parentness checks.
- `btrfs_supported_super_csum()` accepts CRC32C, XXHASH, SHA256, and BLAKE2 superblock checksum types.
- `btrfs_check_super_csum()` verifies the superblock checksum over the full 4 KiB superblock area after the checksum field.
- `btrfs_read_extent_buffer()` reads an extent buffer with mirror retry. If a bad mirror is found and another mirror succeeds, it attempts repair through `btrfs_repair_eb_io_failure()`.
- `btree_csum_one_bio()` validates and writes a dirty tree block checksum before metadata write I/O. It also detects write-time tree block corruption, bad generation, wrong bytenr, and zoned zeroout buffers.
- `btrfs_validate_extent_buffer()` performs read-time validation: bytenr, FSID/metadata UUID or seed FSID, level, checksum, parent transid, first key, owner root, and node/leaf structural checks.
- `read_tree_block()` allocates/fetches an extent buffer and reads it with the provided `btrfs_tree_parent_check`.

## Btree Address-Space Operations

- `btree_release_folio()` refuses to release dirty or writeback metadata folios and delegates to `try_release_extent_buffer()`.
- `btree_invalidate_folio()` invalidates extent I/O state and warns if private state remains.
- `btree_migrate_folio()` is available under migration support and refuses migration for dirty or privately pinned metadata folios.
- Debug `btree_dirty_folio()` verifies dirty extent-buffer invariants for normal and subpage metadata before marking the folio dirty.
- `btree_aops` wires metadata writeback, folio release, invalidation, migration, and dirtying behavior for the internal btree inode.

## Root Allocation, Lookup, and Lifetime

- `btrfs_alloc_root()` initializes an in-memory root: xarrays, reservation structures, delalloc/ordered/log lists, locks, waitqueues, qgroup state, log counters, references, and debug leak tracking.
- `btrfs_create_tree()` allocates a new tree root, creates its initial leaf, initializes root item fields and UUID, inserts it into the tree root, and returns the new root.
- `alloc_log_tree()`, `btrfs_alloc_log_tree_node()`, `btrfs_init_log_root_tree()`, and `btrfs_add_log_tree()` create log-tree roots and per-subvolume log roots.
- `read_tree_root_path()` reads a root item from the tree root, loads its root node, validates generation/owner, and sets `commit_root`.
- `btrfs_read_tree_root()` is the public wrapper around `read_tree_root_path()`.
- `btrfs_init_fs_root()` initializes user-visible filesystem roots, assigns anonymous block devices, marks shareable roots, and seeds `free_objectid`.
- `btrfs_get_fs_root()`, `btrfs_get_new_fs_root()`, and `btrfs_get_fs_root_commit_root()` retrieve root references from global roots, the radix cache, or disk.
- `btrfs_insert_fs_root()`, `btrfs_drop_and_free_fs_root()`, `btrfs_free_fs_roots()`, and `btrfs_put_root()` manage radix-tree membership and root references.
- `btrfs_global_root_insert()`, `btrfs_global_root_delete()`, `btrfs_global_root()`, `btrfs_csum_root()`, and `btrfs_extent_root()` manage the global-root rb-tree used by extent tree v2 and per-global-id roots.

## Superblock and Backup Root Handling

- `find_newest_super_backup()`, `backup_super_roots()`, and `read_backup_root()` maintain the rotating superblock backup root array.
- `validate_sys_chunk_array()` validates the system chunk array embedded in the superblock.
- `btrfs_validate_super()` performs mount/write-time structural validation of magic, flags, root levels, sectorsize, nodesize, alignment, FSID/metadata UUIDs, feature dependencies, bytes-used sanity, stripesize, device count, superblock bytenr, system chunks, and suspicious generation relationships.
- `btrfs_validate_mount_super()` validates the mounted superblock mirror.
- `btrfs_validate_write_super()` repeats super validation before write and additionally validates checksum type and incompat flags.
- `write_dev_supers()` writes superblock mirrors to a device with direct bios and FUA for the primary mirror when barriers are enabled.
- `wait_dev_supers()` waits for submitted superblock writes and treats primary mirror failure specially.
- `write_dev_flush()`, `wait_dev_flush()`, and `barrier_all_devices()` issue and wait for device flushes across writable metadata devices.
- `write_all_supers()` coordinates pre-super barriers, backup root update, per-device dev item population, superblock validation, writes, and wait/error accounting.

## Mount Initialization

`open_ctree()` is the full mount path:

- Initializes `fs_info` counters and root structures, creates the internal btree inode, reads the latest device superblock, validates checksum type and checksum value, and copies it to `super_copy` and `super_for_commit`.
- Validates the superblock, initializes checksum, nodesize, sectorsize, block orders, csum geometry, free-space cache settings, mount options, and feature compatibility.
- Allocates compression workspace and all major workqueues, adjusts readahead, reads the system array, loads chunk root, reads the chunk tree, and frees extra device IDs.
- Loads important roots and global roots, with backup-root retry support when requested.
- Initializes zoned device information, verifies device items and extents, recovers balance state, initializes device stats and device replacement, initializes sysfs, space info, and block groups.
- Starts the cleaner and transaction kthreads, reserves zoned data relocation block groups, reads qgroup config, optionally builds the reference verification tree, replays the log tree when required, and loads the default filesystem tree.
- For read-write mounts, calls `btrfs_start_pre_rw_mount()`, resumes async discard, optionally checks/rescans the UUID tree, sets `BTRFS_FS_OPEN`, and wakes the cleaner for unfinished drops.
- Error labels unwind initialized kthreads, qgroups, sysfs, block groups, roots, workqueues, mapping trees, and the btree inode in reverse order.

## Read-Write Mount Preparation

`btrfs_start_pre_rw_mount()` performs rw-only recovery and format maintenance:

- Rebuilds, deletes, or creates the free-space tree based on mount options and on-disk validity.
- Deletes orphan free-space-tree entries left by older mkfs behavior.
- Finds orphan roots before orphan cleanup so pending deleted subvolumes are not lost.
- Cleans cached filesystem roots and root/tree orphans.
- Recovers relocation, synchronizes space-cache v1 activation, resumes balance and device replace, resumes qgroup rescan, and creates the UUID tree if absent.

## Feature and Runtime Checks

- `btrfs_check_features()` rejects unsupported incompat features and rw mounts with unsupported compat-ro features, blocks unsafe log replay with unsupported compat-ro flags, enforces mixed-group sectorsize/nodesize constraints, sets always-enabled and compression-related incompat flags, enforces block-group-tree and space-cache dependencies, and rejects v1 space cache for subpage sectorsize.
- `fs_is_full_ro()` detects rescue/full-read-only mount modes that must prevent transactions.

## Kthreads and Workqueues

- `cleaner_kthread()` runs delayed iputs, deleted snapshot cleanup, defrag work, fully remapped block-group handling when async discard is off, unused block-group deletion, and block-group reclaim. It parks/stops cooperatively and updates `BTRFS_FS_CLEANER_RUNNING`.
- `transaction_kthread()` periodically commits the running transaction based on `commit_interval` or explicit commit requests, wakes the cleaner, and invokes transaction cleanup on filesystem errors.
- `btrfs_init_workqueues()` creates worker, delalloc, flush, cache, fixup, endio, metadata endio, rmw, freespace, delayed metadata, qgroup rescan, and discard workqueues.
- `btrfs_stop_all_workers()` destroys those queues in an order that preserves metadata I/O safety until dependent queues are gone.

## Unmount and Error Cleanup

- `close_ctree()` begins closing, wakes unfinished drops, cancels reclaim, parks the cleaner, waits for qgroup/UUID tasks, pauses balance, suspends dev-replace, cancels scrub, waits for defrag, handles error cleanup, flushes workqueues in an order that prevents delayed iputs after kthread destruction, cancels reclaim/shrinker work, runs delayed iputs, disables new delayed iputs, cleans up async discard, deletes unused block groups, flushes delayed workers, commits the superblock when appropriate, stops kthreads, frees qgroups, removes sysfs, drops block-group cache, checks uncommitted transactions, frees roots, invalidates btree inode pages, stops workers, frees block groups, releases the btree inode, and frees the mapping tree.
- `btrfs_error_commit_super()` runs transaction cleanup and waits on cleanup work for aborted filesystems.
- `btrfs_cleanup_transaction()` walks all transactions, waits for those already committing, cleans pending ones, destroys ordered extents, delayed inodes, delalloc inodes, logs, and per-transaction qgroup state.
- `btrfs_cleanup_one_transaction()` cleans dirty block groups, delayed refs, dirty metadata extents, pinned extents, and wakes commit waiters.
- `btrfs_cleanup_dirty_bgs()` handles dirty and I/O block-group lists, marks disk cache state error, drops refs, and cleans up free-space cache inode I/O.
- `btrfs_destroy_marked_extents()` and `btrfs_destroy_pinned_extent()` clear transaction extent-state trees during abort/error cleanup.

## Miscellaneous Operations

- `btrfs_init_fs_info()` initializes almost every lock, list, rb-tree, radix/xarray, waitqueue, reservation, default option, counter, and subsystem state in `fs_info`.
- `init_mount_fs_info()` initializes mount-time percpu counters, delayed root, read-only/error state bits, and stripe hash table.
- `btrfs_check_uuid_tree()` starts a UUID tree rescan kthread after taking the rescan semaphore.
- `btrfs_commit_super()` runs delayed iputs, waits for cleanup work, and commits the current transaction.
- `btrfs_mark_buffer_dirty()` asserts transaction/generation correctness before setting an extent buffer dirty.
- `btrfs_btree_balance_dirty()` and `btrfs_btree_balance_dirty_nodelay()` throttle dirty metadata through `balance_dirty_pages_ratelimited()`.
- `btrfs_init_root_free_objectid()` searches the root for the highest object ID and seeds the next free object ID.
- `btrfs_get_free_objectid()` returns and increments a root's free object ID under `objectid_mutex`.
- `btrfs_get_num_tolerated_disk_barrier_failures()` computes the minimum tolerated flush failure count across RAID profiles.

## Dependencies

This file depends on nearly every major Btrfs subsystem: transactions, inode state, delayed inodes, bios, tree locking/checking, free-space cache/tree, dev-replace, RAID56, sysfs, qgroups, compression, ref verification, block groups, discard, space info, zoned mode, subpage metadata, extent tree, root tree, defrag, UUID tree, relocation, scrub, and superblock helpers. It also binds to Linux VFS, block-device, writeback, kthread, workqueue, migration, checksum, UUID, semaphore, and error-injection APIs.

## Research Notes

`disk-io.c` is not just disk I/O. It is the mount lifecycle orchestrator and the point where Btrfs validates durable metadata before trusting it. Its most important behavior is ordering: validation before root loading, device/chunk setup before logical tree I/O, kthreads before transactions, rw recovery before opening, and a very deliberate teardown sequence to avoid delayed iput, ordered extent, workqueue, and transaction races during unmount or abort.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/disk-io.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/disk-io.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/disk-io.h

## Role

Internal header for Btrfs metadata I/O, root management, mount/unmount, superblock writing, log-tree creation, dirty metadata throttling, transaction cleanup, and free object ID allocation.

## Constants and Inline Helpers

- `BTRFS_SUPER_MIRROR_MAX` defines three possible superblock mirrors.
- `BTRFS_SUPER_MIRROR_SHIFT` controls backup superblock mirror spacing.
- `BTRFS_BDEV_BLOCKSIZE` fixes the block-device block size used for metadata/superblock reads at 4096 bytes.
- `btrfs_sb_offset()` maps mirror index 0 to `BTRFS_SUPER_INFO_OFFSET` and higher mirror indices to shifted 16 KiB offsets.
- `btrfs_grab_root()` safely increments a root refcount only if it is nonzero.

## API Surface

- Metadata I/O and validation: `read_tree_block()`, `btrfs_find_create_tree_block()`, `btrfs_validate_extent_buffer()`, `btrfs_buffer_uptodate()`, `btrfs_read_extent_buffer()`, `btree_csum_one_bio()`.
- Mount and superblock operations: `open_ctree()`, `close_ctree()`, `btrfs_start_pre_rw_mount()`, `btrfs_validate_super()`, `btrfs_check_features()`, `btrfs_check_super_csum()`, `write_all_supers()`, `btrfs_commit_super()`.
- Root operations: `btrfs_read_tree_root()`, `btrfs_insert_fs_root()`, `btrfs_free_fs_roots()`, `btrfs_get_fs_root()`, `btrfs_get_new_fs_root()`, `btrfs_get_fs_root_commit_root()`, `btrfs_global_root_insert()`, `btrfs_global_root_delete()`, `btrfs_global_root()`, `btrfs_csum_root()`, `btrfs_extent_root()`, `btrfs_put_root()`, `btrfs_drop_and_free_fs_root()`, `btrfs_create_tree()`.
- Log tree operations: `btrfs_alloc_log_tree_node()`, `btrfs_init_log_root_tree()`, `btrfs_add_log_tree()`.
- Lifecycle and cleanup: `btrfs_init_fs_info()`, `btrfs_free_fs_info()`, `btrfs_check_leaked_roots()`, `btrfs_cleanup_dirty_bgs()`, `btrfs_cleanup_one_transaction()`.
- Utility operations: `btrfs_mark_buffer_dirty()`, `btrfs_btree_balance_dirty()`, `btrfs_btree_balance_dirty_nodelay()`, `btrfs_get_num_tolerated_disk_barrier_failures()`, `btrfs_get_free_objectid()`, `btrfs_init_root_free_objectid()`.
- Test-only declaration: `btrfs_alloc_dummy_root()` under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`.

## Dependencies

Includes core Btrfs tree definitions, bio definitions, and ordered-data definitions. It forward declares common mount, root, device, transaction, superblock, extent-buffer, and parent-check structures to keep compile-time coupling lower for consumers.

## Research Notes

This header exposes the durable metadata lifecycle contract for the rest of Btrfs. The exported functions are broad because `disk-io.c` is the common implementation point for root lookup, tree-block validation, mount setup, unmount cleanup, and superblock commit behavior.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/disk-io.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/export.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/export.c

## Role

Implements Btrfs `export_operations` for NFS/exportfs-style file handles. It encodes Btrfs inode and root identity into file handles, decodes file handles back to dentries, finds parent dentries, and resolves child names from parent/child dentries across ordinary subvolume files and subvolume root entries.

## File Handle Encoding

- `BTRFS_FID_SIZE_NON_CONNECTABLE`, `BTRFS_FID_SIZE_CONNECTABLE`, and `BTRFS_FID_SIZE_CONNECTABLE_ROOT` describe file-handle sizes in 32-bit words.
- `btrfs_encode_fh()` writes:
  - inode object ID;
  - root object ID;
  - inode generation;
  - optional parent object ID and generation;
  - optional parent root object ID when parent and child live in different roots.
- It returns `FILEID_BTRFS_WITHOUT_PARENT`, `FILEID_BTRFS_WITH_PARENT`, `FILEID_BTRFS_WITH_PARENT_ROOT`, or `FILEID_INVALID` when the caller's buffer is too small.

## File Handle Decoding

- `btrfs_get_dentry()` validates object IDs, gets the target root by root object ID, loads the inode with `btrfs_iget()`, verifies generation when provided, and returns `d_obtain_alias()` for the inode.
- `btrfs_fh_to_dentry()` validates file-handle type/length, extracts object ID, root ID, and generation, then delegates to `btrfs_get_dentry()`.
- `btrfs_fh_to_parent()` handles only parent-bearing file-handle types, selects either the child's root ID or explicit parent root ID, and delegates to `btrfs_get_dentry()` for the parent object.

## Parent and Name Lookup

- `btrfs_get_parent()` handles two cases:
  - For a subvolume root inode (`BTRFS_FIRST_FREE_OBJECTID`), it searches the tree root for a `BTRFS_ROOT_BACKREF_KEY` and returns the containing directory in the parent root.
  - For an ordinary inode, it searches the current root for the previous `BTRFS_INODE_REF_KEY` and returns the referenced parent inode.
- The function treats an exact key with offset `-1` as corruption (`-EUCLEAN`) because such an inode/root ID should not exist.
- `btrfs_get_name()` resolves the name of `child` under `parent`. It rejects non-directory parents, then reads either:
  - a `BTRFS_ROOT_BACKREF_KEY` name for subvolume root entries; or
  - a `BTRFS_INODE_REF_KEY` name for ordinary inode references.
- It copies the name from the leaf item payload and appends a null terminator for exportfs reconnect path handling.

## Export Operations

`btrfs_export_ops` wires:

- `.encode_fh = btrfs_encode_fh`
- `.fh_to_dentry = btrfs_fh_to_dentry`
- `.fh_to_parent = btrfs_fh_to_parent`
- `.get_parent = btrfs_get_parent`
- `.get_name = btrfs_get_name`

## Dependencies

Uses VFS/exportfs interfaces, Btrfs inode helpers, root lookup through `disk-io.h`, tree search/accessor helpers, superblock access, and Btrfs root/inode reference item formats.

## Research Notes

The key Btrfs-specific export complexity is that inode numbers are only unique inside a root/subvolume. File handles must include root identity, and connectable file handles may need the parent's root identity too. Subvolume roots are represented through root backrefs rather than ordinary inode refs, so both parent and name lookup have dedicated subvolume-root branches.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/export.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/export.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/export.h

## Role

Declares Btrfs exportfs support: the exported operations table, packed Btrfs file-handle payload, and helper functions used to reconstruct dentries and parents.

## Key Definitions

- `extern const struct export_operations btrfs_export_ops`: operations installed for exportfs/NFS file-handle support.
- `struct btrfs_fid`: packed file-handle layout containing:
  - `objectid`: inode object ID;
  - `root_objectid`: root/subvolume object ID;
  - `gen`: inode generation;
  - `parent_objectid`: optional parent inode object ID;
  - `parent_gen`: optional parent generation;
  - `parent_root_objectid`: optional parent root ID for cross-root parent handles.

## API Surface

- `btrfs_get_dentry()` reconstructs a dentry from superblock, inode object ID, root object ID, and optional generation.
- `btrfs_get_parent()` returns a dentry for the parent of a child dentry.

## Dependencies

Includes Linux exportfs and integer types. It forward declares `dentry` and `super_block` so consumers do not need the full VFS definitions from this header alone.

## Research Notes

The packed file-handle structure mirrors the three encoding modes in `export.c`: non-connectable inode/root/generation, connectable same-root parent information, and connectable cross-root parent information.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/export.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/extent-io-tree.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/extent-io-tree.c

## Role

Implements Btrfs extent state trees: red-black trees of byte ranges tagged with state bits such as dirty, locked, delalloc, boundary, qgroup reserved, and device-allocation state. The file provides range set/clear/convert/test/find/count/lock operations with range splitting, merging, cached-state optimization, wait queues for locked ranges, changeset accounting, and debug leak tracking.

## Data Model

- `struct extent_io_tree` owns an rb-tree of `struct extent_state` records and a spinlock.
- `struct extent_state` stores an inclusive `[start, end]` byte range, rb-node, wait queue, refcount, and state bitmask.
- Adjacent states with identical mergeable bitmasks are merged unless they contain lock bits or boundary bits.
- For inode I/O trees, state changes are mirrored into delalloc accounting through `btrfs_set_delalloc_extent()`, `btrfs_clear_delalloc_extent()`, `btrfs_split_delalloc_extent()`, and `btrfs_merge_delalloc_extent()`.
- `extent_changeset` integration counts changed bytes and can record changed ranges in a ulist.

## Allocation and Debugging

- `btrfs_extent_state_init_cachep()` creates the `btrfs_extent_state` slab cache.
- `btrfs_extent_state_free_cachep()` checks debug leaks and destroys the cache.
- `alloc_extent_state()` masks unsupported GFP flags, allocates a state, initializes rb-node/refcount/waitqueue/state, registers debug leak tracking, and traces allocation.
- `btrfs_free_extent_state()` decrements the state reference and frees only when it reaches zero, warning if the state is still in a tree.
- Under `CONFIG_BTRFS_DEBUG`, leaked states are kept on a global list and reported with range/state/refcount information.
- `btrfs_debug_check_extent_io_range()` warns about suspicious inode I/O ranges in debug builds.

## Tree Search and Structural Helpers

- `tree_search_for_insert()` finds a state containing an offset or the first state after the offset, and can return rb insertion position.
- `tree_search_prev_next()` finds a containing state or previous/next neighbors.
- `tree_search()` is the inexact search wrapper.
- `next_state()` and `prev_state()` navigate rb-tree neighbors.
- `merge_prev_state()`, `merge_next_state()`, and `merge_state()` combine adjacent compatible states and update inode delalloc accounting when relevant.
- `insert_state()` inserts a new state and can merge it into adjacent states.
- `insert_state_fast()` inserts at a known rb position and merges.
- `split_state()` splits an existing state at a byte offset using a preallocated state for the lower half.
- `state_wake_up()` wakes waiters when lock bits are cleared.
- `set_gfp_mask_from_bits()` interprets `EXTENT_NOWAIT` as `GFP_NOWAIT` and strips it from the state bits.

## Clearing Bits

`btrfs_clear_extent_bit_changeset()` clears bits over an inclusive range:

- It optionally treats `EXTENT_CLEAR_ALL_BITS` as deleting all non-control bits.
- Clearing `EXTENT_DELALLOC` also includes `EXTENT_NORESERVE`.
- It uses cached states when possible, searches for overlapping records, splits records at range boundaries, clears target bits, wakes lock waiters, removes states that become empty, and merges remaining compatible states.
- It contains optimized paths for clearing an entire suffix/prefix without allocating a split state when all bits would be removed.
- It supports nowait allocation semantics through `EXTENT_NOWAIT`.
- `btrfs_clear_extent_bit()` and `btrfs_unlock_extent()` are inline wrappers declared in the header, while `btrfs_clear_record_extent_bits()` records changed ranges.

## Setting and Converting Bits

- `set_extent_bit()` is the core range setter. It handles holes, overlapping states, splits, mergeable insertions, cached states, optional changesets, and exclusive lock bits.
- Exclusive lock bits return `-EEXIST` with the failing start offset and optional failed state when the requested range overlaps an already locked state.
- `btrfs_set_extent_bit()` is the public plain setter.
- `btrfs_set_record_extent_bits()` sets non-lock bits while recording changed ranges.
- `btrfs_convert_extent_bit()` sets one set of bits and clears another over a range, intended for mergeable state transitions such as delalloc to dirty. It is not intended for lock/boundary semantics.

## Waiting and Locking

- `wait_extent_bit()` waits for one or more bits to clear in a range, using per-state wait queues and keeping a referenced failed/cached state while sleeping.
- `btrfs_try_lock_extent_bits()` attempts to set lock bits without waiting. If it partially locked a prefix before an existing lock, it clears that prefix and returns false.
- `btrfs_lock_extent_bits()` sets lock bits and waits/retries on `-EEXIST`, clearing any partial prefix before waiting.
- `btrfs_next_extent_state()` returns a referenced next state for contexts where no concurrent tree modification is expected.

## Query Operations

- `btrfs_find_first_extent_bit()` finds the first state with any requested bit set at or after a start offset and can cache the found state for repeated iteration.
- `btrfs_find_contiguous_extent_bit()` finds the full contiguous range covered by states with given bits, used when temporary splits may hide the true contiguous extent.
- `btrfs_find_delalloc_range()` finds a contiguous delalloc range up to `max_bytes`, stopping at holes or `EXTENT_BOUNDARY`.
- `btrfs_find_first_clear_extent_bit()` returns the first range at or after a start offset where requested bits are not set, treating holes as clear ranges and using `-1` as open-ended end.
- `btrfs_count_range_bits()` counts bytes in a range where all requested bits are set, optionally requiring contiguity and supporting cached state reuse.
- `btrfs_test_range_bit_exists()` tests whether a single bit exists anywhere in a range.
- `btrfs_get_range_bits()` ORs together all state bits found in a range and caches the first state.
- `btrfs_test_range_bit()` tests whether a half-open range `[start, end)` is continuously covered by states with a single bit set.

## Lifecycle

- `btrfs_extent_io_tree_init()` initializes an empty tree, lock, owner, and fs_info/inode pointer.
- `btrfs_extent_io_tree_release()` empties a tree after callers guarantee no concurrent access, asserts no lock bits or waiters, clears rb nodes, frees states, and verifies the tree stayed empty.

## Concurrency and Error Handling

- `tree->lock` protects all rb-tree mutations, state bits, wait queue enrollment/removal, and cached-state validity checks.
- Potentially blocking allocations are done outside the spinlock, with atomic allocation attempts inside locked sections and retry paths when allocation fails.
- `cond_resched_lock()` and explicit search retries avoid long lock holds over large trees.
- Structural inconsistencies in insert/split/changeset handling call `extent_io_tree_panic()`, which maps the tree back to `fs_info` for a Btrfs panic.

## Dependencies

Uses Linux slab, rb-tree, spinlock, waitqueue, refcount, and Btrfs tracepoints. It integrates with Btrfs inode delalloc accounting, extent changesets, and the broader extent I/O layer.

## Research Notes

This file is the generic range-state engine behind many Btrfs byte-range operations. The implementation is careful about three competing constraints: preserving exact range state through splits, keeping the tree compact through merging, and supporting lock-like bits that require wait/wakeup semantics and cannot be freely merged with ordinary dirty/delalloc state.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/extent-io-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/extent-io-tree.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/extent-io-tree.h

## Role

Defines Btrfs extent I/O tree state bits, owners, core data structures, and public APIs for range state tracking, locking, state transitions, and queries.

## State Bits

The extent-state bit enum includes:

- Dirty/writeback-related state: `EXTENT_DIRTY`.
- Locking state: `EXTENT_LOCKED`, `EXTENT_DIO_LOCKED`.
- Tree-log dirty tracking: `EXTENT_DIRTY_LOG1`, `EXTENT_DIRTY_LOG2`.
- Delalloc and writeback accounting: `EXTENT_DELALLOC`, `EXTENT_DELALLOC_NEW`, `EXTENT_ADD_INODE_BYTES`.
- Defrag and boundary markers: `EXTENT_DEFRAG`, `EXTENT_BOUNDARY`.
- Data checksum/reservation/accounting flags: `EXTENT_NODATASUM`, `EXTENT_CLEAR_META_RESV`, `EXTENT_NORESERVE`, `EXTENT_QGROUP_RESERVED`, `EXTENT_CLEAR_DATA_RESV`.
- Wait and ordered-completion flags: `EXTENT_NEED_WAIT`, `EXTENT_FINISHING_ORDERED`.
- Control-only flags: `EXTENT_CLEAR_ALL_BITS` and `EXTENT_NOWAIT`.

Derived masks:

- `EXTENT_DO_ACCOUNTING` combines metadata/data reservation clear bits.
- `EXTENT_CTLBITS` identifies control bits that are not persisted as normal state.
- `EXTENT_LOCK_BITS` combines regular and direct-I/O range locks.

## Device Allocation Aliases

The header reuses extent-state bits for device allocation trees:

- `CHUNK_ALLOCATED` maps to `EXTENT_DIRTY`.
- `CHUNK_TRIMMED` maps to `EXTENT_DEFRAG`.
- `CHUNK_STATE_MASK` covers both. The comment warns that lock/boundary/accounting bits are avoided because bit manipulation functions attach special behavior to them.

## Tree Owners

Owner IDs identify the semantic owner of each extent I/O tree:

- Filesystem-wide pinned and excluded extents.
- Btree inode I/O and regular inode I/O.
- Relocation blocks.
- Transaction dirty pages.
- Root dirty log pages.
- Inode file extents.
- Log checksum ranges.
- Selftests.
- Device allocation state.

The owner determines whether the tree's union pointer is interpreted as `fs_info` or `inode`, and whether inode delalloc accounting hooks run.

## Data Structures

- `struct extent_io_tree` contains the rb-root, owner union (`fs_info` or `inode`), owner byte, and spinlock.
- `struct extent_state` contains inclusive range start/end, rb-node, wait queue, refcount, state bitmask, and optional debug leak-list linkage.

## API Surface

- Tree lifecycle and mapping: `btrfs_extent_io_tree_init()`, `btrfs_extent_io_tree_release()`, `btrfs_extent_io_tree_to_inode()`, `btrfs_extent_io_tree_to_fs_info()`.
- Cache lifecycle: `btrfs_extent_state_init_cachep()`, `btrfs_extent_state_free_cachep()`, `btrfs_free_extent_state()`.
- Locking: `btrfs_lock_extent_bits()`, `btrfs_try_lock_extent_bits()`, inline regular lock/unlock helpers, and inline DIO lock/unlock helpers.
- Counting and testing: `btrfs_count_range_bits()`, `btrfs_test_range_bit()`, `btrfs_test_range_bit_exists()`, `btrfs_get_range_bits()`.
- Setting/clearing/converting: `btrfs_set_extent_bit()`, `btrfs_set_record_extent_bits()`, `btrfs_clear_extent_bit_changeset()`, inline `btrfs_clear_extent_bit()`, `btrfs_clear_record_extent_bits()`, inline `btrfs_clear_extent_dirty()`, and `btrfs_convert_extent_bit()`.
- Searching: `btrfs_find_first_extent_bit()`, `btrfs_find_first_clear_extent_bit()`, `btrfs_find_contiguous_extent_bit()`, `btrfs_find_delalloc_range()`.
- Iteration: `btrfs_next_extent_state()`.

## Research Notes

This header is the contract for a reusable Btrfs range-state abstraction. The state bit definitions encode both ordinary extent state and command/control behavior, so callers must be careful to use the right helper: lock bits imply exclusivity and wait queues, accounting bits trigger inode/block reservation side effects, and `EXTENT_NOWAIT` changes allocation behavior rather than becoming persistent state.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/extent-io-tree.h -->