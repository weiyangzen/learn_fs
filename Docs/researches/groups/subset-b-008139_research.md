# subset-b-008139 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestStorageContainerServiceProviderImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestStorageContainerServiceProviderImpl.java

Purpose: This compact unit test verifies that `StorageContainerServiceProviderImpl` delegates Recon SCM-facing pipeline APIs to the injected `StorageContainerLocationProtocol` client. It is a wiring and delegation test rather than an SCM integration test.

Important APIs and types: The test uses Guice `Injector`/`AbstractModule`, `StorageContainerServiceProvider`, `StorageContainerServiceProviderImpl`, `StorageContainerLocationProtocol`, `PipelineID`, protobuf `HddsProtos.PipelineID`, `Pipeline`, `ReconUtils`, and `OzoneConfiguration`. Mockito stubs the SCM client, and `@TempDir` supplies the metadata directory configured through `HddsConfigKeys.OZONE_METADATA_DIRS`.

Control flow: `setup` creates a Guice module, mocks the SCM protocol, generates a random pipeline ID, stubs `getPipeline`, and binds the service provider implementation plus dependencies. `testGetPipelines` obtains provider and SCM client instances from the injector, calls `getPipelines`, and verifies `listPipelines` was called once. `testGetPipeline` calls the provider with the saved protobuf ID, asserts a non-null result, and verifies one `getPipeline` invocation.

State and persistence behavior: The only persisted state is the temporary metadata directory configured into `OzoneConfiguration`; no files are inspected. Runtime state is the Guice object graph and the mock invocation history.

Dependencies and integration points: This guards Recon's SPI implementation boundary to SCM. It assumes constructor injection for `StorageContainerServiceProviderImpl` can resolve `StorageContainerLocationProtocol`, `OzoneConfiguration`, and `ReconUtils`, and that the implementation remains a thin delegate for pipeline reads.

Risks: The test does not cover exception propagation, list return values, RPC retries, authentication, or real SCM connectivity. `setup` catches all exceptions and calls `fail()` without preserving diagnostics, so failures can be less informative than necessary.

Test signals: Exact Mockito `times(1)` verification for `listPipelines` and `getPipeline`, plus a non-null returned `Pipeline`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestStorageContainerServiceProviderImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/package-info.java

Purpose: This package descriptor documents the `org.apache.hadoop.ozone.recon.spi.impl` test package as the location for Recon server implementation tests.

Important APIs and types: It contains only package-level Javadoc and the package declaration. There are no classes, functions, fields, or executable test methods.

Control flow: None. Java compiles the package declaration and associates the Javadoc with the package.

State and persistence behavior: None. This file has no runtime state, no test fixtures, and no persistent side effects.

Dependencies and integration points: The package groups tests such as `TestStorageContainerServiceProviderImpl` that exercise implementations below Recon SPI interfaces. It can also be consumed by generated Javadocs or package-level documentation tooling.

Risks: Behavioral risk is negligible. The only maintenance concern is that the broad phrase "recon server impl tests" may become stale if the package contents narrow or expand.

Test signals: Compilation is the only signal; there are no assertions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/AbstractNSSummaryTaskTest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/AbstractNSSummaryTaskTest.java

Purpose: This abstract fixture centralizes OM/Reconciliation metadata setup for NSSummary task tests. It creates temporary OM DBs, Recon OM metadata managers, Recon SQL/container DB infrastructure, namespace summary managers, and deterministic bucket/key/directory trees across FSO, Legacy, and OBS layouts.

Important APIs and types: The file defines constants for volume, bucket, object IDs, key names, directory names, and file sizes. Key helpers include `commonSetup`, `commonSetUpTestReprocess`, `buildOmKeyInfo`, `buildOmDirInfo`, `buildOmDirKeyInfo`, `initializeNewOmMetadataManager`, `populateOMDB`, `populateOMDBCommon`, `populateOMDBOBS`, getters/setters for shared managers, and `OMConfigParameter`. It depends on `OmMetadataManagerImpl`, `ReconOMMetadataManager`, `ReconTestInjector`, `ReconNamespaceSummaryManager`, `NSSummary`, `BucketLayout`, `OmVolumeArgs`, `OmBucketInfo`, `OmKeyInfo`, `OmDirectoryInfo`, `RDBBatchOperation`, and `OMMetadataManagerTestUtils`.

Control flow: `commonSetup` optionally builds an `OzoneConfiguration`, sets filesystem-path and flush-threshold keys, initializes an OM metadata manager for the requested layout, creates a mocked OM service provider with or without FSO behavior, builds a Recon injector, obtains the namespace summary manager, and populates OM tables according to layout flags. Reprocess tests call `commonSetUpTestReprocess`, which writes a stale NSSummary, commits it, clears the table, runs the supplied reprocess task, verifies stale cleanup, and returns requested bucket summaries.

State and persistence behavior: The fixture writes real RocksDB-backed OM metadata under temp directories and real Recon namespace summary state through `ReconNamespaceSummaryManager`. It persists volume and bucket rows, key rows, directory rows, and namespace summaries. `populateOMDBCommon` creates one key in each of three layouts, `populateOMDBFSO` creates FSO files and directory table entries, `populateOMDBLegacy` models directories as legacy key-table entries ending with `/`, and `populateOMDBOBS` creates flat object-store keys in two buckets.

Dependencies and integration points: All NSSummary task suites depend on this class for consistent object IDs and expected tree topology. It links OM metadata table formats to Recon's namespace summary store, exercises `ReconTestInjector` provisioning, and models the table differences between `FILE_SYSTEM_OPTIMIZED`, `LEGACY`, and `OBJECT_STORE` bucket layouts.

Risks: The fixture bakes in object IDs and file-size-bin expectations; changing OM test utilities, path encoding, bucket layout defaults, or file-size bin constants can break many subclasses. Some boolean combinations in `OMConfigParameter` are subtle, especially `isOBS` versus `legacyPopulate`. Shared mutable managers are instance fields, so subclasses using per-class lifecycle must avoid cross-test contamination by clearing namespace tables.

Test signals: Subclasses rely on successful creation of bucket NSSummaries, absence of the stale `-1` entry after reprocess, exact file counts, byte totals, file-size distribution bins, child directory ID sets, directory names, and parent IDs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/AbstractNSSummaryTaskTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/DummyReconDBTask.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/DummyReconDBTask.java

Purpose: This test helper implements `ReconOmTask` with deterministic pass/fail behavior. It lets controller tests model tasks that always pass, fail once, or always fail without needing a real OM table processor.

Important APIs and types: The class implements `ReconOmTask` methods `getTaskName`, `getTaskTables`, `process`, and `reprocess`, and exposes enum `TaskType` with `ALWAYS_PASS`, `FAIL_ONCE`, and `ALWAYS_FAIL`. It returns `volumeTable` from `getTaskTables` and uses `buildTaskResult` from the interface default/helper contract.

Control flow: The constructor sets `numFailuresAllowed` to `1` for `FAIL_ONCE`, `Integer.MAX_VALUE` for `ALWAYS_FAIL`, and leaves it at `Integer.MIN_VALUE` for `ALWAYS_PASS`. Both `process` and `reprocess` increment `callCtr` and return failure while the counter is within the allowed failure count, otherwise success.

State and persistence behavior: State is in-memory only: `taskName`, `callCtr`, and `numFailuresAllowed`. There is no database access despite the name. Reusing one instance across operations intentionally makes process/reprocess outcomes depend on prior calls.

Dependencies and integration points: It is intended for Recon task controller tests that need predictable retry and failure behavior for `OMUpdateEventBatch` processing and full reprocess. Its `volumeTable` declaration ties it to the controller's table-filtering expectations.

Risks: `ALWAYS_PASS` relies on the sentinel `Integer.MIN_VALUE`, which is terse but non-obvious. The class is package-private through its constructor, so it is mainly usable inside the task test package. Because process and reprocess share one counter, a mixed test can accidentally consume the one allowed failure in a different phase than intended.

Test signals: Consumers observe `TaskResult.isTaskSuccess()` transitions and count calls to validate retry, ignore, or reinitialization behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/DummyReconDBTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestContainerKeyMapperTask.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestContainerKeyMapperTask.java

Purpose: This suite verifies `ContainerKeyMapperTaskOBS` and `ContainerKeyMapperTaskFSO`, which maintain Recon's mapping from container IDs to key prefixes and key counts. It covers full reprocess and delta processing for key-table and file-table events.

Important APIs and types: The test uses `ReconContainerMetadataManager`, `ReconOMMetadataManager`, `ReconTestInjector`, `ContainerKeyPrefix`, `ContainerKeyMapperTaskOBS`, `ContainerKeyMapperTaskFSO`, `ContainerKeyMapperHelper`, `OMDBUpdateEvent`, `OMUpdateEventBatch`, `OmKeyInfo`, `OmKeyLocationInfo`, `OmKeyLocationInfoGroup`, `BlockID`, `Pipeline`, and `BucketLayout`. It relies on `OMMetadataManagerTestUtils` helpers to create OM metadata rows with block locations.

Control flow: `setUp` creates a fresh OM DB and Recon metadata manager, builds a Recon injector with container DB support, clears shared container-count state, and resets table truncation flags. Reprocess tests write keys with location groups containing blocks in containers 1 and 2, run the relevant mapper task, and assert stored prefixes and counts. Process tests build PUT and DELETE batches, run task `process`, and compare pre/post mappings. The duplicate FSO test writes six same-file-name rows under different parent object IDs and expects six distinct container-prefix entries.

State and persistence behavior: The suite writes OM key/file table rows and persists container-key mappings in Recon's container metadata store. It validates per-container prefix maps, per-container key counts, and total container count. FSO keys use object-ID path keys; OBS/default keys use ozone key strings. Runtime shared state in `ContainerKeyMapperHelper` is explicitly cleared between tests.

Dependencies and integration points: These tests exercise how Recon translates OM block location metadata into container-level lookup indexes used by Recon APIs. They integrate OM table encoding, bucket layout selection, block location groups, Recon container metadata persistence, and delta event handling.

Risks: Iterator order is assumed in one FSO process assertion that reads two prefixes from a map. The tests are sensitive to exact key-prefix formatting and object-ID path construction. Shared static container-count state can contaminate other tests if not reset. Some DELETE events use a value object built for a different key, so the signal is mainly container/block removal behavior rather than full key identity fidelity.

Test signals: Empty initial mappings, exact `ContainerKeyPrefix` entries with block version `0`, key count changes for containers 1, 2, and 3, total container count, deletion removing prefixes, FSO slash-prefixed user paths, and six distinct entries for duplicate file names in different directories.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestContainerKeyMapperTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestContainerSizeCountTask.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestContainerSizeCountTask.java

Purpose: This test validates `ContainerSizeCountTask` binning of SCM containers by used bytes and lifecycle state into the Recon SQL utilization table `CONTAINER_COUNT_BY_SIZE`.

Important APIs and types: It uses `ContainerSizeCountTask`, `ContainerInfo`, `ContainerID`, `ContainerManager`, `ReconTaskConfig`, `ReconTaskStatusUpdaterManager`, `ReconTaskStatusUpdater`, JOOQ `DSLContext`, `ContainerCountBySizeDao`, `ReconTaskStatusDao`, `UtilizationSchemaDefinition`, and lifecycle constants `OPEN`, `CLOSED`, `CLOSING`, `QUASI_CLOSED`, and `DELETED`.

Control flow: `setUp` obtains the utilization schema DSL and DAO, configures a one-second task interval, mocks task-status updater creation, constructs the task, and truncates the size-count table. `testProcess` feeds mocked container lists through `processContainers`, then mutates the list to add, resize, and remove containers. `testProcessDeletedAndNegativeSizedContainers` sends valid, deleted, and negative-size containers together.

State and persistence behavior: Persistent state is the Recon SQL table keyed by container-size upper bound. The task inserts or updates counts for power-of-two upper-bound bins, keeps rows whose counts drop to zero, and ignores deleted containers for counting. Negative used-byte values are handled as a valid bucket in this test's first scenario but deleted negative-size containers are not counted in the second.

Dependencies and integration points: The suite focuses on the task's internal `processContainers` path rather than polling `ContainerManager`. It verifies JOOQ/DAO persistence used by Recon utilization endpoints and task status wiring through the updater manager.

Risks: The expected DAO row count includes zero-count rows, so changes that physically delete empty bins would require test updates. The test encodes exact bin boundaries such as 512 MB, 2 GB, and 4 GB. It uses mocked `ContainerInfo`, so it does not cover SCM pagination or real manager failure behavior.

Test signals: DAO row counts, exact counts in upper-bound rows, removal of the old 4 GB count after resizing, zero count after removing a 2 GB-bin container, and filtering of `DELETED` containers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestContainerSizeCountTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestEventBufferOverflow.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestEventBufferOverflow.java

Purpose: This controller-level suite exercises Recon OM event buffer overflow handling, async reinitialization queueing, checkpoint retry behavior, and reset helpers introduced for non-blocking OM synchronization and reinitialization recovery.

Important APIs and types: It uses `ReconTaskControllerImpl`, `ReconTaskController.ReInitializationResult`, `ReconTaskReInitializationEvent.ReInitializationReason.BUFFER_OVERFLOW`, `OMUpdateEventBatch`, `ReconOmTask`, `ReconOMMetadataManager`, `DBStore`, `DBCheckpoint`, `ReconDBProvider`, task status DAOs/updaters, and manager mocks for container, namespace summary, global stats, and file metadata.

Control flow: Tests construct controllers with small `OZONE_RECON_OM_EVENT_BUFFER_CAPACITY` values, register mocked tasks, queue many synthetic OM event batches or explicit reinitialization events, and start the controller executor where needed. Latches coordinate reprocess start/completion. Checkpoint-failure tests spy `createOMCheckpoint` to throw and call `queueReInitializationEvent` repeatedly with sleep intervals to pass retry delay gates.

State and persistence behavior: SQL task-status DAO objects are real via `AbstractReconSqlDBTest`, but most Recon DB/OM DB state is mocked. Runtime state under test includes event-buffer size, overflow flag, dropped-batch count, tasks-failed flag, reinitialization retry counter, checkpoint paths, and controller executor lifecycle. `drainEventBufferAndCleanExistingCheckpoints` clears buffered events, while `resetEventFlags` clears overflow and task-failure flags.

Dependencies and integration points: The tests link the event ingestion path `consumeOMEvents` with reinitialization queueing, staged Recon DB provider access, checkpoint creation from the OM metadata manager, and task `reprocess` execution. They model fallback behavior expected by OM service-provider retry loops without standing up real OM snapshot transfer.

Risks: Several assertions are intentionally broad because async processing may or may not overflow depending on scheduling. Retry tests depend on fixed sleeps around the retry delay, which makes them slower and timing-sensitive. Heavy mocking means checkpoint cleanup, full snapshot fallback, and real DB checkpoint validity are only partially covered.

Test signals: Non-negative dropped batch counts, successful `queueReInitializationEvent`, latch-observed reprocess execution, `RETRY_LATER` for six checkpoint failures, `MAX_RETRIES_EXCEEDED` on the seventh attempt, `createOMCheckpoint` call count, empty buffer after drain/reset, and false overflow/tasks-failed flags after reset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestEventBufferOverflow.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestFileSizeCountTask.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestFileSizeCountTask.java

Purpose: This suite verifies file-size histogram maintenance for `FileSizeCountTaskOBS` and `FileSizeCountTaskFSO`. It covers full reprocess from OM key/file tables and delta processing of PUT, UPDATE, and DELETE events into Recon's RocksDB-backed file metadata store.

Important APIs and types: The tests use `ReconFileMetadataManager`, `FileSizeCountTaskOBS`, `FileSizeCountTaskFSO`, `FileSizeCountKey`, `ReconConstants.FILE_SIZE_COUNT_TABLE_TRUNCATED`, `OMDBUpdateEvent`, `OMUpdateEventBatch`, `OmKeyInfo`, `OMMetadataManager`, `TypedTable`, `TableIterator`, and bucket layouts `OBJECT_STORE` and `FILE_SYSTEM_OPTIMIZED`.

Control flow: `setupOnce` creates a real Recon injector with SQL DB, Recon OM, and container DB and obtains `ReconFileMetadataManager`. `setUp` resets the table-truncation flag, creates OBS/FSO task instances, and deletes all rows from the file-count table. Reprocess tests mock table iterators returning controlled `OmKeyInfo` sequences. Process tests construct event batches and run both tasks over the same batch, then inspect persisted size buckets.

State and persistence behavior: The suite persists counts in the Recon file-count RocksDB table keyed by volume, bucket, and size-bin upper bound. Reprocess truncates and rebuilds counts; process increments on PUT, decrements old bins on DELETE or UPDATE, and increments new bins on UPDATE. Scale tests generate tens of thousands of synthetic keys across volumes and buckets to validate distribution and independence.

Dependencies and integration points: It validates Recon's file-size summary data used by namespace/utilization APIs and tests both OBS key-table and FSO file-table variants. It depends on file-size bin calculation, table names from OMDB definitions, and the shared truncation guard used by parallel task execution.

Risks: Some comments and expected bins are inconsistent with the concrete values, so the assertions are the authoritative signal. Running both OBS and FSO tasks on the same synthetic events can hide layout-filtering problems because each task may ignore different tables. Scale tests use many Mockito mocks, which can be slower and memory-heavy.

Test signals: Non-null `FileSizeCountKey` rows, exact counts for bins `1024`, `2048`, `16384`, `65536`, `131072`, and `Long.MAX_VALUE`, zero-or-null handling after deletion, unchanged counts for unaffected volumes, and successful task results from both reprocess variants.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestFileSizeCountTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTask.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTask.java

Purpose: This suite tests the aggregate `NSSummaryTask` that dispatches FSO, Legacy, and OBS namespace-summary work in parallel. It verifies shared executor reuse, reprocess behavior over mixed-layout buckets, process behavior over interleaved layout events, sub-task seek positions, and bucket-cache invalidation on bucket recreation.

Important APIs and types: It uses `NSSummaryTask`, `NSSummaryTask.BucketType`, `ReconOmTask.TaskResult`, `NSSummary`, `OMDBUpdateEvent`, `OMUpdateEventBatch`, `OmKeyInfo`, `OmBucketInfo`, `ReconOMMetadataManager`, `ReconConstants`, and reflection against `SUB_TASK_EXECUTOR`. It inherits all OM/Recon fixtures from `AbstractNSSummaryTaskTest`.

Control flow: `setUp` creates one bucket per layout and constructs the aggregate task. Reprocess tests clear stale namespace summaries, run `nSSummaryTask.reprocess`, and assert each bucket's baseline count/size/bin state. Process tests reprocess first, then submit mixed event batches that mutate FSO, Legacy, and OBS buckets. Additional nested tests deliberately interleave layout event order, apply layout-specific seek offsets, run sequential batches, and recreate an OBS bucket under the same name with a new object ID.

State and persistence behavior: The task persists `NSSummary` records keyed by bucket or directory object ID. It updates file counts, byte totals, file-size buckets, child directory sets, and per-layout sub-task seek-position maps. The bucket recreate test also exercises an internal bucket-info cache: bucket-table DELETE/PUT events must invalidate cached object IDs so later key events are attributed to the new bucket ID.

Dependencies and integration points: This is the top-level validation that Recon's namespace summary task composes three layout-specific handlers correctly while sharing the Recon namespace summary manager. It connects OM key-table, file-table, directory-table, and bucket-table events to task controller retry metadata via `TaskResult.getSubTaskSeekPositions`.

Risks: Reflection on a private static executor is brittle. Parallel execution can mask ordering assumptions if handlers share state incorrectly. Seek-position expectations are layout-subtask specific and may need updates if retry semantics change. The recreate test manually updates the bucket table because synthetic events do not apply OM DB writes, so it models but does not fully reproduce production ingestion.

Test signals: Same executor object across task instances, stale `-1` summary removed, exact per-bucket file counts and sizes, file-size bin arrays, successful process result, non-null FSO/Legacy/OBS seek positions, layout filtering that leaves unrelated buckets unchanged, independent seek offsets, and new bucket object ID receiving recreated-bucket key counts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTaskControllerIntegration.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTaskControllerIntegration.java

Purpose: This integration-style unit suite verifies that `ReconTaskControllerImpl.reInitializeTasks` cooperates with `NSSummaryTask`'s unified rebuild control. It focuses on static rebuild-state transitions, duplicate rebuild suppression, recovery after failure, and coexistence with other Recon tasks.

Important APIs and types: It uses `ReconTaskControllerImpl`, `NSSummaryTask`, `NSSummaryTask.RebuildState`, `ReconOmTask`, `TaskResult`, `ReconNamespaceSummaryManager`, `ReconOMMetadataManager`, `OMMetadataManager`, `ReconDBProvider`, `DBStore`, task status updater mocks, `ExecutorService`, `CompletableFuture`, `CountDownLatch`, and `AtomicInteger`.

Control flow: `setUp` resets static NSSummary rebuild state, builds a testable anonymous `NSSummaryTask` that overrides `executeReprocess` with mocked sub-task callables, registers it plus a mock task in a started controller, and configures namespace-summary clearing to succeed by default. Individual tests use latches to hold rebuilds in `RUNNING`, invoke direct `reprocess` and/or controller `reInitializeTasks`, then release latches and inspect state and invocation counts.

State and persistence behavior: State is almost entirely mocked and in-memory. The critical state is static `NSSummaryTask` rebuild state moving between `IDLE`, `RUNNING`, and `FAILED`. The controller task registry and executor lifecycle are real. No real namespace summaries are persisted; `clearNSSummaryTable` is the mocked hook used to simulate rebuild work or failure.

Dependencies and integration points: The suite exercises the contract between task-controller reinitialization and NSSummary's global rebuild lock. It ensures other registered Recon tasks can still reprocess while NSSummary rebuild attempts are skipped or rejected due to an already-running rebuild.

Risks: Because `executeReprocess` is overridden, this does not validate actual FSO/Legacy/OBS rebuild logic. Static rebuild state makes isolation critical; `resetRebuildState` in setup and teardown is required. The concurrent test allows a range of call counts, which proves final state consistency more than exact suppression behavior. Shutdown behavior is timing-sensitive.

Test signals: `RUNNING` while a rebuild is blocked, `IDLE` after success, `FAILED` after simulated failure, recovery to `IDLE` on subsequent success, only one rebuild attempt during an external running rebuild, other-task reprocess counts, mixed success/failure tasks all attempted, and no final state stuck in `RUNNING` during shutdown.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTaskControllerIntegration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTaskWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTaskWithFSO.java

Purpose: This suite validates the FSO-specific namespace summary task over OM file and directory tables. It checks reprocess and delta updates for file counts, byte totals, file-size distributions, child directories, directory names, parent IDs, and flush-threshold behavior.

Important APIs and types: It uses `NSSummaryTaskWithFSO`, `NSSummaryTaskDbEventHandler`, `NSSummary`, `OmKeyInfo`, `OmDirectoryInfo`, `OMDBUpdateEvent`, `OMUpdateEventBatch`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `ReconNamespaceSummaryManager`, `FileTable` name constants, `Pair<Integer, Boolean>`, and reflection to set private threshold/manager fields in a mocked task.

Control flow: `setUp` uses `commonSetup` with FSO layout, filesystem paths enabled, and flush threshold `3`, then constructs `NSSummaryTaskWithFSO`. Reprocess tests run `reprocessWithFSO` and inspect the seeded tree. Process tests reprocess a baseline, then submit seven events: file PUT, file DELETE, file UPDATE, directory PUTs under two buckets, directory DELETE under `dir1`, and directory rename. Flush tests inspect returned seek position and simulate flush failure.

State and persistence behavior: FSO summaries are keyed by bucket and directory object IDs. The task persists file counts and total sizes at bucket or parent-directory scope, child directory sets on parents, directory names, and parent IDs. With thresholded processing, it flushes accumulated in-memory summary maps to Recon DB in batches and returns a seek position for retry.

Dependencies and integration points: It exercises FSO OM path semantics where parent object IDs define hierarchy, file records live in the file table, and directories live in the directory table. It validates the shared namespace summary manager's batch commit behavior and the event handler's flush-to-DB path.

Risks: The flush-failure test uses Mockito on a class with private fields set by reflection, so it is brittle. Some assertions/messages around the boolean result wording are confusing, but the expected values define behavior. Static answer sets must be cleared before reuse to avoid accumulation.

Test signals: Bucket one/two file counts and byte totals, file-size bin locations, child directory sets `{dir1}`, `{dir2, dir3}`, `{dir4}`, `{dir5}`, directory names including rename to `dir1_new`, parent IDs for initial and newly added dirs, seek position `7` after threshold flushing, and controlled failure returning seek position `0`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTaskWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTaskWithLegacy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTaskWithLegacy.java

Purpose: This suite validates `NSSummaryTaskWithLegacy` for legacy bucket layout, where directories are represented as key-table entries with trailing separators and hierarchy is inferred from key names.

Important APIs and types: It uses `NSSummaryTaskWithLegacy`, `NSSummary`, `OmKeyInfo`, `OMDBUpdateEvent`, `OMUpdateEventBatch`, `BucketLayout.LEGACY`, `ReconConstants`, `OM_KEY_PREFIX`, and shared fixture builders from `AbstractNSSummaryTaskTest`.

Control flow: `setUp` populates a legacy tree and constructs the legacy task with a flush threshold from OM configuration. Reprocess tests rebuild namespace summaries and validate two buckets plus nested directories. Process tests clear summaries, rebuild, then apply a seven-event batch for file PUT, file DELETE, file-size UPDATE, directory PUTs, directory DELETE, and directory rename.

State and persistence behavior: Persistent `NSSummary` rows are keyed by bucket/directory object IDs even though legacy hierarchy comes from key names. Reprocess records bucket file totals, directory child sets, directory names such as `dir1/dir2`, and file-size bins. Process updates file counts/sizes, child directory membership, and directory names after rename.

Dependencies and integration points: The suite exercises the legacy key-table parser used by Recon to synthesize namespace trees from flat key names. It connects OM key events with namespace summary persistence without using the FSO directory table.

Risks: Legacy directory handling is path-string sensitive, especially trailing `OM_KEY_PREFIX` and nested names. One process test comment says bucket one is empty, but the assertion expects two files due to legacy directory/file accounting. Static answer sets need clearing before assertions that reuse them.

Test signals: Stale summary cleanup, bucket file counts of `2` and `2` after reprocess, correct byte totals, file-size distribution bins, child directory set for bucket one and dir1, dir2 containing the large file, bucket two gaining file5 and dir5, updated key2 size, and dir1 rename to `dir1_new`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTaskWithLegacy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTaskWithLegacyOBSLayout.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTaskWithLegacyOBSLayout.java

Purpose: This suite verifies `NSSummaryTaskWithLegacy` behavior when filesystem paths are disabled and flat OBS-style data is processed through the legacy task path. It is a compatibility/regression test for object-store layout semantics in the legacy handler.

Important APIs and types: It uses `NSSummaryTaskWithLegacy`, `BucketLayout.LEGACY`, `NSSummary`, `OmKeyInfo`, `OMDBUpdateEvent`, `OMUpdateEventBatch`, `ReconConstants`, `OM_KEY_PREFIX`, and the OBS population helper from `AbstractNSSummaryTaskTest` with `isOBS` true and filesystem paths disabled.

Control flow: `setUp` builds two flat buckets using OBS-style population but constructs the legacy task. Reprocess tests rebuild and validate the flat bucket totals. Process tests clear and rebuild, then apply PUT events for key6 and a slash-heavy key7, DELETE for key1, and UPDATE resizing key2.

State and persistence behavior: The namespace summary table contains only bucket-level file totals and no child directories. Reprocess persists three files in bucket1 and two in bucket2. Process preserves flat object-store semantics: key insertions, deletion, and resizing alter bucket counts, byte totals, and size bins without creating directory summaries despite embedded slashes.

Dependencies and integration points: This covers the interaction between legacy task logic, disabled filesystem paths, and object-store-style keys. It guards against interpreting OBS keys as hierarchical directories when the compatibility path is used.

Risks: The setup uses `BucketLayout.LEGACY` while the class name refers to OBS layout, so the test intent depends on the fixture flags more than the local `getBucketLayout` name. It duplicates many assertions from the OBS-specific task suite, which can drift if the two compatibility paths intentionally diverge.

Test signals: Bucket counts `3` and `2` after reprocess, expected byte totals, bins `{0,1,40}` and `{0,2}`, no child dirs, counts `3` and `3` after process, updated bucket sizes including key7 and resized key2, and bins `{1,3,40}` and `{0,2,3}`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTaskWithLegacyOBSLayout.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTaskWithOBS.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTaskWithOBS.java

Purpose: This suite validates the object-store-specific namespace summary task, `NSSummaryTaskWithOBS`, for flat OBS bucket layout. It covers full reprocess and delta events without directory hierarchy.

Important APIs and types: It uses `NSSummaryTaskWithOBS`, `BucketLayout.OBJECT_STORE`, `NSSummary`, `OmKeyInfo`, `OMDBUpdateEvent`, `OMUpdateEventBatch`, `ReconConstants`, `OZONE_RECON_NSSUMMARY_FLUSH_TO_DB_MAX_THRESHOLD`, and the OBS tree populated by `AbstractNSSummaryTaskTest`.

Control flow: `setUp` populates OBS-style buckets and constructs the OBS task with the configured/default flush threshold and retry parameters. Reprocess tests run `reprocessWithOBS` and check bucket summaries. Process tests clear summaries, rebuild, then submit four key-table events: PUT key6 into bucket2, PUT slash-heavy key7 into bucket1, DELETE key1 from bucket1, and UPDATE key2 size in bucket1.

State and persistence behavior: The task persists bucket-level `NSSummary` rows only; child directory sets remain empty. It updates file counts, aggregate size, and file-size distribution arrays for flat object names. Large key3 occupies the final configured file-size bin, and slash-heavy key7 is treated as an object name, not as directories.

Dependencies and integration points: This test isolates Recon's OBS namespace summary path and ensures it uses object-store bucket layout table access and key parsing. It complements the legacy OBS-layout compatibility test by validating the dedicated OBS task implementation.

Risks: The test duplicates expected behavior with `TestNSSummaryTaskWithLegacyOBSLayout`; future changes must decide whether both paths should remain identical. It does not test bucket-table events or retry seek positions for OBS in isolation.

Test signals: Reprocess counts of three files in bucket1 and two in bucket2, exact byte totals, expected bins `{0,1,40}` and `{0,2}`, empty child directory sets, process counts of three files in each bucket, updated sizes after PUT/DELETE/UPDATE, and expected bins `{1,3,40}` and `{0,2,3}`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTaskWithOBS.java -->
