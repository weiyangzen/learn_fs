# sources/compression/zstd/lib/common/pool.h

## Purpose
`pool.h` declares zstd's internal thread-pool API. It hides the concrete `POOL_ctx_s` layout while exposing creation, shutdown, join, resize, size accounting, and job submission functions for multi-threaded compression code.

## Important APIs, Types, and Functions
The header forward-declares `POOL_ctx`, defines `POOL_function` as `void (*)(void*)`, and declares `POOL_create()`, `POOL_create_advanced()`, `POOL_free()`, `POOL_joinJobs()`, `POOL_resize()`, `POOL_sizeof()`, `POOL_add()`, and `POOL_tryAdd()`. `POOL_create_advanced()` accepts `ZSTD_customMem`, so the header enables `ZSTD_STATIC_LINKING_ONLY` before including `../zstd.h`.

## Control Flow, State, and Persistence
This header owns no runtime state. Its comments define the important behavior: `numThreads` must be at least 1, `queueSize` bounds queued jobs before blocking, `POOL_add()` may execute asynchronously and therefore requires `opaque` to outlive job completion, `POOL_tryAdd()` is immediate, and `POOL_resize()` changes only the thread count.

## Dependencies and Integration Points
It includes `zstd_deps.h` and zstd's static-linking declarations for allocator types. `pool.c` implements the API, while zstd multi-threading code uses it either through `POOL_*` names or the public thread-pool aliases exposed elsewhere.

## Risks and Test Signals
The header-level risk is contract mismatch: callers must not pass stack or transient `opaque` data unless they join before it goes out of scope, and callers must treat `POOL_ctx` as opaque. Build tests should cover both `ZSTD_MULTITHREAD` and non-threaded configurations, custom memory creation, and compile-time compatibility for static-linking consumers.
