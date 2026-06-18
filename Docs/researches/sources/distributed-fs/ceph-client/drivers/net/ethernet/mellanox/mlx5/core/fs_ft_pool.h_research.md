# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_ft_pool.h

## Purpose
`fs_ft_pool.h` declares the flow-table size pool API used by mlx5 flow steering to reserve and release firmware-compatible flow table sizes.

## Important APIs, Types, And Functions
- Includes `linux/mlx5/driver.h` and `fs_core.h` so callers can pass `struct mlx5_core_dev` and `enum fs_flow_table_type`.
- `mlx5_ft_pool_init` and `mlx5_ft_pool_destroy` manage `dev->priv.ft_pool`.
- `mlx5_ft_pool_get_avail_sz` reserves an available table size for a given table type and desired size.
- `mlx5_ft_pool_put_sz` releases a previously reserved size.

## Control Flow And State
The header does not implement behavior. Its API implies a lifecycle where the device initializes the pool before flow-table creation, callers reserve a size before creating a hardware table, and callers release that size during flow-table destruction.

## Dependencies And Integration Points
It is an internal mlx5 core header consumed by flow-steering table allocation code and implemented by `fs_ft_pool.c`. The API depends on the flow-table type enum from `fs_core.h` because allocation is capability-sensitive.

## Risks And Edge Cases
Callers must pair each successful reservation with exactly one release and must not pass arbitrary sizes to `mlx5_ft_pool_put_sz`. Since the implementation has fixed firmware bucket assumptions, this header should remain internal rather than becoming a generic allocator contract.

## Test Signals
Compile coverage should ensure all flow-table allocator users include this header cleanly. Runtime signals are successful flow-table creation and teardown across all supported table types without pool exhaustion leaks or invalid-size warnings.
