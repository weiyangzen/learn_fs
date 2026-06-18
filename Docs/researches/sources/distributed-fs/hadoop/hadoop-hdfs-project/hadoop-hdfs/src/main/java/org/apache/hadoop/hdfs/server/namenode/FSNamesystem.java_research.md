# Research: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSNamesystem.java

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007500`: lines 1-6899, `Docs/researches/chunks/subset-b-007500_research.md`
- `subset-b-007501`: lines 6900-9319, `Docs/researches/chunks/subset-b-007501_research.md`

## Chunk Research

### subset-b-007500: lines 1-6899

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSNamesystem.java lines 1-6899

## Purpose

This chunk covers the first 6,899 lines of `FSNamesystem`, the central NameNode coordinator for HDFS namespace, block, lease, safe-mode, edit-log, delegation-token, HA, metrics, and management behavior. The class implements `Namesystem`, `FSNamesystemMBean`, `NameNodeMXBean`, `ReplicatedBlocksMBean`, and `ECBlockGroupsMBean`, and its class comment positions it as the container for persisted and transient namespace state.

Within this range, `FSNamesystem` initializes the NameNode's core managers, loads and transitions FSImage/edit-log state, starts and stops active/standby/observer services, mediates most client namespace operations, handles several DataNode-facing paths, runs active-side maintenance daemons, exposes metrics and JMX JSON, and persists security-token and block-allocation mutations to the edit log. Later lines continue the NameNode MXBean and additional operations, so this chunk should be merged with subsequent chunks for a complete per-file report.

## Important APIs, Types, and Functions

The class-level state is broad and ownership-oriented:

- `dir`, `blockManager`, `snapshotManager`, `snapshotDeletionGc`, `cacheManager`, `leaseManager`, `dtSecretManager`, `fsImage`, `nnResourceChecker`, `editLogTailer`, `standbyCheckpointer`, `haContext`, `retryCache`, `provider`, `topMetrics`, and `inodeAttributeProvider` are the major subsystem references.
- Configuration-derived fields control permissions, storage policy enforcement, HA checkpointing, snapshot trash root behavior, snapshot diff limits, lease recheck/release limits, delegation token behavior, edit-log rolling thresholds, lazy-persist scrubbing, block/listing limits, object limits, checksum defaults, and storage policy satisfier behavior.
- `fsLock` is an `FSNLockManager` selected by `DFS_NAMENODE_LOCK_MODEL_PROVIDER_KEY`. This range uses `RwLockMode.GLOBAL`, `FS`, and `BM` locks to split namespace, block-management, and combined critical sections. `cpLock` serializes checkpoint/save-namespace style work.
- Safe-mode state is split between `blockManager.isInSafeMode()` and local booleans `manualSafeMode` / `resourceLowSafeMode`, with synchronized helpers to distinguish startup safe mode from manual or resource-low safe mode.

Startup and lifecycle APIs include:

- `loadFromDisk`, constructors, `checkConfiguration`, `getNamespaceDirs`, `getNamespaceEditsDirs`, `getRequiredNamespaceEditsDirs`, and `getSharedEditsDirs` validate storage layout and create `FSImage`/`FSNamesystem`.
- `loadFSImage` performs format/recover-transition-read handling, optionally saves stale images, opens edit logs for write when appropriate, and marks the image loaded.
- `startCommonServices`, `stopCommonServices`, `startActiveServices`, `stopActiveServices`, `startStandbyServices`, `prepareToStopStandbyServices`, `stopStandbyServices`, `close`, and `shutdown` control NameNode runtime modes and daemon/service registration.
- `NameNodeResourceMonitor`, `NameNodeEditLogRoller`, and `LazyPersistFileScrubber` are active-side daemon classes for low-resource safe mode, edit-log auto-roll, and removal of corrupt lazy-persist files.

Client-facing namespace and file APIs in this range include:

- Attribute and policy operations: `setPermission`, `setOwner`, `setTimes`, `setReplication`, `setStoragePolicy`, `satisfyStoragePolicy`, `unsetStoragePolicy`, `getStoragePolicy`, `getStoragePolicies`, `getPreferredBlockSize`, and `setQuota`.
- Read/list/stat operations: `getBlockLocations`, `getFileInfo`, `isFileClosed`, `getContentSummary`, `getQuotaUsage`, `getListing`, `getBatchedListing`, `listOpenFiles`, `getFilesBlockingDecom`, `getBlocks`, and `metaSave`.
- Mutation operations: `concat`, `truncate`, `createSymlink`, `startFile`, `appendFile`, `recoverLease`, `getAdditionalBlock`, `getAdditionalDatanode`, `abandonBlock`, `completeFile`, `renameTo`, `delete`, `mkdirs`, and `fsync`.
- Lease and write-pipeline helpers: `recoverLeaseInternal`, `internalReleaseLease`, `reassignLease`, `reassignLeaseInternal`, `commitOrCompleteLastBlock`, `finalizeINodeFileUnderConstruction`, `commitBlockSynchronization`, `closeFileCommitBlocks`, `renewLease`, `checkLease`, `checkFileProgress`, `checkBlocksComplete`, `checkUCBlock`, `bumpBlockGenerationStamp`, and `updatePipeline`.

DataNode, checkpoint, and admin-facing APIs include:

- `registerDatanode`, `handleHeartbeat`, `handleLifeline`, `processIncrementalBlockReport`, `reportBadBlocks`, `datanodeReport`, `slowDataNodesReport`, and `getDatanodeStorageReport`.
- `saveNamespace`, `restoreFailedStorage`, `finalizeUpgrade`, `refreshNodes`, `setBalancerBandwidth`, `setSafeMode`, `rollEditLog`, `startCheckpoint`, `endCheckpoint`, `registerBackupNode`, and `releaseBackupNode`.
- `getRegistrationID`, `getNamespaceInfo`, `unprotectedGetNamespaceInfo`, `getStats`, `getReplicatedBlockStats`, and `getECBlockGroupStats`.

Security, audit, and token APIs include:

- Audit dispatch through `isAuditEnabled`, overloads of `logAuditEvent`, `appendClientPortToCallerContextIfAbsent`, `logFsckEvent`, and `FSNamesystemAuditLogger` integration.
- Delegation token state through `createDelegationTokenSecretManager`, `getDelegationToken`, `renewDelegationToken`, `cancelDelegationToken`, `saveSecretManagerStateCompat`, `saveSecretManagerState`, `loadSecretManagerStateCompat`, `loadSecretManagerState`, `logUpdateMasterKey`, and `logExpireDelegationToken`.
- Authorization helpers `getPermissionChecker`, `checkSuperuserPrivilege`, `createFsOwnerPermissions`, `isAllowedDelegationTokenOp`, `getConnectionAuthenticationMethod`, and `getRemoteUser`.

Metrics and JMX exposure are extensive:

- Metrics include capacity, missing/corrupt/low-redudancy blocks, replicated and EC block groups, active clients, open files, snapshots, encryption zones, SPS paths, lock queue/long-hold counts, transactions since checkpoint/log roll, stale DataNodes/storages, pending DataNode messages, and HA tailer lag.
- MBean registration uses `registerMBean` for `FSNamesystemState`, `ReplicatedBlocksState`, and `ECBlockGroupsState`, and `registerMXBean` for `NameNodeInfo`.
- NameNode MXBean methods in the range include version, used/free/total/provided capacity, safe mode, upgrade finalization, non-DFS use, cache use, missing/badly distributed blocks, thread count, and JSON maps from `getLiveNodes`, `getDeadNodes`, and `getDecomNodes`. The range ends at the start of `getEnteringMaintenanceNodes`.

## Control Flow and Execution Model

Most public or package-private operations follow a consistent template: check the HA operation category, obtain a permission checker if user-facing, acquire the appropriate namesystem lock, repeat the operation-category check while locked, check safe mode for writes, delegate the detailed namespace/block logic to an `FSDir*Op`, `BlockManager`, `DatanodeManager`, `LeaseManager`, `FSImage`, or token manager, release the lock with operation reporting, sync edit logs for mutations, then log audit events.

Startup begins with storage URI validation. `loadFromDisk` creates `FSImage`, constructs `FSNamesystem`, interprets startup options, loads FSImage/edit logs under the global write lock, optionally saves a stale image for non-HA non-rolling-upgrade startup, opens edit logs for write when the NameNode will write, and marks the image loaded. `startCommonServices` registers MBeans/metrics, initializes resource checking, starts block-manager activation and safe-mode progress, starts inode attribute providers, and registers snapshot JMX. Mode-specific service transitions layer active or standby behavior over the common state.

Active transition is a high-risk orchestration path. If edit logs are not open for write, `startActiveServices` initializes journals, recovers unclosed streams, catches up tailing edits from the prior active, clears pending DataNode queues, applies impending generation stamps, initializes reconstruction queues when outside safe mode, sets the next edit-log transaction ID, and opens the edit log for write. It then updates quotas, enables quota checks, starts re-encryption, snapshot deletion GC, lease monitoring, delegation token threads, low-resource monitor, edit-log roller, lazy-persist scrubber, cache monitor, EDEK warm-up, and SPS. Standby/observer transition instead opens shared journals for read, postpones future-block processing, disables quota checks, starts the edit-log tailer, and optionally starts a standby checkpointer.

File creation and append are coordinated in stages. `startFile` validates paths, create flags, block size, replication vs erasure coding, encryption-zone protocol support, and then delegates to `FSDirWriteFileOp.startFile` while preserving edit-log sync if lease recovery generated edits. `getAdditionalBlock` first validates and possibly handles idempotent retry under a read lock, chooses targets outside the lock-heavy mutation phase, then stores the allocated block under the global write lock and syncs the edit log. `completeFile`, `fsync`, `appendFile`, and `abandonBlock` use global locking because lease, namespace, block map, and edit-log state can all be touched.

Lease recovery is state-machine driven. `recoverLeaseInternal` checks whether the file is under construction, verifies the current lease holder, and either immediately calls `internalReleaseLease` on forced recovery or waits for soft-limit expiration. `internalReleaseLease` examines complete, committed, under-construction, and under-recovery states, finalizes files when all blocks or minimally replicated committed blocks are complete enough, removes empty unrecoverable last blocks, starts block recovery by assigning a new generation stamp, and optionally reassigns the lease to a recovery holder.

Block recovery and write-pipeline updates validate both block identity and lease ownership. `commitBlockSynchronization` handles DataNode recovery completion: it locates the stored block, rejects deleted or missing ownership, checks recovery IDs, removes blocks on deleteblock, updates generation stamp and length, resolves target storages, adds close-file locations, handles copy-on-truncate, persists blocks, closes files when requested, and marks recovery successful. `bumpBlockGenerationStamp` and `updatePipeline` similarly call `checkUCBlock`, then persist new generation-stamp or expected-location state.

Safe mode is entered and left through global write-lock paths. `enterSafeMode` stops the secret manager, syncs all open edit-log work when possible, records manual vs resource-low state, and logs a safe-mode tip. `leaveSafeMode` delegates startup safe-mode exit to `BlockManager`, clears local manual/resource flags only if block-manager exit succeeds, and restarts the secret manager when appropriate. The resource monitor repeatedly updates `hasResourcesAvailable`, entering resource-low safe mode when disks are low and leaving it only when low-resource state is the active reason.

DataNode interactions primarily use BM or GLOBAL locking depending on whether namespace state may be affected. Heartbeats are BM-read operations returning commands, HA status, rolling-upgrade info, optional block-report lease IDs, and slow-node flags. Incremental block reports use global write locking because completing blocks can update quotas and block excess selection may need namespace policy context. Bad block reports write-lock BM and mark corrupt replicas.

Administrative control flows use explicit privilege checks and often checkpoint locking. `saveNamespace` requires safe mode and `cpLock`, `restoreFailedStorage` mutates storage policy under `cpLock`, `finalizeUpgrade` uses `cpLock`, `rollEditLog` uses journal operation checks and FS write locking, and checkpoint start/end use global locks while coordinating with `FSImage`.

## State and Persistence Behavior

Persistent namespace and block metadata is owned by `FSDirectory`, `BlockManager`, `FSImage`, `FSEditLog`, `NNStorage`, snapshot state, and the delegation token secret manager. `FSNamesystem` is the coordinator that decides when these mutations become edit-log entries and when they are synchronized.

FSImage loading and saving are explicit persistence paths. `loadFSImage` recovers or upgrades storage, may save a new namespace image, and opens edit logs for subsequent writes. `saveNamespace`, `startCheckpoint`, and `endCheckpoint` coordinate namespace images and checkpoint state. `restoreFailedStorage` and `finalizeUpgrade` change storage behavior or finalize layout state through `NNStorage`/`FSImage`.

Edit-log persistence is central. Namespace operations that mutate state call delegated operations that log edits, then `getEditLog().logSync()` after releasing locks. Examples include permission/owner/time changes, create/append/truncate/symlink/concat, storage policy changes, quota changes, mkdir/delete/rename, fsync, block allocation, block generation stamp allocation, lease reassignment, delegation-token issuance/renewal/cancellation, and close-file logging. Some helpers deliberately do not sync immediately, such as `nextGenerationStamp`, `nextBlockId`, and expired-token logging, with callers responsible for sync or batching.

The active NameNode maintains transient reconstruction and DataNode state that is rebuilt from reports: block-to-storage mappings, DataNode heartbeat/lifeline statistics, stale storage flags, block report leases, pending DataNode messages, corruption iterators, low-redudancy queues, invalidation queues, and cache command state. Active failover clears or rebuilds many of these queues after catching up edits.

Leases are transient runtime state with persisted effects. The `LeaseManager` tracks under-construction files and clients. Lease recovery may log block persistence, reassign leases, finalize files, remove empty blocks, update generation stamps, or close files. `stopActiveServices` updates FSImage's last-applied transaction ID from written edits so a future tailer starts correctly.

Security-token state is both in memory and persisted. `DelegationTokenSecretManager` runs only when security/testing policy and safe-mode/edit-log state allow it. Token creation, renewal, cancellation, master key updates, and expirations are logged to edits, while FSImage save/load uses `SecretManagerState` and compatibility methods for older image formats.

Management state is mostly derived or transient. JMX JSON for live/dead/decommissioning DataNodes is computed from `DatanodeManager` descriptors. Metrics come from `BlockManager`, `DatanodeStatistics`, `LeaseManager`, `SnapshotManager`, `FSDirectory` encryption-zone manager, `FSNLockManager`, `EditLogTailer`, and `NNStorage`.

## Dependencies and Integration Points

`FSNamesystem` is a high-fanout integration point:

- Namespace operations delegate to `FSDirectory` and specialized operation classes such as `FSDirAttrOp`, `FSDirStatAndListingOp`, `FSDirWriteFileOp`, `FSDirAppendOp`, `FSDirConcatOp`, `FSDirTruncateOp`, `FSDirSymlinkOp`, `FSDirRenameOp`, `FSDirDeleteOp`, `FSDirMkdirOp`, `FSDirEncryptionZoneOp`, `FSDirErasureCodingOp`, and `FSDirSatisfyStoragePolicyOp`.
- Block and DataNode state is owned by `BlockManager`, `DatanodeManager`, `DatanodeStatistics`, `DatanodeDescriptor`, `DatanodeStorageInfo`, `BlockInfo`, `BlockUnderConstructionFeature`, `BlockInfoStriped`, `StorageReport`, `HeartbeatResponse`, `NNHAStatusHeartbeat`, and related protocol classes.
- Persistence integrates with `FSImage`, `FSEditLog`, `NNStorage`, `Storage`, `CheckpointSignature`, `NamenodeRegistration`, startup options, layout-version features, FSImage secret manager sections, and checkpoint/upgrade paths.
- HA integrates through `HAContext`, `EditLogTailer`, `StandbyCheckpointer`, `HAServiceState`, `NameNode.OperationCategory`, `StandbyException`, `ObserverRetryOnActiveException`, and active/standby/observer service transitions.
- Security integrates with `UserGroupInformation`, Hadoop RPC `Server`, `FSPermissionChecker`, delegation token classes, `DelegationTokenSecretManager`, `BlockTokenIdentifier`, Kerberos/certificate authentication methods, audit loggers, caller context, and optional proxy-user remote-port logging.
- Storage policy, cache, erasure coding, snapshots, encryption, and SPS integrate through `BlockStoragePolicy`, `CacheManager`, `ErasureCodingPolicyManager`, `ECTopologyVerifier`, `SnapshotManager`, `SnapshotDeletionGc`, `KeyProviderCryptoExtension`, encryption-zone APIs, EDEK warm-up, and `StoragePolicySatisfier`.
- Metrics and management integrate with Hadoop Metrics2 annotations and registries, `DefaultMetricsSystem`, `MBeans`, `StandardMBean`, `NameNodeMXBean`, `FSNamesystemMBean`, `ReplicatedBlocksMBean`, `ECBlockGroupsMBean`, `TopMetrics`, Jetty JSON, and `JsonUtil`.

## Risks and Edge Cases

- Lock mode selection is correctness-critical. Some operations require `GLOBAL` because they cross namespace, block, lease, and quota state, while others use only `FS` or `BM`. Incorrectly narrowing locks can race block reports, file close, quota updates, or namespace deletion.
- Many methods perform `checkOperation` both before and after acquiring locks. Removing the second check can allow HA state transitions between the first check and the actual operation.
- Safe-mode behavior has multiple causes. Startup safe mode is block-manager driven; manual and resource-low modes are local flags. Token threads are stopped before entering safe mode and restarted only on successful exit, so token edit logging while safe mode is active is intentionally guarded by assertions.
- Active transition after HA failover must catch up edits, recover streams, apply generation stamps, clear queues, process pending DataNode messages, and reinitialize reconstruction queues in the right order. Errors here risk duplicate block IDs, stale DataNode state, or missed replication/invalidation work.
- Edit-log sync discipline is subtle. Several helpers log edits without syncing because their callers sync later. Exception paths around create/append/recover lease intentionally preserve sync when lease recovery may have logged edits. Standby exceptions can skip sync.
- Encryption-zone file creation releases and reacquires/re-resolves namespace state while generating EDEKs. That path must revalidate because namespace or encryption-zone metadata can change during key generation.
- `getAdditionalBlock` deliberately chooses targets between validation and storing the allocated block. The retry path returns the previous block if validation detects a retry; idempotency depends on correct client IDs, file IDs, and edit-log/retry-cache state.
- Lease recovery has several fragile states: committed but under-replicated blocks can lead to repeated recovery attempts, empty last blocks may be removed, striped blocks require a different minimum location count, and copy-on-truncate modifies different block objects than normal recovery.
- `commitBlockSynchronization` may observe blocks whose file path was deleted but whose block removal is delayed. The method explicitly checks deleted block collections and deleted files to avoid logging close operations for already removed namespace entries.
- Observer reads that include block locations call `checkBlockLocationsWhenObserver`; stale observer block-location state can force retry on active.
- Batched listing continuation keys embed an MD5 of the source paths. Reusing a `startAfter` with different source paths fails a precondition; the shared `MessageDigest` is synchronized.
- `listCorruptFileBlocks` only proceeds when replication queues are initialized and paginates with a numeric cookie over the corrupt block iterator. Queue initialization and concurrent changes can affect view consistency.
- JMX JSON generation uses live `DatanodeDescriptor` state without explicit namesystem locks in several methods. It is operationally useful but should not be treated as a transactional snapshot.
- The chunk ends inside `getEnteringMaintenanceNodes`; subsequent MXBean node-status methods and other tail APIs are outside this report.

## Test Signals

Good validation coverage for this chunk should include:

- Startup/storage tests for required edits directories, shared edits ordering and duplicate handling, import/format/recover startup modes, stale image save decisions, HA vs non-HA edit-log open behavior, and image-loaded state.
- HA transition tests for standby/observer startup, edit-log tailer catchup during failover, active service startup ordering, generation stamp application, reconstruction queue reinitialization, standby checkpoint cancellation, and operation-category rejection in standby/observer states.
- Locking and safe-mode tests for manual/resource-low/startup safe mode distinctions, secret-manager stop/start around safe mode, `logSyncAll` on safe-mode entry, resource monitor enter/leave behavior, and lock long-hold/queue metrics.
- Namespace operation tests for permission/owner/time, concat, truncate, symlink, replication, quota, mkdir/delete/rename, storage policy set/unset/satisfy, create with replication or EC, create in encryption zones, and edit-log sync/audit behavior on both success and authorization failure.
- File write lifecycle tests for start/create idempotency, add-block retry, target selection, abandon block, fsync block persistence, complete file, append with new block, lease owner mismatch, forced/non-forced lease recovery, committed-block recovery, empty last-block removal, striped block recovery, and block synchronization close/delete/copy-truncate paths.
- DataNode protocol tests for registration ID validation, heartbeat response commands/HA status/rolling-upgrade/block-report lease/slow-node flags, lifeline lightweight updates, incremental block report locking effects, bad-block marking, DataNode reports, slow-node reports, storage reports, and balancer bandwidth changes.
- Persistence/security tests for delegation token issue/renew/cancel authorization and edit logging, secret-manager FSImage save/load compatibility, master-key update logging, expired-token batching, backup node registration/release, saveNamespace safe-mode requirement, failed-storage restore flag, finalize upgrade, roll edit log, and checkpoint start/end.
- Listing/stat tests for block-location sorting, observer stale-location retry, access-time update after reads, file info with and without block tokens, batched listing pagination/checksum validation/error partials, corrupt-file pagination cookies, open-file listing, and files blocking decommission.
- Metrics/JMX tests for capacity counters, missing/corrupt/low-redudancy replicated and EC counters, transaction counters, checkpoint times, lock metrics, snapshot/encryption-zone/SPS counts, top-user JSON, live/dead/decommissioning node JSON fields, and MBean register/unregister lifecycle.

## Chunk Boundary Notes

Lines 1-6899 begin at the source file header and imports, include the class declaration, initialization, major lifecycle paths, many client/admin/DataNode operations, metrics, and most early NameNode MXBean methods. The range ends immediately after the declaration and first local variable of `getEnteringMaintenanceNodes`, so that method and all following APIs require the next chunk for complete analysis.

### subset-b-007501: lines 6900-9319

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSNamesystem.java lines 6900-9319

## Chunk Scope

This chunk is the final span of `FSNamesystem.java`. It starts inside the `NameNodeMXBean` JSON builder for entering-maintenance DataNodes and then covers the class tail: NameNode/JMX status accessors, corrupt-file reporting, snapshot APIs, rolling-upgrade lifecycle, cache directive and cache pool RPC bodies, ACL and XAttr RPC bodies, encryption zone and re-encryption operations, erasure coding operations, snapshot trash provisioning, audit-log formatting, edit-log sync metrics, maintenance-node metrics, topology verification helpers, observer-read validation, and lock-reporting configuration.

The code in this range is mostly a facade layer. `FSNamesystem` performs HA operation-category checks, permission/superuser checks, safe-mode checks, read/write/global lock acquisition, audit logging, edit-log sync boundaries, and metric/JMX formatting, while delegating namespace-specific mutations and reads to helper classes such as `FSDirSnapshotOp`, `FSNDNCacheOp`, `FSDirAclOp`, `FSDirEncryptionZoneOp`, `FSDirErasureCodingOp`, `FSDirXAttrOp`, and `FSDirSatisfyStoragePolicyOp`.

## Purpose

The purpose of this chunk is to expose high-level NameNode administrative, metadata, and observability behavior through `FSNamesystem` while keeping the actual namespace algorithms in specialized helpers. It is the RPC-facing coordination layer for:

- JMX and metrics reporting for storage directories, journals, node usage, software versions, corruption, rolling upgrade status, edit-log sync counts, maintenance-node counts, erasure-coding topology support, and startup/build information.
- Snapshot lifecycle operations: allow/disallow snapshot roots, create/rename/delete/gc snapshots, list snapshot roots, list snapshots, and compute complete or paged snapshot diffs.
- Rolling upgrade lifecycle operations: query, start, finalize, choose effective layout versions, and reject layout-dependent features during downgrade-compatible rolling upgrades.
- Cache administration: add/modify/remove/list cache directives and cache pools.
- Namespace metadata extensions: ACL operations, XAttr operations, encryption zones, zone re-encryption state, erasure coding policies, and storage-policy-satisfaction XAttr cleanup.
- Audit and lock-reporting plumbing used by nearly every public operation in this class.

## Important APIs, Types, and Functions

### NameNode and Cluster Reporting

- `getEnteringMaintenanceNodes()` returns JSON keyed by DataNode transfer address with host name. Each entry includes transfer address, network location, DataNode UUID, under-replicated blocks, maintenance-only replicas, and under-replicated open-file blocks.
- `getLastContact`, `getLastBlockReport`, and `getDfsUsed` are local helpers used by nearby DataNode JMX reporting to derive elapsed time and usage values from `DatanodeDescriptor`.
- `getClusterId()`, `getBlockPoolId()`, `getNameDirStatuses()`, `getNodeUsage()`, `getNameJournalStatus()`, `getJournalTransactionInfo()`, `getNNStartedTimeInMillis()`, `getCompileInfo()`, `getSoftwareVersion()`, and `getNameDirSize()` implement `NameNodeMXBean` or status MBean reporting.
- `getNameDirStatuses()` serializes active and failed NameNode storage directories from `NNStorage`, preserving each directory root and `StorageDirType`.
- `getNodeUsage()` fetches live DataNodes, filters out nodes not in service, and reports min/median/max/stddev DFS-used percentages as formatted JSON strings.
- `getNameJournalStatus()` inspects `FSEditLog` journals without taking the normal edit-log lock. It reports whether each journal is required, disabled, its manager identity, and either the current stream report, "Failed", "not currently writing", or "open for read".
- `getJournalTransactionInfo()` reports the last applied-or-written txid and most recent checkpoint txid from `FSImage`.
- `getCorruptFiles()`, `getCorruptFilesCount()`, and `getCorruptFilesList()` convert `listCorruptFileBlocks("/", null)` into string form for JMX, handling standby and I/O failures by logging and returning what is available.
- `listCorruptFileBlocksWithSnapshot(...)` expands corrupt block listings to include matching paths inside snapshots by resolving snapshottable directories, validating `DirectorySnapshottableFeature`, and querying `FSDirSnapshotOp.getSnapshotFiles(...)`.

### Accessors and Test Hooks

- `getBlockManager()`, `setBlockManagerForTesting(...)`, `getFSDirectory()`, `setFSDirectory(...)`, `getCacheManager()`, `getErasureCodingPolicyManager()`, and `getHAContext()` expose major collaborators.
- Test-only accessors expose `EditLogTailer`, standby checkpoint time, FS lock replacement and inspection, checkpoint lock, `NameNodeResourceChecker`, snapshot manager, metrics enablement, and read/write lock reporting thresholds.
- `verifyToken(...)` delegates delegation-token validation to `DelegationTokenSecretManager`. An `InvalidToken` becomes retriable while the NameNode is transitioning to active, which is important for HA failover clients.

### Snapshot Operations

- `allowSnapshot(String path)` and `disallowSnapshot(String path)` require write operation state, superuser privilege on the path, FS write lock, safe-mode exclusion, delegation to `FSDirSnapshotOp`, edit-log sync, and audit success.
- `createSnapshot(...)` creates a snapshot through `FSDirSnapshotOp.createSnapshot(...)`, using an operation-scoped `FSPermissionChecker` and retry-cache logging. Access failures are audit-logged before rethrowing.
- `renameSnapshot(...)` computes old and new snapshot paths for audit/lock reporting and delegates to `FSDirSnapshotOp.renameSnapshot(...)`.
- `getSnapshottableDirListing()` and `getSnapshotListing(...)` are read-locked listing operations that delegate to `FSDirSnapshotOp` and audit both success and access-denied failure.
- `getSnapshotDiffReport(...)` computes a full snapshot diff, logs comparison statistics and timing from `SnapshotDiffReport.DiffStats`, and audits source/destination snapshot roots.
- `getSnapshotDiffReportListing(...)` computes a paged diff using `startPath`, `index`, and `snapshotDiffReportLimit`, allowing large diff results to be returned across multiple RPCs.
- `deleteSnapshot(...)` uses the global write lock because it collects blocks for later deletion. After the namespace mutation is logged and synced, it queues deleted blocks on `BlockManager` outside the global lock.
- `gcDeletedSnapshot(...)` removes a snapshot previously marked as deleted, asserts deleted state through `SnapshotManager`, delegates actual deletion to `FSDirSnapshotOp.deleteSnapshot(...)`, and queues blocks for deletion outside the global lock.
- `removeSnapshottableDirs(...)` removes directories from `SnapshotManager` if present.

### Rolling Upgrade

- `queryRollingUpgrade()` is superuser-only and read-locked. It returns `null` if no rolling upgrade is active; otherwise it refreshes the rollback-image-created flag from `FSImage.hasRollbackFSImage()`.
- `startRollingUpgrade()` is superuser-only and write-locked. It is idempotent if an upgrade is already active. Non-HA mode requires safe mode, saves a rollback image, leaves safe mode, and marks rollback images created. HA mode rejects safe mode, starts the internal state, logs the start edit, and rolls the edit log so standbys can tail it.
- `startRollingUpgradeInternal(...)`, `startRollingUpgradeInternalForNonHA(...)`, `setRollingUpgradeInfo(...)`, `setCreatedRollbackImages(...)`, `getRollingUpgradeInfo()`, `isNeedRollbackFsImage()`, and `setNeedRollbackFsImage(...)` maintain the in-memory rolling-upgrade flags.
- `getRollingUpgradeStatus()` returns a JMX bean or `null`, refreshing rollback-image presence under the read lock if needed.
- `isRollingUpgrade()`, `getEffectiveLayoutVersion()`, and static `getEffectiveLayoutVersion(...)` define the layout-version compatibility behavior. During rolling upgrade, the effective layout may remain at the prior storage layout if it satisfies the minimum compatible layout.
- `requireEffectiveLayoutVersionForFeature(Feature f)` rejects feature use if the effective layout version does not support it. This prevents edits unreadable by old software during downgrade-compatible rolling upgrades.
- `checkRollingUpgrade(...)` rejects starting a new rolling upgrade when one is already active.
- `finalizeRollingUpgrade()` writes finalization state, rolls edit logs for HA, updates storage version, renames rollback checkpoint image to normal image, syncs edits in non-HA mode, and audits success.

### Cache Directives and Pools

- `addCacheDirective(...)`, `modifyCacheDirective(...)`, `removeCacheDirective(...)`, and `listCacheDirectives(...)` gate `CacheManager` operations with operation checks, optional rescan waits unless `CacheFlag.FORCE` is present, locks, safe-mode checks for writes, edit-log sync after mutations, and audit logging.
- `addCachePool(...)`, `modifyCachePool(...)`, `removeCachePool(...)`, and `listCachePools(...)` provide the corresponding cache pool administration surface. Pool mutations require superuser privilege and sync the edit log after helper delegation.

### ACL, XAttr, and Access Checks

- `modifyAclEntries(...)`, `removeAclEntries(...)`, `removeDefaultAcl(...)`, `removeAcl(...)`, and `setAcl(...)` all follow the same write pattern: check operation, acquire permission checker, FS write lock, safe-mode check, delegate to `FSDirAclOp`, sync edits, and audit with resulting `FileStatus`.
- `getAclStatus(...)` is read-locked and delegates to `FSDirAclOp.getAclStatus(...)`.
- `setXAttr(...)`, `getXAttrs(...)`, `listXAttrs(...)`, and `removeXAttr(...)` wrap `FSDirXAttrOp` with equivalent read/write locking, safe-mode checks for writes, edit-log sync for mutations, and audit events.
- `removeXattr(long id, String xattrName)` implements the `SPSService`-style callback for removing a satisfy-storage-policy XAttr by inode id. It directly resolves the inode, checks its `XAttrFeature`, removes the matching XAttr through `FSDirSatisfyStoragePolicyOp`, and syncs edits.
- `checkAccess(String src, FsAction mode)` resolves symlinks/paths under read lock, verifies the target exists, and delegates to `dir.checkPathAccess(...)` when permissions are enabled.

### Encryption Zones and Re-Encryption

- `createEncryptionZone(...)` requires superuser privilege, initializes or validates the encryption key outside the FS write lock through `FSDirEncryptionZoneOp.ensureKeyIsInitialized(...)`, then creates the zone under lock and syncs the edit log.
- `getEZForPath(...)` reads the encryption zone and corresponding `FileStatus` for audit from `FSDirEncryptionZoneOp.getEZForPath(...)`.
- `listEncryptionZones(...)` is superuser-only, read-locked, and returns batched entries from `FSDirEncryptionZoneOp.listEncryptionZones(...)`.
- `reencryptEncryptionZone(...)` is superuser-only, rejects safe mode, obtains a permission checker, calls `reencryptEncryptionZoneInt(...)`, and audits the start/cancel action.
- `listReencryptionStatus(...)` returns batched re-encryption status entries from `FSDirEncryptionZoneOp.listReencryptionStatus(...)`.
- `reencryptEncryptionZoneInt(...)` validates a key provider, obtains the current key version before taking the FS write lock for `START`, resolves the zone under `dir.writeLock()`, delegates `START` or `CANCEL`, logs XAttr changes if any, unlocks, and syncs edits.
- `getEnclosingRoot(...)` returns the encryption zone path if the path is inside an EZ, otherwise root.

### Erasure Coding

- `setErasureCodingPolicy(...)`, `unsetErasureCodingPolicy(...)`, `addErasureCodingPolicies(...)`, `removeErasureCodingPolicy(...)`, `enableErasureCodingPolicy(...)`, and `disableErasureCodingPolicy(...)` enforce operation checks, feature support through `checkErasureCodingSupported(...)`, safe-mode checks for mutations, edit-log sync on actual changes, and audit logging.
- `addErasureCodingPolicies(...)` iterates over an array and returns an `AddErasureCodingPolicyResponse` per input policy, converting `HadoopIllegalArgumentException` into a per-policy failure response while still adding valid policies.
- `getECTopologyResultForPolicies(...)` is superuser-only and `OperationCategory.UNCHECKED`. It either verifies all enabled EC policies or resolves named policies and checks the current rack/DataNode topology through `ECTopologyVerifier`.
- `getErasureCodingPolicy(...)`, `getErasureCodingPolicies()`, and `getErasureCodingCodecs()` are read-locked lookup/reporting operations.
- `getVerifyECWithTopologyResult()` serializes the enabled-policy topology verifier result as JSON.
- `getEcTopologyVerifierResultForEnabledPolicies()` collects DataNode and rack counts from `DatanodeManager` and enabled policies from `ErasureCodingPolicyManager`.
- `checkErasureCodingSupported(...)` checks the effective layout version for `NameNodeLayoutVersion.Feature.ERASURE_CODING`.

### Snapshot Trash, Audit, Lock Reporting, and Metrics

- `checkAndProvisionSnapshotTrashRoots()` runs after active startup or safe-mode exit. While holding the block-manager write lock, it conditionally upgrades to the global write lock, lists snapshottable directories, checks for `.Trash` under each, and creates missing trash roots with shared trash permissions.
- `getLockReportInfoSupplier(...)` overloads lazily format lock-hold reports with remote user, remote IP, escaped source/destination, and permission info converted from `HdfsFileStatus` or `FileStatus`.
- `FSNamesystemAuditLogger` extends `DefaultAuditLogger`. It initializes caller-context and token-tracking settings from configuration and formats audit lines with allowed flag, UGI, remote IP, command, escaped source/destination, permission, optional delegation-token tracking ID, protocol, and optional truncated caller context/signature.
- `getTotalSyncCount()` and `getTotalSyncTimes()` expose edit-log sync metrics. Sync times come from `JournalSet` when available.
- `getBytesInFuture()` reports block bytes with future generation stamps, which are removable when leaving safe mode.
- `getNumInMaintenanceLiveDataNodes()`, `getNumInMaintenanceDeadDataNodes()`, and `getNumEnteringMaintenanceDataNodes()` count DataNodes in maintenance-related states for metrics.
- `checkSuperuserPrivilege(String operationName, String path)` performs path-scoped superuser checks without holding the FSNamesystem lock and logs audit failure on access denial.
- `getQuotaCommand(...)` and `getFailedStorageCommand(...)` convert low-level parameter combinations into command names for audit/event naming.
- `isObserver()` and `checkBlockLocationsWhenObserver(...)` support observer NameNode behavior. Observer reads that return located blocks with zero locations throw `ObserverRetryOnActiveException`, forcing clients to retry against active when observer state is insufficient.
- `setMetricsEnabled(...)`, `isMetricsEnabled()`, `setReadLockReportingThresholdMs(...)`, `getReadLockReportingThresholdMs()`, `setWriteLockReportingThresholdMs(...)`, and `getWriteLockReportingThresholdMs()` configure `FSNamesystemLock` reporting/metrics.

## Control Flow Patterns

Most mutating RPC bodies follow this sequence:

1. Name the operation for logging and audit.
2. Run HA state/category validation with `checkOperation(OperationCategory.WRITE)`.
3. Run superuser or permission setup when needed.
4. Acquire an FS or global write lock.
5. Re-run `checkOperation(...)` after lock acquisition.
6. Reject safe mode for namespace mutations.
7. Delegate the actual namespace or manager update to a helper class.
8. Release the lock with a lazy lock-report supplier.
9. Sync edits with `getEditLog().logSync()`.
10. Emit an audit success event, or emit audit failure before rethrowing `AccessControlException`.

Read operations follow the same pattern with `OperationCategory.READ`, read lock, helper delegation, and success/failure audit. Some observability methods avoid locks or use weaker checks because they are metrics/JMX paths; for example `getNameJournalStatus()` explicitly avoids holding an `FSEditLog` lock and uses `isOpenForWriteWithoutLock()`.

The global write lock is reserved for operations that cross namespace and block state. Snapshot deletion uses `RwLockMode.GLOBAL` because it collects blocks that must be deleted. The actual block deletion queueing happens after unlocking to avoid holding the global lock while handing work to `BlockManager`.

Rolling upgrade control flow is stateful and persistence-aware. Starting a rolling upgrade creates in-memory `RollingUpgradeInfo`, logs a start edit, and in HA mode rolls edit logs for standby consumption. Non-HA mode first saves a rollback image while in safe mode, then automatically leaves safe mode. Finalization logs the finalization edit, rolls logs in HA mode, updates storage versions, and renames rollback checkpoint files.

Re-encryption uses a two-stage flow for `START`: key-version lookup happens before the FS write lock, then XAttr state is changed under the lock. This avoids holding namespace locks while talking to key-provider-sensitive paths, while still persisting the re-encryption request as edit-log XAttr updates.

`checkAndProvisionSnapshotTrashRoots()` has unusual lock choreography. It is called while the block-manager write lock is held, may temporarily release that lock, acquire the global lock, perform operations that can call back into normal namespace methods, and then restore the BM lock on exit.

## State and Persistence Behavior

Persistent namespace mutations in this chunk are edit-log backed. Snapshot changes, cache directives/pools, ACL changes, XAttr changes, encryption-zone creation, re-encryption XAttr updates, erasure-coding policy/path changes, rolling-upgrade start/finalize events, and satisfy-storage-policy XAttr removals all require edit-log sync after the in-memory update. The `logRetryCache` argument on many mutating operations controls whether retry-cache metadata is recorded with the edit, allowing idempotent RPC replay after failover or client retry.

Snapshot deletion produces two kinds of state: namespace state changed by `FSDirSnapshotOp` and block-deletion work queued through `BlockManager.addBLocksToMarkedDeleteQueue(...)`. The queueing is deliberately outside the global lock after edit-log sync, so tests should distinguish durable namespace deletion from asynchronous block invalidation.

Rolling upgrade state is partly in memory (`rollingUpgradeInfo`, `needRollbackFsImage`) and partly on disk (`IMAGE_ROLLBACK`, image storage layout version, finalized image rename). `getEffectiveLayoutVersion()` controls which layout version newly written images/edit segments use while a rolling upgrade is active.

Cache state is managed by `CacheManager` and persisted through edit logs via `FSNDNCacheOp`. Listing waits for cache rescans unless the write operation was forced, making cache operation latency depend on the manager's rescan lifecycle.

Encryption zone and re-encryption state is stored as namespace metadata/XAttrs and depends on key-provider state. `createEncryptionZone` validates key metadata before the namespace mutation. Re-encryption start persists the chosen key version in XAttr updates, and cancel updates XAttrs to stop the workflow.

Erasure coding policy state is held by `ErasureCodingPolicyManager` and/or namespace metadata, gated by layout-version support. Adding policies can partially succeed across an input array, so callers must inspect each `AddErasureCodingPolicyResponse`.

Audit state is not namespace state but is externally visible and security-significant. The default audit logger includes escaped paths, permissions, protocol, optional token tracking IDs, and optional caller context depending on configuration.

## Dependencies and Integration Points

This chunk integrates with core NameNode collaborators:

- `BlockManager`, `DatanodeManager`, `DatanodeDescriptor`, `NetworkTopology`, and block deletion queues for maintenance metrics, topology checks, corrupt blocks, and snapshot deletion fallout.
- `FSDirectory`, `FSPermissionChecker`, `INodesInPath`, `INode`, `XAttrFeature`, and helper operation classes for namespace reads and mutations.
- `FSImage`, `FSEditLog`, `JournalAndStream`, `EditLogOutputStream`, `JournalSet`, `NNStorage`, and `StorageDirectory` for persistence, journal status, layout versions, rolling upgrade, and sync metrics.
- `SnapshotManager`, `Snapshot`, `DirectorySnapshottableFeature`, `SnapshotDiffReport`, `SnapshotDiffReportListing`, `SnapshottableDirectoryStatus`, and `SnapshotStatus`.
- `CacheManager`, `CacheDirectiveInfo`, `CacheDirectiveEntry`, `CachePoolInfo`, `CachePoolEntry`, `CacheFlag`, and batched-list result types.
- Hadoop security types: `UserGroupInformation`, `DelegationTokenIdentifier`, `DelegationTokenSecretManager`, `TokenIdentifier`, `AuthenticationMethod`, `FSPermissionChecker`, `AccessControlException`, and `CallerContext`.
- Encryption/key types: `EncryptionZone`, `FSDirEncryptionZoneOp`, `ReencryptAction`, `ZoneReencryptionStatus`, `Metadata`, and XAttr types.
- Erasure coding types: `ErasureCodingPolicy`, `ErasureCodingPolicyInfo`, `AddErasureCodingPolicyResponse`, `ECTopologyVerifier`, `ECTopologyVerifierResult`, and `NameNodeLayoutVersion.Feature.ERASURE_CODING`.
- RPC/HA integration: `OperationCategory`, `HAContext`, observer service state, `ObserverRetryOnActiveException`, standby behavior, and `RetriableException` during activation.
- JMX/metrics integration through `NameNodeMXBean`, `FSNamesystemMBean`, Hadoop `@Metric`, JSON serialization, and audit log configuration keys.

## Risks and Edge Cases

- Many methods rely on double `checkOperation(...)` calls, before and after lock acquisition. Removing either check can break HA state transitions where an operation becomes invalid while waiting for a lock.
- Safe-mode checks must occur under the write lock for mutations. Moving them outside can race with safe-mode entry/exit.
- Snapshot deletion and GC collect blocks under the global lock but enqueue deletion outside it. Reordering edit-log sync, unlock, and deletion queueing can create durability or deadlock regressions.
- `deleteSnapshot(...)` initializes `rootPath` inside the lock. If an access failure or validation exception happens earlier, audit may log a null path.
- `getSnapshotDiffReport(...)` may be expensive and logs timing stats. Large diffs should use `getSnapshotDiffReportListing(...)` to avoid oversized RPC responses.
- `getNameJournalStatus()` reads edit-log status without full synchronization by design. It is suitable for metrics but may expose transient stream state.
- `getNodeUsage()` computes median as `usages[length / 2]`, not the average of the two middle values for even counts. Tests and dashboards should match this implementation.
- Rolling upgrade layout-version gating is correctness-critical. Allowing new edit-log features while effective layout is old can make downgrade impossible.
- Non-HA rolling upgrade start calls `saveNamespace(...)` and then leaves safe mode automatically. Failures in this sequence can leave rollback-image and safe-mode state needing careful recovery.
- `finalizeRollingUpgrade()` updates storage version and renames rollback images while holding the FS write lock. Storage failures here can affect restart/downgrade behavior.
- Cache operations can block on `cacheManager.waitForRescanIfNeeded()` unless `FORCE` is supplied, so they can be unexpectedly slow.
- `addErasureCodingPolicies(...)` can partially succeed and still sync/audit once. Callers cannot treat an array return as all-or-nothing.
- `enableErasureCodingPolicy(...)` and `disableErasureCodingPolicy(...)` only sync/audit success when the helper reports a real change. No-op calls may return false without an audit success event.
- `createEncryptionZone(...)` checks key initialization before acquiring the FS write lock. The key provider or key metadata can change between that check and namespace mutation if external systems are modified concurrently.
- `reencryptEncryptionZoneInt(...)` acquires both FSNamesystem and FSDirectory write locks. Lock ordering must remain consistent with the rest of NameNode code.
- `removeXattr(long id, String xattrName)` returns silently for missing inode, missing XAttr feature, or missing XAttr name, but still syncs after unlocking. That behavior matters for idempotent SPS cleanup.
- `checkAndProvisionSnapshotTrashRoots()` calls `getRemoteUser()` while provisioning system-created trash directories. The effective user and audit context can matter in tests.
- The default audit logger escapes Java strings for `src` and `dst`, truncates caller context, and conditionally logs token tracking IDs. Changing formatting can break audit log parsers.
- `checkSuperuserPrivilege(...)` is documented to run without holding the FSN lock. Calling it under locks would increase deadlock risk and could cause audit side effects under lock.
- Observer reads with zero block locations intentionally force retry on active. Tests should cover null `LocatedBlocks`, null located-block lists, and empty location arrays separately.

## Test Signals

Useful tests for this chunk should include:

- JMX JSON tests for entering-maintenance nodes, name directory status, node usage, journal status, journal transaction info, corrupt file count/list, rolling upgrade status, EC topology result, and maintenance-node metrics.
- Corrupt block listing tests covering non-snapshot paths, snapshot paths from snapshottable directories, invalid snapshottable directory input, continuation cookies, standby exceptions, and I/O failure logging.
- Delegation token tests where invalid tokens are normal failures outside activation but become `RetriableException` during transition to active.
- Snapshot operation tests for allow/disallow/create/rename/list/full diff/paged diff/delete/gc, including permission failure audit, safe-mode rejection, retry-cache logging, global-lock deletion behavior, and block deletion queue handoff.
- Rolling upgrade tests for query-before-start, idempotent start, non-HA safe-mode requirement and rollback-image save, HA edit-log rolling, effective layout version selection, feature rejection during rolling upgrade, and finalization storage updates.
- Cache directive and pool tests for add/modify/remove/list, `FORCE` versus rescan waits, safe-mode rejection, superuser requirements for pools, retry-cache persistence, and audit payloads.
- ACL and XAttr tests for each mutating method, edit-log sync, returned audit `FileStatus`, access denial audit, safe-mode rejection, read listing/status behavior, and SPS XAttr removal by inode id.
- Encryption-zone tests for missing key provider/key metadata, successful zone creation, access-denied audit, `getEZForPath`, batched zone listing, re-encryption start/cancel, re-encryption status listing, and XAttr edit logging.
- Erasure coding tests for layout-version support checks, set/unset policy, add policy partial success, remove/enable/disable no-op behavior, policy/codecs reads, named policy topology verification, and enabled-policy topology JSON.
- Audit logger tests for debug command filtering, escaped source/destination, null permissions, permission formatting, token tracking ID inclusion for token-authenticated users, protocol field, caller context truncation, and caller signature size limits.
- Lock-reporting tests for `HdfsFileStatus` to `FileStatus` conversion, symlink handling, null status handling, remote user/IP capture, and metrics threshold setters.
- Snapshot trash provisioning tests in HA active, HA non-active, non-HA, safe-mode, and disabled-configuration states, including lock upgrade/restore behavior and missing `.Trash` creation with shared trash permissions.
- Observer tests verifying that a located block with zero locations triggers `ObserverRetryOnActiveException`, while null blocks or populated locations do not.

## Chunk Boundary Notes

The requested range begins at line 6900, inside the body of `getEnteringMaintenanceNodes()`, and ends at the final class brace. Earlier chunks are needed for the full `FSNamesystem` class context, including fields, constructors, lock helpers, core file/block RPCs, and the first part of DataNode/JMX reporting. This document is intentionally a chunk report only; the final source-tree-aligned per-file research document should be synthesized later from all `FSNamesystem.java` chunks.
