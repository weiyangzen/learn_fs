# sources/distributed-fs/ceph-client/arch/sparc/kernel/iommu.c

## Purpose
`iommu.c` implements sparc64 sun4u-style DMA mapping operations through an IOMMU and streaming buffer. It provides the architecture `dma_map_ops` for coherent allocation, physical and scatterlist streaming mappings, unmapping, synchronization, and DMA mask checks.

## Important APIs, Types, and Functions
Publicly visible functions include `iommu_table_init()` and exported `dma_ops`. DMA operations are `dma_4u_alloc_coherent()`, `dma_4u_free_coherent()`, `dma_4u_map_phys()`, `dma_4u_unmap_phys()`, `dma_4u_map_sg()`, `dma_4u_unmap_sg()`, sync helpers, and `dma_4u_supported()`. Internal helpers include `iommu_flushall()`, `iopte_make_dummy()`, context allocation/free, `strbuf_flush()`, and `fetch_sg_ctx()`.

## Control Flow and State
Table init allocates the bitmap, dummy page, and IOMMU page table, fills all IOPTEs with dummy-page mappings, and sets up the shared pool allocator. Coherent allocation gets pages, allocates IOMMU entries, writes consistent writable IOPTEs, and returns CPU plus DVMA address. Streaming map allocates entries and optional context, writes IOPTEs with streaming-buffer or consistent flags and write permission based on direction. Unmap records context, flushes streaming buffers for device-to-CPU paths unless skipped, replaces IOPTEs with dummy mappings, frees context, and frees bitmap entries. SG mapping allocates and writes per-element IOPTEs while merging adjacent DMA segments subject to max segment and boundary rules, with rollback on failure.

## Persistence and Dependencies
Persistent state is in `struct iommu`, `struct strbuf`, the IOPTE table, context bitmap, dummy page, flush flag memory, and allocator bitmap. Dependencies include physical bypass ASIs, streaming buffer registers, `iommu-common`, device archdata, PCI quirk `ali_sound_dma_hack()`, and Linux DMA API.

## Integration Points, Risks, and Test Signals
Integration points are all sparc64 DMA-capable devices using `dma_ops`. Risks include context leaks on allocation failures, dummy mappings hiding stale-device DMA, streaming-buffer flush timeouts, SG rollback under lock while freeing allocator ranges, unsupported MMIO map path, and order limit for coherent allocation. Test signals are DMA API selftests, disk/network I/O under IOMMU, streaming buffer timeout absence, SG map/unmap leak checks, DMA mask rejection/quirk behavior, and cache coherency for bidirectional transfers.
