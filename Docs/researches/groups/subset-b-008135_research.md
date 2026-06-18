# subset-b-008135 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestEndpoints.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestEndpoints.java

## Purpose
Broad Recon API endpoint test suite covering node, pipeline, Prometheus metrics proxy, cluster state, utilization histograms, volume listing, bucket listing, datanode removal, and decommission status APIs. It builds an in-process Recon test injector backed by temporary OM metadata, Recon SQL state, container DB state, and a Recon SCM facade, then asserts that endpoint DTOs reflect seeded SCM/OM/task state.

## Important APIs, types, and functions
- Endpoints under test: `NodeEndpoint`, `PipelineEndpoint`, `ClusterStateEndpoint`, `UtilizationEndpoint`, `MetricsProxyEndpoint`, `VolumeEndpoint`, and `BucketEndpoint`.
- Fixture construction uses `ReconTestInjector`, `ReconOMMetadataManager`, `ReconStorageContainerManagerFacade`, `ReconPipelineManager`, `ReconFileMetadataManager`, `ReconGlobalStatsManager`, `ContainerHealthSchemaManager`, and jOOQ `DSLContext`.
- Task integrations include `FileSizeCountTaskFSO`, `FileSizeCountTaskOBS`, `ContainerSizeCountTask`, and `OmTableInsightTask`.
- Helper assertions `testDatanodeResponse`, `testVolumeResponse`, and `testBucketResponse` validate endpoint DTO fields, ACL grouping, storage reports, layout versions, quotas, and bucket layouts.
- `waitAndCheckConditionAfterHeartbeat` sends a synthetic SCM heartbeat with container report data and waits until asynchronous event processing has materialized container counts.

## Control flow
`initializeInjector` is run once per test instance and creates random datanodes with stable host/IP values, a one-node pipeline, container-with-pipeline lookup mocks, a mocked Prometheus HTTP call, Guice bindings, endpoint instances, utilization tasks, and a pipeline entry in `ReconPipelineManager`. Each `setUp` registers three datanodes with storage, node, container, and pipeline reports, processes the event queue, adds a second sample volume plus two buckets with ACL/quota/storage metadata, writes three live keys and deleted-key/deleted-directory records, then truncates global stats so each test controls OM table insight results.

Individual tests read endpoint responses and assert exact DTO behavior: datanodes and operational-state changes; pipeline metadata and later container count convergence; Prometheus response streaming; cluster state before and after OM table insight reprocess; file/container size histogram writes and query filters; volume/bucket pagination; explicit datanode removal failure buckets; and decommission status maps assembled from mocked SCM node queries, container-on-decommissioning-node maps, and JSON metrics.

## State and persistence behavior
The suite persists OM metadata in temporary RocksDB-backed managers, Recon global stats in SQL, file-size counts in Recon file metadata storage, container size counts through the SCM facade DAO, and SCM node/pipeline/container state in the in-process Recon SCM facade. The tests deliberately mix synchronous table writes with asynchronous SCM heartbeat/event processing, so some assertions use wait loops after sending a heartbeat. Global stats are truncated between tests because `ClusterStateEndpoint` reads counts from the SQL-backed global stats manager after `OmTableInsightTask` reprocesses OM tables.

## Dependencies and integration points
This file is a high-coverage integration point between Recon REST resources, OM metadata tables, Recon SQL/jOOQ schema definitions, Recon SCM facade components, SCM datanode protocol registration/heartbeat handling, Prometheus proxy plumbing, and task-generated utilization/global-stat data. It also exercises ACL aggregation into API metadata and decommission status translation from SCM protocol and metrics JSON into Recon response maps.

## Risks and edge cases
The suite is sensitive to asynchronous event timing for heartbeat/container processing, exact storage arithmetic, and DTO ordering assumptions in pagination tests. It uses broad in-process state that can leak across tests if setup guards or table truncation change. The mocked Prometheus and SCM decommission JSON strings are narrow and may miss malformed or partially populated production responses. Removal tests currently assert failure paths for decommissioned, non-DEAD, and unknown nodes; they do not prove a successful physical removal of a DEAD node.

## Test signals
Strong signals include exact datanode storage totals, layout versions, operational-state propagation, pipeline leader/count fields, byte-for-byte metrics proxy output, cluster state counts before and after task reprocess, RocksDB histogram bins, endpoint filter results, volume/bucket ACL/quota/layout DTOs, and decommission response container/metric buckets. Failures usually identify a contract change in endpoint DTOs, Recon task output, or SCM/OM state projection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestEndpoints.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestExportJobManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestExportJobManager.java

## Purpose
Unit-level coverage for `ExportJobManager`, the Recon component that asynchronously exports unhealthy-container query results into tarred CSV downloads. It verifies submission, worker completion, chunking, duplicate-state rejection, retry after failure, queue-cap enforcement, cancellation, listing, startup cleanup, and export filename format without starting Derby or Guice.

## Important APIs, types, and functions
- Main APIs under test are `ExportJobManager.submitJob`, `getJob`, `getAllJobs`, `getQueuePosition`, `cancelJob`, and `shutdown`.
- Uses mocked `ContainerHealthSchemaManager.getUnhealthyContainersCount` and `getUnhealthyContainersCursor` as the only DB dependency.
- Uses `ExportJob` and `ExportJob.JobStatus` to observe `RUNNING`, `COMPLETED`, and `FAILED` state.
- Helper cursors are `finiteCursor(recordCount)` for deterministic rows and `blockingCursor(CountDownLatch)` for suspending worker execution.
- `listTarEntryNames` reads generated tar contents with `TarArchiveInputStream` to validate CSV part names.

## Control flow
Each test creates a manager pointed at a temporary export directory with a configurable queue size and max download count. Submission tests stub counts/cursors, submit a state such as `MISSING`, wait for asynchronous status convergence, and inspect `ExportJob` metadata and tar files. Queue and duplicate tests hold the worker inside a blocking cursor to observe the running job and queued jobs. Cancellation tests remove running and completed jobs. Startup cleanup shuts down the manager, creates stale tar/job-directory artifacts, then constructs a new manager and asserts only export leftovers were removed.

## State and persistence behavior
Runtime state is held in the manager's job tracker, queue, single worker thread, and temporary export directory. Completed jobs persist a `.tar` file and metadata path until canceled. Running jobs use a per-job working directory that should be removed on cancellation. Failed jobs should release the unhealthy-container state so a later submit for the same state can proceed. Startup cleanup removes stale tar files and job directories while preserving unrelated files.

## Dependencies and integration points
The test isolates `ExportJobManager` from the database by mocking `ContainerHealthSchemaManager`, but still exercises real file creation, tar assembly, CSV chunk naming, queue logic, worker-thread transitions, Ozone configuration keys, and cleanup logic. It depends on jOOQ record classes for fake unhealthy-container rows and Apache Commons Compress for tar inspection.

## Risks and edge cases
The largest export test synthesizes 1,000,001 rows to cross CSV part boundaries and can be slower than normal unit tests. Async polling can flake if worker timing or status transitions change. The cursor mocks only populate a small subset of unhealthy-container fields, so CSV column additions may need fixture updates. Queue-full behavior depends on the worker pulling the first job before the third submit.

## Test signals
Assertions cover total and estimated record counts, tar existence, exact three-part naming for million-row exports, empty-export completion, duplicate-state exception messages, retry after failed worker execution, queue positions, cancellation cleanup, all-job listing, startup cleanup, and `export_missing_<timestamp>.tar` filename shape.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestExportJobManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestFeaturesEndPoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestFeaturesEndPoint.java

## Purpose
Focused unit/integration test for `FeaturesEndpoint.getDisabledFeatures`, currently centered on whether the Recon heatmap feature appears in the disabled-feature list based on provider class configuration and the heatmap enable flag.

## Important APIs, types, and functions
- Endpoint under test is `FeaturesEndpoint.getDisabledFeatures`.
- Uses `FeatureProvider.initFeatureSupport(OzoneConfiguration)` to refresh static feature availability before each assertion.
- Reads configuration keys `OZONE_RECON_HEATMAP_PROVIDER_KEY` and `OZONE_RECON_HEATMAP_ENABLE_KEY`.
- Builds a minimal `ReconTestInjector` with temporary Recon OM metadata, SQL DB, container DB, SCM facade binding, and storage/OM service provider mocks.

## Control flow
`initializeInjector` creates an `OzoneConfiguration`, temporary OM metadata manager, Recon test injector, and endpoint instance. Tests mutate the same configuration, call `FeatureProvider.initFeatureSupport`, fetch disabled features, cast the response entity to a list of `FeatureProvider.Feature`, and assert whether `FeatureProvider.Feature.HEATMAP` is present or the list is empty.

## State and persistence behavior
The only meaningful state is static feature-support state inside `FeatureProvider`, refreshed from the mutable `OzoneConfiguration`. Temporary OM, SQL, and container DB state exists only to satisfy endpoint injection and is not inspected. Because setup is guarded by `isSetupDone`, the endpoint and configuration are reused within the test instance while each test explicitly reinitializes feature support.

## Dependencies and integration points
The file touches Recon dependency injection, OM metadata test utilities, SCM facade binding, `FeatureProvider` feature detection, and JAX-RS `Response` entities. It verifies the API-level representation of feature gating rather than heatmap provider behavior itself.

## Risks and edge cases
The test depends on static mutable feature state, so missing `initFeatureSupport` calls or parallel test execution could affect isolation. It asserts the first disabled feature is heatmap when disabled; adding other disabled features with earlier ordering may require a less order-sensitive assertion. The valid provider class name is hard-coded to the test heatmap provider implementation.

## Test signals
Signals are simple: empty provider string disables heatmap, valid provider plus enabled flag returns no disabled features, valid provider plus disabled flag includes heatmap, and valid provider plus true flag excludes heatmap.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestFeaturesEndPoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestNSSummaryDiskUsageOrdering.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestNSSummaryDiskUsageOrdering.java

## Purpose
Regression test that `NSSummaryEndpoint.getDiskUsage` returns child subpaths sorted by descending size when the caller requests list-file semantics. It uses a synthetic FSO namespace with multiple volumes, buckets, direct files, and directories of deliberately varied sizes.

## Important APIs, types, and functions
- Endpoint under test is `NSSummaryEndpoint.getDiskUsage(path, true, false, true)`.
- Fixture writes use `writeDirToOm` and `writeKeyToOm` against `ReconOMMetadataManager`.
- Reprocessing uses `NSSummaryTaskWithFSO.reprocessWithFSO` to build namespace summary records.
- `verifyOrdering` copies `DUResponse.getDuData`, sorts the copy by `DUResponse.DiskUsage.getSize` descending, and compares subpath order to the endpoint output.
- Temporary OM setup uses `OmMetadataManagerImpl`, `ReconTestInjector`, and a mocked `ReconStorageContainerManagerFacade`.

## Control flow
`setUp` creates an FSO OM metadata manager, injects Recon services, populates the namespace, and reprocesses summaries. `populateOMDB` creates volumes `volA` and `volB`; buckets `bucketA1`, `bucketA2`, `bucketA3`, and `bucketB1`; three directories per bucket; direct files; and one inner file per directory. Tests call `verifyOrdering` for root, volumes, and buckets. The assertion compares only ordering, not exact full size values, because the fixture's size spread is meant to make descending order unambiguous.

## State and persistence behavior
The test persists volume and bucket rows in the OM volume/bucket tables, directory rows in the FSO directory table, key rows in the FSO key table, and computed summaries in Recon namespace summary storage. Bucket `usedBytes` is set to the sum of direct file and directory contents, while each directory total is represented by a child file. There is no real SCM container accounting beyond mocked container and node manager access.

## Dependencies and integration points
This file integrates FSO OM table layout, namespace summary reprocessing, Recon injection, and disk-usage API response ordering. It also depends on positive random object IDs for generated volumes/buckets/directories/files and mocked SCM/node manager availability.

## Risks and edge cases
The test verifies order by subpath equality after sorting a copy; if two siblings have equal sizes, order would be ambiguous, so fixture sizes should remain distinct. It does not validate pagination, recursive size correctness, replica size, or non-FSO layouts. Random object IDs are positive-masked but could still collide in theory, though the probability is negligible.

## Test signals
Signals are ordering assertions for root-level volume children, volume-level bucket children, and bucket-level file/directory children. A failure indicates `getDiskUsage` no longer sorts returned subpaths by descending size when the ordering mode is enabled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestNSSummaryDiskUsageOrdering.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestNSSummaryEndpointWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestNSSummaryEndpointWithFSO.java

## Purpose
Comprehensive REST-level test for `NSSummaryEndpoint` over `FILE_SYSTEM_OPTIMIZED` buckets. It constructs a three-volume namespace with nested directories, files, quotas, file-size bins, standalone-replicated keys, Ratis factor-three keys, and multi-block keys, then validates basic info, disk usage, replicated size, quota usage, file-size distribution, and full-path reconstruction.

## Important APIs, types, and functions
- Endpoint APIs under test include `getBasicInfo`, `getDiskUsage`, `getQuotaUsage`, and `getFileSizeDistribution` through direct endpoint calls and shared `NSSummaryTests` helper assertions.
- FSO fixture writes use `writeDirToOm` and `writeKeyToOm` with parent object IDs, bucket object IDs, volume object IDs, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, and optional replication configs/location groups.
- `NSSummaryTaskWithFSO.reprocessWithFSO` converts OM tables into Recon namespace summaries.
- Replication fixtures use `OmKeyLocationInfoGroup`, `BlockID`, `ContainerReplica`, mocked `ContainerManager.getContainerReplicas`, `StandaloneReplicationConfig`, `RatisReplicationConfig`, and `QuotaUtil.getReplicatedSize`.
- `ReconUtils.constructFullPath` is tested for normal FSO parent traversal and for negative parent IDs that signal rebuild-in-progress.

## Control flow
`setUp` creates an FSO OM metadata manager, binds `NSSummaryEndpoint` with a mocked Recon SCM, populates a base namespace, adds `vol3` with Ratis factor-three keys, overwrites selected keys with multi-block location info, and runs FSO summary reprocessing. Basic-info tests delegate common expectations to `NSSummaryTests`. Disk-usage tests cover root, volume, bucket, directory, key, invalid path, and replica-aware modes. Quota and file-size distribution tests assert expected aggregate values. Path-construction tests build `OmKeyInfo` instances with parent IDs and verify reconstructed paths, including an explicit corrupt/rebuilding summary with parent id `-1`.

## State and persistence behavior
The file persists volumes, buckets, directories, and keys into temporary OM RocksDB tables and persists derived namespace summaries in Recon summary storage. FSO parent-child structure is represented by object IDs, so directory and file parent IDs are central to path lookup and summary propagation. Replica-aware size depends on mocked SCM container replica sets for six container IDs: some under-replicated, some over-replicated, and some with five replicas, plus Ratis factor-three keys under `vol3`. The mocked SCM node manager reports root quota stats used by quota calculations.

## Dependencies and integration points
This test bridges OM FSO key/directory layout, Recon namespace summary task output, `NSSummaryEndpoint` path parsing and entity handlers, quota utilities, SCM container replica lookup, Recon node stats, and shared `NSSummaryTests` contracts. It verifies that endpoint behavior remains layout-aware while exposing the same REST semantics as legacy buckets.

## Risks and edge cases
There is substantial duplicated constant arithmetic; any fixture change must update raw size, replica size, quota, and file-size-bin expectations consistently. The test relies on ordering of `duData().get(0)` for some replica assertions, so sorting changes can break it. Mocked container replica counts may not cover EC or closed-container behavior. The negative-parent tests are important because FSO path reconstruction can otherwise return misleading partial paths while summaries are being rebuilt.

## Test signals
Signals include shared basic-info expectations, exact root/volume/bucket/dir/key DU counts and sizes, `PATH_NOT_FOUND` and `TYPE_NOT_APPLICABLE` statuses, propagated `sizeWithReplica` at every hierarchy level, Ratis factor-three replicated-size checks, quota values and usage, file-size distribution bins, and full-path strings for nested FSO files.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestNSSummaryEndpointWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestNSSummaryEndpointWithLegacy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestNSSummaryEndpointWithLegacy.java

## Purpose
Comprehensive REST-level test for `NSSummaryEndpoint` over `LEGACY` buckets. It mirrors the FSO namespace scenario while using legacy key naming and filesystem-path configuration, validating that basic info, disk usage, replicated size, quota usage, file-size distribution, and full-path construction work for legacy OM tables.

## Important APIs, types, and functions
- Endpoint APIs under test are the same namespace summary surfaces: basic info via shared helpers, `getDiskUsage`, `getQuotaUsage`, and `getFileSizeDistribution`.
- Legacy fixture setup uses `getMockOzoneManagerServiceProvider`, `setConfiguration`, `OZONE_OM_ENABLE_FILESYSTEM_PATHS`, and `NSSummaryTaskWithLegacy.reprocessWithLegacy`.
- Directory writes use legacy-style key names ending in `OM_KEY_PREFIX`, and key writes use full key paths with `BucketLayout.LEGACY` and default parent id behavior.
- Replication tests use `OmKeyLocationInfoGroup`, `BlockID`, mocked container replica sets, `StandaloneReplicationConfig`, `RatisReplicationConfig`, and `QuotaUtil`.
- `ReconUtils.constructFullPath` is tested for legacy keys where parent object ID is not populated and the key name already carries the path.

## Control flow
`setUp` configures OM metadata with filesystem paths enabled, creates Recon services, populates the legacy namespace, adds the `vol3/bucket5` Ratis subtree, overlays multi-block replicated keys, and runs legacy summary reprocessing. Tests then exercise shared basic-info behavior, DU at root/volume/bucket/directory/key levels, invalid paths, replica-aware sizes, quota usage, file-size distributions, legacy full-path construction, and Ratis replication calculations for `vol3`, `bucket5`, and `dir6`.

## State and persistence behavior
Unlike FSO, legacy directory and key hierarchy is primarily encoded in key names such as `dir1/dir2/file2` and directory marker keys ending with the OM key prefix; parent IDs are mostly set to zero/default in fixture writes. Derived namespace summaries are persisted by `NSSummaryTaskWithLegacy`. Replica-aware DU depends on the same mocked six-container replica map as FSO, while factor-three Ratis keys under `vol3` validate replication-config-based size calculations. Quota state is stored on volume and bucket table rows, and mocked SCM root stats provide root capacity/usage values.

## Dependencies and integration points
The test connects legacy OM key-table semantics, filesystem-path configuration, Recon namespace summary task logic, endpoint path parsing, shared summary assertions, SCM replica lookup, and quota/stat utilities. Its parity with the FSO suite is valuable because it protects a common REST contract across two different metadata layouts.

## Risks and edge cases
The fixture has duplicated expected-size arithmetic and must stay aligned with the FSO twin. Legacy path construction is less parent-ID dependent, so it does not cover rebuild-in-progress negative parent behavior the same way FSO does. Some replica assertions depend on the first returned DU child. The mocked SCM replica model covers replica counts but not datanode health, EC keys, or container lifecycle variations.

## Test signals
Signals include layout-specific basic-info expectations for `BucketLayout.LEGACY`, exact DU counts/sizes, invalid-path and non-applicable quota statuses, replica-aware size totals from root down to keys, Ratis factor-three size checks, quota usage at root/volume/bucket levels, file-size-bin counts, and full-path construction directly from legacy key names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestNSSummaryEndpointWithLegacy.java -->
