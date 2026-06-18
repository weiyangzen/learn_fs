# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestValueQueue.java

## Purpose
`TestValueQueue` verifies queue warmup, low-watermark refill, synchronous generation policies, drain behavior, and partial warmup failures for KMS encrypted-key prefetch queues.

## Important APIs, Types, and Functions
It exercises `ValueQueue<T>`, `QueueRefiller<T>`, `SyncGenerationPolicy.ALL`, `ATLEAST_ONE`, and `LOW_WATERMARK`, plus `initializeQueuesForKeys`, `getNext`, `getAtMost`, `getSize`, `drain`, and `shutdown`. `MockFiller` records fill requests in a `LinkedBlockingQueue<FillInfo>` and appends `"test"` values.

## Control Flow
Initial and warmup tests verify first-fill sizes based on queue capacity and low-watermark percentage. Refill tests consume values, wait for asynchronous refill using `GenericTestUtils.waitFor`, and verify exact filler counts. Policy tests drain queues and check how many values are synchronously generated before asynchronous refill starts. Partial warmup uses reflection and a spy `LoadingCache` to force one key lookup to fail, then asserts an `IOException` and only partial fill calls.

## State and Persistence
State is in-memory queues, cache entries, background refill tasks, and recorded fill calls. Tests call `shutdown()` to stop queue workers.

## Dependencies and Integration Points
Dependencies include `ValueQueue`, Guava `LoadingCache` via Hadoop thirdparty shading, Apache Commons `FieldUtils`, Mockito spies, `GenericTestUtils.waitFor`, concurrency utilities, and JUnit timeouts.

## Risks and Edge Cases
The suite is concurrency- and timing-sensitive. It guards low-watermark math, no-refill conditions above the watermark, asynchronous refill after synchronous calls, drained queue behavior, partial warmup failure propagation, and worker shutdown.

## Test Signals
Passing tests signal correct initial fill counts, multi-key warmup, partial-failure handling, async refill thresholds, no unnecessary refill, `getAtMost` policy semantics, and drain suppression of refill.
