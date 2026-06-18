# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/fun_queue.c

## Purpose
Implements Fungible queue allocation, DMA ring memory management, admin commands for SQ/CQ/RQ creation, CQ processing, receive-buffer queue handling, and IRQ request/free helpers.

## Important APIs, Types, And Functions
Exports include `fun_alloc_ring_mem()`, `fun_free_ring_mem()`, `fun_sq_create()`, `fun_cq_create()`, `fun_alloc_queue()`, `fun_free_queue()`, `fun_create_rq()`, `fun_request_irq()`, `fun_free_irq()`, and `fun_process_cq()`. Internal helpers allocate SQ/CQ/RQ rings, fill RQ pages, gather RQ-buffer responses, and update RQ positions.

## Control Flow
Queue allocation creates a `struct fun_queue`, assigns initial SQ/CQ/RQ IDs, allocates coherent CQ and SQ rings, optionally allocates and fills an RQ ring with mapped pages, initializes phase/tag state, and assigns implicit admin queue doorbells for queue 0. Device-visible SQ/CQ/RQ creation is done later through HCI admin commands. CQ processing walks entries while phase bits match, applies `dma_rmb()`, advances head/phase, optionally gathers response data from RQ buffers, invokes the registered callback, refills consumed RQ entries, and arms the CQ doorbell.

## State And Persistence
Queue state includes coherent DMA ring memory, optional software descriptor rings, page-backed RQ buffers, DMA addresses, doorbell pointers, heads/tails, phase, interrupt coalescing settings, callback data, IRQ handler metadata, and queue IDs. State is live only and freed through `fun_free_queue()`.

## Dependencies And Integration Points
Uses DMA coherent/page mapping APIs, PCI IRQ vectors, Linux IRQ APIs, `fun_dev` doorbell helpers/admin submission, and HCI queue/data-operation formats. `fun_dev.c` uses it for the admin queue; `funeth` uses it for I/O queues.

## Risks
CQ parsing depends on correct phase-bit ordering and descriptor sizes. RQ buffer accounting is subtle: fragmented responses advance buffers and sync DMA in steps. `fun_data_from_rq()` may return NULL after consuming data, converting completion status to ENOMEM. Queue free must unmap all RQ pages. IRQ names are bounded at 24 bytes and may truncate long device names.

## Test Signals
Allocate/free queues with and without RQ, create SQ/CQ/RQ admin resources, process CQ phase wrap, receive CQE-in-RQBUF single and fragmented responses, IRQ request/free, DMA mapping failure injection, and doorbell writes after CQ/RQ processing.
