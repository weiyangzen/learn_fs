# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/fs_tcp.h

Purpose: declares the accelerated TCP flow-steering API with no-op stubs when TLS support is disabled.

Important APIs/types/functions: `mlx5e_accel_fs_tcp_create/destroy`, `mlx5e_accel_fs_add_sk`, and `mlx5e_accel_fs_del_sk`.

Control flow and state: with `CONFIG_MLX5_EN_TLS`, callers create tables, add per-socket TIR rules, delete rules, and destroy tables. Without it, create/destroy are harmless and add returns `-EOPNOTSUPP`.

Dependencies and integration: includes `en/fs.h`; used by kTLS RX init and RX context rule work.

Risks and test signals: feature gating must keep non-TLS builds link-clean. Build both TLS-enabled and disabled configurations and exercise kTLS RX feature toggling.
