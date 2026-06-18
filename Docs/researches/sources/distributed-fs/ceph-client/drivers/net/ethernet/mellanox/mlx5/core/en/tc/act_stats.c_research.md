# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act_stats.c

Purpose: Tracks per-action hardware stats for TC actions by mapping TC action cookies to mlx5 flow counters and returning deltas to flow offload action stats.

Important APIs: `mlx5e_tc_act_stats_create()`, `free()`, `add_flow()`, `del_flow()`, and `fill_stats()`.

Control flow: Creation initializes an auto-shrinking rhashtable. `add_flow()` walks each flow attr, carrying the current counter and adding unique consecutive action cookies to the table. `del_flow()` removes all cookies for flows marked `USE_ACT_STATS` under a spinlock and frees entries with RCU. `fill_stats()` looks up a cookie, queries cached raw counter values, reports deltas from saved last values, and updates saved counters.

State and persistence: `mlx5e_tc_act_stats_handle` owns the rhashtable and spinlock. Each entry stores cookie, counter pointer, last packets/bytes, hash node, and RCU head. State persists until flow deletion or handle free.

Dependencies and integration: Uses rhashtable, RCU, mlx5 flow counters, `flow_stats_update()`, and TC flow attrs/cookies.

Risks and tests: `fill_stats()` updates last counters under only RCU read lock, so concurrent stats reads for the same cookie could race. Add-flow rollback deletes all entries for the flow. Tests should cover duplicate cookies, missing counters, add failure rollback, delete under concurrent lookup, delta correctness, and `USE_ACT_STATS` disabled flows.
