# Group Research: group_945_linux_stable_sources_os_linux_linux_stable_fs_btrfs_discard_c_source_80d9f5b74332

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/discard.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/discard.c

## Purpose
Implements Btrfs asynchronous discard for data-only block groups. It queues free-space trim work outside transaction commit, prioritizes recently freed large extents before bitmap-backed ranges, rate-limits discard IO, and handles fully free block groups before they enter the normal unused block group deletion path.

## Main State And Policy
- Uses `fs_info->discard_ctl` as the controller: delayed work, ordered discard workqueue, per-list queues, current running block group, byte/IOPS limits, previous discard timing, and aggregate discardable counters.
- Maintains `BTRFS_NR_DISCARD_LISTS` queues. Index `BTRFS_DISCARD_INDEX_UNUSED` is special for empty block groups; normal lists use decreasing minimum-size filters: no filter, `BTRFS_ASYNC_DISCARD_MAX_FILTER`, and `BTRFS_ASYNC_DISCARD_MIN_FILTER`.
- Only queues data-only block groups. Mixed block groups are explicitly excluded.
- Treats an empty remapped block group differently: `BTRFS_BLOCK_GROUP_REMAPPED` uses `identity_remap_count == 0`; otherwise emptiness means `used == 0 && remap_bytes == 0`.

## Key Flows
- `btrfs_discard_queue_work()` is the external enqueue path. It checks `DISCARD_ASYNC`, sends empty groups to `add_to_discard_unused_list()`, non-empty groups to `add_to_discard_list()`, and schedules delayed work if needed.
- `btrfs_discard_workfn()` is the worker. It picks an eligible block group with `peek_discard_list()`, verifies discard is still enabled and due, runs one trim segment, updates pass state, stores `prev_discard` and `prev_discard_time`, drops its temporary reference, and schedules the next run.
- `peek_discard_list()` selects work, repairs state transitions for block groups that changed while queued, initializes the cursor on `BTRFS_DISCARD_RESET_CURSOR`, and records a stable `discard_state`/`discard_index` snapshot for the current worker pass.
- The worker does two normal passes: `BTRFS_DISCARD_EXTENTS` via `btrfs_trim_block_group_extents()`, then `BTRFS_DISCARD_BITMAPS` via `btrfs_trim_block_group_bitmaps()`. A fully remapped empty block group uses `btrfs_trim_fully_remapped_block_group()`.
- `btrfs_finish_discard_pass()` removes a completed block group from discard queues, marks fully trimmed empty groups unused via `btrfs_mark_bg_unused()`, requeues untrimmed empty groups on the unused discard list, or advances non-empty groups through the filter lists.
- `btrfs_discard_punt_unused_bgs_list()` moves existing `fs_info->unused_bgs` entries into the async discard path when async discard is enabled, preserving reference ownership.
- `btrfs_discard_resume()`, `btrfs_discard_stop()`, `btrfs_discard_init()`, and `btrfs_discard_cleanup()` provide lifecycle integration for mount/remount/unmount.

## Scheduling And Rate Limiting
- `btrfs_discard_schedule_work()` wraps `__btrfs_discard_schedule_work()` under `discard_ctl->lock`.
- Scheduling delay is the max of the base `delay_ms`, byte-rate delay derived from `kbps_limit` and `prev_discard`, and block-group `discard_eligible_time`.
- `override` lets transaction-commit recalculation adjust the timer while accounting for elapsed time since the previous discard.
- `btrfs_discard_calc_delay()` derives `delay_ms` from `iops_limit`, clamped between 0/1 ms and 1000 ms. It also corrects negative aggregate discardable counters defensively.

## Counters And Accounting
- `btrfs_discard_update_discardable()` propagates per-block-group free-space-cache discardable extent/byte deltas into global atomic counters. It requires the free-space controller tree lock.
- Worker counters distinguish extent-pass bytes (`discard_extent_bytes`) from bitmap-pass bytes (`discard_bitmap_bytes`).
- `discard_bytes_saved` is initialized here but updated elsewhere.

## Concurrency And Lifetime
- Queue membership and `discard_ctl->block_group` are protected by `discard_ctl->lock`.
- Queued block groups hold references via `btrfs_get_block_group()` and release them on removal/purge.
- `btrfs_discard_cancel_work()` removes a block group and, if it was the active one, synchronously cancels the delayed work before rescheduling.
- `btrfs_discard_cleanup()` stops discard, cancels pending delayed work synchronously, and purges all discard lists.
- `btrfs_discard_purge_list()` deliberately drops `discard_ctl->lock` while calling `btrfs_mark_bg_unused()` to avoid doing heavier work under the spinlock.

## Important Dependencies
- Free-space trimming and state: `btrfs_trim_block_group_extents()`, `btrfs_trim_block_group_bitmaps()`, `btrfs_is_free_space_trimmed()`.
- Block group lifecycle: `btrfs_mark_bg_unused()`, `btrfs_get_block_group()`, `btrfs_put_block_group()`.
- Mount/unmount integration: `disk-io.c` initializes discard state, creates/destroys the discard workqueue, resumes discard after writable mount setup, and calls cleanup during close.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/discard.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/discard.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/discard.h

## Purpose
Declares the public async discard interface for Btrfs and defines discard size thresholds used by `discard.c`.

## Constants
- `BTRFS_ASYNC_DISCARD_DEFAULT_MAX_SIZE`: default max discard size, `64M`.
- `BTRFS_ASYNC_DISCARD_MAX_FILTER`: upper list filter, `1M`.
- `BTRFS_ASYNC_DISCARD_MIN_FILTER`: lower list filter, `32K`.

## Exported Operations
- Queue/list operations: `btrfs_discard_check_filter()`.
- Work operations: `btrfs_discard_cancel_work()`, `btrfs_discard_queue_work()`, `btrfs_discard_schedule_work()`.
- Counter/delay updates: `btrfs_discard_calc_delay()`, `btrfs_discard_update_discardable()`.
- Lifecycle: `btrfs_discard_punt_unused_bgs_list()`, `btrfs_discard_resume()`, `btrfs_discard_stop()`, `btrfs_discard_init()`, `btrfs_discard_cleanup()`.

## Dependencies
Forward-declares `btrfs_fs_info`, `btrfs_discard_ctl`, and `btrfs_block_group`; includes only Linux type/size headers. This keeps discard users from needing the full implementation unless they already require Btrfs internals.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/discard.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/disk-io.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/disk-io.c

## Purpose
Central Btrfs mount, metadata IO, root management, superblock write, transaction cleanup, and unmount implementation. This file wires together filesystem startup and teardown with tree-block validation, root caches, worker queues, feature checks, log replay, block-group loading, discard lifecycle, and final error cleanup.

## Metadata Block IO And Validation
- `csum_tree_block()` computes metadata block checksums over an extent buffer, handling contiguous and multi-folio buffers.
- `btrfs_buffer_uptodate()` validates cached extent buffers against parent transid and optional parent/key/owner checks.
- `btrfs_read_extent_buffer()` reads metadata, retries alternate mirrors on failure, and repairs failed mirror reads with `btrfs_repair_eb_io_failure()` when possible.
- `btree_csum_one_bio()` verifies dirty metadata before write: block address, uptodate state, fsid, structural tree checker result, and generation newer than last committed. It writes the checksum only after validation.
- `btrfs_validate_extent_buffer()` performs read-time validation: bytenr, fsid/metadata UUID, level, checksum unless ignored, parent transid, first key, owner root, and leaf/node checker.

## Address-Space And Extent Buffer Integration
- Defines `btree_aops` for the btree inode: `btree_writepages`, folio release, invalidation, migration, and debug dirty-folio checking.
- `btrfs_find_create_tree_block()` allocates normal or test extent buffers.
- `read_tree_block()` allocates/looks up an extent buffer and reads it with strict parent checks.

## Root Allocation, Caching, And Lookup
- `btrfs_alloc_root()` initializes `struct btrfs_root`: xarrays, reservations, lists, locks, log state, qgroup state, refcount, and debug leak tracking.
- Global roots are stored in `fs_info->global_root_tree` with `btrfs_global_root_insert()`, `btrfs_global_root_delete()`, and `btrfs_global_root()`.
- `btrfs_global_root_id()` maps bytenr to a global-root index for extent-tree-v2 via block-group `global_root_id`.
- `btrfs_csum_root()` and `btrfs_extent_root()` select global checksum/extent roots for a bytenr.
- `btrfs_create_tree()` creates a new on-disk tree root item and initializes its first leaf.
- Log trees are allocated by `alloc_log_tree()`, `btrfs_alloc_log_tree_node()`, `btrfs_init_log_root_tree()`, and `btrfs_add_log_tree()`.
- `read_tree_root_path()` and `btrfs_read_tree_root()` read root items from the tree root, validate their root nodes, and enforce owner consistency for normal roots.
- `btrfs_get_fs_root()`, `btrfs_get_new_fs_root()`, and `btrfs_get_fs_root_commit_root()` serve cached/global/subvolume roots with reference management and anon-bdev setup for exposed subvolumes.
- `btrfs_put_root()`, `btrfs_drop_and_free_fs_root()`, `btrfs_free_fs_roots()`, and `btrfs_free_fs_info()` release root and fs-wide resources.

## Mount-Time Threads And Workers
- `cleaner_kthread()` runs delayed iputs, deleted snapshot cleanup, defrag, fully remapped block group handling when async discard is off, unused block group deletion, and block group reclaim.
- `transaction_kthread()` periodically commits the running transaction based on commit interval or explicit commit requests.
- `btrfs_init_workqueues()` creates Btrfs worker pools, including the ordered `btrfs-discard` workqueue stored in `fs_info->discard_ctl.discard_workers`.
- `btrfs_stop_all_workers()` destroys all worker queues, including discard, after higher-level users have been stopped.

## Superblock And Root Loading
- `btrfs_check_super_csum()` validates superblock checksum after checksum type has been established.
- `btrfs_validate_super()` checks magic, flags, levels, sector/node size, alignment, fsid/metadata UUID, feature dependencies, remap-tree constraints, bytes-used sanity, stripesize, device count, super offset, system chunk array, and generation warnings.
- `validate_sys_chunk_array()` parses and validates the embedded system chunk array.
- Backup root handling is implemented by `find_newest_super_backup()`, `backup_super_roots()`, and `read_backup_root()`.
- `load_super_root()`, `load_important_roots()`, `load_global_roots_objectid()`, `load_global_roots()`, `btrfs_read_roots()`, and `init_tree_roots()` load tree, chunk, remap, extent, checksum, free-space, block-group, device, relocation, quota, UUID, stripe, and other roots with backup-root fallback when requested.

## Filesystem Initialization
- `btrfs_init_fs_info()` initializes nearly all in-memory fs-wide state: radix/xarray/rbtree roots, locks, waitqueues, transaction state, reservations, reclaim state, scrub/balance/qgroup/dev-replace state, extent IO trees, defaults, and async discard state via `btrfs_discard_init()`.
- `init_mount_fs_info()` binds the superblock, initializes percpu counters, delayed root, read-only/error state bits, and stripe hash table.
- `open_ctree()` is the main mount path:
  - Initializes `fs_info`, root objects, btree inode, superblock checksum and validation.
  - Sets sector/node/checksum sizes, mount options, feature flags, compression workspaces, and workers.
  - Reads system array, chunk root/tree, device and zone information, tree roots, block groups, sysfs, space info, qgroups, and logs.
  - Replays the tree log unless disabled, reads the default fs tree, runs writable mount setup, resumes async discard with `btrfs_discard_resume()`, checks UUID tree, marks the filesystem open, and wakes cleaner for unfinished drops.
  - Has structured failure labels that unwind workers, sysfs, block groups, roots, mappings, and btree inode state.

## Writable Mount Preparation
`btrfs_start_pre_rw_mount()` handles read-write-only setup:
- Rebuilds, deletes, or creates the free-space tree based on options and on-disk validity.
- Deletes orphan free-space tree entries from older mkfs behavior.
- Finds orphan roots before orphan cleanup to preserve pending deleted-root semantics.
- Cleans orphan items, recovers relocation, resumes balance/dev-replace/qgroup rescan, toggles v1 space cache, and creates UUID tree if missing.

## Feature Checks
`btrfs_check_features()` rejects unknown incompat features, unsupported read-write compat_ro features, dirty log replay with unsupported compat_ro features, mixed block groups with unequal sectorsize/nodesize, block-group-tree without required no-holes/free-space-tree settings, and v1 space cache on unsupported subpage configurations. It also normalizes always-on or implied incompat flags in the super copy.

## Superblock Writes And Barriers
- `write_dev_supers()` writes one or more superblock mirrors per writable metadata device using direct bios and FUA for the primary mirror unless barriers are disabled.
- `wait_dev_supers()` waits for submitted super writes and treats primary-super failure specially.
- `write_dev_flush()`, `wait_dev_flush()`, and `barrier_all_devices()` submit and collect device flushes, checking degradability after errors.
- `write_all_supers()` prepares backup roots, updates per-device `dev_item`, validates the superblock before each write, submits all device super writes, waits for them, and aborts the transaction if error tolerance is exceeded.

## Unmount And Error Cleanup
- `close_ctree()` performs ordered shutdown: set closing state, wake unfinished drops, stop reclaim, park cleaner, wait qgroup/UUID/scrub/defrag, handle error commit cleanup, flush all workqueues that can create delayed iputs or ordered extents, cancel reclaim/shrinker work, disable delayed iputs, cleanup discard with `btrfs_discard_cleanup()`, delete unused block groups, commit final super if needed, stop kthreads, free qgroups/sysfs/block groups/roots/workers/mapping tree, and release the btree inode.
- `btrfs_error_commit_super()` invokes transaction cleanup under cleanup-work synchronization for errored filesystems.
- `btrfs_cleanup_transaction()` cleans all non-committed transactions, ordered extents, delayed inodes, delalloc inodes, logs, and qgroup per-transaction reservations.
- `btrfs_cleanup_one_transaction()` cleans dirty block groups, delayed refs, dirty metadata extent states, pinned extents, and wakes transaction waiters.
- `btrfs_cleanup_dirty_bgs()` marks dirty block group cache IO as errored and releases references.
- `btrfs_destroy_marked_extents()` and `btrfs_destroy_pinned_extent()` use `extent-io-tree.c` helpers to clear dirty/pinned state and release extent buffers or unpin extents.

## Object ID Management
- `btrfs_init_root_free_objectid()` searches the root for the highest valid objectid and initializes `root->free_objectid`.
- `btrfs_get_free_objectid()` allocates monotonically increasing objectids under `root->objectid_mutex`, returning `-ENOSPC` at the upper limit.

## Relationship To This Group
- Owns discard subsystem initialization, workqueue allocation/destruction, mount resume, and unmount cleanup.
- Uses extent IO trees for dirty transaction pages, pinned extents, btree inode IO, root log dirty pages, and cleanup iteration.
- Supplies root lookup used by export support through `btrfs_get_fs_root()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/disk-io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/disk-io.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/disk-io.h

## Purpose
Public declarations for Btrfs disk IO, mount/unmount, root lookup/lifetime, metadata buffer validation, log tree setup, transaction cleanup, superblock writes, and objectid allocation.

## Constants And Inline Helpers
- `BTRFS_SUPER_MIRROR_MAX`: three superblock mirrors.
- `BTRFS_SUPER_MIRROR_SHIFT`: shift used for backup superblock offsets.
- `BTRFS_BDEV_BLOCKSIZE`: fixed 4096-byte block size for superblock-style metadata reads.
- `btrfs_sb_offset()` maps mirror index to its logical superblock location.

## Declared Interfaces
- Mount lifecycle: `open_ctree()`, `close_ctree()`, `btrfs_start_pre_rw_mount()`.
- Superblock handling: `btrfs_check_super_csum()`, `btrfs_validate_super()`, `btrfs_check_features()`, `write_all_supers()`, `btrfs_commit_super()`.
- Root management: `btrfs_read_tree_root()`, `btrfs_insert_fs_root()`, `btrfs_free_fs_roots()`, `btrfs_get_fs_root()`, `btrfs_get_new_fs_root()`, `btrfs_get_fs_root_commit_root()`, global root insert/delete/lookup, csum/extent-root selectors, `btrfs_drop_and_free_fs_root()`, `btrfs_put_root()`.
- Metadata buffers: `read_tree_block()`, `btrfs_find_create_tree_block()`, `btrfs_validate_extent_buffer()`, `btrfs_buffer_uptodate()`, `btrfs_read_extent_buffer()`, `btree_csum_one_bio()`, `btrfs_mark_buffer_dirty()`.
- Log trees: `btrfs_alloc_log_tree_node()`, `btrfs_init_log_root_tree()`, `btrfs_add_log_tree()`.
- Cleanup: `btrfs_cleanup_dirty_bgs()`, `btrfs_cleanup_one_transaction()`.
- Miscellaneous: dirty metadata throttling, tolerated barrier failures, free objectid initialization/allocation.

## Inline Lifetime Helper
`btrfs_grab_root()` safely increments a root refcount only if non-zero, allowing lookup paths to avoid racing with root teardown.

## Compile-Time Conditional
`btrfs_alloc_dummy_root()` is declared only under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/disk-io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/export.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/export.c

## Purpose
Implements Btrfs export operations for file handles, primarily for NFS/exportfs. It encodes inode/root/generation identity into file handles and reconstructs dentries or parent dentries across subvolume boundaries.

## File Handle Encoding
- `btrfs_encode_fh()` fills a packed `struct btrfs_fid`.
- Always records inode objectid, containing root objectid, and inode generation.
- If a parent is supplied, records parent objectid and generation.
- If parent and child live in different roots, records `parent_root_objectid` and returns `FILEID_BTRFS_WITH_PARENT_ROOT`.
- Supports three handle layouts:
  - `FILEID_BTRFS_WITHOUT_PARENT`
  - `FILEID_BTRFS_WITH_PARENT`
  - `FILEID_BTRFS_WITH_PARENT_ROOT`
- Returns `FILEID_INVALID` with the required `max_len` when the caller’s buffer is too small.

## Dentry Reconstruction
- `btrfs_get_dentry()` rejects internal objectids below `BTRFS_FIRST_FREE_OBJECTID`, gets the target root with `btrfs_get_fs_root()`, loads the inode with `btrfs_iget()`, verifies generation when non-zero, and returns `d_obtain_alias()`.
- `btrfs_fh_to_dentry()` validates file handle type/length and resolves the encoded inode.
- `btrfs_fh_to_parent()` validates parent-capable handle types and resolves either the child root or explicit parent root depending on handle type.

## Parent And Name Lookup
- `btrfs_get_parent()` finds the parent of a dentry by looking up the previous matching backref item:
  - For a subvolume root inode (`BTRFS_FIRST_FREE_OBJECTID`), it searches the tree root for `BTRFS_ROOT_BACKREF_KEY`.
  - For normal inodes, it searches the subvolume root for `BTRFS_INODE_REF_KEY`.
  - It then returns the parent dentry, crossing roots when needed.
- `btrfs_get_name()` returns a child name under a parent:
  - Validates that the parent is a directory.
  - Uses `BTRFS_ROOT_BACKREF_KEY` for subvolume roots and `BTRFS_INODE_REF_KEY` for normal inodes.
  - Reads the name payload from the leaf into the exportfs buffer and null terminates it.

## Export Operations
`btrfs_export_ops` wires Btrfs into exportfs:
- `.encode_fh = btrfs_encode_fh`
- `.fh_to_dentry = btrfs_fh_to_dentry`
- `.fh_to_parent = btrfs_fh_to_parent`
- `.get_parent = btrfs_get_parent`
- `.get_name = btrfs_get_name`

## Dependencies
Uses root lookup and inode loading from `disk-io.c`/inode code, B-tree search via `btrfs_search_slot()`, and accessor helpers for inode/root backref items.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/export.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/export.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/export.h

## Purpose
Defines Btrfs exportfs public types and declarations.

## Main Types
- Declares `btrfs_export_ops`, the `struct export_operations` instance implemented by `export.c`.
- Defines packed `struct btrfs_fid`, containing:
  - child `objectid`
  - child `root_objectid`
  - child generation
  - parent `objectid`
  - parent generation
  - optional `parent_root_objectid` for cross-subvolume file handles

## Exported Helpers
- `btrfs_get_dentry()` resolves an objectid/root/generation tuple to a dentry.
- `btrfs_get_parent()` resolves a dentry’s parent for exportfs path reconnection.

## Dependency Shape
Includes only exportfs/types headers and forward-declares `dentry` and `super_block`, keeping the header lightweight for users that only need export operation declarations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/export.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/extent-io-tree.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/extent-io-tree.c

## Purpose
Implements Btrfs extent state trees: rbtrees of byte ranges tagged with state bits such as dirty, locked, delalloc, qgroup-reserved, device allocated/trimmed, and related control flags. These trees are used by inode IO, btree metadata IO, transaction dirty page tracking, pinned extents, excluded extents, log ranges, relocation, and device allocation state.

## Core Model
- Each `extent_io_tree` owns an rb-tree of non-overlapping `extent_state` records.
- Each `extent_state` covers an inclusive `[start, end]` range and has a bitmask, waitqueue, refcount, and rb node.
- Adjacent states with identical mergeable state are coalesced. States with lock bits or `EXTENT_BOUNDARY` are not merged.
- Inode-owned trees call delalloc accounting hooks when states are set, cleared, split, or merged.

## Allocation And Lifetime
- Uses a slab cache `extent_state_cache`.
- `btrfs_extent_state_init_cachep()` creates the cache; `btrfs_extent_state_free_cachep()` checks debug leaks and destroys it.
- `alloc_extent_state()` initializes rb node, waitqueue, refcount, debug tracking, and tracing.
- `btrfs_free_extent_state()` decrements refs and frees only when the state is no longer referenced.
- Debug builds maintain a global leak list and validate suspicious inode IO ranges.
- `btrfs_extent_io_tree_init()` initializes an empty tree, lock, owner, and fs/inode pointer.
- `btrfs_extent_io_tree_release()` empties a tree after all external access has stopped; it asserts no lock bits and no waiters remain.

## Search And Tree Helpers
- `tree_search_for_insert()` finds the state containing an offset or the next state after it, and can return rb insert parent/link pointers.
- `tree_search_prev_next()` finds containing, previous, and next states for clear-range discovery.
- `next_state()` and `prev_state()` wrap rb traversal.
- `merge_prev_state()`, `merge_next_state()`, and `merge_state()` coalesce compatible adjacent ranges.
- `split_state()` splits an existing state at a byte offset using a preallocated state for one side.

## Setting Bits
- `set_extent_bit()` is the internal range setter used by most public set/lock APIs.
- It handles holes, exact matches, leading splits, trailing splits, insertion, merging, cached states, NOWAIT allocation semantics, and exclusive lock-bit conflicts.
- `btrfs_set_extent_bit()` is the basic public setter.
- `btrfs_set_record_extent_bits()` sets bits while recording changed byte counts/ranges in an `extent_changeset`; lock bits are intentionally unsupported for this wrapper.
- `set_state_bits()` strips control bits before setting state and performs inode delalloc accounting plus changeset accounting.

## Clearing Bits
- `btrfs_clear_extent_bit_changeset()` clears a bit range, splitting states when needed, deleting empty states, waking lock waiters, merging remaining states, handling `EXTENT_CLEAR_ALL_BITS`, and optionally recording changes.
- `btrfs_clear_record_extent_bits()` is the changeset-recording clear wrapper.
- `clear_state_bit()` performs the per-state clear, wakeup, deletion/merge, and next-state selection.
- If `EXTENT_DELALLOC` is cleared, `EXTENT_NORESERVE` is also included for accounting consistency.

## Locking Semantics
- `btrfs_try_lock_extent_bits()` attempts to set lock bits; on conflict it clears any partial lock already taken and returns false.
- `btrfs_lock_extent_bits()` loops until it can set the requested lock bits, waiting via `wait_extent_bit()` when another state already has those exclusive bits.
- `wait_extent_bit()` attaches to the state waitqueue under the tree lock, sleeps uninterruptibly, and retries after wakeup.
- Lock waiters are woken by `state_wake_up()` when `EXTENT_LOCKED` or `EXTENT_DIO_LOCKED` bits are cleared.

## Conversion And Queries
- `btrfs_convert_extent_bit()` atomically sets one set of bits and clears another across a range, intended only for mergeable states such as delalloc-to-dirty conversion.
- `btrfs_find_first_extent_bit()` finds the first state with any requested bit and supports cached iteration.
- `btrfs_find_contiguous_extent_bit()` returns the full contiguous area covered by a bit, used when temporary splitting may hide real contiguity.
- `btrfs_find_delalloc_range()` finds a contiguous delalloc range up to `max_bytes`, stopping at boundaries or non-delalloc states.
- `btrfs_find_first_clear_extent_bit()` finds the first range lacking requested bits, treating holes as clear.
- `btrfs_count_range_bits()` counts bytes that have all requested bits, optionally requiring contiguity and supporting cached state.
- `btrfs_test_range_bit_exists()` checks if a single bit exists anywhere in a range.
- `btrfs_get_range_bits()` ORs all bits present across a range and caches the first state.
- `btrfs_test_range_bit()` verifies that a whole half-open range is continuously covered by a single bit.
- `btrfs_next_extent_state()` returns a referenced next state for contexts where concurrent modification is known not to happen.

## Changeset Accounting
`add_extent_changeset()` increments `bytes_changed` and optionally records changed ranges in a ulist. It avoids counting no-op set/clear operations and panics through `extent_io_tree_panic()` if changeset insertion fails in paths that cannot safely recover.

## Concurrency And Allocation Strategy
- All tree mutation and lookup happen under `tree->lock`.
- Range operations preallocate extent states before locking when possible, retry after dropping the lock if atomic allocation fails, and reschedule on long scans.
- `EXTENT_NOWAIT` switches allocation to `GFP_NOWAIT`; otherwise operations use `GFP_NOFS`.
- Cached-state pointers are reference-counted and freed/replaced carefully to avoid repeated tree searches across adjacent operations.

## Relationship To Other Files
- `disk-io.c` uses these helpers to track and clean transaction dirty pages and pinned extents during transaction abort and unmount.
- Inode and writeback paths use lock/delalloc/dirty state management for page and ordered extent coordination.
- Device allocation code aliases `EXTENT_DIRTY` and `EXTENT_DEFRAG` as chunk allocation/trim state bits through the header.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/extent-io-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/extent-io-tree.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/extent-io-tree.h

## Purpose
Declares Btrfs extent IO tree data structures, state bits, owner IDs, and public APIs for range state tracking.

## State Bits
Defines range-state bits including:
- IO/writeback state: `EXTENT_DIRTY`, `EXTENT_LOCKED`, `EXTENT_DIO_LOCKED`.
- Logging and delalloc state: `EXTENT_DIRTY_LOG1`, `EXTENT_DIRTY_LOG2`, `EXTENT_DELALLOC`, `EXTENT_DELALLOC_NEW`.
- Range modifiers/accounting: `EXTENT_BOUNDARY`, `EXTENT_NODATASUM`, `EXTENT_NORESERVE`, `EXTENT_QGROUP_RESERVED`.
- Reservation cleanup/control: `EXTENT_CLEAR_META_RESV`, `EXTENT_CLEAR_DATA_RESV`, `EXTENT_ADD_INODE_BYTES`, `EXTENT_CLEAR_ALL_BITS`.
- Ordered completion marker: `EXTENT_FINISHING_ORDERED`.
- Allocation behavior control: `EXTENT_NOWAIT`, which must remain last and is masked out before storing state.

## Bit Masks And Aliases
- `EXTENT_DO_ACCOUNTING`: reservation cleanup bits.
- `EXTENT_CTLBITS`: control bits not stored as persistent extent state.
- `EXTENT_LOCK_BITS`: lock-bit group.
- Device allocation tree aliases:
  - `CHUNK_ALLOCATED = EXTENT_DIRTY`
  - `CHUNK_TRIMMED = EXTENT_DEFRAG`
  - `CHUNK_STATE_MASK` combines both.

## Tree Owners
Enumerates owner IDs for pinned extents, excluded extents, btree inode IO, inode IO, relocation blocks, transaction dirty pages, root log dirty pages, inode file extents, log checksum ranges, selftests, and device allocation state.

## Main Structures
- `struct extent_io_tree`: rb root, owner tag, spinlock, and union of `fs_info`/`inode` depending on owner.
- `struct extent_state`: inclusive start/end, rb node, waitqueue, refcount, state bits, and optional debug leak-list node.

## Public APIs
- Initialization/release: `btrfs_extent_io_tree_init()`, `btrfs_extent_io_tree_release()`, slab cache init/free.
- Locking: `btrfs_lock_extent_bits()`, `btrfs_try_lock_extent_bits()`, inline normal and DIO lock/unlock wrappers.
- Set/clear/convert: `btrfs_set_extent_bit()`, `btrfs_set_record_extent_bits()`, `btrfs_clear_extent_bit_changeset()`, inline `btrfs_clear_extent_bit()`, inline `btrfs_clear_extent_dirty()`, `btrfs_clear_record_extent_bits()`, `btrfs_convert_extent_bit()`.
- Queries/iteration: `btrfs_count_range_bits()`, `btrfs_test_range_bit()`, `btrfs_test_range_bit_exists()`, `btrfs_get_range_bits()`, `btrfs_find_first_extent_bit()`, `btrfs_find_first_clear_extent_bit()`, `btrfs_find_contiguous_extent_bit()`, `btrfs_find_delalloc_range()`, `btrfs_next_extent_state()`.
- Type conversion helpers: `btrfs_extent_io_tree_to_inode()`, `btrfs_extent_io_tree_to_fs_info()`.

## Notes
The header establishes the contract that many stored bits have semantic side effects in the implementation, especially lock bits, delalloc accounting bits, and control bits. Callers must use the wrappers rather than directly mutating tree state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/extent-io-tree.h -->