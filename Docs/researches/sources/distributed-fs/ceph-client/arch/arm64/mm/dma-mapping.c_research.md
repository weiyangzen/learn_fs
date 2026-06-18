# sources/distributed-fs/ceph-client/arch/arm64/mm/dma-mapping.c

Purpose: provides ARM64 DMA cache synchronization hooks and per-device DMA coherency setup.

Important APIs/types/functions: `arch_sync_dma_for_device`, `arch_sync_dma_for_cpu`, `arch_dma_prep_coherent`, and `arch_setup_dma_ops`.

Control flow: device sync cleans the physical range's linear-map alias to PoC. CPU sync invalidates from PoC for inbound or bidirectional DMA and skips `DMA_TO_DEVICE`. Coherent allocation prep cleans the page range. Setup warns if a non-coherent device's CPU cache writeback granule exceeds `ARCH_DMA_MINALIGN`, records coherency, and applies Xen DMA ops.

State and persistence: issues cache maintenance and sets `dev->dma_coherent`. No disk persistence.

Dependencies/integration: DMA mapping core, cacheflush routines, Xen DMA operation setup, CPU cache line size reporting, and device model.

Risks: `phys_to_virt` assumes the physical range is linearly mapped. Skipping invalidation for `DMA_TO_DEVICE` is correct only for direction semantics. Misreported coherency or cache granule can corrupt DMA buffers.

Test signals: non-coherent DMA tests for all directions, Xen guest DMA setup, cache-line alignment warning paths, coherent allocation visibility, and device-tree/ACPI coherency property coverage.
