# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestOpenFileCtxCache.java

## Purpose
`TestOpenFileCtxCache` verifies open-file-context cache eviction, timeout scan, inactive context removal, and busy-cache rejection.

## Important APIs, Types, And Functions
Tests use `OpenFileCtxCache.put`, `get`, `size`, `scan`, `OpenFileCtx.setActiveStatusForTest`, pending-write and pending-commit test maps, and mocked `DFSClient`/`HdfsDataOutputStream`.

## Control Flow
`testEviction` fills a max-size-two cache, verifies immediate insertion of a third stream fails before timeout, waits the minimum stream timeout, verifies oldest idle eviction succeeds, marks a context inactive and verifies immediate eviction, then makes remaining contexts busy with pending write/commit entries and verifies insertion fails. `testScan` verifies timed-out entries are removed and inactive entries are removed while active entries remain.

## State And Persistence
State is entirely in-memory with mocked streams. The tests sleep for timeout boundaries, so wall-clock duration is part of behavior.

## Dependencies And Integration Points
It directly targets `OpenFileCtxCache` and indirectly validates `OpenFileCtx.streamCleanup`, pending-work detection, and cleanup lifecycle expected by `WriteManager`.

## Risks
Use of real `Thread.sleep` around minimum stream timeout can make tests slow or timing-sensitive. Mock contexts use the same dump path string, which is safe because dump files are not created in these scenarios.

## Test Signals
Passing confirms cache capacity pressure does not evict busy streams, inactive contexts are preferred, and scan cleanup removes expired contexts.
