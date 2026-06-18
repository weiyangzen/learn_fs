# sources/distributed-fs/ceph-client/include/linux/ieee80211-vht.h

## Purpose
Defines IEEE 802.11ac VHT capability, operation, MCS, operating-mode notification, A-MPDU, channel-width, and action-code interfaces.

## Important APIs, Types, And Functions
Key types are `ieee80211_vht_mcs_info`, `ieee80211_vht_cap`, `ieee80211_vht_operation`, `ieee80211_vht_opmode_bits`, `ieee80211_vht_max_ampdu_length_exp`, `ieee80211_vht_mcs_support`, and `ieee80211_vht_chanwidth`. The exported `ieee80211_get_vht_max_nss()` computes maximum usable spatial streams for a bandwidth/MCS combination, considering extended NSS bandwidth capability and operating-mode notification.

## Control Flow
Parsers cast validated VHT capability/operation elements, decode capability masks, MCS maps, channel width, center frequencies, and operation-mode notification bits. Rate-control or association code calls `ieee80211_get_vht_max_nss()` to reconcile advertised MCS/NSS capability with bandwidth and local extended-NSS support.

## State And Persistence
No state is owned here. Parsed VHT capability, operation, and opmode values persist in station/BSS state maintained by the wireless stack.

## Dependencies And Integration Points
Depends on Linux types and Ethernet constants. Integrates with cfg80211/mac80211 VHT association, channel definition, rate control, beamforming capability, aggregation limits, and HE 6 GHz capability definitions that reuse VHT MPDU/A-MPDU encodings.

## Risks
Packed little-endian fields must be converted before bit operations. Extended NSS bandwidth support is subtle and can overstate supported streams if local capability is ignored. Incorrect channel-width or MCS-map parsing can cause failed association or invalid rates.

## Test Signals
VHT capability/operation parsing, MCS map extraction, maximum NSS calculation for 80/160/80+80 and extended-NSS cases, opmode notification handling, A-MPDU exponent limits, and interop with 802.11ac APs.
