# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/fun_queue.h

## Purpose
Declares the shared queue abstraction for Fungible devices, including DMA ring state, doorbells, callback hooks, queue allocation parameters, inline helpers, and queue/IRQ APIs.

## Important APIs, Types, And Functions
Key types are `struct fun_queue`, `struct fun_rq_info`, `struct fun_queue_alloc_req`, and `cq_callback_t`. Inline helpers are `fun_sqe_at()`, `funq_sq_post_tail()`, `funq_cqe_info()`, `funq_rq_post()`, and `fun_set_cq_callback()`. The header also exposes SQ/CQ destroy macros and function prototypes implemented in `fun_queue.c`.

## Control Flow
Callers construct `fun_queue_alloc_req`, allocate with `fun_alloc_queue()`, create device resources with `fun_cq_create()`/`fun_sq_create()`/`fun_create_rq()`, post SQ tails using the helper, process completions through `fun_process_cq()`, and free IRQs/queues during teardown.

## State And Persistence
`struct fun_queue` holds all per-queue live state: DMA addresses, ring pointers, RQ pages, doorbells, IDs, depths, heads/tails, descriptor sizes, RQ buffer cursor, coalescing parameters, flags, writeback pointer, callback, IRQ handler data, vector, phase, and display name.

## Dependencies And Integration Points
Includes Linux interrupt and MMIO helpers and depends on HCI types included indirectly through `fun_dev.h`. Used by funcore admin queue code and funeth data queues.

## Risks
The include guard contains a spelling error (`_FUN_QEUEUE_H`) but is self-consistent. Inline pointer arithmetic assumes byte-addressable `void *` extension supported by kernel C. Doorbell helpers require valid MMIO pointers and correct queue depth wrapping by callers.

## Test Signals
Compile coverage of all consumers, queue allocation parameter validation, SQ tail wrap, CQE info offset correctness, RQ doorbell posting, and callback invocation through processed completions.
