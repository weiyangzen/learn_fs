<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/TestContainerStateMachine.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/TestContainerStateMachine.java

## Purpose
Abstract JUnit 5 base for testing `ContainerStateMachine` behavior under both Ratis leader and follower modes. It verifies that failed writes and failed transaction application mark only the affected container unhealthy, prevent subsequent dispatches for that container, and propagate either thrown dispatcher failures or error responses as expected.

## Important APIs, Types, And Functions
- `ContainerStateMachine.write(LogEntryProto, TransactionContext)` and `applyTransaction(TransactionContext)` are the primary behaviors under test.
- Mocked `ContainerDispatcher` supplies either runtime exceptions or `ContainerCommandResponseProto` failures.
- `ContainerStateMachine.Context` supplies request/log protobufs used by write/apply paths.
- Helper methods build `WriteChunk` requests with `DatanodeBlockID` container and local IDs.
- `ThrowableCatcher` captures asynchronous `CompletableFuture` exceptions.

## Control Flow
`setup()` configures a mocked `XceiverServerRatis`, `RaftServer.Division`, `DivisionInfo`, `RaftGroup`, and peer, then initializes a state machine with a leader flag provided by subclasses. `testWriteFailure` dispatches a failing write, checks the original failure, then attempts a second write for another container and expects rejection after state machine failure handling. `testApplyTransactionFailure` fails one apply, confirms later operations for that same container are rejected without dispatcher invocation, then proves a different container can still succeed. `testWriteTimout` blocks the dispatcher, waits beyond the configured state machine write wait interval, and checks interruption and internal-error propagation.

## State And Persistence
No durable data is written. The relevant state is in-memory state-machine bookkeeping of unhealthy containers or failed write/apply paths, plus mocked log entry term/index and request proto content. The test also manages two daemon executors shared by the state machine and closes them after the class.

## Dependencies And Integration Points
Integrates Apache Ratis types, Ozone container protobufs, dispatcher contexts, `StorageContainerException`, and Ozone configuration key `HDDS_CONTAINER_RATIS_STATEMACHINE_WRITE_WAIT_INTERVAL`. The abstract class is executed through concrete leader and follower subclasses.

## Risks And Edge Cases
The timeout test uses real sleep and a very long dispatcher sleep, making timing and interruption behavior sensitive. `testApplyTransactionFailure` is marked flaky. The tests rely on exact exception wrapping differences between write and apply futures, so implementation changes in async exception handling can break assertions.

## Test Signals
Signals include dispatcher invocation counts, captured future failures, `ContainerProtos.Result.CONTAINER_INTERNAL_ERROR` and `CONTAINER_UNHEALTHY`, and successful parsing of a `SUCCESS` apply response for a different container.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/TestContainerStateMachine.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/TestContainerStateMachineFollower.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/TestContainerStateMachineFollower.java

## Purpose
Concrete test class that runs the shared `TestContainerStateMachine` suite with `DivisionInfo.isLeader()` mocked as `false`, covering follower-side state-machine behavior.

## Important APIs, Types, And Functions
- Extends `TestContainerStateMachine`.
- Constructor calls `super(false)`.

## Control Flow
JUnit discovers the inherited tests from the abstract base. The only local flow is construction, which fixes the role flag before the base `setup()` builds the mocked Ratis division.

## State And Persistence
No local state is introduced. State is inherited from the base class and remains in-memory test fixture state.

## Dependencies And Integration Points
Depends on the base Ratis state-machine test and shares its `ContainerDispatcher`, `ContainerStateMachine`, and Ratis mocks.

## Risks And Edge Cases
Coverage depends entirely on inherited tests. If leader/follower behavior diverges in code paths not exercised by the base suite, this subclass will not catch it.

## Test Signals
Passing inherited tests show the failure, timeout, and per-container unhealthy handling work when the state machine is initialized as a follower.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/TestContainerStateMachineFollower.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/TestContainerStateMachineLeader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/TestContainerStateMachineLeader.java

## Purpose
Concrete test class that runs the shared `TestContainerStateMachine` suite with `DivisionInfo.isLeader()` mocked as `true`, covering leader-side state-machine behavior.

## Important APIs, Types, And Functions
- Extends `TestContainerStateMachine`.
- Constructor calls `super(true)`.

## Control Flow
JUnit executes inherited base tests after the subclass constructor sets the role flag. The base setup then reports the mocked division as leader.

## State And Persistence
No local persistent or mutable state exists beyond the inherited fixture.

## Dependencies And Integration Points
Depends on the abstract Ratis state-machine test and the same Ozone/Ratis mock integrations used by the follower subclass.

## Risks And Edge Cases
This class has no independent assertions. Its value is role coverage, and gaps in base test scenarios apply here as well.

## Test Signals
Passing inherited tests indicate the same failure propagation, timeout handling, and container-specific unhealthy behavior hold when the state machine sees itself as leader.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/TestContainerStateMachineLeader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/utils/TestDiskCheckUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/utils/TestDiskCheckUtil.java

## Purpose
Tests `DiskCheckUtil` low-level disk predicates for permissions, directory existence, and read/write probe cleanup.

## Important APIs, Types, And Functions
- `DiskCheckUtil.checkPermissions(File)` validates read, write, and execute access.
- `DiskCheckUtil.checkExistence(File)` validates directory existence.
- `DiskCheckUtil.checkReadWrite(File, File, int)` writes and deletes a probe file.
- JUnit `@TempDir` provides isolated filesystem state.

## Control Flow
The permission test toggles read, write, and execute bits off and back on, expecting each missing permission to fail. The existence test deletes the temp directory and expects false. The read/write test runs a 10-byte probe and then asserts the temp directory has no leftover children.

## State And Persistence
Only temporary directory permissions and test files are mutated. Successful read/write checks must not leave persistent probe files behind.

## Dependencies And Integration Points
Provides unit coverage for the disk-check utility used by `StorageVolume` health checks and volume scanner tests.

## Risks And Edge Cases
Permission changes can behave differently on platforms or filesystems that ignore POSIX-like permission toggles, especially under privileged users. The test assumes `File.setReadable`, `setWritable`, and `setExecutable` return true.

## Test Signals
Boolean assertions on utility results and an empty temp directory after the write probe show the checker both detects failures and cleans up after successful tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/utils/TestDiskCheckUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/utils/TestHddsVolumeUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/utils/TestHddsVolumeUtil.java

## Purpose
Validates `HddsVolumeUtil` Schema V3 DB-store loading and placement across data volumes and optional DB volumes, including failure handling on restart.

## Important APIs, Types, And Functions
- `HddsVolumeUtil.loadAllHddsVolumeDbStore(...)` loads per-disk DB stores for `HddsVolume` instances.
- Static mocked `HddsVolumeUtil.initPerDiskDBStore(...)` simulates DB initialization failure.
- `MutableVolumeSet` is built for `DATA_VOLUME` and `DB_VOLUME`.
- `StorageVolumeUtil.getHddsVolumesList` and `getDbVolumesList` filter typed volumes.
- `HddsVolume.loadDbStore`, `check`, `isDbLoadFailure`, and `isDbLoaded` expose DB health state.

## Control Flow
Setup enables Schema V3, creates three data directories and three DB directories, and initializes volume sets. Tests format and create working dirs, reinitialize sets to simulate datanode restart, then load DB stores with or without DB volumes. A bad DB-volume scenario deletes the selected DB volume `VERSION` file before restart and verifies affected Hdds volumes do not create duplicate local DB stores.

## State And Persistence
The tests create VERSION files, cluster working directories, DB parent directories, and storage-ID subdirectories. Restart is represented by shutting down and reconstructing `MutableVolumeSet` from the same configuration. DB load failure state is persisted in the rebuilt volume object state, not in a separate durable artifact.

## Dependencies And Integration Points
Uses `ContainerTestUtils.enableSchemaV3`, Ozone configuration keys for data and DB directories, `VolumeCheckResult`, Mockito static mocking, and the real volume directory layout.

## Risks And Edge Cases
The bad DB volume test depends on at least one DB volume receiving Hdds volume IDs during placement. Static mocking must be tightly scoped to avoid leaking into later tests. Duplicate DB-store prevention is sensitive to the restart path reading failed DB volumes correctly.

## Test Signals
Assertions verify DB parent placement, dbVolume linkage, failed-volume counts, `VolumeCheckResult.FAILED`, DB load flags, and absence of duplicate local storage-ID DB directories for volumes whose external DB volume failed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/utils/TestHddsVolumeUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/utils/TestStorageVolumeUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/utils/TestStorageVolumeUtil.java

## Purpose
Tests that `StorageVolumeUtil.checkVolume` does not create duplicate DB stores when checking an already initialized Hdds volume with a DB volume set.

## Important APIs, Types, And Functions
- `StorageVolumeUtil.checkVolume(StorageVolume, clusterId, scmId, conf, log, dbVolumeSet)`.
- `HddsVolume.createDbStore(MutableVolumeSet)` is observed through a Mockito spy.
- `DbVolume.Builder` and `HddsVolume.Builder` construct real temp-backed volumes.

## Control Flow
The test enables Schema V3, builds one Hdds volume and one DB volume, mocks a DB volume set, checks the DB volume first, then checks the spied Hdds volume twice. The first Hdds check creates the DB store; the second sees existing volume contents and must not call `createDbStore` again.

## State And Persistence
Temporary volume directories, VERSION files, and DB-store directories are created under JUnit temp paths. The meaningful persistent signal is the existing DB-store directory that suppresses duplicate creation.

## Dependencies And Integration Points
Integrates the shared volume builders, `MockSpaceUsageCheckFactory.NONE`, Schema V3 test setup, and SLF4J logging passed into the second check.

## Risks And Edge Cases
This is a narrow regression test. It checks invocation count but not all possible duplicate DB layout states or failed DB volume combinations.

## Test Signals
`checkVolume` returns true for both volume types and `createDbStore` is verified exactly once across two Hdds volume checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/utils/TestStorageVolumeUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/utils/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/utils/package-info.java

## Purpose
Declares package-level documentation for common container utility tests.

## Important APIs, Types, And Functions
- Package declaration: `org.apache.hadoop.ozone.container.common.utils`.
- Javadoc summary identifies the package as tests for common container utilities.

## Control Flow
No executable control flow exists. The file is consumed by Java tooling and Javadoc.

## State And Persistence
No state is maintained or persisted.

## Dependencies And Integration Points
Associates utility test classes in the same package with a package-level description.

## Risks And Edge Cases
Risk is limited to stale or vague package documentation.

## Test Signals
Compilation confirms the package declaration is valid.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/utils/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestAvailableSpaceFilter.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestAvailableSpaceFilter.java

## Purpose
Tests `AvailableSpaceFilter` decisions and metric increments when a volume is above soft limits, inside the soft band, or below hard minimum free space.

## Important APIs, Types, And Functions
- `AvailableSpaceFilter.test(HddsVolume)` is the core predicate.
- `HddsVolume.getReport()` supplies capacity, remaining, committed bytes, and usable space.
- `HddsVolume.getFreeSpaceToSpare(capacity)` models hard minimum spare space.
- `VolumeInfoMetrics` counters record soft-band and hard-reject events.

## Control Flow
Each test builds a mocked volume report with specific capacity, remaining, committed, usable, and spare values, invokes the filter with a required-space threshold, and verifies pass/fail plus the exact metric counter called or not called. Additional tests prove committed bytes can move a volume into the soft band or cause hard rejection.

## State And Persistence
There is no durable state. Metric increments on the mocked `VolumeInfoMetrics` object are the observable side effect.

## Dependencies And Integration Points
Connects storage location reports, Hdds volume spare-space logic, and container-create admission metrics.

## Risks And Edge Cases
The tests encode arithmetic assumptions about remaining, committed, hard spare, and report usable space. If production code changes how `StorageLocationReport.getUsableSpace()` is computed, expected metric behavior must be revisited.

## Test Signals
Mockito `verify` calls distinguish soft-band increments, hard-reject increments, and no metric changes for healthy space.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestAvailableSpaceFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestCapacityVolumeChoosingPolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestCapacityVolumeChoosingPolicy.java

## Purpose
Validates capacity-weighted volume selection, out-of-space reporting, policy factory selection, and committed-space accounting for `CapacityVolumeChoosingPolicy`.

## Important APIs, Types, And Functions
- `CapacityVolumeChoosingPolicy.chooseVolume(List<HddsVolume>, long)`.
- `VolumeChoosingPolicyFactory.getPolicy(OzoneConfiguration)`.
- `HddsVolume.incCommittedBytes` and `getCommittedBytes`.
- Mock space usage sources provide fixed capacity and available bytes.

## Control Flow
Setup creates three Hdds volumes with equal capacity and different available space, disables reserved space, and pre-commits bytes on the largest volume. Tests sample selection 1000 times and expect the most available volume to be chosen more often, request more than available and assert `DiskOutOfSpaceException`, test factory defaults and explicit class names, and assert chosen volume committed bytes increase by request size.

## State And Persistence
Temporary Hdds volumes hold in-memory usage trackers and committed-byte counters. No durable Ozone metadata is the focus.

## Dependencies And Integration Points
Uses Ozone configuration key `HDDS_DATANODE_VOLUME_CHOOSING_POLICY`, reserved-percent config, Hadoop `DiskOutOfSpaceException`, and mock space usage factories.

## Risks And Edge Cases
The probabilistic 1000-round selection can be sensitive if weighting or random behavior changes. Error message assertions include exact most-available text.

## Test Signals
Selection counts, factory class equality, exception message content, and committed-byte deltas demonstrate correct policy behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestCapacityVolumeChoosingPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestDbVolume.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestDbVolume.java

## Purpose
Tests `DbVolume` initialization, restart discovery of Hdds volume IDs, and DB-store cache cleanup when a DB volume fails.

## Important APIs, Types, And Functions
- `DbVolume.Builder`, `format`, `createWorkingDir`, `getHddsVolumeIDs`, and `failVolume`.
- `StorageVolumeUtil.getVersionFile` locates the VERSION file.
- `DatanodeStoreCache` exposes cached DB handler count.
- Helper `createHddsVolumeSet` builds data volumes that use the DB volume set.

## Control Flow
The empty-volume test builds an unformatted DB volume, checks `NOT_FORMATTED`, formats it, and verifies VERSION creation and normal state. The non-empty test creates storage-ID subdirectories under the cluster directory, rebuilds the volume, and checks those IDs are discovered. The failure test creates DB stores for three Hdds volumes on one DB volume, asserts cache size, calls `failVolume`, and expects cached stores to close.

## State And Persistence
VERSION files, cluster directories, and DB instance directories are real temporary filesystem artifacts. `DatanodeStoreCache` is shared process state and is expected to be emptied on failure.

## Dependencies And Integration Points
Uses Schema V3 setup, data volume sets, DB volume sets, storage type defaults, and SCM data directory configuration.

## Risks And Edge Cases
The cache cleanup assertion assumes no unrelated DB handles are left in the singleton cache. Tests using a static `OzoneConfiguration` must avoid leaked config changes from other tests.

## Test Signals
Storage state, cluster ID, storage type, VERSION presence, discovered ID count, and cache size validate DB volume lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestDbVolume.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestHddsVolume.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestHddsVolume.java

## Purpose
Broad unit coverage for `HddsVolume`: VERSION metadata, formatting, tmp directory cleanup, space accounting with reserved bytes, Schema V3 DB placement and cache cleanup, health metrics, container-dir paths, usage metrics, and configured directory permissions.

## Important APIs, Types, And Functions
- `HddsVolume.Builder`, `format`, `createWorkingDir`, `createTmpDirs`, `shutdown`, `failVolume`, and `check`.
- `DatanodeVersionFile` and `StorageVolumeUtil` read persisted VERSION properties.
- `VolumeUsage` and mock `SpaceUsageSource` drive capacity, available, used, and reserved-space behavior.
- `DatanodeStoreCache`, `VolumeInfoMetrics`, and `MetricsCollectorImpl` validate integration with DB cache and metrics.

## Control Flow
Tests build temp-backed volumes with reserved-space config. They format volumes and compare VERSION fields, create tmp/delete/disk-check dirs and ensure leftovers are cleared on create and shutdown, verify usage persistence on shutdown, exercise conservative available-space formulas, create DB stores with and without external DB volumes, fail volumes to assert DB cache cleanup, delete container DB directories to force health failure, and check POSIX permissions from configuration.

## State And Persistence
The file heavily uses filesystem state: VERSION files, cluster directories, tmp directories, deleted-container dirs, disk-check dirs, DB directories, cache persistence for used space, and POSIX permissions. In-memory committed bytes and metric counters are also asserted.

## Dependencies And Integration Points
Integrates with Ozone config keys for reserved space, min free space, DB directories, and data-dir permissions; Schema V3 helpers; Hadoop metrics; Commons IO cleanup; and mock space usage factories.

## Risks And Edge Cases
Permission tests require POSIX permission support. Static configuration and singleton DB cache can leak if tests fail before cleanup. Space-accounting tests encode exact formulas around reserved capacity and delayed DU reporting.

## Test Signals
Signals include VERSION property equality, directory existence/removal, persisted used-space value, computed capacity/available values, DB parent paths, cache size, `VolumeCheckResult`, metrics gauges, and POSIX permission equality.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestHddsVolume.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestPeriodicVolumeChecker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestPeriodicVolumeChecker.java

## Purpose
Tests `StorageVolumeChecker.checkAllVolumeSets()` periodic scanning, min-gap skipping, and scan metrics across immutable, data, and metadata volume sets.

## Important APIs, Types, And Functions
- `StorageVolumeChecker.registerVolumeSet` and `checkAllVolumeSets`.
- `BackgroundVolumeScannerMetrics` scan counters.
- `FakeTimer` controls elapsed time.
- `MutableVolumeSet` for data and metadata volumes.
- `TestStorageVolumeChecker.DummyChecker` supplies immediate health results.

## Control Flow
Setup creates data and metadata volume sets from temp directories. The test registers two immutable sets plus the mutable sets, installs a dummy checker, verifies zero counters, advances time before the first scan, runs a scan, then advances within the min gap and expects a skipped iteration, then advances by the periodic interval and expects a second real scan.

## State And Persistence
Volume directories are temporary. Scan state is held in `StorageVolumeChecker` timestamps and metrics counters.

## Dependencies And Integration Points
Uses datanode disk-check configuration, metadata storage directory config, fake timer infrastructure, and shared volume-count assertion helper from `TestVolumeSet`.

## Risks And Edge Cases
The test depends on default `DatanodeConfiguration` gap and interval values and exact registered volume counts. Changes to what counts as data vs metadata scans require updates.

## Test Signals
Metrics for scan iterations, data scans, metadata scans, skipped iterations, and volumes scanned in the last iteration provide the main pass/fail signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestPeriodicVolumeChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestReservedVolumeSpace.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestReservedVolumeSpace.java

## Purpose
Tests reserved capacity calculation for Hdds volumes from percentage and explicit per-volume configs, invalid config fallback/errors, symlink canonicalization, and minimum free space calculation.

## Important APIs, Types, And Functions
- `VolumeUsage.getReservedInBytes`, `realUsage`, and `getCurrentUsage`.
- Config keys `HDDS_DATANODE_DIR_DU_RESERVED_PERCENT`, `HDDS_DATANODE_DIR_DU_RESERVED`, and datanode min-free-space settings.
- `DatanodeConfiguration.getMinFreeSpace(capacity)`.
- `HddsVolume.Builder.conf`.

## Control Flow
Tests build Hdds volumes with default, percent, explicit path, mismatched path, invalid unit, invalid percent, invalid pair format, and symlink path configurations. They compare expected reserved bytes to reported capacity reduction. The min-free-space test sets absolute and percentage values and confirms the max rule.

## State And Persistence
Temporary folders and a symlink are created. Reserved-space behavior is in-memory configuration-derived state on `VolumeUsage`.

## Dependencies And Integration Points
Uses Ozone configuration parsing, `StorageUnit`, `ConfigurationException`, mock usage factories, and filesystem canonical path resolution.

## Risks And Edge Cases
Symlink creation can fail on platforms without symlink support. Invalid config handling is split between fallback and exception cases, so parser behavior changes may alter expected outcomes.

## Test Signals
Reserved byte equality, capacity equals total minus reserved, thrown `ConfigurationException`, and `getMinFreeSpace` equality validate the config contract.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestReservedVolumeSpace.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestRoundRobinVolumeChoosingPolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestRoundRobinVolumeChoosingPolicy.java

## Purpose
Tests `RoundRobinVolumeChoosingPolicy` ordering, space-aware skipping, out-of-space errors, and committed-space increments.

## Important APIs, Types, And Functions
- `RoundRobinVolumeChoosingPolicy.chooseVolume(List<HddsVolume>, long)`.
- `HddsVolume.getCurrentUsage` and `incCommittedBytes`.
- `DiskOutOfSpaceException` reports insufficient capacity.

## Control Flow
Setup creates two volumes with fixed capacities and availability, disables reserved space, and pre-commits bytes on the second. Tests assert alternating volume selection for zero-size requests, then a larger request skips the first volume. Additional tests request more than available and check the exception message, and verify committed bytes increase on the selected volume.

## State And Persistence
State consists of policy cursor position and per-volume committed-byte counters. Filesystem-backed temp volume roots are created but not the primary behavior.

## Dependencies And Integration Points
Uses the same Hdds volume and mock space usage infrastructure as the capacity policy tests.

## Risks And Edge Cases
Exact error message text includes computed available space after committed/min-free calculations. Cursor state can make tests order-sensitive if a policy instance is reused unexpectedly.

## Test Signals
Selected volume equality, exception message content, and committed-byte delta show expected behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestRoundRobinVolumeChoosingPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestStorageVolumeChecker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestStorageVolumeChecker.java

## Purpose
Tests asynchronous `StorageVolumeChecker` behavior for single and bulk checks, failed volume removal from container state, skipped scan metrics, Guava timeout exception semantics, and timeout tolerance handling.

## Important APIs, Types, And Functions
- `StorageVolumeChecker.checkVolume`, `checkAllVolumes`, and `shutdownAndWait`.
- `AsyncChecker<Boolean, VolumeCheckResult>` and local `DummyChecker`.
- `ThrottledAsyncChecker` timeout behavior is exercised through real `Futures.withTimeout`.
- `MutableVolumeSet.checkAllVolumes`, `OzoneContainer`, and `ContainerSet` integration remove containers from failed volumes.
- `makeVolumes` creates mocked Hdds volumes returning each `VolumeCheckResult` or throwing.

## Control Flow
Parameterized tests run across all `VolumeCheckResult` values plus exception and across container layout versions. Single-volume checks validate callback healthy/failed sets. Bulk checks return failed sets. Volume deletion creates containers on a volume, deletes that volume directory, runs checks, and expects the volume and containers to be removed. Timeout tests use latches to block `check`, verify first timeouts are tolerated, and verify subsequent timeouts produce failures.

## State And Persistence
Temporary Ozone container directories and volume maps are created. Runtime state includes last-check timestamps, metrics counters, timeout sliding windows, container maps, failed volume lists, and mocked callback counters.

## Dependencies And Integration Points
Integrates Guava futures, Hadoop disk checker exceptions, fake timers, Ozone container test utilities, container layout versions, datanode configuration, and key-value container metadata paths.

## Risks And Edge Cases
Timeout tests are concurrency-sensitive but bounded with latches and short timeouts. The Guava exception-type test protects against a subtle dependency behavior change. Volume deletion tests depend on real filesystem deletion and container layout setup.

## Test Signals
Signals include delegate `check` invocation counts, callback counts, failed set sizes, metrics `numScansSkipped`, removed containers, failed volume counts, captured `TimeoutException`, and `recordTimeoutAndCheckFailure` calls.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestStorageVolumeChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestStorageVolumeHealthChecks.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestStorageVolumeHealthChecks.java

## Purpose
Tests real `StorageVolume` health checks for Hdds, metadata, and DB volumes using injectable disk-check implementations, including existence, permissions, IO failure sliding windows, timeout failure windows, and correct disk-check directory selection.

## Important APIs, Types, And Functions
- `StorageVolume.check(boolean)` runs health checks.
- `DiskCheckUtil.setTestImpl` injects custom `DiskChecks`.
- `DatanodeConfiguration` controls disk check enablement, IO tolerance, timeout tolerance, and sliding-window durations.
- `StorageVolume.recordTimeoutAndCheckFailure` and `getTimeoutFailureSlidingWindow` expose timeout accounting.
- Builders for `HddsVolume`, `MetadataVolume`, and `DbVolume` are supplied by a parameterized source.

## Control Flow
Setup clears the shared temp path, resets disk-check injection, configures tolerances, and resets a test clock. Tests inject failing existence or permission checks, simulate full-volume cases where IO checks are skipped due to insufficient probe space, disable IO checks, validate config fallback for negative tolerance, run sequences of IO pass/fail events through a time-based sliding window, verify directory arguments, and test timeout event tolerance/expiry/disable behavior.

## State And Persistence
Temporary storage directories, tmp dirs, disk-check dirs, and volume usage counters are real state. Sliding-window event queues and the shared test clock drive persistence of health events over simulated time.

## Dependencies And Integration Points
Integrates volume builders, `DiskCheckUtil`, `TestClock`, datanode health configuration, and the three storage volume subclasses.

## Risks And Edge Cases
The static `@TempDir` path is reused and manually cleaned, so cleanup is critical. The sliding-window tests rely on artificial time advancement and exact tolerance semantics. Disk-check override state must be cleared before each test.

## Test Signals
Expected `VolumeCheckResult.HEALTHY` or `FAILED`, event counts in timeout windows, asserted disk-check paths, and config-derived tolerance values validate health-check behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestStorageVolumeHealthChecks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestVolumeIOStatsWithPrometheusSink.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestVolumeIOStatsWithPrometheusSink.java

## Purpose
Verifies multiple `VolumeIOStats` sources are exported through `PrometheusMetricsSink` with distinct `storagedirectory` labels.

## Important APIs, Types, And Functions
- `DefaultMetricsSystem` lifecycle.
- `PrometheusMetricsSink.writeMetrics`.
- `VolumeIOStats` registration with storage directory labels.
- Config key `OZONE_DATANODE_IO_METRICS_PERCENTILES_INTERVALS_SECONDS_KEY` supplies percentile intervals.

## Control Flow
Setup initializes the default metrics system and registers a Prometheus sink. The test creates two `VolumeIOStats` instances with different storage directories, publishes metrics, writes Prometheus output to a byte stream, and asserts both labels are present. Teardown stops and shuts down the metrics system.

## State And Persistence
Metrics registration is process-global state inside `DefaultMetricsSystem`. Output is held in memory only.

## Dependencies And Integration Points
Integrates Hadoop metrics2, Ozone Prometheus sink, and volume IO metrics source naming.

## Risks And Edge Cases
Metrics system global state can interfere with other tests if teardown is skipped. The test checks label presence, not metric values or percentile data.

## Test Signals
Prometheus text output containing both `storagedirectory` label values demonstrates that multiple volume IO metrics coexist.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestVolumeIOStatsWithPrometheusSink.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestVolumeInfoMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestVolumeInfoMetrics.java

## Purpose
Tests that `VolumeInfoMetrics` exposes both Ozone-adjusted capacity gauges and raw filesystem gauges, plus derived non-Ozone usage.

## Important APIs, Types, And Functions
- `VolumeInfoMetrics.getMetrics(MetricsCollector, boolean)`.
- Mocked `HddsVolume` metadata and `VolumeUsage`.
- `SpaceUsageSource.Fixed` supplies raw filesystem stats.
- Helper `findMetric` extracts metric values from `MetricsRecordImpl`.

## Control Flow
The test mocks a disk-backed normal data volume, volume usage reserved bytes, raw filesystem capacity/available/used, and Ozone-adjusted current usage. It collects metrics, asserts one record, and checks `OzoneCapacity`, `OzoneAvailable`, `OzoneUsed`, `FilesystemCapacity`, `FilesystemAvailable`, `FilesystemUsed`, `MinFreeSpace`, and `NonOzoneUsed`. It unregisters metrics in a finally block.

## State And Persistence
Only in-memory mocked metrics data is used. Metrics source registration is cleaned up.

## Dependencies And Integration Points
Connects Hdds volume metadata, `VolumeUsage`, Hadoop metrics collector internals, and min-free-space reporting.

## Risks And Edge Cases
The test depends on exact metric names and derived formulas. It does not cover failed-volume metrics or real filesystem usage.

## Test Signals
Collected gauge equality validates that adjusted and raw capacity metrics are distinct and that `NonOzoneUsed` is computed as filesystem used minus Ozone used.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestVolumeInfoMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestVolumeSet.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestVolumeSet.java

## Purpose
Tests `MutableVolumeSet` initialization, explicit volume failure, inconsistent volume detection, shutdown behavior, startup failure metrics, and interruption preservation.

## Important APIs, Types, And Functions
- `MutableVolumeSet` constructors, `getVolumesList`, `getFailedVolumesList`, `getVolumeMap`, `failVolume`, and `shutdown`.
- Static helper `assertNumVolumes` checks volume health metrics.
- `HddsVolumeUtil.getHddsRoot` maps configured data dir to storage root.

## Control Flow
Setup configures two data and Ratis metadata directories and initializes a data volume set. Tests assert both volumes load, fail one volume and verify maps/metrics, add a non-empty volume missing VERSION and verify it becomes failed, shutdown volumes and still allow usage reads, detect read-only startup failure, and reflectively invoke `checkAllVolumes` while interrupted to confirm interruption is preserved.

## State And Persistence
Temporary volume directories, failed volume lists, volume maps, and metrics gauges are mutated. Cleanup deletes storage dirs from both healthy and failed lists.

## Dependencies And Integration Points
Uses Ozone configuration for data and metadata dirs, Commons IO cleanup, metrics assertions, and assumptions for read-only filesystem behavior.

## Risks And Edge Cases
Read-only directory behavior is platform-dependent and guarded by an assumption. The interruption test uses reflection and current-thread interrupt state, which can affect subsequent code if not handled carefully.

## Test Signals
Volume list sizes, failed list sizes, volume map membership, and metrics gauges `TotalVolumes`, `NumHealthyVolumes`, and `NumFailedVolumes` validate behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestVolumeSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestVolumeSetDiskChecks.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestVolumeSetDiskChecks.java

## Purpose
Verifies `MutableVolumeSet` startup disk-check behavior for data, metadata, and DB volumes, and validates container/report handling when a volume fails.

## Important APIs, Types, And Functions
- `MutableVolumeSet.checkAllVolumes` and constructor health filtering.
- Local `DummyChecker` extends `StorageVolumeChecker` to fail the first N volumes.
- `ContainerSet.handleVolumeFailures(StateContext)` removes containers on failed volumes and queues reports.
- `StorageVolumeUtil.getHddsVolumesList` and key-value container creation utilities set up real containers.

## Control Flow
Tests generate configured data, metadata, and DB directories, assert Ozone dirs are created, then run dummy checkers that fail some or all volumes for each volume type. The volume-failure integration test creates two containers on different volume sets, fails one volume, handles failures through a `StateContext`, and verifies only the affected container is removed and a full container report appears.

## State And Persistence
Temporary directories, volume maps, failed lists, container metadata, missing-container sets, and queued SCM reports are mutated. Schema V3 DB parent dirs are configured for created containers.

## Dependencies And Integration Points
Integrates volume checker, datanode state context, SCM report protobufs, key-value containers, Ozone container mock, and randomized directory names.

## Risks And Edge Cases
The dummy checker fails volumes by iteration order, so changes in collection ordering could affect which paths fail but not counts. Report-count assertions depend on `StateContext` report generation semantics.

## Test Signals
Healthy/failed counts, created directory checks, missing container set membership, container presence/absence, and queued report type counts provide coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestVolumeSetDiskChecks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/package-info.java

## Purpose
Declares package-level documentation for container volume tests.

## Important APIs, Types, And Functions
- Package declaration: `org.apache.hadoop.ozone.container.common.volume`.
- Javadoc summary identifies tests for container volumes.

## Control Flow
No runtime control flow exists.

## State And Persistence
No state is held or persisted.

## Dependencies And Integration Points
Provides package metadata for the volume test namespace.

## Risks And Edge Cases
Only documentation drift is relevant.

## Test Signals
Compilation verifies the package declaration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerServiceTestImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerServiceTestImpl.java

## Purpose
Test-only subclass of `DiskBalancerService` that replaces periodic scheduling with latch-controlled execution for deterministic service tests.

## Important APIs, Types, And Functions
- Constructors call the superclass with zero service timeout in milliseconds.
- `runBalanceTasks()` releases one scheduled service iteration.
- `isStarted()` reports test thread liveness.
- `getTimesOfProcessed()` returns completed iteration count.
- Overridden `start()` and `shutdown()` manage a daemon control thread.

## Control Flow
`start()` creates a daemon thread that repeatedly installs a new `CountDownLatch`, waits for `runBalanceTasks`, submits a `PeriodicalTask` to the service executor, waits up to 3000 seconds, and increments a processed counter. `shutdown()` interrupts the control thread and delegates to the superclass.

## State And Persistence
State is in-memory test control state: latch, daemon thread, executor futures, and processed counter. No disk balancer info persistence is introduced by this subclass.

## Dependencies And Integration Points
Used by disk balancer service tests to drive `DiskBalancerService` without waiting for real intervals. It still uses the superclass executor, container dependencies, configuration, and optional injected clock.

## Risks And Edge Cases
`runBalanceTasks` throws if called before the latch is reset or after count reaches zero. The long future timeout avoids test flakiness but could delay failure if a task hangs.

## Test Signals
Service tests can observe `isStarted`, processed count, and deterministic task execution instead of relying on wall-clock scheduling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerServiceTestImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDefaultContainerChoosingPolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDefaultContainerChoosingPolicy.java

## Purpose
Comprehensive tests for `DefaultContainerChoosingPolicy` volume-pair and container selection used by the disk balancer.

## Important APIs, Types, And Functions
- `DefaultContainerChoosingPolicy.chooseVolumesAndContainer`.
- `DiskBalancerVolumeCalculation.getVolumeUsages` and `VolumeFixedUsage`.
- `ContainerCandidate` returns selected container, source volume, and destination volume.
- Test data classes `VolumeTestConfig` and `TestScenario` encode utilization, capacity, threshold, container inventory, blocked destinations, and in-progress IDs.
- `DiskBalancerConfiguration.getMovableContainerStates` controls CLOSED and QUASI_CLOSED eligibility.

## Control Flow
Setup creates policy state, delta maps, and in-progress sets. Helpers create Hdds volumes with fixed usage, install them into a test `MutableVolumeSet`, and add containers to a `ContainerSet`. Parameterized scenarios cover imbalance shapes, threshold boundaries, insufficient destination space, one/zero volumes, blocked destinations, in-progress containers, zero-size containers, and expected source/destination ordering. A separate test verifies QUASI_CLOSED containers are chosen only when configured as movable.

## State And Persistence
The test uses temporary volume roots, in-memory volume maps, container sets, per-container byte stats, committed-byte changes for blocked destinations, and a delta map representing planned balance effects.

## Dependencies And Integration Points
Integrates Hdds volume usage, Ozone container/controller mocks, key-value container data, SCM container size config, disk balancer configuration, and container state protobuf enums.

## Risks And Edge Cases
The suite encodes detailed balancing math and expected sorted-volume indices. Changes to ideal utilization calculation, boundary inclusivity, destination fit checks, or container ordering may require broad test updates.

## Test Signals
Assertions validate whether a candidate is null or non-null, exact source/destination volumes, expected container ID, source/destination sorted indices, destination lower utilization, and configured movable-state behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDefaultContainerChoosingPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerProtocolServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerProtocolServer.java

## Purpose
Unit tests for `DiskBalancerProtocolServer` RPC-facing operations: info/status reporting, start, stop, configuration update, and admin privilege enforcement.

## Important APIs, Types, And Functions
- `DiskBalancerProtocolServer.getDiskBalancerInfo`, `startDiskBalancer`, `stopDiskBalancer`, and `updateDiskBalancerConfiguration`.
- `DiskBalancerInfo` stores running status, thresholds, bandwidth, thread count, state filters, move counters, density, ideal usage, and volume reports.
- `PrivilegedOperation` callback enforces admin checks.
- Protobufs include `DatanodeDiskBalancerInfoProto`, `DiskBalancerConfigurationProto`, and `VolumeReportProto`.

## Control Flow
Setup mocks `DatanodeStateMachine`, `OzoneContainer`, and `DiskBalancerService`, builds a populated `DiskBalancerInfo`, returns it from the container, and constructs a protocol server with either accepting or denying admin operations. Tests fetch reports and compare every volume/config field, start/stop/update the balancer and verify state/config changes plus service refresh calls, and assert denied operations throw expected IOExceptions.

## State And Persistence
State is in-memory `DiskBalancerInfo` mutated by protocol operations. No YAML file or disk persistence is exercised here.

## Dependencies And Integration Points
Integrates datanode identity details, Ozone container disk balancer service, HDDS protobuf models, and admin authorization hooks.

## Risks And Edge Cases
The request uses an old client version constant, so compatibility behavior is indirectly covered. Exact exception messages for denied operations are asserted.

## Test Signals
Field-by-field protobuf equality, running status changes, service `refresh` invocation counts, and thrown admin-denial exceptions validate the protocol server surface.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerProtocolServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerService.java

## Purpose
Tests `DiskBalancerService` lifecycle, configuration refresh validation, default policy initialization, bytes-to-move calculation, task concurrency limits, disk-balancer info persistence, stale temp cleanup, threshold validation, and movable container state parsing.

## Important APIs, Types, And Functions
- `DiskBalancerService.refresh`, `getTasks`, `calculateBytesToMove`, `start`, and `shutdown`.
- `DiskBalancerInfo` drives operational state, threshold, bandwidth, thread count, and stop-after-even behavior.
- `DiskBalancerYaml` reads persisted info files.
- `DiskBalancerConfiguration.setThreshold` and `setContainerStates` validate user configuration.
- `ContainerChoosingPolicy` and `ContainerCandidate` are mocked to exercise task scheduling.
- `DiskBalancerServiceTestImpl` supplies deterministic service execution.

## Control Flow
Setup creates two data volumes with mock half-terabyte usage and Schema V3 DB instances. Tests refresh running and stopped info and assert live service state changes, reject invalid thresholds/bandwidth/thread counts, assert default policy class, compute bytes to move across parameterized volume counts and imbalance percentages, schedule background tasks up to the configured thread limit, validate info-file parent creation and write failure handling, and start the real service to clean stale diskBalancer tmp dirs both with initialized and uninitialized `tmpDir`.

## State And Persistence
State includes real temporary volume directories, DB instances, background task queues, in-progress container IDs, `DiskBalancerInfo`, YAML info files under configurable directories, stale tmp directory trees, and global BlockUtils cache cleanup.

## Dependencies And Integration Points
Integrates volume sets, key-value handlers, container metrics, checksum manager, Ozone container mocks, `BackgroundTaskQueue`, layout/schema parameterization, disk balancer volume calculations, and HDDS/Ozone configuration keys.

## Risks And Edge Cases
Tests touch concurrency, filesystem persistence, and startup cleanup. Log text is used to confirm thread-limit behavior. Info-file failure tests depend on creating path conflicts with files vs directories. Movable state parsing intentionally rejects lowercase, unknown, blank, and non-movable states.

## Test Signals
Assertions cover service info fields, invalid refresh exceptions, policy type, bytes-to-move tolerance, queued task count, in-progress count, persisted YAML equality, IO exception message prefixes, stale directory absence, threshold exceptions, and parsed movable state sets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerService.java -->
