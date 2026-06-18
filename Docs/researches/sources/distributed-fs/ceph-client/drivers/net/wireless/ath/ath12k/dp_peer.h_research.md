# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_peer.h

## Purpose

`dp_peer.h` defines datapath peer state and peer lookup/lifecycle contracts for ath12k. It bridges RX/TX datapath code, monitor statistics, mac80211 station objects, firmware peer map events, and MLO link-peer mapping.

## Important APIs, Types, and Functions

`ATH12K_DP_PEER_ID_INVALID` and `ATH12K_PEER_ML_ID_VALID` define peer ID sentinel and ML peer ID tagging.

`struct ppdu_user_delayba`, `ath12k_rx_peer_rate_stats`, `ath12k_rx_peer_stats`, `ath12k_wbm_tx_stats`, and `ath12k_dp_peer_stats` hold per-peer PPDU, RX, rate, and WBM TX completion statistics.

`struct ath12k_dp_link_peer` represents a firmware/device link peer. It stores vdev ID, MAC, peer IDs, AST hash, pdev/hw link IDs, MLO fields, primary-link flag, station pointer, rhashtable node, TID activity bitmask, rate/RSSI/duration fields, and optional per-peer stats.

`struct ath12k_dp_peer` represents the host peer across one or more links. It stores MLO status, security/key state, host station pointer, hardware link-to-link ID map, RCU link-peer pointers, per-TID reorder state, and REO queue buffers.

The header declares link-peer map/unmap event handlers, lookup helpers by vdev/address/AST/pdev/peer ID, rhashtable lifecycle, host peer create/delete, peer ID indexing, link-peer conversion to `ath12k_link_sta`, and link-peer free.

## Control Flow and Integration

Firmware map events create `ath12k_dp_link_peer` objects; mac80211/peer setup creates `ath12k_dp_peer` objects; assignment binds the two and publishes RCU lookups. RX hot paths use peer ID or address helpers to find peer state. Aggregation and fragmentation setup use the per-peer `rx_tid[]` and `reoq_bufs[]` arrays declared here.

## State and Persistence Behavior

The structures declared here persist for peer lifetime and are mutated by firmware events, station lifecycle code, RX reorder setup, key configuration, monitor statistics, and TX completion statistics. The `link_peers[]` table is RCU-protected; the list/rhashtable fields are protected by datapath locks in implementation.

## Dependencies and Integration Points

This header includes `dp_rx.h`, so it depends on RX TID and REO buffer definitions. It also references mac80211 station/key/rate types, HAL encryption and RX stat constants, WMI key index limits, and ath12k MLO constants.

## Risks and Contract Notes

- Hot-path lookup helpers have lock requirements not visible from type signatures; callers must follow implementation lockdep warnings.
- The header exposes both host peer and link peer objects. Mixing them up can break MLO mapping, because host peer IDs and link peer IDs have different index semantics.
- Statistics pointers are optional; update code must tolerate `NULL`.
- `primary_link` controls whether RX reorder/fragment operations run for a peer, so MLO setup must initialize it consistently.

## Test Signals

Compile coverage under MLO and non-MLO configurations, station association/teardown tests, peer stats debugfs tests, RX aggregation start/stop, and static analysis for lookup calls outside required lock/RCU sections are useful header-level signals.
