# sources/distributed-fs/ceph-client/include/xen/swiotlb-xen.h

## Purpose
`swiotlb-xen.h` declares Xen-specific SWIOTLB DMA synchronization hooks and DMA map operations used when guest-visible DMA addresses differ from machine addresses or when bounce buffering is required.

## Important APIs, Types, and Functions
The header declares `xen_dma_sync_for_cpu()`, `xen_dma_sync_for_device()`, and `xen_swiotlb_dma_ops`. It includes generic `linux/swiotlb.h` and architecture-specific Xen SWIOTLB definitions.

## Control Flow
Device DMA paths use `xen_swiotlb_dma_ops` for mapping and unmapping; sync helpers transfer ownership/cache visibility between device and CPU for a DMA address, size, and direction.

## State and Persistence Behavior
State is held by the SWIOTLB pool and DMA mappings in implementation code. Sync calls operate on transient DMA buffers and do not persist beyond mapping lifetime.

## Dependencies and Integration Points
It integrates Linux DMA API, SWIOTLB bounce buffering, Xen grant/DMA restrictions, and architecture-specific address translation.

## Risks and Test Signals
Risks include stale CPU/device cache visibility, wrong DMA direction, bounce-buffer size exhaustion, and missing arch support. Test signals include DMA mapping tests on Xen guests, bidirectional sync coverage, high-memory DMA, and restricted-memory virtio/grant DMA configurations.
