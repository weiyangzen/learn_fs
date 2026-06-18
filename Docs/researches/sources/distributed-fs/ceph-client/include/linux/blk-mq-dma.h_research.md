# sources/distributed-fs/ceph-client/include/linux/blk-mq-dma.h

## Purpose
`blk-mq-dma.h` defines DMA mapping iterators for blk-mq requests. It abstracts walking request data or integrity vectors and coalescing them into DMA address ranges, including support for PCI peer-to-peer DMA and IOVA-based coalescing.

## Important APIs, Types, And Functions
`struct blk_map_iter` stores the current `bvec_iter`, current `bio`, bvec array, and whether the iterator is walking integrity data. `struct blk_dma_iter` exposes output `addr` and `len`, peer-to-peer map state, final `blk_status_t status`, and internal `blk_map_iter`.

The main functions are `blk_rq_dma_map_iter_start()` and `blk_rq_dma_map_iter_next()`. `blk_rq_dma_map_coalesce()` returns whether the DMA state represents a single coalesced IOVA range via `dma_use_iova()`. `blk_rq_dma_unmap()` handles teardown: bus-address peer-to-peer mappings need no action, IOVA mappings are destroyed with optional `DMA_ATTR_MMIO`, and non-IOVA mappings report whether manual unmapping is still needed based on `dma_need_unmap()`.

## Control Flow And State
Mapping starts with a request, DMA device, `dma_iova_state`, and iterator. Repeated `*_next()` calls advance the internal bio/bvec state and emit address ranges until false is returned; at that point `iter->status` indicates the terminal error/status. Unmap control branches on the peer-to-peer mapping type and whether an IOVA state was used.

State is transient and caller-owned: DMA address/length outputs, peer-to-peer state, IOVA state, and the iterator cursor. The request's data direction is derived through `rq_dma_dir(req)`.

## Dependencies And Integration Points
The header includes `linux/blk-mq.h` and `linux/pci-p2pdma.h`; it also relies on DMA APIs such as `dma_use_iova()`, `dma_iova_destroy()`, and `dma_need_unmap()`. It is used by block drivers that map requests for hardware submission, and by integrity code for protection metadata mapping.

## Risks And Test Signals
Risks include leaked DMA mappings on partial failure, wrong DMA direction, mishandling peer-to-peer bus addresses vs host-bridge mappings, assuming all segments coalesced, and ignoring `iter->status`. Tests should exercise normal multi-segment mapping, IOVA coalesced mapping, P2PDMA map types, integrity mapping, partial-map failure cleanup, and devices where `dma_need_unmap()` is false.
