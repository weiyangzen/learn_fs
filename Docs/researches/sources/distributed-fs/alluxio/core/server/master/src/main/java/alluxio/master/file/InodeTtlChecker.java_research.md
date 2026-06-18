# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/InodeTtlChecker.java

## Purpose
`InodeTtlChecker` is a heartbeat executor that scans expired inode TTL buckets and applies the configured TTL action: free, delete from Alluxio and UFS, or delete only from Alluxio.

## Important APIs, types, and functions
The constructor receives `FileSystemMaster` and `InodeTree`, then uses `inodeTree.getTtlBuckets()`. `heartbeat(long)` polls expired `TtlBucket`s, resolves each inode id to a path, reloads the inode from the bucket list, checks expiration again, and dispatches by `TtlAction`. `close()` is a no-op.

## Control flow
For each expired inode entry, the checker first verifies interruption, skips exhausted retries, locks the full path read-only to get a stable URI, then reloads the inode. `FREE` invokes public `free` and `setAttribute` to unpin and set minimum replication to zero, then journals TTL reset and pinned reset directly through `InodeTree.updateInode`. `DELETE` invokes public delete, recursive for directories. `DELETE_ALLUXIO` invokes public delete with `alluxioOnly`, recursive for directories. Failures decrement retry count and reinsert failed inodes into TTL buckets.

## State and persistence behavior
The checker mutates persistent inode state through public master APIs and direct journaled inode updates. Failed retry state is held in TTL buckets as retry counts. It uses `NoopJournalContext` only for the first read lock, then obtains a real journal context for TTL reset after `FREE`.

## Dependencies and integration points
It integrates with the heartbeat service, `TtlBucketList`, inode locking, public `FileSystemMaster` free/delete/setAttribute methods, delete/free/set-attribute contexts, and journal contexts.

## Risks
Because it calls public APIs after resolving paths, the path can change between the read lock and the action. Retry reinsertion depends on `mTtlBuckets.loadInode` returning a usable inode. `FREE` performs multiple operations, so partial failure can free data but fail to reset TTL or pin state. Permission behavior is whatever the public master methods enforce for the checker's service user.

## Test signals
Tests should cover each TTL action for files and directories, retry reinsertion, exhausted retries, already-deleted inodes, interruption, and journaled TTL reset after `FREE`.
