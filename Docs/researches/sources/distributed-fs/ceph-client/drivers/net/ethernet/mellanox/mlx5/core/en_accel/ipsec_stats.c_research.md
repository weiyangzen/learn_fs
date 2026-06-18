# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec_stats.c

Purpose: exposes IPsec hardware and software counters to the mlx5e ethtool stats framework.

Important APIs/types/functions: static counter descriptor arrays for HW/SW IPsec stats, `MLX5E_READ_CTR_ATOMIC64`, and generated stats group ops for num stats, strings, and values. Defines `MLX5E_DEFINE_STATS_GRP(ipsec_hw, 0)` and `ipsec_sw`.

Control flow and state: HW fill path calls `mlx5e_accel_ipsec_fs_read_stats` to refresh `priv->ipsec->hw_stats` from flow counters, then emits descriptor offsets. SW fill path reads atomic64 counters directly from `priv->ipsec->sw_stats`. Both report zero stats if IPsec is not initialized.

Dependencies and integration: depends on ethtool helpers, mlx5e stats group macros, `ipsec.h` stats structs, and flow-steering stats read.

Risks and test signals: descriptor order must match userspace expectations; atomic offset reads assume descriptor type alignment. Test ethtool stats with IPsec absent/present, traffic/drop counter increments, and uplink representative aggregation.
