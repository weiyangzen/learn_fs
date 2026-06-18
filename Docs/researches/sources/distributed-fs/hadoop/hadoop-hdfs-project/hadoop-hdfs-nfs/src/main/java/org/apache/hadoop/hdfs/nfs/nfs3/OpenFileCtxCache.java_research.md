# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/OpenFileCtxCache.java

## Purpose
`OpenFileCtxCache` stores active `OpenFileCtx` instances keyed by NFS `FileHandle`. It bounds the number of open HDFS append streams and periodically removes inactive or idle stream contexts.

## Important APIs, Types, And Functions
The core APIs are `put(FileHandle, OpenFileCtx)`, `get(FileHandle)`, `scan(long)`, `cleanAll()`, `shutdown()`, `start()`, and test-visible `getEntryToEvict()`. The inner `StreamMonitor` daemon runs scans every five seconds while enabled.

## Control Flow
`put` synchronizes around cache-size checks. If the cache is full, it asks `getEntryToEvict` for an inactive context, then an idle no-pending-work context older than the minimum stream timeout. Evicted contexts are removed under the lock but cleaned outside it. `scan` iterates current entries, asks each `OpenFileCtx.streamCleanup` if it should be removed, rechecks under lock, removes confirmed entries, and then calls `cleanup` outside the lock.

## State And Persistence
The only persistent runtime state is the concurrent map of open contexts plus `maxStreams`, `streamTimeout`, and monitor lifecycle flags. It does not persist data itself; `OpenFileCtx.cleanup` handles HDFS stream and dump-file cleanup for removed entries.

## Dependencies And Integration Points
It is constructed by `WriteManager` from `NfsConfiguration` and participates in write, commit, attribute, and read-before-commit flows. It depends on `OpenFileCtx` methods for pending-work, active-state, last-access, timeout, and cleanup decisions.

## Risks
Eviction is conservative: if all streams have pending writes or commits, `put` fails and callers must tell clients to retry. Idle eviction uses monotonic timestamps and minimum timeout enforcement, so tests and production behavior can be time-sensitive. A missed cleanup would keep HDFS append streams open; an overly eager cleanup could break in-flight writes.

## Test Signals
`TestOpenFileCtxCache` covers max-stream rejection, eviction after minimum idle time, immediate inactive eviction, all-busy failure, and scan removal of expired or inactive entries.
