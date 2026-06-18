# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/stats.c

Purpose: Bridges firmware statistics notifications to mac80211 station statistics, scan traffic-load heuristics, CQM RSSI notifications, MLO low-RSSI scans, EMLSR exits, and PHY channel-load state.

Important APIs and functions: `iwl_mld_request_periodic_fw_stats()` enables/disables periodic operational stats. `iwl_mld_clear_stats_in_fw()` requests on-demand reset notifications. `iwl_mld_mac80211_sta_statistics()` serves mac80211 station statistics. `iwl_mld_handle_stats_oper_notif()` processes operational notifications. `iwl_mld_handle_stats_oper_part1_notif()` is currently a placeholder.

Control flow: On-demand station statistics install waits for operational, part1, and end notifications, send `SYSTEM_STATISTICS_CMD`, fill signal average from per-STA data, then delete handlers so the response is not processed as general periodic data. Periodic notifications process per-link airtime/RSSI, per-STA average energy, and per-PHY channel load. Traffic load is recalculated from elapsed firmware timestamps and airtime, then stored in scan state to influence later scan type selection.

State and persistence: Updates `mld->scan.traffic_load`, each `iwl_mld_link_sta.signal_avg`, each PHY `channel_load_by_us` and averaged `avg_channel_load_not_by_us`, and link CQM RSSI last-event state. State is runtime-only but affects future scan, CQM, and EMLSR decisions.

Dependencies and integration points: Depends on firmware statistics ABI, notification wait infrastructure, station/link mapping, PHY/channel context iteration, scan internal MLO scan trigger, and MLO/EMLSR helpers. It integrates with mac80211 `sta_statistics`, CQM RSSI events, and EMLSR policy.

Risks: On-demand statistics are not EMLSR-ready and intentionally return nothing with more than one active link. Firmware timestamp wrap/short windows can skew traffic load. Per-STA lookup is through RCU/wiphy pointers and must tolerate removed stations. Invalid channel load over 100 is rejected. Signal value zero is treated as invalid and skipped.

Test signals: Cover periodic enable/disable command masks, on-demand wait success/timeout, signal average updates, traffic-load thresholds, CQM high/low hysteresis, low-RSSI MLO scan trigger, EMLSR low-RSSI exit, invalid PHY load rejection, and multi-link station-stat no-op.
