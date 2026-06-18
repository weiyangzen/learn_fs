# sources/distributed-fs/ceph-client/net/mac80211/wme.c

## Purpose
`wme.c` maps packets and existing 802.11 frames to WMM/802.11e access categories, downgrades traffic when admission control or reserved TIDs require it, and writes QoS control fields before transmission.

## Important APIs, Types, And Functions
The exported internal table is `ieee802_1d_to_ac[8]`. Public functions are `ieee80211_select_queue_80211()`, `ieee80211_select_queue()`, and `ieee80211_set_qos_hdr()`. Internal helpers include `wme_downgrade_ac()`, `ieee80211_fix_reserved_tid()`, and `ieee80211_downgrade_queue()`. Important state includes `skb->priority`, station WME capability, `sdata->wmm_acm`, managed-mode TSPEC admission state, `sta->reserved_tid`, `sdata->qos_map`, `sdata->noack_map`, and mesh QoS bits.

## Control Flow
For already formed 802.11 frames, `ieee80211_select_queue_80211()` sets a hash, sends non-reorderable or single-queue hardware to queue 0, maps non-data to VO, non-QoS data to BE, extracts TID from QoS control for QoS data, and then runs downgrade logic.

For Ethernet-style payloads, `ieee80211_select_queue()` determines whether QoS applies from mesh/OCB requirements or station WME support. Non-QoS frames force BE priority for WPA/11i MIC correctness. Control-port frames use priority 7. Other frames use `cfg80211_classify8021d()` with an optional QoS map and then admission/reserved-TID downgrade.

`ieee80211_set_qos_hdr()` updates the QoS control field unless the frame was injected. It preserves unrelated QoS bits, writes TID and no-ack policy, sets `IEEE80211_TX_CTL_NO_ACK` for multicast or configured no-ack TIDs, and handles mesh control-present bits.

## State And Persistence
The file mutates only per-packet state (`skb->priority`, QoS control bytes, TX info flags). Persistent policy comes from runtime interface and station fields configured elsewhere.

## Dependencies And Integration Points
It depends on netdevice/skbuff, packet classifier helpers, cfg80211 QoS mapping, mac80211 station/interface state, mesh helpers, and TX handler code that calls queue selection and QoS header setup before encryption and driver transmission.

## Risks And Edge Cases
Admission-control downgrade loops can end at BK when an AP marks all lower ACs as requiring admission, an intentional workaround. Reserved TID remapping is local and must stay aligned with aggregation/session reservation logic. Injected frames preserve existing QoS bytes but still honor no-ack policy, so packet injection tests need to account for changed TX flags. Incorrect priority handling can break TKIP/WPA MIC calculation or reorder-sensitive traffic.

## Test Signals
Useful tests cover 802.1D-to-AC mapping, DSCP/QoS-map classification, control-port priority, WMM ACM downgrade with and without TSPEC admission, reserved TID remapping, mesh QoS byte preservation, injected no-ack handling, and single-queue hardware behavior.
