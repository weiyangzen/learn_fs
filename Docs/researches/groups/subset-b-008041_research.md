# Research Group subset-b-008041

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerReportHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerReportHandler.java

## Purpose
`TestContainerReportHandler` is a broad unit test suite for SCM full container report handling. It exercises how `ContainerReportHandler` reconciles datanode full reports with SCM's container and replica state, including replica add/remove behavior, lifecycle transitions, EC replica-index validation, DELETING/DELETED resurrection rules, usage counters, and replica data checksums.

## Important APIs, Types, and Functions
The fixture uses a real `ContainerStateManagerImpl` backed by an SCM metadata `DBStore`, a `MockNodeManager`, and a mocked `ContainerManager` whose read and write methods delegate into the state manager. Important tested types include `ContainerReportHandler`, `ContainerReportFromDatanode`, `ContainerInfo`, `ContainerID`, `ContainerReplica`, `ContainerReplicaProto.State`, `LifeCycleState`, `ECReplicationConfig`, and `RatisReplicationConfig`. Helpers such as `getContainerReportsProto`, `getContainerReportFromDatanode`, `setupECContainerForTesting`, `createAndHandleContainerReport`, and `testReplicaIndexUpdate` construct report payloads with explicit state, BCSID, replica index, emptiness, key counts, bytes used, and checksums.

## Control Flow and State Behavior
`setup()` wires mocked `ContainerManager` calls to `containerStateManager.updateContainerStateWithSequenceId`, `updateContainerReplica`, `removeContainerReplica`, and `transitionDeletingOrDeletedToTargetState`, so invoking `reportHandler.onMessage(...)` mutates real in-memory and DB-backed SCM state. Full report reconciliation removes missing replicas for under-replication, adds unexpected replicas for over-replication, and updates node-container membership through `MockNodeManager`. Lifecycle tests assert CLOSING to CLOSED or QUASI_CLOSED transitions, QUASI_CLOSED to CLOSED transitions, and no state change when a CLOSED report has a lower mismatching BCSID.

EC-specific control flow validates that only replica index 1 or parity indexes can close a CLOSING EC container, and invalid replica indexes do not overwrite stored replica indexes. Usage aggregation differs by state and replication type: open RATIS containers use the minimum reported bytes/key count; non-open RATIS containers use the maximum; EC stats ignore non-authoritative data indexes and aggregate from replica index 1 or parity indexes with state-sensitive min/max behavior. DELETING/DELETED handling distinguishes empty stale replicas, non-empty RATIS replicas that can resurrect to CLOSED or QUASI_CLOSED, non-resurrecting EC replicas that receive force delete commands, and invalid/DELETED replica states that must not trigger resurrection.

## Dependencies and Integration Points
The suite integrates SCM metadata tables (`SCMDBDefinition.CONTAINERS`), HA stubs (`SCMHAManagerStub`), pipeline creation (`MockPipelineManager`), event dispatch (`SCMEvents.DATANODE_COMMAND`), and Ozone command emission (`CommandForDatanode`). It reuses `HddsTestUtils` factories and shares checksum helper methods with the incremental report test. Because the `ContainerManager` is mocked but delegates to real state-manager methods, the tests sit between pure unit tests and persistence-backed integration tests.

## Risks and Test Signals
The main risks covered are stale full reports corrupting SCM state, handler thread crashes on mismatched BCSIDs, incorrect EC replica-index acceptance, resurrecting containers that should stay deleted, and losing data checksum updates. Test signals are mostly direct assertions on container state, replica sets, replica indexes, usage counters, checksum fields, and `publisher.fireEvent` counts. A residual risk is that the fixture does not run a full SCM service stack; event side effects beyond publication are mocked.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerReportHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerStateManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerStateManager.java

## Purpose
`TestContainerStateManager` validates core `ContainerStateManagerImpl` behavior around replica tracking, lifecycle transitions, persistence reload, sequence-id handling, and stale-replica delete commands. It complements the report-handler tests by directly asserting state-manager APIs and by routing selected report-handler calls through a real state manager.

## Important APIs, Types, and Functions
The test fixture creates a `ContainerStateManagerImpl` with a real SCM DB table, mocked `PipelineManager`, `MockNodeManager`, mocked `ContainerManager`, `SCMContext`, and mocked `EventPublisher`. Important methods under test include `addContainer`, `getContainerReplicas`, `transitionDeletingOrDeletedToTargetState`, `getContainerIDs`, `reinitialize`, and `updateContainerStateWithSequenceId`. Helper methods `allocateContainer`, `addReplica`, `sendReportAndCaptureDeleteCommand`, `verifyForceDeleteCommand`, `verifyContainerState`, and `getContainerReportsProto` keep the scenarios focused.

## Control Flow and State Behavior
The first tests verify that adding two or three `ContainerReplica` entries produces the expected replica count independent of the replication factor. `testTransitionDeletingOrDeletedToTargetState` builds raw `ContainerInfoProto` records in DELETING or DELETED and asserts they can transition to CLOSED through the special transition API. The negative parameterized test confirms the same API rejects other lifecycle states such as CLOSING, QUASI_CLOSED, CLOSED, and RECOVERING by surfacing `InvalidContainerStateException`.

Stale replica tests use `ContainerReportHandler` with the mocked `ContainerManager` delegation to simulate deleted-container report handling. For DELETED RATIS containers, CLOSED replicas with equal or lower BCSID receive `DeleteContainerCommand` with `force=true`, and the container remains DELETED. For DELETING or DELETED EC containers, non-empty stale replicas are also force-deleted without changing the SCM lifecycle state.

Persistence-sensitive coverage includes `testGetContainerIDs`, which filters stored containers by lifecycle state, and `testReinitializeWithOpenContainerWithoutPipelineID`, which directly inserts an OPEN container with no pipeline ID into the SCM table and verifies `reinitialize` does not call `addContainerToPipelineSCMStart` with a null pipeline. `testSequenceIdOnStateUpdate` ensures newer sequence IDs advance state metadata while older sequence IDs are ignored after a later transition.

## Dependencies and Integration Points
This file depends on SCM DB definitions, HA stubs, protobuf lifecycle enums, pipeline IDs, replication configs, `DeleteContainerCommand`, and `SCMEvents.DATANODE_COMMAND`. It is an integration point between state-manager lifecycle validation and container report delete-command emission.

## Risks and Test Signals
The suite targets high-risk metadata corruption paths: illegal resurrection transitions, stale replica cleanup, missing pipeline IDs during SCM restart, and sequence-id regression. Signals include state assertions, captured command assertions, exception type checks, and Mockito verification of pipeline-manager calls. The tests use mocked managers for surrounding SCM services, so they validate state-manager semantics rather than full cluster behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerStateManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestIncrementalContainerReportHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestIncrementalContainerReportHandler.java

## Purpose
`TestIncrementalContainerReportHandler` tests the incremental-report counterpart to the full container report suite. It verifies that single-container deltas update SCM replica state, lifecycle state, node membership, and checksum metadata consistently, and that incremental and full reports do not race into inconsistent `NodeManager` and `ContainerStateManager` views.

## Important APIs, Types, and Functions
The central type is `IncrementalContainerReportHandler`, driven by `IncrementalContainerReportFromDatanode` and `IncrementalContainerReportProto`. The fixture uses a real `SCMNodeManager`, `NetworkTopologyImpl`, `EventQueue`, `SCMStorageConfig`, mocked `HDDSLayoutVersionManager`, `MockPipelineManager`, real `ContainerStateManagerImpl`, and mocked `ContainerManager`. Helpers include `getIncrementalContainerReportProto`, `setupECContainerForTesting`, `createAndHandleICR`, and `testReplicaIndexUpdate`. The file imports checksum helpers and full-report proto helpers from `TestContainerReportHandler`.

## Control Flow and State Behavior
The report handler is called through `reportHandler.onMessage(icrFromDatanode, publisher)`. Tests cover CLOSING to CLOSED, CLOSING to QUASI_CLOSED, and QUASI_CLOSED to CLOSED transitions for RATIS containers, plus EC-specific close eligibility based on replica indexes. A lower BCSID CLOSED report is deliberately sent against CLOSING and QUASI_CLOSED containers to assert the handler does not throw and leaves state unchanged. `testOpenWithUnhealthyReplica` verifies an UNHEALTHY incremental report for an OPEN container moves the SCM container to CLOSING.

Replica and node state mutation is covered by `testDeleteContainer`: a DELETED replica report removes one replica from the container-state manager and removes the container from the reporting datanode in `NodeManager`, while preserving other datanode memberships. `testICRFCRRace` runs full and incremental handlers concurrently using a two-thread executor for ten iterations; it asserts a container is present in both `NodeManager` and replica state, or in neither, preventing the HDDS-5249 split-brain condition.

Checksum tests mirror the full-report suite for incremental reports: absent `dataChecksum` leaves stored replica checksums zero, unique checksum reports update each replica independently, and later matching checksums converge all replica records. EC replica-index validation prevents invalid index 0 or out-of-range index 6 from replacing stored indexes and accepts valid index changes.

## Dependencies and Integration Points
This suite integrates with `SCMNodeManager` rather than `MockNodeManager`, giving stronger coverage for node registration and membership mutations. It also uses the SCM metadata DB, HA stub, pipeline manager, layout version manager, and event publisher. It shares lifecycle and checksum semantics with `ContainerReportHandler`, making it a regression guard for parity between FCR and ICR paths.

## Risks and Test Signals
Major risks are missed replica removals, inconsistent node/container state under report races, handler crashes on stale BCSIDs, EC index corruption, and checksum drift. Signals include direct lifecycle assertions, replica count assertions, node-container membership checks, concurrent consistency checks, and checksum equality over every replica.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestIncrementalContainerReportHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestUnknownContainerReport.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestUnknownContainerReport.java

## Purpose
`TestUnknownContainerReport` verifies how `ContainerReportHandler` reacts when a datanode reports a container that SCM cannot find. The test exists to guard the configurable behavior that unknown containers may either be ignored or deleted from the datanode.

## Important APIs, Types, and Functions
The test uses `ContainerReportHandler.UnknownContainerAction`, `ScmConfig.HDDS_SCM_UNKNOWN_CONTAINER_ACTION`, `ContainerReportFromDatanode`, `ContainerReportsProto`, `CommandForDatanode`, and `SCMEvents.DATANODE_COMMAND`. `setup()` creates a `MockNodeManager`, mocked `ContainerManager`, and event publisher; the mocked container manager always throws `ContainerNotFoundException.newInstanceForTesting()` from `getContainer`.

## Control Flow and State Behavior
`testUnknownContainerNotDeleted` sends a full report using a default `OzoneConfiguration`. Since no explicit unknown-container action is configured, the handler should not emit any datanode command. `testUnknownContainerDeleted` sets `HDDS_SCM_UNKNOWN_CONTAINER_ACTION` to `DELETE`, sends the same report, and verifies that one datanode command is published. `sendContainerReport` constructs the handler with `SCMContext.emptyContext()` and the supplied configuration, creates a CLOSED synthetic container only to obtain a container ID, selects an in-service healthy mock datanode, and invokes `onMessage`.

The report proto includes realistic size, usage, key-count, read/write, final hash, BCSID, and delete transaction fields. There is no persistence mutation in this test because the container manager lookup always fails and the outcome is exclusively event publication.

## Dependencies and Integration Points
This is a narrow integration point between SCM configuration, container report processing, and datanode command emission. It depends on `MockNodeManager` for a reporting datanode and on Mockito verification for the publisher side effect.

## Risks and Test Signals
The main risk is accidentally deleting unknown containers by default, or failing to delete them when the operator explicitly configures DELETE. The signal is precise: zero or one `SCMEvents.DATANODE_COMMAND` publication. The test does not inspect the exact command payload, so it validates command emission policy rather than delete-command structure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestUnknownContainerReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerConfigBuilder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerConfigBuilder.java

## Purpose
`ContainerBalancerConfigBuilder` is a small test helper for constructing `ContainerBalancerConfiguration` instances suitable for synthetic cluster-balancer tests. It centralizes defaults used by `TestContainerBalancerDatanodeNodeLimit` and related balancer fixtures.

## Important APIs, Types, and Functions
The class wraps `OzoneConfiguration.getObject(ContainerBalancerConfiguration.class)` and exposes two constructors plus `build()`. The no-configuration constructor creates a fresh `OzoneConfiguration`; the second constructor accepts an existing `OzoneConfiguration` so tests can preload settings such as container size. It depends on `TestContainerBalancerTask.STORAGE_UNIT` to express size limits.

## Control Flow and State Behavior
Construction mutates a `ContainerBalancerConfiguration` object with deterministic test defaults: `iterations=1`, `threshold=10`, `maxSizeToMovePerIteration=50GB`, and `maxSizeEnteringTarget=50GB`. For clusters smaller than `DATANODE_COUNT_LIMIT_FOR_SMALL_CLUSTER` (15), it sets `maxDatanodesPercentageToInvolvePerIteration=100` so small clusters are not artificially capped by percentage rounding. `build()` simply returns the configured object; there is no persistence layer or external I/O.

## Dependencies and Integration Points
The helper integrates with Ozone's configuration object mapping and the balancer test cluster sizes. It is intentionally package-private and belongs to the balancer test package, so production code does not depend on it.

## Risks and Test Signals
The main risk is hidden coupling: changing these defaults can alter many parameterized balancer tests at once. The small-cluster percentage override is particularly important because without it tests on 4-14 node clusters could fail due to low allowed datanode involvement rather than balancer logic. Test signal is indirect through the suites that consume the builder.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerConfigBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/MockedSCM.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/MockedSCM.java

## Purpose
`MockedSCM` is a reusable balancer test fixture that presents a mocked `StorageContainerManager` backed by a deterministic `TestableCluster`. It allows balancer tasks to run against realistic node, container, replica, placement, replication-health, move-manager, and service-state interfaces without starting a full SCM.

## Important APIs, Types, and Functions
The public surface includes `init`, `startBalancerTask`, `startBalancerTaskAsync`, `getMoveManager`, `getReplicationManager`, `getNodeManager`, `getStorageContainerManager`, `getCluster`, `getContainerManager`, `getPlacementPolicy`, and `getEcPlacementPolicy`. Internally it mocks `ContainerManager`, `SCMServiceManager`, `MoveManager`, `ReplicationManager`, `StatefulServiceStateManager`, and placement policies. `MockedPlacementPolicies` builds real placement policies through `ContainerPlacementPolicyFactory`.

## Control Flow and State Behavior
The constructor creates a mocked SCM, a `MockNodeManager` seeded from `TestableCluster.getDatanodeToContainersMap`, a container manager backed by the cluster's container and replica maps, a completed `MoveManager`, and a healthy `ReplicationManager`. `init` writes the balancer config into an `OzoneConfiguration`, creates service and placement fixtures, and wires `StorageContainerManager` getters. `startBalancerTask` constructs a `ContainerBalancerTask`, calls `run()`, and returns the task for inspection. `startBalancerTaskAsync` starts the task in a new thread and is used by status-info tests that observe intermediate states.

Persistent service state is emulated with an in-memory `Map<String, ByteString>` in `MockedServiceStateManager`; `saveConfiguration` stores bytes and `readConfiguration` retrieves them. Move operations default to `CompletableFuture.completedFuture(MoveResult.COMPLETED)`, while tests can override the mock for failure, timeout, or exception scenarios.

## Dependencies and Integration Points
`MockedSCM` integrates synthetic cluster topology with production `ContainerBalancer`, `ContainerBalancerTask`, placement validation, `ReplicationManager`, and `MoveManager` APIs. It is the shared fixture for datanode-limit and status-info suites.

## Risks and Test Signals
The main risk is fixture realism: because move and replication health are mocked healthy by default, tests using `MockedSCM` primarily validate balancer selection and accounting logic, not actual replication execution. Its value is high because it keeps placement policies real and exposes metrics, selected sources/targets, and iteration history after a task run.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/MockedSCM.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestContainerBalancer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestContainerBalancer.java

## Purpose
`TestContainerBalancer` validates the service-level `ContainerBalancer` wrapper: start/stop state transitions, persisted run configuration, SCM leadership notifications, delayed restart behavior, configuration validation, status reporting, and validation of include/exclude node hostnames.

## Important APIs, Types, and Functions
The suite targets `ContainerBalancer`, `ContainerBalancerTask.Status`, `ContainerBalancerConfiguration`, `ContainerBalancerStatusInfo`, `IllegalContainerBalancerStateException`, and `InvalidContainerBalancerConfigurationException`. The fixture mocks `StorageContainerManager`, `NodeManager`, `MoveManager`, `SCMServiceManager`, and `StatefulServiceStateManager`, with an in-memory `serviceToConfigMap` for configuration persistence.

## Control Flow and State Behavior
`setup()` configures short SCM wait and node-report intervals, enables DU triggering, stores balancer configuration in `OzoneConfiguration`, wires SCM getters, and constructs `ContainerBalancer`. `testShouldRun` proves the persisted enable flag controls `shouldRun`. `testStartBalancerStop` verifies idempotent stop, rejects duplicate starts, and confirms RUNNING then STOPPED status. `testStartStopSCMCalls` exercises the service `start()` and `stop()` paths after persisted configuration says the balancer should run.

Leadership behavior is covered by `testNotifyStateChangeStopStart`: when `SCMContext` loses leadership the running balancer stops; when leadership returns and is marked ready, `notifyStatusChanged` restarts it. `testDelayedStartOnSCMStatusChange` captures logs and waits for the balancing thread to enter `TIMED_WAITING`, proving restart honors `hdds.scm.wait.time.after.safemode.exit`.

Configuration validation asserts move replication timeout must be less than move timeout and must leave enough datanode offset slack. Invalid include/exclude node names are rejected using `NodeManager.getNodesByAddress`, while valid hosts allow start. `testGetBalancerStatusInfo` checks that status info reflects explicitly configured threshold, iteration count, and DU trigger flag.

## Dependencies and Integration Points
The file integrates balancer service lifecycle with SCM HA context, stateful service configuration storage, host resolution through `NodeManager`, and logging. It does not depend on a real cluster or container placement.

## Risks and Test Signals
Risks covered include duplicate balancer threads, stale persisted run flags, incorrect behavior during SCM leadership changes, invalid timeout settings, and silent acceptance of bad node filters. Signals include status enum assertions, exception assertions, log capture, and status-info field comparisons.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestContainerBalancer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestContainerBalancerDatanodeNodeLimit.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestContainerBalancerDatanodeNodeLimit.java

## Purpose
`TestContainerBalancerDatanodeNodeLimit` is a parameterized `ContainerBalancerTask` suite that runs the same behavioral checks across synthetic clusters from 4 to 30 datanodes. It focuses on datanode involvement limits, movement size limits, utilization calculation, container eligibility, placement policy, target health, include/exclude container filters, iteration results, and move-result accounting.

## Important APIs, Types, and Functions
The suite uses `MockedSCM`, `TestableCluster`, `ContainerBalancerConfigBuilder`, `ContainerBalancerTask`, `ContainerBalancerMetrics`, `MoveManager`, `ContainerInfo`, `ContainerReplica`, `DatanodeUsageInfo`, and placement policy APIs. Utility methods include `createMockedSCMs`, `getMockedSCM`, `getUnBalancedNodes`, `stillHaveUnbalancedNodes`, `genCompletableFuture`, and `genCompletableFutureWithException`.

## Control Flow and State Behavior
Each parameterized test receives a fresh `MockedSCM`, builds a configuration, runs `mockedSCM.startBalancerTask(config)`, and inspects the completed task and metrics. Datanode-limit tests compare `getCountDatanodesInvolvedPerIteration` and `metrics.getNumDatanodesInvolvedInLatestIteration` to `maxDatanodesPercentageToInvolvePerIteration * nodeCount / 100`. Size-limit tests lower `maxSizeEnteringTarget` or `maxSizeLeavingSource` so no container can be selected, then rerun with defaults to prove movement resumes.

The suite verifies threshold-driven unbalanced-node selection against `TestableCluster.getUnBalancedNodes`, checks average-utilization math, and confirms the balancer calls `MoveManager.move`. Eligibility tests mutate all containers to OPEN or all replicas to CLOSING and assert no movement occurs. Selection tests assert moved containers are CLOSED, target datanodes do not already host the selected container, placement policy remains satisfied after source-to-target substitution, targets are in-service healthy, and a container is not selected more than once.

Include/exclude container filters are tested through `setExcludeContainers` and `setIncludeContainers`. Iteration-result tests validate `ITERATION_COMPLETED` under normal moves, failed moves, explicit future timeouts, replication-manager timeout results, and exceptions from `MoveManager`.

## Dependencies and Integration Points
The suite depends heavily on `MockedSCM` and real placement-policy validation. It also uses metrics, container manager maps, node manager status, and Ozone size constants.

## Risks and Test Signals
Risks include over-involving datanodes, violating movement caps, selecting ineligible containers or unhealthy targets, breaking placement, duplicate container moves, and miscounting timeouts/failures. Signals are task maps, selected source/target sets, metrics counters, movement sizes, and iteration result enums. Two tests are marked flaky for known HDDS issues, indicating timing and move-result accounting sensitivity.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestContainerBalancerDatanodeNodeLimit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestContainerBalancerSelectionCriteria.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestContainerBalancerSelectionCriteria.java

## Purpose
`TestContainerBalancerSelectionCriteria` unit-tests `ContainerBalancerSelectionCriteria.shouldBeExcluded`. It verifies that the balancer rejects unhealthy or actively changing containers by default while optionally allowing selected non-standard but safe cases such as over-replicated closed containers and healthy quasi-closed containers.

## Important APIs, Types, and Functions
The fixture uses `ContainerBalancerConfiguration`, `ContainerBalancerSelectionCriteria`, `ContainerManager`, `ReplicationManager`, `NodeManager`, `FindSourceStrategy`, `ContainerHealthResult`, `ReplicationTestUtil`, `ContainerInfo`, and `ContainerReplica`. It constructs RATIS replication with factor THREE and manipulates replica states `CLOSED` and `QUASI_CLOSED`, including an explicit empty quasi-closed replica.

## Control Flow and State Behavior
`setup()` creates a CLOSED container with one CLOSED source replica, mocks container/replica lookup, returns healthy replication status, disables active replication/deletion, and allows source size to leave. Basic tests assert under-replicated, over-replicated, and mis-replicated health results are excluded, while a healthy container is not. When `isContainerReplicatingOrDeleting` is true, the container is excluded after health and replica lookups.

The non-standard container tests pivot on `balancerConfiguration.setIncludeNonStandardContainers`. With the flag enabled, an over-replicated CLOSED container with at least the required number of non-empty CLOSED replicas plus one non-empty QUASI_CLOSED replica can be selected from any replica source. With the flag disabled, the same over-replicated container is excluded. If an over-replicated container has only two CLOSED replicas for RF=3, all sources are excluded because moving any closed or quasi-closed replica could drop below minimum closed coverage. Empty QUASI_CLOSED replicas remain excluded even when non-standard inclusion is enabled. Healthy QUASI_CLOSED containers with all non-empty quasi-closed replicas are allowed only when the flag is enabled.

## Dependencies and Integration Points
This test isolates criteria logic from full balancer execution while using production health-result classes. It is an integration point between replication health classification, source-size checks, replica state/emptiness rules, and the balancer configuration flag for non-standard containers.

## Risks and Test Signals
The main risks are moving containers that replication manager is already repairing, worsening under/over/mis-replication, moving empty quasi-closed replicas, or excluding safe non-standard cases when the operator enables them. Signals are direct boolean assertions on `shouldBeExcluded` and Mockito verifications for expected health checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestContainerBalancerSelectionCriteria.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestContainerBalancerStatusInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestContainerBalancerStatusInfo.java

## Purpose
`TestContainerBalancerStatusInfo` verifies the live and historical iteration statistics exposed by `ContainerBalancerTask.getCurrentIterationsStatistic`. It covers completed iterations, repeated reads, reads between iterations, delayed start, in-progress balancing, and a regression where sleeping balancing threads could trigger a null pointer exception.

## Important APIs, Types, and Functions
The suite uses `MockedSCM`, `TestableCluster`, `ContainerBalancerConfiguration`, `ContainerBalancerTask`, `ContainerBalancerTaskIterationStatusInfo`, `ContainerBalancer`, and `StorageContainerManager`. Assertion helpers include `verifyCompletedIteration`, `verifyStartedEmptyIteration`, `assertCurrentIterationStatisticWhileBalancingInProgress`, and `getTotalMovedData`.

## Control Flow and State Behavior
Synchronous tests run `mockedScm.startBalancerTask(config)` with two iterations and zero balancing interval, then assert two completed statistics entries. Re-requesting statistics after a delay must return equal entries, proving history is stable after completion. Asynchronous tests start tasks with long balancing intervals or delay flags and use `LambdaTestUtils.await` or sleeps to inspect partial progress.

Completed iteration validation checks iteration number, result string `ITERATION_COMPLETED`, non-null duration, positive scheduled/completed moves, zero failed/timeouts, positive scheduled and moved data, non-empty entering/leaving maps, and equality between total entering and leaving bytes. Delayed-start validation expects an initial iteration entry with no result and zero movement. In-progress validation intentionally avoids flaky counters and checks only that iteration 2 has no result yet, no failed/timeouts, and positive entering/leaving node sizes.

The regression test for HDDS-11350 enables DU triggering so the balancing thread sleeps while waiting for datanode usage updates, starts the task on a daemon thread, and asserts `getCurrentIterationsStatistic` does not throw.

## Dependencies and Integration Points
This suite depends on `MockedSCM` for asynchronous balancer execution, Ozone configuration keys for safe-mode wait behavior, `ArithmeticUtils.addAndCheck` for summing movement maps, and `LambdaTestUtils` for wait loops.

## Risks and Test Signals
Risks include unstable status snapshots, missing current-iteration records during sleep/delay windows, incorrect entering/leaving accounting, null dereferences, and mutation of completed history. Signals are status list sizes, iteration fields, movement counters, map contents, and exception-free statistic retrieval.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestContainerBalancerStatusInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestContainerBalancerTask.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestContainerBalancerTask.java

## Purpose
`TestContainerBalancerTask` is a focused balancer-task unit suite using an internally generated 10-node cluster. It validates node include/exclude filtering, configuration parsing, delayed task startup, source requeue behavior after move failures, and exclusion of zero-size containers.

## Important APIs, Types, and Functions
The fixture constructs `ContainerBalancerTask`, `ContainerBalancer`, `ContainerBalancerConfiguration`, `MoveManager`, `ContainerManager`, `ReplicationManager`, `MockNodeManager`, placement policies, `DatanodeUsageInfo`, `ContainerInfo`, and `ContainerReplica`. Helper methods `generateUtilizations`, `generateData`, `createCluster`, `createReplicasForContainers`, `createContainer`, `createReplica`, and `startBalancer` build and run a synthetic cluster. Containers alternate between RATIS and EC replication based on ID parity.

## Control Flow and State Behavior
`setup()` creates mocked SCM dependencies, a completed `MoveManager`, healthy replication-manager responses, in-memory service-state persistence, real placement policies from a `MockNodeManager`, and a `ContainerBalancerTask` configured for one iteration with full datanode involvement. `generateData` creates 10 datanodes with increasing utilization, assigns containers of varying used sizes, and records container-to-replica and datanode-to-container maps. `createCluster` computes node capacity from target utilization and used bytes, then sets `SCMNodeStat` values on each `DatanodeUsageInfo`.

`balancerShouldFollowExcludeAndIncludeDatanodesConfigurations` configures include and exclude node lists using IPs and hostnames, runs the task, and verifies every selected source and target belongs to included-minus-excluded nodes. `testContainerBalancerConfiguration` reads storage and time settings through the config object and checks threshold, max source-leaving size, move timeout, and replication timeout parsing.

`testDelayedStart` starts a task thread with delayed startup enabled, waits until the thread is sleeping, interrupts it, and asserts STOPPED status and thread death. `testSourceDatanodeAddedBack` and `testSourceDatanodeAddedBackForReplicationNotHealthyBeforeMove` make the first move fail with retryable move results, then complete the second move; they assert two datanodes are involved, one failed move is counted, at least one move completes, and the source/target sets contain the expected endpoints. `balancerShouldMoveOnlyPositiveSizeContainers` uses a special size array for that test and asserts no selected container has non-positive used bytes.

## Dependencies and Integration Points
This file integrates task-level balancing logic with placement policy construction, mocked replication health, move manager futures, node statistics, and Ozone configuration parsing. It overlaps conceptually with `TestContainerBalancerDatanodeNodeLimit` but uses a local cluster generator rather than `TestableCluster`.

## Risks and Test Signals
Risks covered include ignoring include/exclude node filters, parsing size/time config incorrectly, leaving delayed threads running, abandoning sources after retryable move failures, and scheduling zero-byte containers. Signals are selected source/target maps, metric counters, task status, thread state, and parsed configuration values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestContainerBalancerTask.java -->
