# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_ft_pool.c

## Purpose
`fs_ft_pool.c` tracks coarse flow-table capacity buckets for mlx5 firmware flow tables. Firmware does not expose live pool availability, so the driver keeps software counts for a fixed set of supported table sizes.

## Important APIs, Types, And Functions
- `FT_POOLS` lists supported flow table sizes from large to small plus a size-1 termination-table bucket.
- `struct mlx5_ft_pool` stores remaining table counts per bucket.
- `mlx5_ft_pool_init` allocates and initializes `dev->priv.ft_pool`.
- `mlx5_ft_pool_destroy` frees the pool.
- `mlx5_ft_pool_get_avail_sz` selects and reserves a bucket at least as large as the desired size, or the largest available bucket when `desired_size == MLX5_FS_MAX_POOL_SIZE`.
- `mlx5_ft_pool_put_sz` returns a previously reserved size to the matching bucket.

## Control Flow And State
Initialization derives each bucket count from a fixed 16 MiB virtual region divided by that bucket size. Allocation scans from the smallest bucket upward, filters by remaining count and per-table-type `log_max_ft_size` capability, reserves the selected bucket by decrementing its count, and returns the selected size. Release scans for an exact bucket-size match and increments the count.

## Dependencies And Integration Points
The file depends on `fs_ft_pool.h`, `fs_core.h`, `mlx5_core_dev`, and `MLX5_CAP_FLOWTABLE_TYPE` capability lookup. It integrates with flow-table creation code that needs a firmware-compatible table size and must return the size on destroy.

## Risks And Edge Cases
The pool is purely software accounting; if firmware behavior or supported bucket sizes change, accounting may diverge. There is no visible lock in this file, so callers must ensure serialization around `ft_left` updates. Releasing an unknown size only warns, which can hide leaks or double-release asymmetry. Allocation returning 0 means no bucket is available and must be handled by the caller.

## Test Signals
Validate bucket selection for exact, smaller, maximum, and unsupported sizes; allocation exhaustion and subsequent release; capability-limited maximum table sizes; termination-table size handling; and warning behavior for invalid release sizes.
