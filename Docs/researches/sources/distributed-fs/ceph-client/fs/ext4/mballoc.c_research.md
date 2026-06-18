# sources/distributed-fs/ceph-client/fs/ext4/mballoc.c

## Purpose
`mballoc.c` implements ext4's multiblock allocator: the block/cluster allocation, preallocation, free, discard/TRIM, and allocator-statistics machinery used by ext4 regular data and metadata allocation paths. It keeps an in-memory buddy view of each block group's free clusters, overlays active preallocation descriptors on top of the on-disk block bitmap, and updates persistent bitmaps and group descriptors under journal control.

This file is not just a search routine. It owns the lifecycle of allocator state (`ext4_mb_init()`/`ext4_mb_release()` and module slab caches), the public allocation/free entry points (`ext4_mb_new_blocks()`, `ext4_free_blocks()`, `ext4_group_add_blocks()`), fast-commit replay helpers, delayed post-commit freeing (`ext4_process_freed_data()`), fstrim handling (`ext4_trim_fs()`), and range query support (`ext4_mballoc_query_range()`).

## Important APIs, Types, And Functions
Allocator entry points are `ext4_mb_new_blocks()`, `ext4_free_blocks()`, `ext4_group_add_blocks()`, `ext4_trim_fs()`, `ext4_mballoc_query_range()`, `ext4_discard_preallocations()`, `ext4_process_freed_data()`, `ext4_mb_mark_bb()`, `ext4_mb_prefetch()`, `ext4_mb_prefetch_fini()`, `ext4_mb_init()`, `ext4_mb_release()`, `ext4_init_mballoc()`, and `ext4_exit_mballoc()`.

Core state comes from `mballoc.h`: `struct ext4_allocation_context` carries the original, normalized goal, best, and final extents plus scan criteria, prefetch state, flags, selected PA, locality group, and pinned buddy-cache folios. `struct ext4_buddy` binds a loaded block group's in-core bitmap, buddy bitmap, group info, folios, and superblock. `struct ext4_prealloc_space` tracks inode or locality-group preallocations. `struct ext4_free_data` records blocks freed in a still-uncommitted journal transaction.

Important internal groups are bitmap/buddy primitives, buddy cache lifecycle, group selection, optimized xarray scan structures, preallocation lifecycle, and persistent bitmap updates through `ext4_mb_mark_context()` and `ext4_mb_mark_diskspace_used()`.

## Control Flow
`ext4_mb_new_blocks()` handles fast-commit replay with `ext4_mb_new_blocks_simple()`, reserves clusters and quota for normal allocations, initializes an allocation context, and tries preallocation before normalized buddy allocation. `ext4_mb_regular_allocator()` tries the exact goal first, then scans groups through `CR_POWER2_ALIGNED`, `CR_GOAL_LEN_FAST`, `CR_BEST_AVAIL_LEN`, `CR_GOAL_LEN_SLOW`, and `CR_ANY_FREE`.

Candidate groups are checked cheaply before buddy load when possible, then locked and scanned. A selected extent is marked used in-core by `ext4_mb_use_best_found()`, which also pins buddy-cache folios and creates a PA if the allocator found more space than the caller requested. `ext4_mb_mark_diskspace_used()` persists the allocation. Error paths reverse in-core allocation or PA accounting before releasing the context.

Freeing flows through `ext4_free_blocks()` into `ext4_mb_clear_bb()`. The on-disk bitmap is cleared first; reuse is immediate only for safe cases. Journaled metadata or ordered-data frees are stored as `ext4_free_data` and released to the buddy after commit by `ext4_process_freed_data()`. `ext4_trim_fs()` walks groups and temporarily marks free extents used while discard is issued. `ext4_mballoc_query_range()` iterates free extents with caller callbacks.

## State And Persistence Behavior
Persistent state includes block bitmaps, group descriptor free-cluster counters, flex counters, metadata checksums, quota, and journaled metadata buffers. `ext4_mb_mark_context()` centralizes persistent bitmap mutation and checksum/counter updates.

In-memory state includes the buddy-cache inode, `ext4_group_info`, optimized scan xarrays, preallocation descriptors, locality-group lists, and post-commit-free rb-trees. The key invariant is that the in-core buddy equals the on-disk bitmap plus active preallocation descriptors, so preallocated blocks are treated as unavailable until used or discarded.

Freed data can be cleared from disk but not yet reusable. The per-group `bb_free_root` and superblock freed-data lists hold such ranges until jbd2 commit completion, and the buddy folios are pinned so reinitialization from disk does not expose them early.

## Dependencies And Integration Points
The file depends on ext4 internals, jbd2, buffer heads, folios/page cache, block discard, slab caches, xarrays, rb-trees, RCU, per-CPU counters, quota, tracepoints, and KUnit static stubs. It integrates with ext4 mapping/allocation, truncate, resize, migration, fast commit replay, fstrim, proc/sysfs stats, online resize, and mount/unmount allocator setup.

## Risks And Edge Cases
Major risks are divergence among disk bitmap, buddy bitmap, PA descriptors, group counters, and delayed-free trees; race windows during PA use/deletion and buddy initialization; quota/reservation rollback under ENOSPC; bigalloc cluster/block conversion; cross-group frees; corruption handling that intentionally leaks unsafe blocks; and TRIM temporarily removing free ranges while the group lock is dropped for discard I/O.

Fast-commit replay bypasses normal allocation and must tolerate idempotent bitmap operations, including already-free blocks that trigger buddy regeneration.

## Test Signals
KUnit should exercise bit helpers, buddy generation/load/unload, `mb_mark_used()`, `mb_free_blocks()`, replay simple allocation, and diskspace marking. Functional tests should cover exact goal allocation, power-of-two and stripe-aligned scans, optimized scan on/off, ENOSPC with PA discard retry, inode/group PA lifecycle, delayed-free commit release, bigalloc partial-cluster frees, cross-group frees, online resize additions, fstrim, metadata-overlap detection, quota failure, and corrupted bitmap/group descriptor handling. Tracepoints and `mb_stats`/group summaries are useful runtime signals.
