# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_ap.c

## Purpose
Access-point mode management for the RTL8723BS driver. It parses hostapd beacon data, starts/restores/stops BSS state, maintains associated station state, handles beacon/TIM/capability updates, manages AP security keys and ACLs, and ages inactive stations.

## Important APIs, Types, And Functions
Key entry points include `init_mlme_ap_info()`, `free_mlme_ap_info()`, `start_bss_network()`, `rtw_check_beacon_data()`, `expire_timeout_chk()`, `add_ratid()`, `update_bmc_sta()`, `update_sta_info_apmode()`, `sta_info_update()`, `ap_sta_info_defer_update()`, `bss_cap_update_on_sta_join()`, `bss_cap_update_on_sta_leave()`, `ap_free_sta()`, `rtw_sta_flush()`, `rtw_ap_restore_network()`, `start_ap_mode()`, `stop_ap_mode()`, `update_beacon()`, ACL helpers, and key helpers `rtw_ap_set_pairwise_key()`, `rtw_ap_set_group_key()`, `rtw_ap_set_wep_key()`.

## Control Flow
AP initialization sets locks, ACL queues, and AP counters. `rtw_check_beacon_data()` validates the driver is in AP state, copies supplied beacon IEs, extracts beacon interval/capability/SSID/channel/rates, parses ERP, WPA/WPA2, WMM, HT capability/operation, updates security and HT/QoS state, starts BSS through the command path, allocates the AP's own station info, and indicates connection. `start_bss_network()` programs hardware BSSID, security, EDCA, beacon interval, channel/bandwidth, basic rates, capability, beacon/TIM, and bc/mc station state. Station join/update paths calculate QoS/HT/VCS/rate masks and update beacon protection counters; leave/free paths tear down AMPDU, clear keys, notify cfg80211/firmware, update counters, and free station info. Periodic expiry checks auth/asoc lists, sends null-data keepalives when configured, handles sleeping stations through TIM bits, and flushes dead stations.

## State And Persistence
State spans `mlme_priv`, `mlme_ext_priv`, `sta_priv`, `security_priv`, per-station HT/security fields, ACL list, TIM bitmap, beacon IE buffers, AP capability counters, and hardware CAM/key/rate state. It is all runtime state; WPS/P2P IE pointers are reset on AP mode start/stop.

## Dependencies And Integration Points
Depends on Realtek MLME, command, station management, security, HAL register/key/rate APIs, cfg80211 notifications, beacon command transmission, HT/WMM/ERP parsers, SDIO channel selection, and BT coexistence disconnect notification.

## Risks
The code mutates raw beacon IE buffers and uses many protocol offsets, so length validation is critical. Several beacon update stubs are empty, leaving some IEs unchanged. `rtw_ht_operation_update()` returns early when HT is enabled, which may be intentional legacy behavior but is easy to misread. Station list manipulation mixes locks with callbacks that may free state. Static ACL capacity is fixed. Security key commands are asynchronous and allocation failures return generic `_FAIL`.

## Test Signals
Hostapd AP start with open/WEP/WPA/WPA2, WMM and HT beacons, 20/40 MHz channel selection, TIM updates for sleeping stations, station join/leave capability counters, ACL add/remove/broadcast clear, pairwise/group/WEP key installation, inactive station expiry and keepalive, AP restore after power save, AP stop cleanup, and cfg80211 disassociation events.
