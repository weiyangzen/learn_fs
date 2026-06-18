# subset-b-008069 Ozone Recon and S3 integration-test research

This grouped report covers the requested Apache Ozone Recon and S3 integration-test files. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconContainerHealthSummaryEndToEnd.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconContainerHealthSummaryEndToEnd.java

## Purpose

This is a comprehensive end-to-end Recon integration test for container state summaries and unhealthy-container summaries. It validates that Recon and SCM agree on lifecycle-state counts after explicit synchronization, and that Recon's `UNHEALTHY_CONTAINERS` Derby records match SCM ReplicationManager classification for induced `UNDER_REPLICATED`, `OVER_REPLICATED`, `MISSING`, and `EMPTY_MISSING` scenarios. It also documents the important boundary where CLOSED empty missing containers are classified as `EMPTY` and intentionally are not persisted as unhealthy records.

## Important APIs, types, and functions

The class drives `MiniOzoneCluster`, `ReconService`, `ReconStorageContainerManagerFacade`, `ReconContainerManager`, `ContainerManager`, `ReplicationManagerReport`, `ContainerHealthSchemaManager`, `ContainerInfo`, `ContainerReplica`, `Pipeline`, `XceiverClientManager`, and `ContainerProtocolCalls`. Test entry points are `testContainerStateSummaryMatchesBetweenSCMAndRecon()`, `testContainerHealthSummaryMatchesBetweenSCMAndRecon()`, and `testComprehensiveSummaryReport()`. Scenario helpers include `setupStateSummaryScenario()`, `setupHealthSummaryScenario()`, `setupUnderReplicatedContainers()`, `setupOverReplicatedContainers()`, `setupMissingContainers()`, `setupEmptyMissingContainers()`, `setupEmptyOnlyContainers()`, `syncAndWaitForReconContainers()`, and `backfillMissingContainersFromScm()`.

## Control flow, state, and persistence

Each test starts a 3-datanode mini cluster with Recon, long full-container-report intervals, delayed background SCM container sync, short missing-container task intervals, and slow SCM replication remediation. The state-summary path allocates containers in SCM, syncs them into Recon, then mutates both SCM and Recon container managers through lifecycle events so counts can be compared state by state. The health-summary path builds targeted container states by creating real containers on pipelines, waiting for replica reports, closing containers in both managers, deleting physical replicas, injecting phantom replicas, mutating `numberOfKeys`, or leaving containers never created on datanodes. It then runs SCM and Recon ReplicationManagers explicitly and queries Recon's unhealthy schema manager.

## Dependencies and integration points

The test integrates Recon SCM sync, SCM container lifecycle state machines, datanode container reports, Recon's in-memory container manager, SCM and Recon ReplicationManager health-check chains, and the Derby-backed unhealthy-container schema. It depends on event queues being drained and on direct manager mutations being visible to later health scans. `LambdaTestUtils.await()` guards asynchronous replica propagation, and custom logging helpers emit report-like summaries.

## Risks and test signals

This file intentionally manipulates internal metadata and physical datanode container files, so race control is the main risk. The long FCR interval prevents removed replicas from being reintroduced; remediation intervals prevent SCM from healing states before assertions; and manual event-queue drains reduce timing windows. The most important behavioral signal is the distinction between `MISSING` and `EMPTY_MISSING`: Recon refines missing empty CLOSING containers into `EMPTY_MISSING`, while CLOSED 0-key/0-replica containers remain `EMPTY` and are not stored in `UNHEALTHY_CONTAINERS`. Failure signals include replica counts not converging, Recon missing synced containers, mismatch between SCM and Recon lifecycle counts, or stale unhealthy rows after recovery.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconContainerHealthSummaryEndToEnd.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconEndpointUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconEndpointUtil.java

## Purpose

This utility class centralizes HTTP access to Recon endpoints for integration tests. It builds the correct Recon web base URL from Ozone configuration, triggers the OM DB sync endpoint, fetches unhealthy-container JSON, and normalizes HTTP/HTTPS address handling.

## Important APIs, types, and functions

The main methods are `triggerReconDbSyncWithOm()`, `getUnhealthyContainersFromRecon()`, `makeHttpCall()`, `getReconWebAddress()`, `getHostOnly()`, `getPort()`, and `isHTTPSEnabled()`. It uses `URLConnectionFactory`, `HttpURLConnection`, Jackson `ObjectMapper`, `UnhealthyContainersResponse`, and Recon configuration keys for RPC, HTTP, and HTTPS addresses.

## Control flow, state, and persistence

The class is stateless. `triggerReconDbSyncWithOm()` calls `/api/v1/triggerdbsync/om` and logs failures if the response is not `true`. `getUnhealthyContainersFromRecon()` calls `/api/v1/containers/unhealthy/{state}` and deserializes the response body. `makeHttpCall()` opens a URL connection, optionally with SPNEGO when HTTPS-only is configured, returns payloads for HTTP 200/201, and returns null on initialization or refused-connection cases.

## Dependencies and integration points

It integrates test code with Recon's REST API and with Hadoop HTTP policy configuration. `getReconWebAddress()` uses the configured HTTP or HTTPS bind address but falls back to the Recon RPC hostname when the web host remains at its default wildcard host. This matters in mini-cluster tests where bind addresses often use `0.0.0.0` but clients need a reachable host.

## Risks and test signals

The helpers swallow several exceptions and return null or log only, so caller tests may fail later during JSON parsing rather than at the original connection failure. `getHostOnly()` and `getPort()` split on the first colon and are not IPv6-safe. Positive test signals are successful sync trigger responses, valid unhealthy-container JSON deserialization, and correct URL construction for HTTP and HTTPS policies.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconEndpointUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconInsightsForDeletedDirectories.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconInsightsForDeletedDirectories.java

## Purpose

This integration test validates Recon OM DB insight reporting for deleted directories in FILE_SYSTEM_OPTIMIZED buckets. It exercises simple, nested, and wide directory deletions under both RATIS THREE and EC RS-3-2 replication, then verifies Recon's deleted-directory insight sizes and namespace summary accounting.

## Important APIs, types, and functions

The test uses `MiniOzoneCluster`, Hadoop `FileSystem`, `OzoneClient`, `OzoneBucket`, OM `Table` instances for file, directory, and deleted-directory tables, `ReconOMMetadataManager`, `ReconNamespaceSummaryManagerImpl`, `ReconGlobalMetricsService`, and `OMDBInsightEndpoint`. Parameterization comes from `replicationConfigs()`. Main tests are `testGetDeletedDirectoryInfo()`, `testGetDeletedDirectoryInfoForNestedDirectories()`, and `testGetDeletedDirectoryInfoWithMultipleSubdirectories()`. Helpers include `createLargeDirectory()`, `cleanupTables()`, `removeAllFromDB()`, `assertTableRowCount()`, `syncDataFromOM()`, and `waitForAsyncProcessingToComplete()`.

## Control flow, state, and persistence

The cluster disables frequent directory and block deletion services, enables ACLs, and sets a small FSO iterate batch size. Each test creates an FSO bucket with a default replication config, creates directory trees through the Hadoop FS API, checks OM table row counts, syncs OM data into Recon, and then checks Recon table row counts. After deletion, the tests instantiate `OMDBInsightEndpoint` directly and assert `KeyInsightInfoResponse` unreplicated and replicated sizes. Cleanup manually deletes rows from OM deleted-directory, file, and directory tables.

## Dependencies and integration points

The tests integrate the Ozone FS client, OM metadata tables, Recon OM snapshot synchronization, Recon namespace summary updates, quota replicated-size calculations, and the OM DB insight endpoint. `QuotaUtil.getReplicatedSize()` is used as the replication-aware expected value, making the same assertions valid for RATIS and EC.

## Risks and test signals

The async wait helper is time-based rather than tied to the Recon event buffer, so slow CI environments can still race namespace-summary processing. Manual table cleanup touches OM metadata directly and assumes no other test state is sharing the cluster. Strong test signals are row-count convergence in OM and Recon tables, deleted-directory table growth after delete, and insight endpoint sizes of 10, 3, and 100 bytes/files adjusted by replication.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconInsightsForDeletedDirectories.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconOmMetaManagerUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconOmMetaManagerUtils.java

## Purpose

This utility class provides wait helpers for Recon OM metadata processing in integration tests. It bridges asynchronous Recon event-buffer processing and delayed Recon container-key index updates.

## Important APIs, types, and functions

`waitForEventBufferEmpty(OMUpdateEventBuffer)` returns a `CompletableFuture<Void>` that waits for `eventBuffer.getQueueSize() == 0` and then sleeps briefly. `waitUntilReconKeyCounts(ReconContainerMetadataManager, Map<Long, Integer>)` repeatedly checks that each container has at least the expected key count. It uses `GenericTestUtils.waitFor()` and handles `IOException` from the metadata manager.

## Control flow, state, and persistence

The class stores no state. The event-buffer wait runs asynchronously and wraps failures in `RuntimeException`. The key-count wait polls for up to 90 seconds and treats transient read failures as not-ready rather than fatal, which is useful while Recon is concurrently applying RocksDB-backed updates.

## Dependencies and integration points

The helpers are used by tests that call `OzoneManagerServiceProviderImpl.syncDataFromOM()` and then need Recon task processing to complete before assertions. They integrate with `OMUpdateEventBuffer`, `ReconContainerMetadataManager`, and `GenericTestUtils`.

## Risks and test signals

An empty event buffer does not necessarily prove a dequeued batch has fully updated all derived indexes; the second helper addresses this by checking container-key counts directly. The extra sleep in `waitForEventBufferEmpty()` is a pragmatic stabilization delay. Positive signals are completed futures and converged per-container key counts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconOmMetaManagerUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconQuasiClosedContainerEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconQuasiClosedContainerEndpoint.java

## Purpose

This integration test validates the Recon `GET /containers/quasiClosed` endpoint through direct `ContainerEndpoint` calls. It checks basic listing, pagination, count-only behavior for `limit=0`, and bad-request handling for invalid parameters.

## Important APIs, types, and functions

The test uses `MiniOzoneCluster`, `ReconService`, `ReconStorageContainerManagerFacade`, `ReconContainerManager`, `ContainerEndpoint`, `QuasiClosedContainersResponse`, `QuasiClosedContainerMetadata`, `ContainerInfo`, and `ContainerWithPipeline`. The key helper is `createQuasiClosedContainer()`, which injects containers directly into Recon's container manager and applies `FINALIZE` and `QUASI_CLOSE` lifecycle events.

## Control flow, state, and persistence

The cluster is started once per class with three datanodes. After Recon pipeline state is available, tests create artificial container IDs from an `AtomicLong` starting at 10000 so each test can page from its own cursor. The containers are not created in SCM or on datanodes; they are in-memory Recon state only. Pagination walks `getQuasiClosedContainers(pageSize, cursor)` and updates the cursor from `lastKey`.

## Dependencies and integration points

The file isolates endpoint behavior from container health and metadata managers by constructing `ContainerEndpoint` with only the Recon SCM facade and nulls for unused collaborators. It depends on at least one RF3 pipeline being present in Recon to attach to injected containers.

## Risks and test signals

Because it mutates shared Recon state across class-level tests, the cursor strategy is critical to avoid cross-test contamination. Direct injection bypasses SCM sync and datanode reports, so it tests endpoint filtering/pagination rather than full ingestion. Passing signals include returned IDs containing created quasi-closed containers, expected replica count of 3, valid pipeline IDs and state-enter times, exactly four pages for 25 containers at page size 7, nonzero count with empty result for `limit=0`, and HTTP 400 for negative inputs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconQuasiClosedContainerEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconScmSnapshot.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconScmSnapshot.java

## Purpose

This test validates Recon's SCM snapshot download and node-manager persistence behavior. It verifies that Recon can refresh containers, pipelines, and node DB state from SCM after being stopped, and that explicit node removal updates both persistent and in-memory node tracking.

## Important APIs, types, and functions

The class uses `MiniOzoneCluster`, `ReconService`, `ReconStorageContainerManagerFacade`, `ReconNodeManager`, `ContainerManager`, `PipelineManager`, `NodeStatus`, and `LogCapturer`. Test methods are `testScmSnapshot()` and `testExplicitRemovalOfNode()`.

## Control flow, state, and persistence

Setup enables SCM snapshot support, sets a zero container threshold to force snapshot behavior, and configures short heartbeat, stale, and dead-node intervals. `testScmSnapshot()` records Recon's initial empty container view and node DB key count, stops Recon, allocates ten SCM containers, restarts Recon, and compares SCM and Recon container/pipeline counts. It also checks that node DB key count remains stable. `testExplicitRemovalOfNode()` stops one datanode, waits for DEAD status, verifies the node remains tracked, then calls `removeNode()` and verifies DB and memory counts drop to three.

## Dependencies and integration points

The test integrates Recon restart lifecycle, SCM metadata snapshot transfer, Recon node DB persistence, and heartbeat-driven node status transitions. Log capture on `ReconStorageContainerManagerFacade` is used as an additional signal that container count comparison happened.

## Risks and test signals

Timing depends on heartbeat and dead-node intervals; `GenericTestUtils.waitFor()` bounds the node-death wait. The snapshot test assumes the restart path reinitializes Recon storage managers against the same mini-cluster SCM. Positive signals are SCM/Recon container count equality, pipeline count equality, unchanged node DB count after snapshot refresh, and explicit removal reducing both DB key count and `getAllNodes()` size.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconScmSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconTasks.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconTasks.java

## Purpose

This integration test suite exercises Recon's `ContainerHealthTask` and SCM container sync behavior. It covers unhealthy states persisted in `UNHEALTHY_CONTAINERS`: `UNDER_REPLICATED`, `EMPTY_MISSING`, `MISSING`, `OVER_REPLICATED`, `NEGATIVE_SIZE`, and `REPLICA_MISMATCH`, while documenting why `MIS_REPLICATED` and `ALL_REPLICAS_BAD` are not covered here.

## Important APIs, types, and functions

The suite uses `MiniOzoneCluster`, `ReconService`, `ReconStorageContainerManagerFacade`, `ReconContainerManager`, `ContainerHealthSchemaManager`, SCM `ContainerManager`, `PipelineManager`, `ContainerReplica`, `ContainerChecksums`, `XceiverClientGrpc`, `XceiverClientRatis`, and helper methods from `TestOzoneContainer`. Test methods are `testSyncSCMContainerInfo()`, `testContainerHealthTaskDetectsUnderReplicatedAfterNodeFailure()`, `testContainerHealthTaskDetectsEmptyMissingWhenAllReplicasLost()`, `testContainerHealthTaskDetectsMissingForContainerWithKeys()`, `testContainerHealthTaskDetectsOverReplicatedAndNegativeSize()`, and `testContainerHealthTaskDetectsReplicaMismatch()`.

## Control flow, state, and persistence

Each test starts a three-datanode cluster with short container/pipeline reports, tuned dead-node intervals, and slow SCM remediation. Sync testing allocates and closes SCM containers, verifies Recon is behind, then calls `triggerSCMContainerSync()`. Health tests create real containers, wait for Recon replica reports, directly transition lifecycle state in SCM and Recon when needed, and call `reconScm.getReplicationManager().processAll()` to force scans. Some scenarios use physical datanode shutdown and restart; others inject or remove `ContainerReplica` entries directly in Recon metadata for deterministic missing, over-replicated, negative-size, and checksum-mismatch states.

## Dependencies and integration points

The tests integrate datanode reports, SCM dead-node handling, Recon replica bookkeeping, lifecycle-state-gated health handlers, Recon-specific checks such as negative size and checksum mismatch, and Derby unhealthy-row cleanup after recovery. RF3 paths deliberately use `XceiverClientRatis` so create-container commands reach all three replicas; RF1 paths use `XceiverClientGrpc`.

## Risks and test signals

Main risks are asynchronous replica reports, dead-node timing, and health-handler ordering. The tests wait for expected replica counts before mutating state and repeatedly force health scans during waits. Key signals include unhealthy rows appearing only in the expected state, rows clearing after recovery, `MISSING` being distinct from `EMPTY_MISSING` based on `numberOfKeys`, co-detection of `NEGATIVE_SIZE` with over-replication, and cleanup of `REPLICA_MISMATCH` after checksums become uniform.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconTasks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconTasksMultiNode.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconTasksMultiNode.java

## Purpose

This class provides additional multi-node ContainerHealthTask checks using a shared three-datanode cluster. It is separated from `TestReconTasks` because the cluster lifecycle and timing configuration differ.

## Important APIs, types, and functions

The suite uses `MiniOzoneCluster`, `ReconService`, `ReconStorageContainerManagerFacade`, `ReconContainerManager`, `PipelineManager`, `ContainerHealthSchemaManager.UnhealthyContainerRecord`, and `ContainerSchemaDefinition.UnHealthyContainerStates`. Test methods are `testContainerHealthTaskUnderReplicated()` and `testContainerHealthTaskOverReplicated()`.

## Control flow, state, and persistence

Setup creates a three-datanode cluster with five-second container and pipeline reports, ten-second missing-container task interval, and six/eight-second stale/dead intervals. Before each test it clears all unhealthy records and waits for Recon pipeline state. The tests wait for RF3 or RF1 pipelines and then query the unhealthy-container table for `UNDER_REPLICATED` or `OVER_REPLICATED`, expecting no rows in normal operation.

## Dependencies and integration points

The class verifies the query surface for unhealthy-container records in a multi-node Recon cluster, but it does not induce actual under- or over-replication. The comments point to more complete end-to-end coverage in `TestReconTasks`.

## Risks and test signals

These are low-depth smoke tests: they prove table access and normal healthy-cluster emptiness, not detection logic. The risk is false confidence because no unhealthy state is created. Positive signals are successful pipeline readiness and empty query results for both states after clearing the unhealthy table.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconTasksMultiNode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconWithOzoneManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconWithOzoneManager.java

## Purpose

This integration test validates Recon synchronization from a non-HA Ozone Manager. It checks full snapshot sync, delta update sync, restart behavior, task-status REST reporting, sequence-number lag metrics, and fallback to full snapshot when Recon's local OM snapshot sequence number is ahead of active OM.

## Important APIs, types, and functions

The class uses `MiniOzoneCluster`, `ReconService`, `OzoneManagerServiceProviderImpl`, `OzoneManagerSyncMetrics`, `OMMetadataManager`, `RDBStore`, task names `OmSnapshotRequest` and `OmDeltaRequest`, Apache `CloseableHttpClient`, and OM metadata types `OmKeyInfo`, `OmKeyLocationInfo`, and `OmKeyLocationInfoGroup`. Test methods are `testOmDBSyncing()` and `testOmDBSyncWithSeqNumberMismatch()`. Helpers include `makeHttpCall()`, `getReconTaskAttributeFromJson()`, `addKeys()`, `writeDataToOm()`, and block-location builders.

## Control flow, state, and persistence

Setup configures Recon OM delta update limit, starts a one-datanode mini cluster with Recon, exits SCM safe mode, and creates an HTTP client for `/api/v1/task/status`. Tests write synthetic key metadata directly into OM's key table, call `syncDataFromOM()`, read OM and Recon RocksDB sequence numbers, and parse task-status JSON for last updated sequence number and timestamp. The mismatch test mutates Recon's OM snapshot DB directly to increment its sequence number beyond OM, then verifies the failed delta update path logs the expected DBUpdates failure and normalizes by full snapshot.

## Dependencies and integration points

The tests integrate OM RocksDB sequence numbers, Recon snapshot and delta sync tasks, metrics lag accounting, task-status REST JSON, and Recon restart. Direct metadata table writes avoid client-level volume/bucket creation but depend on OM key-table semantics and synthetic block locations.

## Risks and test signals

Direct RocksDB table mutation is efficient but bypasses higher-level invariants. The HTTP timeout configuration appears to map variables inconsistently by name, though the test only needs a functioning client. Positive signals are OM and Recon sequence numbers matching, zero sequence-number lag, delta task status advancing after new keys and restart, logs containing the expected failed-update messages for the mismatch, and later logs showing successful DB update.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconWithOzoneManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconWithOzoneManagerFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconWithOzoneManagerFSO.java

## Purpose

This integration test validates Recon namespace summary behavior when OM uses FILE_SYSTEM_OPTIMIZED bucket layout by default. It creates volume/bucket/key hierarchies through the client API, syncs Recon from OM, and queries `NSSummaryEndpoint` for directory and root summary responses.

## Important APIs, types, and functions

The class uses `MiniOzoneCluster`, `ReconService`, `OzoneClient`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `TestDataUtil.createKey()`, `OzoneManagerServiceProviderImpl`, `ReconNamespaceSummaryManager`, `ReconOMMetadataManager`, `NSSummaryEndpoint`, and `NamespaceSummaryResponse`. The main test is `testNamespaceSummaryAPI()`, supported by `writeKeys()`, `addKeys()`, and `waitForAsyncProcessingToComplete()`.

## Control flow, state, and persistence

Setup sets the default bucket layout to FSO, starts a three-datanode cluster, waits for RF1 pipelines, and initializes an object store. The test creates ten volumes and buckets with keys under `dirN/keyN`, syncs OM data into Recon, waits for async processing, and checks that `/vol1/bucket1/dir1` is a directory with one key and no child directories. It then creates two more entries, syncs again, checks Recon's volume table via `getSkipCache()`, and validates root counts for volume, bucket, directory, and key totals.

## Dependencies and integration points

The test integrates client-side key creation, FSO OM metadata, Recon OM sync, Recon namespace summary indexing, and the namespace summary REST resource instantiated directly in-process.

## Risks and test signals

The async wait helper is time-based and may race under slow event processing. The expected root volume count is 13 while only 12 loop-created volumes exist, implying a built-in/system/default volume is counted and should be documented if that behavior changes. The comments note expectation changes after removing deleted-table processing. Positive signals are directory entity typing, count stats for a specific directory, Recon OM volume-table visibility after sync, and expected root aggregate counts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconWithOzoneManagerFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconWithOzoneManagerHA.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconWithOzoneManagerHA.java

## Purpose

This integration test validates Recon behavior with an HA Ozone Manager cluster. It verifies that Recon downloads OM snapshots from the current leader and that container-to-key metadata indexing works after syncing HA OM data.

## Important APIs, types, and functions

The class uses `MiniOzoneHAClusterImpl`, `ReconService`, `OzoneClientFactory.getRpcClient()`, `ObjectStore`, `OzoneManagerServiceProviderImpl`, `ReconTaskControllerImpl`, `ReconContainerMetadataManagerImpl`, `TestReconOmMetaManagerUtils`, `OZONE_DB_CHECKPOINT_HTTP_ENDPOINT`, and OM lookup types `OmKeyArgs` and `OmKeyLocationInfo`. The main test is `testReconGetsSnapshotFromLeader()`, with helper `getContainerIdForKey()`.

## Control flow, state, and persistence

Setup enables RocksDB sync-to-disk, builds a three-OM/one-datanode HA mini cluster, starts Recon as an added service, creates a test volume, and creates an OBJECT_STORE bucket because Recon's container ID to key mapping does not yet support FSO buckets. The test waits for leader election, constructs the expected leader checkpoint URL, compares it with `getOzoneManagerSnapshotUrl()`, writes a RATIS ONE key, calls `syncDataFromOM()`, waits for Recon event-buffer completion, waits until the expected container has at least one key in Recon's container metadata manager, and finally verifies the stored key prefix.

## Dependencies and integration points

The test integrates OM HA leader discovery, HTTP checkpoint URL construction, Recon OM sync, asynchronous Recon task processing, and Recon's container-key table. It deliberately reads the key from the current OM leader to find the authoritative block/container ID.

## Risks and test signals

Leader readiness is asynchronous, so a long wait guards election. The test only covers OBJECT_STORE bucket layout due to a known FSO limitation. Positive signals are an expected snapshot URL pointing to the leader's HTTP server, successful sync after key creation, event-buffer drain, container-key count convergence, and a key prefix of `/testrecon/testrecon/ratis` in Recon metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconWithOzoneManagerHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestStorageDistributionEndpointEC.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestStorageDistributionEndpointEC.java

## Purpose

This subclass tests the Recon storage-distribution and pending-deletion endpoints under EC replication. It uses a five-datanode cluster to satisfy RS-3-2 placement and reuses shared setup and verification logic from `AbstractTestStorageDistributionEndpoint`.

## Important APIs, types, and functions

The class extends `AbstractTestStorageDistributionEndpoint`, overrides `getNumDatanodes()`, and provides `setup()` and `testStorageDistributionEndpoint()`. It uses `ECReplicationConfig(3, 2)`, `OzoneBucket`, Hadoop `FileSystem`, `Path`, and `GenericTestUtils.waitFor()`.

## Control flow, state, and persistence

The test initializes a five-datanode cluster, creates an FSO bucket with EC default replication, creates open and multipart keys through the base helper, then writes 20 finalized filesystem keys across `/dir1` and `/dir2`. It waits for storage distribution to show expected global namespace and storage data, closes all containers, deletes `/dir1`, and then waits for pending-deletion signals at OM, SCM, and DN components. It finally waits for SCM's deleted-block summary to clear and for DN pending deletion to clear.

## Dependencies and integration points

The test depends on the abstract base for cluster tuning, endpoint HTTP calls, JSON parsing, OM sync, pending-deletion checks, and container close events. It integrates EC replicated-size accounting with Recon's storage-distribution and pending-deletion APIs.

## Risks and test signals

The EC path needs enough datanodes and can be timing-sensitive around block deletion and datanode metric collection. Positive signals are the base verifier's expected namespace totals, per-datanode usage matching SCM reports, OM pending deletion of 300 bytes, SCM pending deletion of 10 blocks/100 unreplicated bytes/300 replicated bytes, DN pending deletion distributed across five nodes, and eventual DN pending-deletion clearance.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestStorageDistributionEndpointEC.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestStorageDistributionEndpointRatis.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestStorageDistributionEndpointRatis.java

## Purpose

This subclass tests the Recon storage-distribution and pending-deletion endpoints under RATIS THREE replication. It also verifies the DN pending-deletion endpoint's behavior when a datanode is stopped.

## Important APIs, types, and functions

The class extends `AbstractTestStorageDistributionEndpoint`, overrides `getNumDatanodes()`, and provides `setup()` and `testStorageDistributionEndpoint()`. It uses `RatisReplicationConfig.getInstance(THREE)`, `OzoneBucket`, Hadoop `FileSystem`, `Path`, and `GenericTestUtils.waitFor()`.

## Control flow, state, and persistence

The test initializes a three-datanode cluster, creates an FSO bucket with RATIS THREE replication, creates open and multipart keys, writes 20 filesystem keys under two directories, and waits for storage-distribution assertions. It closes all containers, deletes `/dir1`, waits for pending-deletion visibility at OM, SCM, and DN, waits for SCM deleted blocks to clear, waits for DN pending deletion to clear, then stops one datanode and verifies the DN endpoint records a query failure.

## Dependencies and integration points

Like the EC subclass, it relies on the abstract base for configuration, endpoint access, OM sync, and verification. The final stopped-datanode scenario integrates Recon's datanode metrics collection with partial failure reporting.

## Risks and test signals

Timing is sensitive around container close events, block deletion, DN metric collection, and the stopped-node query failure. Positive signals include the same storage and pending-deletion totals as the base verifier with three datanodes, DN pending deletion distributed as 100 bytes per node before cleanup, zero pending deletion after cleanup, and a DN metrics response with one query failure and a `-1` per-node pending block size.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestStorageDistributionEndpointRatis.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/resources/ozone-site.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/resources/ozone-site.xml

## Purpose

This test resource supplies Ozone configuration defaults for Recon integration tests. It tunes OM, SCM, datanode, Ratis, heartbeat, snapshot-diff, container, and stream-buffer settings to make mini-cluster integration tests faster and more deterministic.

## Important settings

The file sets `ozone.om.transport.class` to `Hadoop3OmTransportFactory`, disables `ozone.om.s3.grpc.server_enabled`, raises OM and SCM handler counts to 20, enables Ratis datastream, shortens heartbeat intervals, limits SCM Ratis pipelines to 3, and sets close-container wait duration to 1 second. It also configures Ratis appender queue byte limits, chunk/block/container sizes, client stream buffer sizes, datastream packet/window sizes, and datanode minimum free space.

## Control flow, state, and persistence

The XML has no executable control flow. It is loaded into test configurations as a resource and changes runtime behavior of mini clusters created by the integration-test-recon module. Values persist only for the process-level configuration used by each test cluster.

## Dependencies and integration points

Settings affect Recon tests that rely on prompt heartbeat/report propagation, stream and datastream behavior, smaller block/container sizes, and predictable SCM/OM service responsiveness. The transport factory setting controls the OM client protocol implementation used in tests.

## Risks and test signals

Overly aggressive intervals can increase load or expose timing flakiness; larger handler counts can hide bottlenecks present in smaller deployments. Positive signals are faster cluster readiness, quick heartbeat-driven state convergence, and tests completing with bounded container/block sizes. Changes here can have broad effects across many Recon integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/resources/ozone-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/dev-support/findbugsExcludeFile.xml

## Purpose

This SpotBugs filter suppresses one static-analysis warning for the S3 integration-test module.

## Important rules

The filter matches `org.apache.hadoop.ozone.s3.awssdk.v2.AbstractS3SDKV2Tests$S3BucketOwnershipVerificationConditionsTests` and suppresses the `SIC_INNER_SHOULD_BE_STATIC` pattern.

## Control flow, state, and persistence

The XML has no runtime control flow. It is consumed by the module's SpotBugs Maven plugin configuration and affects static-analysis reporting during builds.

## Dependencies and integration points

The file is referenced by `integration-test-s3/pom.xml` as `${basedir}/dev-support/findbugsExcludeFile.xml`. It exists because the nested test class is intentionally non-static or cannot be made static without disrupting test access to enclosing test state.

## Risks and test signals

The risk is that the suppression can hide a real retention or lifecycle issue if the nested class starts holding heavier outer state. The positive build signal is a SpotBugs run that remains focused on actionable warnings while allowing this specific JUnit nested-test structure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/pom.xml

## Purpose

This Maven module defines Apache Ozone S3 integration tests. It packages test code for S3 Gateway, AWS SDK v1 and v2 coverage, proxy/load-balancing helpers, and mini-cluster S3 scenarios.

## Important APIs, types, and functions

The POM inherits from the `org.apache.ozone:ozone` parent at `2.3.0-SNAPSHOT`, sets artifact ID `ozone-integration-test-s3`, and imports the AWS SDK v2 BOM at `2.46.5`. Dependencies include AWS SDK v1 `aws-java-sdk-core` and `aws-java-sdk-s3`, AWS SDK v2 `s3`, `s3-transfer-manager`, `apache-client`, auth/core/regions/sdk utilities, Jetty server/proxy/client/servlet/util, Ozone client/common/mini-cluster/s3gateway, HDDS server and test utilities, Hadoop common, Ratis common, Guava, commons-io, commons-lang3, Kerby util, JAXB API, servlet API, and SLF4J.

## Control flow, state, and persistence

The POM drives build-time dependency resolution and plugin behavior. The `spotbugs-maven-plugin` points at the module's `dev-support/findbugsExcludeFile.xml`. The compiler plugin disables annotation processing with `<proc>none</proc>`.

## Dependencies and integration points

This module bridges Ozone mini-cluster tests with both AWS SDK generations and Jetty-based proxying. Test dependencies are scoped to avoid exporting the integration harness. The imported SDK v2 BOM keeps v2 AWS artifacts aligned while v1 dependencies are inherited/managed elsewhere by the parent.

## Risks and test signals

Version skew between AWS SDK v1, SDK v2, Jetty, and Ozone S3 Gateway can break compatibility tests. Disabling annotation processing is usually fine for tests but can mask generated-code expectations if new test dependencies require processors. Positive signals are successful compilation of nested SDK v1/v2 suites, SpotBugs using the intended exclusion, and all S3 gateway/proxy tests resolving test-scope dependencies.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/LoadBalanceStrategy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/LoadBalanceStrategy.java

## Purpose

This interface defines the pluggable strategy used by the S3 test proxy to choose an S3 Gateway endpoint for each incoming request.

## Important APIs, types, and functions

It declares one method: `String selectEndpoint(List<String> endpoints)`. Implementations receive the current list of available endpoint base URLs and return the selected target base URL.

## Control flow, state, and persistence

The interface has no state or implementation. State and concurrency behavior are delegated to implementations such as `RoundRobinStrategy`.

## Dependencies and integration points

`ProxyServer.ProxyHandler.rewriteTarget()` calls this method on every proxied request before appending the request URI and query string. `MultiS3GatewayService` supplies the endpoint list when constructing `ProxyServer`.

## Risks and test signals

Implementations must handle null or empty endpoint lists consistently; the interface does not specify exception behavior beyond the Java signature. Positive signals are deterministic endpoint selection in `ProxyServerIntegrationTest` and easy substitution of alternative strategies for future S3 Gateway load-balancing tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/LoadBalanceStrategy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/MultiS3GatewayService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/MultiS3GatewayService.java

## Purpose

This mini-cluster service starts multiple S3 Gateway instances and exposes them through one Jetty reverse proxy. It lets SDK integration tests exercise S3 behavior through a load-balanced gateway front door.

## Important APIs, types, and functions

The class implements `MiniOzoneCluster.Service`. It owns a list of `S3GatewayService` instances, a `ProxyServer`, and a constructor that accepts the number of gateways. `start()` launches each gateway, collects its HTTP endpoint, rewrites the cluster S3G HTTP address to the proxy address, and starts the proxy. `stop()` shuts down the proxy and all gateways while preserving/suppressing exceptions.

## Control flow, state, and persistence

At startup, each child gateway receives the same input `OzoneConfiguration` and internally binds to free ports. The service collects `http://host:port` URLs from each child gateway's held configuration. It then allocates a free proxy address, stores it in the passed configuration under `OZONE_S3G_HTTP_ADDRESS_KEY`, constructs `ProxyServer`, and starts it. Runtime state is in-memory Jetty/S3G processes only.

## Dependencies and integration points

The class integrates `S3GatewayService`, `ProxyServer`, `S3GatewayConfigKeys`, and `MiniOzoneCluster` service lifecycle. `OzoneS3SDKTests` adds `new MultiS3GatewayService(5)` to the test cluster, so all nested AWS SDK tests use the proxy-facing S3 endpoint.

## Risks and test signals

The `configuration` field is never assigned, so `getConf()` returns null; current callers appear to use the mutated cluster config instead, but direct callers would fail. Startup does not roll back already-started child gateways if a later gateway or proxy fails. Positive signals are the SDK tests reaching the proxy address from configuration, requests being distributed by the proxy, and `stop()` collecting failures without skipping remaining services.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/MultiS3GatewayService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/ProxyServer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/ProxyServer.java

## Purpose

This class implements a Jetty reverse proxy for S3 Gateway endpoints. It selects a backend endpoint per request using a `LoadBalanceStrategy`, rewrites the target URL, and forwards the request to the selected S3G.

## Important APIs, types, and functions

The class owns endpoint list, load-balancing strategy, Jetty `Server`, host, and port. Constructors default to `RoundRobinStrategy` unless a strategy is supplied. Lifecycle methods are `start()`, `stop()`, and `isStarted()`. The inner `ProxyHandler` extends `ProxyServlet.Transparent` and overrides `init()`, `rewriteTarget()`, `service()`, `onProxyResponseFailure()`, and `onProxyRewriteFailed()`.

## Control flow, state, and persistence

The constructor creates a Jetty server on the proxy port, installs a servlet context at `/`, and maps `ProxyHandler` to `/*`. For each request, `rewriteTarget()` chooses a base URL, appends request URI and query string, and returns the target. `service()` wraps requests containing an `Expect` header so the proxy sees that header as absent, avoiding Jetty 100-continue handling issues observed in S3 put-object tests. Failures are logged and rewrite failure attempts to send HTTP 502 text.

## Dependencies and integration points

It depends on Jetty server/servlet/proxy/client APIs, Guava `HttpHeaders`, servlet request wrappers, and `LoadBalanceStrategy`. It is used by `MultiS3GatewayService` for real S3 Gateway tests and by `ProxyServerIntegrationTest` with mock backends.

## Risks and test signals

The endpoint list is accepted without constructor validation; null or empty lists fail later in the strategy. The proxy binds `new Server(proxyPort)` without the host, so the host parameter is mostly informational. Removing `Expect` is a test compatibility workaround that may hide behavior differences for clients relying on 100-continue semantics. Positive signals include correct URL rewriting with query strings, round-robin distribution, successful direct and proxied GETs, useful failure logs, and no hangs on requests with `Expect`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/ProxyServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/ProxyServerIntegrationTest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/ProxyServerIntegrationTest.java

## Purpose

This integration test verifies the standalone `ProxyServer` routing behavior. It starts three mock Jetty backends, starts the proxy, checks round-robin routing through the proxy, and checks that each backend remains directly reachable.

## Important APIs, types, and functions

The test uses Jetty `Server`, `ServletContextHandler`, `ServletHolder`, a local `ServiceServlet`, `ProxyServer`, `GenericTestUtils.waitFor()`, `HttpURLConnection`, and AssertJ assertions. Helpers include `startMockServer()`, `startProxy()`, `waitForMockServersStarted()`, `waitForProxyReady()`, and `sendRequest()`.

## Control flow, state, and persistence

`@BeforeAll` starts three mock servers on free localhost ports, each serving `/service-name` with its own name. It then starts a `ProxyServer` over those endpoints and records `proxyUrl`. `testRouting()` sends twice as many requests as servers and expects responses in modulo order. `testDirectAccess()` requests each backend URL directly and expects the matching server name. `@AfterAll` stops the proxy and all mock servers.

## Dependencies and integration points

The test exercises `ProxyServer`, `RoundRobinStrategy`, Jetty servlet plumbing, and Java URL connections. It does not involve Ozone or S3 Gateway, which keeps proxy routing failures isolated.

## Risks and test signals

The test assumes no concurrent tests share the same static proxy state and that free ports remain available until binding. It does not test POST bodies, headers, query strings, or failure handling. Positive signals are proxy startup readiness, direct backend responses, and deterministic round-robin sequence `server-0`, `server-1`, `server-2`, repeated.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/ProxyServerIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/RoundRobinStrategy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/RoundRobinStrategy.java

## Purpose

This class implements the default load-balancing strategy for the test S3 proxy. It cycles through endpoint URLs in round-robin order.

## Important APIs, types, and functions

It implements `LoadBalanceStrategy` and defines `selectEndpoint(List<String> endpoints)`. An `AtomicInteger counter` stores the next index and is updated with `getAndUpdate(i -> (i + 1) % endpoints.size())`.

## Control flow, state, and persistence

Each call validates that the endpoint list is non-null and non-empty, atomically returns the current index, advances the counter modulo the current list size, and returns the endpoint at the chosen index. State is process-local and not persisted.

## Dependencies and integration points

`ProxyServer` uses this strategy by default. `ProxyServerIntegrationTest.testRouting()` indirectly verifies its behavior by expecting alternating backend names.

## Risks and test signals

Changing endpoint list size between calls can still work for normal size changes, but a concurrent empty list would throw. The atomic counter can overflow after enough requests; modulo update keeps indices bounded for usual operation, though negative overflow is avoided because the stored value remains modulo size. Positive signal is deterministic cycling through all configured endpoints under concurrent-safe atomic updates.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/RoundRobinStrategy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/S3ClientFactory.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/S3ClientFactory.java

## Purpose

This factory creates AWS SDK v1 and v2 S3 clients configured for the mini-cluster S3 Gateway endpoint. It supports sync and async v2 clients and path-style toggles for endpoint compatibility tests.

## Important APIs, types, and functions

The class exposes `createS3Client()`, `createS3Client(boolean)`, `createS3ClientV2()`, `createS3ClientV2(boolean)`, `createS3AsyncClientV2()`, `createS3AsyncClientV2(boolean)`, and generic `configureCommon()`. It uses AWS SDK v1 `AmazonS3ClientBuilder`, `BasicAWSCredentials`, `AWSStaticCredentialsProvider`, and SDK v2 `S3ClientBuilder`, `S3AsyncClientBuilder`, `AwsBasicCredentials`, `StaticCredentialsProvider`, and `S3BaseClientBuilder`.

## Control flow, state, and persistence

The factory stores the `OzoneConfiguration`. For each client creation, it reads Hadoop HTTP policy, chooses HTTP or HTTPS S3G address keys, builds an endpoint URI, applies static test credentials `user/password`, sets a fixed region, and enables path-style access when requested. No state is persisted beyond the created client instances.

## Dependencies and integration points

The factory integrates S3 Gateway test configuration with AWS SDK clients. It depends on `S3GatewayConfigKeys` and Hadoop HTTP policy. The created clients are consumed by abstract AWS SDK integration suites outside this subset.

## Risks and test signals

HTTPS is noted as currently disabled in tests, so HTTPS client paths are lightly exercised. Static credentials must match S3G test authentication expectations. Endpoint host comes directly from configuration; if a service mutates the configuration to a proxy address, clients route through the proxy. Positive signals are SDK v1/v2 clients successfully issuing bucket/object operations with path-style addressing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/S3ClientFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/S3GatewayService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/S3GatewayService.java

## Purpose

This mini-cluster service starts a single Ozone S3 Gateway for integration tests and binds its HTTP, HTTPS, and webadmin endpoints to free localhost ports.

## Important APIs, types, and functions

The class implements `MiniOzoneCluster.Service` and defines `start()`, `stop()`, `toString()`, `getConf()`, and private `configureS3G()`. It owns a `Gateway` instance and uses `OzoneConfigurationHolder` to pass the configured S3G addresses to the gateway.

## Control flow, state, and persistence

`start()` asserts no gateway is running, clones the input configuration, sets all S3G and webadmin bind addresses to free localhost ports, resets and sets `OzoneConfigurationHolder`, creates `Gateway`, and executes it with no args. `stop()` asserts a gateway exists and stops it. Runtime state is the running gateway and global configuration holder; no test data is persisted by this wrapper.

## Dependencies and integration points

It integrates `Gateway`, `S3GatewayConfigKeys`, `OzoneConfigurationHolder`, `MiniOzoneCluster.Service`, and port allocation utilities. `MultiS3GatewayService` composes several instances and reads each child's `getConf()` to discover its HTTP endpoint.

## Risks and test signals

Because it uses a global `OzoneConfigurationHolder`, multiple gateway instances rely on each service starting and capturing its configuration correctly. `stop()` does not null out `s3g`, so a stopped instance cannot be restarted by the same object without failing the start assertion. Positive signals are unique free ports, a `toString()` showing live HTTP/HTTPS addresses, and SDK clients successfully reaching the configured S3G endpoint.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/S3GatewayService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/OzoneS3SDKTests.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/OzoneS3SDKTests.java

## Purpose

This abstract test harness runs the shared AWS SDK S3 compatibility suites against a MiniOzoneCluster fronted by multiple S3 Gateways behind a proxy. It provides nested SDK v1 and SDK v2 test classes over the same cluster.

## Important APIs, types, and functions

The class extends `ClusterForTests<MiniOzoneCluster>`, overrides `createCluster()`, and defines nested classes `V1` and `V2`. `createCluster()` calls `newClusterBuilder().addService(new MultiS3GatewayService(5)).build()`. `V1` extends `AbstractS3SDKV1Tests`; `V2` extends `AbstractS3SDKV2Tests`; both implement `cluster()` by returning `getCluster()`.

## Control flow, state, and persistence

The inherited `ClusterForTests` lifecycle creates and tears down the mini cluster. The added `MultiS3GatewayService` starts five S3G instances and a proxy, mutating S3G endpoint configuration so SDK clients use the proxy. Nested JUnit suites run many inherited S3 operations against that cluster.

## Dependencies and integration points

This is the glue between Ozone mini-cluster lifecycle, the S3 proxy/gateway service, and the broad abstract AWS SDK v1/v2 test suites. Concrete subclasses adjust Ozone configuration for normal or Ratis streaming write modes.

## Risks and test signals

Any lifecycle bug in `MultiS3GatewayService` affects all nested SDK tests. Because both nested suites share one cluster, state cleanup in the abstract suites must be reliable. Positive signals are both SDK generations running against the same proxied multi-gateway endpoint and inherited tests passing under this cluster harness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/OzoneS3SDKTests.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/S3SDKTestUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/S3SDKTestUtils.java

## Purpose

This utility class supports AWS SDK S3 compatibility tests with digest calculation, random test-file creation, multipart upload ID extraction, and low-level presigned URL HTTP calls.

## Important APIs, types, and functions

The public API includes `UPLOAD_ID_PATTERN`, `calculateDigest(InputStream, int, int)`, `createFile(File, int)`, `extractUploadId(String)`, and `openHttpURLConnection(URL, String, Map<String, List<String>>, byte[])`. It uses `MessageDigest` MD5, `InputSubstream`, `RandomUtils.secure()`, `RandomAccessFile`, Apache Commons IO, regex `Matcher`, and `HttpURLConnection`.

## Control flow, state, and persistence

`calculateDigest()` optionally wraps the provided input stream in an `InputSubstream`, reads 1024-byte chunks, and returns the MD5 digest without closing the caller-owned stream. `createFile()` writes cryptographically random bytes to a sync-on-write random access file and calls `FileDescriptor.sync()` before close. `extractUploadId()` parses the first `<UploadId>...</UploadId>` from XML. `openHttpURLConnection()` sets method and headers, writes an optional body, flushes it, and returns the open connection to the caller.

## Dependencies and integration points

The abstract SDK v1/v2 suites use these helpers for multipart ETag/digest checks, presigned GET/HEAD/PUT/POST/DELETE tests, and file upload inputs. The random-data choice avoids filesystem compression invalidating expected sizes.

## Risks and test signals

The upload ID regex is simple and not namespace-aware; it is suitable for controlled S3 XML responses but not a general XML parser. `openHttpURLConnection()` writes the body before the caller reads status, so request setup failures surface early. Positive signals are correct MD5 ranges for multipart parts, durable random files, upload ID extraction from S3 responses, and successful presigned URL operations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/S3SDKTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/TestS3SDK.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/TestS3SDK.java

## Purpose

This concrete AWS SDK integration-test class runs the shared `OzoneS3SDKTests` harness with Ratis datastream disabled. It represents the standard non-datastream S3 write path.

## Important APIs, types, and functions

The class extends `OzoneS3SDKTests` and overrides `createOzoneConfig()`. It uses `OzoneConfigKeys.HDDS_CONTAINER_RATIS_DATASTREAM_ENABLED` and `ScmConfigKeys.OZONE_SCM_PIPELINE_OWNER_CONTAINER_COUNT`.

## Control flow, state, and persistence

`createOzoneConfig()` calls the superclass configuration factory, disables container Ratis datastream, sets SCM pipeline owner container count to 1, and returns the modified configuration. Cluster creation and test execution are inherited from `OzoneS3SDKTests` and its nested SDK suites.

## Dependencies and integration points

The configuration feeds `MiniOzoneCluster` before `MultiS3GatewayService` and the SDK v1/v2 abstract suites run. It integrates S3 Gateway compatibility tests with the regular block-output path.

## Risks and test signals

This class is intentionally small; most behavior is inherited. A low pipeline owner container count may increase pipeline churn and expose allocation edge cases. Positive signals are all inherited AWS SDK v1/v2 tests passing while datastream is disabled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/TestS3SDK.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/TestS3SDKWithRatisStreaming.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/TestS3SDKWithRatisStreaming.java

## Purpose

This concrete AWS SDK integration-test class runs the shared S3 SDK compatibility suite with Ratis datastream enabled and configured as the default write path. It validates SDK behavior over Ozone's streaming write stack.

## Important APIs, types, and functions

The class extends `OzoneS3SDKTests` and overrides `createOzoneConfig()`. It sets `ScmConfigKeys.OZONE_SCM_PIPELINE_AUTO_CREATE_FACTOR_ONE`, `OzoneConfigKeys.HDDS_CONTAINER_RATIS_DATASTREAM_ENABLED`, `OzoneConfigKeys.OZONE_FS_DATASTREAM_ENABLED`, and `OzoneConfigKeys.OZONE_FS_DATASTREAM_AUTO_THRESHOLD`.

## Control flow, state, and persistence

`createOzoneConfig()` starts from the superclass configuration, disables automatic factor-one pipeline creation, enables container Ratis datastream, enables filesystem datastream, and sets the auto threshold to `0MB` so all writes use datastream. Cluster and nested SDK test execution are inherited.

## Dependencies and integration points

The class integrates the same proxy-backed multi-S3G harness with the datastream-enabled client/server code path. It is important coverage for put-object, multipart, and presigned operations under streaming semantics.

## Risks and test signals

Forcing all writes through datastream can expose differences in buffering, multipart upload handling, and small-object behavior. Disabling factor-one auto-create changes pipeline availability assumptions. Positive signals are inherited AWS SDK v1/v2 tests passing with datastream enabled for all write sizes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/TestS3SDKWithRatisStreaming.java -->
