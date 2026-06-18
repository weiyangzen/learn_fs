# Research group subset-b-007502

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSNamesystemLock.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSNamesystemLock.java

Purpose: `FSNamesystemLock` is the NameNode namespace lock wrapper used where plain `ReentrantReadWriteLock` behavior is not enough. It exposes read/write lock operations while adding fairness configuration, long-hold detection, throttled diagnostics, detailed lock-hold metrics, and per-RPC processing details.

Important APIs and types: constructors accept `Configuration`, a lock name, `MutableRatesWithAggregation`, and optionally a test `Timer`. Public lock APIs include `readLock`, `readLockInterruptibly`, `readUnlock` overloads, `writeLock`, `writeLockInterruptibly`, and `writeUnlock` overloads with operation names, optional suppression, and optional lock-report detail suppliers. Introspection/configuration APIs expose hold counts, write-owner state, `newWriteLockCondition`, queue length, long-hold counters, metrics enablement, reporting thresholds, and test lock injection. The private `LockHeldInfo` captures start time, interval, stack trace, operation, and supplied report detail.

Control flow: lock acquisition records `LOCKWAIT` timing, takes either the read or write lock, then stores the first acquisition timestamp for non-reentrant accounting. Unlocking computes the hold interval before releasing, records per-operation and overall metrics when enabled, updates RPC `ProcessingDetails`, and only emits long-hold logs when the outermost hold exits. Read-lock warning selection is concurrent: the longest interval since the last report is stored in an `AtomicReference`, warning timestamps are CAS-updated, and suppressed warning counts are accumulated. Write-lock reporting uses `LogThrottlingHelper` and keeps the longest write hold seen in the throttle window.

State and persistence behavior: all state is in-memory instrumentation around the underlying lock. Configuration keys control fair locking, detailed metrics, warning suppression interval, and read/write reporting thresholds. There is no durable persistence, but emitted metrics and logs become operational telemetry. Thread-local read timestamps are removed after outermost unlock to avoid leaking thread state across RPC worker reuse.

Dependencies and integration points: this class integrates with `FSNamesystem.LOG`, DFS lock configuration keys, Hadoop metrics, `Server.getCurCall()` processing details, `Timer`, `Time`, and `LogThrottlingHelper`. `FSNamesystem`, `FSDirectory`, and namespace operations rely on it indirectly for lock correctness and lock diagnostics.

Risks: lock accounting depends on balanced acquire/release calls and correct outermost-hold detection. Long report suppliers run while handling unlock reporting, so expensive suppliers can add latency. Metric names are built from capitalized operation names and can proliferate if callers pass unstable names. Replacing `coarseLock` in tests while state counters remain live can hide race bugs if used outside tests.

Test signals: useful tests cover reentrant read/write holds, interruptible acquisition, fair-lock configuration, metric enable/disable behavior, RPC processing detail updates, long-hold threshold reporting, throttling/suppression counts, and ThreadLocal cleanup after read unlock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSNamesystemLock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSPermissionChecker.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSPermissionChecker.java

Purpose: `FSPermissionChecker` is the NameNode authorization engine for filesystem paths and cache pools. It implements the default POSIX permission, ACL, sticky-bit, traversal, owner, and subtree access rules, while also acting as the default `INodeAttributeProvider.AccessControlEnforcer` and as the bridge to external authorization providers.

Important APIs and types: constructors capture the filesystem owner, supergroup, caller UGI, optional attribute provider, context-API enablement, and external enforcer slowness threshold. Public utilities expose caller user/group/superuser state, the attribute provider, `checkSuperuserPrivilege`, `denyUserAccess`, and cache-pool permission checks. Package-scope `checkPermission` overloads authorize `INodesInPath` or a single `INode`. Static traversal helpers validate ancestors and symlinks after path resolution. The nested `CheckPermission` functional interface and `runCheckPermission` time external authorization calls. `TraverseAccessControlException` tunnels `UnresolvedPathException` and `ParentNotDirectoryException` through the older enforcer interface.

Control flow: path permission checking builds arrays of raw `INode`s and effective `INodeAttributes`, applying an attribute provider to each resolved component. If context-aware authorization is enabled and an operation type is set, it creates an `AuthorizationContext`; otherwise it calls the legacy `checkPermission` signature. The default implementation first verifies traverse execute permission and directory/symlink shape, then checks sticky-bit delete/rename constraints, ancestor access, parent access, target access, recursive subtree access, and optional ownership. `hasPermission` prefers ACL enforcement when an access ACL exists, otherwise checks owner/group/other bits. ACL checks apply named-user and group entries with the mask encoded in group permission bits and stop before default ACL entries.

State and persistence behavior: checker instances are immutable snapshots of caller identity and provider configuration. Permission metadata comes from in-memory inode attributes, including snapshot attributes when requested; no durable state is written. `operationType` is a static `ThreadLocal` used to add operation names to context and logging, so lifecycle discipline is important in reused RPC threads.

Dependencies and integration points: it depends on `INodesInPath`, `INode`, `INodeAttributes`, ACL encoding (`AclEntryStatusFormat`, `AclFeature`), `FsPermission`, `FsAction`, `CallerContext`, UGI, `FSDirectory` path resolution, and `INodeAttributeProvider`. NameNode operations call it while holding the FS read lock. External providers can replace both attributes and authorization decisions.

Risks: recursive `checkSubAccess` can be expensive on large subtrees and must run under read-lock expectations. Attribute-provider TODOs remain in subtree/sticky-bit checks where only limited path context is reconstructed. `AuthorizationContext.equals` dereferences fields and omits newer fields such as operation/caller context, so it is only suitable for narrow tests. Incorrect `operationType` cleanup can misattribute external authorization logs. Wrapping external ACE subclasses into plain `AccessControlException` intentionally loses subclass type except for traversal exceptions.

Test signals: tests should cover owner/group/other permissions, ACL mask semantics, default ACL ignoring, sticky-bit denials, recursive subtree checks with empty-directory bypass, symlink/parent-not-directory tunneling, single-inode checks, cache-pool permissions, superuser auditing through external enforcers, context-vs-legacy provider paths, and slowness warning thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSPermissionChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSTreeTraverser.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSTreeTraverser.java

Purpose: `FSTreeTraverser` is an abstract NameNode utility for depth-first namespace traversal that processes file inodes in batches. It is designed for long-running namespace walks that must periodically submit work, throttle, and release/reacquire locks without retaining an entire directory stack in memory.

Important APIs and types: the constructor stores an `FSDirectory`, reads the NameNode read-lock reporting threshold, and creates a `Timer`. `traverseDir` starts traversal from a parent directory, start inode id, and start-after cursor. `traverseDirInt` performs one locked iteration step. `readLock` and `readUnlock` acquire/release both `FSNamesystem` and `FSDirectory` read locks. Abstract hooks define subclass policy: `checkPauseForTesting`, `processFileInode`, `shouldSubmitCurrentBatch`, `checkINodeReady`, `submitCurrentBatch`, `throttle`, and `canTraverseDir`. `TraverseInfo` is an extension holder for subclass-specific traversal metadata.

Control flow: `traverseDir` converts the start-after file into a list of path-component cursors from the traversal root to the current point, then repeatedly calls `traverseDirInt` until the cursor is exhausted. `traverseDirInt` asserts the proper locks, validates the start inode, gets children for current state, resumes at `INodeDirectory.nextChild`, processes file inodes, descends into traversable directories by editing the cursor, and submits batches when the subclass threshold is reached. Around batch submission and read-lock overrun, it releases locks, calls subclass hooks, reacquires locks, revalidates the start inode, and resolves the parent path again.

State and persistence behavior: traversal state is transient: the current inode, start-after path components, batch state held by subclasses, and lock timing. The filesystem namespace may change while locks are released, so `resolvePaths` reanchors the cursor and truncates changed lower-level cursors. No persistent state is written here; subclasses may persist or queue batches.

Dependencies and integration points: it integrates with `FSDirectory`, `FSNamesystem` locking, snapshot current-state child lists, `HdfsFileStatus.EMPTY_NAME`, permission-aware path resolution, and `INodeDirectory.nextChild`. Subclasses in HDFS features such as re-encryption or storage policy satisfaction can reuse the safe traversal mechanics.

Risks: correctness depends on subclasses respecting lock assumptions and making `processFileInode` idempotent enough for cursor repositioning. Parent deletion/recreation during an unlocked interval ends the current subtree. The read-lock threshold is used as a wall for yielding, so misconfiguration can either hold locks too long or yield too often. `resolvePaths` assumes intermediate resolved nodes are directories.

Test signals: tests should simulate traversal across files and directories, resume after `startAfter`, batch submission with lock release, namespace mutation while unlocked, deletion of the start inode, non-traversable directories, long read-hold yielding, and subclass pauses/throttling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSTreeTraverser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FileJournalManager.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FileJournalManager.java

Purpose: `FileJournalManager` is the `JournalManager` implementation for edit logs stored as files in a NameNode `StorageDirectory`. It creates in-progress edit segments, finalizes them, discovers segments for readers, recovers unfinalized logs, purges obsolete files, handles upgrade/rollback directory operations, and exposes journal creation time.

Important APIs and types: key methods include `startLogSegment`, `finalizeLogSegment`, `purgeLogsOlderThan`, `getRemoteEditLogs`, `selectInputStreams`, `recoverUnfinalizedSegments`, `getLogFiles`, `getLogFile`, `discardSegments`, upgrade hooks, and `getJournalCTime`. Static regex matchers parse finalized `edits_start-end`, current `edits_inprogress_start`, and stale-suffixed in-progress files during purge. The nested `EditLogFile` records file path, first and last transaction IDs, corrupt-header state, and in-progress status, and supports log scanning and rename-aside suffixes.

Control flow: starting a segment computes the in-progress filename, opens `EditLogFileOutputStream`, and reports storage errors on failure. Finalization renames in-progress to finalized using `NativeIO.renameTo` after asserting no destination exists. Discovery lists the current directory, parses matching names, optionally scans in-progress logs up to `lastReadableTxId`, skips corrupt headers, and returns sorted streams or `RemoteEditLog`s that overlap the requested transaction range. Recovery scans every non-current in-progress file: zero-length files are deleted, corrupt headers are moved aside and raise `CorruptionException`, transactionless files are marked `.empty`, and valid files are finalized. Purge deletes or marks stale files based on `minTxIdToKeep` and current in-progress status.

State and persistence behavior: durable state is the edit-log files and their names under the storage directory. `currentInProgress` tracks the writer-side active file, `lastReadableTxId` bounds readers away from concurrently written transactions, `outputBufferCapacity` configures new streams, and `purger` performs deletion/marking. Rename suffixes `.trash`, `.empty`, `.corrupt`, and `.stale` preserve recovery evidence and prevent active files from being mistaken for valid segments.

Dependencies and integration points: it depends on `NNStorage`, `NameNodeFile`, `EditLogFileInputStream`, `EditLogFileOutputStream`, `FSEditLogLoader.EditLogValidation`, `NNStorageRetentionManager`, `StorageDirectory`, `StorageErrorReporter`, `NativeIO`, `RemoteEditLog`, and `NNUpgradeUtil`. It is explicitly not thread-safe except for synchronized methods and expects external NameNode edit-log coordination.

Risks: filename parsing defines transaction-range truth, so malformed names are silently skipped after logging. `lastReadableTxId` must be maintained correctly to avoid readers racing active writers. Recovery and purge rely on rename/delete behavior that can vary by filesystem/platform. `discardEditLogSegments` asserts the start txid is at a segment boundary and will fail if segment ranges overlap unexpectedly.

Test signals: coverage should include regex matching, finalized/in-progress selection, in-progress scanning limits, recovery of zero-length/header-only/corrupt/valid logs, finalization rename failures, purge and stale marking, remote log overlap behavior, duplicate start txid errors, discard-to-trash, and upgrade/rollback delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FileJournalManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FileUnderConstructionFeature.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FileUnderConstructionFeature.java

Purpose: `FileUnderConstructionFeature` is the feature attached to an `INodeFile` while a client lease is still writing the file. It stores lease identity and provides helpers for mutating the last under-construction block during length update and deletion cleanup.

Important APIs and types: the class implements `INode.Feature`. It stores mutable `clientName` and final `clientMachine`, exposes getters, has package-scope `setClientName`, `updateLengthOfLastBlock`, and `cleanZeroSizeBlock`. It interacts directly with `INodeFile`, `BlockInfo`, and `INode.BlocksMapUpdateInfo`.

Control flow: construction records the lease holder and client machine. `updateLengthOfLastBlock` fetches the file's last block, asserts it exists and is not complete, then sets the reported byte length. `cleanZeroSizeBlock` checks whether the file has a trailing incomplete block, and if that block is zero bytes, records it for block-map deletion and removes it from the file.

State and persistence behavior: this feature is in-memory inode state but is part of the NameNode namespace model that can be represented in fsimage/edit-log operations through the owning file. The client machine is immutable after construction; client name can be updated, for example during lease recovery. Block length and removal mutate the owning file/block state.

Dependencies and integration points: it is used by `INodeFile` and lease-management/recovery paths, and its cleanup feeds `BlocksMapUpdateInfo` so the block manager can delete stale zero-length under-construction blocks. Snapshot-aware deletion paths rely on it when a current file also has snapshot history.

Risks: assertions protect against impossible states but are disabled in normal JVM operation, so callers must ensure the last block is present and under construction. Removing a zero-sized UC block must stay coordinated with block-map cleanup or stale blocks can remain. Length updates trust client-reported length and depend on higher-level validation.

Test signals: tests should cover lease holder mutation, last-block length update, assertion/error behavior for missing or complete blocks, zero-size UC block collection/removal, nonzero UC blocks remaining, and interaction with snapshot deletion cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FileUnderConstructionFeature.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FsImageValidation.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FsImageValidation.java

Purpose: `FsImageValidation` is a command-line and programmatic tool that loads an fsimage into a real `FSNamesystem`, builds the namespace tree, and validates structural invariants that offline image viewers cannot check. Its visible validations include INode reference validation during load and inode-map reachability cleanup.

Important APIs and types: `newInstance`, `initConf`, `setHaConf`, `initLogLevels`, `run` overloads, `loadImage`, `checkINodeReference`, static `validate(FSNamesystem)`, static `validate(File, AtomicInteger)`, and `main` are the primary entry points. `Util` contains memory/log/filename helpers. `INodeMapValidation.run` counts the tree via `INodeCountVisitor`, removes inaccessible map entries, and increments an error counter. `Cli` implements Hadoop `Tool`, parses an argument or `FS_IMAGE` environment variable, and centralizes output/error printing.

Control flow: the CLI initializes verbose or suppressed log levels, parses the image path, and invokes validation. `run` logs memory, mutates configuration to avoid short lock warnings and retry cache, initializes NameNode metrics, loads the image while `INodeReferenceValidation` is active, then runs inode-map validation. If errors were found, it reports them; if the inode map changed, it saves a repaired fsimage into a temporary sibling directory. `loadImage` supports both a NameNode storage directory path and a single image file path. Directory load uses `FSNamesystem.loadFSImage`; single-file load constructs namespace info, takes global and FSDirectory write locks, and calls `FSImageFormat.LoaderDelegator`.

State and persistence behavior: normal validation reads an fsimage and builds in-memory NameNode state. It may write a new fsimage only when `INodeMapValidation` removed inaccessible entries. Environment variables `FS_IMAGE` and `PRINT_ERROR` influence input and output behavior. A Java `Timer` periodically logs fsimage load progress and memory while loading.

Dependencies and integration points: it integrates with `FSImage`, `FSNamesystem`, `NNStorage`, `NameNode`, startup progress, `INodeReferenceValidation`, `INodeMap`, `INodeCountVisitor`, block/datanode/top metrics classes for logging suppression, and Hadoop `ToolRunner`. It deliberately creates fake HA settings where needed so edit logs are not loaded as part of validation.

Risks: `validate(File, AtomicInteger)` warns that a path is neither file nor directory even after processing file/directory cases because there is no final `else return`, which can produce misleading output. Loading a full namespace can consume large memory. Saving a repaired fsimage is a side effect that must be expected by operators. Single-file loading fabricates namespace info and may not mirror all production storage context.

Test signals: tests should cover CLI parsing from args/env, `PRINT_ERROR`, directory and file loading paths, lock acquisition during file load, progress timer cancellation, inode-map removal and repaired image save, log-level initialization, no-image directory handling, exit codes, and the stray warning behavior in `validate(File, ...)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FsImageValidation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FsckServlet.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FsckServlet.java

Purpose: `FsckServlet` is the NameNode HTTP endpoint that runs HDFS fsck from the web server. It adapts a servlet request into a privileged `NamenodeFsck` invocation and records an audit event for success or failure.

Important APIs and types: it extends `DfsServlet` and overrides `doGet(HttpServletRequest, HttpServletResponse)`. It uses servlet request parameters, response writer, remote address, servlet context, NameNode HTTP helpers, caller UGI, `FSNamesystem`, `BlockManager`, `DatanodeReportType.LIVE`, and `NamenodeFsck`.

Control flow: `doGet` obtains the raw parameter map, output writer, parsed remote address, `Configuration`, and caller UGI. It executes the fsck body inside `ugi.doAs`. Inside the privileged action, it retrieves the `NameNode`, namesystem, block manager, network topology, and live datanode count, constructs `NamenodeFsck`, captures its audit source, runs `fsck.fsck()`, and marks success only after it returns. The `finally` block calls `namesystem.logFsckEvent` with success state, audit source, and remote address. Interrupted fsck execution maps to HTTP 400.

State and persistence behavior: the servlet itself has no mutable state beyond `serialVersionUID`. It reads live NameNode state and writes response output. Persistent side effects are indirect: audit logging and any operational effects of fsck reporting; fsck itself is primarily diagnostic.

Dependencies and integration points: it integrates with the NameNode web server context, servlet container, Hadoop security impersonation, `NamenodeFsck`, block management, network topology, live datanode reporting, and audit logging through `FSNamesystem`.

Risks: request parameter map is passed through directly to fsck, so fsck must validate option semantics. Reverse DNS or invalid remote addresses can throw `IOException`. Only `InterruptedException` is converted to a client error; other exceptions propagate through servlet handling after the audit `finally`. Long fsck runs can tie up servlet threads and NameNode read paths depending on fsck internals.

Test signals: tests should cover UGI selection, parameter propagation, successful and failing audit logging, live datanode count wiring, remote-address handling, interrupted execution returning HTTP 400, and servlet-context lookup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FsckServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/GlobalStateIdContext.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/GlobalStateIdContext.java

Purpose: `GlobalStateIdContext` is the server-side `AlignmentContext` for HDFS state-id propagation. It helps clients coordinate observer reads by returning the NameNode's last applied/written transaction ID and by rejecting or adjusting requests whose client state is incompatible with the server role.

Important APIs and types: the constructor takes `FSNamesystem` and discovers coordinated `ClientProtocol` methods by scanning `@ReadOnly(isCoordinated=true)` annotations. Implemented `AlignmentContext` methods include `updateResponseState`, `receiveResponseState`, `updateRequestState`, `receiveRequestState`, `getLastSeenStateId`, and `isCoordinatedCall`. Constants estimate transaction throughput and the server-side fraction of client wait time.

Control flow: response headers are stamped with `getLastSeenStateId`. Server-side request and response methods unused for the opposite direction are no-ops. `receiveRequestState` first rejects observer requests with no state id so clients configured without observer-aware proxy providers fail over instead of reading stale data. It compares client and server state IDs, clamps unexpected future client state when active, and, for observers, throws `RetriableException` when the client is too far ahead for the declared wait time. Otherwise it returns the client state id.

State and persistence behavior: state is derived from `namesystem.getFSImage().getLastAppliedOrWrittenTxId()` and is not persisted here. The coordinated-method set is built once per context from `ClientProtocol` reflection and remains immutable in normal use.

Dependencies and integration points: it integrates with Hadoop IPC request/response headers, `AlignmentContext`, HA service states, observer-read proxy providers, `ClientProtocol`, `ReadOnly` annotations, and `FSImage` transaction IDs. Client-side proxy providers use the state IDs to route or retry reads against active/observer NameNodes.

Risks: coordination is method-name based, so overloaded or renamed methods need care. The observer lag rejection threshold uses a rough fixed transaction-per-second estimate and may be conservative or permissive for unusual clusters. Missing state IDs from legacy clients are rejected only for observers. Active-side client-state clamping logs a warning but can mask upstream state propagation anomalies.

Test signals: tests should cover coordinated method discovery, response state stamping, no-op methods, observer missing-state rejection, active client-state clamping, observer lag threshold/retry behavior, protocol-name filtering, and last-state retrieval from fsimage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/GlobalStateIdContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/HdfsAuditLogger.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/HdfsAuditLogger.java

Purpose: `HdfsAuditLogger` is the evolving public HDFS audit logger extension interface. It preserves the base `AuditLogger` contract while adding HDFS-specific context needed for caller-context and delegation-token tracking.

Important APIs and types: it implements `AuditLogger`. The base seven-argument `logAuditEvent` is implemented to delegate to the richer overload with null `CallerContext`, `UserGroupInformation`, and `DelegationTokenSecretManager`. Subclasses must implement the overload with caller context and token tracking objects, and another overload without caller context but with UGI and delegation token manager.

Control flow: default control flow is a compatibility shim: older callers invoke the base method, and the class forwards to the richer signature so subclasses can centralize formatting and token tracking. Actual logging behavior is supplied by concrete subclasses such as the default NameNode audit logger.

State and persistence behavior: this abstract class stores no state and writes nothing itself. Implementations generally persist audit records to logs and may include token tracking IDs when UGI and secret manager are available.

Dependencies and integration points: it integrates with `AuditLogger`, `FileStatus`, `CallerContext`, `UserGroupInformation`, `DelegationTokenSecretManager`, and NameNode audit call sites for commands, source/destination paths, remote addresses, and operation success.

Risks: implementers must keep both abstract overloads consistent or audit output can differ depending on call path. Null caller context, UGI, or token manager values are expected and must be handled. Because the interface is public/evolving, signature changes carry downstream compatibility risk.

Test signals: tests should verify delegation from the base method, concrete logger handling of null optional context, token tracking output when UGI/secret manager are present, and consistent formatting across overloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/HdfsAuditLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INode.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INode.java

Purpose: `INode` is the abstract base for the NameNode namespace tree. It models common file, directory, symlink, and reference behavior: identity, parent linkage, snapshot-aware metadata, path construction, type casting, subtree cleanup, content summary, quota accounting, block reclamation bookkeeping, and visitor dispatch.

Important APIs and types: abstract metadata APIs include id, permission status, user/group/mode setters, ACL/XAttr feature access, modification/access time, storage policy, `recordModification`, `cleanSubtree`, `destroyAndCollectBlocks`, `computeContentSummary`, and `computeQuotaUsage`. Type predicates/casts cover file, directory, symlink, and reference. Static path helpers validate and split absolute paths. Nested `QuotaDelta`, `ReclaimContext`, and `BlocksMapUpdateInfo` carry quota deltas, deletion context, blocks to delete, replication updates, removed inodes, and removed under-construction leases. `Feature` is a marker for inode feature attachments.

Control flow: snapshot-aware mutators call `recordModification(latestSnapshotId)` before changing current metadata. State membership helpers walk parents, references, and snapshot children to decide current/latest-snapshot presence. Path reconstruction walks parents twice, first for size and then for byte copy. Content summary and quota entry points seed storage policy context, delegate to subclass traversal, then convert counters to public `ContentSummary`. Deletion paths call subclass cleanup, while `BlocksMapUpdateInfo.addDeleteBlock` marks blocks deleted and recursively collects copy-on-truncate blocks.

State and persistence behavior: each inode holds a parent pointer that can be either an `INodeDirectory` or `INodeReference`. Subclasses persist most fields in fsimage/edit logs; this base class defines how snapshot copies and current state are distinguished. Reclaim and quota contexts are transient operation state used to later update block maps, leases, and quota caches.

Dependencies and integration points: it sits at the center of NameNode code, integrating with `INodeDirectory`, `INodeFile`, `INodeSymlink`, `INodeReference`, snapshot classes, block management, storage policies, quota/content summary classes, `FSDirectory`, visitor APIs, ACL/XAttr features, and edit-log operation cleanup.

Risks: equality and hashing are id-only, so id uniqueness is critical. Parent/reference handling is subtle around rename plus snapshots; quota updates may need propagation along old and new paths. Many safety checks are assertions or preconditions whose misuse can corrupt namespace accounting. Recursive cleanup/content summary can be expensive and must coordinate with lock-yielding contexts in callers/subclasses.

Test signals: tests should cover snapshot-aware metadata mutation, current/latest-snapshot membership, reference parent resolution, path component generation, quota/content summary conversion, block deletion including truncate blocks, reclaim context copy semantics, id-based equality, invalid path assertions, and visitor unsupported/default behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeAttributeProvider.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeAttributeProvider.java

Purpose: `INodeAttributeProvider` is the public unstable extension point that lets deployments substitute effective inode attributes and optionally replace or augment permission enforcement. It is the key hook behind external authorization systems that need path, operation, caller, and inode context.

Important APIs and types: providers implement `start`, `stop`, and `getAttributes(String[] pathElements, INodeAttributes inode)`. Deprecated helpers support full-path string splitting. The byte-component overload converts path bytes to strings and delegates. `getExternalAccessControlEnforcer` can return a custom `AccessControlEnforcer`. `AuthorizationContext` stores filesystem owner, supergroup, caller UGI, inode attributes, raw inodes, path components, snapshot id, path, ancestor index, owner/ancestor/parent/access/subAccess requirements, empty-directory behavior, operation name, and caller context. Its nested `Builder` provides fluent construction.

Control flow: NameNode permission checking asks the provider for effective attributes per path component, then uses either the default enforcer or the external enforcer returned by `getExternalAccessControlEnforcer`. Legacy enforcers implement the large `checkPermission` parameter list. Newer enforcers can implement `checkPermissionWithContext` for a single context object and may override `checkSuperUserPermissionWithContext` and `denyUserAccess`; defaults throw denial for unsupported context authorization, perform simple fsOwner/supergroup superuser checks, and throw the provided denial message.

State and persistence behavior: provider lifecycle is tied to NameNode startup/shutdown. The base class has no fields, but implementations may maintain policy caches or external service clients. Attribute substitutions are transient authorization views; they do not directly mutate inode persistence. Context objects are per-check data carriers.

Dependencies and integration points: this class integrates with `FSPermissionChecker`, `INodeAttributes`, `INode`, `FsAction`, UGI, caller context, DFS path conversion, and external authorization plugins. Because it is public/unstable, it also forms a compatibility boundary for downstream security integrations.

Risks: deprecated `getPathElements` is hand-written and sensitive to absolute/trailing slash edge cases. `AuthorizationContext.equals` is testing-oriented, assumes non-null fields, and ignores operation/caller context. Custom enforcers must preserve HDFS traversal, sticky-bit, owner, ACL, and subtree semantics unless intentionally replacing them. Slow external checks can block NameNode operations, making the slowness wrapper in `FSPermissionChecker` important.

Test signals: tests should cover lifecycle calls, path-element conversion for root/trailing paths, attribute substitution, legacy and context enforcer routing, default superuser checks, denied-access notification, equality behavior in test contexts, and integration with `FSPermissionChecker` operation/caller context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeAttributeProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeAttributes.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeAttributes.java

Purpose: `INodeAttributes` is the read-only metadata contract used by permission checking, snapshots, and namespace code when the caller needs inode metadata without necessarily mutating or holding the live inode object directly.

Important APIs and types: the interface exposes directory status, local name bytes, user, group, `FsPermission`, permission short/long, ACL feature, XAttr feature, modification time, and access time. The abstract nested `SnapshotCopy` implements immutable copies of common attributes, storing name bytes, packed permission status, optional de-duplicated ACL feature, modification/access times, and XAttr feature.

Control flow: `SnapshotCopy` constructors either pack a provided `PermissionStatus` or copy fields from an `INode`. If an ACL feature is present, it is passed through `AclStorage.addAclFeature` for feature de-duplication/reference management. Accessors unpack user/group/mode through `INodeWithAdditionalFields.PermissionStatusFormat` and construct `FsPermission` from the stored short.

State and persistence behavior: `SnapshotCopy` is read-only except for its private XAttr field reference and represents metadata captured for snapshot/history use. Packed permissions mirror the compact in-memory/on-disk encoding used by live inodes. ACL feature references participate in shared ACL storage accounting; XAttr features are referenced as captured.

Dependencies and integration points: it is consumed by `FSPermissionChecker`, snapshot diff classes, directory/file attribute copies, and external attribute providers. It depends on `PermissionStatus`, `FsPermission`, `AclFeature`, `AclStorage`, `XAttrFeature`, and permission status packing.

Risks: name bytes and XAttr feature references are not defensively copied in this class, so callers must treat supplied data as immutable. ACL reference accounting must be balanced by cleanup paths elsewhere. Constructing new `FsPermission` on each call is simple but not allocation-free. Attribute providers can return implementations with different behavior, so consumers should rely only on the interface.

Test signals: tests should cover copying from live inodes and explicit fields, permission packing/unpacking, ACL feature de-duplication, null local names, XAttr retention, snapshot read-only behavior, and permission-checker use against provider-supplied attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeAttributes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeDirectory.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeDirectory.java

Purpose: `INodeDirectory` is the concrete directory inode implementation. It stores sorted child inodes, manages directory quota and snapshot features, handles child insertion/removal/replacement, computes directory quota/content summaries, supports snapshot operations, and performs recursive cleanup for deletes and snapshot deletion.

Important APIs and types: constructors create a new directory or copy/adopt children and selected features. Static `valueOf` validates directory existence/type. Directory APIs include storage policy lookup, quota setters/getters, snapshot feature access, snapshottable add/remove, snapshot add/remove/rename, child lookup/search/listing, `nextChild`, add/remove child variants, load-time child insertion, rename undo helpers, recursive cleanup, content/quota computation, dump helpers, visitor dispatch, and child count. It uses `DirectoryWithQuotaFeature`, `DirectoryWithSnapshotFeature`, `DirectorySnapshottableFeature`, `DirectoryDiffList`, and `SnapshotAndINode`.

Control flow: child lists are maintained in binary-search order by local name bytes. Adding/removing a child checks whether the directory is in the latest snapshot; if so, a snapshot feature is created as needed and the operation is recorded through diff lists. Otherwise it mutates the current child list directly, sets the child's parent, inherits group if unset, and optionally updates modification time. Quota computation either uses cached quota feature state or walks children with inherited storage policy. Content summary includes snapshot-deleted data for current-state calls, checks directory read/execute permission, walks children, and repositions if a lock-yield occurred. Cleanup delegates to snapshot features when present or destroys/recurses otherwise.

State and persistence behavior: children, features, quota caches, snapshot diffs, ACL/XAttr features, storage policy XAttr, and metadata are NameNode namespace state persisted through fsimage/edit logs by surrounding serializers. Copy constructors can share children/features intentionally. Snapshot feature transitions preserve diffs when toggling snapshottable state. Cleanup updates reclaim-context quota deltas and removed-inode lists.

Dependencies and integration points: it integrates with `INodeWithAdditionalFields`, `INodeReference`, snapshot manager/features, lease manager, quota and storage policy suites, ACL storage, XAttrs, `FSDirectory`, content summary contexts, namespace visitors, and block reclamation. `FSTreeTraverser` and permission code rely on child list ordering and `nextChild`.

Risks: sorted child-list invariants are critical; incorrect insertion positions break lookup/traversal. Snapshot/reference rename logic is subtle and precondition-heavy. Copy constructor feature sharing can be dangerous if callers expect deep copies. Content-summary traversal must handle lock yields and concurrent namespace mutation. Quota cache correctness depends on every mutation updating space consumed consistently.

Test signals: tests should cover child order/search/add/remove, load-time insertion, duplicate names, group inheritance, snapshot diff recording, snapshottable transitions, quota setting/removal and cache usage, storage policy inheritance, content summary with snapshots and lock yields, rename undo paths, recursive destroy/cleanup, ACL cleanup, and visitor/dump output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeDirectory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeDirectoryAttributes.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeDirectoryAttributes.java

Purpose: `INodeDirectoryAttributes` extends `INodeAttributes` with directory-specific quota metadata and comparison support. It provides snapshot-copy implementations for normal directories and quota-bearing directories.

Important APIs and types: interface methods are `getQuotaCounts` and `metadataEquals`. `SnapshotCopy` extends `INodeAttributes.SnapshotCopy`, always reports `isDirectory()`, returns reset quota counts of `-1` for namespace/storage/type quotas, and compares quota, permission long, ACL feature identity, and XAttr feature identity. `CopyWithQuota` extends `SnapshotCopy` and stores a `QuotaCounts` copy for namespace, storage-space, and storage-type quotas.

Control flow: normal snapshot copies capture directory metadata but report no quotas. `CopyWithQuota` constructors either build quota counts from explicit values and type quotas or copy them from a live quota-set `INodeDirectory` after a precondition check. `getQuotaCounts` returns a defensive `QuotaCounts` copy rather than the stored object.

State and persistence behavior: instances are snapshot/history attribute copies, not live mutable directories. Quota counts mirror persistent directory quota metadata captured at snapshot time. ACL features are de-duplicated by the superclass constructor; XAttr references are captured as supplied.

Dependencies and integration points: it integrates with directory snapshot diffs, `INodeDirectory`, `QuotaCounts`, `StorageType` counters, ACL/XAttr metadata, and permission status packing. `INodeDirectory.metadataEquals` mirrors the comparison logic for live directories.

Risks: metadata equality compares ACL and XAttr feature object identity, not deep content, relying on feature sharing/de-duplication invariants. Normal `SnapshotCopy` uses reset quotas, so callers needing quota history must choose `CopyWithQuota`. Stored quota is mutable internally but returned by copy, reducing external mutation risk.

Test signals: tests should cover snapshot copy from live directory, explicit quota copy, defensive quota returns, `metadataEquals` with equal/different quota/permission/features, precondition failure for non-quota directories, and `isDirectory` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeDirectoryAttributes.java -->
