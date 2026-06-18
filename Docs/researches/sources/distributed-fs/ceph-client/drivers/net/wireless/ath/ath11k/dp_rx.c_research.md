# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dp_rx.c

## Purpose

`dp_rx.c` is the ath11k datapath receive implementation. It bridges hardware/FW receive rings to mac80211, owns RXDMA buffer refill and reclaim, builds and tears down REO reorder queues, handles HTT target-to-host events, processes normal REO destination traffic, recovers selected RX error paths, performs fragment defragmentation/reinjection, and delivers monitor-mode/radiotap traffic. The file is central to runtime packet ingress and also carries some transmit-statistics parsing because HTT PPDU stats are received through the RX/HTT event path.

## Important APIs, Types, and Functions

- RX descriptor access helpers at the top of the file abstract chip-specific `ab->hw_params.hw_ops` callbacks for fields such as encrypt type, decap type, MSDU length, PPDU id, rate, bandwidth, peer id, sequence number, checksum status, and attention errors. This makes the rest of RX code work across hardware descriptor variants.
- `ath11k_dp_rxbufs_replenish()` allocates aligned skb buffers, maps them for DMA, records them in a per-ring `idr`, writes RXDMA refill descriptors, and returns the actual number posted. It is the common normal-data refill path.
- `ath11k_dp_rx_pdev_alloc()` and `ath11k_dp_rx_pdev_free()` set up/free per-radio RX rings and buffers, then configure those rings in firmware with HTT SRNG setup commands from `dp_tx.c`.
- `ath11k_dp_pdev_reo_setup()` / `ath11k_dp_pdev_reo_cleanup()` allocate the REO destination rings shared by normal RX processing.
- `ath11k_peer_rx_tid_setup()`, `ath11k_peer_rx_tid_delete()`, `ath11k_dp_rx_ampdu_start()`, and `ath11k_dp_rx_ampdu_stop()` own per-peer/TID REO queue descriptor allocation, WMI reorder queue setup, and REO command update/delete flows.
- `ath11k_dp_process_rx()` drains a REO destination ring, converts hardware cookies back to skb buffers through the RX refill `idr`, unmaps DMA, batches skbs by radio, and refills consumed RX buffers.
- `ath11k_dp_rx_process_msdu()` validates descriptors, coalesces multi-buffer MSDUs, fills PPDU/rate and MPDU crypto/status metadata, and prepares the skb for delivery.
- `ath11k_dp_rx_deliver_msdu()` copies the populated `ieee80211_rx_status`, sets fast-rx `RX_FLAG_8023` when safe, and calls `ieee80211_rx_napi()`.
- `ath11k_dp_process_rx_err()`, `ath11k_dp_rx_process_wbm_err()`, and `ath11k_dp_process_rxdma_err()` handle REO exception, WBM release error, and RXDMA error destination rings.
- `ath11k_dp_rx_frag_h_mpdu()` and its helpers accumulate raw MPDU fragments per peer/TID, validate fragment order and PN progression, perform TKIP MIC verification where needed, and reinject a defragmented skb into REO.
- `ath11k_dp_htt_htc_t2h_msg_handler()` dispatches HTT events such as version confirmation, peer map/unmap, PPDU stats, extended stats, pktlog, and backpressure.
- `ath11k_dp_htt_tlv_iter()` is a generic HTT TLV parser used by PPDU stats parsing.
- Monitor-mode APIs include `ath11k_dp_rx_mon_status_bufs_replenish()`, `ath11k_dp_rx_process_mon_status()`, `ath11k_dp_rx_process_mon_rings()`, `ath11k_dp_rx_pdev_mon_attach()`, `ath11k_dp_rx_pdev_mon_detach()`, `ath11k_dp_rx_pktlog_start()`, and `ath11k_dp_rx_pktlog_stop()`.
- Crypto-size helpers `ath11k_dp_rx_crypto_mic_len()`, `ath11k_dp_rx_crypto_param_len()`, and `ath11k_dp_rx_crypto_icv_len()` translate HAL encrypt types into 802.11 header/trailer lengths.

## Control Flow

Normal RX starts with buffers posted by `ath11k_dp_rxbufs_replenish()` onto RXDMA refill rings. Hardware/FW fills those buffers and emits REO destination descriptors. `ath11k_dp_process_rx()` locks the selected REO destination SRNG, drains descriptors until the budget is reached or the ring is empty, decodes the software cookie into `mac_id` and `buf_id`, removes the skb from the refill ring `idr`, unmaps it, stores descriptor-derived flags in `ATH11K_SKB_RXCB`, and queues the skb on a per-radio temporary list. It has a retry path for incomplete continuation chains when hardware advanced the head pointer after the cached value was read.

After ring draining, `ath11k_dp_rx_process_received_packets()` checks that the radio is still active and not in CAC, then processes each skb through `ath11k_dp_rx_process_msdu()`. Single-buffer MSDUs are trimmed/pulled past HAL descriptors and L3 padding. Continuation buffers are coalesced by `ath11k_dp_rx_msdu_coalesce()`, which copies the end TLVs from the last buffer into the first and appends payload data from continuation skbs. The code then populates PPDU metadata with `ath11k_dp_rx_h_ppdu()` and rate fields with `ath11k_dp_rx_h_rate()`, evaluates MPDU crypto/error state with `ath11k_dp_rx_h_mpdu()`, performs undecapsulation for native-wifi/raw/Ethernet decap modes, and marks monitor-skip/duplicate-validation flags. Delivery finally goes through `ath11k_dp_rx_deliver_msdu()`.

REO reorder setup is driven by mac80211 AMPDU callbacks. `ath11k_dp_rx_ampdu_start()` calls `ath11k_peer_rx_tid_setup()` to allocate an aligned noncoherent REO queue descriptor, initialize it with `ath11k_hal_reo_qdesc_setup()`, sync it for device access, and notify firmware via `ath11k_wmi_peer_rx_reorder_queue_setup()`. Existing active queues are updated through `ath11k_peer_rx_tid_reo_update()`. Stop paths shrink the BA window and update WMI; peer cleanup sends REO update/delete commands and later flushes cached REO descriptors before freeing DMA memory.

HTT event flow enters via `ath11k_dp_htt_htc_t2h_msg_handler()`. Version confirmations complete `dp->htt_tgt_version_received`, peer-map events update the peer table, PPDU stats are parsed through `ath11k_htt_pull_ppdu_stats()` and `ath11k_dp_htt_tlv_iter()`, and backpressure events update `ab->soc_stats.bp_stats`. PPDU stats are accumulated by PPDU id in `ar->ppdu_stats_info` and flushed into per-peer tx-rate/debugfs stats when the list depth exceeds `HTT_PPDU_DESC_MAX_DEPTH` or matching entries are revisited.

Error flow is split by source. `ath11k_dp_process_rx_err()` consumes REO exception descriptors, parses link descriptors, drops multi-MSDU/non-fragment exceptions, and sends valid one-MSDU fragments to `ath11k_dp_rx_frag_h_mpdu()`. `ath11k_dp_rx_process_wbm_err()` consumes WBM release descriptors and can salvage null queue descriptor cases or TKIP MIC errors into mac80211 while dropping most other error codes. `ath11k_dp_process_rxdma_err()` mostly frees buffers described by RXDMA error entries and returns the link descriptor to the idle list.

Monitor-mode flow uses a separate status-buffer refill ring and, on rxdma1 hardware, monitor destination and descriptor rings. `ath11k_dp_rx_reap_mon_status_ring()` reclaims status buffers, handles missing DONE tags with a lookahead rule, queues completed status skbs, and immediately posts replacement buffers. `ath11k_dp_rx_process_mon_status()` parses monitor TLVs into `hal_rx_mon_ppdu_info`, updates peer RX stats, emits pktlog traces, and, in non-full-monitor mode, calls `ath11k_dp_rx_mon_dest_process()` when a PPDU is complete. Full-monitor mode coordinates destination entries and status buffers with `pmon->hold_mon_dst_ring`, `pmon->buf_state`, and a pending MPDU list before delivering the PPDU.

## State and Persistence Behavior

This file maintains volatile driver state only; there is no on-disk persistence. Runtime state lives in `ath11k_base`, `ath11k_dp`, `ath11k_pdev_dp`, `ath11k_mon_data`, `ath11k_peer`, and `dp_rx_tid` objects.

RX buffer ownership is tracked through `idr` tables in `dp_rxdma_ring`. A posted buffer is DMA-mapped and registered in `bufs_idr`; a completion removes the id, unmaps the DMA address stored in `ATH11K_SKB_RXCB`, and either delivers or frees the skb. REO queue descriptors are noncoherent DMA allocations referenced by `dp_rx_tid::{vaddr_unaligned,paddr_unaligned,vaddr,paddr,size,active}` and are freed asynchronously after REO command status/cache flushes.

Fragment state is per peer/TID: `cur_sn`, `last_frag_no`, `rx_frag_bitmap`, `rx_frags`, `dst_ring_desc`, and `frag_timer`. The timer purges incomplete sequences after `ATH11K_DP_RX_FRAGMENT_TIMEOUT_MS`. Monitor state is per pdev in `ath11k_mon_data`, including PPDU status, last link descriptor/cookie deduplication, status buffer matching state, full-monitor pending MPDU list, and monitor counters.

Synchronization is primarily SRNG spinlocks, `rx_ring->idr_lock`, `ab->base_lock` for peer tables and peer/TID state, `ar->data_lock` for PPDU stats list access, and `pmon->mon_lock` for monitor aggregation state. The code intentionally releases `base_lock` around `timer_delete_sync()` to avoid deadlocks.

## Dependencies and Integration Points

`dp_rx.c` depends on HAL descriptor/ring helpers (`hal_rx.h`, `hal_desc.h`, `hal_srng` APIs), TX-side REO/HTT command submission (`ath11k_dp_tx_send_reo_cmd()` and `ath11k_dp_tx_htt_srng_setup()`), WMI peer reorder commands, mac80211 RX/TX status APIs, Linux DMA mapping and skb APIs, peer lookup/map logic, debugfs statistics, tracepoints, and hardware-specific `hw_ops`.

It integrates with interrupt/NAPI polling through the exported RX processing functions, with mac80211 AMPDU/key setup through reorder and PN replay APIs, with firmware over HTT/HTC for control/status messages, with WBM/REO/RXDMA hardware rings through HAL SRNG operations, and with monitor/pktlog features through tracepoints and radiotap metadata.

## Risks and Edge Cases

- Buffer lifecycle correctness is critical. A missed `idr_remove()`, double unmap, or failure to replenish consumed buffers can stall RX or corrupt DMA ownership.
- Multi-buffer MSDU coalescing assumes descriptor length fields and continuation flags are coherent. Malformed lengths are checked, but error paths must ensure all continuation buffers are freed exactly once.
- Fragment handling has complex lock/timer interactions and stores a copied destination ring descriptor for later REO reinjection. Bugs here can leak link descriptors, free the wrong skb, or reinject malformed descriptors.
- PN replay and multicast crypto policy are split between hardware and mac80211. The code deliberately keeps multicast PN validation in mac80211 and reconstructs headers for EAPOL/MCBC cases; regressions can become security issues.
- Monitor-mode synchronization between status and destination rings has multiple lag/lead/stuck workarounds. Full-monitor delivery is sensitive to PPDU id wrap, status-buffer matching, and pending-list cleanup.
- REO command completion is asynchronous. If firmware does not return expected statuses, descriptor memory can remain on `reo_cmd_list` or cache-flush lists until cleanup.
- Several TODOs mark incomplete handling for 802.3 undecap, other REO/RXDMA errors, and some monitor ring corner cases.

## Test Signals

Useful validation signals include sustained RX throughput without refill starvation, absence of invalid `buf_id` and length warnings, stable RX during CAC transitions, AMPDU start/stop with reorder queue updates, PN replay behavior for pairwise keys, multicast/EAPOL delivery through slow paths, fragmented encrypted traffic including TKIP MIC failure reporting, WBM/REO/RXDMA error counter behavior, monitor-mode captures with valid radiotap HE/HE-MU metadata, pktlog start/stop purge completion, and lockdep/KASAN/KMSAN runs around peer teardown and monitor toggling.
