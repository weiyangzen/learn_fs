# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_mlme_ext.c

## Purpose

`rtw_mlme_ext.c` is the Realtek RTL8723BS staging driver's extended MAC-layer management engine. It owns 802.11 management-frame dispatch, AP and station authentication and association state machines, scan progression, IBSS/AP beacon construction, channel-plan handling, Block Ack negotiation, SA Query handling, MLME event reporting, and the command handlers that bridge the driver's command thread into hardware and firmware operations.

This file is not persistent storage code. Its durable state is in adapter-owned runtime structures such as `struct mlme_ext_priv`, `struct mlme_ext_info`, `struct mlme_priv`, `struct sta_priv`, `struct security_priv`, CAM key tables, firmware/hardware registers, timers, and command queues. The file is central to connection lifetime because it decides when the interface is scanning, linking, authenticated, associated, AP-mode serving stations, disconnecting, or restoring the operating channel after off-channel scan work.

## Important APIs, types, and functions

Key static dispatch tables are `mlme_sta_tbl[]`, mapping management subtypes to handlers, and `OnAction_tbl[]`, mapping action categories to action handlers. Important exported or cross-file entry points include `init_mlme_ext_priv()`, `free_mlme_ext_priv()`, `mgt_dispatcher()`, `issue_*()` management transmit helpers, `site_survey()`, `collect_bss_info()`, `start_clnt_join()`, `receive_disconnect()`, `report_*_event()`, timer handlers, and H2C command handlers such as `join_cmd_hdl()`, `sitesurvey_cmd_hdl()`, `setkey_hdl()`, and `add_ba_hdl()`.

The main data carriers are adapter substructures: `mlmeextpriv` holds current channel, bandwidth, scan result state, action duplicate cache, timers, and event sequence; `mlmext_info` holds connection state bits, current BSS, auth/assoc counters, HT/WMM state, key index, SA Query sequence, and firmware station slots; `mlmepriv` holds host MLME state, cfg80211-facing buffers, scanned queues, QoS/HT details, and WPS IEs; `stapriv` and `sta_info` hold station lists, per-station auth/assoc state, rates, AID, HT capability, reorder state, and sleep queues.

The file also defines channel plan tables, Realtek/WPA/WMM/WPS/P2P OUIs, and helper functions such as `rtw_ch_set_search_ch()`, `init_channel_set()`, `init_channel_list()`, `update_hidden_ssid()`, and `rtw_scan_ch_decision()`.

## Control flow

Initialization flows through `init_mlme_ext_priv()`: it stores the adapter pointer, resets MLME extension values, installs timers, initializes AP info, builds the regulatory channel set and P2P channel list, and enables active keepalive checks. `init_hw_mlme_ext()` then applies the current channel and bandwidth to hardware. Cleanup only deletes timers when the driver is stopped.

Receive management flow starts at `mgt_dispatcher()`, usually from the receive path after `validate_recv_mgnt_frame()`. It rejects non-management frames and frames not addressed to the interface or broadcast, checks duplicate management sequence numbers per station, picks the subtype handler, and switches auth handling between AP-side `OnAuth()` and client-side `OnAuthClient()`. Probe/beacon frames feed scanning and BSS update paths; auth/assoc frames advance AP or station state; deauth/disassoc reports disconnect; action frames delegate to spectrum, BACK, public, HT, and SA Query handlers.

AP association control is split between `OnAuth()` and `OnAssocReq()`. `OnAuth()` allocates or refreshes a station, maintains auth and assoc lists, supports open/shared-key auth including WEP challenge text, and transmits auth replies. `OnAssocReq()` validates authenticated state, SSID, supported rates, WPA/WPA2/WPS/WMM/HT capabilities, assigns an AID, moves the station to the associated list, updates AP capability state, stores the assoc request, sends the assoc response, and reports an add-station event.

Station association control starts in `join_cmd_hdl()`. It tears down an existing station link if necessary, resets join state, copies the selected `wlan_bssid_ex`, parses WMM and HT IEs, decides channel/bandwidth with `rtw_chk_start_clnt_join()`, writes BSSID and join state to hardware, switches channel, and enters `start_clnt_join()`. The station then waits for a beacon in `WIFI_FW_AUTH_NULL`, starts auth from `OnBeacon()` via `start_clnt_auth()`, handles auth response in `OnAuthClient()`, transmits assoc in `start_clnt_assoc()`, and finalizes from `OnAssocRsp()` by parsing WMM/HT/ERP IEs, storing the assoc response, and reporting join result.

Scanning starts in `sitesurvey_cmd_hdl()`. It copies requested SSIDs and channels, filters channels through the local channel plan, optionally sends null data to enter AP power-save mode before leaving the serving channel, disables dynamic PHY functions, sets initial gain and no-link MSR, marks hardware under site survey, and calls `site_survey()`. `site_survey()` switches to each channel, sends active probe requests when allowed, arms `survey_timer`, reports BSS records from beacons/probe responses with `report_survey_event()`, then restores channel/bandwidth, MSR, dynamic functions, and null-data wake state before reporting survey done.

Transmit management helpers all allocate an extended xmit frame and xmit buffer, populate 802.11 headers and IEs, update `mgnt_seq`, set packet attributes, and submit through `rtw_hal_mgnt_xmit()` or an ack/wait variant. This includes beacon, probe response/request, auth, assoc response/request, null data, QoS null data, deauth, SA Query, BA actions, and 20/40 coexistence public actions.

Command and timer flows keep the state machine moving. `link_timer_hdl()` handles auth-null timeout, re-auth retries, and re-assoc retries. `survey_timer_hdl()` requeues `_SiteSurvey` commands and handles scan abort. `sa_query_timer_hdl()` disconnects when protected-management SA Query times out. H2C handlers set op mode, create BSS, join, disconnect, set auth/key/station-key, request ADDBA, send queued multicast frames, transmit beacon, change channel/channel plan, and run a callback in the command thread.

## State and persistence behavior

All state is volatile and adapter-scoped. Important counters include `event_seq`, `mgnt_seq`, `sa_query_seq`, auth/reassoc/link retry counts, scan channel index and BSS count, and AP alive retry counters. Timers persist state transitions across asynchronous gaps. CAM programming through `write_cam()`, hardware registers such as `HW_VAR_BSSID`, `HW_VAR_MLME_JOIN`, `HW_VAR_SEC_CFG`, and `HW_VAR_H2C_FW_PWRMODE`, and beacon/TIM updates are side effects outside normal memory but are still runtime device state.

The file updates stored association buffers in `mlmepriv->assoc_req` and `assoc_rsp`, stores AP-side per-station assoc request copies, and updates channel plans after Country IE processing. It never writes files or stable on-disk configuration.

## Dependencies and integration points

The module depends on `drv_types.h`, `rtw_wifi_regd.h`, `hal_btcoex.h`, Linux timer/work/memory primitives, cfg80211 notification helpers, and many local driver helpers from receive, transmit, station, security, command, AP, HT, WMM, HAL, and regulatory layers. Integration points include `rtw_enqueue_cmd()` for MLME events and H2C commands, `rtw_hal_set_hwreg()` and `rtw_hal_get_hwreg()` for device state, `rtw_cfg80211_rx_action()` for public action frames, Bluetooth coexistence notifications, `rtw_lps_ctrl_wk_cmd()` for power-save state, CAM key management, and AP-mode beacon/TIM update functions.

`rtw_recv.c` invokes `mgt_dispatcher()` after management-frame validation. `rtw_pwrctrl.c` and transmit code depend on `issue_nulldata()`, `issue_qos_nulldata()`, and LPS connect/disconnect notifications. AP data-path power-save behavior depends on station state established by this file.

## Risks and edge cases

Several frame-building paths return after allocating transmit resources without freeing them on some error branches, for example oversized beacon/probe response IE paths. This is important in AP mode because malformed or oversized IEs could leak xmit resources over repeated attempts.

`rtw_ch_set_search_ch()` uses `if (i >= ch_set[i].ChannelNum)` after the loop, which compares an index to a channel number rather than to a channel-set size. The zero sentinel often makes this work for not-found cases, but the condition is suspicious and should be regression-tested before reuse.

Much parsing uses raw offsets into received IEs and frame bodies. Many paths check top-level lengths, but several loops trust IE lengths while incrementing through `pnetwork->ies` or received bodies. Fuzzing malformed management frames, especially vendor IEs, HT IEs, Country IEs, and action frames, is high-value.

State changes are split across timers, command thread, receive context, and AP station lists. Locking is present for station auth/assoc lists and beacon updates, but many `mlmeext_info` fields are updated without a dedicated lock. Tests should watch for races during scan while disconnecting, reconnect while link timer fires, AP station re-auth during timeout, and protected-management SA Query timeout during deauth.

802.11w handling is split with receive validation in `rtw_recv.c` and SA Query actions here. Robust-management failures should be tested because incorrect failures can disconnect valid protected sessions or accept unauthenticated teardown frames.

## Test signals

Useful signals are successful init/free with timers, complete active and passive scans, survey event counts, channel restoration after scan, station open and shared-key auth, WPA/WPA2/WPS assoc acceptance and rejection paths, AP station AID allocation exhaustion, WMM/HT capability negotiation, ADDBA request/response/DELBA behavior, null-data and QoS-null LPS transitions, SA Query timeout disconnect, 802.11d Country IE channel-plan changes, and correct event callbacks for join, add STA, del STA, WMM, survey, and survey done. Kernel tests should include malformed IE fuzzing, repeated beacon/probe response generation with oversized IEs to detect leaks, and concurrent scan/disconnect/join stress with lockdep and KASAN enabled.
