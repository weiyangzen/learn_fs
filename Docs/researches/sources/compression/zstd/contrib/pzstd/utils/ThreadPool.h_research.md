<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/ThreadPool.h -->
# sources/compression/zstd/contrib/pzstd/utils/ThreadPool.h

## Purpose
`ThreadPool.h` implements pzstd's simple FIFO worker pool.

## Important APIs, Types, And Functions
`ThreadPool` owns a vector of worker threads and a `WorkQueue<std::function<void()>>`. It exposes a constructor, destructor, and `add`.

## Control Flow
The constructor starts N threads that repeatedly pop tasks and execute them. The destructor finishes the task queue and joins all threads. `add` pushes a copyable `std::function`.

## State And Persistence
State is thread objects and the task queue. There is no persisted state.

## Dependencies And Integration Points
`Pzstd.cpp` uses one pool for compression/decompression workers and a one-thread pool for reader tasks. Tests cover ordering and destruction behavior.

## Risks
Queued lambdas cannot capture move-only objects directly because tasks are `std::function`. Exceptions escaping tasks would terminate the process.

## Test Signals
`ThreadPoolTest.cpp` validates FIFO-ish completion assumptions, job draining before destruction, and adding work during joining.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/ThreadPool.h -->
