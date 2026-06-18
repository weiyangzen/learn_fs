# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_queue.c

Purpose: coherent DMA ring allocation for Ionic RDMA queues. It initializes queue geometry, allocates queue memory, and frees it during teardown.

Important APIs/functions: `ionic_queue_init()` validates requested depth and stride, computes power-of-two depth/stride logs, enforces at least page-sized allocation, sets size and mask, allocates coherent DMA memory, checks page alignment, and initializes producer/consumer/doorbell state. `ionic_queue_destroy()` frees the coherent allocation.

Control flow: callers pass logical usable depth and element stride. The implementation adds one entry to preserve a hole for full/empty detection, rounds depth and stride up with `order_base_2()`, raises depth when necessary so the total queue is at least one page, rejects log values above 16, and allocates `BIT_ULL(depth_log2 + stride_log2)` bytes. The ring mask is `2^depth_log2 - 1`, so actual queue capacity is mask entries.

State and persistence: initialized state is stored in `struct ionic_queue`: size, DMA address, CPU pointer, producer, consumer, mask, depth/stride logs, and doorbell bits. Memory persists until explicit destroy and is visible to the device as coherent DMA.

Dependencies and integration: depends on Linux coherent DMA allocation and helper math. `ionic_queue.h` inline helpers perform all subsequent indexing, producer/consumer movement, and doorbell value construction.

Risks: destroy assumes `q->ptr`/`q->size` are valid from successful init. The requested stride is rounded up to a power of two, so firmware queue stride must be programmed with `stride_log2`, not the original byte stride. Capacity differs from raw allocation depth because one slot is reserved.

Test signals: queue creation for minimum depth, maximum depth/stride rejection, page-sized small queues, DMA allocation failure, and create/destroy of AQ/EQ/CQ/SQ/RQ paths under probe/remove and reset.
