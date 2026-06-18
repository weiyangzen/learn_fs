# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_rx.h

## Purpose

`dp_rx.h` declares ath12k RX datapath data structures and helper APIs. It defines RX reorder queue state, REO command state, fragment state, decap types, small inline HAL descriptor wrappers, and externally used RX setup/delivery functions.

## Important APIs, Types, and Functions

Core data structures include `ath12k_reoq_buf`, `ath12k_dp_rx_tid`, `ath12k_dp_rx_tid_rxq`, `ath12k_dp_rx_reo_cache_flush_elem`, `dp_reo_update_rx_queue_elem`, and `ath12k_dp_rx_reo_cmd`. These represent DMA-backed REO queue buffers, per-TID reorder/fragment state, inactive-update elements, delayed cache-flush elements, and REO commands with completion handlers.

Constants include `DP_MAX_NWIFI_HDR_LEN`, `ATH12K_DP_RX_FRAGMENT_TIMEOUT_MS`, `ATH12K_DP_RX_REO_DESC_FREE_THRES`, and `ATH12K_DP_RX_REO_DESC_FREE_TIMEOUT_MS`.

Inline helpers translate HE GI values, inspect 802.11 fragment fields after HAL descriptor offset, fetch L3 padding, copy descriptor end TLVs, set/get RX descriptor fields through `hal->ops`, clean skb lists, and extract descriptor data.

Declared APIs cover undecap/delivery, native Wi-Fi header validation, PN extraction and fragment sorting, AMPDU start/stop, PN replay configuration, TID setup/cleanup/delete, REO setup/cleanup, RX allocation/free, RX buffer replenish, monitor attach, peer fragment setup, PPDU status filling, crypto MIC length, and REO command callbacks.

## Control Flow and Integration

RX processing code includes this header to operate on per-peer TID state and to call HAL descriptor ops without knowing hardware-specific descriptor layouts. `dp_peer.h` includes this file because `ath12k_dp_peer` embeds `ath12k_dp_rx_tid` and `ath12k_reoq_buf`.

Typical runtime flow is: allocate RX rings, replenish buffers, parse completion descriptors into `hal_rx_desc_data`, undecap if required, fill PPDU/rate status, deliver to mac80211, and manage TID reorder state through AMPDU callbacks and REO command completions.

## State and Persistence Behavior

The structures declared here persist in peer objects and datapath command lists. They hold DMA addresses, fragment queues, timers, active flags, and command handlers. The inline helpers are thin wrappers over mutable HAL descriptor state and skb contents.

## Dependencies and Integration Points

The header includes `core.h` and `debug.h` and depends on HAL descriptor abstractions, Linux skb/timer/mac80211 types, REO command statuses, encryption types, and ath12k datapath/core structures.

## Risks and Contract Notes

- Several inline helpers assume `skb->data + hal_desc_sz` points to a valid 802.11 header; callers must only use them after descriptor/body layout validation.
- `ath12k_dp_clean_up_skb_list()` consumes the entire skb queue without locking; caller owns queue serialization.
- REO command handler callbacks carry `void *ctx`, so type discipline is by convention.
- Declarations expose many setup and teardown entry points that require `dp_lock` or wiphy lock in implementation; callers must follow surrounding mac80211/datapath sequencing.

## Test Signals

Compile coverage for all RX users, static checking of inline descriptor access, AMPDU/fragment tests for all TIDs, and build coverage across hardware descriptor ops variants are the main header-level signals.
