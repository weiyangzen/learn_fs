# sources/distributed-fs/ceph-client/drivers/parisc/iommu-helpers.h

## Purpose
This header contains common inline scatter-gather DMA mapping helpers for PA-RISC IOMMU drivers. It separates SG coalescing and I/O page-directory filling so SBA, CCIO, and similar controllers can share the algorithm while supplying controller-specific range allocation and PDIR entry programming callbacks.

## Important APIs, Types, And Functions
`iommu_coalesce_chunks()` walks an SG list, detects virtually contiguous chunks within device segment limits, allocates IOVA ranges through a callback, and marks stream starts using `PIDE_FLAG` in `sg_dma_address()`. `iommu_fill_pdir()` consumes those markers, programs PDIR entries through `iommu_io_pdir_entry()`, and rewrites the SG list into DMA-visible address/length pairs.

## Control Flow
Mapping is a two-pass process. The first pass starts a DMA stream at each SG head, clears previous DMA fields, extends the stream while virtual addresses are contiguous, page-boundary conditions are valid, and max segment size/boundary limits are respected, then allocates a PDIR range and stores the index plus original offset in the stream head. The second pass walks the original SG entries, starts a new output DMA entry whenever `PIDE_FLAG` is seen, initializes the final DMA address, accumulates lengths into the coalesced entry, and calls the supplied PDIR writer for each I/O page.

## State And Persistence
The helpers mutate the caller’s scatterlist in place. Temporary state is encoded in `sg_dma_address()` and `sg_dma_len()` between passes. Persistent hardware state is created only through the caller’s callbacks.

## Dependencies And Integration Points
The helpers depend on Linux scatterlist accessors, DMA segment-size/boundary helpers, PA-RISC IOVP constants, `PIDE_FLAG`, optional `ZX1_SUPPORT`, and controller-specific `struct ioc` fields such as `pdir_base` and `ibase`. `sba_iommu.c` includes this file after defining the required macros and callback types.

## Risks
The implementation assumes SG entries expose meaningful kernel virtual addresses via `sg_virt()`, which is central to PA-RISC coherence handling. Incorrect `PIDE_FLAG` definitions or DMA address reuse would corrupt stream boundaries. The second pass deliberately decrements `dma_sg` before the loop for speed, making off-by-one changes risky. Boundary and segment calculations must stay aligned with DMA API expectations.

## Test Signals
Test with single-entry, multi-entry contiguous, non-contiguous, offset, max-segment, and segment-boundary SG lists. Verify returned mapping count, final `sg_dma_address()`/`sg_dma_len()` values, PDIR entry count, and correct behavior with non-zero IOVA bases under `ZX1_SUPPORT`.
