# sources/compression/lz4/programs/threadpool.h

Purpose: declares the portable `TPool` interface for LZ4 program worker jobs.

Important APIs/types: opaque `TPool`, `TPool_create(int nbThreads, int queueSize)`, `TPool_free()`, `TPool_submitJob()`, and `TPool_jobsCompleted()`.

Control flow/state contract: submit may block on full queues; completion waits for queued/running work; free waits before releasing resources. In no-thread builds the same API executes synchronously.

Dependencies/integration: implemented by `threadpool.c`; used primarily by `lz4io.c`; C++ compatible through `extern "C"`.

Risks: no cancellation or job status; caller must preserve or transfer job argument lifetime.

Test signals: indirectly covered by multithread-enabled compression/decompression tests.
