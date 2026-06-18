# sources/distributed-fs/ceph-client/include/linux/platform_data/amd_qdma.h

Purpose: defines platform data and DMA-channel filter metadata for AMD QDMA engine integration.

Important APIs and types: `struct qdma_queue_info` carries `enum dma_transfer_direction dir` for DMA channel matching. `QDMA_FILTER_PARAM(qinfo)` casts queue info for dmaengine filter callbacks. `struct qdma_platdata` provides `max_mm_channels`, `irq_index`, a `dma_slave_map *device_map`, and a `device *dma_dev` for DMA operations.

Control flow: platform code supplies QDMA platform data during device registration. DMA clients pass `QDMA_FILTER_PARAM()` to request channels matching transfer direction; the QDMA driver uses max channel counts, IRQ index base, slave map, and DMA device pointer during probe and channel allocation.

State and persistence: static probe-time capability and mapping data. Runtime DMA descriptors, queues, interrupts, and channel state live in the DMA engine driver.

Dependencies and integration points: depends on `linux/dmaengine.h`, `dma_slave_map`, and device model. Integrates platform devices, dmaengine channel lookup, interrupt allocation, and DMA client mapping.

Risks and test signals: risks include direction filter mismatches, wrong IRQ base, stale or undersized slave maps, and invalid channel-count limits. Test dmaengine channel requests for both directions, interrupt handling, probe/remove, slave-map lookup, and DMA transfer completion/error paths.
