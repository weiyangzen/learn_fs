# sources/distributed-fs/ceph-client/drivers/misc/mei/client.c

## Purpose
`client.c` is the core MEI host-client and firmware-client state machine. It manages firmware client references, host client IDs, callback queues, connect/disconnect handshakes, flow-control credits, virtual tags, read/write fragmentation, notifications, forced disconnects, and per-client DMA map/unmap.

## Important APIs, Types, and Functions
Important groups are `mei_me_cl_*()` firmware-client reference/list helpers; `mei_cl_allocate/link/unlink/connect/disconnect`; callback allocation/free/queue helpers; `mei_cl_read_start()`, `mei_cl_write()`, `mei_cl_irq_write()`, `mei_cl_complete()`, notification helpers, and `mei_cl_dma_alloc_and_map()/mei_cl_dma_unmap()`. It works with `struct mei_cl`, `struct mei_me_client`, `struct mei_cl_cb`, and `struct mei_cl_vtag`.

## Control Flow
Firmware clients are discovered elsewhere and stored under `me_clients_rwsem` with krefs. Host clients link by allocating a host ID bit and entering `file_list`. Connect queues or sends an HBM connect request, waits for state transition, and sets disconnected on failure. Reads enqueue flow-control requests and completed callbacks. Writes build MEI headers, optional vtag/GSC extended headers, choose host-buffer or DMA-ring transfer, fragment as needed, consume TX credits, and queue for completion. Completion wakes waiters or schedules bus callbacks.

## State and Persistence
State includes client file state, writing state, status, host/me IDs, firmware client krefs/connect counts, RX/TX flow-control credits, vtag maps and pending-read flags, DMA mapping metadata, waitqueues, and queued callbacks. No disk persistence.

## Dependencies and Integration Points
Depends on HBM helpers, interrupt processing, DMA ring helpers, runtime PM, waitqueues, fasync notification, and MEI bus APIs. It is used by both `/dev/mei` file operations and MEI bus client drivers.

## Risks
This file is concurrency critical. Risks include callback double-free/leaks, stale firmware client refs, host ID leaks, flow-control credit imbalance, timeout recovery, incorrect vtag-to-file routing, runtime PM imbalance, and DMA buffer ID conflicts. The message-fragment and DMA-ring paths must preserve header lengths and completion semantics.

## Test Signals
Signals include connect/disconnect success and timeout handling, forced disconnect on reset, host-client ID exhaustion handling, TX queue limit waiting, MTU enforcement, read flow-control behavior, vtag routing, notification start/stop/events, large writes via fragmentation and DMA ring, client DMA map/unmap, and clean queue flushing on close/reset.
