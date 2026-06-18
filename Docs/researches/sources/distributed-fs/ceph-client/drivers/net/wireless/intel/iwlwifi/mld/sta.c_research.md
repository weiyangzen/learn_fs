# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/sta.c

Purpose: Implements MLD station lifecycle and firmware station configuration, including per-link station IDs, add/modify/remove commands, duplicate RX data allocation, MPDU counters for EMLSR throughput gating, internal broadcast/multicast/aux/monitor stations, and resource migration when active MLO links change.

Important APIs and functions: `iwl_mld_add_sta()` and `iwl_mld_remove_sta()` manage peer STAs. `iwl_mld_update_all_link_stations()` refreshes firmware STA config. `iwl_mld_update_link_stas()` handles MLO link add/remove transitions. `iwl_mld_fw_sta_id_from_link_sta()` and `iwl_mld_fw_sta_id_mask()` map mac80211 link STAs to firmware IDs. Internal station APIs add/remove bcast, mcast, aux, and monitor stations. `iwl_mld_count_mpdu_rx()` and `iwl_mld_count_mpdu_tx()` update throughput counters.

Control flow: Adding a peer initializes driver-private station state, TXQs, duplicate tracking, MPDU counters, and data antenna state, then adds each active link STA to firmware. Link STA add either reuses preserved IDs during restart or allocates a new FW ID, maps it through RCU pointers, sends `STA_CONFIG_CMD`, and marks it in firmware. Removal flushes and waits for TXQs, removes TXQs and AP keys as needed, sends `STA_REMOVE_CMD`, cancels pending notifications, clears mappings, and frees non-default link STAs through RCU.

State and persistence: `struct iwl_mld_sta` stores station type/state, VIF pointer, duplicate RX data, TID-to-BAID mapping, default and per-link STAs, PTK PN pointers, and MPDU counters. `struct iwl_mld_link_sta` stores restart-zeroed `last_rate_n_flags`, `in_fw`, `signal_avg`, and persistent `fw_id`. FW ID preservation across hardware restart is deliberate so firmware can recover sequence/PN state.

Dependencies and integration points: Uses mac80211 station/link abstractions, MLD VIF/link allocation maps, TXQ helpers, key removal, aggregation/BAID updates, TLC configuration, firmware STA/AUX/remove commands, RCU, wiphy locking, and KUnit static stubs for `iwl_mld_fw_sta_id_mask`.

Risks: RCU pointer updates and FW ID maps must stay in sync; leaks or stale pointers can route notifications to freed link STAs. Error unwind in multi-link add must remove only newly added resources. Command-version conversion in `iwl_mld_send_sta_cmd()` assumes old firmware has exactly one link and no NAN/UHR-only fields. Removing AP keys before STA removal is required by firmware ordering. MPDU counters are per RXQ and use spinlocks; throughput unblock scheduling depends on window reset timing.

Test signals: Cover peer add/remove, restart ID reuse, failed add unwind, multi-link link add/remove transitions, TXQ/key/BAID resource mask changes, internal station queue allocation failure, AP key removal ordering, FW command version 2 vs newer, MPDU counter thresholds, and RCU lookup under notification paths.
