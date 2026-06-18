# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rqt.c

Purpose: Owns mlx5 receive queue table creation, destruction, and redirection for direct and RSS-indirection receive paths.

Important APIs: `mlx5e_rqt_init_direct()`, `mlx5e_rqt_init_indir()`, `mlx5e_rqt_destroy()`, `mlx5e_rqt_redirect_direct()`, `mlx5e_rqt_redirect_indir()`, `mlx5e_rqt_size()`, `mlx5e_rqt_max_num_channels_allowed_for_xor8()`, and `mlx5e_rss_params_indir_init_uniform()`.

Control flow: Direct initialization creates an RQT with one initial RQN and max size either one or the indirection-table size. Indirect initialization translates an RSS indirection table into RQNs, optionally inverting indices for XOR hash, then creates an RQT. Redirect paths build `modify_rqt_in` input and rewrite the RQN list. `fill_rqn_list()` handles plain RQNs or cross-vHCA `rq_vhca` entries.

State and persistence: `struct mlx5e_rqt` stores the primary mlx5 device, RQTN, and max size. Hardware RQT state persists until `mlx5_core_destroy_rqt()`. Indirection arrays are caller-owned and are copied into command buffers only during create/modify.

Dependencies and integration: Uses mlx5 transobj commands, device capabilities for `cross_vhca_rqt`, `max_rqt_vhca_id`, and `log_max_rqt_size`, and ethtool RSS hash constants. RSS and RX resource code call this file for all hardware RQT programming.

Risks: Invalid indirection entries produce `WARN_ON` and `-EINVAL`. Cross-vHCA support must be capability-gated and id ranges validated. XOR hash is capped by a 256-entry allowed RQT size. Tests should validate direct and indirect creation, table resizing, XOR index inversion, out-of-range indirection indices, cross-vHCA enabled/disabled, and redirect error rollback by callers.
