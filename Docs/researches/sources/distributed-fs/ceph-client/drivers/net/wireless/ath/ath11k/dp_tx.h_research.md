# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dp_tx.h

## Purpose

`dp_tx.h` is the public header for ath11k transmit datapath and HTT host-to-target commands. It exposes the TX completion status helper type and the TX, REO-command, HTT statistics, RX-filter, and monitor-mode configuration entry points implemented in `dp_tx.c`.

## Important APIs, Types, and Functions

- `struct ath11k_dp_htt_wbm_tx_status` is a compact internal representation of HTT WBM TX completion status: MSDU id, ack state, ack RSSI, and peer id.
- `ath11k_dp_tx()` is the exported skb submission path.
- `ath11k_dp_tx_completion_handler()` processes completion rings.
- `ath11k_dp_tx_update_txcompl()` updates station tx-rate/debug statistics from HAL TX status.
- `ath11k_dp_tx_send_reo_cmd()` submits REO commands and optional callbacks used heavily by RX reorder cleanup.
- `ath11k_dp_tx_htt_h2t_ver_req_msg()`, `ath11k_dp_tx_htt_h2t_ppdu_stats_req()`, and `ath11k_dp_tx_htt_h2t_ext_stats_req()` expose HTT control requests.
- `ath11k_dp_tx_htt_monitor_mode_ring_config()`, `ath11k_dp_tx_htt_rx_filter_setup()`, and `ath11k_dp_tx_htt_rx_full_mon_setup()` configure RX/monitor rings through firmware.

## Control Flow

The header itself has no executable flow. It defines the surface used by mac80211 TX paths, datapath interrupt handlers, RX pdev setup, monitor mode configuration, and REO queue management. RX code uses the REO command API even though it is declared in the TX header, reflecting that REO commands are transmitted to hardware/firmware through the datapath command rings.

## State and Persistence Behavior

No persistent state is declared here. The functions operate on runtime ath11k structures, skbs, HAL statuses, RX TID descriptors, and HTT configuration structures. All state remains in driver memory and hardware/FW rings.

## Dependencies and Integration Points

The header includes `core.h` and `hal_tx.h`, providing core ath11k object definitions and HAL TX status/descriptor types. It integrates with mac80211 transmit handling, HAL SRNG/TCL/WBM rings, firmware HTT messaging, RX reorder logic, debug/statistics requests, and monitor-mode setup.

## Risks and Edge Cases

- The header exposes cross-direction coupling: RX code depends on TX command submission for REO operations and ring configuration.
- Callers must pass ring ids and ring types that match firmware expectations; there is little type safety between `u32 ring_id` and `enum hal_ring_type`.
- The completion handler is ring-index based and assumes the selected `dp->tx_ring` state has been initialized consistently.

## Test Signals

Build coverage plus runtime TX submission/completion, REO command callbacks, HTT version negotiation, PPDU/ext stats requests, RX ring setup, and monitor-mode ring configuration are the key signals for this header.
