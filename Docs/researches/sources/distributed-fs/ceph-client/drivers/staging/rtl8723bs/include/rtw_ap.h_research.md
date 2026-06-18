<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ap.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ap.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ap.h` declares AP-mode helpers for beacon updates, station association/disassociation handling, client expiration, and AP initialization/free. The source was reviewed as a complete 39-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `init_mlme_ap_info`, `free_mlme_ap_info`, `rtw_indicate_sta_assoc_event`, `rtw_indicate_sta_disassoc_event`, `rtw_sta_flush`, `expire_timeout_chk`, `update_beacon`, `add_RATid`, and `rtw_ap_inform_ch_switch`.

## Control Flow

When operating as AP, MLME and station events call these helpers to maintain station state, refresh beacon IEs, notify cfg80211/hostapd, and update rate-adaptation entries.

## State and Persistence Behavior

Touches AP MLME state, station tables, beacon contents, TIM/WMM/ERP/HT IEs, and rate masks.

## Dependencies and Integration Points

Integrates with `sta_info.h`, `rtw_mlme.h`, `rtw_mlme_ext.h`, `ieee80211.h`, and cfg80211 AP notifications. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Beacon updates and station table changes must be serialized. Incorrect TIM or association indication behavior breaks power-save clients and userspace AP control.

## Test Signals

AP bring-up, client association/disassociation, beacon IE changes, inactivity expiration, channel switch indication, and multi-client traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ap.h -->
