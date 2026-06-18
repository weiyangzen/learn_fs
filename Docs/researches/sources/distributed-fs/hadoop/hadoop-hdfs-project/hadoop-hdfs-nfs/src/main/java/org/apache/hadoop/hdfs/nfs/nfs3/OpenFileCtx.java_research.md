# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/OpenFileCtx.java

## Purpose
`OpenFileCtx` is the per-open-HDFS-file write context used by the Hadoop NFSv3 gateway. It turns NFS write and commit traffic into ordered appends on a single `HdfsDataOutputStream`, handles retransmitted writes, out-of-order writes, overlapping write ranges, stable-write synchronization, and deferred COMMIT replies.

## Important APIs, Types, And Functions
The main public/package APIs are `receivedNewWrite(...)`, `checkCommit(...)`, `streamCleanup(...)`, `executeWriteBack()`, `cleanup()`, `getNextOffset()`, and test accessors for pending maps and state. `COMMIT_STATUS` encodes normal completion, wait, inactive-context cases, error, `COMMIT_DO_SYNC`, and large-upload special wait/success outcomes. `CommitCtx` records deferred COMMIT response state: offset, channel, xid, pre-op attributes, and start time.

## Control Flow
New writes enter `receivedNewWrite`, reject inactive contexts, update access time, check for repeated write ranges, and call `receivedNewWriteInternal`. `addWritesToCache` trims writes that partially overlap already-appended bytes, rejects complete old overwrites, assigns `NO_DUMP` to sequential writes and `ALLOW_DUMP` to holes, and stores `WriteCtx` in `pendingWrites`. If the write starts at `nextOffset`, `checkAndStartWrite` schedules `AsyncDataService.WriteBackTask`; otherwise it may trigger `waitForDump` and replies immediately as unstable.

`executeWriteBack` repeatedly calls `offerNextToWrite`, which removes the next contiguous range, trims overlaps against `nextOffset`, advances `nextOffset`, and returns a `WriteCtx`. `doSingleWrite` writes data to HDFS, verifies stream position, optionally hsyncs stable writes, sends the write response if not already replied, and calls `processCommits`. `checkCommit` delegates to synchronized `checkCommitInternal`, then performs hsync outside the lock when needed.

## State And Persistence
In-memory state includes `activeState`, `asyncStatus`, `asyncWriteBackStartOffset`, `nextOffset`, `latestAttr`, `pendingWrites`, `pendingCommits`, `lastAccessTime`, and the non-sequential memory counter. Persistence is through the HDFS output stream and optional local dump file. The `Dumper` thread spills non-sequential write data to `dumpFilePath` once `nonSequentialWriteInMemory` crosses the 1 MiB water mark; `WriteCtx` later reloads spilled data through `RandomAccessFile`. `cleanup` closes HDFS and dump streams, replies errors to pending writes, and deletes the dump file.

## Dependencies And Integration Points
`OpenFileCtx` is owned by `WriteManager` and cached by `OpenFileCtxCache`. It depends on `DFSClient`, `HdfsDataOutputStream`, `AsyncDataService`, `Nfs3Utils`, `Nfs3FileAttributes`, NFS response/request classes, Netty `Channel`, id mapping, and metrics on `RpcProgramNfs3`. It relies on `OffsetRange.ReverseComparatorOnMin` so descending iteration finds contiguous low-offset writes while normal iteration favors higher-offset dump candidates.

## Risks
The class is concurrency-sensitive: pending maps are concurrent, but key state transitions rely on object locks, volatile flags, and atomic offsets. Races around `asyncStatus`, deferred commits, dump reloads, and cleanup can affect data visibility or duplicate replies. The local dump-file path must be unique per file context and cleanup must run or disk can leak. Large-file upload special commit behavior intentionally trades RFC purity for client progress and can return success before all holes are filled for non-sequential ranges. Perfect-overwrite support reads back HDFS data and compares content, which is expensive and fragile around concurrent close.

## Test Signals
Direct signals come from `TestOpenFileCtxCache` for cleanup/eviction behavior, `TestOffsetRange` for ordering assumptions, and manual `TestOutOfOrderWrite` for out-of-order writes. Broader NFS write/commit behavior is exercised through `RpcProgramNfs3`, `WriteManager`, and integration tests that create, write, read, and commit through MiniDFSCluster.
