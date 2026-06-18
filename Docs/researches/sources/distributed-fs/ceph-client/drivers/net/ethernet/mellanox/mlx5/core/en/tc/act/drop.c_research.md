# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/drop.c

Purpose: Provides TC drop action parsing for mlx5e.

Important API: `mlx5e_tc_act_drop` sets `MLX5_FLOW_CONTEXT_ACTION_DROP` and is marked terminating.

Control flow, state, dependencies: No persistent state. It only mutates `attr->action` during parse and depends on common action/TC private headers.

Risks and tests: Tests should confirm drop is terminating and does not leave forwarding destinations active in combinations where higher-level parser must reject conflicting actions.
