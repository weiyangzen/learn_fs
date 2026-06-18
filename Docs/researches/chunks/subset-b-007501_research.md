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
