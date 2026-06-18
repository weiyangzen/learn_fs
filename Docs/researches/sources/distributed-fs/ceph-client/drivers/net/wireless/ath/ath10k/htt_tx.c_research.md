# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/htt_tx.c

## Purpose

`htt_tx.c` implements host-to-target HTT setup and transmit submission. It allocates and frees TX descriptor memory, maintains pending MSDU IDs and pending-count backpressure, configures RX rings and fragment descriptor banks in firmware, sends HTT control commands, builds management/data TX commands for 32-bit, 64-bit, and high-latency targets, and supports firmware peer-flow-control TX fetch mode.

## Important APIs, Types, and Functions

- TXQ state: `ath10k_htt_tx_txq_recalc()`, `ath10k_htt_tx_txq_sync()`, `ath10k_htt_tx_txq_update()`, and internal `ath10k_htt_tx_txq_calc_size()`.
- Pending accounting: `ath10k_htt_tx_inc_pending()`, `ath10k_htt_tx_dec_pending()`, `ath10k_htt_tx_mgmt_inc_pending()`, `ath10k_htt_tx_mgmt_dec_pending()`, `ath10k_htt_tx_alloc_msdu_id()`, `ath10k_htt_tx_free_msdu_id()`.
- Memory lifecycle: `ath10k_htt_tx_start()`, `ath10k_htt_tx_destroy()`, `ath10k_htt_tx_stop()`, `ath10k_htt_tx_free()`, plus 32/64-bit txbuf and frag-desc alloc/free helpers.
- HTT commands: `ath10k_htt_h2t_ver_req_msg()`, `ath10k_htt_h2t_stats_req()`, `ath10k_htt_send_frag_desc_bank_cfg_*()`, `ath10k_htt_send_rx_ring_cfg_*()`, `ath10k_htt_h2t_aggr_cfg_msg_*()`, `ath10k_htt_tx_fetch_resp()`.
- TX submission: `ath10k_htt_mgmt_tx()`, `ath10k_htt_tx_hl()`, `ath10k_htt_tx_32()`, `ath10k_htt_tx_64()`.
- Operation selector: `ath10k_htt_set_tx_ops()` chooses high-latency, 32-bit, or 64-bit function table.

## Control Flow

Startup initializes `tx_lock` and `pending_tx`, skips descriptor allocation on high-latency buses, then allocates contiguous TX command buffers, optional continuous fragment descriptor banks, optional peer-flow-control TXQ state, and `txdone_fifo`. Teardown stops HTC HL traffic, force-completes all pending IDs with discard status, destroys the IDR, frees DMA/coherent buffers, unmaps TXQ state, and releases the completion FIFO.

Transmit pending accounting is lock-protected. When `num_pending_tx` reaches `max_num_pending_tx`, mac80211 TX is paused with `ATH10K_TX_PAUSE_Q_FULL`; dropping below the limit unlocks TX. Management probe responses are separately limited by `max_probe_resp_desc_thres`.

RX ring and fragment descriptor configuration commands are built as HTT H2T SKBs and sent through HTC. Ring setup fills firmware-visible ring base, firmware shadow index address, ring length, buffer size, descriptor offset table, and RX flags selecting MAC header, payload, PPDU/MPDU/MSDU descriptor sections, and RX classes. High-latency ring setup sends a minimal config without host DMA ring addresses.

Data TX has three implementations. The high-latency path prepends an HTT command header and TX descriptor directly to the MSDU SKB, reallocating headroom if needed, optionally allocating an HL MSDU ID, then sends with `ath10k_htc_send_hl()`. The 32-bit and 64-bit low-latency paths allocate an MSDU ID, append crypto MIC space for protected management/raw frames where firmware expects it, DMA-map the payload, fill a per-ID TX command buffer and fragment pointer, optionally use continuous fragment descriptor memory, set vdev/TID/checksum/offchannel flags, then bypass normal HTC TX by sending two SG items through `ath10k_hif_tx_sg()`: the prebuilt HTC+HTT header and a prefetch slice of the payload. Completion from `htt_rx.c` releases the ID and unmaps/free resources through txrx unref logic.

Peer-flow-control mode keeps a DMA-mapped shared queue-state table. TXQ depth is encoded as exponent/factor byte values, per-peer/TID bitmap bits mark non-empty queues, and sync increments a sequence number followed by `dma_sync_single_for_device()`. Firmware TX fetch indications are handled in `htt_rx.c`, which calls back into `ath10k_htt_tx_fetch_resp()`.

## State and Persistence Behavior

State is in memory under `struct ath10k_htt`: `pending_tx` IDR maps firmware MSDU IDs to SKBs, `num_pending_tx` and `num_pending_mgmt_tx` drive flow control, `txbuf` and `frag_desc` hold coherent TX descriptor banks, `tx_q_state` holds peer-flow-control metadata and a DMA address, `txdone_fifo` queues completions, and `tx_mem_allocated` prevents duplicate allocation. SKB control blocks persist DMA addresses until completion. No file-backed persistence exists.

## Dependencies and Integration Points

This file depends on HTC allocation/send APIs, HIF scatter-gather transmit, mac80211 TXQ APIs and TX control flags, ath10k MAC flow-control helpers, firmware feature bits, hardware params, DMA APIs, IDR, kfifo, and HTT protocol definitions. It integrates with `htt_rx.c` for TX completions, TX fetch requests, RX ring configuration, and selected operation tables. It integrates with firmware through H2T HTT messages and target-specific 32/64-bit descriptor layouts.

## Risks

- TX resource lifetime spans IDR entries, DMA mappings, SKBs, HTT completions, and optional HTC completions. Missing unmap/free on an error path would leak or double-release.
- 32-bit and 64-bit descriptor formats are parallel but not identical; continuous fragment descriptors and checksum offload flags differ.
- High-latency TX intentionally shares SKB ownership between mac80211 and HTC completion by taking an extra reference; regressions here can cause use-after-free or leaks.
- Management frame MIC padding is added based on protected/action/deauth/disassoc detection and cipher assumptions.
- TXQ shared-state writes require correct locking and DMA sync; stale sequence/count/map values can stall firmware fetch scheduling.
- RX ring config assumes coherent RX ring allocation already succeeded and that descriptor offset ops match the target hardware.

## Test Signals

Good coverage includes allocation failure at every TX buffer stage, DMA mapping failures, max pending TX lock/unlock transitions, management probe-response threshold behavior, protected management and raw frame MIC padding, 32-bit vs 64-bit SG descriptor contents, high-latency headroom reallocation, checksum offload flag emission, offchannel frequency field handling, peer-flow-control TXQ count/map/sequence updates, RX ring config command contents, fragment descriptor bank config with and without firmware peer-flow-control feature, and teardown with pending SKBs. Runtime signals include `trace_ath10k_htt_tx`, `trace_ath10k_tx_hdr/payload`, TX pause state, `txdone_fifo` warnings from RX completion, and HTT command send errors.
