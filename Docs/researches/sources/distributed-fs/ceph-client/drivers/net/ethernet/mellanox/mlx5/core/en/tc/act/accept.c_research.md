# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/accept.c

Purpose: Provides the TC `FLOW_ACTION_ACCEPT` parser for mlx5e TC offload.

Important API: Exports `mlx5e_tc_act_accept`, whose `parse_action` sets `MLX5_FLOW_CONTEXT_ACTION_FWD_DEST` and `MLX5_ATTR_FLAG_ACCEPT`, and marks the action as terminating.

Control flow, state, dependencies: No persistent state. It mutates the current `mlx5_flow_attr` during TC action parsing and depends on `act.h` and `tc_priv.h`.

Risks and tests: Its behavior is intentionally small; tests should verify accept terminates parsing as expected and sets FWD_DEST without adding destinations incorrectly in FDB/NIC contexts.
