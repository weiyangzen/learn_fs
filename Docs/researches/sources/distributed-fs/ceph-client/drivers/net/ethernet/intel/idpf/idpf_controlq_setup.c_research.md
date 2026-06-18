# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_controlq_setup.c

## Purpose
This file owns DMA memory allocation and deallocation for IDPF control queue descriptor rings and receive buffers. It is separated from queue operation logic so lifecycle code can request or release resources through `idpf_ctlq_alloc_ring_res()` and `idpf_ctlq_dealloc_ring_res()`.

## Important APIs, Types, And Functions
Public functions are `idpf_ctlq_alloc_ring_res()` and `idpf_ctlq_dealloc_ring_res()`. Internal helpers allocate and free descriptor rings (`idpf_ctlq_alloc_desc_ring()`, `idpf_ctlq_free_desc_ring()`) and buffer arrays (`idpf_ctlq_alloc_bufs()`, `idpf_ctlq_free_bufs()`). The code uses `idpf_alloc_dma_mem()` and `idpf_free_dma_mem()` for DMA-visible memory and `kzalloc_objs()` for pointer/header arrays.

## Control Flow
Allocation first creates the descriptor ring sized as `ring_size * sizeof(struct idpf_ctlq_desc)`. It then allocates queue buffers. TX queues do not allocate DMA payload buffers here. RX queues allocate an array of `struct idpf_dma_mem *` and allocate mapped buffers for all but the last ring slot, matching the one-empty-slot ring convention. On failure, allocation unwinds previously allocated RX buffers and descriptor memory. Deallocation frees RX DMA buffers if present, frees the RX or TX backing array, then frees the descriptor ring.

## State And Persistence
Allocated state is stored in `cq->desc_ring` and `cq->bi.rx_buff` or `cq->bi.tx_msg`. RX buffers remain associated with descriptors until receive transfers them to upper layers or repost returns them. TX payload buffers are explicitly not owned by this file.

## Dependencies And Integration Points
This file depends on `idpf_controlq.h` for queue state and descriptor sizing. It is called from `idpf_ctlq_add()` during queue creation and `idpf_ctlq_shutdown()` during queue removal. The DMA helpers are platform/driver allocation wrappers.

## Risks
The ownership distinction between RX buffers and TX buffers is important. Freeing TX DMA payloads here would double-free upper-layer memory, while failing to free RX buffers leaks DMA memory. The "all but last" RX allocation must stay consistent with ring-full accounting. `idpf_ctlq_dealloc_ring_res()` assumes buffers were initialized enough for the selected queue type; callers must avoid deallocating uninitialized queue structs.

## Test Signals
Fault-injection tests should cover descriptor allocation failure, RX pointer array allocation failure, RX buffer header failure, DMA buffer failure after partial allocation, TX queue allocation with no RX buffers, and deallocation after partially and fully initialized queues. DMA leak detection and KASAN/KFENCE are useful signals.
