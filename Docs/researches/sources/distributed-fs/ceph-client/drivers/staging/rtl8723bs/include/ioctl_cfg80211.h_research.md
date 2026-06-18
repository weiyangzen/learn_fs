<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/ioctl_cfg80211.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/ioctl_cfg80211.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/ioctl_cfg80211.h` declares the cfg80211 integration layer that owns `wireless_dev` state, informs scan/connect/disconnect events, and bridges management-frame operations to the Linux wireless stack. The source was reviewed as a complete 58-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct rtw_wdev_priv`, `wiphy_to_adapter`, `wdev_to_ndev`, `rtw_wdev_alloc`, `rtw_wdev_free`, `rtw_wdev_unregister`, `rtw_cfg80211_init_wiphy`, `rtw_cfg80211_inform_bss`, `rtw_cfg80211_indicate_connect`, `rtw_cfg80211_indicate_disconnect`, `rtw_cfg80211_indicate_scan_done`, and management TX/RX wrapper macros.

## Control Flow

Driver MLME events call cfg80211 indication helpers; scan completion reports BSS entries, connection state changes update userspace, and action/management frames are passed to cfg80211 APIs.

## State and Persistence Behavior

`rtw_wdev_priv` stores the adapter backpointer, active scan request, monitor netdev, and power-management state around the kernel `wireless_dev`.

## Dependencies and Integration Points

Depends on Linux cfg80211/netdev types, `struct wlan_network`, `struct adapter`, and MLME event callbacks. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Incorrect scan-request lifetime or duplicate connect/disconnect indications can confuse cfg80211 and userspace. Kernel API wrapper macros must match the kernel version used by this source tree.

## Test Signals

iw scan/connect/disconnect flows, aborted scans, AP station association indications, remain-on-channel/action frame tests, and suspend with cfg80211 power management.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/ioctl_cfg80211.h -->
