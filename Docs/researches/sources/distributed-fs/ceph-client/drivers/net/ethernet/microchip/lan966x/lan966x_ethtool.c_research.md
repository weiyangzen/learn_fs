# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_ethtool.c

Purpose: provides LAN966x ethtool operations and statistics aggregation. It exposes link settings, pause parameters, private hardware counters, standard MAC/RMON stats, timestamping capabilities, and the background counter polling worker.

Important APIs and functions: `lan966x_ethtool_ops` wires phylink-backed link/pause operations, string/set count/stat retrieval, MAC/RMON stats, link state, and `get_ts_info`. `lan966x_stats_init` allocates counter storage and starts the delayed workqueue. `lan966x_stats_update` snapshots per-port 32-bit hardware counters into 64-bit software counters with wrap handling. `lan966x_stats_get` fills `rtnl_link_stats64` for netdev users.

Control flow: stats update iterates every physical port, selects the port counter view in `SYS_STAT_CFG`, reads each offset from `lan966x_stats_layout`, and extends it into a 64-bit counter. EtHTool stat reads force an immediate update, then copy the relevant port slice. MAC and RMON standard stats are synthesized from named counter indexes, including PMAC counters. The delayed work refreshes counters every two seconds so wraparound is handled even without user polling. Timestamp info reports PHC capabilities only when PTP is present and the port PHC is registered; otherwise it falls back to generic software timestamp info.

State and persistence: `lan966x->stats_layout`, `num_stats`, `stats`, `stats_lock`, `stats_work`, and `stats_queue` are initialized once at probe. Hardware counters are 32-bit and persist until hardware reset; software counters preserve wrap-extended totals in memory. Netdev `dev->stats` is combined with hardware drop counters for some fields.

Dependencies and integration points: depends on phylink ethtool helpers, ethtool MAC/RMON structures, PTP clock index APIs, LAN966x SYS counter registers, and netdev stats consumers. TC police/mirror stats also call `lan966x_stats_get`.

Risks: counter index constants must match `lan966x_stats_layout`; a mismatch silently corrupts reported stats. `FrameCheckSequenceErrors` adds the same CRC counter twice rather than PMAC CRC, which is a likely accounting bug. RMON jumbo histogram currently reuses the 1024-1526 counters for the 1519-10239 bucket. Workqueue teardown must cancel delayed work before destroying the queue.

Test signals: `ethtool -S`, `ethtool --include-statistics`, standard `ip -s link`, MAC/RMON ethtool netlink stats, counter wrap simulation or long traffic runs, PTP present/absent `ethtool -T`, pause/link setting get/set, and probe/remove workqueue cleanup.
