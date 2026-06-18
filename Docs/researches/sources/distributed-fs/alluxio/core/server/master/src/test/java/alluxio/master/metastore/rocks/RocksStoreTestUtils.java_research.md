# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/rocks/RocksStoreTestUtils.java

## Purpose
`RocksStoreTestUtils` is a tiny test utility class shared by Rocks metastore tests. It centralizes waiting on asynchronous reader futures so failures in background tasks surface as JUnit failures.

## Important APIs, Types, and Functions
The only public API is `waitForReaders(List<Future<Void>> futures)`. It iterates over each future, calls `get`, and fails the test if any future throws.

## Control Flow, State, and Persistence
The helper has no state and no persistence. It synchronously joins all submitted tasks in order. If `Future.get` throws, the exception stack trace is printed and `Assert.fail` is invoked with the exception message.

## Dependencies and Integration Points
It depends on Java `Future` and JUnit `fail`. It is imported by `RocksInodeStoreTest` to join reader/list/add task batches after latch-controlled concurrent operations.

## Risks
The helper does not enforce a timeout, so a deadlocked test worker can hang the suite. It prints stack traces directly, which is useful for local diagnosis but can add noise in CI logs. It preserves interrupt state only indirectly through the thrown exception path.

## Test Signals
The utility is indirectly covered by Rocks metastore concurrency tests. A good signal is that background task exceptions fail the owning test instead of being silently dropped.
