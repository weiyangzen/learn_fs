# Research Group: subset-b-007441

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/OpenFileCtx.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/OpenFileCtx.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/OpenFileCtxCache.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/OpenFileCtxCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/PrivilegedNfsGatewayStarter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/PrivilegedNfsGatewayStarter.java

## Purpose
`PrivilegedNfsGatewayStarter` is an Apache Commons Daemon entry point that pre-binds a privileged UDP socket for NFS gateway portmap registration. It works around rpcbind variants that require registration traffic to originate from a port below 1024.

## Important APIs, Types, And Functions
It implements `Daemon` with `init`, `start`, `stop`, and `destroy`. State fields are daemon arguments, `registrationSocket`, and the running `Nfs3` server.

## Control Flow
`init` loads `NfsConfiguration`, reads `dfs.nfs.registration.port`, validates that it is in the privileged range 1-1023, creates a reusable datagram socket bound to `localhost:clientPort`, and stores daemon arguments. `start` passes the socket to `Nfs3.startService`. `stop` stops the NFS service, and `destroy` closes the socket if it remains open.

## State And Persistence
The class has no durable state. Its runtime state is the bound UDP socket and service reference. Socket lifetime spans daemon initialization through destroy.

## Dependencies And Integration Points
It integrates with JSVC or another Commons Daemon launcher, `Nfs3`, and NFS configuration keys. The socket is passed into the RPC program registration path so portmap registration uses the privileged source port.

## Risks
Startup fails if the configured registration port is not privileged or cannot bind, which is expected but operationally sharp. It binds to localhost only; deployments that need different registration behavior must use the regular gateway path or configuration changes. Socket cleanup relies on daemon lifecycle callbacks.

## Test Signals
No direct test in this subset exercises it. Indirect signals are NFS service startup tests and environments that verify portmap registration under rpcbind implementations requiring privileged source ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/PrivilegedNfsGatewayStarter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/RpcProgramNfs3.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/RpcProgramNfs3.java

## Purpose
`RpcProgramNfs3` is the Hadoop NFSv3 server-side RPC program. It implements `Nfs3Interface`, translates NFSv3 requests to HDFS `DFSClient` operations, enforces export and port access checks, manages metrics and duplicate-call caching, and delegates asynchronous write/commit work to `WriteManager`.

## Important APIs, Types, And Functions
The class exposes handlers for NFSv3 procedures: `getattr`, `setattr`, `lookup`, `access`, `readlink`, `read`, `write`, `create`, `mkdir`, `mknod`, `remove`, `rmdir`, `rename`, `symlink`, `link`, `readdir`, `readdirplus`, `fsstat`, `fsinfo`, `pathconf`, and `commit`. Lifecycle APIs are `createRpcProgramNfs3`, `startDaemons`, `stopDaemons`, `handleInternal`, `isIdempotent`, and test-visible accessors. Support methods include `setattrInternal`, `mapErrorStatus`, `listPaths`, `getSecurityHandler`, and `checkAccessPrivilege`.

## Control Flow
Construction configures umask, id mapping, exports, `WriteManager`, `DFSClientCache`, HDFS create defaults, dump directory cleanup, Kerberos login, superuser name, duplicate-call cache, and HTTP server. `startDaemons` starts the pause monitor, async write service, and info server; `stopDaemons` stops them.

`handleInternal` validates authentication flavor except for NULL, checks duplicate non-idempotent calls in `RpcCallCache`, dispatches by `NFSPROC3`, records metrics for synchronous procedures, serializes a response if one is returned, and sends it through Netty. `write` and `commit` usually return `null` because response delivery is handled asynchronously through `WriteManager` and `OpenFileCtx`.

Each handler deserializes its XDR request, obtains a user/namenode-specific `DFSClient` from `DFSClientCache`, checks export privilege through `NfsExports`, maps file handles to `.reserved/.inodes` paths via `Nfs3Utils`, performs HDFS operations, and builds NFS response plus weak-cache-consistency data where applicable.

## State And Persistence
Persistent filesystem effects are HDFS creates, deletes, renames, symlinks, attribute updates, appends, and syncs. In-memory state includes config, id mapper, client cache, export table, write manager, RPC call cache, metrics, pause monitor, info server, and dump directory path. Startup can delete and recreate the configured write dump directory when dump support is enabled.

## Dependencies And Integration Points
It depends on Hadoop HDFS client APIs, NFS protocol request/response classes, ONCRPC/Netty transport, `NfsExports`, `ShellBasedIdMapping`, `DFSClientCache`, `WriteManager`, `Nfs3HttpServer`, metrics, Kerberos/security utilities, and MiniDFS-backed tests. It is instantiated and hosted by `Nfs3`.

## Risks
The class is broad and security-sensitive. Export checks are separate from HDFS permission checks; missing either can expose operations. `getSecurityHandler` only builds handlers for AUTH_SYS and returns null otherwise, while `handleInternal` allows RPCSEC_GSS flavor through the initial check, so unsupported credential paths need care. READ retries are effectively once despite the comment. Directory cookies use HDFS file IDs and special dot handling to satisfy Linux clients; deleted-cookie recovery restarts listing from the beginning and can duplicate entries. Asynchronous write/commit responses must preserve xid/channel correctness and duplicate-call semantics.

## Test Signals
This subset covers startup and portmap timeout propagation (`TestMountd`), export privilege denial (`TestClientAccessPrivilege`), export-point validation (`TestExportsTable`), HTTP info server (`TestNfs3HttpServer`), directory listing cookies (`TestReaddir`), access-right utility behavior (`TestNfs3Utils`), and manual write/UDP harnesses. Broader regression signals are NFS gateway integration tests over MiniDFSCluster.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/RpcProgramNfs3.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/WriteCtx.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/WriteCtx.java

## Purpose
`WriteCtx` represents one NFS WRITE request buffered by an `OpenFileCtx`. It keeps the file handle, byte range, stable-write mode, request data, Netty reply channel, xid, reply status, optional dump-file location, and trimming metadata for overlapping writes.

## Important APIs, Types, And Functions
`DataState` tracks `ALLOW_DUMP`, `NO_DUMP`, and `DUMPED`. Key methods are `trimWrite`, `dumpData`, `getData`, `writeData`, `getOffset`, `getCount`, `getStableHow`, channel/xid/replied accessors, and `toString`. `INVALID_ORIGINAL_COUNT` marks unmodified requests.

## Control Flow
New contexts start with a byte buffer and state chosen by `OpenFileCtx`. Out-of-order contexts may be dumped by `dumpData`, which writes the original request bytes to a shared dump file, records the file offset, clears memory, and marks the state `DUMPED` if the write has not concurrently started. When write-back needs data, `getData` returns the in-memory buffer or reloads from the dump file. `trimWrite` and `trimData` adjust offset/count/buffer position when a request overlaps already-written bytes. `writeData` obtains the final buffer, validates position and count, checks modified-write consistency, and writes to `HdfsDataOutputStream`.

## State And Persistence
State is per-request and mostly mutable under synchronization: offset, count, original count, trim delta, replied flag, `ByteBuffer`, `RandomAccessFile`, dump offset, and data state. Persistent side effects are limited to optional bytes in the context dump file and writes to the shared HDFS output stream.

## Dependencies And Integration Points
It is created and consumed by `OpenFileCtx`, uses NFS `FileHandle` and `WriteStableHow`, Netty `Channel`, `HdfsDataOutputStream`, Hadoop `Preconditions`, and dump streams owned by the open-file context.

## Risks
The data-state transitions race with dumping and write-back. Trimming dumped data requires retaining original count/position semantics, and invalid original-count handling can break client-visible byte counts. `ByteBuffer.array()` assumes heap-backed buffers. Dump reload reads the full original count before trimming, so dump-file corruption or offset mismatch becomes an IOException during write-back.

## Test Signals
Overlap and out-of-order behavior is indirectly covered by `OpenFileCtx` tests and manual `TestOutOfOrderWrite`. Stronger signals would include tests for dumped-and-trimmed writes, original-count replies, and stable write modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/WriteCtx.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/WriteManager.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/WriteManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/TestMountd.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/TestMountd.java

## Purpose
`TestMountd` is a JUnit test for NFS gateway startup and portmap UDP timeout propagation to both mountd and nfsd RPC programs.

## Important APIs, Types, And Functions
The single test `testStart` uses `MiniDFSCluster`, `NfsConfiguration`, `Nfs3`, `RpcProgramMountd`, `RpcProgramNfs3`, and a NULL XDR call.

## Control Flow
The test starts a one-node MiniDFSCluster, sets mountd and NFS ports to 0 for parallel-safe ephemeral binding, sets the portmap timeout config, starts `Nfs3`, invokes mountd `nullOp` and nfsd `nullProcedure`, and asserts each RPC program sees the configured timeout.

## State And Persistence
It creates temporary MiniDFSCluster state and starts local NFS services on ephemeral ports. No durable repository state is written.

## Dependencies And Integration Points
It integrates the HDFS test cluster, NFS service startup, mount daemon, NFS daemon, and ONCRPC XDR handling.

## Risks
The test does not use `finally` around cluster shutdown, so failures before the explicit shutdown can leak test resources. It verifies startup/config plumbing, not actual mount or NFS data operations.

## Test Signals
Passing indicates NFS and mount daemons can start against MiniDFSCluster and share the UDP portmap timeout configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/TestMountd.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/TestOutOfOrderWrite.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/TestOutOfOrderWrite.java

## Purpose
`TestOutOfOrderWrite` is a manual TCP client harness for sending NFS CREATE and out-of-order WRITE requests to a running NFS gateway. It is not a JUnit test.

## Important APIs, Types, And Functions
Helpers `create`, `write`, and `testRequest` build XDR/RPC requests. `WriteHandler` captures the file handle from the CREATE response. `WriteClient` customizes the Netty pipeline, and `main` sends writes for offsets 2000, 1000, and 0.

## Control Flow
`main` fills three data arrays, opens a TCP client to the configured NFS port, sends CREATE, waits until `WriteHandler` extracts the new handle, then sends three WRITE frames in reverse order using `Nfs3Utils.writeChannel`.

## State And Persistence
Runtime state is static handle/channel references and test byte arrays. If run against a live gateway, it creates a file named `out-of-order-write<timestamp>` and writes data through NFS.

## Dependencies And Integration Points
It depends on ONCRPC request framing, Netty, NFSv3 request/response types, and a separately running NFS server. It is intended to exercise `OpenFileCtx` out-of-order buffering.

## Risks
The write RPC header appears to use the CREATE procedure value when constructing WRITE requests, so the harness may not work as intended without inspection. It has no assertions, no automated cleanup, and can hang waiting for a handle.

## Test Signals
As a manual tool, useful signals are server logs and final HDFS file content. It should be converted to an automated integration test before being relied on for regression coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/TestOutOfOrderWrite.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/TestUdpServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/TestUdpServer.java

## Purpose
`TestUdpServer` is a manual UDP portmap request harness. It sends raw ONCRPC UDP packets to local rpcbind/portmap for NFS and mount service discovery. It is not a JUnit test.

## Important APIs, Types, And Functions
`createPortmapXDRheader` writes RPC call headers. `testGetportMount`, `testGetport`, and `testDump` build portmap GETPORT/DUMP requests. `Runtest1` and `Runtest2` are `SubjectInheritingThread` wrappers.

## Control Flow
`main` starts `Runtest1`, which sends a MOUNT GETPORT request to `localhost:SUN_RPCBIND`. `testRequest` opens a `DatagramSocket`, sends the bytes, waits for one response, and closes the socket.

## State And Persistence
There is no durable state. The only runtime state is the UDP socket and request/response byte arrays.

## Dependencies And Integration Points
It depends on a local rpcbind service and Hadoop ONCRPC XDR/RpcCall classes. It is adjacent to NFS gateway registration behavior rather than HDFS data paths.

## Risks
It exits the JVM on IO or host errors, has no assertions, ignores the `request2` argument, and contains likely copy/paste errors where headers are written to `xdr_out` instead of `request2`. It is unsuitable for automated CI as written.

## Test Signals
Manual success is receipt of a UDP response. Automated regression coverage would need assertions over decoded portmap responses and cleanup/timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/TestUdpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestClientAccessPrivilege.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestClientAccessPrivilege.java

## Purpose
`TestClientAccessPrivilege` verifies that export-table read-only privileges prevent mutating NFS operations, specifically REMOVE.

## Important APIs, Types, And Functions
The fixture uses `MiniDFSCluster`, `DistributedFileSystem`, `NameNode`, `Nfs3`, `RpcProgramNfs3.remove`, mocked `SecurityHandler`, and XDR request construction. The test method is `testClientAccessPrivilegeForRemove`.

## Control Flow
Setup configures proxy-user rules, starts MiniDFSCluster, chooses ephemeral NFS ports, and mocks the security user. Each test recreates `/tmp/f1`. The test sets exports to `* ro`, starts NFS, builds a REMOVE request for `f1` under the `/tmp` file handle, calls `nfsd.remove` directly, and asserts `NFS3ERR_ACCES`.

## State And Persistence
It creates and deletes `/tmp` content inside MiniDFSCluster. NFS service state is in-process and ephemeral.

## Dependencies And Integration Points
It directly targets `RpcProgramNfs3.checkAccessPrivilege` via the REMOVE path and depends on `NfsExports` parsing the allowed-hosts configuration.

## Risks
Only REMOVE is checked, so other write operations rely on parallel code patterns rather than this test. The NFS server is not explicitly stopped, and cluster shutdown occurs only after all tests.

## Test Signals
Passing confirms read-only export policy blocks a direct REMOVE handler call even when the mocked HDFS user has filesystem access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestClientAccessPrivilege.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestDFSClientCache.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestDFSClientCache.java

## Purpose
`TestDFSClientCache` verifies caching and impersonation behavior in `DFSClientCache`, which is the user/namenode client source used by `RpcProgramNfs3`.

## Important APIs, Types, And Functions
Tests cover `getDfsClient`, cache eviction, `getUserGroupInformation`, and construction with multiple export points on the same namenode. Helper `isDfsClientClose` probes closed clients via `exists`.

## Control Flow
`testEviction` creates a cache of size one, fetches a client for `test1`, verifies reuse, fetches `test2`, then checks the first client was closed and the cache stayed bounded. Two UGI tests verify proxy UGI creation under Kerberos and simple login users. `testMultipleExportPointsSameNamenode` ensures duplicate export paths resolving to the same namenode do not throw false collision errors.

## State And Persistence
It mutates global `UserGroupInformation` state and resets it after each test. It creates DFSClient objects targeting `hdfs://localhost` but does not start a cluster in this file.

## Dependencies And Integration Points
It protects the client-cache layer used by all NFS RPC handlers. It depends on HDFS client close behavior, NFS export-point config, and Hadoop security UGI.

## Risks
The closed-client probe depends on exception text `Filesystem closed`. Tests do not exercise input-stream cache behavior or live NameNode interactions.

## Test Signals
Passing confirms bounded DFSClient caching, proxy user construction, Kerberos auth-method transition to PROXY, and same-namenode multi-export tolerance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestDFSClientCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestExportsTable.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestExportsTable.java

## Purpose
`TestExportsTable` verifies NFS export-point discovery and validation for HDFS and ViewFs-backed configurations.

## Important APIs, Types, And Functions
The tests use `MiniDFSCluster`, federated `MiniDFSNNTopology`, ViewFs `ConfigUtil.addLink`, `Nfs3`, `Mountd`, and `RpcProgramMountd.getExports`. Cases cover root HDFS export, multiple ViewFs export links, internal ViewFs export, invalid ViewFs root export, internal HDFS export, and invalid local filesystem export.

## Control Flow
Each test configures ephemeral NFS/mount/http ports, starts a MiniDFSCluster, optionally builds ViewFs links to federated HDFS namespaces, starts NFS, and asserts the mount daemon's export list. Invalid configurations assert `FileSystemException` messages indicating unsupported underlying schemes.

## State And Persistence
Tests create temporary MiniDFSCluster state and HDFS directories such as `/user1`, `/user2`, `/myexport1`, and ViewFs links in configuration. Clusters are shut down in `finally` blocks.

## Dependencies And Integration Points
This suite covers integration among export configuration, mount daemon export reporting, NFS startup validation, HDFS filesystems, and ViewFs resolution.

## Risks
Assertions use `assertTrue` equality checks and message substrings rather than stronger typed status objects. Startup of full MiniDFS clusters makes tests relatively heavy. Export ordering is assumed for the multiple-export case.

## Test Signals
Passing indicates NFS exports are advertised correctly for valid HDFS/ViewFs internal paths and fail fast for unsupported root ViewFs or local filesystem configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestExportsTable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestNfs3HttpServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestNfs3HttpServer.java

## Purpose
`TestNfs3HttpServer` verifies that the NFS gateway HTTP/HTTPS info server starts and exposes default servlet endpoints.

## Important APIs, Types, And Functions
Setup uses `NfsConfiguration`, `HttpConfig.Policy.HTTP_AND_HTTPS`, `KeyStoreTestUtil`, `MiniDFSCluster`, and ephemeral NFS/http/https addresses. `testHttpServer` starts `Nfs3`, obtains `Nfs3HttpServer`, fetches `/jmx`, and checks the secure port.

## Control Flow
Before all tests, SSL config and keystores are generated under a temp directory, then MiniDFSCluster starts. The test starts NFS, reads the info server URI, downloads `/jmx`, asserts JMX content includes a Java MBean prefix, and asserts HTTPS port is positive. Teardown deletes temp files, shuts down the cluster, and cleans SSL config.

## State And Persistence
It writes temporary keystore and SSL config files under the test temp path and creates an in-process MiniDFSCluster. No durable repository files are modified.

## Dependencies And Integration Points
It covers `RpcProgramNfs3.startDaemons`, `Nfs3HttpServer`, Hadoop HTTP server defaults, HTTPS configuration, and metrics/JMX exposure.

## Risks
The NFS service is not explicitly stopped in the test method. Network-bound tests can be sensitive to local port allocation and HTTP policy configuration.

## Test Signals
Passing confirms the NFS info server can start with HTTP and HTTPS enabled and serve the standard `/jmx` endpoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestNfs3HttpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestNfs3Utils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestNfs3Utils.java

## Purpose
`TestNfs3Utils` verifies access-right calculation from NFS file attributes, user id, group id, and auxiliary groups.

## Important APIs, Types, And Functions
The single test `testGetAccessRightsForUserGroup` mocks `Nfs3FileAttributes` and calls `Nfs3Utils.getAccessRightsForUserGroup` for regular files and directories.

## Control Flow
The test mutates mocked uid/gid/mode/type values across scenarios: owner mismatch under `0700`, group mismatch under `0070`, other permissions under `0007`, auxiliary-group read under `0440`, owner directory lookup under `0700`, denied group/auxiliary matches when mode lacks group bits, and directory lookup under `0711`.

## State And Persistence
There is no persistent state. Mockito stubs on a local mock object drive all cases.

## Dependencies And Integration Points
It supports `RpcProgramNfs3.access` and zero-count `read` permission checks, which call the same utility to translate POSIX mode bits into NFS ACCESS masks.

## Risks
Expected numeric masks are asserted directly with comments, which can obscure intent if constants change. The test does not cover symlink or special-file types.

## Test Signals
Passing confirms owner, group, auxiliary group, other, regular-file, and directory lookup/execute translations for common mode combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestNfs3Utils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestOffsetRange.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestOffsetRange.java

## Purpose
`TestOffsetRange` verifies validation and ordering behavior for `OffsetRange`, the key type used by `OpenFileCtx.pendingWrites`.

## Important APIs, Types, And Functions
It constructs `OffsetRange` instances and uses `OffsetRange.ReverseComparatorOnMin`.

## Control Flow
Four constructor tests assert invalid ranges throw `IllegalArgumentException`: empty, negative start, both negative, and negative-to-positive. `testCompare` checks equality for identical ranges and reverse ordering by minimum offset.

## State And Persistence
There is no state beyond local objects.

## Dependencies And Integration Points
The comparator contract directly affects `ConcurrentSkipListMap` ordering in `OpenFileCtx`, including dump traversal and contiguous write-back selection.

## Risks
The test only checks min-offset ordering, not overlap behavior, max boundaries, or map interactions with equal minimum and different maximum values.

## Test Signals
Passing protects basic range invariants and reverse comparator semantics needed for out-of-order write buffering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestOffsetRange.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestOpenFileCtxCache.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestOpenFileCtxCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestReaddir.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestReaddir.java

## Purpose
`TestReaddir` verifies NFS READDIR and READDIRPLUS responses for initial cookies, resume cookies, and deleted-cookie recovery.

## Important APIs, Types, And Functions
The suite uses `MiniDFSCluster`, `DistributedFileSystem`, `NameNode`, `Nfs3`, `RpcProgramNfs3.readdir`, `RpcProgramNfs3.readdirplus`, NFS `FileHandle`, XDR request construction, and mocked `SecurityHandler`.

## Control Flow
Setup configures proxy users, starts MiniDFSCluster and NFS, and mocks the current user. Before each test, `/tmp` is recreated with files `f1`, `f2`, and `f3`. `testReaddirBasic` sends cookie-zero READDIR, expects dot/dotdot plus three files, then uses `f2`'s file ID as a resume cookie and expects only `f3`; after deleting `f2`, the same cookie causes listing restart without dot/dotdot and returns two entries. `testReaddirPlus` repeats the same scenarios while expecting attributes and handles in entries.

## State And Persistence
It mutates MiniDFSCluster filesystem contents under `/tmp`. NFS and HDFS cluster state live for the class and are shut down after all tests.

## Dependencies And Integration Points
It directly covers `RpcProgramNfs3.listPaths`, cookie-to-inode-id path conversion, dot/dotdot special handling, and READDIRPLUS child attribute lookup through `WriteManager.getFileAttr`.

## Risks
The tests assume stable HDFS listing order and file-id cookie behavior. They do not assert cookie verifier mismatch handling, count truncation, non-directory errors, or export privilege failures.

## Test Signals
Passing confirms basic directory enumeration, resume-after-cookie semantics, and recovery when the cookie's start-after entry has been deleted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestReaddir.java -->
