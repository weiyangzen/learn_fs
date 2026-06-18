# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_stats.c

## Purpose
Collects and reports Ocelot statistics. It maps SYS hardware counters to software stats, periodically extends 32-bit counters to 64-bit values, and serves ethtool strings, netdev stats64, standard ethtool MAC/PHY/RMON/pause/MM stats, and timestamp stats.

## Important APIs/types/functions
Public APIs include `ocelot_stats_init/deinit`, `ocelot_get_strings`, `ocelot_get_sset_count`, `ocelot_get_ethtool_stats`, standard ethtool stats getters, `ocelot_port_get_ts_stats`, and `ocelot_port_get_stats64`. Internal core: `ocelot_prepare_stats_regions`, `ocelot_port_update_stats`, `ocelot_port_transfer_stats`, `ocelot_check_stats_work`, and `ocelot_port_stats_run`.

## Control flow, state, persistence
Init allocates per-port stats, optional PTP timestamp stats, a single-thread stats workqueue, locks, contiguous counter regions, and delayed polling. The worker selects each port with `SYS_STAT_CFG`, bulk-reads regions, transfers counters under lock with wrap detection, calls optional chip `update_stats`, and reschedules. On-demand ethtool reads run the same update/transfer/callback path. State is `ocelot->stats`, `stats_regions`, region buffers, locks, workqueue, and per-port timestamp stats.

## Dependencies and integration
Depends on SYS counter register layout, Ocelot bulk reads, workqueues, ethtool netlink structures, PTP stats, and MM support. Exposed by `ocelot_net.c`.

## Risks and test signals
Risks are enum/register order drift, missed wraps under high traffic, lock-order regressions, and aggregate stats depending on netdev aggregation. Test ethtool `-S`, `ip -s link`, EMAC/PMAC/aggregate standard stats, counter wrap, PTP and MM stats, and teardown.
