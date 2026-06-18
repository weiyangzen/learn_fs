<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_mlme.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_mlme.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_mlme.h` defines the core MLME state machine data: Wi-Fi state flags, scan/join timeouts, scanned-network queues, current network, roam state, timers, link detection, and many scan/join/connect/disconnect APIs. The source was reviewed as a complete 398-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct mlme_priv`, `struct sitesurvey_ctrl`, `struct rt_link_detect_t`, `struct hostapd_priv`, Wi-Fi state macros such as `WIFI_ASOC_STATE` and `WIFI_UNDER_LINKING`, `rtw_init_mlme_priv`, `rtw_free_mlme_priv`, `rtw_joinbss_event_callback`, `rtw_survey_event_callback`, `rtw_indicate_connect`, `rtw_indicate_disconnect`, `rtw_scan_abort`, `check_fwstate`, `set_fwstate`, `rtw_update_scanned_network`, `rtw_restruct_sec_ie`, and roaming helpers.

## Control Flow

Scan commands populate scanned queues, join selection chooses a target, join/connect events update firmware state and cfg80211, timers handle scan/join timeouts, and roaming helpers select better candidates when configured.

## State and Persistence Behavior

`mlme_priv` is long-lived adapter state containing locks, free/scanned BSS queues, current network, association SSID/BSSID, timers, WMM/HT/security IEs, scan deny flags, link metrics, and roam counters.

## Dependencies and Integration Points

Integrated with `rtw_cmd.h`, `rtw_event.h`, `rtw_security.h`, `rtw_ht.h`, `sta_info.h`, `ioctl_cfg80211.h`, and AP/hostapd support. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

MLME state flags are shared across timers, command thread, RX management handling, and cfg80211 notifications. Races can produce stuck scanning/linking states or double indications.

## Test Signals

Scan timeout, successful and failed join, roaming, disconnect during scan/join, AP/IBSS paths, security IE restructuring, and cfg80211 notification sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_mlme.h -->
