# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-dma.h

## Purpose

This header declares IPU7 DMA allocation, synchronization, mmap, and scatterlist mapping APIs.

## Important APIs, Types, and Functions

It defines `DMA_ATTR_RESERVE_REGION`, `struct ipu7_dma_mapping`, and prototypes for single/SG cache sync, allocate/free, mmap, SG map/unmap, and sgtable map/unmap helpers.

## Control Flow

No implementation flow. The API is used by firmware boot/config code and buffer queues to obtain IPU-visible IOVA mappings.

## State and Persistence Behavior

`struct ipu7_dma_mapping` stores MMU info and an IOVA domain. Allocated mappings are tracked by the implementation on the MMU.

## Dependencies and Integration Points

It includes Linux DMA map ops, DMA mapping, IOVA, scatterlist, and IPU7 bus definitions.

## Risks and Edge Cases

Callers must match map/unmap and alloc/free, pass the correct `ipu7_bus_device`, and handle the special reserve-region attribute.

## Test Signals

Compile coverage and allocation/map/unmap tests through boot config, firmware queues, and V4L2 capture buffers.
