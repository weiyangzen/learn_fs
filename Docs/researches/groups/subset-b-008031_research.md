# Research: subset-b-008031

Grouped research for the source-tree-aligned Apache Ozone SCM container, placement, balancer, reconciliation, and replication files in subset B. Each file section preserves the source path and is bounded for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerTaskIterationStatusInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerTaskIterationStatusInfo.java

Purpose: immutable status aggregate for one Container Balancer iteration, combining `IterationInfo`, `ContainerMoveInfo`, and `DataMoveInfo` into a public read model and protobuf export.

Important APIs: constructor, getters for iteration number/result/duration, scheduled and moved bytes, move counts, timeout counts, and entering/leaving node maps. `toProto()` builds `ContainerBalancerTaskIterationStatusInfoProto`; `mapToProtoNodeTransferInfo()` converts `Map<DatanodeID, Long>` into protobuf node transfer records using `DatanodeID.toString()` as UUID text.

Control flow and state: no persistence and no mutation after construction, but it exposes the underlying maps returned by `DataMoveInfo`. `toProto()` substitutes an empty string for a null iteration result, but assumes iteration duration and maps are non-null.

Dependencies and integration: consumed by balancer status APIs and tests in `TestContainerBalancerStatusInfo`; serialized through `StorageContainerLocationProtocolProtos` for SCM client responses.

Risks: null maps or duration can fail protobuf conversion; node UUID formatting depends on `DatanodeID.toString()`. Test signals should cover proto conversion, empty/null result text, and map ordering independence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerTaskIterationStatusInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerMoveInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerMoveInfo.java

Purpose: value object containing latest-iteration container move counters for scheduled, completed, failed, and timed-out moves.

Important APIs: direct long constructor; metrics constructor reading `ContainerBalancerMetrics` latest-iteration counters; four getters. No setters, persistence, or background behavior.

Control flow and state: construction snapshots counter values. The direct constructor is useful for tests and synthetic reports; the metrics constructor integrates with live balancer metrics.

Dependencies and integration: used by `ContainerBalancerTaskIterationStatusInfo` and balancer status reporting. Tests in `TestContainerBalancerStatusInfo` indirectly validate fields as part of current and historical iteration status.

Risks: no validation prevents negative counters if supplied by a bad caller; metrics constructor assumes metrics object is non-null and already initialized. Test signals should check both constructors and consistency with `ContainerBalancerMetrics` reset/iteration boundaries.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerMoveInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerMoveSelection.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerMoveSelection.java

Purpose: mutable pair describing a selected container and its target datanode for a balancer move.

Important APIs: constructor, getters/setters for `DatanodeDetails targetNode` and `ContainerID containerID`, plus `equals`/`hashCode`.

Control flow and state: a simple DTO with mutable fields and no synchronization. It does not persist anything and is expected to be short lived during target selection.

Dependencies and integration: returned by `FindTargetStrategy.findTargetForContainerMove()` implementations and consumed by the container balancer task before invoking `MoveManager`.

Risks: `equals()` compares `targetNode` and `containerID` using reference identity (`!=` and `==`) while `hashCode()` uses `Objects.hash`, which delegates to value equality. This can violate the equals/hashCode contract if logically equal but non-identical objects are used. Mutability also makes it unsafe as a map key after mutation. Test signals should include equality contract tests if this object is ever stored in sets or maps.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerMoveSelection.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/DataMoveInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/DataMoveInfo.java

Purpose: value object for balancer data movement volume: scheduled bytes, actually moved bytes, bytes entering target nodes, and bytes leaving source nodes.

Important APIs: constructor and getters for `sizeScheduledForMove`, `dataSizeMoved`, `sizeEnteringNodes`, and `sizeLeavingNodes`.

Control flow and state: construction records references, not defensive copies. The object is otherwise immutable by field assignment but map contents may still be externally mutable.

Dependencies and integration: built from source and target strategy accounting maps, then included in `ContainerBalancerTaskIterationStatusInfo` and converted to protobuf status.

Risks: exposed mutable maps can drift after status construction if callers reuse strategy maps; no validation for negative byte totals. Tests should verify status snapshots do not accidentally change across balancer iteration reset, or callers should pass copies before construction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/DataMoveInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/FindSourceGreedy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/FindSourceGreedy.java

Purpose: greedy source selection strategy for container balancing. It prefers datanodes with the highest projected utilization after already scheduled outgoing bytes are subtracted.

Important APIs: `reInitialize`, `resetPotentialSources`, `getNextCandidateSourceDataNode`, `increaseSizeLeaving`, `canSizeLeaveSource`, `removeCandidateSourceDataNode`, `addBackSourceDataNode`, and map access/clear methods.

Control flow and state: maintains `sizeLeavingNode` in a `ConcurrentHashMap` and `potentialSources` in a priority queue ordered by projected utilization and datanode ID. `increaseSizeLeaving()` updates outgoing bytes and re-adds the source to the queue, but does not remove an existing queue entry first; callers must manage duplicates via strategy contract or balancer flow.

Dependencies and integration: depends on `NodeManager.getUsageInfo`, `DatanodeUsageInfo.calculateUtilization`, and `ContainerBalancerConfiguration` max outgoing bytes. Used by the balancer task to select overloaded sources and update iteration data.

Risks: `PriorityQueue` is not thread-safe; duplicate entries can skew source selection; missing map entries cause warnings and false decisions. Tests exist around balancer behavior, but direct tests should cover lower-limit enforcement, zero/negative sizes, max outgoing bytes, and requeue ordering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/FindSourceGreedy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/FindSourceStrategy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/FindSourceStrategy.java

Purpose: strategy interface for choosing source datanodes and tracking outgoing data during a balancing iteration.

Important APIs: candidate polling/removal/re-addition, `increaseSizeLeaving`, `canSizeLeaveSource`, `reInitialize`, `resetPotentialSources`, and outgoing-size map access/clear.

Control flow and state: the interface defines mutable iteration state but leaves storage and ordering to implementations. The comments warn that `addBackSourceDataNode` does not check duplicates and callers own removal when needed.

Dependencies and integration: integrates `DatanodeDetails`, `DatanodeUsageInfo`, and `ContainerBalancerConfiguration`; implemented by `FindSourceGreedy` and called from Container Balancer selection loops.

Risks: Javadoc for `canSizeLeaveSource` still says target in places, which can mislead maintainers. Implementations should be tested through both direct strategy tests and balancer task tests for size accounting and queue exhaustion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/FindSourceStrategy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/FindTargetGreedyByNetworkTopology.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/FindTargetGreedyByNetworkTopology.java

Purpose: target selection strategy that sorts target candidates by network topology distance from the selected source, then by usage.

Important APIs: constructor wiring `ContainerManager`, `PlacementPolicyValidateProxy`, `NodeManager`, and `NetworkTopology`; `sortTargetForSource`; `resetPotentialTargets`.

Control flow and state: stores potential targets in a raw `LinkedList` passed to `AbstractFindTargetGreedy`. Sorting computes `networkTopology.getDistanceCost(source, target)` and uses inherited `compareByUsage` as tie breaker. Reset transforms datanode details into current `DatanodeUsageInfo` snapshots from `NodeManager`.

Dependencies and integration: depends on topology map, target placement validation, and inherited target selection logic. Tested by `TestFindTargetStrategy` for nearest-target ordering.

Risks: raw `List` loses generic compile-time safety; `networkTopology` must be non-null. Distance subtraction can theoretically overflow if distance costs grow, though current costs are small. Test signals should cover equal-distance usage tiebreaks, null topology rejection, and placement-policy filtering through the superclass.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/FindTargetGreedyByNetworkTopology.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/FindTargetGreedyByUsageInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/FindTargetGreedyByUsageInfo.java

Purpose: greedy target strategy that prioritizes lowest projected datanode usage without considering topology distance.

Important APIs: constructor, no-op `sortTargetForSource`, and `resetPotentialTargets`.

Control flow and state: delegates most behavior to `AbstractFindTargetGreedy`, using a `TreeSet` ordered by inherited `compareByUsage`. Reset reconstructs usage info from `NodeManager` for a fresh iteration view.

Dependencies and integration: relies on `ContainerManager`, `PlacementPolicyValidateProxy`, `NodeManager`, and inherited size-entering accounting. Tests in `TestFindTargetStrategy` validate usage ordering and target selection behavior.

Risks: because `TreeSet` comparator equality collapses entries, two datanodes with comparator-equal usage and no stable identity tiebreak in the comparator may cause one to be dropped depending on `compareByUsage`. Test signals should cover equal utilization, equal raw usage, and size-entering updates that change ordering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/FindTargetGreedyByUsageInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/FindTargetStrategy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/FindTargetStrategy.java

Purpose: target strategy interface for choosing where a specific container from a source should move and for tracking incoming bytes.

Important APIs: `findTargetForContainerMove`, `increaseSizeEntering`, `reInitialize`, `resetPotentialTargets`, `getSizeEnteringNodes`, and `clearSizeEnteringNodes`.

Control flow and state: implementations own candidate ordering, placement validation, and size-limit enforcement. The interface exposes incoming-size state for iteration status reporting.

Dependencies and integration: used by Container Balancer task with `ContainerID`, `DatanodeDetails`, `DatanodeUsageInfo`, and `ContainerBalancerConfiguration`; implemented by network-topology and usage-info greedy variants.

Risks: Javadoc mentions a functional interface that is not present in the method signature, likely stale from an older API. Tests should validate both implementations under the same interface contract: no target, failed placement, size entering max, and reset semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/FindTargetStrategy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/IllegalContainerBalancerStateException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/IllegalContainerBalancerStateException.java

Purpose: domain exception for invalid Container Balancer state transitions.

Important APIs: no-arg and message constructors, extending `SCMServiceException`.

Control flow and state: carries only exception message/cause state inherited from the superclass. No persistence or side effects.

Dependencies and integration: thrown by balancer service lifecycle/control code when an operation such as start, stop, or configuration update is illegal for the current state.

Risks: no cause constructor, so call sites that catch a lower-level cause cannot preserve it directly. Test signals are mostly service-level: invalid lifecycle transitions should assert this specific exception type and useful message text.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/IllegalContainerBalancerStateException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/InvalidContainerBalancerConfigurationException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/InvalidContainerBalancerConfigurationException.java

Purpose: domain exception for invalid `ContainerBalancerConfiguration` values.

Important APIs: no-arg constructor, message constructor, and message plus `IOException` cause constructor, all extending `SCMServiceException`.

Control flow and state: pure exception wrapper with inherited message/cause persistence. The IOException constructor supports configuration parsing failures while preserving the original IO problem.

Dependencies and integration: used by configuration validation and balancer service startup/update paths.

Risks: cause constructor is specialized to `IOException`, so non-IO validation causes cannot be preserved without wrapping elsewhere. Test signals should assert invalid threshold, size, timeout, and file parsing paths fail with this type and include actionable messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/InvalidContainerBalancerConfigurationException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/IterationInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/IterationInfo.java

Purpose: immutable metadata for a Container Balancer iteration: number, result text, and duration.

Important APIs: constructor and getters for `Integer iterationNumber`, `String iterationResult`, and `Long iterationDuration`.

Control flow and state: construction boxes the primitive duration into `Long`; no validation, persistence, or mutation after construction.

Dependencies and integration: included in `ContainerBalancerTaskIterationStatusInfo` and surfaced in current/history balancer status tests.

Risks: nullable result is tolerated by proto conversion in the aggregate, but nullable iteration number or duration would fail later. Test signals should cover successful and failed iteration result reporting, including in-progress or not-yet-set result text if used by callers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/IterationInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/MoveManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/MoveManager.java

Purpose: schedules, tracks, and completes balancer replica moves as a two-phase operation: replicate to target, then delete from source.

Important APIs/types: `move`, `opCompleted`, timeout setters, `setIncludeNonStandardContainers`, `getPendingMove`, `resetState`, nested `MoveOperation`, and `MoveResult`. It implements `ContainerReplicaPendingOpsSubscriber`.

Control flow and state: `move()` validates source/target health and in-service status, source existence, target absence, container lifecycle, health before and after projected move, and no pending ADD/DELETE ops. It stores one pending move per `ContainerID` in a `ConcurrentHashMap`, sends a low-priority replicate command, then reacts to pending-op callbacks. Successful ADD triggers source delete if future health remains acceptable; successful DELETE completes the future. Expired ADD/DELETE complete with timeout-specific results.

Dependencies and integration: depends on `ReplicationManager`, `ContainerManager`, pending ops notifications, node status, container health results, Ratis leader checks, and replica indexes. Heavily tested by `TestMoveManager` and balancer task/node-limit tests.

Risks: synchronization is on `ContainerInfo`, but pending-op notifications can race with health changes; TODO notes lock coupling with pending ops. `includeNonStandardContainers` relaxes over-replication/quasi-closed rules and needs focused coverage. Unexpected exception paths complete futures but callback failure may leave map entries in some branches. Test signals should include every `MoveResult`, timeout callback ordering, quasi-closed/over-replicated moves, source disappearing after add, duplicate move requests, and leader loss.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/MoveManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/package-info.java

Purpose: package documentation marker for Container Balancer classes.

Important APIs: declares package `org.apache.hadoop.hdds.scm.container.balancer`; no runtime API.

Control flow and state: no executable code, persistence, or dependencies beyond Java package metadata.

Dependencies and integration: helps Javadoc grouping for balancer strategies, move management, status DTOs, metrics, and configuration classes.

Risks and tests: no direct tests needed. Documentation should remain accurate as balancer responsibilities evolve, especially around move manager and strategy packages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/metrics/SCMContainerManagerMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/metrics/SCMContainerManagerMetrics.java

Purpose: Hadoop metrics source for SCM ContainerManager operation and report counters.

Important APIs: static `create`, `unRegister`, increment methods for create/delete/list/container-report/ICR success and failure, and getters for all counters.

Control flow and state: private constructor; `create()` registers a new metrics source with `DefaultMetricsSystem` under source name `SCMContainerManagerMetrics`. Counters are mutable metrics objects reset by process restart and unregistered explicitly.

Dependencies and integration: used by ContainerManager and report handlers to expose operational counters in Ozone metrics context.

Risks: repeated `create()` without unregister may conflict depending on metrics system behavior; no idempotent get-existing logic unlike placement metrics. Counter fields are injected by metrics framework, so direct construction outside registration would leave null counters. Test signals should verify registration/unregistration and report handler increments for success/failure paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/metrics/SCMContainerManagerMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/metrics/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/metrics/package-info.java

Purpose: package documentation for StorageContainerManager container metric classes.

Important APIs: declares package `org.apache.hadoop.hdds.scm.container.metrics`; no runtime API.

Control flow and state: no executable logic or persistence.

Dependencies and integration: groups `SCMContainerManagerMetrics` in Javadocs.

Risks and tests: no direct tests needed. Keep documentation synchronized if more container-level metric sources are added.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/metrics/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/package-info.java

Purpose: package documentation for SCM container location and mapping management.

Important APIs: declares package `org.apache.hadoop.hdds.scm.container`; no runtime API.

Control flow and state: no executable logic, state, or persistence.

Dependencies and integration: high-level Javadoc anchor for container manager, state manager, report handlers, replication-related DTOs, and placement subpackages.

Risks and tests: no direct tests. Documentation should remain broad enough for the package, which includes both container metadata and report-processing responsibilities.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/ContainerPlacementPolicyFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/ContainerPlacementPolicyFactory.java

Purpose: factory that instantiates configured container placement policy implementations for replicated and EC containers.

Important APIs: `getPolicy`, `getECPolicy`, and private `getPolicyInternal`. Defaults are `SCMContainerPlacementRackAware` for replicated placement and `SCMContainerPlacementRackScatter` for EC placement.

Control flow and state: reads configured class from `ConfigurationSource`, finds a constructor `(NodeManager, ConfigurationSource, NetworkTopology, boolean, SCMContainerPlacementMetrics)`, and invokes it reflectively. No persistence or static mutable state beyond constants.

Dependencies and integration: uses `ScmConfigKeys` placement keys, `PlacementPolicy`, `NodeManager`, `NetworkTopology`, and placement metrics. Used by SCM and balancer mock/test setup. Covered by `TestContainerPlacementFactory`.

Risks: constructor error message omits the metrics parameter in text; instantiation exceptions are wrapped in `RuntimeException`, not `SCMException`, which can surprise callers. Tests should cover bad class, missing constructor, default replicated policy, default EC policy, and custom policy creation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/ContainerPlacementPolicyFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/ContainerPlacementStatusDefault.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/ContainerPlacementStatusDefault.java

Purpose: default `ContainerPlacementStatus` implementation for rack-count and max-replicas-per-rack validation.

Important APIs: constructors, `isPolicySatisfied`, `misReplicatedReason`, `misReplicationCount`, `expectedPlacementCount`, and `actualPlacementCount`.

Control flow and state: immutable fields describe required/current/total racks, max replicas per rack, and per-rack replica counts. Policy is satisfied when current racks meet `min(totalRacks, requiredRacks)` and no rack exceeds max replicas.

Dependencies and integration: returned by placement policies and used throughout replication health checks to classify mis-replication. Unit-tested by `TestContainerPlacementStatusDefault` and used in many replication handler tests.

Risks: constructor trusts the caller to provide a rack count list consistent with current racks. Mis-replication count returns the max of missing racks and excess-per-rack sum, which is a policy choice that tests should pin down for mixed violations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/ContainerPlacementStatusDefault.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/SCMContainerPlacementCapacity.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/SCMContainerPlacementCapacity.java

Purpose: capacity-biased placement policy using the "power of two choices": randomly sample two healthy candidates and choose the lower-utilization node.

Important APIs: constructor, `chooseDatanodesInternal`, and `chooseNode`.

Control flow and state: delegates base filtering to `SCMCommonPlacementPolicy`, increments placement metrics, returns preselected healthy nodes if enough are already chosen, otherwise repeatedly chooses from the healthy list. `chooseNode` removes the selected node from the candidate list.

Dependencies and integration: uses `NodeManager.getNodeStat` and `SCMNodeMetric.isGreater` to compare utilization. Tests exist in `TestSCMContainerPlacementCapacity` and older placement tests.

Risks: metrics must be non-null; node stats must be available for sampled nodes. If both random indexes match, only one node is considered. Test signals should cover removal, metric increments, low-utilization bias, insufficient healthy nodes through the superclass, and zero-capacity stats handled by `SCMNodeMetric`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/SCMContainerPlacementCapacity.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/SCMContainerPlacementMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/SCMContainerPlacementMetrics.java

Purpose: Hadoop metrics source for topology-aware container placement activity.

Important APIs: static `create`, increment methods for request, attempt, success, and fallback counts, `unRegister`, testing getters, and `getMetrics`.

Control flow and state: `create()` returns an already registered source if available; otherwise it initializes a static `MetricsRegistry` and registers a new metrics source. `getMetrics()` snapshots the static registry into a record.

Dependencies and integration: used by placement policies to count allocation attempts and fallback choices. Tested indirectly by rack-aware/rack-scatter placement tests and metrics getters.

Risks: `registry` is static while metric fields are instance fields; after unregister/re-register sequences, stale registry behavior should be tested. Direct construction without `create()` may leave metric fields uninitialized. Test signals should include idempotent create and unregister behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/SCMContainerPlacementMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/SCMContainerPlacementRackAware.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/SCMContainerPlacementRackAware.java

Purpose: rack-aware placement policy for replicated containers, following HDFS-style 3-replica layout with two replicas on one rack and the third on another when racks allow.

Important APIs: `chooseDatanodesInternal`, legacy choose path, private `chooseNode` and `chooseNodes`, plus rack-policy overrides `getMaxReplicasPerRack` and `getRequiredRackCount`.

Control flow and state: validates node counts, filters favored nodes, handles new-pipeline versus add-replica scenarios, and chooses nodes with same-rack affinity or cross-rack exclusion. `chooseNode` retries random topology selection, checks disk resources via superclass `isValidNode`, and optionally falls back by dropping affinity or rack constraints.

Dependencies and integration: depends on `NetworkTopology`, `NodeManager`, `SCMCommonPlacementPolicy`, and `SCMContainerPlacementMetrics`. Covered by `TestSCMContainerPlacementRackAware` and factory tests.

Risks: in the branch for two or more used nodes with all used nodes on different racks, code references `chosenNodes.get(0)` before any node is added, which looks like an `IndexOutOfBoundsException` path. Favored nodes are accepted in some branches without a local `isValidNode` check. Tests should cover that all-used-on-different-racks add-replica case, fallback disabled behavior, excluded/favored overlap, and capacity failure retry accounting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/SCMContainerPlacementRackAware.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/SCMContainerPlacementRackScatter.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/SCMContainerPlacementRackScatter.java

Purpose: rack-scatter placement policy, used especially for EC, that tries to distribute replicas across as many racks as possible while respecting max replicas per rack and resource constraints.

Important APIs: constructors, `chooseDatanodesInternal`, `chooseNodesFromRacks`, private `chooseNode`, `getRequiredRackCount`, `findRacksWithOnlyExcludedNodes`, `sortRackWithExcludedNodes`, and `getAllRacks`.

Control flow and state: filters available nodes, validates enough candidates, shuffles racks and favored nodes, counts used nodes per rack, removes unavailable racks, chooses required new racks first, then fills remaining nodes while honoring max replicas per rack. It validates final placement and avoids worsening mis-replication relative to initial used nodes.

Dependencies and integration: uses `NetworkTopology`, `SCMCommonPlacementPolicy`, `ContainerPlacementStatus`, and metrics. Tested extensively by `TestSCMContainerPlacementRackScatter` and used as default EC placement.

Risks: constructor accepts `fallback` but does not store/use it. The second fill phase adds used racks to the rack list twice, which may be intentional preference or duplicate risk. `chooseNode` mutates the excluded list passed in. Tests should include all-excluded racks, dead nodes with null rack, favored nodes, EC required rack count, and no-worse mis-replication behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/SCMContainerPlacementRackScatter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/SCMContainerPlacementRandom.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/SCMContainerPlacementRandom.java

Purpose: simple random placement policy that chooses healthy datanodes without utilization or topology weighting.

Important APIs: constructor, `chooseDatanodesInternal`, and `chooseNode`.

Control flow and state: base class filters available healthy nodes by used/excluded/favored and space requirements. If more nodes are needed, `getResultSet` repeatedly calls `chooseNode`, which selects a random element, removes it, and increments metrics.

Dependencies and integration: implements `PlacementPolicy`, extends `SCMCommonPlacementPolicy`, uses `NodeManager`, config, and metrics. Tested by `TestSCMContainerPlacementRandom` and some pipeline manager tests.

Risks: metrics must be non-null. Random behavior makes statistical assertions fragile; tests should seed or mock randomness where possible. Since the policy intentionally ignores balancing, deployments relying on it need balancer coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/SCMContainerPlacementRandom.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/package-info.java

Purpose: Javadoc package marker for container placement algorithms.

Important APIs: package declaration only.

Control flow and state: no executable code or persistence.

Dependencies and integration: groups random, capacity, rack-aware, rack-scatter, factory, status, and metrics classes.

Risks and tests: no direct tests. Documentation may need expansion as more placement policy variants are added.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/ContainerStat.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/ContainerStat.java

Purpose: mutable aggregate of container statistics: max size, used bytes, key count, read/write bytes, and read/write counts.

Important APIs: default and full constructors, getters for seven `LongMetric` fields, `add`, `subtract`, and `toJsonString`.

Control flow and state: validates non-negative constructor inputs, stores each metric as a mutable `LongMetric`, and mutates in place on add/subtract. JSON serialization uses `JsonUtils` and returns null on `IOException`.

Dependencies and integration: used by `SCMMetrics` for last and cumulative container report statistics.

Risks: constructor checks `readBytes >= 0` twice and does not check `writeBytes >= 0`, allowing negative write bytes. `subtract` can produce negative values despite constructor guards. Test signals should cover JSON names, add/subtract math, negative validation including write bytes, and null handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/ContainerStat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/DatanodeMetric.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/DatanodeMetric.java

Purpose: generic metric interface for comparing datanode metrics and checking resource availability.

Important APIs: comparison helpers `isGreater`, `isLess`, `isEqual`; `hasResources`; `get`; `set`; `add`; `subtract`.

Control flow and state: interface only; implementations define mutability and comparison semantics.

Dependencies and integration: implemented by `LongMetric` and `SCMNodeMetric`; used by placement and pipeline selection to compare capacity utilization.

Risks: `hasResources` has implementation-specific meaning and can be misleading where implementations return placeholders. Tests should be implementation-specific and verify comparator consistency with equals/hashCode where values are used in sorted collections.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/DatanodeMetric.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/LongMetric.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/LongMetric.java

Purpose: mutable `Long` implementation of `DatanodeMetric`.

Important APIs: constructor, comparison helpers, `hasResources`, `get`, `set`, `add`, `subtract`, `compareTo`, `equals`, and `hashCode`.

Control flow and state: stores a boxed `Long` and mutates it directly. `hasResources` requires strictly greater than requested, not greater-than-or-equal.

Dependencies and integration: embedded in `ContainerStat` and `SCMNodeStat`; serialized by Jackson with field visibility.

Risks: not thread-safe; null values can be set and later cause NPEs in comparison/add/subtract. Strict resource comparison may reject exact-fit resources if used for capacity checks. Test signals should cover exact resource boundary, equality/hash behavior, and mutation effects in parent objects.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/LongMetric.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/NodeStat.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/NodeStat.java

Purpose: package-private interface describing SCM node capacity and usage statistics.

Important APIs: getters for capacity, SCM used, remaining, committed, free space to spare, and reserved; test-visible `set`; `add`; `subtract`.

Control flow and state: interface only. Implementations decide validation and mutability; `SCMNodeStat` is the concrete class in this subset.

Dependencies and integration: used by `SCMNodeStat` and `SCMNodeMetric` to support node manager statistics and placement comparisons.

Risks: package-private visibility limits external contract enforcement. Add/subtract may allow negative derived values unless implementations guard. Test signals should focus on concrete `SCMNodeStat` arithmetic and equality.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/NodeStat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/SCMMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/SCMMetrics.java

Purpose: Storage Container Manager metrics source for container report totals, last report gauges, DB checkpoint metrics, and bounded Ratis event text.

Important APIs: static `create`, setters/increment/decrement methods for container stats, `setLastContainerStat`, `incrContainerStat`, `decrContainerStat`, `addRatisEvent`, metric getter `getRatisEvents`, `getDBCheckpointMetrics`, and `unRegister`.

Control flow and state: registers with `DefaultMetricsSystem`; creates `DBCheckpointMetrics`; keeps a synchronized `LinkedList` of formatted Ratis events capped by configured max size.

Dependencies and integration: used by SCM report processing and Ratis event tracking; reads `OZONE_SCM_RATIS_EVENTS_MAX_LIMIT` from config.

Risks: `create()` is not idempotent; repeated registration can conflict. Counter decrements are implemented as negative increments, so totals can go negative. Tests should cover bounded event eviction, stat gauge/counter updates, unregister behavior, and DB checkpoint metrics creation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/SCMMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/SCMNodeMetric.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/SCMNodeMetric.java

Purpose: comparable metric wrapper around `SCMNodeStat` for placement and pipeline capacity comparisons.

Important APIs: constructors, `isGreater`, `isLess`, `isEqual`, `hasResources`, `get`, `set`, `add`, `subtract`, `compareTo`, equality/hash, and `toString`.

Control flow and state: compares nodes primarily by used/capacity utilization with epsilon tolerance, then by raw used bytes. Zero capacity denominators are replaced by one in `isGreater`/`isLess`, but not in `isEqual`.

Dependencies and integration: returned by `NodeManager.getNodeStat`; used by capacity placement and pipeline choose policy. Tested through node and pipeline tests.

Risks: `hasResources` always returns false, so it should not be used as a real resource check. `isEqual` can divide by zero and produce NaN behavior for zero-capacity stats. `compareTo` equality by utilization may be inconsistent with `equals` by full stat. Test signals should cover zero capacity, sorted collection behavior, and comparator ties.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/SCMNodeMetric.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/SCMNodeStat.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/SCMNodeStat.java

Purpose: mutable node storage statistic containing capacity, SCM used, remaining, committed, free space to spare, and reserved bytes.

Important APIs: default/copy/full constructors, metric getters, test-visible `set`, `add`, `subtract`, equality/hash, and `toString`.

Control flow and state: constructors and `set` validate capacity, used, and remaining are non-negative, but not committed, free space to spare, or reserved. Add/subtract mutate each `LongMetric` in place and can produce negative fields.

Dependencies and integration: wrapped by `SCMNodeMetric`, maintained by node manager, and used by placement/pipeline choice logic.

Risks: partial validation can allow negative committed/reserved/free-space values. `hashCode` XORs long values before `Long.hashCode`, which is adequate but coarse. Test signals should include copy independence, arithmetic, negative validation for all fields, and equality across all six metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/SCMNodeStat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/SCMPerformanceMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/SCMPerformanceMetrics.java

Purpose: metrics source for SCM performance counters and latencies around delete-key and allocate-block operations.

Important APIs: static singleton `create`, `unRegister`, `getMetrics`, latency update methods, delete-key success/failure stats, block counters, and block getter methods.

Control flow and state: `create()` caches a static instance and registers it once. Updates compute elapsed nanoseconds using `Time.monotonicNowNanos()` and add to `MutableRate` fields; counters are mutable metrics fields.

Dependencies and integration: integrated with SCM block/key deletion and block allocation paths; uses Ozone metrics context.

Risks: `unRegister()` does not clear the static `instance`, so re-create after unregister may return an unregistered object. Direct construction relies on metrics injection for annotated fields. Tests should verify singleton lifecycle, latency updates with mocked start times, and block counter getters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/SCMPerformanceMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/package-info.java

Purpose: package documentation for datanode and SCM metrics used by placement strategies.

Important APIs: package declaration only.

Control flow and state: no executable code or persistence.

Dependencies and integration: groups `ContainerStat`, `SCMNodeStat`, `SCMNodeMetric`, `SCMMetrics`, and `SCMPerformanceMetrics`.

Risks and tests: no direct tests. Keep wording aligned if package grows beyond placement-related metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/package-info.java

Purpose: package documentation for container placement classes.

Important APIs: package declaration only.

Control flow and state: no executable code or persistence.

Dependencies and integration: Javadoc anchor for placement algorithms and metrics subpackages.

Risks and tests: no direct tests. Documentation is intentionally high-level and should stay accurate as placement policy responsibilities evolve.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/reconciliation/ReconcileContainerEventHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/reconciliation/ReconcileContainerEventHandler.java

Purpose: event handler that starts container reconciliation by sending reconcile commands to all datanodes holding an eligible container replica.

Important APIs: constructor and `onMessage(ContainerID, EventPublisher)`.

Control flow and state: first checks `SCMContext.isLeader`; then uses `ReconciliationEligibilityHandler`. If eligible, it gathers all replica datanodes, and for each replica fires a `DATANODE_COMMAND` containing `ReconcileContainerCommand(containerId, otherReplicas)` with the current leader term. It catches container-not-found and not-leader cases.

Dependencies and integration: depends on `ContainerManager`, `SCMContext`, event bus, `CommandForDatanode`, and `ReconcileContainerCommand`. Tested by `TestReconcileContainerEventHandler`.

Risks: TODO notes peer/target nodes are not restricted by node status. The replica set can change between eligibility and command creation. Tests should cover leader false, not-leader exception, no replicas, ineligible state/type, and command peer sets for each target.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/reconciliation/ReconcileContainerEventHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/reconciliation/ReconciliationEligibilityHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/reconciliation/ReconciliationEligibilityHandler.java

Purpose: utility that decides whether a container may be reconciled.

Important APIs: static `isEligibleForReconciliation`, eligible container/replica state sets, enum `Result`, and nested `EligibilityResult`.

Control flow and state: fetches container and replicas from `ContainerManager`; rejects missing containers, non-CLOSED/non-QUASI_CLOSED containers, empty replicas, replica states outside CLOSED/QUASI_CLOSED/UNHEALTHY, non-Ratis replication, and replication configs with required nodes <= 1. Returns `OK` otherwise.

Dependencies and integration: called by `ReconcileContainerEventHandler` and tested in `TestReconcileContainerEventHandler`.

Risks: OK message concatenates instead of formatting (`"Container %s..." + containerID`), so it contains a literal `%s`. Eligibility ignores datanode operational/health state until HDDS-10714. Test signals should assert every rejection reason and message, plus eligible CLOSED and QUASI_CLOSED Ratis containers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/reconciliation/ReconciliationEligibilityHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/reconciliation/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/reconciliation/package-info.java

Purpose: package documentation for container reconciliation classes.

Important APIs: package declaration only.

Control flow and state: no executable logic or persistence.

Dependencies and integration: groups reconciliation event handling and eligibility checks.

Risks and tests: no direct tests. Package docs should be expanded if reconciliation gains EC support or node-status filtering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/reconciliation/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/AbstractOverReplicationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/AbstractOverReplicationHandler.java

Purpose: shared base for over-replication handlers, centralizing placement-aware replica removal helpers.

Important APIs: constructor, `isPlacementStatusActuallyEqualAfterRemove`, `selectReplicasToRemove`, and `getPlacementStatus`.

Control flow and state: holds a `PlacementPolicy`. To test a removal, it temporarily removes a replica from the passed set, computes new placement, then adds the replica back. It considers placement "actually equal" if both statuses are satisfied or if both are unsatisfied with the same actual placement count.

Dependencies and integration: used by concrete Ratis/EC over-replication handlers; delegates removal selection and placement validation to `PlacementPolicy`. Tested through over-replication handler suites.

Risks: mutates the caller's replica set temporarily, which is unsafe if the set is concurrently shared or if exceptions occur between remove/add. Equality ignores detailed max-replica-per-rack violations. Tests should cover placement-preserving deletion and exception-safe behavior expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/AbstractOverReplicationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/CommandTargetOverloadedException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/CommandTargetOverloadedException.java

Purpose: checked exception indicating that all possible command targets are overloaded.

Important APIs: message constructor extending `IOException`.

Control flow and state: pure exception type; no additional fields or behavior.

Dependencies and integration: thrown by replication scheduling paths when command load limits prevent selecting a target or source. Tests in `TestReplicationManager` assert overloaded target scenarios.

Risks: no cause constructor, so lower-level selection errors cannot be preserved directly. Test signals should assert callers distinguish overload from no suitable node and from leader failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/CommandTargetOverloadedException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerCheckRequest.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerCheckRequest.java

Purpose: immutable request wrapper for container health checks in ReplicationManager.

Important APIs: getters, nested `Builder` setters, and `build`.

Control flow and state: constructor wraps replica set and pending ops list with unmodifiable views. It stores container info, maintenance redundancy, report, replication queue, and read-only flag.

Dependencies and integration: passed to replication health check handlers; combines `ContainerInfo`, `ContainerReplica`, `ContainerReplicaOp`, `ReplicationManagerReport`, and `ReplicationQueue`.

Risks: builder does not validate required fields; null `containerReplicas` or `pendingOps` will cause NPE in construction, while null report/queue may fail later. Unmodifiable wrappers are shallow and reflect mutations to the original collection if the caller keeps it. Tests should cover builder completeness, read-only behavior in handlers, and immutability expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerCheckRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerHealthResult.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerHealthResult.java

Purpose: result hierarchy representing container replication health and any commands generated while checking it.

Important APIs/types: base `ContainerHealthResult`, `HealthyResult`, `UnHealthyResult`, `UnderReplicatedHealthResult`, `MisReplicatedHealthResult`, `OverReplicatedHealthResult`, and enum `HealthState`.

Control flow and state: base stores container info, health state, and mutable command list. Under-replicated results track remaining redundancy, out-of-service weighting, pending sufficiency, unrecoverable/missing/offline-index flags, healthy replica presence, vulnerable unhealthy replicas, and requeue count. Mis-replication subclasses under-replication with weighted redundancy 6. Over-replication tracks excess redundancy, pending correction, mismatched replicas, and safe over-replication.

Dependencies and integration: produced by replication health handlers and consumed by ReplicationManager queues, balancer selection, deleted block log, and tests.

Risks: mutable command list is exposed directly; requeue count mutates priority semantics. Mis-replication inheriting under-replication behavior requires careful queue tests. Test signals should cover weighted redundancy ordering, pending-corrected flags, missing/unrecoverable flags, over-replicated safety, and balancer rejection/allowance decisions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerHealthResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerReplicaCount.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerReplicaCount.java

Purpose: common interface for Ratis and EC replica-count health calculations.

Important APIs: container/replica getters, sufficient/over-replicated checks, offline safety check, decommission/maintenance counts, `isHealthy`, `isHealthyEnoughForOffline`, and `isUnrecoverable`.

Control flow and state: default `isHealthy()` requires container lifecycle CLOSED or QUASI_CLOSED and all IN_SERVICE replicas to compare equal to the container state via `ReplicationManager.compareState`.

Dependencies and integration: implemented by Ratis and EC replica-count classes, used by ReplicationManager and datanode admin/decommission workflows. Tests exercise concrete implementations and admin monitor decisions.

Risks: default health ignores replicas not in persisted IN_SERVICE state; correctness depends on `DatanodeDetails.getPersistedOpState()` freshness. Test signals should cover maintenance/decommission states, quasi-closed comparison rules, and offline eligibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerReplicaCount.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerReplicaOp.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerReplicaOp.java

Purpose: immutable descriptor for a pending replica ADD or DELETE operation.

Important APIs: constructor, getters for op type, target, replica index, command, deadline epoch millis, container size, and enum `PendingOpType`.

Control flow and state: no internal mutation; all pending-op lifecycle state is managed by `ContainerReplicaPendingOps`. The command may be nullable.

Dependencies and integration: stored by pending ops, passed to subscribers like `MoveManager`, and used by ReplicationManager tests to assert scheduled operations.

Risks: no equals/hashCode, so duplicate detection must compare fields manually as pending ops does. Deadline semantics rely on caller-provided clock values. Test signals should cover ADD/DELETE tracking, EC replica indexes, command retention, and size accounting for ADD ops.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerReplicaOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerReplicaPendingOps.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerReplicaPendingOps.java

Purpose: in-memory tracker for pending container replica ADD and DELETE operations across the cluster.

Important APIs/types: constructor, `scheduleAddReplica`, `scheduleDeleteReplica`, completion/removal methods, `removeExpiredEntries`, `getPendingOps`, `clear`, `registerSubscriber`, pending op counters by type/replication type, `getContainerSizeScheduled`, and nested `SizeAndTime`.

Control flow and state: uses `ConcurrentHashMap<ContainerID, List<ContainerReplicaOp>>`, striped read/write locks per container, and a global clear lock. Scheduling removes duplicate same-type target/index ops before adding a new one, increments counters, and tracks pending ADD bytes per target datanode. Completion removes matching ops, decrements counters, releases scheduled size, and notifies subscribers after locks are released. Expiration removes ADD ops but leaves DELETE ops for resending, while still notifying and updating timeout metrics.

Dependencies and integration: used by ReplicationManager, report handlers, block manager setup, and MoveManager callbacks. Tests in `TestReplicationManager` and balancer move tests exercise pending-op behavior.

Risks: `rmConf` may be null, but `releaseScheduledContainerSize` calls `rmConf.getEventTimeout()` on ADD expiration; null config plus expiring ADD can NPE. `subscribers` is an unsynchronized `ArrayList`. Counter/map consistency depends on all mutation paths using locks. Test signals should include duplicate scheduling, concurrent clear/update, ADD size release, DELETE expiry retention, subscriber callbacks, EC/Ratis counters, and null configuration expiration behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerReplicaPendingOps.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerReplicaPendingOpsSubscriber.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerReplicaPendingOpsSubscriber.java

Purpose: callback interface for objects interested in pending replica operation completion or timeout.

Important APIs: `opCompleted(ContainerReplicaOp op, ContainerID containerID, boolean timedOut)`.

Control flow and state: interface only. Implementations receive individual operations after pending ops has removed or observed timeout state.

Dependencies and integration: `ContainerReplicaPendingOps` invokes it; `MoveManager` implements it to progress two-phase balancer moves.

Risks: callback name says completed even when `timedOut` is true, so implementers must inspect the flag. Subscribers are invoked synchronously; slow or throwing subscribers can affect notification flow. Tests should include multiple subscribers, timeout and normal completion, and exception containment expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerReplicaPendingOpsSubscriber.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/DatanodeCommandCountUpdatedHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/DatanodeCommandCountUpdatedHandler.java

Purpose: event handler for `DATANODE_COMMAND_COUNT_UPDATED` notifications.

Important APIs: constructor and `onMessage(DatanodeDetails, EventPublisher)`.

Control flow and state: logs at trace and delegates the datanode to `ReplicationManager.datanodeCommandCountUpdated`. No local persistence or mutation.

Dependencies and integration: wired into SCM event framework; used to wake or inform ReplicationManager when datanode command load changes. Tested by `TestDatanodeCommandCountUpdatedHandler`.

Risks: no null guard for datanode or replication manager; errors propagate from ReplicationManager. Test signals should verify delegation exactly once and no event publisher dependency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/DatanodeCommandCountUpdatedHandler.java -->
