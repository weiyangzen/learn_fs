<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-buf-mapping.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-buf-mapping.h

## Purpose
Declares helper functions for converting physical-vector DMA-buf mappings into scatter-gather tables and freeing them.

## Important APIs, Types, And Functions
The APIs are `dma_buf_phys_vec_to_sgt()` and `dma_buf_free_sgt()`. Inputs include a `dma_buf_attachment`, optional peer-to-peer provider, an array of `struct phys_vec`, range count, total size, and DMA direction.

## Control Flow
Importers/exporters build an SG table from physical ranges for an attachment and direction, use it for DMA, then free it through the paired helper.

## State And Persistence
State is transient SG table mapping state associated with an attachment. No persistence is defined.

## Dependencies And Integration Points
Depends on `dma-buf.h`, DMA directions, physical-vector and PCI P2P concepts. It integrates DMA-buf sharing with peer-to-peer or physical-range backed exporters.

## Risks And Edge Cases
Range count, total size, and direction must match the buffer and DMA operation. Peer-to-peer ranges may not have normal pages, so importers must support that path. Free must pair with successful conversion to avoid mapping leaks.

## Test Signals
Tests should cover single/multiple ranges, P2P and non-P2P providers, invalid size/count, every valid DMA direction, and error cleanup after partial SG construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-buf-mapping.h -->
