# Research: subset-b-008076

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/storage/TestContainerCommandsEC.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/storage/TestContainerCommandsEC.java

Purpose: integration coverage for EC container command behavior in a secure MiniOzoneCluster. It validates EC block listing, orphan block handling, recovery-container creation, reconstruction coordinator success/failure paths, retries caused by close-container races, and token-protected container/block access.

Important APIs/types/functions: `TestContainerCommandsEC`, `startCluster`, `prepareData`, `createSingleNodePipeline`, `testOrphanBlock`, `testListBlock`, `testCreateRecoveryContainer`, `testCreateRecoveryContainerAfterDNRestart`, parameterized `testECReconstructionCoordinator*`, `recoverableMissingIndexes`, `createKeyAndWriteData`, `triggerRetryByCloseContainer`, `closeContainer`, `checkBlockData*`. It drives `MiniOzoneCluster`, `StorageContainerManager`, `Pipeline`, `ContainerProtocolCalls`, `XceiverClientGrpc`, `XceiverClientManager`, `ECReconstructionCoordinator`, `ECContainerOperationClient`, `ContainerTokenSecretManager`, `OzoneBlockTokenSecretManager`, and `SecretKeyTestClient`.

Control flow: class setup configures ACLs, block/container tokens, one EC writable pipeline, small deletion intervals, certificate/secret-key test clients, a cluster with `EC_DATA + EC_PARITY + 3` DNs, then writes randomized EC keys into one container group. Each test opens one-node xceiver clients per EC replica index. The orphan test writes a full stripe, closes the pipeline, deletes one block from replica index 2 via a `DeleteBlocksCommand`, reconstructs parity indexes 4 and 5, then asserts the reconstructed target has no orphan block metadata. Recovery-container tests allocate SCM state, force SCM lifecycle to closed, create a DN-side RECOVERING container, write/read chunks under block tokens, and verify DN restart converts RECOVERING to UNHEALTHY. Reconstruction tests delete selected replica containers, reconstruct onto spare DNs, compare block IDs, sizes, metadata and chunk lists, and assert metrics.

State and persistence: persistent behavior is real SCM metadata, DN container databases, chunk files, container states, token material, pipeline state, deleted containers, and reconstruction metrics inside a live mini cluster. `closeContainer` manipulates SCM container state manager directly. Retry injection asynchronously closes a replica container during key write to exercise duplicated/partial chunk metadata.

Dependencies and integration points: Ozone client API, SCM pipeline/container managers, datanode state machines, EC reconstruction subsystem, protobuf container protocol, HDDS security tokens, certificate and symmetric-key clients, `GenericTestUtils.waitFor`, and randomized Apache commons data.

Risks: highly stateful/flaky due to timing, async close-container retry, random key sizes, port/cluster resource usage, direct SCM state mutation, and exact error-message assertions. One loop constructing target pipeline indexes appears to use the first target entry while iterating all targets, so changes around multi-target reconstruction should be inspected carefully.

Test signals: assertions cover token-authenticated list/read/write paths, missing-container errors, expected block/chunk counts, container states RECOVERING/CLOSED/UNHEALTHY, insufficient EC locations, cleanup after failed reconstruction, and `ECReconstructionMetrics.getReconstructionTotal()`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/storage/TestContainerCommandsEC.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/upgrade/TestDNDataDistributionFinalization.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/upgrade/TestDNDataDistributionFinalization.java

Purpose: integration tests for datanode-side behavior of the `STORAGE_SPACE_DISTRIBUTION` layout feature during upgrade finalization. It focuses on pending deletion statistics on `KeyValueContainerData` before and after the feature is finalized, plus metadata recalculation behavior when pending-delete fields are absent.

Important APIs/types/functions: `TestDNDataDistributionFinalization`, `init`, `testDataDistributionUpgradeScenario`, `testMissingPendingDeleteMetadataRecalculation`, `validatePreDataDistributionFeatureState`, `validatePostDataDistributionFeatureState`, `validateContainerPendingDeletions`, `validateRecalculationScenario`. It uses `MiniOzoneHAClusterImpl`, `UniformDatanodesFactory`, `SCMConfigurator`, `StorageContainerLocationProtocol`, `OzoneBucket`, `KeyValueContainer`, `KeyValueContainerData`, and `VersionedDatanodeFeatures`.

Control flow: `init` creates a 3-SCM/3-DN HA cluster initialized at `HBASE_SUPPORT`, with DNs explicitly starting at `INITIAL_VERSION`, short heartbeat/block-deletion intervals, no safe-mode wait, and an SCM finalization executor disabled through configurator. It creates a random volume/bucket. The main scenario writes two keys, deletes one to create pending deletion data, validates pre-finalization container statistics, launches `finalizeScmUpgrade` on a background executor, waits for finalization from the SCM client, confirms SCM metadata layout version reaches `STORAGE_SPACE_DISTRIBUTION`, writes/deletes more keys, and validates post-finalization statistics. The recalculation test writes and deletes one key, finalizes, then walks DN containers to confirm pending-delete statistics remain valid.

State and persistence: state lives in the real mini-cluster SCM layout version, datanode layout version managers, OM key/delete operations, container sets on each DN, and `KeyValueContainerData` statistics. It does not directly mutate metadata tables; instead it creates natural pending delete state by writing/deleting keys.

Dependencies and integration points: Ozone HA cluster builder, SCM upgrade finalization RPC, SCM and DN layout managers, block deleting service intervals, client volume/bucket/key APIs, datanode container controllers, and `TestHddsUpgradeUtils.waitForFinalizationFromClient`.

Risks: assertions around `VersionedDatanodeFeatures.isFinalized` are partly guarded by a possible null DN layout version manager, which weakens signal in some test environments. Pending deletion byte-count assertions are broad (`>= 0`) except pre-finalization expecting zero bytes, so this is more smoke/regression coverage than precise accounting. The executor created for finalization is not explicitly shut down.

Test signals: verifies initial SCM MLV, post-finalization MLV, valid container statistics, block pending deletion counts nonnegative, post-finalization pending deletion bytes nonnegative, and pre-finalization pending deletion bytes zero.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/upgrade/TestDNDataDistributionFinalization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/upgrade/TestHDDSUpgrade.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/upgrade/TestHDDSUpgrade.java

Purpose: broad HA integration suite for SCM and datanode HDDS layout upgrade finalization. It validates the happy path from initial layout to latest and many failure-injection combinations across SCM restart, DN restart, and simultaneous SCM/DN disruption at upgrade finalizer checkpoints.

Important APIs/types/functions: `TestHDDSUpgrade`, `initClass`, `init`, `shutdown`, `loadSCMState`, `createKey`, `createTestContainers`, `testFinalizationFromInitialVersionToLatestVersion`, injection helpers `injectSCMFailureDuringSCMUpgrade`, `injectDataNodeFailureDuringSCMUpgrade`, `injectDataNodeFailureDuringDataNodeUpgrade`, `injectSCMAndDataNodeFailureTogetherAtTheSameTime`, many `test*Failures*` methods, and `testFinalizationWithFailureInjectionHelper`. It relies on `MiniOzoneClusterProvider`, `InjectedUpgradeFinalizationExecutor`, `BasicUpgradeFinalizer`, `SCMUpgradeFinalizationContext`, `StorageContainerManager`, `PipelineManager`, `ContainerManager`, and `TestHddsUpgradeUtils`.

Control flow: class setup builds a reusable HA cluster provider with 3 SCMs, 3 DNs, initial SCM/OM/DN layout versions, constrained pipeline counts, and short heartbeat intervals. Each test obtains a cluster, reloads live SCM managers, creates a RATIS THREE container/key, checks pre-upgrade state, starts finalization, then either waits or injects failure at configured `UpgradeTestInjectionPoints`. SCM failure restarts the SCM and starts a new finalize call from another thread. DN failure restarts one or all DNs. Combined failure restarts all DNs and an SCM under synchronization. The helper polls finalization progress, retries finalization if status returns `FINALIZATION_REQUIRED`, validates post-upgrade SCM/DN state, waits for DNs to return HEALTHY, and verifies post-upgrade pipeline creation or a valid "all DNs already used" reason.

State and persistence: real SCM metadata layout versions, DN layout versions, OM layout initialization, container states, open/closed pipelines, HA cluster state, client-created keys, and finalization checkpoints. The provider keeps cluster lifecycle outside individual test construction, while tests explicitly destroy/reinitialize clusters after looped fault cases.

Dependencies and integration points: MiniOzone HA, injected upgrade executor hooks, SCM Ratis/HA behavior, DN upgrade finalizers, Hadoop RPC/Ozone client APIs, pipeline/container protocol calls, and asynchronous threads.

Risks: annotated flaky/slow; nested loops over all injection points can be expensive. Synchronization is used around cluster mutation, but multiple helper threads still make timing important. Some failure helpers swallow exceptions into `testPassed`, so diagnosis can depend on logs. `createKey` uses fixed volume/bucket/key names per fresh cluster.

Test signals: pre/post layout version checks, container lifecycle expectations, pipeline freeze/recreation effects through utility assertions, finalization statuses `STARTING_FINALIZATION`, `FINALIZATION_DONE`, `ALREADY_FINALIZED`, DN node states HEALTHY/HEALTHY_READONLY, and successful client key creation after upgrade.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/upgrade/TestHDDSUpgrade.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/upgrade/TestHddsUpgradeUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/upgrade/TestHddsUpgradeUtils.java

Purpose: shared assertion/wait helpers for HDDS upgrade integration tests. It centralizes expected pre-upgrade and post-upgrade SCM/DN states, finalization polling, and SCM-visible datanode health checks.

Important APIs/types/functions: `waitForFinalizationFromClient`, `testPreUpgradeConditionsSCM`, `testPostUpgradeConditionsSCM` for list and single SCM, `testPreUpgradeConditionsDataNodes`, `testPostUpgradeConditionsDataNodes`, and `testDataNodesStateOnSCM` for list and single SCM. It uses `StorageContainerLocationProtocol`, `StorageContainerManager`, `HDDSLayoutVersionManager`, `FinalizationCheckpoint`, `PipelineManager`, `ContainerInfo`, `HddsDatanodeService`, `DatanodeStateMachine`, and `ContainerProtos.ContainerDataProto.State`.

Control flow: finalization polling repeatedly queries `queryUpgradeFinalizationProgress` until `FINALIZATION_DONE` or `ALREADY_FINALIZED`. Pre-SCM checks require initial MLV and all containers OPEN. Post-SCM checks require checkpoint crossing `FINALIZATION_COMPLETE`, MLV equal to SLV, at least one open RATIS THREE pipeline, SCM node health HEALTHY or HEALTHY_READONLY, and all containers in closed/deleting/quasi-closed states. Pre-DN checks require DN MLV 0 and open containers. Post-DN checks wait for every DN upgrade status to finish, then assert MLV equals SLV and containers are in provided closed states or default CLOSED/QUASI_CLOSED. Node-state helpers iterate all SCM-known nodes and compare health to expected/alternate states.

State and persistence: no own persistence; it observes live SCM metadata layout versions, finalization checkpoints, pipeline manager state, DN version managers, container controllers, and SCM node manager health.

Dependencies and integration points: JUnit assertions, AssertJ, `GenericTestUtils.waitFor`, `LambdaTestUtils.await`, SCM node manager, pipeline manager, and datanode upgrade status RPCs.

Risks: wait durations are fixed and broad, which can make failures slow. It assumes at least one RATIS THREE pipeline after upgrade and at least one pre-upgrade container for DN preconditions. Alternate node-state support deliberately accepts timing races, so tests using it trade precision for stability.

Test signals: this file is not itself a test class but provides core pass/fail signals for upgrade suites: layout version equality/progression, finalization checkpoint crossing, pipeline availability, container state closure, and DN health transitions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/upgrade/TestHddsUpgradeUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/upgrade/TestScmDataDistributionFinalization.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/upgrade/TestScmDataDistributionFinalization.java

Purpose: integration coverage for SCM-side `STORAGE_SPACE_DISTRIBUTION` finalization and deleted-block summary accounting in SCM HA. It verifies empty and non-empty clusters, old-format vs new-format deletion transactions, leader transfer, transaction removal, and block deletion service confirmation.

Important APIs/types/functions: `init`, `testFinalizationEmptyClusterDataDistribution`, `testFinalizationNonEmptyClusterDataDistribution`, `generateDeletedBlocks`, `findLastTx`, `waitForScmsToFinalize`, `waitForScmToFinalize`, `flushDBTransactionBuffer`, `getRowsInTable`. It uses `MiniOzoneHAClusterImpl`, `StorageContainerManager`, `DeletedBlockLogImpl`, `SCMDeletedBlockTransactionStatusManager`, `SCMHADBTransactionBuffer`, `DeletedBlocksTransaction`, `DeletedBlock`, `Table`, and `TestDataUtil`.

Control flow: `init` builds a 3-SCM/3-DN HA cluster at `HBASE_SUPPORT`, shortens heartbeats, command/container/pipeline reports and deletion intervals, creates a bucket, and optionally launches finalization asynchronously. The empty-cluster test finalizes, waits for all SCM checkpoints, asserts empty summaries, injects old-format transactions without size data, removes them, injects new-format transactions with size data, checks aggregate transaction/block/byte/replicated-byte counts, waits for deletion service cleanup, and exercises summary behavior when old and already-removed transactions are removed. The non-empty test stops SCM block deletion services, injects old-format txs before finalization, finalizes, writes/deletes an actual RATIS key, waits for non-empty summary, transfers leadership to verify summary replication, restarts deletion services, closes the container to allow deletion, waits summary count to zero, then transfers leadership back and confirms empty summary.

State and persistence: real SCM metadata DB deleted block TX table, HA transaction buffer flushes, deleted-block status manager summaries, SCM finalization checkpoint, SCM leadership, container state, and block deletion service state. The helper directly iterates RocksDB-backed tables and flushes HA buffers.

Dependencies and integration points: SCM HA/Ratis, Ozone client key deletion, block manager/deleted block log, protobuf summary objects, `TestHddsUpgradeUtils`, `GenericTestUtils.waitFor`, and `TestDataUtil`.

Risks: annotated flaky for empty-cluster path. Uses randomized block IDs and direct DB-table inspection. Exact accounting differs for old-format entries with `SIZE_NOT_AVAILABLE`, so future schema changes need careful updates. Repeated `setTimeDuration` for block deletion interval is redundant but harmless.

Test signals: verifies empty/non-empty summary equality, exact total transaction count, block count, logical size, replicated size, last tx presence, leader-transfer consistency, deletion-service clearing, and post-upgrade SCM/DN conditions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/upgrade/TestScmDataDistributionFinalization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/upgrade/TestScmHAFinalization.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/upgrade/TestScmHAFinalization.java

Purpose: SCM HA-specific upgrade finalization tests. It validates finalization survival across leader loss, full SCM restart, inactive SCM snapshot catch-up, and mid-finalization checkpoint semantics including pipeline creation freeze/unfreeze.

Important APIs/types/functions: `init`, `injectionPointsToTest`, `testFinalizationWithLeaderChange`, `testFinalizationWithRestart`, `testSnapshotFinalization`, `waitForScmsToFinalize`, `waitForScmToFinalize`, `checkMidFinalizationConditions`. It uses `UpgradeTestUtils.newPausingFinalizationExecutor`, `newTerminatingFinalizationExecutor`, `DefaultUpgradeFinalizationExecutor`, `FinalizationCheckpoint`, `FinalizationStateManagerImpl`, `MiniOzoneHAClusterImpl`, and `StorageContainerLocationProtocol`.

Control flow: `init` starts a 3-SCM HA cluster at initial layout version with configurable inactive SCM count and immediately submits `finalizeScmUpgrade` on a background executor. Parameterized tests pause/terminate finalization after pre-finalize, complete-finalization, or post-finalize checkpoints. Leader-change test stops the active leader during the pause, waits for new leadership, validates mid-state on remaining SCMs, restarts the old leader as follower, resumes finalization, waits for client and all SCMs. Restart test terminates at a checkpoint, switches new SCMs to normal finalization executor, restarts all SCMs, validates persisted mid-state, and relies on automatic resume after election. Snapshot test leaves one SCM inactive, finalizes active SCMs, advances SCM raft log by allocating/closing containers, starts inactive SCM, and checks it finalizes via snapshot install.

State and persistence: SCM HA finalization checkpoint, pipeline creation frozen flag, SCM metadata layout version, raft log/snapshot state, inactive SCM startup state, and DN finalization. Log capture observes snapshot receipt.

Dependencies and integration points: SCM HA Ratis, SCM client failover, upgrade finalization executors, latches/futures for controlled concurrency, `TestHddsUpgradeUtils`, and mini-cluster SCM lifecycle methods.

Risks: restart test is marked flaky. Client futures may complete after IOException from interrupted leader, which is expected. Mid-finalization assertions account for leader-applied raft entries while followers may lag, so they use "at least one" and filtered all-match checks rather than all-SCM equality.

Test signals: finalization checkpoint crossing, pipeline creation freeze at `FINALIZATION_STARTED`, unfreeze at later checkpoints, leadership change, all SCMs reaching `FINALIZATION_COMPLETE`, post-upgrade SCM/DN assertions, and log evidence for snapshot-based metadata layout catch-up.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/upgrade/TestScmHAFinalization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/utils/ClusterContainersUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/utils/ClusterContainersUtil.java

Purpose: test utility for locating, corrupting, verifying, and retrieving container data on disk inside a `MiniOzoneCluster`.

Important APIs/types/functions: `getChunksLocationPath`, `corruptData`, `verifyOnDiskData`, `getContainerByID`. It uses `OzoneKeyDetails`, `KeyValueContainerData`, `BlockUtils.getDB`, `DBHandle`, `BlockData`, `KeyValueContainerLocationUtil`, Apache Commons `FileUtils`, and DN `ContainerSet`.

Control flow: `getChunksLocationPath` requires the provided `OzoneKey` to be `OzoneKeyDetails`, extracts the first key location's container ID and local ID, opens the key-value container DB, verifies the block exists via block key lookup, then computes the chunks directory from the container volume root, cluster ID and container ID. `corruptData` gets that directory and overwrites every top-level chunk file with `"corrupted data"`. `verifyOnDiskData` reads every top-level chunk file and returns false on first content mismatch. `getContainerByID` scans all datanodes and returns the first matching container from each DN state machine's container set.

State and persistence: this utility directly reads and writes on-disk chunk files and opens the container DB. Corruption is destructive to the mini-cluster's test data and intended only for tests that isolate their cluster state.

Dependencies and integration points: MiniOzoneCluster configuration and cluster ID, datanode container sets, key-value container DB layout, block metadata keys, and chunk path layout helper. It bridges Ozone client metadata (`OzoneKeyDetails`) to DN local storage.

Risks: only the first key location is considered, so multi-block or EC keys may not be fully handled. Chunk file listing is non-recursive. `verifyOnDiskData` reads using default charset while corruption writes UTF-8 bytes, which is fine for ASCII test strings but not arbitrary binary chunks. Direct file mutation can invalidate checksums and affect later tests.

Test signals: not a test class; downstream tests use it to assert a block exists, force corruption, verify chunk content, or locate a container replica.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/utils/ClusterContainersUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/utils/db/managed/TestRocksObjectLeakDetector.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/utils/db/managed/TestRocksObjectLeakDetector.java

Purpose: manual/unhealthy integration test for managed RocksDB object leak detection metrics. It intentionally creates leaked managed Rocks objects and expects cluster shutdown to fail because leaked objects remain.

Important APIs/types/functions: `setUp`, `cleanUp`, `testLeakDetector`, generic `testLeakDetector(Supplier<T>)`, and `allocate`. It exercises many managed wrappers: `ManagedBloomFilter`, `ManagedColumnFamilyOptions`, `ManagedEnvOptions`, `ManagedFlushOptions`, `ManagedIngestExternalFileOptions`, `ManagedLRUCache`, `ManagedOptions`, `ManagedReadOptions`, `ManagedSlice`, `ManagedStatistics`, `ManagedWriteBatch`, and `ManagedWriteOptions`.

Control flow: setup enables RocksDB statistics (`OZONE_METADATA_STORE_ROCKSDB_STATISTICS=ALL`) and starts a MiniOzoneCluster. The test iterates wrapper suppliers. For each type, it snapshots total managed objects and leak objects, allocates and closes one object, runs GC and sleeps for leak detector background processing, then expects total object count to increase but leak count unchanged. It then allocates another object without closing it, runs GC/sleeps again, and expects both total object count and leak count to increase. Cleanup asserts that `cluster.shutdown()` throws `AssertionError`, matching the intentional leak behavior.

State and persistence: process-global `ManagedRocksObjectMetrics.INSTANCE` counters, native RocksDB object lifetimes, GC/finalizer/leak detector timing, and MiniOzoneCluster resources. The leaked objects are intentionally not closed.

Dependencies and integration points: managed RocksDB wrappers, Ozone metadata store statistics, JUnit `@Unhealthy`, MiniOzoneCluster, JVM GC behavior, and leak detector background tasks.

Risks: explicitly documented as manual-only and flaky because background processes can allocate additional managed Rocks objects, invalidating exact counter deltas. Sleep-based timing and GC are nondeterministic. Running it with normal suites can poison later tests by leaving leak metrics and leaked native objects.

Test signals: exact counter assertions for total managed objects and leak objects, plus expected shutdown `AssertionError`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/utils/db/managed/TestRocksObjectLeakDetector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/ClientConfigForTesting.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/ClientConfigForTesting.java

Purpose: fluent test helper that applies coherent Ozone client stream, chunk, block, and data-stream buffer sizes to a mutable configuration.

Important APIs/types/functions: `newBuilder(StorageUnit)`, setters for chunk size, block size, stream buffer size, stream buffer flush/max sizes, data stream flush/window/min packet sizes, `applyTo`, and `toBytes`. It writes to `OzoneClientConfig`, `OZONE_SCM_CHUNK_SIZE_KEY`, and `OZONE_SCM_BLOCK_SIZE`.

Control flow: callers choose an input `StorageUnit`, chain optional setters, then call `applyTo`. Missing values are defaulted from the chunk size: stream buffer size and flush size default to chunk size, stream max to twice flush, data-stream flush to four chunks, data min packet to quarter chunk, data window to eight chunks, and block size to twice stream max. The helper then mutates the typed `OzoneClientConfig`, writes it back with `setFromObject`, and stores chunk/block sizes as bytes.

State and persistence: no persistence beyond configuration mutation. The builder object is stateful: `applyTo` fills null fields, so subsequent setter calls after `applyTo` operate on already-defaulted values.

Dependencies and integration points: HDDS configuration object mapping, `StorageUnit` conversion, Ozone client stream tuning, SCM chunk size, and Ozone block size. It is intended for tests needing small deterministic block/chunk boundaries.

Risks: conversion uses `Math.round(unit.toBytes(value))`, and integer fields cast to `int`; oversized units/values can overflow for int-backed settings. Defaulting mutates the builder, so reuse across tests may leak choices. No validation enforces block size relative to stream max if caller sets inconsistent values manually.

Test signals: no tests in this file; downstream tests can infer behavior by checking generated key/block/chunk splitting under controlled config sizes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/ClientConfigForTesting.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/OzoneTestUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/OzoneTestUtils.java

Purpose: shared Ozone integration-test utilities for closing containers, operating on containers that back a key, asserting OM exceptions, flushing deleted block logs, and waiting for block deletion.

Important APIs/types/functions: `triggerCloseContainerEvent`, `closeContainers`, `closeAllContainers`, `performOperationOnKeyContainers`, `expectOmException`, `closeContainer`, `flushAndWaitForDeletedBlockLog`, `waitBlockDeleted`. It integrates with `StorageContainerManager`, `SCMEvents`, `EventPublisher`, `OmKeyLocationInfoGroup`, `BlockID`, `ContainerInfo`, `Pipeline`, and OM/SCM metadata APIs.

Control flow: key-container operations iterate key location groups and each `OmKeyLocationInfo`, extract `BlockID`, and pass it to a checked consumer. Triggering close fires `SCMEvents.CLOSE_CONTAINER`; direct close transitions OPEN containers through FINALIZE and CLOSING containers through CLOSE, then asserts the container is not open. `closeAllContainers` fires close events for every SCM container. `expectOmException` wraps a callable and compares result code. `closeContainer` closes the container's pipeline and waits until the `ContainerInfo` state becomes CLOSED. Deleted-block helpers repeatedly flush the SCM HA transaction buffer and poll valid transaction count until nonzero or zero.

State and persistence: observes and mutates SCM container lifecycle state, event queue, pipeline state, SCM HA transaction buffer, and deleted block log. No independent storage.

Dependencies and integration points: SCM event framework, container manager state machine, pipeline manager, OM key-location metadata, `GenericTestUtils.waitFor`, `LambdaTestUtils.VoidCallable`, and Ratis checked consumers.

Risks: direct state transitions can bypass parts of normal datanode reporting. `closeContainer` waits on the passed `ContainerInfo` object, which must reflect updates. Deleted-block helpers swallow IOExceptions inside polling lambdas, potentially hiding transient failures until timeout. `closeAllContainers` is asynchronous because it only fires events.

Test signals: downstream tests use these helpers to assert specific OM exception codes, force/observe container closure, and wait for deleted block log state transitions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/OzoneTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/RatisTestHelper.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/RatisTestHelper.java

Purpose: static helper interface for Ratis-related Ozone integration tests. It configures Ratis transport and exposes datanode raft server division/state-machine/role lookup for a pipeline.

Important APIs/types/functions: `initRatisConf`, `initXceiverServerRatis`, `getRaftServerDivision`, `getStateMachine`, `isRatisLeader`, and `isRatisFollower`. It uses `RatisHelper`, `XceiverServerRatis`, `RaftClient`, `RaftPeer`, `RaftServer.Division`, `StateMachine`, `RpcType`, and Ozone Ratis configuration keys.

Control flow: `initRatisConf` enables container Ratis, selects RPC type, shortens container report interval, and extends SCM stale node interval. `initXceiverServerRatis` converts a datanode to a raft peer, opens a short-lived Raft client, and adds a raft group for the pipeline. `getRaftServerDivision` first verifies the pipeline includes the datanode, casts the datanode write channel to `XceiverServerRatis`, and looks up the server division by raft group ID. Role/state-machine helpers delegate to that division.

State and persistence: mutates test configuration and raft group membership. Reads live raft server state from a datanode process.

Dependencies and integration points: HDDS Ratis helpers, datanode write channel, Ratis group management API, pipeline membership and raft group conversion.

Risks: assumes the DN write channel is Ratis-backed; callers must configure/start cluster accordingly. Throws `IllegalArgumentException` for non-member DNs. Role checks are instantaneous and may race with leader election.

Test signals: downstream tests can assert leader/follower role, inspect state machine, or initialize raft groups without duplicating Ratis boilerplate.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/RatisTestHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestBlockTokens.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestBlockTokens.java

Purpose: secure HA integration tests for block token validation against SCM secret key rotation, expiry, unknown key IDs, and invalid token passwords.

Important APIs/types/functions: `init`, `createTestData`, `blockTokensHappyCase`, `blockTokenFailsOnExpiredSecretKey`, `blockTokenOnExpiredSecretKeyRetrySuccessful`, `blockTokenFailsOnWrongSecretKeyId`, `blockTokenFailsOnWrongPassword`, `extractSecretKeyId`, `getTestKeyInfo`, `readData`, secure setup helpers, and `startCluster`. It uses MiniKdc, `MiniOzoneHAClusterImpl`, `SecretKeyManager`, `ManagedSecretKey`, `OzoneBlockTokenIdentifier`, `KeyInputStream`, `BlockInputStreamFactoryImpl`, and Ozone client/OM key metadata.

Control flow: setup disables system exits, starts MiniKdc, writes Kerberos principals/keytabs for SCM/OM/DN/SPNEGO/test user, configures secret-key rotate/check/expiry durations, enables block/container tokens, starts a 3-SCM/1-OM secure HA cluster, creates one test key, and retains a client. The happy case confirms key metadata token uses the current SCM key, reads from DNs, waits for key rotation, then verifies old token still works before expiry. Expiry failure waits until the signing secret key expires and expects `BLOCK_TOKEN_VERIFICATION_FAILED`. Retry success uses `KeyInputStream` retry callback to fetch fresh key info after expiry. Wrong-key and wrong-password tests mutate embedded block tokens in `OmKeyLocationInfo` and assert verification failure messages.

State and persistence: Kerberos keytabs in temp dir, secure Ozone cluster, SCM secret key manager state, OM key metadata tokens, client-side mutated token objects, and stream reads from datanodes. Test disables checksum verification to isolate token behavior.

Dependencies and integration points: Hadoop security/Kerberos, SCM secret key rotation, OM-generated key info, datanode block token verifier, `KeyInputStream` retry path, HA SCM active selection.

Risks: timing depends on short secret-key durations and `waitFor` polling. Mutating token objects in returned key info assumes in-memory metadata objects are isolated enough for the test. Static cluster and KDC lifecycle make failures expensive. Uses same Kerberos principal strings for several services in test mode.

Test signals: exact secret key ID match, successful 100-byte reads, expired-key verification result/message, retry recovery, unknown secret-key message, and invalid password message.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestBlockTokens.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestBlockTokensCLI.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestBlockTokensCLI.java

Purpose: secure HA integration tests for Ozone admin CLI operations around block-token secret keys: OM fetch-key and SCM rotate-key with and without force.

Important APIs/types/functions: `init`, `testFetchKeyOMAdminCommand`, `testFetchKeyOMAdminCommandUtil`, `testRotateKeySCMAdminCommandWithForceFlag`, `testRotateKeySCMAdminCommandWithoutForceFlag`, `testRotateKeySCMAdminCommandUtil`, `shouldRotate`, `createArgsForCommand`, secure setup helpers, and `startCluster`. It uses `OzoneAdmin`, `MiniKdc`, `MiniOzoneHAClusterImpl`, `SecretKeyManager`, `ManagedSecretKey`, `ScmConfig`, `SCMHTTPServerConfig`, and config diffing via Guava `Maps.difference`.

Control flow: setup gets the admin command's configuration, starts MiniKdc, sets secure Kerberos principals/keytabs, enables block/container tokens, starts a 3-SCM/3-OM HA secure cluster with service IDs, and creates a client. Fetch-key redirects `System.out` to a byte stream, runs `ozoneAdmin.execute("om", "fetch-key", "--service-id=...")`, parses `Current Secret Key ID:`, and compares it to the active SCM secret key. Rotate tests wait for SCM leader, construct host:port and augmented `--set=key=value` args for secure/HA config differences, run `scm rotate`, and compare current secret key before/after based on `--force` or elapsed rotation duration.

State and persistence: process global stdout is temporarily replaced, MiniKdc keytabs and secure cluster state are created, SCM secret key manager current key may rotate, and admin command configuration is patched through CLI `--set` options.

Dependencies and integration points: Ozone admin shell, SCM/OM HA service IDs, Kerberos configuration, SCM secret-key rotation policy, and `SecretKeyConfig.parseRotateDuration`.

Risks: `System.setOut(System.out)` after redirection does not preserve the original PrintStream if it was already changed; a local saved original would be safer. Non-force rotation can be timing-sensitive because it depends on current key age. Config diff only handles entries present on the secure test config and absent from default admin config.

Test signals: fetched UUID equals active SCM current key ID; forced rotate changes current key; non-forced rotate changes only if configured rotation duration has elapsed; cluster leader presence is awaited.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestBlockTokensCLI.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestContainerBalancerOperations.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestContainerBalancerOperations.java

Purpose: integration tests for SCM container balancer client operations exposed through `ContainerOperationClient`: start, stop, status, CLI-option/config precedence, include/exclude container parsing, and idempotent stop.

Important APIs/types/functions: `setup`, `cleanup`, `testContainerBalancerCLIOperations`, `testIfCBCLIOverridesConfigs`, `testStopBalancerIdempotent`, and `parseContainerIDs`. It uses `MiniOzoneCluster`, `ContainerOperationClient`, `ScmClient`, `ContainerBalancerConfiguration`, `SCMContainerPlacementCapacity`, and `ContainerID`.

Control flow: setup starts a 3-DN cluster with capacity placement policy, node report interval 5 seconds, and DU trigger before move enabled. The first test asserts balancer initially stopped, starts it with a full set of optional CLI values, verifies running, waits until it stops naturally, starts it again, then stops it explicitly. Config precedence test mutates `ozoneConf` values for iterations and max datanode percentage, starts with some optionals empty and others present, inspects the live balancer config from SCM, and asserts defaults, config values, and CLI overrides are selected correctly. Stop-idempotent test calls stop while already stopped, starts/stops, then calls stop again under `assertDoesNotThrow`.

State and persistence: live SCM container balancer state/config, cluster configuration, and balancer runtime thread status. No durable output beyond cluster metadata.

Dependencies and integration points: SCM CLI client, container balancer service, placement policy class binding, node reports/DU, optional CLI argument mapping, and `GenericTestUtils.waitFor`.

Risks: tests do not create intentional imbalance or assert actual move plans; they primarily validate command plumbing. Natural stop timing can depend on balancer internals and cluster state. Shared static `ozoneConf` and client across tests means config mutations can persist within the class.

Test signals: balancer status false/true/false transitions, no exception from idempotent stop, and exact config values for balancing interval, iterations, max datanode percentage, excluded containers, and included containers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestContainerBalancerOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestCpuMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestCpuMetrics.java

Purpose: abstract non-HA integration test that verifies SCM Prometheus metrics endpoint exposes JVM CPU metrics.

Important APIs/types/functions: `TestCpuMetrics` implements `NonHATests.TestCase`, has an `OkHttpClient`, and one test method `testCpuMetrics`. It uses `cluster()` from the test-case interface, `HddsUtils.getPortNumberFromConfigKeys`, `OZONE_SCM_HTTP_ADDRESS_KEY`, OkHttp `Request`/`Response`, and AssertJ.

Control flow: it builds `http://localhost:<scm-http-port>/prom` from cluster configuration, performs an HTTP GET, reads the response body as a string, and asserts the body contains `jvm_metrics_cpu_available_processors`, `jvm_metrics_cpu_system_load`, and `jvm_metrics_cpu_jvm_load`.

State and persistence: no own persistence. It observes the running SCM HTTP server and metrics registry exposed by the non-HA test cluster.

Dependencies and integration points: SCM HTTP endpoint, Prometheus metrics servlet, JVM metrics source, OkHttp, and the non-HA test harness that supplies the cluster.

Risks: assumes the SCM HTTP address resolves to localhost and the port is present in config. It does not assert HTTP status code or close the response explicitly beyond reading the body, relying on OkHttp cleanup. Metric names are exact string checks and will fail on metrics rename/export format changes.

Test signals: non-null response body and presence of three CPU metric names in `/prom` output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestCpuMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestDataUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestDataUtil.java

Purpose: general-purpose Ozone integration-test data factory and metadata cleanup utility for volumes, buckets, keys, linked buckets, and OM tables.

Important APIs/types/functions: overloads of `createVolumeAndBucket`, `createVolume`, `createStringKey`, `createOutputStream`, `createKey`, `readFully`, `getKey`, `createBucket`, `createLinkedBucket`, `createKeys`, `cleanupDeletedTable`, `cleanupOpenKeyTable`, and `lookupOmKeyInfo`. It uses Ozone client APIs, `BucketArgs`, `VolumeArgs`, `DefaultReplicationConfig`, `ReplicationConfig`, `BucketLayout`, `OmKeyArgs`, `OmKeyInfo`, `RepeatedOmKeyInfo`, and OM metadata `Table`.

Control flow: volume/bucket helpers construct storage type DISK and optional bucket layout/default replication, create a random owner/admin volume, then create/get buckets. Random helper retries up to five times on volume/bucket name collisions. Key helpers generate random alphanumeric content or write provided bytes through optional replication config, then read fully or return string content. Linked bucket helper creates a source bucket then a linked bucket with `sourceVolume/sourceBucket`. `createKeys` opens a cluster client, creates a bucket, writes N RATIS ONE keys, and returns OM key info for each. Cleanup helpers iterate deleted/open key tables, collect keys, and delete them while ignoring per-key IOExceptions.

State and persistence: creates real OM metadata entries and key data in the cluster. Cleanup mutates OM metadata tables directly, bypassing normal service flows.

Dependencies and integration points: Ozone object store, OM metadata manager, bucket layouts, replication configs, Apache Commons random strings/IO, Guava maps, and MiniOzoneCluster.

Risks: direct metadata table deletion can leave related state inconsistent if used outside targeted tests. Cleanup silently ignores delete failures. Random names reduce but do not eliminate collisions. `getKey` uses Scanner with whole-stream delimiter, which assumes textual content and non-empty stream.

Test signals: no test methods; downstream tests use it to create reproducible data and assert reads do not throw, returned key info exists, and OM tables can be reset for isolation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestDataUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestDelegationToken.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestDelegationToken.java

Purpose: secure Ozone integration test for OM delegation token lifecycle and Hadoop RPC authentication behavior, parameterized by token service using host names or IPs.

Important APIs/types/functions: `init`, `stop`, MiniKdc helpers, `setSecureConfig`, `initSCM`, `testDelegationToken(boolean useIp)`, `generateKeyPair`, and `setupOm`. It uses `StorageContainerManager`, `OzoneManager`, `OzoneManagerProtocolClientSideTranslatorPB`, `OmTransportFactory`, `OzoneTokenIdentifier`, `UserGroupInformation`, `MiniKdc`, SCM/OM storage config, `HASecurityUtils`, and audit log capture.

Control flow: each test creates a secure configuration with random ports, metadata dirs, Kerberos auth, MiniKdc principals/keytabs, SCM security initialization, and an OM key pair. The test starts a simple SCM, captures Hadoop RPC audit logs, configures `SecurityUtil.setTokenServiceUseIp`, creates and starts a secure OM with certificate and topology test clients, closes unrelated SCM clients to force fresh RPC handshakes, then obtains an OM client via Kerberos. It requests a delegation token, renews it, validates token kind/service, closes the Kerberos client, installs the token on a remote UGI using TOKEN auth, creates a new OM client as that UGI, confirms token-authenticated operation reaches OM by expecting `VOLUME_NOT_FOUND` on `deleteVolume`, verifies renewal fails under token auth with `INVALID_AUTH_METHOD`, switches back to Kerberos, cancels the token, waits for client timeout, then confirms further cancellation via the token-authenticated client fails with `TOKEN_ERROR_OTHER`.

State and persistence: Kerberos KDC/keytabs, SCM version/security files, OM version/cert metadata, generated HDDS key pair, UGI login user global state, Hadoop RPC client cache/connection state, OM delegation token cache, and audit logs.

Dependencies and integration points: Hadoop security, MiniKdc, SCM security bootstrap, OM RPC translator, token service construction, UGI auth modes, Hadoop RPC audit logging, and OM exception mapping.

Risks: manipulates global UGI login user and token-service-use-IP flag; failures can leak state into later tests. Sleep-based client timeout is coarse. Log assertions depend on audit message text. The comments highlight Hadoop RPC client caching as a critical subtlety.

Test signals: token issuance/renewal, token kind/service, token-authenticated RPC success, renewal rejection with token auth, cancellation success, post-cancel token failure, and expected OM result codes/log messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestDelegationToken.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestGetClusterTreeInformation.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestGetClusterTreeInformation.java

Purpose: abstract HA integration test for SCM network topology serialization/deserialization through the block location protocol client.

Important APIs/types/functions: `TestGetClusterTreeInformation` implements `HATests.TestCase`, has `init` and `testGetClusterTreeInformation`. It uses `SCMBlockLocationFailoverProxyProvider`, `ScmBlockLocationProtocolClientSideTranslatorPB`, `StorageContainerManager`, `InnerNode`, and `NetConstants.ROOT`.

Control flow: `@BeforeAll` captures the HA cluster configuration and active SCM from the test harness. The test creates a failover proxy provider, forces the current proxy to the SCM node ID under test, builds the protobuf translator, obtains expected root `InnerNode` from `scm.getClusterMap().getNode(ROOT)`, fetches actual topology via `getNetworkTopology()`, and compares equality.

State and persistence: no own persistence; observes the live SCM cluster map and serialized topology returned over RPC.

Dependencies and integration points: HA cluster harness, SCM block location failover proxy, SCM block location protobuf client, SCM network topology tree, and `InnerNode` equality semantics.

Risks: equality is structural and depends on stable serialization of topology node attributes. The client is not explicitly closed. The test assumes the SCM selected by node ID is reachable and that the cluster map has root populated before the test.

Test signals: exact equality between SCM in-process root topology and RPC-returned topology.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestGetClusterTreeInformation.java -->
