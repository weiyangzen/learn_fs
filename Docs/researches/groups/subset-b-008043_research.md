# Research: subset-b-008043

Grouped research for SCM container replication tests in Apache Ozone. Each section is source-tree-aligned and wrapped for reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestECMisReplicationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestECMisReplicationHandler.java

Purpose: Tests `ECMisReplicationHandler`, the erasure-coded specialization of mis-replication repair, by extending the shared `TestMisReplicationHandler` harness with an `ECReplicationConfig(3, 2)`. The class verifies that placement-policy violations for EC containers produce bounded replicate commands for the copied indexes, and that the handler avoids repair when the container is actually under-replicated, over-replicated, already placement-satisfied, or covered by pending operations.

Important APIs and types: The test uses `ECMisReplicationHandler`, `MisReplicationHandler`, `ECReplicationConfig`, `ContainerReplica`, `ContainerReplicaOp`, `PlacementPolicy`, `ContainerPlacementStatus`, `SCMException`, `InsufficientDatanodesException`, and `ReplicationManagerMetrics`. It relies heavily on `ReplicationTestUtil.createReplicas`, `MockDatanodeDetails`, and Mockito stubs for `chooseDatanodes`, `validateContainerPlacement`, and throttled replication dispatch. The EC-specific assertion keeps the replica index from the copied source and checks it on `ReplicateContainerCommand`.

Control flow: `setup` delegates to the abstract base harness, which prepares a closed EC container, mocked `ReplicationManager`, network topology schema, command capture set, and metrics. Parameterized cases vary the reported mis-replication count, then the base helper asks the placement policy which replicas to copy and how many targets to choose. The file covers all-in-service sources, maintenance sources excluded from eligible copies, no-node placement failures, pending add/delete suppression, throttled source failures, and partial target selection.

State and persistence behavior: No production persistence is exercised. State is in-memory test state: container metadata, replica sets with op-state and EC index, pending ops, command-capture pairs, and metrics counters. The tests confirm command side effects rather than persisted database updates.

Dependencies and integration points: Integrates with the abstract mis-replication harness, `ReplicationManager.sendThrottledReplicationCommand`, placement policy target selection, and metrics for EC partial replication caused by mis-replication.

Risks and test signals: Main risks are copying from invalid source states, losing EC replica indexes, issuing repair while pending ops already satisfy placement, and partial commands when placement returns fewer targets than requested. Strong signals include exact command counts, exception assertions, target/source membership checks, and metric verification for partial EC mis-replication.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestECMisReplicationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestECOverReplicationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestECOverReplicationHandler.java

Purpose: Tests `ECOverReplicationHandler`, which removes excess erasure-coded container replicas by replica index. The scenarios prove the handler deletes only redundant EC indexes, ignores replicas that should not count toward actionable excess, and can process over-replicated indexes even when the health object is an under-replicated result.

Important APIs and types: Uses `ECOverReplicationHandler`, `ContainerHealthResult.OverReplicatedHealthResult`, `UnderReplicatedHealthResult`, `DeleteContainerCommand`, `ContainerReplicaOp.PendingOpType.DELETE`, `NodeStatus`, `PlacementPolicy.replicasToRemoveToFixOverreplication`, and `ReplicationManager.sendThrottledDeleteCommand`. `MockNodeManager`, `NodeSchemaManager`, and `ReplicationTestUtil.mockRMSendThrottledDeleteCommand` supply topology and command capture.

Control flow: `setup` builds a closed `rs-3-2` container, a mocked replication manager that can mark one node stale, a simple placement policy, and a command set. Tests first prove no deletion when indexes 1-5 are present exactly once, when overage is fixed by pending delete, or when extra replicas are decommissioning, stale, or open. Other tests create duplicate index groups and assert delete counts per index. A defensive policy test returns a replica with the wrong index and expects no unsafe delete. Delete throttling injects an overloaded exception on the first send while confirming later eligible work can still be captured.

State and persistence behavior: The handler is observed through in-memory command generation. Replica index distribution is the key state; `staleNode` changes mocked node status, pending ops reduce actionable overage, and the command set records generated `DeleteContainerCommand`s with nonzero EC replica indexes.

Dependencies and integration points: Covers interaction with node health, placement policy, pending op accounting, replication manager delete throttling, and EC index semantics. It also exercises the integration path where an under-replicated health result is sent to the over-replication handler to resolve excess duplicate indexes.

Risks and test signals: Risks include deleting stale/open/decommissioning replicas incorrectly, deleting the wrong EC index, failing to honor pending deletes, and losing retry behavior on throttling. Signals are exact command counts, per-index delete accounting, nonzero replica-index assertions, and exception-path checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestECOverReplicationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestECUnderReplicationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestECUnderReplicationHandler.java

Purpose: Tests `ECUnderReplicationHandler`, the staged repair engine for under-replicated erasure-coded containers. It covers missing-index reconstruction, decommission and maintenance copy-out, partial repair behavior, overloaded command handling, fallback to over-replication repair, and cleanup of unhealthy replicas that block target selection.

Important APIs and types: The file uses `ECUnderReplicationHandler`, `ECReplicationConfig`, `UnderReplicatedHealthResult`, `ReconstructECContainersCommand`, `ReplicateContainerCommand`, `DeleteContainerCommand`, `ContainerReplica`, `ContainerReplicaOp`, `PlacementPolicy`, `ContainerPlacementStatusDefault`, `ReplicationManagerMetrics`, `SCMException`, and `InsufficientDatanodesException`. `PlacementPolicySpy` records used and excluded node lists for target selection.

Control flow: Setup constructs a closed `rs-3-2` container, mocked `ReplicationManager`, metrics, node-status behavior, simple placement policy, and command capture. The first parameterized tests distinguish critical and non-critical partial reconstruction across `rs-3-2`, `rs-6-3`, and `rs-10-4`: non-critical partials are deferred/skipped, while critical partials send reconstruction commands. Core tests then validate reconstruction for missing parity/data indexes, replication of decommissioning indexes, maintenance thresholds, mixed missing/decommission/maintenance stages, invalid placement tolerance, and no-node failures. Later tests cover fallbacks: if no target exists and no command was created, the handler calls `processOverReplicatedContainer` when the container is also over-replicated, or tries deleting one unhealthy replica to free a target. Other cases assert partial replication metrics, overloaded reconstruction continuing to later stages, not requesting zero maintenance targets, excluding pending-add datanodes, and copying decommissioning or maintenance replicas when unrecoverable.

State and persistence behavior: No persistent store is mutated. State is represented by replica index sets, operational states, pending ops, remaining maintenance redundancy, excluded nodes from replication manager, and captured SCM commands. Metrics counters are observable state for skipped, critical, and partial repair paths.

Dependencies and integration points: Integrates with placement selection, replication-manager excluded nodes, throttled reconstruction/replication/delete dispatch, EC command encoding of missing indexes, node health/op-state, and over-replication processing. It is a broad regression suite for HDDS issues around maintenance/decommission and target selection.

Risks and test signals: High-risk areas are partial reconstruction safety, command loss when later stages fail, wrong used/excluded lists, copying from out-of-service sources, deleting the wrong unhealthy replica, and retry semantics after overload. Signals include exact command types/counts, encoded missing-index assertions, metrics checks, Mockito verification of over-rep fallback, and explicit exception assertions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestECUnderReplicationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestMisReplicationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestMisReplicationHandler.java

Purpose: Abstract test harness for concrete Ratis and EC mis-replication handler tests. It centralizes setup, placement-policy stubbing, command capture, and shared assertions for `MisReplicationHandler.processAndSendCommands`.

Important APIs and types: Uses `MisReplicationHandler`, `ReplicationManager`, `ReplicationManagerMetrics`, `ReplicationConfig`, `ContainerInfo`, `ContainerReplica`, `ContainerReplicaOp`, `PlacementPolicy`, `ContainerPlacementStatus`, `ReplicateContainerCommand`, `SCMCommand`, `NodeStatus`, and `NodeSchemaManager`. Subclasses provide `getMisreplicationHandler` and `assertReplicaIndex`.

Control flow: `setup` creates a closed container from the supplied replication config, initializes topology schemas, mocks replication-manager config/metrics/node status/pending ops, and records commands from normal and throttled replication sends. `mockPlacementPolicy` returns an unsatisfied placement status. `testMisReplication` constructs a mocked `MisReplicatedHealthResult`, computes healthy in-service source replicas, asks the placement policy for replicas to copy, stubs `chooseDatanodes` to return expected targets, invokes the handler, and finally checks command count and command content in a `finally` block so exception paths still validate side effects.

State and persistence behavior: The harness is in-memory. Important state is the selected source set, remaining datanodes after copied replicas are removed, target datanodes, replica-index map, throttling boolean, captured commands, and metrics object. It does not persist container state or update SCM metadata.

Dependencies and integration points: Provides the integration layer between concrete handler implementations and common replication manager APIs. It also models placement-policy collaboration by asserting the used-node list passed to `chooseDatanodes` contains remaining replicas after selected sources are copied.

Risks and test signals: Risks include regressions hidden by duplicated subclass tests, incorrect source eligibility, wrong target selection inputs, and lost command assertions after exceptions. The harness gives strong shared signals: replicate command type, container ID, source membership, target membership, command count, and subclass-specific replica-index behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestMisReplicationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestOverReplicatedProcessor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestOverReplicatedProcessor.java

Purpose: Tests `OverReplicatedProcessor`, the queue processor that drains over-replicated health results and delegates actual repair to `ReplicationManager.processOverReplicatedContainer`.

Important APIs and types: Uses `OverReplicatedProcessor`, `ReplicationQueue`, `ReplicationManager`, `ReplicationManagerConfiguration`, `OverReplicatedHealthResult`, `ECReplicationConfig`, and `ContainerInfo`.

Control flow: Setup creates a real `ReplicationQueue`, mocked replication manager, `OverReplicatedProcessor`, and EC container config. It forces `shouldRun()` true and deliberately configures in-flight replication count higher than the limit to show that over-replication processing is not blocked by add/replication limits because over-rep handlers delete. `testSuccessfulRun` enqueues one over-replicated result, mocks successful processing, runs `processAll`, and expects the queue to empty. `testMessageReQueuedOnException` makes processing throw, then asserts the same health result remains queued and is not replaced.

State and persistence behavior: State is entirely queue-local. The queue size and dequeued object identity are the observable persistence-like behavior. No SCM metadata or durable state is modified.

Dependencies and integration points: Integrates queue scheduling with `ReplicationManager.shouldRun`, configured over-replicated interval supplier, and the `processOverReplicatedContainer` handoff. It intentionally checks that replication in-flight limits do not suppress delete-only work.

Risks and test signals: Risks include losing queued work on handler exceptions, over-rep processing being starved by replication limits, and repeated processing after one failure. Signals are queue size, object identity after requeue, and successful emptying on normal completion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestOverReplicatedProcessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestQuasiClosedStuckOverReplicationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestQuasiClosedStuckOverReplicationHandler.java

Purpose: Tests `QuasiClosedStuckOverReplicationHandler`, which deletes excess replicas for quasi-closed stuck Ratis containers while preserving required copies per origin. The key model is origin-aware: best origin by highest BCSID has a different target copy count from other origins.

Important APIs and types: Uses `QuasiClosedStuckOverReplicationHandler`, `RatisReplicationConfig`, `ContainerInfo`, `ContainerReplica`, `DatanodeID`, `ContainerReplicaOp`, `DeleteContainerCommand` via `SCMCommand`, `ReplicationManagerMetrics`, and throttled delete dispatch.

Control flow: Setup creates a quasi-closed Ratis container, a push-replication config, mocked healthy node status, metrics, and captured throttled delete commands. Tests assert no commands when origin groups are at target, and no action when pending delete ops exist. Over-replicated scenarios create origin1 with higher BCSID and too many copies, plus origin2 at target, expecting one delete. A throttling test creates two over-replicated origins, injects an overloaded delete on the first attempt, confirms the handler continues to process the second origin, and rethrows. A final case ensures no delete when the best origin and other origin are exactly at configured targets.

State and persistence behavior: State is in-memory origin/BCSID distribution and command capture. The handler does not persist metadata; behavior is visible through returned command counts and the command set.

Dependencies and integration points: Depends on `QuasiClosedStuckReplicaCount` semantics, replication-manager config for quasi-closed stuck copy targets, node status, and throttled delete command delivery.

Risks and test signals: Risks include deleting a required origin copy, ignoring pending deletes, failing to continue after one target overload, or not rethrowing to allow retry. Signals are returned counts, command type checks, command-set size, and `CommandTargetOverloadedException` assertions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestQuasiClosedStuckOverReplicationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestQuasiClosedStuckReplicaCount.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestQuasiClosedStuckReplicaCount.java

Purpose: Tests `QuasiClosedStuckReplicaCount`, the origin-aware counting model behind quasi-closed stuck replication. It determines whether each origin group is under- or over-replicated using best-origin and other-origin copy targets, with special handling for out-of-service and maintenance replicas.

Important APIs and types: Uses `QuasiClosedStuckReplicaCount`, nested `MisReplicatedOrigin`, `ContainerReplica`, `ContainerID`, `DatanodeID`, node op states, and `QUASI_CLOSED` replica state. `ReplicationTestUtil` creates origin-specific replicas and BCSID variants.

Control flow: The tests build replica sets grouped by origin with different sequence IDs. Correct-replication cases prove best origin target 3 and other-origin target 2 are sufficient for one, two, or three origins. Under-replication cases validate deltas for one or multiple deficient origins. Over-replication cases validate excess deltas for best and other origins. Decommissioning and maintenance cases show out-of-service copies reduce effective availability for under-replication but should not create false over-replication. The shift test introduces a new origin with a higher BCSID and proves the previous best origin can become over-replicated while the new best becomes under-replicated.

State and persistence behavior: Pure in-memory counting. Inputs are replica sets with origin IDs, op states, and sequence IDs; outputs are booleans and `MisReplicatedOrigin` collections with sources and deltas. No external state is read or written.

Dependencies and integration points: This is the core state model consumed by quasi-closed stuck under/over handlers. Its output determines how many replicate or delete commands handlers send per origin.

Risks and test signals: Risks are off-by-one copy targets, treating decommissioned or maintenance replicas as excess, selecting the wrong best origin after higher BCSID appears, and losing source-origin identity. Signals are explicit `isUnderReplicated`, `isOverReplicated`, source counts, replica deltas, and origin-ID assertions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestQuasiClosedStuckReplicaCount.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestQuasiClosedStuckUnderReplicationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestQuasiClosedStuckUnderReplicationHandler.java

Purpose: Tests `QuasiClosedStuckUnderReplicationHandler`, which copies under-replicated quasi-closed stuck origin groups until best and other origins meet configured copy targets.

Important APIs and types: Uses `QuasiClosedStuckUnderReplicationHandler`, `RatisReplicationConfig`, `PlacementPolicy`, `ContainerHealthResult.UnderReplicatedHealthResult`, `ContainerReplica`, `ContainerReplicaOp`, `DatanodeID`, `ReplicationManagerConfiguration`, `InsufficientDatanodesException`, and `SCMException`.

Control flow: Setup creates a quasi-closed Ratis container, simple placement policy, push-replication config, metrics, pending-op mock, healthy node status, and command captures for throttled replication/delete. Tests assert no action when not under-replicated and no action when pending add ops exist. A one-copy origin schedules two copies to reach the best-origin target. Overload handling creates two deficient origins, injects an overloaded source, verifies another command can still be sent, and expects the overload exception to be rethrown. No-node and insufficient-node policies produce `SCMException` and `InsufficientDatanodesException` respectively, with partial command counts. The origin-copies test overrides config to best=3 and other=2 and verifies only the deficient best origin is copied.

State and persistence behavior: State is in-memory: origin/BCSID replica sets, pending ops, configurable copy targets, and captured commands. There is no durable write; command count is the behavioral side effect.

Dependencies and integration points: Depends on placement policy target choice, replication-manager push replication dispatch, metrics/config, pending-op accounting, and `QuasiClosedStuckReplicaCount` output.

Risks and test signals: Risks include scheduling duplicate work while pending ops exist, losing partial progress on insufficient nodes, swallowing overloaded exceptions, and ignoring configured copy targets. Signals are command counts, exception types, and config-specific expected counts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestQuasiClosedStuckUnderReplicationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestRatisContainerReplicaCount.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestRatisContainerReplicaCount.java

Purpose: Tests `RatisContainerReplicaCount`, the health/counting model for Ratis containers. It evaluates sufficient replication, over-replication, unrecoverability, pending add/delete effects, decommission/maintenance treatment, unhealthy/mismatched replica accounting, remaining redundancy, and quasi-closed sequence correctness.

Important APIs and types: Uses `RatisContainerReplicaCount`, `RatisReplicationConfig`, `ContainerInfo`, `ContainerReplica`, `ContainerReplicaOp`, `ContainerID`, node op states, replica states (`CLOSED`, `CLOSING`, `OPEN`, `QUASI_CLOSED`, `UNHEALTHY`), and helper factories from `ReplicationTestUtil`.

Control flow: The tests progress from basic healthy replica counts for replication factor three and one, through pending add/delete combinations, over-replication, and then decommission and maintenance cases. The helper `validate` checks `isSufficientlyReplicated`, `additionalReplicaNeeded`, `isOverReplicated`, and `insufficientDueToOutOfService`. Later tests inspect detailed counters for healthy, matching, mismatched, unhealthy, decommission counts; compare behavior with `considerUnhealthy` true/false; verify safe over-replication requirements; check remaining redundancy; compare sufficient replication with and without pending ops; and validate quasi-closed replicas by sequence ID.

State and persistence behavior: Pure value-object tests. The state is the constructed set of replicas, pending ops, replication factor, min healthy for maintenance, and `considerUnhealthy` mode. No persistence or external manager is involved.

Dependencies and integration points: This counting class feeds Ratis health results and repair handlers, so these tests anchor decisions for under-replication, over-replication, maintenance safety, and whether unhealthy replicas should be counted as excess or unavailable.

Risks and test signals: Risks include counting pending ops too optimistically, mistaking maintenance/decommission replicas for healthy capacity, treating mismatched states as matching, over-deleting when only unhealthy/mismatched replicas are excess, and accepting quasi-closed replicas with stale sequence IDs. Signals are direct assertions on health booleans, deltas, counts, redundancy, and sequence-ID handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestRatisContainerReplicaCount.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestRatisMisReplicationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestRatisMisReplicationHandler.java

Purpose: Tests `RatisMisReplicationHandler`, the Ratis specialization of the shared mis-replication repair flow. It verifies placement repair by copying from eligible replicas without EC replica indexes.

Important APIs and types: Uses `RatisMisReplicationHandler`, shared `TestMisReplicationHandler`, `RatisReplicationConfig`, `PlacementPolicy`, `ContainerPlacementStatus`, `ContainerReplicaOp`, `SCMException`, `CommandTargetOverloadedException`, and Ratis replica states including `QUASI_CLOSED`.

Control flow: Setup configures a closed Ratis container with factor three through the abstract harness. Parameterized tests vary mis-replication count for all in-service closed replicas and quasi-closed replicas, expecting at most three targets. Other tests cover placement no-node exceptions, maintenance replicas excluded from sources, no repair when under- or over-replicated, no repair when placement is already satisfied, no repair with pending add/delete, and overload propagation when all sources are throttled.

State and persistence behavior: State is the base harness in-memory container, replica set, pending ops, placement mocks, command capture, and metrics. The Ratis-specific assertion requires every `ReplicateContainerCommand` to have replica index zero.

Dependencies and integration points: Integrates with placement policy, replication-manager throttled replication command path, node op-state filtering, and common mis-replication command assertions inherited from the base class.

Risks and test signals: Risks are issuing Ratis commands with EC-style indexes, copying maintenance replicas, repairing containers that are not purely mis-replicated, and swallowing throttling. Signals are command counts, exception assertions, source/target membership, and replica-index-zero checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestRatisMisReplicationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestRatisOverReplicationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestRatisOverReplicationHandler.java

Purpose: Tests `RatisOverReplicationHandler`, which chooses safe replicas to delete from over-replicated Ratis containers while respecting placement, replica state, origin preservation, pending deletes, and throttling.

Important APIs and types: Uses `RatisOverReplicationHandler`, `RatisReplicationConfig`, `ContainerHealthResult.OverReplicatedHealthResult`, `PlacementPolicy`, `ContainerPlacementStatusDefault`, `ContainerReplica`, `ContainerReplicaOp`, `DeleteContainerCommand`, `NodeStatus`, and command throttling.

Control flow: Setup creates a closed Ratis container, placement policy mock, healthy node-status mock, and delete command capture. Tests cover closed over-replication with pending delete, stale node exclusion, quasi-closed containers with same vs different origins, all-unhealthy and excess-unhealthy handling, placement-aware deletion that avoids making placement worse, deletion when already mis-replicated but not worsened, staged deletion stopping before second removal breaks placement, all-unhealthy deterministic selection by BCSID/hash, deleting mismatched quasi-closed replicas from closed containers, avoiding decommissioning/maintenance replicas as delete candidates, perfect replication, wrong-sequence quasi-closed behavior, and throttling.

State and persistence behavior: In-memory replica sets encode state, op-state, origin, and sequence ID. Pending delete ops reduce excess. Placement validation controls whether deletion is safe. Commands are captured rather than persisted.

Dependencies and integration points: Integrates with placement-policy validation, node status, `ReplicationManager.sendThrottledDeleteCommand`, Ratis container state semantics, and command retry behavior after `CommandTargetOverloadedException`.

Risks and test signals: Risks include deleting unique-origin quasi-closed replicas, worsening placement, deleting decommission/maintenance replicas prematurely, selecting high-BCSID unhealthy replicas before lower-BCSID ones, or continuing too far after throttling. Signals are exact command counts, target datanode assertions, placement mock behavior, exception assertions, and command type/index checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestRatisOverReplicationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestRatisUnderReplicationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestRatisUnderReplicationHandler.java

Purpose: Tests `RatisUnderReplicationHandler`, which chooses replication sources and targets for under-replicated Ratis containers, including unhealthy, decommissioning, maintenance, quasi-closed, and vulnerable replica cases.

Important APIs and types: Uses `RatisUnderReplicationHandler`, `RatisReplicationConfig`, `UnderReplicatedHealthResult`, `PlacementPolicy`, `ContainerReplica`, `ContainerReplicaOp`, `SCMCommand`, `NodeStatus`, `ReplicationManagerMetrics`, `InsufficientDatanodesException`, and throttled replication/delete dispatch.

Control flow: Setup creates a closed Ratis container, simple placement policy, push-replication config, metrics, pending-op mock, healthy node-status behavior, and command capture. Early tests check pending adds, unrecoverable empty containers, decommission/maintenance under-replication, and maintenance minimums. Placement failure tests distinguish no targets, insufficient targets with partial replication metrics, and no-node fallbacks that may delete a removable unhealthy replica only when enough healthy replicas remain and no pending delete exists. Source-selection tests prefer healthy closed replicas, use unhealthy only when no healthy source exists, avoid wrong-sequence quasi-closed replicas when better sources exist, choose highest BCSID, and verify used/excluded target lists. Vulnerable quasi-closed tests replicate unique unhealthy replicas on decommissioning or entering-maintenance nodes and continue across overloaded sources while rethrowing. Final tests define when quasi-closed replicas can be sources for closed and quasi-closed containers.

State and persistence behavior: No durable writes. State is replica/op-state/sequence sets, pending ops, min healthy for maintenance, command captures, and metrics counters. Delete fallback emits forced delete commands for selected unhealthy replicas.

Dependencies and integration points: Integrates with placement policy, replication manager metrics, pending-op accounting, node health/op-state, throttled push replication, delete fallback, and health-result flags such as `hasVulnerableUnhealthy`.

Risks and test signals: Risks include selecting stale or wrong-sequence sources, ignoring pending add/delete exclusions, deleting unhealthy replicas when unsafe, failing to preserve vulnerable unique unhealthy replicas, and losing partial progress after overload. Signals include command counts, command target/source identity, metrics, captured placement arguments, exception assertions, and source equality checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestRatisUnderReplicationHandler.java -->
