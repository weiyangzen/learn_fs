# sources/distributed-fs/ceph-client/rust/helpers/dma.c

## Purpose
Exposes DMA allocation, mask, mapping, and segment-size helpers to Rust device drivers.

## APIs, Types, and Functions
APIs include `dma_alloc_attrs`, `dma_free_attrs`, `dma_set_mask_and_coherent`, `dma_set_mask`, `dma_set_coherent_mask`, `dma_map_sgtable`, `dma_max_mapping_size`, and `dma_set_max_seg_size` wrappers.

## Control Flow, State, and Persistence
State is managed by DMA/IOMMU subsystems and device DMA configuration; helper calls allocate coherent memory, map scatter-gather tables, or mutate device constraints.

## Dependencies and Integration
Depends on `linux/dma-mapping.h`, device DMA masks, scatterlist tables, and architecture/IOMMU DMA ops.

## Risks and Test Signals
Risks include leaks on allocation/free mismatch, wrong DMA direction/attrs, mapping errors not propagated by Rust callers, and mask setup after allocations. Test signals are DMA API debug, IOMMU-enabled test systems, and Rust driver teardown tests.
