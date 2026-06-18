# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcMultiplexer.java

## Purpose
`RpcMultiplexer` is the strategy interface used by `FairCallQueue` to choose which priority queue should be polled next.

## Important APIs, Types, and Functions
`getAndAdvanceCurrentIndex()` returns the current queue index and advances any internal schedule.

## Control Flow
`FairCallQueue.removeNextElement` calls this method after acquiring a semaphore permit, then falls back to scanning all queues if the chosen queue is empty.

## State and Persistence Behavior
The interface has no state. Implementations such as weighted round-robin maintain in-memory cursor/weight state.

## Dependencies and Integration Points
It integrates with priority-level queues and scheduler decisions in Hadoop IPC.

## Risks and Test Signals
Risks include returning out-of-range indexes or starving lower/higher priorities. Tests should plug deterministic multiplexers into `FairCallQueue` and verify dequeue distribution.
