# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/debugfs_sta.c

Purpose: provides the ath10k per-station debugfs surface and the helper routines that feed per-station RX/TX observability. It exposes station-scoped controls for aggregation sessions, peer log triggering, peer power-save state, RX TID counters, and extended TX statistics, and it lets RX/firmware-stat paths accumulate data into `struct ath10k_sta` fields that are later dumped through debugfs.

Important APIs/types/functions: exported helpers are `ath10k_sta_update_rx_tid_stats_ampdu`, `ath10k_sta_update_rx_tid_stats`, `ath10k_sta_update_rx_duration`, and `ath10k_sta_add_debugfs`. Debugfs file handlers include aggregation mode, ADDBA/DELBA controls, peer debug trigger, peer power-save readout, TID stats dump, and TX stats dump. Main data objects are `struct ath10k_sta`, `struct ath10k_sta_tid_stats`, `struct ath10k_htt_data_stats`, firmware peer-stat structures, and mac80211 `struct ieee80211_sta`.

Control flow: RX statistics enter from `htt_rx.c`; code parses 802.11 headers, rejects non-data frames, derives QoS TID, honors `ar->sta_tid_stats_mask`, finds the station under RCU, and updates counters under `ar->data_lock`. A-MPDU updates look up peers by firmware ID and bucket MPDU ranges. RX duration updates walk firmware peer lists. Debugfs writes parse user input, validate TIDs, serialize with `ar->conf_mutex`, check `ATH10K_STATE_ON`, and send WMI commands.

State and persistence: all state is runtime-only in station driver-private memory and debug settings. Per-station debugfs files are recreated by `ath10k_sta_add_debugfs`; nothing is stored on disk.

Dependencies/integration: integrates with mac80211 station debugfs, HTT RX paths, firmware statistics, WMI aggregation commands, and ath10k debug feature gates. Locking relies on RCU, `ar->data_lock`, and `ar->conf_mutex`.

Risks: zero counters can mean disabled collection; manual aggregation writes can be no-ops while still returning `count`; fixed dump buffers assume current counter dimensions; firmware command errors are often logged but not surfaced as short writes.

Test signals: test station add/remove, all debugfs reads/writes, invalid inputs, TID mask toggling, extd TX stats enablement, RX QoS/non-QoS/error/A-MPDU paths, and concurrent station teardown during reads.
