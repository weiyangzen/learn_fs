# subset-b-008042 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestFindTargetStrategy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestFindTargetStrategy.java

Purpose: This test covers the target ordering strategies used by container balancer move planning. It verifies that `FindTargetGreedyByUsageInfo` sorts candidate targets by usage and that `FindTargetGreedyByNetworkTopology` prioritizes network proximity before usage when selecting target order for a source datanode.

Important APIs and types: The suite directly exercises `FindTargetStrategy.resetPotentialTargets`, `FindTargetGreedyByUsageInfo.reInitialize`, `sortTargetForSource`, `getPotentialTargets`, `FindTargetGreedyByNetworkTopology`, `DatanodeUsageInfo`, `SCMNodeStat`, `MockNodeManager`, `NetworkTopologyImpl`, `NodeSchemaManager`, and the root/rack/nodegroup/leaf schemas.

Control flow: Usage tests build three `DatanodeUsageInfo` instances with different used-space values, reinitialize the strategy, sort for an arbitrary source, and assert descending usage order. Reset tests create a `MockNodeManager`, restrict potential targets to one datanode, and verify the strategy maps the datanode back to its usage info. Topology tests construct a source and five targets across nodegroups and racks, assert expected distance costs, then verify nearest targets sort ahead of farther but higher-used nodes.

State and persistence behavior: There is no persistence. State is held in strategy candidate collections, generated datanode details, node stats, and the singleton `NodeSchemaManager` topology schema initialization.

Dependencies and integration points: These strategies feed container balancer target selection and depend on SCM node metrics plus network topology distance semantics. The test anchors behavior used before `MoveManager` issues actual container moves.

Risks: The topology test assumes stable distance costs for the configured schema and mutates the singleton schema manager. Equal-distance ordering depends on usage, so changes in tie-breaking or collection ordering can break assertions.

Test signals: Exact target order after sorting, exact potential target count, successful reset to a single mapped `DatanodeUsageInfo`, and expected topology distance costs of 2, 4, and 6.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestFindTargetStrategy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestMoveManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestMoveManager.java

Purpose: This suite validates `MoveManager`, the balancer component that turns a requested container move into a low-priority replication command followed by a forced delete from the source. It checks preflight rejection, asynchronous completion, timeout handling, EC replica indexes, and the optional ability to move non-standard containers.

Important APIs and types: It mocks `ReplicationManager` and `ContainerManager`, and asserts `MoveManager.MoveResult` values including node health failures, in-flight op failures, replication/delete timeouts, policy failures, and `COMPLETED`. It uses `ContainerReplicaOp` ADD/DELETE events, `ContainerHealthResult`, `NodeStatus`, `TestClock`, `ContainerInfo`, `ContainerReplica`, `RatisReplicationConfig`, `ECReplicationConfig`, and `ReplicationTestUtil`.

Control flow: Setup creates a closed RATIS container, replica set, node-status map, pending-op list, and mocked health checks. Tests call `move`, inspect immediate future results for rejected moves, or drive the normal two-stage path by invoking `opCompleted` for ADD and DELETE operations. Helper `setupSuccessfulMove` verifies that the replicate command is sent, while `completeMove` simulates successful add and delete completion.

State and persistence behavior: There is no on-disk state. Runtime state includes the active move future, source/target datanodes, replica set mutation, pending operation list, node status map, clock-derived deadlines, and `includeNonStandardContainers` / timeout configuration inside `MoveManager`.

Dependencies and integration points: The test models integration with replication health checks, pending replica operation tracking, command dispatch to datanodes, container metadata lookup, and balancer rules for CLOSED, QUASI_CLOSED, over-replicated, and EC containers.

Risks: Many assertions depend on mocked replica sets and future completion rather than real datanode reports. Source replica selection uses set iteration in helpers. Deadline behavior is sensitive to replication timeout, move timeout, and the default datanode timeout offset.

Test signals: Signals include exact `MoveResult` values, no duplicate active move, replicate/delete command verification with replica indexes, future completion after callbacks, delete suppression when the source replica disappears, policy rejection before deleting an unsafe source, and successful QUASI_CLOSED/over-replicated moves only when enabled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestMoveManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestableCluster.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestableCluster.java

Purpose: `TestableCluster` is a package-private balancer test fixture that creates a deterministic-shaped but partly random SCM cluster with datanodes, containers, replicas, capacity statistics, and expected utilization boundaries. It supports tests that need realistic container-to-datanode and container-to-replica maps without a live SCM.

Important APIs and types: The helper exposes `getDatanodeToContainersMap`, `getCidToInfoMap`, `getCidToReplicasMap`, `getNodesInCluster`, `getNodeUtilizationList`, `getAverageUtilization`, `getNodeCount`, and `getUnBalancedNodes`. It constructs `DatanodeUsageInfo`, `SCMNodeStat`, `ContainerInfo`, `ContainerID`, `ContainerReplica`, RATIS and EC `ReplicationConfig` instances, and `MockDatanodeDetails`.

Control flow: The constructor creates equally spaced target utilization values, calls `generateData` to assign increasing numbers of variable-size containers to nodes, calls `createReplicasForContainers` to add remaining replicas according to each container replication config, then computes used space, capacity, remaining space, and cluster average utilization. `getUnBalancedNodes` compares generated utilization values with average +/- threshold and returns over-utilized nodes first, then under-utilized nodes.

State and persistence behavior: There is no persistence. All state is in maps keyed by `ContainerID` and `DatanodeUsageInfo`, an array of cluster nodes, generated replica sets, and calculated average utilization. Random replica placement avoids zero-utilization nodes.

Dependencies and integration points: The fixture integrates balancer tests with SCM container metadata, EC/RATIS required-node counts, replica byte accounting, and node capacity statistics. It is intended to feed mocked `ContainerManager`, `NodeManager`, and balancer logic.

Risks: It uses `ThreadLocalRandom`, so replica placement and resulting datanode container membership are nondeterministic. Capacity is derived from generated used bytes and target utilization, with zero-utilization nodes assigned random capacity. Container IDs are computed from loop indexes and may collide if the generation scheme changes.

Test signals: Consumers can assert expected average utilization, expected unbalanced nodes for a threshold, per-datanode container membership, per-container replication sets, and mixed RATIS/EC replication behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestableCluster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/package-info.java

Purpose: This package descriptor documents that the package contains unit tests for `org.apache.hadoop.hdds.scm.container.balancer.ContainerBalancer`.

Important APIs and types: It contains only Javadoc and the package declaration `org.apache.hadoop.hdds.scm.container.balancer`; the Javadoc links to the production `ContainerBalancer` class.

Control flow: There is no executable control flow.

State and persistence behavior: There is no runtime state or persistence.

Dependencies and integration points: The file is a Java package-info artifact used by Javadoc and Checkstyle/package documentation rules. It aligns the balancer test package with the production container balancer API.

Risks: The only practical risk is stale documentation if the package scope grows beyond `ContainerBalancer` tests or if the linked production class is renamed.

Test signals: Compilation and Checkstyle/package documentation validation are the only signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/package-info.java

Purpose: This package descriptor exists to satisfy package documentation / Checkstyle requirements for the SCM container test package.

Important APIs and types: It contains a short Javadoc comment and the package declaration `org.apache.hadoop.hdds.scm.container`.

Control flow: There is no executable logic.

State and persistence behavior: There is no state, mutation, or persistence.

Dependencies and integration points: It integrates only with Java compilation, Javadoc generation, and style checks for the test package that contains SCM container-level tests and helpers.

Risks: The comment is intentionally generic, so it does not explain package responsibilities. Functional risk is limited to package declaration drift if files are moved.

Test signals: Successful compilation and style checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestContainerPlacementFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestContainerPlacementFactory.java

Purpose: This test validates `ContainerPlacementPolicyFactory` policy construction and a basic rack-aware placement result. It ensures configured classes instantiate correctly, EC placement defaults to rack scatter, and invalid or incompatible policy classes fail.

Important APIs and types: It uses `ContainerPlacementPolicyFactory.getPolicy`, `getECPolicy`, `SCMContainerPlacementRackAware`, `SCMContainerPlacementRackScatter`, `PlacementPolicy`, `ContainerPlacementStatusDefault`, `SCMContainerPlacementMetrics`, `NodeManager`, `DatanodeInfo`, `NetworkTopologyImpl`, `NodeSchemaManager`, storage and metadata reports, and SCM config keys.

Control flow: The rack-aware test configures the placement implementation class, initializes a three-rack topology with 15 datanodes, injects storage reports with varied free space, mocks `NodeManager` lookups, obtains a policy from the factory, and asks for three datanodes. Other tests assert class identity for configured rack-aware and EC policies. Negative tests configure a dummy `PlacementPolicy` lacking the expected constructor or a nonexistent class and assert exceptions.

State and persistence behavior: There is no persistence. State is configuration, topology membership, datanode info storage reports, and metrics object creation.

Dependencies and integration points: The factory is the integration point between SCM configuration and placement algorithm implementations. The test also covers network topology and node manager metadata required by rack-aware placement.

Risks: Reflection-based constructor checks are brittle by design. The topology test relies on random choice satisfying rack placement rules and on singleton `NodeSchemaManager` initialization. It does not exhaustively test every policy constructor path.

Test signals: Signals include policy class identity, three selected datanodes, first two selected on the same rack and third on another rack, and expected exceptions for invalid implementation configuration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestContainerPlacementFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestContainerPlacementStatusDefault.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestContainerPlacementStatusDefault.java

Purpose: This compact suite locks down how `ContainerPlacementStatusDefault` reports policy satisfaction and misreplication counts for rack-placement results.

Important APIs and types: It constructs `ContainerPlacementStatusDefault` with actual placement count, expected placement count, total rack count, and in some cases per-rack occupancy inputs. It asserts `isPolicySatisfied` and `misReplicationCount`.

Control flow: `testPlacementSatisfiedCorrectly` covers cases where actual placement meets expected placement or where the cluster cannot provide enough racks, so the effective policy is satisfied. `testPlacementNotSatisfied` covers insufficient rack spread and occupancy constraints, including zero actual racks and cases where multiple additional rack placements are needed.

State and persistence behavior: There is no persistence. State is immutable placement-count data passed into the status object.

Dependencies and integration points: The status object is returned by placement policies and consumed by replication manager health checks, misreplication repair, and over/under placement diagnostics.

Risks: The tests encode exact misreplication arithmetic. If policy semantics change, especially for clusters with fewer racks than requested or per-rack replica constraints, these assertions must be updated intentionally.

Test signals: Exact boolean satisfaction results and exact `misReplicationCount` values, including satisfied single-rack cluster cases and unsatisfied multi-rack / per-rack occupancy cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestContainerPlacementStatusDefault.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestSCMContainerPlacementCapacity.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestSCMContainerPlacementCapacity.java

Purpose: This test checks that the capacity-biased placement policy excludes used nodes and nodes without sufficient free space, while favoring nodes with more available capacity over many selections.

Important APIs and types: It uses `SCMContainerPlacementCapacity`, `SCMContainerPlacementMetrics`, `NodeManager`, `DatanodeInfo`, `SCMNodeMetric`, storage and metadata reports, `OzoneConfiguration`, and `OZONE_DATANODE_RATIS_VOLUME_FREE_SPACE_MIN`.

Control flow: The test creates seven healthy datanodes with 100-byte capacity, modifies three storage reports to lower remaining space, mocks `NodeManager.getNodes`, `getNodeStat`, and `getNode`, constructs the capacity policy, and repeatedly requests one target while two existing nodes are excluded. It counts how often each selected datanode appears over 1000 iterations.

State and persistence behavior: There is no persistence. Runtime state is datanode storage report data, mocked node metrics, exclusion list, and selection count map.

Dependencies and integration points: The policy relies on SCM node metrics and storage-report-derived node details. It is used when SCM wants probability-weighted target selection by free capacity rather than pure random selection.

Risks: The final distribution assertions are probabilistic and may be sensitive to random selection implementation or sample size. The test uses tiny byte-scale capacities, which is efficient but can obscure real-world unit behavior. Metadata-space filtering is present through reports but not deeply varied.

Test signals: Every iteration returns exactly one node, excludes the two existing nodes, excludes the low-space node, and selects high-capacity nodes more often than nodes with less remaining space.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestSCMContainerPlacementCapacity.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestSCMContainerPlacementRackAware.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestSCMContainerPlacementRackAware.java

Purpose: This large suite verifies RATIS-style rack-aware placement, where two replicas may share a rack and additional replicas should spread across racks when possible. It covers fresh placement, used/excluded/favored nodes, fallback behavior, validation, out-of-service handling, and metrics.

Important APIs and types: It exercises `SCMContainerPlacementRackAware`, `SCMContainerPlacementMetrics`, `NetworkTopologyImpl`, `NodeSchemaManager`, `NodeManager`, `DatanodeInfo`, `NodeStatus`, storage and metadata reports, `ContainerPlacementStatus`, and SCM placement configuration.

Control flow: Setup parameterizes clusters from 3 to 15 datanodes, with five nodes per rack, healthy node statuses, topology membership, and varied low-space nodes. Tests request different replica counts and assert rack relationships. Other tests supply existing/used nodes, excluded nodes, favored nodes, single-node racks, default rack locations, and full-rack exclusion cases. Fallback tests compare policies that allow or prohibit fallback and assert metric counters.

State and persistence behavior: No data is persisted. State lives in topology, datanode info reports, node statuses, selected nodes, and metrics counters. Some tests mutate persisted operational state or `DatanodeInfo` status to simulate decommissioned/read-only nodes.

Dependencies and integration points: This policy feeds SCM container and pipeline placement for replicated containers. It integrates network topology with node health, free-space filtering, and replication manager placement validation.

Risks: Parameterized tests use assumptions for cluster shapes and contain random node selection, so assertions focus on relationships rather than exact identities. Singleton topology schema initialization is shared. Some out-of-service selection tests tolerate SCMException because retry logic may miss the only eligible node.

Test signals: Signals include selected counts, same-rack/different-rack relationships, exclusion and favored-node behavior, SCMException when fallback is prohibited or no valid target exists, metric request/success/attempt/fallback counts, validation misreplication counts, and ignoring out-of-service replicas when evaluating placement.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestSCMContainerPlacementRackAware.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestSCMContainerPlacementRackScatter.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestSCMContainerPlacementRackScatter.java

Purpose: This suite verifies the EC/pipeline rack-scatter placement policy, which tries to maximize rack diversity for selected nodes and existing replicas. It covers cluster shapes from small single-rack cases to 30 datanodes, failure modes, fallback behavior, validation, and repair-adjacent selection scenarios.

Important APIs and types: It uses `SCMContainerPlacementRackScatter`, `SCMContainerPlacementMetrics`, `NetworkTopologyImpl`, `NodeSchemaManager`, `NodeManager`, `DatanodeInfo`, `NodeStatus`, `ContainerPlacementStatus`, `SCMException` result codes, and `OZONE_SCM_PIPELINE_PLACEMENT_IMPL_KEY`.

Control flow: Setup builds configurable topologies with a fixed number of nodes per rack or one node per rack plus extras, mocks node manager lookups, and initializes a rack-scatter policy. Tests choose nodes with no exclusions, with used/excluded/favored nodes, with insufficient racks, with default rack locations, and with storage reports adjusted to remove candidates. Helper assertions combine used and chosen nodes and validate the resulting rack spread.

State and persistence behavior: There is no persistence. State is in topology membership, datanode status, storage reports, metric counters, used/excluded/favored lists, and pending selected-node lists. Tests mutate storage space and remove nodes from the topology to model unavailable nodes.

Dependencies and integration points: Rack scatter is central to EC placement and can also be configured for pipeline placement. It integrates rack-count calculation, available-node filtering, fallback semantics, and placement validation used by replication health.

Risks: Randomized selection means many assertions validate rack count and membership constraints rather than exact order. Some tests target known edge cases, such as choosing one node when two racks are ideally required, all nodes on a rack excluded, and insufficient available nodes; these are sensitive to algorithm changes.

Test signals: Exact selected counts, rack-size equality with `min(required, rack count)`, specific `SCMException` result codes, favored/excluded behavior, default-rack collapse to one rack, validation misreplication counts, and chosen nodes from expected racks under edge-case constraints.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestSCMContainerPlacementRackScatter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestSCMContainerPlacementRandom.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestSCMContainerPlacementRandom.java

Purpose: This test covers the baseline random placement policy: choosing valid nodes while excluding existing nodes, validating the minimal placement policy, and rejecting datanodes without enough data or metadata space.

Important APIs and types: It uses `SCMContainerPlacementRandom`, `SCMContainerPlacementMetrics`, `ContainerPlacementStatus`, `NodeManager`, `DatanodeInfo`, `NodeStatus`, storage and metadata reports, `OzoneConfiguration`, and the minimum RATIS volume free-space config.

Control flow: `chooseDatanodes` builds five healthy datanodes, marks one low on data space, excludes two existing nodes, and repeatedly asserts the chosen target is neither excluded nor low-space. `testPlacementPolicySatisified` verifies the random policy's relaxed one-rack placement semantics. `testIsValidNode` creates three datanodes and independently makes one data-space constrained and one metadata-space constrained, then calls `isValidNode`.

State and persistence behavior: There is no persistence. State is stored in mocked node manager responses, `DatanodeInfo` storage reports, exclusion lists, and policy validation results.

Dependencies and integration points: Random placement is the base/simple SCM placement behavior and shares free-space validation with other placement policies. Its validation result is consumed by replication and placement health logic.

Risks: The spelling of `testPlacementPolicySatisified` is cosmetic. The random chooser loop is probabilistic but only checks exclusion constraints, so it is robust against exact random order. The test uses small byte-sized thresholds.

Test signals: Chosen node count is one, excluded and low-space datanodes are never selected, empty placement is unsatisfied with one missing placement, single-node placement is satisfied for the random policy, and `isValidNode` distinguishes data-space and metadata-space shortages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestSCMContainerPlacementRandom.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/reconciliation/TestReconcileContainerEventHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/reconciliation/TestReconcileContainerEventHandler.java

Purpose: This suite verifies eligibility and command dispatch for `ReconcileContainerEventHandler`, which sends reconcile commands to datanodes hosting eligible container replicas.

Important APIs and types: It uses `ReconcileContainerEventHandler`, `ReconciliationEligibilityHandler`, `EligibilityResult`, `Result`, `ContainerManager`, `SCMContext`, `EventPublisher`, `DATANODE_COMMAND`, `CommandForDatanode<ReconcileContainerCommandProto>`, `SCMCommand`, `ContainerInfo`, `ContainerReplica`, RATIS and EC replication configs, and replica/container lifecycle states.

Control flow: Setup mocks a leader SCM context with a fixed term, a container manager, and an event publisher. Tests create containers and replica sets through helpers, call the static eligibility checker, then invoke `onMessage`. In accepted cases, the event handler fires one datanode command per replica; in rejected cases, no event is fired.

State and persistence behavior: There is no persistence. Runtime state includes mocked container metadata, replica sets, SCM leadership/term, and captured published commands. Command payload state includes container ID, command ID, term, target datanode, and peer list.

Dependencies and integration points: The handler integrates SCM event processing, leadership gating, container manager reads, reconciliation eligibility rules, and datanode command publication. It currently supports RATIS THREE-style reconciliation while rejecting EC and RATIS ONE scenarios.

Risks: Peer-selection behavior is noted as subject to change by a TODO. The tests use mocked manager state and do not validate actual datanode reconciliation execution. The parameterized lifecycle and replica-state tests encode which states are currently eligible.

Test signals: Signals include exact eligibility result codes, no command when SCM is not leader or container is ineligible/missing, three commands for eligible three-replica containers, command term equal to leader term, command ID equal to container ID, and peer lists that include all other replica hosts but exclude the target.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/reconciliation/TestReconcileContainerEventHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationTestUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationTestUtil.java

Purpose: `ReplicationTestUtil` is a shared test helper for SCM replication manager tests. It creates container metadata, replica sets, simple placement policies, and Mockito command-capture stubs for replication, reconstruction, delete, and generic datanode commands.

Important APIs and types: It exposes many static helpers around `ContainerReplica`, `ContainerInfo`, `ContainerID`, `ReplicationConfig`, `PlacementPolicy`, `SCMCommonPlacementPolicy`, `ContainerPlacementStatusDefault`, `ReplicateContainerCommand`, `DeleteContainerCommand`, `ReconstructECContainersCommand`, `SCMCommand`, `CommandTargetOverloadedException`, and `NotLeaderException`.

Control flow: Replica helpers build sets from replica indexes, operational states, replica states, origins, sequence IDs, key counts, and bytes used. Container helpers delegate to `TestContainerInfo.newBuilderForTest`. Placement helpers return anonymous `SCMCommonPlacementPolicy` implementations that either pick random nodes, return a specific node, or throw configured SCM exceptions. Mockito helpers install `doAnswer` callbacks that convert replication-manager method calls into command objects stored in a caller-provided set, optionally simulating one overload failure.

State and persistence behavior: There is no persistence. Helpers mutate `DatanodeDetails` persisted operational state when creating replicas and collect commands in caller-owned sets. Some helpers assert expected required replication space from configuration during policy calls.

Dependencies and integration points: This utility is widely used by replication manager, handler, and balancer tests to avoid repeated boilerplate and to make command-sending behavior observable without a running SCM or datanode.

Risks: Because it centralizes test construction, defaults such as sequence ID, key count, bytes used, `empty` flag, and origin handling can shape many tests. Some generated policies intentionally ignore real topology. Overloaded-command helpers only throw once by flipping an `AtomicBoolean`.

Test signals: Consumers observe constructed replica membership, op state/index/state fields, container metadata fields, expected SCMException result codes, and captured command objects with target datanodes and replica indexes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestContainerReplicaPendingOps.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestContainerReplicaPendingOps.java

Purpose: This suite validates `ContainerReplicaPendingOps`, the in-memory tracker for scheduled replica ADD and DELETE commands. It checks scheduling, de-duplication, completion, expiration, metrics, subscriber notifications, and target-datanode scheduled-size accounting.

Important APIs and types: It uses `ContainerReplicaPendingOps`, `ContainerReplicaOp`, `ContainerReplicaPendingOpsSubscriber`, `ReplicationManagerMetrics`, `ReplicationManagerConfiguration`, `TestClock`, `ContainerID`, `DatanodeDetails`, `DatanodeID`, `ReplicateContainerCommand`, `DeleteContainerCommand`, `ReplicationType`, and the nested `SizeAndTime` scheduled-size value.

Control flow: Setup creates a test clock, pending-op tracker, metrics, datanodes, and commands. Tests schedule ADD/DELETE operations for different containers, query pending lists and counts, complete operations by type/index/datanode, remove specific ops, advance the clock to expire entries, and register mock subscribers to verify callbacks. Size tests inspect the `containerSizeScheduled` map as ADD ops are scheduled, completed, and expired.

State and persistence behavior: There is no persistence. State includes per-container pending-op lists, per-type and per-replication-type counts, metrics counters, subscriber list, deadlines, and a concurrent map from target datanode ID to scheduled container size and last update time. Expired ADDs are removed, while expired deletes are retained but still counted for timeout metrics.

Dependencies and integration points: Replication manager uses this tracker to avoid duplicate scheduling, process command completions, notify `MoveManager` or other subscribers, expose metrics, and account for in-flight size when picking targets.

Risks: Expiration semantics are nuanced: deadlines equal to current time are not removed until older, ADD and DELETE retention differs, and duplicate ADD scheduling replaces deadlines without subscriber notification. Metrics distinguish RATIS index 0 from EC nonzero indexes.

Test signals: Exact pending counts, duplicate replacement behavior, completion boolean return values, timeout metrics, created/deleted metrics, subscriber `opCompleted` calls with timeout flags, no notification for non-expired/replaced ops, and scheduled-size map updates/removals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestContainerReplicaPendingOps.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestDatanodeCommandCountUpdatedHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestDatanodeCommandCountUpdatedHandler.java

Purpose: This focused test verifies that `DatanodeCommandCountUpdatedHandler` forwards datanode command-count update events to `ReplicationManager`.

Important APIs and types: It uses `DatanodeCommandCountUpdatedHandler`, `ReplicationManager`, `DatanodeDetails`, `MockDatanodeDetails`, and Mockito verification.

Control flow: Setup creates a mocked replication manager and handler. The test generates one datanode, invokes `handler.onMessage(datanode, null)`, and verifies that `replicationManager.datanodeCommandCountUpdated(datanode)` is called.

State and persistence behavior: There is no persistence and no meaningful internal state beyond the handler's reference to `ReplicationManager`.

Dependencies and integration points: The handler sits in the SCM event path where datanode command-count changes are reported and replication manager may use updated counts for throttling or scheduling decisions.

Risks: The test only verifies forwarding and does not cover null datanodes, publisher usage, event registration, or downstream replication-manager behavior.

Test signals: A single Mockito verification that the exact datanode object is passed to `datanodeCommandCountUpdated`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestDatanodeCommandCountUpdatedHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestECContainerReplicaCount.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestECContainerReplicaCount.java

Purpose: This suite validates `ECContainerReplicaCount`, the EC replication accounting object used to decide if an EC container is sufficiently replicated, over-replicated, missing, unrecoverable, or in need of maintenance/decommission replacement.

Important APIs and types: It uses `ECContainerReplicaCount`, `ECReplicationConfig(3,2)`, `ContainerReplica`, `ContainerReplicaOp`, `ContainerInfo`, replica indexes, `HddsProtos.NodeOperationalState` values, replica states such as `CLOSED` and `UNHEALTHY`, and helper methods from `ReplicationTestUtil`.

Control flow: Setup creates a closed EC container. Individual tests build replica sets with different index coverage, duplicate indexes, unhealthy replicas, maintenance states, decommissioning states, pending ADDs, and pending DELETEs. They instantiate `ECContainerReplicaCount` with a maintenance redundancy requirement, call methods such as `isSufficientlyReplicated`, `isOverReplicated`, `unavailableIndexes`, `overReplicatedIndexes`, `maintenanceOnlyIndexes`, `decommissioningOnlyIndexes`, `isMissing`, `isUnrecoverable`, and `isSufficientlyReplicatedForOffline`, then assert exact results.

State and persistence behavior: There is no persistence. State is derived from replica sets, pending op lists, EC data/parity indexes, operational state, replica health, and configured maintenance redundancy. Pending ops can also be added after construction with `addPendingOp`.

Dependencies and integration points: Replication manager uses this accounting to choose reconstruction, replication, deletion, maintenance, and decommission actions for EC containers. It directly affects safety decisions about whether an offline/decommissioning replica can be tolerated.

Risks: EC accounting is index-sensitive and has subtle interactions between pending deletes, pending adds, unhealthy replicas, maintenance-only copies, and decommissioned replicas. Some tests rely on duplicate replicas created with random datanodes, while equality/set behavior must preserve distinct hosts.

Test signals: Exact unavailable and over-replicated index lists, sufficient/insufficient replication with and without pending ops, maintenance copy counts capped by parity, missing vs unrecoverable distinction, decommissioning-only indexes, offline-safety checks, and pending-delete handling for unhealthy versus healthy indexes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestECContainerReplicaCount.java -->
