# sources/distributed-fs/ceph-client/net/mac80211/s1g.c

## Purpose
`s1g.c` contains mac80211 support for IEEE 802.11ah/S1G-specific station setup and Target Wake Time handling. It initializes S1G rate/statistics representation, recognizes and processes S1G TWT action frames, builds S1G TWT setup/teardown management responses, translates S1G capability IEs into station capability state, and decides when S1G NDP BlockAck should be used.

## Important APIs, Types, and Functions
Public mac80211 helpers are `ieee80211_s1g_sta_rate_init()`, `ieee80211_s1g_is_twt_setup()`, `ieee80211_s1g_rx_twt_action()`, `ieee80211_s1g_status_twt_action()`, `ieee80211_s1g_cap_to_sta_s1g_cap()`, and `ieee80211_s1g_use_ndp_ba()`.

Internal frame-building helpers are `ieee80211_s1g_send_twt_setup()` and `ieee80211_s1g_send_twt_teardown()`. Internal receive/status helpers are `ieee80211_s1g_rx_twt_setup()`, `ieee80211_s1g_rx_twt_teardown()`, and `ieee80211_s1g_tx_twt_setup_fail()`. Key protocol structures are `struct ieee80211_mgmt`, `struct ieee80211_twt_setup`, `struct ieee80211_twt_params`, `struct ieee80211_s1g_cap`, and `struct ieee80211_sta_s1g_cap`.

## Control Flow, State, and Persistence
`ieee80211_s1g_sta_rate_init()` marks a station's default-link last TX/RX rate state as S1G so generic rate/stat reporting does not expose legacy bitrates for S1G peers. `ieee80211_s1g_is_twt_setup()` is a small classifier for action frames with S1G category and TWT setup action code.

For received TWT action frames, `ieee80211_s1g_rx_twt_action()` asserts the wiphy lock, finds the BSS station by source address, and dispatches setup or teardown. Setup handling clears the requester bit, rejects broadcast TWT negotiation by rewriting the setup command to reject, marks TWT information as RX-disabled because it is not supported yet, calls `drv_add_twt_setup()` for accepted unicast setup, and sends a TWT setup response back to the station. Teardown handling calls `drv_twt_teardown_request()` with the flow id carried in the action body.

For TX status of TWT action frames, `ieee80211_s1g_status_twt_action()` finds the station by destination address and treats failed setup transmission as a reason to tear down the negotiated flow. `ieee80211_s1g_tx_twt_setup_fail()` extracts the flow id from `req_type`, notifies the driver teardown hook, and sends an S1G TWT teardown frame.

`ieee80211_s1g_cap_to_sta_s1g_cap()` clears and fills the public station S1G capability from the S1G capability IE, marks `s1g = true`, updates `agg.max_amsdu_len` according to the S1G max-MPDU bit, and recalculates aggregate limits. `ieee80211_s1g_use_ndp_ba()` returns true only when the vif is configured for S1G, hardware advertises NDP BlockAck support, and the peer has S1G capability.

Persistent side effects include station rate/stat fields, station S1G capability bytes, aggregate maximum A-MSDU length, driver-owned TWT flow state through callbacks, and transmitted management action skbs.

## Dependencies and Integration Points
The file includes Linux/mac80211 IEEE 802.11 definitions plus `ieee80211_i.h` and `driver-ops.h`. It integrates with driver callbacks `drv_add_twt_setup()` and `drv_twt_teardown_request()`, transmit helper `ieee80211_tx_skb()`, station lookup `sta_info_get_bss()`, aggregate recalculation `ieee80211_sta_recalc_aggregates()`, and RX/BLOCKACK logic in `rx.c` through `ieee80211_s1g_use_ndp_ba()`.

## Risks and Test Signals
Risks include insufficient length validation before dereferencing TWT bodies if callers do not prefilter correctly, incorrect flow-id extraction on failed setup, mismatch between driver TWT state and response/teardown frame transmission failures, unsupported broadcast TWT negotiation being represented accurately as a rejection, and stale aggregate limits after capability updates. Tests should cover S1G station init, S1G/non-S1G action classification, TWT setup acceptance and broadcast rejection, teardown request flow ids, TX-status setup failure teardown, S1G capability conversion for both max-MPDU values, aggregate recalculation, and NDP BA selection for all combinations of vif S1G, hardware support, and peer capability.
