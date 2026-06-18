# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestWrites.java

## Purpose
Focused tests for the NFS write path, especially `OpenFileCtx`, `WriteCtx`, `WriteManager`, commit state transitions, stable-write semantics, and out-of-order/overlapping write assembly. Unlike `TestRpcProgramNfs3`, much of this class tests the write state machine directly with mocks.

## Important APIs, Types, and Functions
Key production types under test are `OpenFileCtx`, `WriteCtx`, `OffsetRange`, `OpenFileCtx.CommitCtx`, `OpenFileCtx.COMMIT_STATUS`, and `WriteManager`. `testAlterWriteRequest()` validates `OpenFileCtx.alterWriteRequest()` by checking `ByteBuffer` position/limit after trimming already-flushed bytes. `testCheckCommit*` methods exercise `checkCommit`, `checkCommitInternal`, and `commitBeforeRead` under normal, large-file-upload, AIX compatibility, and read-before-commit modes. `waitWrite()` polls the NFS write manager cache until pending writes drain.

## Control Flow
The direct commit tests construct mocked `DFSClient` and `HdfsDataOutputStream`, set `fos.getPos()` and `ctx.nextOffset`, seed `pendingWrites` and `pendingCommits`, then assert each expected `COMMIT_STATUS`: inactive, inactive-with-pending-write, do-sync, finished, wait, special-wait, and special-success. The integration tests start a mini cluster and NFS service, create files via NFS `CREATE3Request`, issue `WRITE3Request`s with `DATA_SYNC`, `FILE_SYNC`, `UNSTABLE`, out-of-order offsets, or overlapping byte ranges, wait for pending writes to drain, then read back through NFS.

## State and Persistence Behavior
`OpenFileCtx` state includes active/inactive flags, pending write ranges, pending commit offsets, stream position, next expected write offset, large-file-upload mode, and AIX compatibility behavior. In the integration tests, the state persists through the write manager's open-file cache keyed by `FileHandle`, while HDFS persists completed byte content and file length.

## Dependencies and Integration Points
The tests integrate HDFS `DFSClient`, `HdfsDataOutputStream`, mini clusters, the Hadoop NFS RPC program, ONC RPC XDR request serialization, Netty `Channel` mocks for deferred commit replies, shell-based ID mapping, proxy-user authorization, and NFS status codes. Mockito is used heavily to force stream positions that would be hard to stage through real I/O.

## Risks and Test Signals
Important edge cases include trimming write requests at multiple offsets, commit offsets beyond flushed position, zero-offset commit behavior with pending ranges, inactive contexts, large-file upload divergences, read-triggered commits that must not enqueue waits, and overlapping writes. Signals include exhaustive commit-status assertions, pending-commit map checks, `commitBeforeRead` status codes, readback equality after stable writes, file-length sync after `FILE_SYNC`, out-of-order verification, complete overlapping reconstruction, and `checkSequential()` boundary checks.
