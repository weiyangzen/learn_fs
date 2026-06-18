# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/xmit.c

## Purpose
`xmit.c` is the main ath9k transmit engine. It bridges mac80211 TXQs to ath9k hardware descriptors, implements AMPDU aggregation and BlockAck window management, handles DMA queueing and completion for legacy DMA and EDMA, reports TX status/airtime/rate-control feedback, supports power-save buffered frame release, and provides the TX99 send path.

## Important APIs, types, and functions
External entry points include `ath9k_wake_tx_queue()`, `ath_tx_aggr_start()`, `ath_tx_aggr_stop()`, `ath_tx_aggr_sleep()`, `ath_tx_aggr_wakeup()`, `ath9k_release_buffered_frames()`, `ath_txq_setup()`, `ath_txq_update()`, `ath_cabq_update()`, `ath_draintxq()`, `ath_drain_all_txq()`, `ath_tx_cleanupq()`, `ath_txq_schedule()`, `ath_txq_schedule_all()`, `ath_tx_start()`, `ath_tx_cabq()`, `ath_tx_tasklet()`, `ath_tx_edma_tasklet()`, `ath_tx_init()`, `ath_tx_node_init()`, `ath_tx_node_cleanup()`, and `ath9k_tx99_send()`. Important internal helpers include `ath_tx_prepare()`, `ath_tx_setup_buffer()`, `ath_tx_fill_desc()`, `ath_buf_set_rate()`, `ath_tx_sched_aggr()`, `ath_tx_form_aggr()`, `ath_tx_complete_aggr()`, `ath_tx_process_buffer()`, `ath_tx_complete_buf()`, and `ath_tx_rc_status()`.

## Control flow and integration
Normal TX starts in mac80211 with `ath_tx_start()` or TXQ scheduling. Frames are prepared by assigning sequence numbers, adding hardware alignment padding, computing frame metadata, mapping DMA, merging rate tables, filling hardware descriptors, and linking descriptors into a hardware TX queue. TXQ scheduling pulls SKBs from mac80211 TXQs through `ieee80211_tx_dequeue()`, forms either short bursts or aggregates, respects queue depth limits, and adds descriptors to DMA. Completion tasklets poll hardware TX status, handle descriptor holding/stale races, process non-aggregate or aggregate results, update airtime/rate-control status, retry unacked aggregate subframes, send BARs when the BlockAck window advances past failures, and queue final SKB status back to mac80211 after dropping the queue lock.

## State and persistence behavior
Persistent transmit state is spread across `sc->tx`, per-queue `struct ath_txq`, per-node/per-TID `struct ath_atx_tid`, per-frame `struct ath_frame_info`, and hardware descriptors. Key state includes free descriptor lists, DMA addresses, queue depth and AMPDU depth, pending frame counts, retry queues, BlockAck window head/tail bitmap, TID sequence counters, BAR index, power-save filter flags, EDMA FIFO indices, and completion queues. Hardware state persists in TX descriptors, TXDP registers/FIFOs, TX status rings, and DMA engine state until completion, drain, or reset.

## Dependencies
The file depends heavily on mac80211 TXQ, STA, rate-control, airtime, UAPSD, and BlockAck APIs; Linux DMA mapping; ath9k HAL descriptor/TX queue/status functions; ath9k debug/stat/reset/power-save helpers; beacon and channel-context code; Bluetooth coexistence aggregation limits; dynack; PAPRD; and TX99 debug support.

## Risks
This file is concurrency and hardware-state sensitive. Risks include DMA leaks on setup or completion errors, queue lock misuse around mac80211 callbacks, BlockAck window corruption, retry queue ordering bugs, stale descriptor handling races, EDMA FIFO desynchronization, incorrect padding restoration for status SKBs, queue depth underflow, BAR storms, power-save buffered-frame state drift, and reset races while tasklets process completions. Rate/power descriptor programming must also stay aligned with hardware revisions and regulatory limits.

## Test signals
Signals include sustained TCP/UDP throughput, AMPDU start/stop/retry correctness, BlockAck and BAR behavior under packet loss, no TX stalls after queue drain/reset, EDMA and legacy DMA coverage, mac80211 TX status correctness, airtime accounting, UAPSD release/EOSP tests, beacon CABQ delivery, PAPRD completion, TX99 operation, DMA debug clean runs, and stress with station sleep/wake and channel reset.
