# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/MetadataSyncLockManagerTest.java

## Purpose
This unit test validates `MetadataSyncLockManager` path locking, invalid path rejection, lock-pool garbage collection, URI normalization, and ancestor/descendant concurrency blocking.

## Important APIs, Types, and Functions
- `setup()` reloads configuration and sets metadata sync lock pool initial size, low watermark, and high watermark to zero for deterministic garbage collection.
- `lookPoolGC()` acquires locks for `/a/b/c/d` and `/e`, checks pool size, closes locks, and waits for unused locks to be recycled.
- `invalidPath()` asserts malformed paths throw `InvalidPathException`.
- `concurrentLock()` checks independent, same, sibling, descendant, duplicate slash, and `alluxio://` normalized path cases.
- `metadataSyncLockTest()` acquires one path lock, asynchronously attempts a second lock, and uses a timeout to detect expected blocking.

## Control Flow
The test creates a `MetadataSyncLockManager`, acquires `MetadataSyncPathList` instances through `lockPath`, and closes them with try-with-resources or explicit `close`. Blocking behavior is detected by `CompletableFuture.get(200ms)`; if it times out while blocking is expected, the held lock is released and the future must complete.

## State and Persistence Behavior
The lock manager maintains an in-memory lock pool. This test checks that pool size grows with path components and shrinks to zero when watermarks are configured to zero and locks are closed. No persistent state is involved.

## Dependencies and Integration Points
It uses Alluxio path parsing via `AlluxioURI`, configuration keys for lock pool sizing, `CommonUtils.waitFor`, `InvalidPathException`, Java `Closeable`, `CompletableFuture`, and timeout-based concurrency checks.

## Risks
- Timeout-based blocking detection can be sensitive to heavily loaded test environments.
- The test name `lookPoolGC` appears to mean lock-pool GC, but the behavior is clear.
- Invalid path coverage is narrow and focused on whitespace/non-absolute examples.
- Exact pool size expectations encode the lock manager's path-component allocation model.

## Test Signals
Signals are pool-size counts after lock acquisition/release, thrown `InvalidPathException`, whether a second path lock completes within 200ms, and successful completion after the first lock is closed.
