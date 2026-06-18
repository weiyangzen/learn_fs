# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestCallQueueManager.java

## Purpose
`TestCallQueueManager` validates queue capacity, scheduler compatibility, queue swapping under contention, fair-call-queue capacity weights, constructor error propagation, overflow exception semantics, and failover-on-overflow configuration.

## Important APIs, Types, and Functions
The test defines `FakeCall implements Schedulable`, `Putter`, and `Taker`. It uses `CallQueueManager`, `LinkedBlockingQueue`, `FairCallQueue`, `DefaultRpcScheduler`, `DecayRpcScheduler`, `RpcScheduler`, `CallQueueOverflowException`, and `Server.getSchedulerClass()`. Helpers `assertCanPut()` and `assertCanTake()` test bounded queue behavior.

## Control Flow
Basic tests construct managers with different queue/scheduler classes and assert capacity or empty-consume behavior. Compatibility tests ensure selecting `FairCallQueue` without an explicit scheduler defaults to `DecayRpcScheduler`, and that `DecayRpcScheduler` also works with `LinkedBlockingQueue`. `testSwapUnderContention()` runs 1000 producers and 100 consumers while swapping queues five times, then verifies no calls were dropped. Overflow tests use Mockito to verify backoff, add/put paths, and failover-triggering exceptions.

## State and Persistence
State is entirely in in-memory queues, fake call priority levels, producer/consumer counters, and manager flags. No persistent state is used.

## Dependencies and Integration Points
The suite integrates server IPC configuration keys, scheduler and queue reflection conversion helpers, UGI on schedulable calls, fair queue capacity weights, and client backoff/failover signaling used by RPC servers.

## Risks and Edge Cases
The contention test is timing-heavy and starts many threads. Capacity assertions use short joins and interrupts to infer blocking behavior. Overflow tests rely on exact Mockito interactions with `put()` versus `add()`.

## Test Signals
Signals include exact number of accepted puts/takes under capacity, correct default scheduler selection, no lost calls across queue swaps, expected priority dequeue order under capacity weights, constructor exceptions preserving causes, overflow exception class selection, and namespace/global failover config flags.
