# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dp_tx.c

## Purpose

`dp_tx.c` implements ath11k transmit datapath submission, transmit completion handling, REO command submission, and host-to-target HTT control messages. It turns mac80211 skbs into TCL data descriptors, tracks in-flight buffers by software ids, parses WBM/HTT completion descriptors, returns tx status to mac80211, updates peer rate/statistics state, and configures RX/monitor rings in firmware.

## Important APIs, Types, and Functions

- `ath11k_dp_tx()` is the main TX enqueue path. It chooses a TCL ring, allocates an MSDU id in the ring `idr`, fills `hal_tx_info`, maps the skb for DMA, writes a TCL descriptor, starts the shadow timer, and increments pending TX count.
- `ath11k_dp_tx_get_encrypt_type()` maps mac80211 cipher suites to HAL encrypt types for raw mode TX.
- `ath11k_dp_tx_completion_handler()` drains the WBM/TCL completion ring, stages status descriptors in `tx_ring->tx_status`, parses each completion, removes the skb from the IDR, decrements pending TX count, and calls the appropriate completion routine.
- `ath11k_dp_tx_complete_msdu()` completes normal TQM-origin completions to mac80211 with ack signal, rate status, and cached per-peer stats.
- `ath11k_dp_tx_process_htt_tx_complete()` and `ath11k_dp_tx_htt_tx_complete_buf()` handle FW-origin HTT WBM completions.
- `ath11k_dp_tx_update_txcompl()` converts HAL tx-rate status into mac80211 `rate_info` for legacy/HT/VHT/HE and updates extended debugfs stats.
- `ath11k_dp_tx_send_reo_cmd()` writes REO commands and optionally records callbacks in `dp->reo_cmd_list` for RX-side status processing.
- `ath11k_dp_tx_htt_srng_setup()` sends HTT SRNG setup messages describing ring base addresses, entry sizes, HP/TP addresses, MSI data, and thresholds.
- `ath11k_dp_tx_htt_h2t_ver_req_msg()`, `ath11k_dp_tx_htt_h2t_ppdu_stats_req()`, `ath11k_dp_tx_htt_h2t_ext_stats_req()`, `ath11k_dp_tx_htt_rx_filter_setup()`, `ath11k_dp_tx_htt_monitor_mode_ring_config()`, and `ath11k_dp_tx_htt_rx_full_mon_setup()` build and send HTT control commands.

## Control Flow

Transmit submission starts in `ath11k_dp_tx()`. The function rejects crash-flush and unsupported non-data frames, derives a queue/pool id and hardware ring selector, and may retry alternate TCL rings when IDR allocation or descriptor availability fails and `tcl_ring_retry` is enabled. The skb is registered in `tx_ring->txbuf_idr` before DMA mapping so the hardware software cookie can identify it later. The descriptor id encodes pdev/mac id, MSDU id, and pool id. Encap mode is selected from raw-mode device flags and mac80211 HW 802.11 encapsulation flags; native-wifi TX strips QoS control before descriptor submission, while raw TX validates raw mode and appends CCMP MIC room when needed.

After DMA mapping, `ath11k_dp_tx()` locks the selected TCL SRNG, begins ring access, obtains a source entry, writes the HAL TCL command descriptor, ends ring access, starts the shadow timer, unlocks, and returns success. Failure paths unmap DMA and remove the IDR entry, retrying another ring only for the explicit descriptor-full retry case.

Completion flow starts in `ath11k_dp_tx_completion_handler()`. It drains hardware descriptors into a software circular `tx_status` buffer while holding the status SRNG lock, then processes that FIFO outside the SRNG lock. `ath11k_dp_tx_status_parse()` distinguishes FW-origin completions from TQM completions. FW completions are parsed as HTT status and may produce mac80211 status with ack RSSI or simply free the skb for reinject/inspect statuses. TQM completions remove the skb from the IDR, update pending counts, unmap DMA, fill ack/noack/rate status, resolve the peer under `base_lock`, and call `ieee80211_tx_status_ext()`.

HTT control command flow allocates an HTC skb, writes the command-specific structure with `FIELD_PREP()` encodings, sends it through `ath11k_htc_send()`, and frees the skb on send failure. Version request waits on `dp->htt_tgt_version_received`, which is completed by the RX HTT handler.

## State and Persistence Behavior

TX state is volatile. In-flight skbs are tracked per TX ring in `txbuf_idr` protected by `tx_idr_lock`. `ATH11K_SKB_CB` stores the DMA physical address, vif, and `ar` pointer needed at completion. `ar->dp.num_tx_pending` and `ar->dp.tx_empty_waitq` track drain state. Per-peer tx stats are cached in `ar->cached_stats`, `ar->last_ppdu_id`, and `ar->cached_ppdu_id` before being folded into debugfs/mac80211 state.

REO command state is shared with RX: `ath11k_dp_tx_send_reo_cmd()` allocates `dp_reo_cmd` entries in `dp->reo_cmd_list`, and `dp_rx.c` consumes them when REO status descriptors arrive. HTT target version fields live in `dp->htt_tgt_ver_major/minor` and a completion object.

## Dependencies and Integration Points

This file depends on mac80211 TX metadata and status APIs, Linux DMA mapping and IDR APIs, HAL TCL/WBM/SRNG helpers, peer lookup, debugfs station stats, hardware parameter hooks, HTC for firmware messaging, and RX-side REO/monitor configuration consumers. It is tightly coupled to `hal.c` for SRNG access and to `dp_rx.c` for REO command status and HTT version responses.

## Risks and Edge Cases

- TX buffer lifetime depends on exactly one IDR removal and DMA unmap per submitted skb. Unknown completion ids are warned and skipped, but leaks or double completions are high-risk.
- Ring retry logic must preserve the correct `tx_ring` and `ti.ring_id` after failures; otherwise descriptors or IDR entries can be associated with the wrong ring.
- Completion FIFO overflow currently logs and drops processing of some status descriptors, marked by a TODO.
- Peer lookup can fail at completion time if peers were removed; the code frees the skb without status-to-sta in that case.
- HTT SRNG setup must encode correct pdev ids, HP/TP addresses, flags, and entry sizes for each ring type; firmware misconfiguration can stall RX/TX rings.
- Raw/native/Ethernet encapsulation handling is deliberately limited; unsupported 802.3 encap returns `-EINVAL`.

## Test Signals

Exercise TX in native-wifi, Ethernet HW encap, and raw modes; verify DMA mapping failures and full ring retry paths; run association teardown under traffic to catch peer lookup races; inspect mac80211 ack/noack status and ack signal; validate extended TX stats for legacy/HT/VHT/HE; test HTT version negotiation timeout/version mismatch; and confirm monitor/RX ring HTT setup commands succeed during pdev allocation and monitor toggles.
