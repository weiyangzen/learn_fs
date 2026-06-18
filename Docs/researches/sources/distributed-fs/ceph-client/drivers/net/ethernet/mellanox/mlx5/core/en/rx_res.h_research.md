# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rx_res.h

Purpose: Declares the RX resource manager interface and feature flags used by mlx5e receive flow steering.

Important types and APIs: `MLX5E_MAX_NUM_RSS` limits RSS contexts to 16. `enum mlx5e_rx_res_features` controls inner flow-table support, PTP TIR, multi-vHCA RQT entries, and self-loopback block. The header exports setup/teardown, TIRN/RQTN getters, activate/deactivate, XSK update, RSS ethtool operations, packet merge, RSS context management, and TLS TIR creation.

Control flow and state: The opaque `struct mlx5e_rx_res` is created once for the netdev profile and then reprogrammed as channels open, close, or change. Callers must not use TIR/RQTN getters before create succeeds.

Dependencies and integration: Includes RQT, TIR, FS, and RSS headers; used by channel setup, flow steering, reporters, TLS acceleration, PTP, and ethtool RSS configuration.

Risks and test signals: The header declares `bool mlx5_rx_res_rss_inner_ft_support(struct mlx5e_rx_res *res);`, but this function is not implemented in the read source set, so callers must be checked elsewhere or this is dead/API drift. Tests should validate compile/link coverage for all exported symbols and feature-flag combinations.
