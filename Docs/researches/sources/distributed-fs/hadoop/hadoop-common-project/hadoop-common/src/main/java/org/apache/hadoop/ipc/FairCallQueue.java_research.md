# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/FairCallQueue.java

## Purpose
`FairCallQueue` is Hadoop IPC's multi-priority `BlockingQueue` implementation for server calls. It partitions total capacity across per-priority `LinkedBlockingQueue` instances, uses a `RpcMultiplexer` to select dequeue priority, and exports queue-size and overflow metrics through a per-namespace MBean/metrics source.

## Important APIs, Types, and Functions
Constructors allocate weighted subqueues and install `WeightedRoundRobinMultiplexer`. `add`, `put`, `offer`, `take`, `poll`, `peek`, `drainTo`, `remainingCapacity`, `getQueueSizes`, and `getOverflowedCalls` implement the queue contract. `MetricsProxy` implements `FairCallQueueMXBean` and `MetricsSource`, tracks delegate revisions, and avoids retaining retired queues with a `WeakReference`.

## Control Flow
Enqueue paths read `Schedulable.getPriorityLevel()`. `add` and `put` can overflow into lower-priority queues; `offer` only targets the assigned queue. Successful insertions release a semaphore permit. Consumers acquire a permit before `removeNextElement`, then poll the multiplexer-selected queue and scan all queues if races left that queue empty. Overflow behavior maps to `CallQueueOverflowException` variants, optionally failover when server failover is enabled.

## State and Persistence Behavior
State is in-memory only: subqueue contents, semaphore permits, overflow counters, multiplexer cursor, and metrics delegate. Correctness depends on keeping semaphore permits synchronized with actual queued elements. Metrics registration is global per namespace and revisions distinguish queue replacement.

## Dependencies and Integration Points
It depends on `Schedulable`, `RpcMultiplexer`, `WeightedRoundRobinMultiplexer`, `CallQueueManager`, Hadoop metrics/MBeans, and server call scheduling. `TestFairCallQueue` covers capacity distribution, queue operations, blocking semantics, overflow counters, MBean, and metrics signals.

## Risks and Test Signals
Risks include semaphore/subqueue skew, starvation if multiplexer behavior changes, priority overflow policy mistakes, and stale metrics delegates. Tests should stress concurrent producers/consumers, `drainTo`, failover-enabled overflow, weighted capacity residue, and replacement of queues under one metrics namespace.
