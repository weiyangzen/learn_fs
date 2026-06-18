# subset-b-008136 Research

Grouped research for the listed Apache Ozone Recon API test files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestNSSummaryEndpointWithOBSAndLegacy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestNSSummaryEndpointWithOBSAndLegacy.java

## Purpose
Tests `NSSummaryEndpoint` against Object Store buckets and Legacy buckets when filesystem paths are disabled. The fixture models two volumes, four buckets, and nine flat keys, then verifies namespace basic info, disk usage, replicated disk usage, quota usage, file-size distribution, and utility path behavior.

## Important APIs, Types, And Functions
Primary APIs under test are `NSSummaryEndpoint.getBasicInfo`, `getDiskUsage`, `getQuotaUsage`, and `getFileSizeDistribution`. The test also covers `EntityHandler.parseRequestPath`, `BucketHandler.getKeyName`, `BucketHandler.buildSubpath`, `OmUtils.normalizePathUptoBucket`, and `ReconUtils.constructFullPath`. It uses `ReconTestInjector`, `ReconOMMetadataManager`, `ReconNamespaceSummaryManager`, `NSSummaryTaskWithOBS`, `NSSummaryTaskWithLegacy`, `OMMetadataManager`, `OmVolumeArgs`, `OmBucketInfo`, `OmKeyInfo`, `OmKeyLocationInfoGroup`, `DUResponse`, `NamespaceSummaryResponse`, `QuotaUsageResponse`, and `FileSizeDistributionResponse`.

## Control Flow
`setUp` creates an OM metadata database with `OZONE_OM_ENABLE_FILESYSTEM_PATHS=false`, injects a mocked Recon SCM, populates OM volume, bucket, and key tables, then reprocesses namespace summaries with both OBS and Legacy tasks. The test cases call endpoint methods at root, volume, bucket, and key paths and compare response types, counts, object metadata, sizes, status codes, and distributions. Additional helper paths insert multi-block keys and mock container replica counts so replicated-size calculations can be validated independently from logical file sizes.

## State And Persistence
State lives in temporary RocksDB-backed OM metadata tables and Recon namespace summary tables created under JUnit `@TempDir`. `populateOMDB` writes volumes, buckets, and flat keys with fixed object IDs, quotas, sizes, and bucket layouts. Multi-block helpers overwrite key table entries with block location groups and depend on a mocked `ContainerManager` returning replica sets for containers 1 through 6. No external cluster state is used.

## Dependencies And Integration Points
This test integrates Recon REST endpoint code with OM metadata table semantics, namespace summary reprocessing tasks, SCM node/container replica lookup, quota utilities, and path normalization helpers. It specifically exercises the boundary where Legacy buckets behave like OBS buckets because filesystem paths are disabled.

## Risks
The assertions rely on hard-coded object IDs, path strings, and sorted response order for disk usage child entries. Replicated-size tests depend on mocked replica counts matching the constants, so changes in `QuotaUtil`, container-replica interpretation, or namespace summary aggregation can break many expectations. The flat-key behavior is sensitive to path normalization around leading, trailing, and repeated slashes.

## Test Signals
Strong signals include root counts of 2 volumes, 4 buckets, and 9 keys; bucket layout reporting for OBS versus Legacy; `PATH_NOT_FOUND` for invalid paths; `TYPE_NOT_APPLICABLE` for key quota usage; per-bin file-size distribution checks; and replicated-size totals for root, volume, bucket, and key paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestNSSummaryEndpointWithOBSAndLegacy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestOmDBInsightEndPoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestOmDBInsightEndPoint.java

## Purpose
Provides broad integration-style coverage for `OMDBInsightEndpoint`. It verifies open-key inspection, deleted-key inspection, deleted-directory inspection, key summaries from global stats, directory-size enrichment from namespace summaries, and `listKeys` filtering and pagination across FSO, OBS, and Legacy bucket layouts.

## Important APIs, Types, And Functions
The main endpoint methods are `getOpenKeyInfo`, `getOpenKeySummary`, `getDeletedKeySummary`, `getDeletedKeyInfo`, `getDeletedDirInfo`, `listKeys`, `getReconGlobalStatsManager`, and `getNsSummaryTable`. Core test types include `KeyInsightInfoResponse`, `ListKeysResponse`, `ReconBasicOmKeyInfo`, `NSSummary`, `GlobalStatsValue`, `RepeatedOmKeyInfo`, `OmKeyInfo`, `OmKeyLocationInfoGroup`, `BucketLayout`, `ReplicationConfig`, `ECReplicationConfig`, and `StandaloneReplicationConfig`.

## Control Flow
`setUp` creates a Recon test injector with SQL DB, OM metadata, container DB, a real `ReconStorageContainerManagerFacade`, and `OMDBInsightEndpoint`. It adds a mock pipeline, writes committed key/block data for container mapping, creates volume and bucket metadata for OBS, FSO, Legacy, and empty buckets, writes directories and keys into open, key, deleted, and deleted-directory tables, then clears and rebuilds namespace summaries with Legacy, OBS, and FSO tasks. Individual tests seed additional table rows or global stats, invoke endpoint methods with limits, previous keys, prefixes, layout toggles, filters, and pagination cursors, and assert response lists, sizes, last keys, and status behavior.

## State And Persistence
State is persisted in temporary Recon SQL tables, OM RocksDB tables, Recon container metadata, Recon global stats, and namespace summary tables. Global stats tests explicitly insert and delete keys such as `openKeyTableCount`, `openFileTableReplicatedDataSize`, and invalid-prefix variants. Deleted directory size tests write `NSSummary` rows keyed by object ID and use `QuotaUtil.getReplicatedSize` to validate replicated totals for RATIS and EC configs.

## Dependencies And Integration Points
The test links OM metadata tables to Recon-specific managers: `ReconContainerMetadataManager` via `ContainerKeyMapperTaskOBS`, `ReconGlobalStatsManager`, `ReconNamespaceSummaryManager`, and `ReconPipelineManager`. It also checks `listKeys` behavior that depends on bucket layout, namespace summary path resolution, replication config filtering, creation-date parsing, size filtering, and RocksDB lexicographic iteration.

## Risks
This file is sensitive to iterator ordering and cursor semantics. Several assertions depend on exact `lastKey` strings, FSO object-ID table keys, and Legacy path ordering. Time-zone handling and date filter parsing are explicit concerns because the fixture imports `TimeZone` and uses fixed formatted date strings. Tests that mix extra ad hoc rows with setup data can be brittle if endpoint defaults, include flags, or table naming conventions change.

## Test Signals
Key signals include rejecting root or volume-level open-key searches with bad request; splitting open-key results into FSO and non-FSO lists; correct totals for replicated and unreplicated sizes; pagination for open, deleted, and list-keys APIs; empty-bucket zero results; valid no-content behavior when include flags exclude all keys; Legacy and FSO list traversal through nested directories; and directory-size totals enriched from namespace summaries.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestOmDBInsightEndPoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestOpenContainerCount.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestOpenContainerCount.java

## Purpose
Tests that `NodeEndpoint.getDatanodes` reports the open-container count for a datanode and that the count decreases as containers move from `OPEN` to `CLOSED`.

## Important APIs, Types, And Functions
The test drives `NodeEndpoint`, `ReconStorageContainerManagerFacade`, Recon datanode protocol registration, heartbeat handling, `ContainerReportsProto`, `PipelineReportsProto`, `ContainerWithPipeline`, `ContainerInfo`, `DatanodesResponse`, and `DatanodeMetadata`. Helpers `initializeInjector`, `closeContainer`, `updateContainerReport`, and `waitAndCheckConditionAfterHeartbeat` build and mutate the SCM-side fixture.

## Control Flow
The injector initializes a Recon OM, two pipelines for one datanode, and ten open containers split across those pipelines. `setUp` registers the datanode with storage, container, and pipeline reports and processes the SCM event queue. The test waits until `NodeEndpoint` observes 10 containers and 2 pipelines, then closes containers one by one, updates mocked `StorageContainerServiceProvider` responses and the container report, re-registers the datanode, processes events, and asserts that `getOpenContainers` decrements each time.

## State And Persistence
Temporary Recon SQL, OM, and container DB state is created through `ReconTestInjector`. Runtime state is primarily SCM in-memory state plus mocked service-provider responses for `getContainerWithPipeline` and `getExistContainerWithPipelinesInBatch`. The mutable `ContainerReportsProto.Builder` and `cpw` list are the local sources of truth for each close transition.

## Dependencies And Integration Points
The test integrates datanode registration, heartbeat/container report processing, Recon pipeline management, SCM container lookup, and the Node REST endpoint. It mocks HTTP calls and Recon node details through `ReconUtils`, but uses the real Recon facade event processing path.

## Risks
The test is asynchronous and uses `LambdaTestUtils.await`, so event queue timing and processing delays are possible flake points. It assumes one datanode and exact container ordering by ID in the report builder. If NodeEndpoint changes container-count semantics to count only reported replicas, only SCM containers, or only pipelines known before report processing, this test will expose the behavior change.

## Test Signals
The main signal is an initial datanode metadata row with 10 containers, 2 pipelines, and 10 open containers followed by a deterministic decrement to zero as each container is marked closed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestOpenContainerCount.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestOpenKeysSearchEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestOpenKeysSearchEndpoint.java

## Purpose
Tests `OMDBInsightEndpoint.getOpenKeyInfo` as a search endpoint for open keys. The fixture emphasizes path-prefix validation, bucket-or-deeper search requirements, FSO directory traversal, OBS and Legacy open-key lookup, result limits, pagination cursors, and empty or missing paths.

## Important APIs, Types, And Functions
The file uses `OMDBInsightEndpoint.getOpenKeyInfo`, `KeyInsightInfoResponse`, `ReconOMMetadataManager`, `ReconNamespaceSummaryManager`, `NSSummaryTaskWithFSO`, and OM metadata helper writers `writeDirToOm`, `writeOpenFileToOm`, and `writeOpenKeyToOm`. Helper methods create volumes, buckets, directories, FSO open files, and non-FSO open keys with generated positive object IDs.

## Control Flow
`setUp` creates OM metadata, a Recon injector, and a namespace summary manager; it populates an FSO hierarchy, OBS bucket keys, Legacy bucket keys, and empty buckets; then it reprocesses FSO namespace summaries. Tests call `getOpenKeyInfo(limit, prevKey, startPrefix, includeFso, includeNonFso)` for root, volume, bucket, directory, nested directory, exact key, missing path, limit-only, bad request, and cursor combinations.

## State And Persistence
All data is written to temporary OM tables. FSO files use object IDs and parent IDs in the open file table, while OBS and Legacy entries use flat open key table keys. Bucket metadata stores layouts and used bytes. Namespace summaries persist parent-child relationships needed to search beneath FSO directories.

## Dependencies And Integration Points
This test exercises endpoint path parsing against OM bucket layouts, FSO namespace summary traversal, open file/open key tables, and pagination state represented by `prevKey` and `lastKey`. It uses Recon SQL and container DB infrastructure through the injector even though the tested behavior is mostly OM metadata search.

## Risks
Search behavior is tightly coupled to normalized path strings and table key ordering. The bad-request contract rejects root and volume-level prefixes, while empty `prevKey` and empty `startPrefix` can still return global results in specific cases. Refactors to prefix validation, pagination cursor format, or FSO summary traversal can affect many assertions.

## Test Signals
Signals include 400 responses for root and volume prefixes, 204 no-content responses for non-existent bucket/directory/key searches, exact counts for FSO bucket and nested directory searches, replicated size equal to three times unreplicated size for RATIS data, limited result counts, and stable `lastKey` values across pages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestOpenKeysSearchEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestPendingDeletionEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestPendingDeletionEndpoint.java

## Purpose
Unit-tests `PendingDeletionEndpoint` dispatch and response behavior for component-specific pending deletion metrics: datanode (`dn`), SCM (`scm`), and OM (`om`).

## Important APIs, Types, And Functions
The key method is `PendingDeletionEndpoint.getPendingDeletionByComponent`. Collaborators are `ReconGlobalMetricsService`, `DataNodeMetricsService`, `StorageContainerLocationProtocol`, `DataNodeMetricsServiceResponse`, `DatanodePendingDeletionMetrics`, `ScmPendingDeletion`, and `HddsProtos.DeletedBlocksTransactionSummary`.

## Control Flow
`setup` builds the endpoint with Mockito mocks. Validation tests send missing, empty, invalid, and whitespace components plus invalid datanode limits. Datanode tests return finished or in-progress `DataNodeMetricsServiceResponse` objects and assert OK versus accepted responses. SCM tests return a deleted-block summary, null, or an exception. OM tests pass through the pending-size map calculated by `ReconGlobalMetricsService`.

## State And Persistence
No persistent state is created. All state is mock return data: datanode pending deletion lists, SCM summary values, and OM pending size maps.

## Dependencies And Integration Points
The endpoint integrates Recon global metrics, datanode metrics collection, and SCM protocol deleted-block summaries behind one REST parameter. The test ensures component names are case-normalized for valid `DN` input but otherwise strictly validated.

## Risks
The whitespace component case currently returns the invalid-component message rather than the missing-component message. SCM exception handling intentionally returns OK with `-1` sentinel values, which clients must distinguish from real metrics. Limit validation only applies to datanode collection.

## Test Signals
Signals include 400 for missing or invalid components, 400 for `dn` limit below 1, 200 for finished datanode and OM metrics, 202 for in-progress datanode metrics, 204 when SCM summary is absent, and sentinel `-1` values when SCM summary retrieval fails.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestPendingDeletionEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestStorageDistributionEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestStorageDistributionEndpoint.java

## Purpose
Tests `StorageDistributionEndpoint` cluster storage distribution and CSV download behavior, including datanode filesystem/Ozone capacity aggregation, namespace usage breakdown, pending deletion metrics, in-progress responses, and missing-metrics failures.

## Important APIs, Types, And Functions
The tested methods are `getStorageDistribution` and `downloadDataNodeStorageDistribution`. Important types are `StorageCapacityDistributionResponse`, `DatanodeStorageReport`, `DataNodeMetricsServiceResponse`, `DatanodePendingDeletionMetrics`, `ReconGlobalMetricsService`, `ReconGlobalStatsManager`, `NSSummaryEndpoint`, `ReconNodeManager`, `SCMNodeMetric`, `SpaceUsageSource.Fixed`, and `DUResponse`.

## Control Flow
`setup` constructs the endpoint with mocked SCM, node manager, global metrics, global stats, namespace summary endpoint, datanode metrics service, and Recon context. `mockStorageDistributionData` creates a configurable number of datanodes, storage stats, pending deletion rows, global pending/open MPU summaries, root disk usage with replicas, and global key counts. Tests then assert the JSON endpoint response, accepted download response when collection is in progress, server error when metrics are missing after a finished status, and streamed CSV content plus attachment filename.

## State And Persistence
There is no durable persistence. The endpoint response is driven by mocked datanode lists, per-node SCM stats, filesystem usage, global metrics maps, namespace root DU response, and global stats rows. CSV output is emitted through a `StreamingOutput` entity and captured into memory.

## Dependencies And Integration Points
The endpoint combines SCM node telemetry, filesystem usage, Recon namespace summary disk usage, global stats counts, pending OM deletion sizes, open key summaries, MPU summaries, datanode pending deletion metrics, and Recon cluster ID for export filenames.

## Risks
The endpoint depends on multiple independent services returning internally consistent metrics. The test highlights a finished-but-empty datanode metrics response as an internal server error. Computed Ozone capacity, used, and remaining values subtract reserved, non-Ozone used, and minimum free space, so changes in those formulas will alter both per-node and global assertions.

## Test Signals
Signals include total Ozone used/free/capacity and committed space multiplied by datanode count, namespace total used from pending plus open plus finalized bytes, expected total key count of 14, exact open-key breakdown values, per-node storage reports, accepted JSON for in-progress collection, text error for missing metrics, and CSV rows containing all expected datanode values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestStorageDistributionEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestTaskStatusService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestTaskStatusService.java

## Purpose
Tests that `TaskStatusService.getTaskStats` returns rows from the Recon task status SQL table without altering key status fields.

## Important APIs, Types, And Functions
The file uses `TaskStatusService`, `AbstractReconSqlDBTest`, Guice child injector binding, `ReconTaskStatusDao`, `ReconTaskStatus`, JAX-RS `Response`, and a parameterized JUnit test over `lastTaskRunStatus` values `0`, `1`, and `-1`.

## Control Flow
`setUp` creates a child injector and binds a new `TaskStatusService` instance. The parameterized test inserts one `ReconTaskStatus` record into the DAO, invokes `getTaskStats`, casts the response entity to a list, and compares task name, last-updated timestamp, last run status, and current-running flag.

## State And Persistence
State is stored in the in-memory/test SQL database provided by `AbstractReconSqlDBTest`. The only persisted row per invocation is a `Dummy_Task` record with current timestamp and the parameterized status value.

## Dependencies And Integration Points
The test validates the service’s integration with generated jOOQ DAO/POJO classes under `org.apache.ozone.recon.schema.generated`. It also confirms Guice injection can provide the service in the Recon SQL test harness.

## Risks
The test does not assert response status code or ordering beyond a single row. It covers status value preservation but not multiple tasks, empty table behavior, or running-task flag variations.

## Test Signals
The signal is successful round-trip retrieval of inserted task status rows for success, failure, and unknown-like numeric task statuses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestTaskStatusService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestTriggerDBSyncEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestTriggerDBSyncEndpoint.java

## Purpose
Tests `TriggerDBSyncEndpoint` for OM DB snapshot sync triggering and SCM DB snapshot sync trigger/status/cancel REST behavior.

## Important APIs, Types, And Functions
The tested endpoint methods are `triggerOMDBSync`, `triggerSCMDBSnapshotSync`, `getSCMDBSnapshotSyncStatus`, and `cancelSCMDBSnapshotSync`. Important collaborators are `OzoneManagerServiceProviderImpl`, `ReconStorageContainerManagerFacade`, `ReconUtils.createTarFile`, `DBCheckpoint`, `ReconTaskStatusUpdaterManager`, `ReconTaskStatusUpdater`, `ScmDbSnapshotTriggerResponse`, `ScmDbSnapshotStatusResponse`, `ScmDbSnapshotCancelResponse`, `ScmDbSnapshotSyncStatus`, and `ScmDbSnapshotSyncPhase`.

## Control Flow
`setUp` configures temporary Recon and OM snapshot directories, initializes OM metadata, creates a checkpoint tarball, mocks HTTP snapshot download and OM DB updates, starts an `OzoneManagerServiceProviderImpl`, and injects `TriggerDBSyncEndpoint`. The OM test calls `triggerOMDBSync` and expects a 200 `true` response. SCM tests instantiate the endpoint with mocked OM provider and Recon SCM facade and assert accepted, conflict, status, and cancel mappings from facade responses to HTTP responses.

## State And Persistence
Temporary local database directories, OM checkpoints, a tar snapshot file, and Recon SQL DB state are created. The service provider is started and uses mocked task status updater plumbing. SCM snapshot state is not persisted in these tests; it is represented by mocked facade response objects.

## Dependencies And Integration Points
The OM path integrates snapshot download, checkpoint packaging, OM protocol DB update polling, Recon context, task status updater management, and Guice injection. The SCM path checks REST translation of facade-level snapshot sync lifecycle states.

## Risks
The OM fixture opens an input stream from the tar file while stubbing `HttpURLConnection.getInputStream`, so stream lifetime and mock behavior are important. The test does not cover failed OM sync or SCM cancel rejection, but it anchors the key HTTP status mapping: accepted sync uses 202 and already-running sync uses 409.

## Test Signals
Signals include OM trigger returning status 200 with `true`, SCM trigger accepted returning 202 with `IN_PROGRESS`, SCM trigger conflict returning 409 with `accepted=false`, status reporting phase `DOWNLOADING_CHECKPOINT` and cancel allowance, and cancel returning 200 with `CANCELLED` status and phase.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestTriggerDBSyncEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/filters/TestAdminFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/filters/TestAdminFilter.java

## Purpose
Tests Recon admin access policy. It verifies that REST endpoint classes are annotated with `@AdminOnly` unless explicitly allowlisted as non-admin, and that `ReconAdminFilter` permits or denies requests based on Ozone and Recon admin user/group configuration.

## Important APIs, Types, And Functions
The file covers `ReconAdminFilter.doFilter`, `AdminOnly`, `ReconServer.isAdmin`, `OzoneAdmins`, `OzoneConfiguration`, `OzoneConfigKeys`, `ReconConfigKeys`, `UserGroupInformation`, servlet `FilterChain`, `HttpServletRequest`, and `HttpServletResponse`. Reflection uses `Reflections`, `TypeAnnotationsScanner`, and `SubTypesScanner` to discover `@Path` endpoints.

## Control Flow
`testAdminOnlyEndpoints` scans `org.apache.hadoop.ozone.recon` for JAX-RS `@Path` classes, defines a non-admin allowlist, asserts those classes are not annotated, and asserts every other endpoint is annotated `@AdminOnly`. The remaining tests create configurations for Ozone admins, Recon admins, combined admins, no configured admins, starter-user auto-admin behavior, and starter user plus configured admins. `testAdminFilterWithPrincipal` mocks request principal, response, and filter chain, runs the filter, and verifies chain continuation or HTTP 403.

## State And Persistence
No persistent state is written. The only mutable process state is `UserGroupInformation.createUserForTesting` for group membership scenarios, reset in `finally` blocks. Mock `ReconServer` admin checks are implemented from config-derived `OzoneAdmins`.

## Dependencies And Integration Points
This test ties endpoint annotation policy to runtime authorization. It integrates Hadoop security configuration keys, Recon-specific admin config, servlet filter behavior, and package-level endpoint discovery. The allowlist includes cluster/node/status-style read-only endpoints such as `UtilizationEndpoint`, `ClusterStateEndpoint`, `NodeEndpoint`, `PipelineEndpoint`, `MetricsProxyEndpoint`, `ChatbotEndpoint`, and `TaskStatusService`.

## Risks
The reflection-based policy test can fail when a new endpoint is added without a deliberate admin decision, which is intentional. The allowlist must be kept small and reviewed because adding an endpoint there makes it public. Starter-user auto-admin behavior means an otherwise empty admin config still permits the Recon process user.

## Test Signals
Signals include non-admin endpoints being present and unannotated, all other endpoints requiring `@AdminOnly`, configured Ozone or Recon admin users passing, wildcard admins passing, configured admin groups passing, rejected users receiving 403, and the current user being accepted as starter admin.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/filters/TestAdminFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/package-info.java

## Purpose
Provides package-level documentation for the Recon API test package, stating that classes in `org.apache.hadoop.ozone.recon.api` test Recon’s REST API layer.

## Important APIs, Types, And Functions
The file contains only a Javadoc package comment and the `package org.apache.hadoop.ozone.recon.api;` declaration. There are no classes, methods, or executable tests.

## Control Flow
No runtime control flow exists. The compiler associates the Javadoc with the test package.

## State And Persistence
No state is read or written.

## Dependencies And Integration Points
The file integrates with Java package documentation and generated Javadocs for the Recon API test package.

## Risks
The only maintenance risk is that the package description is broad and may become less informative as test coverage expands.

## Test Signals
There are no direct test signals. Successful compilation confirms the package declaration is valid.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/types/TestExportJob.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/types/TestExportJob.java

## Purpose
Unit-tests the `ExportJob` POJO’s small business rules: download reservation limits, remaining download count, file path to file name derivation, null file path handling, and initial status defaults.

## Important APIs, Types, And Functions
The tests call `ExportJob.isDownloadAllowed`, `tryReserveDownload`, `getDownloadCount`, `getMaxDownloads`, `getDownloadsRemaining`, `setFilePath`, `getFilePath`, `getFileName`, `getStatus`, `getSubmittedAt`, `getEstimatedTotal`, and `getTotalRecords`. Assertions use AssertJ.

## Control Flow
Each test creates a new `ExportJob("job-1", "MISSING", maxDownloads)` and exercises one behavior. Download tests reserve downloads until the limit is reached and confirm further reservations return false. File path tests set a tar filename and then null. Initial status verifies constructor defaults.

## State And Persistence
State is entirely in-memory within an `ExportJob` instance. The download count increments only through successful `tryReserveDownload` calls and never persists externally.

## Dependencies And Integration Points
This POJO likely backs export job APIs or managers that expose downloadable generated files. The test anchors assumptions those callers depend on: queued default state, positive submission timestamp, unknown estimated total as `-1`, zero records initially, and no negative remaining download count.

## Risks
The test does not cover concurrent reservations, filesystem paths with directories, or status transitions beyond the constructor default. If `ExportJob` becomes shared across threads, `tryReserveDownload` atomicity would need additional coverage.

## Test Signals
Signals include initial downloads remaining equal to max, reservation decrementing remaining count, denial at limit, remaining count staying at zero after repeated failed reservations, file name mirroring file path for simple filenames, null path clearing file name, and initial status `QUEUED`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/types/TestExportJob.java -->
