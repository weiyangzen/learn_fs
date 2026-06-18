# subset-b-008049 Research

Grouped research for SCM tests, replication-manager fixtures, HDDS test utilities, and Ozone admin CLI sources. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestSCMDatanodeHeartbeatDispatcher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestSCMDatanodeHeartbeatDispatcher.java

Purpose: This unit test verifies how `SCMDatanodeHeartbeatDispatcher` converts datanode heartbeat protobuf fields into SCM events and how it reacts to heartbeats from unregistered datanodes after SCM restart. It protects the boundary between the datanode heartbeat RPC path, `NodeManager`, and the event bus.

Important APIs and types: The tests build `SCMHeartbeatRequestProto` messages carrying `NodeReportProto`, `ContainerReportsProto`, and `CommandStatusReportsProto`. They assert emitted events `NODE_REPORT`, `CONTAINER_REPORT`, and `CMD_STATUS_REPORT`, and payload wrapper types `NodeReportFromDatanode`, `ContainerReportFromDatanode`, and `CommandStatusReportFromDatanode`. The restart path verifies `NodeManager.addDatanodeCommand(DatanodeID, ReregisterCommand)`.

Control flow: Each dispatch test mocks `NodeManager.isNodeRegistered` as true, installs a small `EventPublisher`, builds one heartbeat, calls `dispatcher.dispatch`, and counts callbacks. The restart test leaves the registration check false by default, dispatches a heartbeat without reports, and verifies one re-register command is queued for the datanode ID.

State and persistence behavior: There is no durable state. Runtime state is limited to Mockito call history and an `AtomicInteger` event counter. The important state transition is the dispatcher deciding between report fan-out for registered nodes and re-registration command scheduling for unknown nodes.

Dependencies and integration points: This file integrates SCM heartbeat decoding with `NodeManager`, Ozone protocol command objects, generated datanode protocol protobufs, `MockDatanodeDetails`, and SCM's server event framework.

Risks: The tests only cover one command-status report and default report messages, not multiple command reports or malformed heartbeats. Event order is not asserted for the container/status case because the publisher only accepts either event. The unregistered-node case depends on Mockito's default false return for boolean methods.

Test signals: Strong signals are exact event counts, exact payload report identity, accepted event types, and the single `ReregisterCommand` enqueue when the node is not registered.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestSCMDatanodeHeartbeatDispatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestStorageContainerManagerStarter.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestStorageContainerManagerStarter.java

Purpose: This class tests the picocli front end for `StorageContainerManagerStarter` without starting SCM services. It validates that top-level start, initialization, bootstrap, and cluster-id generation options dispatch to `SCMStarterInterface` correctly and produce the expected exit codes.

Important APIs and types: The test uses `StorageContainerManagerStarter.execute`, `SCMStarterInterface`, `GenericCli.EXECUTION_ERROR_EXIT_CODE`, and picocli `ExitCode`. The nested `MockSCMStarter` records calls to `start`, `init`, `bootStrap`, and `generateClusterId`, captures the cluster ID argument, and can throw from each operation.

Control flow: `@BeforeEach` replaces `System.out` and `System.err` with UTF-8 `PrintStream`s backed by byte arrays, then creates a fresh mock starter. Individual tests call `executeCommand` with option combinations such as no args, `--init`, `--bootstrap`, `--clusterid`, `--genclusterid`, and invalid switches. `@AfterEach` restores the original streams.

State and persistence behavior: There is no SCM metadata persistence. The observable state is the mock starter's boolean flags, the saved cluster ID, process-style exit code, and captured stderr usage text for invalid input.

Dependencies and integration points: It covers the CLI binding around SCM startup actions, including usage validation, exception mapping, standard output/error behavior, and the `OzoneConfiguration` parameter contract exposed through `SCMStarterInterface`.

Risks: Because global streams are replaced, failures before `restoreStreams` can contaminate later tests. The mock `initStatus` is always true, so unsuccessful false-return init/bootstrap behavior is not tested. The usage assertion uses a regex tied to picocli's invalid-option wording.

Test signals: Expected signals are OK for start/init/bootstrap/genclusterid, usage exit for invalid parameters with no side-effect call, execution-error exit when mock operations throw, cluster ID propagation for `--init --clusterid=...`, and stderr containing unknown-option usage text.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestStorageContainerManagerStarter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/upgrade/FinalizationManagerTestImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/upgrade/FinalizationManagerTestImpl.java

Purpose: This test helper subclasses `FinalizationManagerImpl` so tests can inject a custom `FinalizationStateManager`. It exists to make SCM upgrade-finalization tests deterministic without using the production builder's normal state-manager construction path.

Important APIs and types: The class extends `FinalizationManagerImpl` and implements `FinalizationManager`. Its nested `Builder` extends `FinalizationManagerImpl.Builder`, adds `setFinalizationStateManager(FinalizationStateManager)`, and overrides `build` to create `FinalizationManagerTestImpl`.

Control flow: Tests configure the inherited builder fields, call `setFinalizationStateManager`, and then `build`. The constructor delegates to the parent constructor overload with both the builder and injected state manager.

State and persistence behavior: This class persists no data itself. It influences persistence indirectly by allowing tests to use mocked finalization tables, transaction buffers, Ratis server stubs, and version managers inside the production finalization manager flow.

Dependencies and integration points: It is tightly coupled to `FinalizationManagerImpl.Builder` and the protected or package-visible constructor signature that accepts an explicit state manager. `TestScmFinalization` uses it to drive resume and checkpoint behavior.

Risks: The helper bypasses some production construction logic; if the production builder adds mandatory validation or side effects, tests using this helper may miss them. It also relies on superclass builder field compatibility.

Test signals: The helper is validated indirectly when `TestScmFinalization` can inject mocked state and verify finalization ordering, persisted marks, and status messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/upgrade/FinalizationManagerTestImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/upgrade/FinalizationStateManagerTestImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/upgrade/FinalizationStateManagerTestImpl.java

Purpose: This compact helper exposes a `FinalizationStateManagerImpl` variant that can be built directly for tests without the production invocation-handler wiring. It simplifies mocked SCM finalization-state tests.

Important APIs and types: The class extends `FinalizationStateManagerImpl` and implements the `FinalizationStateManager` contract through inheritance. Its nested `Builder` extends `FinalizationStateManagerImpl.Builder` and overrides `build` to return the test implementation.

Control flow: Test code configures the inherited builder with a finalization store table, Ratis server, transaction buffer, and upgrade finalizer, then calls `build`. The constructor simply delegates to `super(builder)`.

State and persistence behavior: The helper owns no additional state beyond what the superclass builder initializes. Its value is enabling tests to control where the finalizing marker, layout-version key, and in-memory checkpoint state are read and written.

Dependencies and integration points: It is used by `TestScmFinalization` with mocked `Table<String, String>`, `SCMRatisServer`, `DBTransactionBuffer`, and `SCMUpgradeFinalizer` instances.

Risks: Like most test-only subclasses, it can hide production construction behavior if the production manager gains required invocation-handler semantics. It also depends on the parent builder remaining extensible.

Test signals: Indirect signals are successful checkpoint mapping, `crossedCheckpoint` behavior, and resume-finalization assertions in the finalization test suite.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/upgrade/FinalizationStateManagerTestImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/upgrade/TestScmFinalization.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/upgrade/TestScmFinalization.java

Purpose: This suite verifies SCM upgrade finalization as a checkpointed state machine. It locks down checkpoint ordering, maps persisted upgrade state into checkpoints, and verifies that finalization resumes from the correct step after failure, leader change, or restart.

Important APIs and types: Key types include `FinalizationCheckpoint`, `FinalizationManager`, `FinalizationStateManager`, `SCMUpgradeFinalizer`, `SCMUpgradeFinalizationContext`, `HDDSLayoutVersionManager`, `HDDSLayoutFeature`, `SCMContext`, `PipelineManager`, `NodeManager`, `SCMStorageConfig`, `DBTransactionBuffer`, `Table<String, String>`, and `UpgradeFinalization.StatusAndMessages`.

Control flow: `testCheckpointOrder` asserts enum order because ordering determines `hasCrossed` semantics. `testUpgradeStateToCheckpointMapping` builds a state manager with mocked persistence, adds a finalizing mark, finalizes layout features until MLV equals SLV, removes the mark, and checks the checkpoint after each phase. The parameterized resume test builds mock table and version-manager state for every checkpoint, calls `finalizeUpgrade`, and uses Mockito `InOrder` to verify only not-yet-crossed operations run.

State and persistence behavior: The tests model persistent finalization state with `OzoneConsts.FINALIZING_KEY` and `OzoneConsts.LAYOUT_VERSION_KEY` in the finalization table. They also model SCM layout version persistence by verifying `SCMStorageConfig.setLayoutVersion` and `persistCurrentState`, transaction-buffer writes/removes, and in-memory `SCMContext` checkpoint updates.

Dependencies and integration points: The suite integrates upgrade finalizer logic with HA transaction buffering, Ratis-facing state managers, SCM storage VERSION files, pipeline creation freeze/resume state, and node health transitions through `forceNodesToHealthyReadOnly`.

Risks: It relies on enum order as behavior, so reordering checkpoints is a functional change. Mocked pipeline state may not cover all production pipeline recovery paths. The table mock only answers the initial finalizing-key read; later state is assumed to be held in memory.

Test signals: Signals include exact checkpoint order, `crossedCheckpoint` truth table, status `FINALIZED_MSG` versus `STARTING_MSG`, ordered writes of finalizing mark and layout version, `freezePipelineCreation`, per-feature storage persistence, forced healthy-readonly transition at max layout version, and final removal of the finalizing mark.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/upgrade/TestScmFinalization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/upgrade/TestScmStartupSlvLessThanMlv.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/upgrade/TestScmStartupSlvLessThanMlv.java

Purpose: This downgrade-protection test verifies that SCM refuses to start when the metadata layout version recorded in its VERSION file is greater than the software layout version supported by the running binary.

Important APIs and types: It uses `StorageContainerManager`, `OzoneConfiguration`, `UpgradeTestUtils.createVersionFile`, `HDDSLayoutFeature`, `LayoutFeature`, `HddsProtos.NodeType.SCM`, `ScmConfigKeys.OZONE_SCM_DB_DIRS`, and `HddsConfigKeys.OZONE_METADATA_DIRS`. VERSION file properties include `SCM_ID` and `SCM_HA`.

Control flow: The test creates temporary SCM metadata, Ratis, and snapshot directories, computes `mlv` as one greater than the maximum known `HDDSLayoutFeature` layout version, writes an SCM VERSION file with that MLV, and asserts that constructing `StorageContainerManager` throws `IOException` with the exact expected message.

State and persistence behavior: Persistent state is the on-disk SCM `current/VERSION` file plus realistic Ratis directories used to simulate a newer prior SCM. Runtime behavior under test is startup validation in the version manager before SCM services are initialized.

Dependencies and integration points: This anchors upgrade/downgrade safety across SCM storage configuration, VERSION file parsing, HA metadata properties, and `StorageContainerManager` construction.

Risks: The test asserts the full exception message, so wording-only changes can fail it. It does not test a full cluster downgrade, only the constructor path after detecting `MLV > SLV`.

Test signals: The key signal is an `IOException` whose message includes the generated metadata layout version and current maximum software layout version.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/upgrade/TestScmStartupSlvLessThanMlv.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/upgrade/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/upgrade/package-info.java

Purpose: This package-info file documents the `org.apache.hadoop.hdds.scm.upgrade` test package as containing tests related to SCM upgrade.

Important APIs and types: It declares the package and has no classes, methods, annotations, or runtime API.

Control flow: There is no executable control flow. The file exists for package documentation and checkstyle compliance.

State and persistence behavior: None.

Dependencies and integration points: It groups helper classes and tests such as `FinalizationManagerTestImpl`, `FinalizationStateManagerTestImpl`, `TestScmFinalization`, and `TestScmStartupSlvLessThanMlv` under a documented package.

Risks: Behavioral risk is negligible. Removing it may affect documentation or style checks if package documentation is expected.

Test signals: Compile and style checks are the only signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/upgrade/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/ozone/container/common/TestEndPoint.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/ozone/container/common/TestEndPoint.java

Purpose: This integration-heavy test suite validates datanode endpoint RPC tasks against a mock SCM RPC server. It covers version negotiation, datanode registration, heartbeat processing, command-status creation, datanode layout storage, deleted-container cleanup, cluster-ID mismatch handling, invalid endpoints, and RPC timeout behavior.

Important APIs and types: The suite uses `EndpointStateMachine`, `VersionEndpointTask`, `RegisterEndpointTask`, `HeartbeatEndpointTask`, `DatanodeStateMachine`, `StateContext`, `OzoneContainer`, `MutableVolumeSet`, `HddsVolume`, `DatanodeLayoutStorage`, `ScmTestMock`, `SCMTestUtils`, Hadoop `RPC.Server`, storage report protos, heartbeat/register/version protos, `CommandStatus`, and SCM command protos for close, replicate, and delete-block commands.

Control flow: `@BeforeAll` creates configuration, initializes datanode layout storage, starts a mock SCM RPC server, captures its address, and selects a volume policy. Tests create endpoint state machines against valid or invalid addresses, set expected endpoint states, call the endpoint task, and assert state transitions. Helpers create volumes, add schema-v3 containers, move containers to deleted paths, construct register tasks, and run heartbeat tasks with a temporary datanode state machine.

State and persistence behavior: The test writes real datanode layout VERSION files, hdds volume directories, container files and DB paths, and deleted-container temp directories. It verifies cleanup of deleted container directories on version task startup, cluster ID persistence in layout storage, failed-volume movement on mismatched cluster IDs, and in-memory command-status map updates from heartbeat responses.

Dependencies and integration points: It joins SCM RPC protocol handling, datanode state-machine endpoint tasks, layout-version negotiation, volume formatting, key-value container utility paths, container reports, pipeline reports, node reports, replication server configuration, and log capture.

Risks: Timing and port behavior are important: tests set random ports and use bounded RPC timeouts. Global `scmServerImpl` response-delay and cluster-ID mutations must be reset carefully. Some tests compare elapsed time with tolerances and one heartbeat timeout allows extra shutdown delay.

Test signals: Signals include version response description keys, endpoint state transitions GETVERSION to REGISTER to HEARTBEAT, invalid endpoint state retention, SHUTDOWN on missing datanode details or cluster mismatch, empty deleted-container directory, layout cluster ID values, register container/node report counts, heartbeat command counts, command-status map entry for delete blocks command ID 3, and elapsed time below timeout tolerance.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/ozone/container/common/TestEndPoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/ozone/container/common/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/ozone/container/common/package-info.java

Purpose: This package-info file exists to satisfy style/package documentation expectations for `org.apache.hadoop.ozone.container.common` tests in the server-scm module.

Important APIs and types: It declares only the package and exposes no runtime API.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: The package contains endpoint and datanode/SCM integration tests such as `TestEndPoint`. This file only documents the package boundary.

Risks: No behavioral risk beyond losing package documentation or triggering checkstyle rules if removed.

Test signals: Compile and style checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/ozone/container/common/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/ozone/container/placement/TestContainerPlacement.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/ozone/container/placement/TestContainerPlacement.java

Purpose: This simulation test compares SCM's capacity-aware container placement with random placement and asserts that capacity-aware placement improves cluster space distribution over many create/delete operations.

Important APIs and types: It uses `MockNodeManager`, `NodeManager`, `NodeStatus.inServiceHealthy`, `SCMContainerPlacementCapacity`, `SCMContainerPlacementRandom`, `SCMContainerPlacementMetrics`, `SCMNodeStat`, `DatanodeDetails`, `OzoneConfiguration`, `DescriptiveStatistics`, and `OzoneConsts.GB`.

Control flow: The test creates two comparable 100-node mock clusters, computes initial standard deviation of used/capacity ratios, instantiates capacity and random placement policies, then runs 200,000 simulated operations. For each operation it chooses three datanodes, randomly picks container and metadata sizes, and either adds or deletes container usage every fifth iteration. It compares final standard deviations.

State and persistence behavior: There is no durable state. Runtime state is node space accounting inside `MockNodeManager`, which is mutated through `addContainer` and `delContainer`. The test's key state metric is standard deviation of SCM-used fraction across healthy in-service nodes.

Dependencies and integration points: It exercises the placement algorithms against `NodeManager` stats and SCM placement metrics mocks. It is a probabilistic integration point for algorithm behavior rather than a deterministic single-choice unit test.

Risks: The test depends on random operation ordering and a large operation count to stabilize statistics. It asserts a bold statistical claim, so algorithm changes, mock cluster initialization changes, or random distribution shifts can affect stability.

Test signals: Initial cluster standard deviations must match within tolerance; capacity placement must reduce standard deviation versus its starting state; random placement's final standard deviation must remain worse than capacity placement.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/ozone/container/placement/TestContainerPlacement.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/ozone/container/placement/TestDatanodeMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/ozone/container/placement/TestDatanodeMetrics.java

Purpose: This unit test validates comparison and aggregation behavior for placement metrics represented by `SCMNodeMetric` and `SCMNodeStat`.

Important APIs and types: It constructs `SCMNodeStat` values containing capacity, SCM-used, remaining, committed, free space, and other counters, wraps them in `SCMNodeMetric`, and calls `isEqual`, `add`, and `isGreater`.

Control flow: The test creates an initial stat and verifies its accessors. It creates an equivalent metric and checks equality, adds the original stat to the new metric and checks greater-than comparison, compares against a zero-capacity metric, and verifies that a small used-space difference on large-capacity nodes is ordered correctly.

State and persistence behavior: There is no persistence. State is in-memory metric values and derived comparison weights.

Dependencies and integration points: These metrics are used by SCM placement algorithms to rank datanodes by capacity pressure and space utilization. The test supports the placement behavior covered by `TestContainerPlacement`.

Risks: It covers only a few comparison scenarios and does not exhaust rounding or committed-space effects. A change to comparison semantics may require reinterpreting the final large-capacity assertion.

Test signals: Exact getter values, equality for identical stats, greater-than after addition, safe comparison against zero capacity, and greater-than for 51 used versus 50 used on otherwise identical large nodes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/ozone/container/placement/TestDatanodeMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/ozone/container/placement/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/ozone/container/placement/package-info.java

Purpose: This file documents the `org.apache.hadoop.ozone.container.placement` test package and keeps style checks satisfied.

Important APIs and types: It declares only the package.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: The package contains tests for SCM container placement algorithms and datanode placement metrics.

Risks: No runtime risk. Removing it could affect package documentation or checkstyle.

Test signals: Compile and style validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/ozone/container/placement/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/proto/Proto2SCMRatisProtocolForTesting.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/proto/Proto2SCMRatisProtocolForTesting.proto

Purpose: This proto2 schema defines a test-only SCM Ratis protocol envelope for serializing method-style requests and responses across different SCM state-machine subsystems.

Important APIs and types: It sets `java_package` to `org.apache.hadoop.hdds.protocol.proto.testing`, `java_outer_classname` to `Proto2SCMRatisProtocolForTesting`, and enables generated equals/hash. `RequestType` enumerates subsystem targets including pipeline, container, block, sequence ID, cert store, move, stateful service config, finalize, secret key, and cert rotate. Messages include `Method`, `MethodArgument`, `ListArgument`, `SCMRatisRequestProto`, and `SCMRatisResponseProto`.

Control flow: There is no executable flow in the schema. Generated code will require `SCMRatisRequestProto.type` and `method`, where `method` contains a method name plus repeated typed byte arguments. Responses contain a required string type and required byte value.

State and persistence behavior: Serialized requests and responses are transient protocol data. Field numbering and required fields are the persistence-sensitive contract if test logs, snapshots, or wire payloads are decoded later.

Dependencies and integration points: The schema integrates tests with protobuf code generation and SCM HA/Ratis request routing. It mirrors production concepts but is isolated under a testing package.

Risks: Proto2 `required` fields make partially populated messages invalid. Adding enum values or fields is generally compatible, but changing field numbers, requiredness, package, or outer class name would break generated-code callers.

Test signals: Protobuf compilation, generated Java availability, and successful serialization/deserialization by SCM Ratis tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/proto/Proto2SCMRatisProtocolForTesting.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/resources/replicationManagerTests/basic.json -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/resources/replicationManagerTests/basic.json

Purpose: This fixture file provides declarative replication-manager scenarios for basic healthy, under-replicated, and over-replicated containers across Ratis and erasure-coded replication.

Important APIs and types: Each JSON object describes `description`, `containerState`, `replicationConfig`, optional `sequenceId`, `replicas`, optional `pendingReplicas`, `expectation`, optional `checkCommands`, and expected `commands`. Replica entries include state, replica index, datanode alias, sequence ID, empty flag, and origin.

Control flow: The replication-manager test harness reads each object, creates a container state model, injects current and pending replicas, runs the replication check, then compares expected queue counters and command types. This file has scenarios for perfect Ratis and EC replication, Ratis and EC under-replication, pending ADD suppression, Ratis and EC over-replication, pending DELETE suppression, EC simultaneous over/under behavior, and Ratis over-replication already covered by pending delete.

State and persistence behavior: This is fixture data, not runtime persistence. It models SCM's in-memory replication state, pending replica operations, and expected command queues.

Dependencies and integration points: It is consumed by replication-manager parameterized tests and couples to command type names such as `replicateContainerCommand`, `reconstructECContainersCommand`, and `deleteContainerCommand`, plus expectation keys like `underReplicatedQueue` and `overReplicatedQueue`.

Risks: Stringly typed command and counter names must match the harness. The scenarios intentionally simplify datanode identity to aliases, so they depend on deterministic alias expansion by the loader.

Test signals: Expected counters and command lists for ten core Ratis/EC cases, especially suppression of queue commands when pending add/delete operations already exist.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/resources/replicationManagerTests/basic.json -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/resources/replicationManagerTests/mismatched_replicas.json -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/resources/replicationManagerTests/mismatched_replicas.json

Purpose: This fixture covers a closed Ratis container whose replicas are in mismatched states, specifically open replicas alongside a closed replica.

Important APIs and types: The scenario uses `containerState` CLOSED, `replicationConfig` RATIS:THREE, three replicas with states OPEN, OPEN, and CLOSED, and `checkCommands` expecting close-container commands for the open replica datanodes.

Control flow: The replication-manager harness loads the fixture, builds the replica set, runs the container check, and verifies that the manager schedules close commands to bring mismatched open replicas toward the container's closed state rather than enqueueing over-replication work.

State and persistence behavior: The file is static fixture data. It represents SCM's in-memory view of replica lifecycle state and expected command emission.

Dependencies and integration points: It depends on the shared replication-manager JSON schema and command verifier recognizing `closeContainerCommand` and datanode aliases `d1` and `d2`.

Risks: The file lacks a trailing newline between JSON arrays in some concatenated terminal views, but the actual file is a valid JSON array. Because it is a single scenario, it does not cover EC mismatch or quasi-closed mismatch behavior.

Test signals: No over-replicated queue work and two close-container check commands targeting the open replicas.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/resources/replicationManagerTests/mismatched_replicas.json -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/resources/replicationManagerTests/quasi_closed.json -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/resources/replicationManagerTests/quasi_closed.json

Purpose: This large fixture set models quasi-closed Ratis container edge cases for replication-manager tests. It focuses on stuck quasi-closed detection, origin diversity, BCSID differences, open or unhealthy replicas, maintenance/decommission state, and over/under-replication decisions.

Important APIs and types: Scenarios use `containerState` QUASI_CLOSED, `replicationConfig` RATIS:THREE, replica fields `state`, `sequenceId`, `origin`, `operationalState`, and `healthState`, plus expectations such as `quasiClosedStuck`, `quasiClosedStuckUnderReplicated`, `quasiClosedStuckOverReplicated`, `underReplicatedQueue`, `overReplicatedQueue`, and `unhealthy`. Commands include close, replicate, and delete container commands with exact or alternation-style datanode selectors.

Control flow: The test harness iterates each object, materializes replicas from aliases, runs the replication-manager check, verifies metric/queue expectations, and compares generated command types and selected source datanodes. Scenarios cover one open replica needing close, too few quasi-closed replicas needing replication, all origins closed enough to close, unhealthy highest-BCSID handling, correct replication by one/two/three origins, maintenance/decommission suppression, and stale-node restrictions.

State and persistence behavior: Fixture data represents SCM's in-memory replica topology and expected pending work. No durable state is written by the resource itself.

Dependencies and integration points: This file is tightly coupled to Ratis quasi-closed placement logic, origin-based replica health rules, operational state handling, and the replication-manager JSON test loader.

Risks: The fixture is stringly typed and dense; small changes in command selection policy can affect many expected rows. Datanode alternation strings such as `d1|d2` assume the verifier accepts one of several valid choices.

Test signals: Broad signals include stuck quasi-closed counters, under/over queue entries, close commands for open lower-state replicas, replication commands from suitable source replicas, delete commands for over-replicated origins, and no commands when maintenance, decommission, stale, or already-correct origin coverage should suppress action.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/resources/replicationManagerTests/quasi_closed.json -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/resources/replicationManagerTests/simple_decommission.json -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/resources/replicationManagerTests/simple_decommission.json

Purpose: This fixture verifies that containers hosted on decommissioning datanodes are treated as under-replicated for both Ratis and EC replication so replacement replicas are scheduled.

Important APIs and types: It contains two scenarios, one `RATIS:THREE` closed container with a decommissioning replica and one `EC:RS-3-2-1024k` closed container with one decommissioning EC index. Both expect `underReplicated` and `underReplicatedQueue` counters and `replicateContainerCommand`.

Control flow: The replication-manager harness loads the scenarios, marks one datanode as `DECOMMISSIONING`, runs the replication check, and verifies that the manager queues replication work even though the nominal replica count still includes the decommissioning node.

State and persistence behavior: Static fixture data only. It models operational state effects in SCM's in-memory replication evaluation.

Dependencies and integration points: It depends on operational-state parsing and the replication-manager command verifier. The EC scenario also depends on replica index handling.

Risks: The fixture covers simple one-node decommission only. It does not cover decommissioned, dead, or mixed maintenance states in the same file.

Test signals: One under-replication queue entry and a replicate command for both Ratis and EC decommission scenarios.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/resources/replicationManagerTests/simple_decommission.json -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/resources/replicationManagerTests/simple_maintenance.json -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/resources/replicationManagerTests/simple_maintenance.json

Purpose: This fixture verifies replication-manager behavior for containers with datanodes entering maintenance, including when configured maintenance redundancy is sufficient and when extra replication is required.

Important APIs and types: It defines Ratis and EC closed-container scenarios with `operationalState` ENTERING_MAINTENANCE. Scenario-specific knobs include `ratisMaintenanceMinimum` and `ecMaintenanceRedundancy`. Expected commands are either absent or `replicateContainerCommand`.

Control flow: The harness applies the maintenance redundancy settings, builds replica sets with maintenance nodes, runs replication checks, and compares expected under-replication counters and command lists. The first two scenarios allow maintenance without commands; the latter two require one Ratis replicate command or two EC replicate commands.

State and persistence behavior: Static test data only. It models how SCM computes effective replication while nodes are transitioning into maintenance.

Dependencies and integration points: The resource is coupled to replication-manager maintenance redundancy logic, Ratis versus EC command counts, and the JSON fixture loader.

Risks: It uses simple topologies and does not include unhealthy or stale replicas. Changes to default maintenance policy or command batching can require fixture updates.

Test signals: Empty expectations and no commands when maintenance redundancy is adequate; under-replication counters and expected replicate command counts when the redundancy knobs require extra copies.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/resources/replicationManagerTests/simple_maintenance.json -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/test-utils/pom.xml

Purpose: This Maven module descriptor builds the shared `hdds-test-utils` jar used by Ozone and HDDS tests. It centralizes test helper dependencies and disables annotation processing for this utility module.

Important APIs and types: The POM inherits from `org.apache.ozone:hdds`, sets artifact `hdds-test-utils`, packaging `jar`, and version `2.3.0-SNAPSHOT`. Dependencies include reload4j, Guava, commons-io/lang3, Jakarta annotations, Log4j API/core, Ratis common, AssertJ, JUnit Jupiter API, Mockito, SLF4J, Hadoop common as provided with all transitive dependencies excluded, JaCoCo core as provided, and JUnit platform engine/launcher as provided.

Control flow: Maven resolves the parent and dependencies, compiles utility classes, and uses `maven-compiler-plugin` with `<proc>none</proc>` to prevent annotation processing.

State and persistence behavior: Build metadata only. It affects generated artifacts in the Maven target directory, not runtime application persistence.

Dependencies and integration points: This module provides helper classes imported throughout the source tree, including wait utilities, log capturers, metrics assertions, test clocks, tag annotations, and timeout listeners. Its dependency scopes avoid pulling some heavy runtime dependencies into consumers.

Risks: Excluding all transitive dependencies from Hadoop common requires required classes to be supplied elsewhere. Provided dependencies must be available in test runtime or build plugins. Dependency drift can break helpers that bridge Log4j1, Log4j2, and SLF4J.

Test signals: Successful Maven compile/test classpath resolution for downstream modules that depend on `hdds-test-utils`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/GenericTestUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/GenericTestUtils.java

Purpose: `GenericTestUtils` is a broad static utility class for Ozone tests. It provides timing helpers, wait loops, log-level manipulation, reflection helpers, log capture, standard stream capture, synthetic stdin, tee print streams, deterministic port allocation, and thread diagnostics through timeout failures.

Important APIs and types: Key APIs include `getTestStartTime`, `waitFor`, `assertThrows`, `setLogLevel`, `withLogDisabled`, `mockFieldReflection`, `getFieldReflection`, `getReverseMap`, nested `LogCapturer`, `PrintStreamCapturer`, `SystemErrCapturer`, `SystemOutCapturer`, `TeePrintStream`, `PortAllocator`, and `ReflectionUtils`. It bridges SLF4J to reload4j/Log4j1 and exposes a Log4j2 capture singleton.

Control flow: `waitFor` polls a boolean condition until true or timeout and includes a thread dump from `TimedOutTestsListener` on timeout. Reflection helpers temporarily make fields accessible and clear final modifiers, optionally spy the field value with Mockito, then restore metadata. Stream capturers replace global system streams with tee streams and restore them on close. `supplyOnSystemIn` replaces `System.in` with a newline-joined stream.

State and persistence behavior: There is no durable state, but the class mutates JVM-global state: logger levels and appenders, `System.in/out/err`, and static port allocation. `PortAllocator.NEXT_PORT` monotonically advances and wraps in a fixed range.

Dependencies and integration points: It integrates Guava preconditions, Apache Commons IO, Mockito, JUnit, Ratis checked suppliers, Log4j1, SLF4J, and the local timeout listener. Many tests use it for asynchronous waits and output/log assertions.

Risks: Global stream and logger changes require disciplined close/finally handling. Reflection utilities depend on JDK internals, including Java 9 fallback access to `Class.getDeclaredFields0`. `PortAllocator` does not reserve sockets, so allocated ports can still race with other processes.

Test signals: Downstream tests signal correctness by reliable waits, restored globals, captured output/log content, successful final-field spying, and useful timeout diagnostics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/GenericTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/InputSubstream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/InputSubstream.java

Purpose: `InputSubstream` exposes a bounded byte range from an underlying `InputStream` without closing the underlying stream when the substream is closed. It is useful for tests that need range reads or multipart stream slices.

Important APIs and types: The class extends `FilterInputStream` and overrides `read()`, `read(byte[], int, int)`, `mark`, `reset`, `close`, and `available`. Constructor arguments are the wrapped stream, a skip offset, and requested length.

Control flow: On first read, it repeatedly calls `skip` until `currentPosition` reaches `requestedSkipOffset`, failing after `MAX_SKIPS` zero-length skips. It then computes remaining bytes as `skip + length - currentPosition`, caps the requested read length, reads from the delegate, and updates `currentPosition`. `mark` and `reset` preserve the logical current position.

State and persistence behavior: Runtime state includes `currentPosition`, `requestedSkipOffset`, `requestedLength`, and `markedPosition`. There is no persistence. `close` is intentionally a no-op to leave the wrapped stream open.

Dependencies and integration points: It depends only on Java IO and is likely used by tests validating range transfer, upload/download offsets, or stream lifecycle behavior.

Risks: If the wrapped stream returns `-1`, `currentPosition += bytesRead` can decrement by one; callers usually avoid reading past EOF, but this is a subtle edge case. Repeated zero skips can fail on streams with unusual skip behavior. No constructor validation prevents negative skip or length.

Test signals: Expected signals are reads limited to the requested range, underlying stream not closed by substream close, correct available count, and reset returning to marked logical position.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/InputSubstream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/IntLambda.java -->
# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/IntLambda.java

Purpose: `IntLambda` provides a small functional helper for tests that execute integer-returning code while supplying text on `System.in`.

Important APIs and types: It defines static method `withTextFromSystemIn(String...)` returning `ToIntExecutable`, and nested functional interface `ToIntExecutable` with `execute(IntSupplier code)`.

Control flow: `withTextFromSystemIn` creates an executable that uses `GenericTestUtils.supplyOnSystemIn` in a try-with-resources block, invokes the supplied `IntSupplier`, returns its integer result, rethrows runtime exceptions, and wraps checked restore failures in `RuntimeException`.

State and persistence behavior: No durable state. It temporarily mutates global `System.in` and relies on the returned `AutoCloseable` to restore it.

Dependencies and integration points: It integrates with CLI-style tests where command handlers read from stdin and return integer status codes. It depends on `GenericTestUtils`.

Risks: Like all global stdin replacement helpers, it is unsafe if used concurrently with other tests reading `System.in`. `IntSupplier` cannot throw checked exceptions directly.

Test signals: Downstream tests can assert integer return codes while providing deterministic stdin content.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/IntLambda.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/JacocoServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/JacocoServer.java

Purpose: `JacocoServer` is a simple TCP collector for JaCoCo remote coverage execution data. It accepts multiple agent connections and writes combined execution data to one `.exec` file.

Important APIs and types: It uses `ServerSocket`, `Socket`, `ExecutionDataWriter`, `RemoteControlReader`, `RemoteControlWriter`, `ISessionInfoVisitor`, and `IExecutionDataVisitor`. Static defaults are port `6300`, destination `/tmp/jacoco-combined.exec`, and a shared `lockMonitor`.

Control flow: `main` opens the destination file, starts a server socket, registers a shutdown hook to flush and close, then loops in `acceptConnections`. Each accepted socket is handled in a new thread. The handler wires reader visitors through synchronized wrappers, calls `reader.read()` until the remote stream ends, flushes the destination under the lock, and closes the socket.

State and persistence behavior: Persistent output is the combined JaCoCo exec file. Runtime state is the open server socket, destination writer, per-connection threads, and synchronized visitor access to avoid concurrent writes.

Dependencies and integration points: This utility integrates test JVMs using JaCoCo remote control with a centralized coverage file used by build or CI workflows.

Risks: Port and destination are hard-coded static fields, with no argument parsing. Handler threads are unmanaged and non-daemon by default. Exceptions print stack traces directly, and there is no graceful stop command beyond socket closure. `RemoteControlWriter` is constructed but not otherwise used.

Test signals: Successful server startup, accepted JaCoCo agent connections, nonempty combined exec output, and clean flush on shutdown.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/JacocoServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/LambdaTestUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/LambdaTestUtils.java

Purpose: `LambdaTestUtils` provides Java-lambda-friendly retry and await utilities for tests, modeled after Hadoop wait helpers and ScalaTest-style await behavior.

Important APIs and types: Main APIs are `await(int, Callable<Boolean>, Callable<Integer>, TimeoutHandler)`, `await(int, int, Callable<Boolean>)`, `TimeoutHandler`, `GenerateTimeout`, `FixedRetryInterval`, `FailFastException`, and `VoidCallable`. It uses Hadoop `Time.monotonicNow` and SLF4J logging.

Control flow: `await` computes an end time, repeatedly invokes the check callable, returns the iteration count on success, stores non-fatal throwables for timeout diagnostics, rethrows `InterruptedException`, `FailFastException`, and `VirtualMachineError` immediately, and sleeps according to the retry callable while time remains. On timeout it invokes the timeout handler, falls back to `GenerateTimeout` if the handler returns null, then rethrows the resulting throwable as exception or error.

State and persistence behavior: No persistence. Runtime state includes iteration count, last caught throwable, retry invocation count in `FixedRetryInterval`, and timeout messages.

Dependencies and integration points: Used by asynchronous tests that need custom retry intervals, fail-fast aborts, or richer timeout exception handling than a simple polling loop.

Risks: A negative retry interval ends polling early. Timeout handlers can throw or return unexpected throwable types; `raise` casts non-Exception throwables to `Error`. The utility logs repeated failures only at debug level.

Test signals: Downstream tests can assert iteration counts, generated `TimeoutException` messages, retry invocation counts, and fail-fast behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/LambdaTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/Log4j1Capturer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/Log4j1Capturer.java

Purpose: `Log4j1Capturer` is the Log4j1/reload4j implementation of `GenericTestUtils.LogCapturer`. It captures log output from a specific logger into an in-memory writer for assertions.

Important APIs and types: It uses Log4j1 `Logger`, `Appender`, `Layout`, `PatternLayout`, and `WriterAppender`. Constructors accept a logger and optional layout.

Control flow: Construction selects the root `stdout` or `console` appender layout when no layout is supplied, falls back to a default `PatternLayout`, creates a `WriterAppender` targeting the inherited `StringWriter`, and adds it to the target logger. `stopCapturing` removes that appender.

State and persistence behavior: No durable state. Runtime state is the installed appender and captured writer buffer. It mutates logger configuration until `stopCapturing` is called.

Dependencies and integration points: It is returned by `GenericTestUtils.LogCapturer.captureLogs` for Log4j1 and SLF4J-to-Log4j bridged loggers.

Risks: Forgetting to call `stopCapturing` leaves an appender attached and may duplicate log output or leak memory. It captures only the specified logger, and logger additivity/layout configuration affects content.

Test signals: Downstream tests inspect `getOutput`, call `clearOutput`, and stop capture after assertions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/Log4j1Capturer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/Log4j2Capturer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/Log4j2Capturer.java

Purpose: `Log4j2Capturer` is a singleton Log4j2 implementation of `GenericTestUtils.LogCapturer` that captures Log4j2 output into an in-memory writer.

Important APIs and types: It uses Log4j2 core `LoggerContext`, `Configuration`, `LoggerConfig`, `Appender`, `WriterAppender`, and `PatternLayout`. The appender name is fixed as `capture`.

Control flow: The private singleton constructor calls `addAppender`, which creates and starts a writer appender, adds it to the configuration, then attaches it to every configured logger and the root logger. `stopCapturing` removes the named appender from all logger configs and root.

State and persistence behavior: No durable state. Runtime state is singleton capture writer and logger configuration mutations across the JVM. Because the instance is static, captured output can survive across uses unless cleared.

Dependencies and integration points: `GenericTestUtils.LogCapturer.log4j2` returns this singleton. The method currently ignores the requested logger name, so capture is broad.

Risks: The TODO notes it does not capture only a specific logger. Singleton behavior can cross-contaminate tests if output is not cleared. It mutates all logger configs and does not call `context.updateLoggers` explicitly after changes.

Test signals: Captured Log4j2 output appears in `getOutput`, and `stopCapturing` removes the capture appender from logger configs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/Log4j2Capturer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/MetricsAsserts.java -->
# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/MetricsAsserts.java

Purpose: `MetricsAsserts` provides assertion and extraction helpers for Hadoop Metrics2 sources. It lets tests mock metrics collectors, invoke a `MetricsSource`, and verify gauges, counters, tags, and quantile gauges by metric name.

Important APIs and types: Key APIs include `mockMetricsSystem`, `mockMetricsRecordBuilder`, `getMetrics`, overloaded `assertGauge` and `assertCounter`, `getIntGauge`, `getLongGauge`, `getDoubleGauge`, `getFloatGauge`, `getLongCounter`, `getStringMetric`, `assertCounterGt`, `assertGaugeGt`, `assertGaugeGte`, `assertQuantileGauges`, `assertInverseQuantileGauges`, `assertTag`, and `getStringTag`. It uses `MetricsCollector`, `MetricsRecordBuilder`, `MetricsSource`, `DefaultMetricsSystem`, `MutableQuantiles`, Mockito captors/matchers, and AssertJ offsets.

Control flow: `mockMetricsRecordBuilder` returns a Mockito builder that chains most metric methods to itself and returns the collector for `parent` or `endRecord`. `getMetrics` invokes a source with the mock collector. Getter methods verify the builder received exactly one matching metric call by name and return the captured value. Quantile helpers verify percentile gauge names for the default quantiles.

State and persistence behavior: No persistence. `mockMetricsSystem` mutates the global `DefaultMetricsSystem` singleton. Assertions inspect Mockito invocation history and captured values.

Dependencies and integration points: Used throughout Ozone metrics tests to verify Metrics2 source output without starting a real metrics sink. It bridges Hadoop metric names created through `Interns.info` with Mockito name matchers.

Risks: `atLeast(0)` permits missing invocations until `checkCaptured` catches zero captures. Global metrics system replacement can affect tests running in parallel. Quantile naming is tied to Hadoop's default `MutableQuantiles` percentiles and suffix conventions.

Test signals: Exact metric values, greater-than comparisons, single-capture enforcement, tag values, and presence of all expected quantile percentile gauges.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/MetricsAsserts.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/OzoneTestBase.java -->
# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/OzoneTestBase.java

Purpose: `OzoneTestBase` is a base class for JUnit 5 tests that need the current test method name and deterministic unique lowercase object names.

Important APIs and types: It uses JUnit `TestInfo` and `@BeforeEach`, Java reflection `Method`, `Locale.ROOT`, `Objects`, and a static `AtomicInteger` counter. Public/static API includes `uniqueObjectName(String)`, while subclasses use `getTestName()` and `uniqueObjectName()`.

Control flow: Before each test, `storeTestInfo` saves the JUnit `TestInfo`. `getTestName` extracts the method name or returns `unknown`. `uniqueObjectName` truncates the prefix to 50 characters, lowercases it, and appends a zero-padded 10-digit counter.

State and persistence behavior: Runtime state includes per-instance `TestInfo` and static process-wide `OBJECT_COUNTER`. There is no persistence.

Dependencies and integration points: Subclasses can generate bucket, volume, key, or other object names tied to test names while avoiding collisions in the same JVM.

Risks: The static counter is process-local and not reset per test class. Lowercasing and truncation may still produce collisions if many long prefixes share the same first 50 characters, though the counter mitigates within the JVM.

Test signals: Downstream tests rely on names being lowercase, bounded to 60 characters, and unique for repeated calls.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/OzoneTestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/SpyInputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/SpyInputStream.java

Purpose: `SpyInputStream` wraps an `InputStream` and records how many times it is closed so tests can assert close behavior.

Important APIs and types: It extends `FilterInputStream`, uses an `AtomicInteger` close counter, overrides `close`, and exposes `assertClosedExactlyOnce`.

Control flow: Construction delegates to `FilterInputStream`. Each `close` increments the counter and then closes the wrapped stream. `assertClosedExactlyOnce` asserts the counter equals one through JUnit.

State and persistence behavior: No persistence. Runtime state is the close counter.

Dependencies and integration points: Useful in tests that validate resource ownership and stream lifecycle for APIs receiving or returning input streams.

Risks: It only exposes the exact-once assertion; tests needing zero, at-least, or exact-N closes need another helper. The underlying close is still executed on every call, so repeated close behavior depends on the wrapped stream.

Test signals: JUnit assertion passes only when exactly one close call occurred.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/SpyInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/SpyOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/SpyOutputStream.java

Purpose: `SpyOutputStream` wraps an `OutputStream` and records close calls so tests can assert output stream lifecycle behavior.

Important APIs and types: It extends `FilterOutputStream`, uses an `AtomicInteger`, overrides `close`, and provides `assertClosedExactlyOnce`.

Control flow: `close` increments the counter and delegates to the wrapped output stream close. The assertion method verifies the counter is one with JUnit.

State and persistence behavior: Runtime-only close count; no persistent state.

Dependencies and integration points: Used by tests that verify writers, serializers, or IO helpers close caller-provided output streams exactly once.

Risks: Repeated close calls are passed through to the underlying stream. Like the input variant, it supports only one specific assertion.

Test signals: Exact one close invocation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/SpyOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/TestClock.java -->
# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/TestClock.java

Purpose: `TestClock` is a mutable `java.time.Clock` implementation for tests that need deterministic control over current time.

Important APIs and types: It extends `Clock` and exposes `newInstance`, constructor `(Instant, ZoneId)`, `getZone`, `withZone`, `instant`, `fastForward(long)`, `fastForward(TemporalAmount)`, `rewind(long)`, `rewind(TemporalAmount)`, and `set(Instant)`.

Control flow: `instant` returns the stored instant. Fast-forward and rewind compute a new instant by adding or subtracting milliseconds or a temporal amount, then delegate to `set`.

State and persistence behavior: Runtime state is mutable `instant` plus immutable `zoneId`. There is no persistence.

Dependencies and integration points: Used by tests for timeouts, stale container detection, lifecycle timestamps, and services that accept an injected `Clock`.

Risks: `withZone` returns a new clock using `Instant.now()` rather than preserving the current test instant, which can surprise callers expecting standard `Clock.withZone` semantics. It is mutable and not synchronized.

Test signals: Consumers assert time-dependent transitions after explicit `fastForward`, `rewind`, or `set` calls without sleeping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/TestClock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/TimedOutTestsListener.java -->
# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/TimedOutTestsListener.java

Purpose: `TimedOutTestsListener` is a JUnit Platform listener that prints full thread diagnostics to `System.err` when a test fails with `TimeoutException`.

Important APIs and types: It implements `TestExecutionListener`, handles `TestExecutionResult` and `TestIdentifier`, and uses `Thread.getAllStackTraces`, `ManagementFactory.getThreadMXBean`, `ThreadInfo`, `MonitorInfo`, and `LockInfo`. Static API `buildThreadDiagnosticString` is also used by wait utilities.

Control flow: `executionFinished` checks for failed results whose throwable is a `TimeoutException`, prints a banner, then prints diagnostics. Diagnostics include a timestamp, a thread dump built from all JVM stack traces, and optional monitor-deadlock details from `findMonitorDeadlockedThreads`.

State and persistence behavior: No durable state. It reads live JVM thread state and writes diagnostics to stderr. Date formatting uses a local `SimpleDateFormat` instance per call.

Dependencies and integration points: Integrated with JUnit Platform launcher configuration and `GenericTestUtils.waitFor`, which embeds thread diagnostics in timeout exceptions.

Risks: Thread dump output can be large. It detects monitor deadlocks but not all ownable-synchronizer deadlocks unless exposed through the selected MXBean call. Printing to global stderr can interleave under parallel test execution.

Test signals: On timeout failures, stderr contains the timeout banner, timestamp, thread stack traces, and deadlock section when applicable.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/TimedOutTestsListener.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/package-info.java

Purpose: This package-info file documents the `org.apache.ozone.test` package as containing test utilities.

Important APIs and types: It declares only the package and no runtime API.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: It groups shared helpers such as `GenericTestUtils`, `LambdaTestUtils`, stream spies, metrics assertions, and timeout diagnostics.

Risks: No behavioral risk beyond style/package documentation expectations.

Test signals: Compile and style checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/tag/Flaky.java -->
# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/tag/Flaky.java

Purpose: `@Flaky` marks JUnit 5 tests or test classes that have intermittent issues and should be handled separately by CI, often with retries.

Important APIs and types: It is an annotation targeting types and methods, retained at runtime, meta-annotated with `@Tag("flaky")`, and exposes required `String[] value()` for issue identifiers.

Control flow: There is no executable code. JUnit discovers the `flaky` tag and build tooling can include, exclude, or retry these tests based on tag selection.

State and persistence behavior: Annotation metadata is retained in compiled classes at runtime. No mutable state.

Dependencies and integration points: It integrates with JUnit Jupiter tags and project CI conventions. The value usually names Jira issues such as `HDDS-123`.

Risks: Misusing the annotation can hide real regressions from normal CI. Because `value` is required, callers must provide a tracking issue or description.

Test signals: Tagged tests are discoverable under the `flaky` JUnit tag and carry runtime annotation metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/tag/Flaky.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/tag/Slow.java -->
# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/tag/Slow.java

Purpose: `@Slow` marks JUnit 5 tests or classes that take too much time for regular per-commit CI but may run manually or in scheduled jobs.

Important APIs and types: It targets types and methods, is retained at runtime, is meta-annotated with `@Tag("slow")`, and has optional `String value()` defaulting to empty.

Control flow: No executable code. JUnit and build tooling use the `slow` tag for test selection.

State and persistence behavior: Runtime annotation metadata only.

Dependencies and integration points: Integrates with JUnit Jupiter tags and CI profiles that exclude or include slow tests.

Risks: Overuse can reduce coverage in normal CI. The optional value may be empty, so not every slow test has a tracking issue.

Test signals: JUnit discovery shows the `slow` tag and runtime metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/tag/Slow.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/tag/Unhealthy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/tag/Unhealthy.java

Purpose: `@Unhealthy` marks JUnit 5 tests or classes considered unstable or inconsistent to run. These tests are excluded from normal CI and run only manually or in selected jobs.

Important APIs and types: It targets types and methods, retains metadata at runtime, is meta-annotated with `@Tag("unhealthy")`, and has optional `String value()` for a Jira issue or description.

Control flow: No executable code. The annotation influences JUnit tag filtering and project CI policy.

State and persistence behavior: Runtime annotation metadata only.

Dependencies and integration points: It integrates with JUnit Jupiter and the project's test categorization conventions.

Risks: Marking tests unhealthy can mask product regressions if not tracked and repaired. Optional empty value weakens traceability.

Test signals: Tagged tests are discoverable under the `unhealthy` JUnit tag.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/tag/Unhealthy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/tag/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/tag/package-info.java

Purpose: This package-info file documents `org.apache.ozone.test.tag` as the package containing annotations for grouping tests.

Important APIs and types: It declares only the package.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: It groups `Flaky`, `Slow`, and `Unhealthy` tag annotations.

Risks: No runtime risk. Removal may affect package documentation or style checks.

Test signals: Compile and style checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/tag/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/pom.xml

Purpose: This Maven descriptor builds the `ozone-cli-admin` jar, which contains admin subcommands and SCM/container operation client code for Ozone.

Important APIs and types: The module inherits from `hdds-hadoop-dependency-client`, sets artifact `ozone-cli-admin`, and enables classpath generation. Dependencies include Jackson, Guava, commons-io/lang3/codec, picocli, Hadoop common/HDFS client, HDDS CLI/client/common/config/interface/server framework modules, Ozone shell/client/common/interface modules, Ratis common, SLF4J, reload4j binding, and `metainf-services` as provided. Test dependencies include `hdds-common` test-jar and `hdds-test-utils`.

Control flow: The compiler plugin runs annotation processors for `@MetaInfServices` and picocli Graal native-image config generation, passing `-Aproject=group/artifact`. The enforcer plugin overrides root import restrictions for this module and bans selected HDDS config annotations.

State and persistence behavior: Build metadata only. It affects generated service-provider metadata and native-image configuration during compilation.

Dependencies and integration points: This module is an integration point between CLI command registration, picocli, SCM admin/client interfaces, Ozone shell/client libraries, and Hadoop dependencies.

Risks: Annotation processor configuration is critical for admin subcommands to be discoverable. Dependency changes can affect CLI packaging, native-image metadata, and runtime logging. The enforcer override must stay aligned with root policy.

Test signals: Maven compile, generated `META-INF/services` entries, picocli metadata generation, and downstream CLI tests resolving the admin commands.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ContainerBalancerCommands.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ContainerBalancerCommands.java

Purpose: This class registers the `ozone admin containerbalancer` command group and documents container balancer usage for administrators.

Important APIs and types: It implements `AdminSubcommand`, is annotated with picocli `@Command`, uses `HddsVersionProvider`, and is registered with `@MetaInfServices(AdminSubcommand.class)`. Subcommands are `ContainerBalancerStartSubcommand`, `ContainerBalancerStopSubcommand`, and `ContainerBalancerStatusSubcommand`.

Control flow: The class has no methods. Picocli uses annotation metadata to route nested `start`, `stop`, and `status` invocations, while service-provider metadata makes the group discoverable by the admin CLI.

State and persistence behavior: No runtime state or persistence. It controls CLI registration and help text.

Dependencies and integration points: It integrates admin command discovery, picocli command hierarchy, version output, and the container balancer SCM operations implemented by child commands.

Risks: Removing `@MetaInfServices` or changing command names breaks CLI discovery or compatibility. The long help text must stay aligned with actual option names and server-side defaults.

Test signals: The admin CLI lists `containerbalancer`, routes child commands, and displays version/help metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ContainerBalancerCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ContainerBalancerStartSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ContainerBalancerStartSubcommand.java

Purpose: This subcommand starts SCM's container balancer with optional runtime configuration overrides supplied from the command line.

Important APIs and types: It extends `ScmSubcommand`, is annotated as picocli command `start`, accepts many `Optional` options, and calls `ScmClient.startContainerBalancer`. It consumes `StartContainerBalancerResponseProto`.

Control flow: Picocli populates option fields for threshold, iterations, max datanodes involved, move-size limits, iteration interval, move timeouts, network topology flag, include/exclude datanodes, and include/exclude containers. `execute` passes all optionals to the SCM client. If the response has `start=true`, it prints success. Otherwise it prints failure, optional reason, and throws `IOException`.

State and persistence behavior: The command itself persists no state. It sends desired balancer configuration to SCM, where balancer runtime state is controlled.

Dependencies and integration points: It maps CLI syntax to `ScmClient` and SCM protocol `StartContainerBalancerResponseProto`. Option aliases preserve older camelCase names for compatibility.

Risks: Option validation is largely delegated to server-side handling; invalid values may reach SCM. Include/exclude lists are raw comma-separated strings. Failure throws after printing to stderr, which affects CLI exit behavior.

Test signals: Successful response prints `Container Balancer started successfully.` Failed response prints failure and reason and raises `IOException`; client method receives all optionals in the documented order.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ContainerBalancerStartSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ContainerBalancerStatusSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ContainerBalancerStatusSubcommand.java

Purpose: This subcommand reports whether the container balancer is running and, in verbose mode, prints configuration, current iteration statistics, and optional iteration history.

Important APIs and types: It extends `ScmSubcommand`, calls `ScmClient.getContainerBalancerStatusInfo`, and formats `ContainerBalancerStatusInfoResponseProto`, `ContainerBalancerStatusInfoProto`, `HddsProtos.ContainerBalancerConfigurationProto`, and `ContainerBalancerTaskIterationStatusInfoProto`. It uses `DurationUtil.getPrettyDuration`, Hadoop `StringUtils.byteDesc`, `OzoneConsts.GB`, and Java time formatting.

Control flow: `execute` prints running/not-running. When running and `isVerbose()` is true, it formats start time in the system zone, computes duration to now, prints configuration, finds the current iteration as the first status entry with empty `iterationResult`, and prints it or `-`. With `--history`, it also prints completed iterations whose result is nonempty.

State and persistence behavior: The command reads balancer status from SCM and writes formatted text. No local state is persisted.

Dependencies and integration points: It integrates CLI verbose handling, SCM balancer status protocol, byte/duration formatting utilities, and administrator-facing status output.

Risks: Output formatting is column-width based and may be brittle for tests or parsing. `Duration.between(startedAtInstant, OffsetDateTime.now())` mixes instant and offset temporal types but works through temporal conversion. Current iteration detection assumes empty result means active.

Test signals: Expected output for running/not-running, configuration values converted to GB/minutes, current iteration info, history filtering, and placeholder `-` for absent lists or no active iteration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ContainerBalancerStatusSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ContainerBalancerStopSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ContainerBalancerStopSubcommand.java

Purpose: This subcommand sends a request to stop SCM's container balancer and reports the outcome to the administrator.

Important APIs and types: It extends `ScmSubcommand`, is picocli command `stop`, and calls `ScmClient.stopContainerBalancer`.

Control flow: `execute` prints that the stop command is being sent, calls the SCM client, prints `Container Balancer stopped.` on success, and on `IOException` prints a failure message to stderr before rethrowing.

State and persistence behavior: No local persistence. The command affects remote balancer runtime state in SCM.

Dependencies and integration points: It is registered under `ContainerBalancerCommands` and relies on `ScmClient` to reach SCM.

Risks: The initial message says it is waiting for the balancer to stop, but actual blocking semantics depend entirely on `ScmClient.stopContainerBalancer`. Errors are rethrown after printing, so callers receive both stderr and nonzero exit behavior.

Test signals: Client stop method invocation, success text, and stderr failure text plus propagated `IOException`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ContainerBalancerStopSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ContainerOperationClient.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ContainerOperationClient.java

Purpose: `ContainerOperationClient` is the concrete CLI/admin implementation of `ScmClient`. It bridges administrator commands to SCM RPCs and, for container data operations, to datanode container protocol calls through xceiver clients.

Important APIs and types: It implements many `ScmClient` methods and wraps `StorageContainerLocationProtocol`, `SecretKeyProtocolScm`, `XceiverClientManager`, `XceiverClientSpi`, `ContainerProtocolCalls`, `ContainerWithPipeline`, `Pipeline`, `ContainerInfo`, `ContainerReplicaInfo`, `ReplicationConfig`, `ReplicationManagerReport`, `StartContainerBalancerResponseProto`, `ContainerBalancerStatusInfoResponseProto`, `StatusAndMessages`, and datanode admin response types.

Control flow: Construction creates an SCM container RPC client for the configured HA service or a target SCM node, creates a secret-key client, reads container size and default replication settings, detects container-token support, and stores the max list count. `getXceiverClientManager` lazily creates a client manager, using CA certificates and `ClientTrustManager` when security is enabled. Container create/read/delete methods allocate or fetch pipelines from SCM, acquire xceiver clients, issue datanode protocol calls with optional encoded container tokens, and release clients in finally blocks. Most admin methods delegate directly to `storageContainerLocationClient`.

State and persistence behavior: Local state includes configuration, clients, token-enabled flag, default replication type/factor, container size, and max list count. It persists nothing locally. Remote side effects include allocating/closing/deleting containers, changing pipeline state, safe mode, replication manager state, container balancer state, SCM upgrade finalization, SCM leadership, secret key rotation, and suppressed-container flags.

Dependencies and integration points: This class is a central integration point across CLI commands, SCM HA utilities, security certificate handling, datanode xceiver protocol, container tokens, replication manager, container balancer, safe mode, datanode admin, SCM roles, upgrade finalization, metrics, and reconciliation APIs.

Risks: Many methods are thin delegations, so protocol drift in `ScmClient` or `StorageContainerLocationProtocol` affects this class broadly. `createContainer(type, factor, owner)` ignores the passed `type` and uses the instance default replication type with the passed factor, which is a notable behavior risk. `containerSizeB` casts a storage size to `int` before assigning to long. `close` logs but suppresses close exceptions. List operations silently cap requested count and only warn.

Test signals: Signals include correct lazy client-manager construction under secure/insecure configs, token generation only when enabled, xceiver acquire/release around create/read/delete, SCM delete after datanode delete, capped list counts, direct delegation for admin operations, and propagated IO failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ContainerOperationClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ReplicationManagerCommands.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ReplicationManagerCommands.java

Purpose: This class registers the `ozone admin replicationmanager` command group for starting, stopping, and checking SCM's replication manager.

Important APIs and types: It implements `AdminSubcommand`, is annotated with picocli `@Command`, uses `HddsVersionProvider`, registers subcommands `ReplicationManagerStartSubcommand`, `ReplicationManagerStopSubcommand`, and `ReplicationManagerStatusSubcommand`, and uses `@MetaInfServices(AdminSubcommand.class)` for discovery.

Control flow: It has no executable methods. Picocli and service-provider loading use the annotations to expose the command group.

State and persistence behavior: No local state or persistence.

Dependencies and integration points: It integrates admin CLI discovery with SCM replication-manager control subcommands.

Risks: Command name or service registration changes can break admin CLI compatibility. Help text is minimal and relies on child commands for details.

Test signals: CLI discovery of `replicationmanager` and routing of `start`, `stop`, and `status` subcommands.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ReplicationManagerCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ReplicationManagerStartSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ReplicationManagerStartSubcommand.java

Purpose: This subcommand asks SCM to start its replication manager.

Important APIs and types: It extends `ScmSubcommand`, is picocli command `start`, and calls `ScmClient.startReplicationManager`.

Control flow: `execute` delegates to the SCM client and then prints `Starting ReplicationManager...`.

State and persistence behavior: No local persistence. Remote SCM replication-manager runtime state may change.

Dependencies and integration points: Registered under `ReplicationManagerCommands` and relies on `ContainerOperationClient` or another `ScmClient` implementation for transport.

Risks: The message is printed after the RPC returns but says starting, not started; actual async semantics are determined by SCM. IOException is not caught and will propagate to the CLI framework.

Test signals: Client method invocation and the expected stdout line.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ReplicationManagerStartSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ReplicationManagerStatusSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ReplicationManagerStatusSubcommand.java

Purpose: This subcommand reports whether SCM's replication manager is running.

Important APIs and types: It extends `ScmSubcommand`, is picocli command `status`, and calls `ScmClient.getReplicationManagerStatus`.

Control flow: `execute` reads the boolean status from SCM and prints either `ReplicationManager is Running.` or `ReplicationManager is Not Running.`.

State and persistence behavior: Read-only command; no local state or persistence.

Dependencies and integration points: Registered under the replication manager command group and depends on SCM's status RPC.

Risks: It provides only a boolean summary, not queue depth, health, or last-run details. IOException propagates.

Test signals: Correct output for true and false client responses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ReplicationManagerStatusSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ReplicationManagerStopSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ReplicationManagerStopSubcommand.java

Purpose: This subcommand requests SCM to stop the replication manager.

Important APIs and types: It extends `ScmSubcommand`, is picocli command `stop`, and calls `ScmClient.stopReplicationManager`.

Control flow: `execute` delegates to SCM, prints `Stopping ReplicationManager...`, then prints a second line explaining that SCM was requested to stop it and the stop may take time.

State and persistence behavior: No local persistence. The remote SCM replication-manager service state may transition asynchronously.

Dependencies and integration points: Registered under `ReplicationManagerCommands` and transported through an `ScmClient` implementation.

Risks: It does not poll until stopped. The user-facing text contains `sometime`, and the command assumes the RPC request was accepted if no exception is thrown.

Test signals: Client stop method invocation and the two stdout lines.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ReplicationManagerStopSubcommand.java -->
