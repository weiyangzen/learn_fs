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
