# subset-b-008001 research

Grouped research report for the requested Apache Ozone HDDS datanode protocol, UI, service-test, checksum-test, and test-helper files. Each section is bounded for reconciliation into a source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/ReconstructECContainersCommand.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/ReconstructECContainersCommand.java

Purpose: `ReconstructECContainersCommand` is the SCM-to-datanode command used to request erasure-coded container reconstruction. It carries the container ID, source datanodes with replica indexes, target datanodes, missing EC indexes as a `ByteString`, and an `ECReplicationConfig`.

Important APIs and types: the class extends `SCMCommand<ReconstructECContainersCommandProto>`, reports type `reconstructECContainersCommand`, serializes through `getProto()`, and deserializes through `getFromProtobuf()`. The nested `DatanodeDetailsAndReplicaIndex` type serializes `DatanodeDetails` plus an EC replica index and implements value equality.

Control flow and state: constructors either allocate a command id through `HddsIdFactory.getLongId()` or accept an id during protobuf reconstruction. The main validation enforces `targetDatanodes.size() == missingContainerIndexes.size()`, tying each reconstruction target to one missing index byte. `getProto()` copies source and target details into protobuf lists and writes the EC config. Deserialization maps protobuf source and target lists back to Java objects and preserves `cmdId`.

Persistence and integration: the object itself is transient command state; persistence is protobuf transport and any command queues using the base `SCMCommand` id, term, encoded token, and deadline. It integrates with EC reconstruction scheduling, datanode command handlers, `DatanodeDetails`, and `StorageContainerDatanodeProtocolProtos`.

Risks and test signals: the command stores input lists directly, so callers can mutate lists after construction unless they provide immutable lists. The target/index cardinality check is important because a malformed command cannot be interpreted safely. `toString()` logs encoded tokens and all participating nodes; that is useful for diagnosis but sensitive if tokens are meaningful. No direct tests are in this subset, so coverage likely comes from command serialization tests elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/ReconstructECContainersCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/RefreshVolumeUsageCommand.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/RefreshVolumeUsageCommand.java

Purpose: `RefreshVolumeUsageCommand` is a simple SCM command that asks a datanode to refresh disk usage information immediately.

Important APIs and types: it extends `SCMCommand<RefreshVolumeUsageCommandProto>`, returns command type `refreshVolumeUsageInfo`, emits a protobuf containing only `cmdId`, and has a static `getFromProtobuf()` factory.

Control flow and state: construction uses the default `SCMCommand` id allocator. `getProto()` builds `RefreshVolumeUsageCommandProto` with the current id. `getFromProtobuf()` only null-checks the protobuf and returns a new command, which means it does not preserve the incoming `cmdId`.

Persistence and integration: state is limited to inherited command metadata: id, term, token, and deadline. The command is transported over `StorageContainerDatanodeProtocolProtos` and is consumed by datanode command processing that refreshes volume usage metrics or caches.

Risks and test signals: the id-loss during protobuf reconstruction is a behavioral risk if command status tracking expects response status to reference the original SCM command id. There are no direct tests in this subset. Tests around command status reporting or refresh handling should assert that command identity is either intentionally irrelevant or preserved by an outer wrapper.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/RefreshVolumeUsageCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/RegisteredCommand.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/RegisteredCommand.java

Purpose: `RegisteredCommand` models the response to a datanode register call. It returns the SCM registration result, the datanode identity, and the cluster ID.

Important APIs and types: the class wraps `SCMRegisteredResponseProto.ErrorCode`, `DatanodeDetails`, and cluster ID. `newBuilder()` returns a builder with `setDatanode`, `setClusterID`, `setErrorCode`, and `build`. `getProtoBufMessage()` emits `SCMRegisteredResponseProto`.

Control flow and state: the builder validates successful registrations: on `ErrorCode.success`, datanode, datanode UUID, and cluster ID must be present or `IllegalArgumentException` is thrown. Protobuf conversion always writes cluster ID, datanode UUID, and error code, and conditionally writes hostname, IP address, network name, and network location when non-empty.

Persistence and integration: this is transport response state for datanode registration. It integrates with SCM registration implementations, `DatanodeDetails`, and the `StorageContainerDatanodeProtocol` register path. No durable persistence happens in this class.

Risks and test signals: unsuccessful responses can be built with null datanode or cluster fields, but `getProtoBufMessage()` assumes `datanode` is non-null, so callers must avoid serializing incomplete failure responses or this can fail. The validation only covers success. There are no direct tests here, but `ScmTestMock.register()` constructs equivalent successful registration protobufs in test infrastructure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/RegisteredCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/ReplicateContainerCommand.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/ReplicateContainerCommand.java

Purpose: `ReplicateContainerCommand` tells a datanode to replicate a container, either from a list of source datanodes or to a target datanode depending on how the command is constructed.

Important APIs and types: the class is final and extends `SCMCommand<ReplicateContainerCommandProto>`. Static factories are `fromSources`, `toTarget`, and `forTest`. It exposes container ID, sources, target, replica index, priority, protobuf conversion, and `contributesToQueueSize()`.

Control flow and state: normal commands are created through private constructors without an explicit id, while protobuf reconstruction preserves `cmdId`. `getProto()` writes container ID, all source nodes, replica index, optional target, and priority. `getFromProtobuf()` reconstructs optional target, optional replica index, and optional priority. Queue accounting returns false for non-normal priorities.

Persistence and integration: command state is serialized through `ReplicateContainerCommandProto` and participates in SCM command queue throttling through `contributesToQueueSize`. It integrates with datanode replication tasks, container balancer or replication manager paths, and `DatanodeDetails` protobuf conversion.

Risks and test signals: source and target modes are not mutually enforced by the constructor, so invalid combinations rely on factory discipline and downstream handling. Source list mutability is exposed. Priority affects queue size and can change scheduling behavior. Direct tests are not in this subset; `TestReconcileContainerTask` gives comparable replication-task status and equality signals for a neighboring command family.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/ReplicateContainerCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/ReregisterCommand.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/ReregisterCommand.java

Purpose: `ReregisterCommand` tells a datanode to register with SCM again.

Important APIs and types: it extends `SCMCommand<ReregisterCommandProto>`, reports type `reregisterCommand`, returns a default empty `ReregisterCommandProto`, and overrides `getId()`.

Control flow and state: unlike most `SCMCommand` subclasses, `getId()` always returns `0` with a comment that id handling is not implemented for this command. `getProto()` emits no command id. The inherited term, encoded token, and deadline methods still exist and are included in `toString()`.

Persistence and integration: this is transient command signaling. It integrates with datanode endpoint state machines that need to restart registration after SCM-side state changes or rejected heartbeats. There is no local persistence in the class.

Risks and test signals: the constant id means command status tracking cannot distinguish multiple reregister commands by id. If a generic command queue assumes non-zero ids, this command is an exception. No direct tests are present in this subset; heartbeat and registration tests using `ScmTestMock` can indirectly exercise reregistration when SCM command responses include this type.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/ReregisterCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/SCMCommand.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/SCMCommand.java

Purpose: `SCMCommand` is the abstract base for commands SCM sends to datanodes. It standardizes command identity, command type, protobuf conversion, leader term, encoded token, optional deadline, and queue accounting.

Important APIs and types: the generic type parameter is a protobuf `Message`. Subclasses implement `getType()` and `getProto()`. The class implements `IdentifiableEventPayload`, so `getId()` is the event identity. `hasExpired(currentEpochMs)` enforces optional deadline semantics.

Control flow and state: constructors either allocate a long id through `HddsIdFactory.getLongId()` or accept a provided id for protobuf reconstruction. Term defaults to zero until set. Encoded token defaults to empty string. Deadline defaults to zero, which means no deadline. `hasExpired()` returns true only when a positive deadline is earlier than the checked time. `contributesToQueueSize()` defaults true and can be overridden, as `ReplicateContainerCommand` does for priority.

Persistence and integration: this base state is serialized by each concrete command's protobuf and used by SCM event queues, heartbeat command delivery, and datanode status reporting. It has no direct disk persistence.

Risks and test signals: subclasses must remember to serialize inherited metadata that matters; the base class cannot enforce that. Mutable token, term, and deadline are not synchronized. Deadline enforcement is caller-owned, so omission in command handlers can make deadlines inert. This subset contains multiple subclasses showing both normal id preservation and intentional exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/SCMCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/SetNodeOperationalStateCommand.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/SetNodeOperationalStateCommand.java

Purpose: `SetNodeOperationalStateCommand` asks a datanode to persist its current operational state, optionally with an expiry epoch.

Important APIs and types: it extends `SCMCommand<SetNodeOperationalStateCommandProto>`, uses `HddsProtos.NodeOperationalState`, exposes `getOpState()` and `getStateExpiryEpochSeconds()`, and supports `getFromProtobuf()`.

Control flow and state: construction requires explicit command id, operational state, and expiry seconds. `getProto()` writes all three values. `getFromProtobuf()` null-checks and preserves the command id, state, and expiry. The expiry value is zero for indefinite state according to the constructor documentation.

Persistence and integration: this command is transport state for SCM-to-datanode operational-state synchronization. The actual durable persistence is expected in datanode state storage, not here. It integrates with node maintenance, decommission, state transitions, and `StorageContainerDatanodeProtocolProtos`.

Risks and test signals: `opState` is not null-checked in the constructor; callers rely on protobuf builder or enum defaults to reject invalid state. The `stateExpiryEpochSeconds` field is mutable only within the class but is not final. There are no direct tests in this subset; integration tests should assert datanode-side persistence and expiry interpretation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/SetNodeOperationalStateCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/package-info.java

Purpose: this package descriptor documents `org.apache.hadoop.ozone.protocol.commands` as a set of classes that help in protobuf conversions.

Important APIs and types: it declares the Java package only. There are no classes, methods, or runtime state in the file.

Control flow, state, and persistence: none. The file contributes package-level Javadoc to generated documentation.

Dependencies and integration: it applies to the command model classes in the same package, including `SCMCommand` and its concrete command subclasses.

Risks and test signals: no executable risk. The wording is narrow but accurate for the conversion-focused command wrappers. No tests are needed beyond compilation and documentation generation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/package-info.java

Purpose: this package descriptor documents `org.apache.hadoop.ozone.protocol` as containing HDDS protocol definition classes.

Important APIs and types: it only declares the package and package-level Javadoc.

Control flow, state, and persistence: none.

Dependencies and integration: it scopes the higher-level protocol interfaces used by the PB translators, such as `StorageContainerDatanodeProtocol` and Recon-related protocol contracts.

Risks and test signals: no runtime risk. Compilation is the only practical validation signal for this file.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocolPB/ReconDatanodeProtocolPB.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocolPB/ReconDatanodeProtocolPB.java

Purpose: `ReconDatanodeProtocolPB` is the protobuf RPC interface used by datanodes when talking to Recon, reusing the storage-container datanode protocol surface.

Important APIs and types: it extends `StorageContainerDatanodeProtocolPB` and adds Hadoop RPC annotations: `@ProtocolInfo` with protocol name `org.apache.hadoop.ozone.protocol.ReconDatanodeProtocol` and version `1`, plus `@KerberosInfo` with Recon server principal and datanode client principal.

Control flow and state: it is an interface with no methods beyond the inherited PB blocking interface. Runtime behavior is supplied by Hadoop RPC and the inherited protocol translator/service implementation.

Persistence and integration: this is an RPC binding contract, not persisted state. It integrates with Recon, datanode authentication, `HddsConfigKeys.HDDS_DATANODE_KERBEROS_PRINCIPAL_KEY`, and Recon configuration principal keys.

Risks and test signals: because it inherits SCM datanode PB methods, authorization and endpoint routing must ensure calls intended for Recon are served by Recon implementations. Principal misconfiguration will break secure RPC. No direct tests are in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocolPB/ReconDatanodeProtocolPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocolPB/StorageContainerDatanodeProtocolClientSideTranslatorPB.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocolPB/StorageContainerDatanodeProtocolClientSideTranslatorPB.java

Purpose: this client-side translator adapts the Java `StorageContainerDatanodeProtocol` interface to the protobuf RPC interface `StorageContainerDatanodeProtocolPB`.

Important APIs and types: it implements `StorageContainerDatanodeProtocol`, `ProtocolTranslator`, and `Closeable`. The central helper is `submitRequest(Type, Consumer<SCMDatanodeRequest.Builder>)`, which wraps a typed request and calls `rpcProxy.submitRequest`. Public methods implement `getVersion`, `sendHeartbeat`, and `register`.

Control flow and state: `NULL_RPC_CONTROLLER` is passed because Hadoop protobuf RPC does not use a controller here. `submitRequest()` sets the `cmdType`, lets the caller populate the matching payload, builds the wrapper, and unwraps `ServiceException` to an `IOException` through `ProtobufHelper.getRemoteException`. `register()` builds `SCMRegisterRequestProto` with extended datanode details, container report, pipeline reports, node report, and optional layout info.

Persistence and integration: no local persistence. It owns an RPC proxy and stops it in `close()`. It integrates with datanode endpoint state machines and SCM registration/heartbeat/version RPCs.

Risks and test signals: `getVersion()` ignores its request argument and sends an empty request, which is fine only if version requests have no fields. Response status is not checked locally; callers assume the server filled the requested response field. `SCMTestUtils.createEndpoint()` constructs this translator for test endpoint state machines.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocolPB/StorageContainerDatanodeProtocolClientSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocolPB/StorageContainerDatanodeProtocolPB.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocolPB/StorageContainerDatanodeProtocolPB.java

Purpose: `StorageContainerDatanodeProtocolPB` is the Hadoop RPC protobuf service interface for datanode-to-SCM communication.

Important APIs and types: it extends `StorageContainerDatanodeProtocolService.BlockingInterface`, adds `@ProtocolInfo` for protocol name `org.apache.hadoop.ozone.protocol.StorageContainerDatanodeProtocol` version `1`, and adds `@KerberosInfo` with SCM server and datanode client principal config keys.

Control flow and state: this interface has no implementation or local state. Hadoop RPC uses the annotations and generated blocking interface to bind client and server calls.

Persistence and integration: it is an RPC contract integrated with the client-side and server-side translators, SCM security configuration, datanode Kerberos identity, and generated protobuf service definitions.

Risks and test signals: protocol name and version are compatibility-sensitive. Principal keys must match secure deployment configuration. `SCMTestUtils.startScmRpcServer()` sets the protobuf RPC engine for this interface and registers a reflective blocking service, which is the primary test signal in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocolPB/StorageContainerDatanodeProtocolPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocolPB/StorageContainerDatanodeProtocolServerSideTranslatorPB.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocolPB/StorageContainerDatanodeProtocolServerSideTranslatorPB.java

Purpose: this server-side translator receives protobuf RPC requests and forwards them to a Java `StorageContainerDatanodeProtocol` implementation.

Important APIs and types: it implements `StorageContainerDatanodeProtocolPB`, wraps an `OzoneProtocolMessageDispatcher<SCMDatanodeRequest, SCMDatanodeResponse, Type>`, and exposes `submitRequest`, `processMessage`, and a helper `register()`.

Control flow and state: `submitRequest()` delegates to the dispatcher with trace ID and command type. `processMessage()` switches on `Type`: `GetVersion`, `SendHeartbeat`, and `Register` each return an OK `SCMDatanodeResponse` with the corresponding implementation result. Unknown types throw `ServiceException`. `register()` extracts container, node, pipeline, and layout reports; if layout version is absent it supplies the initial layout version for backward compatibility.

Persistence and integration: no durable state. It integrates generated protobuf RPC, protocol metrics, logging, SCM implementation code, and upgrade layout compatibility helpers.

Risks and test signals: only three command types are supported in this translator; adding a new datanode protocol RPC requires updating both client and server switches. Exceptions from `IOException` and `TimeoutException` are wrapped as `ServiceException`. `SCMTestUtils.startScmRpcServer()` exercises this translator in tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocolPB/StorageContainerDatanodeProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocolPB/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocolPB/package-info.java

Purpose: this package descriptor documents `org.apache.hadoop.ozone.protocolPB` as containing storage container protocol translator related classes.

Important APIs and types: it only declares the package and package-level Javadoc.

Control flow, state, and persistence: none.

Dependencies and integration: it documents the package containing the PB interfaces and client/server translators used by datanode-to-SCM and datanode-to-Recon RPC.

Risks and test signals: no runtime risk. Compilation and documentation generation validate it.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocolPB/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/resources/webapps/hddsDatanode/dn.js -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/resources/webapps/hddsDatanode/dn.js

Purpose: `dn.js` defines AngularJS modules, routes, controllers, filters, and formatting helpers for the HDDS datanode web UI.

Important APIs and functions: it creates module `dn` depending on `ozone` and `nvd3`, registers `dnOverview`, adds routes `/iostatus` and `/dn-scanner`, defines `IOStatusController`, `DNScannerController`, filters `millisecondsToMinutes` and `twoDecimalPlaces`, and helper functions `transform()` and `convertTimestampToDate()`.

Control flow and state: `dnOverview` fetches JMX volume metrics and SCM connection manager metrics. It transforms byte-size fields to human-readable units and converts heartbeat timestamps from seconds since epoch to local date-time strings. IO status and scanner controllers fetch their respective JMX beans into controller fields. Filters defensively return `Invalid input` for `NaN`.

Persistence and integration: all state is client-side view model data fetched from datanode JMX endpoints. The file integrates with Angular route templates `dn-overview.html`, `iostatus.html`, and `dn-scanner.html`, plus JMX bean naming conventions.

Risks and test signals: there is no error handling for failed `$http` requests. `transform()` loops while `Math.floor(v) > 0`, so zero and non-numeric inputs can produce odd output. Timestamp formatting uses browser local time. The use of arrow functions and template literals requires browser support despite AngularJS age. No tests are in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/resources/webapps/hddsDatanode/dn.js -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/TestHddsDatanodeService.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/TestHddsDatanodeService.java

Purpose: this JUnit test class validates selected `HddsDatanodeService` startup, shutdown, JMX, and HTTP/HTTPS port behaviors.

Important APIs and tests: `setUp()` creates an `OzoneConfiguration` with SCM addresses, metadata and datanode volume dirs, a mock service plugin, security disabled, and token flags enabled. Tests include `testDeletedContainersClearedOnShutdown`, `testDatanodeUuidInMXBean`, and `testHttpPorts`. `MockService` is a no-op `ServicePlugin`.

Control flow and state: the deletion test starts the service under each key-value schema version, accesses the single `HddsVolume`, creates and moves a container into the deleted container directory, then stops, joins, closes, and shuts down metrics. It asserts deleted tmp containers are removed on shutdown. The JMX test reads `DatanodeUuid` from the platform MBean server and matches it to service details. The HTTP policy test checks published datanode HTTP/HTTPS ports according to `HttpConfig.Policy`.

Persistence and integration: tests create real temp metadata and volume directories, use `ContainerTestUtils` to create containers, and observe MBeans and metrics system behavior.

Risks and test signals: the setup intentionally validates that token misconfiguration does not block insecure datanode startup. Cleanup relies on explicit service close and `DefaultMetricsSystem.shutdown()` to prevent cross-test contamination. It is an integration-style test with real filesystem state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/TestHddsDatanodeService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/TestHddsSecureDatanodeInit.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/TestHddsSecureDatanodeInit.java

Purpose: this test class validates secure datanode certificate-client initialization and certificate rotation behavior for `HddsDatanodeService`.

Important APIs and tests: setup enables Ozone security, configures short renewal and CA rotation intervals, uses an overridden service that mocks `createScmSecurityClient()`, captures `DNCertificateClient` logs, and prepares key/certificate storage helpers. Startup cases 0 through 7 cover combinations of missing/present private key, public key, and certificate. Rotation tests validate renewal success and recoverable failure.

Control flow and state: each test deletes key and certificate files, creates a fresh `DNCertificateClient`, then writes selected key/cert material before calling `service.initializeCertificateClient(client)`. Expected outcomes include `GETCERT`, `FAILURE`, or `SUCCESS` log signals and key/cert nullability checks. Rotation tests mock `getDataNodeCertificateChain()` and root CA lookup, start the renewer service, and wait until serial numbers change.

Persistence and integration: state is persisted in temp key and certificate directories via `KeyStorage` and `CertificateCodec`. The tests integrate SCM security protocol mocks, self-signed certificate generation, and datanode certificate-renewer scheduling.

Risks and test signals: `callQuietly()` prints and ignores setup exceptions, so failures before assertions can be noisy. The recoverable-failure test is marked flaky and uses `Thread.sleep(CERT_LIFETIME * 1000)`. These tests are high-value because they lock down secure bootstrap edge cases and renewal recovery.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/TestHddsSecureDatanodeInit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/checksum/ContainerMerkleTreeTestUtils.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/checksum/ContainerMerkleTreeTestUtils.java

Purpose: this final utility class provides shared builders and assertions for container checksum tree, Merkle tree, diff, and reconciliation tests.

Important APIs and functions: helpers include `assertTreesSortedAndMatch`, `buildChunk`, `readChecksumFile`, `buildTestTree`, `getDeletedBlockData`, `buildTestTreeWithMismatches`, `updateTreeProto`, `assertContainerDiffMatch`, `containerChecksumFileExists`, `verifyAllDataChecksumsMatch`, and `buildBlockData`.

Control flow and state: the builders synthesize deterministic chunk, block, and container Merkle structures from Ozone configuration chunk size and checksum settings. Mismatch introduction mutates a tree builder by removing blocks, removing chunks, or corrupting chunk checksum values while recording the expected `ContainerDiffReport`. File helpers read and write the `.tree` checksum protobuf directly. `verifyAllDataChecksumsMatch()` compares in-memory container data, checksum file data, and RocksDB metadata.

Persistence and integration: utilities interact with actual container checksum files under container metadata paths and RocksDB through `BlockUtils.getDB`. They integrate with `ContainerChecksumTreeManager`, `ContainerMerkleTreeWriter`, `ContainerDiffReport`, `HddsDatanodeService`, and key-value container data.

Risks and test signals: the direct file helpers intentionally bypass production synchronization, so they are test-only. Random checksum mutation prevents reliance on exact corrupt values. Assertions enforce sorted block IDs and chunk offsets, making ordering part of the contract.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/checksum/ContainerMerkleTreeTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/checksum/TestContainerChecksumTreeManager.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/checksum/TestContainerChecksumTreeManager.java

Purpose: this test class validates `ContainerChecksumTreeManager` file creation, read/modify/write behavior, corruption recovery, deleted-block merging, metrics, and path compatibility.

Important APIs and tests: it mocks `KeyValueContainerData` with container ID and metadata path, uses `ContainerChecksumTreeManager`, and checks methods such as `updateTree`, `addDeletedBlocks`, `read`, `diff`, `hasDataChecksum`, `getContainerChecksumFile`, and metric counters.

Control flow and state: tests write empty trees, write deleted-block-only trees, write normal trees, deduplicate and sort deleted blocks, preserve deleted blocks across tree writes, preserve trees across deleted-block writes, and assert read/write/create latency metrics change. Failure tests make tmp-file writes fail, corrupt final files with invalid bytes, and truncate final files to empty protobufs, then verify recovery.

Persistence and integration: the checksum file name is asserted as `<containerID>.tree` under the metadata path, explicitly protecting on-disk compatibility. Writes use temporary files and swaps, and reads use protobuf parsing. The diff failure test verifies a bad peer checksum increments failure metrics.

Risks and test signals: permission manipulation may behave differently on some filesystems. The tests strongly signal that production must tolerate corrupted or empty checksum files and keep existing valid files intact on tmp write failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/checksum/TestContainerChecksumTreeManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/checksum/TestContainerDiff.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/checksum/TestContainerDiff.java

Purpose: this test class validates the container Merkle tree diff algorithm used to decide whether a local container needs repair relative to a peer checksum tree.

Important APIs and tests: parameterized mismatch cases cover missing blocks, missing chunks, and corrupt chunks. Tests call `ContainerChecksumTreeManager.read()` and `diff()`, then assert `ContainerDiffReport` contents and metrics. Additional tests cover no-diff cases and deleted-block filtering.

Control flow and state: one direction of mismatch matters: if the local tree is missing or corrupt relative to the peer, the diff reports repair work. If only the peer is missing or corrupt relative to local, this local diff reports no repair because the peer should generate its own diff. Deleted blocks in the peer or local tree suppress repair entries for those blocks.

Persistence and integration: tests write local checksum protobufs to temp files using helpers, construct peer `ContainerChecksumInfo` in memory, and verify `ContainerChecksumTreeManager` metrics such as repair/no-repair counts and identified missing/corrupt counts.

Risks and test signals: the tests define subtle asymmetric semantics. A regression that treats peer deficiencies as local repair work would cause unnecessary repairs. Deletion handling is critical because deleted blocks must not be resurrected by reconciliation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/checksum/TestContainerDiff.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/checksum/TestContainerMerkleTreeWriter.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/checksum/TestContainerMerkleTreeWriter.java

Purpose: this test class validates `ContainerMerkleTreeWriter`, including checksum construction, ordering, duplicate handling, deleted-block semantics, proto round trips, and merge/update conflict rules.

Important APIs and tests: tests cover empty trees, one-chunk trees, missing chunks, block ID inclusion in checksums, identical-block determinism, non-contiguous block IDs, append behavior, `setDeletedBlock`, constructor from proto, `addDeletedBlocks`, and `update(existingTree)`.

Control flow and state: expected trees are built independently by hashing chunk checksum bytes, block IDs plus chunk checksums, and block checksums through the same checksum implementation. Writer output is compared for sorted block IDs and chunk offsets. Duplicate chunks overwrite existing entries by offset. Deleted blocks remove chunk trees and carry deleted checksums. Merge tests define precedence: existing deleted blocks override writer live blocks, writer live blocks override existing live blocks, writer deleted blocks override existing live blocks, and writer deleted checksums override existing deleted checksums.

Persistence and integration: this class is in-memory only, but it defines the protobuf structure written later by `ContainerChecksumTreeManager`. It integrates with `ContainerProtos`, `BlockData`, and checksum byte-buffer implementation.

Risks and test signals: checksum semantics intentionally include block ID, preventing identical content under different block IDs from colliding. Deleted-block precedence is central to avoiding deleted data resurrection during checksum file updates.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/checksum/TestContainerMerkleTreeWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/checksum/TestReconcileContainerTask.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/checksum/TestReconcileContainerTask.java

Purpose: this test class validates task status and equality behavior for `ReconcileContainerTask`.

Important APIs and tests: tests construct tasks from mocked `ContainerController`, mocked `DNContainerOperationClient`, and `ReconcileContainerCommand`. They inspect `AbstractReplicationTask.Status` transitions and Java equality.

Control flow and state: `testFailedTaskStatus` makes `mockController.reconcileContainer` throw `IOException`, then asserts the task moves from `QUEUED` to `FAILED`. `testSuccessfulTaskStatus` runs without exception and asserts `DONE`. Equality tests show tasks with the same container ID are equal even when peer sets differ, while different container IDs are not equal.

Persistence and integration: no filesystem or network persistence. The task integrates reconciliation command state, container controller repair logic, and replication task scheduling semantics.

Risks and test signals: equality ignoring peers means the scheduler deduplicates reconciliation per container ID, not per peer set. That prevents duplicate work but may hide peer-set changes if a queued task already exists. Status tests confirm exceptions are contained and reflected in task state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/checksum/TestReconcileContainerTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/BlockDeletingServiceTestImpl.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/BlockDeletingServiceTestImpl.java

Purpose: `BlockDeletingServiceTestImpl` is a test-only subclass of `BlockDeletingService` that makes block deletion execution manually triggerable and observable.

Important APIs and types: constructor wires the superclass with zero service timeout, millisecond units, a batch limit of `10`, and a new `ContainerChecksumTreeManager`. Test APIs are `runDeletingTasks()`, `isStarted()`, and `getTimesOfProcessed()`.

Control flow and state: `start()` launches a daemon testing thread that repeatedly creates a `CountDownLatch`, waits for `runDeletingTasks()` to count it down, submits one `PeriodicalTask` to the executor, waits up to three seconds, and increments `numOfProcessed` on success. `shutdown()` interrupts the testing thread and delegates to superclass shutdown.

Persistence and integration: actual deletion persistence comes from inherited `BlockDeletingService` behavior against `OzoneContainer`; this subclass only controls scheduling. It integrates checksum tree updates by constructing a manager for the superclass.

Risks and test signals: `runDeletingTasks()` throws if the latch is already zero, preventing double triggers for one cycle. If the task fails or times out, the test thread returns and stops processing further triggers. It is package-private and intentionally limited to tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/BlockDeletingServiceTestImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/ContainerTestUtils.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/ContainerTestUtils.java

Purpose: `ContainerTestUtils` is a broad test utility class for constructing datanode endpoints, containers, handlers, dispatchers, scan results, layouts, Ratis servers, and block metadata.

Important APIs and functions: major helpers include `createEndpoint`, `getOzoneContainer`, `getMockContext`, `createDatanodeDetails`, `getContainer`, overloaded `getKeyValueHandler`, `getHddsDispatcher`, schema V3 toggles, `createDbInstancesForTestIfNeeded`, `setupMockContainer`, healthy/unhealthy scan result builders, `addContainerToDeletedDir`, `addContainerToVolumeDir`, `getNoopContainerDispatcher`, `getEmptyContainerController`, `newXceiverServerRatis`, `initializeDatanodeLayout`, and `createBlockMetaData`.

Control flow and state: endpoint creation configures protobuf RPC and wraps a proxy in `StorageContainerDatanodeProtocolClientSideTranslatorPB`. Container helpers create realistic `KeyValueContainerData`, choose volumes, create and close containers, or move them to deleted dirs. Mock helpers stub scan and context behavior. Metadata creation writes block rows and checksum-bearing chunks into the container DB.

Persistence and integration: utilities create real volume directories, initialize layout storage, create container DB entries, and can construct live RPC clients and Ratis servers. They integrate with most container-service subsystems.

Risks and test signals: because this utility is broad, changes have large test blast radius. Static shared no-op dispatcher and empty controller are safe only for tests that do not need real dispatch behavior. Schema V3 DB initialization mirrors production volume checks and is important for compatibility tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/ContainerTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/SCMTestUtils.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/SCMTestUtils.java

Purpose: `SCMTestUtils` provides test helpers for starting mock SCM RPC servers and building datanode test configurations.

Important APIs and functions: helpers include `startScmRpcServer` overloads, private `startRpcServer`, `getReuseableAddress`, `getConf`, `getOzoneConf`, `getReplicationType`, and `getReplicationFactor`. `CLUSTER_ID` is a shared fixed cluster id for tests.

Control flow and state: `startScmRpcServer` converts Ozone configuration to Hadoop configuration, sets `ProtobufRpcEngine` for `StorageContainerDatanodeProtocolPB`, wraps a `StorageContainerDatanodeProtocolServerSideTranslatorPB` in a reflective blocking service, starts the RPC server, and can update `OZONE_SCM_NAMES` to the actual listener address when binding to port zero. `getConf()` creates datanode, metadata, and datanode ID directories and configures mock space usage and test authorization.

Persistence and integration: helpers create temp filesystem directories and live Hadoop RPC servers. They integrate with `ScmTestMock`, PB translators, `ProtocolMessageMetrics`, and RATIS configuration.

Risks and test signals: `getReuseableAddress()` is inherently race-prone, and the newer port-zero overload documents avoiding that TOCTOU race. Tests using live RPC must shut servers down. Replication type/factor helpers mirror the RATIS enabled flag.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/SCMTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/ScmTestMock.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/ScmTestMock.java

Purpose: `ScmTestMock` is an in-memory `StorageContainerDatanodeProtocol` implementation used by datanode tests.

Important APIs and state: it tracks RPC count, heartbeat count, container report count, command status report count, cluster ID, SCM ID, optional response delay, per-datanode container reports, per-datanode node reports, command status reports, and queued SCM command responses. Public methods expose counters, aggregate container/key/bytes-used counts, reset state, and mutate queued SCM commands and IDs.

Control flow: `getVersion()` increments RPC count, optionally sleeps, and returns version, SCM ID, and cluster ID. `sendHeartbeat()` increments RPC and heartbeat counts, records command status reports, optionally sleeps, and returns queued SCM command protos with the heartbeat datanode UUID. `register()` records node and container reports, optionally sleeps, and returns a successful registration protobuf with a generated cluster ID and datanode UUID.

Persistence and integration: all state is in memory. It integrates with live PB RPC through `SCMTestUtils`, datanode endpoint tests, SCM command delivery tests, and report aggregation assertions.

Risks and test signals: maps keyed by `DatanodeDetails` require consistent equality semantics. Raw `Map` usage in `updateContainerReport` bypasses generic checks. `register()` returns a random cluster ID rather than the mock's configured `clusterId`, which may be intentional for older tests but is surprising. Response delay simulates slow SCM calls.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/ScmTestMock.java -->
