# Research: subset-b-008044

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManager.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManager.java

Purpose: exercises the central `ReplicationManager` unit behavior without starting background subservices. It validates container health classification, queue population, command dispatch, pending-op tracking, throttling, excluded-node maintenance, metrics, service lifecycle, and report sampling for RATIS and EC containers.

Important APIs and types: `ReplicationManager`, `ReplicationManagerConfiguration`, `ContainerManager`, `ContainerReplicaPendingOps`, `ReplicationQueue`, `ReplicationManagerReport`, `ContainerHealthResult`, `RatisOverReplicationHandler`, `ECUnderReplicationHandler`, `DeleteContainerCommand`, `ReplicateContainerCommand`, `ReconstructECContainersCommand`, `NodeManager`, `PlacementPolicy`, `SCMContext`, and `TestClock`. The test overrides `startSubServices()` to keep execution deterministic and captures commands through mocked `NodeManager.addDatanodeCommand`.

Control flow: setup builds a mocked SCM environment, in-memory `containerReplicaMap` / `containerInfoSet`, placement policies, and real pending-op and queue objects. Individual tests call `processContainer`, `checkContainerStatus`, `processAll`, or direct send/throttled-send methods. Health tests cover open containers, mismatched replicas, closed/quasi-closed RATIS cases, EC under/over/mis replication, unhealthy replicas, unrecoverable EC containers, and pending operations that repair under/over replication. Command tests verify that `sendDatanodeCommand` creates pending ADD/DELETE records, stamps deadlines, and increments EC vs RATIS metrics correctly.

State and persistence behavior: no durable persistence is used, but the test models SCM state with in-memory maps and pending-op structures. It checks that pending ops are cleared when the service starts, pending ADD/DELETE suppress queueing when they already repair a condition, expired delete ops can be resent with a new deadline, and container reports honor the current sample limit after reconfiguration. It also verifies node-command limit state through `getExcludedNodes()` and `datanodeCommandCountUpdated`.

Dependencies and integration points: depends on Ozone SCM container, node, placement, HA, event, pipeline, token, command, and metrics types. It integrates with `SCMServiceManager` for lifecycle notification, `SCMEvents.CLOSE_CONTAINER` for unhealthy open containers, `StorageContainerManager` / `PipelineManager` for command construction, and `NodeManager` for command counts and status.

Risks: many assertions depend on handler ordering and exact health-state precedence, especially under-vs-over precedence, unhealthy EC deletion before mis-replication, and quasi-closed stuck handling. Mocked placement policies can hide real topology behavior. Command capture uses a `HashSet`, so tests generally assert size/type/target rather than ordering. Metrics registration needs cleanup to avoid cross-test contamination.

Test signals: strong coverage of report counters, queue sizes, command counts, pending op contents, command deadlines, throttle-deferred metrics, excluded-node transitions, live monitor wakeup behavior, and dynamic report sample-limit changes. The file is the broadest regression signal for SCM replication-manager orchestration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerEventHandler.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerEventHandler.java

Purpose: validates the event adapter that reacts to datanode events by waking `ReplicationManager` only when SCM is leader-ready and not in safe mode.

Important APIs and types: `ReplicationManagerEventHandler`, `ReplicationManager.notifyNodeStateChange`, `SCMContext.isLeaderReady`, `SCMContext.isInSafeMode`, `EventPublisher`, and `DatanodeDetails`.

Control flow: a parameterized `MethodSource` enumerates four leader/safe-mode combinations. The test stubs SCM context, sends a random datanode message through `onMessage`, and verifies whether `notifyNodeStateChange()` was called exactly once or not at all.

State and persistence behavior: no persistence. The observable state is the mocked leader/safe-mode gate and invocation count.

Dependencies and integration points: integrates SCM HA state with replication-manager scheduling. The `EventPublisher` is passed through but not used by the asserted behavior.

Risks: the test intentionally covers only the gate, not event payload content or publisher interactions. Any future requirement to react to specific datanode identities would need added coverage.

Test signals: compact truth-table coverage confirms the handler wakes replication work only for active, non-safe-mode SCM leadership.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerEventHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerMetrics.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerMetrics.java

Purpose: verifies that `ReplicationManagerMetrics` exposes gauges for container lifecycle states and replication health states based on `ReplicationManagerReport`.

Important APIs and types: `ReplicationManagerMetrics.create`, `ReplicationManagerReport`, `HddsProtos.LifeCycleState`, `ContainerHealthState`, `MetricsAsserts.getMetrics`, and `getLongGauge`.

Control flow: setup builds a report with deterministic counts by incrementing lifecycle states according to proto numbers and health states according to enum ordinals. The mocked manager returns config, report, pending ops, and a real queue, then metrics are registered. Tests read gauges by metric name and compare expected values.

State and persistence behavior: metrics are registered in the process metrics system and unregistered in `@AfterEach` to prevent leakage. The report is the source of gauge state.

Dependencies and integration points: ties report accounting to the Hadoop/Ozone metrics source named by `ReplicationManagerMetrics.METRICS_SOURCE_NAME`.

Risks: metric-name compatibility is critical; renaming `ContainerHealthState.getMetricName()` or lifecycle gauge names will break consumers and these tests. Metrics registration lifecycle must remain isolated.

Test signals: confirms all lifecycle gauges and every `ContainerHealthState` gauge are present with expected values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerScenarios.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerScenarios.java

Purpose: provides a JSON-driven scenario harness for replication-manager health checks and command execution. It lets resource files describe containers, replicas, pending operations, expected report counters, queue sizes, and expected commands.

Important APIs and types: `Scenario`, `TestReplica`, `PendingReplica`, `ExpectedCommands`, `Expectation`, `ReplicationManager`, `ReplicationQueue`, `ReplicationManagerReport`, `ContainerReplicaPendingOps`, Jackson `ObjectMapper` / `MappingIterator`, `NodeStatus`, `DatanodeDetails`, `DatanodeID`, and command type `SCMCommandProto.Type`.

Control flow: `@BeforeAll` loads every JSON file under `/replicationManagerTests`, rejects duplicate descriptions per file, and stores resource names for diagnostics. Each parameterized test creates a fresh mocked SCM environment, applies scenario maintenance settings, builds `ContainerInfo`, schedules pending ops, builds replicas, runs `processContainer`, checks report and queue expectations, checks read-only `checkContainerStatus` emits no commands, then processes one queued under- or over-replicated result and checks repair commands.

State and persistence behavior: scenario aliases create stable in-test datanode and origin identities through static maps cleared before each test. `NODE_STATUS_MAP` models datanode operational and health states. Pending operations are scheduled into a real `ContainerReplicaPendingOps`; no durable store is touched.

Dependencies and integration points: integrates test resources, Jackson deserialization, simple test placement policies, `NodeManager` command capture, SCM context leadership/safe-mode gating, and command-count mocks. It is the bridge between human-readable replication scenarios and `ReplicationManager` behavior.

Risks: the class comment notes scenario support does not cover mis-replicated containers. Static alias maps require careful clearing to avoid cross-scenario leakage. JSON field setters define the external scenario schema, so renaming setters changes resource compatibility.

Test signals: broad data-driven coverage across many container/replica combinations, including check-phase commands, read-only status checks, queue sizes, and execution-phase commands. Failures include scenario resource names and descriptions, making regressions traceable to the JSON case.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerScenarios.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerUtil.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerUtil.java

Purpose: validates `ReplicationManagerUtil.getExcludedAndUsedNodes`, which partitions datanodes into placement-policy used and excluded sets for replication target selection.

Important APIs and types: `ReplicationManagerUtil.ExcludedAndUsedNodes`, `ContainerReplica`, `ContainerReplicaOp`, `NodeStatus`, `NodeManager`, `SCMNodeMetric`, `ContainerReplicaPendingOps.SizeAndTime`, `ReplicationManagerConfiguration`, and `TestClock`.

Control flow: tests build closed or quasi-closed RATIS containers with good, to-be-removed, unhealthy, decommissioning, maintenance, dead-maintenance, pending-add, and pending-delete nodes. The utility is called with replicas, removal candidates, pending ops, and a mocked manager. A disk-space test also stubs scheduled-size maps and node stats to exclude datanodes whose scheduled bytes would violate min free space.

State and persistence behavior: no persistent state. The important mutable state is pending-op scheduled size with timestamps; expired entries should not cause exclusion, while live scheduled bytes can exclude a full target.

Dependencies and integration points: integrates node health/operational state, pending replication/deletion bookkeeping, node capacity metrics, and placement-policy inputs.

Risks: quasi-closed unhealthy replicas are special: a unique origin can remain usable, but a non-unique origin is excluded. Dead maintenance nodes are intentionally neither used nor excluded. Disk-space exclusion depends on timely cleanup of scheduled-size entries.

Test signals: asserts exact used/excluded memberships for normal, quasi-closed, and insufficient-disk-space cases, making this a strong guard for placement candidate filtering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestUnderReplicatedProcessor.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestUnderReplicatedProcessor.java

Purpose: tests the queue processor that drains under-replicated work and delegates each item to `ReplicationManager.processUnderReplicatedContainer`.

Important APIs and types: `UnderReplicatedProcessor`, `ReplicationQueue`, `UnderReplicatedHealthResult`, `ReplicationManagerMetrics`, `ReplicationManager.getReplicationInFlightLimit`, and `ReplicationManager.getInflightReplicationCount`.

Control flow: setup uses a real queue and metrics object with a mocked manager that should run. One test confirms successful processing removes the queued result. Another makes processing throw `IOException`, expecting the same result to be requeued. A limit test sets in-flight count above the global limit, verifies no processing and requeue, then lowers the count and verifies processing succeeds.

State and persistence behavior: queue contents and metrics are the state under test. No durable persistence is involved. The pending-replication-limit-reached metric increments when processing is deferred by the global in-flight limit.

Dependencies and integration points: connects queue scheduling to replication-manager execution and metrics. It depends on `UnderReplicatedHealthResult` priority state only enough to enqueue/dequeue.

Risks: exception handling must preserve the original work item or replication work can be lost. In-flight limit logic must avoid both starvation and overload.

Test signals: queue size, object identity after requeue, manager invocation counts, and metric increment verify the processor's retry and throttling contracts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestUnderReplicatedProcessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestClosedWithUnhealthyReplicasHandler.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestClosedWithUnhealthyReplicasHandler.java

Purpose: verifies `ClosedWithUnhealthyReplicasHandler`, which handles closed EC containers that are otherwise sufficiently replicated but have extra unhealthy replicas.

Important APIs and types: `ClosedWithUnhealthyReplicasHandler`, `ContainerCheckRequest`, `ReplicationManager.sendDeleteCommand`, `ReplicationManagerReport`, `ContainerHealthState.UNHEALTHY_OVER_REPLICATED`, `ECReplicationConfig`, and `RatisReplicationConfig`.

Control flow: setup builds a handler with mocked replication manager and request builder. Negative tests cover non-closed containers, RATIS containers, no unhealthy replicas, and EC under-replication. The positive test builds a closed EC 3-2 container with all five healthy indexes plus unhealthy copies for indexes 2 and 5, runs normal and read-only requests, and verifies delete commands target unhealthy indexes.

State and persistence behavior: report state increments `UNHEALTHY_OVER_REPLICATED`; read-only requests update report state but should not send new delete commands. No persistent storage is touched.

Dependencies and integration points: integrates EC replica-index accounting with replication-manager delete command dispatch.

Risks: this handler must run before generic mis/over replication in cases where unhealthy extras block cleaner repair. Deleting a healthy copy instead of the unhealthy copy would reduce durability.

Test signals: handler boolean result, report counter, read-only behavior, and delete-command verification for target replica indexes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestClosedWithUnhealthyReplicasHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestClosingContainerHandler.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestClosingContainerHandler.java

Purpose: tests `ClosingContainerHandler`, responsible for containers in CLOSING state, including replica close commands and state transitions when replicas are absent or only unhealthy.

Important APIs and types: `ClosingContainerHandler`, `ContainerCheckRequest`, `ReplicationManager.sendCloseContainerReplicaCommand`, `ReplicationManager.updateContainerState`, lifecycle events `CLOSE` and `QUASI_CLOSE`, `TestClock`, `ReplicationManagerConfiguration`, `ECReplicationConfig`, and `RatisReplicationConfig`.

Control flow: negative tests ensure non-closing EC/RATIS containers pass through. Other tests ensure unhealthy replicas are not closed, open/closing replicas are sent close commands, read-only mode avoids side effects, empty closing containers close only after a configured timeout, RATIS all-unhealthy closing containers move to quasi-closed, and EC all-unhealthy closing containers move to closed. Parameterized tests verify force-close is true for EC and false for RATIS.

State and persistence behavior: no durable store is modified, but tests verify lifecycle state update calls and report behavior. Time-dependent state uses `TestClock` and `rmConf.getInterval()` to simulate the empty-closing timeout.

Dependencies and integration points: integrates lifecycle state machine events, replication config type, command dispatch, read-only checks, and SCM timing configuration.

Risks: premature state transitions for empty containers can hide late replicas; failing to force-close EC replicas can leave EC containers stuck; closing unhealthy replicas is intentionally avoided.

Test signals: return values, close-command counts and force flags, lifecycle update calls, read-only no-op behavior, and timeout-driven close behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestClosingContainerHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestDeletingContainerHandler.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestDeletingContainerHandler.java

Purpose: verifies `DeletingContainerHandler`, which advances DELETING containers to deleted state when replicas are gone and sends delete commands for remaining empty replicas lacking pending deletes.

Important APIs and types: `DeletingContainerHandler`, `ContainerCheckRequest`, `ContainerReplicaOp.PendingOpType.DELETE`, `ReplicationManager.updateContainerState`, `ReplicationManager.sendDeleteCommand`, `ECReplicationConfig`, and `RatisReplicationConfig`.

Control flow: negative tests cover non-DELETING EC/RATIS containers. Cleanup tests build DELETING containers with no replicas and verify read-only mode suppresses state update while normal mode updates. Delete-resend tests compare replicas with complete pending deletes, partial pending deletes, and no pending deletes. Non-empty replicas must not receive delete commands.

State and persistence behavior: modeled state is lifecycle transition to deleted and pending delete operations. Read-only requests must not mutate lifecycle state. The handler only sends deletes for empty replicas, avoiding data loss.

Dependencies and integration points: integrates container lifecycle, pending-op tracking, replica emptiness, EC/RATIS replica indexes, and replication-manager command APIs.

Risks: resending deletes without checking pending ops can duplicate work; deleting non-empty replicas would be unsafe; failing to mark no-replica containers deleted can leave stale metadata.

Test signals: handler return values, lifecycle update invocation counts, and delete-command counts for RATIS and EC cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestDeletingContainerHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestECMisReplicationCheckHandler.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestECMisReplicationCheckHandler.java

Purpose: tests EC placement-policy mis-replication detection and queueing behavior.

Important APIs and types: `ECMisReplicationCheckHandler`, `PlacementPolicy.validateContainerPlacement`, `ContainerPlacementStatusDefault`, `ContainerHealthResult`, `ReplicationQueue`, `ContainerReplicaOp`, and `ContainerHealthState.MIS_REPLICATED`.

Control flow: setup mocks placement as satisfied by default and builds a request with queue, report, pending ops, and maintenance redundancy. Tests assert healthy EC containers and non-EC containers return false. Mis-replicated EC containers are queued to the under-replicated queue and counted as `MIS_REPLICATED`. Pending ADD can make placement OK after pending and suppress queueing. A pending DELETE for an excess unhealthy replica can also suppress queueing.

State and persistence behavior: queue and report counters are the mutable state. Pending ADD/DELETE records alter whether the current violation needs active processing.

Dependencies and integration points: depends on EC replication configs, placement-policy validation, pending operations, and the replication queue used by the manager.

Risks: placement status must be evaluated with the correct datanode set after pending operations. Mis-replication is queued on the under-replicated path, so prioritization and processor behavior matter.

Test signals: health-state result, handler return, queue sizes, and exact report counters for under/over/mis replication.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestECMisReplicationCheckHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestECReplicationCheckHandler.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestECReplicationCheckHandler.java

Purpose: exhaustively tests EC health classification for under-replication, over-replication, unrecoverable/missing/unhealthy states, out-of-service replicas, pending operations, and precedence among under/over/mis conditions.

Important APIs and types: `ECReplicationCheckHandler`, `ContainerHealthResult.UnderReplicatedHealthResult`, `OverReplicatedHealthResult`, `ReplicationQueue`, `ContainerReplicaOp` ADD/DELETE, `ContainerHealthState`, `ECReplicationConfig`, `NodeOperationalState`, and `ContainerReplicaProto.State.UNHEALTHY`.

Control flow: setup uses EC 3-2, queue, report, and maintenance redundancy. Tests call `checkHealth` for direct result details and `handle` for queue/report effects. Cases include healthy full sets, missing indexes, pending adds, decommission/maintenance-driven under-replication, unrecoverable data loss, unhealthy replicas, offline indexes with and without pending repair, excess replicas, pending deletes, maintenance over-replication ignored as healthy, and combinations where under-replication takes precedence over over/mis-replication while over-replication takes precedence over mis-replication.

State and persistence behavior: no persistence. State under test is report counters and queue contents. Pending operations can suppress queue insertion while still leaving report counters incremented because the current physical state is not yet repaired.

Dependencies and integration points: integrates EC replica-index math, maintenance redundancy policy, out-of-service node semantics, pending operations, and report/queue contracts consumed by `ReplicationManager`.

Risks: EC safety hinges on distinguishing recoverable missing indexes from unrecoverable data loss and on not treating maintenance extras as harmful over-replication. Combined states such as `MISSING_UNDER_REPLICATED` and `UNHEALTHY_UNDER_REPLICATED` are sensitive to classification order.

Test signals: direct assertions on remaining redundancy, `isReplicatedOkAfterPending`, `underReplicatedDueToOutOfService`, `isUnrecoverable`, offline-index flags, queue sizes, and all relevant health counters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestECReplicationCheckHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestEmptyContainerHandler.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestEmptyContainerHandler.java

Purpose: tests `EmptyContainerHandler`, which detects empty closed/quasi-closed containers and deletes their replicas before updating container state.

Important APIs and types: `EmptyContainerHandler`, `ContainerCheckRequest`, `ReplicationManager.sendDeleteCommand`, `ReplicationManager.updateContainerState`, `ContainerHealthState.EMPTY`, `ECReplicationConfig`, `RatisReplicationConfig`, and lifecycle states `CLOSED`, `CLOSING`, `QUASI_CLOSED`.

Control flow: tests verify empty closed EC and RATIS containers return true, increment `EMPTY`, send delete commands in normal mode, and suppress commands in read-only mode. Non-closed empty containers, non-empty containers, and empty containers with a non-empty replica return false. Empty containers with no replicas still count as empty. A sequence-id test ensures state is not updated when no replica sequence matches the container. Quasi-closed RATIS empty containers are also handled.

State and persistence behavior: no durable state changes occur, but lifecycle update calls are verified. Empty is defined by key count rather than bytes used, and replica emptiness must agree before deletion. Read-only mode only reports.

Dependencies and integration points: integrates replica key/byte metadata, sequence ID checks, delete commands, lifecycle events, and report counters.

Risks: deleting replicas for a container that only appears empty due to stale metadata would be unsafe. The sequence-id guard prevents advancing state based on unrelated stale replicas.

Test signals: handler result, delete-command counts, `EMPTY` report count, lifecycle update calls, read-only behavior, and sequence-id mismatch behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestEmptyContainerHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestMismatchedReplicasHandler.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestMismatchedReplicasHandler.java

Purpose: verifies `MismatchedReplicasHandler`, which sends close commands to replicas whose state does not match a closed or quasi-closed container while letting later handlers continue health processing.

Important APIs and types: `MismatchedReplicasHandler`, `ContainerCheckRequest`, `ReplicationManager.sendCloseContainerReplicaCommand`, `ECReplicationConfig`, `RatisReplicationConfig`, `ContainerReplicaProto.State`, and container sequence IDs.

Control flow: tests confirm open containers and already-healthy closed EC/RATIS containers return false without commands. Mismatched EC and RATIS replicas in OPEN/CLOSING state get close commands, while UNHEALTHY replicas do not. The handler always returns false so under/over-replication handlers can continue. Quasi-closed RATIS mismatches are closed without force. Quasi-closed replicas of closed containers are force-closed only when sequence IDs match. A BCSID-focused case verifies force behavior for quasi-closed matching sequence and non-force behavior for open/closing replicas with older or matching sequence.

State and persistence behavior: no persistent state; the side effect is close-command dispatch. Read-only requests do not generate additional commands.

Dependencies and integration points: integrates replica-state cleanup with replication-manager close-command APIs and downstream health-handler chaining.

Risks: returning true would short-circuit later repair. Force-close semantics differ by replication type and replica state, and incorrect sequence handling can close the wrong data.

Test signals: command invocation counts and force flags, negative checks for unhealthy replicas, read-only suppression, and explicit false return values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestMismatchedReplicasHandler.java -->
