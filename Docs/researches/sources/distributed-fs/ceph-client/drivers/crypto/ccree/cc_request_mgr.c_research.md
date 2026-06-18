# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_request_mgr.c

## Purpose

`cc_request_mgr.c` is the central descriptor submission and completion engine for the ccree driver. It maintains a software FIFO matching hardware completions, writes six-word descriptors into the hardware queue, handles synchronous initialization requests, manages a backlog for async requests when the hardware queue is full, and releases runtime PM references when requests complete.

## Important APIs, Types, And Functions

`struct cc_req_mgr_handle` stores hardware queue capacity, free-slot accounting, software request ring, completion counters, locks, dummy completion descriptor, optional workqueue/tasklet, and backlog list. `struct cc_bl_item` stores a deferred request and copied descriptor sequence. Public APIs are `cc_req_mgr_init()`, `cc_req_mgr_fini()`, `cc_send_request()`, `cc_send_sync_request()`, `send_request_init()`, and `complete_request()`.

Important internals include `enqueue_seq()`, `cc_queues_status()`, `cc_do_send_request()`, `cc_enqueue_backlog()`, `cc_proc_backlog()`, `proc_completions()`, `cc_axi_comp_count()`, and `comp_handler()`. `cc_cpp_int_mask()` maps CPP algorithm/slot completion status to abort interrupt masks using `array_index_nospec()`.

## Control Flow

Initialization allocates the manager, initializes locks and backlog, sets up a tasklet or workqueue, reads hardware queue size, validates it, allocates a coherent dummy completion word, and builds a completion descriptor. Async submission calls `cc_pm_get()`, takes the hardware lock, checks software and hardware capacity, optionally copies the request into the backlog and returns `-EBUSY`, or writes descriptors and returns `-EINPROGRESS`. Backlogged requests are retried from the completion tasklet after space becomes available.

Synchronous submission sets a completion callback, holds runtime PM, waits until enough room exists for the request plus dummy completion descriptor, enqueues both, and blocks until the dummy completion completes. `send_request_init()` is the early/init path: it polls for room, marks the last supplied descriptor as queue-last, writes the sequence, and refreshes free-slot accounting.

Interrupt handling starts in `complete_request()`, which completes hardware-queue waiters and schedules the bottom half. `comp_handler()` clears/masks completion interrupts, samples AXI completion counts, calls `proc_completions()` until drained, unmasks completion interrupts, then processes backlog. `proc_completions()` dequeues software requests, derives CPP error status if relevant, invokes user callbacks, advances the ring tail, and drops runtime PM references.

## State And Persistence Behavior

The manager owns volatile in-kernel state only: software FIFO head/tail, backlog list, free-slot estimates, and AXI completion counts. Hardware queue contents and AXI monitor counters are MMIO state. There is no persistence across driver remove or reboot; `cc_req_mgr_fini()` tears down tasklet/workqueue and coherent memory.

## Dependencies And Integration Points

The file depends on `cc_driver` register helpers and global IRQ state, `cc_hw_queue_defs.h` descriptors, `cc_pm` runtime PM wrappers, the crypto async request backlog contract, and callbacks supplied by hash/cipher/AEAD modules through `struct cc_crypto_req`. The platform IRQ handler in `cc_driver.c` calls `complete_request()`.

## Risks And Edge Cases

Software FIFO size must remain a power of two because head/tail wrap uses `MAX_REQUEST_QUEUE_SIZE - 1`. A completion count without a queued request indicates serious desynchronization and is logged. Backlog descriptors are copied into a fixed `CC_MAX_DESC_SEQ_LEN` array; callers must not submit longer sequences. PM references must be released exactly once per accepted request, including CPP error completions. `cc_send_sync_request()` waits interruptibly for queue space but does not propagate interruption from that wait.

## Test Signals

High-concurrency crypto stress should exercise queue-full and backlog paths without dropped requests. `CRYPTO_TFM_REQ_MAY_BACKLOG` callers should receive `-EBUSY` then `-EINPROGRESS` notification. Runtime PM counters should remain balanced. Forced CPP aborts should surface as request errors. Descriptor queue mismatch and empty-queue completion logs indicate bugs.
