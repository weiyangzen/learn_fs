# subset-b-008138 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestUnhealthyContainersDerbyPerformance.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestUnhealthyContainersDerbyPerformance.java

## Purpose
Performance and regression benchmark for Recon's Derby-backed `UNHEALTHY_CONTAINERS` persistence path at one-million-row scale. The test documents expected behavior for the `ContainerHealthSchemaManager` APIs used by Recon container health scans and UI pagination, with Derby-specific safeguards for large `IN` clauses, delete chunking, cursor reads, and atomic replace operations.

## Important APIs, types, and functions
- Builds an in-memory Derby Recon SQL schema through Guice modules: `JooqPersistenceModule`, `ReconSchemaGenerationModule`, `ReconDaoBindingModule`, and `ReconSchemaManager`.
- Uses `ContainerHealthSchemaManager`, `UnhealthyContainersDao`, `ContainerSchemaDefinition`, jOOQ `DSLContext`, and generated table `UNHEALTHY_CONTAINERS`.
- Exercises `insertUnhealthyContainerRecords`, `getUnhealthyContainersSummary`, `getUnhealthyContainers`, `replaceUnhealthyContainerRecordsAtomically`, `getExistingInStateSinceByContainerIds`, and `batchDeleteSCMStatesForContainers`.
- Generates `UnhealthyContainerRecord` rows for five `UnHealthyContainerStates`: under-replicated, missing, over-replicated, mis-replicated, and empty-missing.

## Control flow
`@BeforeAll` creates a unique in-memory Derby database, overrides only the JDBC URL from the normal Derby configuration provider, creates schema, and captures DAO/schema manager instances. Ordered tests then insert 200,000 container IDs across five states, verify total counts, run per-state counts, group summaries, paginated reads for one state, paginated reads for all states, atomic delete-plus-insert replacement, large existing timestamp lookups, full dataset delete, and post-delete state counts. `@AfterAll` drops the in-memory database.

## State and persistence behavior
The table uses `(container_id, container_state)` uniqueness and an index shaped for state-count and state-ordered pagination. The suite intentionally shares one dataset across ordered methods: read-only checks depend on the insert, atomic replace rewrites all rows with a new timestamp while preserving row count, and the final delete removes the whole dataset. Chunk sizes are part of the persistence contract: inserts commit in 2,000-container chunks, reads page at 5,000 rows, and deletes rely on internal 1,000-ID partitioning to avoid Derby bytecode limits.

## Dependencies and integration points
The test integrates Recon SQL schema generation, jOOQ generated DAOs/tables, Derby connection configuration, `ContainerHealthTask` preservation lookups, and Recon UI-style container health pagination and summary queries. It is a local embedded database benchmark rather than a cluster test.

## Risks and edge cases
Timing thresholds are deliberately generous but still environment-sensitive. The test is order-dependent and mutates shared state, so parallelization or method reordering would invalidate it. Derby-specific statement-size limits are central: removing internal chunking can produce statement-too-complex or generated-bytecode failures for large ID lists.

## Test signals
Signals include exact row counts, per-state distribution of 200,000 rows, ordered cursor reads, one-million-row full read coverage, replacement timestamp visibility, existing `in_state_since` lookup cardinality, delete completion, and elapsed-time checks for insert, count, summary, pagination, atomic replace, and delete phases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestUnhealthyContainersDerbyPerformance.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestUtilizationSchemaDefinition.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestUtilizationSchemaDefinition.java

## Purpose
End-to-end SQL schema and DAO test for Recon utilization tables. It verifies generated Derby schema metadata and CRUD behavior for cluster growth and file-count-by-size persistence.

## Important APIs, types, and functions
- Extends `AbstractReconSqlDBTest` for a real Recon SQL test database, jOOQ `DSLContext`, and DAO lookup helpers.
- Uses `UtilizationSchemaDefinition` table constants for `CLUSTER_GROWTH_DAILY`, `FILE_COUNT_BY_SIZE`, and `CONTAINER_COUNT_BY_SIZE`.
- Uses JDBC `DatabaseMetaData` to inspect columns and jOOQ-generated DAOs/POJOs such as `ClusterGrowthDailyDao`, `FileCountBySizeDao`, `ClusterGrowthDaily`, and `FileCountBySize`.

## Control flow
`testReconSchemaCreated` queries column metadata for all utilization tables and compares column names and JDBC types in expected order. `testClusterGrowthDailyCRUDOperations` confirms the table exists, inserts one composite-key record, reads it through a jOOQ record key, updates two fields, re-reads, deletes by composite key, and checks the row is gone. `testFileCountBySizeCRUDOperations` inserts a volume/bucket/file-size count row, reads it by the three-part key, updates the count, and inspects the table keys.

## State and persistence behavior
The tested state is relational schema shape and jOOQ DAO persistence. `CLUSTER_GROWTH_DAILY` is keyed by timestamp and datanode id. `FILE_COUNT_BY_SIZE` is keyed by volume, bucket, and file size. The test makes sure updates overwrite rows in place and deletes clear the composite-key lookup.

## Dependencies and integration points
This file sits between Recon schema definitions, generated jOOQ classes, Derby metadata, and utilization APIs that depend on daily growth and histogram tables. It is a schema compatibility guard for generated DAO code.

## Risks and edge cases
Assertions depend on exact column order returned by Derby metadata and exact JDBC type constants. The file-count test does not assert unique key names, only that keys are accessible. It does not cover container-count CRUD beyond schema shape.

## Test signals
Signals are exact column lists, successful insert/read/update/delete cycles, null after deletion, and correct count update behavior through generated DAOs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestUtilizationSchemaDefinition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/package-info.java

## Purpose
Package documentation for Recon persistence tests. It labels `org.apache.hadoop.ozone.recon.persistence` as containing end-to-end tests for persistence classes.

## Important APIs, types, and functions
This file exports no runtime APIs. Its only Java element is the package declaration and Javadoc package comment.

## Control flow
There is no executable control flow.

## State and persistence behavior
No state is stored or mutated. The comment describes the test package that validates Recon SQL and persistence behavior.

## Dependencies and integration points
The package name groups Derby/jOOQ/Recon persistence tests under the same Java namespace as the tested persistence support classes.

## Risks and edge cases
The only maintenance risk is stale package documentation if the package scope broadens beyond persistence end-to-end tests.

## Test signals
No direct test signals. Build-time signal is successful Java package compilation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/recovery/TestReconOmMetadataManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/recovery/TestReconOmMetadataManagerImpl.java

## Purpose
Validates `ReconOmMetadataManagerImpl` startup and snapshot replacement behavior using real OM metadata checkpoints. It proves Recon can open an OM DB snapshot, expose OM metadata tables, and replace an existing opened snapshot DB while closing the old `DBStore`.

## Important APIs, types, and functions
- Uses `OmMetadataManagerImpl` to create a source OM RocksDB and `ReconOmMetadataManagerImpl` as the Recon-side consumer.
- Writes `OmVolumeArgs`, `OmBucketInfo`, and `OmKeyInfo` directly into OM metadata tables.
- Uses `DBCheckpoint`, `DBStore`, `OZONE_OM_DB_DIRS`, `OZONE_RECON_OM_SNAPSHOT_DB_DIR`, `FileUtils.copyDirectory`, and `ReconUtils`.

## Control flow
`testStart` creates a source OM DB, writes one volume, one bucket, and two keys, takes a checkpoint, renames the checkpoint directory to an OM snapshot-style name, copies the parent snapshot area into Recon's snapshot directory, starts `ReconOmMetadataManagerImpl`, and verifies tables and entries are readable. `testUpdateOmDB` starts Recon without a snapshot table initialized, calls `updateOmDB` with a checkpoint, verifies the metadata appears, then updates with another checkpoint and asserts the previous store was closed.

## State and persistence behavior
Persistent state lives in real RocksDB metadata directories under JUnit temp paths. The source OM DB contains volume, bucket, and default-layout key table entries. Recon should not expose tables before a snapshot update in the second test, should open the checkpoint atomically enough for reads afterward, and should close superseded DB handles on replacement.

## Dependencies and integration points
This is the recovery-layer bridge between OM metadata checkpoints and Recon's metadata reader. It depends on OM table key formatting, default bucket layout key tables, RocksDB checkpoint creation, and Recon snapshot directory configuration.

## Risks and edge cases
The tests use direct table writes rather than OM request processing, so they verify snapshot consumption but not OM transaction semantics. Snapshot directory copying and rename behavior may be platform-sensitive. Coverage is limited to default bucket layout and two keys.

## Test signals
Signals are non-null Recon volume, bucket, and key table lookups after startup/update, null table before first update, non-null new checkpoint location, and `current.isClosed()` after replacing the opened Recon OM DB.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/recovery/TestReconOmMetadataManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/recovery/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/recovery/package-info.java

## Purpose
Package documentation for Recon recovery tests. It identifies `org.apache.hadoop.ozone.recon.recovery` as the package for Recon server OM-service-specific tests.

## Important APIs, types, and functions
No APIs or functions are declared. The file contains only license text, package Javadoc, and the package declaration.

## Control flow
There is no executable control flow.

## State and persistence behavior
No runtime state or persistence behavior.

## Dependencies and integration points
The package groups tests around Recon's recovery and OM snapshot service integration.

## Risks and edge cases
The package-level description can become stale if recovery tests expand beyond OM service behavior.

## Test signals
No direct test signals beyond compilation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/recovery/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/AbstractReconContainerManagerTest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/AbstractReconContainerManagerTest.java

## Purpose
Shared test fixture for Recon SCM container-manager tests. It creates a real Recon SCM RocksDB store, real `ReconPipelineManager`, real `ReconContainerManager`, and a mocked `StorageContainerServiceProvider` with representative container responses.

## Important APIs, types, and functions
- Creates `ReconSCMDBDefinition` tables with `DBStoreBuilder`.
- Builds SCM HA stubs (`SCMHAManagerStub`, `SCMHADBTransactionBufferStub`) and `SequenceIdGenerator`.
- Creates `SCMNodeManager`, `ReconPipelineManager`, `ReconContainerManager`, `ContainerReplicaPendingOps`, and mocked `ContainerHealthSchemaManager`/`ReconContainerMetadataManager`.
- Helper methods expose `getConf`, `getPipelineManager`, `getContainerManager`, `getContainerTable`, and `getTestContainer` overloads.

## Control flow
`@BeforeEach` configures temp metadata paths, creates the DB store and transaction buffer, mocks max layout versions, initializes node and pipeline managers, and instantiates a container manager wired to a mocked SCM service provider. `@AfterEach` closes the pipeline manager and DB store. Helper methods create container-with-pipeline objects for open, closed, quasi-closed, and ranged container sets.

## State and persistence behavior
The fixture backs container and pipeline managers with real RocksDB tables. Container additions and state transitions performed by subclasses can be validated both through in-memory managers and DB table reads. The mocked SCM provider returns containers 100, 101, 102 and a batch range 200-299 across lifecycle states.

## Dependencies and integration points
It provides the integration base between Recon SCM DB definitions, container state management, pipeline state management, HA transaction buffering, node topology, and SCM service-provider RPC contracts.

## Risks and edge cases
Because this base creates real managers with mocked support services, subclasses may depend on the mocked provider's fixed IDs and states. It uses a null event publisher in some flows and mocked health/metadata managers, so tests extending it do not validate those side effects.

## Test signals
The fixture itself has no assertions, but subclasses use it to assert DB persistence, container existence, pipeline membership, lifecycle state transitions, replica history, and sync behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/AbstractReconContainerManagerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconContainerManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconContainerManager.java

## Purpose
Unit/integration tests for `ReconContainerManager` using the real fixture from `AbstractReconContainerManagerTest`. It verifies new container insertion, DB persistence, state transitions inferred from datanode replica reports, pipeline bookkeeping, and replica history maintenance.

## Important APIs, types, and functions
- Exercises `addNewContainer`, `checkAndAddNewContainer`, `checkAndAddNewContainerBatch`, `transitionOpenToClosing`, `updateContainerReplica`, `removeContainerReplica`, `containerExist`, `getContainers`, and `getPipelineToOpenContainer`.
- Uses HDDS `ContainerInfo`, `ContainerID`, `ContainerWithPipeline`, `ContainerReplica`, `ContainerReplicaHistory`, `Pipeline`, `ContainerChecksums`, and replica proto states.
- Verifies SCM client calls with Mockito, especially that some transitions avoid `getContainerWithPipeline`.

## Control flow
The first tests add open and closed containers and verify in-memory state plus DB existence after closing the transaction buffer. Batch-add tests feed container replica protos for IDs 200-299 and then repeat the call to prove idempotency. Transition tests cover open-to-closing from CLOSING/CLOSED replica reports, no SCM lookup for open-to-closing, failure handling that leaves open-container counts unchanged, and ignoring unhealthy/invalid/deleted replica reports for open or closing containers. Replica-history tests add and update replicas from two datanodes, then remove one. The final test ensures adding a container with an unknown pipeline first registers that pipeline.

## State and persistence behavior
Container state is tracked in the manager and written to RocksDB. Open containers update pipeline-to-open-container counts; moving out of open removes that mapping. Replica history is an in-memory map keyed by container id and datanode id, preserving first/last seen time, BCS ID, and checksum. Adding a container can also persist/register a missing pipeline.

## Dependencies and integration points
The tests cover interactions among Recon's container state machine, SCM DB transaction buffer, pipeline manager, SCM service-provider fallback, and datanode replica report processing.

## Risks and edge cases
State-machine behavior is intentionally conservative: only open and closing states advance from replica reports; unhealthy/invalid/deleted reports must not downgrade or retire live containers. Regression risk is high around count updates if transition failures occur after partial bookkeeping changes.

## Test signals
Signals include exact lifecycle states, DB table existence, open-container pipeline map contents, no unexpected SCM lookup calls, exception preservation for missing containers, replica history map size/content/timestamps/checksums, and successful handling of duplicate or missing-pipeline additions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconContainerManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconIncrementalContainerReportHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconIncrementalContainerReportHandler.java

## Purpose
Tests Recon's incremental container report (ICR) handler. It verifies that datanode replica reports add missing containers, update replica sets, advance container lifecycle state, and merge multiple reports for one datanode.

## Important APIs, types, and functions
- Uses `ReconIncrementalContainerReportHandler.onMessage`.
- Builds `IncrementalContainerReportFromDatanode`, `IncrementalContainerReportProto`, and `ContainerReplicaProto`.
- Integrates `ReconContainerManager`, `NodeManager`/`SCMNodeManager`, `SCMContext`, `EventPublisher`, and helper methods for report creation.

## Control flow
`testProcessICR` creates a missing container report, stubs batch container lookup from the SCM client, registers the datanode in a real `SCMNodeManager`, invokes the handler, and verifies container plus replica state. `testProcessICRStateMismatch` starts with Recon containers in OPEN and feeds CLOSING, QUASI_CLOSED, and CLOSED replica states to verify expected lifecycle advancement without SCM lookup. `testClosingContainerAdvancesViaScmHandlerWithoutScmLookup` starts from CLOSING and advances to QUASI_CLOSED or CLOSED. `testMergeMultipleICRs` merges three single-entry reports and checks report-list growth.

## State and persistence behavior
The handler mutates the real `ReconContainerManager` from the base fixture. Missing containers are fetched in batch from SCM and persisted through the manager. Replica state is stored in container replicas, while lifecycle state is advanced from datanode report state when allowed.

## Dependencies and integration points
This is the bridge from SCM heartbeat event payloads to Recon container state. It depends on node lookup, datanode registration, event handling, container manager add/check logic, and SCM batch lookup for unknown containers.

## Risks and edge cases
The important edge is avoiding SCM lookups for state mismatches that can be resolved locally. Incorrect mappings from replica states to lifecycle states can leave Recon behind SCM or incorrectly downgrade containers. Merged ICR behavior matters for batching multiple heartbeats from the same datanode.

## Test signals
Signals are container existence, one replica recorded, expected lifecycle state, `never()` verification for SCM lookup in local-transition paths, and report-list sizes after merges.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconIncrementalContainerReportHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconNodeManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconNodeManager.java

## Purpose
Tests `ReconNodeManager` registration, heartbeat, persisted node DB reload, operational-state synchronization from SCM, command filtering, and datanode detail updates.

## Important APIs, types, and functions
- Constructs `ReconNodeManager` with `ReconStorageConfig`, `NetworkTopologyImpl`, `ReconSCMDBDefinition.NODES`, `HDDSLayoutVersionManager`, `ReconContext`, and `EventQueue`.
- Uses `register`, `processHeartbeat`, `getNode`, `getAllNodes`, `getNodeStatus`, `getNodes`, `updateNodeOperationalStateFromScm`, and `addDatanodeCommand`.
- Tests `ReconNewNodeHandler`, `RegisteredCommand`, `ReregisterCommand`, and `SetNodeOperationalStateCommand`.

## Control flow
Setup creates a temp Recon SCM DB and context. One test registers a datanode with invalid network topology and expects registration rejection plus ReconContext health/error updates. The main DB test registers a node, runs new-node handling, injects both an illegal operational-state command and a valid reregister command, verifies heartbeat returns only the valid command, updates persisted operational state via heartbeat, closes and recreates the manager, and checks the node was reloaded. Another test applies an SCM node operational-state update after proving unregistered nodes throw `NodeNotFoundException`. The final test confirms heartbeat updates changed hostname and returns reregister.

## State and persistence behavior
Datanode records are persisted in the Recon SCM `NODES` table and reloaded after manager recreation. Node status mirrors persisted operational state and expiry. ReconContext records invalid-topology errors and unhealthy state when registration is not permitted.

## Dependencies and integration points
This file covers the Recon variant of SCM node management, network topology validation, heartbeat command filtering, node DB persistence, and synchronization of SCM-sourced operational state into Recon's local node table.

## Risks and edge cases
Recon must not send SCM-only commands such as `SetNodeOperationalStateCommand` back to datanodes. Invalid topology must not partially register nodes. Persisted operational state and node status can drift if heartbeat update logic or reload logic changes.

## Test signals
Signals include registration error code, ReconContext error/health state, node counts, node lookup null/non-null results, heartbeat returned command types, persisted operational state/expiry equality, node reload from DB, thrown `NodeNotFoundException`, and hostname update.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconNodeManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconPipelineManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconPipelineManager.java

## Purpose
Tests Recon's pipeline manager initialization and stubbed pipeline factory. It verifies Recon can reconcile pipelines from SCM, update existing pipeline states, remove obsolete pipelines, accept new and duplicate additions, and expose no-op provider behavior.

## Important APIs, types, and functions
- Uses `ReconPipelineManager.newReconPipelineManager`, `initializePipelines`, `addPipeline`, `containsPipeline`, `getPipeline`, `getPipelines`, and `getPipelineFactory`.
- Builds `SCMNodeManager`, `SCMHAManagerStub`, `SCMContext`, `SCMSafeModeManager.SafeModeStatus`, `PipelineFactory`, and `ReconPipelineFactory.ReconPipelineProvider`.
- Uses generated `ReconSCMDBDefinition.PIPELINES` table.

## Control flow
Setup creates temp metadata, Recon storage config, DB store, SCM HA stub, and empty SCM context. `testInitialize` creates three SCM open pipelines, one Recon allocated pipeline with the same ID as an SCM pipeline, and one obsolete closed pipeline. It sets a leader/safe-mode-passed SCM context, adds old pipelines, calls `initializePipelines`, and verifies three final SCM pipelines, state update to OPEN, and obsolete removal. Other tests add a new pipeline, add a duplicate without exception, and inspect the pipeline factory type/providers.

## State and persistence behavior
Pipeline state is stored in the Recon SCM pipeline table and in the manager's runtime maps. Initialization should replace Recon's view with SCM's current view while preserving valid IDs through state updates and deleting stale records.

## Dependencies and integration points
The tests sit between Recon pipeline DB, SCM node manager, HA transaction buffering, safe-mode/leader context, and pipeline factory abstractions used by SCM container placement code.

## Risks and edge cases
Duplicate pipeline handling must remain idempotent. Initialization must not keep obsolete pipelines or fail to update allocated pipelines that SCM has opened. The stub factory should remain inert in Recon because Recon observes SCM pipelines rather than allocating them.

## Test signals
Signals are exact pipeline counts, `containsPipeline` checks for all SCM pipelines, state equality for updated pipelines, absence of obsolete pipeline ID, no exception on duplicate add, and factory/provider instance checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconPipelineManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconPipelineReportHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconPipelineReportHandler.java

## Purpose
Tests Recon's pipeline report handler for known and unknown pipeline IDs reported by datanodes. It ensures Recon fetches and adds a missing pipeline from SCM but does not re-add a pipeline that it already tracks.

## Important APIs, types, and functions
- Exercises `ReconPipelineReportHandler.processPipelineReport`.
- Uses mocked `ReconPipelineManager`, `StorageContainerServiceProvider`, `PipelineReport`, `EventPublisher`, and `ReconSafeModeManager`.
- Converts `PipelineID` to protobuf for the report and SCM service-provider lookup.

## Control flow
The test first stubs a pipeline that is absent from Recon but available from SCM, processes a report for it, and verifies `addPipeline` and `getPipeline` are called. It then stubs another pipeline as already contained in Recon, processes a second report, and verifies no add occurs while the pipeline is still looked up.

## State and persistence behavior
The file uses mocks only, so no actual DB state is mutated. It validates the handler's decision boundary for when to mutate the real pipeline manager.

## Dependencies and integration points
This handler is part of datanode heartbeat processing and bridges pipeline reports to Recon's SCM pipeline cache, with SCM RPC fallback for missing pipeline definitions.

## Risks and edge cases
The test depends on Mockito call counts and reused mocks. A behavior change that performs additional lookups or handles missing SCM pipeline responses differently may need adjusted assertions.

## Test signals
Signals are exact `addPipeline` and `getPipeline` invocation counts for missing versus already-known pipeline reports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconPipelineReportHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconSCMContainerSyncIntegration.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconSCMContainerSyncIntegration.java

## Purpose
Large integration-style suite for `ReconStorageContainerSyncHelper` using a real `ReconContainerManager` and mocked SCM RPC provider. It validates all four container synchronization passes and large-scale end-to-end state correction without a live cluster.

## Important APIs, types, and functions
- Exercises `syncWithSCMContainerInfo`, `getContainerCount`, `getListOfContainerIDs`, `getExistContainerWithPipelinesInBatch`, `getListOfContainerInfos`, and real `ReconContainerManager` state APIs.
- Uses lifecycle states OPEN, CLOSING, CLOSED, QUASI_CLOSED, DELETING, and DELETED plus lifecycle events `FINALIZE` and `DELETE`.
- Configures `OZONE_RECON_SCM_CONTAINER_ID_BATCH_SIZE` and `OZONE_RECON_SCM_DELETED_CONTAINER_CHECK_BATCH_SIZE`.
- Uses `ReconScmContainerSyncMetrics` and helper methods `seedRecon`, `seedReconAsClosing`, `containerCwp`, `containerInfo`, and `idRange`.

## Control flow
The class groups scenarios by sync pass. Pass 1 adds missing CLOSED containers and corrects OPEN, CLOSING, and QUASI_CLOSED to CLOSED, including multi-page and mixed existing/missing pages. Pass 2 adds missing OPEN containers only, avoids downgrading already-advanced containers, tolerates null pipelines, and verifies cursor behavior across repeated syncs. Pass 3 adds QUASI_CLOSED containers, handles null pipelines, skips existing/closed containers, and advances OPEN/CLOSING to QUASI_CLOSED. Pass 4 scans SCM's DELETED list, retires CLOSED/QUASI_CLOSED/DELETING/OPEN containers to DELETED, adds missing DELETED containers via info lookup, and respects deleted-list batch size. Large-scale tests run 100,000-container corrections, retirements, a mixed 100,000-container scenario, idempotent reruns, and exhaustive transition groups.

## State and persistence behavior
Recon state is real RocksDB-backed container manager state from the base fixture. SCM state is represented through mocked count/list/batch RPCs. Sync mutates container records by adding absent containers, applying lifecycle events to stale containers, and retiring containers present in SCM's deleted list. Null pipelines are intentionally accepted for non-live or cleaned-up SCM cases.

## Dependencies and integration points
The suite tests the integration of SCM service-provider pagination, Recon container lifecycle state machine, container DB persistence, sync metrics, and batch-size configuration. It also validates behavior expected by `ReconStorageContainerManagerFacade.triggerSCMContainerSync`.

## Risks and edge cases
Risks include off-by-one pagination cursors, non-atomic SCM count/list races, silent skipping when SCM returns null pipelines, accidental downgrades from CLOSED to OPEN/QUASI_CLOSED, partial sync reporting, and large-batch performance. The `@Timeout(120)` signal means several tests are intentionally heavy.

## Test signals
Signals are final container counts by state, exact lifecycle states for specific IDs, successful sync return values, partial/error-tolerant return behavior, Mockito call counts for pagination and info lookup, idempotent second sync counts, and 100,000-container state distributions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconSCMContainerSyncIntegration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconStorageContainerManagerFacade.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconStorageContainerManagerFacade.java

## Purpose
Tests `ReconStorageContainerManagerFacade` snapshot DB replacement and container sync metric/status handling. It verifies SCM DB snapshots are opened from Recon's canonical path and that manual container sync reports success/failure duration consistently.

## Important APIs, types, and functions
- Uses `ReconTestInjector` to build a real Recon facade with Recon SQL DB, OM metadata manager, container DB, and mocked service providers.
- Exercises `updateReconSCMDBWithNewSnapshot`, `getScmDBStore`, and `triggerSCMContainerSync`.
- Uses `DBCheckpoint`, `DBStoreBuilder`, `ReconSCMDBDefinition.RECON_SCM_DB_NAME`, `ReconScmContainerSyncMetrics`, and reflection to replace/read private `containerSyncHelper` and `containerSyncMetrics`.

## Control flow
The snapshot test creates a temporary SCM checkpoint DB under a non-canonical snapshot name, mocks `getSCMDBSnapshot`, calls `updateReconSCMDBWithNewSnapshot`, and checks the facade opened the DB at the canonical `recon-scm.db` path, moved data there, and removed the original checkpoint directory. Three sync tests replace the internal helper with a mock returning true, false, or throwing; they call `triggerSCMContainerSync` and assert status/duration fields and exception propagation.

## State and persistence behavior
The facade manages a real SCM RocksDB store location. Snapshot import should relocate/open the DB at the canonical Recon SCM DB path rather than leaving Recon pointed at a transient checkpoint directory. Metrics persist only in the registered metrics object and are unregistered after each test.

## Dependencies and integration points
This file integrates dependency injection, Recon OM metadata fixture, storage-container service provider, SCM DB snapshots, and container sync metrics. It is a facade-level guard over lower-level sync helper behavior.

## Risks and edge cases
Private-field reflection makes the tests sensitive to implementation field names. Snapshot path assertions depend on canonical file behavior. Metric unregister cleanup is required to avoid metric registry collisions across tests.

## Test signals
Signals include canonical DB location equality, existence/removal of expected directories, boolean return for sync success/failure, failure status on false or exception, duration updated from sentinel `-1`, and original exception object propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconStorageContainerManagerFacade.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconStorageContainerSyncHelper.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconStorageContainerSyncHelper.java

## Purpose
Focused mock-based unit tests for `ReconStorageContainerSyncHelper`. It verifies metrics, missing-container add behavior, pagination batching, skip behavior for existing containers, and benign handling of empty SCM lists.

## Important APIs, types, and functions
- Instantiates `ReconStorageContainerSyncHelper` with mocked `StorageContainerServiceProvider` and `ReconContainerManager`.
- Uses `ReconScmContainerSyncMetrics`, `getContainerCount`, `getContainerStateCount`, `getListOfContainerIDs`, `getExistContainerWithPipelinesInBatch`, `addNewContainer`, `updateContainerState`, and `getContainer`.
- Configures `OZONE_RECON_SCM_CONTAINER_ID_BATCH_SIZE` for pagination.

## Control flow
Setup creates metrics and a helper with default config; teardown unregisters metrics. One test feeds SCM and Recon counts for all tracked states and verifies drift and duration metrics. Missing-container tests stub CLOSED ID pages and batch SCM fetches, then verify only absent containers are added, including multi-page behavior with batch fetch for only missing IDs. Existing-container and zero-count tests verify no add/update/fetch occurs. Empty-list handling verifies an SCM count/list race returns true without mutations.

## State and persistence behavior
All state is mocked except metrics. The helper's observable effects are calls to the mocked container manager and metrics updates. No RocksDB persistence is exercised here; that is covered by the integration suite.

## Dependencies and integration points
This file isolates SCM RPC pagination, Recon container manager mutation calls, and sync metrics. It complements `TestReconSCMContainerSyncIntegration` by pinning call-level behavior.

## Risks and edge cases
SCM count/list operations are not atomic, so empty pages must not always be treated as fatal. Batch fetch should include only missing IDs to avoid unnecessary RPC and duplicate additions. Metrics must record drift before sync mutations.

## Test signals
Signals are metric drift values/durations, boolean sync results, exact `addNewContainer` calls, no update/add calls in skip paths, no batch fetch for existing containers, and expected paginated `getListOfContainerIDs` invocations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconStorageContainerSyncHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestKeyPrefixContainerCodec.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestKeyPrefixContainerCodec.java

## Purpose
Tests binary encoding for `KeyPrefixContainerCodec`, which persists key-prefix/version/container-id composite keys used by Recon container metadata indexes.

## Important APIs, types, and functions
- Uses singleton `KeyPrefixContainerCodec.get()` as a `Codec<KeyPrefixContainer>`.
- Exercises `toCodecBuffer`, `fromCodecBuffer`, `toPersistedFormat`, `fromPersistedFormat`, `supportCodecBuffer`, and `getTypeClass`.
- Uses `CodecBuffer.Allocator.getHeap`, `KeyPrefixContainer.get` overloads, and `LONG_SERIALIZED_SIZE`.

## Control flow
`testKeyPrefixWithDelimiter` runs multiple prefixes, including underscores and an empty string, through `runTest`. For each case it creates full, key-plus-version, and key-only objects, encodes them to buffers, verifies full decode, verifies shorter buffers are prefixes of the full buffer, compares codec-buffer bytes with persisted-format bytes, and checks expected prefix lengths. Separate tests assert codec-buffer support and type class.

## State and persistence behavior
No external DB is used, but byte layout is persistence-critical. The encoded format must support prefix scans: key-only and key-plus-version encodings must be byte prefixes of the full key/version/container encoding.

## Dependencies and integration points
The codec feeds RocksDB table keys for Recon APIs that map key prefixes to containers and containers to key prefixes. Prefix compatibility is required for range scans by key prefix and version.

## Risks and edge cases
Delimiter-like underscores and empty prefixes guard against ambiguous string parsing. Any change in long serialization size, byte order, or concatenation order can break persisted DB compatibility and prefix scans.

## Test signals
Signals are round-trip equality from buffer and persisted bytes, `startsWith` prefix checks, exact byte-array equality, prefix-length calculations, codec-buffer support, and type-class equality.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestKeyPrefixContainerCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestOzoneManagerServiceProviderImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestOzoneManagerServiceProviderImpl.java

## Purpose
Comprehensive tests for `OzoneManagerServiceProviderImpl`, covering OM snapshot download/import, failure error tracking, repeated snapshot replacement, raw snapshot extraction, delta update fetch/apply, delta limits, task status updates, metrics, and fallback to full snapshot on missing transaction sequence numbers.

## Important APIs, types, and functions
- Uses `OzoneManagerServiceProviderImpl`, `ReconOMMetadataManager`, `OzoneManagerProtocol.getDBUpdates`, `ReconTaskController`, `ReconTaskStatusUpdaterManager`, `ReconContext`, and `OzoneManagerSyncMetrics`.
- Uses OM test utilities to create OM DBs, write sample keys, create checkpoints/tar files, and build Recon OM metadata managers.
- Exercises `updateReconOmDBWithNewSnapshot`, `getOzoneManagerDBSnapshot`, `syncDataFromOM`, `getCurrentOMDBSequenceNumber`, and `getOMMetadataManagerInstance`.
- Uses RocksDB transaction log iteration (`ManagedTransactionLogIterator`, `BatchResult`, `WriteBatch`) to build `DBUpdates`.

## Control flow
Snapshot tests create source OM metadata, tar a checkpoint, mock Recon HTTP download utilities, start the tar extractor, update Recon's OM DB, and verify key visibility plus ReconContext error add/remove behavior. A repeated snapshot test imports two snapshots into the same manager. `testGetOzoneManagerDBSnapshot` validates untar output for a generic two-file checkpoint. Delta tests collect RocksDB write batches from a source OM DB and mock OM RPC updates; one applies all four updates, while the limit test applies only three one-update requests. `syncDataFromOM` tests cover empty DB full-snapshot trigger, non-empty DB delta consumption, and `SequenceNumberNotFoundException` fallback to full snapshot.

## State and persistence behavior
The suite uses real RocksDB OM metadata stores and Recon OM metadata stores under temp directories. Snapshot import replaces Recon's metadata state. Delta update application advances the Recon OM DB sequence number and writes volume, bucket, and key changes into Recon's RocksDB. ReconContext stores snapshot failure error codes. Metrics count snapshot requests and delta update request sizes.

## Dependencies and integration points
This file spans HTTP snapshot retrieval, tar extraction, OM metadata checkpoint format, OM DB update RPCs, RocksDB WAL batches, Recon task reinitialization/event consumption, task status updater naming, and metrics.

## Risks and edge cases
The tests are sensitive to OM write batch counts and sequence-number semantics. Mocked `ReconUtils` must call real untar behavior while faking HTTP. The limit test assumes exactly four OM operations from the fixture. Full-snapshot fallback must happen both for empty Recon DB and for `SequenceNumberNotFoundException`.

## Test signals
Signals include key table null/non-null checks, thrown runtime cause on HTTP failure, ReconContext error membership, extracted file count, current sequence-number deltas, key existence/non-existence after limited updates, metrics averages/counters, task status updater names for snapshot and delta tasks, queued reinitialization events, and task controller event consumption.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestOzoneManagerServiceProviderImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestReconContainerMetadataManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestReconContainerMetadataManagerImpl.java

## Purpose
Tests `ReconContainerMetadataManagerImpl`, the RocksDB-backed manager for container-to-key-prefix mappings, key-prefix-to-container mappings, per-container key counts, and total container count.

## Important APIs, types, and functions
- Uses `ReconTestInjector` with Recon SQL DB, container DB, and Recon OM metadata fixture to obtain `ReconContainerMetadataManager`.
- Exercises `reinitWithNewContainerDataFromOm`, `batchStoreContainerKeyMapping`, `batchStoreContainerKeyCounts`, `commitBatchOperation`, `getCountForContainerKeyPrefix`, `getKeyPrefixesForContainer`, `getContainerForKeyPrefixes`, `getContainers`, `batchDeleteContainerMapping`, `getKeyContainerTable`, `storeContainerCount`, `getCountForContainers`, `incrementContainerCountBy`, and `doesContainerExists`.
- Uses `RDBBatchOperation`, `ContainerKeyPrefix`, `KeyPrefixContainer`, and `ContainerMetadata`.

## Control flow
The static setup creates a shared manager; `@BeforeEach` resets container data. Helper `populateKeysInContainers` writes mappings for two containers. Tests cover reinitialization replacing old mappings with a provided map, batch insertion and counts, per-container key-count overwrites, existence checks, prefix-count lookup, container-to-prefix scans, scans after a previous key prefix, reverse key-prefix-to-container scans, container pagination with previous-container cursor and limit, deletion of one mapping from both directions, and total container count store/increment behavior.

## State and persistence behavior
State lives in the Recon container RocksDB. The manager maintains at least two correlated indexes: container-key-prefix to count and key-prefix-container to count. Batch operations are committed atomically via `RDBBatchOperation`. Reinitialization clears old container metadata and loads new counts, while delete removes both forward and reverse mapping entries.

## Dependencies and integration points
The manager supports Recon APIs that answer "which keys are in a container" and "which containers contain this key prefix." It depends on codec prefix ordering, RocksDB batch semantics, Recon OM metadata manager initialization, and `ReconDBProvider`.

## Risks and edge cases
Bidirectional index consistency is critical; deleting or reinitializing only one side would create stale API results. Cursor semantics for previous container and key prefix are easy to get wrong. Static shared manager setup requires per-test clearing to prevent data leakage.

## Test signals
Signals are exact counts for mappings and containers, zero values for missing prefixes/containers, map sizes and contents for scans, null reverse-table entry after deletion, total container count overwrites/increments, and empty results for invalid cursor/prefix cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestReconContainerMetadataManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestReconDBProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestReconDBProvider.java

## Purpose
Minimal dependency-injection test for `ReconDBProvider`, the provider for Recon's container-key metadata DB store.

## Important APIs, types, and functions
- Creates a Guice injector with `OzoneConfiguration` bound to a temp `OZONE_RECON_DB_DIR`.
- Binds `ReconDBProvider` as a singleton and calls `getDbStore`.

## Control flow
`@BeforeEach` builds the injector and temp DB configuration. `testGet` obtains the provider instance and asserts the DB store is non-null.

## State and persistence behavior
The provider opens or creates a Recon DB store under the configured temp path. The test does not write records; it only verifies construction and store availability.

## Dependencies and integration points
This provider underlies Recon container metadata managers and other SPI implementations that need the Recon DB store.

## Risks and edge cases
Coverage is intentionally narrow. It does not assert DB path, schema/table creation, close behavior, singleton reuse, or failure modes for invalid directories.

## Test signals
The only signal is a non-null `DBStore` from `ReconDBProvider.getDbStore()`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestReconDBProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestReconNamespaceSummaryManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestReconNamespaceSummaryManagerImpl.java

## Purpose
Tests `ReconNamespaceSummaryManagerImpl`, which stores and retrieves namespace summary records used by Recon namespace/file-system summary APIs.

## Important APIs, types, and functions
- Uses `ReconTestInjector` with Recon SQL DB, Recon OM metadata manager, and container DB to obtain `ReconNamespaceSummaryManagerImpl`.
- Exercises `batchStoreNSSummaries`, `commitBatchOperation`, `getNSSummary`, `getNSSummaryTable`, and `clearNSSummaryTable`.
- Uses `RDBBatchOperation` and `NSSummary` fields for file count, file size, bucket distribution, child directories, directory name, and parent id.

## Control flow
Static setup creates the manager and a 40-bucket test array. `@BeforeEach` clears the namespace summary table. `testStoreAndGet` batch-writes three namespace summaries, reads each by object id, checks counts/sizes/names/child dirs, and verifies a missing id returns null. `testInitNSSummaryTable` writes the same data, checks the table is non-empty, clears it, and checks it is empty.

## State and persistence behavior
Namespace summaries are persisted in Recon's container DB as RocksDB records keyed by namespace object id. Batch commit writes multiple summaries atomically. Clearing the table removes all summaries between tests.

## Dependencies and integration points
The manager supports Recon namespace summary tasks and APIs. It depends on Recon DB setup, OM metadata manager fixture, `NSSummary` serialization, and RocksDB batch operations.

## Risks and edge cases
The test covers only three records and table clearing, not updates, parent traversal, bucket histogram correctness beyond round-trip, or concurrent task updates. Static manager reuse requires strict clearing to avoid cross-test contamination.

## Test signals
Signals are exact retrieved file counts, total sizes, directory names, child-dir set size, null for missing id, non-empty table after batch write, and empty table after clear.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestReconNamespaceSummaryManagerImpl.java -->
