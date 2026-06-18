# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-queue.h

## Purpose
This header declares ivtv queue and stream-buffer helpers and defines inline policy for DMA vs PIO use and DMA cache synchronization.

## Important APIs, Types, and Functions
It defines `IVTV_DMA_UNMAPPED` and `SLICED_VBI_PIO`, inline helpers `ivtv_might_use_pio`, `ivtv_use_pio`, `ivtv_might_use_dma`, `ivtv_use_dma`, buffer/stream DMA sync helpers, and prototypes for buffer copy/swap, queue operations, and stream allocation/freeing.

## Control Flow
The inline helpers decide whether a stream can or should use PIO based on stream DMA direction and sliced-VBI policy. Sync helpers gate DMA cache operations so PIO streams skip DMA API calls.

## State and Persistence Behavior
The header stores no state. Its helpers affect DMA synchronization of stream buffers and SG descriptors; implementation functions mutate queues and allocations.

## Dependencies and Integration Points
It depends on `struct ivtv_stream`, `struct ivtv_buffer`, `struct ivtv_queue`, PCI device DMA APIs, and stream type constants. IRQ, fileops, stream setup, VBI, UDMA, and YUV paths rely on its policy helpers.

## Risks
Changing PIO/DMA policy changes interrupt and buffer-flow behavior globally. Sync helpers must be used consistently around CPU and device access or stale/corrupt data can appear.

## Test Signals
Build coverage plus DMA and PIO capture/decode tests, sliced VBI behavior with policy toggled, cache-coherency checks on non-coherent platforms, and allocation/free leak checks validate the header contract.
