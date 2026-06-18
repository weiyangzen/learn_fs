# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/buddy.h

## Purpose
`buddy.h` declares the HWS buddy allocator used by pool implementations that need variable-sized allocations from a fixed object range.

## Important APIs, Types, And Functions
`struct mlx5hws_buddy_mem` contains an array of per-order bitmaps, per-order free counts, and the maximum order. The exported functions are `mlx5hws_buddy_create()`, `mlx5hws_buddy_cleanup()`, `mlx5hws_buddy_alloc_mem()`, and `mlx5hws_buddy_free_mem()`.

## Control Flow And State
The state model is intentionally minimal. The allocator starts with one free block at `max_order`; allocations split larger blocks and frees coalesce with buddy blocks. The header does not declare any lock, so ownership and serialization are delegated to pool-level callers.

## Dependencies And Integration Points
This header is included by `buddy.c` and by HWS pool code that needs low-level chunk management. The returned segment offsets feed into `struct mlx5hws_pool_chunk` offsets used by action STCs, match STEs, and action STE chunks.

## Risks And Test Signals
The contract assumes valid power-of-two order semantics and serialized callers. Tests should check allocation exhaustion, reuse after free, coalescing to the top order, and caller behavior when `mlx5hws_buddy_create()` returns NULL.
