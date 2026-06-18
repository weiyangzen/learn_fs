# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-io-uring.c

## Purpose

This file provides an optional liburing-backed fast path for `readv`, `writev`, and `fsync` in the POSIX translator. When built with `HAVE_LIBURING` and successfully initialized, `posix_io_uring_on` replaces the translator fop table entries with asynchronous implementations; `posix_io_uring_off` restores the synchronous implementations.

## Important APIs, Types, and Functions

`struct posix_uring_ctx` carries the Gluster call frame, fd reference, backend fd, xdata reference, pre-operation iatt, operation code, fop-specific read/write/fsync arguments, and function pointers for SQE preparation and completion unwind. `posix_io_uring_ctx_init` allocates and initializes this context and captures prebuf for write/fsync. Completion functions are `posix_io_uring_readv_complete`, `posix_io_uring_writev_complete`, and `posix_io_uring_fsync_complete`. SQE preparers are `posix_prep_readv`, `posix_prep_writev`, and `posix_prep_fsync`. Runtime functions include `posix_io_uring_submit`, `posix_io_uring_thread`, `posix_io_uring_init`, `posix_io_uring_drain`, `posix_io_uring_fini`, `posix_io_uring_on`, and `posix_io_uring_off`.

## Control Flow

The on path initializes an io_uring queue with `POSIX_URING_MAX_ENTRIES`, initializes submission/completion mutexes, starts a `posix-iouring` completion thread, then patches `this->fops->readv`, `writev`, and `fsync`.

Each async fop allocates a context, fills operation-specific fields, and submits an SQE under `priv->sq_mutex`. The completion thread waits for CQEs under `priv->cq_mutex`, extracts the context pointer, treats a null context plus exit flag as shutdown, marks the CQE seen, then calls the context's unwind callback. Completion callbacks translate negative CQE results to op_errno, collect post-operation `posix_fdstat`, update counters, fill response xdata for writes, unwind the original frame, and release context resources.

Shutdown sets `uring_thread_exit`, submits a drain NOP with null data, joins the thread, exits the queue, and destroys mutexes. Without liburing, `posix_io_uring_on` logs build-time unavailability and returns `-1`.

## State and Persistence Behavior

Persistent storage effects are the same kernel read/write/fsync operations, but completion ordering and error reporting are mediated by io_uring. In-memory state lives in `struct posix_private`: `ring`, `sq_mutex`, `cq_mutex`, `uring_thread`, `uring_thread_exit`, `io_uring_capable`, and `io_uring_init_done`. Contexts hold fd and xdata references until completion.

## Dependencies and Integration Points

The file depends on `posix.h`, `posix-messages.h`, `posix-io-uring.h`, `posix-handle.h`, liburing, fd contexts, iobuf pools, `posix_fdstat`, `_fill_writev_xdata` from the synchronous implementation, and Gluster stack unwind macros. It mutates the active translator fop table, so it integrates directly with `posix.c` registration and runtime option/reconfigure code.

## Risks

Parity with the synchronous paths is the main risk. The async read/write/fsync paths do not run all synchronous checks visible in `posix-inode-fd-ops.c`, such as disk reserve checks, cloudsync maintenance, internal-write checks, ctime metadata updates, O_DIRECT alignment handling, atomic write locking, and durable xdata handling. `posix_io_uring_submit` fails immediately if no SQE is available and has a TODO to retry. Write contexts store caller iovec pointers without retaining an `iobref`, so lifetime must be guaranteed by the stack above. `posix_io_uring_drain` does not take the SQ mutex. Completion thread aborts on unexpected `io_uring_wait_cqe` errors. Fsync completion increments `write_value` by the fsync result, which is typically zero.

## Test Signals

Test build without liburing, init failure fallback, runtime on/off fop table restoration, read/write/fsync success and error propagation, EOF signaling, xdata append/fd-count response on async writes, fd/xdata/iobuf reference lifetime under delayed completion, queue-full `EAGAIN`, shutdown with in-flight operations, and parity against synchronous behavior for cloudsync, ctime, O_DIRECT, atomic writes, and disk-reserve scenarios.
