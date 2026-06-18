# sources/distributed-fs/ceph-client/include/linux/ieee80211-ht.h

## Purpose
Defines IEEE 802.11n HT frame structures, capability/operation bit masks, MCS layout, aggregation parameters, spatial multiplexing power-save values, and HT/BACK action codes.

## Important APIs, Types, And Functions
Key structures are `ieee80211_bar`, `ieee80211_mcs_info`, `ieee80211_ht_cap`, and `ieee80211_ht_operation`. Macros describe MPDU sizes, HT control length, BAR control fields, MCS masks and stream calculation, capability bits, extended capability bits, A-MPDU parameters, operation-mode fields, block-ack parameters, and max A-MPDU buffer sizes for HT/HE/EHT.

## Control Flow
This is mostly declarative. Management-frame and action-frame parsers cast validated bytes to packed structures, inspect capability/operation masks, and use action-code enums to dispatch HT and block-ack actions. `IEEE80211_HT_MCS_CHAINS()` derives chain count from an MCS index.

## State And Persistence
No mutable state is stored. HT capability, MCS, operation, and block-ack negotiation results are cached by wireless stack station/session state outside the header.

## Dependencies And Integration Points
Depends on Linux types and Ethernet address size. Integrates with mac80211/cfg80211 HT association, rate control, aggregation setup/teardown, block-ack handling, channel-width negotiation, and later HE/EHT code that references HT aggregation and SMPS constants.

## Risks
Endian conversion is required for packed little-endian fields. Incorrect MCS or A-MPDU interpretation affects rate selection and aggregation limits. Block-ack masks are protocol-sensitive; wrong shifts can corrupt TID or buffer-size negotiation.

## Test Signals
HT capability parsing, MCS mask/rate derivation, 20/40 MHz operation handling, SMPS mode handling, ADDBA/DELBA frame parsing, A-MPDU limit enforcement, and interop with 802.11n APs and clients.
