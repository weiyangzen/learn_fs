<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_ethtool.c

## Purpose

`icssg_ethtool.c` exposes ICSSG netdev controls and counters through `struct ethtool_ops`. It bridges standard ethtool requests to PHY settings, ICSSG hardware stats, PTP timestamp capability reporting, TX/RX interrupt coalescing state, channel count selection, EEE, and RMON histograms.

## Important APIs, Types, and Functions

The exported object is `icssg_ethtool_ops`. Local callbacks include driver info, message level get/set, link ksettings, EEE get/set, autonegotiation reset, stats string/count/data export, timestamp info, channel get/set, global and per-queue coalescing get/set, and RMON stats. It consumes `icssg_all_miig_stats`, `icssg_all_pa_stats`, `emac_update_hardware_stats()`, and `emac_get_stat_by_name()`.

## Control Flow

Stats reads first refresh hardware counters with `emac_update_hardware_stats()`, then copy non-standard MIIG counters and optional PA counters into the ethtool buffer. Channel changes are allowed only while the interface is down; SR1 reports one user-visible TX queue while internally reserving an extra management TX channel. Coalescing setters clamp nonzero values below `ICSSG_MIN_COALESCE_USECS` and store nanosecond delays in `emac->rx_pace_timeout_ns` or `tx_chn->tx_pace_timeout_ns`.

## State and Persistence Behavior

This file mutates `emac->msg_enable`, `emac->tx_ch_num`, RX coalescing timeout, and per-TX-channel coalescing timeout. It reads and accumulates stats through `icssg_stats.c` and reports PTP clock index from `emac->iep`. State persists in the in-memory driver structures until device close/reprobe.

## Dependencies and Integration Points

It integrates with PHY library ethtool helpers, ICSSG stats tables, netdev private `struct prueth_emac`, `icss_iep_get_ptp_clock_idx()`, and kernel ethtool APIs including `kernel_ethtool_ts_info`, `ethtool_channels`, `ethtool_coalesce`, and RMON histogram ranges.

## Risks and Edge Cases

`emac_get_stat_by_name()` returns an `int` even though backing counters are `u64`, so RMON values can truncate if counters exceed `INT_MAX`. Per-queue coalescing validates against `PRUETH_MAX_TX_QUEUES`, not current `emac->tx_ch_num`, so inactive queues may be writable. Channel count changes do not validate `ch->tx_count` against zero or max directly in the setter, relying on ethtool core constraints and reported limits.

## Test Signals

Run `ethtool -i`, `-S`, `-c`, `-C`, `-l`, `-L`, `--show-eee`, `--set-eee`, and timestamp info queries on SR1 and SR2 devices. Validate channel changes while down versus `-EBUSY` while up, PA-stats-present and absent paths, coalescing clamp messages, and RMON counter consistency under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_ethtool.c -->
