# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_stats.c

Purpose: publishes mlx5e kTLS software counters through the driver stats interface.

Important APIs/types/functions: counter descriptor array for `tx_tls_ctx`, `tx_tls_del`, `tx_tls_pool_alloc`, `tx_tls_pool_free`, `rx_tls_ctx`, `rx_tls_del`; `mlx5e_ktls_get_count`, `mlx5e_ktls_get_strings`, and `mlx5e_ktls_get_stats`.

Control flow and state: functions no-op when `priv->tls` is absent. Otherwise, count returns descriptor count, strings emit ethtool names, and stats read atomic64 fields from `priv->tls->sw_stats`.

Dependencies and integration: depends on ethtool helpers, mlx5e stat emit helpers, and `struct mlx5e_tls_sw_stats` from `ktls.h`.

Risks and test signals: descriptor offsets must match stats struct; stats must disappear cleanly when TLS unsupported. Test ethtool stats before/after kTLS init, TX/RX context add/delete increments, and TLS-disabled build stubs.
