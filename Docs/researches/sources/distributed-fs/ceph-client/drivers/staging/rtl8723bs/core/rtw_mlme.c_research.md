# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_mlme.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_mlme.c` implements the RTL8723BS MLME state machine and network database. It initializes and frees MLME state, manages scanned-network/free-network queues, handles survey/join/station/power events, indicates connect/disconnect/scan completion to cfg80211, selects join and roaming candidates, sets authentication and keys, restructures WMM/security/HT IEs, manages HT capability state, and drives roaming. The file was read completely as a 2580-line source file.

## Important APIs, Types, and Functions

Initialization and cleanup functions include `rtw_init_mlme_priv()`, `_rtw_free_mlme_priv()`, `rtw_free_mlme_priv()`, `rtw_free_mlme_priv_ie_data()`, and timer setup through static `rtw_init_mlme_timer()`. Queue and network helpers include `rtw_alloc_network()`, `_rtw_free_network()`, `_rtw_free_network_nolock()`, `_rtw_find_network()`, `rtw_find_network()`, `rtw_free_network_queue()`, `rtw_free_network_nolock()`, `_rtw_find_same_network()`, `rtw_get_oldest_wlan_network()`, `update_network()`, `rtw_update_scanned_network()`, `rtw_add_network()`, `rtw_is_same_ibss()`, `is_same_ess()`, and `is_same_network()`.

Event/state functions include `rtw_survey_event_callback()`, `rtw_surveydone_event_callback()`, `rtw_joinbss_event_prehandle()`, `rtw_joinbss_event_callback()`, `rtw_stassoc_event_callback()`, `rtw_stadel_event_callback()`, `rtw_cpwm_event_callback()`, `rtw_wmm_event_callback()`, `_rtw_join_timeout_handler()`, `rtw_scan_timeout_handler()`, `rtw_dynamic_check_timer_handler()`, `rtw_scan_abort()`, `rtw_indicate_connect()`, `rtw_indicate_disconnect()`, and `rtw_indicate_scan_done()`.

Candidate/security/IE/HT helpers include `rtw_select_roaming_candidate()`, `rtw_select_and_join_from_scanned_queue()`, `rtw_set_auth()`, `rtw_set_key()`, `rtw_restruct_wmm_ie()`, `rtw_restruct_sec_ie()`, `rtw_reset_securitypriv()`, `rtw_init_registrypriv_dev_network()`, `rtw_update_registrypriv_dev_network()`, `rtw_joinbss_reset()`, `rtw_ht_use_default_setting()`, `rtw_build_wmm_ie_ht()`, `rtw_restructure_ht_ie()`, `rtw_update_ht_cap()`, `rtw_issue_addbareq_cmd()`, `rtw_append_exented_cap()`, `rtw_set_to_roam()`, `rtw_dec_to_roam()`, `rtw_to_roam()`, `rtw_roaming()`, `_rtw_roaming()`, and `rtw_linked_check()`.

## Control Flow

Initialization sets default station state, queue heads, locks, active scan mode, association identity, scan-deny state, roaming defaults, and four timers: association timeout, scan timeout, dynamic check, and scan-deny expiration. A preallocated `MAX_BSS_CNT` pool of `struct wlan_network` objects backs the free and scanned queues.

Survey events validate BSS size, update IBSS timestamps when relevant, and add or update scanned networks unless currently linking. `rtw_update_scanned_network()` matches by BSSID/SSID/capability, updates signal quality with smoothing, selects whether beacon/probe-response IEs should replace the existing IEs, reuses the oldest slot if the free pool is empty, and links new entries into the scanned queue. Survey-done clears `_FW_UNDER_SURVEY`, deletes the scan timeout, restarts signal stats, then either continues a pending join, creates an IBSS master network, handles roaming candidate selection, or simply indicates scan completion.

Join event prehandling validates returned BSS length and join result, clears traffic transition counters, finds the target scanned network under the scanned-queue lock, updates `cur_network` from firmware result plus scanned IEs, creates/updates station info for station mode, indicates connection, and cancels the association timer. Join failures schedule the association timer for immediate failure handling. Station association/deletion events update AP/IBSS station tables, media status reports to firmware, cfg80211 station indications, and IBSS recreation when the last peer leaves.

Timeouts provide state recovery. `_rtw_join_timeout_handler()` retries roaming joins while attempts remain, otherwise indicates disconnect and frees scan queue entries. `rtw_scan_timeout_handler()` clears survey state and indicates aborted scan. The dynamic timer either performs LPS-aware link/traffic checks while firmware is in PS mode or enqueues the dynamic-check work command; it also triggers periodic auto-scans when configured and idle enough.

Candidate selection scans `scanned_queue` under lock. Join candidates must match requested BSSID/SSID, desired security, optional roaming freshness and ESS constraints, and highest RSSI. Roaming candidates must be same ESS, desired security, optionally match a target BSSID, be fresh, exceed the current scanned RSSI by the configured threshold, and beat any previous candidate.

Security and IE restructuring runs before join commands. `rtw_set_auth()` and `rtw_set_key()` enqueue firmware commands for auth/key state. `rtw_restruct_sec_ie()` copies fixed IEs, appends WPS or supplicant WPA/RSN IE, and appends PMKID when cached. `rtw_restruct_wmm_ie()` copies and rewrites a WMM vendor IE. HT helpers derive default HT settings from registry and HAL capabilities, build outgoing WMM/HT/extended-capability IEs, update current HT capability state from AP IEs, and issue ADDBA requests after enough unicast TX activity.

## State and Persistence Behavior

MLME state is stored in `struct mlme_priv`: firmware-state bitmask, current network, scanned network queue, free BSS pool, association intent (`assoc_ssid`, `assoc_bssid`, `assoc_by_bssid`, `to_join`), scan state/timers, scan-deny atomic, roaming counters and target, QoS/HT state, WPS/P2P custom IE buffers, and cached association request/response IEs. `struct security_priv` holds auth/encryption algorithms, keys, PMKID cache, TKIP countermeasure state, WPS IE, supplicant IE, and group-key state. `struct sta_priv` owns station entries for the current AP/peers and broadcast/multicast station.

There is no file persistence. Runtime state persists across scans/joins until explicitly reset on disconnect, mode change, security reset, or driver teardown. PMKID and TKIP countermeasure state are explicitly backed up and restored across `rtw_reset_securitypriv()` for 802.1X. Hardware/firmware state is updated indirectly through command enqueues and `rtw_hal_set_hwreg()` calls, including media status, RX aggregation thresholds, power state, and ADDBA.

## Dependencies and Integration Points

Direct includes are `linux/etherdevice.h`, `drv_types.h`, `hal_btcoex.h`, and `linux/jiffies.h`. This file is the main integration hub for the driver core: it calls command helpers in `rtw_cmd.c`, IE/rate helpers in `rtw_ieee80211.c`, ioctl-set paths in `rtw_ioctl_set.c`, cfg80211 indication functions, station-table and AP-mode helpers, MLME extension callbacks, HAL register/default-variable APIs, Bluetooth coexistence through command paths, transmit scheduling, receive signal-stat timers, security/CAM/key helpers, and power-management helpers.

## Risks and Edge Cases

Locking and asynchronous state transitions are the dominant risks. MLME lock, scanned-queue lock, free-queue lock, station locks, timers, command callbacks, and cfg80211 indications interleave. Some functions document required caller locking, and violating those assumptions can corrupt queue lists or firmware-state bits. Timer handlers can race with successful scan/join completion unless timers are deleted in the right order.

Network queue management reuses fixed preallocated objects. Incorrect handling of `fixed`, oldest-entry reuse, or scanned/free queue movement can lose the current network, leak BSS entries, or leave stale cfg80211 BSS links. IE handling copies large buffers such as `MAX_IE_SZ` and rewrites WMM/security/HT IEs with limited local capacity checks; malformed or oversized IEs from firmware/scans should be fuzzed. Several functions depend on fixed offsets into beacon IEs.

Roaming state is subtle. `to_roam`, `to_join`, `roam_network`, `roam_tgt_addr`, scan freshness, and RSSI thresholds interact with disconnect handling and active roam reason codes. A failed roam can either retry, reconnect to another candidate, or indicate disconnect. Security reset preserves PMKID/TKIP state only in the 802.1X path. IBSS/AP paths share station resource cleanup but have different link indication semantics.

HT and aggregation behavior depends on registry flags, HAL capabilities, AP HT info, and current encryption. Regressions can change negotiated bandwidth, SGI, STBC, LDPC, AMPDU density, or ADDBA issuance. `rtw_issue_addbareq_cmd()` relies on TX packet counts and station pointer consistency, so stale `pattrib->psta` or peer removal must be handled.

## Test Signals

High-value tests include MLME init/free leak checks, scan event add/update/expire behavior, scanned queue full reuse, beacon-vs-probe-response IE precedence, join success/failure/timeout, scan timeout, scan abort, station connect/disconnect indications, AP station association/deassociation, IBSS creation/recreation, and driver stop/surprise removal during timers. Roaming tests should cover expired-link roaming, active roaming, no candidate, stale candidate, target-BSSID roam, retry exhaustion, and RSSI threshold decisions.

Security tests should cover open/WEP/WPA/WPA2/WPS IE restructuring, PMKID append, PMKID preservation across security reset, key command allocation failures, TKIP countermeasure behavior via higher-level callers, and 802.1X station blocking. HT/WMM tests should cover WMM IE rewrite, default HT capability construction from registry/HAL flags, AP HT operation parsing, 20/40 MHz offset decisions, AMPDU max length/density, ADDBA issuance thresholds, and extended-capability BSS coexistence. Static analysis should focus on list operations under the correct locks, timer deletion with locks dropped/reacquired, unchecked IE lengths, and ownership of dynamically allocated WPS/P2P/assoc IE buffers.
