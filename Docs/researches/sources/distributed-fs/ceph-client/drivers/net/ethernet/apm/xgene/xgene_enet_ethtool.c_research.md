## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_ethtool.c

Purpose: exposes original X-Gene driver information, link settings, software and hardware statistics, and pause configuration through ethtool.

Important APIs, types, and functions: `gstrings_stats` maps generic `rtnl_link_stats64` counters; `gstrings_extd_stats` maps MAC statistic registers and masks. `xgene_get_link_ksettings` delegates to PHYLIB for RGMII or MDIO-backed SGMII, synthesizes fixed 1G SGMII settings without MDIO, and fixed 10G fiber settings for XGMII. `xgene_set_link_ksettings` only permits PHY-backed modes. `xgene_get_extd_stats` reads hardware counters, applies errata corrections, and adds MAC drop counts. `xgene_extd_stats_init` allocates and zeroes accumulated extended stats. Pause operations validate PHY pause for RGMII/SGMII and directly program MAC flow control for XGMII. `xgene_enet_set_ethtool_ops` installs the ops table.

Control flow, state, and persistence: `xgene_enet_probe` installs ops and initializes extended stats. Stats accumulate in `pdata->extd_stats` and are adjusted by software errata counters `false_rflr` and `vlan_rjbr`. Pause settings persist in `pdata->pause_autoneg`, `tx_pause`, and `rx_pause`.

Dependencies and integration points: relies on `xgene_enet_rd_stat`, MAC operation callbacks for drop counters and flow control, PHYLIB helpers, and netdev stats from `xgene_enet_get_stats64`.

Risks: extended stat accumulation assumes sane hardware counter semantics and masks. Errata corrections subtract counters and can underflow if ordering/width assumptions are wrong. Link settings intentionally reject non-PHY 10G changes.

Test signals: `ethtool -i`, `ethtool -S`, pause toggles, PHY-backed speed changes, fixed XGMII link reporting, and traffic/error generation to verify errata-adjusted counters.
