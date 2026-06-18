# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/macsec_stats.c

Purpose: exposes MACsec hardware offload counters through the mlx5e ethtool statistics framework.

Important APIs, types, and functions: `mlx5e_macsec_hw_stats_desc` lists RX/TX packet, byte, and drop counters in `struct mlx5_macsec_stats`. The generated stats-group operations report count, fill strings, and fill values. `MLX5E_DEFINE_STATS_GRP(macsec_hw, 0)` registers the group.

Control flow: stats are hidden unless `priv->macsec` exists and the device reports MACsec support. Filling values obtains `priv->mdev->macsec_fs`, refreshes stats through `mlx5_macsec_fs_get_stats_fill()`, then reads each counter descriptor into ethtool data.

State and persistence: no local persistent state. It reads counters stored by MACsec flow steering and hardware counter snapshots.

Dependencies and integration points: depends on ethtool stats helpers, mlx5e stats macros, `priv->macsec`, and `mlx5_macsec_fs` counter accessors.

Risks: stats callbacks assume `mdev->macsec_fs` is valid when `priv->macsec` exists. Cleanup ordering must prevent ethtool reads from racing freed MACsec FS state. Counter descriptor order must match user-visible string order.

Test signals: ethtool `-S` on MACsec-capable and non-capable devices, packet/drop counter increments for encrypted/decrypted/drop flows, and cleanup/reload with repeated stats reads.
