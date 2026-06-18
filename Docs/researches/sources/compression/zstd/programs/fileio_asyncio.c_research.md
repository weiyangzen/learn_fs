# sources/compression/zstd/programs/fileio_asyncio.c

## Purpose
`fileio_asyncio.c` implements the asynchronous read/write pool abstraction used by file decompression paths. The current backend uses one worker thread per pool when multithreading is available, while retaining the same API for synchronous fallback and future OS-specific async implementations.

## Important APIs, types, and functions
The public functions are `AIO_supported()`, write-pool lifecycle and operations (`AIO_WritePool_create()`, `AIO_WritePool_free()`, `AIO_WritePool_setFile()`, `AIO_WritePool_getFile()`, `AIO_WritePool_acquireJob()`, `AIO_WritePool_enqueueAndReacquireWriteJob()`, `AIO_WritePool_releaseIoJob()`, `AIO_WritePool_sparseWriteEnd()`, `AIO_WritePool_closeFile()`, `AIO_WritePool_setAsync()`), and read-pool lifecycle and operations (`AIO_ReadPool_create()`, `AIO_ReadPool_free()`, `AIO_ReadPool_setFile()`, `AIO_ReadPool_getFile()`, `AIO_ReadPool_fillBuffer()`, `AIO_ReadPool_consumeBytes()`, `AIO_ReadPool_consumeAndRefill()`, `AIO_ReadPool_closeFile()`, `AIO_ReadPool_setAsync()`).

The generic internal layer is built around `IOPoolCtx_t` and `IOJob_t`. `AIO_IOPool_init()` creates jobs and optional thread pool, `AIO_IOPool_acquireJob()` and `AIO_IOPool_releaseIoJob()` manage the free-list, `AIO_IOPool_enqueueJob()` either submits to `POOL_add()` or runs synchronously, and `AIO_IOPool_setFile()` gates file changes on all jobs being completed.

## Control flow
Write jobs are acquired, filled by caller code, and enqueued. `AIO_WritePool_executeWriteJob()` writes through `AIO_fwriteSparse()`, updates `storedSkips`, and releases the job. Sparse writes accumulate zero-run skips and finalize the last zero byte in `AIO_fwriteSparseEnd()`.

Read pools enqueue reads immediately when a file is set. Each read job records an offset. Completed reads are appended to a completed-job list, and `AIO_ReadPool_getNextCompletedJob()` waits for the job matching `waitingOnOffset`, preserving logical input order even if a future backend completes out of order. `AIO_ReadPool_fillBuffer()` exposes either a job buffer directly or coalesces leftover bytes plus the next job into a separate buffer when the caller needs a contiguous minimum.

## State and persistence behavior
Persistent effects are limited to reading from and writing to the currently configured `FILE*`, closing files through close helpers, and sparse seek/write behavior. Runtime state includes available job stacks, completed read jobs, thread-pool active flag, mutex/condition variables, current held read job, read offsets, EOF flag, coalesced buffer, source buffer pointer/length, and write sparse skip count. File changes require all jobs to be joined and all acquired jobs released.

## Dependencies and integration points
The file depends on `fileio_asyncio.h`, `fileio_common.h` for display/error macros and sparse seek helpers, `platform.h`, zstd threading and pool abstractions, and `FIO_prefs_t` options such as `asyncIO`, `testMode`, and `sparseFileSupport`. `fileio.c` uses write pools and read pools in decompression and pass-through paths.

## Risks and edge cases
Threaded mode depends on `ZSTD_MULTITHREAD`; otherwise `AIO_supported()` is false and work runs synchronously. `ctx->storedSkips` is updated by write jobs and therefore relies on serialized execution; changing the pool to multiple write workers would need stronger ordering. Several invariants are asserted rather than recovered, such as available job counts and file state. Read completion scans a small fixed array, which is fine for `MAX_IO_JOBS` but should stay bounded. `AIO_WritePool_closeFile()` assumes a real file unless test mode is active; callers must not close stdout unexpectedly outside intended paths.

## Test signals
Tests should cover sync and async modes, switching async on/off after jobs have drained, ordered reads with multiple in-flight jobs, partial-buffer coalescing, EOF handling, read errors, sparse write zero-run finalization, test mode no-output behavior, small and large file decompression through `fileio.c`, and cleanup assertions that all jobs return before pool destruction.
