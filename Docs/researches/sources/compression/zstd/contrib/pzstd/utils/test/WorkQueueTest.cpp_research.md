<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/WorkQueueTest.cpp -->
# sources/compression/zstd/contrib/pzstd/utils/test/WorkQueueTest.cpp

## Purpose
This test suite validates the blocking queue behavior that underpins pzstd's thread pipeline.

## Important APIs, Types, And Functions
It defines helper worker structs and tests `WorkQueue::push`, `pop`, `finish`, `setMaxSize`, bounded queues, failed push after finish, and `BufferWorkQueue::size`.

## Control Flow
Tests run single-threaded queue operations, producer/consumer patterns with one or many threads, bounded backpressure scenarios, and size accounting that waits for finish.

## State And Persistence
State is local queues, threads, vectors, atomics, and buffers. No persistence exists.

## Dependencies And Integration Points
It depends on GoogleTest, `WorkQueue.h`, `Buffer.h`, and C++ threading. It directly protects `Pzstd.cpp` queue semantics.

## Risks
Some tests use sleeps to force scheduling, which can be timing-sensitive.

## Test Signals
Passing tests provide strong confidence for queue synchronization, finish wakeups, and pzstd writer size accounting.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/WorkQueueTest.cpp -->
