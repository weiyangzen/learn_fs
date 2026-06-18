# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/sample.c

Purpose: Parses TC sample actions into mlx5 flow attributes and decides whether sampling requires a multi-table implementation.

Important APIs: `mlx5e_tc_act_sample` parses sample rate, psample group, optional truncation, sets `MLX5_ATTR_FLAG_SAMPLE`, and marks flow flag `SAMPLE`. `mlx5e_tc_act_sample_is_multi_table()` returns true when `reg_c_preserve` is supported or decap is present.

Control flow and state: No long-lived state here; it fills `attr->sample_attr` for the later offload implementation in `tc/sample.c`.

Dependencies and integration: Includes psample and `en/tc/sample.h`. The multi-table decision is reused by the full sample offload path.

Risks and tests: Tests should cover truncation enabled/disabled, group number propagation, rate propagation, decap requiring post-action path, and no-reg-preserve fallback path.
