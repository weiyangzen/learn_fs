# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_counters.c

## Purpose
`fs_counters.c` implements mlx5 flow-counter allocation, pooling, destruction, direct query, cached query, and periodic bulk polling. It bridges firmware counter commands with the internal `mlx5_fc` structures defined in `fs_core.h`.

## Important APIs, Types, And Functions
- `struct mlx5_fc_stats` stores the aging-counter xarray, single-thread workqueue, delayed polling work, sampling interval, reusable bulk query buffer, and `mlx5_fs_pool` counter pool.
- Public APIs include `mlx5_fc_create`, `mlx5_fc_destroy`, `mlx5_fc_id`, `mlx5_fc_query`, `mlx5_fc_query_cached`, `mlx5_fc_query_cached_raw`, `mlx5_fc_query_lastuse`, `mlx5_init_fc_stats`, and `mlx5_cleanup_fc_stats`.
- Local-counter APIs `mlx5_fc_local_create`, `mlx5_fc_local_get`, `mlx5_fc_local_put`, and `mlx5_fc_local_destroy` wrap already-acquired counter IDs with independent refcounting.
- Pool-specific hooks `mlx5_fc_bulk_create`, `mlx5_fc_bulk_destroy`, and `mlx5_fc_pool_update_threshold` adapt the generic `fs_pool` allocator to firmware bulk counter allocation.

## Control Flow And State
`mlx5_init_fc_stats` allocates state, initializes the xarray, allocates an initial small bulk query buffer, creates the `mlx5_fc` workqueue, initializes the counter pool, and starts periodic polling. Aging counters are inserted into the xarray on create and removed on destroy. The delayed work reschedules itself, grows the query buffer when the active counter count exceeds the initial bulk length, and calls `mlx5_fc_stats_query_all_counters`.

Bulk polling walks the xarray under the xarray lock, releases the lock around each firmware `mlx5_cmd_fc_bulk_query`, resets the xarray cursor, and only updates counters whose `lastuse` predates the bulk query start. Cached query returns deltas since the caller's last cached read, while raw cached query returns absolute cached values.

## State And Persistence Behavior
Firmware owns the actual counter values and IDs. Driver state persists in `dev->priv.fc_stats`, the xarray keyed by counter ID, pooled bulk bitmaps, `lastbytes/lastpackets`, and per-counter cache. Cleanup cancels work synchronously, destroys the workqueue, releases all remaining counters, destroys the xarray, tears down the pool, and frees the bulk query buffer.

## Dependencies And Integration Points
The file depends on `fs_core.h`, `fs_pool.h`, `fs_cmd.h`, xarray locking, workqueues, firmware flow-counter allocation/query/free commands, and device capabilities such as `flow_counter_bulk_alloc` and `log_max_flow_counter_bulk`. It is used by flow steering, tc/eswitch rules, aging logic, and HWS action data.

## Risks And Edge Cases
Create/destroy races with the poller are managed through xarray locking and cursor reset; regressions here can produce use-after-free or stale cache updates. Pool-acquired, single, and local counters have distinct release paths. Bulk allocation fallback must preserve correctness when pooling fails. `mlx5_fc_update_sampling_interval` only reduces the interval, so callers expecting later expansion need a separate policy.

## Test Signals
Exercise single and pooled counter allocation, aging and non-aging counters, cached delta reads, raw reads, bulk buffer growth, destruction while polling, cleanup with live counters, pool exhaustion/fallback, and warnings for invalid pooled releases.
