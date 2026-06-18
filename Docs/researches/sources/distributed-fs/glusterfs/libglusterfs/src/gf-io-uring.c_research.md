# sources/distributed-fs/glusterfs/libglusterfs/src/gf-io-uring.c

## Purpose
`gf-io-uring.c` implements the Linux `io_uring` backend for GlusterFS' I/O framework. It uses direct `io_uring_setup`, `io_uring_enter`, and `io_uring_register` syscalls, maps submission/completion rings, dispatches callbacks through CQEs, and supports asynchronous cancellation and callback NOP requests.

## Important APIs, Types, and Functions
- `gf_io_engine_io_uring`: exported `gf_io_engine_t` named `io_uring`.
- `gf_io_uring_setup()`, `gf_io_uring_cleanup()`: create, validate, map, probe, and destroy the ring.
- `gf_io_uring_sq_init()`, `gf_io_uring_cq_init()`, corresponding fini functions: manage ring memory mappings.
- `gf_io_uring_enter()`, `gf_io_uring_dispatch()`, `gf_io_uring_dispatch_no_process()`: submit SQEs and optionally wait/process completions.
- `gf_io_uring_cq_process()`, `gf_io_uring_cq_process_some()`: consume CQEs with atomic head updates and invoke `gf_io_cbk()`.
- `gf_io_uring_sq_commit()`, `gf_io_uring_sq_flush()`: use SQE padding to mark committed batches and advance the SQ tail.
- `gf_io_uring_cancel()`, `gf_io_uring_callback()`: build cancellation and NOP SQEs.

## Control Flow
Setup calls `io_uring_setup()` with `IORING_SETUP_CLAMP`, logs parameters, verifies required features `IORING_FEAT_NODROP` and `IORING_FEAT_SUBMIT_STABLE`, ensures at least `GF_IO_URING_QUEUE_MIN` SQ entries, maps SQ/CQ structures, runs `IORING_REGISTER_PROBE`, preinitializes the SQ array, clears SQEs, and returns `GF_IO_URING_WORKER_THREADS`.

Submit-side logic obtains an SQE for a sequence slot, waiting/flushing if the ring is full. `gf_io_uring_common()` writes `user_data`, clears padding, and commits the batch when the id is not chained. Flush consumes committed batch lengths from SQE padding, updates SQ tail with memory barriers, calls `io_uring_enter()`, and processes CQEs when the kernel accepted fewer requests than submitted. Worker loops process one CQE if available, then dispatch with wait enabled if no completion was immediately available.

## State and Persistence
All state is runtime-only: static `gf_io_uring` stores mapped SQ/CQ pointers, masks, entry counts, params, and ring fd. SQE padding is repurposed as intra-process pending batch metadata, so compatibility with kernel struct layout is crucial.

## Dependencies and Integration Points
Depends on Linux syscall numbers, `<linux/io_uring.h>` through `compat-io_uring.h`, URCU atomics/memory barriers, poll, Gluster event dispatch for non-I/O-framework events, and the common `gf_io` request/callback pool. It is selected by `gf-io.c` when compiled with `HAVE_IO_URING` and when setup succeeds.

## Risks and Edge Cases
- Unsupported kernels or missing features cause setup failure and fallback to legacy at the caller.
- Unexpected `io_uring_enter()` errors other than `EAGAIN`, `EBUSY`, or `ENOMEM` abort the process because request stream recovery is considered unsafe.
- The implementation relies on `__pad2` in `struct io_uring_sqe` for private batch counts.
- CQ head is advanced by compare/exchange across workers; memory-ordering mistakes can drop or duplicate completions.
- `IORING_SETUP_SQPOLL` is noted as currently impractical without fd registration.

## Test Signals
Test setup fallback on unsupported kernels, feature validation, SQ/CQ mmap failure cleanup, SQ commit/flush batching, chained request behavior, CQ processing under multiple workers, cancel for timer vs normal ids, and stress tests for partial submission and full-ring backpressure.
