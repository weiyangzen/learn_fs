# sources/distributed-fs/ceph-client/include/linux/ieee80211-eht.h

## Purpose
Defines IEEE 802.11be EHT data structures, capability/operation bit fields, multi-link element layouts, protected EHT action codes, TID-to-link mapping, and inline validators/parsers used by cfg80211/mac80211 and drivers.

## Important APIs, Types, And Functions
Important packed types include EHT capability and operation elements, MCS/NSS maps, EHT operation info, bandwidth indication, multi-link element/common-info variants, per-STA profiles, and TTLM elements. Inline helpers compute MCS/NSS and PPE sizes, validate EHT capability/operation/bandwidth indication/MLE/STA-profile/TTLM lengths, extract MLE common fields, derive EMLSR delays/timeouts, and iterate MLE subelements.

## Control Flow
Management-frame parsers first validate element size (`ieee80211_eht_capa_size_ok`, `ieee80211_eht_oper_size_ok`, `ieee80211_mle_size_ok`, `ieee80211_mle_type_ok`) and then consume optional fields based on presence bits. Accessor helpers advance through optional common-info fields in spec order and return defaults when a field is absent.

## State And Persistence
No mutable state is stored. The header describes on-wire state from association, beacon, probe, action, and multi-link frames. Parsed capabilities persist in higher-level station/BSS data structures outside this file.

## Dependencies And Integration Points
Depends on Linux types, Ethernet length, bitfield helpers, unaligned little-endian access, element iteration, and HE definitions for EHT capability sizing. It integrates with Wi-Fi 7/EHT negotiation, MLO link management, station profiles, action frame handling, and rate/control capability selection.

## Risks
Most risk is parser correctness: optional fields are variable length and many accessors assume prior validation. Missing `from_ap` handling changes MCS/NSS length. Multi-link common fields require exact offset progression; malformed presence bits can otherwise cause out-of-bounds reads. Draft/standard evolution also risks bit drift.

## Test Signals
Fuzz EHT elements and MLE subelements, validate boundary lengths for PPE/MCS/NSS/disabled-subchannel fields, test AP vs non-AP capabilities, multi-link profiles with every presence-bit combination, TTLM map sizes, EMLSR delay encodings, and interop association with EHT APs.
