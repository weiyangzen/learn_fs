# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/AsyncBlockRemoverTest.java

## Purpose
`AsyncBlockRemoverTest` verifies that asynchronous block removal drains queued blocks both when worker removal succeeds and when it throws.

## Important APIs, Types, and Functions
`blockRemove()` mocks `BlockWorker.removeBlock` to record block IDs and returns normally. `failedBlockRemove()` records block IDs and throws `IOException`. Both create `AsyncBlockRemover` with concurrency 10, enqueue 100 blocks, wait until all were attempted, and assert the queue is empty.

## Control Flow, State, and Persistence
State is an in-memory blocking queue and concurrent set of attempted removals. The test confirms removal attempts are not left queued after errors.

## Dependencies and Integration Points
It depends on Mockito, `CommonUtils.waitFor`, `WaitForOptions`, `BlockWorker`, and `AsyncBlockRemover`.

## Risks and Test Signals
Signals cover successful drain and failed-attempt drain. Gaps include duplicate block suppression, shutdown behavior, retry policy, session IDs, and listener/master reporting around removals.
