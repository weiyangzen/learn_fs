# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/WriteManager.java

## Purpose
`WriteManager` coordinates asynchronous NFS WRITE and COMMIT handling. It owns the `OpenFileCtxCache`, opens HDFS append streams when needed, starts/stops the async write service, maps commit outcomes to NFS statuses, and adjusts reported file attributes for cached unwritten data.

## Important APIs, Types, And Functions
Important methods are `handleWrite`, `handleCommit`, `commitBeforeRead`, `getFileAttr` overloads, `addOpenFileStream`, `startAsyncDataService`, `shutdownAsyncDataService`, and `getOpenFileCtxCache`. `MultipleCachedStreamException` is declared but not used in this file.

## Control Flow
`handleWrite` validates request data length, finds an existing `OpenFileCtx`, or opens an HDFS append stream for the file-id path. It treats `AlreadyBeingCreatedException` as a transient close/retry condition, sends IO errors on append failure, constructs a new `OpenFileCtx`, inserts it into the cache, and delegates the write to `OpenFileCtx.receivedNewWrite`.

`commitBeforeRead` checks whether cached writes need syncing before a READ and converts `COMMIT_STATUS` to `NFS3_OK`, `NFS3ERR_IO`, or `NFS3ERR_JUKEBOX` without blocking. `handleCommit` does the same for explicit COMMIT, except `COMMIT_WAIT` returns without a synchronous response because `OpenFileCtx` will respond later.

## State And Persistence
State includes config, id mapper, async service lifecycle, maximum streams, AIX compatibility mode, stream timeout, and the open-file cache. Persistent changes are performed by `OpenFileCtx` and HDFS append streams; this class mediates when streams are opened, closed, and synced.

## Dependencies And Integration Points
`RpcProgramNfs3` calls it from WRITE, COMMIT, READ, GETATTR, LOOKUP, and READDIRPLUS paths. It depends on `DFSClient`, `HdfsDataOutputStream`, `Nfs3Utils`, NFS response types, `AsyncDataService`, `OpenFileCtx`, and the config keys controlling stream timeout, cache size, dump directory, and AIX behavior.

## Risks
When the stream cache is full, new writes get `NFS3ERR_JUKEBOX` and clients must retry. Append failure handling must avoid leaking `HdfsDataOutputStream`. Returning success for commits without an open stream assumes all data is already durable enough, which is normal but depends on cache correctness. Attribute adjustment with `openFileCtx.getNextOffset()` exposes buffered size before HDFS metadata fully catches up.

## Test Signals
Coverage is mostly indirect through `RpcProgramNfs3` tests and `TestOpenFileCtxCache`. READ-before-COMMIT, explicit COMMIT wait paths, append retry after `AlreadyBeingCreatedException`, and cache-full jukebox behavior are important regression targets.
