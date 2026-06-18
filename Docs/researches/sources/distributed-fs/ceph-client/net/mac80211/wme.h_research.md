# sources/distributed-fs/ceph-client/net/mac80211/wme.h

## Purpose
`wme.h` declares mac80211's internal WME queue-selection and QoS-header helpers.

## Important APIs, Types, And Functions
It declares `ieee80211_select_queue_80211()`, `ieee80211_select_queue()`, and `ieee80211_set_qos_hdr()`. The declarations expose dependencies on `struct ieee80211_sub_if_data`, `struct sta_info`, `struct sk_buff`, and `struct ieee80211_hdr`.

## Control Flow
The header contains no executable flow. Its functions are implemented in `wme.c` and called by TX path code after packet classification/frame construction and before final transmission/encryption stages.

## State And Persistence
No state is defined here. The declared helpers mutate skb priority, QoS control bytes, and TX flags at runtime.

## Dependencies And Integration Points
The header includes `ieee80211_i.h` and netdevice definitions, tying it to mac80211 internal TX state. It is included by `util.c` and TX path files that need queue/QoS decisions.

## Risks And Edge Cases
The header-level risk is API misuse: callers must pass an skb containing the expected frame format for either Ethernet-style classification or already formed 802.11 classification.

## Test Signals
Compilation and TX path tests using queue selection are the main signals.
