# subset-b-008040 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/TestSCMCommonPlacementPolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/TestSCMCommonPlacementPolicy.java

## Purpose

This JUnit 5 test class exercises `SCMCommonPlacementPolicy`, the shared SCM placement-policy base used for datanode selection and container placement validation. It focuses on rack-aware mis-replication repair, over-replication removal, node validity under committed-space accounting, and placement validation when topology information is incomplete or stale.

## Important APIs, Types, and Functions

- `DummyPlacementPolicy extends SCMCommonPlacementPolicy` supplies deterministic rack mapping through `getPlacementGroup`, `getRequiredRackCount`, and `chooseNode`.
- `testReplicasToFixMisreplication(...)` wraps `replicasToCopyToFixMisreplication` and verifies copy counts per rack.
- `replicasToRemoveToFixOverreplication` is tested across indexed and non-indexed replicas.
- `isValidNode` is tested with mocked `DatanodeInfo`, `NodeStatus`, storage reports, metadata reports, `committed`, and `freeSpaceToSpare`.
- `validateContainerPlacement` is tested with dead/in-maintenance nodes and a topology that temporarily reports zero racks.

## Control Flow and State Behavior

`setup` creates a `MockNodeManager` with ten synthetic nodes and a temporary SCM configuration. Most tests build a `DummyPlacementPolicy`, map datanode indices to mock rack `Node` instances, synthesize `ContainerReplica` sets using `HddsTestUtils`, and assert which replicas should be copied or removed. The mis-replication path groups replicas by placement group and expects extra replicas from overfull racks to be selected for copying. The over-replication path verifies that duplicates or rack-skewed replicas are preferred for removal.

The storage-space test drives `isValidNode` through sequential storage report returns, proving that increasing committed bytes can make an otherwise writable node invalid when `remaining - committed` no longer exceeds the larger of requested space and spare-space reservation. Placement-validation tests mock `NodeManager` and `NetworkTopology` state to ensure maintenance nodes can use their embedded network location and zero-rack topology does not trigger divide-by-zero.

## State and Persistence

The class has no durable persistence. State is in-memory test fixtures: rack maps, mock topology, mock node status, synthetic storage reports, and replica sets. It indirectly validates production behavior that depends on SCM topology and datanode storage-report state.

## Dependencies and Integration Points

The tests integrate with `NodeManager`, `NetworkTopology`, `DatanodeInfo`, `NodeStatus`, `ContainerReplica`, `ContainerID`, `SCMException`, `HddsTestUtils`, `MockNodeManager`, and Mockito. They are regression coverage for replication manager decisions that call common placement utilities.

## Risks and Test Signals

Risk areas are rack-count arithmetic, choosing copy/removal candidates when replica indices are absent, honoring uncopyable replicas, accounting for committed bytes, and handling transient topology loss. Strong test signals include explicit per-rack expected copy counts, exact over-replication removal sets, and HDDS-15350 zero-rack regression coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/TestSCMCommonPlacementPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/TestStorageContainerManagerHttpServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/TestStorageContainerManagerHttpServer.java

## Purpose

This parameterized JUnit 5 test verifies that `StorageContainerManagerHttpServer` exposes HTTP and HTTPS endpoints according to each `HttpConfig.Policy`. It confirms that SCM binds ephemeral local ports and that enabled schemes serve `/jmx` while disabled schemes are not reachable.

## Important APIs, Types, and Functions

- `setUp` creates SSL test material with `KeyStoreTestUtil.setupSSLConfig`, configures Ozone client/server keystore resources, and initializes a `URLConnectionFactory`.
- `testHttpPolicy(HttpConfig.Policy policy)` iterates all HTTP policies via `@EnumSource`.
- `StorageContainerManagerHttpServer.start/stop`, `getHttpAddress`, and `getHttpsAddress` are the production APIs under test.
- `canAccess` opens a URL to `/jmx` through the configured connection factory.
- `implies` keeps assertions compact for policy-dependent access rules.

## Control Flow and State Behavior

For each policy, the test updates `OZONE_HTTP_POLICY_KEY`, sets HTTP and HTTPS bind and advertised addresses to `localhost:0`, initializes the Hadoop metrics system, starts the SCM HTTP server, and probes the published addresses. Assertions encode both positive and negative policy expectations: HTTP-only should not expose HTTPS, HTTPS-only should not expose HTTP, and dual-enabled policy should expose both.

## State and Persistence

The test writes temporary metadata and SSL keystore configuration under JUnit `@TempDir`. It cleans SSL configuration and destroys the connection factory in `tearDown`. There is no SCM metadata persistence beyond temporary directories.

## Dependencies and Integration Points

The file depends on Ozone configuration keys, SCM HTTP address keys, Hadoop `HttpConfig.Policy`, `DefaultMetricsSystem`, `URLConnectionFactory`, `NetUtils`, and `KeyStoreTestUtil`. It is an integration-style test for SCM web server startup and TLS wiring.

## Risks and Test Signals

The main risks are false negatives from local networking, stale metrics system state, or SSL setup failures. The strongest signal is end-to-end connection to `/jmx` through the same URL connection stack clients use, proving bind address, policy, and keystore configuration work together.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/TestStorageContainerManagerHttpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/block/TestBlockManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/block/TestBlockManager.java

## Purpose

This test class validates SCM block allocation behavior through a realistic in-process `StorageContainerManager` fixture. It covers successful allocation, pipeline exclusion, concurrent allocation, distribution across containers and disks, safe mode checks, oversized blocks, pipeline creation fallback, and reopening containers after close events.

## Important APIs, Types, and Functions

- `BlockManagerImpl.allocateBlock` is the primary API under test.
- `PipelineManagerImpl`, `MockRatisPipelineProvider`, `ContainerManagerImpl`, `SCMMetadataStoreImpl`, `SequenceIdGenerator`, `SCMSafeModeManager`, and `StorageContainerManager` form the fixture.
- `ExcludeList` influences pipeline selection.
- `CloseContainerEventHandler` and `DatanodeCommandHandler` simulate SCM event-driven container and pipeline lifecycle.
- `verifyNumberOfContainersInPipelines` and `expectedContainersPerPipeline` validate pipeline container counts.

## Control Flow and State Behavior

`setUp` builds a temporary SCM stack with safemode disabled, a mock node manager, HA stubs, metadata tables, pipeline manager, container manager, event queue, lease manager, and SCM context moved out of safe mode. Tests create and open RATIS pipelines, then call `allocateBlock` with a fixed 128 MB size and owner `OzoneConsts.OZONE`.

Allocation tests assert that excluded pipelines are avoided when alternatives exist but may be reused when all pipelines are excluded. Concurrent tests launch single-thread executors and require all futures to complete. Distribution tests constrain pipeline-per-datanode and healthy volume counts, then verify blocks are spread across the expected number of open containers. Safe mode tests move SCM context into `PRE_CHECKS_PASSED` and expect the safe-mode precheck error, then verify allocation after exiting safe mode. Closed-container tests fill pipelines, fire `CLOSE_CONTAINER` events for each container, wait for counts to drop, and confirm allocation recreates the expected container count.

## State and Persistence

The fixture uses a real temporary SCM metadata store and sequence-id table. Pipeline and container state are persisted in the test DB during the test lifecycle and closed in `cleanup`. Event queue state is in-memory. No state survives beyond the temp directory.

## Dependencies and Integration Points

The test integrates block manager allocation with pipeline creation/opening, container allocation, SCM metadata tables, event publishing, safe-mode state, HA transaction stubs, lease management, and node capacity/volume reporting from `MockNodeManager`.

## Risks and Test Signals

Risk areas include race conditions in parallel allocation, container-count accounting under multi-disk limits, stale excluded-pipeline logic, and hidden dependence on event timing. Signals are strong because the tests use production managers rather than pure mocks and assert exact container distribution and safe-mode error text.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/block/TestBlockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/block/TestDeletedBlockLog.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/block/TestDeletedBlockLog.java

## Purpose

This large test class exercises `DeletedBlockLogImpl` and `SCMDeletedBlockTransactionStatusManager`, the SCM-side transaction log used to send deleted-block transactions to datanodes and remove them after enough acknowledgements. It validates batching, persistence, per-datanode command status, resend suppression, timeout behavior, unhealthy-container filtering, and data-distribution summaries.

## Important APIs, Types, and Functions

- `DeletedBlockLogImpl.addTransactions`, `getTransactions`, `recordTransactionCreated`, `onSent`, and `close` are central APIs.
- `SCMDeletedBlockTransactionStatusManager.commitTransactions`, `commitSCMCommandStatus`, `getTransactionSummary`, `removeTransactions`, and `getTxSizeMap` are exercised directly or indirectly.
- Helper methods `generateData`, `updateContainerMetadata`, `commitTransactions`, `getTransactions`, `recordScmCommandToStatusManager`, and `sendSCMDeleteBlocksCommand` model the SCM-to-DN lifecycle.
- `mockStandAloneContainerInfo`, `mockInadequateReplicaUnhealthyContainerInfo`, and `mockContainerHealthResult` shape replication health and replica placement.

## Control Flow and State Behavior

`setup` creates a temporary SCM, mocks `ReplicationManager` and `ContainerManager`, opens the SCM container table, installs an HA transaction buffer stub, creates delete-service metrics, and constructs `DeletedBlockLogImpl`. Generated test transactions create one container per transaction and five deleted blocks per container. `getTransactions` asks the log for work for selected DNs, then records each created `DeleteBlocksCommand` in the status manager and marks it sent.

The tests prove that unflushed transactions are invisible, flushing advances container delete transaction IDs, and iterator progress avoids resending in-flight transactions. Commit tests show that invalid transaction IDs are ignored, partial DN acknowledgements leave transactions pending, and command timeout enables resend. Command-status tests cover unsent, sent, pending, failed, and timed-out commands. Replica-health tests prevent deletion commands when a container is unhealthy or has inadequate replicas. Standalone containers route transactions to their single hosting DN. Parameterized tests assert max-blocks-per-datanode splitting and optional data-distribution summary behavior.

## State and Persistence

The class uses real SCM metadata tables for containers and deleted block transactions, plus `SCMHADBTransactionBufferStub` to control flush boundaries. It explicitly closes and reopens `DeletedBlockLogImpl` to verify persisted transactions and current transaction state. It also mutates in-memory `containers` and `replicas` maps that back mocked `ContainerManager` calls.

## Dependencies and Integration Points

Dependencies include SCM metadata tables, HA transaction buffering, `ContainerManager`, `ReplicationManager`, `ContainerHealthResult`, `DeleteBlocksCommand`, datanode command status protos, `ScmBlockDeletingServiceMetrics`, and Ozone `DeletedBlock`/`BlockID`. The file ties block deletion to container health, container delete transaction IDs, datanode command reporting, and DB persistence.

## Risks and Test Signals

High-risk behavior includes duplicate delete transaction delivery, premature DB removal before enough DN acknowledgements, lost command-status state, slow large-batch operations, and deleting blocks from unhealthy or already deleted containers. The strongest signals are DB reopen persistence checks, timeout/resend assertions, no-duplicate set comparisons, and randomized add/get/commit/invariant loops.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/block/TestDeletedBlockLog.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/block/TestSCMBlockDeletingService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/block/TestSCMBlockDeletingService.java

## Purpose

This unit test validates `SCMBlockDeletingService`, the background SCM service that scans the deleted-block log and publishes `deleteBlocksCommand` events for eligible datanodes. It focuses on command fan-out and queue-limit filtering.

## Important APIs, Types, and Functions

- `SCMBlockDeletingService.getTasks().poll().call()` triggers one scanner execution.
- `getDatanodesWithinCommandLimit` filters datanodes by pending delete-command counts.
- `DeletedBlockLog.getTransactions` is mocked to return `DatanodeDeletedBlockTransactions`.
- `EventPublisher.fireEvent` is verified for `SCMEvents.DATANODE_COMMAND`.
- `ScmBlockDeletingServiceMetrics` counters are asserted after command publication.

## Control Flow and State Behavior

`setup` mocks `NodeManager`, `EventPublisher`, `SCMContext`, and `SCMServiceManager`. It creates three random healthy datanodes, associates the same synthetic `DeletedBlocksTransaction` with each DN, and configures the deleted-block log to return those assignments. The service is spied so `shouldRun` returns true. `testCall` executes one task and captures three `CommandForDatanode` events, proving one command is emitted to each healthy DN and metrics count both commands and transactions. `testLimitCommandSending` changes `NodeManager.getTotalDatanodeCommandCount` to simulate full and empty queues and verifies inclusion/exclusion.

## State and Persistence

There is no persistent state. Service state is in memory, metrics are registered for the test and unregistered afterward, and the mocked deleted-block transaction set is fixed.

## Dependencies and Integration Points

The test integrates `SCMBlockDeletingService` with `DeletedBlockLog`, `NodeManager`, `DatanodeConfiguration` queue limits, SCM event publishing, command protos, metrics, reconfiguration handler, and service lifecycle.

## Risks and Test Signals

Risk areas are overloading datanodes with delete commands, dropping eligible datanodes, and incorrect metrics. The event-captor assertions and queue-limit boundary checks provide direct signals for the scanner's external behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/block/TestSCMBlockDeletingService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/block/TestSCMDeleteBlocksCommandStatusManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/block/TestSCMDeleteBlocksCommandStatusManager.java

## Purpose

This unit test targets the nested `SCMDeleteBlocksCommandStatusManager`, which tracks SCM delete-block command IDs per datanode and maps each command to deleted-block transaction IDs until the command is sent, acknowledged, failed, or timed out.

## Important APIs, Types, and Functions

- `createScmCmdStatusData` creates `CmdStatusData` with default `TO_BE_SENT` state.
- `recordScmCommand` inserts command status under a datanode ID.
- `onSent` moves commands from `TO_BE_SENT` to `SENT`.
- `updateStatusByDNCommandStatus` reacts to DN heartbeat statuses `PENDING`, `EXECUTED`, and `FAILED`.
- `cleanTimeoutSCMCommand` and `cleanAllTimeoutSCMCommand` remove timed-out pending/sent records.

## Control Flow and State Behavior

`setup` creates two datanode IDs, four SCM command IDs, and four single-transaction sets. `testRecordScmCommand` verifies insertion and default state. `testOnSent` verifies the sent transition. Status-update tests record and send four commands, then simulate heartbeat reports: pending commands remain tracked as sent/pending execution, executed and failed commands are removed for downstream commit or resend processing. Cleanup tests use `Long.MAX_VALUE` to prove records do not expire early and `-1` to force timeout cleanup.

## State and Persistence

All state is in-memory within `manager.getScmCmdStatusRecord()`, a datanode-to-command map. The test does not touch the deleted-block DB; it isolates command-status lifecycle state.

## Dependencies and Integration Points

The test depends on `DatanodeID`, `StorageContainerDatanodeProtocolProtos.CommandStatus.Status`, and delete-service metrics. Production integration is with `DeletedBlockLogImpl` command creation, `onSent`, heartbeat status handling, and resend decisions.

## Risks and Test Signals

Risks include leaked command records, premature resend while a command is pending, or failure to resend failed/lost commands. Assertions inspect the exact map entries after each transition, giving precise state-machine coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/block/TestSCMDeleteBlocksCommandStatusManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/block/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/block/package-info.java

## Purpose

This package descriptor exists only to satisfy checkstyle for the `org.apache.hadoop.hdds.scm.block` test package.

## Important APIs, Types, and Functions

It declares the package and exports no classes, methods, fields, or annotations beyond the package declaration.

## Control Flow and State Behavior

There is no executable control flow, mutable state, or persistence.

## Dependencies and Integration Points

The file integrates only with Java package documentation/checkstyle conventions.

## Risks and Test Signals

Risk is minimal. If removed, package-level documentation checks may fail; otherwise it has no runtime or test behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/block/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/command/TestCommandStatusReportHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/command/TestCommandStatusReportHandler.java

## Purpose

This test verifies `CommandStatusReportHandler`, the event handler that processes datanode heartbeat command-status reports and fires SCM events for command-specific status consumers. The test concentrates on delete-block status reporting and log-visible event publication.

## Important APIs, Types, and Functions

- `CommandStatusReportHandler.onMessage` is the handler under test.
- `CommandStatusReportFromDatanode` wraps a datanode and `CommandStatusReportsProto`.
- `HddsTestUtils.createCommandStatusReport` builds heartbeat report protos.
- The test class implements `EventPublisher.fireEvent` and logs fired events for assertion.
- `getCommandStatusList` creates `deleteBlocksCommand` and `replicateContainerCommand` statuses.

## Control Flow and State Behavior

The first report contains an empty status list and should produce no delete-block or replicate-command event log entries. The second report contains executed delete-block status and failed replicate-container status. `onMessage` is expected to publish events, which the test observes by capturing this test class's logger output and checking for `Delete_Block_Status` and `deleteBlocksCommand`.

## State and Persistence

There is no persistent state. The only state is the captured logger buffer and synthesized command-status protos.

## Dependencies and Integration Points

The file depends on SCM heartbeat dispatcher payloads, datanode details, command-status protobufs, `HddsIdFactory`, `HddsTestUtils`, event publishing, and `GenericTestUtils.LogCapturer`. Production integration is with datanode heartbeat handling and downstream consumers such as deleted-block transaction status management.

## Risks and Test Signals

The test is log-based, so message wording changes can affect it even if events still fire. It gives useful signal that empty reports are ignored and non-empty reports dispatch command-specific events.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/command/TestCommandStatusReportHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/command/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/command/package-info.java

## Purpose

This package descriptor exists to satisfy checkstyle for the `org.apache.hadoop.hdds.scm.command` test package.

## Important APIs, Types, and Functions

It declares the package only. There are no exported types, functions, constants, or annotations.

## Control Flow and State Behavior

No executable control flow, state mutation, or persistence exists.

## Dependencies and Integration Points

The only integration point is Java package documentation/checkstyle.

## Risks and Test Signals

Risk is limited to style/build checks if package documentation is required. There are no behavioral test signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/command/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/MockNodeManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/MockNodeManager.java

## Purpose

`MockNodeManager` is a substantial test implementation of the SCM `NodeManager` interface. It supplies synthetic datanodes, storage metrics, network topology, pipeline membership, container membership, pending container allocation accounting, command queues, and node health transitions for SCM container, pipeline, placement, and block-manager tests.

## Important APIs, Types, and Functions

- Constructors create fake nodes, register provided nodes, or initialize from `DatanodeUsageInfo` and container sets.
- `getNodes`, `getAllNodes`, `getNodeCount`, `getStats`, `getNodeStats`, `getUsageInfo`, and `getDatanodeInfo` expose node inventory and storage reports.
- `checkSpaceAndRecordAllocation` and `removePendingAllocationForDatanode` delegate to `PendingContainerTracker`.
- `getPipelines`, `addPipeline`, `removePipeline`, `setNode2PipelineMap`, and `pipelineLimit` model pipeline membership.
- `setContainers`, `getContainers`, `addContainer`, `removeContainer`, `addContainer(size)`, and `delContainer(size)` model container placement and capacity changes.
- `register`, `getNode`, `getNodesByAddress`, and `getClusterNetworkTopologyMap` maintain topology and address lookup.
- `addDatanodeCommand`, `onMessage`, `getCommandCount`, and `clearCommandQueue` record commands sent to datanodes.

## Control Flow and State Behavior

The class initializes healthy, stale, and dead node lists based on a static `NodeData` table with capacity and used-space values. Registration adds `DatanodeInfo` to `NodeStateMap`, records DNS/IP-to-UUID mappings, assigns network names, and inserts nodes into `NetworkTopologyImpl`. Node queries synthesize `DatanodeInfo` objects with storage and metadata storage reports from `SCMNodeStat` values. Capacity mutations update both per-node metrics and aggregate metrics.

Pipeline state is tracked by `Node2PipelineMap`; container state by `NodeStateMap`; command state by a `Map<DatanodeID, List<SCMCommand<?>>>`; and pending allocation by `PendingContainerTracker`. Several `NodeManager` methods are intentionally no-op or return simple defaults because the class is a targeted test double rather than a full SCM node manager.

## State and Persistence

All state is in-memory. No SCM DB tables are used. The class simulates persistent-looking datanode reports and topology, but they are rebuilt per test instance.

## Dependencies and Integration Points

`MockNodeManager` integrates with a broad test surface: placement policies, pipeline manager, container manager, block allocation, disk balancer tests, event handlers, `NetworkTopologyImpl`, `DatanodeInfo`, `SCMNodeStat`, `NodeStateMap`, `Node2PipelineMap`, and storage-report helpers from `HddsTestUtils`.

## Risks and Test Signals

Because it returns simplified defaults for many methods, tests using it can miss behavior present in real `SCMNodeManager`. Important risks are stale aggregate metrics after manual mutation, topology lookup assumptions based on default rack paths, and no-op operational state methods. Its value is deterministic, low-overhead integration testing with realistic storage-report and topology enough for placement/allocation code.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/MockNodeManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/SimpleMockNodeManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/SimpleMockNodeManager.java

## Purpose

`SimpleMockNodeManager` is a minimal `NodeManager` implementation for tests that need controllable node status, pipeline counts, and container sets without the heavier behavior of `MockNodeManager`. Its own TODO notes it overlaps with `MockNodeManager` and exists because decommission/maintenance support made the older mock hard to refactor.

## Important APIs, Types, and Functions

- `register(DatanodeDetails, NodeStatus)` stores a `DatanodeInfo` and persists operational state fields onto the datanode details.
- `setNodeStatus` mutates a registered node's health and operational status.
- `setNodeOperationalState` updates operational state or throws `NodeNotFoundException`.
- `setPipelines` creates synthetic `PipelineID` sets; `getPipelines` returns null when empty to mirror SCM behavior.
- `setContainers` and `getContainers` manage datanode-to-container sets, returning an empty set by default.
- `getPendingContainerTracker` lazily creates a tracker; `checkSpaceAndRecordAllocation` always returns true.

## Control Flow and State Behavior

The implementation is map-backed: `nodeMap`, `pipelineMap`, and `containerMap` are concurrent maps keyed by `DatanodeID`. Registration and status changes update both the map and the persisted operational-state fields in `DatanodeDetails`. Most `NodeManager` interface methods below the functional core are placeholders that return null, zero, empty maps, or no-op, making the class suitable only for narrow tests that call the implemented subset.

## State and Persistence

All state is in-memory and local to the mock. It mutates `DatanodeDetails` persisted state fields for realistic status behavior but writes no external storage.

## Dependencies and Integration Points

It depends on `DatanodeInfo`, `NodeStatus`, `PipelineID`, `ContainerID`, `PendingContainerTracker`, and the `NodeManager` interface. Integration points are tests for replication, container placement, or node-state decisions that do not require full topology, storage metrics, heartbeat, or command-queue behavior.

## Risks and Test Signals

The main risk is accidental use in code paths requiring unimplemented `NodeManager` methods, where null or zero defaults can hide bugs or cause unrelated failures. The useful signal is precise control over node operational state, pipeline presence, and container membership with minimal fixture cost.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/SimpleMockNodeManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestCloseContainerEventHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestCloseContainerEventHandler.java

## Purpose

This test class verifies `CloseContainerEventHandler`, which responds to SCM close-container events by transitioning container state and sending `CloseContainerCommand` messages to pipeline datanodes. It covers invalid containers, invalid states, delayed lease-based close, RATIS close, and EC force-close behavior.

## Important APIs, Types, and Functions

- `CloseContainerEventHandler.onMessage(ContainerID, EventPublisher)` is the handler under test.
- `ContainerManager.getContainer` and `updateContainerState` provide container metadata and state transition.
- `PipelineManager.getPipeline` provides target datanodes.
- `LeaseManager.acquire` optionally delays command publication.
- `CloseContainerCommand` and `CommandForDatanode` are captured from `SCMEvents.DATANODE_COMMAND`.
- `createPipeline` and `createContainer` build RATIS and EC fixtures.

## Control Flow and State Behavior

`setup` mocks container manager, pipeline manager, leader SCM context, event publisher, and lease manager. Invalid-container and already-closed tests confirm no datanode commands are fired. The lease-delay test puts a container in `CLOSING`, uses a real `LeaseManager` behind a mock wrapper, verifies no immediate command publication, then waits for delayed publication. Valid close tests use an OPEN container, mock `updateContainerState(FINALIZE)` to set it CLOSING, and verify one close command per pipeline node. EC containers are expected to use force close, while RATIS containers are not.

## State and Persistence

No durable storage is used. Container state is held in mutable `ContainerInfo` objects and changed by Mockito answers. Lease state is in memory and shut down after the delay test.

## Dependencies and Integration Points

The test connects container lifecycle state, pipeline membership, SCM leader gating, lease scheduling, and event publication. It uses `RatisReplicationConfig`, `ECReplicationConfig`, `Pipeline`, `CloseContainerCommand`, `LeaseManager`, and Mockito captors.

## Risks and Test Signals

Risks include sending close commands for invalid containers, duplicate or missing datanode commands, incorrect EC force flag, and timing flakiness in delayed close. Captured command assertions verify target DN set, container ID, pipeline ID, and force flag.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestCloseContainerEventHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerActionsHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerActionsHandler.java

## Purpose

This unit test verifies that `ContainerActionsHandler` translates datanode-reported container actions into SCM container events. It specifically covers a datanode `CLOSE` action caused by a full container.

## Important APIs, Types, and Functions

- `ContainerActionsHandler` handles `SCMEvents.CONTAINER_ACTIONS`.
- `CloseContainerEventHandler` is mocked as the downstream `SCMEvents.CLOSE_CONTAINER` handler.
- `ContainerActionsFromDatanode` wraps a datanode and `ContainerActionsProto`.
- `EventQueue.fireEvent` and `processAll` drive asynchronous handler execution.

## Control Flow and State Behavior

The test creates an `EventQueue`, registers the real actions handler and mocked close handler, builds a single `ContainerAction` with container ID 1, action `CLOSE`, and reason `CONTAINER_FULL`, then fires the container-actions event. After processing the queue, it verifies the close handler received `ContainerID.valueOf(1L)` once.

## State and Persistence

There is no persistence. State exists only in the event queue and generated protobuf action.

## Dependencies and Integration Points

The test integrates datanode heartbeat container-action payloads with SCM's internal event queue and close-container event handling.

## Risks and Test Signals

The key risk is losing or misrouting datanode close requests, causing full containers to remain open. The single verification provides a focused signal that close actions are converted to the expected SCM event.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerActionsHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerManagerImpl.java

## Purpose

This test class verifies `ContainerManagerImpl` allocation, matching, lifecycle transitions, listing/counting, EC support, and pending replica operation completion. It uses a real SCM DB store and mock pipeline manager to cover persistent container table behavior.

## Important APIs, Types, and Functions

- `ContainerManagerImpl.allocateContainer`, `getMatchingContainer`, `getContainer`, `getContainers`, `getContainerStateCount`, `updateContainerState`, `transitionDeletingOrDeletedToTargetState`, `updateContainerReplica`, and `removeContainerReplica`.
- `DBStoreBuilder` and `SCMDBDefinition.CONTAINERS` provide the real container table.
- `SequenceIdGenerator` assigns container IDs.
- `MockPipelineManager` and spied `PipelineManager.checkSpaceAndRecordAllocation` control allocation viability.
- `ContainerReplicaPendingOps.completeAddReplica` and `completeDeleteReplica` are verified.

## Control Flow and State Behavior

`setUp` creates an SCM DB in a temp directory, HA stub, mock node manager, sequence ID generator, spied mock pipeline manager, one RATIS pipeline, and `ContainerManagerImpl`. Allocation tests verify an initially empty manager gains retrievable containers. Matching-container tests force space-check failure to return null and success to allocate for both RATIS and EC pipelines. Lifecycle tests traverse OPEN to CLOSING, QUASI_CLOSED, CLOSED, then DELETING/DELETED back to CLOSED through `transitionDeletingOrDeletedToTargetState`, while negative tests reject OPEN-to-CLOSED repair transitions. Listing tests allocate ten containers, page by start ID and count, filter by lifecycle state, and assert state counts after transitions. Replica tests verify updating/removing replicas completes pending add/delete operations.

## State and Persistence

The container table and sequence table are real DB tables under `@TempDir`; they are closed after each test. Container lifecycle state is persisted through `ContainerManagerImpl` into the table. Pending operation state is mocked and verified through method calls.

## Dependencies and Integration Points

Dependencies include SCM DB definitions, HA manager stubs, node manager mock, pipeline manager, replication configs, `ContainerStateMap`, `ContainerReplicaPendingOps`, and Ozone lifecycle events. The test is a central integration point for container metadata and pipeline space accounting.

## Risks and Test Signals

Risk areas include allocating containers when datanodes lack space, illegal lifecycle repairs, incorrect pagination/state indexes, EC/RATIS divergence, and pending operation leaks. Signals are strong because tests use real DB tables and assert exact state counts, null/non-null allocation outcomes, and pending-op method invocations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerReplica.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerReplica.java

## Purpose

This small test verifies that `ContainerReplica.toBuilder()` preserves all significant fields when rebuilding a replica object.

## Important APIs, Types, and Functions

- `ContainerReplica.newBuilder` sets bytes used, container ID, state, key count, origin node ID, sequence ID, replica index, and datanode details.
- `ContainerReplica.toBuilder().build()` creates the copy under test.
- `assertEquals` compares the original and copy, and also compares `toString`.

## Control Flow and State Behavior

The test builds one randomized closed `ContainerReplica`, calls `toBuilder`, rebuilds it, and verifies equality. It also compares string representations because a comment notes `equals` is incomplete, making the string check a guard for fields not covered by equality.

## State and Persistence

No persistence exists. Random field values are generated in memory using `ThreadLocalRandom`, `DatanodeID.randomID`, and `MockDatanodeDetails`.

## Dependencies and Integration Points

The file depends on `ContainerReplica`, `ContainerID`, `DatanodeID`, and mock datanode details. It protects builder/copy behavior used by container report processing, replica state mutation, and tests that clone replicas before modifying fields.

## Risks and Test Signals

The main risk is `toBuilder` omitting a field, causing later mutation code to drop metadata silently. Equality plus `toString` comparison provides a compact regression signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerReplica.java -->
