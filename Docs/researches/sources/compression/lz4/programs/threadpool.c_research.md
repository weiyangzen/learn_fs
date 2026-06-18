# sources/compression/lz4/programs/threadpool.c

Purpose: implements the `TPool` job queue abstraction with synchronous fallback, Windows completion ports, or POSIX pthreads.

Important APIs/functions: `TPool_create()`, `TPool_free()`, `TPool_submitJob()`, `TPool_jobsCompleted()`. POSIX internals include worker loop, shutdown, queue-full detection, and condition variables; Windows uses completion-port worker threads and semaphore/event synchronization.

Control flow: non-MT builds execute jobs inline. Threaded builds create workers, block submitters when queues are full, execute `job_function(arg)`, and allow callers to wait until queued/running jobs drain before freeing.

State and persistence: pools own threads/handles, queues, mutexes/conditions or Win32 sync objects, plus shutdown/pending counters. Job argument lifetime is caller-managed.

Dependencies/integration: selected by `LZ4IO_MULTITHREAD` from `lz4conf.h`; used by `lz4io.c` for compression/decompression and writer queues.

Risks: type-unsafe Windows argument cast through `LPOVERLAPPED`; no per-job result/cancel mechanism; queue blocking can deadlock if callers violate ownership/lifetime expectations.

Test signals: threaded CLI builds and valgrind/memory tests exercise pool creation, job execution, and cleanup.
