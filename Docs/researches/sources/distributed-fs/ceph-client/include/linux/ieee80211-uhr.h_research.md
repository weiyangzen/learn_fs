# sources/distributed-fs/ceph-client/include/linux/ieee80211-uhr.h

## Purpose
Defines draft IEEE 802.11bn UHR operation and capability element layouts, UHR MAC/PHY capability bits, DPS/NPCA/P-EDCA/DBE parameter structures, SMD information, and inline validators/accessors.

## Important APIs, Types, And Functions
Important structures include `ieee80211_uhr_operation`, `ieee80211_uhr_npca_info`, `ieee80211_uhr_dps_info`, `ieee80211_uhr_dbe_info`, `ieee80211_uhr_p_edca_info`, `ieee80211_uhr_cap`, `ieee80211_uhr_cap_phy`, and `ieee80211_smd_info`. Helpers are `ieee80211_uhr_oper_size_ok()`, `ieee80211_uhr_npca_info()`, `ieee80211_uhr_npca_dis_subch_bitmap()`, `ieee80211_uhr_capa_size_ok()`, and `ieee80211_uhr_phy_cap()`.

## Control Flow
UHR operation validation starts with fixed operation fields, returns immediately for beacons, and otherwise walks optional DPS, NPCA, P-EDCA, and DBE fields in bit-order, adding disabled-subchannel bitmap lengths when presence bits are set. Capability validation accounts for AP-only DBE capability parameters before locating PHY capabilities.

## State And Persistence
No mutable state is stored. UHR operation/capability data is on-wire management-frame state cached elsewhere after validation.

## Dependencies And Integration Points
Depends on Linux types, Ethernet length, packed little-endian fields, and bit operations. Integrates with emerging Wi-Fi UHR/cfg80211/mac80211 parsing, DBE bandwidth negotiation, NPCA/P-EDCA operation, DPS mode handling, and SMD information exchange.

## Risks
This tracks draft 802.11bn fields, so spec churn is a major compatibility risk. Accessors assume `ieee80211_uhr_oper_size_ok(..., false)` or capability validation has already succeeded. AP vs non-AP capability size differences and optional bitmap offsets are likely bug sources.

## Test Signals
Operation-size tests for every optional-field combination, beacon vs non-beacon behavior, NPCA/DBE bitmap presence, AP and non-AP capability parsing, DBE MCS map length combinations, malformed/truncated UHR elements, and interop against updated draft vectors.
