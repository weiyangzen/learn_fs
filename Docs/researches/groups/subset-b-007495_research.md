# Research Report: subset-b-007495

This grouped report covers the requested Hadoop HDFS NameNode files. Each file section is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CacheManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CacheManager.java

## Purpose
`CacheManager` is the NameNode-side controller for path-based caching. It stores cache pools, cache directives, and the cached-block-to-DataNode map, then coordinates with `CacheReplicationMonitor` and `BlockManager` to schedule cache and uncache work. It is constructed by `FSNamesystem`, and most public mutating APIs assert that the appropriate `FSNamesystem` lock is already held.

## Important APIs and Types
Key state includes `directivesById`, `directivesByPath`, `cachePools`, `nextDirectiveId`, `cachedBlocks`, and the CRM `ReentrantLock`. `PersistState` packages protobuf fsimage state. External-facing operations include `addDirective`, `modifyDirective`, `removeDirective`, `listCacheDirectives`, `addCachePool`, `modifyCachePool`, `removeCachePool`, `listCachePools`, `processCacheReport`, `saveState`, and `loadState`. Compatibility persistence is isolated in `SerializerCompat`.

## Control Flow
Directive creation validates pool name, path, replication, expiry, permissions, and pool capacity unless `CacheFlag.FORCE` is set, then allocates a monotonic ID and calls `addInternal`. Modifications build a merged directive from supplied fields and defaults, validate against source/destination pools, remove the old directive, and re-add the new one. Cache reports take the BM write lock, resolve the DataNode, clear its cached list, then insert or reuse `CachedBlock` entries and link them into DataNode cached/pending lists.

## State and Persistence
Persistent state is limited to pools, directives, and `nextDirectiveId`; DataNode cached block reports are in-memory and rebuilt from reports. Fsimage save/load supports protobuf `PersistState` and legacy `DataOutputStream`/`DataInput` serialization with startup progress steps. Edit log replay paths bypass time-dependent validation to remain deterministic.

## Dependencies and Integration
The class integrates with `FSNamesystem`, `FSDirectory`, `BlockManager`, `CacheReplicationMonitor`, `NameNodeMetrics`, protobuf helpers, `FSImageSerialization`, `StartupProgress`, and permission checking through `FSPermissionChecker`.

## Risks and Test Signals
Correctness depends on external lock discipline: FS lock for directives/pools and BM lock for cached blocks. Expiry validation depends on wall-clock time, so replay must use `modifyDirectiveFromEditLog`. Pool limit checks use a shallow direct-child directory size computation, which is a behavior boundary worth testing. `setCachedLocations` contains a duplicated `return;` after cache miss; harmless, but a cleanup/test signal. Tests should cover fsimage round trip, edit-log replay, list pagination/filtering, forced over-limit directives, disabled caching, DataNode cache report transitions, and CRM rescan signaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CacheManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CachePool.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CachePool.java

## Purpose
`CachePool` is the NameNode-internal representation of a path-based cache pool. It carries ownership, permission, quota-like limits, default directive parameters, current aggregate cache statistics, and an intrusive list of member `CacheDirective` objects.

## Important APIs and Types
`DirectiveList` extends `IntrusiveCollection<CacheDirective>` and binds directives back to their pool. Factory methods `createFromInfoAndDefaults` and `createFromInfo` transform client-facing `CachePoolInfo` into fully populated internal state. Getters/setters expose pool metadata, while `resetStatistics`, `addBytesNeeded`, `addBytesCached`, `addFilesNeeded`, and `addFilesCached` maintain counters.

## Control Flow
Pool creation fills missing owner and group from `NameNode.getRemoteUser`, default mode from `FsPermission.getCachePoolDefault`, default limit/replication/expiry from `CachePoolInfo`, and stores a defensive copy of permissions. `getEntry` performs read permission filtering: callers without `FsAction.READ` see only the pool name and empty stats.

## State and Persistence
The object itself is in-memory, but its fields are serialized by `CacheManager` into fsimage/edit-log representations. Statistics are recomputed by cache scans and are not independent durable records.

## Dependencies and Integration
`CachePool` is used by `CacheManager`, `CacheDirective`, `FSPermissionChecker`, `CachePoolInfo`, `CachePoolEntry`, and `CachePoolStats`. The intrusive directive list is a central integration point for efficient pool removal and directive enumeration.

## Risks and Test Signals
All access is documented as requiring the `FSNamesystem` lock; missing lock coverage can corrupt counters or intrusive list membership. Permission-filtered listing should be tested for both privileged and unprivileged users. Default-owner/group resolution is RPC-context sensitive. Tests should also cover statistic reset/rebuild and pool limit overrun calculations through `CacheManager`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CachePool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CachedBlock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CachedBlock.java

## Purpose
`CachedBlock` is the compact in-memory identity and linkage object for a block known to NameNode cache tracking. It serves both as a `LightWeightGSet.LinkedElement` keyed by block ID and as an `IntrusiveCollection.Element` that can belong to multiple DataNode cached-block lists.

## Important APIs and Types
The main fields are immutable `blockId`, GSet `nextElement`, packed `replicationAndMark`, and `triplets`, an array of repeated `(CachedBlocksList, prev, next)` references. Public APIs expose identity, replication/mark bits, presence checks, DataNode listing by `CachedBlocksList.Type`, intrusive list operations, and GSet next-link operations.

## Control Flow
Insertion rejects duplicate membership in the same list, appends a triplet, and later `setPrev`/`setNext` mutate that triplet. Removal copies the array minus the removed triplet. `equals` and `hashCode` intentionally use only `blockId`, allowing lookup by temporary `CachedBlock` instances.

## State and Persistence
This object is non-persistent. It is reconstructed from cache reports and cache directive scans, and its membership is in-memory only. The replication and mark bits guide cache replication monitor scan decisions rather than fsimage content.

## Dependencies and Integration
It is consumed by `CacheManager`, `CacheReplicationMonitor`, `DatanodeDescriptor.CachedBlocksList`, `LightWeightGSet`, and `IntrusiveCollection`.

## Risks and Test Signals
The packed bit layout assumes non-negative replication within 15 bits; assertions do not run in production. The triplet array favors low allocation overhead but relies on exact list object identity and throws runtime exceptions on misuse. Tests should stress adding/removing one block across cached, pending-cached, and pending-uncached lists, GSet lookup equality, and DataNode filtering by list type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CachedBlock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CheckableNameNodeResource.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CheckableNameNodeResource.java

## Purpose
`CheckableNameNodeResource` is a small private interface for NameNode resources whose availability participates in service-health decisions, such as storage volumes or redundant resource groups.

## Important APIs and Types
It defines `isResourceAvailable()` and `isRequired()`. Required resources must all be available, while redundant resources allow operation as long as at least one redundant resource remains available.

## Control Flow
The interface has no implementation logic; callers aggregate implementations according to the required/redundant semantics described in the class comment.

## State and Persistence
There is no state or persistence in the interface. Implementations own the actual availability checks and durability implications.

## Dependencies and Integration
The interface is intended for internal NameNode resource-checking code and is marked `InterfaceAudience.Private`.

## Risks and Test Signals
The risk is semantic rather than algorithmic: implementations must correctly classify required versus redundant resources. Tests should use mock implementations to verify NameNode resource-policy aggregation around all-required, any-redundant, and mixed-resource cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CheckableNameNodeResource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CheckpointConf.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CheckpointConf.java

## Purpose
`CheckpointConf` centralizes secondary/backup checkpoint scheduling and upload configuration derived from Hadoop `Configuration`.

## Important APIs and Types
Constructor fields include checkpoint period, edit-log check period, transaction trigger count, max merge retries, legacy OIV image directory, quiet multiplier, and parallel upload enablement. Getters expose `getPeriod`, `getCheckPeriod`, `getTxnCount`, `getMaxRetriesOnMergeError`, `getLegacyOivImageDir`, `getQuietPeriod`, and `isParallelUploadEnabled`.

## Control Flow
Construction reads current DFS config keys and warns if deprecated `fs.checkpoint.size` or `dfs.namenode.checkpoint.size` are present. `getCheckPeriod` caps the check period by the checkpoint period so polling cannot be less frequent than the maximum time-based checkpoint interval.

## State and Persistence
The class is immutable except `quietMultiplier` not declared final. It does not persist itself; checkpoint daemons consume these settings at initialization.

## Dependencies and Integration
Used by `Checkpointer` and other checkpointing components. It depends on `DFSConfigKeys`, `Configuration`, `TimeUnit`, and Guava `ImmutableList`.

## Risks and Test Signals
Misconfigured durations directly affect checkpoint latency and edit-log growth. Deprecated size keys are ignored, so tests should verify warnings and that transaction count comes only from `DFS_NAMENODE_CHECKPOINT_TXNS_KEY`. Configuration tests should cover check-period capping, quiet-period multiplication, and parallel-upload flag propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CheckpointConf.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CheckpointFaultInjector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CheckpointFaultInjector.java

## Purpose
`CheckpointFaultInjector` is a test hook class for injecting failures or altered file-transfer behavior during checkpoint and image-transfer flows.

## Important APIs and Types
It exposes a mutable singleton via `getInstance` and `set`. Hook methods include `beforeGetImageSetsHeaders`, `afterSecondaryCallsRollEditLog`, `duringMerge`, `afterSecondaryUploadsNewImage`, `aboutToSendFile`, `afterMD5Rename`, `beforeEditsRename`, and `duringUploadInProgess`. Boolean hooks `shouldSendShortFile` and `shouldCorruptAByte` control transfer corruption scenarios.

## Control Flow
Production behavior is no-op and returns false for corruption/short-send decisions. Tests replace `instance` with subclasses to throw exceptions, block, corrupt, or shorten files at well-defined checkpoint phases.

## State and Persistence
Only the static singleton is stateful. It is not persisted and must be reset by tests to avoid cross-test contamination.

## Dependencies and Integration
Used by checkpoint/image transfer code such as `TransferFsImage` and edit/image rename paths. Dependencies are limited to `File` and checked exceptions.

## Risks and Test Signals
The singleton is globally mutable and not synchronized; tests running concurrently can interfere. The method name `duringUploadInProgess` is misspelled, so callers and tests must match that exact API. Test suites should reset the singleton in teardown and cover short file, corrupted byte, MD5 rename, and upload interruption paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CheckpointFaultInjector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CheckpointSignature.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CheckpointSignature.java

## Purpose
`CheckpointSignature` uniquely identifies checkpoint compatibility between checkpointing nodes and the active NameNode. It combines storage identity, cluster identity, block pool identity, recent checkpoint transaction ID, and current edit-log segment transaction ID.

## Important APIs and Types
The class extends `StorageInfo` and implements `Comparable<CheckpointSignature>`. Constructors build signatures from `FSImage`, serialized strings, or explicit fields. Methods expose cluster/block-pool IDs, checkpoint and segment txids, serialization through `toString`, compatibility checks, validation, ordering, equality, and hash code.

## Control Flow
String parsing expects seven colon-separated fields. `validateStorageInfo` rejects mismatched namespace, cluster ID, block pool ID, layout version, or cTime. `compareTo` orders all fields with Guava `ComparisonChain`, and equality is compare-to-zero.

## State and Persistence
The signature is serialized as a compact colon-separated string for checkpoint RPC/protocol exchange. It does not write files directly but gates whether checkpoint images and edit logs are accepted.

## Dependencies and Integration
Used by `Checkpointer`, `FSImage`, `NNStorage`, and `NamenodeProtocol` checkpoint commands. It depends on `StorageInfo`, `NodeType.NAME_NODE`, and Guava comparison utilities.

## Risks and Test Signals
The parsing constructor uses `assert fields.length == NUM_FIELDS`; asserts may be disabled, so malformed strings can fail later with less controlled exceptions. Colon-containing cluster or block-pool IDs would break the plain separator format if ever allowed. Tests should cover valid round trip, mismatched namespace/cluster/block pool, layout/cTime mismatch, compare ordering, and malformed string handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CheckpointSignature.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/Checkpointer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/Checkpointer.java

## Purpose
`Checkpointer` is the `Daemon` used by a BackupNode to periodically create HDFS namespace checkpoints from the active NameNode. It decides when to checkpoint, downloads missing images/edits when needed, applies edit logs, saves a fresh fsimage, uploads it if requested, and finalizes the checkpoint with the active NameNode.

## Important APIs and Types
Important methods are the constructor, `initialize`, `shutdown`, `work`, `countUncheckpointedTxns`, `doCheckpoint`, `getImageListenAddress`, and static `rollForwardByApplyingLogs`. It uses `BackupNode`, `BackupImage`, `CheckpointConf`, `NamenodeProtocol`, `CheckpointCommand`, `RemoteEditLogManifest`, `TransferFsImage`, `EditLogFileInputStream`, and `FSNamesystem` locks.

## Control Flow
The daemon loop wakes at the GCD of time and transaction polling periods. It checkpoints when the time period expires or uncheckpointed transactions exceed the configured threshold. `doCheckpoint` freezes the backup namespace at the next roll, starts a remote checkpoint, validates the signature, fetches missing image/edit logs if log-only roll-forward is impossible, optionally reloads the image under the global write lock, applies edits, saves fsimage in all dirs, uploads the image if requested, calls `endCheckpoint`, converges backup journals, and refreshes registration.

## State and Persistence
Checkpoint output is persisted through `BackupImage` and `NNStorage`. Downloaded edit logs are read from finalized files, then the new fsimage is saved with the resulting txid. Runtime state includes `shouldRun`, checkpoint config, and HTTP bind address.

## Dependencies and Integration
Integrates with active NameNode RPC and HTTP image transfer, backup node storage, global namespace locks, and edit-log loading. It also handles rolling-upgrade storage version behavior.

## Risks and Test Signals
Failure windows include missing edit-log ranges, signature mismatch, partial image download, image reload under lock, upload failure, and active NN shutdown command. `lastCheckpointTime` is updated to the pre-checkpoint `now`, so long checkpoints influence next scheduling. Tests should simulate log gaps, download/reload fallback, upload-needed and no-upload commands, rolling upgrade, startup checkpoint suppression, and `ACT_SHUTDOWN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/Checkpointer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/Content.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/Content.java

## Purpose
`Content` is an enum of namespace content counters used while computing HDFS content summaries.

## Important APIs and Types
The enum values are `FILE`, `DIRECTORY`, `SYMLINK`, `LENGTH`, `DISKSPACE`, `SNAPSHOT`, and `SNAPSHOTTABLE_DIRECTORY`.

## Control Flow
There is no executable logic; values are consumed by `EnumCounters<Content>` in `ContentCounts` and namespace summary traversal code.

## State and Persistence
The enum has no mutable state and is not directly persisted. Its ordinal/name stability matters for in-memory counters and APIs that map these counters to content summary fields.

## Dependencies and Integration
Primary integration is `ContentCounts`, `ContentSummaryComputationContext`, and INode content summary computation.

## Risks and Test Signals
Adding or reordering enum values could affect counter array layout if any code assumes ordinal positions. Tests should verify that content summary fields map to the intended enum values and that snapshots/snapshottable directories are counted separately from normal directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/Content.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ContentCounts.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ContentCounts.java

## Purpose
`ContentCounts` is the mutable counter bundle used by content summary computation. It tracks logical namespace contents and storage-space consumption by storage type.

## Important APIs and Types
The nested `Builder` initializes `EnumCounters<Content>` and `EnumCounters<StorageType>` and provides fluent setters for files, directories, symlinks, length, diskspace, snapshots, and snapshottable directories. The main object exposes getters, `addContent`, `addContents`, `addTypeSpace`, and `addTypeSpaces`.

## Control Flow
Builders create zeroed counters and set requested values. Traversal code mutates `ContentCounts` in place while visiting INodes and snapshots. `addContents` merges both content and storage-type counters from another `ContentCounts`.

## State and Persistence
State is purely in-memory and mutable. It is usually scoped to a content-summary request, not durable metadata.

## Dependencies and Integration
It depends on `Content`, `StorageType`, and HDFS `EnumCounters`. It is owned by `ContentSummaryComputationContext` and used by INode implementations.

## Risks and Test Signals
The builder passes counter instances into `ContentCounts` without cloning, so builders should not be reused after `build` if caller expects immutability. Tests should cover aggregation across content and type-space counters, empty builder defaults, and storage-type quota summary calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ContentCounts.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ContentSummaryComputationContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ContentSummaryComputationContext.java

## Purpose
`ContentSummaryComputationContext` carries state and lock-yield policy for namespace content summary traversal. It holds active counts, snapshot counts, storage policy access, optional permission checker, and parameters for yielding long computations.

## Important APIs and Types
Constructors support yielding traversal with `FSDirectory`/`FSNamesystem` or blocking traversal with a `BlockStoragePolicySuite`. Key methods are `yield`, `getCounts`, `getSnapshotCounts`, `getBlockStoragePolicySuite`, `getErasureCodingPolicyName`, and `checkPermission`.

## Control Flow
`yield` checks whether the counted file/symlink/directory/snapshottable count exceeds the next threshold. If the context holds exactly the expected read locks and no write locks, it releases `FSDirectory` and global `FSNamesystem` read locks, sleeps for the configured interval, reacquires them, increments `yieldCount`, and continues. EC policy lookup handles striped files directly, replicated files with a constant, symlinks as empty, and directories by reading the EC xattr or recursing to parents.

## State and Persistence
The context is request-local and non-persistent. Its `yieldCount` is used by quota consistency checks to avoid comparing cached usage after a lock-yield window where state may have changed.

## Dependencies and Integration
It integrates with `FSDirectory`, `FSNamesystem`, `BlockStoragePolicySuite`, `FSPermissionChecker`, `XAttrFeature`, EC policy manager, and global/read lock APIs.

## Risks and Test Signals
Lock assumptions are strict: yielding is skipped if nested read holds or write locks are present. EC policy lookup can return empty string on parsing/lookup errors, which may hide metadata issues behind warnings. Tests should cover yield/no-yield paths, lock reacquisition ordering, permission audit behavior for superusers, inherited directory EC policy lookup, symlink behavior, and quota consistency with `yieldCount`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ContentSummaryComputationContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/DefaultAuditLogger.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/DefaultAuditLogger.java

## Purpose
`DefaultAuditLogger` is an evolving public base class for NameNode and Router audit loggers. It captures shared audit logging configuration and requires subclasses to implement initialization and event emission.

## Important APIs and Types
Fields include a thread-local `StringBuilder`, caller context enablement and max lengths, token tracking ID logging flag, and a debug command set. Abstract methods are `initialize`, `logAuditMessage`, and two overloads of `logAuditEvent`, one with `CallerContext`.

## Control Flow
This base class only manages caller context enablement through package-private setter/getter. Subclasses decide how to format and emit audit events, including user, remote address, command, source/destination, status, caller context, UGI, and delegation token secret manager.

## State and Persistence
State is process-local logger configuration. Audit event persistence depends on subclass output targets such as logs.

## Dependencies and Integration
It extends `HdfsAuditLogger` and integrates with `Configuration`, `FileStatus`, `CallerContext`, `UserGroupInformation`, and `DelegationTokenSecretManager`.

## Risks and Test Signals
Subclasses must clear/reuse the thread-local builder correctly to avoid leaking prior event text. Caller context length enforcement is not implemented here, so subclass tests must verify truncation and signature handling. Tests should cover both overloads, token tracking IDs, debug command behavior, and caller-context enable/disable transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/DefaultAuditLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/DefaultINodeAttributesProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/DefaultINodeAttributesProvider.java

## Purpose
`DefaultINodeAttributesProvider` is the identity implementation of `INodeAttributeProvider`, used when no custom provider is configured.

## Important APIs and Types
It exposes a static `DEFAULT_PROVIDER` instance. `start` and `stop` are no-ops. `getAttributes` returns the supplied `INodeAttributes` unchanged.

## Control Flow
There is no conditional behavior; all paths pass through existing inode attributes directly.

## State and Persistence
The class has no mutable state beyond the static instance and persists nothing.

## Dependencies and Integration
It is used by `FSDirectory`/NameNode attribute lookup paths as the baseline provider and can be replaced by custom implementations.

## Risks and Test Signals
The static field is mutable rather than final, so accidental replacement can affect global behavior. Tests should verify default provider identity behavior and lifecycle no-ops, and integration tests should ensure custom provider fallback returns to this behavior when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/DefaultINodeAttributesProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/DfsServlet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/DfsServlet.java

## Purpose
`DfsServlet` is a base servlet for DFS-related NameNode web endpoints. It centralizes user identity extraction from HTTP requests.

## Important APIs and Types
It extends `HttpServlet`, defines a logger, and provides `getUGI(HttpServletRequest, Configuration)` which delegates to `JspHelper.getUGI`.

## Control Flow
Subclasses call `getUGI` to resolve the request's effective `UserGroupInformation`, using servlet context, request parameters/headers, and security configuration handled by `JspHelper`.

## State and Persistence
There is no persistent state. Servlet state is limited to standard `HttpServlet` behavior.

## Dependencies and Integration
It integrates with NameNode HTTP servlets, `JspHelper`, `Configuration`, servlet APIs, and Hadoop security UGI.

## Risks and Test Signals
Authentication correctness is delegated to `JspHelper`; servlet tests should cover secure and insecure modes, proxy user behavior, missing/invalid request credentials, and subclass use of the resolved UGI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/DfsServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/DirectoryWithQuotaFeature.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/DirectoryWithQuotaFeature.java

## Purpose
`DirectoryWithQuotaFeature` is the `INode.Feature` attached to directories with namespace, storage-space, or per-storage-type quotas. It stores quota limits and cached usage and validates deltas before namespace changes.

## Important APIs and Types
The builder initializes default namespace quota to `Long.MAX_VALUE`, storage quota to reset/unset, type quotas to reset/unset, and initial usage namespace to one directory. Methods expose quota/usage copies, setters, `computeContentSummary`, `addSpaceConsumed2Cache`, `setSpaceConsumed`, `verifyQuota`, quota-presence checks, and string rendering.

## Control Flow
Quota verification checks namespace, storage-space, and type-space independently using `Quota.isViolated`. Content summary computation compares cached and computed storage-space only if the traversal did not yield, avoiding false warnings when the namespace may have changed mid-computation.

## State and Persistence
Quota and cached usage live in inode metadata and are persisted through inode/fsimage mechanisms outside this class. The class returns defensive `QuotaCounts` copies for public reads.

## Dependencies and Integration
It integrates with `INodeDirectory`, `QuotaCounts`, storage-type counters, snapshot content summary traversal, and HDFS quota exception types.

## Risks and Test Signals
Usage updates do not enforce quotas themselves; callers must call `verifyQuota` first. `typeSpaceString` appears to print `usage/usage` instead of `usage/quota`, making diagnostics misleading. Tests should cover all quota dimensions, unset quotas, content-summary consistency warnings, storage-type quota rendering, and quota bypass paths during image loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/DirectoryWithQuotaFeature.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogBackupInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogBackupInputStream.java

## Purpose
`EditLogBackupInputStream` adapts byte arrays received by a BackupNode journal RPC into the generic `EditLogInputStream` interface so backup namespace state can apply streamed edits.

## Important APIs and Types
The class holds sender `address`, a mutable `ByteBufferInputStream`, `DataInputStream`, `FSEditLogOp.Reader`, position tracker, and layout version. Important methods are `setBytes`, `clear`, `nextOp`, `nextValidOp`, `getVersion`, `getPosition`, `length`, `setMaxOpSize`, and stream metadata accessors.

## Control Flow
Callers must invoke `setBytes` before reading. That resets the backing byte array, wraps it in a position tracker and `DataInputStream`, records the log version, and creates a reader. `nextOp` reads without recovery; `nextValidOp` reads with recovery and wraps unexpected IOExceptions in `RuntimeException`.

## State and Persistence
This stream is in-memory and always reports in-progress with invalid first/last txids. It does not persist edits; it consumes bytes delivered by the active NameNode.

## Dependencies and Integration
It integrates with `BackupImage`/journal replay paths, `FSEditLogOp.Reader`, `FSEditLogLoader.PositionTrackingInputStream`, and `EditLogInputStream`.

## Risks and Test Signals
`close` assumes `in` is non-null, so closing before `setBytes` can throw `NullPointerException`. `setMaxOpSize` assumes `reader` is initialized. Tests should cover lifecycle ordering, clearing/reusing the stream, malformed byte arrays, max operation size, and position accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogBackupInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogBackupOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogBackupOutputStream.java

## Purpose
`EditLogBackupOutputStream` streams serialized edit-log operations from an active NameNode to a BackupNode over `JournalProtocol` RPC.

## Important APIs and Types
It extends `EditLogOutputStream`, owns an RPC proxy to `JournalProtocol`, backup registration, active `JournalInfo`, a reusable `DataOutputBuffer`, and an `EditsDoubleBuffer`. It implements `write`, `create`, `close`, `abort`, `setReadyToFlush`, `flushAndSync`, `getRegistration`, and `startLogSegment`.

## Control Flow
Writes serialize operations into the current double buffer. `setReadyToFlush` swaps buffers. `flushAndSync` copies ready bytes into a byte array, resets the output buffer, and calls `backupNode.journal(journalInfo, 0, firstTxToFlush, numReadyTxns, data)`. `create` resets buffers and updates log version; `close` refuses unflushed data and stops the RPC proxy.

## State and Persistence
The stream itself has no local durable storage. Durability depends on the remote BackupNode journal handling. Buffer state must be flushed before close.

## Dependencies and Integration
It depends on `NameNodeProxies`, `JournalProtocol`, `NamenodeRegistration`, `JournalInfo`, `RPC.stopProxy`, and `EditsDoubleBuffer`.

## Risks and Test Signals
`writeRaw` is unsupported, so callers must not use raw journal copying through this class. The `durable` argument is ignored because durability is delegated to RPC receiver behavior. Tests should cover connection failure, journal RPC payload txid/count correctness, close with pending bytes, abort idempotence, and start-log-segment forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogBackupOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogFileInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogFileInputStream.java

## Purpose
`EditLogFileInputStream` is the concrete `EditLogInputStream` for edit logs stored in local files, fetched by URL, or carried as an in-memory protobuf `ByteString`. It handles header parsing, layout flag parsing, bounded scanning, recovery-oriented reading, and garbage skipping at finalized log tails.

## Important APIs and Types
Construction supports `File`, `fromUrl`, and `fromByteString`. Internal `LogSource` implementations are `FileLog`, `URLLog`, and `ByteStringLog`. Key methods include lazy `init`, `nextOpImpl`, `nextOp`, `nextValidOp`, `scanNextOp`, `getVersion`, `scanEditLog`, `readLogVersion`, `setMaxOpSize`, and `isLocalLog`.

## Control Flow
The stream starts `UNINIT` and initializes on first read/version request. Initialization opens the source, reads the layout version, rejects missing or `-1` headers, optionally reads layout flags, creates an `FSEditLogOp.Reader`, and transitions to `OPEN`. Reads delegate to the reader. When a known `lastTxId` has been reached, the stream skips remaining bytes to avoid trailing garbage from recovered in-progress logs.

## State and Persistence
The stream is read-only. It tracks source txid range, in-progress flag, max op size, current reader, byte position, and layout version. URL sources require a valid positive `Content-Length` header and remember the advertised size.

## Dependencies and Integration
It integrates with `FSEditLogLoader`, `FSEditLogOp.Reader`, `LayoutFlags`, `NameNodeLayoutVersion`, `URLConnectionFactory`, SPNEGO-aware `SecurityUtil`, and storage recovery code.

## Risks and Test Signals
Lazy initialization means errors surface on first use, not construction. Header handling distinguishes empty/corrupt logs from IO failures. URL reads fail without `Content-Length`. Tests should cover corrupt headers, unsupported/future layout versions, layout flags EOF, trailing garbage skipping, `scanEditLog`, URL HTTP failures/authentication, byte-string reads, max op size, and close-before-open behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogFileInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogFileOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogFileOutputStream.java

## Purpose
`EditLogFileOutputStream` writes NameNode edit-log operations to a local file using double buffering, file preallocation, and optional fsync behavior.

## Important APIs and Types
It extends `EditLogOutputStream`. Important fields are the target `File`, `FileOutputStream`, `FileChannel`, `EditsDoubleBuffer`, static preallocation `fill` buffer, and fsync-skip flags. Public operations include `write`, `writeRaw`, `create`, `writeHeader`, `close`, `abort`, `setReadyToFlush`, `flushAndSync`, `shouldForceSync`, `getFile`, `isOpen`, and testing hooks for file channel and fsync skipping.

## Control Flow
Construction opens a `RandomAccessFile` in `rw` or `rwd` mode and positions the channel at EOF. `create` truncates the file, writes the layout header and layout flags through the current buffer, flushes it, and records the log version. `flushAndSync` preallocates if needed, flushes the ready buffer to the file, and calls `FileChannel.force(false)` unless durability is disabled for tests or handled by synchronous writes.

## State and Persistence
This is a durable edit-log writer. It preallocates invalid opcode bytes in 1 MiB chunks and truncates padding on close. Pending buffer bytes must be flushed before close.

## Dependencies and Integration
Used by `FSEditLog`/journal managers. It depends on `EditsDoubleBuffer`, `FSEditLogOpCodes.OP_INVALID`, `LayoutFlags`, `DFSConfigKeys`, and Java NIO file channels.

## Risks and Test Signals
Preallocation writes beyond logical EOF, so close truncation is critical. `abort` closes without flushing. Static `fill` is shared; although reused with position reset, concurrent writes rely on `IOUtils.writeFully` consuming the buffer safely. Tests should cover durable and non-durable modes, preallocation/truncation, close with unflushed edits, abort behavior, header compatibility, and fsync-skip test isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogFileOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogInputException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogInputException.java

## Purpose
`EditLogInputException` is an `IOException` subtype that reports edit-log read failure while preserving how many edits were successfully loaded before the failure.

## Important APIs and Types
The constructor accepts message, cause, and `numEditsLoaded`. `getNumEditsLoaded` exposes that count.

## Control Flow
There is no additional control flow beyond normal exception construction and retrieval.

## State and Persistence
The exception carries transient failure context only. It is not persisted.

## Dependencies and Integration
Used by edit-log loading code to propagate partial-progress information up to callers that may decide recovery or failover behavior.

## Risks and Test Signals
Callers must inspect `getNumEditsLoaded`; otherwise partial replay context is lost. Tests should verify wrapping cause preservation, count propagation, and caller behavior when some edits were applied before failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogInputException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogInputStream.java

## Purpose
`EditLogInputStream` is the abstract base for all edit-log readers. It defines transaction range metadata, operation reading, corruption resynchronization, skipping by transaction ID, layout version access, position reporting, length reporting, in-progress status, operation-size limits, and locality hints.

## Important APIs and Types
Subclasses implement `getName`, `getFirstTxId`, `getLastTxId`, `close`, `nextOp`, `getVersion`, `getPosition`, `length`, `isInProgress`, `setMaxOpSize`, and `isLocalLog`. The base class implements `readOp`, `resync`, default `nextValidOp`, `scanNextOp`, `skipUntil`, and cached-op handling.

## Control Flow
`readOp` returns a previously cached operation first, otherwise delegates to `nextOp`. `resync` populates the cache with `nextValidOp`, enabling callers to skip corrupted sections. `skipUntil` reads forward until it finds an operation with txid at least the requested value and caches that operation for the next `readOp`.

## State and Persistence
Only `cachedOp` is stored in the base class. Persistence belongs to concrete stream sources.

## Dependencies and Integration
Used by `FSEditLogLoader`, checkpoint roll-forward, journal recovery, backup-node input streams, file/URL/byte-string streams, and any custom journal manager stream.

## Risks and Test Signals
The default `nextValidOp` catches `Throwable` and returns null, so subclasses needing precise corruption handling should override it. `skipUntil` consumes operations and depends on txid ordering. Tests should cover cached-op behavior, resync behavior, skip boundaries, EOF, corrupted stream subclasses, and stream name/current-name reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogOutputStream.java

## Purpose
`EditLogOutputStream` is the abstract base for edit-log journal writers. It defines how edit operations and raw edit bytes are written, initialized, flushed, synced, aborted, and reported.

## Important APIs and Types
Subclasses implement `write`, `writeRaw`, `create`, `close`, `abort`, `setReadyToFlush`, and `flushAndSync`. The base class tracks `numSync`, `totalTimeSync`, and `currentLogVersion`, and provides `flush`, `flush(boolean)`, `shouldForceSync`, `generateReport`, and version getters/setters.

## Control Flow
Callers write operations, call `setReadyToFlush`, then `flush`. The base `flush` increments sync count, times `flushAndSync`, and accumulates sync duration. Subclasses decide actual durability and buffering policy.

## State and Persistence
The abstract class does not persist edits itself. It stores metrics and the current layout version used by concrete writers.

## Dependencies and Integration
Implemented by local file, backup-node, and other journal streams. Used by `FSEditLog`, `JournalSet`, and NameNode metrics/reporting paths.

## Risks and Test Signals
`getLastJournalledTxId` defaults to invalid, so tracking must be provided elsewhere or overridden. `shouldForceSync` defaults false, making subclass implementation important for buffer pressure. Tests should verify sync metric accounting, durable flag propagation, version propagation, report generation, and subclass behavior for abort-after-failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditsDoubleBuffer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditsDoubleBuffer.java

## Purpose
`EditsDoubleBuffer` provides the two-buffer edit-log staging mechanism used by edit-log output streams. New edits are written into the current buffer while the ready buffer is flushed, avoiding allocation and allowing callers to separate write and sync phases.

## Important APIs and Types
Main methods are `writeOp`, `writeRaw`, `close`, `setReadyToFlush`, `flushTo`, `shouldForceSync`, `isFlushed`, byte/transaction counters, and ready/current buffer accessors. Nested `TxnBuffer` extends `DataOutputBuffer`, tracks `firstTxId` and `numTxns`, and serializes operations through `FSEditLogOp.Writer`.

## Control Flow
Writes append to `bufCurrent`. `setReadyToFlush` asserts the previous ready buffer is empty, then swaps current and ready. `flushTo` writes the ready buffer to an output stream and resets it. `close` refuses to close if current bytes remain and logs a decoded dump of unflushed edits for diagnostics.

## State and Persistence
State is in-memory buffer content plus transaction metadata. Persistence occurs only when a caller flushes the ready buffer to a concrete stream.

## Dependencies and Integration
Used by `EditLogFileOutputStream` and `EditLogBackupOutputStream`. It depends on `FSEditLogOp.Writer`, `DataOutputBuffer`, `HdfsServerConstants.INVALID_TXID`, and diagnostic hex encoding.

## Risks and Test Signals
Correct use requires `setReadyToFlush` only when the ready buffer is empty. Closing with unflushed data intentionally fails and can log raw edit bytes. Tests should cover txid tracking, raw writes, force-sync threshold, swap/flush/reset behavior, close diagnostics, and malformed unflushed edit decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditsDoubleBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EncryptionFaultInjector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EncryptionFaultInjector.java

## Purpose
`EncryptionFaultInjector` is a visible-for-testing singleton that provides no-op hooks for injecting failures around encrypted file creation and re-encryption processing.

## Important APIs and Types
The class exposes static `instance` and `getInstance`. Hook methods include `startFileNoKey`, `startFileBeforeGenerateKey`, `startFileAfterGenerateKey`, `reencryptEncryptedKeys`, `reencryptUpdaterProcessOneTask`, `reencryptUpdaterProcessCheckpoint`, and `ensureKeyIsInitialized`.

## Control Flow
Production behavior is no-op. Tests replace or mutate the singleton with a subclass that throws `IOException` at specific encryption lifecycle points.

## State and Persistence
Only the static singleton is stateful. It is not persisted.

## Dependencies and Integration
Used by encryption-zone, encrypted file creation, and re-encryption code paths to exercise failure handling.

## Risks and Test Signals
Like other global test injectors, it can leak state across tests if not reset. The methods are instance methods but `instance` is public, so tests can replace it directly. Test suites should verify reset behavior and each hook's effect on edit-log rollback, key generation, and re-encryption updater recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EncryptionFaultInjector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EncryptionZoneManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EncryptionZoneManager.java

## Purpose
`EncryptionZoneManager` manages HDFS encryption-zone metadata and re-encryption lifecycle state. It maps encryption-zone root inode IDs to cryptographic suite/version/key metadata, validates moves across zones, creates zone xattrs, lists zones/statuses, and coordinates background `ReencryptionHandler` threads.

## Important APIs and Types
`EncryptionZoneInt` is the internal zone record. Core state includes `TreeMap<Long, EncryptionZoneInt> encryptionZones`, `FSDirectory dir`, list response limits, optional re-encryption executor/handler, and `ReencryptionStatus`. Important APIs cover testing pauses, constructor setup, thread start/stop, zone add/remove, `isInAnEZ`, `getKeyName`, `getEZINodeForPath`, `checkMoveValidity`, `createEncryptionZone`, `listEncryptionZones`, `reencryptEncryptionZone`, `cancelReencryptEncryptionZone`, `listReencryptionStatus`, `isEncryptionZoneRoot`, `checkEncryptionZoneRoot`, `getNumEncryptionZones`, and `getKeyNames`.

## Control Flow
Zone creation validates that the target exists, is a directory, is not already a zone, and is empty, then writes the crypto xattr via `FSDirXAttrOp`; xattr handling calls back to add the zone so fsimage/edit-log loading shares the same path. Zone lookup walks path components upward, using the live map for current paths or xattrs for snapshots. Move validation rejects moves into/out of zones or between different zones and also blocks moves while the relevant zone is under re-encryption. Listing uses inode ID cursors and re-resolves full paths to filter snapshot-only zones.

## State and Persistence
The authoritative durable metadata is the encryption xattr on the zone inode and re-encryption xattrs/status persisted by related FSDir operations. The `encryptionZones` map and `ReencryptionStatus` are in-memory indexes reconstructed from namespace metadata.

## Dependencies and Integration
It integrates with `FSDirectory`, `FSNamesystem` locks, `KeyProviderCryptoExtension`, `ReencryptionHandler`, `ReencryptionStatus`, xattr helpers, protobuf crypto metadata, snapshots, and permission/path resolution.

## Risks and Test Signals
The class comment warns not to take the `FSDirectory` lock while holding the manager lock; actual methods primarily rely on FSDirectory lock assertions. `removeEncryptionZone` returns early if the removed zone lacks running re-encryption status, which makes handler cleanup conditional. Listing can underfill a page after filtering snapshot-only zones while still setting `hasMore` from the unfiltered tail size. Tests should cover snapshot zone lookup, rename restrictions, non-empty directory rejection, missing key provider for re-encryption, re-encryption cancellation, list pagination with deleted/snapshotted zones, and thread start/stop under locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EncryptionZoneManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ErasureCodingPolicyManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ErasureCodingPolicyManager.java

## Purpose
`ErasureCodingPolicyManager` manages system and user-defined erasure coding policies for the NameNode. It tracks all known policies, enabled policies, removed policies, and the subset of policy state persisted into fsimage.

## Important APIs and Types
It is a lazy singleton returned by `getInstance`. State includes maps by name and ID, cached arrays of all/enabled policies, persisted policy info, maximum cell size, user-defined-policy enablement, and default policy name. Important APIs are `init`, `getEnabledPolicies`, `getEnabledPolicyByName`, `checkStoragePolicySuitableForECStripedMode`, `getPolicies`, `getPersistedPolicies`, `getCopyOfEnabledPolicies`, lookup by ID/name, `addPolicy`, `removePolicy`, `getRemovedPolicies`, `disablePolicy`, `enablePolicy`, `loadPolicies`, and `getEnabledPoliciesMetric`.

## Control Flow
Initialization loads built-in system policies as disabled, enables the configured default policy, caches arrays, then reads max cell size and user-defined enablement. Adding a policy validates user policy enablement, codec support, maximum block group size, maximum cell size, duplicate schema/cell-size/name, and ID exhaustion, then assigns a composed name and next user ID. Enable/disable/remove update both runtime enabled maps and persisted-policy state.

## State and Persistence
Runtime maps include built-in, user-defined, disabled, enabled, and removed policies. `allPersistedPolicies` captures the fsimage representation, intentionally treating a default policy enabled only by startup config differently from an explicitly enabled persisted policy.

## Dependencies and Integration
It integrates with `FSNamesystem`, inode EC policy xattrs, `SystemErasureCodingPolicies`, `ErasureCodingPolicyInfo`, `CodecUtil`, DFS config keys, and storage policy validation for striped files.

## Risks and Test Signals
The singleton lazy initialization is not synchronized, so concurrent early access could race. `init` calls `enableDefaultPolicy` before reading configured `maxCellSize`, so persisted loading later performs max-size checks with the initialized value but built-ins/defaults are handled earlier. `clear` is a placeholder. Tests should cover duplicate policy detection, ID assignment boundaries, disabled user-defined policies, unsupported codecs, persisted state differences for default policy, remove/disable/enable transitions, replication policy lookup, and storage-policy suitability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ErasureCodingPolicyManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirAclOp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirAclOp.java

## Purpose
`FSDirAclOp` contains static helper operations for NameNode ACL mutation and retrieval on inodes. It is the FSDirectory-facing implementation behind client ACL APIs.

## Important APIs and Types
Operations include `modifyAclEntries`, `removeAclEntries`, `removeDefaultAcl`, `removeAcl`, `setAcl`, `getAclStatus`, `unprotectedSetAcl`, and private config/removal helpers. It uses `AclStorage`, `AclTransformation`, `AclFeature`, `AclEntry`, `AclStatus`, `FsPermission`, and FSDirectory path resolution.

## Control Flow
Mutating methods first check that ACLs are enabled, take the FSDirectory write lock, resolve the path for write, check owner, compute transformed ACL entries, update inode ACL state with the latest snapshot ID, log `OP_SET_ACL`, and release the lock. `removeAcl` uses `unprotectedRemoveAcl` and logs an empty ACL list. `getAclStatus` takes a read lock, handles `.snapshot` specially, reads inode attributes and logical ACL entries, and builds an `AclStatus`.

## State and Persistence
ACL state is stored as inode ACL features and permission bits. Persistence is through edit-log `logSetAcl` and fsimage inode serialization. Unprotected methods are intended for edit-log replay or callers already holding the write lock.

## Dependencies and Integration
It integrates with `FSDirectory`, permission checking, snapshots, edit logging, and HDFS ACL storage/transformation utilities.

## Risks and Test Signals
`unprotectedRemoveAcl` restores group permission bits from the ACL feature's group entry, so malformed feature ordering can trigger an index exception. `AclException` messages are augmented with path context. Tests should cover ACL disabled config, owner enforcement, default ACL removal, full ACL removal restoring group bits, `.snapshot` status, edit-log replay with `fromEdits`, and snapshot-aware ACL updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirAclOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirAppendOp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirAppendOp.java

## Purpose
`FSDirAppendOp` implements the namespace side of appending to existing HDFS files. It validates append eligibility, recovers or establishes a lease, converts the file to under construction, handles last-block behavior, updates quota usage, and logs the append/open operation.

## Important APIs and Types
The static APIs are `appendFile` and `prepareFileForAppend`; private helpers verify and compute quota delta for converting a complete block to under construction. The class uses `FSNamesystem`, `FSDirectory`, `INodesInPath`, `INodeFile`, `BlockManager`, `BlockInfo`, `LocatedBlock`, `QuotaCounts`, and `NameNodeLayoutVersion.Feature.APPEND_NEW_BLOCK`.

## Control Flow
`appendFile` asserts the global write lock, takes the FSDirectory write lock, resolves the path, rejects directories and missing files, enforces write permission, rejects EC append without `NEW_BLOCK`, rejects lazy-persist files, recovers the lease, checks the last block's replication/UC state, then calls `prepareFileForAppend`. `prepareFileForAppend` verifies quota for a preferred-size UC block, records modification, converts the file to under construction, adds a lease, either converts the last block to UC or returns the last complete block when appending with a new block, updates quota counts if needed, and logs `logAppendFile` or legacy `logOpenFile`.

## State and Persistence
Persistent state changes include inode under-construction state, lease manager state, block UC conversion, quota cache updates, and edit-log records. During edit-log loading, quota checks may be skipped because the image is not fully loaded.

## Dependencies and Integration
It integrates with block management, lease recovery, FSDirectory locking, quota verification, storage policy suite, edit logs, retry cache logging, and client protocol append semantics.

## Risks and Test Signals
Append behavior differs for striped EC files and older layout versions. Quota delta assumes preferred block size minus current last-block size; appending to an over-preferred block is guarded by a state check when quota is updated. Tests should cover missing path, directory path, permission denial, EC append with/without new block, lazy-persist rejection, COMMITTED last-block retriable failure, insufficient replication, quota update for partial block, retry-cache edit logging, and legacy layout fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirAppendOp.java -->
