<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx.c

## Purpose
Implements Siena transmit hot-path logic for SKB and XDP frames, including TX queue selection, copy-buffer handling, queue stop/restart decisions, PTP transmit diversion, descriptor submission, and mqprio traffic-class setup.

## Important APIs, Types, And Functions
- SKB path: `efx_siena_hard_start_xmit()` and `__efx_siena_enqueue_skb()`.
- XDP path: `efx_siena_xdp_tx_buffers()`.
- Queue helpers: `efx_tx_get_copy_buffer()`, `efx_enqueue_skb_copy()`, `efx_tx_maybe_stop_queue()`, `efx_tx_send_pending()`, `efx_siena_init_tx_queue_core_txq()`.
- TC setup: `efx_siena_setup_tc()` for `TC_SETUP_QDISC_MQPRIO`.

## Control Flow
`efx_siena_hard_start_xmit()` maps the skb queue index to a TX channel and checksum/high-priority TXQ type, diverts timestamped PTP packets to the PTP path after flushing pending descriptors, and otherwise calls `__efx_siena_enqueue_skb()`. Enqueue handles GSO by software TSO fallback, copies short fragmented packets into DMA copy buffers, maps remaining SKB data to descriptors, stops the netdev queue when thresholds are crossed, marks descriptors pending, and rings the doorbell when `xmit_more` allows. XDP TX selects a per-CPU XDP TX queue, optionally locks borrowed netdev queues, maps each frame as one descriptor, and pushes on `flush`.

## State And Persistence Behavior
TX queue state is in-memory ring counters and descriptor buffers: `insert_count`, `read_count`, `xmit_pending`, `old_read_count`, per-queue stats, copy-buffer pages, and core netdev queue mapping. No persistent storage is changed.

## Dependencies And Integration Points
Depends on TX common mapping/completion helpers, NIC type `tx_limit_len`, farch doorbell push, PTP helpers, XDP frame lifecycle, DMA mapping APIs, Linux netdev queue accounting, and Siena hardware workaround definitions. It is wired into Siena `net_device_ops` as `.ndo_start_xmit` and `.ndo_setup_tc`.

## Risks And Test Signals
Queue stop logic relies on memory barriers to avoid missed wakeups. DMA mapping failure must unwind descriptors and still push earlier pending traffic when needed. XDP borrowed queues must not leave netdev queues permanently stopped. Test signals include high-load TX with `xmit_more`, small fragmented SKBs, GSO fallback, PTP timestamped packets, XDP redirect/TX under CPU count changes, mqprio with high-priority queues, and no TX watchdog stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx.c -->
