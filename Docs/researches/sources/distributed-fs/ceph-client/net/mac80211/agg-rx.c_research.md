# sources/distributed-fs/ceph-client/net/mac80211/agg-rx.c

Purpose: this file manages receive-side A-MPDU Block Ack aggregation sessions for mac80211. It handles incoming ADDBA requests, session creation/teardown, reorder-buffer allocation when the driver does not own reordering, timers, ADDBA extension elements for HE/EHT/S1G cases, and driver notifications through `ampdu_action`.

Important APIs and functions: `__ieee80211_start_rx_ba_session()` is the core setup path. `__ieee80211_stop_rx_ba_session()` tears sessions down and optionally sends DELBA. `ieee80211_process_addba_request()` parses an ADDBA request action frame and calls the setup helper. Driver-facing exports include `ieee80211_stop_rx_ba_session()`, `ieee80211_manage_rx_ba_offl()`, and `ieee80211_rx_ba_timer_expired()`. `ieee80211_add_addbaext()` and `ieee80211_retrieve_addba_ext_data()` handle extended ADDBA element data and larger EHT/MLO buffer sizes.

Control flow: incoming ADDBA processing extracts dialog token, timeout, start sequence, policy, TID, and buffer size from the management frame, then retrieves optional extension data. The setup path validates TID range, S1G NDP BA requirements, HT/HE/S1G capability, `WLAN_STA_BLOCK_BA`, BA policy, and max buffer sizes. If a duplicate request has the same dialog token, it may return success only when the timeout did not change. If a conflicting session exists, it stops the old session. Hardware that advertises `SUPPORTS_REORDERING_BUFFER` receives only a driver `IEEE80211_AMPDU_RX_START` callback. Otherwise mac80211 allocates `tid_ampdu_rx`, timers, reorder queues, and reorder timestamps before notifying the driver and installing the RCU pointer.

State and persistence behavior: per-TID state lives in `sta->ampdu_mlme.tid_rx[tid]`, `agg_session_valid`, token arrays, and timer bitmaps. Reorder buffers hold queued `sk_buff`s until release. Session timers track inactivity, and reorder timers drive timeout release. Teardown clears the RCU pointer/valid bit, marks removed under `reorder_lock`, synchronously deletes timers, purges queues, and frees via RCU.

Dependencies and integration: this code depends on `sta_info`, `ieee80211_i.h`, `driver-ops.h`, timers, RCU, wiphy work, and action-frame TX helpers. It integrates with RX reorder release paths, driver `ampdu_action`, management frame parsing in `iface.c`, and TX-side helpers for shared ADDBA extension code.

Risks: races between timers, RCU readers, and teardown are the main risk; correct lockdep/wiphy locking is essential. Buffer-size negotiation must stay aligned with HT/HE/EHT limits and driver capabilities. Incorrect duplicate ADDBA handling can leave peers with inconsistent BA state. Memory pressure can reject sessions.

Test signals: interoperability tests with HT/HE/EHT APs, forced DELBA, duplicate ADDBA requests, timeout expiry, hardware-vs-software reorder-buffer modes, S1G NDP BA negotiation, and stress tests around station teardown while timers are active.
