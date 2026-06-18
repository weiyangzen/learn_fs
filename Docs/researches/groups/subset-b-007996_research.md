# Research: subset-b-007996

This grouped report covers the requested Apache Ozone datanode volume and disk balancer source files. Each section is bounded with the exact source-path markers required by the research reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/CapacityVolumeChoosingPolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/CapacityVolumeChoosingPolicy.java

Purpose: Implements the default `VolumeChoosingPolicy` for new container placement on datanode HDDS volumes. It uses a "power of two random choices" strategy: filter volumes that can fit `maxContainerSize`, sample two candidates, then choose the one with more effective available space.

Important APIs and types: `chooseVolume(List<HddsVolume>, long)` is the public policy method. The constructor accepts a shared `ReentrantLock`; the visible-for-testing constructor creates a private lock. It depends on `AvailableSpaceFilter`, `HddsVolume.getCurrentUsage()`, `HddsVolume.getCommittedBytes()`, `HddsVolume.incCommittedBytes()`, and `VolumeChoosingUtil` helpers.

Control flow: empty input throws `DiskOutOfSpaceException`. The method filters volumes under the lock, throws with the best observed available-space detail if no volume can satisfy the request, logs partial out-of-space conditions, and either picks the sole surviving volume or samples two indexes from the filtered list. After choosing, it reserves the requested bytes by incrementing committed bytes before returning.

State and persistence: The class itself persists no state, but it mutates per-volume in-memory reservation state through `committedBytes`. That reservation is meant to protect later writes from overcommitting capacity while open containers are being created or filled.

Dependencies and integration points: Created by `VolumeChoosingPolicyFactory`, used by datanode container allocation paths through `VolumeChoosingPolicy`. It shares the same reservation lock with disk balancer container selection so normal allocation and balancing do not race destination reservations.

Risks: The random policy favors low utilization probabilistically, not deterministically. Correctness depends on callers decrementing committed bytes elsewhere when a reservation is consumed or abandoned. Tests should cover empty volume sets, all-full volume sets, single eligible volume, two-volume bias, and concurrent selection under the shared lock.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/CapacityVolumeChoosingPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/DbVolume.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/DbVolume.java

Purpose: Represents a datanode volume dedicated to per-HDDS-volume container database storage. Its on-disk layout is rooted under a `db` storage directory, with per-cluster and per-HDDS-storage-ID subdirectories containing `container.db`.

Important APIs and types: Extends `StorageVolume`; exposes `DB_VOLUME_DIR`, `addHddsDbStorePath`, and `getHddsVolumeIDs`. The nested `Builder` fixes the storage subdirectory name to `db`.

Control flow: Construction delegates base volume initialization, initializes an empty `hddsDbStorePathMap`, and scans existing database store paths when the volume is not a failed placeholder. `initializeImpl` extends normal `StorageVolume` initialization, then calls `scanForDbStorePaths`. Failure and shutdown both close cached DB handles.

State and persistence: Persistent state is the inherited VERSION file and the directory tree under `<db volume>/db/<clusterID>/<hddsStorageID>/container.db`. Runtime state is a map from HDDS volume storage IDs to DB store paths. `scanForDbStorePaths` rebuilds that map from disk when the volume is normal and the cluster directory exists.

Dependencies and integration points: Uses `DatanodeStoreCache.removeDB` to close RocksDB instances. `HddsVolume.createDbStore` registers newly created DB paths with the chosen `DbVolume`.

Risks: The map is a plain `HashMap`, so external concurrent mutations would need higher-level synchronization. `scanForDbStorePaths` trusts every child directory under the cluster directory to represent an HDDS volume storage ID. Tests should cover unformatted volumes, missing cluster dirs, listFiles failure, fail/shutdown closing all mapped DBs, and restart scanning of existing DB stores.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/DbVolume.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/DbVolumeFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/DbVolumeFactory.java

Purpose: Factory for constructing `DbVolume` instances from configured datanode DB directories.

Important APIs and types: Extends `StorageVolumeFactory`. Implements `createVolume(String, StorageType)` and `createFailedVolume(String)`.

Control flow: Normal creation wires configuration, datanode UUID, cluster ID, usage check factory, storage type, and containing volume set into a `DbVolume.Builder`, builds the volume, then validates or learns the cluster ID through `checkAndSetClusterID`. Failed-volume creation builds a minimal failed placeholder without normal initialization.

State and persistence: The factory itself has no persistence. The built `DbVolume` manages VERSION files and discovered DB paths.

Dependencies and integration points: Instantiated by `MutableVolumeSet` when the requested `StorageVolume.VolumeType` is `DB_VOLUME`. Relies on `StorageVolumeFactory` for cluster-ID consistency checks across all volumes in the set.

Risks: A mismatched cluster ID in any VERSION file raises `InconsistentStorageStateException` and turns that configured location into a failed volume through the `MutableVolumeSet` initialization path. Tests should verify cluster-ID inheritance, mismatch rejection, storage type propagation, and failed placeholder creation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/DbVolumeFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/HddsVolume.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/HddsVolume.java

Purpose: Main datanode data-volume implementation for Ozone containers. It extends `StorageVolume` with container tracking, per-volume metrics, committed-space reservation, schema V3 RocksDB management, deleted-container cleanup, and volume-specific health checks.

Important APIs and types: Exposes `HDDS_VOLUME_DIR`, `TMP_CONTAINER_DELETE_DIR_NAME`, `VolumeIOStats`, `VolumeInfoMetrics`, container ID set operations, `incCommittedBytes`, `getCommittedBytes`, `loadDbStore`, `createDbStore`, `compactDb`, `checkDbHealth`, and helpers for container and DB directories. The nested builder fixes storage subdirectory `hdds`.

Control flow: Construction initializes metrics and then calls base initialization unless building a failed placeholder. `createWorkingDir` creates normal working directories and creates per-disk DB stores when schema V3 is finalized. `createTmpDirs` prepares the inherited tmp and disk-check directories plus the `deleted-containers` staging directory. `check` increments scan metrics, updates space/risk gauges, runs base directory/IO checks, and for schema V3 validates that the DB exists and can be opened read-only when RocksDB disk checking is enabled.

State and persistence: Persistent state includes inherited VERSION metadata, `<hdds>/<cluster>/current` container directories, temporary deleted-container directories, and optional per-volume `container.db` under either the HDDS volume or a selected `DbVolume`. Runtime state includes committed bytes, container IDs, DB loaded/failure booleans, DB parent directory, optional `DbVolume`, and metrics registrations.

Dependencies and integration points: `MutableVolumeSet` owns instances. Volume choosing policies mutate committed bytes. `DiskBalancerService` reads usage, increments/decrements space, and uses tmp directories. Schema V3 DB operations go through `HddsVolumeUtil`, `DatanodeStoreCache`, and `RawDB`. Container counts can be delegated to `ContainerController`.

Risks: DB lifecycle is sensitive to schema-finalization state, chosen DB volume, and whether `dbParentDir` has been initialized. `compactDb` assumes a non-null DB parent. Deleted-container cleanup is best-effort and logs failures without failing startup. Tests should cover schema V3 enabled/disabled behavior, DB load failure health checks, committed-byte accounting, SCM-HA container path fallback, cleanup of deleted-container tmp dirs, and shutdown unregistering metrics and closing DBs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/HddsVolume.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/HddsVolumeFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/HddsVolumeFactory.java

Purpose: Factory for constructing normal and failed `HddsVolume` objects for data storage directories.

Important APIs and types: Extends `StorageVolumeFactory`; implements `createVolume` and `createFailedVolume`.

Control flow: Normal creation configures an `HddsVolume.Builder` with config, datanode UUID, cluster ID, usage factory, storage type, and parent set, then builds and validates cluster ID. Failed creation builds a failed placeholder from the raw location string.

State and persistence: No factory-local state beyond inherited constructor fields. Built volumes own VERSION, usage, DB, tmp, and metrics state.

Dependencies and integration points: Selected by `MutableVolumeSet` for `DATA_VOLUME`. It is the main bridge from configured storage locations to usable `HddsVolume` instances.

Risks: Failed placeholder construction uses the raw location string as storage directory, while normal construction parses `StorageLocation` before factory invocation. Tests should verify proper storage type propagation, failed-volume state, and cluster-ID consistency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/HddsVolumeFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/ImmutableVolumeSet.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/ImmutableVolumeSet.java

Purpose: Simple immutable `VolumeSet` implementation for fixed collections of volumes, mainly useful when callers need the `VolumeSet` interface without mutable maps or locks.

Important APIs and types: Constructors accept varargs or collections of `StorageVolume`. `getVolumesList` returns the immutable list. `checkAllVolumes` delegates to `StorageVolumeChecker`. Lock methods are no-ops.

Control flow: Disk checks are synchronous through `StorageVolumeChecker.checkAllVolumes`; interruption is converted to `IOException` while preserving interrupt status.

State and persistence: Holds only an immutable in-memory list. It does not manage failed-volume maps or metrics.

Dependencies and integration points: Implements `VolumeSet` and can be used with `StorageVolumeChecker` wherever a stable volume collection is enough.

Risks: No lock enforcement means callers must not expect mutation coordination. It also does not remove failed volumes after checks; it only delegates and lets exceptions propagate. Tests should cover immutable copy behavior and interrupted check handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/ImmutableVolumeSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/MetadataVolume.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/MetadataVolume.java

Purpose: Represents a datanode metadata/Ratis volume. Ozone tracks health and usage for it but does not format it like HDDS data volumes.

Important APIs and types: Extends `StorageVolume`; returns `VolumeType.META_VOLUME`; overrides `format`, `createTmpDirs`, and `getStorageID`. The builder uses an empty storage subdirectory, meaning the configured root is the storage directory.

Control flow: Constructor delegates base initialization and immediately creates tmp/disk-check directories at the volume root. Formatting and later tmp-dir creation are no-ops because metadata volumes are independent of SCM cluster IDs.

State and persistence: It still uses `StorageVolume` usage/check state, but it does not expose a storage ID and should not rely on HDDS VERSION formatting semantics in normal operation.

Dependencies and integration points: Built by `MetadataVolumeFactory` and managed by `MutableVolumeSet` when `META_VOLUME` is selected. Used for Ratis/metadata directory health, not container placement.

Risks: `getStorageID` returning an empty string is intentional but can surprise generic reporting or map-key logic. Tests should verify metadata volumes do not format on cluster registration and that tmp dirs are available immediately.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/MetadataVolume.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/MetadataVolumeFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/MetadataVolumeFactory.java

Purpose: Factory for metadata/Ratis volumes.

Important APIs and types: Extends `StorageVolumeFactory`; normal creation wires configuration, usage factory, storage type, and volume set into `MetadataVolume.Builder`; failed creation marks the builder as failed.

Control flow: Unlike data and DB factories, it passes null datanode UUID and cluster ID into the superclass because metadata volumes are not formatted with datanode VERSION fields by Ozone.

State and persistence: No factory persistence. Built `MetadataVolume` handles usage and health-check state.

Dependencies and integration points: Selected by `MutableVolumeSet` for `META_VOLUME` and fed configured Ratis directories from `HddsServerUtil.getOzoneDatanodeRatisDirectory`.

Risks: This factory does not call `checkAndSetClusterID`, intentionally avoiding data-volume cluster validation. Tests should ensure metadata creation does not require cluster ID or datanode UUID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/MetadataVolumeFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/MutableVolumeSet.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/MutableVolumeSet.java

Purpose: Owns a datanode's active and failed volumes for one `StorageVolume.VolumeType`. It initializes configured locations, runs health checks, moves failed volumes out of service, reports volume state, and exposes lifecycle operations.

Important APIs and types: Implements `VolumeSet`. Key methods include `checkAllVolumes`, `checkVolumeAsync`, `failVolume`, `startAllVolume`, `refreshAllVolumeUsage`, `setGatherContainerUsages`, `hasEnoughVolumes`, `getStorageReport`, and lock methods. It maintains `volumeMap`, `failedVolumeMap`, `ReentrantReadWriteLock`, `StorageVolumeChecker`, selected `StorageVolumeFactory`, and `VolumeHealthMetrics`.

Control flow: Construction registers with a checker, selects a volume factory and tolerated-failure count based on volume type, creates metrics, then initializes configured directories. Initialization parses storage locations, creates volumes, ensures directories and data permissions, records successes, and converts failures to failed-volume placeholders. Health checks snapshot active volumes, ask `StorageVolumeChecker`, and call `handleVolumeFailures` for failed results. Failure handling acquires the write lock, marks volumes failed, updates maps and metrics, checks fatal tolerance, and runs an optional listener.

State and persistence: Active and failed volume maps are runtime state. Persistent effects are delegated to volume constructors and directory permission fixes. Metrics are registered per volume type and unregistered on initialization failure or shutdown.

Dependencies and integration points: Used by `OzoneContainer`, `DiskBalancerService`, volume factories, and background health scanning. Configuration sources for locations differ for data, metadata, and DB volumes. Fatal failure escalation goes through `StateContext.getParent().handleFatalVolumeFailures()`.

Risks: `failVolume` itself takes the write lock, and callers such as `handleVolumeFailures` already hold it; this works because the lock is reentrant, but it is important to preserve. Initialization throws if no active volumes exist. Tests should cover partial location failures, tolerated failure thresholds, async callback failure handling, metrics increments/decrements, and fatal-volume callback invocation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/MutableVolumeSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/RoundRobinVolumeChoosingPolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/RoundRobinVolumeChoosingPolicy.java

Purpose: Alternative `VolumeChoosingPolicy` that scans HDDS volumes in round-robin order and returns the first volume with enough usable space for the requested container size.

Important APIs and types: `chooseVolume(List<HddsVolume>, long)` is the policy entry point. It uses `AvailableSpaceFilter`, the shared `ReentrantLock`, `nextVolumeIndex`, and `VolumeChoosingUtil`.

Control flow: Empty input throws `DiskOutOfSpaceException`. The current index is normalized in case the volume list shrank after a failure. Under the lock, the method tests each volume, advances circularly, reserves committed bytes on success, and throws a detailed out-of-space exception after a full loop with no eligible volume.

State and persistence: The only class-local state is `nextVolumeIndex`, which controls future selection fairness. It mutates volume committed bytes but has no durable state.

Dependencies and integration points: Can be configured through `VolumeChoosingPolicyFactory`. Requires callers to pass a volume list that remains consistent for the duration of selection.

Risks: `currentVolumeIndex` is computed before acquiring the policy lock, so list size changes by other mechanisms must still be controlled by caller-side volume-set locking. Tests should cover index wraparound, list shrinkage, out-of-space logging/throwing, and reservation increments.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/RoundRobinVolumeChoosingPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/StorageVolume.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/StorageVolume.java

Purpose: Abstract base class for datanode storage volumes. It centralizes VERSION-file lifecycle, volume state, storage directory paths, usage accounting, temporary directories, storage reports, and health checks.

Important APIs and types: Defines `VolumeType` and `VolumeState`. Core methods include `initialize`, `initializeImpl`, `format`, `createWorkingDir`, `createTmpDirs`, `getCurrentUsage`, `getReport`, `incrementUsedSpace`, `decrementUsedSpace`, `failVolume`, `shutdown`, `check`, `recordTimeoutAndCheckFailure`, and the generic nested `Builder`.

Control flow: Construction parses the configured storage location, creates the root if needed, configures `VolumeUsage`, initializes disk-check sliding windows, and sets initial state. `initializeImpl` analyzes the storage directory and either creates it, creates a VERSION file, reads an existing VERSION file, or fails on inconsistency. `check` verifies existence/permissions, optionally performs read/write disk checks, handles low-space bypasses, and marks failure only when the IO sliding window exceeds tolerance.

State and persistence: Persistent state is the VERSION file with storage ID, cluster ID, datanode UUID, creation time, and layout version. Runtime state includes `VolumeUsage`, current state, working/tmp/disk-check dirs, config, storage type, and sliding windows for IO and timeout failures.

Dependencies and integration points: Subclasses specialize data, metadata, and DB behavior. `StorageVolumeChecker` invokes `check` and `recordTimeoutAndCheckFailure`. `StorageLocationReport` is used for SCM heartbeats and reports. Permission setup uses `ServerUtils` and SCM config keys for data dirs.

Risks: VERSION state transitions are strict; a non-empty directory without VERSION is inconsistent. `shutdown` sets state to `NON_EXISTENT`, which is a lifecycle marker rather than a fresh disk analysis. Tests should cover all `analyzeVolumeState` branches, cluster/datanode/version validation, disk-check low-space behavior, timeout tolerance, and permission setting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/StorageVolume.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/StorageVolumeChecker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/StorageVolumeChecker.java

Purpose: Coordinates synchronous, asynchronous, and periodic disk health checks for datanode storage volumes. It detects failed volumes but leaves failure handling to the owning `VolumeSet`.

Important APIs and types: Uses `AsyncChecker<Boolean, VolumeCheckResult>` implemented by `ThrottledAsyncChecker`. Public APIs include `start`, `registerVolumeSet`, `checkAllVolumeSets`, `checkAllVolumes(Collection)`, `checkVolume(StorageVolume, Callback)`, `shutdownAndWait`, and testing accessors. The nested `ResultHandler` interprets future results.

Control flow: `start` schedules periodic scans. `checkAllVolumeSets` respects the minimum all-volume scan gap, updates background scanner metrics, and delegates to each registered volume set. `checkAllVolumes` schedules eligible checks, waits up to the configured timeout, snapshots completed healthy/failed sets under a result lock, and records timeout tolerance for pending volumes. `checkVolume` schedules one volume and calls a callback when complete.

State and persistence: Runtime state includes last full-scan timestamp, registered volume sets, executors, metrics, and the throttling delegate. No durable state is written.

Dependencies and integration points: `MutableVolumeSet` registers itself and calls checker methods. `StorageVolume.check` supplies actual health logic. Guava futures and callbacks manage asynchronous execution.

Risks: Correct timeout handling depends on distinguishing batch checks, where pending-volume timeout accounting happens in `checkAllVolumes`, from single-volume checks, where the callback records timeout failure. The `onFailure` interruption test checks `t instanceof InterruptedException`, while wrapped causes may differ. Tests should cover skipped recent checks, batch timeout tolerance, explicit failed results, single-volume callbacks, periodic metrics, and shutdown cancellation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/StorageVolumeChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/StorageVolumeFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/StorageVolumeFactory.java

Purpose: Abstract base factory for data, metadata, and DB volume factories. It holds construction dependencies and enforces cluster-ID consistency for volumes with VERSION files.

Important APIs and types: Provides getters for `ConfigurationSource`, `SpaceUsageCheckFactory`, `VolumeSet`, datanode UUID, and cluster ID. Defines abstract `createVolume` and `createFailedVolume`. `checkAndSetClusterID` validates discovered cluster IDs.

Control flow: When the first created volume reports a cluster ID and the factory does not already have one, the factory adopts it. Later volumes must match or an `InconsistentStorageStateException` is thrown.

State and persistence: Factory-local state is in-memory only; persistent VERSION creation and reading belong to `StorageVolume`.

Dependencies and integration points: Concrete factories are selected by `MutableVolumeSet`. Cluster-ID validation prevents mixing directories from different Ozone clusters within the same data/DB volume set.

Risks: The cluster ID field mutates based on the first volume, so creation order can determine the adopted ID when no cluster ID was provided. Tests should cover null initial cluster ID, matching IDs, mismatched IDs, and failed-volume creation bypass behavior in concrete factories.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/StorageVolumeFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/ThrottledAsyncChecker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/ThrottledAsyncChecker.java

Purpose: Generic asynchronous checker that throttles repeated checks of the same `Checkable` and optionally wraps checks with a timeout.

Important APIs and types: Implements `AsyncChecker<K,V>`. Main methods are `schedule(Checkable<K,V>, K)` and `shutdownAndWait`. Internal maps track in-progress checks and last completed checks; `LastCheckResult` stores completion time and result/exception marker.

Control flow: `schedule` returns empty if the target already has an in-progress check or completed too recently. Otherwise it submits `target.check(context)`, wraps with `Futures.withTimeout` when configured, records the future in `checksInProgress`, and attaches a direct callback to move the target into `completedChecks` on success or failure.

State and persistence: Runtime-only state includes throttling timestamps in a `WeakHashMap` and active futures in a `HashMap`, protected by synchronization. No durable state.

Dependencies and integration points: Used by `StorageVolumeChecker` for volume checks. It relies on Hadoop `Timer`, Guava `ListeningExecutorService`, timeout futures, and a scheduled executor for timeout enforcement.

Risks: The cache uses `Checkable` object identity/equality, so equality changes would break throttling. Timed-out underlying tasks may continue until interrupted by the executor depending on future behavior. Tests should cover duplicate in-progress scheduling, minimum-gap skipping after failures and successes, timeout propagation, weak completed-cache behavior, and shutdown interrupting active work.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/ThrottledAsyncChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeChoosingPolicyFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeChoosingPolicyFactory.java

Purpose: Creates configured `VolumeChoosingPolicy` instances and owns the shared lock used for committed-space reservation.

Important APIs and types: `getPolicy(ConfigurationSource)` reads `HDDS_DATANODE_VOLUME_CHOOSING_POLICY`, defaults to `CapacityVolumeChoosingPolicy`, and instantiates the policy reflectively with a `ReentrantLock`. `getVolumeSpaceReservationLock` exposes the same lock.

Control flow: Reflection constructs policies that accept a `ReentrantLock` constructor parameter. The static lock is process-wide for this factory.

State and persistence: The only state is static in-memory `LOCK`.

Dependencies and integration points: Used for normal container volume placement and by disk balancer's `ContainerChoosingPolicyFactory`, so balancing reservations and container-creation reservations share one synchronization mechanism.

Risks: Custom policies must provide the expected constructor signature. The static lock serializes reservation operations across all policy instances, which is simple but can reduce concurrency. Tests should cover default selection, configured class selection, constructor failure behavior, and lock identity sharing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeChoosingPolicyFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeChoosingUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeChoosingUtil.java

Purpose: Package-private helper methods shared by volume choosing policies.

Important APIs and types: `throwDiskOutOfSpace(AvailableSpaceFilter, Logger)` builds and logs a detailed `DiskOutOfSpaceException`; `logIfSomeVolumesOutOfSpace` emits debug diagnostics when the filter saw at least one full volume.

Control flow: The throw helper includes `filter.mostAvailableSpace()` in the message and logs both message and filter detail before throwing. The logging helper is gated by debug level and `foundFullVolumes`.

State and persistence: Stateless utility class.

Dependencies and integration points: Used by `CapacityVolumeChoosingPolicy` and `RoundRobinVolumeChoosingPolicy` after applying `AvailableSpaceFilter`.

Risks: The utility's usefulness depends on `AvailableSpaceFilter` accurately tracking candidate and rejected volumes during predicate calls. Tests should verify exception contents and debug logging conditions around mixed eligible/ineligible volume sets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeChoosingUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeHealthMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeHealthMetrics.java

Purpose: Metrics source tracking total, healthy, and failed volume counts per volume type on a datanode.

Important APIs and types: Static `create(StorageVolume.VolumeType)` registers a metrics source named with the volume type. Methods increment/decrement healthy and failed counters, `unregister` removes the source, and `getMetrics` emits gauges.

Control flow: `MutableVolumeSet` creates one instance per set, increments healthy/failed counts during initialization, adjusts counts during failure transitions, and unregisters on shutdown.

State and persistence: Runtime metrics state only, stored in `AtomicInteger` counters. No durable state.

Dependencies and integration points: Uses Hadoop Metrics2 `DefaultMetricsSystem`, `MetricsRegistry`, `Interns`, and `MetricsSource`.

Risks: Counter decrement methods do not guard against negative values, so callers must maintain balanced transitions. Tests should cover registration naming, gauge values after transitions, unregister behavior, and failure during volume-set initialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeHealthMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeIOStats.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeIOStats.java

Purpose: Per-HDDS-volume metrics source for read/write bytes, operation counts, latencies, and latency quantiles.

Important APIs and types: Constructor names the metrics source by identifier and optionally creates quantiles from configured intervals. Increment methods update bytes, op counts, and read/write timings; `recordReadOperation` combines elapsed time, op count, and bytes. Getter methods expose counter/rate values and `getStorageDirectory` is annotated as a metric.

Control flow: Construction sets quantile arrays when intervals are configured and registers with the default metrics system. `HddsVolume` creates and unregisters it for normal data volumes.

State and persistence: Runtime metrics only. No on-disk persistence.

Dependencies and integration points: Uses Metrics2 mutable counters, rates, and quantiles. `HddsVolume.getVolumeIOStats` exposes it to container IO code.

Risks: If no percentile intervals are configured, `readLatencyQuantiles` and `writeLatencyQuantiles` may remain null, but `incReadTime` and `incWriteTime` iterate them unconditionally. Tests should cover empty/null interval behavior, registration/unregistration, and counter updates through both direct increments and convenience methods.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeIOStats.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeInfoMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeInfoMetrics.java

Purpose: Per-HDDS-volume metrics source for capacity, availability, used space, reserved space, min-free thresholds, container count, scan counts, soft/hard min-free request counters, and RocksDB compaction latency.

Important APIs and types: Constructor registers a metrics source per identifier. Annotated getters expose storage type, storage directory, datanode UUID, layout version, volume state/type, committed bytes, and container count. Mutators update scan counters, min-free-space request counters, reserved-limit and insufficient-space gauges, and DB compaction rate.

Control flow: `getMetrics` snapshots the volume's `VolumeUsage`, computes real filesystem usage and Ozone-adjusted usage, then emits gauges for Ozone capacity/available/used, reserved, filesystem capacity/available/used, min-free space, and non-Ozone used.

State and persistence: Runtime metrics only. Values derive live from `HddsVolume` and `VolumeUsage`.

Dependencies and integration points: Created by `HddsVolume`; `HddsVolume.checkVolumeUsages` updates gauges; `HddsVolume.compactDb` records compaction latency. Used by reporting/monitoring systems through Metrics2.

Risks: The metrics source holds a strong reference to its volume until unregistered. `getMetrics` skips capacity gauges if `VolumeUsage` is null, which can happen for failed placeholders. Tests should cover gauge derivation with reserved space, scan skipped counters, soft/hard min-free counters, and unregister on failure/shutdown.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeInfoMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeSet.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeSet.java

Purpose: Minimal interface for a collection of `StorageVolume` objects with read/write locking and health-check delegation.

Important APIs and types: Extends `ReadWriteLockable`; declares `getVolumesList` and `checkAllVolumes(StorageVolumeChecker)`.

Control flow: Implementations decide whether locks are active (`MutableVolumeSet`) or no-op (`ImmutableVolumeSet`) and how failed checks are handled.

State and persistence: Interface only; no state.

Dependencies and integration points: Used by `StorageVolume`, `StorageVolumeChecker`, `MutableVolumeSet`, `ImmutableVolumeSet`, and code that wants a common abstraction over active volume collections.

Risks: The interface does not specify whether returned lists are mutable, snapshots, or live views; callers must rely on implementation behavior. Tests should target concrete implementations and call sites that assume snapshot semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeUsage.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeUsage.java

Purpose: Wraps cached filesystem/DU usage for a volume and converts raw filesystem capacity/available/used into Ozone usable capacity and available space after reserved-space accounting.

Important APIs and types: Holds `CachingSpaceUsageSource` and `reservedInBytes`. Key methods include `realUsage`, `getCurrentUsage`, `incrementUsedSpace`, `decrementUsedSpace`, `start`, `shutdown`, `refreshNow`, `getReservedInBytes`, `getUsableSpace`, and static `getOtherUsed`.

Control flow: Construction creates the caching source and computes reserved bytes from either per-directory reserved size config or reserved percent. `getCurrentUsage` returns raw usage when no reservation exists; otherwise it subtracts total reserved from capacity and subtracts only remaining reservation from available space, accounting for non-Ozone usage already consuming reserved space.

State and persistence: Runtime cached usage state only. It reads configuration but writes no files. `shutdownComplete` prevents double shutdown of the source.

Dependencies and integration points: Built by `StorageVolume` from `SpaceUsageCheckParams`. Used by reports, volume choosing, disk balancer calculations, and metrics.

Risks: Directory-specific reserved config compares canonical configured path to the root path string from check params; mismatches can silently fall back to percent reservation. Invalid percent logs and uses default. Tests should cover reserved-byte precedence, malformed reserved entries, percent bounds, other-used math, usable-space helpers, and start/shutdown idempotency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeUsage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/package-info.java

Purpose: Package-level documentation for the datanode volume/disk classes.

Important APIs and types: Declares package `org.apache.hadoop.ozone.container.common.volume` and states that the package contains volume/disk related classes.

Control flow: No executable control flow.

State and persistence: None.

Dependencies and integration points: Provides Java package documentation for the volume subsystem that includes storage volume implementations, volume sets, choosing policies, health checks, usage accounting, and metrics.

Risks: The comment is broad and minimal; richer package docs could help orient future changes around lifecycle, locking, and committed-space accounting. Test signals are not applicable beyond documentation generation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/ContainerChoosingPolicyFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/ContainerChoosingPolicyFactory.java

Purpose: Creates configured disk balancer `ContainerChoosingPolicy` instances.

Important APIs and types: `getDiskBalancerPolicy(ConfigurationSource)` reads `hdds.datanode.disk.balancer.container.choosing.policy`, defaults to `DefaultContainerChoosingPolicy`, and reflectively constructs the policy with a `ReentrantLock`.

Control flow: The factory passes `VolumeChoosingPolicyFactory.getVolumeSpaceReservationLock()` into the policy, sharing reservation synchronization with normal volume selection.

State and persistence: Stateless factory.

Dependencies and integration points: Used by `DiskBalancerService` during construction. Custom policies must implement `ContainerChoosingPolicy` and provide a matching constructor.

Risks: Reflection failures become service initialization failures. Tests should cover default class selection, configured policy class, constructor signature validation, and shared lock identity with normal volume choosing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/ContainerChoosingPolicyFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerConfiguration.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerConfiguration.java

Purpose: Configuration bean and validation layer for datanode disk balancer settings.

Important APIs and types: Annotated with `@ConfigGroup`. Defines config keys for info directory, density threshold, bandwidth, parallel threads, default run state, service interval/timeout, container choosing policy, stop-after-even behavior, replica deletion delay, and movable container states. Provides setters with validation, `getMovableContainerStates`, `toProtobufBuilder`, and `updateFromProtobuf`.

Control flow: Numeric setters reject threshold outside `(0,100)`, non-positive bandwidth, and non-positive parallelism. Container-state parsing requires non-empty uppercase enum names, rejects open-to-write, CLOSING, and DELETED states, and returns an unmodifiable set. Proto updates only apply fields present in the proto.

State and persistence: In-memory configuration object; persistence happens when `DiskBalancerInfo` is written to YAML or sent over protobuf.

Dependencies and integration points: Loaded from `ConfigurationSource` by `DiskBalancerService`; mutated through `DiskBalancerProtocolServer` RPCs; converted to/from `HddsProtos.DiskBalancerConfigurationProto`.

Risks: Direct config injection may set raw `containerStates` without setter validation, but reads through `getMovableContainerStates` still validate. `toString` formatting lists fewer key/value rows than the formatted header suggests. Tests should cover invalid state casing, non-movable states, proto partial updates, threshold bounds, and default state set.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerInfo.java

Purpose: Mutable data transfer and persistence model for disk balancer status and configuration. It separates persisted configuration/state from report-only live fields.

Important APIs and types: Holds `DiskBalancerRunningStatus`, threshold, bandwidth, parallel thread count, stop-after-even, version, success/failure counts, bytes-to-move, balanced bytes, density, container states, ideal usage, and per-volume report protos. Provides constructors, `updateFromConf`, `toConfiguration`, getters/setters, `equals`, and `hashCode`.

Control flow: The boolean constructor maps `shouldRun` to RUNNING or STOPPED and copies config values. `toConfiguration` reconstructs a validated `DiskBalancerConfiguration`, which is used before persistence/application.

State and persistence: This is the object persisted to `diskBalancer.info` through `DiskBalancerYaml`, but comments indicate `idealUsage` and `volumeInfo` are report-only and not persisted.

Dependencies and integration points: Produced by `DiskBalancerService.getDiskBalancerInfo`, consumed by `DiskBalancerProtocolServer`, and serialized by `DiskBalancerYaml`.

Risks: `equals` excludes counters, bytes, density, ideal usage, and volume info, intentionally treating those as operational/report state rather than configuration identity. Setters do not validate directly; validation occurs through conversion to `DiskBalancerConfiguration`. Tests should cover persisted-vs-report fields, config round trips, version/default constructor behavior, and equality semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerProtocolServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerProtocolServer.java

Purpose: Server-side datanode implementation of `DiskBalancerProtocol` for reading disk balancer status and starting, stopping, or updating service configuration.

Important APIs and types: Implements `getDiskBalancerInfo`, `startDiskBalancer`, `stopDiskBalancer`, `updateDiskBalancerConfiguration`, and `close`. Uses a `PrivilegedOperation` functional interface for admin authorization.

Control flow: Read-only info requires no admin check. Start/update/stop call `adminChecker`. Start checks datanode operational state: IN_SERVICE becomes RUNNING, otherwise PAUSED. Optional config proto is merged into current persisted config using `DiskBalancerConfiguration.updateFromProtobuf`, then `refreshService` applies and persists it through the service.

State and persistence: Does not store state locally. It mutates `DiskBalancerInfo`, and `DiskBalancerService.refresh` persists the resulting state.

Dependencies and integration points: Bridges RPC clients to `DatanodeStateMachine`, `OzoneContainer`, and `DiskBalancerService`. Info responses include datanode details, config, counters, bytes, status, ideal usage, and volume reports.

Risks: If service is disabled, operations throw `IOException`. Start on non-IN_SERVICE nodes persists PAUSED, not STOPPED, which affects later resume behavior. Tests should cover admin enforcement, disabled service errors, node-state-dependent start behavior, partial proto updates, and response field population.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerProtocolServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerService.java

Purpose: Background datanode service that balances container data across HDDS volumes by moving eligible closed/quasi-closed containers from overused volumes to underused volumes.

Important APIs and types: Extends `BackgroundService`. Key methods include constructor initialization, `refresh`, `start`, `getTasks`, nested `DiskBalancerTask.call`, `getDiskBalancerInfo`, `calculateBytesToMove`, `cleanupPendingDeletionContainers`, `nodeStateUpdated`, and testing setters/getters. Important state includes operational status, threshold, bandwidth, parallelism, movable states, in-progress container IDs, delta sizes, pending deletion queues, metrics, and persisted info file path.

Control flow: Startup resolves the info file path, creates the container choosing policy, loads persisted disk balancer info, validates and applies it, and cleans stale tmp dirs before the background service starts. `getTasks` does nothing when STOPPED or PAUSED except cleanup pending deletions, delays work when bandwidth throttling requires it, computes available task lanes, asks the policy for candidates, records in-progress IDs and source delta sizes, and stops/persists itself when no work remains and stop-after-even is enabled. Each task locks the source container, verifies state, copies it to destination tmp, validates container YAML checksum, marks temp state RECOVERING, atomically moves into the destination layout, imports the new container, updates the container set and destination usage, marks the old container for deletion, records bytes/metrics, and schedules delayed deletion.

State and persistence: `diskBalancer.info` YAML stores operational state and configuration. Runtime state includes in-progress containers, source-volume delta adjustments, committed bytes on destination volumes, bandwidth windows, and pending delayed deletions. Successful moves persist container YAML changes and mutate on-disk container directories.

Dependencies and integration points: Uses `OzoneContainer`, `ContainerController`, `ContainerSet`, `MutableVolumeSet`, `HddsVolume`, `DiskBalancerYaml`, `DiskBalancerVolumeCalculation`, `ContainerChoosingPolicy`, container YAML utilities, key-value container utilities, and Metrics2. Node operational state updates pause/resume the service and persist changes.

Risks: Move correctness spans filesystem atomic moves, container-set replacement, source deletion, and committed-byte rollback. Failures after import but before old-container deletion intentionally leave both replicas on disk with the new one active. `postCall` must always roll back destination committed bytes and source delta. Tests should cover copy/import failures, existing destination dirs, state changes after selection, bandwidth throttling, delayed deletion, stop-after-even persistence, node-state pause/resume persistence failure rollback, and startup cleanup of stale tmp dirs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerServiceMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerServiceMetrics.java

Purpose: Singleton Metrics2 source for disk balancer service activity.

Important APIs and types: Static `create` registers the singleton, `unRegister` removes it. Counters track successful jobs, successfully moved bytes, failed jobs, running loops, idle loops with no volume pair, and idle loops due to bandwidth. Mutable rates track successful and failed move durations.

Control flow: `DiskBalancerService` increments counters throughout scheduling and task completion. `toString` reports current counter values and mean move times.

State and persistence: Runtime metrics only; no durable state. Static singleton `instance` is reset on unregister.

Dependencies and integration points: Uses Hadoop Metrics2 default system. `DiskBalancerService.getDiskBalancerInfo` reads success/failure counters and bytes to populate reports.

Risks: `create` is not synchronized, so concurrent service construction could race registration. `unRegister` unregisters regardless of whether the source is registered. Tests should cover singleton behavior, counter increments, rate updates from task completion, and unregister/recreate lifecycle.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerServiceMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerVersion.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerVersion.java

Purpose: Enumerates supported disk balancer info/config versions.

Important APIs and types: Currently defines `ONE(1, "First Version")`, `DEFAULT_VERSION`, a list of all values, and lookup helpers by int or string.

Control flow: Lookup methods linearly scan the immutable value list and return null when unsupported.

State and persistence: Version values are persisted in `diskBalancer.info` YAML and validated on read.

Dependencies and integration points: `DiskBalancerInfo` stores a version; `DiskBalancerYaml` writes and validates it.

Risks: Returning null on unknown versions means callers must check; `DiskBalancerYaml` does and throws `IOException`. Tests should cover known int/string lookup, unknown versions, and default version serialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerVolumeCalculation.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerVolumeCalculation.java

Purpose: Shared utility for immutable-ish volume usage snapshots and disk balancer utilization calculations.

Important APIs and types: Provides `getVolumeUsages`, `getIdealUsage`, `calculateVolumeDataDensity`, `computeUtilization`, `newVolumeFixedUsage`, and nested `VolumeFixedUsage` containing an `HddsVolume`, a fixed usage snapshot, effective used bytes, utilization, and usable-space calculation.

Control flow: `getVolumeUsages` snapshots each active volume and applies delta-map adjustments. `getIdealUsage` sums capacities and effective-used bytes, validating non-negative and not-over-capacity values. Density sums absolute deviations from ideal usage for positive-capacity volumes. Effective usage is filesystem used plus committed bytes plus required/delta bytes.

State and persistence: Stateless utility. `VolumeFixedUsage` captures a point-in-time usage snapshot from `HddsVolume.getCurrentUsage`.

Dependencies and integration points: Used by `DiskBalancerService` for status and bytes-to-move calculations and by `DefaultContainerChoosingPolicy` for selection. Depends on `VolumeUsage.getUsableSpace` for destination viability.

Risks: `newVolumeFixedUsage` asserts every `StorageVolume` is an `HddsVolume`; callers must not pass metadata or DB volume sets. Negative deltas can make effective-used negative and trigger exceptions. `calculateVolumeDataDensity` catches exceptions and returns `-1.0`, while `getIdealUsage` throws. Tests should cover zero-capacity volumes, delta effects, invalid negative/effective-over-capacity states, and consistency between status and policy calculations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerVolumeCalculation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerYaml.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerYaml.java

Purpose: Serializes and deserializes `DiskBalancerInfo` to the local `diskBalancer.info` YAML file.

Important APIs and types: `createDiskBalancerInfoFile` writes YAML using SnakeYAML and `YamlUtils.dump`. `readDiskBalancerInfoFile` reads YAML into nested `DiskBalancerInfoYaml`, validates required fields/version/container states, creates `DiskBalancerInfo`, and validates it via `toConfiguration`.

Control flow: On read, missing `operationalState` or version throws `IOException`; unsupported version throws `IOException`; missing/blank container states defaults to `CLOSED,QUASI_CLOSED`; malformed YAML is wrapped as `IOException`. On write, only persisted fields are included: operational state, threshold, bandwidth, parallel thread, stop-after-even, container states, and version.

State and persistence: This is the persistence boundary for disk balancer service config and running status. Report-only fields such as ideal usage and volume reports are intentionally omitted.

Dependencies and integration points: Called by `DiskBalancerService` during load, refresh, stop-after-even, and node-state persistence. Uses `DiskBalancerVersion` and `DiskBalancerConfiguration` for validation.

Risks: Flow-style YAML may be less readable but compact. Backward compatibility for absent `containerStates` is handled by defaulting, but missing version is not tolerated. Tests should cover malformed YAML, missing fields, unsupported versions, invalid persisted config values, default container states, and write/read round trip.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerYaml.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/package-info.java

Purpose: Package-level documentation for the datanode disk balancer service package.

Important APIs and types: Declares package `org.apache.hadoop.ozone.container.diskbalancer` and states that it contains classes related to the DiskBalancer service.

Control flow: No executable behavior.

State and persistence: None.

Dependencies and integration points: Documents the package containing service, configuration, protocol server, YAML persistence, metrics, calculations, and policy factory code.

Risks: The documentation is minimal and does not describe operational state, persistence, or move safety. Test signals are not applicable beyond javadoc/package documentation checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/policy/ContainerCandidate.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/policy/ContainerCandidate.java

Purpose: Immutable result object returned by disk balancer container selection.

Important APIs and types: Stores `ContainerData`, source `HddsVolume`, and destination `HddsVolume`; exposes getters for each.

Control flow: No logic beyond construction and field access.

State and persistence: Runtime selection result only. It is not persisted directly.

Dependencies and integration points: Returned by `ContainerChoosingPolicy.chooseVolumesAndContainer`, consumed by `DiskBalancerService.getTasks` to create a `DiskBalancerTask`.

Risks: Constructor does not validate non-null fields, so policy implementations must avoid returning incomplete candidates. Tests should cover candidate field propagation and service behavior when policy returns null versus a valid candidate.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/policy/ContainerCandidate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/policy/ContainerChoosingPolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/policy/ContainerChoosingPolicy.java

Purpose: Strategy interface for selecting a source volume, destination volume, and container to move in one disk balancer decision.

Important APIs and types: Declares `chooseVolumesAndContainer(OzoneContainer, MutableVolumeSet, Map<HddsVolume, Long>, Set<ContainerID>, double, Set<State>)`.

Control flow: Implementations are expected to combine volume-pair and container selection, account for in-progress source deltas and container IDs, and reserve destination space only after selecting an actual container.

State and persistence: Interface only; no state. Implementations may hold runtime caches or locks.

Dependencies and integration points: Instantiated by `ContainerChoosingPolicyFactory`; called from `DiskBalancerService.getTasks`; default implementation is `DefaultContainerChoosingPolicy`.

Risks: Contract correctness depends on consistent use of `deltaMap`, `inProgressContainerIDs`, threshold semantics, and movable state filtering. Tests should be written against custom policy implementations if introduced, especially around reservation and null-return behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/policy/ContainerChoosingPolicy.java -->
