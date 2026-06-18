# Research: subset-b-008104

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/OMRangerBGSyncService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/OMRangerBGSyncService.java

Purpose: `OMRangerBGSyncService` is a leader-only `BackgroundService` that reconciles Ozone Manager multi-tenancy state in OM DB with Ranger policies and roles. OM DB is treated as the source of truth; Ranger is eventually corrected after OM crashes, Ranger failures, manual Ranger edits, or interleaved tenant operations.

Important APIs and types: the public constructor wires `OzoneManager`, `OMMultiTenantManager`, `MultiTenantAccessController`, service interval, and timeout. `getTasks()` returns a single `RangerBGSyncTask`; `start()` and `shutdown()` maintain `isServiceStarted`; `triggerRangerSyncOnce()` is the testable one-shot sync entrypoint. State is staged in `mtRangerPoliciesToBeCreated`, `mtRangerPoliciesToBeDeleted`, `mtRangerRoles`, and `mtOMDBRoles`. Helper types are `BGRole`, `PolicyType`, and `PolicyInfo`.

Control flow: `RangerBGSyncTask.call()` first checks `shouldRun()`, which requires a started service, initialized Ratis server, and `ozoneManager.isLeaderReady()`. `triggerRangerSyncOnce()` compares the persisted OM DB Ranger service version with `accessController.getRangerServicePolicyVersion()`. While the values differ, up to `MAX_ATTEMPT` times, it executes OM-to-Ranger reconciliation, writes the observed Ranger version back through a Ratis `SetRangerServiceVersion` request, and then re-reads Ranger's service version. The extra second attempt is intentional because Ranger updates normally bump the Ranger service version.

Policy reconciliation: `executeOMDBToRangerSync()` clears staging maps, then uses `withOptimisticRead()` on the `AuthorizerLock` to load labeled Ranger policies, load all Ranger roles referenced by those policies, and load OM role membership from cache or DB. `processAllPoliciesFromOMDB()` iterates tenant state rows, expects each tenant's bucket namespace and bucket policies, removes matching Ranger entries from the delete map, queues missing policies for recreation, and deletes leftover labeled Ranger policies. Missing policies are recreated through default policy builders on `OMMultiTenantManager`, and all Ranger mutations run under `withWriteLock()`.

Role reconciliation: `loadAllRolesFromOM()` prefers `OMMultiTenantManagerImpl.getAllRolesFromCache()` and falls back to DB tables. `loadAllRolesFromDB()` builds role-to-user sets from tenant state and tenant access ID records, including admin-role membership when `isAdmin` is true. `processAllRolesFromOMDB()` creates missing Ranger roles, compares Ranger user sets against OM DB sets, pushes full OM DB role membership via `updateRole()`, and then deletes leftover Ranger roles in reverse sorted order so user roles are attempted before admin roles.

State, persistence, and dependencies: persistent state is split between OM DB tenant/access/meta tables and Ranger's external service. The OM DB service-version update is submitted through `OzoneManagerRatisUtils`, so followers apply the same version marker. Ranger operations are performed through `MultiTenantAccessController`. The service relies on `AuthorizerLock` optimistic reads and write locks to coordinate against live tenant mutation requests.

Risks: Ranger calls can be slow and may race with OM leadership changes; `checkLeader()` is called before Ranger requests to abort stale leaders, with a test flag escape hatch. The service catches most Ranger create/delete/update failures inside write-lock blocks and relies on future runs. `withOptimisticRead()` retries only twice, so high tenant mutation activity can postpone convergence. `processAllRolesFromOMDB()` mutates the `BGRole` Ranger user set while comparing; this is safe because the map is per-run scratch state but would be risky if reused elsewhere.

Test signals: integration tests reference `TestRangerBGSyncService`, `TestOzoneTenantShell`, and `TestMultiTenantVolume`. They exercise one-shot sync, version persistence, Ranger state recovery, and tenant-shell paths. Unit-sensitive paths include the in-memory access controller fallback, leader skip flag, and `getRangerSyncRunCount()`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/OMRangerBGSyncService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/OpenKeyCleanupService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/OpenKeyCleanupService.java

Purpose: `OpenKeyCleanupService` is a single-threaded OM background service that cleans expired open-key metadata. It deletes abandoned non-hsync open keys and commits expired hsync keys so client-side lease loss does not leave indefinite metadata or block namespace accounting.

Important APIs and types: the constructor reads open-key expiration, lease hard/soft limits, and per-task cleanup limit from configuration. Test hooks include `suspend()`, `resume()`, and `getSubmittedOpenKeyCount()`. `getTasks()` returns two `OpenKeyCleanupTask` instances, one for `BucketLayout.DEFAULT` and one for `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

Control flow: each task requires `!suspended` and `ozoneManager.isLeaderReady()`. It calls `keyManager.getExpiredOpenKeys(expireThreshold, cleanupLimitPerTask, bucketLayout, leaseThreshold)`, counts expired non-hsync keys grouped into `OpenKeyBucket` builders, submits a single `DeleteOpenKeys` OM request for those groups, then individually submits `CommitKey` requests for hsync builders. Successful responses update OM metrics for cleaned and hsync-cleaned open keys, record performance latency, and add to `submittedOpenKeyCount`.

State and persistence behavior: the service never mutates RocksDB tables directly. It submits Ratis-backed `OMRequest`s with a service-owned random `ClientId` and monotonically increasing `callId`, letting normal OM request handlers apply table mutations. This protects leader/follower consistency and keeps cleanup idempotent if a key is committed or removed between scan and request execution.

Dependencies and integration points: it depends on `KeyManager` for expiration scanning, `ExpiredOpenKeys` for split non-hsync/hsync results, `OzoneManagerRatisUtils` for submission, and OM metrics/perf metrics for observability. It is integrated through key-manager service startup and handles both OBS and FSO layouts explicitly.

Risks: the constructor throws if the hard lease limit is below the soft limit, making misconfiguration fail early. Cleanup is bounded by `cleanupLimitPerTask`, but both layout tasks run each cycle, so aggregate work can be twice the configured limit. Hsync commit requests are submitted one at a time, which is simple but potentially expensive under many expired hsync keys. The service logs and retries later on scan or Ratis submission failure.

Test signals: `TestOpenKeyCleanupService`, `TestHSync`, `TestHSyncUpgrade`, `TestOzoneShellHA`, and multipart-abort tests cover expired-key deletion, hsync commit handling, recovery-flag cases, service suspension, and interactions with client-visible lease behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/OpenKeyCleanupService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/QuotaRepairTask.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/QuotaRepairTask.java

Purpose: `QuotaRepairTask` is an asynchronous repair operation that recomputes bucket used-bytes and namespace counts from OM metadata and submits a Ratis `QuotaRepair` request containing only the needed deltas. It can repair all buckets or a supplied list of bucket keys.

Important APIs and types: `repair()` and `repair(List<String>)` start the asynchronous task and return `CompletableFuture<Boolean>`. `getStatus()` exposes the static `RepairStatus` JSON-like status. Internal helpers create an active DB checkpoint, prepare bucket maps, recalculate counts, and submit the final request. `CountPair` stores atomic space and namespace totals; `RepairStatus` records task id, start/finish times, errors, and per-bucket diffs.

Control flow: only one repair may run because `IN_PROGRESS` is a static `AtomicBoolean`. `repairTask()` creates a fixed thread pool sized for three table families and their worker threads, opens an active DB checkpoint via `createActiveDBCheckpoint()`, calls `repairActiveDb()`, builds a `QuotaRepairRequest`, and submits it through Ratis. Cleanup shuts down the executor, removes the temporary checkpoint directory, and clears `IN_PROGRESS`.

Counting algorithm: `prepareAllBucketInfo()` loads selected buckets or all bucket table entries, copies original bucket info, resets mutable used counters, and indexes each bucket by OBS name prefix and FSO volume/bucket object-ID prefix. `repairCount()` initializes count maps for key, file, and directory tables, then scans OBS key table, FSO key table, and directory table concurrently. `recalculateUsages()` batches table key/value rows into an `ArrayBlockingQueue`; worker tasks call `extractCount()`, which derives the first two path components as the bucket prefix, increments namespace by one, and increments space for `OmKeyInfo` values by replicated size. Counts are merged into `OmBucketInfo` objects and converted to delta fields.

State and persistence behavior: the scan is done against a checkpoint metadata manager, avoiding long reads over a mutating active DB. Persistent updates are not local writes; the built `QuotaRepairRequest` goes through `OzoneManagerRatisUtils.submitRequest()`. The request also carries `supportOldQuota` flags for buckets with legacy quota defaults and a volume-level old-quota flag for full repairs.

Dependencies and integration points: the class depends on OM metadata tables, `OmMetadataManagerImpl.createCheckpointMetadataManager`, `DBCheckpoint`, `OmBucketInfo`, `OmKeyInfo`, and protocol `BucketQuotaCount`. It is likely invoked by OM admin commands or internal repair paths rather than as a periodic `BackgroundService`.

Risks: temporary checkpoint cleanup deletes and recreates `temp-repair-quota` under the DB parent directory; any unexpected reuse of that path would be destructive. `executor.shutdown()` assumes the executor was created, which is true after `repairTask()` starts but worth preserving. Interrupt handling in `recalculateUsages()` resets the interrupt flag but does not fail the repair immediately. Prefix parsing assumes OM key path shape `/<volume>/<bucket>/...` for both name and ID forms.

Test signals: `TestQuotaRepairTask` covers full and bucket-scoped repairs. Broader quota tests should validate old-quota compatibility, OBS/FSO mixed counts, directory namespace inclusion, and failure status serialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/QuotaRepairTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/SnapshotDeletingService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/SnapshotDeletingService.java

Purpose: `SnapshotDeletingService` reclaims metadata from deleted snapshots. It walks the snapshot chain, moves deleted-key, deleted-directory, and rename records from a deleted snapshot toward the next active snapshot or active object store, and purges snapshot metadata once no moveable records remain.

Important APIs and types: it extends `AbstractKeyDeletingService` and returns a single `SnapshotDeletingTask`. The constructor wires `OzoneManager`, `OmSnapshotManager`, `SnapshotChainManager`, cleanup limits, Ratis byte limit, and a `MultiSnapshotLocks` instance over `SNAPSHOT_GC_LOCK`. Public/test APIs include `shouldIgnoreSnapshot()`, `getTasks()`, and `getSuccessfulRunCount()`.

Control flow: `SnapshotDeletingTask.call()` first requires `shouldRun()`, then iterates the chain manager in deleted-snapshot order while snapshot and key limits remain. It skips active snapshots and deleted snapshots whose DB changes are not flushed. It also skips a deleted snapshot when the next snapshot in the chain is itself deleted, avoiding pointless moves into a soon-to-be-deleted target. For each processable snapshot, it locks the current snapshot ID and, if present, the next active snapshot ID, opens the snapshot DB from `OmSnapshotManager`, pulls bounded entries from deleted key, deleted dir, and rename tables, and submits `SnapshotMoveTableKeys` requests. If no entries remain, it queues the snapshot for a `SnapshotPurge` request.

Batching behavior: `submitSnapshotMoveDeletedKeysWithBatching()` builds batches constrained by `ratisByteLimit`, calculated as 90 percent of the OM Ratis log appender queue byte limit. It adds deleted keys first, renamed keys second, and deleted dirs third, flushing before an addition would exceed the limit. `submitSingleSnapshotMoveBatch()` converts each batch into a `SnapshotMoveTableKeysRequest` with `fromSnapshotID` and checks the `OMResponse` success flag.

State and persistence behavior: the service does not directly edit snapshot metadata tables. It reads snapshot-local tables and submits Ratis requests for move and purge operations. This centralizes state transitions in OM request handlers and lets followers replay the same changes. `successRunCount` increments after each snapshot processed, not necessarily after full deletion completion.

Dependencies and integration points: key dependencies include `SnapshotChainManager`, `SnapshotUtils`, `OmSnapshotManager`, per-snapshot `KeyManager`, `MultiSnapshotLocks`, `ClientVersion` protobuf conversion, and `OzoneManagerRatisUtils` inherited submission. It interacts closely with key deleting service behavior, snapshot flush state, and snapshot cache lifetimes.

Risks: the service holds snapshot GC locks while reading snapshot tables and submitting Ratis move requests, so slow submissions can extend lock hold time. Oversized individual entries larger than the byte limit are still added to an empty batch and submitted, so only aggregate batching is enforced. Failure to acquire locks silently continues to the next candidate. Correctness depends on deleted snapshots being processed in chain order and on request handlers moving data to the intended next active snapshot or AOS.

Test signals: `TestSnapshotDeletingService`, `TestSnapshotDeletingServiceIntegrationTest`, `TestDirectoryDeletingServiceWithFSO`, HA snapshot tests, and checkpoint servlet tests cover batching, service suspension/resume, failover, locking, deleted-dir movement, and interactions with active object store cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/SnapshotDeletingService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/SnapshotDiffCleanupService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/SnapshotDiffCleanupService.java

Purpose: `SnapshotDiffCleanupService` is a single-threaded background service that removes persisted snapshot-diff reports and moves old terminal or stale jobs out of the active job table. It keeps snapshot diff metadata bounded after jobs are done, cancelled, failed, rejected, or old enough to be considered stale.

Important APIs and types: the constructor receives the RocksDB handle, column family handles for active jobs, purged jobs, and reports, and a `CodecRegistry`. `run()` is the testable cleanup operation. `getEntryFromPurgedJobTable()` exposes purge-table content for tests. Background execution is via nested `SnapshotDiffCleanUpTask`.

Control flow: `run()` intentionally removes reports first by calling `removeOlderJobReport()`, then calls `moveOldSnapDiffJobsToPurgeTable()`. This order avoids a window where a snapshot-diff request sees a completed active job moved to purge while its report has already disappeared. `SnapshotDiffCleanUpTask.call()` checks `shouldRun()`, increments `runCount`, and invokes `run()`.

RocksDB behavior: `moveOldSnapDiffJobsToPurgeTable()` iterates the active job column family, decodes `SnapshotDiffJob`, and for up to `maxJobToPurgePerTask` jobs writes the job ID and total diff entry count into the purged-job column family and deletes the active-job key. Jobs qualify if older than `maxAllowedTime` or status is `FAILED`, `REJECTED`, or `CANCELLED`; stale queued/in-progress jobs are intentionally purged by age. `removeOlderJobReport()` iterates purged jobs, deletes the report range from `jobId + DELIMITER + 0` to the lexicographically higher job prefix, then deletes the purged-job entry.

State and persistence behavior: this class writes directly to RocksDB using `ManagedWriteBatch` and `ManagedWriteOptions`, not Ratis. That is appropriate for local snapshot diff job/report metadata but means callers must understand the column families' replication and lifecycle semantics. `successRunCount` is present but never incremented, so it does not currently measure successful runs.

Dependencies and integration points: it depends on `SnapshotDiffJob`, Ozone snapshot diff statuses, RocksDB managed wrappers, and OM configuration keys for max jobs per task and report persistence time. It is owned by the snapshot manager and referenced by integration tests for snapshot diff lifecycle.

Risks: `shouldRun()` only checks suspension; a TODO notes that `ozoneManager.isLeaderReady()` was removed for Mockito-related test failures. In HA deployments, direct RocksDB cleanup without a leader check deserves scrutiny. Runtime exceptions are thrown for RocksDB/codec failures rather than being handled gracefully. The report-first cleanup protocol assumes a full cleanup interval passes before any consumer reads reports for purged jobs.

Test signals: `TestSnapshotDiffCleanupService`, `TestSnapshotDiffManager`, and `TestOmSnapshot` exercise job movement and report deletion. Tests should also pin `successRunCount` semantics if it becomes observable.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/SnapshotDiffCleanupService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/package-info.java

Purpose: this package descriptor documents `org.apache.hadoop.ozone.om.service` as the package containing Ozone Manager background services.

Important APIs and types: it declares only the package and contains no exported Java types, functions, or runtime logic. Its role is Javadoc/package metadata rather than behavior.

Control flow and state: none. There is no persistence, no dependencies beyond the Java package declaration, and no integration code.

Integration points: the package contains service implementations such as open-key cleanup, snapshot deletion, snapshot diff cleanup, Ranger background sync, quota repair, and related OM maintenance services. This file gives generated Javadocs a package-level description.

Risks: low. The only meaningful risk is documentation drift if the package grows beyond background service responsibilities.

Test signals: no direct tests are expected for this descriptor.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/FSODirectoryPathResolver.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/FSODirectoryPathResolver.java

Purpose: `FSODirectoryPathResolver` resolves absolute bucket-relative paths for FSO directory object IDs. It implements `ObjectPathResolver` for directory metadata stored in OM's FSO directory table.

Important APIs and types: the constructor takes a table key prefix, bucket object ID, and `Table<String, OmDirectoryInfo>`. The primary API is `getAbsolutePathForObjectIDs(Optional<Set<Long>>, boolean)`, which returns `Map<Long, Path>` and can either skip unresolved IDs or fail fast.

Control flow: the resolver copies the requested object IDs into a mutable set, seeds a breadth-first traversal with the bucket root pair `(bucketId, ROOT_PATH)`, and records the root path if requested. While there are queued parents and unresolved IDs, it opens a table iterator at `prefix + parentObjectId + OM_KEY_PREFIX`, treats returned `OmDirectoryInfo` values as children, resolves child paths by appending child names to the parent path, records requested IDs, and enqueues every child for further traversal.

State and persistence behavior: the class is stateless apart from constructor fields. It reads the directory table with prefix iterators and does not mutate metadata. The returned paths are derived from table contents at read time.

Dependencies and integration points: it depends on OM key prefix conventions, `OmDirectoryInfo` object IDs/names, Apache Commons `Pair`, Guava `Sets`, and the `ObjectPathResolver` interface. Snapshot diff and reclaimable-object code can use it to present FSO directory IDs as paths.

Risks: traversal breadth is limited only by table contents and requested IDs; large unresolved sets may walk large directory subtrees. Iterator prefix correctness depends on the provided `prefix` matching the bucket's directory table key layout. If `skipUnresolvedObjs` is false, stale or cross-bucket IDs cause `IllegalArgumentException`.

Test signals: `TestFSODirectoryPathResolver` covers path resolution behavior, including root and nested directories.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/FSODirectoryPathResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/MultiSnapshotLocks.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/MultiSnapshotLocks.java

Purpose: `MultiSnapshotLocks` is a small lock helper for acquiring and releasing read or write locks over multiple snapshot IDs as one logical operation.

Important APIs and types: constructors accept an `IOzoneManagerLock`, lock `Resource`, read/write mode, and optional expected lock count. `acquireLock(Collection<UUID>)` maps UUIDs to one-element lock key arrays and delegates to `acquireWriteLocks()` or `acquireReadLocks()`. `releaseLock()` releases the recorded keys. Test-visible `getObjectLocks()` exposes held key arrays, and `isLockAcquired()` mirrors the latest lock details.

Control flow: `acquireLock()` is synchronized and refuses nested acquisition on the same helper instance by throwing `OMException(INTERNAL_ERROR)` if a lock is already recorded. Null IDs are filtered out. On successful acquisition, the helper records all key arrays and sets internal details to an acquired sentinel; otherwise it records not-acquired. `releaseLock()` releases exactly the recorded keys and clears them.

State and persistence behavior: no persistent state. Runtime state is the list of currently held lock keys and an `OMLockDetails` flag.

Dependencies and integration points: it wraps `IOzoneManagerLock` and is used by `SnapshotDeletingService` to lock a deleted snapshot and the next active snapshot before moving snapshot metadata. The caller is responsible for supplying IDs in chain-safe order to avoid deadlocks, as noted in local comments elsewhere.

Risks: if release is called without a successful acquire, it delegates with an empty key list; behavior depends on the lock implementation. The class records acquired state using empty sentinel lock details rather than the exact details returned by the underlying lock. Reusing one instance concurrently across unrelated operations is prevented by synchronization but still not a good ownership model.

Test signals: `TestMultiSnapshotLocks` validates multiple lock acquisition, nested acquisition errors, and read/write release behavior. Integration tests mock construction in snapshot deletion scenarios.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/MultiSnapshotLocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/OMDBCheckpointUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/OMDBCheckpointUtils.java

Purpose: `OMDBCheckpointUtils` contains utility methods for OM DB checkpoint transfer behavior, especially snapshot-data inclusion and tarball size estimation.

Important APIs and types: `includeSnapshotData(HttpServletRequest)` reads the `OZONE_DB_CHECKPOINT_INCLUDE_SNAPSHOT_DATA` request parameter and parses it as a boolean. `logEstimatedTarballSize(Path dbLocation, Collection<Path> snapshotPaths)` counts SST files and byte size under the active DB path and optionally supplied snapshot paths.

Control flow: `logEstimatedTarballSize()` creates Commons IO path counters and a `CountingPathVisitor` configured with an SST suffix file filter and a directory-true filter. It walks the DB location, then walks each snapshot directory when the collection is non-empty, and logs total kilobytes, file count, and snapshot count. Exceptions are caught and logged; checkpoint streaming should not fail solely because estimation failed.

State and persistence behavior: no state is written. The utility performs filesystem reads only.

Dependencies and integration points: it depends on servlet requests, Commons IO file visitors, `ROCKSDB_SST_SUFFIX`, and `OZONE_DB_CHECKPOINT_INCLUDE_SNAPSHOT_DATA`. It is likely used by OM DB checkpoint servlet or transfer code when snapshot SST data can be included in checkpoint downloads.

Risks: the byte count is an estimate over files matching the SST filter; it may not account for hardlink de-duplication or files created/deleted during traversal. Logging errors instead of propagating them is intentional but can hide repeated filesystem permission problems unless logs are monitored.

Test signals: checkpoint servlet integration tests, especially inode-based transfer tests, are the expected coverage area.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/OMDBCheckpointUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/OMSnapshotDirectoryMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/OMSnapshotDirectoryMetrics.java

Purpose: `OMSnapshotDirectoryMetrics` is an `OMPeriodicMetrics` and Hadoop `MetricsSource` implementation that tracks disk usage and SST counts for the `db.snapshots` directory and the SST backup directory.

Important APIs and types: `create()` registers the metrics source with `DefaultMetricsSystem`. `updateMetrics()` performs synchronous refresh. `getMetrics()` emits gauges. Test-visible getters expose cached gauge values. `unRegister()` stops the periodic scheduler and unregisters the source. `SnapshotMetricsInfo` enumerates metric names and descriptions.

Control flow: on each update, the class verifies the metadata store is an `RDBStore`, obtains `snapshotsParentDir`, validates that it exists as a directory, obtains the optional RocksDB checkpoint differ SST backup directory, and calls `calculateAndUpdateMetrics()`. Invalid or failing conditions call `resetMetrics()` and return false. `calculateAndUpdateMetrics()` lists immediate snapshot checkpoint directories, counts each as one snapshot, and calls `calculateDirSize()` for each. Backup directory size/count is calculated separately.

State and persistence behavior: the class only updates in-memory `MutableGaugeLong` metrics. It does not persist state. To avoid double-counting hardlinked snapshot SST files, it tracks visited inode/file keys across snapshot directories. If inode retrieval is unsupported or fails, it falls back to path-plus-size or direct file size counting.

Dependencies and integration points: it depends on OM metadata store APIs, `RDBStore`, `RocksDBCheckpointDiffer`, `IOUtils.getINode()`, Hadoop metrics2, and `ROCKSDB_SST_SUFFIX`. It reports operational signals for snapshot storage growth and backup SST retention.

Risks: `calculateDirSize()` only lists one directory level and does not recursively walk subdirectories; this is probably aligned with RocksDB checkpoint SST layout but should be revisited if checkpoint structure changes. It collects stream contents to lists before iteration, trading simplicity for extra memory. The inode fallback can overcount hardlinks on filesystems without inode support.

Test signals: direct tests should assert reset behavior, inode de-duplication, SST suffix filtering, backup directory counting, and unregister behavior. Checkpoint servlet/inode transfer integration tests also provide indirect signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/OMSnapshotDirectoryMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/ObjectPathResolver.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/ObjectPathResolver.java

Purpose: `ObjectPathResolver` is a small interface for resolving object IDs to filesystem paths in snapshot-related code.

Important APIs and types: `getAbsolutePathForObjectIDs(Optional<Set<Long>> objIds, boolean skipUnresolvedObjs)` is the core contract and may throw `IOException`. The default overload calls it with `skipUnresolvedObjs=false`.

Control flow and state: the interface itself has no state or implementation beyond the default overload. Implementations decide how to traverse metadata and how to handle missing IDs.

Dependencies and integration points: it is implemented by `FSODirectoryPathResolver`, which resolves FSO directory IDs through OM directory tables. Other snapshot diff or filtering code can depend on the interface rather than specific table layouts.

Risks: callers must understand the behavior of `Optional.empty()` and the unresolved-object flag in the concrete implementation they use. The default overload is strict and can throw for unresolved object IDs.

Test signals: tests target implementations, especially `TestFSODirectoryPathResolver`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/ObjectPathResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/OmSnapshotLocalDataManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/OmSnapshotLocalDataManager.java

Purpose: `OmSnapshotLocalDataManager` owns local, non-Ratis snapshot metadata stored next to snapshot checkpoint directories as YAML. It records live SST files, snapshot-local versions, previous snapshot IDs, previous-version dependencies, defrag timestamps, and purge transaction metadata. It also mirrors those YAML dependencies in an in-memory directed graph to validate updates and prune orphan versions.

Important APIs and types: public creation/access methods include `createNewOmSnapshotLocalDataFile()`, `getOmSnapshotLocalDataMeta()`, `getOmSnapshotLocalData()`, `getWritableOmSnapshotLocalData()`, and static `getSnapshotLocalPropertyYamlPath()`. Nested provider types are `ReadableOmSnapshotLocalDataMetaProvider`, `ReadableOmSnapshotLocalDataProvider`, and `WritableOmSnapshotLocalDataProvider`. Internal model types are `LocalDataVersionNode` and `SnapshotVersionsMeta`.

Initialization flow: the constructor builds a YAML serializer that computes checksums, initializes `localDataGraph`, `versionNodeMap`, locks, orphan-check tracking, and optionally a scheduler. `init()` obtains the snapshot directory from `RDBStore`, creates missing YAML files during pre-`SNAPSHOT_DEFRAG` upgrade, loads YAML files matching the active DB checkpoint prefix, verifies each file path matches its snapshot ID, and calls `addVersionNodeWithDependents()` so previous snapshot dependencies are loaded before dependents. Every loaded snapshot ID is queued for orphan checking.

Graph and version behavior: each `LocalDataVersionNode` represents `(snapshotId, version, previousSnapshotId, previousSnapshotVersion)`. Edges point from a version to the version it depends on in the previous snapshot. `addSnapshotVersionMeta()` validates that previous versions are loaded, adds nodes, and connects edges. `validateVersionRemoval()` prevents removing a version while other graph nodes still depend on it. `upsertNode()` removes old nodes, stores predecessor relationships, adds new nodes, and reconnects predecessors for versions that remain.

Readable provider flow: a readable provider acquires a per-snapshot read lock, loads and validates YAML, optionally resolves its previous snapshot reference against a requested snapshot ID, and lazily loads previous snapshot local data. Resolution can walk backward through the previous-snapshot chain, acquiring read locks in order and replacing version metadata so the current data points to the relative previous version for the resolved snapshot. `needsDefrag()` checks the explicit flag and whether the current version points to an older previous snapshot version than the resolved previous snapshot's latest version.

Writable provider flow: writable providers acquire write locks. Mutators add snapshot versions from live RocksDB SST metadata, remove versions, set purge transaction info, and mark the provider dirty. `commit()` validates modifications, atomically writes YAML through a `.tmp` file and `ATOMIC_MOVE`, persists `lastDefragTime` for new versions, deletes YAML when no versions remain, updates the in-memory graph, and queues potential orphan checks when previous IDs or versions changed.

State and persistence behavior: durable state is YAML files named from `OmSnapshotManager.getSnapshotPath(..., 0)` plus the YAML extension. In-memory state is `versionNodeMap`, `localDataGraph`, and orphan-check counts protected by per-snapshot hierarchical locks and an internal read/write lock. `checkOrphanSnapshotVersions()` removes unreferenced non-current versions and removes version zero only when the snapshot is purged; if purge transaction info remains and versions remain, it requeues the snapshot for later checks.

Dependencies and integration points: it depends on snapshot info tables, `SnapshotChainManager`, `OMLayoutVersionManager`, `OmSnapshotLocalData`, `RDBStore`, live SST metadata via `getLiveSSTFilesForCFs`, Guava graph, hierarchical OM locks, and a scheduler. Snapshot defrag, snapshot purge, diff delta computation, and checkpoint transfer code all rely on these YAML and graph semantics.

Risks: this class has complex lock ordering and graph mutation invariants. Resolution assumes all versions for an iterated snapshot point to a single previous snapshot ID; if not, it treats state as corrupt. YAML path validation is strict and will fail startup on mismatched paths. Atomic move depends on filesystem support. `checkOrphanSnapshotVersions()` takes a read lock while calling `removeVersion()` on the local data object, relying on the provider's write lock and later commit for mutation safety; maintainers should be cautious when changing lock scopes. A typo in `checkForOphanVersionsAndIncrementCount` is harmless but makes searching harder.

Test signals: `TestOmSnapshotManager`, snapshot defrag tests, reclaimable filter tests, delta diff tests, snapshot purge request/response tests, and `TestOMSnapshotDAG` exercise local data creation, version graph behavior, defrag state, purge cleanup, and DAG-derived snapshot semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/OmSnapshotLocalDataManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/OmSnapshotUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/OmSnapshotUtils.java

Purpose: `OmSnapshotUtils` contains filesystem utilities used by OM snapshot checkpoint and hardlink handling.

Important APIs and types: `truncateFileName(int, Path)` removes a leading path prefix. `getFileInodeAndLastModifiedTimeString(Path)` returns an inode/file-key plus modification-time identity string. `createHardLinkList(int, Map<Path, Path>)` writes a temporary text file describing hardlinks for tarball transfer. `linkFiles(File oldDir, File newDir)` recreates a directory tree using hardlinks for files.

Control flow: `createHardLinkList()` iterates link-target mappings, truncates both paths, strips active DB checkpoint paths down to filenames when the source begins with `OM_CHECKPOINT_DIR`, joins target and source with `HARDLINK_SEPARATOR`, and writes the accumulated UTF-8 content to a temp `data*.txt` file. `linkFiles()` walks the old directory, sorts relative paths so parents precede children, creates directories as needed, and uses `Files.createLink()` for files.

State and persistence behavior: methods create temporary link-list files, directories, and hardlinks. They do not modify OM DB metadata. Hardlink identity is filesystem-level state and may fail on filesystems that do not support hardlinks.

Dependencies and integration points: it uses `IOUtils.getINode`, Ozone constants for hardlink separators and checkpoint directory names, and Java NIO file APIs. It supports checkpoint servlet/tarball code and snapshot SST de-duplication workflows.

Risks: `truncateFileName()` assumes `truncateLength` is valid for every path. `linkFiles()` fails if destination entries already exist or if parent directories cannot be created. Hardlinks across filesystems are not supported. The hardlink list format is simple string serialization and depends on paths not containing the separator semantics unexpectedly.

Test signals: checkpoint servlet inode-based transfer tests and snapshot utility tests should cover hardlink list generation, active DB path stripping, and hardlink tree reproduction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/OmSnapshotUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/PersistentList.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/PersistentList.java

Purpose: `PersistentList<E>` defines the minimal list abstraction used by snapshot diff and metadata components that want storage-backed list semantics.

Important APIs and types: `add(E)`, `addAll(PersistentList<E>)`, `get(int)`, and `iterator()` returning `ClosableIterator<E>`.

Control flow and state: the interface has no state. Implementations decide how indexes are assigned, how entries persist, and how iterators are closed. The primary implementation in this subset is `RocksDbPersistentList`.

Dependencies and integration points: it depends on Ozone's `ClosableIterator` and is implemented over RocksDB column families for snapshot data structures.

Risks: the contract does not expose size, remove, clear, or transactional semantics. Callers must close iterators and should not assume `addAll()` is atomic unless an implementation documents it.

Test signals: `TestRocksDbPersistentList` validates the RocksDB implementation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/PersistentList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/PersistentMap.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/PersistentMap.java

Purpose: `PersistentMap<K,V>` defines a simple storage-backed map abstraction for snapshot-related metadata.

Important APIs and types: core operations are `get(K)`, `put(K,V)`, `remove(K)`, and bounded/unbounded iteration through `ClosableIterator<Map.Entry<K,V>>`. The default `iterator()` delegates to the optional-bound overload with empty bounds.

Control flow and state: the interface is stateless. Implementations define persistence, key ordering, and bound interpretation. `RocksDbPersistentMap` provides ordered RocksDB iteration with optional lower and upper raw key bounds.

Dependencies and integration points: it depends on Java `Map.Entry`, `Optional`, and Ozone `ClosableIterator`. Snapshot diff manager MXBean tests use the RocksDB implementation.

Risks: no atomic batch or compare-and-set operations are exposed. Iteration ordering is implementation-defined by the backing store's key encoding. Callers must close iterators.

Test signals: `TestRocksDbPersistentMap` covers puts, gets, removals, and bounded iteration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/PersistentMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/PersistentSet.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/PersistentSet.java

Purpose: `PersistentSet<E>` defines a minimal storage-backed set abstraction.

Important APIs and types: it exposes `add(E)` and `iterator()` returning `ClosableIterator<E>`.

Control flow and state: the interface contains no implementation. Persistence, uniqueness, and ordering semantics are supplied by implementations. `RocksDbPersistentSet` stores set entries as RocksDB keys with empty values.

Dependencies and integration points: it depends only on Ozone `ClosableIterator` and is used where snapshot code needs persistent unique membership.

Risks: the contract lacks `contains`, `remove`, size, clear, and transaction APIs. Callers must infer membership through iteration or implementation-specific access, and must close iterators.

Test signals: `TestRocksDbPersistentSet` validates the RocksDB-backed implementation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/PersistentSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/ReferenceCounted.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/ReferenceCounted.java

Purpose: `ReferenceCounted<T>` wraps an object and tracks references to it, including per-thread counts, so snapshot cache entries can be closed only after all users release them.

Important APIs and types: `get()` returns the wrapped object. `incrementRefCount()` and `decrementRefCount()` update counts. `getTotalRefCount()` and `getCurrentThreadRefCount()` expose counters. The constructor accepts `disableCounter`, in which case counter methods return `-1`, and a `ReferenceCountedCallback` parent.

Control flow: normal mode initializes a `ConcurrentHashMap` from thread ID to count and an `AtomicLong` total. Increment creates a thread entry, synchronizes on `refCountLock`, increments the thread count and total, and checks overflow. Decrement checks that the current thread holds a positive reference, synchronizes, decrements/removes the thread entry, decrements total, checks underflow, and invokes `parentWithCallback.callback(this)` when the total reaches zero.

State and persistence behavior: all state is in-memory. It does not close the wrapped object itself; the callback owner decides what zero references mean.

Dependencies and integration points: it uses Guava `Preconditions` and is used by `SnapshotCache` to wrap `OmSnapshot` DB handles. The callback enqueues entries for eviction after total ref count reaches zero.

Risks: each decrement must happen on the same thread that incremented; releasing from a different thread fails. Callback invocation occurs outside the synchronized block but immediately after total reaches zero. Disabled-counter mode bypasses safety and should only be used where reference accounting overhead is intentionally avoided. The class is package-private, limiting misuse outside snapshot package.

Test signals: `TestSnapshotCache` indirectly exercises reference count behavior through auto-closeable snapshot suppliers, pending eviction, and cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/ReferenceCounted.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/ReferenceCountedCallback.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/ReferenceCountedCallback.java

Purpose: `ReferenceCountedCallback` is the callback contract used by `ReferenceCounted` when a wrapped object's total reference count reaches zero.

Important APIs and types: it exposes one method, `callback(ReferenceCounted referenceCounted)`. The raw `ReferenceCounted` parameter keeps the interface simple but sacrifices generic type precision.

Control flow and state: no implementation or state exists here. `ReferenceCounted.decrementRefCount()` invokes the callback when total count becomes zero.

Dependencies and integration points: `SnapshotCache` implements this interface and uses the callback to add an `OmSnapshot` ID to the pending eviction queue.

Risks: callback implementations must avoid heavy or blocking work if called from latency-sensitive release paths. They must also handle raw type casting carefully.

Test signals: `TestSnapshotCache` indirectly validates callback behavior by asserting cleanup queue and cache-size transitions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/ReferenceCountedCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/RequireSnapshotFeatureState.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/RequireSnapshotFeatureState.java

Purpose: `RequireSnapshotFeatureState` is a runtime method annotation used to require a desired filesystem snapshot feature state before invoking annotated operations.

Important APIs and types: it targets methods, is retained at runtime, and has one boolean element `value()`. Current production use is for `true`, meaning snapshot feature must be enabled.

Control flow and state: the annotation itself has no behavior. `RequireSnapshotFeatureStateAspect` provides the runtime enforcement through AspectJ before advice.

Dependencies and integration points: it integrates with methods on OM request handlers, OM client requests, and test utility classes that need snapshot feature gating.

Risks: annotated methods are protected only when AspectJ weaving/configuration includes the aspect. The aspect's comments note that classes may need to be added to `META-INF/aop.xml` if the annotation does not take effect.

Test signals: `SnapshotFeatureEnabledUtil` and `TestRequireSnapshotFeatureStateAspect` cover enforcement paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/RequireSnapshotFeatureState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/RequireSnapshotFeatureStateAspect.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/RequireSnapshotFeatureStateAspect.java

Purpose: `RequireSnapshotFeatureStateAspect` is an AspectJ aspect that enforces `@RequireSnapshotFeatureState` before annotated methods execute.

Important APIs and types: `checkFeatureState(JoinPoint)` is the before advice. `checkIsAllowed()` performs the policy check. Static `aspectOf()` returns a new aspect instance to avoid occasional `NoSuchMethodError` in tests.

Control flow: advice extracts the desired boolean value from the method annotation. It determines actual snapshot-feature state from one of three target shapes: `OzoneManagerRequestHandler.getOzoneManager()`, `OMClientRequest.preExecute(..)` first argument cast to `OzoneManager`, or a test-style target exposing `isFilesystemSnapshotEnabled()` by reflection. It then calls `checkIsAllowed()`. Desired `true` passes only when OM reports snapshots enabled; otherwise it throws `OMException(FEATURE_NOT_ENABLED)`. Desired `false` is not implemented and throws `NotImplementedException`.

State and persistence behavior: no state is persisted. The aspect only guards method invocation.

Dependencies and integration points: it depends on AspectJ, OM request handler/client request types, `OzoneManager.isFilesystemSnapshotEnabled()`, and `OMException`. It is part of snapshot feature compatibility and rollout gating.

Risks: unsupported join point targets throw `NotImplementedException`, so new annotation sites need aspect handling. The `preExecute` detection uses `joinPoint.toShortString().endsWith(".preExecute(..))")`, which is brittle if AspectJ string formatting changes. Desired `false` is explicitly unsupported. Missing weaving configuration would silently bypass enforcement.

Test signals: `TestRequireSnapshotFeatureStateAspect` and `SnapshotFeatureEnabledUtil` cover enabled/disabled cases and the reflection path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/RequireSnapshotFeatureStateAspect.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/RocksDbPersistentList.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/RocksDbPersistentList.java

Purpose: `RocksDbPersistentList<E>` implements `PersistentList` using a RocksDB column family, assigning integer keys for list indexes and codec-encoded values.

Important APIs and types: the constructor takes `ManagedRocksDB`, `ColumnFamilyHandle`, `CodecRegistry`, and entry class. `add()`, `addAll()`, `get()`, and `iterator()` implement the interface. `currentIndex` is an in-memory append index.

Control flow: `add()` encodes the current index, increments `currentIndex`, encodes the entry, and puts it into RocksDB. `addAll()` iterates another persistent list and adds each entry. `get()` encodes the requested index and decodes the fetched value. `iterator()` creates a managed Rocks iterator, seeks to first, decodes each iterator value, and closes the iterator through `ClosableIterator.close()`.

State and persistence behavior: entries persist in RocksDB, but `currentIndex` starts at zero for each Java object. If an instance is recreated over a non-empty column family, new `add()` calls can overwrite index zero onward unless the caller controls lifecycle or the column family is fresh.

Dependencies and integration points: it depends on RocksDB managed wrappers and `CodecRegistry`. Snapshot diff manager tests use it as a persistent ordered collection.

Risks: exception handling wraps IO/RocksDB failures in `RuntimeException` with TODOs to fail gracefully. There is no size discovery, remove, transaction batching, or recovery of append index. Iterator `next()` names the value bytes `rawKey`, a harmless readability issue.

Test signals: `TestRocksDbPersistentList` should cover add/get/iteration behavior and resource closure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/RocksDbPersistentList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/RocksDbPersistentMap.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/RocksDbPersistentMap.java

Purpose: `RocksDbPersistentMap<K,V>` implements `PersistentMap` on top of a RocksDB column family with `CodecRegistry` serialization.

Important APIs and types: the constructor requires non-null DB, column family, codec registry, key type, and value type. `get()`, `put()`, `remove()`, and `iterator(Optional<K>, Optional<K>)` implement the map contract.

Control flow: `get()` encodes a key, fetches raw bytes, and decodes the value type. `put()` encodes key and value and writes to RocksDB. `remove()` deletes the encoded key. Bounded `iterator()` creates managed lower and upper `Slice` bounds when present, attaches them to `ManagedReadOptions`, creates a Rocks iterator, seeks to first, and returns a `ClosableIterator` that decodes immutable `Map.Entry` objects and closes iterator, read options, and slices.

State and persistence behavior: data persists in RocksDB. Iteration is ordered by RocksDB raw encoded key order and excludes the upper bound through RocksDB iterate-upper-bound semantics. The returned entries do not support `setValue()`.

Dependencies and integration points: it depends on Jakarta `@Nonnull`, RocksDB managed wrappers, `CodecRegistry`, and Ozone `ClosableIterator`. Snapshot diff manager MXBean tests instantiate it for job/report metadata.

Risks: `get()` behavior for missing keys depends on `CodecRegistry.asObject(null, valueType)`, so callers should confirm null handling. All RocksDB/codec failures become unchecked runtime exceptions. Iterators must be closed to release native resources. Bound correctness depends on codec byte ordering matching intended key ordering.

Test signals: `TestRocksDbPersistentMap` covers map operations and bounded iteration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/RocksDbPersistentMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/RocksDbPersistentSet.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/RocksDbPersistentSet.java

Purpose: `RocksDbPersistentSet<E>` implements `PersistentSet` using a RocksDB column family, storing entries as keys with empty byte-array values.

Important APIs and types: the constructor takes `ManagedRocksDB`, `ColumnFamilyHandle`, `CodecRegistry`, and entry class. `add(E)` writes an encoded entry key. `iterator()` returns a closeable RocksDB key iterator.

Control flow: `add()` encodes the entry as the raw key and an encoded empty byte array as the value, then puts it into RocksDB. Duplicate adds overwrite the same key, giving set semantics. The iterator seeks to the first key and decodes each key as an entry.

State and persistence behavior: set membership persists in RocksDB. Ordering is RocksDB raw key order. No remove or contains operation is exposed by the interface.

Dependencies and integration points: it depends on RocksDB managed wrappers, `CodecRegistry`, and `ClosableIterator`. Snapshot diff structures can use it for persistent uniqueness.

Risks: failures are converted to `RuntimeException`; TODO comments indicate graceful handling is not implemented. The empty value is encoded through the codec registry instead of using the raw empty array directly, so the actual stored value depends on byte-array codec behavior. Iterators must be closed.

Test signals: `TestRocksDbPersistentSet` covers add and iteration semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/RocksDbPersistentSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/SnapshotCache.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/SnapshotCache.java

Purpose: `SnapshotCache` is a thread-safe, unbounded custom cache for open `OmSnapshot` DB handles. It reference-counts users, enqueues zero-reference snapshots for eviction, optionally compacts non-snapshot-diff RocksDB tables before close, and exposes write-lock helpers that drain cache entries before destructive operations.

Important APIs and types: the constructor wires a `CacheLoader<UUID, OmSnapshot>`, soft cache size limit, OM metrics, cleanup interval, compaction flag, and OM lock. Public APIs include `get(UUID)`, `invalidate(UUID)`, `invalidateAll()`, `close()`, `release(UUID)`, `lock()`, `lock(UUID)`, and `size()`. It implements `ReferenceCountedCallback`. The `Reason` enum is currently unused.

Get/release flow: `get()` warns through throttled `BatchLogger` if the soft limit is exceeded, acquires a read lock on `SNAPSHOT_DB_LOCK` for the snapshot ID, atomically loads the snapshot through `cacheLoader` if absent, wraps it in `ReferenceCounted`, increments the ref count, updates cache-size metrics, and returns an `UncheckedAutoCloseableSupplier<OmSnapshot>`. The supplier's `close()` decrements the reference count and releases the read lock exactly once. If loading returns `FILE_NOT_FOUND`, `get()` throws an OM file-not-found exception and releases the read lock.

Eviction behavior: when `ReferenceCounted` reaches zero, `callback()` adds the snapshot ID to `pendingEvictionQueue`. Scheduled `cleanup(false)` only acts when cache size exceeds the soft limit; forced cleanup drains pending entries regardless of size. `cleanup(UUID, boolean)` compacts eligible tables when total refs are zero, then atomically removes and closes the snapshot if still unreferenced, decrementing metrics. `invalidate()` closes and removes an entry immediately, independent of ref count, so it should only be used when external locking guarantees no active users.

Locking helpers: `lock()` acquires a resource write lock for all snapshot DBs, forces cleanup, and requires the entire cache to be empty. `lock(UUID)` acquires a write lock for one snapshot ID, forces cleanup of that snapshot, and requires it to be absent. Both return auto-closeable suppliers that release the write lock once.

State and persistence behavior: cache maps and pending queues are in-memory only. Persistent effects are closing RocksDB handles and optional table compaction on snapshot DBs. Metrics track current cache size. The scheduler is optional based on cleanup interval.

Dependencies and integration points: it depends on `CacheLoader`, `ReferenceCounted`, OM lock resources, `OmSnapshot`, `OMMetrics`, `Scheduler`, RocksDB table listing/compaction, and `COLUMN_FAMILIES_TO_TRACK_IN_DAG` to avoid compacting snapshot-diff DAG tables. `OmSnapshotManager` owns the cache, while snapshot reads, diff reads, GC, and checkpoint operations use it to coordinate snapshot DB access.

Risks: the cache is described as LRU but does not track recency; it evicts zero-ref entries from a concurrent set when over limit or forced. `invalidate()` can close a referenced snapshot if misused. `release(UUID)` decrements ref count without releasing the read lock acquired by `get()`, so the auto-closeable supplier path is safer and likely preferred. Compaction before close can add latency to cleanup. `success` of write-lock helpers depends on all readers closing suppliers promptly.

Test signals: `TestSnapshotCache` is extensive and covers metrics, loading, reference counting, eviction, scheduler cleanup, lock draining, error paths, and cache limit warnings. Snapshot diff manager and checkpoint servlet integration tests exercise cache use in larger workflows.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/SnapshotCache.java -->
