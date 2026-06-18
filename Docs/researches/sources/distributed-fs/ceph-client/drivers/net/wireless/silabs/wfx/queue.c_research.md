# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/queue.c

Purpose: Implements WFx software queues between mac80211 TX and the BH firmware TX path, including TX locks, flushes, weighted queue selection, pending-frame lookup, and drop diagnostics.

Important APIs and functions: `wfx_tx_lock()`, `wfx_tx_unlock()`, `wfx_tx_flush()`, and `wfx_tx_lock_flush()` provide global TX gating. Queue APIs initialize/check/drop/enqueue per-vif queues and select the next HIF message with `wfx_tx_queues_get()`. Pending helpers manage `wdev->tx_pending`, locate confirms by packet ID, drop pending frames on frozen chip, dump old frames, and compute firmware delay.

Control flow and integration: `data_tx.c` enqueues SKBs into normal/CAB/offchannel queues; BH calls `wfx_tx_queues_get()` when firmware credits are available. Queue selection sorts all vif/AC queues by pending weight, prioritizes offchannel frames, blocks normal/CAB during scan as needed, allows CAB only after DTIM, and then normal traffic. Pending SKBs move to `tx_pending` when handed to firmware and are removed by TX confirmations.

State and persistence: Per-vif queues store normal/CAB/offchannel SKB heads and `pending_frames` counts. Global `tx_lock`, `tx_pending`, `tx_dequeue`, `hif.tx_buffers_empty`, `chip_frozen`, and `after_dtim_tx_allowed` coordinate flow control.

Dependencies: Depends on mac80211 queue mapping, SKB queues, atomics, scan lock, BH TX request, data TX SKB accessors, and station/vif iteration.

Risks and test signals: Risks include pending counter imbalance, TX lock underflow, flush timeout freezing the chip, CAB starvation, scan/offchannel ordering, packet ID lookup while list unlocked, and queue weight fairness. Tests should cover multi-vif AC scheduling, scan lock blocking normal traffic, CAB after DTIM, offchannel priority, flush with and without drop, pending confirm lookup, frozen-chip drop, and queue-empty assertions on interface removal.

Test signals: Source read size: 322 lines, 8842 bytes.
