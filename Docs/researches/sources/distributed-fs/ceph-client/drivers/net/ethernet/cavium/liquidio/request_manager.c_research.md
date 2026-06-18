# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/request_manager.c

Purpose: Implements LiquidIO instruction queue lifecycle, command posting, descriptor reclaim, doorbell timeout handling, and soft-command buffer pool management.

Important APIs, types, and functions: `octeon_setup_iq()` and `octeon_init_instr_queue()` allocate queue objects, coherent DMA rings, request lists, locks, queue masks, chip register setup, and per-IQ delayed doorbell-check workqueues. `octeon_send_command()` posts one descriptor through `__post_command2()`, records request cleanup metadata, updates stats/BQL, and rings the doorbell when thresholds or force conditions require it. `octeon_flush_iq()` updates Octeon read index, processes fetched requests, decrements pending instructions, and honors NAPI budget. `lio_process_iq_request_list()` frees no-response network buffers or moves response-bearing soft commands to `OCTEON_ORDERED_SC_LIST`. Soft-command APIs allocate fixed 2048-byte coherent buffers, align context/data/response regions, prepare chip-specific control instructions, send them, and return buffers to pool/done/zombie lists.

Control flow: TX/control producers post commands to IQs; hardware fetches descriptors; interrupts, NAPI, or delayed work call flush; request-list entries are freed or enqueued for ordered response polling. Doorbell timeout work periodically flushes stale queues and reenables IRQs.

State and persistence: State includes DMA rings, request lists, queue indexes, pending atomics, stats, workqueues, global reqtype cleanup callbacks, and soft-command pool/done/zombie lists. All are volatile.

Dependencies and integration: Uses chip config for instruction size/db thresholds, `fn_list` queue operations, BQL helpers, response-manager lists, and netdev buffer cleanup callbacks.

Risks: Queue wrap protection leaves one slot free; bugs around pending counts, flush indexes, or barriers can corrupt the ring. The global `reqtype_free_fn` table must be registered before reclaim. Soft-command pool exhaustion returns NULL; zombie cleanup handles late firmware writes.

Test signals: IQ allocation failure unwind, descriptor full/stop behavior, doorbell batching/timeout, concurrent flush exclusion, NAPI budget partial reclaim, soft-command pool exhaustion, response vs no-response cleanup, and shutdown drain.
