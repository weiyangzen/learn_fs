<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-direction.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-direction.h

## Purpose
Defines the standard DMA data direction enum and validation helper.

## Important APIs, Types, And Functions
`enum dma_data_direction` contains `DMA_BIDIRECTIONAL`, `DMA_TO_DEVICE`, `DMA_FROM_DEVICE`, and `DMA_NONE`. `valid_dma_direction()` accepts the first three and rejects `DMA_NONE`.

## Control Flow
DMA APIs use the enum to decide ownership transfer and cache-maintenance direction. `DMA_NONE` is a sentinel and should not reach actual map/sync operations.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Used by nearly every DMA mapping, DMA-BUF, and dmaengine interface that maps memory for device access.

## Risks And Edge Cases
Using the wrong direction can skip required cache invalidation or flush stale data. Passing `DMA_NONE` into map/unmap/sync paths should be rejected by callers or debug code.

## Test Signals
Build and DMA API debug coverage should flag invalid directions. Runtime tests should verify cache-coherency behavior for to-device, from-device, and bidirectional mappings on non-coherent platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-direction.h -->
