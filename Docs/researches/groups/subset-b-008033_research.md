# subset-b-008033 Research

Grouped source research for Apache Ozone SCM replication health handling, container report validation, in-memory container state indexes, SCM event declarations, and SCM HA support utilities. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationManagerMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationManagerMetrics.java

## Purpose

`ReplicationManagerMetrics` is the Hadoop metrics source for SCM ReplicationManager. It exposes inflight add/delete gauges, queue depths, lifecycle and health-state gauges from `ReplicationManagerReport`, and counters/rates for Ratis and EC replication, deletion, reconstruction, partial replication, skipped inflight operations, and deferred commands.

## Important APIs, Types, and Functions

The class implements `MetricsSource`. Key APIs are `create`, `unRegister`, `getMetrics`, the `incr*` counter methods, `addReplicationTime`, `addDeletionTime`, and gauge getters such as `getInflightReplication`, `getEcReplication`, and `getPendingReplicationLimitReachedTotal`. It builds `MetricsInfo` maps for every `LifeCycleState` and `ContainerHealthState`.

## Control Flow

`create` registers a singleton source with `DefaultMetricsSystem`. `getMetrics` constructs a metrics record, reads live queue and pending-op state from `ReplicationManager`, snapshots counters, and publishes dynamic report gauges. Mutator methods are called by replication command scheduling, timeout handling, pending-op completion, EC reconstruction paths, and throttling paths.

## State and Persistence Behavior

State is in-memory metrics registry state: `MutableCounterLong` and `MutableRate` fields plus live references to `ReplicationManager`. It does not persist values across SCM restart. Gauge values are derived at collection time from pending ops, queues, and the latest replication-manager report.

## Dependencies and Integration Points

It integrates with Hadoop metrics2, `ReplicationManager`, `ContainerReplicaPendingOps`, `ReplicationQueue`, `ReplicationManagerReport`, `ContainerHealthState`, `LifeCycleState`, and replication types. Dashboards and tests consume the metric names, so names are effectively a monitoring contract.

## Risks and Edge Cases

Metrics are only as accurate as the callers incrementing them; missing increments silently hide work. Dynamic lifecycle/health metrics expand if enums expand, which is useful but may surprise dashboards. The `getMetrics` body snapshots `ecReplicasDeletedTotal` twice and omits several byte/rate snapshots, which is a possible observability gap if not intentional.

## Test Signals

Useful tests assert registration idempotence, counter increments after command scheduling and timeout paths, inflight gauges matching pending-op counts split by Ratis/EC, queue gauges matching `ReplicationQueue`, lifecycle and health gauges matching sampled reports, and unregister cleanup from the metrics system.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationManagerMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationManagerUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationManagerUtil.java

## Purpose

`ReplicationManagerUtil` holds shared policy helpers for target selection, used/excluded datanode derivation, scheduled-capacity exclusion, and deterministic unhealthy replica deletion choices. It centralizes rules used by under/over/mis-replication handlers so Ratis and EC processing choose compatible nodes and preserve safety invariants.

## Important APIs, Types, and Functions

Major APIs are `getTargetDatanodes`, `getExcludedAndUsedNodes`, `selectUnhealthyReplicasForDelete`, `selectUnhealthyReplicaForDelete`, and package-visible `findNonUniqueDeleteCandidates`. `ExcludedAndUsedNodes` returns placement inputs. The code depends on `PlacementPolicy`, `ContainerInfo`, `ContainerReplica`, `ContainerReplicaOp`, `ReplicationManager`, `NodeStatus`, and `NodeManager`.

## Control Flow

Target selection calculates required space from the greater of used bytes and default container size, calls the placement policy, and backs off the requested node count until success or zero. Used/excluded derivation walks replicas, treats unhealthy, decommissioning, maintenance-dead, and pending delete/add nodes differently, then excludes nodes whose remaining space minus spare and recent scheduled size cannot hold the container. Unhealthy deletion selection first refuses unsafe cases, sorts candidates by sequence ID, and for quasi-closed containers only returns candidates whose origin IDs are not uniquely represented by valid replicas.

## State and Persistence Behavior

The class owns no persistent state. It reads transient pending-op scheduled-size maps, node status/statistics, container metadata, and replica sets. Deterministic ordering matters because leaders can change; deletion choices should remain stable across SCMs when inputs match.

## Dependencies and Integration Points

It integrates with placement policy validation/selection, pending replica ops, SCM node metrics, maintenance/decommission state, and `ReplicationManager.compareState`. It is called by replication handlers that issue commands and by quasi-closed unhealthy cleanup logic.

## Risks and Edge Cases

The logic deliberately avoids deleting when there are pending deletes, when too few replicas remain, or when no replica matches container state. Node-not-found and null node-status paths bias toward exclusion or no deletion. Scheduled-size exclusion only considers entries newer than the event timeout, so stale pending sizes are ignored. Origin uniqueness is subtle and protects data in quasi-closed containers.

## Test Signals

Tests should cover placement backoff, detailed used/excluded classification for unhealthy/decommission/maintenance/dead/pending ops, full-node exclusion with scheduled sizes, closed versus quasi-closed deletion candidate ordering, non-unique origin preservation, node-not-found fallbacks, and deterministic behavior under reordered sets where sorting is expected.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationManagerUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationQueue.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationQueue.java

## Purpose

`ReplicationQueue` encapsulates ReplicationManager's under-replicated and over-replicated work queues. It gives processors a small API for enqueue/dequeue and size inspection while preserving prioritization for under-replicated containers.

## Important APIs, Types, and Functions

Public methods are overloaded `enqueue`, `dequeueUnderReplicatedContainer`, `dequeueOverReplicatedContainer`, `underReplicatedQueueSize`, `overReplicatedQueueSize`, and `isEmpty`. The under queue stores `UnderReplicatedHealthResult`; the over queue stores `OverReplicatedHealthResult`.

## Control Flow

Under-replicated results go into a synchronized priority queue ordered by weighted redundancy and then requeue count. Re-enqueue increments the result's requeue count, reducing its priority after a failed processing attempt. Over-replicated results use a synchronized FIFO `LinkedList`.

## State and Persistence Behavior

All state is in-memory queue state rebuilt periodically by ReplicationManager health scans. Duplicate entries can occur if a result is requeued while the queue is refreshed; later processing observes pending ops and naturally discards no-op duplicates.

## Dependencies and Integration Points

It integrates with health check handlers that enqueue results and with `UnderReplicatedProcessor`/over-replicated processors that dequeue and command datanodes. Metrics read queue sizes through `ReplicationManagerMetrics`.

## Risks and Edge Cases

The synchronized queue wrapper protects single queue operations, not compound workflows. Requeue count mutates the health result object. Duplicate entries are accepted by design, relying on periodic refresh and idempotent replication processing.

## Test Signals

Tests should assert under-replication priority ordering by weighted redundancy then requeue count, requeue-count increment on enqueue, FIFO behavior for over-replicated results, null dequeue on empty queues, and size/is-empty consistency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationQueue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/UnderReplicatedProcessor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/UnderReplicatedProcessor.java

## Purpose

`UnderReplicatedProcessor` specializes `UnhealthyReplicationProcessor` for under-replicated health results. It drains the under-replicated queue and delegates repair command generation to `ReplicationManager.processUnderReplicatedContainer`.

## Important APIs, Types, and Functions

It overrides `dequeueHealthResultFromQueue`, `requeueHealthResult`, `inflightOperationLimitReached`, and `sendDatanodeCommands`. The processed type is `ContainerHealthResult.UnderReplicatedHealthResult`.

## Control Flow

The base processor loop calls this subclass to poll `ReplicationQueue.dequeueUnderReplicatedContainer`. If processing fails, the result is requeued through `ReplicationQueue.enqueue`, which increments retry priority state. The inflight limit check compares `ReplicationManager.getInflightReplicationCount` to the configured pending-op limit.

## State and Persistence Behavior

The class owns no durable state. It relies on the queue and pending replica ops for transient coordination. Actual repair work is persisted only indirectly through commands and pending-op tracking maintained by ReplicationManager.

## Dependencies and Integration Points

It integrates with `ReplicationManager`, `ReplicationQueue`, metrics triggered by the base processor, and datanode command generation in under-replication handlers.

## Risks and Edge Cases

If the cluster-level inflight limit is reached, the processor stops the current pass without draining remaining queue entries. Requeued failures lose priority via requeue count but can still duplicate with queue rebuilds.

## Test Signals

Tests should verify correct queue method usage, requeue on exception or overload, stopping when replication inflight limit is reached, and delegation count/exception propagation from `processUnderReplicatedContainer`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/UnderReplicatedProcessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/UnhealthyReplicationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/UnhealthyReplicationHandler.java

## Purpose

`UnhealthyReplicationHandler` is the command-generation interface for handlers that repair unhealthy, under-replicated, over-replicated, or mis-replicated containers after health checks classify them.

## Important APIs, Types, and Functions

The single method `processAndSendCommands` receives available replicas, pending ops, a `ContainerHealthResult`, and remaining maintenance redundancy, then returns the number of commands sent. It may throw `IOException`.

## Control Flow

Implementations inspect current replicas and inflight operations, compute required add/delete/reconstruct actions, send SCM commands to selected datanodes, and update pending-op tracking. This interface has no implementation flow itself.

## State and Persistence Behavior

It owns no state. Implementations affect transient pending ops and eventually persistent SCM/container state through command completion reports and container metadata updates.

## Dependencies and Integration Points

It links health classification output to concrete datanode commands. Implementations depend on `ContainerReplica`, `ContainerReplicaOp`, `ContainerHealthResult`, placement policy, node manager state, and ReplicationManager command APIs.

## Risks and Edge Cases

Callers assume command counts reflect actual scheduled work. Implementations must account for pending adds/deletes, maintenance redundancy, overloaded targets, and read-after-classification drift in replica sets.

## Test Signals

Interface-level signals are implementation tests asserting command counts, pending-op mutations, handling of maintenance/decommission replicas, and expected exceptions for placement or overloaded-target failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/UnhealthyReplicationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/UnhealthyReplicationProcessor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/UnhealthyReplicationProcessor.java

## Purpose

`UnhealthyReplicationProcessor` is the reusable runnable loop for queue-driven replication repair processors. It drains a specific health-result queue, enforces inflight limits, synchronizes per-container processing, requeues failures, and sleeps between passes.

## Important APIs, Types, and Functions

Subclasses implement `dequeueHealthResultFromQueue`, `requeueHealthResult`, `inflightOperationLimitReached`, and `sendDatanodeCommands`. Public/visible methods are `processAll`, `run`, and testing-only `runImmediately`.

## Control Flow

`processAll` caches the current inflight limit, repeatedly checks `ReplicationManager.shouldRun`, stops when limits are reached or the queue is empty, and processes each result under `synchronized(containerInfo)`. `CommandTargetOverloadedException` and other exceptions are counted and requeued after the pass. `run` loops until interrupted, optionally processes the queue, waits for the configured interval, and supports immediate wakeup.

## State and Persistence Behavior

State is transient: `runImmediately`, the interval supplier, counters local to a pass, and failed results. No direct persistence occurs, but `sendDatanodeCommands` can update pending ops and trigger command side effects.

## Dependencies and Integration Points

It integrates with `ReplicationManager`, `ReplicationQueue`, `ContainerHealthResult`, metrics for pending limit reached, and processor subclasses for under/over/mis-replication.

## Risks and Edge Cases

The loop handles broad exceptions to keep the processor alive, but repeated failures can churn requeue counts. The inflight limit is sampled once per pass, so fast topology changes are seen on the next pass. Synchronizing on mutable `ContainerInfo` requires all competing paths to honor the same lock.

## Test Signals

Tests should cover draining, failed-result requeue, overload requeue, pending-limit short circuit and metric increment, no work when `shouldRun` is false, container-level synchronization, interrupt shutdown, and `runImmediately` wake behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/UnhealthyReplicationProcessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/AbstractCheck.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/AbstractCheck.java

## Purpose

`AbstractCheck` is the base class for ReplicationManager container health checks. It implements a simple chain-of-responsibility so each handler can either handle a container or pass it to the next handler.

## Important APIs, Types, and Functions

It implements `HealthCheck.handleChain` and `HealthCheck.addNext`, stores one successor `HealthCheck`, and leaves `handle(ContainerCheckRequest)` abstract for concrete checks.

## Control Flow

`handleChain` calls the current handler's `handle`. If it returns `false` and a successor exists, it invokes the successor's `handleChain`; otherwise it returns the current result. `addNext` replaces the successor and returns the added handler to support fluent chain construction.

## State and Persistence Behavior

State is an in-memory successor pointer. There is no persistence and no synchronization, so chains are expected to be built during initialization.

## Dependencies and Integration Points

Concrete handlers in the `health` package extend this class and receive `ContainerCheckRequest`, which carries container info, replicas, pending ops, reports, queue, and read-only mode.

## Risks and Edge Cases

Handler return values are semantically important: some handlers send commands but return `false` so later checks continue. Replacing the successor after startup could alter chain behavior without thread safety.

## Test Signals

Tests should verify pass-through on `false`, stop on `true`, fluent chaining order, and concrete handlers that intentionally return `false` after side effects.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/AbstractCheck.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ClosedWithUnhealthyReplicasHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ClosedWithUnhealthyReplicasHandler.java

## Purpose

This handler deletes extra unhealthy replicas from closed EC containers after normal EC under/over checks have determined the container is otherwise sufficiently replicated by closed indexes.

## Important APIs, Types, and Functions

The main method is `handle`. The helper `sendDeleteCommand` calls `ReplicationManager.sendDeleteCommand(container, replicaIndex, datanode, true)`. It uses EC `ReplicationType`, `LifeCycleState.CLOSED`, replica states, and `ContainerHealthState.UNHEALTHY_OVER_REPLICATED`.

## Control Flow

The handler ignores non-EC and non-closed containers. It gathers indexes with closed replicas, scans unhealthy replicas, and refuses to handle if an unhealthy index has no closed counterpart because that index is actually under-replicated. Otherwise it samples the report and, unless read-only, sends force delete commands for unhealthy replicas.

## State and Persistence Behavior

It owns no state except the ReplicationManager reference. Side effects are pending delete commands and report samples. Persistent metadata changes happen later when delete commands complete.

## Dependencies and Integration Points

It integrates with EC health checks, ReplicationManager command sending, `NotLeaderException` handling, and report classification. It is intended to run after under/over replication detection so it does not mask missing EC indexes.

## Risks and Edge Cases

Incorrect chain order could delete an unhealthy replica when no healthy index exists. Read-only mode records classification without commands. Not-leader failures are logged and not retried here.

## Test Signals

Tests should cover closed EC with duplicate unhealthy index deletion, unhealthy index without closed counterpart returning false, non-EC/non-closed pass-through, read-only no command, report increment, and not-leader logging behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ClosedWithUnhealthyReplicasHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ClosingContainerHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ClosingContainerHandler.java

## Purpose

`ClosingContainerHandler` handles SCM containers in `CLOSING` state. It sends close commands to non-unhealthy replicas, transitions all-unhealthy closing containers, and eventually closes empty containers that never acquired replicas.

## Important APIs, Types, and Functions

The main method is `handle`; `hasWaitTimeElapsed` computes the empty-closing grace period as replication-manager interval times five. It uses `sendCloseContainerReplicaCommand`, `updateContainerState`, `LifeCycleEvent.QUASI_CLOSE`, `CLOSE`, and `ContainerHealthState.MISSING`.

## Control Flow

Non-closing containers pass through. Empty replica sets are sampled as missing. Read-only mode returns after classification. For each non-unhealthy replica, it sends a close command, force-closing non-Ratis replicas. If all replicas are unhealthy, Ratis moves to quasi-closed and EC moves to closed. If there are no replicas, no keys, and the wait time has elapsed, it closes the container.

## State and Persistence Behavior

It uses the container's `stateEnterTime` and a `Clock` to determine elapsed time. Command sends are transient; `updateContainerState` changes SCM container metadata through the normal state machine.

## Dependencies and Integration Points

It integrates with ReplicationManager, container lifecycle events, safe/read-only scanning, and the broader health chain that should not run replication repairs on still-closing containers.

## Risks and Edge Cases

The all-unhealthy branch treats EC differently from Ratis. Empty containers require both no replicas and zero key count to avoid premature close. Clock or interval misconfiguration can delay cleanup or close too early.

## Test Signals

Tests should assert close command issuance for non-unhealthy replicas, no command for unhealthy replicas, all-unhealthy Ratis/EC transitions, read-only no mutation, empty missing sampling, and grace-period close for empty no-replica containers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ClosingContainerHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/DeletingContainerHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/DeletingContainerHandler.java

## Purpose

`DeletingContainerHandler` handles containers in `DELETING` or `DELETED` state. It marks replica-free deleting containers for cleanup and resends delete commands for empty replicas that are not already covered by pending delete ops.

## Important APIs, Types, and Functions

The main method is `handle`. It uses `ReplicationManager.updateContainerState`, `ReplicationManager.sendDeleteCommand`, `LifeCycleEvent.CLEANUP`, pending-op type `DELETE`, `ContainerReplica.isEmpty`, and `NotLeaderException`.

## Control Flow

Already deleted containers return handled. Non-deleting containers pass through. Read-only deleting containers return handled without mutation. If no replicas exist, the handler emits the cleanup lifecycle event. Otherwise it builds the pending-delete datanode set and sends delete commands for empty replicas not already pending.

## State and Persistence Behavior

It changes persistent SCM lifecycle state through `updateContainerState` and schedules transient delete commands. Replica deletion completion later removes container replica state.

## Dependencies and Integration Points

It integrates with pending ops, datanode command sending, lifecycle state manager, and the health chain to prevent normal replication repairs for deleting containers.

## Risks and Edge Cases

Only empty replicas are resent delete commands, so non-empty replicas in deleting state are not force-deleted by this handler. Not-leader failures are logged. Duplicate pending deletes are avoided by datanode matching.

## Test Signals

Tests should cover deleted pass-through, deleting no-replica cleanup, read-only no mutation, resend for empty replica without pending delete, suppression when pending delete exists, non-empty replica skip, and not-leader handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/DeletingContainerHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ECMisReplicationCheckHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ECMisReplicationCheckHandler.java

## Purpose

`ECMisReplicationCheckHandler` detects EC containers whose replica datanodes do not satisfy placement policy even though the container is not under/over replicated. It queues mis-replication repairs when pending ops will not already fix placement.

## Important APIs, Types, and Functions

Key methods are `handle`, `checkMisReplication`, and private `getPlacementStatus`. It uses `PlacementPolicy.validateContainerPlacement`, `ContainerHealthResult.MisReplicatedHealthResult`, and `ContainerHealthState.MIS_REPLICATED`.

## Control Flow

The handler ignores non-EC containers. It validates placement from current replica datanodes. If placement fails, it revalidates after applying pending add/delete ops to a datanode set. It reports mis-replication and enqueues only when pending ops do not satisfy placement.

## State and Persistence Behavior

It owns no state. It samples the report and enqueues transient repair work. Placement state is computed from current replicas and pending ops.

## Dependencies and Integration Points

It integrates with the EC health chain after replication-count checks, placement policy, ReplicationManager queue, and mis-replication repair handlers.

## Risks and Edge Cases

It uses datanode uniqueness, not EC index counts, so it assumes earlier EC replication checks handled missing/excess indexes. Pending-op application removes/introduces datanodes without validating command success.

## Test Signals

Tests should verify non-EC pass-through, placement satisfied pass-through, current placement failure with pending add fix not queued, pending delete worsening placement, report increment, queued `MisReplicatedHealthResult`, and reason propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ECMisReplicationCheckHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ECReplicationCheckHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ECReplicationCheckHandler.java

## Purpose

`ECReplicationCheckHandler` classifies EC containers as healthy, under-replicated, over-replicated, missing, unhealthy, or combinations involving offline indexes. It enqueues repair work when pending ops are insufficient.

## Important APIs, Types, and Functions

Important methods are `handle` and `checkHealth`. It constructs `ECContainerReplicaCount`, reads `ECReplicationConfig`, emits `UnderReplicatedHealthResult` or `OverReplicatedHealthResult`, and samples `ContainerHealthState` variants including `MISSING_UNDER_REPLICATED`, `UNHEALTHY_UNDER_REPLICATED`, `MISSING`, `UNHEALTHY`, `UNDER_REPLICATED`, and `OVER_REPLICATED`.

## Control Flow

The handler ignores non-EC containers. `checkHealth` first tests sufficient replication without pending ops, computes missing indexes and remaining redundancy, distinguishes true missing from out-of-service-only cases, sets offline-index and missing flags, and returns under health. It then checks over-replication. `handle` maps the result to report states and queues only if pending operations do not already repair the relevant deficit.

## State and Persistence Behavior

No direct persistence occurs. State changes are report samples and queue entries. The calculation includes pending ops and maintenance redundancy from `ContainerCheckRequest`.

## Dependencies and Integration Points

It integrates with `ECContainerReplicaCount`, EC replication config, decommission/maintenance monitors that rely on offline-index state, ReplicationQueue, and later EC under/over replication handlers.

## Risks and Edge Cases

EC containers can be both unrecoverable and blocked by offline indexes; this handler intentionally reports both through combined states. Pending-op checks differ for offline indexes versus missing indexes. Incorrect `remainingRedundancy` can affect reconstruction urgency.

## Test Signals

Tests should cover missing indexes, unrecoverable EC sets, offline-only under replication, pending-add fixes, over-replicated indexes, maintenance redundancy, missing versus unhealthy classification, and queue suppression when pending ops are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ECReplicationCheckHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/EmptyContainerHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/EmptyContainerHandler.java

## Purpose

`EmptyContainerHandler` deletes closed or quasi-closed containers whose replicas are empty. It prevents empty containers from being treated as missing or under-replicated and handles quasi-closed empty deletion carefully to preserve resurrection sequence semantics.

## Important APIs, Types, and Functions

Important methods are `handle`, `isContainerEmptyAndClosed`, `isContainerEmptyAndQuasiClosed`, and `deleteContainerReplicas`. It uses `ContainerHealthState.EMPTY`, `LifeCycleEvent.DELETE`, `sendDeleteCommand`, `ContainerReplica.isEmpty`, and sequence-id updates.

## Control Flow

For closed containers, all replicas must be closed and empty; delete commands are sent and the container moves to deleting, except Ratis closed containers whose replica sequence IDs do not match the container sequence ID. For quasi-closed containers, all replicas must be empty regardless of state; the container BCSID is raised to the max replica BCSID if needed, SCM state moves to deleting, and delete commands are sent only to closed or quasi-closed replicas. Closed empty containers with no replicas are reported as empty but not deleted.

## State and Persistence Behavior

It mutates container sequence ID in memory before lifecycle update when quasi-closed replicas have a higher BCSID. It schedules delete commands and updates persistent lifecycle state through ReplicationManager. It does not inspect used bytes because orphaned chunks can make it misleading.

## Dependencies and Integration Points

It integrates with ReplicationManager lifecycle updates, delete commands, health reports, and resurrection/stale replica logic that depends on BCSID.

## Risks and Edge Cases

Deleting empty quasi-closed containers before all replicas reach stable states can leave open/closing replicas for a later retry. Closed Ratis sequence mismatch suppresses state transition. Preconditions assert replicas are empty before deletion.

## Test Signals

Tests should verify closed-empty deletion, quasi-closed empty deletion and BCSID update, skip of unstable replica delete commands, no-replica closed empty report-only path, Ratis sequence mismatch suppression, read-only no mutation, and report sampling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/EmptyContainerHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/HealthCheck.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/HealthCheck.java

## Purpose

`HealthCheck` defines the contract for ReplicationManager container health check handlers and their chain-of-responsibility execution.

## Important APIs, Types, and Functions

The interface declares `handle`, `handleChain`, and `addNext`, all using `ContainerCheckRequest`.

## Control Flow

Concrete handlers implement direct classification and side effects in `handle`. `handleChain` is implemented by `AbstractCheck` to call handlers in sequence until one returns handled or the chain ends. `addNext` wires the chain.

## State and Persistence Behavior

The interface owns no state. Implementations may sample reports, enqueue health results, send commands, or update container lifecycle state.

## Dependencies and Integration Points

It is the common type for all health handlers in `org.apache.hadoop.hdds.scm.container.replication.health`, used during ReplicationManager scans.

## Risks and Edge Cases

Handler return semantics are not simply "did anything": some handlers return `false` after command side effects to allow later checks. Read-only behavior is implementation-specific but expected for report-only scans.

## Test Signals

Tests should focus on concrete chain ordering and verify that each handler's return value either stops or continues processing as intended.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/HealthCheck.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/MismatchedReplicasHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/MismatchedReplicasHandler.java

## Purpose

`MismatchedReplicasHandler` sends close commands for replicas whose state lags the SCM container state, while deliberately allowing later health checks to continue processing under/over/mis-replication.

## Important APIs, Types, and Functions

Main methods are `handle` and private `getTransitionState`. It calls `ReplicationManager.sendCloseContainerReplicaCommand` and examines `LifeCycleState.CLOSED`, `QUASI_CLOSED`, replica states `OPEN`, `CLOSING`, `QUASI_CLOSED`, and replication type.

## Control Flow

Read-only requests pass through. Non-closed/non-quasi-closed containers pass through. For open or closing replicas, Ratis targets quasi-closed and EC/non-Ratis targets closed. For quasi-closed replicas of closed containers, it force closes only when sequence IDs match. The handler always returns `false`.

## State and Persistence Behavior

No direct persistent update occurs. It sends commands whose completion later changes replica reports and container state. It does not mutate the report.

## Dependencies and Integration Points

It integrates with the health chain before replication-count handlers, allowing replica state convergence before over-replication cleanup. It relies on ReplicationManager's close-command API.

## Risks and Edge Cases

Always returning `false` means later handlers can also act on the same scan. Sequence-ID equality protects closed container force-close safety. Read-only scans skip command sending entirely.

## Test Signals

Tests should assert commands for open/closing replicas, force close for matching quasi-closed closed replicas, no command for mismatched sequence IDs, no mutation in read-only mode, non-relevant states pass through, and chain continuation after side effects.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/MismatchedReplicasHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/OpenContainerHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/OpenContainerHandler.java

## Purpose

`OpenContainerHandler` handles open containers by closing those that have no healthy pipeline or whose replicas no longer match the open state. It stops further ReplicationManager processing for open containers.

## Important APIs, Types, and Functions

The main methods are `handle` and private `isOpenContainerHealthy`. It uses `ReplicationManager.hasHealthyPipeline`, `sendCloseContainerEvent`, `ReplicationManager.compareState`, and report states `OPEN_WITHOUT_PIPELINE` and `OPEN_UNHEALTHY`.

## Control Flow

Only `OPEN` containers are handled. The handler first checks for a healthy pipeline; if absent it closes without testing replica health. Otherwise it checks all replicas match the container state. Unhealthy open containers are sampled and, unless read-only, a close-container event is sent. All open containers return handled to stop the chain.

## State and Persistence Behavior

It owns no state. Side effects are report sampling and a close event that later drives lifecycle transition and datanode commands.

## Dependencies and Integration Points

It integrates with pipeline health, event-driven close handling, health reports, and the chain ordering that should keep open containers out of closed-container replication repair logic.

## Risks and Edge Cases

An empty replica set is considered healthy by `allMatch` if a pipeline exists, so no-pipeline is the primary empty-open protection. Read-only scans still classify but do not close.

## Test Signals

Tests should cover open-without-pipeline close event, open unhealthy replica close event, healthy open no event, read-only no event, non-open pass-through, and chain stop for any open container.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/OpenContainerHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/QuasiClosedContainerHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/QuasiClosedContainerHandler.java

## Purpose

`QuasiClosedContainerHandler` handles Ratis containers in `QUASI_CLOSED` state. It force-closes safe candidates and reports stuck quasi-closed containers that cannot be force-closed without risking data loss.

## Important APIs, Types, and Functions

Important methods are `handle`, static `isQuasiClosedStuck`, private static `canForceCloseContainer`, and `forceCloseContainer`. It sends close commands through `ReplicationManager.sendCloseContainerReplicaCommand` and reports `ContainerHealthState.QUASI_CLOSED_STUCK`.

## Control Flow

The handler ignores non-Ratis and non-quasi-closed containers. `canForceCloseContainer` requires at least one quasi-closed replica, the max quasi-closed sequence ID to be at least the max unhealthy sequence ID, and enough unique origins among quasi-closed or unhealthy replicas to meet the replication factor. When safe, it force-closes quasi-closed replicas with the highest sequence ID; otherwise it samples stuck state. It always returns `false`.

## State and Persistence Behavior

It owns no persistent state. Close commands eventually move replicas/container forward. Report sampling records stuck state without changing metadata.

## Dependencies and Integration Points

It integrates with Ratis replication checks, quasi-closed-stuck replication checks, origin-datanode tracking, sequence IDs, and ReplicationManager close command dispatch.

## Risks and Edge Cases

The safety rule intentionally leaves some containers stuck forever if unique origins are permanently lost. Including unhealthy origins prevents closing if an unhealthy replica may have newer data. Returning `false` permits replication health checks to run afterward.

## Test Signals

Tests should cover safe force close at highest BCSID, unsafe due to insufficient unique origins, unsafe due to unhealthy higher sequence ID, stuck report sampling, non-Ratis pass-through, read-only no command, and chain continuation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/QuasiClosedContainerHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/QuasiClosedStuckReplicationCheck.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/QuasiClosedStuckReplicationCheck.java

## Purpose

`QuasiClosedStuckReplicationCheck` applies special replication rules to quasi-closed Ratis containers that cannot be force-closed. It tries to preserve several copies of the highest-BCSID origin and fewer copies of other origins rather than applying ordinary Ratis replica-count rules.

## Important APIs, Types, and Functions

Important methods are static `shouldHandleAsQuasiClosedStuck`, `handle`, and private `hasEnoughOriginsWithOpen`. It uses `QuasiClosedStuckReplicaCount`, configuration values `getQuasiClosedStuckBestOriginCopies` and `getQuasiClosedStuckOtherOriginCopies`, and combined health states such as `QUASI_CLOSED_STUCK_UNDER_REPLICATED`.

## Control Flow

The static gate requires a quasi-closed container, force-close-stuck status, more than the single-origin normal case, and not enough open/quasi-closed origins waiting to close naturally. `handle` reports stuck-missing when no replicas exist. Otherwise it builds a configured replica counter, skips all-unhealthy cases, counts pending adds/deletes, reports under or over replication, and enqueues only if the corresponding pending operation type is absent.

## State and Persistence Behavior

It owns no state beyond configuration. It samples reports and enqueues transient repair work; persistent changes happen later via normal command processors.

## Dependencies and Integration Points

It integrates with `QuasiClosedContainerHandler`, `QuasiClosedStuckReplicaCount`, ReplicationQueue, and Ratis health handling, which explicitly defers when this special handler applies.

## Risks and Edge Cases

The static gate uses default copy counts for initial origin counting, while `handle` uses configured counts. Pending-op suppression is coarse by add/delete count, not target quality. All-unhealthy stuck containers are intentionally handled by another handler.

## Test Signals

Tests should cover the static gate, single-origin fallback to normal handler, open-origin suppression, missing no-replica report, under/over queueing without pending ops, queue suppression with pending ops, configured copy counts, and all-unhealthy pass-through.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/QuasiClosedStuckReplicationCheck.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/RatisReplicationCheckHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/RatisReplicationCheckHandler.java

## Purpose

`RatisReplicationCheckHandler` is the main health classifier for Ratis containers. It detects under-replication, over-replication, mis-replication, missing containers, and containers with excess unhealthy replicas while deferring special all-unhealthy and quasi-closed-stuck cases to other handlers.

## Important APIs, Types, and Functions

Important methods are `handle`, `checkHealth`, and private `getPlacementStatus`. It uses `RatisContainerReplicaCount`, `PlacementPolicy`, `ReplicationManagerUtil.selectUnhealthyReplicaForDelete`, `ContainerHealthResult` subclasses, and report states `MISSING`, `UNDER_REPLICATED`, `OVER_REPLICATED`, and `MIS_REPLICATED`.

## Control Flow

The handler ignores non-Ratis containers and quasi-closed-stuck containers. `checkHealth` first checks sufficient replication without counting unhealthy replicas; if insufficient it returns under health. It checks over-replication without unhealthy replicas, then over-replication while considering unhealthy replicas. For quasi-closed over-replication, it only reports over-replicated if a safely deletable unhealthy replica exists. Finally it validates placement policy after pending ops and returns unhealthy or healthy if no other issue exists. `handle` samples reports and enqueues only when pending ops are insufficient and safety flags allow.

## State and Persistence Behavior

It owns no persistent state. It reads replicas, pending ops, maintenance redundancy, and node status through ReplicationManager. It mutates report samples and replication queues only.

## Dependencies and Integration Points

It integrates with placement policy, ReplicationQueue, Ratis replica-count logic, ReplicationManager node status, quasi-closed stuck checks, and later under/over/mis-replication processors.

## Risks and Edge Cases

Counting unhealthy replicas differently for under versus over checks is intentional and subtle. A recoverable container with no healthy replicas is left for unhealthy replication checks. Mismatched replicas suppress over-replication queueing until close commands can converge state.

## Test Signals

Tests should cover under-replication without unhealthy counting, over-replication with and without unhealthy replicas, quasi-closed unique-origin preservation, missing/unrecoverable classification, pending-op queue suppression, mis-replication placement reasons, mismatched-replica queue suppression, and special stuck pass-through.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/RatisReplicationCheckHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/RatisUnhealthyReplicationCheckHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/RatisUnhealthyReplicationCheckHandler.java

## Purpose

`RatisUnhealthyReplicationCheckHandler` handles Ratis containers that have no healthy replicas but do have unhealthy or stale quasi-closed-style replicas. It maintains the expected replication factor of those unhealthy replicas instead of immediately declaring only missing.

## Important APIs, Types, and Functions

Important methods are `handle`, testing-visible `checkReplication(ContainerCheckRequest)`, private `getReplicaCount`, and private `checkReplication(RatisContainerReplicaCount)`. It reports `UNHEALTHY_UNDER_REPLICATED`, `UNHEALTHY_OVER_REPLICATED`, or `UNHEALTHY`.

## Control Flow

The handler ignores non-Ratis containers and containers with any healthy replica or no unhealthy replicas. It constructs `RatisContainerReplicaCount` with unhealthy replicas considered. It returns under health if insufficient, over health if excessive, or unhealthy if sufficiently replicated. Under/over results are reported and queued when pending ops do not already fix them.

## State and Persistence Behavior

It owns no state. It samples reports and enqueues repair results. Actual replication/delete commands are produced later by processors.

## Dependencies and Integration Points

It integrates with Ratis replica-count calculations, ReplicationQueue, and the health chain after the main Ratis replication check declines recoverable no-healthy-replica cases.

## Risks and Edge Cases

It returns `false` after reporting sufficiently replicated unhealthy containers, allowing later handlers to continue. Because all healthy replicas are absent, repair commands must avoid assuming a clean source unless downstream handlers explicitly support unhealthy replication.

## Test Signals

Tests should cover no healthy replicas under/over/sufficient cases, pending-op fix suppression, report state selection, queueing behavior, pass-through when healthy replicas exist, and pass-through when no unhealthy replicas exist.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/RatisUnhealthyReplicationCheckHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/VulnerableUnhealthyReplicasHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/VulnerableUnhealthyReplicasHandler.java

## Purpose

`VulnerableUnhealthyReplicasHandler` protects quasi-closed Ratis containers whose unhealthy replicas may contain unique or highest-sequence data. It queues under-replication work to copy such vulnerable replicas before they are lost.

## Important APIs, Types, and Functions

The main method is `handle`. It builds `RatisContainerReplicaCount` considering unhealthy replicas, calls `getVulnerableUnhealthyReplicas`, reports `UNHEALTHY_UNDER_REPLICATED`, and enqueues an `UnderReplicatedHealthResult` marked with `setHasVulnerableUnhealthy(true)`.

## Control Flow

The handler ignores non-Ratis and non-quasi-closed containers. It asks `ReplicationManager.getNodeStatus` for datanode health while calculating vulnerability. If vulnerable unhealthy replicas exist, it samples the report and, unless read-only, queues under-replication work that downstream handlers can interpret as vulnerable-unhealthy repair.

## State and Persistence Behavior

It owns no state. Node status and replica sets are read at scan time. Persistent effects occur only later if queued work produces copy commands and those commands complete.

## Dependencies and Integration Points

It integrates with `RatisContainerReplicaCount`, ReplicationManager node status, ReplicationQueue, and quasi-closed recovery logic.

## Risks and Edge Cases

Node-not-found is logged and treated as null status by the vulnerability calculation. Read-only scans report without queueing. Incorrect vulnerability detection can either lose rare data or create unnecessary copies.

## Test Signals

Tests should cover vulnerable unique-origin or high-sequence unhealthy replicas, no-vulnerability pass-through, node-not-found fallback, read-only queue suppression, report sampling, and queued under-health result carrying the vulnerable flag.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/VulnerableUnhealthyReplicasHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.hdds.scm.container.replication.health` as the package containing HDDS container replication check classes.

## Important APIs, Types, and Functions

There are no APIs beyond the package declaration and package-level Javadoc.

## Control Flow

No runtime control flow exists.

## State and Persistence Behavior

No state or persistence is owned by this file.

## Dependencies and Integration Points

It groups health-check handlers used by ReplicationManager's container scan chain.

## Risks and Edge Cases

The only risk is stale package documentation if the package's responsibility changes.

## Test Signals

Compile/package Javadoc checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.hdds.scm.container.replication` as the package for HDDS closed-container replication related classes.

## Important APIs, Types, and Functions

There are no runtime APIs beyond the package declaration and package-level Javadoc.

## Control Flow

No runtime control flow exists.

## State and Persistence Behavior

No state or persistence is owned by this file.

## Dependencies and Integration Points

It groups ReplicationManager processors, queues, health result types, pending-op tracking, and replication repair handlers.

## Risks and Edge Cases

The package comment is broad and may not describe newer EC, unhealthy, or quasi-closed-stuck behavior in detail.

## Test Signals

Compile/package Javadoc checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/report/ContainerReportValidator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/report/ContainerReportValidator.java

## Purpose

`ContainerReportValidator` validates datanode container-replica reports before SCM accepts them. Current validation is specific to EC replicas: reported replica indexes must be present and within the configured EC required-node range.

## Important APIs, Types, and Functions

The public API is static `validate(ContainerInfo, DatanodeDetails, ContainerReplicaProto)`. Internally it uses a singleton validator map from `ReplicationType` to `ReplicaValidator`, with `ECReplicaValidator` implementing index validation.

## Control Flow

`validate` extracts the container replication config and dispatches by replication type. If no validator exists for the type, validation succeeds. The EC validator rejects non-EC configs defensively and then checks `hasReplicaIndex`, index greater than zero, and index less than or equal to `replicationConfig.getRequiredNodes`.

## State and Persistence Behavior

State is a static immutable validator map. No persistence occurs. Rejection affects report processing upstream rather than modifying metadata here.

## Dependencies and Integration Points

It integrates with datanode full/incremental container report handling, `ContainerInfo`, `ReplicationConfig`, EC replication configuration, and SCM logging.

## Risks and Edge Cases

Ratis and other non-EC types pass by default. Invalid EC reports are logged with container ID, datanode, required node count, and reported index. A null replication type also passes because of the optional dispatch.

## Test Signals

Tests should assert EC index absent/zero/negative/too-large rejection, valid EC indexes acceptance, non-EC pass-through, and defensive rejection when an EC validator receives non-EC config.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/report/ContainerReportValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/report/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/report/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.hdds.scm.container.report` as the package for container report classes.

## Important APIs, Types, and Functions

There are no APIs beyond package Javadoc and declaration.

## Control Flow

No runtime control flow exists.

## State and Persistence Behavior

No state or persistence is owned by this file.

## Dependencies and Integration Points

It groups report validation and report-processing classes that support SCM's datanode container-report path.

## Risks and Edge Cases

Only stale documentation is a concern.

## Test Signals

Compile/package Javadoc checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/report/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerAttribute.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerAttribute.java

## Purpose

`ContainerAttribute` is a generic enum-keyed index from container attributes, such as lifecycle state or replication type, to sorted maps of `ContainerID` to `ContainerInfo`. It supports fast in-memory selection by attribute for `ContainerStateMap`.

## Important APIs, Types, and Functions

Important methods are `addNonExisting`, `clearSet`, `remove`, `removeExisting`, `getCollection`, `tailMap`, `count`, and `update`. It stores an immutable enum map whose values are mutable `TreeMap`s.

## Control Flow

Construction creates one empty `TreeMap` for each enum constant. Add/remove operations assert consistency. `update` removes a container ID from its current enum bucket and adds the same `ContainerInfo` to the new bucket, throwing `SCMException` if the old mapping is missing.

## State and Persistence Behavior

State is in-memory only. The class is explicitly not thread-safe and relies on `ContainerStateMap` external locking/serialization. Sorted maps preserve container-ID ordering for pagination.

## Dependencies and Integration Points

It is used by `ContainerStateMap` to index lifecycle states and replication types. It depends on `ContainerID`, `ContainerInfo`, Guava immutable enum maps, Ratis preconditions, and SCM exceptions.

## Risks and Edge Cases

Passing an enum value not in the attribute class throws. Updating from a missing current bucket throws `FAILED_TO_CHANGE_CONTAINER_STATE`. `getCollection` returns a copy, while `tailMap` exposes the underlying sorted map view.

## Test Signals

Tests should cover all enum buckets created, add duplicate assertion, remove existing identity assertion, update success and missing-current failure, sorted tail-map behavior, count accuracy, and external synchronization assumptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerAttribute.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerEntry.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerEntry.java

## Purpose

`ContainerEntry` stores a `ContainerInfo` and its current replica set for `ContainerStateMap`. It keeps replicas keyed by datanode ID while exposing immutable snapshot sets to readers.

## Important APIs, Types, and Functions

Public methods are `getInfo`, `getReplicas`, `put`, and `removeReplica`. The private `copyAndUpdate` updates the mutable map and rebuilds the immutable exposed replica set.

## Control Flow

Adding or removing a replica mutates the `TreeMap<DatanodeID, ContainerReplica>`, then copies map values into a new `HashSet` and publishes it as an unmodifiable set. `put` returns the replaced replica, and `removeReplica` returns the removed replica.

## State and Persistence Behavior

State is in-memory container info plus a replica map and immutable set snapshot. There is no persistence. Thread safety relies on owning `ContainerStateMap` usage.

## Dependencies and Integration Points

It integrates with `ContainerStateMap` replica update/remove paths. Datanode ID ordering in the `TreeMap` gives deterministic map storage, while set exposure prevents external mutation.

## Risks and Edge Cases

Every replica update copies the full replica map to a set, which is fine for small replication factors but worth noting. Equality semantics of `ContainerReplica` affect set uniqueness after values are copied.

## Test Signals

Tests should assert immutable set exposure, replacement return value on same datanode, removal return value, info identity preservation, and snapshot changes after updates.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerEntry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerState.java

## Purpose

`ContainerState` is a value object representing a container selection key composed of owner and pipeline ID.

## Important APIs, Types, and Functions

It exposes `getOwner`, `equals`, `hashCode`, and `toString`. Fields are immutable `owner` and `PipelineID`.

## Control Flow

There is no complex flow. Equality checks class and compares owner plus pipeline ID using Apache commons builders; hash code uses the same fields.

## State and Persistence Behavior

State is immutable and in-memory. The class does not persist data.

## Dependencies and Integration Points

It depends on `PipelineID` and is intended for container state/key maps where owner and pipeline distinguish allocation pools.

## Risks and Edge Cases

`toString` labels the object as `ContainerKey`, which may be legacy naming. Null owner or pipeline is not rejected in the constructor, so equality and hash code must tolerate nulls through the builder implementation.

## Test Signals

Tests should assert equality/hash-code for same and different owner/pipeline pairs, null-field behavior if allowed, and stable string format if logs depend on it.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerStateMap.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerStateMap.java

## Purpose

`ContainerStateMap` is SCM's in-memory index of containers and their replicas. It maintains the primary container-ID map plus secondary indexes by lifecycle state and replication type for allocation, listing, and replication scans.

## Important APIs, Types, and Functions

Important methods include `addContainer`, `contains`, `removeContainer`, `getContainerInfo`, `getContainerReplicas`, `updateContainerReplica`, `removeContainerReplica`, `updateState`, `getContainerIDs`, `getContainerInfos`, and `getContainerCount`. The nested `ContainerMap` stores `ContainerID -> ContainerEntry` in a `ConcurrentSkipListMap`.

## Control Flow

Adding a container inserts into the primary map if absent, then adds to lifecycle and type indexes. Removing a container removes from all indexes. Replica updates delegate to the entry for the target container. State updates move the container ID between lifecycle buckets and then mutate the `ContainerInfo` state field. Listing uses sorted tail maps for pagination.

## State and Persistence Behavior

All state is in-memory and reconstructed from persistent SCM metadata elsewhere. The class declares itself not thread-safe despite the concurrent primary map; consistency across primary and secondary indexes depends on external synchronization.

## Dependencies and Integration Points

It integrates with SCM container manager/state manager, replication manager scans, allocation queries, report processing, and container lifecycle state transitions. It depends on `ContainerAttribute`, `ContainerEntry`, protobuf lifecycle/replication enums, `ContainerReplica`, and `SCMException`.

## Risks and Edge Cases

Duplicate add is idempotent and does not update existing info. Updating state for a missing container silently returns, while missing secondary-index state raises from `ContainerAttribute`. `getContainerReplicas` returns null for missing containers, not an empty set.

## Test Signals

Tests should cover add/remove index consistency, idempotent duplicate add, replica add/replace/remove, sorted pagination by ID, state update moving counts and mutating info, missing-container behavior, replication type listing, and external locking assumptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerStateMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.hdds.scm.container.states` as the container states package.

## Important APIs, Types, and Functions

There are no runtime APIs beyond package Javadoc and declaration.

## Control Flow

No runtime control flow exists.

## State and Persistence Behavior

No state or persistence is owned by this file.

## Dependencies and Integration Points

It groups in-memory container state maps and helper value/index types.

## Risks and Edge Cases

Only stale package documentation is a concern.

## Test Signals

Compile/package Javadoc checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/events/SCMEvents.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/events/SCMEvents.java

## Purpose

`SCMEvents` is the namespace of typed events used by SCM subsystems to communicate through the HDDS event queue. It centralizes event names and payload types for reports, datanode commands, pipeline actions, node state changes, replication notifications, and state-machine readiness.

## Important APIs, Types, and Functions

The class exposes static `TypedEvent` and `Event` constants including `NODE_REPORT`, `DATANODE_COMMAND_COUNT_UPDATED`, `NODE_REGISTRATION_CONT_REPORT`, `CONTAINER_REPORT`, `INCREMENTAL_CONTAINER_REPORT`, `CONTAINER_ACTIONS`, `PIPELINE_REPORT`, `OPEN_PIPELINE`, `PIPELINE_ACTIONS`, `CMD_STATUS_REPORT`, `DATANODE_COMMAND`, `RETRIABLE_DATANODE_COMMAND`, `CLOSE_CONTAINER`, node health/admin events, `DELETE_BLOCK_STATUS`, `REPLICATION_MANAGER_NOTIFY`, `RECONCILE_CONTAINER`, and `STATEMACHINE_READY`.

## Control Flow

There is no executable flow beyond static event construction. Producers fire these constants into the event queue; listeners subscribe elsewhere based on the typed payload.

## State and Persistence Behavior

State is static event identity and event names. No persistence occurs. Event payloads are transient runtime messages.

## Dependencies and Integration Points

It integrates SCMDatanode heartbeat dispatchers, NodeManager, PipelineManager, ReplicationManager, command status handlers, safe mode rules, close-container workflows, Ratis state-machine readiness, and datanode command dispatch.

## Risks and Edge Cases

Event names and payload types form an internal compatibility contract. Changing a constant type or name can break listener registration. Some events use raw `Event<CommandForDatanode>` while most are `TypedEvent`.

## Test Signals

Tests should verify event queue wiring for each major producer/listener path, especially report dispatch, close-container events, retryable datanode commands, replication notifications, and state-machine ready events.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/events/SCMEvents.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/events/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/events/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.hdds.scm.events` as the package containing events used internally by SCM subsystems.

## Important APIs, Types, and Functions

There are no APIs beyond package Javadoc and declaration.

## Control Flow

No runtime control flow exists.

## State and Persistence Behavior

No state or persistence is owned by this file.

## Dependencies and Integration Points

It groups `SCMEvents` and related event definitions used for SCM internal communication.

## Risks and Edge Cases

Only stale package documentation is a concern.

## Test Signals

Compile/package Javadoc checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/events/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/BackgroundSCMService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/BackgroundSCMService.java

## Purpose

`BackgroundSCMService` is a reusable daemon wrapper for SCM background services that should run only when the SCM leader is ready and out of safe mode. It handles start/stop, status transitions, delayed activation, periodic execution, and test-triggered immediate runs.

## Important APIs, Types, and Functions

It implements `SCMService` with `start`, `stop`, `notifyStatusChanged`, `shouldRun`, and `getServiceName`. Testing APIs are `runImmediately` and `getRunning`. The nested `Builder` supplies interval, wait time, service name, periodical task, `SCMContext`, and `Clock`.

## Control Flow

Construction starts the daemon. `notifyStatusChanged` sets status to running only when `SCMContext.isLeaderReady` and not safe mode, recording the ready timestamp; otherwise it pauses. The run loop executes the task if `shouldRun`, catches all task throwables, then waits for the interval unless woken immediately. `stop` flips the running flag and interrupts the thread.

## State and Persistence Behavior

State is in-memory thread/run status, service status, ready timestamp, and wake flag. No persistence occurs. Work performed by the supplied task may persist state elsewhere.

## Dependencies and Integration Points

It integrates with SCM HA leader readiness, safe mode, service managers, and background tasks such as monitors or flushers. Thread names are prefixed by `SCMContext`.

## Risks and Edge Cases

The constructor starts the thread before the caller can further configure the object. `notifyStatusChanged` must be called after context changes or the service can remain paused. Task exceptions are logged and retried rather than stopping the service.

## Test Signals

Tests should cover builder validation, delayed `shouldRun`, safe-mode and leader-ready transitions, task retry after exception, immediate wake, idempotent start/stop, interrupt handling, and daemon thread naming.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/BackgroundSCMService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/ExecutionUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/ExecutionUtil.java

## Purpose

`ExecutionUtil` is a small utility for running a checked action once and, if it fails, running cleanup while rethrowing the original exception.

## Important APIs, Types, and Functions

The API is `create(CheckedRunnable)`, `onException(CheckedRunnable)`, and `execute`. It is generic over exception type `E extends Throwable`.

## Control Flow

`execute` is guarded by a `completed` flag so the try block runs at most once. If the try block throws, it runs the registered cleanup block, logs cleanup failures, and rethrows the original exception.

## State and Persistence Behavior

State is in-memory: the try runnable, cleanup runnable, and volatile completion flag. No persistence occurs.

## Dependencies and Integration Points

It uses Ratis `CheckedRunnable` and SLF4J. It is useful around HA operations that need best-effort rollback without masking the root failure.

## Risks and Edge Cases

If `onException` is not set and the try block fails, `execute` will throw a null-pointer while attempting cleanup, masking behavior may differ from intent. `completed` prevents retry after a failed first execution.

## Test Signals

Tests should cover success running once, failure invoking cleanup and rethrowing original, cleanup failure logged but not replacing original, and repeated `execute` no-op behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/ExecutionUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/HASecurityUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/HASecurityUtils.java

## Purpose

`HASecurityUtils` contains SCM HA security helpers for SCM certificate initialization, root CA creation, Ratis TLS setup, sending certificate-related requests through Ratis, and certificate classification.

## Important APIs, Types, and Functions

Important methods are `initializeSecurity`, overloaded `initializeRootCertificateServer`, `createSCMRatisTLSConfig`, `submitScmRequestToRatis`, `isSelfSignedCertificate`, and `isCACertificate`. Private `getScmSecurityClientWithFixedDuration` builds a bounded-wait SCM security client.

## Control Flow

Security initialization creates a `SecurityConfig`, obtains a failover SCM security client with adjusted retry count, constructs an `SCMCertificateClient`, and calls `initWithRecovery`, updating storage config when a certificate ID is received. Root CA initialization creates and initializes a `DefaultCAServer`. Ratis request submission builds a GRPC Raft client with TLS parameters and fixed retry policy, sends asynchronously, waits, and decodes `SCMRatisResponse`.

## State and Persistence Behavior

Certificate material and SCM cert serial ID are persisted by the certificate client and `SCMStorageConfig`. Ratis submission does not persist locally except through the replicated state machine handling the request.

## Dependencies and Integration Points

It integrates with HDDS security config, SCM security protocol failover proxies, certificate stores/clients, Default CA server, Ratis GRPC TLS, UGI, and SCM Ratis response decoding.

## Risks and Edge Cases

Retry count calculation depends on duration and retry interval units. TLS config is only returned when both security and gRPC TLS are enabled. Ratis request submission uses fixed retry constants and blocks on the future. Certificate ID persistence failures are wrapped in runtime exceptions from the callback.

## Test Signals

Tests should cover secure and insecure TLS config creation, root CA initialization defaults, retry-count adjustment for bounded init waits, certificate serial callback persistence, Ratis response decode path, and self-signed/CA certificate predicates.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/HASecurityUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/InterSCMGrpcClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/InterSCMGrpcClient.java

## Purpose

`InterSCMGrpcClient` downloads RocksDB checkpoints from another SCM through the inter-SCM gRPC service. It is the client-side implementation of `SCMSnapshotDownloader`.

## Important APIs, Types, and Functions

Public APIs are the constructor, `download(Path)`, `shutdown`, and `close`. Nested `StreamDownloader` implements `StreamObserver<CopyDBCheckpointResponseProto>` and adapts streamed protobuf chunks into a local file and `CompletableFuture<Path>`.

## Control Flow

Construction builds a Netty channel with plaintext by default, or mutual TLS when security and gRPC TLS are enabled. `download` sends a flush-enabled checkpoint request and returns a future. The stream observer writes each received chunk to the output stream, completes the future on `onCompleted`, and on error closes the stream, deletes the partial output, and completes exceptionally.

## State and Persistence Behavior

State includes the gRPC channel/stub, deadline timeout, output stream, and output path. Persistence is the checkpoint file written to `outputPath`; partial files are deleted on failure.

## Dependencies and Integration Points

It integrates with HA snapshot download, inter-SCM protobuf/gRPC stubs, Ozone chunk-size constants, `SecurityConfig`, SCM certificate client key/trust managers, and Netty gRPC TLS.

## Risks and Edge Cases

The deadline is read in milliseconds but applied with `TimeUnit.SECONDS`, which deserves scrutiny. Stream constructor throws unchecked IO if the output path cannot be opened. If deleting a failed partial file fails, it logs but leaves residue.

## Test Signals

Tests should cover plaintext and TLS channel setup, successful multi-chunk download, completion future path, stream open failure, on-error partial deletion and exceptional completion, close/shutdown interruption, and deadline unit behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/InterSCMGrpcClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/InterSCMGrpcProtocolService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/InterSCMGrpcProtocolService.java

## Purpose

`InterSCMGrpcProtocolService` hosts the gRPC endpoint that serves SCM DB checkpoints to peer SCMs in HA deployments.

## Important APIs, Types, and Functions

Public methods are `getPort`, `start`, and `stop`. Construction binds an `InterSCMGrpcService` implementation to a Netty gRPC server and optionally configures mutual TLS.

## Control Flow

The constructor reads the gRPC port, builds a Netty server with max inbound chunk size, adds the checkpoint service, and configures server TLS with SCM certificate key/trust managers when enabled. `start` is idempotent through `AtomicBoolean` and starts the server. `stop` shuts down and awaits termination.

## State and Persistence Behavior

State is in-memory server, port, and start flag. The service streams checkpoint data from SCM metadata store but this wrapper does not persist data.

## Dependencies and Integration Points

It integrates with `StorageContainerManager`, `InterSCMGrpcService`, SCM security config, certificate client, Netty gRPC, and SCM HA bootstrap/snapshot transfer.

## Risks and Edge Cases

TLS setup failures throw runtime exceptions after logging. `stop` only acts when the start flag is true. Server construction is package-private, so lifecycle is controlled by SCM HA components.

## Test Signals

Tests should cover start idempotence, stop after start, configured port, TLS enabled/disabled setup, TLS setup failure, max message size, and checkpoint service registration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/InterSCMGrpcProtocolService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/InterSCMGrpcService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/InterSCMGrpcService.java

## Purpose

`InterSCMGrpcService` is the gRPC service implementation that streams a flushed SCM RocksDB checkpoint to peer SCMs.

## Important APIs, Types, and Functions

It extends `InterSCMProtocolServiceGrpc.InterSCMProtocolServiceImplBase` and overrides `download`. Constructor initializes the transaction-info table and `SCMDBCheckpointProvider`. It uses `SCMGrpcOutputStream` for streaming response chunks.

## Control Flow

On `download`, it flushes the SCM HA transaction buffer, reads `TRANSACTION_INFO_KEY` to ensure transaction info exists, creates a gRPC output stream with the cluster ID and buffer size, and asks the checkpoint provider to write the DB checkpoint to the stream. IO failures are logged and sent through `responseObserver.onError`.

## State and Persistence Behavior

The service reads persistent SCM metadata store state and transaction info. It forces buffered transactions to disk before checkpointing. It does not store checkpoint files itself; the provider creates and cleans checkpoint snapshots.

## Dependencies and Integration Points

It integrates with `StorageContainerManager`, SCM HA transaction buffer, metadata store transaction info table, `HAUtils`, `SCMDBCheckpointProvider`, and inter-SCM gRPC protobufs.

## Risks and Edge Cases

`transactionInfo` is required non-null after flush; a missing table row fails the download. The request's flush flag is passed to the provider, but the transaction buffer is always flushed first. Runtime exceptions other than IO are not explicitly caught.

## Test Signals

Tests should cover transaction buffer flush before streaming, transaction-info lookup, provider invocation with request flush flag, successful chunk completion, IO error propagation, and missing transaction info behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/InterSCMGrpcService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/RatisUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/RatisUtil.java

## Purpose

`RatisUtil` builds and configures Ratis properties for SCM HA and maps low-level Ratis/security exceptions into service exceptions with the correct retry/failover semantics.

## Important APIs, Types, and Functions

Important APIs are `newRaftProperties`, `setRaftStorageDir`, and `checkRatisException`. Private helpers configure RPC, leader election, log, retry cache, and snapshots. It defines behavior for `NonRetriableException`, `RetriableWithNoFailoverException`, `RetriableWithFailOverException`, and converted not-leader exceptions.

## Control Flow

`newRaftProperties` creates properties, sets storage directory, log settings, RPC settings, retry cache, snapshot settings, leader-election settings, and applies raw overrides matching the SCM HA Ratis prefix. `checkRatisException` examines IOException causes through `SCMHAUtils`, converts not-leader responses with peer endpoint metadata, and maps selected SCM security error codes to retry categories.

## State and Persistence Behavior

The utility owns no state. It points Ratis at the configured SCM Ratis storage directory and influences Ratis log/snapshot persistence through returned properties.

## Dependencies and Integration Points

It integrates with `ScmConfigKeys`, `SCMHAUtils`, Ratis server config keys, `RatisHelper`, gRPC config, SCM Ratis server peer ID conversion, and SCM security exception codes.

## Risks and Edge Cases

Ratis request timeout must exceed 1000 ms or configuration fails. Log appender buffer byte limit is cast to int. Raw prefixed overrides can override earlier settings. Security exception mapping is selective; unmapped security errors fall through without throwing.

## Test Signals

Tests should assert property values for storage, RPC type/port/timeouts, log sizes and purge settings, retry cache, snapshots, pre-vote, prefixed overrides, invalid timeout rejection, and exception mapping for not-leader, non-retriable, no-failover retry, failover retry, and certificate failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/RatisUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMContext.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMContext.java

## Purpose

`SCMContext` is SCM's shared source of truth for HA leader state, leader readiness, Raft term, safe-mode status, finalization checkpoint, SCM reference, and thread-name prefix.

## Important APIs, Types, and Functions

Important APIs are `emptyContext`, `updateLeaderAndTerm`, `setLeaderReady`, `setFinalizationCheckpoint`, `isLeader`, `isLeaderReady`, `getTermOfLeader`, `updateSafeModeStatus`, `isInSafeMode`, `isPreCheckComplete`, `getFinalizationCheckpoint`, `getScm`, `threadNamePrefix`, and the nested `Builder`.

## Control Flow

Leader/term updates acquire the write lock, update fields, and reset leader-ready when leadership is lost. Read methods acquire the read lock. In non-HA mode, represented by `INVALID_TERM`, leader and leader-ready checks always return true. `getTermOfLeader` throws a not-leader exception from the Ratis server when called on a follower SCM with a real term.

## State and Persistence Behavior

State is in-memory and protected by a read/write lock, except finalization checkpoint is also volatile. It does not persist state itself; Ratis and safe-mode managers feed updates.

## Dependencies and Integration Points

It integrates with SCM HA manager, Ratis server, safe mode manager, background services, upgrade finalization, and thread naming for SCM services.

## Risks and Edge Cases

`emptyContext` returns leader-ready in non-HA mode even with null SCM. `getTermOfLeader` only throws when the SCM reference is a `StorageContainerManager`; otherwise a follower can return the term. Builder `build` requires SCM, but testing `buildMaybeInvalid` does not.

## Test Signals

Tests should cover non-HA defaults, leader-ready reset on follower transition, set leader ready, not-leader exception path, safe-mode status reads, finalization checkpoint updates, builder validation, and concurrent read/write behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMDBCheckpointProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMDBCheckpointProvider.java

## Purpose

`SCMDBCheckpointProvider` creates and streams SCM RocksDB checkpoints to an output stream, cleaning up checkpoint resources afterward.

## Important APIs, Types, and Functions

The main API is `writeDBCheckPointToSream(OutputStream, boolean)`. It uses `DBStore.getCheckpoint`, `HddsServerUtil.writeDBCheckpointToStream`, `DBCheckpoint.cleanupCheckpoint`, and logs duration.

## Control Flow

The method validates that the store exists, obtains a checkpoint with optional flush, rejects null checkpoints or missing locations, streams the checkpoint directory/archive to the caller, logs elapsed time, rethrows IO errors, and always attempts checkpoint cleanup.

## State and Persistence Behavior

State is a transient `DBStore` reference. The DB checkpoint is a temporary persistent snapshot created by the DB layer and cleaned up in `finally`.

## Dependencies and Integration Points

It integrates with inter-SCM gRPC streaming, DBStore checkpoint support, and HDDS checkpoint streaming utilities.

## Risks and Edge Cases

The method name contains `Sream`, which is API spelling. If the store is null it logs and returns without signaling failure. Cleanup failures are logged but not rethrown. An empty file name returns without streaming.

## Test Signals

Tests should cover successful stream and cleanup, null store behavior, null checkpoint rejection, null checkpoint location rejection, streaming IO error propagation, flush flag propagation, and cleanup failure logging.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMDBCheckpointProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMGrpcOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMGrpcOutputStream.java

## Purpose

`SCMGrpcOutputStream` adapts an `OutputStream` interface to a gRPC `StreamObserver` for streaming SCM DB checkpoint bytes as `CopyDBCheckpointResponseProto` chunks.

## Important APIs, Types, and Functions

It overrides `write(int)`, `write(byte[], int, int)`, and `close`. Private `flushBuffer` emits protobuf chunks containing cluster ID, data, EOF flag, read offset, and length.

## Control Flow

Writes append into a `ByteString.Output` buffer. When the buffer reaches the configured size, it emits a chunk with `eof=false`, increments `writtenBytes`, and resets the buffer. `close` flushes any remaining bytes with `eof=true`, logs the total, calls `onCompleted`, and closes the buffer.

## State and Persistence Behavior

State is in-memory buffer, cluster ID, buffer size, observer, and byte offset. No local persistence occurs; remote client persists received bytes.

## Dependencies and Integration Points

It integrates with `InterSCMGrpcService`, inter-SCM protobufs, and gRPC stream observers.

## Risks and Edge Cases

If the buffer is empty on `close`, no EOF chunk is sent; completion is the final signal. `write` catches exceptions and calls `onError` but does not rethrow. The chunk `readOffset` is based on bytes emitted so far and should remain monotonic.

## Test Signals

Tests should cover single-byte and array writes, offset/length validation, chunk boundaries, offsets and lengths across multiple flushes, close completion, empty close behavior, observer error on write exception, and total byte logging.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMGrpcOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHADBTransactionBuffer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHADBTransactionBuffer.java

## Purpose

`SCMHADBTransactionBuffer` defines the HA transaction-buffer contract for batching SCM DB writes, tracking the latest transaction info, and coordinating snapshot/flush state while applying Ratis transactions.

## Important APIs, Types, and Functions

It extends `DBTransactionBuffer` and adds `updateLatestTrxInfo`, `getLatestTrxInfo`, `getLatestSnapshot`, `setLatestSnapshot`, `getLatestSnapshotRef`, `flush`, `flushIfNeeded`, `shouldFlush`, `init`, `beginApplyingTransaction`, and `endApplyingTransaction`.

## Control Flow

Implementations buffer table puts/deletes inherited from `DBTransactionBuffer`, update latest transaction metadata, flush batches to RocksDB, expose latest Ratis snapshot info, and suppress periodic flushes while transactions are actively being applied.

## State and Persistence Behavior

The interface specifies persistent behavior: flush must commit DB batch contents and transaction info. Snapshot references are in-memory but reflect persisted transaction positions.

## Dependencies and Integration Points

It integrates SCM metadata mutations with Ratis state machine apply, snapshot installation, transaction monitoring tasks, and checkpoint serving.

## Risks and Edge Cases

Implementations must keep transaction info in the same batch as data mutations or snapshots can advertise uncommitted state. Apply counters must be balanced to avoid starving flushes.

## Test Signals

Implementation tests should verify batch commit atomicity, transaction info monotonicity, flush-if-needed timing, suppression during active apply, snapshot reference updates, and reinitialization after snapshot install.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHADBTransactionBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHADBTransactionBufferImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHADBTransactionBufferImpl.java

## Purpose

`SCMHADBTransactionBufferImpl` is the RocksDB-backed SCM HA transaction buffer. It batches table writes/deletes, commits latest transaction info atomically with the batch, updates snapshot position, and coordinates periodic flushing around active Ratis transaction application.

## Important APIs, Types, and Functions

Important methods are `addToBuffer`, `removeFromBuffer`, `updateLatestTrxInfo`, `getLatestTrxInfo`, snapshot getters/setters, `flush`, `flushIfNeeded`, `shouldFlush`, `init`, `beginApplyingTransaction`, `endApplyingTransaction`, `toString`, and `close`. It uses `BatchOperation`, `TransactionInfo`, `SnapshotInfo`, `SCMMetadataStore`, and `DeletedBlockLogImpl.onFlush`.

## Control Flow

Buffered writes/deletes take the read lock, increment `txFlushPending`, and append to the current batch. `updateLatestTrxInfo` rejects non-monotonic transaction info. `flush` takes the write lock and calls `flushUnderWriteLock`, which writes transaction info into the transaction table in the same batch, commits, closes the batch, updates latest snapshot, opens a new batch, notifies deleted block log flush, resets pending count, and records flush time. `flushIfNeeded` skips while applying transactions and flushes only after pending writes exceed the wait time. `init` closes any old batch and reloads transaction info from DB.

## State and Persistence Behavior

Persistent state is committed RocksDB batch contents plus `TRANSACTION_INFO_KEY`. In-memory state includes the current batch, latest transaction info, latest snapshot reference, pending flush counter, active apply counter, last snapshot time, and read/write lock.

## Dependencies and Integration Points

It integrates with `StorageContainerManager`, SCM metadata store, Ratis state machine apply and snapshots, transaction buffer monitor, checkpoint service, and deleted block log flush hooks.

## Risks and Edge Cases

`latestTrxInfo` must be updated before flush; otherwise the previous/default transaction info is committed. Active apply counters must be balanced. `flushUnderWriteLock` assumes the deleted block log is `DeletedBlockLogImpl`. `close` closes the current batch without forcing a final commit.

## Test Signals

Tests should cover add/delete batch writes, atomic transaction info commit, monotonic transaction guard, snapshot update after flush, flush-if-needed timing and active-apply suppression, init from empty and populated transaction table, deleted-block-log `onFlush`, close behavior, and concurrent read/write locking.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHADBTransactionBufferImpl.java -->
