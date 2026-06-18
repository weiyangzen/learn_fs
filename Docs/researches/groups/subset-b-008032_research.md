# subset-b-008032 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ECContainerReplicaCount.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ECContainerReplicaCount.java

Purpose: `ECContainerReplicaCount` is the EC-specific implementation of `ContainerReplicaCount`. It classifies EC container replicas by replica index and node operational state so health checks and repair handlers can decide whether a container is under-replicated, over-replicated, unrecoverable, missing, or safe enough for decommission and maintenance transitions.

Important APIs and behavior: the constructor accepts `ContainerInfo`, current `ContainerReplica` set, pending ops, and remaining maintenance redundancy. It sorts replicas deterministically by hash, records pending add/delete indexes, validates EC replica indexes against `ECReplicationConfig.getRequiredNodes()`, and builds separate count maps for healthy, unhealthy, decommissioning/decommissioned, and maintenance replicas. Pending deletes against healthy replicas are immediately subtracted from `healthyIndexes`; pending deletes for datanodes that only have unhealthy replicas are ignored because unhealthy replicas are already excluded from healthy availability.

Control flow: `isSufficientlyReplicated(includePendingAdd)` first checks for a full set of healthy EC indexes, then allows maintenance indexes to fill the set only if enough online redundancy remains. `unavailableIndexes`, `decommissioningOnlyIndexes`, `maintenanceOnlyIndexes`, and `additionalMaintenanceCopiesNeeded` feed EC under-replication handling. `isOverReplicated(includePendingDelete)` and `overReplicatedIndexes` identify EC indexes with more than one in-service healthy copy after optional pending-delete treatment. `isUnrecoverable` requires fewer than `data` distinct available indexes; `isMissing` repeats that check with unhealthy indexes included.

State and persistence: the class is in-memory and has no persistence of its own. `addPendingOp` mutates its pending-op/index view so multi-stage handlers can account for commands scheduled earlier in the same processing pass.

Dependencies and integration: it depends on EC replication config, `ContainerReplicaOp`, datanode persisted operational state, and `NodeManager` only for the offline-check interface. It is consumed by EC health checks, EC under/over/mis handlers, and datanode admin code.

Risks: pending-delete treatment is safety-critical; double-counting deletes or applying unhealthy deletes to healthy counts can create false under-replication. The `hasFullSetOfIndexes` check only tests map size because indexes are validated on insert. EC maintenance calculations depend on `remainingMaintenanceRedundancy` being bounded correctly by the caller.

Test signals: `TestECContainerReplicaCount` covers full/missing index sets, pending add/delete effects, maintenance/decommission handling, unrecoverable and missing detection, index validation, over-replication, and offline sufficiency behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ECContainerReplicaCount.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ECMisReplicationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ECMisReplicationHandler.java

Purpose: `ECMisReplicationHandler` specializes the abstract `MisReplicationHandler` for EC containers. It fixes placement-policy violations only after the common mis-replication flow confirms the container is neither under- nor over-replicated and has no pending operations.

Important APIs and behavior: `getContainerReplicaCount` validates that the container replication type is `EC` and creates an `ECContainerReplicaCount`. `sendReplicateCommands` sends one command per source replica and target datanode, preserving the EC replica index in the command.

Control flow: the inherited flow selects healthy in-service `CLOSED` or `QUASI_CLOSED` source replicas, asks the placement policy which replicas should be copied, computes target datanodes, then calls this class to issue commands. EC command emission walks `replicasToBeReplicated` and `targetDns` together until targets are exhausted. In push mode it calls `ReplicationManager.sendThrottledReplicationCommand(containerInfo, singleton source, target, replicaIndex)`. In pull mode it builds `ReplicateContainerCommand.fromSources`, sets the EC replica index, and sends it to the target.

State and persistence: the handler keeps no state. Command state is recorded by `ReplicationManager.sendDatanodeCommand`, which schedules pending add ops and metrics.

Dependencies and integration: it depends on `PlacementPolicy`, SCM configuration, `ReplicationManager`, EC replica counts, `ReplicateContainerCommand`, and Ratis `NotLeaderException`. It is selected by `ReplicationManager.processUnderReplicatedContainer` when a health result is `MIS_REPLICATED` and replication type is EC.

Risks: the handler ignores the `sources` list passed by the abstract class and uses the datanode of each selected source replica directly, which is correct for per-index EC copies but assumes `replicasToBeReplicated` only contains usable sources. If target count is smaller than source count, it silently stops after available targets and the parent detects partial placement by comparing target count with required count. Overloaded sources are collected and rethrown after the loop so partial progress can occur.

Test signals: `TestECMisReplicationHandler` and `TestMisReplicationHandler` exercise EC type validation, placement target selection, push/pull command construction, replica-index preservation, and partial target handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ECMisReplicationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ECOverReplicationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ECOverReplicationHandler.java

Purpose: `ECOverReplicationHandler` fixes EC containers with duplicate healthy in-service copies of the same replica index. It sends delete commands only when removal will not drop an EC index to zero.

Important APIs and behavior: `processAndSendCommands` is the entry point. It filters input replicas to datanodes whose `NodeStatus` is healthy and whose operational state is `IN_SERVICE`, creates `ECContainerReplicaCount`, checks current and future over-replication with and without pending deletes, selects delete candidates through `AbstractOverReplicationHandler.selectReplicasToRemove`, and sends throttled delete commands.

Control flow: non-healthy or non-in-service replicas are removed before over-replication evaluation to avoid deleting the only stable copy while stale/dead replicas disappear. If `isOverReplicated()` is false, or if pending deletes already correct the excess, it returns zero. Otherwise it builds a list of pending-delete datanodes, keeps only healthy `CLOSED` replicas not already pending delete, selects candidates, counts candidate replicas by EC index, and deletes a candidate only when its current index count is at least two. After each successful delete, it decrements the local count.

State and persistence: no local persistent state. Delete commands flow through `ReplicationManager.sendThrottledDeleteCommand`, which enforces per-datanode delete limits and records pending delete ops.

Dependencies and integration: it depends on `ReplicationManager` for node health and delete command dispatch, `PlacementPolicy` through the abstract superclass, EC count logic, node status, and container replica state. `ReplicationManager.processOverReplicatedContainer` selects it for EC containers.

Risks: candidate selection requests only one removal (`selectReplicasToRemove(candidates, 1)`) even if multiple indexes are over-replicated, so repeated queue passes may be required. The placement-policy selection is index-agnostic, and the handler relies on the index-count sanity check to prevent data loss. Filtering out non-healthy nodes avoids a common race but can delay cleanup of excess stale records.

Test signals: `TestECOverReplicationHandler` covers pending delete short-circuiting, non-healthy replica filtering, no-delete cases, overloaded delete targets, and preserving at least one copy per EC index.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ECOverReplicationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ECUnderReplicationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ECUnderReplicationHandler.java

Purpose: `ECUnderReplicationHandler` repairs EC containers by reconstructing missing indexes and copying indexes that exist only on decommissioning or maintenance nodes. It emits EC reconstruction commands for truly missing indexes and replication commands for one-to-one copies of existing indexes.

Important APIs and behavior: `processAndSendCommands` builds `ECContainerReplicaCount`, exits if the container is already sufficient or will be sufficient after pending adds, computes excluded/used nodes, filters usable sources by replica index, and then runs three repair stages: `processMissingIndexes`, `processDecommissioningIndexes`, and `processMaintenanceOnlyIndexes`. It also exposes `integers2ByteString` for reconstruction target index encoding.

Control flow: source filtering accepts `CLOSED` replicas on healthy datanodes, excluding pending deletes, preferring an `IN_SERVICE` source when multiple copies of an index exist. Missing indexes are reconstructed when at least `data` source indexes are available. The handler asks placement for targets, defers non-critical partial reconstruction if full placement would be possible only by using overloaded nodes, validates but does not require placement satisfaction, sends one `ReconstructECContainersCommand`, and records local pending adds. Decommission-only and maintenance-only indexes are copied one-for-one with `ReplicateContainerCommand` or push replication.

State and persistence: local state is limited to the mutable `ECContainerReplicaCount`, local used/excluded lists, and command counters. Durable operational state is in pending ops scheduled by `ReplicationManager`. Metrics track skipped partial reconstruction, critical partial reconstruction, non-overload placement shortage, and partial out-of-service copies.

Dependencies and integration: it depends on EC configs, placement policy, `ReplicationManagerUtil`, `ReplicationManager`, node status, `ReconstructECContainersCommand`, `ReplicateContainerCommand`, pending ops, and SCM metrics. It is selected for EC `UNDER_REPLICATED` queue entries.

Risks: partial reconstruction is complex: target list pruning must stay aligned with the missing-index list, and command scheduling assumes target order matches encoded index order. Placement failures can trigger over-replication processing or unhealthy replica deletion to free targets, which is useful in small clusters but can interact with pending-delete races. Reconstruction reads may include maintenance/decommission sources if they are healthy and no in-service source exists for an index.

Test signals: `TestECUnderReplicationHandler` covers reconstruction command content, source filtering, pending-op updates, maintenance/decommission handling, overloaded nodes, insufficient targets, partial reconstruction metrics, and unhealthy-replica deletion fallback.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ECUnderReplicationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/InflightAction.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/InflightAction.java

Purpose: `InflightAction` is a small value object that records an in-flight replication-related action target and start time. It is used by replication tracking code to remember which datanode an operation targets and when it began.

Important APIs and behavior: the constructor stores a `DatanodeDetails` and a `long` timestamp. `getDatanode` is annotated `@VisibleForTesting`, while `getTime` is public production API.

Control flow: there is no branching or command flow in this class. It is a passive wrapper.

State and persistence: instances are immutable after construction. They are not persisted by this class; any timeout or ledger behavior belongs to the container pending-op or queue components that hold these objects.

Dependencies and integration: it depends only on `DatanodeDetails` and Guava's testing annotation. It sits in the replication package beside `InflightType`, `ContainerReplicaOp`, and pending-operation tracking.

Risks: because `getDatanode` is testing-visible rather than ordinary public API, production code should not rely on inspecting targets through this class unless visibility is intentionally changed. The timestamp has no unit encoded in the type; callers must consistently use the same clock and unit.

Test signals: direct tests are likely indirect through pending-operation timeout and command-tracking tests, especially `TestContainerReplicaPendingOps` and replication processor tests that assert in-flight scheduling and expiry behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/InflightAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/InflightType.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/InflightType.java

Purpose: `InflightType` is a package-private enum classifying pending replication-manager actions as `REPLICATION` or `DELETION`.

Important APIs and behavior: the enum has two values and no methods. Package-private visibility keeps it internal to `org.apache.hadoop.hdds.scm.container.replication`.

Control flow: no control flow exists here; consumers branch on the enum to distinguish add-like work from delete-like work.

State and persistence: enum values are JVM constants. This type itself has no persistence. Any persisted or timed behavior is owned by pending-operation trackers or command queues that store the classification.

Dependencies and integration: it has no imports. It is intended to be used by in-flight action maps, pending-operation logic, or legacy tracking code in the same package.

Risks: the enum names are broad; code that needs EC reconstruction versus Ratis replication, or push versus pull, must not rely on this type alone. Adding new action types would require auditing package-private switch statements and metrics.

Test signals: coverage is indirect through tests that verify pending replication and deletion accounting, such as `TestContainerReplicaPendingOps`, `TestUnderReplicatedProcessor`, and `TestOverReplicatedProcessor`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/InflightType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/MisReplicationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/MisReplicationHandler.java

Purpose: `MisReplicationHandler` is the shared template for fixing placement-policy violations when a container is otherwise sufficiently replicated and not over-replicated. It is subclassed by Ratis and EC handlers for replica-count construction and command emission.

Important APIs and behavior: subclasses implement `getContainerReplicaCount` and `sendReplicateCommands`. The main `processAndSendCommands` rejects containers with pending ops, verifies sufficient and not over-replicated state, validates current placement, selects eligible source replicas, asks the placement policy which replicas should be copied, computes target datanodes, dispatches subclass commands, and throws `InsufficientDatanodesException` if placement found fewer targets than required.

Control flow: `filterSources` allows `CLOSED` and `QUASI_CLOSED` replicas on healthy `IN_SERVICE` datanodes. The placement policy receives a map of every replica to a boolean indicating source eligibility via `replicasToCopyToFixMisreplication`. Used/excluded nodes are computed by `ReplicationManagerUtil`, with selected source replicas excluded so new copies do not land on inappropriate hosts. Partial placement increments EC or Ratis mis-replication metrics.

State and persistence: the handler stores injected placement policy, current container size, `ReplicationManager`, and metrics. It does not persist decisions; commands sent through `ReplicationManager` create pending add records and metrics.

Dependencies and integration: it integrates placement policy, SCM config, `ReplicationManagerUtil`, node health lookup, and per-type subclasses. `ReplicationManager.processUnderReplicatedContainer` uses it for `MIS_REPLICATED` health results.

Risks: skipping all mis-replication work when any pending op exists is conservative but can delay placement repair behind unrelated delete/add work. If placement policy marks a replica for copying that is no longer in `filterSources`, subclass command logic must tolerate missing or unusable sources. The raw `new ArrayList(replicas)` call loses generic type information but is not behaviorally significant.

Test signals: `TestMisReplicationHandler`, `TestRatisMisReplicationHandler`, and `TestECMisReplicationHandler` cover pending-op suppression, placement-satisfied no-op, insufficient target metrics, and type-specific command behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/MisReplicationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/MonitoringReplicationQueue.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/MonitoringReplicationQueue.java

Purpose: `MonitoringReplicationQueue` is a no-op `ReplicationQueue` used for read-only health checks. It allows the normal health-check chain to run without enqueueing under- or over-replicated containers for later command processing.

Important APIs and behavior: it overrides both `enqueue(UnderReplicatedHealthResult)` and `enqueue(OverReplicatedHealthResult)` with empty implementations.

Control flow: the class intentionally discards queue requests. It does not override dequeue methods, so inherited behavior remains irrelevant when used as a sink.

State and persistence: no state is stored and no queue entries persist. This protects read-only callers from side effects while still allowing reports to be updated.

Dependencies and integration: `ReplicationManager` keeps a `noOpsReplicationQueue` instance and uses it in `checkContainerStatus`, where a caller wants the same health classification as a monitor pass but no command work. It depends on `ContainerHealthResult` nested result types and `ReplicationQueue`.

Risks: this queue suppresses only enqueue side effects. Health handlers that send commands directly even in read-only mode would still be risky, so handler implementations must honor `ContainerCheckRequest.readOnly` separately. If future queue types add new enqueue overloads, this class must override them to preserve no-op semantics.

Test signals: coverage is indirect through read-only `ReplicationManager.checkContainerStatus` tests and health-check report tests that confirm status classification without queue growth or command dispatch.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/MonitoringReplicationQueue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/OverReplicatedProcessor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/OverReplicatedProcessor.java

Purpose: `OverReplicatedProcessor` is the queue worker for over-replicated containers. It extends `UnhealthyReplicationProcessor` with the over-replication queue type and delegates command creation to `ReplicationManager`.

Important APIs and behavior: `dequeueHealthResultFromQueue` calls `ReplicationQueue.dequeueOverReplicatedContainer`; `requeueHealthResult` re-enqueues over-replicated results; `inflightOperationLimitReached` always returns false because delete operations have no global in-flight limit; `sendDatanodeCommands` calls `replicationManager.processOverReplicatedContainer`.

Control flow: the superclass owns the processing loop, interval sleeping, exception handling, and requeue behavior. This subclass only selects the over-replication queue and dispatch method.

State and persistence: it has no state beyond superclass state. Queue entries live in `ReplicationQueue`; pending delete commands are recorded when selected handlers call `ReplicationManager.sendDatanodeCommand`.

Dependencies and integration: constructed by `ReplicationManager` with the over-replicated interval supplier. It integrates with EC, Ratis, and quasi-closed stuck over-replication handlers through `ReplicationManager.processOverReplicatedContainer`.

Risks: no global limit for delete operations means per-datanode delete throttling is the only guard against excessive delete command load. If requeue behavior in the superclass treats all IO exceptions equally, overloaded delete targets can cause repeated retries until datanode command counts drop.

Test signals: `TestOverReplicatedProcessor` covers queue selection, requeue behavior, lack of global in-flight limit, and delegation to `ReplicationManager`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/OverReplicatedProcessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/QuasiClosedStuckOverReplicationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/QuasiClosedStuckOverReplicationHandler.java

Purpose: `QuasiClosedStuckOverReplicationHandler` removes excess replicas from Ratis containers that are quasi-closed stuck, where multiple origin datanodes may represent diverged histories. It preserves configured copy counts per origin rather than treating all replicas as equivalent.

Important APIs and behavior: `processAndSendCommands` skips work when any delete is already pending, filters stale/dead replicas by requiring node health `HEALTHY`, constructs `QuasiClosedStuckReplicaCount` with configured best-origin and other-origin copy targets, gets over-replicated origins, sorts each origin's removable replicas deterministically, and sends forced throttled delete commands with replica index `0`.

Control flow: for each mis-replicated origin, it deletes `replicaDelta` replicas from the sorted source list. It records the first `CommandTargetOverloadedException` but continues trying other deletes. If any overloaded exception occurred, it increments partial replication metrics when some commands were sent and rethrows to requeue.

State and persistence: no local persistence. Delete commands are tracked by `ReplicationManager`. The handler uses metrics for partial cleanup.

Dependencies and integration: it depends on `ReplicationManager` for node status, config, delete throttling, and metrics; `QuasiClosedStuckReplicaCount` for origin-aware redundancy; and `QuasiClosedStuckReplicationCheck.shouldHandleAsQuasiClosedStuck` through `ReplicationManager` routing.

Risks: the handler assumes `origin.getSources()` has at least `replicaDelta` entries; the count object currently constructs deltas from set sizes, so this should hold. Filtering out non-healthy datanodes can delay deletion until node state stabilizes. Sorting by `hashCode` gives deterministic deletion but does not prefer lower BCSID within an overfull origin.

Test signals: `TestQuasiClosedStuckOverReplicationHandler` and `TestQuasiClosedStuckReplicaCount` cover pending-delete suppression, origin target counts, deterministic deletes, overload handling, and partial metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/QuasiClosedStuckOverReplicationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/QuasiClosedStuckReplicaCount.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/QuasiClosedStuckReplicaCount.java

Purpose: `QuasiClosedStuckReplicaCount` counts replicas for quasi-closed stuck Ratis containers by origin datanode. This preserves diverged container histories: origins with the highest healthy BCSID are considered best origins and get more target copies, while other origins still receive configured preservation copies.

Important APIs and behavior: the constructor groups all replicas by `originDatanodeId`, separately tracks in-service and maintenance replicas by origin, flags whether any healthy or out-of-service replicas exist, and computes best origins by the maximum non-unhealthy sequence ID. Public APIs include `availableOrigins`, `hasOutOfServiceReplicas`, `hasHealthyReplicas`, `isUnderReplicated`, `isOverReplicated`, `getUnderReplicatedReplicas`, and `getOverReplicatedOrigins`. `MisReplicatedOrigin` carries a source set and replica delta.

Control flow: for a single origin, normal target is three in-service copies, or `minHealthyForMaintenance` when maintenance replicas exist. For multiple origins, best origins target `bestOriginCopies`, all others target `otherOriginCopies`; when maintenance replicas exist, the under-replication path requires at least one online copy of the origin. Over-replication ignores maintenance replicas and compares in-service count with the same target.

State and persistence: all state is in-memory maps and flags derived at construction time. There is no mutation after construction except through mutable sets held internally, and no persistence.

Dependencies and integration: it depends on `ContainerReplica`, `DatanodeID`, and datanode operational states. It is consumed by quasi-closed stuck under/over handlers and configured by `ReplicationManagerConfiguration` best/other origin copy settings.

Risks: only non-unhealthy replicas with non-null sequence IDs participate in best-origin ranking; origins with all unhealthy replicas are never best. If all replicas are unhealthy, best origin set is empty and multi-origin logic applies other-origin targets. Maintenance handling for multiple origins intentionally requires only one online copy, which is a lower target than normal and should remain aligned with the quasi-closed stuck design.

Test signals: `TestQuasiClosedStuckReplicaCount` is extensive and covers single/multiple origin under/over counts, best BCSID ranking, tied best origins, maintenance behavior, all-unhealthy cases, out-of-service flags, and changing origin copy targets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/QuasiClosedStuckReplicaCount.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/QuasiClosedStuckUnderReplicationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/QuasiClosedStuckUnderReplicationHandler.java

Purpose: `QuasiClosedStuckUnderReplicationHandler` creates additional replicas for quasi-closed stuck Ratis containers, preserving each origin according to the origin-aware counts from `QuasiClosedStuckReplicaCount`.

Important APIs and behavior: `processAndSendCommands` skips empty containers because `EmptyContainerHandler` will delete them, suppresses work while pending adds exist, builds a count object with configured best/other origin copy targets, finds under-replicated origins, chooses targets per origin, and sends push replication commands with replica index `0`.

Control flow: for each mis-replicated origin, it asks placement for `replicaDelta` targets using current replicas plus a mutable pending-op list. After each successful command it appends a synthetic pending ADD to the mutable list so later origins do not choose the same target. Source datanodes are all replicas in the origin source set. If target selection or command sending fails, it records the first exception, continues where possible, increments partial metrics when not all required replicas were scheduled, and rethrows or raises `InsufficientDatanodesException`.

State and persistence: local state is limited to counters and mutable pending ops for one processing call. Durable command state is scheduled by `ReplicationManager.sendThrottledReplicationCommand`.

Dependencies and integration: it depends on Ratis placement policy, SCM container size config, `ReplicationManagerUtil`, `ReplicationManager`, metrics, and `QuasiClosedStuckReplicaCount`. `ReplicationManager` routes Ratis under-replicated results to this handler when the quasi-closed stuck health check says the container needs special handling.

Risks: source lists are origin-specific but not filtered by node health in this handler; the count object includes all replicas passed by the caller, so routing must provide appropriate replica sets and command throttling must handle overloaded sources. Pending-add suppression at the top means only one batch is scheduled at a time, which avoids overfill but can slow recovery across many origins.

Test signals: `TestQuasiClosedStuckUnderReplicationHandler` covers empty-container skipping, pending-add suppression, target selection with mutable pending ops, partial failure metrics, insufficient datanodes, and best/other origin configuration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/QuasiClosedStuckUnderReplicationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/RatisContainerReplicaCount.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/RatisContainerReplicaCount.java

Purpose: `RatisContainerReplicaCount` is the Ratis implementation of `ContainerReplicaCount`. It summarizes scalar replica counts, pending add/delete counts, state mismatches, maintenance/decommission replicas, and optional unhealthy-replica availability for Ratis health checks and repair handlers.

Important APIs and behavior: constructors accept either raw in-flight counts or `ContainerReplicaOp` lists. The main constructor can `considerUnhealthy`, which affects pending-delete accounting, available replicas, maintenance/decommission counts, and under-replication decisions. `countReplicas` classifies each replica by datanode operational state and replica health. A `QUASI_CLOSED` replica with the wrong sequence ID for a `CLOSED` container is treated as unhealthy.

Control flow: `additionalReplicaNeeded` computes the repair delta using a worst-case model where deletes succeed and adds fail. `missingReplicas` ignores maintenance for over-replication and uses maintenance/decommission counts to decide whether under-replication can be covered by out-of-service replicas while maintaining minimum healthy count. `isSufficientlyReplicated`, `isOverReplicated`, `getExcessRedundancy`, `insufficientDueToOutOfService`, and `getRemainingRedundancy` feed health results. `getVulnerableUnhealthyReplicas` identifies non-empty unhealthy quasi-closed replicas at the container sequence ID whose origins lack an in-service copy.

State and persistence: the object is mostly a derived snapshot, but `getVulnerableUnhealthyReplicas` mutates the internal `replicas` list by removing replicas on non-healthy datanodes. No data is persisted here.

Dependencies and integration: it depends on `ReplicationManager.compareState`, container lifecycle state, replica state, `ContainerReplicaOp`, `NodeStatus`, and datanode operational states. It is used by Ratis health checks, under/over/mis handlers, and datanode admin offline checks.

Risks: the `considerUnhealthy` flag changes semantics significantly; using the wrong count object can cause either missed recovery of only-unhealthy containers or unsafe counting of bad replicas. The mutable list side effect in `getVulnerableUnhealthyReplicas` can surprise callers that reuse the object. Remaining redundancy uses `available + out-of-service - inflight deletes - 1`, so pending delete accuracy is important.

Test signals: `TestRatisContainerReplicaCount` covers pending ops, maintenance minimums, decommission, over/under deltas, mismatched replicas, vulnerable unhealthy replicas, sequence IDs, and offline health checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/RatisContainerReplicaCount.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/RatisMisReplicationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/RatisMisReplicationHandler.java

Purpose: `RatisMisReplicationHandler` is the Ratis-specific subclass of `MisReplicationHandler`. It fixes placement-policy violations for Ratis containers by copying the container to selected target datanodes.

Important APIs and behavior: `getContainerReplicaCount` validates the replication type is `RATIS` and returns a `RatisContainerReplicaCount` with `considerUnhealthy=true`. `sendReplicateCommands` sends one command to each selected target, using all available source datanodes for Ratis replication.

Control flow: inherited logic verifies no pending ops, not under-replicated, not over-replicated, and placement violation before target selection. In push mode, the handler sends throttled replication commands to source datanodes with target and replica index `0`. In pull mode, it sends `ReplicateContainerCommand.fromSources(containerID, sources)` to each target.

State and persistence: no local mutable or persistent state. Pending add ops and metrics are created by `ReplicationManager` when commands are sent.

Dependencies and integration: it depends on `PlacementPolicy`, SCM configuration, `ReplicationManager`, `RatisContainerReplicaCount`, `ReplicateContainerCommand`, and `NotLeaderException`. It is selected by `ReplicationManager.processUnderReplicatedContainer` for Ratis `MIS_REPLICATED` health results.

Risks: because `considerUnhealthy=true`, the count check may treat unhealthy replicas as part of the availability model for mis-replication gating. That is consistent with existing Ratis mis-replication behavior but should be reviewed if unhealthy placement repair semantics change. Push mode can throw if all sources are overloaded; unlike EC, Ratis does not collect multiple exceptions because it sends per target.

Test signals: `TestRatisMisReplicationHandler` and `TestMisReplicationHandler` verify type validation, no-op conditions, placement target count, push/pull command construction, and partial target exception behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/RatisMisReplicationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/RatisOverReplicationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/RatisOverReplicationHandler.java

Purpose: `RatisOverReplicationHandler` removes excess Ratis replicas while preserving enough matching replicas, unique origins for non-closed containers, and placement-policy quality.

Important APIs and behavior: `processAndSendCommands` filters replicas to healthy datanodes, builds a `RatisContainerReplicaCount` with unhealthy considered, verifies over-replication, builds eligible delete candidates, computes excess redundancy, and sends delete commands. `getEligibleReplicas` sorts candidates deterministically, removes non-`IN_SERVICE` and pending-delete replicas, and for non-`CLOSED` containers saves one replica per unique origin. `createCommands` deletes mismatched-state replicas before deleting otherwise healthy excess replicas.

Control flow: after mismatched replicas are targeted, the handler removes them from the candidate list and performs placement-aware deletion. It computes original placement status and only deletes a replica if `isPlacementStatusActuallyEqualAfterRemove` says removing it does not worsen placement, or preserves the same placement count when already mis-replicated. Even failed throttled delete attempts for selected replicas decrement local excess to keep deterministic selection and avoid deleting extra healthy replicas later.

State and persistence: no handler persistence. Delete command scheduling and pending ops are handled by `ReplicationManager`. Local `replicaSet` models deletions already selected in the current pass.

Dependencies and integration: depends on `AbstractOverReplicationHandler`, `PlacementPolicy`, `ReplicationManager`, `ReplicationManagerUtil.findNonUniqueDeleteCandidates`, `NodeStatus`, and Ratis count logic. `ReplicationManager.processOverReplicatedContainer` selects it for ordinary Ratis over-replication.

Risks: treating failed mismatched deletes as locally removed is deliberate but can leave actual excess until retry. `allUnhealthy` sorting by sequence ID only applies when healthy count is zero, so mixed unhealthy and healthy cases use hash ordering after mismatched preference. Placement equality checks are central to avoiding a fix that creates mis-replication.

Test signals: `TestRatisOverReplicationHandler` covers healthy filtering, pending deletes, unique-origin preservation, mismatched replica deletion preference, placement-aware deletion, all-unhealthy sorting, and overloaded delete exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/RatisOverReplicationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/RatisUnderReplicationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/RatisUnderReplicationHandler.java

Purpose: `RatisUnderReplicationHandler` creates additional replicas for under-replicated Ratis containers. It supports normal healthy-source replication, only-unhealthy recovery, vulnerable unhealthy quasi-closed replicas, and target-unblocking by deleting unhealthy replicas when placement cannot find a target.

Important APIs and behavior: `processAndSendCommands` skips empty `QUASI_CLOSED` containers, builds count objects with and without unhealthy replicas, handles `UnderReplicatedHealthResult.hasVulnerableUnhealthy`, verifies real under-replication after pending adds, selects sources, selects placement targets, sends push or pull replication commands, and throws `InsufficientDatanodesException` on partial target results.

Control flow: `verifyUnderReplication` returns null for already sufficient, pending-add sufficient, or unrecoverable containers. It chooses the count excluding unhealthy replicas when any healthy replicas exist, otherwise the count including unhealthy replicas. `getSources` prefers `CLOSED` replicas, allows `QUASI_CLOSED` when no closed replicas exist or the container is quasi-closed, allows `UNHEALTHY` only when no healthy replicas exist, filters to healthy datanodes not pending delete, and keeps only replicas at the maximum sequence ID. Vulnerable unhealthy handling replicates each vulnerable source independently and updates used nodes after success.

State and persistence: local state is per-call only. `sendReplicationCommands` uses `ReplicationManager` to schedule pending adds and metrics. `removeUnhealthyReplicaIfPossible` may send an unthrottled delete command to free a target when placement is blocked.

Dependencies and integration: depends on Ratis placement policy, SCM config, `ReplicationManagerUtil`, `RatisContainerReplicaCount`, `ReplicationManager`, `ReplicateContainerCommand`, and metrics. `ReplicationManager` selects it for ordinary Ratis under-replication.

Risks: max-sequence filtering prevents stale copy propagation but can eliminate otherwise available sources. Vulnerable unhealthy replication shuffles sources, which improves fairness but makes exact command order nondeterministic. Deleting an unhealthy replica to unblock placement must respect pending deletes and unique-origin logic in `ReplicationManagerUtil.selectUnhealthyReplicaForDelete`.

Test signals: `TestRatisUnderReplicationHandler` covers source-state selection, max sequence ID, only-unhealthy recovery, vulnerable unhealthy replicas, pending adds, placement failures, delete-unblock behavior, push/pull command generation, and partial replication metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/RatisUnderReplicationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationManager.java

Purpose: `ReplicationManager` is the SCM service that continuously evaluates container replication health and dispatches repair commands for closed and quasi-closed containers. It owns the monitor thread, under/over queue processors, health-check chain, command throttling, pending-op scheduling, metrics, and service readiness gating.

Important APIs and behavior: construction wires EC and Ratis health checks and handlers, quasi-closed stuck handlers, queue processors, metrics, and the health-check chain. Public APIs include lifecycle methods `start`, `stop`, `shouldRun`, `notifyStatusChanged`, `processAll`, read-only `checkContainerStatus`, health lookup `getContainerReplicationHealth`, command methods for close/delete/replicate/reconstruct, pending-op access, replica-count construction, node-status lookup, and node-state wakeup `notifyNodeStateChange`.

Control flow: `run` loops while `running`, calling `processAll` then waiting for the configured interval. `processAll` obtains all containers, builds a fresh report and queue, processes each container through the health-check chain, then atomically swaps `replicationQueue`. Separate `UnderReplicatedProcessor` and `OverReplicatedProcessor` threads drain queues and call `processUnderReplicatedContainer` or `processOverReplicatedContainer`, which choose EC, Ratis, mis-replication, or quasi-closed stuck handlers. `processContainer` synchronizes on each `ContainerInfo`, skips suppressed containers, builds `ContainerCheckRequest`, runs the chain, and writes final health state back to the container object.

State and persistence: durable state is external: `ContainerManager` stores containers/replicas, `NodeManager` queues datanode commands, and `ContainerReplicaPendingOps` records pending adds/deletes with deadlines. Internal state includes service status, excluded overloaded nodes, queue snapshot, metrics, monitor/processor threads, and config. `opCompleted` retries timed-out delete commands with a fresh deadline unless leadership changed.

Dependencies and integration: it integrates SCM context and leadership, event publisher, placement policies, node manager, container manager, replication server config, token generation, metrics, health handlers, and Ozone command types. It implements `SCMService` and `ContainerReplicaPendingOpsSubscriber`.

Risks: thread coordination is central: service readiness, queue replacement, pending-op clearing on leadership transition, and `notifyNodeStateChange` wakeups must avoid duplicate work and stale commands. Command throttling uses per-datanode counts and an excluded-node map; reconstruction commands have weighted cost. Push versus pull replication changes which datanode receives the command and which target is recorded in pending ops. `processContainer` mutates container health state after the chain, so read-only checks must use `MonitoringReplicationQueue` and handler read-only guards to avoid side effects.

Test signals: `TestReplicationManager`, `TestReplicationManagerScenarios`, `TestReplicationManagerEventHandler`, processor tests, handler tests, and `TestContainerReplicaPendingOps` cover monitor processing, command scheduling, pending ops, leadership/safe-mode gating, throttling, node-state wakeups, health reports, and EC/Ratis routing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationManagerEventHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationManagerEventHandler.java

Purpose: `ReplicationManagerEventHandler` handles datanode-related events by waking `ReplicationManager` when a node state change may require a new replication scan.

Important APIs and behavior: it implements `EventHandler<DatanodeDetails>`. The constructor stores a `ReplicationManager` and `SCMContext`. `onMessage` returns immediately unless the SCM is leader-ready and not in safe mode, logs the datanode event at debug level, and calls `replicationManager.notifyNodeStateChange()`.

Control flow: this is a guard-and-forward handler. It deliberately mirrors `ReplicationManager` readiness conditions so events do not wake or mutate replication state while SCM cannot safely act.

State and persistence: the handler has only final references to collaborators. It persists no state. Wakeup behavior is controlled by `ReplicationManager.notifyNodeStateChange`, which checks running/service status, monitor thread state, and queue emptiness.

Dependencies and integration: it depends on the Ozone event framework (`EventHandler`, `EventPublisher`), `DatanodeDetails`, `SCMContext`, and `ReplicationManager`. It is intended to be registered for node state events.

Risks: events received while safe mode is active or leadership is not ready are dropped rather than queued; this is acceptable because the monitor will scan later after readiness. If the replication queue is not empty, `ReplicationManager` will decline to wake the monitor to avoid repeated queue replacement during active work.

Test signals: `TestReplicationManagerEventHandler` covers notification forwarding and suppression when SCM is not leader-ready or is in safe mode. `TestDatanodeCommandCountUpdatedHandler` and `ReplicationManager` tests cover related event-driven wakeup behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationManagerEventHandler.java -->
