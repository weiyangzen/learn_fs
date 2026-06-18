# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_ethtool.c

## Purpose
Implements ethtool operations for ENETC PFs, VFs, ENETC4 PFs, and ENETC4 PPM devices. It provides register dumps, statistics strings/data, RSS configuration, RX flow classification, coalescing, timestamp capability reporting, phylink settings, WOL delegation, pause controls, and MAC Merge preemption support.

## Important APIs, Types, and Functions
Main exported symbols are `enetc_pf_ethtool_ops`, `enetc4_pf_ethtool_ops`, `enetc4_ppm_ethtool_ops`, `enetc_vf_ethtool_ops`, `enetc_set_ethtool_ops`, `enetc_set_rss_key`, `enetc_mm_commit_preemptible_tcs`, and `enetc_mm_link_state_update`. Key internals include `enetc_get_regs`, `enetc_get_ethtool_stats`, `enetc_get_rxfh`, `enetc_set_rxfh`, `enetc_set_rxnfc`, `enetc_set_cls_entry`, `enetc_get_ts_info`, `enetc_get_mm`, and `enetc_set_mm`.

## Control Flow
Stats flow builds string counts from SI rings plus PF-only port/MAC counters, selecting rev1 or rev4 register sets and optional pMAC/QBU counters. RSS operations access PF RSS key registers and dispatch table get/set through `si->ops`, which maps to legacy CBDR or NTMP. RXNFC inserts/deletes RFS rules by translating ethtool flow specs into `struct enetc_cmd_rfse` CBDR commands and mirroring rule state in `priv->cls_rules`. Coalesce changes update private interrupt settings and restart the netdev if running. MAC Merge operations serialize with `mm_lock`, program `PFPMR`, `MMCSR`, and preemptible TC registers, and poll verification when needed.

## State and Persistence
Persistent state includes hardware counters, RSS key and indirection table, RFS table entries, interrupt coalescing registers, PHC association, wakeup enable state, pause negotiation through phylink, and MAC Merge registers. Software mirrors classification rules, interrupt moderation mode, RX DIM enablement, `active_offloads`, preemptible traffic classes, and last known speed.

## Dependencies and Integration Points
Integrates with ethtool core, phylink, PHY WOL APIs, PTP qoriq devices, ENETC CBDR/NTMP RSS ops, netdev flow classifier state, and revision-specific register maps. PF/VF selection happens indirectly through `si->drvdata->eth_ops` in `enetc_set_ethtool_ops`.

## Risks
Risks include string/stat count drift, incorrect rev1/rev4 counter selection, byte-order quirks in RFS MAC matches, stale software `cls_rules` after failed hardware commands, netdev restart side effects during coalesce updates, PHC lookup assumptions by PCI devfn, and MAC Merge workaround behavior depending on link partner timing.

## Test Signals
Run `ethtool -S`, `-d`, `-x`, `-X`, RXNFC add/delete/list, coalescing get/set with device running, PTP timestamp info with and without PHC, WOL through PHY, pause settings through phylink, and `ethtool --show-mm/--set-mm` on QBU-capable hardware. Compare stat counts with `get_sset_count` and verify rev4 pseudo-MAC counters skip unavailable MAC blocks.
