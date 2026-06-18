# Group Research: group_246_btrfs_linux_sources_local_fs_btrfs_linux_fs_btrfs_discard_c_sources__088fd5cf15c7

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/discard.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/discard.c

## Summary
Implements Btrfs asynchronous discard/trim scheduling for data-only block groups. It keeps discard work outside transaction commit by maintaining per-filesystem discard queues, rate limits, eligibility delays, and block-group cursor state.

## Main Responsibilities
- Queue free or fully-free data block groups for async discard.
- Prioritize discard passes by block-group recency and free-space size filters.
- Run a delayed ordered work item that trims one region at a time.
- Track discardable byte/extent counters from free-space cache state.
- Move fully discarded empty block groups to the normal unused block-group path.
- Initialize, resume, stop, and clean up async discard state.

## Key APIs
- `btrfs_discard_queue_work()`
- `btrfs_discard_cancel_work()`
- `btrfs_discard_schedule_work()`
- `btrfs_discard_check_filter()`
- `btrfs_discard_calc_delay()`
- `btrfs_discard_update_discardable()`
- `btrfs_discard_punt_unused_bgs_list()`
- `btrfs_discard_resume()`
- `btrfs_discard_stop()`
- `btrfs_discard_init()`
- `btrfs_discard_cleanup()`

## Important Behavior
Async discard uses multiple lists in `btrfs_discard_ctl`. Index `BTRFS_DISCARD_INDEX_UNUSED` handles fully free block groups before they are released to `unused_bgs`; the other lists perform progressively smaller trim filters using `discard_minlen`.

Newly queued block groups get an eligibility timestamp. Normal discard waits about 120 seconds to favor reuse, while unused block groups wait about 10 seconds. `find_next_block_group()` chooses the earliest eligible group across all lists.

Discard work has a pass-based state machine:
- `BTRFS_DISCARD_RESET_CURSOR` initializes the cursor to the block-group start.
- `BTRFS_DISCARD_EXTENTS` trims free-space extent entries first.
- `BTRFS_DISCARD_BITMAPS` trims bitmap-backed free space afterward.
- `BTRFS_DISCARD_FULLY_REMAPPED` handles empty remapped block groups specially.

The delayed work delay is the maximum of the base IOPS delay, byte-rate delay from the previous trim, and the selected block group's eligibility timeout. `btrfs_discard_calc_delay()` recomputes the base delay from `iops_limit`, clamped between 0/1 ms and 1000 ms.

`btrfs_discard_update_discardable()` propagates block-group free-space-cache deltas to global async discard counters while the free-space tree lock is held.

## State and Synchronization
`discard_ctl->lock` protects discard lists, current running block group, eligibility time, previous discard timing, and scheduling decisions. Queued block groups hold a block-group reference until removed.

The work function temporarily stores the active block group in `discard_ctl->block_group` so cancellation can detect a currently running trim, cancel the delayed work synchronously, and reschedule.

## Risks
Discard state depends on free-space-cache bitmap semantics and is intentionally approximate. Trimmed bitmap state can be reset and retrimmed after later allocation/free patterns.

Reference ownership is subtle: list insertion takes a block-group reference, removal drops it, and unused block-group punting drops the reference previously held by `btrfs_mark_bg_unused()`.

`peek_discard_list()` must avoid loops when an unused-list block group is no longer empty. The code explicitly asserts that a data-only block group moved out of the unused index actually changed index.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/discard.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/discard.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/discard.h

## Summary
Declares the Btrfs async discard interface and discard filter size constants.

## Main Contents
- Default max discard size: `BTRFS_ASYNC_DISCARD_DEFAULT_MAX_SIZE` at 64 MiB.
- High-size filter: `BTRFS_ASYNC_DISCARD_MAX_FILTER` at 1 MiB.
- Low-size filter: `BTRFS_ASYNC_DISCARD_MIN_FILTER` at 32 KiB.
- Public discard queue, schedule, accounting, lifecycle, and resume/stop function declarations.

## Key Interfaces
The header exposes queueing and cancellation (`btrfs_discard_queue_work()`, `btrfs_discard_cancel_work()`), scheduling (`btrfs_discard_schedule_work()`), accounting (`btrfs_discard_calc_delay()`, `btrfs_discard_update_discardable()`), and lifecycle operations (`btrfs_discard_init()`, `btrfs_discard_resume()`, `btrfs_discard_stop()`, `btrfs_discard_cleanup()`).

## Important Details
The header only forward-declares `btrfs_fs_info`, `btrfs_discard_ctl`, and `btrfs_block_group`, keeping discard internals private to implementation files and shared Btrfs structs.

## Risks
Callers must only use these helpers when async discard mount options and block-group type checks make sense. The implementation further rejects non-data-only or disabled-discard cases, but incorrect callers can still cause unnecessary scheduling attempts.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/discard.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/disk-io.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/disk-io.c

## Summary
Implements core Btrfs disk I/O, metadata block validation, root loading/caching, mount and unmount orchestration, superblock writing, background kthreads, workqueue setup, and transaction cleanup after errors.

## Main Responsibilities
- Validate and checksum metadata extent buffers and superblocks.
- Read tree blocks with mirror retry and repair failed mirror reads.
- Allocate, load, cache, reference, and free Btrfs roots.
- Initialize `btrfs_fs_info`, btree inode, worker pools, qgroup/scrub/balance/discard state.
- Execute the main mount flow in `open_ctree()`.
- Execute read-write mount preparation in `btrfs_start_pre_rw_mount()`.
- Write all superblock mirrors with barriers/FUA handling.
- Shut down the filesystem in `close_ctree()`.
- Clean up aborted or uncommitted transactions.

## Key APIs
- Metadata I/O: `read_tree_block()`, `btrfs_read_extent_buffer()`, `btrfs_validate_extent_buffer()`, `btree_csum_one_bio()`, `btrfs_buffer_uptodate()`.
- Superblock validation/writes: `btrfs_check_super_csum()`, `btrfs_validate_super()`, `write_all_supers()`, `btrfs_commit_super()`.
- Root management: `btrfs_read_tree_root()`, `btrfs_insert_fs_root()`, `btrfs_get_fs_root()`, `btrfs_get_new_fs_root()`, `btrfs_get_fs_root_commit_root()`, `btrfs_put_root()`, `btrfs_drop_and_free_fs_root()`, `btrfs_free_fs_roots()`.
- Global roots: `btrfs_global_root_insert()`, `btrfs_global_root_delete()`, `btrfs_global_root()`, `btrfs_csum_root()`, `btrfs_extent_root()`.
- Mount lifecycle: `btrfs_init_fs_info()`, `btrfs_start_pre_rw_mount()`, `open_ctree()`, `close_ctree()`.
- Dirty metadata: `btrfs_mark_buffer_dirty()`, `btrfs_btree_balance_dirty()`, `btrfs_btree_balance_dirty_nodelay()`.
- Transaction cleanup: `btrfs_cleanup_dirty_bgs()`, `btrfs_cleanup_one_transaction()`.

## Important Behavior
Metadata read validation checks bytenr, fsid/metadata UUID, tree level, checksum, parent transid, first key, owner root, and node/leaf structural consistency. Failed reads can retry alternate mirrors; successful retry after a failed mirror attempts metadata repair.

Write-time metadata checksum through `btree_csum_one_bio()` verifies the extent buffer bytenr, uptodate state, fsid, node/leaf structure, and generation relative to the last committed transaction before writing the checksum.

Root management distinguishes essential/global trees from subvolume roots. Global roots use an rb-tree keyed by root key, while subvolume roots are cached in `fs_roots_radix`. Extent tree v2 uses block-group `global_root_id` to select per-global extent and csum roots.

`open_ctree()` is the central mount sequence. It initializes counters and roots, reads and validates the primary superblock, parses features/options, initializes compression and workers, reads system chunks and chunk tree, loads important roots and all global roots, verifies devices and extents, initializes block groups, sysfs, qgroups, dev-replace, zoned mode, cleaner/transaction kthreads, log replay, fs root loading, read-write mount preparation, async discard resume, and UUID-tree checking.

`btrfs_start_pre_rw_mount()` handles rw-only preparation: free-space-tree rebuild/delete/create, orphan free-space cleanup, orphan root discovery, orphan cleanup, relocation recovery, balance/dev-replace resume, qgroup rescan resume, and UUID-tree creation.

Superblock writes use per-device direct bios rather than page-cache writeback. Transaction commits write all mirrors and update backup roots; fsync-like callers write only the primary mirror. Barriers are sent to all writable metadata devices first unless disabled. The primary superblock gets FUA when barriers are enabled.

`close_ctree()` is carefully ordered. It wakes unfinished drops, stops reclaim and parks cleaner, waits for qgroup/UUID/balance/dev-replace/scrub/defrag work, handles error commits, flushes workqueues that can create delayed iputs or ordered completions, runs delayed iputs, cancels reclaim and discard work, optionally commits the final superblock, stops kthreads, checks leaks/counters, removes sysfs, drops roots/block groups, invalidates btree inode pages, stops workers, and frees mapping state.

## State and Synchronization
Major state lives in `btrfs_fs_info`: roots, global root rb-tree, fs-root radix tree, transaction lists, block reservations, workqueues, block-group trees, delayed iputs, ordered roots, discard control, qgroup/scrub/balance/dev-replace state, sysfs state, and mount flags.

The cleaner kthread performs delayed iputs, deleted snapshot cleanup, defrag, fully remapped block-group handling, unused block-group deletion, and block-group reclaim. The transaction kthread commits based on interval or explicit commit requests and performs cleanup when the filesystem is aborted.

Locking spans spinlocks for radix/list state, rwlocks for global roots and tree-mod log, mutexes for transactions, cleaner, chunk, relocation, qgroup, block-group reclaim, and semaphores/rwsems for cleanup, commits, subvolumes, and UUID rescans.

## Risks
Mount error unwinding is high risk because each initialization phase has different ownership: roots, btree inode, worker pools, sysfs, block groups, mapping tree, devices, qgroups, and kthreads must be unwound in the right order.

Metadata validation is strict and central to corruption detection. Any missed check can admit bad tree blocks; any over-strict check can reject recoverable filesystems.

Unmount ordering is fragile because workqueues, ordered extents, delayed iputs, reclaim workers, and cleaner/transaction kthreads can wake or depend on each other.

Superblock writing must tolerate missing devices according to RAID/degradability rules while treating primary superblock failure specially.

Transaction cleanup forcibly errors ordered extents, destroys delayed refs/inodes, dirty metadata, pinned extents, block-group I/O state, and logs. Mistakes here can leak reservations or leave waiters blocked.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/disk-io.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/disk-io.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/disk-io.h

## Summary
Declares the public interface for Btrfs disk I/O, root management, superblock handling, mount lifecycle, metadata validation, log tree setup, and transaction cleanup.

## Main Contents
- Superblock mirror constants: `BTRFS_SUPER_MIRROR_MAX`, `BTRFS_SUPER_MIRROR_SHIFT`.
- Fixed block-device block size: `BTRFS_BDEV_BLOCKSIZE`.
- `btrfs_sb_offset()` helper for primary and backup superblock locations.
- Function declarations for mount/open/close, root lookup/loading, metadata reads, super writes, and cleanup.

## Key Interfaces
Important declarations include `open_ctree()`, `close_ctree()`, `btrfs_start_pre_rw_mount()`, `btrfs_validate_super()`, `btrfs_check_features()`, `write_all_supers()`, `btrfs_commit_super()`, `read_tree_block()`, `btrfs_validate_extent_buffer()`, `btrfs_read_extent_buffer()`, `btree_csum_one_bio()`, root lookup helpers, global root helpers, and transaction cleanup helpers.

## Important Details
`btrfs_sb_offset()` encodes Btrfs fixed superblock mirror placement: the primary uses `BTRFS_SUPER_INFO_OFFSET`, while mirrors shift from 16 KiB by `BTRFS_SUPER_MIRROR_SHIFT`.

`btrfs_grab_root()` is an inline reference helper that increments a root refcount only if nonzero, preventing resurrection after final put.

## Risks
Most declarations here expose lifetime-sensitive root and metadata-buffer APIs. Callers must pair returned roots with `btrfs_put_root()` and must pass correct parent-check data when reading tree blocks.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/disk-io.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/export.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/export.c

## Summary
Implements Btrfs exportfs/NFS file-handle encoding and decoding, including subvolume-aware parent lookup and name reconstruction.

## Main Responsibilities
- Encode Btrfs inode identity into export file handles.
- Include parent inode and parent root identity when a connectable handle is requested.
- Decode file handles back to dentries.
- Decode parent file handles.
- Locate a child’s parent dentry.
- Recover a child name under a parent for exportfs reconnect paths.

## Key APIs
- `btrfs_encode_fh()`
- `btrfs_get_dentry()`
- `btrfs_fh_to_dentry()`
- `btrfs_fh_to_parent()`
- `btrfs_get_parent()`
- `btrfs_get_name()`
- `btrfs_export_ops`

## Important Behavior
File handles store objectid, root objectid, and inode generation. Connectable handles additionally store parent objectid and parent generation. If the parent is in a different subvolume root, the handle also stores `parent_root_objectid` and uses the `FILEID_BTRFS_WITH_PARENT_ROOT` type.

`btrfs_get_dentry()` rejects objectids below `BTRFS_FIRST_FREE_OBJECTID`, obtains the requested root with `btrfs_get_fs_root()`, loads the inode with `btrfs_iget()`, verifies generation when provided, and returns an alias dentry.

`btrfs_get_parent()` handles two cases. For a subvolume root inode (`BTRFS_FIRST_FREE_OBJECTID`), it searches the tree root for a `BTRFS_ROOT_BACKREF_KEY`. For normal inodes, it searches the current root for the previous `BTRFS_INODE_REF_KEY`. It then returns either the parent directory inode in the same root or a dentry from the parent root.

`btrfs_get_name()` reconstructs the child name from either root backrefs or inode refs and writes a NUL terminator for exportfs path reconnect logic.

## State and Dependencies
The implementation depends on Btrfs root references, inode lookup, tree searches, inode refs, root backrefs, and extent-buffer accessors. It is wired into VFS exportfs through `const struct export_operations btrfs_export_ops`.

## Risks
Subvolume boundaries are the main correctness risk. Handles must distinguish parent roots when parent and child are not in the same root, or exportfs can reconnect to the wrong directory.

Generation checks protect against stale handles; bypassing them would risk resolving a reused inode number as the wrong file.

`btrfs_get_parent()` relies on finding the immediately preceding backref/ref item after a search for offset `-1`; corruption or unexpected key ordering returns `-EUCLEAN` or `-ENOENT`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/export.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/export.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/export.h

## Summary
Defines the Btrfs exportfs file-handle structure and declares export-related entry points.

## Main Contents
- `extern const struct export_operations btrfs_export_ops`.
- Packed `struct btrfs_fid`.
- Declarations for `btrfs_get_dentry()` and `btrfs_get_parent()`.

## Important Details
`struct btrfs_fid` stores:
- inode objectid,
- inode root objectid,
- inode generation,
- parent objectid,
- parent generation,
- parent root objectid.

The parent root field is needed for cross-subvolume connectable file handles.

## Risks
The structure is packed and interpreted as a generic exportfs `u32` file-handle payload. Field size/order must stay compatible with `export.c` size macros and existing file-handle types.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/export.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/extent-io-tree.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/extent-io-tree.c

## Summary
Implements Btrfs extent state trees: rb-tree-backed interval state tracking for inode I/O, metadata dirty ranges, pinned extents, device allocation state, log ranges, and other filesystem-owned byte ranges.

## Main Responsibilities
- Allocate, reference, free, and leak-check `extent_state` records.
- Insert, split, merge, and remove byte-range state records.
- Set, clear, convert, test, count, and search extent-state bits.
- Provide blocking and nonblocking extent locks.
- Wake waiters when lock bits clear.
- Integrate inode I/O tree state changes with delalloc accounting callbacks.

## Key APIs
- Initialization/lifecycle: `btrfs_extent_io_tree_init()`, `btrfs_extent_io_tree_release()`, `btrfs_extent_state_init_cachep()`, `btrfs_extent_state_free_cachep()`.
- Locking: `btrfs_lock_extent_bits()`, `btrfs_try_lock_extent_bits()`.
- State mutation: `btrfs_set_extent_bit()`, `btrfs_set_record_extent_bits()`, `btrfs_clear_extent_bit_changeset()`, `btrfs_clear_record_extent_bits()`, `btrfs_convert_extent_bit()`.
- Search/query: `btrfs_find_first_extent_bit()`, `btrfs_find_first_clear_extent_bit()`, `btrfs_find_contiguous_extent_bit()`, `btrfs_find_delalloc_range()`, `btrfs_count_range_bits()`, `btrfs_test_range_bit()`, `btrfs_test_range_bit_exists()`, `btrfs_get_range_bits()`.
- Iteration: `btrfs_next_extent_state()`.

## Important Behavior
Each `extent_state` covers an inclusive byte range and a bitmask. Ranges are stored in an rb-tree and are split when a mutation touches only part of a record. Adjacent records with identical mergeable state are merged. Records with lock bits or `EXTENT_BOUNDARY` are not merged because waiters and I/O completion paths depend on stable records.

Set operations can take exclusive bits (`EXTENT_LOCKED` or `EXTENT_DIO_LOCKED`). If any part of the target range already has those bits, `set_extent_bit()` returns `-EEXIST` and identifies the failed range. Blocking lock wrappers then wait for those bits to clear and retry. Try-lock wrappers roll back any partially acquired range.

Clear operations can delete all bits with `EXTENT_CLEAR_ALL_BITS`, update changesets, split leading/trailing portions, wake lock waiters, and remove records whose state becomes zero.

`EXTENT_NOWAIT` is a control bit that switches allocations to `GFP_NOWAIT` and is masked out before state mutation. Other control bits drive accounting behavior but are not persisted as normal state bits.

For inode I/O trees, state mutation calls into inode delalloc hooks:
- `btrfs_set_delalloc_extent()`
- `btrfs_clear_delalloc_extent()`
- `btrfs_split_delalloc_extent()`
- `btrfs_merge_delalloc_extent()`

## State and Synchronization
Each `extent_io_tree` has a spinlock protecting the rb-tree. Each `extent_state` has a refcount and waitqueue. Waiting on extent bits is done by taking an extra state reference, preparing to wait on the state waitqueue, dropping the tree lock, scheduling, and retrying.

The optional cached-state pointer speeds repeated operations over adjacent ranges. Functions carefully drop stale cached references when state is no longer useful or when exclusive clear operations make caching unsafe.

Debug builds keep a global leak list for `extent_state` allocations and perform odd-range diagnostics for inode I/O trees.

## Risks
Inclusive range arithmetic is error-prone, especially at `end + 1`, `start - 1`, and `(u64)-1` sentinel boundaries.

Cached state references must be released exactly once and must not be trusted after unlock/retry unless the record is still in the tree.

Lock-bit records cannot be merged without breaking waitqueue semantics. Accidentally merging them could lose waiters or wake the wrong range.

Delalloc accounting is coupled to split/merge/set/clear paths for inode trees. Incorrect callback ordering can corrupt delayed allocation byte accounting, qgroup reservations, or inode byte updates.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/extent-io-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/extent-io-tree.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/extent-io-tree.h

## Summary
Defines Btrfs extent-state bits, extent I/O tree ownership types, core extent-state structures, and public APIs for range state mutation, locking, and queries.

## Main Contents
- Extent state bits such as `EXTENT_DIRTY`, `EXTENT_LOCKED`, `EXTENT_DIO_LOCKED`, `EXTENT_DELALLOC`, `EXTENT_BOUNDARY`, `EXTENT_NODATASUM`, reservation/accounting bits, ordered-completion bits, and `EXTENT_NOWAIT`.
- Control masks: `EXTENT_DO_ACCOUNTING`, `EXTENT_CTLBITS`, `EXTENT_LOCK_BITS`.
- Device allocation aliases: `CHUNK_ALLOCATED`, `CHUNK_TRIMMED`, `CHUNK_STATE_MASK`.
- Tree owner enum values such as inode I/O, btree inode I/O, pinned extents, dirty transaction pages, log csum ranges, device allocation state, and selftests.
- `struct extent_io_tree`.
- `struct extent_state`.

## Key Interfaces
The header declares all extent-state lifecycle, lock, set/clear/convert, search, count, and test helpers implemented in `extent-io-tree.c`. It also provides inline convenience wrappers for normal extent locks, direct-I/O extent locks, dirty clearing, and unlocking.

## Important Details
`extent_io_tree` stores either `fs_info` or an owning `btrfs_inode` depending on `owner`. `owner == IO_TREE_INODE_IO` means the inode pointer is valid and `fs_info` is reached through `inode->root`.

`EXTENT_DELALLOC_NEW` has a narrow ownership rule: it must be cleared during ordered extent completion or on submission error paths that did not create ordered extents. Page release/invalidation must not clear it when ordered extents are in flight.

`EXTENT_ADD_INODE_BYTES` is a control flag used when clearing new delalloc after successful ordered completion so VFS inode byte accounting and Btrfs new-delalloc accounting change atomically.

## Risks
The bit definitions encode accounting contracts, not just range labels. Misusing `EXTENT_DO_ACCOUNTING`, `EXTENT_DELALLOC_NEW`, or `EXTENT_ADD_INODE_BYTES` can cause reservation leaks or incorrect stat data.

The device allocation tree reuses bit values under `CHUNK_*` aliases, so generic extent-state helpers must be used with awareness of the tree owner and bit meaning.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/extent-io-tree.h -->