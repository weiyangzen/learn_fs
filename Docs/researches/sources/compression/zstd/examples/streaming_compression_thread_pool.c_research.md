# sources/compression/zstd/examples/streaming_compression_thread_pool.c

Purpose: demonstrates parallel file compression using pthreads and, when static-only zstd APIs are available, a shared `ZSTD_threadPool` attached to each compression context.

Important types/functions/APIs: `compress_args_t`, `compressFile_orDie`, `createOutFilename_orDie`, `main`, `pthread_create`, `pthread_join`, `ZSTD_createThreadPool`, `ZSTD_CCtx_refThreadPool`, `ZSTD_c_nbWorkers`, and streaming compression APIs.

Control flow: CLI expects `POOL_SIZE LEVEL FILES`. In static-linking builds it creates one shared thread pool; otherwise each zstd context uses its own pool. It allocates arrays of pthreads and args, starts one OS thread per input file, each thread creates its own CCtx and file buffers, optionally references the shared zstd pool, sets compression level/checksum/16 workers, streams input to `<file>.zst`, frees per-thread output name, and returns. Main joins all threads and frees the pool.

State and persistence: per-thread state is isolated except the optional shared zstd thread pool. Persistent outputs are `.zst` files. Args/thread arrays are process-local.

Dependencies/integration: pthreads, public zstd streaming API, static-only thread-pool API behind `ZSTD_STATIC_LINKING_ONLY`, and `common.h`. It is not included in the examples Makefile `all` target in this source snapshot.

Risks: pthread creation return values are not checked. Thread count equals input file count and can oversubscribe. Each compression context also requests 16 workers, so total concurrency can be very high. Output names are freed in worker threads; args arrays are freed only by process exit. Shared-pool behavior depends on static API availability.

Test signals: build with `-pthread` and static-only APIs, compress several files with a small pool size, verify outputs, run under TSAN/ASan, and test pthread creation failures or very large file lists.
