# subset-b-008047 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestSCMNodeManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestSCMNodeManager.java

Purpose: this large JUnit 5 suite is the main behavioral contract for `SCMNodeManager`. It exercises datanode registration, heartbeat processing, health transitions, layout-version compatibility, SCM command queues, storage and filesystem statistics, topology registration, address indexes, pipeline-limit defaults, and operational-state notification behavior.

Important APIs and types: helpers build an `SCMNodeManager` through `HddsTestUtils.getScm`, configure `SCMContext` as leader with safe-mode pre-checks passed, and use the real `PipelineManagerImpl` from SCM. The tests use `DatanodeDetails`, `DatanodeID`, `DatanodeInfo`, `NodeStatus`, `SCMNodeStat`, `NodeReportProto`, `StorageReportProto`, `MetadataStorageReportProto`, `CommandQueueReportProto`, `LayoutVersionProto`, `SCMCommand`, `CommandForDatanode`, `RegisteredCommand`, and SCM events including `DATANODE_COMMAND`, `DATANODE_COMMAND_COUNT_UPDATED`, `NEW_NODE`, and `REPLICATION_MANAGER_NOTIFY`.

Control flow: setup creates a metadata directory and cleanup stops SCM. `createNodeManager` wires SCM, context, and pipeline manager. Heartbeat tests register nodes, call `processHeartbeat`, wait for the health-check scheduler, and query counts and lists. Layout tests register nodes with correct and incorrect MLV/SLV, force safe-mode exit, then assert that invalid layout reports close affected pipelines and that older MLV nodes are excluded from pipelines until they report a current layout. Command queue tests add queued SCM commands, process datanode queue reports, and verify reported plus pending counts. Storage tests feed node reports through `NodeReportHandler`, wait for stats updates, and compare cluster totals, per-node totals, volume health, and filesystem aggregates. Topology tests configure table mappings and schema files, register nodes, then assert rack/nodegroup paths and address lookup behavior. Operational-state tests set desired op states, heartbeat reported states, and verify whether replication manager notifications fire.

State and persistence behavior: the tests cover in-memory health state changes from healthy to stale to dead and back, and persistent state indirectly through SCM and pipeline manager state. Command queues are tracked per datanode and per command type, with missing command types in a later report intentionally clearing stale reported values. Node reports update aggregate stats while stale nodes retain their last stats and dead nodes are removed from active aggregate totals until a heartbeat revives them. Layout version reports mutate effective node eligibility and can trigger datanode commands. Network topology registration mutates the cluster map and address indexes, including re-registration with the same datanode ID and changed IP/hostname.

Dependencies and integration points: this file integrates `SCMNodeManager` with `StorageContainerManager`, `PipelineManagerImpl`, `SCMContext`, `SCMSafeModeManager`, `EventQueue`, `NodeReportHandler`, `NetworkTopologyImpl`, Hadoop table mapping, HDDS layout finalization, and Ozone command classes. It also depends heavily on `HddsTestUtils`, `MockDatanodeDetails`, `GenericTestUtils.waitFor`, Mockito, AssertJ, and JUnit parameterized tests.

Risks and edge cases: several tests use real sleeps and large node counts, so timing can be flaky under slow CI. `findNodes` ignores its `state` argument and always checks stale count, which is harmless for current callers but misleading. `testScmShutdown` has no meaningful assertion. Layout and pipeline assertions depend on asynchronous auto-creation and closing, making timeout values important. The topology tests rely on classpath resources such as `rack-mapping`, `nodegroup-mapping`, and `network-topology-nodegroup.xml`.

Test signals: strong coverage exists for heartbeat success/failure, stale/dead recovery, JVM pause handling, layout incompatibility, finalization command emission, command queue accounting, node report stats, topology indexing, filesystem usage aggregation, default pipeline limit fallback, and replication-manager notification rules. The suite is especially valuable as a regression detector for SCM node lifecycle and datanode eligibility changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestSCMNodeManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestSCMNodeMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestSCMNodeMetrics.java

Purpose: verifies metrics exported by `SCMNodeManager` and `SCMNodeMetrics`, including heartbeat counters, node report counters, state gauges, writable-node gauge, and ozone/filesystem capacity gauges.

Important APIs and types: constructs an `SCMNodeManager` directly with `OzoneConfiguration`, `SCMStorageConfig`, `EventQueue`, `NetworkTopologyImpl`, empty `SCMContext`, and mocked `HDDSLayoutVersionManager`. It uses `MetricsAsserts.getMetrics`, `getLongCounter`, and `assertGauge` against `SCMNodeMetrics.SOURCE_NAME`.

Control flow: `@BeforeAll` initializes one registered datanode with a simple node report. Counter tests snapshot a metric, call `processHeartbeat` or `processNodeReport`, and expect the counter to increment. Failure tests send heartbeat or node report for an unregistered random datanode. The gauge test updates storage and filesystem fields, reads metrics, and checks every operational/health-state gauge plus capacity totals.

State and persistence behavior: all state is in-memory for a static node manager. Registration seeds node-state and metric state; report processing mutates per-node storage stats and cluster aggregate metrics. The test closes the manager in `@AfterAll`; no RocksDB persistence is involved.

Dependencies and integration points: depends on Hadoop metrics2, `HddsTestUtils.createStorageReport`, protobuf node reports, SCM layout-version compatibility, and the SCM node manager metrics source registration.

Risks and edge cases: the static node manager means metric state is shared across tests, so tests rely on snapshot-before-action rather than absolute counter values. The gauge test sleeps after a heartbeat, making it sensitive to timing. It intentionally expects `NonWritableNodes` to be 1 because the synthetic datanode lacks metadata-volume space.

Test signals: gives direct signal that successful and failed heartbeat/node-report paths update counters and that the public metrics surface includes all expected node state and capacity gauges.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestSCMNodeMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestSCMNodeStorageStatMap.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestSCMNodeStorageStatMap.java

Purpose: tests `SCMNodeStorageStatMap`, the datanode-to-volume usage map used by SCM node accounting.

Important APIs and types: uses `SCMNodeStorageStatMap`, `StorageLocationReport`, `StorageReportProto`, `NodeReportProto`, `StorageType`, utilization thresholds, and `StorageReportResult`. Test data is a `ConcurrentHashMap<UUID, Set<StorageLocationReport>>` of 100 datanodes with one DISK volume each.

Control flow: setup generates test data. Tests validate known-node lookup, duplicate insert rejection, update of unknown datanodes, processing of single-node reports, and aggregate behavior after bulk inserts, updates, threshold queries, and removals. Single-node report flow starts with matching storage, adds a full storage report to trigger out-of-space, then adds a failed full disk to trigger combined failed-and-out-of-space status.

State and persistence behavior: state is entirely in-memory inside `SCMNodeStorageStatMap`. Inserts, updates, report processing, and removals mutate volume sets and aggregate total capacity/free/used counters. Threshold queries classify datanodes as normal, warn, or critical according to the updated utilization.

Dependencies and integration points: depends on Ozone constants for GB units, HDDS test report builders, storage protobuf conversion from `StorageLocationReport`, and `SCMException` messages for invalid operations.

Risks and edge cases: generated datanode UUID keys differ from the storage report IDs in `generateData`, so the test focuses on map behavior rather than ID consistency between key and volume. Some assertions use floating-point arithmetic for expected counts. The single-node test includes a builder variable used only to assemble a final report.

Test signals: good coverage for map membership, duplicate protection, unknown update errors, report status classification, aggregate counter updates, threshold list sizes, and removal behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestSCMNodeStorageStatMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestStatisticsUpdate.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestStatisticsUpdate.java

Purpose: verifies that node statistics in `NodeManager` are updated from node reports and adjusted when a datanode becomes dead.

Important APIs and types: uses real SCM from `HddsTestUtils.getScm`, `NodeReportHandler`, `DeadNodeHandler`, `SCMNodeStat`, `SCMNodeMetric`, `NodeReportFromDatanode`, `PipelineManager`, and SCM events.

Control flow: setup creates an SCM with short heartbeat/stale/dead intervals, obtains its node manager, and registers a `DeadNodeHandler` on a local event queue. The test registers two datanodes with storage reports, sends both reports through `NodeReportHandler`, verifies aggregate and per-node stats, then heartbeats only the second datanode until the first ages out. Final assertions show aggregate stats contain only the surviving node.

State and persistence behavior: state is the live SCM node manager state. Node reports add per-node and aggregate stat entries; heartbeat timing moves one node out of active accounting. The test does not explicitly close SCM in this class, so lifecycle is inherited from the test harness/object reachability.

Dependencies and integration points: integrates node reports, heartbeat health transitions, dead-node handling, SCM event constants, and mocked pipeline manager behavior for dead-node processing.

Risks and edge cases: uses sleeps around one-second stale/dead intervals, so it can be timing-sensitive. The comment notes missing direct logic to mark a node dead in `NodeManager`, so the test simulates it by heartbeat omission. The local `EventQueue` handler is configured but report handling uses mocked publishers.

Test signals: confirms stat aggregation from multiple datanodes, per-node stat retrieval, and aggregate removal of dead-node capacity/usage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestStatisticsUpdate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/package-info.java

Purpose: package-level metadata for `org.apache.hadoop.hdds.scm.node` tests. Its only functional role is to satisfy Checkstyle/package documentation requirements.

Important APIs and types: no Java types, methods, or fields are declared. The file contains the package declaration and a short Javadoc comment.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: indirectly marks the test package for SCM node-related tests.

Risks and edge cases: any package rename must update this declaration. Otherwise the file has no runtime behavior.

Test signals: no direct tests; its presence supports style and package documentation checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/states/TestNodeStateMap.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/states/TestNodeStateMap.java

Purpose: unit-tests `NodeStateMap`, the internal map used by `NodeStateManager` to track datanode details, health/operational state combinations, and per-node container lists.

Important APIs and types: uses `NodeStateMap`, `DatanodeInfo`, `DatanodeDetails`, `DatanodeID`, `NodeStatus`, `NodeOperationalState`, `NodeState`, `ContainerID`, and exceptions `NodeAlreadyExistsException` and `NodeNotFoundException`.

Control flow: helper methods add a generated datanode with a given `NodeStatus`. Tests add and retrieve nodes, update health while preserving operational state/expiry, update operational state while preserving health, generate one node for every op-state/health combination, and query counts by exact status and partial op/health filters. The concurrency test iterates a node's container collection while another thread removes an element.

State and persistence behavior: all state is in-memory. The map maintains indexes for total nodes, status-specific lists, datanode info lookup, and containers per datanode. Health and operational-state updates return the new status and update subsequent lookups. Container iteration is expected to tolerate concurrent mutation without surfacing an exception.

Dependencies and integration points: depends on `DatanodeInfo` construction with layout/roll interval values from `HddsTestUtils`, and on Ozone container ID value objects.

Risks and edge cases: `NodeOperationalState.values()` and `NodeState.values()` drive expected counts, so adding enum values changes asserted totals. The concurrency test only checks for thrown exceptions, not deterministic iteration content.

Test signals: strong low-level signal for node-state indexing correctness, expiry preservation, partial count APIs, and safe container-list iteration during concurrent modifications.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/states/TestNodeStateMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/states/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/states/package-info.java

Purpose: package-level Javadoc for `org.apache.hadoop.hdds.scm.node.states` tests.

Important APIs and types: no executable code or declared types. The comment says "Test Node2Container Map" and the package declaration places tests in the node states package.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: only Java package metadata for test sources.

Risks and edge cases: stale wording may not fully describe all current tests in the package, which now include node-state map behavior beyond node-to-container mapping.

Test signals: style/package documentation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/states/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/package-info.java

Purpose: package-level Javadoc for SCM tests under `org.apache.hadoop.hdds.scm`.

Important APIs and types: no types, methods, fields, or imports. It contains only a package declaration with documentation.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: documents the root SCM test package.

Risks and edge cases: only package-name drift or style rules affect this file.

Test signals: none beyond Checkstyle/package documentation compliance.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/MockPipelineManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/MockPipelineManager.java

Purpose: lightweight test implementation of `PipelineManager` backed by a real `PipelineStateManager`. It lets tests create, query, and mutate pipelines without starting the full production pipeline manager.

Important APIs and types: implements `PipelineManager`; owns `PipelineStateManager` and `NodeManager`. It creates RATIS-style mock pipelines with random datanodes, EC pipelines with required-node counts, read pipelines from `ContainerReplica` sets and replica indexes, and delegates pipeline lookup, counts, container membership, open/close/deactivate transitions, and space allocation checks to `PipelineStateManager`/`NodeManager`.

Control flow: constructor builds `PipelineStateManagerImpl` from a DB table, SCM HA Ratis server, transaction buffer, and node manager. `createPipeline` branches on replication type: EC calls `buildECPipeline`; non-EC builds a three-node open pipeline. The created pipeline protobuf is added to state. Read pipeline creation copies replica datanodes and replica indexes into a closed pipeline. Many lifecycle methods are intentionally no-ops.

State and persistence behavior: pipeline metadata is stored through the `PipelineStateManager` and the supplied RocksDB table/transaction buffer. Container-to-pipeline relationships are delegated to the state manager. Deletion, scrub, creator start/trigger, freeze/resume, locks, metrics, and pipeline info do not maintain state in this mock.

Dependencies and integration points: integrates tests with `SCMDBDefinition.PIPELINES`, `SCMHAManager`, `NodeManager.checkSpaceAndRecordAllocation`, `ContainerReplica`, `ClientVersion`, and Ozone replication configs.

Risks and edge cases: because several `PipelineManager` methods are no-ops or return null/defaults, this mock is suitable only for tests that do not need production lifecycle, locking, metrics, deletion, or safe-mode semantics. Non-EC `createPipeline` ignores favored/excluded nodes. `deletePipeline` leaves state untouched.

Test signals: not itself a test, but it is a reusable fixture. Its value is preserving realistic state-manager behavior while isolating tests from production scheduling and SCM services.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/MockPipelineManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/MockRatisPipelineProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/MockRatisPipelineProvider.java

Purpose: test subclass of `RatisPipelineProvider` that suppresses real datanode initialization and can force newly-created pipelines to remain allocated.

Important APIs and types: extends `RatisPipelineProvider`; constructors accept `NodeManager`, `PipelineStateManager`, `ConfigurationSource`, optional `EventPublisher`, and an `autoOpen` flag. Overrides `initializePipeline`, `create(RatisReplicationConfig)`, and `create(RatisReplicationConfig, List<DatanodeDetails>)`. Provides static `markPipelineHealthy`.

Control flow: `initializePipeline` is a no-op because test datanodes do not exist. If `autoOpenPipeline` is true, `create` delegates to the parent. If false, it delegates first, then rebuilds the pipeline with the same ID/nodes/config but state `ALLOCATED`. The node-list overload always returns an open pipeline from the provided nodes.

State and persistence behavior: the provider itself stores only the `autoOpenPipeline` flag. Pipeline state is embodied in returned `Pipeline` objects and persisted only when callers add them to `PipelineStateManager`. `markPipelineHealthy` mutates a pipeline object by reporting every datanode and setting the first node as leader.

Dependencies and integration points: depends on `RatisPipelineProvider`, SCM context, event publisher, pipeline state manager, and replication config conversion.

Risks and edge cases: default constructor without explicit `autoOpen` leaves the boolean default false, while the constructor with event publisher sets true; tests must choose the intended constructor. The rebuild path may omit fields from the parent-created pipeline if new fields are later added.

Test signals: fixture for tests needing deterministic open/allocated pipeline behavior without contacting datanodes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/MockRatisPipelineProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestCreateForReadComparator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestCreateForReadComparator.java

Purpose: tests `ECPipelineProvider.CREATE_FOR_READ_COMPARATOR`, which orders replica datanodes when building EC read pipelines.

Important APIs and types: uses `Comparator<NodeStatus>`, `NodeStatus`, `NodeOperationalState`, and `NodeState`.

Control flow: parameterized `readOnly` verifies healthy and healthy-readonly compare as equal for every operational state. `healthyFirst` asserts healthy statuses sort before stale/dead statuses, including maintenance/decommissioning healthy states. `inServiceFirst` asserts in-service healthy sorts ahead of decommissioning or entering-maintenance healthy nodes.

State and persistence behavior: none; tests compare immutable status values.

Dependencies and integration points: directly protects EC read pipeline node ordering used by `ECPipelineProvider.createForRead`.

Risks and edge cases: comparator ordering is tested by sign only, not full stable order. Equal treatment of read-only health states is intentional and important for read-path inclusion.

Test signals: focused regression signal that EC read pipelines prefer in-service healthy nodes, then other healthy operational states, then stale/dead nodes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestCreateForReadComparator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestECPipelineProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestECPipelineProvider.java

Purpose: verifies EC pipeline creation and read-pipeline construction in `ECPipelineProvider`.

Important APIs and types: uses `ECPipelineProvider`, `PipelineProvider`, `ECReplicationConfig`, `Pipeline`, `PipelineStateManager`, `PlacementPolicy`, `NodeManager`, `ContainerReplica`, and `NodeStatus`.

Control flow: setup mocks placement policy to return the requested number of random datanodes and mocks all node statuses as in-service healthy by default. Creation tests assert EC type, required node count, allocated state, and one-based replica indexes. Read tests build `ContainerReplica` sets and assert read pipelines preserve replica indexes. Additional tests mark some replica nodes dead and expect omission, add duplicate replica indexes on healthy/decommissioning/stale nodes and expect sorted output, and verify excluded/favored lists plus container-size bytes are passed to placement policy.

State and persistence behavior: provider returns pipeline objects but state manager is mocked, so no real persistence occurs. Replica-index state is stored in the pipeline's datanode-to-index map. Read-pipeline node selection is derived from current `NodeManager.getNodeStatus` calls.

Dependencies and integration points: integrates EC replication config, SCM placement policy API, Ozone container size configuration, container replica metadata, and node health/operational status ordering.

Risks and edge cases: mocked placement policy masks real rack and capacity behavior. `HashSet` replica iteration order is not deterministic, but assertions use sets or ordered groups matching comparator categories. Dead-node omission depends on node-manager status lookup for each replica datanode.

Test signals: strong signal for EC required-node sizing, index numbering, read-path filtering/sorting, and propagation of placement constraints.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestECPipelineProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineActionHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineActionHandler.java

Purpose: tests `PipelineActionHandler`, especially close-pipeline actions reported by datanodes and leader/follower behavior.

Important APIs and types: uses `PipelineActionHandler`, `PipelineActionsFromDatanode`, `PipelineActionsProto`, `PipelineAction`, `ClosePipelineInfo`, `PipelineManager`, `SCMContext`, `EventQueue`, `SCMEvents.DATANODE_COMMAND`, and `CommandForDatanode`.

Control flow: helper constructs a datanode action containing one CLOSE action with reason `PIPELINE_FAILED`. Valid-pipeline leader test expects `PipelineManager.closePipeline`. Follower test updates context to non-leader and expects no close and no command event. Unknown-pipeline leader test makes `closePipeline` throw `PipelineNotFoundException` and expects a datanode command event, while the follower variant expects no event.

State and persistence behavior: no persistent state; behavior depends on `SCMContext` leadership and mocked pipeline manager exceptions.

Dependencies and integration points: covers datanode heartbeat action handling, pipeline manager close API, SCM command event emission, and HA leader gating.

Risks and edge cases: only CLOSE action is covered. The tests verify interactions, not command payload details.

Test signals: good signal that only leaders act on pipeline actions and that unknown pipelines cause corrective datanode commands only from leaders.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineActionHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineDatanodesIntersection.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineDatanodesIntersection.java

Purpose: stress-style parameterized test that creates many RATIS/THREE pipelines and detects when newly-created pipelines contain the same datanode set as existing ones.

Important APIs and types: uses `MockNodeManager`, `PipelineStateManagerImpl`, `MockRatisPipelineProvider`, `RatisPipelineUtils.checkPipelineContainSameDatanodes`, `SCMHAManagerStub`, RocksDB `DBStore`, and pipeline-limit configuration.

Control flow: for each `(nodeCount, nodeHeaviness)` case, the test configures a mock node manager and pipeline limit, creates a state manager, then loops creating pipelines until `SCMException` or the theoretical node-count times heaviness bound. Each pipeline is persisted to state, added to node manager, and checked for overlap with previous pipelines. Intersections are logged rather than asserted.

State and persistence behavior: pipelines are stored in the test RocksDB-backed state manager and also registered in mock node manager pipeline mappings. The `end` flag controls the creation loop and is reset afterward.

Dependencies and integration points: exercises the Ratis pipeline provider against pipeline state, node pipeline load accounting, SCM DB definitions, and overlap utility logic.

Risks and edge cases: the test has no assertion on `intersectionCount`, so it mainly detects unexpected exceptions other than expected capacity exhaustion. It logs overlap information but does not fail on duplicate datanode sets. Loop count can be high for larger parameters.

Test signals: weak but useful stress signal that pipeline creation runs to capacity without regular IO failures and that overlap detection can inspect created pipelines.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineDatanodesIntersection.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineManagerImpl.java

Purpose: primary test suite for `PipelineManagerImpl`, covering pipeline creation, HA leadership gates, persisted state transitions, reports, scrub behavior, safe-mode gating, container membership, stale pipeline detection, allocated-pipeline waiting, and read-pipeline creation.

Important APIs and types: uses `PipelineManagerImpl`, `PipelineManager`, `PipelineStateManager`, `SCMPipelineMetrics`, `WritableRatisContainerProvider`, `HealthyPipelineChoosePolicy`, `PipelineReportHandler`, `SCMSafeModeManager`, `SCMContext`, `SCMHADBTransactionBufferStub`, `SCMHAManagerStub`, `MockNodeManager`, `DBStore`, `SCMDBDefinition.PIPELINES`, `ContainerManager`, `ContainerInfo`, `ContainerReplica`, `TestClock`, and Ozone replication configs.

Control flow: setup creates SCM, DB store, mock node manager, max pipeline count, leader SCM context, and service manager. Factory helpers create managers with leader/follower HA state and optional transaction buffer. Tests create RATIS and EC pipelines, close/reopen managers to verify DB reload, update allocated/open/dormant states and flush to the table, assert follower operations fail with `SCM_NOT_LEADER`, reject removal of open pipelines, process datanode pipeline reports until all nodes and a leader report, fill the cluster until creation fails and metrics increment, scrub old allocated/closed pipelines using `TestClock`, close open EC pipelines with unregistered nodes, enforce safe-mode precheck, log closed-container-before-pipeline-close order, identify stale pipelines when IP/hostname changes for the same UUID, close stale pipelines, wait for allocated pipelines to open before container selection, and create read pipelines from replicas.

State and persistence behavior: the suite explicitly verifies RocksDB-backed pipeline persistence through `SCMDBDefinition.PIPELINES` and transaction buffer flushes. Pipeline state transitions include ALLOCATED, OPEN, DORMANT, and CLOSED. Container membership is stored in pipeline state and is guarded against adding to closed pipelines except during SCM-start recovery. Scrub removes expired allocated/closed pipelines and closes open pipelines whose datanodes are no longer registered. Metrics state changes through `SCMPipelineMetrics`.

Dependencies and integration points: integrates pipeline manager with SCM HA, DB transaction buffers, event queue, safe mode, pipeline reports, container manager, container provider, node manager topology, metrics, Ratis exceptions, and test clock.

Risks and edge cases: `testCreatePipelineForRead` lacks an `@Test` annotation in the source outline, so it may not run unless invoked elsewhere. Several tests use mocks/spies and log string assertions, which can become brittle after refactors. Persistence tests must manage transaction buffer flush/close carefully. Follower assertions depend on `SCMHAManagerStub` internals.

Test signals: broad, high-value regression coverage for production pipeline manager lifecycle, HA correctness, persistence, safe-mode behavior, stale datanode handling, metrics, and container allocation waits.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelinePlacementFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelinePlacementFactory.java

Purpose: verifies `PipelinePlacementPolicyFactory` and placement behavior selected by default and rack-scatter policy configuration.

Important APIs and types: uses `PipelinePlacementPolicyFactory`, `PipelinePlacementPolicy`, `SCMContainerPlacementRackScatter`, `PlacementPolicy`, `NetworkTopologyImpl`, `NodeSchemaManager`, `MockNodeManager`, `PipelineStateManagerImpl`, `DatanodeInfo`, and storage/meta-storage reports.

Control flow: setup initializes configuration. `setupRacks` creates rack-aware datanodes, inserts them into a three-level topology, builds `DatanodeInfo` with enough storage and metadata space, spies node manager lookups, and creates a pipeline state manager. Tests check default factory class, configured rack-scatter class, default placement pattern across racks, rack-scatter all-racks behavior, anchor change when the first rack lacks a second node, used-node-aware placement, and combined used/excluded-node placement.

State and persistence behavior: topology and node-manager state are in-memory. Pipeline state manager is RocksDB-backed but these tests mainly need it as policy context, not for persisted pipeline mutations. Datanode storage reports establish space eligibility.

Dependencies and integration points: covers policy factory configuration key `OZONE_SCM_PIPELINE_PLACEMENT_IMPL_KEY`, rack schema initialization, ratis free-space minimum, SCM DB definitions, HA transaction buffer, and node-manager topology.

Risks and edge cases: `setupRacks` accumulates datanodes and `dnInfos` fields across calls within a test instance; JUnit creates fresh instances by default, but changing lifecycle would matter. The rack-scatter test passes `excludedNodes` twice in one call, likely intentionally using an empty list for both used/excluded but easy to misread. Assertions assume deterministic selection order enough to reason about positions.

Test signals: validates policy selection by config and important rack-aware placement rules involving anchors, used nodes, excluded nodes, and rack scatter.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelinePlacementFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelinePlacementPolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelinePlacementPolicy.java

Purpose: comprehensive unit suite for `PipelinePlacementPolicy`, covering rack-aware node choice, space filtering, load balancing, heavy-node exclusion, fallback behavior, placement validation, single-healthy-rack behavior, pipeline-count calculations, and default pipeline-limit filtering.

Important APIs and types: uses `PipelinePlacementPolicy`, `MockNodeManager`, `PipelineStateManagerImpl`, `NetworkTopologyImpl`, `NodeSchemaManager`, `DatanodeDetails`, `NodeStatus`, `Pipeline`, `PipelineID`, `ReplicationConfig`, `RatisReplicationConfig`, `ContainerPlacementStatus`, `SCMException`, and SCM placement configuration keys.

Control flow: initialization builds a rack-aware topology with ten datanodes, sets pipeline load limits and free-space minimums, creates DB-backed pipeline state manager, and instantiates the policy. Tests choose anchors, select same-rack and different-rack nodes, verify single-node rack placement, assert insufficient space errors for huge requirements, repeatedly create pipelines to test lowest-load selection, check fallback without rack awareness, simulate heavy nodes by adding more than the configured RATIS/THREE limit to node-manager and state-manager mappings, validate placement satisfaction/mis-replication across rack distributions, exercise skewed racks with stale or overloaded first rack, count only RATIS/THREE pipelines for load, and ensure the default pipeline limit is honored when the config is unset.

State and persistence behavior: selected pipelines are inserted into both `MockNodeManager` pipeline mappings and the DB-backed `PipelineStateManager`. Heavy-node simulation mutates load state repeatedly. Topology membership drives rack calculations and validation; removing a node from topology makes placement validation treat it as unavailable/dead. The policy itself is mostly stateless and derives decisions from node manager, topology, configuration, and state manager.

Dependencies and integration points: integrates network topology schemas, SCM DB/HA stubs, node-manager healthy node lists, datanode pipeline counts, Ratis replication configs, and container placement status logic. It also uses Ozone capacity constants for space tests.

Risks and edge cases: tests depend on deterministic enough node ordering from mock node manager and topology. `insertHeavyNodesIntoNodeManager` creates pipelines with random extra datanodes that may not belong to topology, which is acceptable for load counting but not full placement realism. Some tests rebuild `nodeManager` without rebuilding `stateManager`, so state-manager node-manager references can diverge in narrowly scoped tests. The suite relies on static `NodeSchemaManager` reinitialization.

Test signals: high-value coverage for placement correctness under rack awareness, one-rack fallback, capacity filtering, load limits, validation output, and exact definition of "current RATIS THREE pipeline count."
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelinePlacementPolicy.java -->
