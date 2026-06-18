# subset-b-004731 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dp_rx.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dp_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dp_rx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dp_rx.h

## Purpose

`dp_rx.h` is the public header for ath11k receive datapath services. It exposes RX decapsulation constants, RX MPDU error bits, small wire-format helper structs, and the RX/REO/HTT/monitor function prototypes used by core datapath, MAC, peer, and interrupt code.

## Important APIs, Types, and Functions

- `DP_MAX_NWIFI_HDR_LEN` bounds the temporary native-wifi header buffer used while rebuilding 802.11 headers.
- `DP_RX_MPDU_ERR_*` bits define the internal normalized MPDU error map for FCS, decrypt, TKIP MIC, A-MSDU, overflow, MSDU length, MPDU length, and unencrypted-frame problems.
- `enum dp_rx_decap_type` mirrors hardware decapsulation modes: raw, native wifi, Ethernet II/DIX, and 802.3.
- `struct ath11k_dp_amsdu_subframe_hdr` and `struct ath11k_dp_rfc1042_hdr` describe packed on-wire headers used by undecapsulation logic in `dp_rx.c`.
- AMPDU/reorder APIs: `ath11k_dp_rx_ampdu_start()`, `ath11k_dp_rx_ampdu_stop()`, `ath11k_peer_rx_tid_setup()`, `ath11k_peer_rx_tid_delete()`, `ath11k_peer_rx_tid_cleanup()`, and `ath11k_peer_frags_flush()`.
- Key/security API: `ath11k_dp_peer_rx_pn_replay_config()` updates REO PN replay behavior for pairwise keys.
- HTT and REO APIs: `ath11k_dp_htt_htc_t2h_msg_handler()`, `ath11k_dp_htt_tlv_iter()`, `ath11k_dp_pdev_reo_setup()`, `ath11k_dp_pdev_reo_cleanup()`, `ath11k_dp_reo_cmd_list_cleanup()`, and `ath11k_dp_process_reo_status()`.
- Ring processing APIs: normal RX, REO error, WBM error, RXDMA error, monitor status, and monitor rings are exported for NAPI/IRQ handlers.
- Allocation/lifecycle APIs: `ath11k_dp_rx_pdev_alloc()`, `ath11k_dp_rx_pdev_free()`, monitor attach/detach, pktlog start/stop, and buffer replenish helpers.

## Control Flow

This header does not implement control flow, but it defines the receive datapath surface used by the rest of the driver. Setup code calls pdev REO/RX allocation and monitor attach functions. Runtime NAPI code calls the process functions for normal REO destination rings, REO exceptions, WBM release errors, RXDMA errors, and monitor rings. MAC/peer code calls AMPDU, PN replay, and fragment setup/cleanup functions as stations and keys change. Firmware HTT messages enter through `ath11k_dp_htt_htc_t2h_msg_handler()`.

## State and Persistence Behavior

No state is stored in the header. The prototypes operate on runtime objects such as `ath11k_base`, `ath11k`, `ath11k_vif`, `ath11k_peer`, `dp_rxdma_ring`, `dp_rx_tid`, `sk_buff`, and `napi_struct`. All state is volatile driver memory maintained by implementation files.

## Dependencies and Integration Points

The header includes `core.h`, `rx_desc.h`, and `debug.h`, so users see core ath11k object definitions, RX descriptor definitions, and debug helpers. It depends on mac80211 types for AMPDU/key arguments and Linux networking types for skbs/NAPI through included headers. Its prototypes are consumed by datapath initialization, MAC callbacks, peer lifecycle code, interrupt/NAPI polling, HTT receive dispatch, and monitor/pktlog control paths.

## Risks and Edge Cases

- The decap enum and MPDU error bit definitions must stay aligned with `dp_rx.c` and hardware/HAL interpretation; mismatches would corrupt header reconstruction or error reporting.
- Exported buffer-replenish/process APIs assume callers pass the correct ring and mac id. Mixing pdev ids, LMAC ids, or ring types can break DMA ownership.
- The header exposes broad cross-module coupling between RX and TX because REO commands are submitted through TX code while RX owns reorder state.

## Test Signals

Compile coverage is the primary signal for this header. Runtime validation should exercise all declared entry points through RX pdev setup/free, AMPDU start/stop, key install/remove PN replay updates, normal/error RX NAPI polling, monitor start/stop, and pktlog start/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dp_rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dp_tx.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dp_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dp_tx.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dp_tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/fw.c

## Purpose

`fw.c` handles ath11k firmware container pre-initialization for the API 2 firmware format. It requests `firmware-2.bin`, validates the ath11k firmware magic, parses aligned information elements, records embedded AMSS and M3 image spans, captures advertised feature bits, and falls back to API 1 behavior when API 2 firmware is unavailable.

## Important APIs, Types, and Functions

- `ath11k_fw_request_firmware_api_n()` is the parser/loader for named API-N firmware files. In this file it is used for `ATH11K_FW_API2_FILE`.
- `ath11k_fw_pre_init()` attempts to load API 2 firmware, sets `ab->fw.api_version` to 2 on success, and otherwise sets it to 1 while returning success to let older firmware flows continue.
- `ath11k_fw_destroy()` releases `ab->fw.fw` and is exported.
- Parsed IE ids come from `enum ath11k_fw_ie_type`: timestamp, feature bitmap, AMSS image, and M3 image.

## Control Flow

`ath11k_fw_pre_init()` calls `ath11k_fw_request_firmware_api_n(ab, "firmware-2.bin")`. The helper requests firmware through `ath11k_core_firmware_request()`, stores the `struct firmware` in `ab->fw.fw`, and validates that the file starts with `ATH11K_FIRMWARE_MAGIC` including its terminating null byte. The parser aligns past the magic to a 4-byte boundary and then iterates `struct ath11k_fw_ie` records while enough bytes remain.

For each IE, the parser converts little-endian `id` and `len`, ensures the payload fits inside the remaining file, and dispatches by IE type. Timestamp IEs are logged when exactly 4 bytes. Feature IEs set bits in `ab->fw.fw_features` up to `ATH11K_FW_FEATURE_COUNT`. AMSS and M3 IEs set `ab->fw.amss_data/amss_len` and `ab->fw.m3_data/m3_len` to point directly into the firmware blob. Unknown IEs are warned but skipped. Payload length is aligned to 4 bytes before moving to the next IE.

If validation fails, the helper releases the firmware and clears `ab->fw.fw`. If API 2 loading fails, `ath11k_fw_pre_init()` deliberately records API version 1 and returns 0.

## State and Persistence Behavior

Firmware state is stored in `ab->fw`. The firmware blob remains owned by the kernel firmware loader until `ath11k_fw_destroy()` releases it. AMSS and M3 image pointers are not copied; they reference slices inside `ab->fw.fw->data`, so they are valid only while the firmware object is held. Feature bits are set in `ab->fw.fw_features`. There is no on-disk persistence.

## Dependencies and Integration Points

The file depends on `ath11k_core_firmware_request()`, Linux firmware release APIs, endian helpers, bitmap helpers, debug logging, and `struct ath11k_fw_ie` from core firmware definitions. It integrates with boot/pre-init code that needs firmware API version, feature flags, and image payload pointers before hardware start.

## Risks and Edge Cases

- API 2 parser returns success even if mandatory AMSS/M3 images are absent; later boot stages must validate required image pointers/lengths.
- AMSS/M3 pointers alias the firmware blob. Releasing `ab->fw.fw` too early invalidates them.
- The IE loop stops silently if aligned IE length exceeds remaining bytes after the earlier payload-fit check; this avoids overrun but can leave trailing malformed padding unreported.
- `ATH11K_FW_FEATURE_COUNT` is currently only a sentinel with no feature values in this snapshot, so feature parsing is structurally present but has no meaningful feature bits to set.
- Any parser change must preserve little-endian interpretation and 4-byte alignment.

## Test Signals

Test with missing `firmware-2.bin` to verify API 1 fallback, invalid magic and too-small files for `-EINVAL` cleanup, malformed IE lengths, unknown IE ids, valid timestamp/features/image IEs, and module/device teardown to ensure `ath11k_fw_destroy()` releases the firmware without dangling later access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/fw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/fw.h

## Purpose

`fw.h` defines the ath11k firmware API 2 filename, firmware magic string, firmware IE identifiers, firmware feature enum, and the pre-init/destroy entry points implemented by `fw.c`.

## Important APIs, Types, and Functions

- `ATH11K_FW_API2_FILE` is `"firmware-2.bin"`.
- `ATH11K_FIRMWARE_MAGIC` is the magic string expected at the start of API 2 containers.
- `enum ath11k_fw_ie_type` defines IE ids for timestamp, features, AMSS image, and M3 image.
- `enum ath11k_fw_features` currently contains only the `ATH11K_FW_FEATURE_COUNT` sentinel.
- `ath11k_fw_pre_init()` and `ath11k_fw_destroy()` are the exported firmware lifecycle hooks.

## Control Flow

There is no executable control flow in this header. Boot code calls `ath11k_fw_pre_init()` to parse or fall back from API 2 firmware and calls `ath11k_fw_destroy()` during cleanup.

## State and Persistence Behavior

The header declares constants and prototypes only. Runtime firmware state lives in `ab->fw` and is managed by `fw.c`.

## Dependencies and Integration Points

`fw.h` is included by ath11k boot/core code that needs firmware API constants and lifecycle APIs. The IE definitions must match the binary container format consumed by `fw.c` and produced by firmware packaging.

## Risks and Edge Cases

- Changing IE ids, filename, or magic string breaks compatibility with packaged firmware.
- Adding feature enum values requires corresponding parser/users and enough bitmap storage in `ab->fw.fw_features`.
- The header does not define the actual IE record struct; parser code depends on the core definition remaining compatible with these ids.

## Test Signals

Compile coverage for firmware lifecycle users and boot tests with API 2 and API 1 firmware layouts are the key signals. New feature enum values should be accompanied by parser and behavior tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal.c

## Purpose

`hal.c` implements ath11k hardware abstraction for SRNG ring configuration, ring pointer access, CE descriptor helpers, WBM idle link setup, shadow register configuration, and SRNG lifecycle diagnostics. It is the low-level layer that maps datapath ring types to hardware ring ids/registers and provides safe producer/consumer operations for source and destination rings.

## Important APIs, Types, and Functions

- `hw_srng_config_template[]` describes all supported ring classes: REO destination/exception/reinject/cmd/status, TCL data/cmd/status, CE source/destination/status, WBM idle/release, RXDMA buffer/destination/monitor rings, and direct RXDMA buffer rings. Each entry defines start ring id, maximum ring count, descriptor entry size in dwords, LMAC ownership, direction, and max register size.
- `ath11k_hal_srng_init()` allocates per-ring configuration, coherent read/write pointer memory (`rdp` and `wrp`), and lockdep classes.
- `ath11k_hal_srng_deinit()` unregisters lock classes, frees coherent pointer memory, and frees copied SRNG config.
- `ath11k_hal_srng_setup()` initializes one `hal_srng`, maps ring type/number/mac id to a ring id, assigns ring memory, pointer addresses, flags, thresholds, and hardware registers, then programs hardware for non-LMAC rings.
- `ath11k_hal_srng_access_begin()` and `ath11k_hal_srng_access_end()` synchronize cached HP/TP state with hardware/FW-visible pointers and enforce DMA barriers.
- Ring entry APIs include `ath11k_hal_srng_src_get_next_entry()`, `ath11k_hal_srng_dst_get_next_entry()`, `ath11k_hal_srng_src_num_free()`, `ath11k_hal_srng_dst_num_free()`, source reap helpers, and peek helpers.
- CE helpers `ath11k_hal_ce_src_set_desc()`, `ath11k_hal_ce_dst_set_desc()`, `ath11k_hal_ce_dst_status_get_length()`, and `ath11k_hal_ce_get_desc_size()` encode/copy CE descriptors.
- `ath11k_hal_set_link_desc_addr()` writes link descriptor address/cookie fields.
- `ath11k_hal_setup_link_idle_list()` programs the WBM idle link scatter list and ring pointers.
- Shadow register APIs configure and expose shadow HP/TP registers when supported.
- `ath11k_hal_dump_srng_stats()` emits CE, IRQ group, and per-SRNG pointer/timestamp diagnostics.

## Control Flow

Initialization starts with `ath11k_hal_srng_init()`, which clears the HAL object, copies the static ring template, fills hardware-specific register base/stride values in `ath11k_hal_srng_create_config()`, allocates coherent pointer arrays for read pointers and write pointers, and registers one lockdep key per possible ring id. Higher-level datapath code then allocates ring memory and calls `ath11k_hal_srng_setup()` for each ring it needs.

`ath11k_hal_srng_setup()` validates the ring number, computes ring id with LMAC offset if needed, initializes the `hal_srng` object, zeros ring memory, applies endian swap flags on big-endian builds, and assigns source or destination pointer fields. Source rings track software head pointer and hardware/FW tail pointer; destination rings track software tail pointer and hardware/FW head pointer. LMAC rings use coherent shared pointer arrays and set `HAL_SRNG_FLAGS_LMAC_RING`; non-LMAC rings use MMIO or shadow-register addresses and are immediately programmed by `ath11k_hal_srng_hw_init()`.

Hardware programming is split by direction. Destination rings write MSI config if enabled, base address, size, ring id/entry size, interrupt thresholds, HP address, initial HP/TP, swap flags, and enable bit. Source rings similarly program MSI, base address/size, entry size, consumer interrupt thresholds, low threshold, TP address, initial HP/TP, loop-count-disable, swap flags, and enable bit.

Runtime users must hold `srng->lock`, call `ath11k_hal_srng_access_begin()`, consume or produce entries, then call `ath11k_hal_srng_access_end()`. Begin refreshes cached hardware pointers and prefetches cached destination descriptors. End publishes software pointer updates either through shared LMAC memory or MMIO writes and records `srng->timestamp` for diagnostics.

Shadow-register flow is optional. `ath11k_hal_srng_shadow_config()` iterates non-CE, non-LMAC rings and assigns target HP/TP registers to limited shadow slots. `ath11k_hal_srng_update_shadow_config()` records target register addresses and rewires the SRNG HP/TP pointer address to the shadow register memory window.

## State and Persistence Behavior

State is entirely runtime memory and hardware register state. `ab->hal.srng_config` is a kmemdup of the template with hardware-specific register addresses. `ab->hal.srng_list[]` stores each live ring's pointer offsets, ring memory, direction, flags, cached HP/TP values, thresholds, MSI data, and last access timestamp. `hal->rdp` and `hal->wrp` are coherent DMA allocations used for FW/HW-visible ring pointers. Shadow register configuration is held in `hal->shadow_reg_addr[]` and `hal->num_shadow_reg_configured`.

No on-disk persistence exists. Hardware-visible state persists only until device reset/deinit. `ath11k_hal_srng_clear()` clears SRNG and shadow bookkeeping without freeing the coherent pointer arrays.

## Dependencies and Integration Points

This file depends on Linux DMA coherent allocation, hif MMIO read/write accessors, HAL descriptor definitions, hardware parameter macros, lockdep, and CE/IRQ state from ath11k core. It is used by datapath TX/RX (`dp_tx.c`, `dp_rx.c`), CE transport, WBM link descriptor setup, HTT ring setup, interrupt diagnostics, and reset/recovery paths.

## Risks and Edge Cases

- Ring pointer barriers are correctness-critical. Source descriptors must be visible before HP updates; destination descriptors must be read before TP updates. Barrier regressions can cause hardware to read stale descriptors or software to process stale DMA data.
- LMAC, non-LMAC MMIO, and shadow-register pointer paths differ. A wrong `supports_shadow_regs` or LMAC flag can publish HP/TP updates to the wrong address.
- Ring sizes are tracked in dwords, while several external APIs use bytes. Entry-size conversion mistakes can corrupt ring strides or HTT setup values.
- `ath11k_hal_srng_src_get_next_entry()` uses modulo because not all ring sizes are powers of two; changing this casually can break non-power-of-two descriptor rings.
- Shadow configuration has a fixed `HAL_SHADOW_NUM_REGS` limit; exceeding it returns `-EINVAL`, and callers must tolerate unavailable shadow slots.
- CE destination setup writes max-buffer length after generic SRNG setup; ring type ordering matters.
- `ath11k_hal_setup_link_idle_list()` programs several WBM scatter registers and assumes valid scatter buffers/counts supplied by caller.

## Test Signals

Strong signals include boot-time SRNG setup across all supported hardware variants, TX/RX traffic through TCL/REO/RXDMA rings, CE transport activity, monitor ring operation, big-endian build coverage, shadow-register capable and non-shadow hardware tests, lockdep runs ensuring SRNG locks are held, ring full/empty boundary tests, reset/deinit/reinit cycles, and `ath11k_hal_dump_srng_stats()` output that shows moving HP/TP timestamps under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal.c -->
