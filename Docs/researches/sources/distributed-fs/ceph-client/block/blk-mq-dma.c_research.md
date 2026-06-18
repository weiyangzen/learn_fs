# sources/distributed-fs/ceph-client/block/blk-mq-dma.c

## Purpose
`blk-mq-dma.c` maps blk-mq requests into DMA segments and scatterlists. It supports normal request payloads, special payloads, PCI peer-to-peer DMA, IOVA-coalesced mappings, direct physical mappings, and integrity metadata mappings.

## Important APIs, Types, And Functions
Exported APIs are `blk_rq_dma_map_iter_start()`, `blk_rq_dma_map_iter_next()`, `__blk_rq_map_sg()`, and, under integrity support, `blk_rq_integrity_dma_map_iter_start()`, `blk_rq_integrity_dma_map_iter_next()`, and `blk_rq_map_integrity_sg()`. Internal iterators include `struct blk_map_iter`, `blk_map_iter_next()`, `blk_dma_map_iter_start()`, `blk_dma_map_bus()`, `blk_dma_map_direct()`, and `blk_rq_dma_map_iova()`.

## Control Flow
Mapping starts by initializing an iterator from request bios, special payload, or an empty flush request. `blk_map_iter_next()` emits physically mergeable vectors while respecting queue segment size limits and bio boundaries. The first vector determines PCI P2PDMA behavior: bus-address mapping returns a bus address directly; host-bridge P2P is treated like normal DMA with `DMA_ATTR_MMIO`; unsupported P2P fails with `BLK_STS_INVAL`. If request gap constraints allow and IOVA allocation succeeds, the code links all physical vectors into one IOVA mapping and synchronizes it; otherwise it maps one segment at a time with `dma_map_phys()`. Scatterlist mapping mirrors the iterator and marks the final entry.

## State And Persistence
State is caller-provided and transient: `struct dma_iova_state` must survive until unmap, while `struct blk_dma_iter` tracks current mapping status, P2P state, DMA address, and length during iteration. No persistent kernel policy state is owned.

## Dependencies And Integration Points
The file integrates with DMA mapping APIs, PCI P2PDMA, block queue segment limits, request integrity metadata, scatterlist helpers, and drivers that consume DMA iterators or legacy scatterlists.

## Risks And Test Signals
Risks include incorrect physical segment coalescing, IOVA cleanup on partial link/sync failure, P2PDMA map-mode misclassification, scatterlist termination reuse, and integrity segment overrun. Tests should cover empty flush requests, special payloads, mixed-bio request chains, P2P bus and host-bridge cases, IOMMU merge-boundary restrictions, DMA mapping errors, and integrity metadata segment counts.
