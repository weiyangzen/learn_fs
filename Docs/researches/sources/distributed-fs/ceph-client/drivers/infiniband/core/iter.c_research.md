# sources/distributed-fs/ceph-client/drivers/infiniband/core/iter.c

## Purpose
This file implements exported scatterlist block-iterator primitives for RDMA drivers. The iterator advances over DMA-mapped scatterlist data in fixed-size blocks chosen by the driver, reporting block DMA addresses that may span scatterlist entries.

## Important APIs, Types, And Functions
The exported APIs are `__rdma_block_iter_start()` and `__rdma_block_iter_next()`, operating on `struct ib_block_iter` from `<rdma/iter.h>`. The iterator tracks the current scatterlist pointer, remaining SG entries, current SG byte advance, current block DMA address, and page/block-size bit.

## Control Flow
`__rdma_block_iter_start()` zeroes the iterator, stores the scatterlist and entry count, and derives the block-size bit with `__fls(pgsz)`. `__rdma_block_iter_next()` stops when no SG entries remain, sets the current DMA address, computes bytes until the next block boundary, consumes complete SG fragments as needed, advances into the final SG entry, and returns true for the produced block.

## State And Persistence
The iterator is caller-owned transient state. There is no persistent storage or locking; callers must provide a stable DMA-mapped scatterlist and valid block size during iteration.

## Dependencies And Integration Points
It depends on Linux scatterlist DMA accessors and RDMA iterator definitions. Drivers use it when walking DMA segments by hardware page or block boundaries during MR registration or memory-key programming.

## Risks And Test Signals
Risks include invalid or non-power-of-two `pgsz`, zero `pgsz`, zero-length SG entries, exact block-boundary arithmetic, and callers using unmapped or mutated scatterlists. Tests should cover single and multi-entry SG lists, unaligned DMA addresses, exact boundaries, empty input, large block sizes, and expected DMA address sequences.
