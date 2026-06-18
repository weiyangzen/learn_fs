# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/wlan_bssdef.h

Purpose: defines the rtl8723bs driver's NDIS-style 802.11 BSS, SSID, authentication, encryption, network, beacon, and power-save data structures used by MLME, cfg80211 translation, scan cache, and connection setup.

Important APIs/types/functions: constants include `MAX_IE_SZ`, SSID/rate lengths, `MIC_CHECK_TIME`, `NUM_PRE_AUTH_KEY`, and `NUM_PMKID_CACHE`. Core types are `struct ndis_802_11_ssid`, `enum ndis_802_11_network_type`, `struct ndis_802_11_conf`, `enum ndis_802_11_network_infrastructure`, `struct ndis_802_11_wep`, `struct wlan_phy_info`, `struct wlan_bcn_info`, `struct wlan_bssid_ex`, and `struct wlan_network`. The inline `get_wlan_bssid_ex_sz()` computes the variable-size BSS record length by subtracting the fixed IE array capacity and adding the active IE length.

Control flow: this header has no active runtime flow beyond the inline size helper. It shapes scan/connect control flow by placing `struct wlan_bssid_ex network` as the last major payload inside `struct wlan_network`, letting scan queues carry list metadata plus a full BSS descriptor.

State and persistence: all state is in caller-owned structures. `struct wlan_network` persists scan results with `last_scanned`, `fixed`, `aid`, `join_res`, raw IEs, and parsed beacon metadata. Security state is represented as NDIS auth/encryption enums and WEP/PMKID constants consumed by `security_priv`.

Dependencies and integration: depends on kernel/list and Ethernet types from surrounding rtl8723bs headers. Used by MLME, cfg80211, AP, security, and command paths to translate between firmware/Realtek NDIS-like state and Linux wireless abstractions.

Risks: `struct wlan_bssid_ex` is packed and embeds a fixed `ies[MAX_IE_SZ]`; callers must validate `ie_length` before copying. `get_wlan_bssid_ex_sz()` trusts `ie_length`, so corrupted scan data can produce oversized lengths if not guarded by readers. Several enums include "Max" sentinels that are not valid runtime modes.

Test signals: scan and association tests should exercise SSID length bounds, IE length truncation/rejection, WEP key sizing, WPA/WPA2 parsed beacon metadata, PMKID cache size assumptions, and cfg80211 BSS reporting from `struct wlan_network`.
