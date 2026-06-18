# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls.c

Purpose: top-level kTLS device integration for mlx5e: key creation, TLS device ops, netdev feature publication, RX feature toggling, RX/TX init hooks, and debugfs root management.

Important APIs/types/functions: `mlx5_ktls_create_key`, `mlx5_ktls_destroy_key`, `mlx5e_ktls_build_netdev`, `mlx5e_ktls_set_feature_rx`, `mlx5e_ktls_init_rx/cleanup_rx`, `mlx5e_ktls_init/cleanup`, and TLS dev ops add/delete/resync dispatchers.

Control flow and state: add checks cipher/version/device support and dispatches by TX/RX direction. RX resync is only supported for RX. kTLS RX capability requires non-kdump, TLS RX cap, no subdevice, and enough ICOSQ WQE size for static/progress/get-PSV WQEs. Build netdev sets HW TLS TX/RX features and `tlsdev_ops`. RX feature enable creates TCP accel flow tables and reopens channels the first time RX is enabled; init creates RX workqueue and tables if feature already active. Top-level init allocates `priv->tls`, records mdev, and creates debugfs.

Dependencies and integration: uses Linux TLS offload ops, mlx5 crypto DEK pool helpers, TCP acceleration FS, channel reopen, debugfs, and TX/RX kTLS implementation files.

Risks and test signals: feature toggling under `state_lock` must coordinate with channel state; RX workqueue/table cleanup must match feature state; unsupported cipher handling must be strict. Test TLS 1.2 AES-GCM-128/256, unsupported ciphers, RX feature toggle on open netdev, init cleanup with feature enabled, and resync direction rejection.
