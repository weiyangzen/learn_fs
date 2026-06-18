<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ioctl_set.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ioctl_set.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ioctl_set.h` declares high-level setters used by ioctl/cfg80211 paths to request authentication, WEP keys, scans, infrastructure mode, SSID/BSSID joins, and current-rate queries. The source was reviewed as a complete 28-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `rtw_set_802_11_authentication_mode`, `rtw_set_802_11_add_wep`, `rtw_set_802_11_disassociate`, `rtw_set_802_11_bssid_list_scan`, `rtw_set_802_11_infrastructure_mode`, `rtw_set_802_11_ssid`, `rtw_set_802_11_connect`, `rtw_validate_bssid`, `rtw_validate_ssid`, `rtw_do_join`, and `rtw_get_cur_max_rate`.

## Control Flow

Userspace requests are validated, translated into MLME/security state changes, and often enqueue commands through `rtw_cmd.h` to scan, join, set keys, or disconnect.

## State and Persistence Behavior

Mutates MLME association targets, security mode/key material, requested infrastructure mode, and scan state.

## Dependencies and Integration Points

Depends on NDIS-style structs, `rtw_mlme.h`, `rtw_security.h`, `rtw_cmd.h`, and cfg80211/ioctl front ends. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Input validation is security-sensitive. SSID/BSSID length checks and WEP key bounds must be enforced before state mutation.

## Test Signals

Invalid SSID/BSSID inputs, WEP/WPA configuration, scan/connect/disconnect through iw/wpa_supplicant, and current-rate reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ioctl_set.h -->
