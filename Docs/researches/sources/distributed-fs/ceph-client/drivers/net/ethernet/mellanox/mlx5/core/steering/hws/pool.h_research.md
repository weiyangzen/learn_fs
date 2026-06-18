# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/pool.h

## Purpose
`pool.h` declares the generic HWS STE/STC pool data model. It defines pool resource types, allocation chunks, pool attributes, database backends, function-pointer hooks, and inline helpers for base IDs and fullness checks.

## Important APIs, types, and functions
`enum mlx5hws_pool_type` distinguishes STE and STC pools. `struct mlx5hws_pool_chunk` carries offset and order. `struct mlx5hws_pool_resource` stores base object ID and range. `enum mlx5hws_pool_flags` enables buddy allocation. `enum mlx5hws_pool_optimize` controls original/mirror allocation optimization. `struct mlx5hws_pool_attr` configures pool type, table type, flags, optimization, and allocation size.

`struct mlx5hws_pool_db` stores bitmap or buddy backend state. `struct mlx5hws_pool` combines context, type, flags, mutex, size, available count, table type, resources, backend, and backend callbacks. Public functions create/destroy pools and allocate/free chunks. Inline helpers return base IDs and test empty/full state under the pool lock.

## Control flow
The header has no substantial runtime flow aside from inline getters and lock-protected `mlx5hws_pool_empty()` / `mlx5hws_pool_full()`. Implementation in `pool.c` fills callback pointers based on bitmap or buddy backend.

## State and persistence behavior
The pool struct is persistent runtime state for firmware STE/STC ranges. Resource base IDs remain valid until destroy. Backend state tracks free offsets. `available_elems` mirrors backend free space and is used by fullness helpers and destroy checks.

## Dependencies and integration points
The header depends on HWS context/table enums, Linux mutexes and bit operations, and the HWS buddy allocator type. It is consumed by context, matcher, action, and action STE pool code.

## Risks and edge cases
The backend function pointers must be initialized before allocation. The fullness helpers rely on `available_elems` being accurate. Optimization modes can create zero-sized original or mirror resources, so base-ID callers must use the right side for their table direction. Chunk order must match the backend capabilities.

## Test signals
Build coverage and generic pool runtime tests for bitmap and buddy modes, full/empty helpers, base ID access, and invalid allocation orders are the main signals.
