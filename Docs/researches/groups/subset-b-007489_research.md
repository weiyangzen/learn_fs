# subset-b-007489 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataXceiver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataXceiver.java

Purpose: `DataXceiver` is the per-connection HDFS data-transfer protocol worker. It extends `Receiver` and implements `Runnable`, accepts one accepted `Peer`, negotiates SASL/data-transfer encryption, loops over one or more `Op` requests on the socket, and dispatches block read, write, copy, replace, checksum, and short-circuit operations against the owning `DataNode`.

Important APIs and functions: `create(...)` constructs the worker for `DataXceiverServer`; `run()` registers the peer, configures socket timeouts, receives SASL streams, reads protocol ops, invokes `processOp`, and closes the peer. Protocol handlers include `readBlock`, `writeBlock`, `transferBlock`, `blockChecksum`, `blockGroupChecksum`, `copyBlock`, `replaceBlock`, `requestShortCircuitFds`, `releaseShortCircuitFds`, and `requestShortCircuitShm`. Test seams include `getBlockReceiver`, `getBufferedOutputStream`, and `checkAndWaitForBP`.

Control flow: normal reads build a `BlockSender`, send a success response with checksum metadata, stream bytes through the read throttler, optionally read client status, update read metrics, and report bad blocks for disk/meta exceptions. Writes validate block tokens with target storage metadata, open or recover a local replica through `BlockReceiver`, optionally connect to the next pipeline target with SASL, forward `writeBlock`, relay connect acks, receive and mirror packets, finalize replication or close-recovery blocks, and release reserved space and streams in `finally`. Copy/replace operations use `DataXceiverServer.balanceThrottler` as a concurrency/bandwidth gate and must always release it.

State and persistence: the class keeps socket streams, remote/local address strings, `previousOpClientName`, the current `BlockReceiver`, the serving thread, and `opStartTime`. Persistent effects happen through `DataNode.data`, `BlockReceiver`, short-circuit shared-memory registry state, NameNode notifications, bad-block handling, and replica files/metadata managed by the dataset. The socket may be released to the `DomainSocketWatcher` after shared-memory creation.

Dependencies and integration points: it is tightly coupled to `DataNode`, `DNConf`, `DataXceiverServer`, `BlockSender`, `BlockReceiver`, `Sender`, `DataTransferProtoUtil`, protobuf response types, block-token secret managers, SASL client/server helpers, `ShortCircuitRegistry`, metrics, and `DataNodeFaultInjector`. It is the bridge between external HDFS clients/peer DataNodes and local dataset mutations.

Risks: the class has many network cleanup paths where leaks or double-close bugs would affect live clients. `decrReadWriteOpMetrics(op)` uses the last op rather than `firstOp`, so metric correctness depends on keepalive op sequencing. Short-circuit operations require domain sockets and correct slot unregister on failure. Write mirroring must preserve original block identity while mutating local generation/length. Interrupt-driven shutdown must not strand reserved bytes or balancer permits. Bad-block reporting must distinguish client disconnects from disk corruption.

Test signals: tests should exercise SASL fallback/errors, keepalive multi-op connections, invalid tokens, block-pool readiness wait/timeout, read status EOF, mirrored write connect failures, transfer stages with illegal multi-target input, replace/copy throttler release, short-circuit fd/shm success and rollback, and metrics increments/decrements for read/write active xceivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataXceiver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataXceiverServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataXceiverServer.java

Purpose: `DataXceiverServer` is the lightweight, non-IPC data-transfer listener for a DataNode. It accepts `Peer` connections from clients and other DataNodes, starts `DataXceiver` daemon threads, tracks active peers, enforces receiver limits, and owns shared transfer/balancer throttles.

Important APIs and types: `run()` is the accept loop; `kill`, `addPeer`, `closePeer`, `releasePeer`, `closeAllPeers`, `restartNotifyPeers`, `sendOOBToPeers`, and `stopWriters` manage connection lifecycle. `BlockBalanceThrottler` extends `DataTransferThrottler` and combines bandwidth throttling with a fair `Semaphore` for concurrent balancer moves. Reconfiguration methods include `updateBalancerMaxConcurrentMovers`, `setMaxXceiverCount`, and throttler setters/getters.

Control flow: the server loops while the DataNode should run and is not shutting down for upgrade. Each accepted peer is rejected if the current xceiver count exceeds `maxXceiverCount`; otherwise a daemon `DataXceiver` is started. Socket timeouts wake the loop for shutdown checks, asynchronous listener close is expected during shutdown, and OOM causes peer close plus a backoff sleep. At termination it closes the listener under lock, optionally interrupts peers for upgrade restart, waits briefly, then closes all peers and resets metrics.

State and persistence: in-memory state is guarded by `lock`: `peers`, `peersXceiver`, `closed`, and `noPeers`. Volatile state includes max receiver count and three transfer throttlers. It has no durable state; it mutates DataNode metrics and affects external socket state. `estimateBlockSize` supplies a fallback block length for older clients and downstream space checks.

Dependencies and integration points: it depends on `PeerServer`, `Peer`, `DataNode`, `Daemon`, `DataTransferThrottler`, and DFS config keys for xceiver count, block size, data-transfer bandwidth, read/write bandwidth, balance bandwidth, and concurrent mover limits. `DataXceiver` calls back into this server for peer registration, release, throttlers, and balancer permits.

Risks: active count enforcement checks `curXceiverCount > maxXceiverCount`, so boundary behavior allows the count to reach the configured maximum before rejecting later accepts. Reconfiguring balancer concurrency downward blocks while acquiring permits; interruption or timeout must preserve the old cap. Peer maps and metrics must stay paired across `releasePeer`, `closePeer`, and `closeAllPeers`, especially when domain sockets are handed to the short-circuit watcher.

Test signals: validate peer add/close metrics, shutdown-for-upgrade OOB and writer interruption, wait-for-no-peers behavior, listener close handling, max-xceiver rejection, independent read/write/transfer throttler configuration, and increasing/decreasing balancer mover limits under active permits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataXceiverServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DatanodeUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DatanodeUtil.java

Purpose: `DatanodeUtil` centralizes small DataNode filesystem helpers for block metadata naming, temporary unlink files, block directory hashing, recursive empty-directory checks, disk-error wrapping, and metadata stream access.

Important APIs: `createFileWithExistsCheck` atomically guards creation of temporary files through `FileIoProvider`; `getMetaName` builds `blk_generation.meta` names; `getUnlinkTmpFile` appends `.unlinked`; `dirNoFilesRecursive` verifies a directory tree has no files; `idToBlockDirSuffix` and `idToBlockDir` map block IDs to the two-level `subdirN/subdirM` finalized layout; `getAllSubDirNameForDataSetLock` enumerates all 32x32 subdirectories; `getMetaDataInputStream` extracts the `FileInputStream` wrapped by dataset metadata input.

Control flow and state: the class is stateless except constants. The block-directory mapping uses bits 16-20 and 8-12 of the block ID with mask `0x1F`, matching DataNode finalized directory sharding. Creation failures from the provider are wrapped with the `DISK_ERROR` prefix so `getCauseIfDiskError` can recover the original cause.

Dependencies and integration points: it depends on `Block`, `ExtendedBlock`, `FsDatasetSpi`, `FsVolumeSpi`, `LengthInputStream`, `DataStorage`, and `FileIoProvider`. `LocalReplica` uses its metadata names, unlink tmp files, and ID-to-directory parsing; dataset locking code can use the subdirectory enumeration.

Risks: `getMetaDataInputStream` casts the wrapped stream to `FileInputStream`, so provided or non-local dataset implementations must match that assumption or avoid this helper. `dirNoFilesRecursive` treats directories as ignorable only if recursively empty; list failures become IOExceptions. The comment in `idToBlockDirSuffix` says `subdir0/subdir0` for an example, but the code correctly returns `subdir<d1>/subdir<d2>`.

Test signals: cover block ID to subdirectory mapping at boundary values, existing temp file rejection, disk-error prefix cause extraction, recursive directory traversal with files and empty subdirs, metadata name formatting, and dataset metadata stream null/non-`FileInputStream` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DatanodeUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DirectoryScanner.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DirectoryScanner.java

Purpose: `DirectoryScanner` periodically reconciles finalized block files on DataNode volumes with the in-memory dataset block map. It detects missing block files, missing metadata files, blocks present on disk but absent in memory, mismatched generation/length, and duplicate block records.

Important APIs and types: the main lifecycle methods are `start`, `run`, `shutdown`, `reconcile`, `scan`, and `getVolumeReports`. `Stats` stores per-block-pool counters. `ScanInfoVolumeReport` groups scan results per volume and block pool. `BlockPoolReport` is a multimap of block pool IDs to sorted `ScanInfo` rows. Inner `ReportCompiler` is a `Callable` that asks a volume to `compileReport` while applying throttling.

Control flow: `start` schedules `run` at a randomized initial delay and fixed scan interval. `run` calls `reconcile` and records dataset finish time, logging recoverable exceptions and rethrowing fatal errors. `reconcile` calls `scan`, waits on a fault-injection hook, then iterates `diffs` and invokes `dataset.checkAndUpdate` in batches with sleeps to reduce long lock holds. `scan` compiles reports in parallel, skips PROVIDED volumes, sorts disk and memory records, then merges by block ID to classify differences.

State and persistence: persistent state lives in the dataset, not this scanner. The scanner keeps transient `diffs`, `stats`, timing counters, executor services, scan intervals, throttle settings, and `shouldRun`. If `retainDiffs` is false, differences are cleared after reconciliation or shutdown. Dataset updates may add, delete, or correct block records based on on-disk files.

Dependencies and integration points: it integrates with `FsDatasetSpi`, `FsVolumeSpi`, `FsVolumeSpi.ScanInfo`, `DataNodeFaultInjector`, `FileUtil`, Guava `ListMultimap`, and DFS config keys for scan interval, thread count, throttle, and reconciliation batch behavior. Volume implementations provide the actual directory traversal via `compileReport`.

Risks: the merge logic is sensitive to sorted order and duplicate block IDs. Scans intentionally skip PROVIDED storage, so provided replicas need separate consistency mechanisms. Interrupts in `ReportCompiler` return `null` and cause the whole volume report list to be cleared. Batch sleeps happen while synchronized on `diffs`, which avoids concurrent mutation but can extend lock ownership. Throttle configuration above 1000 ms/sec is normalized to default.

Test signals: test missing block/meta/memory/mismatch/duplicate classification, deletion-in-progress suppression, PROVIDED-volume exclusion, report compiler interruption, throttle timing counters, invalid config fallbacks, batch reconciliation sleep behavior, shutdown clearing when `retainDiffs` is false, and dataset `checkAndUpdate` calls in diff order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DirectoryScanner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DiskBalancer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DiskBalancer.java

Purpose: `DiskBalancer` admits, validates, schedules, reports, and cancels local disk-balancing plans for one DataNode. Plans move finalized blocks between volumes to satisfy planner-generated byte movement goals while respecting disk bandwidth, tolerance, and error limits.

Important APIs and types: public control APIs include `submitPlan`, `queryWorkStatus`, `cancelPlan`, `getVolumeNames`, `getBandwidth`, `shutdown`, `setDiskBalancerEnabled`, and plan-validity accessors. `verifyPlanVersion`, `verifyPlanHash`, `verifyTimeStamp`, `verifyNodeUUID`, and `createWorkPlan` implement admission. `BlockMover` abstracts the mover. `VolumePair` keys source/destination volume pairs. `DiskBalancerMover` implements block selection and copying.

Control flow: `submitPlan` requires the balancer to be enabled, rejects concurrent plans, validates the SHA-1, version, timestamp, and DataNode UUID, translates planner `Step`s into `DiskBalancerWorkItem`s, records plan identity, and starts one scheduler thread. The scheduler iterates work-map entries and calls `BlockMover.copyBlocks`. `queryWorkStatus` converts `workMap` into `DiskBalancerWorkStatus`, moving completed futures to `PLAN_DONE`. Cancel and shutdown set the mover exit flag and stop the scheduler outside the lock.

State and persistence: durable block data is moved by `FsDatasetSpi.moveBlockAcrossVolumes`; `DiskBalancer` itself maintains in-memory plan ID, plan file, current result, work map, bandwidth, plan-validity interval, and scheduler future. Work item state tracks copied bytes, block count, start time, elapsed time, errors, and error text.

Dependencies and integration points: it depends on `FsDatasetSpi`, `FsVolumeSpi`, `NodePlan`, `Step`, `DiskBalancerWorkItem`, `DiskBalancerWorkStatus`, `DiskBalancerException`, `JsonUtil`, DFS disk-balancer config keys, and `Time`. It is exposed through DataNode control paths that submit/query/cancel plans and through dataset APIs that enumerate volume references and block iterators.

Risks: only one plan is allowed, but `ConcurrentHashMap` iteration order means work-pair execution order is not deterministic. `DiskBalancerMover` checks destination space using `item.getBytesToCopy()` rather than current block size in the pre-copy condition, which is conservative but may stop earlier than necessary. The mover uses first-fit block selection and can fail with "No source blocks" even when smaller/later blocks are unavailable under iterator order and tolerance. Runtime exceptions set the exit flag. Throughput limiting is burst-then-sleep and approximate.

Test signals: verify disabled-state errors, plan hash/version/timestamp/UUID validation, duplicate volume-pair compression, invalid source/destination handling, cancel/shutdown state, status transition to `PLAN_DONE`, volume-name JSON, block iterator round-robin, max error stop, tolerance close-enough logic, transient-storage rejection, destination-space failure, and `computeDelay` boundary behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DiskBalancer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DiskFileCorruptException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DiskFileCorruptException.java

Purpose: `DiskFileCorruptException` is a specific `IOException` used when the kernel reports low-level input/output errors that imply a disk file may be corrupt, for example bad media sectors.

Important APIs: it exposes two constructors: `(String msg, Throwable cause)` and `(String msg)`. It adds no fields or behavior beyond the type.

Control flow and state: this is a marker exception class. Callers can throw or catch it to distinguish likely disk-file corruption from ordinary IO failures. It has no mutable state besides inherited exception message/cause and no persistence behavior.

Dependencies and integration points: it depends only on `java.io.IOException`. It fits into DataNode disk-error handling paths that may mark blocks bad, schedule volume checks, or report failures to the NameNode.

Risks: because no extra metadata is stored, all context must be encoded in the message/cause by callers. Catching broad `IOException` before this type would erase its signal. It should be used only for actual disk-file corruption indications, not protocol/client disconnect errors.

Test signals: tests should assert cause preservation, type-based catch behavior, and integration with disk error paths that classify block or volume corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DiskFileCorruptException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ErrorReportAction.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ErrorReportAction.java

Purpose: `ErrorReportAction` is a `BPServiceActorAction` that carries a DataNode error code and message to be reported to a NameNode for a block pool service actor.

Important APIs: the constructor stores `errorCode` and `errorMessage`; `reportTo` calls `DatanodeProtocolClientSideTranslatorPB.errorReport` with the block-pool registration. `equals`, `hashCode`, and `toString` make actions comparable and loggable.

Control flow and state: instances are immutable after construction. `reportTo` logs `RemoteException` at info level without rethrowing, but wraps ordinary `IOException` in `BPServiceActorActionException`, allowing actor action queues to distinguish remote NameNode-side rejection from local/reporting failure.

Dependencies and integration points: it integrates with `BPServiceActorAction`, `DatanodeProtocolClientSideTranslatorPB`, `DatanodeRegistration`, `RemoteException`, `BPServiceActorActionException`, and `DataNode.LOG`. It is likely enqueued by `BPOfferService` or actor code when the DataNode must notify the NameNode about an error condition.

Risks: `RemoteException` is swallowed after logging, so callers will treat that path as completed. Equality includes the full message string; small formatting differences create distinct actions. Fields have package visibility/finality-like immutability by convention but are not declared `private`.

Test signals: verify successful translator invocation, RemoteException logging/no throw, IOException wrapping, equality and hash code for null/non-null messages, and stable `toString` contents for debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ErrorReportAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/FSCachingGetSpaceUsed.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/FSCachingGetSpaceUsed.java

Purpose: `FSCachingGetSpaceUsed` is an HDFS DataNode specialization point for cached filesystem-space accounting. It extends Hadoop `CachingGetSpaceUsed` and adds builder context for an `FsVolumeImpl` and block-pool ID.

Important APIs: the abstract constructor delegates to `CachingGetSpaceUsed`. Nested `Builder` extends `GetSpaceUsed.Builder` with `setVolume/getVolume`, `setBpid/getBpid`, and an overridden `build` that detects subclasses of `FSCachingGetSpaceUsed` and installs a `Builder` constructor reflectively before delegating to the base builder.

Control flow and state: all mutable configuration is in the builder. `build` allows concrete implementations to receive the richer builder instead of the generic base builder. The built object inherits cached refresh behavior from `CachingGetSpaceUsed`; this class does not implement scanning itself.

Dependencies and integration points: it depends on `GetSpaceUsed`, `CachingGetSpaceUsed`, `FsVolumeImpl`, and the concrete classes configured as the builder's `klass`. Volume/block-pool context lets implementations compute HDFS-specific usage for a volume and block pool.

Risks: reflection requires subclasses to expose a constructor accepting exactly `FSCachingGetSpaceUsed.Builder`; missing constructors become `RuntimeException`. The raw `Class clazz` loses generic type safety. Misconfigured `volume` or `bpid` may be discovered only by the concrete implementation.

Test signals: verify builder chaining, volume/bpid propagation, reflective constructor selection for subclasses, fallback behavior for non-`FSCachingGetSpaceUsed` classes, and IOException propagation from concrete build paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/FSCachingGetSpaceUsed.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/FaultInjectorFileIoEvents.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/FaultInjectorFileIoEvents.java

Purpose: `FaultInjectorFileIoEvents` is the DataNode file-IO fault-injection hook used by `FileIoProvider` before metadata and data operations. In this implementation it records whether fault injection is enabled by configuration, but the hook methods are no-ops.

Important APIs: the constructor reads `DFS_DATANODE_ENABLE_FILEIO_FAULT_INJECTION_KEY`. `beforeMetadataOp(FsVolumeSpi, FileIoProvider.OPERATION)` and `beforeFileIo(FsVolumeSpi, FileIoProvider.OPERATION, long)` are called before provider operations.

Control flow and state: the only state is `isEnabled`, which is currently not read by the hook methods. Subclasses, test-time instrumentation, or future patches can add behavior at these call sites without changing `FileIoProvider` call structure.

Dependencies and integration points: it depends on `Configuration`, `DFSConfigKeys`, `FsVolumeSpi`, and `FileIoProvider.OPERATION`. `FileIoProvider` invokes it before open, read, write, list, move, sync, delete, transfer, and native-copy operations.

Risks: because methods are no-ops, simply setting the configuration key has no effect unless code is extended or instrumented. The unused `isEnabled` field can mislead readers into expecting runtime behavior. Fault-injection exceptions would be routed through normal provider failure handling if implemented later.

Test signals: validate constructor default/explicit config handling and that `FileIoProvider` invokes the hook for each operation category, ideally with a subclass or instrumentation if behavior is added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/FaultInjectorFileIoEvents.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/FileIoProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/FileIoProvider.java

Purpose: `FileIoProvider` is the DataNode's central filesystem operation wrapper. It delegates actual Java/native file operations while adding profiling hooks, fault-injection hooks, and asynchronous disk-error checks on failures.

Important APIs and types: `OPERATION` categorizes operations. Public methods cover `flush`, `sync`, `dirSync`, `syncFileRange`, `posixFadvise`, deletion, `transferToSocketFully`, stream/file creation, share-delete input streams, open-and-seek, random access files, recursive delete, replace/rename/move/native copy, mkdirs, listings, hard-link counts, and existence checks. Wrapped stream classes intercept `read` and `write` on `FileInputStream`, `FileOutputStream`, and `RandomAccessFile`.

Control flow: each operation records a begin timestamp via `ProfilingFileIoEvents`, invokes `FaultInjectorFileIoEvents`, performs the underlying filesystem call, reports success latency, and on exceptions calls `onFailure` before rethrowing. `transferToSocketFully` suppresses disk-error handling for common network errors such as broken pipe and connection reset. Stream factory methods close partially opened streams when wrapping fails.

State and persistence: the provider has no durable state, but operations mutate block files, metadata files, and directories. It holds profiling/fault hooks plus an optional `DataNode`; `onFailure` calls `datanode.checkDiskErrorAsync(volume)` when both DataNode and volume are available. Wrapped streams preserve the associated volume for later read/write instrumentation.

Dependencies and integration points: it integrates with `FsVolumeSpi`, `DataNode`, `ProfilingFileIoEvents`, `FaultInjectorFileIoEvents`, `NativeIO`, `IOUtils`, `FileUtil`, `Storage`, `HardLink`, Commons IO `FileUtils`, Java NIO `Files`, and `SocketOutputStream`. `LocalReplica`, dataset code, block send/receive paths, and disk-balancer moves rely on it for consistent disk instrumentation.

Risks: wrapped `read` methods pass `numBytesRead` to profiling and may pass `-1` at EOF, so metrics consumers must tolerate it. `getMetadataOutputStream` in `LocalReplica` bypasses this provider, so not every metadata write is instrumented. Failure handling catches `Exception`, so runtime exceptions also trigger disk checks. Some methods intentionally retain old behavior compatibility, so replacing them with a single move/delete primitive could change semantics.

Test signals: cover hook ordering and lengths for each operation, stream wrapper read/write metrics, failure-triggered volume checks, broken-pipe transfer suppression, partial factory cleanup, mkdirs failure semantics, delete-with-exists behavior, hard-link count errors, and null volume/DataNode handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/FileIoProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/FinalizedProvidedReplica.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/FinalizedProvidedReplica.java

Purpose: `FinalizedProvidedReplica` represents a finalized HDFS block whose bytes are served from provided/external storage rather than local block files.

Important APIs: constructors accept direct file URI/offset/length/generation/path-handle fields, a `FileRegion`, or path prefix/suffix components. It overrides `getState` to `FINALIZED`, `getBytesOnDisk` and `getVisibleLength` to `getNumBytes`, and unsupported recovery/original-replica methods to throw `UnsupportedOperationException`.

Control flow and state: all location and access behavior is inherited from `ProvidedReplica`. The `FileRegion` constructor translates a provided storage location nonce into a `RawPathHandle`, preserving stable access to external storage. Since finalized replicas expose all bytes, visible length and bytes-on-disk are identical.

Dependencies and integration points: it depends on `ProvidedReplica`, `FileRegion`, `ProvidedStorageLocation`, `FsVolumeSpi`, `FileSystem`, `Path`, `PathHandle`, `RawPathHandle`, `Configuration`, and `ReplicaState`. Dataset code can treat it as a finalized `ReplicaInfo` while reads resolve through provided-storage mechanisms.

Risks: recovery mutation APIs are intentionally unsupported, so callers must not attempt append/recovery workflows on provided finalized replicas. Correctness depends on the external file, offset, length, generation stamp, and path handle remaining valid. Equality/hash behavior is inherited, so provided-location identity semantics come from `ProvidedReplica`.

Test signals: verify constructor field translation from `FileRegion`, `FINALIZED` state, visible/on-disk length equality, unsupported recovery APIs, and read integration against a provided `FileSystem`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/FinalizedProvidedReplica.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/FinalizedReplica.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/FinalizedReplica.java

Purpose: `FinalizedReplica` describes a fully written local block replica. It extends `LocalReplica`, exposes all bytes as visible, and carries cached metadata for finalized-read and recovery-adjacent workflows.

Important APIs: constructors accept block fields or `Block` objects plus volume/directory and optional last partial chunk checksum. Overrides return `ReplicaState.FINALIZED`, `getVisibleLength == getNumBytes`, `getBytesOnDisk == getNumBytes`, and unsupported recovery/original methods. `getMetadataLength` caches the metadata length on first call. `loadLastPartialChunkChecksum` asks the volume to compute/load the last partial chunk checksum.

Control flow and state: the object is mostly immutable block identity/location inherited from `LocalReplica`, with mutable `lastPartialChunkChecksum` and cached `metaLength`. It does not perform writes except checksum cache loading; file IO is inherited through local replica methods.

Dependencies and integration points: it depends on `LocalReplica`, `Block`, `FsVolumeSpi`, `ReplicaState`, and `ReplicaRecoveryInfo`. Block readers, scanners, and dataset maps use it as the normal finalized local replica representation.

Risks: `metaLength` is cached and not invalidated; this is correct for finalized metadata but would be stale if callers mutate metadata after finalization. Recovery APIs throw, so recovery code must convert to another replica state before setting recovery IDs. The checksum byte array is stored by reference, so callers should avoid mutating it after setting.

Test signals: verify finalized state/length values, metadata length caching, copy constructor checksum preservation, last partial checksum loading from volume, unsupported recovery methods, and inherited local file path behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/FinalizedReplica.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/IncrementalBlockReportManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/IncrementalBlockReportManager.java

Purpose: `IncrementalBlockReportManager` batches and sends incremental block reports (IBRs) from a DataNode actor to a NameNode between full block reports. It tracks per-storage received, receiving, and deleted block changes.

Important APIs and types: `notifyNamenodeBlock` queues a `ReceivedDeletedBlockInfo`; `triggerIBR` marks reports ready and optionally forces immediate timing; `sendImmediately`, `waitTillNextIBR`, and `sendIBRs` coordinate actor heartbeat timing. `PerStorageIBR` stores one pending entry per `Block`, supports remove/removeAll/put/putMissing, and increments pending-block metrics by status.

Control flow: adding an RDBI first removes older entries for the same block across all storages, then inserts it for the target storage. `RECEIVING_BLOCK` sets `readyToSend` for the next heartbeat; `RECEIVED_BLOCK` triggers immediate reporting, forced for transient storage. `sendIBRs` snapshots and clears pending reports under synchronization, performs the NameNode RPC outside the lock, records metrics and `lastIBR` on success, or requeues missing reports and logs on failure.

State and persistence: state is in-memory per BP service actor: `pendingIBRs`, `readyToSend`, `ibrInterval`, `lastIBR`, and metrics. Persistence is externalized by the NameNode RPC `blockReceivedAndDeleted`; failed RPCs are requeued so events are not lost unless process state is lost.

Dependencies and integration points: it depends on `DatanodeProtocol`, `DatanodeRegistration`, `DatanodeStorage`, `StorageReceivedDeletedBlocks`, `ReceivedDeletedBlockInfo`, `BlockStatus`, `DataNodeMetrics`, and `Time.monotonicNow`. It is driven by DataNode block lifecycle events and BP service actor heartbeat loops.

Risks: metrics for pending blocks increment on `put`, but `generateIBRs` resets only aggregate pending counts after removal; tests should ensure status-specific counters are interpreted correctly. `putMissing` assumes a `PerStorageIBR` already exists for each storage in failed reports. Process crash loses pending in-memory reports, relying on later full block reports for convergence. Synchronization protects maps but RPC occurs outside locks, so newer entries can coexist while old reports are in flight.

Test signals: verify duplicate block replacement across storages, timing gates for `sendImmediately`, forced transient reports, success metrics and `lastIBR`, failure requeue without overwriting newer entries, deletion report test trigger wait, empty report no-op, and `clearIBRs` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/IncrementalBlockReportManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/LocalReplica.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/LocalReplica.java

Purpose: `LocalReplica` is the abstract base for replicas backed by local block and metadata files. It implements file path derivation, stream access, hard-link breaking, pinning, generation-stamp metadata rename, truncation, copy, delete, and directory fsync behavior.

Important APIs: `getBlockFile`, `getMetaFile`, `getDir`, `parseBaseDir`, `breakHardLinksIfNeeded`, data/metadata stream methods, delete/existence/length methods, `renameMeta`, `renameData`, `updateWithReplica`, pinning accessors, `bumpReplicaGS`, `truncateBlock`, `compareWith`, `copyMetadata`, `copyBlockdata`, static `truncateBlock`, and `fsyncDirectory`.

Control flow: directory state stores an interned base directory plus a `hasSubdirs` flag. If the provided directory matches the sharded block-ID layout, `getDir` recomputes the leaf via `DatanodeUtil.idToBlockDir`; otherwise it uses the base directly. Hard-link breaking copies a block/meta file to an `.unlinked` temp file, verifies length, and atomically replaces the original. Truncation rewrites both block file length and final checksum metadata after recomputing the last chunk checksum.

State and persistence: object state includes block identity inherited from `ReplicaInfo`, `baseDir`, and `hasSubdirs`. Persistent state is the block data file, metadata file, sticky-bit pinning, directory entries, and generation-stamped metadata filename. `internedBaseDirs` reduces duplicate `File` object memory across replicas.

Dependencies and integration points: it uses `FileIoProvider`, `DatanodeUtil`, `DataStorage`, `BlockMetadataHeader`, `DataChecksum`, `NativeIO`, `FsVolumeSpi`, `ScanInfo`, `LocalFileSystem`, `FsPermission`, and `StorageLocation`. `FinalizedReplica` and `LocalReplicaInPipeline` inherit this local-file contract.

Risks: `getMetadataOutputStream` directly creates `FileOutputStream`, bypassing `FileIoProvider` instrumentation. `parseBaseDir` relies on subdirectory names starting with the block subdir prefix. Hard-link breaking must clean temp files on failure or upgrades can leave restart artifacts. `truncateBlock` must handle zero-length and checksum geometry carefully; new length greater than old length is rejected.

Test signals: cover sharded/non-sharded directory parsing, base-dir interning, block/meta path generation, hard-link break replacement and cleanup, NativeIO/share-delete and open-and-seek paths, sticky-bit pinning, generation stamp rename rollback, truncation checksum updates, copy operations through provider, and fsync directory error wrapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/LocalReplica.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/LocalReplicaInPipeline.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/LocalReplicaInPipeline.java

Purpose: `LocalReplicaInPipeline` models a local replica currently being written, replicated, or copied. It extends `LocalReplica` and implements `ReplicaInPipeline`, tracking writer ownership, bytes acknowledged, bytes on disk, reserved space, and last checksum.

Important APIs: constructors create zero-length or existing pipeline replicas. State accessors include `getState`, `getVisibleLength`, `getBytesAcked`, `setBytesAcked`, `getBytesOnDisk`, reserved-space accessors, `setLastChecksumAndDataLen`, `getLastChecksumAndDataLen`, `waitForMinLength`, writer setters/interruption methods, `createStreams`, `createRestartMetaStream`, `moveReplicaFrom`, and `getReplicaInfo`.

Control flow: writes update `bytesOnDisk` and checksum under a lock and signal waiters. Acknowledged bytes release equivalent reserved volume space. `stopWriter` repeatedly interrupts and joins the current writer, handling races where the writer reference changes. `createStreams` opens metadata as a `RandomAccessFile`, validates checksum compatibility and existing lengths for append/recovery, positions block and checksum streams, and returns `ReplicaOutputStreams`.

State and persistence: in-memory state includes `bytesAcked`, `bytesOnDisk`, `lastChecksum`, `writer`, `bytesReserved`, and `originalBytesReserved`. Persistent effects include appending/truncating block and meta files, restart meta file creation, and moving finalized files into an RBW location. Reservation methods mutate volume reserved-space and locked-memory accounting.

Dependencies and integration points: it depends on `ReplicaInPipeline`, `ReplicaOutputStreams`, `BlockMetadataHeader`, `DataChecksum`, `FsVolumeSpi`, `FileIoProvider`, `IOUtils`, and DataNode logging. `BlockReceiver` and recovery code use it while receiving packets and transitioning replicas.

Risks: `getVisibleLength` returns `-1`, so callers must use pipeline-specific bytes when serving in-progress data. `setBytesAcked` assumes monotonic progress; lower values would release negative space. `createStreams` creates a raw `RandomAccessFile(blockFile, "rw")` just to obtain an FD before wrapping, so failure cleanup is important. `createRestartMetaStream` uses `File.pathSeparator` in the constructed filename, which is unusual for a path component and deserves compatibility coverage.

Test signals: verify reserved-space release, wait timeout/signal behavior, writer CAS and stop timeout, append checksum mismatch rejection, corrupt length detection, stream positioning, restart meta deletion/recreation, move rollback when block rename fails, unsupported recovery methods, and `releaseAllBytesReserved` interaction with locked memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/LocalReplicaInPipeline.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ProfilingFileIoEvents.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ProfilingFileIoEvents.java

Purpose: `ProfilingFileIoEvents` records sampled latency and error metrics for DataNode metadata and data-file IO operations. `FileIoProvider` calls it before and after each wrapped operation.

Important APIs: `beforeMetadataOp` and `afterMetadataOp` time metadata operations. `beforeFileIo` samples data IO according to `sampleRangeMax`; `afterFileIo` records aggregate data IO latency plus operation-specific latencies for sync, flush, read, write, transfer, and native copy. `onFailure` records IO error latency. `setSampleRangeMax`, `getDiskStatsEnabled`, and `getSampleRangeMax` expose configuration/test behavior.

Control flow and state: the constructor reads `DFS_DATANODE_FILEIO_PROFILING_SAMPLING_PERCENTAGE_KEY`. `setSampleRangeMax` enables profiling through `Util.isDiskStatsEnabled`, caps percentages above 100 with a warning, and converts percentage to an `Integer.MAX_VALUE` sampling threshold. Metadata operations are not sampled once enabled; file IO is sampled by `ThreadLocalRandom`.

State and persistence: state is volatile `isEnabled` and `sampleRangeMax`. Metrics persist externally in each `DataNodeVolumeMetrics` instance reachable from the operation volume. A begin timestamp of `0` marks an unsampled or disabled operation and suppresses after-file metrics.

Dependencies and integration points: it depends on `FsVolumeSpi`, `DataNodeVolumeMetrics`, `FileIoProvider.OPERATION`, `DFSConfigKeys`, `Util`, and `Time`. It is created by `FileIoProvider` and therefore affects all provider-mediated disk operations.

Risks: `onFailure` records `Time.monotonicNow() - begin` even when `begin` is `0`, so disabled/unsampled failures can produce a large duration if `isEnabled` is true but begin was not captured. The file-IO sampling condition is a long line but functionally compares random integer to the configured threshold. Null volumes silently skip metrics. Percentages below or equal to zero disable stats through `Util`.

Test signals: validate percentage-to-threshold conversion for 0, normal, and >100 values; metadata latency when enabled; sampled and unsampled file IO; per-operation latency routing; null-volume no-op; and failure metrics when begin is zero/non-zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ProfilingFileIoEvents.java -->
