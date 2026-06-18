# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_ethtool.c

## Purpose
`wx_ethtool.c` implements shared ethtool operations for WangXun libwx based Ethernet devices. It exposes statistics strings and values, driver information, link settings through phylink, WOL, pause parameters, ring and interrupt coalescing controls, channel counts, RSS indirection/key/hash-field controls, debug message level, timestamp capability reporting, PTP timestamp statistics, and a reduced VF ethtool operation table.

## Important APIs, types, and functions
The local `struct wx_stats` maps ethtool stat names to offsets inside `struct wx`. `wx_gstrings_stats`, `wx_gstrings_fdir_stats`, and `wx_gstrings_rsc_stats` define global, Flow Director, and RSC counters. Exported APIs include `wx_get_sset_count`, `wx_get_strings`, `wx_get_ethtool_stats`, `wx_get_mac_stats`, `wx_get_pause_stats`, `wx_get_drvinfo`, `wx_nway_reset`, `wx_get_link_ksettings`, `wx_set_link_ksettings`, `wx_get_wol`, `wx_set_wol`, `wx_get_pauseparam`, `wx_set_pauseparam`, `wx_get_ringparam`, `wx_get_coalesce`, `wx_set_coalesce`, `wx_get_channels`, `wx_set_channels`, `wx_rss_indir_size`, `wx_get_rxfh_key_size`, `wx_get_rxfh`, `wx_set_rxfh`, `wx_get_rxfh_fields`, `wx_set_rxfh_fields`, `wx_get_msglevel`, `wx_set_msglevel`, `wx_get_ts_info`, `wx_get_ptp_stats`, and `wx_set_ethtool_ops_vf`.

## Control flow and behavior
Stats retrieval first calls `wx_update_stats()` and then copies counters from `struct wx` and per-ring `u64_stats` into the ethtool buffer in the same order used by `wx_get_strings()`. Link and pause operations delegate to `phylink_ethtool_*`. WOL writes `WX_PSR_WKUP_CTL` and updates PCI device wakeup state. Coalescing validation chooses per-MAC EITR limits, handles adaptive ITR mode, writes each q-vector EITR through `wx_write_eitr()`, and may reset the device if RSC must change. Channel changes update RSS/FDIR limits and call `wx->setup_tc()`. RSS changes update `wx->rss_indir_tbl`, `wx->rss_key`, or `wx->rss_flags` and push them to hardware through `wx_store_reta()`, `wx_store_rsskey()`, and `wx_config_rss_field()`.

## State and persistence
This file mutates persistent driver runtime state in `struct wx`: WOL flags, interrupt moderation settings, `adaptive_itr`, per-vector `itr`, ring feature limits, RSS indirection table, RSS key, RSS flow flags, debug message mask, and RSC enable flags. Values live in memory and hardware registers; they are not persisted across driver unload except where firmware or PCI wake state keeps WOL semantics.

## Dependencies and integration points
It depends on Linux ethtool, phylink, PCI, PTP clock, netdev feature, and `u64_stats` APIs. It integrates with `wx_hw.c` for RSS and stats programming, `wx_lib.c` for EITR writes and resource-level settings, and `wx_ptp.c` for timestamp clock state visible through `wx->ptp_clock` and timestamp counters. VF support is intentionally narrower and installs `wx_ethtool_ops_vf` on VF netdevices.

## Risks and edge cases
Stats ordering must remain synchronized between count, strings, and value generation or userspace will mislabel counters. `wx_get_coalesce()` assumes `wx->q_vector[0]` exists. Coalescing can silently switch adaptive mode and RSC, with reset side effects through `wx->do_reset`. RSS setters accept user indirection values without local range validation beyond ethtool core expectations. VF ethtool timestamp info uses `ethtool_op_get_ts_info`, not the PF PTP path. Channel changes depend on `other_count == 1`, so callers must provide the expected misc vector count.

## Test signals
Useful tests are `ethtool -S`, `ethtool -i`, `ethtool -c/-C`, `ethtool -l/-L`, `ethtool -x/-X`, `ethtool -n/-N rx-flow-hash`, WOL toggling with suspend/resume, and checking that RSC/LRO behavior changes only when coalescing thresholds require it. Kernel-level signals include no stat count mismatch warnings, successful q-vector EITR writes, and correct PTP `phc_index` when `wx_ptp_init()` registered a clock.
