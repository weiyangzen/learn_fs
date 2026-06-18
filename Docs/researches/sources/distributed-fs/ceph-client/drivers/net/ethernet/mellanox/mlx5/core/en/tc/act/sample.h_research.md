# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/sample.h

Purpose: Declares the shared helper that determines whether a TC sample action should be implemented as a multi-table action.

Important API: `mlx5e_tc_act_sample_is_multi_table(struct mlx5_core_dev *mdev, struct mlx5_flow_attr *attr)`.

Control flow and state: No state. The declaration lets the action parser and sample offload implementation share one decision.

Dependencies and integration: Includes flow offload and `tc_priv` types. Used by `tc/act/sample.c` and `tc/sample.c`.

Risks and tests: The decision must stay synchronized with offload implementation capabilities. Tests should compile with sampling enabled and disabled, and verify decap/reg_c_preserve behavior.
