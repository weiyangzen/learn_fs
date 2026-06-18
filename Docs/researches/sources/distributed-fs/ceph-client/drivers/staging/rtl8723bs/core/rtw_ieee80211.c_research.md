# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_ieee80211.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_ieee80211.c` contains 802.11 utility routines for RTL8723BS: supported-rate classification, IE construction/search/removal, WPA/WPA2/WAPI/WPS parsing, generic management-frame IE parsing, MAC address selection, beacon security/HT information extraction, MCS max-rate calculation, action-frame parsing, and public action string lookup. The file was read completely as a 1171-line source file.

## Important APIs, Types, and Functions

The file defines WPA/RSN OUI and cipher-suite arrays (`RTW_WPA_OUI_TYPE`, `WPA_CIPHER_SUITE_*`, `RSN_CIPHER_SUITE_*`) and rate tables (`WIFI_CCKRATES`, `WIFI_OFDMRATES`). Rate helpers include `rtw_get_bit_value_from_ieee_value()`, `rtw_is_cckrates_included()`, `rtw_is_cckratesonly_included()`, `rtw_check_network_type()`, `rtw_set_supported_rate()`, `rtw_get_rateset_len()`, and `rtw_mcs_rate()`.

IE helpers include `rtw_set_fixed_ie()`, `rtw_set_ie()`, `rtw_get_ie()`, `rtw_get_ie_ex()`, `rtw_ies_remove_ie()`, `rtw_generate_ie()`, `rtw_get_wpa_ie()`, `rtw_get_wpa2_ie()`, `rtw_get_wapi_ie()`, `rtw_get_sec_ie()`, `rtw_get_wps_ie()`, `rtw_get_wps_attr()`, and `rtw_get_wps_attr_content()`. Security parsers include `rtw_get_wpa_cipher_suite()`, `rtw_get_wpa2_cipher_suite()`, `rtw_parse_wpa_ie()`, and `rtw_parse_wpa2_ie()`.

Management-frame parsing is centered on `rtw_ieee802_11_parse_elems()` and static `rtw_ieee802_11_parse_vendor_specific()`, filling `struct rtw_ieee802_11_elems`. Device/network helpers include `rtw_macaddr_cfg()`, static `rtw_get_cipher_info()`, `rtw_get_bcn_info()`, `rtw_action_frame_parse()`, and `action_public_str()`.

## Control Flow

Rate helpers classify a null-terminated rate set by stripping the basic-rate bit and matching CCK or OFDM encoded rates. IE writers append `[id, length, payload]` tuples and update frame length counters. `rtw_generate_ie()` builds an IBSS-style fixed IE area, SSID, supported rates, DS params, IBSS params, extended rates, and leaves HT generation as a placeholder.

IE scanning generally walks a byte buffer by reading `id` and `len`, checking that the tuple fits within the caller-provided limit, then either returning/copying the match or moving to the next IE. `rtw_get_ie_ex()` and `rtw_ieee802_11_parse_elems()` are the most robust bounded parsers. WPA/WPA2 parsing validates EID/OUI/version/length, reads group cipher, pairwise cipher count, each cipher selector, and optionally detects 802.1X AKM. WPS attribute parsing validates the WPS vendor OUI, then walks big-endian attribute ID/length/value records.

`rtw_ieee802_11_parse_elems()` iterates generic management IEs, filling pointers and lengths for SSID, rates, FH/DS/CF/TIM/IBSS/challenge/ERP, extended rates, RSN, power capability, supported channels, mobility/FT/timeout, HT/VHT capability/operation, opmode notification, and selected vendor-specific WPA/WME/WPS/Broadcom HT records. It returns `PARSE_OK`, `PARSE_UNKNOWN`, or `PARSE_FAILED`.

`rtw_macaddr_cfg()` prefers the module parameter `rtw_initmac` if parseable, otherwise starts from the EFUSE-provided address, and replaces broadcast/zero addresses with an OF `local-mac-address` property or a random MAC. `rtw_get_bcn_info()` extracts privacy, WPA/RSN protocol, cipher information, and HT capability/operation data from a scanned network's beacon/probe IEs.

## State and Persistence Behavior

Most functions are stateless buffer utilities. Persistent effects are limited to caller-provided structures: `registry_priv.dev_network` IE buffers, `wlan_network.bcn_info`, `wlan_network.network.privacy`, and the netdev MAC address buffer. Global OUI/cipher arrays are mutable `u8`/`u16` globals, though they are treated as constants.

The parser functions typically store pointers into the original IE buffer rather than deep-copying into `struct rtw_ieee802_11_elems`, so the source buffer must outlive the parsed result. IE construction and removal mutate caller-owned buffers in place and require the caller to provide sufficient capacity.

## Dependencies and Integration Points

Direct includes are `drv_types.h`, `linux/hex.h`, `linux/of.h`, and `linux/unaligned.h`. The file integrates with Linux Ethernet helpers (`ether_addr_copy()`, broadcast/zero checks, `eth_random_addr()`), device tree MAC lookup, unaligned endian helpers, cfg80211/IEEE 802.11 constants, MLME scanned-network handling in `rtw_mlme.c`, join IE rewriting in `rtw_cmd.c`, ioctl-set max-rate reporting in `rtw_ioctl_set.c`, and security state setup in MLME/security code.

## Risks and Edge Cases

Several older IE walkers (`rtw_get_wapi_ie()`, `rtw_get_sec_ie()`, `rtw_get_wps_ie()`, and WPS attribute parsing) do less complete `cnt + 2 + len <= in_len` validation than `rtw_get_ie_ex()` and `rtw_ieee802_11_parse_elems()`. Malformed beacon/probe-response buffers can therefore stress out-of-bounds reads unless upstream frame validation is strict. `rtw_action_frame_parse()` assumes `frame_len` is sufficient for a 3-address header and action body but does not check it before dereferencing.

WPA/WPA2 parsing ORs pairwise cipher results into caller-provided integers and does not clear them internally; callers must initialize outputs. `rtw_get_wpa_ie()` returns the IE pointer but reports only payload length in `*wpa_ie_len`, while parse callers add two bytes; this convention is easy to misuse. `rtw_generate_ie()` writes fixed and variable IEs into `dev_network->ies` with no local capacity checks. Public OUI arrays are not `const`, so accidental writes could corrupt parser behavior.

## Test Signals

Parser fuzzing is the strongest signal: truncated IEs, overlong lengths, zero-length vendor IEs, invalid pairwise counts, malformed WPS attributes, and short action frames. Unit tests should cover WPA/WPA2 cipher and 802.1X detection, WPS IE and attribute extraction, IE removal with repeated matching IEs, rate-set classification for B/G/BG/invalid channels, MAC address fallback order, beacon encryption classification, HT capability extraction, and MCS max-rate outputs for each MCS bit with 20/40 MHz and short-GI combinations. Integration tests should include scanning APs advertising WPA, WPA2, WEP, open, WPS, WME, HT, and malformed vendor-specific IEs.
