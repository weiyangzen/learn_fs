<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/tx.c

## Purpose
Implements the Falcon EF4 transmit path: SKB DMA mapping or copy-buffer coalescing, descriptor production, hardware doorbell pushes, completion processing, Linux netdev queue flow control, traffic class setup, and TX queue lifecycle.

## Important APIs, types, and functions
- Public transmit entry points: `ef4_hard_start_xmit`, `ef4_enqueue_skb`, `ef4_xmit_done`, `ef4_setup_tc`, `ef4_init_tx_queue_core_txq`, `ef4_probe_tx_queue`, `ef4_init_tx_queue`, `ef4_fini_tx_queue`, and `ef4_remove_tx_queue`.
- Sizing API: `ef4_tx_max_skb_descs`.
- Internal helpers: `ef4_tx_get_copy_buffer`, `ef4_enqueue_skb_copy`, `ef4_tx_map_data`, `ef4_tx_map_chunk`, `ef4_enqueue_unwind`, `ef4_dequeue_buffer(s)`, and `ef4_tx_maybe_stop_queue`.

## Control flow
`ef4_hard_start_xmit` chooses a channel and TX queue type from SKB queue mapping and checksum state, then delegates to `ef4_enqueue_skb`. Enqueue copies short or small fragmented packets into per-queue copy-buffer pages, otherwise maps SKB head/frags for DMA and creates one or more NIC-limited descriptors. It updates BQL, pushes descriptors immediately unless `xmit_more` can batch them, and may push a partner queue to avoid watchdog stalls. Completion calls `ef4_xmit_done`, dequeues through the completion index, unmaps DMA, consumes SKBs, updates completion counters, wakes stopped queues when paired fill levels fall below the wake threshold, and records empty queue state.

## State and persistence behavior
Per-queue state includes software descriptor buffers, copy-buffer pages, insert/write/read counts, stale read/write snapshots, BQL state, queue stop/wake thresholds from `efx`, and stats such as `tx_packets`, `pkts_compl`, `bytes_compl`, `merge_events`, and `cb_packets`. DMA mappings are owned by the final descriptor for each mapped fragment. No durable persistence exists.

## Dependencies and integration points
Uses Linux PCI DMA, SKB fragments, BQL, netdev TX queues, traffic-control mqprio setup, cache/page helpers, and driver NIC operations `ef4_nic_probe_tx`, `ef4_nic_init_tx`, `ef4_nic_push_buffers`, and `ef4_nic_remove_tx`. Hardware workaround macros from `workarounds.h` affect descriptor bounds and minimum transmit size.

## Risks and test signals
Risks include DMA unwind leaks after partial mapping failure, queue stop/wake races, partner queue batching leaving descriptors unpushed, and spurious completions causing reset. Test signals are TX completion counters, BQL behavior, netdev watchdog absence, mqprio queue count changes, loopback self-test TX completion counts, DMA mapping error paths, and reset logs for `RESET_TYPE_TX_SKIP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/tx.c -->
