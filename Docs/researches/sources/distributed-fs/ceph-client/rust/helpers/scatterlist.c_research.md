# sources/distributed-fs/ceph-client/rust/helpers/scatterlist.c

## Purpose
Exposes scatterlist DMA address/length traversal and DMA unmap helpers to Rust.

## APIs, Types, and Functions
APIs are `sg_dma_address`, `sg_dma_len`, `sg_next`, and `dma_unmap_sgtable` wrappers.

## Control Flow, State, and Persistence
State is in DMA-mapped scatter-gather tables; helper reads entries or unmaps a mapping.

## Dependencies and Integration
Depends on `linux/dma-direction.h`, scatterlist structures, and DMA mapping code.

## Risks and Test Signals
Risks include unmapping with wrong device/direction/attrs, iterating past the table, and using DMA fields before mapping. Test signals are DMA API debug and Rust scatter-gather wrapper tests.
