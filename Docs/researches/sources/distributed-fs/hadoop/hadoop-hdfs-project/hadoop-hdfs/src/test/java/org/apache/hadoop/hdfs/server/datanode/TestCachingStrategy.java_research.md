# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestCachingStrategy.java

## Purpose
`TestCachingStrategy` validates HDFS client and DataNode drop-behind caching behavior by intercepting native `posix_fadvise` calls and checking byte ranges dropped from the OS page cache after writes and reads.

## Important APIs, Types, and Functions
- `NativeIO.POSIX.setCacheManipulator` installs `TestRecordingCacheTracker`.
- `Stats` records byte offsets that received `POSIX_FADV_DONTNEED`.
- `createHdfsFile` and `readHdfsFile` optionally call `setDropBehind` on output/input streams.
- Tests use `DFS_DATANODE_DROP_CACHE_BEHIND_READS_KEY`, `DFS_DATANODE_DROP_CACHE_BEHIND_WRITES_KEY`, and client defaults `DFS_CLIENT_CACHE_DROP_BEHIND_READS/WRITES`.
- `BlockSender.CACHE_DROP_INTERVAL_BYTES` and `BlockReceiver.CACHE_DROP_LAG_BYTES` are lowered to 4096 for small deterministic tests.

## Control Flow and Behavior
The class-level setup skips edit-log fsyncs for speed, installs the tracker, and adjusts cache-drop intervals. Write/read tests create a one-DataNode cluster, write a 1 MiB file with explicit or default drop-behind policy, identify the underlying block file, and assert the expected range was dropped or not. The small-read test verifies that a positional 17-byte read does not trigger fadvise. The seek test ensures `FSDataInputStream.seek` works after `setDropBehind(false)` clears a block reader.

## State and Persistence
Temporary HDFS block files are created in MiniDFSCluster. `TestRecordingCacheTracker` keeps a process-global map from native file name to `Stats`. It tracks bytes up to `MAX_TEST_FILE_LEN`.

## Dependencies and Integration Points
The test integrates HDFS read/write streams, DataNode `BlockSender` and `BlockReceiver`, client cache strategy settings, native IO cache manipulation, MiniDFSCluster, and block file lookup via NameNode located blocks.

## Risks and Edge Cases
Covered risks include client defaults overriding DataNode defaults, explicit drop-behind true and false, fadvise lag near write packet boundaries, excessive fadvise for small reads, and stream reader reset after policy changes. Because the tracker calls through to the superclass, behavior can depend on platform native IO support.

## Test Signals
Signals are `Stats` presence or absence, byte-range dropped/not-dropped assertions, successful small-read non-dropping behavior, and successful seek after changing drop-behind policy.
