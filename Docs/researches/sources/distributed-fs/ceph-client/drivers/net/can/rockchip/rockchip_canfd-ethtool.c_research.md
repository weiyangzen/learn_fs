# sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd-ethtool.c

Purpose: this file wires Rockchip-specific ethtool support into the netdev, exposing hardware timestamp capability and two driver statistics tied to documented RK3568 errata workarounds.

Important APIs and types: `enum rkcanfd_stats_type` indexes `rx_fifo_empty_errors` and `tx_extended_as_standard_errors`. `rkcanfd_stats_strings` supplies the ethtool stat names. `rkcanfd_ethtool_ops` uses `can_ethtool_op_get_ts_info_hwts` plus custom `get_strings`, `get_sset_count`, and `get_ethtool_stats`. `rkcanfd_ethtool_init()` installs the ops and initializes `u64_stats_sync`.

Control flow: core registration calls `rkcanfd_ethtool_init()` before `register_candev()`. At ethtool query time, the driver copies stat names for `ETH_SS_STATS`, reports the stat count, and reads the two `u64_stats_t` counters under the sequence-counter retry loop required for lockless 64-bit stats.

State and persistence: stats live in `priv->stats` for the life of the netdev and are not persisted across unregister. The counters are incremented in RX/TX paths for erratum 5 empty-FIFO observations and erratum 6 extended-as-standard transmit failures.

Dependencies and integration points: depends on `linux/ethtool.h`, SocketCAN hardware timestamp ethtool helper, `u64_stats_sync`, and the shared `rkcanfd_priv` structure. It integrates with user-visible `ethtool -S` and timestamp capability reporting.

Risks and test signals: stat ordering must stay synchronized between the enum and string array. Any new stats need matching names, count, and fetch logic. Tests should verify `ethtool -S canX` exposes stable names, concurrent stat updates are read without torn values, and `ethtool -T` reports hardware timestamp support through the CAN helper.
