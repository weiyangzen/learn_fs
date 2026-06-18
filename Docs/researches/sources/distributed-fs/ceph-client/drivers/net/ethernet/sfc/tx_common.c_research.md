# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tx_common.c

Purpose: contains shared SFC TX queue allocation, initialization, teardown, descriptor cleanup, DMA mapping, and software TSO fallback helpers used by multiple NIC generations.

Important functions: `efx_probe_tx_queue()` allocates software rings, copy-buffer page metadata, and NIC hardware TX rings. `efx_init_tx_queue()`, `efx_fini_tx_queue()`, and `efx_remove_tx_queue()` reset counters, initialize hardware, drain outstanding buffers, and free resources. `efx_dequeue_buffer()` unmaps DMA and consumes SKBs/XDP frames. `efx_xmit_done()` handles completion ranges and queue wakeups. `efx_tx_map_chunk()` splits DMA ranges by NIC limits. `efx_tx_map_data()` maps skb head/frags and records the final buffer as the completion owner. `efx_tx_tso_fallback()` software-segments and re-enqueues.

Control flow: probing sets a power-of-two descriptor mask and registers the queue by type. Completion walks buffers up to the hardware index, detects spurious completions, updates packet/byte counters, wakes stopped queues when fill falls below the wake threshold, and publishes empty state with barriers. Mapping records unmap ownership only on the final descriptor for each mapped region and tags the last buffer with `EFX_TX_BUF_SKB`.

State and dependencies: queue state includes buffers, copy pages, descriptor counts, completion counters, timestamp state, XDP flags, and per-type channel lookup. Dependencies include NIC-specific `efx_nic_*` operations, DMA APIs, GSO, and PTP timestamp conversion.

Risks and test signals: risks include DMA leak on mid-fragment mapping failure before caller unwind, incorrect final-buffer ownership, stale queue-empty publication, and software TSO recursion/backpressure. Test probe/remove failures, forced DMA mapping errors, completion of merged descriptors, XDP completion accounting, queue wake thresholds, and GSO fallback.
