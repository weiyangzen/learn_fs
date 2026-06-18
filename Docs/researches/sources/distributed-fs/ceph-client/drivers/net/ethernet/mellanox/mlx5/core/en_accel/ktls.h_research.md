# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls.h

Purpose: defines the kTLS capability checks, shared TLS state, stats structs, and public kTLS lifecycle/stat APIs.

Important APIs/types/functions: `mlx5e_is_ktls_device`, `mlx5e_ktls_type_check`, `mlx5e_is_ktls_tx`, `mlx5e_is_ktls_rx`, `struct mlx5e_tls_sw_stats`, `struct mlx5e_tls_debugfs`, `struct mlx5e_tls`, key helpers, TX/RX init/cleanup, RX feature setter, resync response-list helpers, and stats getters.

Control flow and state: `struct mlx5e_tls` is rooted at `priv->tls` and holds mdev, atomic SW stats, RX workqueue, TX pool, DEK pool, and debugfs dentries. Disabled builds provide no-op stubs and `-EOPNOTSUPP` for RX feature enable.

Dependencies and integration: includes Linux TLS headers, mlx5 crypto/lib helpers, and mlx5e core structures. Shared by kTLS TX, RX, stats, and netdev feature setup.

Risks and test signals: capability checks must reject kdump/subdevice/unsupported TLS versions; stats layout must remain stable. Build with/without `CONFIG_MLX5_EN_TLS`, test feature bits on devices with only TX/RX caps, and verify stats count/string/value consistency.
