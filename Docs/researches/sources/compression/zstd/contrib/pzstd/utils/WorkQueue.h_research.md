<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/WorkQueue.h -->
# sources/compression/zstd/contrib/pzstd/utils/WorkQueue.h

## Purpose
`WorkQueue.h` provides the blocking producer/consumer queues used to connect pzstd reader, worker, and writer threads.

## Important APIs, Types, And Functions
Template `WorkQueue<T>` exposes `push`, `pop`, `setMaxSize`, `finish`, and `waitUntilFinished`. `BufferWorkQueue` wraps `WorkQueue<Buffer>` and tracks total queued bytes atomically.

## Control Flow
`push` blocks when a bounded queue is full unless finished; `pop` blocks until data or finish; `finish` wakes all readers/writers. `BufferWorkQueue::size` waits until finish so compressed frame size is final before the writer emits the pzstd header.

## State And Persistence
State is queue contents, condition variables, done flag, max size, and byte count. No persistence exists.

## Dependencies And Integration Points
This is core to `Pzstd.cpp` ordering/backpressure. Thread pool tasks also use `WorkQueue<std::function<void()>>`.

## Risks
Incorrect finish ordering can deadlock producers or readers. `BufferWorkQueue::push` increments size before checking push success, so callers rely on normal non-finished use.

## Test Signals
`WorkQueueTest.cpp` covers single-threaded, SPSC, SPMC, MPMC, bounded queues, failed push, setMaxSize, and byte-size tracking.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/WorkQueue.h -->
