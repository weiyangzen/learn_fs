# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/tx.c

## Purpose
Implements the shared mt76 transmit scheduler, TX status tracking, power-save frame release, pending/offchannel queues, AQL backpressure fallback, hardware queue blocking, token management, and common queue-completion helpers.

## Important APIs, Types, And Functions
Major exports include `mt76_tx()`, `mt76_wake_tx_queue()`, `mt76_txq_schedule_all()`, `mt76_tx_worker_run()`, `mt76_release_buffered_frames()`, `__mt76_tx_complete_skb()`, TX status helpers (`mt76_tx_status_*`), `mt76_stop_tx_queues()`, `mt76_queue_tx_complete()`, token APIs (`mt76_token_consume()`, `mt76_token_release()`, RX token variants), `mt76_ac_to_hwq()`, `mt76_skb_adjust_pad()`, and `__mt76_set_tx_blocked()`.

## Control Flow
mac80211 or chip code queues SKBs through `mt76_tx()` or iTXQ wakeups. The worker drains pending WCID queues first, then schedules mac80211 TXQs per AC. Burst scheduling dequeues frames, gets rates when needed, checks PS/reset/offchannel/AQL limits, calls bus-specific `queue_ops->tx_queue_skb()`, and kicks hardware. Completion either reports immediate status or waits for both DMA_DONE and TXS_DONE via IDR packet ids. Status timeout/flush paths mark missing TXS as failed or ACKed depending on driver flags.

## State And Persistence
State spans per-WCID pending/offchannel queues, `tx_list`, `non_aql_packets`, packet-id IDRs, `wcid_list`, queue head/tail/queued counts, queue blocked/stopped flags, per-PHY TX lists, `mgmt_tx_pending`, token IDRs, token counts, WED token counts, and TX callback flags embedded in SKBs.

## Dependencies And Integration Points
Integrates with mac80211 TXQs, sta/vif status APIs, mt76 queue ops for USB/SDIO/MMIO, WED offload token ranges, testmode, RCU WCID lookup, driver `tx_complete_skb()`, and the mt76 worker framework.

## Risks
The highest risks are lifetime and accounting bugs: SKBs must be reported once, IDR packet ids removed, non-AQL counters balanced, queue locks respected, and token blocking lifted when enough tokens return. Offchannel and management queue decisions affect association and ROC correctness. WED packet-id shortcuts and unreliable TXS fallback can hide real firmware status failures.

## Test Signals
High-throughput TX, per-AC scheduling fairness, PS release EOSP behavior, aggregation BAR generation, offchannel management TX, testmode TX completion, TX status timeout/flush, WED active/inactive operation, token exhaustion/unblock, reset while queues are non-empty, and lockdep/KASAN coverage around status callbacks.
