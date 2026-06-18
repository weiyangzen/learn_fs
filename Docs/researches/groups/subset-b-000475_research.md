# subset-b-000475 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemJournalEntryMerger.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemJournalEntryMerger.java

## Purpose
`FileSystemJournalEntryMerger` compacts file-system master journal entries during metadata sync and inode creation flows. Its main job is to merge an inode creation entry with later inode update entries for the same inode so journal replay has fewer redundant records while preserving non-mergeable updates.

## Important APIs, types, and functions
The class implements `JournalEntryMerger`. `add(JournalEntry)` accepts raw journal entries and performs on-the-fly compaction. `getMergedJournalEntries()` exposes an unmodifiable view of the merged list. `clear()` resets the in-memory merge state. `getInodeId()` extracts ids from supported inode create/update entry variants. It uses `MutableInodeFile` and `MutableInodeDirectory` to replay update fields onto a mutable inode representation before replacing the earlier entry.

## Control flow
Create entries for files and directories are appended and indexed by inode id. Later `UpdateInode`, `UpdateInodeFile`, and `UpdateInodeDirectory` entries are appended only when no earlier create entry exists. If an earlier create entry exists, the code reconstructs a mutable inode from the create entry, applies the update, and replaces the create entry in place. Directory `UpdateInode` entries with non-empty UFS fingerprints are both merged and appended because the generic directory update path cannot fully preserve directory fingerprint behavior.

## State and persistence behavior
State is purely in memory: `mJournalEntries` holds the current compacted sequence and `mEntriesMap` maps inode id to the sequence index. The persisted effect appears when the enclosing journal context flushes the merged entries. The class is annotated `@ThreadSafe` and all public mutation/access methods are synchronized, though the class comment still says it should not be shared across threads.

## Dependencies and integration points
It depends on Alluxio journal proto entries, inode mutable models, and the `JournalEntryMerger` abstraction. `InodeSyncStream` uses it through `MetadataSyncMergeJournalContext`, and journal tests reference it together with `FileSystemMergeJournalContext`.

## Risks
The supported entry set is narrow; unsupported entries sent to `getInodeId()` throw a runtime exception. Ordering matters because replacing an early create entry with a later-mutated create entry assumes no intervening journal entry requires the old metadata. The conflicting thread-safety documentation can mislead maintainers. Directory fingerprint handling is deliberately special-cased and easy to regress when journal proto fields change.

## Test signals
Signals are in journal-context merge tests and metadata-sync flush journal tests. Useful coverage should assert create-plus-update compaction, unmerged updates without prior create entries, directory fingerprint preservation, and replay equivalence of merged versus unmerged sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemJournalEntryMerger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMaster.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMaster.java

## Purpose
`FileSystemMaster` is the central service contract for the Alluxio file-system master. It defines the namespace, metadata, mount-table, active-sync, worker-heartbeat, permission, persistence, and metadata-sync operations implemented by `DefaultFileSystemMaster` and exposed through client, worker, and job-service RPC handlers.

## Important APIs, types, and functions
The interface extends `Master`. User-facing metadata APIs include `getFileId`, `getFileInfo`, `listStatus`, streaming `listStatus`, `checkAccess`, `exists`, `checkConsistency`, `createFile`, `createDirectory`, `completeFile`, `delete`, `rename`, `free`, `setAcl`, `setAttribute`, and `scheduleAsyncPersistence`. Block/file location APIs include `getNewBlockIdForFile`, `getFileBlockInfoList`, `getInAlluxioFiles`, and `getInMemoryFiles`. Mount APIs include `mount`, `unmount`, `updateMount`, `getMountPointInfoSummary`, `getDisplayMountPointInfo`, `getUfsInfo`, `getUfsAddress`, `reverseResolve`, and `updateUfsMode`. Worker and maintenance APIs include `workerHeartbeat`, `getWorkerInfoList`, `cleanupUfs`, `validateInodeBlocks`, `getLostFiles`, `getPinIdList`, `getInodeCount`, and time-series access. Sync APIs include active sync start/stop/list, `activeSyncMetadata`, `recordActiveSyncTxid`, `needsSync`, synchronous and asynchronous `syncMetadata`, progress lookup, and cancellation.

## Control flow
This file has no implementation flow, but its method signatures define the control path for the master. RPC handlers translate protobuf requests into `AlluxioURI` and operation context objects, then call these methods. Implementations are responsible for permission checks, inode locking, journaling, block-master coordination, UFS access, and metadata loading. Several methods have internal-server semantics and TODOs for permission enforcement.

## State and persistence behavior
The contract covers persistent namespace state: inode metadata, completed-file state, ACLs, pinning, TTLs, persistence state, mount points, UFS mode, active-sync points and transaction ids, and lost-file markers. Mutating implementations must journal changes and coordinate block deletions or worker commands. Methods returning summaries or views expose snapshots rather than ownership of mutable state.

## Dependencies and integration points
The interface is consumed by `DefaultFileSystemMaster`, `FileSystemMasterFactory`, client/worker/job gRPC service handlers, scheduler/job submission, active sync, async persistence, TTL/lost-file checkers, block master, and web/UI or internal services that use `FileSystemMasterView`. It depends on Alluxio wire types, gRPC option contexts, exception hierarchy, security ACL types, UFS mode, and metadata sync response protos.

## Risks
Because this is the service boundary, signature changes ripple across generated RPC layers, tests, workers, and job services. Methods mix user-facing and internal operations, and comments note missing permission checks for some internal APIs. Sync and active-sync operations cross thread pools, UFS clients, journals, and inode locks, making cancellation and partial failure semantics important. Backward compatibility matters for exceptions and default option behavior.

## Test signals
Coverage is spread through `DefaultFileSystemMaster` tests, sync metadata tests, partial listing tests, permission tests, worker heartbeat tests, mount tests, job-service handler tests, and RPC handler tests. Contract-level signals are compile failures in handlers and mock implementations such as journal test helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMaster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterAuditContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterAuditContext.java

## Purpose
`FileSystemMasterAuditContext` captures one file-system master operation for asynchronous user access audit logging. It accumulates authorization, success, identity, command, path, inode permission, timing, client-version, and protocol fields, then appends itself to an `AsyncUserAccessAuditLogWriter` when closed.

## Important APIs, types, and functions
The class implements `AuditContext`. Fluent setters include `setAllowed`, `setSucceeded`, `setCommand`, `setSrcPath`, `setDstPath`, `setUgi`, `setAuthType`, `setIp`, `setSrcInode`, `setCreationTimeNs`, and `setClientVersion`. `close()` computes elapsed time and submits the context to the async writer. `toString()` formats the audit line, including inode owner/group/mode when a source inode is available.

## Control flow
Callers create the context around an RPC, populate fields as permission checks and operations proceed, and close it after the operation. Closing is no-op when no writer is configured. Formatting branches on whether `mSrcInode` is present and on `USER_CLIENT_REPORT_VERSION_ENABLED` for including client version.

## State and persistence behavior
The context is not thread-safe and is intended for one operation. It does not persist metadata itself, but it emits audit records to the configured async log writer. The elapsed time is derived from `System.nanoTime()` minus the stored creation time.

## Dependencies and integration points
It depends on master audit interfaces, authentication type, inode metadata, permission mode extraction, `AlluxioURI`, and global configuration. It is integrated with `DefaultFileSystemMaster` audit-context creation and with `InodeSyncStream` when metadata loading wants the audit source inode populated after locking.

## Risks
Forgetting to set creation time yields misleading execution-time values. Missing source inode produces `perm=null`, which is expected for some paths but loses useful audit context. Because `toString()` pulls from mutable fields, reusing one instance across operations would corrupt logs. Client-version emission depends on global config at formatting time.

## Test signals
Audit-log tests should assert line formatting with and without source inode, success/allowed flags, optional client-version field, and close behavior when the writer is null. Integration signals come from RPC audit tests that validate operation-specific command and path fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterAuditContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterClientServiceHandler.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterClientServiceHandler.java

## Purpose
`FileSystemMasterClientServiceHandler` is the gRPC server adapter for client-facing file-system master RPCs. It converts protobuf requests into Alluxio domain objects and operation contexts, invokes `FileSystemMaster`, converts return values back to protobufs, and routes failures through `RpcUtils`.

## Important APIs, types, and functions
The class extends `FileSystemMasterClientServiceGrpc.FileSystemMasterClientServiceImplBase`. It implements RPCs for access checks, consistency checks, existence, complete/create/free/list/status, mount table operations, delete/rename, active sync, UFS mode updates, ACLs, state-lock holder introspection, metadata sync, and scheduler-backed job submission/progress/stop. `listStatus` uses `ListStatusResultStream`; `listStatusPartial` uses `ListStatusPartialResultStream`; `checkBucketPathExists` enforces S3 bucket-path existence when requested.

## Control flow
Most methods use `RpcUtils.call` with a lambda that builds an `AlluxioURI`, wraps request options in the matching context, calls the master, and builds the response. Streaming list calls use `RpcUtils.callAndReturn` so they can manage stream completion explicitly. Mount wraps exceptions with records from the `Recorder` so clients receive detailed diagnostics. Job submission deserializes a `JobRequest`, builds a job through `JobFactoryProducer`, and submits it to `Scheduler`.

## State and persistence behavior
The handler owns no persistent state beyond references to `FileSystemMaster` and `Scheduler`. Persistence effects are delegated to the master and scheduler. It does, however, attach `GrpcCallTracker` to contexts for long-running operations so cancellation can be observed by lower layers.

## Dependencies and integration points
It integrates generated gRPC protos, `GrpcUtils`, `RpcUtils`, `FileSystemMaster`, `Scheduler`, job factories, context classes, `PathUtils` for S3 bucket-path checks, and result-stream classes. It is the main transport boundary for Alluxio clients.

## Risks
Handlers must preserve option defaulting semantics; using `create` instead of `mergeFrom` is deliberate where request options are already client-specified. Streaming methods must avoid double-completing or calling `onNext` after `onError`; `listStatusPartial` currently calls `complete()` in `finally` even after `onError`, which relies on observer behavior and can be risky. Deserializing job requests from arbitrary bytes requires strict error handling. Logging entire requests may be expensive for large option payloads.

## Test signals
Useful tests mock `FileSystemMaster` and `Scheduler` to verify translation, option contexts, streaming batches, error propagation, bucket-path checks, job deserialization failures, and metadata-sync progress/cancel calls. Broader integration coverage comes from client RPC tests and partial listing tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterClientServiceHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterFactory.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterFactory.java

## Purpose
`FileSystemMasterFactory` creates and registers the core file-system master during master startup. It is the factory implementation used by the master registry to wire `DefaultFileSystemMaster` with its required block master and core context.

## Important APIs, types, and functions
The class implements `MasterFactory<CoreMasterContext>`. `isEnabled()` always returns true. `getName()` returns `Constants.FILE_SYSTEM_MASTER_NAME`. `create(MasterRegistry, CoreMasterContext)` retrieves `BlockMaster`, constructs `DefaultFileSystemMaster`, registers it under `FileSystemMaster.class`, and returns it.

## Control flow
Startup code invokes the factory, the factory logs creation, obtains the block master dependency from the registry, creates the default implementation, and adds it back to the registry for later lookup by RPC handlers and other services.

## State and persistence behavior
The factory has no mutable state. Persistence behavior is delegated to `DefaultFileSystemMaster` and the provided `CoreMasterContext`.

## Dependencies and integration points
It depends on `MasterRegistry`, `CoreMasterContext`, `BlockMaster`, Alluxio constants, and `DefaultFileSystemMaster`. It integrates with the master bootstrapping sequence and service registration.

## Risks
Factory creation assumes `BlockMaster` is already registered. Changing registration order or the registry key would break downstream lookups. Because `isEnabled()` is unconditional, disabling the file-system master requires a higher-level configuration mechanism rather than this factory.

## Test signals
Startup and registry tests should confirm the factory name, enabled status, block-master dependency lookup, registration of `FileSystemMaster.class`, and construction with the expected context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterJobServiceHandler.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterJobServiceHandler.java

## Purpose
`FileSystemMasterJobServiceHandler` is the gRPC adapter for calls made by the Alluxio job service to the file-system master. It exposes a small internal API for resolving file metadata and UFS mount information needed by jobs.

## Important APIs, types, and functions
The class extends `FileSystemMasterJobServiceGrpc.FileSystemMasterJobServiceImplBase`. `getFileInfo(GetFileInfoPRequest, StreamObserver)` returns proto `FileInfo` for a file id. `getUfsInfo(GetUfsInfoPRequest, StreamObserver)` returns proto `UfsInfo` for a mount id.

## Control flow
Each RPC extracts ids and options from the request, delegates to `FileSystemMaster`, converts the wire object with `GrpcUtils.toProto`, and wraps execution through `RpcUtils.call` for logging and error-to-gRPC translation.

## State and persistence behavior
The handler stores only the master reference and does not mutate persistent state. It reads current master metadata and mount information.

## Dependencies and integration points
It integrates generated job-service gRPC code, `RpcUtils`, `GrpcUtils`, and `FileSystemMaster`. It is consumed by job workers or job masters that need namespace and UFS context for distributed jobs.

## Risks
The file-id lookup is an internal call and depends on the master implementation for permission behavior. Options are currently logged but not used by handler logic, so future option semantics must be added explicitly. Stale file ids can return not-found errors to jobs.

## Test signals
Handler tests should verify successful proto conversion, propagated master exceptions, null-checking in the constructor, and that request options do not alter behavior unless intentionally supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterJobServiceHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterOptions.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterOptions.java

## Purpose
`FileSystemMasterOptions` centralizes master-side default option construction for file-system master operations. In this file it provides the default `CompleteFilePOptions` used when completing files.

## Important APIs, types, and functions
`completeFileDefaults()` builds `CompleteFilePOptions` with common options from `FileSystemOptionsUtils.commonDefaults(Configuration.global())` and sets `ufsLength` to zero.

## Control flow
There is no branching. Callers request defaults, then context classes such as `CompleteFileContext.mergeFrom` merge caller options over these defaults.

## State and persistence behavior
The class is stateless. Its behavior depends on global configuration at call time. The resulting options influence persisted completed-file metadata, especially common metadata options and UFS length handling.

## Dependencies and integration points
It depends on `Configuration`, `CompleteFilePOptions`, and `FileSystemOptionsUtils`. `CompleteFileContext` is the direct consumer.

## Risks
Changing defaults affects every complete-file path that uses merged defaults, including metadata-load completion. A default UFS length of zero is safe only when callers provide a real length where required.

## Test signals
Context tests should assert the default UFS length and common option defaults. Integration tests around complete-file behavior cover whether caller-provided values override these defaults correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterWorkerServiceHandler.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterWorkerServiceHandler.java

## Purpose
`FileSystemMasterWorkerServiceHandler` is the gRPC adapter for calls from Alluxio workers to the file-system master. It handles file-system heartbeats, file-info lookup, pinned file-id lookup, and UFS-info lookup.

## Important APIs, types, and functions
The class extends `FileSystemMasterWorkerServiceGrpc.FileSystemMasterWorkerServiceImplBase`. `fileSystemHeartbeat` sends persisted file ids to `FileSystemMaster.workerHeartbeat` and returns a `FileSystemCommand`. `getFileInfo` returns metadata for a file id. `getPinnedFileIds` returns the master pin set. `getUfsInfo` returns mount UFS information.

## Control flow
Each method extracts request fields, wraps options in the matching context where needed, calls `mFileSystemMaster`, converts results with `GrpcUtils`, and uses `RpcUtils.call` for response and error handling.

## State and persistence behavior
The handler is stateless apart from the master reference. Heartbeats may cause the master to mark persisted files and issue worker commands, but the state changes are delegated to the master implementation.

## Dependencies and integration points
It integrates generated worker-service gRPC code, `WorkerHeartbeatContext`, `RpcUtils`, `GrpcUtils`, and `FileSystemMaster`. It is part of the worker-to-master control plane for persistence and pinning.

## Risks
Heartbeat request sizes can be large when many files are persisted. The handler logs persisted file ids in the formatted request data, which can be noisy. Worker-visible command semantics depend on exact proto conversion of the master command.

## Test signals
Useful tests mock the master and assert heartbeat context construction, proto conversion of commands and file/UFS info, pinned ids, and error propagation through `RpcUtils`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterWorkerServiceHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/InodeSyncStream.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/InodeSyncStream.java

## Purpose
`InodeSyncStream` implements metadata synchronization between Alluxio inodes and mounted under file systems. It loads missing UFS metadata, updates inode attributes when UFS metadata changes, deletes Alluxio-only inodes when UFS entries disappear, recursively processes descendants, and maintains sync-path timestamps and metrics.

## Important APIs, types, and functions
The class exposes `sync()` returning `SyncStatus.OK`, `FAILED`, or `NOT_NEEDED`. Constructors accept a root `LockingScheme`, `DefaultFileSystemMaster`, sync cache, RPC context, descendant scope, common options, audit hooks, force/load flags, and absent-cache behavior. Core methods are `syncInternal`, `processSyncPath`, `syncInodeMetadata`, `syncExistingInodeMetadata`, `loadMetadataForPath`, `loadMetadata`, `loadFileMetadataInternal`, `loadDirectoryMetadata`, `loadMountPointDirectoryMetadata`, and `getMetadataSyncRpcContext`. `mergeCreateComplete` compacts file create/complete journal sequences.

## Control flow
`sync()` first checks `LockingScheme.shouldSync` and optionally acquires path-based metadata sync locks to deduplicate concurrent syncs. `syncInternal` records a sync start time, locks the root path, syncs it, then drains `mPendingPaths` through `mMetadataSyncService` up to configured concurrency. Existing inodes are compared with UFS fingerprints via `UfsSyncUtils.computeSyncPlan`; plans can update metadata, delete the inode Alluxio-only, load metadata, or queue children. Missing paths fetch `UfsStatus` and create file or directory metadata. Recursive loads prefetch child statuses, skip temporary files, and respect `DescendantType`.

## State and persistence behavior
The stream is per-sync-operation state: pending paths, submitted futures, status cache, sync counters, and journal context wrappers. Persistent effects go through `DefaultFileSystemMaster` internals and `RpcContext`: create directory/file, complete file, set attributes, delete internal, and set direct-children-loaded. It updates `UfsSyncPathCache` only on successful sync and may use `MetadataSyncMergeJournalContext` plus `FileSystemJournalEntryMerger` to flush merged inode journals asynchronously.

## Dependencies and integration points
It is tightly coupled to `DefaultFileSystemMaster`, `InodeTree`, `LockedInodePath`, `InodeLockManager`, `ReadOnlyInodeStore`, `MountTable`, UFS clients, `UfsStatusCache`, absent path cache, ACL objects, `UfsSyncUtils`, metrics, journal contexts, operation contexts, and configuration keys for traversal order, concurrency, sync interval, journaling, ACL, and prefetch. It backs explicit metadata sync RPCs, lazy path loading, active sync, and list/status flows.

## Risks
This is high-risk concurrency and persistence code. Callers must not hold conflicting inode write locks before `sync()`. Cancellation is cooperative and checked while waiting for UFS tasks and while draining jobs. Some child futures are cancelled after failure, so partial syncs can leave only some metadata refreshed. UFS status caching and ACL-dependent fingerprint construction must match UFS behavior. Journal merging must preserve replay equivalence. The code uses a shared `RpcContext` unless merge journaling creates wrapped contexts, so resource close and flush order matter. Configuration switches change traversal, load-only semantics, and failure reporting.

## Test signals
There are dedicated sync tests: metadata sync behavior, concurrent sync deduplication, flush-journal behavior, metrics, and journal context merge tests. Additional signals come from partial listing, metadata load, mount point, ACL, and UFS status cache tests. Strong coverage should include recursive UFS additions/deletions, changed mode/owner/group/fingerprint, missing UFS entries, persisted files under active persistence, cancellation, and both BFS/DFS traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/InodeSyncStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/InodeTtlChecker.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/InodeTtlChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/ListStatusPartial.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/ListStatusPartial.java

## Purpose
`ListStatusPartial` contains helper logic for paginated and prefix-filtered `listStatus` traversal. It validates offsets, converts `startAfter` and offset ids into path-component cursors, checks prefix compatibility, and selects inode-store child iterators that start at the correct point.

## Important APIs, types, and functions
Static helpers include `checkPartialListingOffset`, `computePartialListingPaths`, `checkPrefixListingPaths`, `getChildrenIterator`, and `hasPrefixComponentsCanBeLonger`. They operate on `ListStatusContext`, `ListStatusPartialPOptions`, `InodeTree`, `LockedInodePath`, `ReadOnlyInodeStore`, and path component lists.

## Control flow
Offset validation resolves the offset inode id back to component names and confirms it is under the requested listing path. Initial listings can use `startAfter`; absolute `startAfter` values are checked against the listing root before being converted to relative components. Prefix options are split into components and validated against non-initial partial cursors. Child iterator selection chooses among full child listing, prefix listing, listing from a cursor, or prefix-from-cursor listing based on options and traversal depth.

## State and persistence behavior
The class is stateless and does not mutate master state. It influences what metadata is read and how many results are returned by the surrounding listing implementation.

## Dependencies and integration points
It depends on inode tree path lookup, read-only inode-store child iterators, Alluxio path utilities, partial listing protobuf options, and `ListStatusContext` counters/truncation logic elsewhere. It is used by `DefaultFileSystemMaster` list traversal for partial listings.

## Risks
Cursor validation is subtle: offset ids can be stale, renamed, or outside the requested subtree. Prefix semantics intentionally allow the prefix to be longer than the cursor components if prior components match. Absolute and relative `startAfter` normalization must remain consistent with client expectations. Iterator choice assumes inode-store ordering by name.

## Test signals
`FileSystemMasterPartialListingTest` is the primary signal, with cases for offsets, `startAfter`, prefix filters, invalid offsets, truncation, nested directories, and missing paths. Unit tests for `hasPrefixComponentsCanBeLonger` and iterator selection help isolate edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/ListStatusPartial.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/ListStatusPartialResultStream.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/ListStatusPartialResultStream.java

## Purpose
`ListStatusPartialResultStream` collects a partial listing result and emits one `ListStatusPartialPResponse` containing file infos plus pagination metadata.

## Important APIs, types, and functions
The class implements `ResultStream<FileInfo>`. The constructor takes a gRPC `StreamObserver` and `ListStatusContext`, requiring partial options. `submit(FileInfo)` converts each item to proto and appends it. `onError(Throwable)` forwards errors. `complete()` sends file count, truncation flag, and collected file infos, then completes the observer.

## Control flow
Unlike normal list streaming, partial listing accumulates all results for the requested batch in memory. Batch size, when present, is used as initial `ArrayList` capacity. The caller invokes `submit` during traversal and always invokes `complete` after traversal.

## State and persistence behavior
State is per-RPC in `mInfos` and `mContext`. It does not persist data. Response metadata uses `ListStatusContext.getTotalListings()` and `isTruncated()`.

## Dependencies and integration points
It integrates with `FileSystemMasterClientServiceHandler.listStatusPartial`, `ListStatusContext`, generated partial-listing protos, `GrpcUtils`, and the master list traversal.

## Risks
The class is not synchronized, so traversal must call it from one thread. Calling `complete()` after `onError()` can violate gRPC observer expectations; the handler currently does this in a `finally` block. The response can be large if callers pass a large batch size.

## Test signals
Partial listing integration tests should verify file count, truncation, ordering, proto conversion, and error behavior. Direct tests can assert constructor failure when partial options are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/ListStatusPartialResultStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/ListStatusResultStream.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/ListStatusResultStream.java

## Purpose
`ListStatusResultStream` batches normal `listStatus` results into multiple gRPC `ListStatusPResponse` messages. It prevents very large directory listings from being returned as one response.

## Important APIs, types, and functions
The class implements `ResultStream<FileInfo>`. The constructor validates positive batch size and stores the client observer. `submit(FileInfo)` appends an item and flushes when the batch reaches the configured size. `complete()` flushes remaining results and calls `onCompleted`. `fail(Throwable)` calls `onError`. `toProto()` converts current `FileInfo` objects with `GrpcUtils.toProto`.

## Control flow
The stream starts active. `submit` and terminal methods are synchronized. `complete` and `fail` both set `mStreamActive` false in `finally`, preventing duplicate terminal events. `sendCurrentBatch` sends only non-empty batches and clears after send.

## State and persistence behavior
All state is per-RPC and in memory: current batch, batch size, observer, and active flag. The class does not persist metadata.

## Dependencies and integration points
It integrates with `FileSystemMasterClientServiceHandler.listStatus`, generated list-status protos, `GrpcUtils`, and streaming list traversal in `FileSystemMaster`.

## Risks
Backpressure is limited to gRPC observer behavior; the class does not await client demand. Proto conversion happens while synchronized, which can increase lock hold time for large batches. If `onNext` throws during `complete`, the stream still becomes inactive.

## Test signals
Tests should verify batching boundaries, final partial flush, no duplicate terminal events, error terminal behavior, and constructor rejection of non-positive batch sizes. Integration tests should cover large directory listings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/ListStatusResultStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/LostFileDetector.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/LostFileDetector.java

## Purpose
`LostFileDetector` is a heartbeat executor that consumes lost block reports from `BlockMaster` and marks affected non-persisted files as `LOST` in the file-system master metadata.

## Important APIs, types, and functions
The constructor stores `FileSystemMaster`, `BlockMaster`, and `InodeTree`, and registers the `MASTER_LOST_FILE_COUNT` metric. `heartbeat(long)` iterates `mBlockMaster.getLostBlocksIterator()`, maps each block id to a file id via `BlockId.getContainerId` and `IdUtils.createFileId`, collects candidate files, and journals `UpdateInodeEntry` persistence-state updates. `close()` is a no-op.

## Control flow
The first pass removes lost blocks from the block-master iterator while collecting unique non-persisted file ids. Missing inode paths are ignored. The second pass opens a journal context, write-locks each candidate inode, rechecks that it is not persisted, and updates persistence state to `LOST`.

## State and persistence behavior
The detector mutates persistent inode state through journaled `InodeTree.updateInode` calls. Lost block entries are removed from the block-master lost-block iterator before journal updates are flushed; a comment states this is acceptable because LOST status is currently display-only.

## Dependencies and integration points
It integrates heartbeat scheduling, block-master lost-block tracking, inode locking, file persistence state, journal contexts, and master lost-file metrics.

## Risks
Removing block candidates before journal durability can drop LOST marking after a crash. The second pass adds `fileId` back into `toMarkFiles` while iterating over that set, which is suspicious and could trigger concurrent modification behavior or reflect a simple leftover statement. The code intentionally does not mark persisted files lost. Large lost-block bursts can create large candidate sets in memory.

## Test signals
Tests should cover mapping lost blocks to files, skipping persisted files, missing inode removal, successful journaled LOST updates, unavailable journal handling, and the second-pass set mutation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/LostFileDetector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/MetadataSyncLockManager.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/MetadataSyncLockManager.java

## Purpose
`MetadataSyncLockManager` provides path-based read/write locks used to deduplicate or serialize metadata sync operations before corresponding inodes may exist. It locks path prefixes rather than inode objects.

## Important APIs, types, and functions
`lockPath(AlluxioURI)` returns a `MetadataSyncPathList`, acquiring read locks for every prefix and a write lock for the final path. `getLockPoolSize()` exposes the weak-value lock pool size for tests/metrics. Nested `MetadataSyncPathList` implements `Closeable` and releases locks in reverse order.

## Control flow
`lockPath` splits the URI path into components, builds normalized prefix keys ending in `/`, and obtains locks from `LockPool` in order. If any acquisition fails, it closes already-acquired locks. The caller uses try-with-resources to release the list.

## State and persistence behavior
The lock manager stores only in-memory lock-pool state. It does not persist metadata. Weak lock-pool values allow unused path locks to be reclaimed.

## Dependencies and integration points
It depends on `LockPool`, `LockMode`, configuration keys for pool sizing, `PathUtils`, and `LockResource`. `InodeSyncStream` uses a static instance when concurrent metadata sync deduplication is enabled.

## Risks
Path-key construction must be consistent for all callers or deduplication fails. The method catches `Throwable` but does not rethrow after cleanup in the catch block, so callers could receive a partially constructed list if an error path is not propagated by the thrown exception; this should be reviewed. Invalid path handling is covered by `PathUtils`. Prefix lock ordering avoids deadlocks only if all metadata sync callers use the same order.

## Test signals
`MetadataSyncLockManagerTest` covers pool sizing, invalid paths, lock compatibility, and garbage collection of weak locks. Concurrency tests with overlapping paths provide the most important integration signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/MetadataSyncLockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/NoopBlockDeletionContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/NoopBlockDeletionContext.java

## Purpose
`NoopBlockDeletionContext` is a null-object implementation of `BlockDeletionContext` for operations that should not register block deletions.

## Important APIs, types, and functions
It exposes singleton `INSTANCE`. `registerBlockForDeletion(long)` and `close()` intentionally do nothing.

## Control flow
There is no branching. Callers can pass the singleton wherever a block deletion context is required but no block-master cleanup should be performed.

## State and persistence behavior
The class is stateless and causes no persistence side effects. It is used by `RpcContext.NOOP` and read-only or test operations.

## Dependencies and integration points
It implements `BlockDeletionContext` and integrates with `RpcContext` construction.

## Risks
Using this context in a path that actually deletes inodes with blocks can leave orphaned blocks. Its safety depends entirely on caller intent.

## Test signals
Tests should verify it is accepted by `RpcContext` and that operations using it do not call block deletion. Most coverage is indirect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/NoopBlockDeletionContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/NoopUfsDeleter.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/NoopUfsDeleter.java

## Purpose
`NoopUfsDeleter` is a null-object `UfsDeleter` for delete operations that should not remove corresponding UFS entries, such as Alluxio-only deletes.

## Important APIs, types, and functions
It exposes singleton `INSTANCE` and implements `delete(AlluxioURI, Inode)` as an empty method.

## Control flow
The delete call returns immediately. Callers can use it to avoid conditional checks around optional UFS deletion.

## State and persistence behavior
It stores no state and does not mutate Alluxio or UFS data.

## Dependencies and integration points
It implements the local `UfsDeleter` interface and is used by delete internals when UFS deletion is disabled or unnecessary.

## Risks
Using the no-op deleter for a delete expected to propagate to UFS leaves UFS data intact. The singleton is thread-safe because it has no state.

## Test signals
Delete tests should assert Alluxio-only operations select no UFS deletion and that persisted deletes requiring UFS cleanup do not use this deleter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/NoopUfsDeleter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/PermissionChecker.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/PermissionChecker.java

## Purpose
`PermissionChecker` defines the authorization checks used by the file-system master against locked inode paths. It abstracts parent permission, direct permission, superuser checks, effective permission lookup, and set-attribute authorization.

## Important APIs, types, and functions
Methods are `checkParentPermission(Mode.Bits, LockedInodePath)`, `checkPermission(Mode.Bits, LockedInodePath)`, `checkSuperUser()`, `getPermission(LockedInodePath)`, and `checkSetAttributePermission(LockedInodePath, boolean, boolean, boolean)`.

## Control flow
Implementations inspect the current user, path inode metadata, owners/groups, ACLs, and requested mode bits. Parent checks fall back to the closest existing ancestor for missing paths and pass for invalid paths or root-like paths per interface comments.

## State and persistence behavior
The interface itself is stateless. Implementations read inode permission state and security context but do not normally mutate metadata.

## Dependencies and integration points
It depends on `LockedInodePath`, `Mode.Bits`, `AccessControlException`, and `InvalidPathException`. `DefaultFileSystemMaster` uses a concrete implementation to guard create, delete, rename, set-attribute, access-check, and listing operations.

## Risks
Interface comments define permissive behavior for invalid paths; implementations must match this exactly to avoid breaking create-on-missing-path flows. Set-attribute checks combine superuser, owner, and write requirements and are easy to weaken accidentally. Internal APIs in `FileSystemMaster` still note missing permission checks.

## Test signals
`PermissionCheckerTest` and file-system master permission tests should cover owner/group/other bits, ACLs, superuser/group membership, parent fallback, invalid paths, and set-attribute combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/PermissionChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/PersistJob.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/PersistJob.java

## Purpose
`PersistJob` is a value object representing an async persist job for one file. It tracks the file id, display URI, job id, temporary UFS path, retry timer, and cancellation state.

## Important APIs, types, and functions
The constructor initializes immutable job identity fields and sets `CancelState.NOT_CANCELED`. Getters expose file id, URI, job id, temp UFS path, timer, and cancel state. `setCancelState` mutates cancellation state. The nested `CancelState` enum has `NOT_CANCELED`, `TO_BE_CANCELED`, and `CANCELING`. `equals`, `hashCode`, and `toString` are implemented with Guava helpers.

## Control flow
The class has no job execution logic. Async persistence managers update cancellation state and use the timer to decide retries.

## State and persistence behavior
The object is in-memory and not thread-safe. It represents master scheduling state; any durable persistence of async persist state must happen in surrounding master code.

## Dependencies and integration points
It depends on `AlluxioURI` and `ExponentialTimer`. It integrates with async persist scheduling, worker polling, and retry/cancel code in the file-system master.

## Risks
The URI can be stale and is documented for logging only. Including mutable `ExponentialTimer` and mutable cancel state in equality/hash code can be dangerous if instances are used as map keys or set members. Concurrent access needs external synchronization.

## Test signals
Unit tests should cover equality/toString, cancel-state transitions, and scheduler behavior that uses timers and temp UFS paths. Integration tests should ensure stale URI does not drive correctness decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/PersistJob.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/ResultStream.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/ResultStream.java

## Purpose
`ResultStream<T>` is a minimal callback interface for streaming result items from master operations without requiring the operation to own the transport details.

## Important APIs, types, and functions
The only method is `submit(T item)`.

## Control flow
Producer code calls `submit` for each generated item. Implementations decide whether to buffer, batch, convert, or immediately forward items.

## State and persistence behavior
The interface has no state and no persistence behavior. Implementations such as list-status streams hold per-RPC buffers.

## Dependencies and integration points
It is used by `FileSystemMaster.listStatus` and implemented by `ListStatusResultStream` and `ListStatusPartialResultStream`.

## Risks
The interface has no terminal or error methods, so callers need concrete implementation knowledge for completion and failure. It also does not define threading or backpressure semantics.

## Test signals
Coverage is indirect through list-status streaming tests. Any new implementation should document synchronization and terminal behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/ResultStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/RpcContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/RpcContext.java

## Purpose
`RpcContext` aggregates per-RPC resources used by file-system master operations: journal appends, block deletion registration, operation metadata, and cancellation trackers. It enforces close order after an RPC finishes.

## Important APIs, types, and functions
The class implements `Closeable` and `Supplier<JournalContext>`. It exposes singleton `NOOP`, `getJournalContext`, `journal`, `getBlockDeletionContext`, `getOperationContext`, `throwIfCancelled`, `getOpId`, `isCancelled`, `close`, and `get`. `closeQuietly` collects close failures and suppresses secondary exceptions.

## Control flow
Operations receive an `RpcContext`, append journal entries with `journal` or `getJournalContext`, and register block deletions through the block deletion context. On close, the journal context closes first, then block deletion closes. If either close throws, the context rethrows `UnavailableException` where possible or wraps in `RuntimeException`.

## State and persistence behavior
The journal context is the persistence channel for namespace mutations. The explicit close order is important: file-system journal state is flushed before block-master cleanup so a crash is more likely to leave orphaned blocks than inodes pointing to missing blocks.

## Dependencies and integration points
It integrates `BlockDeletionContext`, `JournalContext`, `OperationContext`, `CallTracker`, `OperationId`, and many master internals. `InodeSyncStream`, delete/create operations, active sync journaling, and tests use it directly.

## Risks
The class is not thread-safe. Sharing one context across concurrent metadata sync tasks can be safe only when the underlying journal/operation contexts support it or when `InodeSyncStream` wraps merge contexts appropriately. `throwIfCancelled` throws a generic `RuntimeException`, so callers must convert or handle it consistently. Close failures from both contexts are aggregated but can hide operation-level exceptions if close happens in a finally block without suppression handling.

## Test signals
`RpcContextTest` covers close order, exception propagation/suppression, cancellation trackers, operation ids, and supplier behavior. Integration tests around delete and metadata sync validate journal-before-block cleanup ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/RpcContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/SafeUfsDeleter.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/SafeUfsDeleter.java

## Purpose
`SafeUfsDeleter` deletes persisted UFS entries for a subtree while avoiding recursive UFS deletes when Alluxio metadata is not known to be in sync with UFS contents.

## Important APIs, types, and functions
The constructor receives `MountTable`, inode store, the subtree inode list, and `DeletePOptions`. It may build a `UfsSyncChecker` and precheck persisted directories. `delete(AlluxioURI, Inode)` performs individual file deletes, recursive directory deletes only when safe, or rejects unsafe directory deletes. `isRecursiveDeleteSafe` checks whether a path is inside the deletion root and either unchecked or marked in sync.

## Control flow
Construction uses the first inode pair as deletion root. Unless delete is unchecked or Alluxio-only, it checks each persisted non-mount directory against UFS. During deletion, if the parent will be recursively deleted safely, the child is skipped. Files are deleted individually. Directories are recursively deleted only if that directory is safe; otherwise an IOException asks the user to sync UFS or delete unchecked.

## State and persistence behavior
The class holds the mount table, root path, and optional sync checker for one delete operation. It mutates external UFS state through `UnderFileSystem.deleteExistingFile` and `deleteExistingDirectory`. It does not mutate Alluxio inode state itself.

## Dependencies and integration points
It integrates delete internals in `DefaultFileSystemMaster`, `UfsSyncChecker`, `MountTable`, UFS resources, inode store, delete options, and mount-point detection.

## Risks
Recursive delete safety depends on accurate precomputed sync checks. Mount points are intentionally excluded from recursive directory checks to preserve mounted directories. Partial UFS recursive delete failures are noted as a TODO. Root-path prefix checks use string prefix matching, so path normalization must remain strict enough to avoid false containment.

## Test signals
Delete integration tests should cover unchecked deletes, Alluxio-only deletes, recursive safe/unsafe directories, mount points, missing UFS files/directories, and partial UFS failure behavior. Unit tests for `UfsSyncChecker` feed into confidence here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/SafeUfsDeleter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/UfsCleaner.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/UfsCleaner.java

## Purpose
`UfsCleaner` is a heartbeat executor that periodically asks the file-system master to clean up under-file-system resources.

## Important APIs, types, and functions
The constructor stores a `FileSystemMaster`. `heartbeat(long)` calls `mFileSystemMaster.cleanupUfs()`. `close()` does nothing.

## Control flow
The heartbeat framework invokes `heartbeat`; cleanup logic is entirely delegated to the master implementation.

## State and persistence behavior
The executor itself has no state beyond the master reference. Any UFS cleanup side effects and persistence bookkeeping are in `cleanupUfs()`.

## Dependencies and integration points
It depends on `HeartbeatExecutor` and `FileSystemMaster`. It is registered with master heartbeat scheduling.

## Risks
The executor ignores `timeLimitMs`, so cleanup duration is controlled only by the master implementation. Exceptions from `cleanupUfs()` would propagate according to heartbeat framework behavior.

## Test signals
Tests can verify heartbeat delegation. Integration coverage should assert that master startup registers the cleaner and that cleanup handles failures without destabilizing heartbeat threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/UfsCleaner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/UfsDeleter.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/UfsDeleter.java

## Purpose
`UfsDeleter` abstracts deletion of persisted UFS entries during Alluxio namespace deletion. It lets delete internals choose between safe UFS deletion and no-op deletion.

## Important APIs, types, and functions
The interface defines `delete(AlluxioURI alluxioUri, Inode inode)` which can throw `IOException` or `InvalidPathException`.

## Control flow
Delete internals call `delete` for each inode that may need UFS cleanup. Implementations decide whether to delete, skip because a parent recursive delete covers it, or fail.

## State and persistence behavior
The interface has no state. Implementations can mutate UFS state; they do not directly mutate Alluxio metadata.

## Dependencies and integration points
It depends on `AlluxioURI`, `Inode`, and UFS/delete exceptions. `SafeUfsDeleter` and `NoopUfsDeleter` are concrete implementations.

## Risks
The method receives an `Inode` but not a lock object, so callers must ensure inode/path consistency and locking. UFS deletion failures need to be coordinated with already-mutated Alluxio state by the surrounding delete transaction.

## Test signals
Delete tests should verify which implementation is selected for option combinations and how thrown exceptions affect master delete behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/UfsDeleter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/UfsSyncChecker.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/UfsSyncChecker.java

## Purpose
`UfsSyncChecker` checks whether persisted Alluxio directory metadata contains all direct children present in the corresponding UFS directory. It supports safe recursive UFS deletion by marking directories in sync only when UFS content is represented in Alluxio.

## Important APIs, types, and functions
The constructor stores `MountTable` and `ReadOnlyInodeStore`. `checkDirectory(InodeDirectory, AlluxioURI)` compares sorted UFS and Alluxio child names and records synced directories. `isDirectoryInSync(AlluxioURI)` queries the recorded result. Private `getChildrenInUFS` recursively lists UFS and caches listings by UFS URI; `trimIndirect` removes indirect descendants from recursive listing results.

## Control flow
`checkDirectory` requires a persisted directory, obtains UFS children, filters temporary names, sorts both sides, and advances through UFS children when a matching Alluxio child is found. If every UFS child is matched, the directory is recorded as synced. Otherwise ancestor synced markers are invalidated until a mount point boundary, and a debug message records the unmatched UFS child.

## State and persistence behavior
The checker is per-operation in-memory state. It caches recursive UFS listing arrays and synced directory markers. It does not mutate Alluxio or UFS state.

## Dependencies and integration points
It integrates with `SafeUfsDeleter`, `MountTable`, `ReadOnlyInodeStore`, UFS resources, `ListOptions.recursive`, `UfsStatus`, and path normalization utilities.

## Risks
The comparison checks that all UFS direct children are present in Alluxio, but extra Alluxio children do not make the directory unsafe. Recursive UFS listings are cached under the listed URI and reused for descendants, so path prefix trimming must be exact. Temporary-file filtering must match UFS temporary naming conventions. The class is not thread-safe.

## Test signals
Tests should cover matching/missing children, temporary files, directories with trailing separators, recursive listing reuse, mount-point ancestor invalidation, empty or null UFS listings, and extra Alluxio-only children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/UfsSyncChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/activesync/ActiveSyncManager.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/activesync/ActiveSyncManager.java

## Purpose
`ActiveSyncManager` manages active UFS sync points, polling threads, initial full sync tasks, and journaled active-sync state. It coordinates UFS event polling with file-system master metadata sync so mounted paths can stay current without only relying on lazy sync.

## Important APIs, types, and functions
The class implements `Journaled`. Public operations include `start`, `stop`, `startSyncAndJournal`, `stopSyncAndJournal`, `stopSyncForMount`, `getFilterList`, `getSyncPathList`, `setTxId`, `getExecutor`, recovery helpers, journal processing, reset, and checkpoint iterator methods. State maps track pollers by mount id, sync filters by mount id, starting tx ids, and initial sync futures by sync point. `launchPollingThread`, `startInitialFullSync`, `startSyncInternal`, and `stopSyncInternal` manage runtime tasks.

## Control flow
Starting the manager initializes UFS sync monitoring for all journaled sync points, launches polling threads for mounts with filters, and optionally starts initial full syncs when no valid tx id exists. Starting a sync point validates UFS support and duplicate coverage, applies and journals `AddSyncPointEntry`, then launches initial sync and polling; failures journal a removal and recover runtime state. Stopping applies and journals `RemoveSyncPointEntry`, cancels initial sync, stops polling when the last filter for a mount disappears, and tells UFS to stop monitoring the path.

## State and persistence behavior
Persistent state is journaled through add/remove sync-point entries and active-sync tx-id entries. `getJournalEntryIterator` checkpoints sync points plus tx ids. Runtime state lives in concurrent maps, a copy-on-write sync path list, futures, and a thread pool. `resetState` stops sync points for every mount using `RpcContext.NOOP`.

## Dependencies and integration points
It depends on `MountTable`, UFS active-sync APIs, `FileSystemMaster.activeSyncMetadata`, `recordActiveSyncTxid`, `ActiveSyncer`, heartbeat threads, retry policy configuration, journal/checkpoint APIs, server user state, and path utilities. Client RPC start/stop/list methods reach this through `FileSystemMaster`.

## Risks
The class is annotated not thread-safe but uses concurrent collections and a lock for some compound operations; all callers must respect locking for multi-step state transitions. `startInitialFullSync` captures a UFS resource in a submitted task while the try-with-resources scope closes after submission, so resource lifetime should be reviewed against the resource wrapper semantics. Failure recovery must keep journaled state and runtime futures/pollers consistent. `stop()` iterates while `stopSyncInternal` mutates maps/lists. Active sync support and tx-id replay are UFS-specific.

## Test signals
Tests should cover journal replay/checkpoint, duplicate sync-point rejection, unsupported UFS, start failure rollback, stop failure recovery, tx-id recording, restart with existing tx ids, initial sync enable/disable, and cleanup of futures/pollers when the last sync point for a mount is removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/activesync/ActiveSyncManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/activesync/ActiveSyncer.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/activesync/ActiveSyncer.java

## Purpose
`ActiveSyncer` is the heartbeat executor for one mount id. It consumes active-sync events from a UFS, submits metadata sync work for changed sync points, and records the processed transaction id after the work completes.

## Important APIs, types, and functions
The constructor stores `FileSystemMaster`, `ActiveSyncManager`, `MountTable`, mount id, mount URI, and creates a bounded queue of sync tasks. `heartbeat(long)` removes completed tasks, gets the mount filter list, reads `SyncInfo` from UFS, submits per-sync-point `CompletableFuture` work, and chains tx-id journaling. `close()` cancels queued sync tasks. `processSyncPoint` resolves UFS URIs back to Alluxio URIs and calls `activeSyncMetadata`.

## Control flow
Each heartbeat exits if no filters are registered or the UFS lacks active sync. Otherwise it processes every UFS sync point in `SyncInfo`. Force sync triggers full metadata sync for the resolved Alluxio path. Incremental sync maps changed UFS files through `MountTable.reverseResolve` and passes them to the master. The queued aggregate future records the tx id only after all per-sync futures complete.

## State and persistence behavior
Runtime state is the bounded queue of in-flight sync futures. Persistent active-sync progress is written indirectly through `FileSystemMaster.recordActiveSyncTxid`.

## Dependencies and integration points
It integrates with UFS active-sync APIs, `ActiveSyncManager` retry/executor/filter state, `FileSystemMaster.activeSyncMetadata`, mount reverse resolution, heartbeat scheduling, and configuration for heartbeat interval.

## Risks
The bounded queue can delay new task admission when prior syncs are slow. Reverse resolution returning null is handled for sync-point URI but changed-file mapping uses `Objects.requireNonNull`, so an unresolved changed file can fail the incremental task. Tx id is recorded after all tasks complete, so a single slow or failed task can delay progress. `timeLimitMs` is not directly enforced.

## Test signals
Tests should cover force versus incremental sync, unresolved UFS URIs, retry behavior, tx-id recording after completion, queue saturation, and cancellation in `close()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/activesync/ActiveSyncer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/async/AsyncPersistHandler.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/async/AsyncPersistHandler.java

## Purpose
`AsyncPersistHandler` defines how the file-system master schedules files for asynchronous persistence and how workers poll for persist tasks.

## Important APIs, types, and functions
The interface declares `scheduleAsyncPersistence(AlluxioURI)` and `pollFilesToPersist(long)`. Nested `Factory.create(FileSystemMasterView)` returns the default implementation, `DefaultAsyncPersistHandler`.

## Control flow
Master code schedules a path after validation. Workers later poll with their worker id and receive `PersistFile` descriptions for files assigned to them. The factory hides the implementation choice from callers.

## State and persistence behavior
The interface itself has no state. Implementations maintain scheduling state and read master metadata. Scheduling does not by itself persist file data; it creates work for workers.

## Dependencies and integration points
It depends on file-system master view, Alluxio exceptions, and wire `PersistFile`. It integrates with `FileSystemMaster.scheduleAsyncPersistence` and worker heartbeat or persist polling flows.

## Risks
Implementations must avoid assigning files to workers that do not have all required blocks. Polling and scheduling can race with file deletion, completion, and worker loss.

## Test signals
Tests should verify factory construction, scheduling of valid files, no assignment when no worker has all blocks, worker polling, and behavior when files disappear before polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/async/AsyncPersistHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/async/DefaultAsyncPersistHandler.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/async/DefaultAsyncPersistHandler.java

## Purpose
`DefaultAsyncPersistHandler` assigns async persist work to a worker that stores all blocks of the target file, then returns that work when the selected worker polls.

## Important APIs, types, and functions
The class implements `AsyncPersistHandler`. `scheduleAsyncPersistence(AlluxioURI)` selects a worker via `getWorkerStoringFile` and records the file id in `mWorkerToAsyncPersistFiles`. `pollFilesToPersist(long)` returns completed files assigned to the worker as `PersistFile` objects and removes those file ids from the assignment set.

## Control flow
For empty files, worker selection chooses any available worker at random. For non-empty files, it counts block locations and returns the first worker whose count equals the number of blocks, requiring all blocks on one worker. Polling skips nonexistent files, includes only completed files, gathers block ids, and removes only included file ids from the scheduled set.

## State and persistence behavior
Scheduling state is an in-memory `Map<Long, Set<Long>>` keyed by worker id. The class is synchronized around scheduling and polling. It does not journal its assignments; failures or master restart can lose pending async persistence assignments unless surrounding master code journals a higher-level state.

## Dependencies and integration points
It depends on `FileSystemMasterView` for file ids, file info, block info, paths, and worker lists. It integrates with worker persistence requests through `PersistFile` wire objects.

## Risks
Random worker selection creates a new `Random` per empty-file scheduling. Files whose blocks are spread across workers cannot be scheduled by this implementation. If `UnavailableException` occurs, scheduling silently returns invalid worker and logs or drops work. Assigned files that never complete remain in the worker set. The map can retain empty worker sets.

## Test signals
Tests should cover empty file assignment, no-worker behavior, single-worker all-block assignment, multi-worker split-block rejection, deletion before poll, incomplete file retention, completed file removal, and unavailable master-view calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/async/DefaultAsyncPersistHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CallTracker.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CallTracker.java

## Purpose
`CallTracker` abstracts cancellation detection for a master RPC or internal operation. It lets `OperationContext` and `RpcContext` discover that a client or state-lock tracker has cancelled the call.

## Important APIs, types, and functions
The interface declares `isCancelled()` and `getType()`. The nested `Type` enum distinguishes `GRPC_CLIENT_TRACKER` from `STATE_LOCK_TRACKER`.

## Control flow
Operation contexts collect trackers. `RpcContext.throwIfCancelled` asks the operation context for cancelled trackers and throws if any are cancelled.

## State and persistence behavior
The interface has no state and no persistence behavior. Implementations hold transport or lock-wait state.

## Dependencies and integration points
It is used by `OperationContext`, `GrpcCallTracker`, state-lock tracking, and long-running file-system operations such as metadata sync and list/status.

## Risks
The interface only reports a boolean, so cancellation reason and timing are limited to the tracker type. Callers must poll cancellation cooperatively; blocking UFS calls cannot be interrupted by this interface alone.

## Test signals
Tests should cover operation-context aggregation of trackers, `RpcContext.throwIfCancelled` messages, and handler attachment of `GrpcCallTracker` for long-running RPCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CallTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CheckAccessContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CheckAccessContext.java

## Purpose
`CheckAccessContext` wraps `CheckAccessPOptions` for file-system master access-check operations and provides master default merging.

## Important APIs, types, and functions
It extends `OperationContext<CheckAccessPOptions.Builder, CheckAccessContext>`. Static constructors are `create`, `mergeFrom`, and `defaults`. `toString()` includes built proto options.

## Control flow
RPC handlers usually call `create` from request options. Internal callers can use `mergeFrom` or `defaults` to combine caller options with `FileSystemOptionsUtils.checkAccessDefaults(Configuration.global())`.

## State and persistence behavior
The context stores mutable protobuf option builder state plus inherited operation metadata/call trackers. It does not mutate persistent metadata; it controls how `checkAccess` runs.

## Dependencies and integration points
It depends on global configuration, `CheckAccessPOptions`, `FileSystemOptionsUtils`, and `OperationContext`. It is passed to `FileSystemMaster.checkAccess`.

## Risks
Misusing `create` versus `mergeFrom` can skip master defaults. Since options are builder-backed, callers can mutate options after context creation if they retain references.

## Test signals
Context tests should assert default merging, `toString`, and operation metadata inheritance. RPC handler tests should verify correct context construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CheckAccessContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CheckConsistencyContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CheckConsistencyContext.java

## Purpose
`CheckConsistencyContext` wraps `CheckConsistencyPOptions` for namespace-versus-UFS consistency checks and provides default option merging.

## Important APIs, types, and functions
It extends `OperationContext<CheckConsistencyPOptions.Builder, CheckConsistencyContext>`. Static constructors are `create`, `mergeFrom`, and `defaults`. `toString()` renders the built proto options.

## Control flow
Client RPCs pass request options through `create`; internal calls can use defaults or merge user options over `FileSystemOptionsUtils.checkConsistencyDefaults(Configuration.global())`.

## State and persistence behavior
The context is per-operation mutable option state. The consistency check reads Alluxio and UFS metadata and returns inconsistent paths; this context does not persist state.

## Dependencies and integration points
It depends on configuration, consistency option protos, file-system option utilities, and `OperationContext`. It is passed to `FileSystemMaster.checkConsistency`.

## Risks
Default drift changes consistency-check behavior globally. Builder-backed options should not be shared across threads. The file contains a minor formatting inconsistency in `toString`, but no behavioral issue.

## Test signals
Tests should verify default merging and check-consistency behavior for recursive or option-dependent scans. Handler tests should confirm request option propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CheckConsistencyContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CompleteFileContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CompleteFileContext.java

## Purpose
`CompleteFileContext` wraps `CompleteFilePOptions` and carries extra master-only state for completing files, including operation time, UFS status, and whether completion comes from metadata loading.

## Important APIs, types, and functions
It extends `OperationContext<CompleteFilePOptions.Builder, CompleteFileContext>`. Static constructors are `create`, `mergeFrom`, and `defaults`. Extra methods include `setMetadataLoad`, `isMetadataLoad`, `getUfsStatus`, `setUfsStatus`, `getOperationTimeMs`, `setOperationTimeMs`, and an override of `getOperationId` that reads common proto operation id first.

## Control flow
The constructor initializes operation time to current system time and UFS status to null. `mergeFrom` overlays caller options on `FileSystemMasterOptions.completeFileDefaults()`. Metadata sync uses the context with UFS length/status and metadata-load flag after creating a file from UFS metadata.

## State and persistence behavior
The context influences persisted completed-file metadata, including UFS length, operation time, metadata-load flag, and common TTL/operation options. It does not journal directly; callers pass it into master internals that journal completion.

## Dependencies and integration points
It depends on complete-file protos, `FileSystemMasterOptions`, `UfsStatus`, `OperationId`, and `OperationContext`. `InodeSyncStream.loadFileMetadataInternal` is a key integration point.

## Risks
`toString()` calls `mUfsStatus.toString()` without a null check, so logging a default context can throw `NullPointerException`. Operation time uses wall-clock time by default, while metadata loads may override with UFS last-modified time. Correct operation-id propagation depends on common options being set.

## Test signals
Tests should cover default/merged options, metadata-load flag, operation-id override, UFS status handling, and the null-status `toString()` edge case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CompleteFileContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CreateDirectoryContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CreateDirectoryContext.java

## Purpose
`CreateDirectoryContext` wraps `CreateDirectoryPOptions` and extends create-path context state for directory creation, including UFS status and default ACLs used when loading directory metadata from UFS.

## Important APIs, types, and functions
It extends `CreatePathContext<CreateDirectoryPOptions.Builder, CreateDirectoryContext>`. Static constructors are `create`, `mergeFrom`, and `defaults`. Extra methods include `getUfsStatus`, `setUfsStatus`, `setDefaultAcl`, `getDefaultAcl`, and an override of `getOperationId` that checks common proto options first. `toString()` includes path context and UFS status.

## Control flow
`mergeFrom` overlays caller options on `FileSystemOptionsUtils.createDirectoryDefaults(Configuration.global(), false)`. Metadata load code populates owner, group, xattrs, mode, mount-point flag, write type, ACL, default ACL, and UFS status before calling create-directory internals.

## State and persistence behavior
The context controls persisted directory metadata: mode, owner/group, ACL/default ACL, xattrs, TTL/common options, mount-point flag, write type, and operation time inherited from create-path context. The context itself is in-memory and per operation.

## Dependencies and integration points
It depends on create-directory protos, configuration defaults, `CreatePathContext`, ACL entries, `UfsStatus`, and `OperationId`. It is used by client create-directory RPCs and by `InodeSyncStream.loadDirectoryMetadata`.

## Risks
`mDefaultAcl` defaults to null, so consumers must distinguish absent default ACL from empty default ACL. As with other contexts, builder-backed options are mutable. Using `create` rather than `mergeFrom` can skip master defaults. Metadata-load callers must set UFS-derived fields consistently to avoid mismatched Alluxio/UFS metadata.

## Test signals
Tests should cover default merging, operation-id override, default ACL copying/immutability, metadata-load directory creation, mount-point creation, and null versus empty default ACL behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CreateDirectoryContext.java -->
