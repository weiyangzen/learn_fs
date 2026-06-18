# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestSinkQueue.java

## Purpose

`TestSinkQueue` validates the half-blocking queue used by metrics sinks. It covers enqueue/dequeue behavior, blocking on empty queues, dropping on full queues, consume-all, exception consistency, clearing, hanging consumers, and illegal concurrent consumers.

## Important APIs, Types, And Functions

The file uses `SinkQueue<T>`, `enqueue()`, `dequeue()`, `consume()`, `consumeAll()`, `front()`, `back()`, `size()`, `capacity()`, `clear()`, `SinkQueue.Consumer`, and test helper `newSleepingConsumerQueue()`.

## Control Flow

Basic tests enqueue and consume integers while checking front/back/size. Empty tests start a consumer thread blocked in `dequeue()` and `consume()` then enqueue values to release it. Full tests assert nonblocking drops when capacity is exceeded. `testConsumerException()` ensures a thrown consumer exception leaves the queue consistent. Hanging-consumer tests run a daemon consumer that sleeps for a long time, then assert producers do not block and queue state is preserved. Concurrent consumer tests assert `ConcurrentModificationException` for clear, consume, consumeAll, and dequeue while another consumer is active.

## State And Persistence Behavior

State is in-memory queue contents, active-consumer tracking, and test threads/latches. There is no persistence. Sleeping consumer threads are daemon threads to avoid blocking JVM exit.

## Dependencies And Integration Points

It integrates with the metrics sink queue implementation and `SubjectInheritingThread`. Metrics system sink adapters depend on these semantics for nonblocking publication and safe backpressure.

## Risks And Test Signals

Risks include producer blocking under full queues, corrupted queue state after consumer exceptions, deadlocks on empty queues, and concurrent consumers violating invariants. Signals are exact queue contents/size/front/back assertions, mock callback counts, dropped enqueue false returns, and expected `ConcurrentModificationException`s.
