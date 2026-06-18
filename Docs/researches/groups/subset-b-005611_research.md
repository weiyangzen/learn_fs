# subset-b-005611 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/discard.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/discard.c

## Purpose
`discard.c` implements Btrfs asynchronous discard/trim scheduling for data-only block groups. It moves free-space trimming out of transaction commit by keeping block groups on LRU-like discard lists, issuing one discard region per delayed-work run, and progressively relaxing size filters so large discardable regions are prioritized before smaller bitmap-backed regions.

## Important APIs, types, and functions
The public entry points are `btrfs_discard_queue_work`, `btrfs_discard_cancel_work`, `btrfs_discard_schedule_work`, `btrfs_discard_check_filter`, `btrfs_discard_calc_delay`, `btrfs_discard_update_discardable`, `btrfs_discard_punt_unused_bgs_list`, `btrfs_discard_resume`, `btrfs_discard_stop`, `btrfs_discard_init`, and `btrfs_discard_cleanup`. Important internals are `find_next_block_group`, `peek_discard_list`, `btrfs_discard_workfn`, `btrfs_finish_discard_pass`, `btrfs_update_discard_index`, and `btrfs_discard_purge_list`. The implementation depends on `struct btrfs_discard_ctl`, per-block-group `discard_index`, `discard_state`, `discard_cursor`, and `discard_eligible_time`, plus the list indexes and minimum length filters defined by the Btrfs discard constants.

## Control flow
When free space or an unused block group becomes eligible, `btrfs_discard_queue_work` places a data-only block group on either an unused list or a size-filtered discard list and schedules the delayed worker. `btrfs_discard_workfn` selects the earliest eligible group, snapshots its discard state/index, checks that async discard is still running, trims either extent entries, bitmap entries, or a fully remapped block group, advances the cursor, and either starts the bitmap pass, moves the group to the next filter, sends a fully trimmed empty group to the unused-block-group path, or reschedules the next delayed run. Delay calculation combines the configured IOPS base delay, optional KB/s throttling from the previous trim size, the block group's eligibility timeout, and an override mode used after commit-time recalculation.

## State and persistence
Discard state is intentionally in-memory. The backing truth is the free-space cache, and mount loads block groups as not discarded, making remount behavior equivalent to crash recovery. `discard_ctl->lock` protects discard lists, current block group, and scheduling fields; block-group references are acquired while queued or running. Atomic counters track discardable extents/bytes and statistics, while `discard_extent_bytes`, `discard_bitmap_bytes`, and `discard_bytes_saved` are runtime accounting only. Persistent device state changes only through issued trim/discard commands; the exact trimmed map is not persisted.

## Dependencies and integration points
This file integrates with block-group lifetime (`btrfs_get_block_group`, `btrfs_put_block_group`, `btrfs_mark_bg_unused`), free-space-cache trim helpers (`btrfs_trim_block_group_extents`, `btrfs_trim_block_group_bitmaps`, `btrfs_is_free_space_trimmed`), remap-tree helpers (`btrfs_trim_fully_remapped_block_group`), mount option `DISCARD_ASYNC`, `fs_info->unused_bgs`, delayed workqueues, and transaction commit paths that update discardable counters and delays. `disk-io.c` initializes the discard control structure, creates the discard workqueue, resumes async discard after RW mount setup, and cancels/purges it during unmount.

## Risks and test signals
Risk centers on list/reference balance, races between disabled discard and queued block groups, cursor transitions between extent and bitmap passes, empty/remapped group handling, and rate-limit delay math. The source also contains an apparent duplicated assignment to `discard_ctl` in `btrfs_discard_update_discardable`, which is harmless but worth flagging during cleanup. Test signals include mounting with `discard=async`, freeing large and small extents, emptying block groups, toggling/remounting discard, transaction-commit delay recalculation, remap-tree fully remapped groups, mixed/non-data block groups being ignored, cancellation while the worker is on a group, and unmount cleanup with queued unused groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/discard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/discard.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/discard.h

## Purpose
`discard.h` declares the async discard interface used by Btrfs block-group, free-space, mount, remount, and transaction code. It also centralizes the default maximum discard size and the two size filters used by the implementation.

## Important APIs, types, and functions
The header forward-declares `struct btrfs_fs_info`, `struct btrfs_discard_ctl`, and `struct btrfs_block_group`. Constants include `BTRFS_ASYNC_DISCARD_DEFAULT_MAX_SIZE`, `BTRFS_ASYNC_DISCARD_MAX_FILTER`, and `BTRFS_ASYNC_DISCARD_MIN_FILTER`. The exported functions cover list/filter updates (`btrfs_discard_check_filter`), work management (`btrfs_discard_cancel_work`, `btrfs_discard_queue_work`, `btrfs_discard_schedule_work`), accounting (`btrfs_discard_calc_delay`, `btrfs_discard_update_discardable`), and lifecycle (`btrfs_discard_punt_unused_bgs_list`, `btrfs_discard_resume`, `btrfs_discard_stop`, `btrfs_discard_init`, `btrfs_discard_cleanup`).

## Control flow
Callers initialize the discard controller during `btrfs_fs_info` setup, resume it after a writable mount is ready, queue block groups as free space changes, recalculate delays after discardable accounting changes, and stop/cleanup the delayed work during remount or unmount. The header intentionally hides list mechanics and state-machine details inside `discard.c`.

## State and persistence
The header itself holds no state. Its API operates on `fs_info->discard_ctl` and block-group runtime fields. The associated state is volatile and reconstructed at mount, while actual trim effects are external device side effects.

## Dependencies and integration points
It includes Linux integer/size types and is included by Btrfs components that need to enqueue discard work or manage discard lifecycle. The function signatures expose only Btrfs core structures, keeping free-space cache and workqueue details private to the implementation file.

## Risks and test signals
The main API risk is lifecycle ordering: callers must not queue work before initialization, must stop/cancel work before freeing block groups or workqueues, and must hold the free-space cache lock where `btrfs_discard_update_discardable` expects it. Test signals are compile coverage from block-group/free-space/disk-io users, async discard mount/remount/unmount tests, and fault-injection around workqueue creation and cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/discard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/disk-io.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/disk-io.c

## Purpose
`disk-io.c` is the central Btrfs filesystem mount, metadata I/O, superblock, root-cache, worker, transaction-thread, and unmount implementation. It validates and reads tree blocks, loads core roots from superblocks and the root tree, starts long-lived kernel threads/workqueues, handles log replay and writable-mount preparation, writes superblocks during commits, and tears the filesystem down safely.

## Important APIs, types, and functions
Major exported functions include `open_ctree`, `close_ctree`, `read_tree_block`, `btrfs_read_extent_buffer`, `btrfs_validate_extent_buffer`, `btrfs_buffer_uptodate`, `btree_csum_one_bio`, `btrfs_check_super_csum`, `btrfs_validate_super`, `btrfs_check_features`, `btrfs_start_pre_rw_mount`, `write_all_supers`, `btrfs_commit_super`, `btrfs_init_fs_info`, `btrfs_free_fs_info`, `btrfs_read_tree_root`, `btrfs_get_fs_root`, `btrfs_get_new_fs_root`, `btrfs_get_fs_root_commit_root`, `btrfs_global_root_insert`, `btrfs_global_root_delete`, `btrfs_global_root`, `btrfs_csum_root`, `btrfs_extent_root`, `btrfs_create_tree`, `btrfs_put_root`, `btrfs_free_fs_roots`, `btrfs_mark_buffer_dirty`, `btrfs_btree_balance_dirty`, `btrfs_cleanup_dirty_bgs`, `btrfs_cleanup_one_transaction`, `btrfs_init_root_free_objectid`, and `btrfs_get_free_objectid`. Central state is in `struct btrfs_fs_info`, `struct btrfs_root`, `struct extent_buffer`, `struct btrfs_transaction`, `struct btrfs_device`, and superblock/root-item structures.

## Control flow
`open_ctree` initializes mount-time `fs_info`, allocates essential roots, creates the btree inode, reads and checks the primary superblock checksum, validates sizes/features/UUIDs, configures block sizes and mount options, initializes compression/workqueues, reads system chunks and the chunk tree, loads important roots and global roots, reads devices/block groups, initializes sysfs, starts cleaner and transaction kthreads, optionally replays the tree log, reads the default fs root, then performs RW-only recovery such as free-space-tree repair, orphan cleanup, relocation recovery, balance/dev-replace resume, UUID tree creation, qgroup resume, and async discard resume. Metadata reads go through extent-buffer allocation, checksum/owner/level/key/transid validation, and mirror retry/repair. Commits write superblocks by preparing backup root slots, flushing devices, validating the superblock image, submitting mirror writes, and waiting for enough devices according to degradability. `close_ctree` reverses mount state in an ordered sequence: stop producers, park/stop threads, flush workqueues and ordered extents, cancel async reclaim/discard, commit or cleanup transactions, remove sysfs, free roots/block groups/workqueues, invalidate the btree inode, and release mapping/device structures.

## State and persistence
Persistent state includes superblock copies, root pointers/generations, backup root arrays, chunk mappings, feature flags, device items, log roots, block group/free-space trees, UUID/qgroup/dev-replace/balance state, and metadata tree blocks. Runtime state includes root radix caches, global-root rbtrees, extent-buffer cache, transaction lists, dirty metadata accounting, kthreads, workqueues, block reservations, delayed iputs/inodes, qgroup state, discard control, and sysfs registrations. `super_copy` mirrors the mounted superblock, while `super_for_commit` is staged and checksummed for writes. The file is careful to use `GFP_NOFS`/NOFS contexts around transaction-held allocations and to clean up partially initialized mount stages through labeled error paths.

## Dependencies and integration points
`disk-io.c` ties together nearly every Btrfs subsystem: transactions, extent I/O, tree locking/checking, block groups, free-space cache/tree, devices/chunks, zoned mode, dev replace, balance, relocation, qgroups, compression, delayed inode handling, scrub, sysfs, ref verify, UUID tree, discard, and VFS address-space operations for the btree inode. It also integrates with kernel block devices, bios, folios, workqueues, kthreads, radix trees/xarrays, percpu counters, rwsems, wait queues, and checksum implementations.

## Risks and test signals
High-risk areas are mount error unwinding, superblock validation gaps, metadata checksum/parent verification, root reference lifetime, backup-root fallback, log replay on degraded or read-only media, feature compatibility checks, flush/FUA and multi-device super write tolerances, unmount ordering against delayed iputs and workqueues, and transaction cleanup after filesystem errors. The source snapshot has minor suspicious code style issues such as duplicated error logging in one super-write path and spacing in a transaction state assignment; these are not behavioral by themselves but are useful review signals. Test signals include xfstests mount/unmount/replay/degraded suites, checksum and tree-checker corruption injection, unsupported feature flags, backup root recovery, log replay with missing devices, remount RO/RW, zoned mounts, qgroup/dev-replace/balance resume, superblock write failure injection, delayed iput/workqueue race tests, and lockdep/KASAN coverage during mount failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/disk-io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/disk-io.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/disk-io.h

## Purpose
`disk-io.h` is the public internal interface for Btrfs disk I/O, root management, superblock handling, mount lifecycle, metadata buffering, log-tree setup, transaction cleanup, and root objectid allocation.

## Important APIs, types, and functions
The header defines superblock mirror constants `BTRFS_SUPER_MIRROR_MAX`, `BTRFS_SUPER_MIRROR_SHIFT`, fixed `BTRFS_BDEV_BLOCKSIZE`, and helper `btrfs_sb_offset`. It declares mount/lifecycle APIs (`open_ctree`, `close_ctree`, `btrfs_init_fs_info`, `btrfs_free_fs_info`, `btrfs_start_pre_rw_mount`), metadata read/write validation (`read_tree_block`, `btrfs_find_create_tree_block`, `btrfs_validate_extent_buffer`, `btrfs_buffer_uptodate`, `btrfs_read_extent_buffer`, `btree_csum_one_bio`, `btrfs_mark_buffer_dirty`), superblock work (`btrfs_check_super_csum`, `btrfs_validate_super`, `btrfs_check_features`, `write_all_supers`, `btrfs_commit_super`), root APIs (`btrfs_read_tree_root`, `btrfs_insert_fs_root`, `btrfs_get_fs_root`, `btrfs_get_new_fs_root`, `btrfs_get_fs_root_commit_root`, `btrfs_global_root_*`, `btrfs_csum_root`, `btrfs_extent_root`, `btrfs_put_root`, `btrfs_create_tree`), and cleanup/objectid helpers.

## Control flow
Callers use the declarations to enter the filesystem through `open_ctree`, fetch or create roots during normal operation, validate/read metadata blocks during tree walks, mark metadata dirty under active transactions, balance dirty btree pages, commit superblocks, and leave through `close_ctree`. Inline `btrfs_grab_root` increments a root ref only if the root is still alive, which is the common fast path for root-cache lookups.

## State and persistence
The header has no storage of its own, but its API governs persistent metadata and runtime state in `fs_info`, roots, extent buffers, superblocks, and transactions. `btrfs_sb_offset` encodes the fixed locations of primary and backup superblock mirrors, which are part of the on-disk format contract.

## Dependencies and integration points
It includes Btrfs core definitions from `ctree.h`, bio support, and ordered-data declarations, and forward-declares core VFS/block/Btrfs structures. It is included across tree walking, transaction, block-group, export, and mount code that needs common disk I/O and root access.

## Risks and test signals
API misuse risks include taking roots without balancing `btrfs_put_root`, marking buffers dirty outside a matching transaction, reading tree blocks with an incomplete parent check, and using global-root helpers with the wrong root key for extent-tree-v2. Test signals include compile coverage across Btrfs, root ref leak checks, metadata read corruption tests, superblock mirror offset tests, and transaction dirty-buffer assertions under debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/disk-io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/export.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/export.c

## Purpose
`export.c` implements Btrfs export operations for file handles, primarily for NFS/exportfs. It encodes Btrfs inode/root/generation identity into stable file handles, resolves handles back to dentries, finds parents across normal directory entries and subvolume roots, and returns child names for reconnecting paths.

## Important APIs, types, and functions
The exported operations table is `btrfs_export_ops`. Key functions are `btrfs_encode_fh`, `btrfs_get_dentry`, `btrfs_fh_to_parent`, `btrfs_fh_to_dentry`, `btrfs_get_parent`, and `btrfs_get_name`. The code uses `struct btrfs_fid` from `export.h` and exportfs handle types `FILEID_BTRFS_WITHOUT_PARENT`, `FILEID_BTRFS_WITH_PARENT`, and `FILEID_BTRFS_WITH_PARENT_ROOT`.

## Control flow
Encoding stores the inode objectid, subvolume root objectid, and generation; when a parent is supplied it stores parent objectid/generation and, if parent and child are in different roots, the parent root id. Decoding validates handle length/type, then calls `btrfs_get_dentry`, which rejects reserved objectids, obtains the requested root with `btrfs_get_fs_root`, igets the inode, verifies generation when present, and returns an alias dentry. Parent lookup searches either `BTRFS_INODE_REF_KEY` in the current root or `BTRFS_ROOT_BACKREF_KEY` in the tree root for subvolume roots, then obtains the parent inode/dentry. Name lookup reads the inode-ref or root-ref name bytes from the relevant leaf and null-terminates them for exportfs reconnect.

## State and persistence
File handles persist outside the kernel in export clients and encode enough on-disk identity to detect stale inodes via generation mismatches. Runtime state is limited to allocated paths, held roots, iget references, and dentries. It relies on Btrfs root and inode items/backrefs as persistent metadata.

## Dependencies and integration points
The file integrates Btrfs with Linux exportfs through `struct export_operations`. It depends on root lookup from `disk-io.c`, inode loading from Btrfs inode code, tree searches, accessors for inode/root refs, dentry aliasing, and VFS inode generation. It is sensitive to Btrfs subvolume semantics because parent and child may belong to different roots.

## Risks and test signals
Risks include stale handle detection, incorrect handle length negotiation, cross-subvolume parent encoding, missing or corrupt inode/root backrefs, name buffer sizing by exportfs callers, and reserved objectid handling. The source snapshot contains an apparent duplicated `btrfs_iget` call in `btrfs_get_parent`; review should confirm whether this is an accidental duplication because it would affect reference handling if compiled as-is. Test signals include NFS export of regular files and subvolumes, reconnect after rename/snapshot/delete, stale generation handles, parent lookup across subvolume boundaries, malformed short handles, and filesystem corruption tests for missing backrefs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/export.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/export.h

## Purpose
`export.h` declares the Btrfs exportfs interface and defines the packed file-handle payload used by `export.c`.

## Important APIs, types, and functions
The key type is packed `struct btrfs_fid`, containing child `objectid`, `root_objectid`, `gen`, optional `parent_objectid`, `parent_gen`, and optional `parent_root_objectid`. The header declares `btrfs_export_ops`, `btrfs_get_dentry`, and `btrfs_get_parent`.

## Control flow
Exportfs consumers call through `btrfs_export_ops`; direct Btrfs users can resolve a dentry by objectid/root/generation or ask for a dentry's parent. The packed struct layout is used by `export.c` to compute handle lengths in 32-bit words, so field order is part of the encoded ABI.

## State and persistence
The header stores no runtime state. Its file-handle layout persists in NFS/export clients and must remain compatible with existing handle decoding. Generation fields provide stale-handle detection against on-disk inode identity.

## Dependencies and integration points
It includes Linux `exportfs.h` and integer types, forward-declares VFS structures, and is consumed by Btrfs super/export setup plus any Btrfs code that needs direct parent/dentry resolution.

## Risks and test signals
Risks are ABI/layout changes to the packed handle, incorrect assumptions about alignment, and incomplete parent-root data for cross-subvolume reconnects. Test signals include handle encode/decode compatibility, NFS reconnect across kernel upgrades, cross-subvolume exports, and stale file-handle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/export.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/extent-io-tree.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/extent-io-tree.c

## Purpose
`extent-io-tree.c` implements Btrfs' in-memory interval state tree for byte ranges. It tracks dirty, locked, delalloc, boundary, reservation, direct-I/O, and related flags over inclusive ranges using an rb-tree of `struct extent_state` records, with split/merge logic, wait queues for lock bits, changeset accounting, and debug leak detection.

## Important APIs, types, and functions
Public APIs include `btrfs_extent_io_tree_init`, `btrfs_extent_io_tree_release`, `btrfs_set_extent_bit`, `btrfs_clear_extent_bit_changeset`, `btrfs_convert_extent_bit`, `btrfs_lock_extent_bits`, `btrfs_try_lock_extent_bits`, `btrfs_find_first_extent_bit`, `btrfs_find_first_clear_extent_bit`, `btrfs_find_contiguous_extent_bit`, `btrfs_find_delalloc_range`, `btrfs_count_range_bits`, `btrfs_test_range_bit`, `btrfs_test_range_bit_exists`, `btrfs_get_range_bits`, `btrfs_set_record_extent_bits`, `btrfs_clear_record_extent_bits`, `btrfs_next_extent_state`, `btrfs_extent_state_init_cachep`, and `btrfs_extent_state_free_cachep`. Important internals are `tree_search_for_insert`, `tree_search_prev_next`, `insert_state`, `split_state`, `merge_state`, `set_state_bits`, `clear_state_bit`, `wait_extent_bit`, and cached-state helpers.

## Control flow
Set/clear/convert operations search for the first state intersecting the requested range, split existing records at range boundaries, insert records for holes, update bits, merge adjacent compatible records, and retry after dropping the spinlock if atomic preallocation fails or rescheduling is needed. Lock operations use exclusive `EXTENT_LOCK_BITS`: if a lock bit already exists, the partially acquired prefix is cleared, callers wait on the existing state's waitqueue, and the operation retries. Range queries walk the rb-tree under the tree lock and optionally preserve a referenced cached state to speed repeated scans.

## State and persistence
All state is volatile memory. `extent_io_tree->state` is an rb-root protected by `tree->lock`; each `extent_state` stores inclusive `start/end`, bitmask, refcount, waitqueue, and optional leak-list linkage. For inode I/O trees, set/clear/split/merge callbacks update delalloc accounting in the owning inode. There is no direct on-disk persistence, but the state drives writeback, transaction dirty page tracking, pinned extents, device allocation state, and other paths that later update persistent metadata.

## Dependencies and integration points
The file depends on Linux slab caches, rbtrees, spinlocks, wait queues, refcounts, tracing, and Btrfs helpers from extent I/O, inode, messages, and ctree code. It is used by inode I/O, btree inode metadata, transaction dirty-page tracking, pinned/excluded extents, relocation, root dirty log pages, log checksum ranges, selftests, and device allocation state. The owner field determines whether the union points to `fs_info` or an inode and whether delalloc accounting callbacks are invoked.

## Risks and test signals
Risk concentrates in off-by-one inclusive range handling, split/merge correctness, cached-state refcounting, lock wait/wakeup ordering, NOWAIT allocation behavior, changeset accounting under GFP_ATOMIC, and owner-specific delalloc callbacks. Because this tree is used in transaction cleanup and writeback, leaks or missed wakeups can cause unmount hangs or metadata/accounting corruption. Test signals include Btrfs extent-io selftests, lock/unlock contention, delalloc writeback and truncation, direct-I/O locking, dirty-range conversion, clear-all truncation paths, fault injection for allocation failures, CONFIG_BTRFS_DEBUG leak checks, lockdep, and KASAN/KCSAN runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/extent-io-tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/extent-io-tree.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/extent-io-tree.h

## Purpose
`extent-io-tree.h` defines the range-state bits, owner identifiers, core data structures, and public helpers for Btrfs extent I/O trees. These trees are the shared mechanism for tracking per-byte in-memory state across inode I/O, metadata, transaction, relocation, logging, and device-allocation paths.

## Important APIs, types, and functions
The header defines state bits such as `EXTENT_DIRTY`, `EXTENT_LOCKED`, `EXTENT_DIO_LOCKED`, `EXTENT_DELALLOC`, `EXTENT_BOUNDARY`, reservation-clearing bits, `EXTENT_DELALLOC_NEW`, `EXTENT_FINISHING_ORDERED`, `EXTENT_ADD_INODE_BYTES`, `EXTENT_CLEAR_ALL_BITS`, and control bit `EXTENT_NOWAIT`. It also aliases device-allocation states `CHUNK_ALLOCATED`, `CHUNK_TRIMMED`, and `CHUNK_STATE_MASK`. Owner IDs include filesystem pinned/excluded extents, btree inode I/O, inode I/O, relocation blocks, transaction dirty pages, root dirty log pages, file extents, log csum ranges, selftests, and device allocation state. Core structures are `struct extent_io_tree` and `struct extent_state`; public helpers cover init/release, set/clear/convert, lock/try-lock/unlock, DIO locks, queries, counting, changeset recording, cached traversal, and slab-cache lifecycle.

## Control flow
Callers initialize a tree with an owner, then set, clear, convert, query, or lock inclusive byte ranges. Inline wrappers specialize common operations such as normal extent locks, DIO locks, unlocks, and clearing dirty/delalloc accounting bits. The implementation uses owner information to interpret the union field as either `fs_info` or inode and to route inode-owned state changes through delalloc accounting hooks.

## State and persistence
The data structures describe runtime-only state: an rb-tree of range records protected by a spinlock, plus each range's waitqueue/refcount/bitmask. The owner value is essential for safe interpretation of the union pointer. Although not persisted directly, these states gate persistent writeback, transaction cleanup, metadata dirty tracking, and allocation/discard decisions.

## Dependencies and integration points
The header depends on Linux rbtree, spinlock, refcount, list, waitqueue, and Btrfs misc helpers. It is included by extent I/O, disk I/O, inode, transaction, block-group/device allocation, relocation, and selftest code that needs shared range-state management.

## Risks and test signals
Risks include adding new bits in the wrong position relative to `EXTENT_NOWAIT`, confusing control bits with stored state bits, using `EXTENT_LOCKED`/`EXTENT_BOUNDARY` semantics for device allocation trees, passing the wrong owner, leaking cached `extent_state` references, and treating inclusive `end` values as exclusive. Test signals include compile coverage for all inline wrappers, extent-state selftests, direct and buffered writeback tests, DIO lock tests, device allocation state tests, and debug builds that check range oddities and leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/extent-io-tree.h -->
