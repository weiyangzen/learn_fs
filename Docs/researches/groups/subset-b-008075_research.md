# subset-b-008075 Research

Grouped research for Apache Ozone SCM integration-test files. Each section preserves the source path and is bounded by reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestXceiverClientGrpc.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestXceiverClientGrpc.java

Purpose: Verifies `XceiverClientGrpc` command-target selection, topology-aware read ordering, retry traversal across pipeline nodes, interruption handling, preference for in-service replicas, and connection reuse after `getBlock`.

Important APIs and types: The test builds `Pipeline` instances with `RatisReplicationConfig`, `PipelineID`, `DatanodeDetails`, `MockDatanodeDetails`, and ordered node lists. It exercises `XceiverClientGrpc.sendCommandAsync`, `XceiverClientSpi`, `XceiverClientReply`, and `ContainerProtocolCalls.getBlock`, `readChunk`, and `readSmallFile`. It toggles `OZONE_NETWORK_TOPOLOGY_AWARE_READ_KEY` and observes `NodeOperationalState`.

Control flow: `setup` creates three random datanodes and a closed three-node Ratis pipeline whose `nodesInOrder` list is reversed. Tests override `sendCommandAsync` in anonymous clients to record or fail requested datanodes. Helpers synthesize get-block, read-chunk, and read-small-file protocol calls and return a completed success response.

State and persistence behavior: No durable state is written. The meaningful state is the pipeline's node ordering, the client's remembered primary connection after a successful command, the current thread interrupt flag, and per-datanode operational state used to avoid maintenance nodes for primary reads.

Dependencies and integration points: Integrates the SCM pipeline model, Ozone network-topology read config, container protocol call helpers, protobuf container commands, and the xceiver client retry path. It is a focused unit-style integration test without a MiniOzoneCluster.

Risks: Several tests catch `IOException` and continue, so a command helper failure could be masked unless the final datanode set assertion detects it. Random maintenance-node selection can set the same node twice, but still asserts the first selected read target is in service. The connection reuse assertion depends on the current set of commands sharing the client's selected datanode.

Test signals: Key signals are `getClosestNode` versus `getFirstNode`, exactly one command target over repeated successful calls, all datanodes removed after repeated failures, `InterruptedIOException` preserving interrupt status and cause, first read target remaining `IN_SERVICE`, and only one seen datanode across get/read calls on one client.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestXceiverClientGrpc.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestXceiverClientManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestXceiverClientManager.java

Purpose: Tests `XceiverClientManager` cache identity, reference counting, eviction, close semantics, and retry-failure invalidation against a real non-HA MiniOzoneCluster.

Important APIs and types: Uses `NonHATests.TestCase`, `StorageContainerLocationProtocolClientSideTranslatorPB.allocateContainer`, `XceiverClientManager`, `ScmClientConfig`, `XceiverClientSpi`, Guava `Cache`, `ClientTrustManager`, and `ContainerProtocolCalls.createContainer`. It varies `OZONE_SECURITY_ENABLED_KEY` and cache max size.

Control flow: `BeforeAll` obtains the cluster's storage-container-location client. Tests allocate containers with different replication factors, acquire clients, inspect refcounts, release with normal or invalidating flags, force cache eviction via max size one, and attempt container operations on retained or closed client references.

State and persistence behavior: Durable cluster state includes allocated containers and pipelines. Runtime state is the client cache keyed by pipeline ID plus replication type, each client's refcount, and whether release closes or invalidates the cached connection. Temporary metadata directories isolate security-enabled and non-security client managers.

Dependencies and integration points: Covers the client manager contract between OM/SCM client code, SCM container allocation, xceiver protocol operations, TLS trust-manager plumbing, and cache eviction. It relies on the non-HA cluster fixture for live datanode transport.

Risks: Cache-key construction is duplicated in assertions, so key-format changes require test updates. Some old client handles remain usable while referenced after eviction, so the test is sensitive to the intended distinction between cache membership and object lifetime. Cleanup releases an old duplicate reference after invalidation, which protects against leaked refcounts.

Test signals: Signals include identical client objects for repeated pipeline acquisition, refcount transitions 1 to 2 to 0, cache size zero after invalidating releases, evicted entries absent from the cache, successful use of a referenced-but-evicted client, `Client is closed` after final release, and new cache entries surviving release of stale invalidated clients.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestXceiverClientManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestXceiverClientMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestXceiverClientMetrics.java

Purpose: Verifies `XceiverClientMetrics` counters for synchronous latency and asynchronous pending operations.

Important APIs and types: Uses `MiniOzoneCluster`, `XceiverClientManager`, `XceiverClientSpi`, `ContainerTestHelper`, `ContainerCommandRequestProto`, `CompletableFuture<ContainerCommandResponseProto>`, metrics helpers `getMetrics`, `assertCounter`, and `getLongCounter`. The test is marked flaky for HDDS-11646.

Control flow: The test allocates one container, acquires a client, sends a synchronous create-container request, and checks zero pending counters plus a create latency operation count. It then starts a sender thread that repeatedly issues ten async write-small-file requests, waits until pending metrics become positive, stops the thread, waits for all futures, and checks pending counters return to zero.

State and persistence behavior: The MiniOzoneCluster persists allocated container state and datanode writes. Runtime state includes the metrics source, outstanding async response futures, `breakFlag`, and a latch that coordinates the sender thread shutdown.

Dependencies and integration points: Integrates live xceiver transport, SCM allocation, datanode command execution, Hadoop metrics2, and Ozone test metrics assertions.

Risks: This is timing-sensitive and explicitly flaky. Pending counters may be transient if async requests complete before metrics sampling. The sender thread catches and ignores exceptions, so the wait condition is the main failure detector.

Test signals: Strong signals are `PendingOps` and `numPendingCreateContainer` at zero after sync command, `CreateContainerLatencyNumOps` incremented to one, positive `PendingOps` and `numPendingPutSmallFile` during async load, all futures completed, and pending counters returning to zero.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestXceiverClientMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerStateManagerIntegration.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerStateManagerIntegration.java

Purpose: Exercises `ContainerStateManager` and `ContainerManager` behavior for allocation, owner scoping, restart recovery, matching-container selection, concurrent allocation distribution, lifecycle transitions, and replica-map mutation.

Important APIs and types: Uses `MiniOzoneCluster`, `StorageContainerManager`, `ContainerManager`, `ContainerStateManager`, `ContainerWithPipeline`, `ContainerInfo`, `ContainerID`, `ContainerReplica`, `LifeCycleEvent`, `LifeCycleState`, `ReplicationConfig`, and datanode replica protobuf states.

Control flow: Setup starts a three-datanode cluster with pipeline limit one and exits safe mode. Tests allocate containers through SCM client protocol, call `getMatchingContainer`, restart SCM without triggering container-report safe-mode exit, submit many concurrent matching-container calls, update lifecycle state through finalization/close/delete/cleanup, and directly add/remove `ContainerReplica` objects.

State and persistence behavior: Container metadata is persisted across SCM restart. The restart test verifies `OPEN` and `CLOSING` counts after allocated containers and finalized containers are reloaded. The lifecycle test exercises in-memory and persisted container counts. Replica-map tests manipulate runtime replica sets tied to container IDs.

Dependencies and integration points: Covers client protocol allocation, pipeline-manager container ownership counts, safe-mode restart behavior, replication config conversion, state-machine transition validation, and SCM's replica tracking.

Risks: The multithreaded matching-container test is marked flaky and fires many `CompletableFuture` tasks without collecting futures before sleeping, making timing and executor completion central. Owner-specific allocation depends on configured `OZONE_SCM_PIPELINE_OWNER_CONTAINER_COUNT`. A duplicate close event is issued to an already closed container to verify counts remain stable.

Test signals: Signals include distinct allocated container IDs, owner and replication metadata, five `OPEN` and five `CLOSING` containers after restart, matching-container cycling after per-owner capacity, balanced distribution under concurrent access, exact per-state counts through lifecycle transitions, and replica set contents after add/remove/reinsert operations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerStateManagerIntegration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/TestPendingContainerTrackerIntegration.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/TestPendingContainerTrackerIntegration.java

Purpose: Integration tests for `PendingContainerTracker`, proving container allocation records pending containers and incremental container reports remove them while metrics advance.

Important APIs and types: Uses `MiniOzoneCluster`, `ContainerManager`, `SCMNodeManager`, `PendingContainerTracker`, `SCMNodeMetrics`, `OzoneClient`, `OzoneBucket`, `OzoneOutputStream`, and `RatisReplicationConfig`.

Control flow: Setup configures slower full container reports, faster heartbeat interval, small container size, one container per owner and per metadata disk, and three datanodes. It validates the node manager exposes a pending tracker and captures its metrics. Tests allocate containers directly or write keys, then use `GenericTestUtils.waitFor` to observe added and removed counters increasing.

State and persistence behavior: Cluster state includes allocated containers and keys written through the object-store client. Pending-container state is maintained in SCM node-manager runtime state and removed when datanodes report the container through ICR processing. Metrics are the observed state contract.

Dependencies and integration points: Bridges SCM allocation, node pending tracking, datanode heartbeats/ICRs, object-store key creation, and SCM node metrics.

Risks: The comments and log message mention shorter intervals than the configured values, which can mislead maintainers. The five-second waits are tight for integration environments. Metrics are cumulative and only checked for increases, so the test validates lifecycle activity rather than exact pending set contents.

Test signals: Signals are non-null pending tracker and metrics, `NumPendingContainersAdded` increasing after allocation/key creation, `NumPendingContainersRemoved` increasing after ICR processing, and successful key writes that cause datanode reports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/TestPendingContainerTrackerIntegration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/TestScmApplyTransactionFailure.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/TestScmApplyTransactionFailure.java

Purpose: Validates failure handling in SCM HA state-machine transaction application for invalid container and pipeline mutations.

Important APIs and types: Uses `HATests.TestCase`, leader `StorageContainerManager`, `ContainerManager`, `PipelineManagerImpl`, `PipelineState`, `ContainerInfoProto`, `SCMException`, `StateMachineException`, `InvalidPipelineStateException`, and `DuplicatedPipelineIdException`.

Control flow: `BeforeAll` captures the leader's managers. One test closes an open Ratis three pipeline, creates a container protobuf referencing it, calls `ContainerStateManager.addContainer`, and verifies a nested exception chain plus absence of the container. It then allocates another container to prove the state machine still works. The second test replays an existing pipeline protobuf through the state manager and expects duplicate-ID failure.

State and persistence behavior: The rejected transactions must not mutate SCM metadata: the failed container ID remains absent and duplicate pipeline insertion does not replace existing state. The final allocation check confirms subsequent Ratis-applied transactions continue.

Dependencies and integration points: Covers SCM HA Ratis state-machine wrapping, pipeline state validation, container-state persistence, pipeline-state persistence, and exception propagation across the manager APIs.

Risks: The helper constructs container ID `1`, which assumes that ID is available in the HA fixture. Assertions depend on exact cause nesting: `SCMException` caused by `StateMachineException` caused by the domain exception.

Test signals: Signals include expected exception classes in order, `ContainerNotFoundException` after rejected add, successful allocation after a rejected transaction, and duplicate pipeline ID rejection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/TestScmApplyTransactionFailure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/metrics/TestSCMContainerManagerMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/metrics/TestSCMContainerManagerMetrics.java

Purpose: Verifies metrics emitted by `SCMContainerManagerMetrics` for container create/delete/list operations and report processing.

Important APIs and types: Uses `NonHATests.TestCase`, `SCMContainerManagerMetrics`, `ContainerManager`, `ContainerInfo`, `ContainerID`, `RatisReplicationConfig`, `ECReplicationConfig`, `ContainerNotFoundException`, `OzoneTestUtils.closeAllContainers`, and metrics helpers.

Control flow: The first test samples initial counters, successfully allocates a Ratis one container, attempts unsupported EC(8,5) allocation, deletes the valid container, attempts deletion of a random missing container, and lists containers. The second test verifies full container reports have already been processed, closes all containers, creates keys, and waits for successful ICR report counter growth.

State and persistence behavior: Container manager state changes through allocate and delete operations. Metrics persist in the running process and are sampled before and after operations. Report metrics reflect asynchronous datanode report processing.

Dependencies and integration points: Integrates SCM container manager, replication config validation, event queue container close helper, object-store key creation, datanode ICR reporting, and Hadoop metrics.

Risks: Metrics are cluster-global, so tests compare deltas rather than absolute values. ICR progress depends on asynchronous reports after key creation. Random missing container IDs are chosen in a narrow range but expected not to exist.

Test signals: Signals include successful-create increment, failure-create increment without successful-create change, successful-delete increment, failure-delete increment without successful-delete change, list-operation increment, positive full report count, and ICR success count increasing after test data creation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/metrics/TestSCMContainerManagerMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerIntegration.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerIntegration.java

Purpose: Integration coverage for `ReplicationManager` handling closed-container replica replacement, decommission and maintenance interactions, report generation, and deletion of empty quasi-closed containers.

Important APIs and types: Uses `MiniOzoneCluster`, `NodeManager`, `ContainerManager`, `ReplicationManager`, `ReplicationManagerConfiguration`, `ContainerOperationClient`, `ContainerReplicaCount`, `ReplicationManagerReport`, `ContainerHealthState`, `ContainerReplica`, `ContainerInfo`, `OzoneBucket`, and node operational states including `IN_MAINTENANCE`, `DECOMMISSIONED`, and `IN_SERVICE`.

Control flow: Setup starts five datanodes with fast heartbeat, report, admin-monitor, and replication intervals. Tests create keys, derive container IDs from key locations, close containers, select replica-hosting datanodes, shut down nodes, decommission or maintain nodes through `ContainerOperationClient`, and wait for node state and replica counts. Quasi-closed tests directly create empty replicas with stable or mixed replica states and notify replication manager.

State and persistence behavior: Persistent cluster state includes keys, containers, replica reports, and node operational state. Runtime state includes replication manager queues/reports and container replica sets. The empty quasi-closed paths transition container metadata from `QUASI_CLOSED` to `DELETING` and may update sequence ID from replica BCS IDs.

Dependencies and integration points: Bridges client key writes, SCM container close, node admin commands, dead-node detection, replica-count health logic, command status/report intervals, and replication-manager status checks.

Risks: The tests are timing-sensitive and rely on fast intervals plus repeated waits. Some count assertions intentionally include decommissioned live replicas or extra maintenance-created replicas, so policy changes around replica inclusion will affect them. Empty quasi-closed replica construction bypasses datanode reports and must stay aligned with production replica semantics.

Test signals: Signals include RM thread waiting after notify, closed containers retaining three healthy replicas after dead-node replacement, decommission adding an extra live replica until recommission, maintenance preserving sufficient replication, health report stats at zero for under/mis/over replication, `QUASI_CLOSED` empty containers becoming `DELETING`, and sequence ID updated to max stable replica BCS ID in mixed-state deletion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerIntegration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/node/TestDecommissionAndMaintenance.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/node/TestDecommissionAndMaintenance.java

Purpose: End-to-end tests for SCM datanode decommission and maintenance workflows across Ratis and EC containers, including open pipeline closure, replica creation/removal, SCM restart recovery, insufficient-node validation, maintenance expiry, and persisted datanode state.

Important APIs and types: Uses `MiniOzoneClusterProvider`, `StorageContainerManager`, `NodeManager`, `ContainerManager`, `PipelineManager`, `ContainerOperationClient`, `ReplicationManagerConfiguration`, `ContainerReplicaCount`, `RatisReplicationConfig`, `ECReplicationConfig`, `ContainerInfo`, `ContainerReplica`, `Pipeline`, and `TestNodeUtil` wait helpers.

Control flow: A shared provider supplies seven-datanode clusters with shortened heartbeat/report/admin-monitor intervals. Each test creates keys to force containers, finds containers and replica-hosting nodes, issues decommission or maintenance commands, waits for `DECOMMISSIONING`, `DECOMMISSIONED`, `ENTERING_MAINTENANCE`, `IN_MAINTENANCE`, or `IN_SERVICE`, restarts SCM or datanodes, and validates replica counts. Helpers generate data, fetch replica sets, choose a replica-hosting DN, stop replication manager, and wait for exact replica counts.

State and persistence behavior: The suite heavily tests persisted node operational state in `DatanodeDetails`, SCM's node status, container replica sets, pipeline states, and container metadata across SCM and datanode restarts. Maintenance expiry is injected by setting node operational state with an end timestamp. Dead maintenance nodes can retain or lose replicas depending on restart timing.

Dependencies and integration points: Integrates SCM admin CLI client, datanode heartbeat/report loops, pipeline manager, replication manager, OM/Ozone key writes, EC and Ratis placement requirements, SCM decommission monitor, and cluster restart behavior.

Risks: The tests are long-running and rely on asynchronous state convergence. The provider reuses clusters, so `tearDown` must destroy supplied clusters. Several checks are policy-sensitive, especially required remaining nodes for EC, maintenance redundancy, and whether dead maintenance replicas are purged after SCM restart.

Test signals: Signals include decommissioned nodes reaching persisted state, Ratis replica counts moving 3 to 4 to 3 and EC 5 to 6 to 5, stuck decommission completing after SCM restart, insufficient non-forced operations leaving zero transition nodes, force operations entering transition state, maintenance preserving or creating replicas as expected, automatic expiry returning nodes to service, dead maintenance node restart causing new replicas, and decommission monitor tracking restored maintenance nodes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/node/TestDecommissionAndMaintenance.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeUtil.java

Purpose: Provides shared helper methods for SCM node integration tests to wait for operational, health, and persisted datanode states and to format datanode host/port strings.

Important APIs and types: Exposes `waitForDnToReachOpState`, `waitForDnToReachHealthState`, `getNodeStatus`, `getDNHostAndPort`, and `waitForDnToReachPersistedOpState`. Uses `NodeManager`, `NodeStatus`, `DatanodeDetails`, `HddsProtos.NodeOperationalState`, `HddsProtos.NodeState`, JUnit assertions, and `GenericTestUtils.waitFor`.

Control flow: Wait helpers poll every 200 ms for up to 30 seconds. `getNodeStatus` wraps `nodeManager.getNodeStatus` in `assertDoesNotThrow` to make lambdas fail with assertion context rather than checked exceptions. `getDNHostAndPort` returns hostname plus the first registered datanode port.

State and persistence behavior: The helper itself has no durable state. It observes SCM runtime `NodeStatus` and datanode-side persisted operational state stored on the mutable `DatanodeDetails` object.

Dependencies and integration points: Used by decommission, maintenance, and replication-manager integration tests. It standardizes polling intervals and CLI address formatting for `ContainerOperationClient` node admin calls.

Risks: Persisted-state waiting checks the supplied object, so callers must pass a `DatanodeDetails` instance that will be updated by the code under test. `getDNHostAndPort` assumes `getPorts().get(0)` is valid and appropriate for admin commands.

Test signals: Consumers rely on these helpers for timeout-based confirmation of health, operational state, persisted datanode operational state, and stable host:port identifiers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/node/TestQueryNode.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/node/TestQueryNode.java

Purpose: Tests SCM node query results for stale and dead nodes after datanode shutdown.

Important APIs and types: Uses `MiniOzoneCluster`, `ContainerOperationClient.queryNode`, `HddsProtos.QueryScope.CLUSTER`, `NodeState.STALE`, `NodeState.DEAD`, and SCM node-count APIs.

Control flow: Setup starts a five-datanode cluster with one-second reports, three-second stale interval, six-second dead interval, and relaxed Ratis pipeline limit. The test asynchronously shuts down two datanodes, waits until querying stale plus dead returns two total nodes, waits for SCM node count of dead nodes to reach two, then asserts stale query returns zero and dead query returns two.

State and persistence behavior: Runtime node health state transitions from healthy to stale/dead based on missing heartbeats. No durable state is under direct test, though the cluster holds normal SCM metadata while running.

Dependencies and integration points: Covers `ContainerOperationClient` query path, SCM node manager health tracking, datanode shutdown behavior, and timing configuration for node-state transitions.

Risks: The executor is not explicitly shut down. The wait from mixed stale/dead to all dead assumes interval timing allows final assertions within four seconds after the intermediate condition. The client is constructed from the same configuration rather than cluster-provided RPC address changes.

Test signals: Signals are stale-plus-dead query count reaching two, SCM dead node count reaching two, final stale query count zero, and final dead query count two.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/node/TestQueryNode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/node/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/node/package-info.java

Purpose: Package-level documentation marker for SCM node-related tests.

Important APIs and types: Declares package `org.apache.hadoop.hdds.scm.node` and contains only a Javadoc comment stating that the package contains unit tests for node-related SCM functions.

Control flow: No runtime control flow; the file only contributes package metadata at compile time.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Provides package documentation for tests around node status, decommission, maintenance, and query behavior in the same package.

Risks: No behavioral risk. Its only maintenance concern is keeping the package declaration synchronized with the directory.

Test signals: Compilation of package metadata is the only signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/node/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/package-info.java

Purpose: Package-level documentation marker for the SCM integration-test package.

Important APIs and types: Declares package `org.apache.hadoop.hdds.scm` and contains only a short Javadoc comment labeled package info tests.

Control flow: No executable logic.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Provides package metadata for SCM integration tests such as xceiver client manager, gRPC client behavior, and metrics.

Risks: No behavioral risk beyond package/directory mismatch.

Test signals: Successful compilation of package metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestLeaderChoosePolicy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestLeaderChoosePolicy.java

Purpose: Tests Ratis pipeline leader-selection policies, including balanced suggested leaders and persistence of suggested leader IDs across SCM restart.

Important APIs and types: Uses `MiniOzoneCluster`, `PipelineManager`, `Pipeline`, `DatanodeID`, `RatisReplicationConfig`, `MinLeaderCountChoosePolicy`, `DefaultLeaderChoosePolicy`, and configuration keys for datanode pipeline limits, Ratis pipeline limits, factor-one auto creation, and leader choosing policy.

Control flow: `init` starts a cluster with tuned heartbeat intervals and configured pipeline limits. `checkLeaderBalance` waits for each pipeline's actual leader to match its suggested leader, counts leaders per datanode, and asserts balance. Tests disable factor-one creation, select policy implementation by class name, wait for three Ratis three pipelines, close random pipelines in a loop, and restart SCM to compare persisted suggested leaders.

State and persistence behavior: Pipeline state and suggested leader IDs are persisted in SCM metadata and reloaded after restart. Runtime leader state is reported by Ratis and compared against SCM's suggested leader.

Dependencies and integration points: Integrates pipeline auto-creation, leader selection implementations, SCM restart recovery, Ratis leader reports, and pipeline manager state.

Risks: The class is annotated `@Unhealthy("This test was never enabled")`, indicating known instability or disabled status. Random pipeline destruction can close multiple pipelines per iteration. Balance assertions assume exact equal distribution and actual leader convergence to suggested leader.

Test signals: Signals include expected Ratis three pipeline counts, no factor-one pipelines when disabled, each datanode having one leader under min-leader policy, persisted pipeline count after restart, matching pipeline IDs and suggested leaders before and after restart, and default policy creating pipelines without balance assertions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestLeaderChoosePolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestMultiRaftSetup.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestMultiRaftSetup.java

Purpose: Verifies multi-Raft pipeline creation behavior with and without disallowing repeated peer sets.

Important APIs and types: Uses `MiniOzoneCluster`, `NodeManager`, `PipelineManager`, `ReplicationConfig`, `PipelineID`, `Pipeline`, `DatanodeDetails`, and config keys `OZONE_DATANODE_PIPELINE_LIMIT`, `OZONE_SCM_DATANODE_DISALLOW_SAME_PEERS`, and `OZONE_SCM_PIPELINE_DESTROY_TIMEOUT`.

Control flow: Tests start clusters with three or five datanodes and pipeline limit two. With same peers allowed, two Ratis three pipelines are expected on three datanodes and each datanode's peer list contains the other nodes. With same peers disallowed, only one Ratis three pipeline can form on three datanodes and only two on five datanodes; explicit extra creation is expected to fail.

State and persistence behavior: Pipeline membership and node-to-pipeline counts live in SCM runtime state during each cluster. No restart persistence is tested.

Dependencies and integration points: Covers node peer-list tracking, pipeline placement constraints, automatic pipeline creation, and explicit pipeline creation failure when no valid peer set remains.

Risks: `assertNotSamePeers` removes from the list returned by `nodeManager.getAllNodes`, so it assumes a mutable copy. Shutdown is manual inside each test rather than an `@AfterEach`, increasing cleanup sensitivity if assertions fail before shutdown.

Test signals: Signals include exact Ratis three pipeline counts, `IOException` on impossible pipeline creation, one datanode with three total pipelines in the five-node case, and pipeline breakdown of one factor-one plus two factor-three pipelines for that datanode.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestMultiRaftSetup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestNode2PipelineMap.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestNode2PipelineMap.java

Purpose: Tests the consistency of mappings from pipeline to open containers and from datanode to pipelines.

Important APIs and types: Uses `NonHATests.TestCase`, `StorageContainerManager`, `ContainerManager`, `PipelineManager`, `ContainerWithPipeline`, `ContainerInfo`, `ContainerID`, `PipelineID`, `DatanodeDetails`, `LifeCycleEvent`, and Ratis three replication config.

Control flow: Setup allocates a Ratis three container and resolves its pipeline. The test fetches containers in that pipeline, verifies the allocated container is present, queries a datanode's pipelines, closes the container through `FINALIZE` and `CLOSE`, verifies the pipeline's open-container set shrinks, then closes and deletes the pipeline and checks datanode mappings no longer contain it.

State and persistence behavior: Runtime SCM maps are the target: pipeline-to-open-container set and node-to-pipeline set. Container lifecycle transitions update whether a container is considered in-pipeline.

Dependencies and integration points: Integrates container lifecycle management, pipeline manager deletion, and SCM node manager pipeline membership tracking.

Risks: The test assumes the allocated pipeline has exactly three nodes and that no unrelated open-container changes affect the initial set except the tested container. It is abstract and relies on the non-HA fixture implementation.

Test signals: Signals include allocated container ID present in pipeline set, datanode pipeline set containing the pipeline ID, pipeline container count decreasing by one after close, and datanode pipeline set excluding the ID after pipeline delete.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestNode2PipelineMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestNodeFailure.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestNodeFailure.java

Purpose: Tests Ratis node-failure detection causing pipeline closure and bounded close-action logging.

Important APIs and types: Uses `MiniOzoneCluster`, `PipelineManager`, `Pipeline`, `PipelineID`, `XceiverServerRatis`, `DatanodeRatisServerConfig`, `RatisReplicationConfig`, `GenericTestUtils.LogCapturer`, and Ratis follower slowness/no-leader timeouts.

Control flow: `BeforeAll` starts six datanodes with datanode pipeline limit one, two-second pipeline reports, and Ratis slowness timeout ten seconds. The test captures `XceiverServerRatis` logs, waits for each Ratis pipeline to be open, shuts down the first node in each pipeline, waits for SCM to mark the pipeline closed or deleted, then counts close-action log tokens.

State and persistence behavior: Pipeline state transitions from open to closed/deleted in SCM due to datanode failure. Datanode runtime Ratis state emits close actions; no persistence is inspected.

Dependencies and integration points: Integrates datanode shutdown, Ratis failure detection, pipeline report handling, SCM pipeline state, and log-based flood protection.

Risks: Log-count assertion is brittle and tied to exact log text `pipeline Action CLOSE`. The wait interval uses `timeForFailure / 2` even though `timeForFailure` is derived from a `Duration` cast path, so timeout unit behavior must remain as expected. Shutdown of first nodes across multiple pipelines can overlap effects.

Test signals: Signals include each pipeline reaching `OPEN`, closure or deletion after first-node shutdown, and exactly two close-action log occurrences.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestNodeFailure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineClose.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineClose.java

Purpose: Tests SCM and datanode behavior around closing pipelines with closed or open containers, pipeline close actions, Ratis log failure triggers, and duplicate close-trigger suppression.

Important APIs and types: Uses `MiniOzoneCluster`, `StorageContainerManager`, `ContainerManager`, `PipelineManager`, `PipelineActionHandler`, `SCMEvents.PIPELINE_ACTIONS`, `PipelineActionsFromDatanode`, `OzoneContainer`, `XceiverServerRatis`, `ClosePipelineCommandHandler`, `RaftGroupId`, and `ClosePipelineInfo`.

Control flow: Setup creates a three-node cluster and allocates a Ratis three container before each test. Tests close containers then close/delete pipelines, close a pipeline with an open container and wait for the container to enter `CLOSING`, inject a datanode pipeline action and wait for the datanode report to omit the pipeline, mock the event handler while triggering `handleNodeLogFailure`, and use reflection to pre-populate `pipelinesInProgress` before repeatedly calling `triggerPipelineClose`.

State and persistence behavior: SCM pipeline and container lifecycle state are mutated. Node-to-pipeline maps are updated on deletion. Datanode Ratis state and command handler in-progress sets affect whether duplicate close commands are emitted. No SCM restart is included.

Dependencies and integration points: Covers SCM event queue, datanode heartbeat pipeline actions, Ratis log failure handling, command dispatcher close-pipeline state, and container/pipeline manager interaction.

Risks: Reflection into `pipelinesInProgress` is implementation-sensitive. Log-based duplicate assertion depends on exact lowercase text. Event queue handler mocking adds another handler to a live queue and assumes captured action ordering. The init method changes some config after cluster build, so only config read later will see those values.

Test signals: Signals include pipeline container set size one then zero after container close, node pipeline mappings removed after delete, open container reaching `CLOSING` on pipeline close, datanode pipeline report no longer containing the closed ID, SCM `PipelineNotFoundException` after datanode action, captured CLOSE action for the right pipeline after log failure, and ten duplicate triggers producing ten skipped-close log messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineClose.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineManagerMXBean.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineManagerMXBean.java

Purpose: Verifies the JMX MXBean view of SCM pipeline state counts.

Important APIs and types: Uses `NonHATests.TestCase`, platform `MBeanServer`, `ObjectName` `Hadoop:service=SCMPipelineManager,name=SCMPipelineManagerInfo`, `TabularData`, `CompositeData`, and `PipelineManager.getPipelineInfo`.

Control flow: The test repeatedly reads the `PipelineInfo` JMX attribute and compares each key/value against the pipeline manager's direct `getPipelineInfo` map until they match or timeout. `getMetricsCount` scans the tabular data for a row whose `key` equals the state string.

State and persistence behavior: No durable state is changed. Runtime pipeline manager state and MXBean-exported state must remain synchronized.

Dependencies and integration points: Covers JMX registration/export for `SCMPipelineManagerInfo` and the conversion of pipeline state counts into open MBean tabular data.

Risks: Three-second timeout is short for slow test environments. The test only verifies states present in the direct map, not extra rows in the MXBean. Values are parsed through `toString`, so MXBean representation changes could break it.

Test signals: All direct pipeline state count entries have matching JMX rows and values within the wait period.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineManagerMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestRatisPipelineCreateAndDestroy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestRatisPipelineCreateAndDestroy.java

Purpose: Tests automatic Ratis pipeline creation after pipeline destruction, optional factor-one auto creation, and pipeline creation behavior when datanodes are stopped and restarted.

Important APIs and types: Uses `MiniOzoneCluster`, `PipelineManager`, `Pipeline`, `HddsDatanodeService`, `RatisReplicationConfig`, `NodeStatus.inServiceHealthy`, `SCMException.ResultCodes.FAILED_TO_FIND_SUITABLE_NODE`, and `SCMService.Event.PRE_CHECK_COMPLETED`.

Control flow: `init` starts a cluster with datanode pipeline limit two and fast pipeline creation interval. The first test waits for two Ratis three pipelines and six factor-one pipelines, closes all open Ratis three pipelines, and waits for replacements. The second disables factor-one auto creation and repeats replacement checks. The restart test starts three datanodes, shuts all down, waits for zero healthy in-service nodes, asserts explicit Ratis three creation fails, waits for open pipeline count to drop, restarts datanodes, closes old pipelines, triggers pre-check completion, and waits for a new pipeline.

State and persistence behavior: Pipeline manager runtime state is mutated through close operations and node liveness changes. The test does not restart SCM, but it checks automatic background services react to pipeline deletion and node availability.

Dependencies and integration points: Covers pipeline creator service, node manager health accounting, factor-one pipeline policy, SCM service manager pre-check events, and placement failure reporting.

Risks: `waitForPipelines(0)` uses `size() >= numPipelines`, so passing zero returns immediately and does not actually wait for destruction. Replacement timing depends on background pipeline creation. Datanode restart branch only waits if enough nodes report healthy.

Test signals: Signals include at least two open Ratis three pipelines after startup and after destruction, factor-one pipeline count equal to datanode count or zero depending on config, explicit creation failure with `FAILED_TO_FIND_SUITABLE_NODE`, zero in-service healthy nodes after shutdown, and new pipeline creation after datanode restart plus pre-check event.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestRatisPipelineCreateAndDestroy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestSCMPipelineMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestSCMPipelineMetrics.java

Purpose: Verifies `SCMPipelineMetrics` counters for pipeline creation, destruction, and per-pipeline block allocation metric lifecycle.

Important APIs and types: Uses `NonHATests.TestCase`, `SCMPipelineMetrics`, `PipelineManager`, `Pipeline`, `AllocatedBlock`, SCM block manager `allocateBlock`, `ExcludeList`, `RatisReplicationConfig`, and metrics assertion helpers.

Control flow: Setup captures the shared MiniOzoneCluster. Tests read the pipeline-created counter after cluster startup, close/delete the first available pipeline and assert the destroyed counter increments, allocate a block on a Ratis one pipeline, read the generated per-pipeline block allocation metric, then close the pipeline via client protocol and assert that metric is no longer exported.

State and persistence behavior: Pipeline manager state changes when a pipeline is deleted or closed. Metrics state is registered and unregistered with pipeline lifecycle. Block allocation updates per-pipeline counters.

Dependencies and integration points: Covers SCM pipeline metrics source, SCM block manager, client protocol close pipeline path, and dynamic metric-name generation based on pipeline identity.

Risks: Uses the first pipeline from a shared test cluster, so concurrent tests or fixture changes can affect available pipeline type/state. The final assertion expects an `AssertionError` from missing metric lookup rather than a zero value.

Test signals: Signals include positive `NumPipelineCreated`, `NumPipelineDestroyed` increment by one, positive per-pipeline block allocation counter, and absence of that metric after pipeline closure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestSCMPipelineMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestSCMRestart.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestSCMRestart.java

Purpose: Tests SCM restart and recovery of persisted pipeline objects and reuse of recovered pipelines for new allocations.

Important APIs and types: Uses `MiniOzoneCluster`, `StorageContainerManager`, `ContainerManager`, `PipelineManager`, `Pipeline`, `ContainerInfo`, `RatisReplicationConfig`, and replication factors one and three.

Control flow: `BeforeAll` starts four datanodes, allocates a Ratis three container for owner `Owner1` and a Ratis one container for owner `Owner2`, opens both pipelines, restarts SCM with persistence, and refreshes managers. The test fetches both pipelines by ID after restart, compares object identity and equality with pre-restart pipeline objects, then allocates another Ratis three container for `Owner1`.

State and persistence behavior: Pipeline metadata and container-to-pipeline ownership survive SCM restart. After restart, objects are new Java instances but equal in persisted identity/content. Matching-container allocation should choose the same recovered pipeline for the same owner.

Dependencies and integration points: Covers SCM metadata store reload, pipeline manager equality semantics, container manager matching allocation, and restart of storage container manager while datanodes continue.

Risks: Static cluster and pipeline fields mean initialization failures affect all tests. The test assumes owner/pipeline matching will continue to reuse the first pipeline under current container-per-owner policy.

Test signals: Signals are `assertNotSame` but `assertEquals` for both recovered pipeline objects, and new container allocation using the original Ratis three pipeline ID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestSCMRestart.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/package-info.java

Purpose: Package-level documentation marker for SCM pipeline-related tests.

Important APIs and types: Declares package `org.apache.hadoop.hdds.scm.pipeline` and contains a short package-info Javadoc comment.

Control flow: No executable logic.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Provides package metadata for pipeline tests covering creation, closure, restart, metrics, and MXBean behavior.

Risks: No behavioral risk beyond package/directory mismatch.

Test signals: Successful compilation of package metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestSCMSafeModeWithPipelineRules.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestSCMSafeModeWithPipelineRules.java

Purpose: Tests SCM safe-mode exit behavior governed by healthy-pipeline and one-replica-pipeline safe-mode rules after SCM restart with only partial datanode recovery.

Important APIs and types: Uses `MiniOzoneCluster`, `PipelineManager`, `SCMSafeModeManager`, `HealthyPipelineSafeModeRule`, `OneReplicaPipelineSafeModeRule`, `SafeModeRuleFactory`, `ReplicationManager`, `RatisReplicationConfig`, and `SCMContainerPlacementCapacity`.

Control flow: Setup starts six datanodes with one Ratis three pipeline per three nodes, factor-one pipelines, same-peer disallowance, and long post-safe-mode pipeline creation interval. The test waits for initial pipelines, stops the cluster, restarts OM and SCM without datanodes, restarts all datanodes from one Ratis three pipeline, validates the healthy-pipeline rule but not the one-replica rule, then restarts one datanode from the second pipeline and waits for full safe-mode exit.

State and persistence behavior: Pipeline metadata is persisted and reloaded by SCM even when datanodes are not all alive. Safe-mode rule state is computed from datanode reports and persisted pipeline membership. Replication manager should start only after safe-mode prechecks finish.

Dependencies and integration points: Covers SCM safe-mode rule factory, pipeline reports, persisted pipeline metadata, datanode restart, OM/SCM restart ordering, and replication-manager activation after safe mode.

Risks: The test depends on exact thresholds: `ceil(0.1 * 2)` and `ceil(0.9 * 2)` for two Ratis three pipelines. Directly using `pipelineList.get(1)` assumes two pipelines exist and stable ordering. Long waits are needed because partial datanode restart controls rule validation.

Test signals: Signals include initial Ratis one and three pipeline counts, healthy-pipeline rule validating after one full pipeline reports, one-replica rule remaining false until a second pipeline member reports, SCM remaining in safe mode before that, SCM exiting safe mode afterward, original total pipeline count retained during wait duration, and replication manager running.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestSCMSafeModeWithPipelineRules.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestSafeModeSCMHA.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestSafeModeSCMHA.java

Purpose: Tests that an SCM follower in an HA cluster can restart and exit safe mode after state has synced from the leader.

Important APIs and types: Uses `MiniOzoneHAClusterImpl`, HA builder with OM and SCM service IDs, `StorageContainerManager`, `SCMStateMachine`, `LastAppliedTermIndex`, `OzoneClient`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, and `RatisReplicationConfig`.

Control flow: Setup builds an HA cluster with one OM and three SCMs, all active. The test creates a volume, bucket, and Ratis three key, identifies one leader SCM and one follower SCM, waits until leader and follower SCM state machines have the same applied log index, restarts the follower SCM, and waits until the restarted follower leaves safe mode.

State and persistence behavior: HA SCM Ratis log state must replicate the object/container changes to the follower before restart. On restart, follower safe-mode state is derived from replicated SCM metadata and live reports.

Dependencies and integration points: Covers SCM HA Ratis replication, follower restart, safe-mode exit, OM/object-store writes, and cluster HA service wiring.

Risks: The leader/follower selection keeps the last non-leader encountered as follower. Waiting for equal log index does not compare term or all internal state, but it is the synchronization signal used here. Safe-mode exit depends on datanode reports after follower restart.

Test signals: Signals include non-null leader and follower, equal last-applied indexes before restart, and restarted follower `isInSafeMode` becoming false.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestSafeModeSCMHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/storage/TestCommitWatcher.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/storage/TestCommitWatcher.java

Purpose: Tests `CommitWatcher` buffer-release behavior after successful Ratis commits and after watch failures.

Important APIs and types: Uses `MiniOzoneCluster`, `XceiverClientManager`, `XceiverClientRatis`, `CommitWatcher`, `BufferPool`, `ChunkBuffer`, `XceiverClientReply`, `ContainerTestHelper`, `BlockID`, Ratis client/server timeout configs, `HddsClientUtils.checkForException`, and Ratis exceptions including `RaftRetryFailureException`, `TimeoutIOException`, `AlreadyClosedException`, and `NotReplicatedException`.

Control flow: Setup configures large block/chunk/flush sizes, disables checksums, stretches SCM node failure timers to keep pipelines alive, and creates a volume/bucket to initialize the cluster. Each test allocates a Ratis three container, acquires an xceiver client, writes chunks asynchronously, sends put-block requests, stores reply log indexes with buffers in `CommitWatcher`, waits for put-block futures, and watches commit indexes. The exception test shuts down two pipeline nodes before watching a future index to force an actual Ratis watch call and error.

State and persistence behavior: Runtime state includes buffer-pool allocation, `CommitWatcher` commit-index map, total acknowledged data length, and the Ratis client's replicated minimum commit index. Persistent cluster state includes container/block writes sent to datanodes.

Dependencies and integration points: Integrates stream buffer management, Ratis async write and watch APIs, SCM container allocation, xceiver client acquisition/refcounting, client timeout configuration, and datanode shutdown failure modes.

Risks: Exception behavior is intentionally broad because different Ratis failure paths can surface under timing. The tests track but do not assert the local `length` variable. Buffer cleanup depends on `finally` clearing the pool. Shutting down two nodes in a five-node cluster targets a three-node pipeline and assumes they are members.

Test signals: Signals include xceiver refcount one, commit-index map size two after put-block futures, first watch removing the first log index and acknowledging at least one chunk, last watch removing all entries and acknowledging two chunks, watch failure unwrapping to one accepted Ratis exception type, and post-failure map/ack length matching whether the target log index was replicated.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/storage/TestCommitWatcher.java -->
