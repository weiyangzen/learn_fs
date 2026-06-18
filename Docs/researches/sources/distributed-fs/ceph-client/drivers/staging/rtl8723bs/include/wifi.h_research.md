<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/wifi.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/wifi.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/wifi.h` defines 802.11 frame control constants, management/data frame structs, address and sequence helper macros, reason/status codes, IE IDs, WMM constants, and frame header manipulation helpers. The source was reviewed as a complete 464-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct rtw_ieee80211_hdr`, `struct rtw_ieee80211_hdr_3addr`, `struct wlan_bssid_ex`, `SetFrameSubType`, `GetFrameSubType`, `GetToDs`, `GetFrDs`, `GetAddr1Ptr`, `GetAddr2Ptr`, `GetAddr3Ptr`, `GetSequence`, `SetSeqNum`, `GetPrivacy`, `SetPrivacy`, frame type/subtype constants, and IE constants such as `_SSID_IE_`, `_SUPPORTEDRATES_IE_`, `_RSN_IE_`, and WMM definitions.

## Control Flow

Management and data TX/RX paths use these macros to construct headers, inspect received frames, parse addresses, manipulate sequence numbers, and recognize IEs/subtypes.

## State and Persistence Behavior

No global storage; helpers mutate or read caller-owned frame buffers and MLME network descriptors.

## Dependencies and Integration Points

Used throughout MLME, MLME extension, receive, transmit, AP, security, and IEEE80211 IE helper code. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Frame header helpers operate on raw packet bytes. Bounds must be enforced before use, and endian assumptions must match 802.11 little-endian fields.

## Test Signals

Management/data frame encode/decode, subtype/address extraction, privacy/sequence bit manipulation, malformed short frame handling, and AP/client interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/wifi.h -->
