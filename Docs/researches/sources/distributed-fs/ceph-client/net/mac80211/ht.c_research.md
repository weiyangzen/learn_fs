<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/ht.c -->
# sources/distributed-fs/ceph-client/net/mac80211/ht.c

## Purpose
Implements HT (802.11n) capability negotiation, user capability overrides, block-ack session lifecycle work, DELBA and SMPS action frame handling, and channel-width notification updates for mac80211 stations and links.

## Important APIs, Types, and Functions
`ieee80211_apply_htcap_overrides()` applies configured HT masks for managed and IBSS interfaces. `ieee80211_ht_cap_ie_to_sta_ht_cap()` converts peer HT Capabilities IEs into `link_sta->pub->ht_cap` intersected with local support. `ieee80211_sta_tear_down_BA_sessions()` and `ieee80211_ba_session_work()` coordinate RX/TX BA start/stop state across TIDs. `ieee80211_send_delba()` and `ieee80211_process_delba()` transmit and consume DELBA action frames. `ieee80211_send_smps_action()`, `ieee80211_request_smps()`, and `ieee80211_smps_mode_to_smps_mode()` handle SMPS requests and action encoding. `ieee80211_ht_handle_chanwidth_notif()` reacts to peer channel width notifications.

## Control Flow
Capability overrides first rewrite MCS masks according to user masks, then disable or enable selected capability bits and constrain AMPDU factor/density. HT IE conversion exits to an empty capability if the peer IE or local HT support is absent, applies local overrides for station/adhoc modes, masks symmetric capability bits, handles asymmetric STBC, copies AMPDU parameters and peer TX MCS metadata, computes usable RX MCS masks based on local TX stream capability, preserves MCS 32 when both sides support it, sets max AMSDU length, and recalculates aggregate limits. It then updates public HT capability, current/public bandwidth based on link channel width and HT40 support, and SMPS mode for AP/AP_VLAN/NAN peers.

BA teardown iterates all TIDs to stop RX and TX aggregation and, for station destruction, cancels pending BA work and completes pending stop callbacks. The BA worker handles expired RX timers, requested RX stops, offloaded RX start/stop management, pending TX aggregation starts after fragment queues drain, and deferred start/stop callbacks. DELBA processing decodes TID/initiator and stops the appropriate RX or TX BA session. SMPS action transmission builds an HT action frame, requests TX status, stores link and mode in `status_data`, and sends on TID 7.

## State and Persistence
Persistent state is stored in per-interface override fields (`u.mgd.ht_capa`, `u.ibss.ht_capa` and masks), `link_sta->pub->ht_cap`, `link_sta->pub->bandwidth`, `link_sta->cur_max_bandwidth`, `link_sta->pub->smps_mode`, station aggregate state under `sta->ampdu_mlme`, TXQ fragment queues, and managed link `driver_smps_mode`. The file uses wiphy locking, RCU link lookups, station locks, and fq locks to coordinate concurrent TX aggregation and queue state.

## Dependencies and Integration Points
Depends on kernel 802.11 definitions, mac80211 private structures, station aggregation helpers implemented elsewhere, rate control, cfg80211 station opmode notification, driver RC update hooks, and management TX helpers from `ieee80211_i.h`. It is used by MLME association, IBSS peer updates, mesh peer links, cfg80211 station update code, block-ack action handling, debugfs SMPS controls, and driver-facing exported `ieee80211_request_smps()`.

## Risks
HT override behavior must remain aligned with hardware registration masks as noted in the source comment. Capability negotiation is dense, especially MCS stream limits, unequal modulation, STBC asymmetry, and MCS 32 handling. BA worker correctness depends on bitmaps, fragment queue draining, `synchronize_net()`, and not starting aggregation while `WLAN_STA_BLOCK_BA` is set. TXQ stop flags during fragmented TX are race-sensitive. SMPS status_data packs link and mode into a limited bitfield. Channel-width notification must keep rate control and cfg80211 opmode reporting synchronized.

## Test Signals
Signals include HT association/IBSS/mesh peers with overridden MCS and capability bits, HT20/HT40 bandwidth transitions, AMPDU start/stop under active fragmented TX, RX BA timer expiry, DELBA initiator/recipient cases, SMPS action status handling, and cfg80211 `STA_OPMODE_MAX_BW_CHANGED` notifications. Kernel warnings in capability/default width handling, BA destruction cleanup, and SMPS invalid modes are important regression indicators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/ht.c -->
