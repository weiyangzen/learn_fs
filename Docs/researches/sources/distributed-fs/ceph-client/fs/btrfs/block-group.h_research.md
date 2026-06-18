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
