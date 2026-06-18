# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act_stats.h

Purpose: Declares the TC action stats handle and lifecycle/flow/stats APIs.

Important APIs: `mlx5e_tc_act_stats_create()`, `mlx5e_tc_act_stats_free()`, `mlx5e_tc_act_stats_add_flow()`, `mlx5e_tc_act_stats_del_flow()`, and `mlx5e_tc_act_stats_fill_stats()`.

Control flow and state: Callers create one handle, add flows after successful offload, remove flows on teardown, and query stats by action cookie.

Dependencies and integration: Includes flow offload and TC private types; implementation depends on mlx5 counters and rhashtable.

Risks and tests: API users must pair add/delete and avoid querying after handle free. Tests should cover missing cookie returning `-ENOENT` and cleanup ordering during flow deletion.
