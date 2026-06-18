# Research Group: subset-b-008140

This grouped report covers the requested Apache Ozone Recon task/upgrade tests and the S3 Vault remote secret-store module. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTreePrecomputeValues.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTreePrecomputeValues.java

Purpose: JUnit coverage for `NSSummaryTaskWithFSO` materialized namespace totals on a hand-built FILE_SYSTEM_OPTIMIZED tree. It extends `AbstractNSSummaryTaskTest`, overrides OM metadata manager initialization to force custom volume/bucket object IDs, and builds a deterministic tree under `customVol/customBucket1` with nested directories and files.

Important APIs and control flow: `setUp` configures FSO layout, creates `NSSummaryTaskWithFSO`, and calls `populateComplexTree`. Helpers write directories and keys through `OMMetadataManagerTestUtils`, then `runProcessEvents` clears the NSSummary table, runs `reprocessWithFSO`, and applies an `OMUpdateEventBatch` through `processWithFSO`. Tests cover full reprocess totals, file PUT propagation, directory PUT child-dir updates, directory-plus-file PUT ordering, file DELETE propagation, directory DELETE unlinking, and directory-first/file-first deletion ordering.

State and persistence behavior: The tests assert persisted `NSSummary` rows for bucket and directory object IDs, especially `numOfFiles`, `sizeOfFiles`, `childDir`, and `parentId`. Deleting a directory unlinks it by setting parent ID to `0` while ancestor totals are decremented; later file deletion under an already unlinked directory exercises idempotence and exposes nuanced expectations around retained versus zeroed local totals.

Dependencies and integration points: Relies on OM metadata tables, Recon namespace summary manager, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `OMDBUpdateEvent`, and `OMUpdateEventBatch`. It validates the contract consumed by Recon namespace APIs and by upgrades that trigger NSSummary rebuilds.

Risks and test signals: Strong signal for aggregate propagation and deletion-order regressions. Risk areas include brittle custom object IDs, event-key simplification to file/dir names rather than full RocksDB keys, and comments/assertions in the directory-first scenario that are not fully aligned, making future changes to deletion semantics easy to misinterpret.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTreePrecomputeValues.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryUnifiedControl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryUnifiedControl.java

Purpose: Tests queue-based unified control for triggering NSSummary tree rebuilds through `ReconTaskControllerImpl.queueReInitializationEvent`. It verifies that production callers can concurrently request rebuilds while a single async event-processing lane serializes actual `NSSummaryTask.reprocess` execution.

Important APIs and control flow: `setUp` resets static `NSSummaryTask` rebuild state, creates mocked Recon managers, configures an event buffer, registers a testable anonymous `NSSummaryTask`, wires checkpoint-capable `ReconOMMetadataManager`, and starts the controller. The overridden `executeReprocess` clears the namespace summary table, invokes dummy subtasks, and drives `RebuildState` transitions. Tests cover initial IDLE state, success, failure, retry after failure delay, concurrent queue attempts, `ReconUtils.getNSSummaryRebuildState`, exception recovery, checkpoint creation failure, and buffer integration.

State and persistence behavior: Focuses on in-memory static `RebuildState` (`IDLE`, `RUNNING`, `FAILED`) and controller event buffer state rather than durable Recon SQL data. Checkpoint mocks simulate DB snapshots used for rebuild isolation. Retry tests depend on the task/controller retry delay, using waits around 2100 ms.

Dependencies and integration points: Integrates `ReconTaskControllerImpl`, `ReconTaskReInitializationEvent`, `OMUpdateEventBuffer`, `ReconUtils`, `DBCheckpoint`, `DBStore`, `ReconOMMetadataManager`, and `ReconTaskStatusUpdaterManager`. The concurrency helper classes use `CountDownLatch`, `CompletableFuture`, and atomic counters to prove no concurrent rebuild execution.

Risks and test signals: High signal for concurrency serialization, retry gating, checkpoint failure behavior, and public state reporting. Risks include time-based sleeps that can be flaky on overloaded CI and reliance on static rebuild state reset in setup/teardown.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryUnifiedControl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestOMDBUpdatesHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestOMDBUpdatesHandler.java

Purpose: Tests `OMDBUpdatesHandler`, the RocksDB write-batch decoder that turns OM metadata WAL updates into typed `OMDBUpdateEvent` instances for Recon tasks.

Important APIs and control flow: `setUp` creates separate source OM and Recon OM metadata managers. Tests write volumes, keys, delegation tokens, deleted entries, file table rows, deleted table rows, and directory rows into source OM DB, then `getBytesFromOmMetaManager` reads RocksDB updates via `getUpdatesSince`, captures `WriteBatch` bytes, and `captureEvents` iterates each batch through `OMDBUpdatesHandler`. Assertions verify PUT, UPDATE, DELETE, key/value type decoding, old-value lookup from Recon OM DB, and same RocksDB key strings across different tables.

State and persistence behavior: Source OM DB supplies WAL mutations; Recon OM DB is used as previous-state reference for old values and DELETE value recovery. Nonexistent DELETE operations are intentionally ignored because no old value can be resolved. Same-key events in file/deleted/directory tables must remain distinct by table to avoid class casts and event loss.

Dependencies and integration points: Uses `OmMetadataManagerImpl`, `RDBStore`, `RocksDatabase`, `ManagedTransactionLogIterator`, `WriteBatch`, `OMDBDefinition`, and OM helper value types (`OmVolumeArgs`, `OmKeyInfo`, `RepeatedOmKeyInfo`, `OmDirectoryInfo`, `OzoneTokenIdentifier`).

Risks and test signals: Strong signal for WAL parsing and type-safe event construction. Risks include assumptions about WAL sequence offsets, RocksDB write order, and random data sizes. Duplicate-key coverage is especially important for FSO paths where table identity is part of event identity.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestOMDBUpdatesHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestOMUpdateEventBuffer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestOMUpdateEventBuffer.java

Purpose: Unit tests for `OMUpdateEventBuffer`, the bounded queue that buffers ordinary OM update batches and synthetic Recon reinitialization events.

Important APIs and control flow: Tests instantiate a capacity-100 buffer, offer and poll `OMUpdateEventBatch`, fill capacity to assert overflow rejection, poll an empty queue with timeout, enqueue a `ReconTaskReInitializationEvent`, clear the queue, reset dropped-batch counters, and verify `clear` preserves the dropped counter.

State and persistence behavior: State is in-memory queue size and a dropped-batches counter. Overflow increments the counter and returns `false`; `clear` drains pending events but intentionally does not reset overflow evidence. `resetDroppedBatches` explicitly clears the counter.

Dependencies and integration points: Uses `ReconEvent`, `OMUpdateEventBatch`, `OMDBUpdateEvent`, and `ReconTaskReInitializationEvent` with a mocked checkpointed `ReconOMMetadataManager`. This buffer feeds `ReconTaskControllerImpl` async processing and overflow-driven rebuild logic.

Risks and test signals: Good signal for bounded-buffer behavior and event polymorphism. It does not exercise concurrent producer/consumer races or controller-level overflow transitions, which are covered elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestOMUpdateEventBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestOmTableInsightTask.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestOmTableInsightTask.java

Purpose: Broad test suite for `OmTableInsightTask`, which computes Recon global statistics for OM table row counts and size totals. It covers count-only tables and size-bearing tables such as open key/file, deleted key, deleted directory, and multipart info tables.

Important APIs and control flow: `initializeInjector` builds a Recon test injector with SQL DB, Recon OM, container DB, namespace summary manager, global stats manager, `OmTableInsightTask`, and `NSSummaryTaskWithFSO`. Tests call `reprocess` over mocked or real OM tables and `process` over `OMUpdateEventBatch` deltas. Helpers read global stats using `OmTableInsightTask.getTableCountKeyFromTable`, `getUnReplicatedSizeKeyFromTable`, and `getReplicatedSizeKeyFromTable`.

State and persistence behavior: Results persist to Recon SQL `GLOBAL_STATS` through `ReconGlobalStatsManager`. The task maintains in-memory count and size maps initialized from persisted stats. Deleted table counts reflect number of contained `OmKeyInfo` entries, not rows. Deleted-directory size handling depends on namespace summary rows keyed by object ID. Multipart size totals derive from part `KeyInfo` data size and replication factor.

Dependencies and integration points: Integrates OM table definitions, Recon OM metadata manager, `ReconNamespaceSummaryManagerImpl`, `NSSummaryTaskWithFSO`, jOOQ DSL, generated `GlobalStatsTable`, OM helpers, replication configs, and `OMDBUpdateEvent` actions. It is a central consumer of OM update events produced by the update handler.

Risks and test signals: High signal for aggregate correctness across reprocess and incremental paths. Risks include singleton/static task fields in the test class, mock iterator behavior that may hide real table implementation issues, and implicit assumptions about deleted directory path parsing and multipart replication arithmetic.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestOmTableInsightTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestOmTableInsightTaskStaleCounterAfterReinit.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestOmTableInsightTaskStaleCounterAfterReinit.java

Purpose: End-to-end regression test for a stale in-memory counter bug after `ReconTaskControllerImpl.reInitializeTasks`. It proves the registered `OmTableInsightTask` must reload its maps after staged DB replacement so later delta events use the rebuilt base count.

Important APIs and control flow: Setup creates a real Recon OM metadata manager, Recon SQL DB, `ReconGlobalStatsManager`, and controller with status updater mocks. The test writes initial volumes, spies an `OmTableInsightTask` whose `getStagedTask` returns a fresh task, registers it, performs initial `reprocess`, adds more volumes, calls `reInitializeTasks`, then routes a PUT delta through the task returned by `getRegisteredTasks`.

State and persistence behavior: The key persisted state is `volumeTableCount` in Recon global stats. Phase 1 writes count 5; reinitialization over the staged task writes count 8; subsequent delta PUT must write 9. Without calling `init` on the live/registered task after the staged DB swap, the old task would retain base 5 and write 6.

Dependencies and integration points: Integrates `ReconTaskControllerImpl`, `ReconOmTask.getStagedTask`, staged Recon DB provider behavior, `ReconGlobalStatsManager.reinitialize`, `OmTableInsightTask.init`, `ReconTaskStatusUpdater`, and OM volume table writes.

Risks and test signals: Very strong signal for reinit correctness across object identity and DB replacement boundaries. It depends on production controller behavior and real SQL-backed global stats, making it more valuable than a narrow mock test but also more setup-sensitive.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestOmTableInsightTaskStaleCounterAfterReinit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestOmUpdateEventValidator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestOmUpdateEventValidator.java

Purpose: Unit tests for `OmUpdateEventValidator`, which validates that decoded OM update event values match the expected value class for their OM table.

Important APIs and control flow: Setup creates an OM metadata manager and validator from `OMDBDefinition`, then injects a mocked logger. `testValidEvents` checks key, bucket, deleted, prefix, and snapshot tables with correctly typed mock values. `testInvalidEvents` passes strings as values to several tables and expects validation failure plus warning logs.

State and persistence behavior: No durable state. The only mutable global effect is replacing the validator logger through `OmUpdateEventValidator.setLogger`, which test setup controls.

Dependencies and integration points: Uses `OMDBDefinition`, `OMMetadataManager` table names, OM helper classes, Mockito logger capture, and `OMDBUpdateEvent.OMDBUpdateAction.PUT`. It protects downstream Recon tasks from class-cast failures caused by malformed or misdecoded events.

Risks and test signals: Good signal for positive and negative type checks plus log visibility. Risk: static logger replacement can leak if tests are parallelized without isolation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestOmUpdateEventValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestReconTaskControllerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestReconTaskControllerImpl.java

Purpose: Tests the Recon task controller responsible for registering Recon OM tasks, buffering and processing OM events, tracking task status, retrying failures, and rebuilding tasks through reinitialization events.

Important APIs and control flow: Setup constructs a `ReconTaskControllerImpl` with mocked Recon managers, a real `ReconTaskStatusDao`, and a status-updater manager. Tests cover prompt `stop`, task registration, `consumeOMEvents` success and exception paths, retry of a fail-once dummy task, staged `reInitializeTasks`, queueing reinit after checkpoint success/failure, buffer drain and checkpoint cleanup, retry counters, max retry exceeded, task-failure reinit retry, blocking deltas while `tasksFailed` is true, and cleanup of checkpointed managers after reinit processing.

State and persistence behavior: Persists per-task status rows (`lastUpdatedTimestamp`, `lastUpdatedSeqNumber`, `lastTaskRunStatus`) in Recon SQL. In-memory state includes registered tasks, event buffer, overflow/tasks-failed flags, retry counters, current OM metadata manager, and checkpointed manager lifecycle. Reprocess staging writes a `REPROCESS_STAGING` status row and task statuses at the OM DB sequence number.

Dependencies and integration points: Integrates `ReconOmTask`, `ReconTaskStatusUpdater`, `ReconTaskReInitializationEvent`, `OMUpdateEventBatch`, `ReconOMMetadataManager`, `DBCheckpoint`, `ReconDBProvider`, and the scheduler/service behavior that retries task-failure reinitialization.

Risks and test signals: Very high signal for controller lifecycle and failure modes. Some tests use sleeps and manual async waits; one bad-task-removal test is disabled, documenting a known unimplemented behavior. Mock-heavy checkpoint tests verify controller branching but not real checkpoint file behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestReconTaskControllerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestReconTaskStatusUpdater.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestReconTaskStatusUpdater.java

Purpose: Tests intended behavior of `ReconTaskStatusUpdater`, the helper that inserts or updates Recon task status rows.

Important APIs and control flow: Setup mocks `ReconTaskStatusDao` and a mocked `ReconTaskStatusUpdater`, stubbing `updateDetails` to insert when `existsById` is false and update otherwise. Tests verify first-time insert, existing-row update after setting task status, and setter invocations for sequence number, timestamp, run status, and running flag.

State and persistence behavior: The production concept is persisted `ReconTaskStatus` rows with task name, sequence, timestamp, status, and running marker. This test uses mocked objects, so it verifies interaction shape rather than actual field mutation or DAO persistence.

Dependencies and integration points: Uses generated jOOQ DAO/POJO classes and Mockito. The updater is consumed by `ReconTaskControllerImpl` around each task run and reprocess.

Risks and test signals: Low-to-moderate signal because the updater itself is mocked, including the method under test. It documents intended insert/update branching but would not catch implementation regressions inside real `ReconTaskStatusUpdater`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestReconTaskStatusUpdater.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/package-info.java

Purpose: Package documentation for Recon task tests under `org.apache.hadoop.ozone.recon.tasks`.

Important APIs and control flow: Declares the package and contains Javadoc stating that the package tests scheduled tasks used by Recon. It has no executable functions, classes, or control flow.

State and persistence behavior: None.

Dependencies and integration points: Provides package-level documentation for Javadoc and source organization only.

Risks and test signals: No runtime risk or test signal; it helps readers understand that neighboring classes are tests for Recon scheduled tasks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/upgrade/TestInitialConstraintUpgradeAction.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/upgrade/TestInitialConstraintUpgradeAction.java

Purpose: Tests `InitialConstraintUpgradeAction`, specifically schema constraints on the Recon unhealthy containers table.

Important APIs and control flow: Setup obtains a real test `DSLContext`/`DataSource`, creates `InitialConstraintUpgradeAction`, and ensures `UNHEALTHY_CONTAINERS` exists with an initial primary key. The main test executes the upgrade, inserts one row for every `UnHealthyContainerStates` enum value, verifies count, and asserts invalid state insertion fails. Additional tests assert NULL `container_state` and duplicate `(container_id, container_state)` primary key insertions fail.

State and persistence behavior: Mutates an in-memory/test SQL schema through jOOQ. The persistent contract is a table with non-null state, constrained state values, and composite primary key behavior.

Dependencies and integration points: Uses `ContainerSchemaDefinition`, jOOQ DSL, `ReconStorageContainerManagerFacade` data-source access, and `AbstractReconSqlDBTest`. This protects upgrade-time compatibility for Recon SCM unhealthy container state storage.

Risks and test signals: Strong signal for constraint correctness. Risks include test-generated table shape diverging from production migrations and use of `System.currentTimeMillis` as container ID, which is practically unique but not semantically tied to real container IDs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/upgrade/TestInitialConstraintUpgradeAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/upgrade/TestNSSummaryAggregatedTotalsUpgrade.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/upgrade/TestNSSummaryAggregatedTotalsUpgrade.java

Purpose: Tests `NSSummaryAggregatedTotalsUpgrade`, an upgrade action that triggers an NSSummary rebuild through the globally available Recon task controller.

Important APIs and control flow: Each test statically mocks `ReconGuiceServletContextListener.getGlobalInjector`, resolves `ReconTaskController`, and stubs `queueReInitializationEvent(MANUAL_TRIGGER)`. It verifies execute behavior for `SUCCESS`, `RETRY_LATER`, and `MAX_RETRIES_EXCEEDED`, plus failure when the injector is null and propagation when injector lookup throws.

State and persistence behavior: The upgrade itself does not directly mutate SQL in these tests; it triggers asynchronous rebuild scheduling. Static global injector state is mocked and scoped with try-with-resources.

Dependencies and integration points: Integrates upgrade execution, Guice global injector access, and `ReconTaskController` reinitialization API. It ties schema/layout upgrade flow to namespace-summary aggregate recomputation.

Risks and test signals: Good signal that upgrade dispatches a rebuild and handles missing injector. It does not verify eventual rebuild completion or durable NSSummary/global-stat changes, only queueing behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/upgrade/TestNSSummaryAggregatedTotalsUpgrade.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/upgrade/TestReconLayoutVersionManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/upgrade/TestReconLayoutVersionManager.java

Purpose: Tests `ReconLayoutVersionManager`, which tracks Recon metadata layout version (MLV), software layout version (SLV), registered layout features, and transactional finalization of upgrade actions.

Important APIs and control flow: Setup mocks `ReconSchemaVersionTableManager`, static `ReconLayoutFeature.values`, a `DataSource`, and `Connection`. Tests verify initialization MLV/SLV, finalizing schema versions, registered-feature listing, no-feature no-op, rollback on upgrade action failure, rollback on schema update failure, version-sorted action order despite unsorted enum array, no-op when no upgrades are needed, and adding a later feature without re-running already finalized ones.

State and persistence behavior: Persistent state is represented by schema version table manager calls inside a JDBC transaction. Connection auto-commit is disabled, commits happen on success, and rollback is expected on failure. In-memory MLV should not advance when finalization fails.

Dependencies and integration points: Uses `ReconLayoutFeature`, `ReconUpgradeAction`, `ReconSchemaVersionTableManager`, `ReconContext`, JDBC `DataSource`/`Connection`, and Mockito static enum mocking. This governs execution of all Recon schema upgrade actions.

Risks and test signals: High signal for ordering and transaction semantics. Heavy static mocking can hide enum-specific production metadata issues, but it makes the version-manager algorithm deterministic and focused.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/upgrade/TestReconLayoutVersionManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/upgrade/TestReplicatedSizeOfFilesUpgradeAction.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/upgrade/TestReplicatedSizeOfFilesUpgradeAction.java

Purpose: Tests `ReplicatedSizeOfFilesUpgradeAction`, which triggers an NSSummary rebuild so replicated-size fields can be recomputed during upgrade.

Important APIs and control flow: Static mocks provide the global Guice injector, which returns a mocked `ReconTaskController`. The success test verifies `queueReInitializationEvent` is called once. The failure test makes the controller throw and asserts the upgrade wraps it in a `RuntimeException` with message `Failed to rebuild NSSummary during upgrade`.

State and persistence behavior: No direct SQL mutation is verified. The upgrade action delegates state recomputation to Recon task reinitialization.

Dependencies and integration points: Uses `ReconGuiceServletContextListener`, Guice `Injector`, `ReconTaskController`, and `ReconTaskReInitializationEvent.ReInitializationReason`. It is part of Recon layout/schema upgrade flow.

Risks and test signals: Moderate signal for dispatch and exception wrapping. It does not verify handling of non-success enum results or actual rebuilt replicated sizes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/upgrade/TestReplicatedSizeOfFilesUpgradeAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/upgrade/TestUnhealthyContainersStateContainerIdIndexUpgradeAction.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/upgrade/TestUnhealthyContainersStateContainerIdIndexUpgradeAction.java

Purpose: Tests `UnhealthyContainersStateContainerIdIndexUpgradeAction`, which creates an index named `idx_state_container_id` on the unhealthy containers table.

Important APIs and control flow: Setup obtains real test `DSLContext` and `DataSource`. Tests create the table without the index, execute the upgrade, verify index existence via JDBC metadata, rerun execute to prove idempotence, and drop the table to prove missing-table no-op behavior.

State and persistence behavior: Mutates test SQL schema by creating/dropping `UNHEALTHY_CONTAINERS` and inspecting metadata indexes. The persistent contract is that the state/container-id index exists when the table exists and repeated upgrade execution is safe.

Dependencies and integration points: Uses `ContainerSchemaDefinition.UNHEALTHY_CONTAINERS_TABLE_NAME`, `SqlDbUtils.TABLE_EXISTS_CHECK`, jOOQ, and JDBC metadata. This supports query performance and upgrade compatibility for Recon unhealthy container APIs.

Risks and test signals: Good signal for idempotent schema migration. Risk is database-specific metadata casing or index reporting, mitigated by case-insensitive comparison.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/upgrade/TestUnhealthyContainersStateContainerIdIndexUpgradeAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/pom.xml

Purpose: Maven module descriptor for `ozone-s3-secret-store`, packaged as a jar under the Apache Ozone parent at version `2.3.0-SNAPSHOT`.

Important APIs and control flow: Declares module identity, UTF-8 encoding, source download property, and dependencies needed to implement remote S3 secret storage: BetterCloud Vault Java driver, Jakarta annotations, Hadoop common, Ozone common, Ozone manager, and SLF4J API. The compiler plugin disables annotation processing with `<proc>none</proc>`.

State and persistence behavior: No runtime state. Build metadata controls classpath and artifact packaging for the Vault-backed S3 secret-store provider.

Dependencies and integration points: This module depends on Ozone OM interfaces (`S3SecretStore`, `S3SecretStoreProvider`, helper value types) and the Vault driver. It integrates into the larger Ozone build through the parent POM.

Risks and test signals: Build risk centers on Vault driver API compatibility and disabled annotation processing. The POM contains no tests or plugin executions beyond compilation configuration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/S3SecretRemoteStoreConfigurationKeys.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/S3SecretRemoteStoreConfigurationKeys.java

Purpose: Defines string constants for configuring the remote Vault-backed S3 secret store.

Important APIs and control flow: Final utility class with private constructor. Constants use prefix `ozone.secret.s3.store.remote.vault.` and cover Vault address, namespace, secret path, auth type, token, AppRole ID/secret/path, KV engine version, truststore type/path/password, and keystore type/path/password.

State and persistence behavior: No mutable state. These keys are read from Hadoop `Configuration` by `VaultS3SecretStore.fromConf` and `AuthType.fromConf`.

Dependencies and integration points: Shared by Vault store, builder, and auth selection code. It forms the external configuration contract for operators.

Risks and test signals: No tests in this subset directly validate spelling or required-key behavior. Missing or null configuration values flow into auth parsing and Vault client construction, so validation is deferred to consumers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/S3SecretRemoteStoreConfigurationKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/package-info.java

Purpose: Package-level documentation for `org.apache.hadoop.ozone.s3.remote`.

Important APIs and control flow: Contains Javadoc stating the package contains S3 secret remote store code and declares the package. No classes or functions.

State and persistence behavior: None.

Dependencies and integration points: Contributes only Javadoc/source organization.

Risks and test signals: No runtime risk or behavioral test signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/VaultS3SecretStorageProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/VaultS3SecretStorageProvider.java

Purpose: Provider implementation that adapts the Vault-backed store to Ozone's `S3SecretStoreProvider` SPI.

Important APIs and control flow: Implements `get(Configuration conf)` and returns `VaultS3SecretStore.fromConf(conf)`. All configuration parsing and client construction is delegated.

State and persistence behavior: Stateless provider. Runtime persistence is handled by the returned Vault store against the remote Vault backend.

Dependencies and integration points: Integrates Hadoop `Configuration`, Ozone `S3SecretStore`, Ozone OM S3 provider SPI, and `VaultS3SecretStore`.

Risks and test signals: Thin wrapper with low local risk. Operational failures from missing config, auth, or Vault connectivity surface from `fromConf` as `IOException`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/VaultS3SecretStorageProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/VaultS3SecretStore.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/VaultS3SecretStore.java

Purpose: Implements Ozone `S3SecretStore` using HashiCorp Vault through the BetterCloud Vault Java driver.

Important APIs and control flow: Constructor builds `VaultConfig` from address, namespace, KV engine version, and SSL config; normalizes `secretPath` by trimming a trailing slash; stores `Auth`; and attempts initial authentication. `storeSecret` writes a map `{kerberosId -> awsSecret}` at `secretPath/kerberosId`. `getSecret` reads that path and returns `S3SecretValue` when the map contains the Kerberos ID. `revokeSecret` deletes the path. `callWithReAuth` executes a logical Vault call, reauthenticates once for HTTP 400/401/403, retries, and throws if auth still fails. `fromConf` builds the store from Hadoop configuration and optional TLS stores.

State and persistence behavior: Holds a mutable authenticated `Vault` client plus immutable config, auth strategy, and secret path. Secret persistence is remote Vault KV data, one path per Kerberos ID. `batcher` is unimplemented and returns null.

Dependencies and integration points: Uses `Vault`, `VaultConfig`, `LogicalResponse`, `SslConfig`, Ozone `S3SecretStore`, `S3SecretValue`, `S3Batcher`, config keys, `AuthType`, and `Auth`. It plugs into Ozone S3 secret management via `VaultS3SecretStorageProvider`.

Risks and test signals: Key risks are silent constructor auth failure after logging, null `auth` or `secretPath` producing runtime failures, treating HTTP 400 as auth failure, no batch support, and no explicit validation of Vault response structure. No tests in this subset exercise live Vault behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/VaultS3SecretStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/VaultS3SecretStoreBuilder.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/VaultS3SecretStoreBuilder.java

Purpose: Fluent builder for `VaultS3SecretStore`, including optional Java keystore and truststore loading for Vault TLS.

Important APIs and control flow: Setter methods populate address, namespace, secret path, engine version, key/trust store settings, and `Auth`. `build` calls `loadKeyStore`, then `loadTrustStore`, and constructs `VaultS3SecretStore`. Store loaders create `SslConfig` as needed, call `loadStore`, and attach key/trust material. `loadStore` gets a `KeyStore` instance and loads from a filesystem path when provided.

State and persistence behavior: Builder holds mutable configuration until `build`. It reads keystore/truststore files from disk but writes no state. Failed store loading is logged and returns null SSL config rather than failing the build.

Dependencies and integration points: Uses BetterCloud `SslConfig`, Java `KeyStore`, `Files`, `Paths`, `InputStream`, and the Vault store/auth abstractions. It is driven by `VaultS3SecretStore.fromConf`.

Risks and test signals: Potential issue: `loadKeyStore`/`loadTrustStore` return null when corresponding type is absent, so a successfully loaded keystore can be lost if no truststore type is configured, and vice versa. `loadStore` does not call `ks.load(null, pass)` when path is null, which may leave an uninitialized keystore. Errors are logged but not surfaced.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/VaultS3SecretStoreBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/auth/AppRoleAuth.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/auth/AppRoleAuth.java

Purpose: Vault authentication strategy using the AppRole auth method.

Important APIs and control flow: Constructor stores optional role auth path, role ID, and secret ID. `auth(VaultConfig config)` creates an unauthenticated `Vault`, calls `loginByAppRole(path, roleId, secretId)` when a path is configured or `loginByAppRole(roleId, secretId)` otherwise, then returns a new `Vault` built from the same config updated with the returned client token.

State and persistence behavior: Immutable auth parameters. Does not persist credentials locally; receives Vault token from remote auth response and embeds it in the returned client config.

Dependencies and integration points: Implements `Auth`, uses BetterCloud `Vault`, `VaultConfig`, `VaultException`, and `AuthResponse`. Selected by `AuthType.APP_ROLE` from Hadoop configuration.

Risks and test signals: Risks include null/invalid role ID or secret ID not being validated before the Vault call, and token renewal/lifetime being left to reauth-on-failure behavior in `VaultS3SecretStore`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/auth/AppRoleAuth.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/auth/Auth.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/auth/Auth.java

Purpose: Small strategy interface for authenticating a Vault client used by the S3 remote secret store.

Important APIs and control flow: Declares `Vault auth(VaultConfig config) throws VaultException`, returning an authenticated BetterCloud `Vault` client for a supplied base config.

State and persistence behavior: Interface has no state. Implementations may carry credentials or token suppliers.

Dependencies and integration points: Used by `VaultS3SecretStore` for initial auth and reauth, implemented by `AppRoleAuth` and token-based auth, and selected by `AuthType.fromConf`.

Risks and test signals: Minimal local risk. Implementations must be thread-safe enough for the store's use and must not leak credentials in logs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/auth/Auth.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/auth/AuthType.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/auth/AuthType.java

Purpose: Enum and factory for selecting Vault auth strategy from Hadoop configuration.

Important APIs and control flow: Defines `APP_ROLE` and `TOKEN`. `fromConf(Configuration conf)` reads `AUTH_TYPE`, uppercases it, and switches. `TOKEN` reads `TOKEN` and returns `DirectTokenAuth` backed by a token supplier. `APP_ROLE` reads AppRole path, ID, and secret and returns `AppRoleAuth`. The default branch throws `IllegalStateException`.

State and persistence behavior: No mutable state. It maps external configuration into auth strategy objects.

Dependencies and integration points: Uses `S3SecretRemoteStoreConfigurationKeys`, Hadoop `Configuration`, `AppRoleAuth`, and token auth. Called by `VaultS3SecretStore.fromConf`.

Risks and test signals: Missing `AUTH_TYPE` causes a null dereference before a helpful error; invalid values throw `IllegalArgumentException` from `valueOf`. There is no validation for absent token, role ID, or role secret. The default switch branch is unreachable for current enum constants.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/auth/AuthType.java -->
