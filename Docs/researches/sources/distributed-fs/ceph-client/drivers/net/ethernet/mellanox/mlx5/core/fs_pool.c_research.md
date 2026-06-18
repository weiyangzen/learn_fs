# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_pool.c

## Purpose
`fs_pool.c` implements a generic bulk-object pool for flow-steering resources. It tracks free indexes inside bulk allocations with bitmaps and moves bulks between fully-used, partially-used, and unused lists.

## Important APIs, Types, And Functions
- `mlx5_fs_bulk_init`, `mlx5_fs_bulk_bitmap_alloc`, `mlx5_fs_bulk_cleanup`, and `mlx5_fs_bulk_get_free_amount` manage per-bulk length and free bitmap state.
- `mlx5_fs_pool_init` initializes pool lists, counters, lock, callbacks, and device/context pointers.
- `mlx5_fs_pool_cleanup` destroys all bulks still on the pool lists through caller-supplied `bulk_destroy`.
- `mlx5_fs_pool_acquire_index` returns a `struct mlx5_fs_pool_index` from a partially used, unused, or newly created bulk.
- `mlx5_fs_pool_release_index` marks an index free and either moves the bulk to the appropriate list or destroys it when unused capacity exceeds the dynamic threshold.

## Control Flow And State
Acquire takes `pool_lock`, prefers partially used bulks, then unused bulks, then allocates a new bulk via `ops->bulk_create`. It clears the selected free bit, decrements available units, increments used units, and updates list placement. Release sets the bit back, increments available units, decrements used units, moves a formerly full bulk to partial use, and for fully free bulks either returns them to the unused list or destroys them if the pool is over threshold.

## Dependencies And Integration Points
The file depends on kernel bitmaps, lists, mutexes, and the callback table in `fs_pool.h`. `fs_counters.c` is a direct consumer, using the pool for firmware bulk flow counters, but the abstraction can serve other bulk-backed flow-steering resources.

## Risks And Edge Cases
The bitmap starts with all bits set to mean free; misuse of bit semantics can invert allocation. `mlx5_fs_pool_acquire_from_list` moves list entries based on free count and caller intent, so list corruption would affect all future allocations. Cleanup calls `bulk_destroy` even for fully used bulks and relies on the backend to reject busy destruction; callers should drain users before cleanup.

## Test Signals
Test acquire/release ordering, transitions between unused/partial/full lists, bulk allocation failure, threshold-triggered destruction, double release returning `-EINVAL`, and cleanup with both empty and busy bulks.
