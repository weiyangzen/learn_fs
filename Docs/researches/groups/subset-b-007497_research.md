# subset-b-007497 Research

Grouped source research for HDFS NameNode namespace directory state and edit-log persistence/replay. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirectory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirectory.java

## Purpose

`FSDirectory.java` is the NameNode's in-memory namespace directory manager. Its class comment draws the key boundary: `FSDirectory` keeps namespace state in memory, while `FSNamesystem` persists operations through the edit log. The file owns the root `INodeDirectory`, inode ID allocation, the `INodeMap`, reserved path resolution, quota accounting, filesystem limit checks, access-control integration, encryption-zone indexing, storage-policy satisfier hooks, and helper APIs used by operation-specific classes such as `FSDirWriteFileOp`, `FSDirDeleteOp`, `FSDirRenameOp`, and `FSDirAttrOp`.

The source was read as a complete 2104-line file for this report.

## Important APIs, Types, and Functions

Core type/state: `FSDirectory implements Closeable`; `DirOp` controls path resolution behavior for read/write/create and symlink-following variants; `rootDir`, `namesystem`, `inodeMap`, `inodeId`, `editLog`, `ezManager`, `nameCache`, `protectedDirectories`, permission/ACL/xattr/quota configuration flags, and reserved path constants for `/.reserved`, `/.reserved/raw`, and `/.reserved/.inodes`.

Initialization and configuration APIs: `FSDirectory(FSNamesystem, Configuration)` builds the root inode, reads NameNode config, initializes `INodeMap`, permissions, ACL/xattr limits, list/content-summary limits, protected directories, access-time precision, quota-by-storage-type support, name cache, edit-log pointer, encryption-zone manager, quota init threads, and external attribute-provider bypass users. `createReservedStatuses`, `parseProtectedDirectories`, `setProtectedDirectories`, `setMaxDirItems`, and feature getters expose this configuration.

Path and inode APIs: `resolvePath`, `unprotectedResolvePath`, static `resolvePath`, `getINodesInPath`, `getINode`, `getINode4Write`, `resolveComponents`, `resolveDotInodesPath`, `constructRemainingPath`, `getINode4DotSnapshot`, and `resolveLastINode`. These are central to all namespace operations.

Mutation and quota APIs: `addINode`, `addLastINode`, `addLastINodeNoQuotaCheck`, `removeLastINode`, `updateCountForQuota`, `updateSpaceConsumed`, the overloaded `updateCount` methods, `updateCountForDelete`, `unprotectedUpdateCount`, `verifyQuota`, `updateSpaceForCompleteBlock`, and `getStorageTypeDeltas`.

Validation/security APIs: `verifyINodeName`, `verifyMaxComponentLength`, `verifyMaxDirItems`, `isValidToCreate`, `verifyParentDir`, `getPermissionChecker`, `checkOwner`, `checkPathAccess`, `checkParentAccess`, `checkAncestorAccess`, `checkTraverse`, `checkPermission`, `checkUnreadableBySuperuser`, and `getAttributes`.

Indexing and lifecycle APIs: `addToInodeMap`, `removeFromInodeMap`, `getInode(long)`, `reset`, `cacheName`, `shutdown`, `allocateNewInodeId`, `getLastInodeId`, `resetLastInodeId`, and `resetLastInodeIdWithoutChecking`.

## Control Flow

Construction initializes a root directory with default quota and snapshottable feature, loads configuration gates, records the owning `FSNamesystem`, and grabs the edit-log instance from it. `readLock`, `writeLock`, and matching unlock methods are now assertions over `FSNamesystem`'s FS lock, so callers are expected to hold the appropriate `FSNamesystem` lock before mutating or reading namespace state.

Client-visible path resolution flows through `resolvePath(pc, src, dirOp)`: create operations first validate path syntax; components are converted from the string path; reserved raw or inode paths are rewritten by `resolveComponents`; `INodesInPath.resolve` builds the inode chain; raw write/create operations require superuser privilege; `checkTraverse` enforces ancestry, symlink, snapshot, and optional permission checks according to `DirOp`.

Internal replay and helper paths often use `getINodesInPath` or `unprotectedResolvePath`, which deliberately skip reserved-path expansion or permission checks as documented. This split matters because edit-log replay must rebuild exact namespace state while normal RPC paths must enforce user permissions and snapshot read-only behavior.

Adding an inode goes through name caching, filesystem limit checks, reserved-name checks, quota calculation, `updateCount`, `parent.addChild`, default ACL inheritance, and `addToInodeMap`. If `parent.addChild` fails, quota deltas are rolled back. Removing a last inode delegates child removal to the parent and then handles snapshot/reference semantics with `INodeReference.tryRemoveReference`.

Quota initialization is parallelized by `InitQuotaTask` over the directory tree. Runtime quota changes build `QuotaCounts`, optionally verify each quota-bearing ancestor, then update cached counts. Deletion and block-completion paths adjust namespace, storage-space, and storage-type quotas to reflect snapshots, erasure coding, and replication.

## State and Persistence Behavior

`FSDirectory` itself is memory-resident. Persistent durability is indirect: operation classes mutate this structure under `FSNamesystem` locks and separately log durable edits through `FSEditLog`. During image/edit loading, `skipQuotaCheck`, `namesystem.isImageLoaded()`, and `resetLastInodeId` alter behavior so old or partially loaded persisted state can be reconstructed before runtime checks become strict.

The persistent identity state is the inode ID counter. `allocateNewInodeId` advances it for new namespace objects, while loader code calls `resetLastInodeId` as edit-log inode IDs are replayed. The `INodeMap` is the runtime lookup index for inode IDs and supports reserved `/.reserved/.inodes/<id>` paths.

Encryption-zone and storage-policy satisfier state is discovered from inode xattrs when inodes enter the map. `addEncryptionZone` parses the crypto xattr protocol buffer and registers the zone and optional re-encryption status with `EncryptionZoneManager`; `removeFromInodeMap` removes associated encryption-zone entries. This means xattr changes and inode-map changes must stay coordinated.

Name caching is an in-memory heap optimization for file local-name byte arrays. It is initialized after load with `markNameCacheInitialized` and reset on namespace reset/shutdown.

## Dependencies and Integration Points

Primary integration is with `FSNamesystem`, which owns locking, persistence orchestration, block management, lease management, audit state, and external invocation context. `FSEditLog` is retained for operation classes that need to log after directory mutation.

Namespace model dependencies include `INode`, `INodeDirectory`, `INodeFile`, `INodeMap`, `INodesInPath`, `DirectoryWithQuotaFeature`, `QuotaCounts`, snapshot classes, ACL and xattr storage, and HDFS protocol status/exception classes.

Storage dependencies include `BlockManager`, `BlockStoragePolicySuite`, `BlockStoragePolicy`, `BlockInfo`, `BlockInfoStriped`, storage type counters, erasure-coding policy lookup, and storage-policy satisfier manager.

Security dependencies include `FSPermissionChecker`, `INodeAttributeProvider`, `UserGroupInformation`, `FsAction`, ACL support, superuser checks, `SECURITY_XATTR_UNREADABLE_BY_SUPERUSER`, and external authorization provider compatibility detection.

Reserved path handling integrates with HDFS semantics for `/.reserved/raw` encryption-zone raw access and `/.reserved/.inodes` inode-ID lookup. Audit status generation integrates with `FileStatus`, symlink targets, file size/replication, and snapshot attributes.

## Risks and Edge Cases

Locking is assertion-based in this class; real exclusion depends on correct `FSNamesystem` lock discipline by every caller. Missing a write lock can corrupt inode trees, quota caches, or inode maps.

Reserved path rewriting is subtle. `/.reserved/raw/.reserved` intentionally does not strip the raw prefix, `/.reserved/.inodes/<id>/..` supports NFS parent lookup, and invalid inode IDs throw `FileNotFoundException`. Changes here risk security bypasses or broken compatibility.

Quota behavior differs during startup/replay versus runtime. Several filesystem limit violations log instead of throw before image load completes. Bugs in `skipQuotaCheck`, rollback after failed add, or snapshot-aware delete accounting can leave quota caches inconsistent.

`addToInodeMap` has side effects beyond indexing: it registers encryption zones and storage-policy satisfier xattrs. Bypassing it, or removing inodes without `removeFromInodeMap`, can leak security/storage state.

Permission checks intentionally treat superusers specially by calling external enforcers for audit and by respecting `unreadableBySuperuser` xattrs. Any shortcut around `resolvePath`/`checkPermission` can miss external provider policy or audit behavior.

## Test Signals

Useful coverage includes path-resolution tests for normal paths, symlinks, snapshots, `/.reserved/raw`, `/.reserved/.inodes`, invalid IDs, and NFS-style `..`; lock/assertion tests around callers that mutate namespace; quota initialization and delta tests for create/delete/rename/snapshot/replication/erasure-coded files; ACL default inheritance tests with masked/unmasked create modes; xattr/encryption-zone registration and removal tests; protected-directory parsing and delete behavior; permission and external attribute-provider tests, including bypass users, superuser audit, and unreadable-by-superuser denial; and edit-log replay tests that confirm startup leniency does not persist after `isImageLoaded`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirectory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSEditLog.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSEditLog.java

## Purpose

`FSEditLog.java` is the NameNode edit-log writer and reader selector. It maintains the transaction ID stream for namespace mutations, writes `FSEditLogOp` records to a `JournalSet`, syncs edits durably, manages edit-log segment lifecycle, exposes manifests and input streams for recovery/standby/checkpoint readers, and supports local, shared, backup, and plugin journal managers.

The source was read as a complete 1929-line file for this report.

## Important APIs, Types, and Functions

Core state: private `State` enum (`UNINITIALIZED`, `BETWEEN_LOG_SEGMENTS`, `IN_SEGMENT`, `OPEN_FOR_READING`, `CLOSED`), `journalSet`, `editLogStream`, monotonically increasing `txid`, last synced `synctxid`, current segment start `curSegmentTxId`, `isSyncRunning`, `isAutoSyncScheduled`, metrics counters, `NNStorage`, `Configuration`, edit directories, shared edit directories, operation cache, proxy users, and `journalSetLock`.

Construction/initialization: `newInstance` chooses `FSEditLogAsync` when `dfs.namenode.edits.async.logging` is enabled. `initJournalsForWrite`, `initSharedJournalsForRead`, and `initJournals` build a `JournalSet` with file journals or plugin journals and required/shared flags.

Write/sync core: `openForWrite`, `logEdit(FSEditLogOp)`, `doEditTransaction`, `beginTransaction`, `endTransaction`, `logSync`, `logSync(long)`, `logSyncAll`, `waitIfAutoSyncScheduled`, `doneWithAutoSyncScheduling`, `waitForSyncToFinish`, `getLastWrittenTxId`, `setNextTxId`, `getSyncTxId`, and metrics helpers.

Operation logging APIs: `logOpenFile`, `logCloseFile`, `logAppendFile`, `logAddBlock`, `logUpdateBlocks`, `logMkDir`, rename overloads, `logSetReplication`, `logSetStoragePolicy`, `logSetQuota`, `logSetQuotaByStorageType`, `logSetPermissions`, `logSetOwner`, `logConcat`, `logDelete`, `logTruncate`, generation stamp/block ID logging, `logTimes`, `logSymlink`, delegation token/master key logging, `logReassignLease`, snapshot logging, cache directive/pool logging, rolling upgrade logging, ACL/xattr logging, and erasure-coding policy logging.

Segment/journal lifecycle: `rollEditLog`, `startLogSegment`, `startLogSegmentAndWriteHeaderTxn`, `endCurrentLogSegment`, `abortCurrentLogSegment`, `purgeLogsOlderThan`, `recoverUnclosedStreams`, shared-log upgrade/finalize/rollback methods, `discardSegments`, backup node registration and release, `journal` for raw backup-node batches, and `logEdit(int, byte[])`.

Read selection/plugin APIs: `selectInputStreams` overloads, `checkForGaps`, `closeAllStreams`, `getEditLogManifest`, `getJournalClass`, `createJournal`, `getJournals`, `getJournalSet`, and test hooks.

## Control Flow

The write lifecycle begins in `UNINITIALIZED`, calls `initJournalsForWrite`, enters `BETWEEN_LOG_SEGMENTS`, then `openForWrite` verifies there is no readable stream at the next transaction ID before starting a segment and writing an `OP_START_LOG_SEGMENT` header transaction. While `IN_SEGMENT`, each operation-specific `log*` method populates an `FSEditLogOp`, optionally records RPC IDs for retry-cache reconstruction, and delegates to `logEdit`.

Synchronous `logEdit` is synchronized while assigning the next transaction ID and writing to the in-memory edit-log stream. If the stream's policy requests a forced sync, the caller marks `isAutoSyncScheduled`, exits the synchronized block, and calls `logSync`. Other writers wait while an auto sync is scheduled to preserve ordering around forced flushes.

`logSync(long)` implements the double-buffered sync protocol. Under the monitor, it waits for any active sync that already covers the caller's txid, sets `isSyncRunning`, captures `editLogStream`, checks journal availability, and calls `setReadyToFlush`. Outside the monitor it flushes to the journals. In `finally`, it updates `synctxid`, updates file-journal readable txid, clears `isSyncRunning`, and notifies waiters. Fatal inability to sync enough journals terminates the NameNode.

Rolling a log ends the current segment by optionally logging `OP_END_LOG_SEGMENT`, calling `logSyncAll`, asserting last-written equals last-synced, finalizing the segment in `JournalSet`, and returning to `BETWEEN_LOG_SEGMENTS`; then it starts the next segment and writes a header transaction.

Standby/checkpoint/recovery readers call `selectInputStreams`, which asks `JournalSet` for streams under `journalSetLock`, then checks that selected ranges cover the requested interval unless recovery mode allows gaps.

## State and Persistence Behavior

The durable state is a sequence of edit-log transactions spread across configured journals. `txid` advances before each write, `synctxid` advances only after successful flush, and `curSegmentTxId` names the in-progress segment. The thread-local `myTransactionId` lets each caller sync only through the edits it produced, while sync batching may flush additional transactions.

`JournalSet` abstracts multiple journal destinations and enforces the minimum redundant journals policy. Local `FileJournalManager` instances are tied to `NNStorage` directories; non-file journal managers are plugin-created from configuration; backup journals stream edits to backup NameNodes. Shared journals support HA standby reading and upgrade/rollback methods.

RPC IDs are persisted into selected operations when requested so edit-log replay can rebuild retry-cache entries and preserve idempotent client semantics after failover or restart.

Segment records (`OP_START_LOG_SEGMENT`, `OP_END_LOG_SEGMENT`) make log boundaries explicit. Purging is allowed only while open for write to avoid standby NameNodes deleting shared edits.

## Dependencies and Integration Points

`FSEditLog` depends on `FSEditLogOp` and its many concrete op types for serialization payloads. It integrates with `JournalSet`, `JournalManager`, `FileJournalManager`, `BackupJournalManager`, `EditLogOutputStream`, `EditLogInputStream`, `RemoteEditLogManifest`, and `LogsPurgeable`.

NameNode integration includes `NNStorage`, `FSNamesystem` edit/shared directory configuration, `NamespaceInfo`, `NamenodeRegistration`, `NameNodeMetrics`, `NameNode.getClientIdAndCallId`, `ExitUtil.terminate`, and storage upgrade/finalize/rollback hooks.

Namespace integration comes from the operation log methods accepting `INodeFile`, `INode`, blocks, ACLs, xattrs, snapshots, cache directives/pools, delegation tokens, storage policies, and erasure-coding policies. The paired `FSEditLogLoader` replays these op types into `FSDirectory`, `BlockManager`, and other managers.

## Risks and Edge Cases

The state machine is strict. Starting a segment at the wrong txid, opening for write when newer readable streams exist, or reducing txid via `setNextTxId` is guarded because any violation risks edit-log fork or data loss.

Sync failure is intentionally fatal when not enough journals can flush. Tests that mock journals need to account for `ExitUtil.terminate` behavior. The unsynchronized flush window is safe only because callers needing isolation call `waitForSyncToFinish`.

`isAutoSyncScheduled` prevents writes from racing ahead of a forced sync, but bugs around `doneWithAutoSyncScheduling` can block writers. The code uses `finally` to avoid runtime exceptions leaving the flag set.

Read stream selection assumes sorted, non-overlapping ranges from `JournalSet`; `checkForGaps` is deliberately simple and will reject missing txids unless recovery mode is active. In-progress streams have unknown end txid and are accepted only when allowed.

Plugin journal construction is reflection-based and supports two constructor signatures. Misconfiguration fails at runtime with `IllegalArgumentException`.

## Test Signals

Useful coverage includes state-machine tests for initialization, open, close, roll, abort, and recovery; transaction ID monotonicity and `setNextTxId` validation; multi-threaded log/sync batching tests; forced-sync scheduling tests; journal quorum failure tests that assert termination or exception behavior; segment finalization and purge tests; HA shared-edits input stream selection and gap detection; backup-node raw journal batch tests; plugin journal constructor tests; retry-cache RPC ID logging checks; and operation serialization/replay round trips with `FSEditLogLoader`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSEditLog.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSEditLogAsync.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSEditLogAsync.java

## Purpose

`FSEditLogAsync.java` is an asynchronous subclass of `FSEditLog`. It decouples RPC handler threads from edit-log disk flush latency by queueing edits to a background sync thread. For normal RPC calls, the server response is postponed and later sent by the sync thread after the corresponding edit becomes durable.

The source was read as a complete 401-line file for this report.

## Important APIs, Types, and Functions

Core state: `syncThreadLock`, `syncThread`, thread-local `THREAD_EDIT`, bounded `editPendingQ`, sync-thread-only `syncWaitQ`, `lastFull`, and an overflow-throttling `Semaphore` with custom drain/release behavior.

Lifecycle APIs: constructor disables the inherited operation instance cache and sizes the pending queue from `DFS_NAMENODE_EDITS_ASYNC_LOGGING_PENDING_QUEUE_SIZE`; `openForWrite` starts the sync thread before delegating to `super.openForWrite`; `close` closes the superclass and stops the thread; `restart` restarts the thread for tests/spies.

Logging APIs: overridden `logEdit`, `logSync`, and `logSyncAll`; internal `enqueueEdit`, `dequeueEdit`, `run`, `terminate`, and `getEditInstance`.

Nested types: abstract `Edit` wraps an op and `FSEditLog`; `SyncEdit` blocks the calling thread until durable; `RpcEdit` postpones and later sends/aborts the current `Server.Call` response.

## Control Flow

When async logging is enabled, `FSEditLog.newInstance` constructs this class. `openForWrite` starts a `SubjectInheritingThread` running `run`, then opens the underlying edit log.

`logEdit(op)` creates either a `RpcEdit` or `SyncEdit`, stores it in `THREAD_EDIT`, then under the inherited edit-log monitor enqueues it and calls `beginTransaction(op)` to assign the txid. Unlike the synchronous superclass, actual stream write is performed later by the background thread.

`logSync()` looks up the caller's thread-local edit. For a `SyncEdit`, it waits until the background thread has written and synced it. For a `RpcEdit`, `logSyncWait` is intentionally a no-op so the RPC handler can return to the server pool while the response remains postponed.

The sync thread loops over `dequeueEdit`. It writes each edit by calling `edit.logEdit()`, which delegates to `doEditTransaction(op)`, then places the edit on `syncWaitQ`. It flushes when the edit stream requests sync or when the pending queue runs dry while edits await durability. On sync, it calls inherited `logSync(getLastWrittenTxId())`, then notifies every queued edit with either success or the captured runtime exception.

Queue overflow handling first tries a nonblocking offer. If full, it verifies the sync thread is alive, logs at most every four seconds, and either waits while releasing the edit-log monitor if the caller holds it or uses the overflow semaphore to throttle non-monitor callers.

## State and Persistence Behavior

Persistent state is still owned by `FSEditLog` and its journals. This class changes timing: txids are assigned in caller threads, but edit records and flushes are performed by the background thread. The inherited op cache is disabled because queued operations cannot safely share reusable op instances before serialization completes.

For RPC calls, durability controls response emission. `RpcEdit` calls `Server.Call.postponeResponse` on creation, then `sendResponse` after successful sync or `abortResponse` if sync failed. Thus the client observes completion after durability even though the RPC handler thread was released earlier.

`logSyncAll` enqueues a synthetic `SyncEdit` whose `logEdit` returns true without writing a new op, forcing the background queue to drain before returning.

## Dependencies and Integration Points

This class integrates tightly with superclass internals: `beginTransaction`, `doEditTransaction`, `logSync(long)`, `getLastWrittenTxId`, and the inherited monitor. It depends on `Server.getCurCall` and `Server.Call` for asynchronous RPC response handling, `SubjectInheritingThread` for thread context, `NameNodeMetrics` for pending edit counts, and `ExitUtil.terminate` for fatal background failures.

Configuration integration is through `DFS_NAMENODE_EDITS_ASYNC_LOGGING` in `FSEditLog.newInstance` and queue-size configuration in this constructor.

## Risks and Edge Cases

Deadlock avoidance is central. If the pending queue fills while the caller holds the edit-log monitor, the code waits and re-offers while temporarily releasing that monitor so the sync thread can enter `doEditTransaction` and `logSync`.

Thread-local `THREAD_EDIT` must be cleared in `logSync`; otherwise a later call could wait on the wrong edit. The implementation sets it to null rather than removing it to avoid thread-local map churn.

RPC calls only become async when there is a current `Server.Call` and the caller does not already hold the edit-log monitor. Log rolling and explicit synchronized callers use `SyncEdit` to preserve coordination.

The background thread is a single point of progress. Enqueue failure, unexpected throwable in the sync loop, or a dead sync thread is fatal because acknowledged namespace mutations cannot be allowed to remain unsynced silently.

## Test Signals

Useful coverage includes async factory selection by config; queue drain and `logSyncAll` behavior; RPC response postponement/send/abort ordering; synchronous fallback when holding the edit-log monitor; queue-full throttling without deadlock; background thread restart/close interruption; metrics pending edit count updates; op cache disabled behavior; and failure injection proving sync exceptions wake `SyncEdit` waiters and abort `RpcEdit` responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSEditLogAsync.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSEditLogLoader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSEditLogLoader.java

## Purpose

`FSEditLogLoader.java` replays edit-log transactions into the NameNode's in-memory state. It reads `FSEditLogOp` records from an `EditLogInputStream`, validates transaction ID ordering, applies each operation to `FSDirectory`, `BlockManager`, leases, snapshot/cache/token/erasure-coding managers, updates retry-cache entries, tracks startup progress, and provides edit-log scan/validation helpers.

The source was read as a complete 1446-line file for this report.

## Important APIs, Types, and Functions

Core state: `fsNamesys`, `blockManager`, injected `Timer`, `lastAppliedTxId`, `totalEdits`, replay log throttling constants, and `LOAD_EDITS_LOG_HELPER`.

Replay APIs: `loadFSEdits` overloads acquire the global write lock, record startup progress, call `loadEditRecords`, close streams, and log throttled load summaries. `loadEditRecords` performs the main read/validate/apply loop with optional `maxTxnsToRead`, `StartupOption`, and `MetaRecoveryContext`.

Apply helpers: `getAndUpdateLastInodeId`, `applyEditLogOp`, `addNewBlock`, `updateBlocks`, `formatEditLogReplayError`, `dumpOpCounts`, `incrOpCount`, and `check203UpgradeFailure`.

Validation utilities: static `scanEditLog`, nested `EditLogValidation`, nested `PositionTrackingInputStream implements StreamLimiter`, `getLastAppliedTxId`, and `createStartupProgressStep`.

Opcode coverage in `applyEditLogOp` includes file create/open/close/append/update/add-block, replication, concat, rename, delete, mkdir, generation stamps, block IDs, permissions/owner/quota/times/symlink, delegation tokens, leases, log segment markers, snapshots, rolling upgrades, cache directives/pools, ACLs, xattrs, truncate, storage policy, and erasure-coding policy add/enable/disable/remove.

## Control Flow

`loadFSEdits` begins a startup-progress step, acquires the global `FSNamesystem` write lock, logs a throttled start message, invokes `loadEditRecords`, logs a throttled completion summary, closes the stream, releases the lock, and ends the progress step.

`loadEditRecords` also acquires global and directory write locks, initializes expected txid and inode-id state, then loops reading `FSEditLogOp` records. Read failures produce a replay error with recent opcode offsets. Without recovery context, the loader throws `EditLogInputException`; with recovery, it prompts and resyncs. Transaction gaps and out-of-order txids are handled through `MetaRecoveryContext` prompts; out-of-order edits are skipped.

For each decoded op, `applyEditLogOp` mutates in-memory state. After successful apply, op counts and startup counters are incremented, `lastAppliedTxId` and `expectedTxId` advance, periodic replay progress is logged, and max transaction limits are honored. In `finally`, the directory inode ID counter is reset to the highest seen value, optional stream closure happens, locks are released, and debug op counts can be dumped.

`applyEditLogOp` is a large opcode switch. File operations resolve upgrade-renamed reserved paths, update or create `INodeFile` instances, adjust leases, update blocks, complete blocks, and reconstruct retry-cache payloads. Namespace operations delegate to unprotected or edit-log-specific methods in `FSDir*Op` helpers. Manager operations call into delegation-token secret manager, snapshot manager, cache manager, rolling-upgrade hooks, and erasure-coding policy manager.

Block replay is split between `addNewBlock` and `updateBlocks`. These verify block ID/generation-stamp continuity, complete prior blocks as needed, update generation stamps, remove abandoned blocks, add contiguous or striped `BlockInfo` instances, attach them to the file and `BlockManager`, and process queued DataNode messages.

## State and Persistence Behavior

The loader consumes persisted edit-log records and reconstructs volatile NameNode state. It updates `lastAppliedTxId` as replay progresses and restores `FSDirectory`'s last inode ID so subsequent allocations do not collide with persisted inode IDs. Old logs without inode IDs allocate new IDs unless the layout version claims inode-ID support, in which case a grandfather ID is an error.

Retry-cache state is reconstructed when the NameNode has retry cache enabled and an op contains RPC IDs. Some operations store only completion, while create/append/snapshot/cache-policy operations may store payloads such as `HdfsFileStatus`, `LastBlockWithStatus`, snapshot path, directive ID, or EC policy.

Rolling-upgrade records can stop replay for rollback, start rolling-upgrade state, trigger rollback checkpoints, finalize upgrade state, update storage version, and rename rollback images.

`scanEditLog` is non-mutating validation: it scans operations up to a requested txid, resyncs after corrupt sections, and returns valid length and end txid. `PositionTrackingInputStream` supports bounded reads for edit-log parsing by tracking current position and enforcing a temporary byte limit.

## Dependencies and Integration Points

The loader is the main consumer of `FSEditLogOp` records produced by `FSEditLog`. It integrates with `FSNamesystem`, `FSDirectory`, `BlockManager`, `BlockIdManager`, `LeaseManager`, `SnapshotManager`, `CacheManager`, delegation token secret manager, erasure-coding policy manager, `FSImage`, startup progress, `MetaRecoveryContext`, layout-version compatibility, and rolling-upgrade startup options.

Namespace mutations are delegated to operation helpers including `FSDirWriteFileOp`, `FSDirAppendOp`, `FSDirDeleteOp`, `FSDirMkdirOp`, `FSDirRenameOp`, `FSDirConcatOp`, `FSDirAttrOp`, `FSDirSymlinkOp`, `FSDirAclOp`, `FSDirXAttrOp`, `FSDirTruncateOp`, and `FSDirErasureCodingOp`.

Block dependencies include `Block`, `BlockInfoContiguous`, `BlockInfoStriped`, `BlockUCState`, `BlocksMapUpdateInfo`, queued block message processing, replication adjustment, and erasure-coding policy lookup.

## Risks and Edge Cases

Replay must be deterministic and compatible across layout versions. Reserved path renaming, old append behavior, duplicate old `OP_CLOSE` handling, missing inode IDs, and 0.20.203 opcode conflicts are explicit compatibility paths.

Transaction ID gaps and corruption are fatal outside recovery mode. In recovery mode, skipping bad sections can produce a namespace that loads but may be missing operations, so prompts and logs are critical evidence.

Block list replay is high risk. Mismatched block IDs or generation stamps throw; removing more than one block is rejected; adding striped versus contiguous blocks depends on EC policy lookup; and generation-stamp updates also update the standby's global block ID manager.

The loader holds global and directory write locks while applying edits. Long replay time can block other NameNode activity during startup or catch-up, so progress logging and `maxTxnsToRead` are important operational controls.

Retry-cache reconstruction depends on ops carrying RPC IDs and on payload reconstruction matching original RPC results. Missing payloads can affect client idempotency after failover/restart.

## Test Signals

Useful coverage includes replay round trips for every opcode emitted by `FSEditLog`; txid gap, out-of-order, corrupt read, and recovery-mode resync tests; layout-version compatibility tests for inode IDs, reserved path upgrades, legacy append/close, and 0.20.203 failures; block replay tests for add, update, abandon, complete, striped EC files, and generation-stamp updates; retry-cache payload reconstruction tests; snapshot delete cleanup tests for block removal and inode-map removal; rolling-upgrade rollback/finalize tests; cache directive/pool and EC policy manager replay tests; startup progress/op count assertions; `scanEditLog` corruption handling; and `PositionTrackingInputStream` limit/mark/reset/skip behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSEditLogLoader.java -->
