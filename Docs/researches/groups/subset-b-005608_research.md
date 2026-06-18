# subset-b-005608 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/block-group.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/block-group.c

## Purpose
`block-group.c` is the core Btrfs block-group implementation. It reconstructs block groups at mount, tracks their lifetime in the in-memory cache tree and per-space-info lists, coordinates free-space caching, handles read-only/removal/reclaim transitions, persists block group and device-extent items during transactions, and drives data/metadata chunk allocation. In Btrfs terms, this file is the bridge between logical chunk mappings, extent-tree block group items, device extents, free-space caches/trees, space accounting, discard, relocation, zoned allocation, and transaction commit.

## Important APIs, types, and functions
- Allocation profile helpers include `btrfs_get_alloc_profile()`, `btrfs_reduce_alloc_profile()`, and wrappers in the header. They merge requested DATA/METADATA/SYSTEM type bits with currently available profiles and active balance conversion targets.
- Block group cache lookup/lifetime APIs are `btrfs_lookup_first_block_group()`, `btrfs_lookup_block_group()`, `btrfs_next_block_group()`, `btrfs_get_block_group()`, and `btrfs_put_block_group()`. The cache is an rb-tree rooted at `fs_info->block_group_cache_tree`.
- Reservation and write-race helpers are `btrfs_inc_nocow_writers()`, `btrfs_dec_nocow_writers()`, `btrfs_wait_nocow_writers()`, `btrfs_dec_block_group_reservations()`, and `btrfs_wait_block_group_reservations()`.
- Free-space caching entry points are `btrfs_cache_block_group()`, `btrfs_wait_block_group_cache_progress()`, `caching_thread()`, `load_extent_tree_free()`, `btrfs_add_new_free_space()`, and `load_block_group_size_class()`.
- Removal and reclaim are implemented by `btrfs_start_trans_remove_block_group()`, `btrfs_remove_block_group()`, `btrfs_delete_unused_bgs()`, `btrfs_mark_bg_unused()`, `btrfs_mark_bg_to_reclaim()`, `btrfs_reclaim_block_groups()`, and `btrfs_reclaim_bgs_work()`.
- Mount-time reconstruction uses `btrfs_read_block_groups()`, `read_one_block_group()`, `find_first_block_group()`, `read_bg_from_eb()`, `exclude_super_stripes()`, `check_chunk_block_group_mappings()`, and rescue-only `fill_dummy_bgs()`.
- New block groups and chunk allocation are handled by `btrfs_make_block_group()`, `btrfs_create_pending_block_groups()`, `btrfs_chunk_alloc()`, `btrfs_force_chunk_alloc()`, `do_chunk_alloc()`, `check_system_chunk()`, and `btrfs_reserve_chunk_metadata()`.
- Transaction persistence and accounting are centered on `btrfs_update_block_group()`, `btrfs_add_reserved_bytes()`, `btrfs_free_reserved_bytes()`, `btrfs_setup_space_cache()`, `btrfs_start_dirty_block_groups()`, `btrfs_write_dirty_block_groups()`, and `update_block_group_item()`.
- Teardown and special-state helpers include `btrfs_put_block_group_cache()`, `btrfs_free_block_groups()`, `btrfs_freeze_block_group()`, `btrfs_unfreeze_block_group()`, swap extent counters, size-class APIs, and fully-remapped block group handling.

## Control flow
At mount, `btrfs_read_block_groups()` chooses the block group root, scans `BTRFS_BLOCK_GROUP_ITEM_KEY` items, verifies each item against the chunk mapping, creates a `struct btrfs_block_group`, loads persisted used/profile/remap state, loads zoned information, excludes superblock mirror stripes from free space, initializes quick full/empty free-space state where possible, inserts the block group into the rb-tree, adds it to its `btrfs_space_info`, and marks available allocation profile bits. If no extent root is available under rescue or unsupported read-only feature conditions, `fill_dummy_bgs()` creates full dummy groups from chunk maps so the filesystem can still mount read-only enough to recover data.

Free-space caching is lazy. `btrfs_cache_block_group()` installs a `btrfs_caching_control`, takes extra references for the async worker and the global caching list, and queues `caching_thread()` unless the group is already cached. The worker optionally samples file extent items to infer a data block group size class, then tries the old space cache, free-space tree, or committed extent tree scan. `load_extent_tree_free()` walks the commit root with locking skipped to avoid extent-tree allocation deadlocks, adds gaps as free space after subtracting excluded super stripes, periodically wakes allocators after `CACHING_CTL_WAKE_UP`, and marks the cache finished or errored.

Runtime allocation has two levels. Extent allocation first reserves bytes in an existing block group with `btrfs_add_reserved_bytes()`, which checks read-only state, enforces size-class policy for data-only groups, moves bytes from `bytes_may_use` to `bytes_reserved`, and tracks delayed allocation. Later delayed references call `btrfs_update_block_group()` to convert reserved bytes into used bytes, or to move freed bytes into pinned extents until transaction commit. That function also dirties the block group for transaction persistence and queues unused or reclaimable groups after usage drops.

Chunk allocation is intentionally split into two phases. `btrfs_chunk_alloc()` is phase 1: it decides whether a chunk is needed, serializes with `space_info->chunk_alloc` and `fs_info->chunk_mutex`, reserves system metadata for chunk-tree updates, calls volume code to allocate device extents and create the mapping/block group, and inserts or updates chunk-tree items. `btrfs_create_pending_block_groups()` is phase 2: it later inserts the block group item into the extent or block-group tree, inserts device extent items into the device tree, adds free-space-tree state, updates sysfs type nodes, drops delayed-ref reservations, and moves still-empty groups to the unused list.

Transaction commit persists dirty block groups in two passes. `btrfs_start_dirty_block_groups()` runs before the critical commit section, sets up old space-cache inodes, starts cache writeout where safe, updates block group items, runs delayed refs, and loops once to catch block groups dirtied by that work. `btrfs_write_dirty_block_groups()` runs in the critical section, waits for any outstanding cache I/O, retries rare `-ENOENT` cases caused by free-space endio workers creating new block groups, updates persisted used/remap/flag fields, drains `io_bgs`, and aborts the transaction for metadata item update errors.

Removal starts by making a block group read-only and cleaning races. `btrfs_delete_unused_bgs()` consumes `fs_info->unused_bgs`, skips groups that are mixed, still used, the only group for a profile, waiting on async discard, blocked by unwritten zoned metadata, or still needed for outstanding reservations, then flips the group read-only, finishes zones, starts a remove-block-group transaction, clears pinned extents, and calls chunk removal. `btrfs_remove_block_group()` removes allocator cluster membership, waits free-space cache I/O, removes free-space inode/tree state, erases the rb-tree node and space-info list entry, clears profile/incompat bits where appropriate, deletes the block group item, marks the group removed, and removes the chunk map only when no frozen trimmer/scrubber still needs it.

Reclaim is relocation-based. `btrfs_mark_bg_to_reclaim()` queues groups whose used bytes crossed below the reclaim threshold. `btrfs_reclaim_block_groups()` sorts by used bytes, takes an exclusive balance operation, turns each candidate read-only, relocates the chunk with `btrfs_relocate_chunk()`, records reclaim stats/errors, and periodically prioritizes empty block-group deletion.

## State and persistence behavior
Persistent on-disk state includes block group items in the extent tree or block-group tree, chunk items in the chunk tree, device extent items in the device tree, optional free-space cache inodes, optional free-space tree entries, and superblock counters/profile feature bits. Runtime state lives in `struct btrfs_block_group`: logical range, counters (`used`, `reserved`, `pinned`, `delalloc_bytes`, `bytes_super`, `zone_unusable`, `remap_bytes`), cached last-committed values, flags/runtime flags, read-only count, cache state, free-space controller, rb/list nodes, discard state, dirty/io lists, allocation barriers, nocow writer counters, swap extent count, zoned write pointers, physical map, and size class.

`space_info` counters are updated in lockstep with block group counters. Reservations move from `bytes_may_use` to `bytes_reserved`, allocation moves to `bytes_used` and `disk_used`, freeing moves to `bytes_pinned`, and read-only/zoned transitions adjust `bytes_readonly` and `bytes_zone_unusable`. Dirty block groups hold delayed-reference reserve units until their block group item updates are handled. `last_used`, `last_remap_bytes`, `last_identity_remap_count`, and `last_flags` suppress unnecessary item writes but are rolled back on failed updates.

The chunk map removal rule is deliberately conservative. A removed block group's chunk map can stay in the mapping tree while the group is frozen by trim or scrub, preventing reuse of the same logical or physical locations until all users unfreeze the group. Fully remapped block groups also preserve cleanup state across unmount by comparing block group and chunk trees and rebuilding `fully_remapped_bgs` on mount.

## Dependencies and integration points
This file depends on Btrfs space-info accounting, the extent tree, chunk/device volume code, free-space cache and free-space tree code, transaction/delayed-ref machinery, sysfs, tree logging, delalloc accounting, discard, RAID56 helpers, zoned mode, ref verification cleanup, and accessor helpers. It is called by extent allocation, delayed refs, balance/relocation, scrub/trim, device add/remove/replace, mount/unmount, transaction commit, and ENOSPC handling.

It also exposes policy to other Btrfs subsystems: profile selection during balance, read-only block group gating for relocation/scrub, NOCOW writer coordination for direct I/O races, data-only size classes used by `find_free_extent()`, and system chunk metadata reservation for callers that mutate the chunk tree outside normal allocation/removal.

## Risks and test signals
The highest risks are accounting mismatches among block group counters, space-info counters, superblock bytes-used, and delayed-ref reservations; races between block group deletion and allocation, discard, scrub, cache writeout, or zone finishing; stale or mismatched block group/chunk/device extent items; transaction aborts during phase-split chunk creation; and chunk-map reuse before frozen users are gone. Zoned paths add risk around `alloc_offset`, `meta_write_pointer`, active zones, and `zone_unusable` migration. Free-space cache paths risk trusting stale cache generations, failing to truncate old cache inodes, or leaking free space when a group is freed before cache loading.

Useful tests include mounting filesystems with old space cache, free-space tree, block-group tree, remap tree, extent tree v2, RAID56/RAID1C34 profiles, degraded profiles, mixed data/metadata groups, and zoned devices; allocating and freeing until groups become unused; concurrent trim/scrub while deleting groups; relocation-triggered reclaim; balance profile conversion; chunk allocation under system-space pressure; read-only scrub/remount interactions; swapfile extents preventing read-only transition; NOCOW direct I/O racing relocation; superblock mirror exclusion; and transaction abort/error injection in free-space cache setup and block group item updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/block-group.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/block-group.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/block-group.h

## Purpose
`block-group.h` defines the public in-kernel contract for Btrfs block groups. It declares the block group state machine, allocation policy enums, runtime flags, caching control structure, primary `struct btrfs_block_group`, and the APIs used by allocation, transaction commit, relocation, discard, zoned mode, mount, and teardown code.

## Important APIs, types, and functions
- `enum btrfs_disk_cache_state` describes old space-cache persistence states: written, error, clear, and setup.
- `enum btrfs_block_group_size_class` classifies data-only groups by first/smallest allocation size: none, small, medium, and large.
- `enum btrfs_discard_state` tracks async discard passes over extents, bitmaps, reset cursor, and fully remapped groups.
- `enum btrfs_chunk_alloc_enum` controls chunk allocation urgency: no force, limited, force, and force-for-extent with zoned activation.
- `enum btrfs_block_group_flags` contains runtime-only flags for inode references, removal, relocation/copy, chunk item insertion, active zones, zoned data relocation, free-space-tree insertion, new transaction-local groups, fully remapped groups, and stripe-removal pending state.
- `enum btrfs_caching_type` describes in-memory free-space cache status: not cached, started, finished, and error.
- `struct btrfs_caching_control` owns async cache work, waiters, progress, and an extra reference to the block group being cached.
- `struct btrfs_block_group` is the central runtime object for a logical chunk range.
- Inline helpers provide range end, used/available checks, data-only tests, allocation profile wrappers, cache-done check, and stable reads of related state.
- Function declarations expose lookup/lifetime, cache loading, free-space insertion, removal/reclaim, mount-time reading, new block group creation, read-only transitions, dirty block group writeback, reservation/accounting, chunk allocation, reverse mapping, teardown, freeze/unfreeze, swap extent counters, size classes, and fully-remapped cleanup.

## Control flow
The header has no runtime control flow by itself, but it codifies the lifecycle implemented in `block-group.c`. A block group is created or read, inserted into `fs_info->block_group_cache_tree`, attached to a `btrfs_space_info`, cached for free-space discovery, used by allocators through reservation/accounting APIs, dirtied and persisted during transactions, optionally made read-only for relocation/scrub/removal, and finally removed from the rb-tree/lists and released by reference count.

The declarations also show the split between fast allocation-facing APIs and transaction-facing APIs. Allocation code uses profile helpers, lookup, `btrfs_add_reserved_bytes()`, `btrfs_free_reserved_bytes()`, size classes, and cache wait helpers. Transaction and cleaner code use dirty writeback, pending block group creation, unused deletion, reclaim, read-only transitions, and removal. Mount/unmount code uses `btrfs_read_block_groups()`, `btrfs_put_block_group_cache()`, and `btrfs_free_block_groups()`.

## State and persistence behavior
`struct btrfs_block_group` contains both persisted values and strictly in-memory coordination state. Persisted or disk-derived fields include logical `start`/`length`, `used`, `flags`, `global_root_id`, `remap_bytes`, `identity_remap_count`, and cache generation. Last-committed mirrors (`last_used`, `last_remap_bytes`, `last_identity_remap_count`, `last_flags`) are in-memory optimization state used to decide whether a block group item needs rewriting.

In-memory counters and coordination fields include `pinned`, `reserved`, `delalloc_bytes`, `bytes_super`, `ro`, `cached`, `caching_ctl`, free-space control, rb/list nodes, reference count, discard cursors, dirty/io lists, allocation reservation and NOCOW writer atomics, free-space-tree bitmap state, swap extent count, zoned offsets/write pointers/capacity, active-zone list node, and data block group size class. The header’s comments document which locks protect key fields: `lock`, `data_rwsem`, `free_space_lock`, `groups_sem`, space-info locks, and list-specific locks in `fs_info`.

## Dependencies and integration points
The header includes Linux atomic/list/spinlock/refcount/wait/rwsem/rbtree primitives, UAPI Btrfs tree flags, and free-space cache declarations. It forward-declares core Btrfs objects so many subsystems can depend on this contract without pulling in every implementation detail. It is a key integration header for extent allocation, block reservations, transaction commit, free-space cache/tree code, volumes/chunks, relocation, discard, zoned mode, and inode code that checks NOCOW or block group state.

## Risks and test signals
Risks mostly come from contract drift: callers must honor locking and reference rules, avoid using list nodes for multiple lists at once without the prescribed helpers, account `bytes_super`/`zone_unusable` when computing available space, and respect the two-phase chunk allocation comments. `btrfs_block_group_done()` intentionally uses a memory barrier before reading cache state, and `btrfs_is_block_group_used()`/`btrfs_block_group_available_space()` require the block group lock.

Test signals include build coverage of all users after struct or enum changes, KCSAN/lockdep for lock annotations, allocation and deletion under concurrent trim/scrub/relocation, old and v2 free-space cache modes, zoned and non-zoned configurations, remap-tree and fully-remapped cleanup, size-class allocation fallback, and mount/unmount leak checks for block group references and list membership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/block-group.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/block-rsv.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/block-rsv.c

## Purpose
`block-rsv.c` implements Btrfs metadata block reserves: in-memory buckets that group pessimistic metadata reservations by purpose and move bytes between `space_info->bytes_may_use`, reserve-local `reserved`/`size` counters, and fallback/global reserves. These reserves are what let transactions, delayed refs, delayed items, delalloc, tree log, chunk updates, remap updates, truncate, and emergency fallback paths account for metadata before they allocate tree blocks.

## Important APIs, types, and functions
- `btrfs_init_block_rsv()`, `btrfs_init_metadata_block_rsv()`, `btrfs_alloc_block_rsv()`, and `btrfs_free_block_rsv()` initialize or allocate reserve objects and bind them to metadata/system/remap `space_info` instances.
- `btrfs_block_rsv_add()` reserves metadata bytes through `btrfs_reserve_metadata_bytes()` and grows both `size` and `reserved`.
- `btrfs_block_rsv_refill()` tops up `reserved` without changing `size`.
- `btrfs_block_rsv_release()` and internal `block_rsv_release_bytes()` shrink a reserve, return excess bytes to the delayed-ref reserve, global reserve, or `space_info`, and optionally report qgroup metadata to release.
- `btrfs_block_rsv_use_bytes()` consumes reserved bytes for a tree block allocation; `btrfs_block_rsv_add_bytes()` puts bytes back into a reserve.
- `btrfs_block_rsv_migrate()` atomically consumes from one reserve and credits another.
- `btrfs_update_global_block_rsv()`, `btrfs_init_global_block_rsv()`, and `btrfs_release_global_block_rsv()` maintain filesystem-wide fallback reserves.
- `btrfs_init_root_block_rsv()` chooses a root’s default reserve according to tree type.
- `btrfs_use_block_rsv()` selects and consumes the correct reserve for a tree block allocation, including global fallback and emergency metadata reservation.
- `btrfs_check_trunc_cache_free_space()` verifies that truncate/cache cleanup has enough metadata slack.

## Control flow
The file starts with a detailed design comment: callers reserve bytes into a logical bucket, use bytes when allocating tree blocks, and release unused excess at operation completion. Normal reserve addition calls `btrfs_reserve_metadata_bytes()` with a caller-selected flush policy, then records bytes under the reserve spinlock. Refill only asks for the gap between requested bytes and current `reserved`. Use subtracts from `reserved`, marks the reserve not full when it falls below `size`, and returns `-ENOSPC` if insufficient.

Release first shrinks `size`, computes excess `reserved - size`, clamps `reserved` to `size`, and similarly computes qgroup excess. If there are excess bytes, it tries to feed another reserve before freeing to `space_info->bytes_may_use`: delayed-ref reserves release toward the global reserve, while most other reserves release toward the delayed refs reserve if it is not full and uses the same space_info. This keeps highly dynamic delayed refs funded before returning bytes to the general pool.

Global reserve updates are based on the current used bytes of global metadata trees: tree root, extent root, checksum root, free-space tree, optional block-group tree, and optional RAID stripe tree. The reserve also includes unlink/delayed-ref slack, is capped at 512 MiB, updates `bytes_may_use` directly under `space_info->lock`, and can force chunk allocation if it consumes the whole metadata space_info.

When allocating a tree block, `btrfs_use_block_rsv()` picks a reserve from the transaction/root context. Shareable roots, UUID root changes, and checksum additions use the transaction reserve; specific global roots use delayed refs, global, chunk, tree-log, or remap reserves; otherwise the empty reserve is used. If the chosen reserve is short, the function may update the global reserve, reserve metadata without flushing, reject log-tree fallback immediately, consume from the global reserve when compatible, or finally attempt an emergency flush reservation.

## State and persistence behavior
Block reserves are in-memory accounting only; they do not create on-disk records. Their state mirrors metadata reservation obligations already represented by `space_info->bytes_may_use` and related reservation counters. Each reserve tracks `size`, `reserved`, `full`, `failfast`, type, `space_info`, and qgroup upper-bound reservation fields. `fs_info` owns long-lived reserves such as global, transaction, chunk, remap, delayed block, delayed refs, tree log, and empty reserves. Inode-local reserves are embedded in `struct btrfs_inode`.

The qgroup fields deliberately differ from normal metadata reservation sizing: qgroup metadata is based on possible net extent-usage changes rather than checksum sizes or exact tree-block counts. Release can report qgroup excess separately so quota accounting can be unwound consistently.

## Dependencies and integration points
This file depends on space-info reservation helpers, transaction state, block group profile constants, root item accessors, filesystem feature checks, and root IDs. It integrates with transaction start/commit, delayed refs, delayed items, inode delalloc metadata reservation, tree-log fsync, chunk-tree modification, remap-tree updates, qgroups, unlink/truncate recovery, and ENOSPC ticket granting.

## Risks and test signals
The main risks are leaks or double-frees in `bytes_may_use`, incorrect reserve fallback that hides ENOSPC until transaction abort, log tree allocations consuming global emergency space, qgroup reservation mismatches, and races on stale `full` reads. `btrfs_block_rsv_full()` is intentionally a lockless fast path using `data_race()`, while precise reads take the reserve spinlock.

Useful tests include metadata ENOSPC stress, delayed-ref heavy workloads, fsync/log-tree fallback under low space, unlink/truncate on nearly full filesystems, qgroup enabled workloads, zoned tree-log reserve selection, chunk/remap operations, transaction abort injection during reserve use/release, and assertions during unmount that long-lived reserves are fully released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/block-rsv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/block-rsv.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/block-rsv.h

## Purpose
`block-rsv.h` declares the Btrfs metadata block reserve abstraction used throughout the filesystem. It defines reserve types, the `struct btrfs_block_rsv` accounting fields, public reserve manipulation APIs, and small inline helpers for returning or reading reserved bytes.

## Important APIs, types, and functions
- `enum btrfs_rsv_type` distinguishes reserve purposes: global, delalloc, transaction, chunk, remap, delayed operations, delayed refs, tree log, empty fallback, and temporary.
- `struct btrfs_block_rsv` stores the target size, current reserved bytes, backing `btrfs_space_info`, spinlock, `full`/`failfast` flags, type, and qgroup reservation size/reserved counters.
- Declarations cover initialization/allocation/freeing, reserve add/check/refill/migrate/use/add-bytes/release, global reserve init/update/release, root reserve initialization, reserve selection for tree block allocation, and truncate cache free-space checking.
- `btrfs_unuse_block_rsv()` returns one tree-block-sized allocation to a reserve and releases any resulting excess.
- `btrfs_block_rsv_full()` is a lockless fast-path fullness check for contexts where a stale value is acceptable.
- `btrfs_block_rsv_reserved()` and `btrfs_block_rsv_size()` provide KCSAN-safe locked reads of mutable counters.

## Control flow
The header’s API describes a simple reserve lifecycle. A caller initializes a reserve and binds it to a metadata-like `space_info`, adds or refills bytes through the implementation, consumes bytes when allocating tree blocks, and releases the remaining size at operation completion. Root and filesystem initialization use the declarations to wire each Btrfs tree or operation class to the correct reserve. `btrfs_unuse_block_rsv()` is the inverse of a single tree block use: it credits bytes back, then lets the implementation free or re-route surplus.

## State and persistence behavior
Reserve state is not persisted on disk. It is an in-memory view of metadata reservation obligations, protected by `struct btrfs_block_rsv::lock` and tied to `btrfs_space_info` accounting. The `full` flag is cached state used by fast paths and can be read without locking only when staleness is acceptable. `failfast` is used by temporary/unbounded operations such as truncate so they can stop and re-reserve instead of consuming emergency space indefinitely.

The qgroup fields track a quota-oriented upper bound rather than exact metadata tree block needs. They are part of the same reserve object so quota release can be correlated with normal metadata reserve release.

## Dependencies and integration points
The header depends only on Linux types/compiler/spinlock definitions plus forward declarations of Btrfs transaction, root, space-info, filesystem, and reserve-flush types. It is included by inode, transaction, delalloc, extent-tree, block-group, and qgroup-related code that needs to reserve or consume metadata.

## Risks and test signals
Risks include callers reading `size`/`reserved` directly without locking, using the wrong reserve type for a tree, forgetting to release temporary reserves, or treating a stale `full` result as authoritative. API changes should be tested with metadata ENOSPC stress, qgroup workloads, fsync/tree-log paths, truncate/iput loops, chunk-tree updates, and unmount assertions that all long-lived reserves have zero size and reserved bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/block-rsv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/btrfs_inode.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/btrfs_inode.h

## Purpose
`btrfs_inode.h` defines the in-memory Btrfs inode extension and the public inode-level APIs used by lookup, directory operations, delalloc, checksumming, NOCOW, fsync logging, orphan cleanup, preallocation, encoded I/O, and inode lifecycle code. It embeds a VFS inode while adding Btrfs-specific roots, extent maps, range state, ordered extents, metadata reservation, logging generation state, compression/defrag properties, and accounting fields.

## Important APIs, types, and functions
- `BTRFS_DIR_START_INDEX` sets the first real directory index after `.` and `..`.
- The anonymous inode runtime flag enum includes fsync/delalloc/defrag/logging/verity/free-space/root-stub state such as `BTRFS_INODE_NEEDS_FULL_SYNC`, `BTRFS_INODE_NO_DELALLOC_FLUSH`, `BTRFS_INODE_FREE_SPACE_INODE`, and `BTRFS_INODE_ROOT_STUB`.
- `struct btrfs_inode` is the core inode container, embedding `struct inode vfs_inode` and Btrfs fields for root ownership, objectid handling, compression, locks, extent maps, range state, log state, delalloc/csum/defrag accounting, inode item flags, a per-inode `btrfs_block_rsv`, delayed nodes, delayed iput linkage, mmap locking, and VFS integration.
- `BTRFS_I()` converts `struct inode *` or `const struct inode *` to the containing Btrfs inode with type-preserving `_Generic`.
- Inline helpers cover inode hashing, inode number handling on 32-bit vs 64-bit systems, inode key construction, size/disk size updates, free-space/data inode tests, outstanding extent tracing, fsync generation state, full-sync marking, compression eligibility, lock assertions, mapping stable-write flags, and experimental folio order setup.
- Function declarations cover checksum calculation/verification, NOCOW checks, delalloc inode lists, lookup/link/unlink/subvolume deletion, truncate, delalloc start/set/clear/merge/split, new inode creation, inode allocation/destruction/drop, iget/get-extent/update/orphan cleanup, delayed iput, preallocation, writeback, encoded read/write, inode search, lock/unlock, inode byte accounting, range-clean assertions, allocation hints, and I/O extent map creation.

## Control flow
The header defines the state that inode implementation files operate on. Lookup/iget code allocates a `struct btrfs_inode`, initializes its root, objectid, VFS inode, extent map tree, range state, block reserve, and counters, then exposes it through the VFS inode. File writes mark delalloc ranges in `io_tree`, update `delalloc_bytes`/`new_delalloc_bytes`/`outstanding_extents`, possibly use the inode’s block reserve, and later run writeback through `btrfs_run_delalloc_range()`. Ordered extents are tracked in the inode’s ordered tree so completion can update metadata, checksums, and logged state.

Fsync and tree logging use `last_trans`, `logged_trans`, `last_sub_trans`, `last_log_commit`, `first_dir_index_to_log`, `last_dir_index_offset`, `last_unlink_trans`, and `last_reflink_trans` to decide whether a fast log is valid or a full inode sync is required. `btrfs_set_inode_last_sub_trans()` records writes after a prior fsync in the same transaction. `btrfs_set_inode_full_sync()` sets the full-sync bit and pessimistically updates reflink tracking while holding appropriate inode or mmap serialization.

Directory operations use `index_cnt`, `dir_index`, `BTRFS_DIR_START_INDEX`, link/unlink declarations, fscrypt names in `btrfs_new_inode_args`, and directory-specific logging offsets. Regular files instead use the union alternatives for delalloc, csum, defrag, reflink, and encoded I/O state. Special free-space inodes are identified by runtime flag and suppress normal outstanding-extent tracing.

## State and persistence behavior
Some fields mirror persisted inode item state: inode number/objectid, generation, `disk_i_size`, inode flags/ro_flags, creation time, and root ownership. Many fields are runtime-only caches or synchronization state: extent maps, `io_tree` state bits, optional `file_extent_tree` for accurate i_size updates when holes are explicit, ordered extent rb-tree, delayed inode list linkage, log mutex, runtime flags, delayed node pointer, delayed iput node, and mmap lock.

Counter fields are carefully protected. The main spinlock protects transaction/log generation counters, delalloc bytes, new delalloc bytes, defrag bytes, disk size, outstanding extents, csum bytes, and file private data setup. `log_mutex` protects directory logging fields. The VFS inode lock or `i_mmap_lock` is required for full-sync transitions and reflink-related state updates. The embedded `btrfs_block_rsv` persists only as in-memory reservation accounting tied to inode operations.

On 32-bit platforms, `struct inode::i_ino` cannot hold the full Btrfs objectid, so `struct btrfs_inode::objectid` stores it separately. Root stub inodes are an exception: `btrfs_ino()` returns the VFS inode number for stubs that represent inaccessible subvolume roots.

## Dependencies and integration points
The header depends on Linux VFS/MM/fscrypt/lockdep primitives, Btrfs tracepoints, `ctree.h`, block reserves, extent maps, and extent I/O trees. It is included by inode implementation, file I/O, tree-log, delayed inode, extent allocation, checksumming, ordered extent, ioctl/encoded I/O, and free-space cache code. It integrates Btrfs root/subvolume identity with the VFS inode model and provides the shared declarations other subsystems need to mutate inode metadata safely.

## Risks and test signals
Risks include stale or incorrectly locked fsync generation state causing missing log replay data, delalloc accounting mismatches leading to ENOSPC or incorrect stat blocks, 32-bit inode number truncation mistakes, root-stub confusion for subvolume snapshots, compression eligibility ignoring NODATACOW/NODATASUM, races between mmap writes and full-sync marking, and failure to clear or merge delalloc/extent state correctly.

Useful tests include fsync after buffered/direct/mmap writes, reflink and dedupe followed by fsync with checksums, directory unlink/relink logging, subvolume root-stub lookup cases, 32-bit build coverage, free-space inode behavior, verity enable serialization, qgroup/delalloc ENOSPC stress, encoded I/O, NOCOW extent checks, preallocation/truncate/contiguous expansion, delayed iput draining, and lockdep/KCSAN runs around inode lock, `i_mmap_lock`, `log_mutex`, and the inode spinlock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/btrfs_inode.h -->
