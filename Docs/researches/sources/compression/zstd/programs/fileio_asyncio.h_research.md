# sources/compression/zstd/programs/fileio_asyncio.h

## Purpose

This header declares zstd CLI asynchronous file I/O pools. It abstracts read and write buffering behind pool contexts so `fileio` can overlap disk I/O with compression work while retaining a serial worker-thread implementation today.

## Important APIs, Types, and Functions

`IOPoolCtx_t` stores common pool state: thread pool, active flag, job array, current `FILE*`, mutex, available job stack, and job buffer size. `ReadPoolCtx_t` adds EOF/offset tracking, held current job, coalescing buffer, exposed `srcBuffer`, completed job queue, and completion condition variable. `WritePoolCtx_t` adds sparse-write skip accounting. `IOJob_t` carries target context, file, buffer, used byte count, and offset. Public APIs create/free pools, set async mode, set/get/close files, acquire/release/enqueue write jobs, end sparse writes, consume/refill read buffers, and report `AIO_supported()`.

## Control Flow, State, and Persistence

Callers create a read or write pool with a maximum buffer size, set a file, then repeatedly consume read buffers or enqueue filled write jobs. The file pointer belongs to the pool until close/free. Job ownership is explicit: acquired jobs must be released or queued, queued jobs must not be touched, and file switching requires all queued work to finish.

## Dependencies and Integration Points

It depends on zstd common types, `FIO_prefs_t`, `platform.h`, `util.h`, `pool.h`, and `threading.h`. The implementation is consumed by `fileio.c` and exposed indirectly through CLI options such as `--asyncio` and `--no-asyncio`.

## Risks and Test Signals

Main risks are race conditions around job arrays, stale file pointers when switching files, buffer lifetime misuse by consumers retaining `srcBuffer`, and sparse-write finalization ordering. Tests should exercise async on/off paths, stdin/stdout style files, sparse output, close/free while queues are empty, and large inputs that require coalescing.
