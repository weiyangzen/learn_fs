# subset-b-008045 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestOpenContainerHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestOpenContainerHandler.java

Purpose: This test suite verifies `OpenContainerHandler`, the replication-health handler that recognizes SCM containers still in `OPEN` state and decides whether they should remain open or be closed by Replication Manager. It covers both EC and Ratis replication configs.

Important APIs and types: The tests build `ContainerInfo` and `ContainerReplica` sets with `ReplicationTestUtil`, `ECReplicationConfig`, `RatisReplicationConfig`, `ContainerCheckRequest`, `ReplicationManagerReport`, and a mocked `ReplicationManager`. The key production calls under observation are `OpenContainerHandler.handle`, `ReplicationManager.hasHealthyPipeline`, and `ReplicationManager.sendCloseContainerEvent`.

Control flow: Setup defaults the mocked replication manager to report a healthy pipeline. Closed containers are ignored. Healthy open containers with open replicas are handled but not closed. Open containers with non-open replica state or no healthy pipeline are handled and, on non-read-only requests, cause one close-container event. The same scenarios are repeated for Ratis containers with replica index `0`.

State and persistence behavior: There is no durable state. Runtime state is the request's container state, replica states, read-only flag, and report counters. The test ensures read-only requests still compute health but do not emit extra close events.

Dependencies and integration points: This is a unit-level guard for the replication health check chain, Replication Manager pipeline knowledge, close-container event dispatch, and `ReplicationManagerReport` statistics.

Risks: The tests rely on Mockito call counts to distinguish mutating and read-only behavior. They do not validate downstream close-event processing or pipeline lookup internals.

Test signals: Key signals are false for closed containers, true for open containers, exactly one close event for unhealthy or no-pipeline non-read-only checks, and one report increment for `OPEN_UNHEALTHY` or `OPEN_WITHOUT_PIPELINE`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestOpenContainerHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestQuasiClosedContainerHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestQuasiClosedContainerHandler.java

Purpose: This suite validates `QuasiClosedContainerHandler`, which force-closes eligible Ratis `QUASI_CLOSED` containers once enough safe replicas exist. It explicitly excludes EC and open containers.

Important APIs and types: The tests use `QuasiClosedContainerHandler`, `ReplicationManager.sendCloseContainerReplicaCommand`, `ContainerCheckRequest`, `ReplicationManagerReport`, `ContainerHealthState.QUASI_CLOSED_STUCK`, `RatisReplicationConfig`, `ContainerReplica`, and `HddsTestUtils.getContainer/getReplicas` helpers for precise sequence ID and origin-node construction.

Control flow: Setup creates a mocked `ReplicationManager` and handler. Non-Ratis and open containers return false. Quasi-closed containers with insufficient unique origins, duplicate origins, or open replicas are not force-closed and may be counted as stuck. Containers with all unique origins and equal highest BCSID send close commands for eligible replicas. Read-only requests re-run the logic but do not add additional commands.

State and persistence behavior: The suite is memory-only. State under test is replica state, BCSID/sequence ID, origin datanode ID uniqueness, datanode identity, and the request read-only flag.

Dependencies and integration points: It anchors the Replication Manager interaction that sends close-replica commands to datanodes and protects the Ratis-only semantics used before regular under/over replication repair.

Risks: Eligibility depends on subtle BCSID and origin rules. A replica with the highest sequence ID but `UNHEALTHY` state can prevent force close, while only highest-BCSID quasi-closed replicas should receive commands.

Test signals: Assertions verify no command for EC/open/stuck cases, report increments for stuck cases, command counts for all-unique cases, and exact datanodes selected when only some replicas have the highest BCSID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestQuasiClosedContainerHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestQuasiClosedStuckReplicationCheck.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestQuasiClosedStuckReplicationCheck.java

Purpose: This class tests `QuasiClosedStuckReplicationCheck`, the health check for quasi-closed containers that cannot be force-closed normally and need missing, under-replicated, or over-replicated repair handling.

Important APIs and types: It uses `QuasiClosedStuckReplicationCheck`, `ReplicationManager.ReplicationManagerConfiguration`, `ReplicationManagerReport`, `ReplicationQueue`, `ContainerCheckRequest`, `ContainerReplicaOp`, `ContainerHealthState.QUASI_CLOSED_STUCK_*`, and `ReplicationTestUtil` helpers for origin and sequence-ID controlled replicas.

Control flow: Setup creates real Replication Manager configuration from `OzoneConfiguration`, a fresh report, and a queue. Closed containers, non-stuck quasi-closed containers, and quasi-closed containers that still have an open replica are ignored. Missing containers are reported but not queued. Under-replicated stuck containers are queued unless a pending add already addresses them. Over-replicated stuck containers are queued unless a pending delete already addresses them.

State and persistence behavior: The state is in-memory replica origin grouping, sequence IDs, pending add/delete operations, report counters, and queue contents. No DB or filesystem persistence is involved.

Dependencies and integration points: This test integrates with the replication queue contract used by Replication Manager's later command-generation stage and with the combined health-state reporting model for quasi-closed stuck containers.

Risks: The handler distinguishes "not handled" from "handled but not queued" based on pending operations and missing-replica state. Those paths can easily regress if generic Ratis replication logic changes.

Test signals: Strong signals are queue sizes, report counters for `QUASI_CLOSED_STUCK_UNDER_REPLICATED`, `QUASI_CLOSED_STUCK_OVER_REPLICATED`, and `QUASI_CLOSED_STUCK_MISSING`, and boolean return values showing whether the handler consumed the request.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestQuasiClosedStuckReplicationCheck.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestRatisReplicationCheckHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestRatisReplicationCheckHandler.java

Purpose: This is the main unit suite for `RatisReplicationCheckHandler`, covering Ratis container health classification and enqueue behavior for under-replication, over-replication, mis-replication, maintenance/decommission scenarios, unhealthy replicas, mismatched replica states, and quasi-closed sequence-ID edge cases.

Important APIs and types: It exercises `RatisReplicationCheckHandler.checkHealth` and `handle`, `ContainerHealthResult` subtypes (`UnderReplicatedHealthResult`, `OverReplicatedHealthResult`, `MisReplicatedHealthResult`), `ReplicationQueue`, `ReplicationManagerReport`, `PlacementPolicy.validateContainerPlacement`, `ContainerPlacementStatusDefault`, `NodeStatus`, `ContainerReplicaOp`, and `ReplicationTestUtil` replica builders.

Control flow: Setup mocks placement as initially satisfied and node status as in-service healthy. Tests first reject non-Ratis containers, then inspect direct health results before checking `handle` side effects. Under-replicated paths vary live replica count, pending deletes, pending adds, out-of-service nodes, all-out-of-service parameterized node states, unrecoverable no-replica cases, and unhealthy replicas. Over-replicated paths vary extra healthy replicas, unhealthy excess, mismatched replicas, pending deletes, maintenance replicas, and safe-over-replication gating. Mis-replication is injected by mocking placement failure and verifying whether it queues as under-replication. Quasi-closed tests validate sequence ID compatibility and unique origin behavior.

State and persistence behavior: There is no durable state. Runtime state includes replica state, datanode operational state, sequence ID, origin datanode ID, pending operations, placement result, request maintenance redundancy, report counters, and queue entries.

Dependencies and integration points: This suite is the compatibility anchor between the Ratis replica-counting policy, placement policy, Replication Manager node status lookup, report counters, and work queues consumed by replication/deletion processors.

Risks: The class encodes many overlapping conditions where a container can be under-replicated, over-replicated, mis-replicated, or temporarily fixed by pending operations. It also protects special behavior for all-unhealthy replicas and quasi-closed origins that generic counting could mishandle.

Test signals: Signals include exact health-state subtype, remaining or excess redundancy, `isReplicatedOkAfterPending`, `underReplicatedDueToOutOfService`, `isUnrecoverable`, mismatched/safe-over-replication flags, queue sizes, and report counters for `UNDER_REPLICATED`, `OVER_REPLICATED`, `MIS_REPLICATED`, and `MISSING`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestRatisReplicationCheckHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestRatisUnhealthyReplicationCheckHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestRatisUnhealthyReplicationCheckHandler.java

Purpose: This suite verifies `RatisUnhealthyReplicationCheckHandler`, which handles Ratis containers whose usable replicas are `UNHEALTHY` or quasi-closed with stale sequence IDs. It deliberately avoids cases owned by the normal Ratis handler.

Important APIs and types: It uses `RatisUnhealthyReplicationCheckHandler`, `ContainerHealthResult.UnderReplicatedHealthResult`, `ContainerHealthResult.OverReplicatedHealthResult`, `ReplicationQueue`, `ReplicationManagerReport`, `ContainerReplicaOp`, `ContainerHealthState.UNHEALTHY`, `UNHEALTHY_UNDER_REPLICATED`, and `UNHEALTHY_OVER_REPLICATED`.

Control flow: Non-Ratis, normally healthy, normally under-replicated, normally over-replicated, and excess-unhealthy-with-sufficient-healthy cases return false. All-unhealthy sets are classified as unhealthy, under-replicated, or over-replicated based on replica count and pending operations. Pending add/delete can prevent queue insertion while still recording the combined unhealthy state. Quasi-closed replicas with correct sequence IDs are ignored, while stale sequence IDs are treated as unhealthy and can produce under/over replication handling.

State and persistence behavior: Runtime-only state includes replica state, sequence ID, pending ops, report counters, and queue sizes. No persistent storage is touched.

Dependencies and integration points: It complements `RatisReplicationCheckHandler` by separating vulnerable unhealthy-replica repair from normal healthy-replica repair, while sharing the same `ContainerCheckRequest`, queue, and report contracts.

Risks: The boundary between "normal Ratis over-replication owns this" and "unhealthy handler owns this" is subtle. Combined report states intentionally replace separate unhealthy plus under/over counters.

Test signals: The tests assert boolean handling, health-result subtype and redundancy values, pending-operation flags, queue sizes, and that only combined unhealthy counters are incremented for under/over unhealthy cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestRatisUnhealthyReplicationCheckHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestVulnerableUnhealthyReplicasHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestVulnerableUnhealthyReplicasHandler.java

Purpose: This suite validates `VulnerableUnhealthyReplicasHandler`, which tries to save unhealthy quasi-closed Ratis replicas that are on vulnerable operational-state nodes and represent a unique origin copy worth preserving.

Important APIs and types: It uses `VulnerableUnhealthyReplicasHandler`, mocked `ReplicationManager.getNodeStatus`, `NodeStatus`, `ReplicationQueue`, `ContainerCheckRequest`, `RatisReplicationConfig`, `ECReplicationConfig`, and `ReplicationTestUtil.createContainerReplica` overloads for sequence ID and origin control.

Control flow: The handler ignores EC containers, closed containers, quasi-closed containers with no unhealthy replicas, and unhealthy replicas that are not vulnerable because another replica has the same origin. It queues under-replication for an unhealthy replica on a decommissioning node when that replica has a unique origin and correct sequence ID, even if the quasi-closed replicas have correct sequence IDs. A read-only request still returns true for detection but does not enqueue work.

State and persistence behavior: All state is in memory: container lifecycle state, replica states, sequence IDs, origins, datanode operational status, read-only flag, and queue contents.

Dependencies and integration points: The test guards the interaction between container health checking and Replication Manager's node status service. It is specifically about preserving quorum/recovery options for quasi-closed containers during decommission-like transitions.

Risks: The value of an unhealthy replica depends on origin uniqueness, not just count. A naive repair path could delete or ignore a vulnerable unique-origin copy before it can be restored or used for closure.

Test signals: Signals are zero queues for ignored cases, one under-replication queue entry for vulnerable unique-origin unhealthy replicas, mocked node-status branching, and no queue entry for read-only detection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestVulnerableUnhealthyReplicasHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/package-info.java

Purpose: This package descriptor documents that the package contains tests for HDDS replication health-check classes.

Important APIs and types: It declares the package `org.apache.hadoop.hdds.scm.container.replication.health` and contains only package-level Javadoc.

Control flow: There is no runtime control flow.

State and persistence behavior: There is no state or persistence.

Dependencies and integration points: The descriptor supports Checkstyle/Javadoc hygiene for the health test package and groups the handler suites for open, quasi-closed, Ratis, unhealthy, and vulnerable replica checks.

Risks: None beyond becoming stale if package purpose changes.

Test signals: Compilation and Checkstyle are the only signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/package-info.java

Purpose: This package descriptor labels the test package for SCM container replication functionality.

Important APIs and types: It declares `org.apache.hadoop.hdds.scm.container.replication` and contains only package-level Javadoc.

Control flow: There is no executable flow.

State and persistence behavior: No state or persistence exists in this file.

Dependencies and integration points: It provides package documentation for replication-related test classes outside the health subpackage.

Risks: Minimal; it can only become inaccurate if the package's test scope changes.

Test signals: Compilation and Checkstyle/Javadoc validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/report/TestContainerReportValidator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/report/TestContainerReportValidator.java

Purpose: This compact suite verifies `ContainerReportValidator.validate` for EC container replica indexes reported by datanodes.

Important APIs and types: It uses `ContainerReportValidator`, `ContainerReplicaProto`, `ContainerInfo`, `ContainerID`, `DatanodeDetails`, `ECReplicationConfig(3,2)`, `PipelineID`, `HddsTestUtils.getECContainer`, and `HddsTestUtils.createContainerReplica`.

Control flow: A helper builds a closed container replica protobuf for a given replica index and datanode. The valid test creates a 3+2 EC container and asserts index `1` is accepted. The parameterized invalid test checks indexes `0`, `6`, `100`, and `-1` are rejected for a five-replica EC layout.

State and persistence behavior: There is no persistence. The test state is the EC replication config, replica index field, container ID, and datanode UUID in the report protobuf.

Dependencies and integration points: This protects SCM's container report ingestion path, where datanode-reported EC replica indexes must fit the container's data+parity index range.

Risks: If EC index rules change or become layout-specific, the hard-coded invalid range must be updated. The suite does not cover Ratis containers or mismatched datanode identity behavior.

Test signals: `validate` returns true for an in-range EC replica index and false for zero, out-of-range, large, and negative indexes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/report/TestContainerReportValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/report/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/report/package-info.java

Purpose: This package descriptor exists to satisfy package documentation requirements for SCM container report tests.

Important APIs and types: It declares `org.apache.hadoop.hdds.scm.container.report` and contains only package Javadoc.

Control flow: There is no runtime flow.

State and persistence behavior: None.

Dependencies and integration points: It documents the package that includes `TestContainerReportValidator`.

Risks: None beyond stale wording.

Test signals: Compilation and Checkstyle/Javadoc validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/report/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/states/TestContainerAttribute.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/states/TestContainerAttribute.java

Purpose: This suite tests `ContainerAttribute`, the generic index structure that maps enum attributes to ordered `ContainerID -> ContainerInfo` collections.

Important APIs and types: It uses `ContainerAttribute<Key>`, `ContainerID`, `ContainerInfo`, `SCMException`, `NavigableMap`, and an internal enum `Key { K1, K2, K3 }`. Helpers `hasContainerID` inspect a key bucket directly.

Control flow: `testAddNonExisting` adds one container and verifies duplicate add throws `IllegalStateException`. `testClearSet` fills all enum buckets with 100 containers and clears one bucket. `testRemove` removes odd IDs from one bucket while confirming other buckets are untouched. `tesUpdate` moves an ID between buckets and verifies updating from a bucket that does not contain the ID throws `SCMException`.

State and persistence behavior: State is entirely in-memory ordered maps per enum key. No DB or filesystem is involved.

Dependencies and integration points: `ContainerAttribute` underpins SCM container state indexing and fast lookup by lifecycle or other enum dimensions. The test guards bucket isolation, duplicate protection, and atomic move semantics.

Risks: A regression in add/remove/update can corrupt state indexes even if the canonical container table is correct. The test does not cover concurrency.

Test signals: Assertions cover collection sizes, map membership, duplicate-add failure, clear behavior, odd-ID removal, successful movement across buckets, and missing-source update failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/states/TestContainerAttribute.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/states/TestContainerStateMap.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/states/TestContainerStateMap.java

Purpose: This test verifies `ContainerStateMap.getContainerIDs` filtering and pagination by container lifecycle state.

Important APIs and types: It uses `ContainerStateMap`, `ContainerInfo`, `ContainerID`, `HddsProtos.LifeCycleState`, and `StandaloneReplicationConfig` with replication factor THREE.

Control flow: The test builds ten containers with known IDs and states, adds them to a new `ContainerStateMap`, and queries IDs by state. It asserts there are four `OPEN` and four `CLOSED` containers, then verifies pagination for closed containers from `ContainerID.MIN` and from `ContainerID.valueOf(7)` with limit three.

State and persistence behavior: State is an in-memory state map populated from constructed `ContainerInfo` objects. No persistence is touched.

Dependencies and integration points: This guards the SCM container-state indexing behavior used by list and scan operations that page through container IDs by lifecycle state.

Risks: Off-by-one errors in start ID or limit handling would affect API pagination. The test only exercises adds and reads, not state transitions or removal.

Test signals: Exact result sizes for state-filtered lookup and limit-bounded pagination.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/states/TestContainerStateMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/states/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/states/package-info.java

Purpose: This package descriptor exists for SCM container state tests and Checkstyle compliance.

Important APIs and types: It declares `org.apache.hadoop.hdds.scm.container.states` and contains package-level Javadoc only.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: It documents the package that holds tests for `ContainerAttribute` and `ContainerStateMap`.

Risks: None beyond stale wording.

Test signals: Compilation and package documentation checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/states/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/SCMRatisProtocolCompatibilityTestUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/SCMRatisProtocolCompatibilityTestUtil.java

Purpose: This utility supports SCM Ratis protocol compatibility tests by constructing random proto2-format method arguments, responses, and requests for the test-only legacy schema.

Important APIs and types: It uses `Proto2SCMRatisProtocolForTesting`, protobuf `ByteString`, `ByteBuffer`, and static random/type fixtures from `TestSCMRatisProtocolCompatibility`. Helpers include `randomValueProto2`, `randomProto2MethodArgument`, `randomProto2SCMRatisResponseProto`, and `proto2Request`.

Control flow: `randomValueProto2` chooses encoding by Java type: UTF-8 digits for `String`, four-byte big-endian integers for `Integer`, and random byte arrays for `byte[]`. Request builders attach a method name, request type, and the requested number of random arguments.

State and persistence behavior: It is stateless except use of the shared random generator. No persistent data is created.

Dependencies and integration points: It feeds `TestSCMRatisProtocolCompatibility`, which verifies wire compatibility between legacy proto2 and current proto3 SCM Ratis protocol definitions.

Risks: Random small values give broad but not exhaustive coverage. The utility must stay aligned with the production/test protocol type list.

Test signals: Utility correctness is observed indirectly through proto2/proto3 round-trip equality in the compatibility tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/SCMRatisProtocolCompatibilityTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestBackgroundSCMService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestBackgroundSCMService.java

Purpose: This suite verifies `BackgroundSCMService` lifecycle and run gating based on SCM safe mode and a post-safe-mode delay.

Important APIs and types: It uses `BackgroundSCMService.Builder`, `SCMContext`, `TestClock`, `PipelineManager.scrubPipelines`, `SafeModeStatus`, and Mockito timeout verification.

Control flow: Setup creates a service with 1 ms interval/wait values and a periodical task that calls a mocked pipeline manager. `testStop` confirms running state toggles off. `testNotifyStatusChanged` starts paused, exits safe mode but remains delayed, advances the test clock by 60 seconds to permit running, then re-enters safe mode and pauses. `testRun` manually notifies, advances time, calls `runImmediately`, and verifies the task executes.

State and persistence behavior: Runtime state includes service running flag, service status, SCM safe-mode status, and injected clock time. No durable state is involved.

Dependencies and integration points: This guards SCM background services that should run only when their SCM context allows them, especially services whose startup is delayed after safe mode.

Risks: The run test is timing-sensitive despite using a `TestClock`, because it verifies execution through a background thread with a timeout.

Test signals: `shouldRun` transitions, `getRunning` after stop, and at-least-once invocation of `scrubPipelines`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestBackgroundSCMService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestInterSCMGrpcProtocolService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestInterSCMGrpcProtocolService.java

Purpose: This integration-style test verifies that `InterSCMGrpcProtocolService` and `InterSCMGrpcClient` use mutual TLS for SCM checkpoint download.

Important APIs and types: It uses `InterSCMGrpcProtocolService`, `InterSCMGrpcClient`, `SCMCertificateClient`, `ReloadingX509KeyManager`, `ReloadingX509TrustManager`, self-signed test certificates, mocked `StorageContainerManager`, `SCMMetadataStore`, `SCMHAManager`, `DBStore`, `DBCheckpoint`, `TypedTable`, and `TarArchiveInputStream`.

Control flow: The test allocates a free gRPC port, enables Ozone security and gRPC TLS, creates separate service and client key/certificate pairs, spies key/trust managers, starts the service, downloads a checkpoint with the client, then verifies both sides presented their certificates and validated the peer certificate. The checkpoint mock creates a directory containing `cpFile`, and the downloaded tar is opened to validate filename and content.

State and persistence behavior: Temporary certificate objects and a checkpoint directory/file are created under the test temp path. Runtime DB and HA components are mocked except the actual gRPC service/client interaction and tar stream.

Dependencies and integration points: This protects inter-SCM snapshot transfer security, certificate-client integration, DB checkpoint packaging, and transaction-info table access used during download.

Risks: The test depends on local port allocation, TLS handshake behavior, and spy call counts. Cleanup closes the client and stops the service after assertions.

Test signals: Key managers' certificate chains are requested, trust managers validate the opposite side's certificate exactly once, server does not perform server-trust validation, client does not perform client-trust validation, and the downloaded tar contains the expected checkpoint file contents.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestInterSCMGrpcProtocolService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestReplicationAnnotation.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestReplicationAnnotation.java

Purpose: This test verifies that methods annotated for SCM Ratis replication are routed through the `SCMRatisServer` proxy submission path rather than invoked directly.

Important APIs and types: It uses an inline `SCMRatisServer` implementation, `SCMRatisServer.getProxyHandler`, `ContainerStateManagerInvoker`, `ContainerStateManager`, `SCMRatisRequest`, `SCMRatisResponse`, and `RequestType.CONTAINER`.

Control flow: Setup creates a minimal `SCMRatisServer` whose `submitRequest` always throws an `IOException` with a known message. The test wraps a mocked `ContainerStateManager` in a generated invoker/proxy, calls `addContainer`, and asserts the thrown exception contains the proxy-submission marker.

State and persistence behavior: There is no persistence. Runtime state is the proxy, mocked manager type, and thrown exception.

Dependencies and integration points: This guards annotation-driven HA replication plumbing for SCM metadata managers. It confirms the proxy path captures method calls and sends them to Ratis.

Risks: The test only checks one replicated method and uses a stub server; it does not validate serialized arguments or Raft execution.

Test signals: `addContainer` throws the known `submitRequest is called` IOException, proving the proxy intercepted the annotated method.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestReplicationAnnotation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMConfiguration.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMConfiguration.java

Purpose: This suite validates SCM HA configuration expansion, node-specific address/port keys, default Ratis log appender settings, and shared-port configuration behavior.

Important APIs and types: It uses `OzoneConfiguration`, `SCMHANodeDetails.loadSCMHAConfig`, `SCMStorageConfig`, `SCMNodeDetails`, `ScmRatisServerConfig`, `RatisUtil.newRaftProperties`, `ConfUtils.addKeySuffixes`, `NetUtils`, `HddsServerUtil`, and multiple `ScmConfigKeys`.

Control flow: `testSCMConfig` configures one SCM service with three nodes and per-node client, block, datanode, security, HTTP, DB, SCM address, and Ratis port keys. After loading HA config, it verifies node `scm1` values remain in the expected suffixed keys and confirms Ratis log appender min wait is zero both in SCM config and generated Raft properties. `testSamePortConfig` sets shared global ports, loads HA details, and verifies local and peer node details use the shared addresses and ports.

State and persistence behavior: Configuration state is in memory. A temp metadata directory is used only as a config value; no persistent SCM DB is initialized.

Dependencies and integration points: This protects HA config parsing used during SCM startup and port binding, including security service address resolution outside `SCMHANodeDetails`.

Risks: The tests are exact about default ports and key suffix behavior. Any intentional config fallback change must update the assertions.

Test signals: Exact config values, socket addresses, local/peer Ratis and gRPC ports, security address from `HddsServerUtil`, and zero Ratis log appender wait duration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMContext.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMContext.java

Purpose: This compact test verifies `SCMContext` state transitions for Raft leadership and SCM safe mode.

Important APIs and types: It uses `SCMContext.Builder`, `updateLeaderAndTerm`, `setLeaderReady`, `getTermOfLeader`, `updateSafeModeStatus`, and `SafeModeStatus`.

Control flow: The Raft test starts as follower, updates to leader term 10, marks leader ready, then steps down and expects leader-ready to reset. The safe-mode test starts in `INITIAL`, moves to `PRE_CHECKS_PASSED`, then `OUT_OF_SAFE_MODE`, checking both `isInSafeMode` and `isPreCheckComplete`.

State and persistence behavior: State is in-memory context flags and term values. No persistence is involved.

Dependencies and integration points: `SCMContext` is consumed by background services, state machines, and HA role-aware managers to decide whether to run or pause.

Risks: Incorrect leader-ready or safe-mode transitions can cause services to run at the wrong time.

Test signals: Boolean leader, leader-ready, safe-mode, pre-check flags, and exact leader term.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHAManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHAManagerImpl.java

Purpose: This integration-heavy suite verifies `SCMHAManagerImpl` and `SCMRatisServerImpl` behavior for adding/removing SCM peers and rejecting invalid HA-ring removal requests.

Important APIs and types: It uses `SCMHAManagerImpl`, `SCMRatisServerImpl.initialize`, `SCMRatisServer`, `AddSCMRequest`, `RemoveSCMRequest`, `StorageContainerManager`, `SCMHANodeDetails`, `SCMNodeDetails`, `SCMSnapshotProvider`, `DivisionInfo`, `GenericTestUtils.waitFor`, and many mocked SCM subsystems.

Control flow: `BeforeAll` creates a leader SCM manager with local Ratis storage/metadata dirs, starts it, waits until its Ratis division is leader-ready, then creates a follower SCM manager. `testAddSCM` starts the follower and adds it to the leader's Ratis group, increasing peer count from one to two. `testRemoveSCM` removes the follower and expects peer count one. `testHARingRemovalErrors` creates an SCM via `HddsTestUtils.getScm` and verifies removing a non-peer or the current leader produces an IOException with identifying text.

State and persistence behavior: The test creates temporary Ratis and metadata directories for leader and follower. Runtime state includes live Ratis server peer membership and mocked SCM metadata/transaction components.

Dependencies and integration points: It stitches together HA manager startup, Ratis peer group mutation, snapshot-provider override, SCM service wiring, and StorageContainerManager HA ring API validation.

Risks: The ordered tests depend on prior peer count and live local Ratis servers. Port use is fixed for leader/follower mocks, so environment conflicts are possible.

Test signals: Ratis division leader readiness, peer count changes 1 -> 2 -> 1, follower start/stop, and expected errors for removing non-peer or leader SCM IDs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHAManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHAMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHAMetrics.java

Purpose: This test verifies the leader-state metric exposed by `SCMHAMetrics`.

Important APIs and types: It uses `SCMHAMetrics.create`, `getMetrics`, `getSCMHAMetricsInfoLeaderState`, `MetricsCollectorImpl`, and random SCM node IDs from `RandomStringUtils`.

Control flow: One test creates metrics with local node ID equal to leader ID and expects leader state `1`. The other creates metrics with a different leader ID and expects leader state `0`. `AfterEach` unregisters the metrics source.

State and persistence behavior: State is runtime metrics registration and current leader/local SCM IDs. No persistence.

Dependencies and integration points: This guards SCM HA metrics consumed by monitoring systems to identify whether an SCM instance is leader or follower.

Risks: The static metrics registration must be cleaned up to avoid cross-test pollution.

Test signals: Exact metric integer values for leader and follower modes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHAMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHATransactionBufferMonitorTask.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHATransactionBufferMonitorTask.java

Purpose: This suite tests race-sensitive persistence behavior between `SCMHATransactionBufferMonitorTask` and `SCMHADBTransactionBufferImpl`, especially ensuring monitor flushes do not persist buffered data with stale transaction indexes while a Ratis transaction is being applied.

Important APIs and types: It uses real `SCMMetadataStoreImpl`, `SCMHADBTransactionBufferImpl`, `SCMHATransactionBufferMonitorTask`, `Table<String, ByteString>` for stateful service config, `Table<String, TransactionInfo>` for transaction info, `TRANSACTION_INFO_KEY`, mocked `StorageContainerManager`, and an injected `Clock` backed by `AtomicLong`.

Control flow: Setup opens a real SCM metadata store and creates a transaction buffer with a mock clock. Tests first demonstrate the old race when `shouldFlush` and `flush` are called separately and when `flush` is called directly inside an apply window. Then they verify `flushIfNeeded` skips during `beginApplyingTransaction`/`endApplyingTransaction`, including zero-wait calls and a concurrent monitor thread loop, and only flushes after the latest transaction info is updated.

State and persistence behavior: Persistent state is written to temporary SCM DB tables. The tests assert exact on-disk table values for the buffered service config and transaction info. Runtime state includes latest transaction info, apply-in-progress flag, buffer contents, and clock-based flush interval.

Dependencies and integration points: This is a high-value guard for HA state-machine apply, DB transaction buffering, stateful service configuration persistence, and background monitor scheduling.

Risks: Race coverage uses threads and latches; missed synchronization would cause flaky or stale-transaction writes. The test intentionally documents old unsafe behavior as contrast for the guarded API.

Test signals: `statefulServiceConfigTable.get("key")` remains null during apply, later equals `value`, and `transactionInfoTable.get(TRANSACTION_INFO_KEY)` stays at T4 for unsafe paths but reaches T5 for deferred safe paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHATransactionBufferMonitorTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisProtocolCompatibility.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisProtocolCompatibility.java

Purpose: This suite validates wire compatibility between legacy proto2 and current proto3 definitions of `SCMRatisProtocol` requests and responses.

Important APIs and types: It uses production `SCMRatisProtocol`, test-only `Proto2SCMRatisProtocolForTesting`, proto2 and Ratis-shaded proto3 `ByteString`, `UnsafeByteOperations`, Java `Random`, and helper methods from `SCMRatisProtocolCompatibilityTestUtil`.

Control flow: The tests generate proto2 requests for each legacy request type and 0-2 arguments, parse them with proto3, verify presence and values, compare string/debug forms, and round-trip back to proto2. Response tests do the same with random proto2 responses. The reverse direction builds proto3 requests/responses, skips default/UNRECOGNIZED request types that cannot satisfy proto2 required fields, parses with proto2, verifies fields, and round-trips back to proto3. `testRequestType` ensures enum numbers and names match.

State and persistence behavior: There is no persistence. Test state is random small strings, integers, byte arrays, method names, request types, and encoded protobuf bytes.

Dependencies and integration points: This is a compatibility anchor for SCM HA/Ratis rolling upgrades where old and new SCMs may exchange replicated method calls and responses.

Risks: Random coverage is small per run, so it guards schema compatibility more than value-space exhaustion. Presence semantics are important because proto3 optional fields must preserve proto2 required data.

Test signals: Successful parse both directions, matching enum numbers, matching method/argument/response byte values, equal short debug strings, and exact round-trip message equality.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisProtocolCompatibility.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisRequest.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisRequest.java

Purpose: This suite tests `SCMRatisRequest` encoding/decoding for replicated SCM method calls and its validation of malformed request protobufs.

Important APIs and types: It uses `SCMRatisRequest.of`, `encode`, `decode`, `SCMRatisProtocol.SCMRatisRequestProto`, `SCMRatisProtocol.MethodArgument`, `RequestType.PIPELINE`, `PipelineID`, `HddsProtos.PipelineID`, Ratis `Message`, `ByteString`, `UnsafeByteOperations`, and `InvalidProtocolBufferException`.

Control flow: Success tests encode/decode a protobuf pipeline ID argument, a list of pipeline ID protobufs, and a `Long`. Failure tests attempt to encode a non-protobuf `PipelineID`, decode a non-protobuf message, and decode request protos missing request type, method, method name, argument type, or argument value.

State and persistence behavior: There is no persistence. Runtime state is serialized request messages and decoded operation/argument arrays.

Dependencies and integration points: This protects the request serialization path used by SCM Ratis proxies and invokers. Explicit missing-field validation is especially important after proto3 migration.

Risks: Reflection-based argument decoding must stay aligned with allowed argument classes and collection codecs. Non-protobuf values should fail predictably rather than being silently corrupted.

Test signals: Successful round-trip equality for supported arguments and `InvalidProtocolBufferException` messages containing "Missing request type", "Missing method", "Missing method name", "Missing argument type", and "Missing argument value".
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisResponse.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisResponse.java

Purpose: This suite tests `SCMRatisResponse` decoding from Ratis client replies and response encoding validation.

Important APIs and types: It uses `SCMRatisResponse.decode`, `SCMRatisResponse.encode`, `RaftClientReply`, `RaftGroupMemberId`, `RaftPeerId`, `RaftGroupId`, `ClientId`, `Message`, `LeaderNotReadyException`, `RaftException`, `SCMRatisProtocol.SCMRatisResponseProto`, and `InvalidProtocolBufferException`.

Control flow: Setup creates a reusable raft member ID. The success test decodes a successful reply with `Message.EMPTY` and verifies the result can be encoded back as an object response. The failure reply test decodes a `LeaderNotReadyException` and verifies response success is false, exception is a `RaftException`, and result is null. Additional tests reject encoding a non-protobuf `Message` object and decoding response protos missing type or value.

State and persistence behavior: There is no persistence. State is the Ratis reply metadata, success flag, exception, and serialized response payload.

Dependencies and integration points: This protects the client-side response handling path for SCM Ratis requests, including preserving Raft exceptions and validating proto3 required-equivalent fields.

Risks: Missing-field handling must remain strict to avoid treating malformed replicated responses as valid null/default values.

Test signals: Success flag/result checks, exception type preservation, non-protobuf encode failure, and missing type/value exception messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisServerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisServerImpl.java

Purpose: This test verifies `SCMRatisServerImpl.getLeaderId` returns the current Ratis leader peer ID or null when no leader is known.

Important APIs and types: It uses `SCMRatisServerImpl`, mocked construction for `SecurityConfig`, static mocks for `RaftServer.newBuilder` and `RatisUtil.newRaftProperties`, mocked `RaftServer.Builder`, `RaftServer`, `RaftServer.Division`, `SCMStateMachine`, `RaftPeer`, and `RaftPeerId`.

Control flow: The test mocks enough construction plumbing to instantiate a spied `SCMRatisServerImpl` without a real Raft server. It stubs `getLeader` to return a `RaftPeer` with ID `peer1`, asserts `getLeaderId` returns that ID, then stubs `getLeader` to null and asserts `getLeaderId` returns null.

State and persistence behavior: No persistent state is created. Runtime state is fully mocked construction and spy behavior.

Dependencies and integration points: This isolates a small leader lookup contract used by SCM HA status, metrics, and request routing.

Risks: Heavy static/construction mocking means the test guards method behavior but not full server initialization.

Test signals: Exact `RaftPeerId.valueOf("peer1")` result and null result when leader is absent.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisServerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMServiceManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMServiceManager.java

Purpose: This suite verifies `SCMServiceManager` propagates SCM context changes to registered services, letting services implement their own leader/safe-mode run conditions.

Important APIs and types: It uses `SCMServiceManager`, `SCMService`, `SCMService.ServiceStatus`, `SCMContext`, and `SafeModeStatus`.

Control flow: Each test creates an inline `SCMService` whose `notifyStatusChanged` sets internal status from a shared `SCMContext`. The first service runs whenever SCM is leader, regardless of safe mode. The second service runs only when SCM is both leader and out of safe mode. The manager registers the service, then context transitions through out-of-safe-mode, leader, in-safe-mode, and step-down states while assertions check `shouldRun`.

State and persistence behavior: State is in-memory service status plus `SCMContext` leader and safe-mode flags. No persistence exists.

Dependencies and integration points: This guards background and HA-aware SCM services that depend on notification fan-out from `SCMServiceManager`.

Risks: Because services decide their own policy, manager regressions would show as missed notification transitions rather than direct policy failure.

Test signals: `shouldRun` toggles exactly according to leader-only and leader-plus-out-of-safe-mode policies.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMServiceManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMSnapshotProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMSnapshotProvider.java

Purpose: This test verifies `SCMSnapshotProvider` constructor validation for configured SCM HA Ratis storage and snapshot directories.

Important APIs and types: It uses `SCMSnapshotProvider`, `SCMHAUtils.getSCMRatisDirectory`, `SCMHAUtils.getSCMRatisSnapshotDirectory`, `OzoneConfiguration`, `HddsConfigKeys.OZONE_METADATA_DIRS`, `ScmConfigKeys.OZONE_SCM_HA_RATIS_STORAGE_DIR`, `OZONE_SCM_HA_RATIS_SNAPSHOT_DIR`, and a mocked `CertificateClient`.

Control flow: The success test creates both configured Ratis and snapshot directories and asserts the provider is constructed with the expected snapshot directory. Failure tests create only Ratis storage or no directories and assert `IllegalStateException` messages for missing snapshot or missing storage directories.

State and persistence behavior: Temporary directories are created under JUnit temp paths. No SCM DB or snapshot content is written.

Dependencies and integration points: This protects follower catch-up/snapshot-provider startup from silently using missing or wrong directories.

Risks: Constructor behavior is strict; deployments or tests that previously expected auto-create semantics would fail intentionally.

Test signals: Provider non-null with exact snapshot path, and exception messages containing "Ratis snapshot directory does not exist" or "Ratis storage directory does not exist".
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMSnapshotProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMStateMachine.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMStateMachine.java

Purpose: This compact test verifies that `SCMStateMachine` records Ratis configuration-change events into SCM metrics.

Important APIs and types: It uses `SCMStateMachine`, `SCMMetrics`, mocked `StorageContainerManager`, mocked `SCMHADBTransactionBuffer`, `TransactionInfo`, `TermIndex`, and `RaftConfigurationProto`.

Control flow: The test creates SCM metrics, wires them into a mocked SCM, stubs the transaction buffer's latest transaction info, constructs an `SCMStateMachine`, calls `notifyConfigurationChanged`, and asserts the metrics event log contains the configuration-change text. Metrics are unregistered at the end.

State and persistence behavior: Runtime metrics state is mutated. No persistent DB is touched.

Dependencies and integration points: This guards observability for SCM HA/Ratis state-machine events.

Risks: Exact event text is a diagnostics contract. The test does not validate other state-machine callbacks.

Test signals: `metrics.getRatisEvents()` contains "Configuration changed at term index".
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMStateMachine.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSequenceIDGenerator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSequenceIDGenerator.java

Purpose: This suite validates `SequenceIdGenerator` batch allocation, Ratis/non-Ratis behavior, leader failure handling, DB-backed state-manager consistency, restart reinitialization, and invalid sequence type rejection.

Important APIs and types: It uses `SequenceIdGenerator`, `SequenceIdType`, `SequenceIdGenerator.StateManagerImpl`, `SCMMetadataStoreImpl`, `SCMHAManagerStub`, `SCMDBTransactionBufferImpl`, `Table<SequenceIdType, Long>`, `OZONE_SCM_SEQUENCE_ID_BATCH_SIZE`, and `SCMException.ResultCodes.SCM_NOT_LEADER`.

Control flow: Non-Ratis and Ratis tests create real SCM metadata stores and assert IDs advance through initial and invalidated batches, using default batch size 1000 or configured batch size 100. The not-leader test spies the state manager, lets the first batch allocate, then makes later batch allocation throw `SCM_NOT_LEADER` and verifies generated IDs never exceed the current batch. Additional tests exercise direct state-manager allocation from empty DB, expected-last-ID mismatch failure, reinitialization from a pre-populated sequence ID table, and rejection of an unknown sequence ID name.

State and persistence behavior: Temporary SCM metadata DB tables persist last allocated IDs. Runtime state includes per-type in-memory last-ID map, current batch range, invalidation, and DB transaction buffer behavior.

Dependencies and integration points: This protects SCM ID allocation for local IDs, delete transaction IDs, container IDs, and HA replicated batch reservations.

Risks: Batch allocation must be monotonic and leader-gated. A stale in-memory map or DB mismatch can cause duplicate IDs after restart or across SCMs.

Test signals: Exact generated ID sequences, no ID beyond current batch after simulated not-leader failure, state-manager `getLastId` values, true/false allocation outcomes, successful reinitialize from DB, and exception path for unknown sequence type.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSequenceIDGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestStatefulServiceStateManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestStatefulServiceStateManagerImpl.java

Purpose: This test verifies `StatefulServiceStateManagerImpl` can save and read service configuration through the SCM HA DB transaction buffer.

Important APIs and types: It uses `StatefulServiceStateManagerImpl.newBuilder`, `StatefulServiceStateManager`, `SCMDBDefinition.STATEFUL_SERVICE_CONFIG`, `DBStoreBuilder`, `SCMHAManagerStub`, `SCMHADBTransactionBuffer`, and protobuf `ByteString`.

Control flow: Setup opens a real SCM DB store under a temp directory, obtains the stateful service config table, creates an HA manager stub backed by that DB store, and builds the state manager with the Ratis server and transaction buffer. The test saves a `ByteString` configuration under service name `test`, flushes the transaction buffer, and reads the configuration back.

State and persistence behavior: The stateful service configuration is persisted to the temporary DB table only after the HA transaction buffer is flushed. Cleanup closes the DB store.

Dependencies and integration points: This guards persisted service configuration paths used by SCM stateful services and HA replicated transaction buffering.

Risks: Without an explicit flush, buffered writes may not be visible. The broader race around flushing during transaction apply is covered by `TestSCMHATransactionBufferMonitorTask`.

Test signals: The read configuration equals the saved `ByteString` after flush.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestStatefulServiceStateManagerImpl.java -->
