# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_ioctl_set.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_ioctl_set.c` implements the driver's legacy 802.11 set operations: validating requested BSSID/SSID, driving scan/join/disconnect mode changes, setting authentication and WEP keys, and reporting current maximum link rate. It is a control-plane bridge between ioctl/cfg80211-facing requests and the MLME/command machinery. The file was read completely as a 500-line source file.

## Important APIs, Types, and Functions

Validation helpers are `rtw_validate_bssid()` and `rtw_validate_ssid()`. Connection flow is driven by `rtw_do_join()`, `rtw_set_802_11_ssid()`, and `rtw_set_802_11_connect()`. Mode and disconnect controls are `rtw_set_802_11_infrastructure_mode()` and `rtw_set_802_11_disassociate()`. Scanning is exposed as `rtw_set_802_11_bssid_list_scan()`. Security setters are `rtw_set_802_11_authentication_mode()` and `rtw_set_802_11_add_wep()`. Link-rate reporting is `rtw_get_cur_max_rate()`.

Important data touched includes `mlme_priv` (`fw_state`, `assoc_ssid`, `assoc_bssid`, `assoc_by_bssid`, `to_join`, `pscanned`, current/scanned networks), `registry_priv.dev_network`, `security_priv`, `wlan_network`, and `sta_info`.

## Control Flow

`rtw_do_join()` assumes MLME state is locked by its caller. It marks `_FW_UNDER_LINKING`, sets `to_join`, and either starts a site survey if the scanned queue is empty or selects a candidate through `rtw_select_and_join_from_scanned_queue()`. If candidate selection fails in IBSS mode, it converts to ADHOC master by updating the registry network, generating a random IBSS BSSID, and issuing `rtw_createbss_cmd()`. If infrastructure selection fails and traffic is not busy or roaming is active, it triggers a directed scan for the associated SSID.

`rtw_set_802_11_ssid()` rejects requests before hardware init, serializes with `mlmepriv->lock`, handles current link/adhoc cleanup when the requested SSID changes, runs TKIP countermeasure and SSID validation, updates `assoc_ssid` and `assoc_by_bssid`, then either defers join until an in-progress survey completes or calls `rtw_do_join()`. `rtw_set_802_11_connect()` is the BSSID/SSID combined path; it validates either identifier, records `assoc_bssid` when valid, and uses the same survey-or-join decision.

`rtw_set_802_11_infrastructure_mode()` transitions between AP, IBSS, infrastructure, and auto/unknown modes. It stops AP mode when leaving AP, disassociates and frees resources as needed, indicates disconnect for previous station/IBSS links, clears firmware state, sets the new state, and starts AP mode when requested. Scan requests are suppressed while scanning, linking, or busy with traffic; otherwise they respect scan-deny and enqueue `rtw_sitesurvey_cmd()`. WEP setup copies key material into `security_priv`, sets algorithm/key index, and enqueues `rtw_set_key()`.

`rtw_get_cur_max_rate()` checks linked/adhoc-master state, finds the station for the current BSSID, and returns either HT MCS-derived max rate through `rtw_mcs_rate()` or the max legacy supported rate converted to 100 Kbps units.

## State and Persistence Behavior

This file mutates volatile association intent and mode state in `mlme_priv`, including `assoc_ssid`, `assoc_bssid`, `assoc_by_bssid`, `_FW_UNDER_LINKING`, `to_join`, and infrastructure mode. It mutates security state for authentication mode, WEP keys, default key lengths, privacy algorithm, and privacy key index. It also indirectly changes firmware, CAM, AP mode, cfg80211 link state, and power state by issuing command helpers and MLME functions.

There is no on-disk persistence. Requested credentials and WEP keys persist only in the adapter's runtime security structures until reset/disconnect or driver teardown.

## Dependencies and Integration Points

The file includes `drv_types.h` and integrates heavily with `rtw_cmd.c` command constructors, `rtw_mlme.c` selection/resource/state helpers, station-table helpers, AP-mode helpers (`start_ap_mode()`, `stop_ap_mode()`), power wakeup, TKIP countermeasure handling, cfg80211 indication helpers, and IEEE rate helpers from `rtw_ieee80211.c`. It is called by the driver's user-facing wireless configuration paths.

## Risks and Edge Cases

The join path is stateful and lock-sensitive. Some command enqueues occur while `mlmepriv->lock` is held, and later asynchronous callbacks/timers complete the transition; regressions can leave `_FW_UNDER_LINKING` or `to_join` stuck. Scan suppression during busy traffic can make connection attempts fail even with a valid SSID/BSSID. BSSID/SSID validation accepts a request if either identifier is valid, so partial requests must be tested.

Security setup is legacy WEP-oriented in this file. `rtw_set_802_11_add_wep()` copies `wep->key_length` bytes into fixed key storage after only algorithm selection by length; callers must provide a properly sized `struct ndis_802_11_wep`. Infrastructure-mode changes clear broad firmware state with `_clr_fwstate_(~WIFI_NULL_STATE)`, making ordering around disconnect indications and resource cleanup important. `rtw_get_cur_max_rate()` depends on a station entry; transient disconnects return zero.

## Test Signals

Tests should cover invalid/zero/broadcast/multicast BSSID, SSID length above 32, connect by SSID only, BSSID only, and both, plus behavior while hardware init is false. MLME integration tests should cover empty scanned queue directed scans, candidate join success, candidate failure with busy traffic, IBSS create-BSS fallback, roaming-directed join, AP/IBSS/infrastructure mode transitions, disconnect while linked, and scan-deny behavior. Security tests should cover WEP40/WEP104/default invalid lengths, key indexes 0-3 and out of range, authentication mode mapping, and command enqueue failures. Link-rate tests should cover not linked, missing station, legacy rates, and HT MCS/short-GI/40 MHz cases.
