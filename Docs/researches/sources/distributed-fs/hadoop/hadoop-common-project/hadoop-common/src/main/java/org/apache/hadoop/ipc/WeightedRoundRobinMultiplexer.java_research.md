<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/WeightedRoundRobinMultiplexer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/WeightedRoundRobinMultiplexer.java

## Purpose
`WeightedRoundRobinMultiplexer` selects the next FairCallQueue priority queue to poll, giving high-priority queues more turns while still periodically serving lower-priority queues.

## Important APIs, Types, And Functions
- Config key `faircallqueue.multiplexer.weights`, used under the supplied namespace.
- Constructor validates positive queue count, loads configured weights, or builds defaults.
- `getAndAdvanceCurrentIndex()` returns the current queue index then decrements the remaining quota.
- Default weights are powers of two, with the highest-priority index receiving the largest weight and the last queue receiving one.

## Control Flow
The multiplexer starts at queue 0 with its weight as `requestsLeft`. Each call returns `currentQueueIndex`, decrements `requestsLeft`, and when it reaches exactly zero advances to the next queue modulo `numQueues` and resets the quota to that queue's weight. Atomic fields allow concurrent callers without coarse locking; races may produce extra reads from a queue, which the class documents as acceptable.

## State And Persistence
State is in-memory only: `currentQueueIndex`, `requestsLeft`, `queueWeights`, and `numQueues`.

## Dependencies And Integration Points
Implements `RpcMultiplexer` for FairCallQueue-like scheduling. Depends on Hadoop `Configuration` and namespace conventions shared with IPC scheduler configuration.

## Risks And Edge Cases
Configured weights must match the queue count exactly; zero or negative weights are not explicitly rejected and would cause strange advancement behavior. Atomic races can overdraw a queue quota by design. Default weight doubling can overflow for very large queue counts, though practical queue counts are small.

## Test Signals
Tests should verify constructor validation, configured/default weight order, cycle distribution, concurrent access tolerance, and invalid weight-count failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/WeightedRoundRobinMultiplexer.java -->
