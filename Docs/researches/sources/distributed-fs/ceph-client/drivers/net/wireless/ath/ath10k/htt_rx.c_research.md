# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/htt_rx.c

## Purpose

`htt_rx.c` implements the target-to-host side of ath10k HTT. It owns low-latency RX ring allocation/refill, in-order physical-address RX delivery, high-latency SDIO/USB-style RX indications, RX descriptor decoding, decapsulation back into mac80211 frame formats, HTT event dispatch, TX completion demultiplexing, peer/TID security replay tracking, peer TX statistics ingestion, and the NAPI completion task that drains RX/TX work.

## Important APIs, Types, and Functions

- RX ring lifecycle: `ath10k_htt_rx_alloc()`, `ath10k_htt_rx_ring_refill()`, `ath10k_htt_rx_free()`, `ath10k_htt_rx_ring_free()`.
- RX buffer ownership helpers: `ath10k_htt_rx_netbuf_pop()`, `ath10k_htt_rx_amsdu_pop()`, `ath10k_htt_rx_pop_paddr()`, `ath10k_htt_rx_pop_paddr32_list()`, `ath10k_htt_rx_pop_paddr64_list()`.
- Frame metadata and decapsulation: `ath10k_htt_rx_h_ppdu()`, `ath10k_htt_rx_h_rates()`, `ath10k_htt_rx_h_channel()`, `ath10k_htt_rx_h_mpdu()`, `ath10k_htt_rx_h_undecap_*()`, `ath10k_htt_rx_h_csum_offload()`.
- Delivery paths: `ath10k_htt_rx_handle_amsdu()` for classic low-latency RX, `ath10k_htt_rx_in_ord_ind()` for in-order paddr indications, and `ath10k_htt_rx_proc_rx_ind_hl()` / `ath10k_htt_rx_proc_rx_frag_ind_hl()` for high-latency buses.
- HTT event dispatch: `ath10k_htt_t2h_msg_handler()` and wrapper `ath10k_htt_htc_t2h_msg_handler()`.
- Completion/statistics: `ath10k_htt_rx_tx_compl_ind()`, `ath10k_htt_rx_tx_fetch_ind()`, `ath10k_htt_rx_tx_mode_switch_ind()`, `ath10k_htt_fetch_peer_stats()`, `ath10k_fetch_10_2_tx_stats()`.
- Poll entry points: `ath10k_htt_rx_hl_indication()` and `ath10k_htt_txrx_compl_task()`.
- Operation selector: `ath10k_htt_set_rx_ops()` installs 32-bit, 64-bit, or high-latency RX ops.

## Control Flow

RX setup allocates a coherent paddr ring and shadow firmware index, initializes `netbufs_ring`, `skb_table`, queues, timer, and counters. Refill allocates aligned SKBs, clears descriptor attention flags, DMA maps each buffer, writes the physical address into the 32-bit or 64-bit ring, optionally hashes the SKB by paddr for in-order RX, then publishes the new alloc index after a memory barrier.

Classic low-latency firmware first sends RX indications that increment `num_mpdus_ready`. `ath10k_htt_txrx_compl_task()` drains queued mac80211 RX frames, processes in-order indications, then repeatedly calls `ath10k_htt_rx_handle_amsdu()` while MPDUs are ready. That handler pops all MSDUs in one A-MSDU, decodes PPDU status, optionally unchains multi-buffer raw MSDUs, filters invalid/no-channel/CAC frames, reconstructs 802.11 frames from firmware decap formats, queues MSDUs, updates station RX stats, and lets the NAPI task deliver them through `ieee80211_rx_napi()`.

In-order RX indications contain physical addresses and optional offload metadata. `ath10k_htt_rx_in_ord_ind()` validates the event, pops matching SKBs from the hash table, handles offloaded frames separately, extracts complete A-MSDUs from the list, then reuses the PPDU/filter/MPDU/enqueue pipeline. Any paddr-pop or A-MSDU extraction inconsistency marks `htt->rx_confused` and forces poll rescheduling.

High-latency RX receives the complete packet in the HTT indication SKB rather than the low-latency host ring. `ath10k_htt_t2h_msg_handler()` queues RX indications for later polling; `ath10k_htt_rx_hl_indication()` calls `ath10k_htt_rx_proc_rx_ind_hl()`, which strips HTT/firmware descriptor headers, derives signal/channel/status flags, synthesizes QoS control when required, reconstructs IV headers for PN checking cases, and delivers directly to mac80211. Fragment indications first decapsulate WEP/TKIP/CCMP headers, enforce unicast/no-retry/PN sequence checks, then pass through the same high-latency RX indication handler.

The HTT dispatcher maps firmware message IDs through `ar->htt.t2h_msg_types`, then handles version confirmation, peer map/unmap, management/data TX completions, security indications, RX fragment and in-order queues, ADD BA/DEL BA offload notifications, channel changes, TX fetch requests, mode-switch events, peer stats, pktlog, and unhandled-event warnings. It returns whether the caller should free the event SKB; queued RX/fetch paths retain ownership.

## State and Persistence Behavior

Persistent driver state is in `struct ath10k_htt` and peer/station objects, not on disk. Key mutable state includes `rx_ring.fill_cnt`, `rx_ring.sw_rd_idx`, `rx_ring.alloc_idx.vaddr`, `rx_ring.netbufs_ring`, `rx_ring.skb_table`, `rx_confused`, `rx_msdus_q`, `rx_in_ord_compl_q`, `rx_indication_head`, `tx_fetch_ind_q`, `num_mpdus_ready`, `txdone_fifo`, `rx_status`, and per-peer PN arrays. RX security indications update `peer->rx_pn[]` and clear PN history. TX completion handling updates pending TX references and station airtime/rate statistics.

DMA state is carefully paired: posted RX buffers are mapped `DMA_FROM_DEVICE` and unmapped when popped or freed; coherent rings and shadow indices are freed at RX teardown. The refill timer persists across memory pressure and reschedules until the desired fill level is restored. `rx_confused` is a sticky in-memory failure flag that prevents further RX pop work after ring corruption is detected.

## Dependencies and Integration Points

This file depends on ath10k core, HTC, HTT protocol structs, mac80211, WMI peer state, rx descriptor ops from hardware parameters, DMA APIs, SKB queues, ID/hash helpers, NAPI, tracepoints, and debug logging. It integrates with mac80211 via `ieee80211_rx_napi()`, BA session offload callbacks, TXQ scheduling, airtime registration, and rate/status update APIs. It integrates with firmware through HTT target-to-host messages and the host-populated RX paddr ring configured by `htt_tx.c`.

## Risks

- Descriptor and SKB pointer arithmetic is extensive. Incorrect `rx_desc_ops` offsets, decap alignment, or malformed firmware lengths can corrupt frame reconstruction or trigger drops.
- The RX ring can enter `rx_confused` on unexpected empty pops, incomplete descriptors, or paddr mismatches; recovery is limited to refusing further processing, with comments suggesting firmware restart may be needed.
- Replay checks are split between low-latency fragments and high-latency indications. Any peer/TID/security indication ordering bug can reject valid fragments or accept stale PN state.
- Some event handlers only warn on unexpected firmware structures, such as multiple HL MPDU ranges, unsupported TX inspect events, or malformed TX fetch records.
- `rx_status` is reused across frames/PPDUs and must be reset in precise places to avoid leaking stale rate/channel flags.
- TX completion RSSI/PPDU-duration parsing depends on optional padding and firmware flags; offset mistakes could misread completion payloads.

## Test Signals

Useful tests include RX ring allocation/refill/free under DMA mapping failure, RX under memory pressure and refill timer retry, malformed HTT event length checks, raw/native-wifi/ethernet/SNAP decapsulation cases, encrypted A-MSDU and fragmented CCMP/TKIP replay cases, in-order paddr RX on 32-bit and 64-bit targets, HL RX delivery with and without RSSI/channel, TX completion FIFO overrun behavior, TX fetch scheduling in push-pull mode, peer map/security indication ordering, and pktlog/peer stats parsing for legacy/HT/VHT rates. Runtime signals are `ath10k_warn()` ring corruption messages, `rx_crc_err_drop`, station RX/TX stats, tracepoints `trace_ath10k_htt_rx_desc`, `trace_ath10k_rx_hdr/payload`, `trace_ath10k_htt_stats`, and NAPI budget behavior.
