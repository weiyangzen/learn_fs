# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/action_ste_pool.c

## Purpose
`action_ste_pool.c` implements per-queue repositories of action STE tables used when actions need their own STE ranges, such as jump-to-STE-table flows. It grows tables on demand, separates RX-only, TX-only, and RX/TX allocations to avoid wasting mirrored entries, and periodically garbage-collects stale full tables.

## Important APIs, Types, And Functions
The public entry points are `mlx5hws_action_ste_pool_init()`, `mlx5hws_action_ste_pool_uninit()`, `mlx5hws_action_ste_chunk_alloc()`, and `mlx5hws_action_ste_chunk_free()`. Creation helpers allocate an STE pool (`hws_action_ste_table_create_pool()`), create RX/TX RTCs (`hws_action_ste_table_create_rtcs()`), and allocate a jump-to-STE-table STC (`hws_action_ste_table_create_stc()`). `hws_action_ste_choose_elem()` maps `skip_rx`/`skip_tx` to the correct pool optimize element. Cleanup is driven by `hws_action_ste_pool_cleanup()` delayed work.

## Control Flow And State
Initialization allocates one `struct mlx5hws_action_ste_pool` per HWS queue and initializes three elements for `MLX5HWS_POOL_OPTIMIZE_NONE`, `ORIG`, and `MIRROR`. Allocation locks the selected pool, tries every available table, creates a larger table if needed, stores the owning table in `chunk->action_tbl`, and moves a table to the `full` list when the backing pool is empty. Freeing returns the chunk to its buddy pool, updates `last_used`, and moves the table back to `available`.

Table size grows from log size 10 by one until log size 20. The delayed cleanup scans all queues and optimization elements, collects available tables that are still full and older than 300 seconds, drops the pool lock, then destroys their STC, RTCs, and STE pool.

## Dependencies And Integration Points
This file integrates with `mlx5hws_pool_create()`, pool chunk alloc/free, RTC and STC command wrappers, `mlx5hws_action_alloc_single_stc()`, context reparse-mode selection, and context lifetime in `context.c`. It is also dumped by `debug.c`.

## Risks And Test Signals
Risks include allocation/free ordering around firmware resources, stale cleanup racing with allocation, choosing the wrong RX/TX optimized pool, and leaked delayed work on context close. Test signals include repeated chunk allocation/free, RX-only and TX-only rules, allocation growth across several log sizes, cleanup after expiration, and failure injection at pool/RTC/STC creation stages to verify unwind paths.
