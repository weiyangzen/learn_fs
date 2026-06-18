# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-io.h

## Purpose
Defines the core asynchronous I/O framework: request ID layout, engine abstraction, global I/O state, worker access, batching/chaining, cancellation, callback dispatch, and async function submission.

## APIs, Types, and Functions
Request IDs combine a 16-bit request index, 8 flag bits, and a counter; macros define masks, `GF_IO_ID_FLAG_CHAIN`, and counter increment. `gf_io_mode_t` selects legacy, io_uring, or threaded mode. Debug builds wrap callbacks and async functions with names/file/line via `GF_IO_CBK()` and `GF_IO_ASYNC()`. Core types include `gf_io_worker_t`, `gf_io_op_t`, `gf_io_request_t`, `gf_io_batch_t`, `gf_io_handlers_t`, `gf_io_engine_t`, and global `gf_io_t`. APIs and inline helpers include `gf_io_run()`, `gf_io_mode()`, `gf_io_worker_get()`, `gf_io_reserve()`, `gf_io_data_wait/read/write()`, `gf_io_get()`, `gf_io_put()`, `gf_io_cbk()`, batch init/add/submit, request chaining, cancel prepare/submit, callback prepare/submit, and async prepare/submit.

## Control Flow, State, and Persistence
`gf_io_run()` initializes the selected engine and blocks until process termination. Submission reserves sequence numbers, waits for free operation slots, fills `gf_io.op_pool`, and calls an engine operation. Completion invokes callbacks and returns slots to `op_map`. Batches submit multiple requests, optionally chaining them sequentially.

## Dependencies and Integration
Depends on urcu atomics/barriers, `gf-io-common.h`, `syscall.h`, pthreads, and engine descriptors. It underpins newer async infrastructure and integrates with logging through slow-callback/debug metadata.

## Risks and Test Signals
Risks include request-ID wrap/reuse races, memory-ordering bugs in `op_map`, callback use-after-free, chain/batch misuse, cancellation races, and global shutdown handling. Test signals include high-concurrency slot reuse tests, debug abort coverage for malformed batches, cancellation tests, callback latency logs, and engine parity tests.
