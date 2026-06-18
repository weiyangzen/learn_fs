<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx_common.c

## Purpose
Provides common Siena TX queue allocation, initialization, teardown, DMA unmapping, completion processing, descriptor mapping, enqueue unwind, descriptor count estimation, and software TSO fallback.

## Important APIs, Types, And Functions
- Queue lifecycle: `efx_siena_probe_tx_queue()`, `efx_siena_init_tx_queue()`, `efx_siena_fini_tx_queue()`, `efx_siena_remove_tx_queue()`.
- Completion path: `efx_siena_xmit_done()`, `efx_siena_xmit_done_check_empty()`, `efx_dequeue_buffer()`, `efx_dequeue_buffers()`.
- Mapping/unwind: `efx_siena_tx_map_chunk()`, `efx_siena_tx_map_data()`, `efx_siena_enqueue_unwind()`.
- Limits/fallback: `efx_siena_tx_max_skb_descs()` and `efx_siena_tx_tso_fallback()`.

## Control Flow
Probe rounds queue entries up to a hardware-compatible power of two, allocates software descriptor and copy-buffer arrays, then delegates hardware ring probing to the NIC type. Init resets ring counters, timestamp/XDP flags, and hardware descriptors. TX mapping maps the SKB head, optionally splits the TSO header, walks fragments, assigns unmap responsibility to final descriptors, and stores the SKB on the final buffer. Completion dequeues through a reported index, unmaps DMA, completes SKBs or XDP frames, updates queue accounting, wakes stopped queues when fill is below threshold, and records empty-read state for hardware.

## State And Persistence Behavior
Maintains runtime TX ring state only: descriptor buffers, copy-buffer pages, DMA mapping metadata, queue counters, completion stats, timestamp completion fields, and `core_txq` state. Teardown frees remaining buffers and resets netdev TX accounting.

## Dependencies And Integration Points
Depends on `net_driver.h`, common NIC TX operations (`efx_nic_probe_tx()`, `efx_nic_init_tx()`, `efx_nic_remove_tx()`), DMA APIs, PTP timestamp conversion, XDP return APIs, Linux GSO segmentation, and reset scheduling on invalid completions.

## Risks And Test Signals
DMA mapping failures after earlier fragments rely on caller unwind to unmap all inserted descriptors. Spurious completions schedule `RESET_TYPE_TX_SKIP`. Timestamp completion fields must be consumed exactly once. Test signals include TX ring probe/remove leak checks, fragmented SKB DMA unmap correctness, software TSO fallback, XDP completion returns, queue wake under high load, and reset logs for bogus completion indices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx_common.c -->
