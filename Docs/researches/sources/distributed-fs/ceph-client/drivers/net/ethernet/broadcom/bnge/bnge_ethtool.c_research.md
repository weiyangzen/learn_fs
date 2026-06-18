# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_ethtool.c

Purpose: Implements ethtool operations for the `bnge` netdev, covering link settings hooks, driver info, pause/autoneg restart, string/stat export, standard MAC/PHY/control/pause/RMON stat groups, and pause parameter updates.

Important APIs/functions: `bnge_set_ethtool_ops()` installs `bnge_ethtool_ops`. `bnge_nway_reset()` restarts link negotiation through HWRM when supported. Stat sizing/string/data paths are `bnge_get_num_stats()`, `bnge_get_sset_count()`, `bnge_get_strings()`, and `bnge_get_ethtool_stats()`. Standardized stat callbacks are `bnge_get_eth_phy_stats()`, `bnge_get_eth_mac_stats()`, `bnge_get_eth_ctrl_stats()`, `bnge_get_pause_stats()`, and `bnge_get_rmon_stats()`. Pause configuration is handled by `bnge_get_pauseparam()` and `bnge_set_pauseparam()`.

Control flow: ethtool queries compute dynamic counts based on ring counts, TPA support, port-stat flags, extended stat sizes returned by firmware, and priority-to-COS mapping. Data retrieval walks NQ/ring software stats, then port and extended stats arrays. Pause changes update cached link info and call HWRM only if the interface is running, rolling back on failure.

State/persistence: Reads `bnge_net` and `bnge_dev` state: ring counts, `bnapi` NQ stats, port stats backing stores, firmware stat sizes, flags, `eth_link_info`, PHY flags, firmware version, and PCI bus name. `bnge_set_pauseparam()` mutates requested flow-control/autoneg state.

Dependencies/integration: Depends on sibling link helpers (`bnge_get_link_ksettings`, `bnge_set_link_ksettings`, `bnge_get_link`, HWRM pause/link setters), HSI stat layouts, `bnge_net` private state, and ethtool netlink/stat APIs.

Risks/test signals: Dynamic stat counts must match string/data writes exactly; priority arrays assume 8 entries and valid `pri2cos_idx`. Pause/autoneg validation must align with firmware capabilities. Test `ethtool -S`, JSON/netlink stats groups, TPA on/off, port/ext stat flags, shared-channel vs separate TX ring indexing, pause get/set/nway reset with link up/down, no-pause PHYs, and firmware stat-size truncation.
