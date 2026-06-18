# Group Research: group_243_btrfs_linux_sources_local_fs_btrfs_linux_fs_btrfs_block_group_c_sour_3b7dd98056c7

Scope: `Docs/research_subset_a.md`, source tree `sources/local-fs/btrfs-linux`.

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/block-group.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/block-group.c

## Scope

This file implements Btrfs block-group lifecycle, allocation profile selection, free-space cache population, chunk creation/removal coordination, dirty block-group writeback during transaction commit, read-only transitions, unused/reclaim block-group cleanup, logical-to-physical reverse mapping for superblock exclusions, zoned block-group accounting hooks, swapfile block-group pins, and data block-group size-class tracking.

It is the operational implementation behind the declarations in `block-group.h` and depends heavily on space-info accounting, extent/tree roots, transactions, free-space cache/tree, chunk mapping, discard, relocation, scrub, zoned allocation, delayed refs, and sysfs.

## Main APIs And Entry Points

- `btrfs_get_alloc_profile()` combines requested DATA/METADATA/SYSTEM flags with currently available profile bits and balance conversion targets, then reduces them to a usable chunk profile.
- `btrfs_lookup_block_group()`, `btrfs_lookup_first_block_group()`, and `btrfs_next_block_group()` search the fs-wide cached rb-tree of block groups with reference handling.
- `btrfs_inc_nocow_writers()`, `btrfs_dec_nocow_writers()`, and `btrfs_wait_nocow_writers()` protect NOCOW writes from racing read-only transitions, relocation, scrub, and similar block-group state changes.
- `btrfs_cache_block_group()` starts or waits for free-space caching for a block group, except on zoned filesystems and remapped block groups where allocator behavior differs.
- `btrfs_add_new_free_space()` adds free regions to a block group's in-memory free-space cache while excluding superblock and other excluded extents.
- `btrfs_read_block_groups()` reads block-group items at mount, validates them against chunk mappings, initializes `space_info`, sysfs entries, free-space state, zoned state, and global reserves.
- `btrfs_make_block_group()` creates an in-memory block group for a newly allocated chunk and links it into the transaction's pending-new-block-groups list.
- `btrfs_create_pending_block_groups()` completes phase 2 of chunk allocation by inserting block-group items, chunk items when needed, device extent items, and free-space-tree entries.
- `btrfs_chunk_alloc()` is the public phase-1 chunk allocator for data/metadata block groups.
- `check_system_chunk()` and `btrfs_reserve_chunk_metadata()` reserve system metadata for chunk-tree modifications under `fs_info->chunk_mutex`.
- `btrfs_inc_block_group_ro()` and `btrfs_dec_block_group_ro()` transition block groups into and out of read-only state with space-info counter adjustments.
- `btrfs_update_block_group()` transfers bytes between used, reserved, pinned, readonly, and reclaimable accounting when extents are allocated or freed.
- `btrfs_add_reserved_bytes()` and `btrfs_free_reserved_bytes()` maintain reservation counters for allocator-selected block groups.
- `btrfs_start_dirty_block_groups()`, `btrfs_write_dirty_block_groups()`, and `btrfs_setup_space_cache()` prepare and commit dirty block-group item updates plus optional v1 free-space-cache writeback.
- `btrfs_delete_unused_bgs()`, `btrfs_reclaim_block_groups()`, `btrfs_mark_bg_unused()`, and `btrfs_mark_bg_to_reclaim()` drive automatic empty/low-used block-group cleanup.
- `btrfs_remove_block_group()` removes a block group and its persistent metadata as part of chunk removal.
- `btrfs_free_block_groups()` tears down all cached block groups and space-info objects during unmount.
- `btrfs_rmap_block()` maps a physical superblock location back to logical block-group offsets for exclusion.
- `btrfs_freeze_block_group()` and `btrfs_unfreeze_block_group()` delay chunk-map reuse while trim/scrub or similar users still hold deleted block-group references.
- `btrfs_inc_block_group_swap_extents()` and `btrfs_dec_block_group_swap_extents()` pin block groups used by active swapfiles.
- `btrfs_calc_block_group_size_class()`, `btrfs_use_block_group_size_class()`, and `btrfs_block_group_should_use_size_class()` implement data block-group size-class segregation.
- `btrfs_mark_bg_fully_remapped()` and `btrfs_populate_fully_remapped_bgs_list()` handle remapped block groups whose old chunk stripes/device extents still need cleanup.

## Control Flow And Behavior

Allocation profile selection first checks paused/running balance conversion state under `balance_lock`. If a conversion target applies, it returns that target profile. Otherwise it masks profiles by writable device count and selects the highest redundancy available in a fixed order: RAID1C4, RAID6, RAID1C3, RAID5, RAID10, RAID1, DUP, RAID0, then single/no profile.

Block groups live in `fs_info->block_group_cache_tree`, a cached rb-tree keyed by logical start. Lookup increments `refs`; removal erases the rb-node and drops the tree reference. `btrfs_next_block_group()` handles the case where the current group was removed while still referenced by falling back to a fresh lookup at the old end offset.

Free-space caching is asynchronous through `struct btrfs_caching_control`. `caching_thread()` locks the caching control and reads the commit root under `commit_root_sem`. It optionally samples extent items to infer data block-group size class, tries v1 space-cache loading when enabled, otherwise uses the free-space tree or scans the extent tree to discover gaps. Progress wakes allocation waiters after enough free space is found. It finalizes the block group as `BTRFS_CACHE_FINISHED` or `BTRFS_CACHE_ERROR`, clears excluded extents, wakes waiters, and drops the block-group/caching-control references.

Extent-tree free-space loading scans extent and metadata items from the commit root, adding gaps between used extents through `btrfs_add_new_free_space()`. It periodically drops and reacquires locks when rescheduling is needed or `commit_root_sem` is contended. Superblock mirror locations are excluded from free-space accounting through `exclude_super_stripes()` using `btrfs_rmap_block()`.

Mount-time block-group reading walks block-group items from either the block-group tree or extent tree depending on features. Each item is cross-checked against a chunk map for start, length, and type. `read_one_block_group()` creates the in-memory block group, loads used/remap counters, initializes zone info, excludes super stripes, pre-fills free space for empty non-zoned groups, marks full groups cached, links into the rb-tree and space-info lists, sets available allocation profile bits, and queues unused empty groups when appropriate. Rescue paths with missing roots or unsupported readonly features build dummy full block groups from chunk maps.

Chunk allocation is explicitly two phase. Phase 1, `btrfs_chunk_alloc()`, decides whether a data/metadata chunk is needed, serializes with `space_info->chunk_alloc` and `fs_info->chunk_mutex`, checks system chunk reservations, creates the chunk mapping and in-memory block group, and inserts the chunk item into the chunk tree. Phase 2, `btrfs_create_pending_block_groups()`, later inserts the block-group item in the block-group/extent tree and device extent items in the device tree. This separation avoids deadlocks when extent-tree COW triggers chunk allocation while holding btree locks.

System chunks are not allocated through `btrfs_chunk_alloc()`. Callers modifying the chunk tree reserve system space through `check_system_chunk()` or `btrfs_reserve_chunk_metadata()` while holding `chunk_mutex`. If existing system space is insufficient, `reserve_chunk_space()` may create a system chunk and attempt to insert its chunk item, but tolerates some failures because phase 2 can retry.

Block-group removal is a multi-stage transaction path. `btrfs_remove_block_group()` requires the group to be read-only unless it was remapped, clears excluded/special ranges, removes it from allocation clusters, treelog/data relocation tracking, dirty/cache IO lists, the rb-tree, space-info lists, sysfs, free-space cache/tree, and the persistent block-group item. It waits for caching when needed, cancels discard work, removes free-space inodes, adjusts space-info counters, marks the group removed, and only removes the chunk map immediately if no frozen users remain. Otherwise chunk-map removal is deferred until `btrfs_unfreeze_block_group()`.

Unused block-group deletion and reclaim are separate cleaner flows. `btrfs_delete_unused_bgs()` handles empty or effectively empty groups, respecting async discard, zoned unusable space, mixed space-info, active reservations, read-only state, singleton profile groups, pinned extents, and unwritten zoned metadata. `btrfs_reclaim_block_groups()` sorts reclaim candidates by used bytes and relocates low-used groups under an exclusive balance operation, periodically prioritizing unused-group cleanup.

Dirty block groups are transaction-scoped. `btrfs_update_block_group()` changes superblock bytes-used, block-group `used/reserved/pinned`, space-info `bytes_used/bytes_reserved/bytes_pinned`, reclaimable accounting, and dirty-list membership. Dirty list insertion is paired with delayed-ref reservation accounting. Commit paths first try to write easy free-space caches before the commit critical section, then retry and finish dirty block groups inside the critical section.

The v1 free-space cache path uses a hidden free-space inode per block group. `cache_save_setup()` creates or looks up that inode, sets its generation to 0 before writing so failures invalidate the cache, truncates stale cache contents, preallocates cache file space, and transitions `disk_cache_state`. `btrfs_write_dirty_block_groups()` waits for outstanding cache IO and updates block-group items before commit completes.

Read-only transitions check swapfile users, account available bytes into `space_info->bytes_readonly`, and on zoned filesystems migrate `zone_unusable` into readonly accounting. The public `btrfs_inc_block_group_ro()` coordinates with transactions and dirty-block-group writeback, optionally preallocates replacement chunks, avoids system chunk storms, and uses `ro_block_group_mutex`.

Size classes apply only to non-zoned data-only block groups. During caching, the code samples up to five extent items to infer the smallest observed size class. During allocation, `btrfs_use_block_group_size_class()` sets an empty group's class or rejects mismatched allocations unless the allocator is in forced wrong-size-class mode.

Fully remapped block groups are tracked so dead chunk stripes/device extents are eventually removed. Async discard sets `BLOCK_GROUP_FLAG_STRIPE_REMOVAL_PENDING`; synchronous handling moves the group to `fully_remapped_bgs`. Mount-time population compares the block-group cache tree and mapping tree to find remapped groups whose identity remap count reached zero but whose chunk map still has stripes.

## State And Data Structures

- `struct btrfs_block_group` fields used here include `start`, `length`, `used`, `reserved`, `pinned`, `delalloc_bytes`, `bytes_super`, `remap_bytes`, `identity_remap_count`, `last_*` committed values, `flags`, `runtime_flags`, `ro`, `cached`, `disk_cache_state`, `caching_ctl`, `free_space_ctl`, `space_info`, rb/list nodes, `reservations`, `nocow_writers`, `swap_extents`, zoned offsets/capacity/write pointer, size class, and discard state.
- `fs_info` state touched includes block-group rb-tree and lock, mapping tree, space-info list, profile bits, balance control, chunk mutex, caching/unused/reclaim/fully-remapped lists, discard control, delalloc root lock, global roots, global block reserves, transaction list, zoned active groups, and feature flags.
- Transaction state includes `new_bgs`, `dirty_bgs`, `io_bgs`, `deleted_bgs`, delayed-ref reservation accounting, pinned extents, cache write mutex, writer wait queue, and transaction flags such as dirty-bg run and cache ENOSPC.
- Persistent items handled include block-group items, chunk items, device extent items, free-space tree entries, free-space cache inode items, superblock bytes-used, and feature/profile bits.
- Runtime flags include `BLOCK_GROUP_FLAG_NEW`, `REMOVED`, `CHUNK_ITEM_INSERTED`, `NEEDS_FREE_SPACE`, `FREE_SPACE_ADDED`, `FULLY_REMAPPED`, and `STRIPE_REMOVAL_PENDING`.

## Dependencies

- Space accounting: `space-info.c`, metadata reservation code, global and delayed-ref block reserves.
- Allocation and mapping: chunk creation/removal, chunk map rb-tree, device extents, RAID profile helpers, zoned allocation activation.
- Free-space mechanisms: v1 free-space cache inode, free-space tree, in-memory free-space cache and bitmap/extent conversion thresholds.
- Transactions: delayed refs, transaction commit phases, dirty block-group cache writeback, commit-root scanning.
- Relocation, balance, scrub, discard, swapfile activation, tree log cleanup, sysfs block-group type registration, rescue mount paths, and feature flags.

## Risks And Invariants

- Chunk allocation must preserve the phase-1/phase-2 split. Inserting block-group items too early can deadlock with extent-tree COW paths.
- `chunk_mutex` is central for system space reservation and chunk-tree modifications. System chunk allocation through the wrong path risks lock recursion and chunk-array exhaustion.
- Dirty block-group list membership owns delayed-ref reservation increments. Missing the paired decrement leaks reservation pressure; double decrement corrupts accounting.
- Block-group removal must remove free-space/tree metadata and persistent block-group items before marking removed, while retaining chunk maps if trim/scrub/frozen users may still need stable logical-to-physical mappings.
- Read-only transitions must wait for block-group reservations and NOCOW writers where required. Otherwise relocation, scrub, and direct NOCOW writes can race.
- Free-space cache loading scans commit roots without normal btree locking. It depends on `commit_root_sem`, skip-locking paths, and safe rescheduling points.
- Zoned filesystems have special invariants around `alloc_offset`, `zone_unusable`, `meta_write_pointer`, active zones, and the prohibition on superblock stripes inside sequential block groups.
- Swapfile extents prevent read-only transitions and block-group removal. `swap_extents` is protected by the block-group spinlock.
- Size-class assignment is best effort and intentionally approximate during cache loading, but allocation-time races must return `-EAGAIN` unless forced.
- Async discard can interpose on unused and fully-remapped block-group cleanup, so list placement and runtime flags must remain consistent across remount/commit boundaries.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/block-group.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/block-group.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/block-group.h

## Scope

This header defines the Btrfs block-group data model, runtime state enums, chunk allocation force modes, caching-control state, inline helpers, and public block-group/chunk-management APIs implemented mostly by `block-group.c`.

## Types And Data Structures

- `enum btrfs_disk_cache_state` tracks v1 free-space-cache persistence: written, error, clear, setup.
- `enum btrfs_block_group_size_class` categorizes data-only block groups as unset, small up to 128 KiB, medium up to 8 MiB, or large.
- `enum btrfs_discard_state` models async discard phases: extents, bitmaps, reset cursor, and fully-remapped cleanup.
- `enum btrfs_chunk_alloc_enum` controls chunk allocation pressure: no force, limited, force, and force-for-extent with zoned activation behavior.
- `enum btrfs_block_group_flags` defines runtime bits such as inode reference held, removed, relocating/copying state, chunk item inserted, active zone, free-space-tree needs, new transaction block group, fully remapped, and stripe removal pending.
- `enum btrfs_caching_type` tracks free-space cache state: no cache, started, finished, error.
- `struct btrfs_caching_control` owns async caching work, wait queue, mutex, block-group pointer, progress counter, list node, and refcount.
- `struct btrfs_block_group` is the central in-memory representation for a logical chunk/block group. It stores accounting (`used`, `reserved`, `pinned`, `delalloc_bytes`, `bytes_super`, remap counters), profile/length/start, committed last values, free-space cache thresholds, locks, rb/list nodes, free-space cache controller, space-info link, dirty/cache IO lists, reservation and NOCOW atomics, discard state, swap extent count, zoned allocation fields, chunk physical map, active-zone list, and size class.

## Inline Helpers

- `btrfs_block_group_end()` returns `start + length`.
- `btrfs_is_block_group_used()` checks used, reserved, pinned, and remap bytes under the block-group lock.
- `btrfs_is_block_group_data_only()` excludes mixed data/metadata groups from data-only heuristics.
- `btrfs_block_group_available_space()` computes available bytes after used, pinned, reserved, super, and zoned-unusable space.
- Allocation-profile wrappers return data, metadata, or system profile via `btrfs_get_alloc_profile()`.
- `btrfs_block_group_done()` uses a memory barrier and tests finished/error cache states.

## Public API Surface

The header exposes APIs for block-group lookup/refcounting, NOCOW writer tracking, reservation waiting, free-space cache loading, free-space insertion, block-group removal, unused/reclaim queues, mount-time block-group reading, new block-group creation, pending phase-2 creation, read-only reference transitions, dirty block-group transaction handling, block/space accounting, chunk allocation, system chunk metadata reservation, teardown, reverse mapping, freeze/unfreeze, swap extent pinning, size-class use, and fully remapped block-group cleanup.

## Dependencies And Consumers

The header includes kernel atomic/list/rbtree/rwsem primitives, UAPI Btrfs tree definitions, and `free-space-cache.h`. It forward-declares Btrfs core types to avoid pulling in broad definitions. It is used by allocation, extent-tree, transaction, inode, relocation, scrub, discard, zoned, and swapfile paths that need block-group state or helper APIs.

## Risks And Invariants

- Most accounting fields require `bg->lock`; list membership often requires fs-wide locks or `groups_sem`.
- `bg_list` is intentionally reused across several fs and transaction lists, so callers must respect ownership and refcount rules.
- `reservations` and `nocow_writers` are waitable atomics and are part of correctness for read-only transitions.
- `frozen` prevents logical/physical reuse after deletion while transactionless trim/scrub users may still hold references.
- Zoned-only fields must not be treated as valid for regular filesystems.
- The struct encodes multiple subsystems in one object, so field ownership is split among allocator, free-space cache, transaction commit, discard, zoned, swap, and relocation code.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/block-group.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/block-rsv.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/block-rsv.c

## Scope

This file implements Btrfs metadata block reserves, which are logical buckets for metadata reservations. It handles reserve initialization, reservation/refill/release, migration between reserves, use during tree block allocation, global reserve sizing, root-to-reserve assignment, and fallback behavior when a reserve is short.

## Main APIs And Entry Points

- `btrfs_init_block_rsv()` initializes a reserve with lock and type.
- `btrfs_init_metadata_block_rsv()` initializes a reserve and attaches it to metadata `space_info`.
- `btrfs_alloc_block_rsv()` and `btrfs_free_block_rsv()` allocate/free dynamic reserves and release all held bytes.
- `btrfs_block_rsv_add()` reserves metadata bytes from `space_info` and adds them to reserve size and reserved counters.
- `btrfs_block_rsv_refill()` reserves only the gap needed to reach a requested reserved byte count.
- `btrfs_block_rsv_release()` releases bytes from a reserve, optionally returning excess to delayed-ref or global reserves before freeing bytes to `space_info->bytes_may_use`.
- `btrfs_block_rsv_migrate()` consumes bytes from one reserve and adds them to another.
- `btrfs_block_rsv_use_bytes()` consumes reserved bytes for a tree-block allocation.
- `btrfs_block_rsv_add_bytes()` credits bytes directly to a reserve.
- `btrfs_update_global_block_rsv()` sizes and fills the global reserve from root-tree, extent-tree, checksum-tree, free-space-tree, block-group-tree, stripe-tree, and unlink fallback needs.
- `btrfs_init_root_block_rsv()` assigns each root to the reserve appropriate for its tree type.
- `btrfs_init_global_block_rsv()` attaches fs-wide reserves to their space-info objects and initializes the global reserve.
- `btrfs_release_global_block_rsv()` drains global reserves during teardown and warns on leaked reserve state.
- `btrfs_use_block_rsv()` selects and consumes the reserve to use for COW/tree block allocation, with fallback to direct reservation, global reserve, or emergency reservation.
- `btrfs_check_trunc_cache_free_space()` verifies that a reserve has enough bytes to safely truncate a free-space cache inode.

## Reserve Model

Each `struct btrfs_block_rsv` has:

- `size`: target logical reservation size.
- `reserved`: currently reserved metadata bytes.
- `space_info`: the metadata/system/remap pool backing the reserve.
- `full`: fast-path fullness indicator.
- `failfast`: used by bounded temporary operations such as truncate/iput.
- `type`: reserve category.
- `qgroup_rsv_size` and `qgroup_rsv_reserved`: quota-group metadata reservation analogues.

The file documents the intended behavior of reserve types:

- Transaction, delayed ops, and chunk reserves behave as normal scoped reservations.
- Global reserve is a safety buffer for under-estimated delayed refs and special ENOSPC recovery paths.
- Delalloc reserve is calculated per inode and backs inode/file-extent/csum metadata updates.
- Delayed refs reserve tracks dynamic delayed-ref work and is the preferred sink for excess returned by other reserves.
- Empty reserve is a fallback for operations without a dedicated bucket.
- Temp reserve is used for unbounded operations that perform work until space runs out, then retry with a new reservation.

## Control Flow And Behavior

`block_rsv_release_bytes()` is the core release helper. It subtracts from reserve `size`, clamps `reserved` down to `size`, marks the reserve full when appropriate, computes qgroup excess, optionally tops up a destination reserve, and frees remaining bytes from `space_info->bytes_may_use`.

`btrfs_block_rsv_release()` chooses a destination for excess bytes. Delayed refs release to the global reserve. Other non-global reserves release to the delayed refs reserve if it is not full and uses the same `space_info`. Otherwise excess returns to the space-info pool.

`btrfs_use_block_rsv()` first chooses a reserve with `get_block_rsv()`. Shareable roots, UUID root updates, and csum-tree updates while adding checksums use the transaction reserve. Otherwise the root's assigned reserve is used, falling back to the empty reserve. If the reserve has enough bytes, it consumes them. If not, `failfast` reserves return immediately; global reserve shortage triggers a global reserve recomputation once; non-delayed-ref shortages can warn under ENOSPC debug.

If the selected reserve is short, `btrfs_use_block_rsv()` tries a direct no-flush metadata reservation. Log-tree allocations fail after this point rather than consuming global reserve, forcing fsync to fall back to full transaction commit. Non-global metadata reserves can then borrow from the global reserve if they share the same `space_info`. As a last resort, the function attempts an emergency flush reservation.

`btrfs_update_global_block_rsv()` computes global reserve size from global root usage, selected global roots, optional block-group and RAID stripe roots, plus unlink and delayed-ref fallback items. It caps the reserve at 512 MiB, updates `bytes_may_use` under `space_info->lock`, and can force a metadata chunk allocation if the global reserve size reaches total metadata bytes.

Root reserve assignment is policy-driven. Extent, checksum, free-space, block-group, and RAID stripe roots use delayed refs reserve. Root, device, and quota roots use global reserve. Chunk root uses chunk reserve. Tree log uses treelog reserve. Remap tree uses remap reserve. Other roots default to no root reserve.

## Dependencies

- Space-info metadata reservation and ticket granting.
- Transaction handles and `trans->block_rsv`.
- Root types and feature flags such as block-group tree and RAID stripe tree.
- Delayed refs and unlink metadata sizing helpers.
- Zoned mode special treelog reserve subgroup.
- Metadata sizing helpers for inserts, updates, and delayed refs.

## Risks And Invariants

- Reserve `size` and `reserved` are protected by the reserve spinlock; space-info counter changes require `space_info->lock`.
- Excess release must not move bytes between reserves with different `space_info`.
- Tree-log allocations intentionally avoid global reserve fallback to keep fsync optimization from consuming emergency metadata.
- Global reserve recalculation must include all global roots that can be touched during delayed refs or commit work.
- `btrfs_release_global_block_rsv()` warnings are leak detectors for reserve accounting.
- `failfast` temp reserves rely on callers handling `-ENOSPC` by unwinding and retrying with a fresh reservation.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/block-rsv.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/block-rsv.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/block-rsv.h

## Scope

This header declares the Btrfs block-reserve types, `struct btrfs_block_rsv`, core reserve management APIs, and small inline helpers for reserve fullness, reserved byte reads, size reads, and unuse behavior.

## Types And Structures

`enum btrfs_rsv_type` defines reserve categories:

- `BTRFS_BLOCK_RSV_GLOBAL`
- `BTRFS_BLOCK_RSV_DELALLOC`
- `BTRFS_BLOCK_RSV_TRANS`
- `BTRFS_BLOCK_RSV_CHUNK`
- `BTRFS_BLOCK_RSV_REMAP`
- `BTRFS_BLOCK_RSV_DELOPS`
- `BTRFS_BLOCK_RSV_DELREFS`
- `BTRFS_BLOCK_RSV_TREELOG`
- `BTRFS_BLOCK_RSV_EMPTY`
- `BTRFS_BLOCK_RSV_TEMP`

`struct btrfs_block_rsv` stores target size, reserved bytes, backing `space_info`, lock, fullness/failfast booleans, reserve type, and qgroup reservation mirrors. The qgroup fields are intentionally separate because quota groups account net metadata changes differently from the normal nodesize-based reserve model.

## Public API Surface

The header exposes initialization, allocation, free, add, check, refill, migrate, use, add-bytes, release, global reserve update/init/release, root reserve assignment, reserve selection/use for tree allocation, and truncate-cache free-space checking.

## Inline Helpers

- `btrfs_unuse_block_rsv()` returns a block to a reserve and then releases excess according to normal reserve-release policy.
- `btrfs_block_rsv_full()` is a data-race-tolerant fast path for fullness checks.
- `btrfs_block_rsv_reserved()` returns reserved bytes under lock.
- `btrfs_block_rsv_size()` returns size under lock.

## Dependencies And Consumers

The header forward-declares core Btrfs types and depends only on basic Linux types and spinlocks. It is consumed by transaction, extent allocation, inode/delalloc, block-group, tree-log, remap, delayed refs, and teardown paths.

## Risks And Invariants

- Direct field access can trigger KCSAN warnings or observe unstable values; helpers should be used where stale reads are acceptable.
- `full` is explicitly a fast-path hint, not a fully synchronized guarantee.
- Qgroup reserve counters are not equivalent to normal metadata reserve counters and must be updated with qgroup-specific semantics.
- `failfast` changes ENOSPC behavior and should be used only by callers prepared to retry bounded work.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/block-rsv.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/btrfs_inode.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/btrfs_inode.h

## Scope

This header defines the in-memory Btrfs inode structure, inode runtime flags, inode helper functions, and public inode-related APIs implemented across `inode.c` and related Btrfs files. It connects VFS inode state to Btrfs extent maps, extent I/O state, delalloc accounting, ordered extents, fsync log state, per-inode metadata reserves, delayed inode/iput handling, compression policy, and encoded I/O.

## Runtime Flags

The anonymous enum defines inode runtime flags including:

- `BTRFS_INODE_FLUSH_ON_CLOSE` for ordered close behavior after truncate/write.
- `BTRFS_INODE_DUMMY` and `BTRFS_INODE_ROOT_STUB` for special placeholder inodes.
- `BTRFS_INODE_IN_DEFRAG`, `BTRFS_INODE_HAS_ASYNC_EXTENT`, and `BTRFS_INODE_NEEDS_FULL_SYNC`.
- `BTRFS_INODE_COPY_EVERYTHING` and `BTRFS_INODE_HAS_PROPS`.
- `BTRFS_INODE_SNAPSHOT_FLUSH` for snapshot delalloc flushing.
- `BTRFS_INODE_NO_XATTRS` and `BTRFS_INODE_NO_CAP_XATTR` for log/xattr optimizations.
- `BTRFS_INODE_NO_DELALLOC_FLUSH` to avoid self-deadlock when dirty pages and locked ranges would be flushed during transaction reservation.
- `BTRFS_INODE_VERITY_IN_PROGRESS`.
- `BTRFS_INODE_FREE_SPACE_INODE`.
- `BTRFS_INODE_COW_WRITE_ERROR` to force ordered extent wait/full fsync behavior after failed COW writeback.

## Main Data Structure

`struct btrfs_inode` embeds `struct inode vfs_inode` and adds Btrfs-specific state:

- Root identity: `root`, 32-bit-only `objectid`, and helpers for inode number/key.
- Compression policy: `prop_compress`, `defrag_compress`, and `defrag_compress_level`.
- Main spinlock protecting log counters, delalloc counters, disk size, outstanding extents, checksum bytes, VFS block usage, and file private-data setup.
- Extent state: `extent_tree`, `io_tree`, and optional `file_extent_tree`.
- Logging: `log_mutex`, `last_trans`, `logged_trans`, `last_sub_trans`, `last_log_commit`, `last_unlink_trans`, and `last_reflink_trans`.
- Delalloc and extent accounting: `outstanding_extents`, `delalloc_bytes`, `new_delalloc_bytes`, `defrag_bytes`, `csum_bytes`, and embedded `block_rsv`.
- Ordered data: `ordered_tree_lock`, `ordered_tree`, and cached last ordered rb-node.
- Directory-specific state: `index_cnt`, `dir_index`, `first_dir_index_to_log`, and `last_dir_index_offset`.
- Relocation/root-stub union state: `reloc_block_group_start` or `ref_root_id`.
- On-disk inode flags split into `flags` and `ro_flags`.
- Delayed infrastructure: `delayed_node`, `delayed_iput`.
- Creation time fields `i_otime_sec` and `i_otime_nsec`.
- `i_mmap_lock` for mmap/write coordination.

## Inline Helpers

- `btrfs_get_first_dir_index_to_log()` and `btrfs_set_first_dir_index_to_log()` use READ/WRITE_ONCE.
- `BTRFS_I()` is a type-checked, const-preserving container conversion from VFS inode.
- `btrfs_inode_hash()` hashes objectid and root objectid, with 32-bit folding on 32-bit platforms.
- `btrfs_ino()` returns a full 64-bit inode number, using `objectid` on 32-bit platforms except root stubs.
- `btrfs_get_inode_key()` builds the inode item key.
- `btrfs_set_inode_number()` updates both Btrfs objectid and VFS inode number as required.
- `btrfs_i_size_write()` updates VFS `i_size` and Btrfs `disk_i_size`.
- `btrfs_is_free_space_inode()` and `is_data_inode()` classify special inodes.
- `btrfs_mod_outstanding_extents()` updates outstanding extent count and emits trace events except for free-space inodes.
- `btrfs_set_inode_last_sub_trans()` records a file change against the root log transaction.
- `btrfs_set_inode_full_sync()` sets full fsync state and conservatively updates `last_reflink_trans`.
- `btrfs_inode_in_log()` checks whether an inode is already safely represented in the log.
- `btrfs_inode_can_compress()` rejects compression when NODATACOW or NODATASUM is set.
- `btrfs_assert_inode_locked()` checks VFS inode lock ownership.
- `btrfs_update_inode_mapping_flags()` toggles stable writes based on NODATASUM.
- `btrfs_set_inode_mapping_order()` configures folio order range under experimental block-size support.

## Declared API Surface

The header declares APIs for:

- Block checksum calculation and verification.
- Data checksum validation.
- NOCOW extent checks.
- Delalloc inode list management and delalloc extent state callbacks.
- Directory lookup, index allocation, link/unlink, subvolume deletion, and truncate-block handling.
- Delalloc flushing across roots and writeback ranges.
- New inode preparation, creation, destruction of args, and subvolume inode creation.
- Inode allocation/free/destroy/drop and cache slab init/teardown.
- Inode lookup by root/path and extent map lookup/creation.
- Inode item update and fallback update.
- Orphan add/cleanup, continuous expansion, delayed iput handling.
- Preallocation with or without an existing transaction.
- COW writepage fixup and delalloc range execution.
- Encoded read/write helpers and compressed encoded I/O.
- In-memory inode search by minimum inode number.
- Inode lock/unlock wrappers supporting shared, trylock, and mmap locking.
- Inode byte accounting and range-clean assertions.
- Extent allocation hinting and I/O extent-map creation.
- `btrfs_dentry_operations`.

## Dependencies And Consumers

The header depends on VFS/MM types, fscrypt, tracepoints, Btrfs ctree definitions, block reserves, extent maps, and extent I/O trees. It is consumed broadly by inode, file, ordered-data, extent I/O, direct I/O, ioctl, tree-log, relocation, free-space cache, verity, and directory operation code.

## Risks And Invariants

- Many `struct btrfs_inode` fields have mode-specific meanings through unions. Callers must only use file fields for files and directory fields for directories.
- `inode->lock` protects several independent-looking counters and fsync fields; updating them without the lock risks fsync/log replay bugs or accounting races.
- `BTRFS_INODE_NO_DELALLOC_FLUSH` is a deadlock avoidance flag and must be set only around contexts that hold file-range locks while reserving transaction space.
- Full fsync marking must preserve reflink-related pessimism to avoid logging incomplete shared checksum/extents state.
- 32-bit inode number handling differs from 64-bit platforms and root stubs are a special case.
- `disk_i_size` and VFS `i_size` intentionally differ during ordered writeback; helpers should be used where both must move together.
- Free-space inodes suppress some tracing/accounting paths and have special behavior in block-group/free-space-cache code.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/btrfs_inode.h -->