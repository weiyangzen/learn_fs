# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-io-uring.h

## Purpose
Declares the io_uring I/O engine descriptor and its queue/retry/thread sizing constants.

## APIs, Types, and Functions
Defines `GF_IO_URING_QUEUE_SIZE` as `GF_IO_ID_REQ_COUNT`, `GF_IO_URING_QUEUE_MIN` as 4096, `GF_IO_URING_MAX_RETRIES` as 100, and `GF_IO_URING_WORKER_THREADS` as 16. Exports `extern const gf_io_engine_t gf_io_engine_io_uring`.

## Control Flow, State, and Persistence
This header carries no runtime state, but constants constrain io_uring setup and retry loops. The exported engine participates in `gf_io_run()` engine selection and implements the common engine callbacks.

## Dependencies and Integration
Depends on `gf-io.h`. It integrates with kernel io_uring feature probing, I/O request ID sizing, worker pool initialization, and LIBGLUSTERFS message IDs for io_uring failures.

## Risks and Test Signals
Risks include queue sizes unsupported by older kernels, insufficient feature checks, retry loops masking unrecoverable kernel errors, and worker-count tuning mismatches. Test signals include io_uring feature-probe tests, fallback-to-legacy tests, queue-min boundary tests, cancellation tests, and shutdown under pending submissions.
