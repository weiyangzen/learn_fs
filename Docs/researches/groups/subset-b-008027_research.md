# subset-b-008027 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-admin/src/main/proto/ScmAdminProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-admin/src/main/proto/ScmAdminProtocol.proto

## Purpose

Defines the SCM administrative protobuf envelope used by Ozone clients to query and mutate container, node, pipeline, safe-mode, replication-manager, deleted-block, upgrade, container-token, container-balancer, SCM decommission, metrics, reconcile, and suppression operations through one submitRequest RPC.

## Important APIs, types, and functions

Package: `hadoop.hdds.container`. Imports: `hdds.proto`. Important declarations include `ScmContainerLocationRequest, ScmContainerLocationResponse, ContainerRequestProto, ContainerResponseProto, GetContainerRequestProto, GetContainerResponseProto, GetContainerWithPipelineRequestProto, GetContainerWithPipelineResponseProto, GetContainerReplicasRequestProto, GetContainerReplicasResponseProto, GetContainerWithPipelineBatchRequestProto, GetExistContainerWithPipelinesInBatchRequestProto, GetSafeModeRuleStatusesRequestProto, SafeModeRuleStatusProto, GetSafeModeRuleStatusesResponseProto, GetContainerWithPipelineBatchResponseProto, GetExistContainerWithPipelinesInBatchResponseProto, SCMListContainerIDsRequestProto, SCMListContainerIDsResponseProto, SCMListContainerRequestProto, SCMListContainerResponseProto, SCMDeleteContainerRequestProto, SCMDeleteContainerResponseProto, SCMCloseContainerRequestProto, SCMCloseContainerResponseProto, NodeQueryRequestProto, NodeQueryResponseProto, SingleNodeQueryRequestProto, ...`. RPC methods: submitRequest(ScmContainerLocationRequest -> ScmContainerLocationResponse).

## Control flow

Callers fill ScmContainerLocationRequest with a Type enum and exactly one matching request body. The server dispatches on cmdType and returns ScmContainerLocationResponse with a Status, optional message, traceID, and the corresponding response body. The nested request/response messages carry no persistence themselves; they serialize administrative intent and SCM state snapshots.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

The main risk is envelope drift: adding a Type without a matching optional field, response field, dispatcher branch, or compatibility test yields requests that compile but fail at runtime. Many fields are optional proto2 fields, so callers must distinguish absent values from default values.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-admin/src/main/proto/ScmAdminProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-client/dev-support/findbugsExcludeFile.xml

## Purpose

This SpotBugs/FindBugs exclude filter suppresses findings for generated protobuf packages in `interface-client`. The matched packages are `org.apache.hadoop.hdds.protocol.datanode.proto`, `org.apache.hadoop.hdds.protocol.proto`, `org.apache.hadoop.hdds.protocol.scm.proto`.

## Important APIs, types, and functions

The file uses `<FindBugsFilter>` with `<Match><Package name="..."/></Match>` entries. It has no executable functions; its API is the XML contract consumed by the SpotBugs Maven plugin.

## Control flow

During Maven analysis, the module's SpotBugs plugin reads this filter and skips matching generated classes. That prevents generated protobuf code from dominating static-analysis output.

## State and persistence behavior

The file persists build configuration only. It does not affect runtime behavior or generated class contents.

## Dependencies and integration points

It is referenced by the module POM through `spotbugs-maven-plugin` `excludeFilterFile` configuration. The package names must match the Java packages emitted by protobuf generation.

## Risks and edge cases

The main risk is over-broad suppression: if hand-written classes are later placed under a suppressed generated package, SpotBugs will ignore them. A stale package name also creates noisy generated-code reports.

## Test signals

Run module SpotBugs or Maven verification and confirm generated protobuf packages are suppressed while hand-written package findings remain visible.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-client/pom.xml

## Purpose

Builds the hdds-interface-client jar containing generated Java protobuf classes for common HDDS, datanode client, disk balancer, IPC, RPC header, protobuf RPC engine, and reconfigure protocols.

## Important APIs, types, and functions

Artifact: `hdds`. Modules: none in this POM. Key dependencies include `com.google.protobuf:protobuf-java`, `org.apache.ratis:ratis-thirdparty-misc`. Key plugins include `com.salesforce.servicelibs:proto-backwards-compatibility`, `org.apache.maven.plugins:maven-compiler-plugin`, `org.xolstice.maven.plugins:protobuf-maven-plugin`, `org.apache.maven.plugins:maven-antrun-plugin`.

## Control flow

The protobuf-maven-plugin compiles selected proto files, including a custom Ratis generation path for DatanodeClientProtocol. Tests and SpotBugs are skipped because the module contains generated code only.

## State and persistence behavior

The POM persists no runtime state. It controls generated source directories, module membership, dependency resolution, native build outputs under `target`, and test/runtime packaging artifacts.

## Dependencies and integration points

It integrates with the parent Ozone Maven reactor, generated protobuf sources, SpotBugs exclude files, rocksdbjni, CMake/JNI tooling for native builds where enabled, and downstream modules that consume the produced jars or test jars.

## Risks and edge cases

Generated-source modules are sensitive to protoc version, include lists, and package names. Omitting a proto from plugin includes or compatibility checks can silently remove public generated APIs.

## Test signals

Useful signals are a module-level Maven compile, protobuf generation for interface modules, native-profile build on supported Linux agents for rocks-native, and downstream module tests that import generated classes or managed RocksDB wrappers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/DatanodeClientProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/DatanodeClientProtocol.proto

## Purpose

Defines datanode container command contracts for client and intra-datanode traffic, including streaming command exchange, container copy/download/upload, block and chunk IO, checksum trees, small-file helpers, and container metadata reports.

## Important APIs, types, and functions

Package: `hadoop.hdds.datanode`. Imports: none. Important declarations include `DatanodeBlockID, KeyValue, ContainerCommandRequestProto, ContainerCommandResponseProto, ContainerDataProto, Container2BCSIDMapProto, CreateContainerRequestProto, CreateContainerResponseProto, ReadContainerRequestProto, ReadContainerResponseProto, UpdateContainerRequestProto, UpdateContainerResponseProto, DeleteContainerRequestProto, DeleteContainerResponseProto, ListContainerRequestProto, ListContainerResponseProto, CloseContainerRequestProto, CloseContainerResponseProto, BlockData, PutBlockRequestProto, PutBlockResponseProto, FinalizeBlockRequestProto, FinalizeBlockResponseProto, GetBlockRequestProto, GetBlockResponseProto, DeleteBlockRequestProto, GetCommittedBlockLengthRequestProto, GetCommittedBlockLengthResponseProto, ...`. RPC methods: send(stream ContainerCommandRequestProto -> stream ContainerCommandResponseProto), download(CopyContainerRequestProto -> stream CopyContainerResponseProto), upload(stream SendContainerRequest -> SendContainerResponse).

## Control flow

Clients send ContainerCommandRequestProto values tagged with Type; the datanode responds with ContainerCommandResponseProto carrying Result and an operation-specific payload. The bidirectional send RPC handles ordinary xceiver commands, while download and upload stream raw container transfer messages for replication and repair.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

The protocol mixes metadata, data buffers, checksums, tokens, and container/block lifecycle actions. Compatibility risk is high around enum ordinal changes, required fields, token/signature fields, checksum versioning, and streaming backpressure.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/DatanodeClientProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/DiskBalancerProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/DiskBalancerProtocol.proto

## Purpose

Defines the datanode disk-balancer control protocol: read current disk-balancer info, start balancing with a target plan, stop a running balancer, and update disk-balancer configuration.

## Important APIs, types, and functions

Package: `hadoop.hdds`. Imports: `hdds.proto`. Important declarations include `GetDiskBalancerInfoRequestProto, GetDiskBalancerInfoResponseProto, StartDiskBalancerRequestProto, StartDiskBalancerResponseProto, StopDiskBalancerRequestProto, StopDiskBalancerResponseProto, UpdateDiskBalancerConfigurationRequestProto, UpdateDiskBalancerConfigurationResponseProto, DiskBalancerProtocolService`. RPC methods: getDiskBalancerInfo(GetDiskBalancerInfoRequestProto -> GetDiskBalancerInfoResponseProto), startDiskBalancer(StartDiskBalancerRequestProto -> StartDiskBalancerResponseProto), stopDiskBalancer(StopDiskBalancerRequestProto -> StopDiskBalancerResponseProto), updateDiskBalancerConfiguration(UpdateDiskBalancerConfigurationRequestProto -> UpdateDiskBalancerConfigurationResponseProto).

## Control flow

The service has four unary RPCs. Requests carry a datanode identifier, balancing plan or configuration, and responses return status booleans/messages or DatanodeDiskBalancerInfoProto from hdds.proto.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

Operational risk is around stale datanode UUIDs, malformed plans, concurrent start/stop calls, and config updates while a balancer is running. Tests should pin idempotency and validation behavior.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/DiskBalancerProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/IpcConnectionContext.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/IpcConnectionContext.proto

## Purpose

Defines Hadoop-compatible IPC framing metadata for protobuf RPC calls, including connection user/protocol context, request method headers, request and response status headers, tracing/caller context, and SASL negotiation messages.

## Important APIs, types, and functions

Package: `hadoop.common`. Imports: none. Important declarations include `UserInformationProto, IpcConnectionContextProto`. RPC methods: none.

## Control flow

Generated classes are used by the RPC engine before service-level messages are dispatched. Request headers identify rpc kind, method, client ID, retry state, trace info, and caller context; response headers carry call ID, status, exception metadata, server IP, and SASL state.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

These messages sit below application protocols, so incompatible tag or enum changes can break every RPC. Security-sensitive fields such as SASL auth lists and effective user names must be validated by the transport layer rather than trusted because they are serialized input.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/IpcConnectionContext.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/ProtobufRpcEngine.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/ProtobufRpcEngine.proto

## Purpose

Defines Hadoop-compatible IPC framing metadata for protobuf RPC calls, including connection user/protocol context, request method headers, request and response status headers, tracing/caller context, and SASL negotiation messages.

## Important APIs, types, and functions

Package: `hadoop.common`. Imports: none. Important declarations include `RequestHeaderProto`. RPC methods: none.

## Control flow

Generated classes are used by the RPC engine before service-level messages are dispatched. Request headers identify rpc kind, method, client ID, retry state, trace info, and caller context; response headers carry call ID, status, exception metadata, server IP, and SASL state.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

These messages sit below application protocols, so incompatible tag or enum changes can break every RPC. Security-sensitive fields such as SASL auth lists and effective user names must be validated by the transport layer rather than trusted because they are serialized input.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/ProtobufRpcEngine.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/ReconfigureProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/ReconfigureProtocol.proto

## Purpose

Defines the generic runtime reconfiguration RPC contract used to identify a server, start reconfiguration, query reconfiguration status, and list reconfigurable properties.

## Important APIs, types, and functions

Package: `hadoop.hdds`. Imports: none. Important declarations include `GetServerNameRequestProto, GetServerNameResponseProto, StartReconfigureRequestProto, StartReconfigureResponseProto, GetReconfigureStatusRequestProto, GetConfigurationChangeProto, GetReconfigureStatusResponseProto, ListReconfigurePropertiesRequestProto, ListReconfigurePropertiesResponseProto, ReconfigureProtocolService`. RPC methods: getServerName(GetServerNameRequestProto -> GetServerNameResponseProto), getReconfigureStatus(GetReconfigureStatusRequestProto -> GetReconfigureStatusResponseProto), startReconfigure(StartReconfigureRequestProto -> StartReconfigureResponseProto), listReconfigureProperties(ListReconfigurePropertiesRequestProto -> ListReconfigurePropertiesResponseProto).

## Control flow

Clients call startReconfigure, then poll getReconfigureStatus. Status responses contain the start/end timestamps and repeated GetConfigurationChangeProto entries with property, old value, new value, and error text.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

The protocol exposes mutable runtime configuration, so authorization and server-side property validation are crucial. Empty strings and absent fields can be ambiguous for old/new values.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/ReconfigureProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/RpcHeader.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/RpcHeader.proto

## Purpose

Defines Hadoop-compatible IPC framing metadata for protobuf RPC calls, including connection user/protocol context, request method headers, request and response status headers, tracing/caller context, and SASL negotiation messages.

## Important APIs, types, and functions

Package: `hadoop.common`. Imports: none. Important declarations include `RPCTraceInfoProto, RPCCallerContextProto, RpcRequestHeaderProto, RpcResponseHeaderProto, RpcSaslProto, SaslAuth, RpcKindProto, OperationProto, RpcStatusProto, RpcErrorCodeProto, SaslState`. RPC methods: none.

## Control flow

Generated classes are used by the RPC engine before service-level messages are dispatched. Request headers identify rpc kind, method, client ID, retry state, trace info, and caller context; response headers carry call ID, status, exception metadata, server IP, and SASL state.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

These messages sit below application protocols, so incompatible tag or enum changes can break every RPC. Security-sensitive fields such as SASL auth lists and effective user names must be validated by the transport layer rather than trusted because they are serialized input.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/RpcHeader.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/hdds.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/hdds.proto

## Purpose

Provides common HDDS protobuf types shared across client, server, and admin interfaces: datanode and SCM identity, node state, pipeline and container metadata, replication configuration, tokens/secrets, reports, topology, compaction, deleted-block, and disk-balancer structures.

## Important APIs, types, and functions

Package: `hadoop.hdds`. Imports: none. Important declarations include `UUID, DatanodeIDProto, DatanodeDetailsProto, ExtendedDatanodeDetailsProto, MoveDataNodePairProto, OzoneManagerDetailsProto, ScmNodeDetailsProto, NodeDetailsProto, Port, PipelineID, ContainerID, Pipeline, KeyValue, Node, NodePool, DatanodeUsageInfoProto, ContainerInfoProto, ContainerWithPipeline, GetScmInfoRequestProto, GetScmInfoResponseProto, AddScmRequestProto, AddScmResponseProto, RemoveScmRequestProto, RemoveScmResponseProto, ECReplicationConfig, DefaultReplicationConfig, ExcludeListProto, ContainerBlockID, ...`. RPC methods: none.

## Control flow

Other protocol files import this file and embed its messages as stable wire-level building blocks. There is no executable control flow; behavior comes from generated Java builders and from consumers that interpret lifecycle enums, IDs, token bytes, and repeated metadata lists.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

Because this file is foundational, changing tags or enum values can break many modules. Optional identity, topology, and security fields require careful presence checks, and repeated maps encoded as KeyValue-style messages can carry duplicate keys unless consumers normalize them.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-client/src/main/proto/hdds.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-server/dev-support/findbugsExcludeFile.xml

## Purpose

This SpotBugs/FindBugs exclude filter suppresses findings for generated protobuf packages in `interface-server`. The matched packages are `org.apache.hadoop.hdds.protocol.proto`, `org.apache.hadoop.hdds.protocol.scm.proto`.

## Important APIs, types, and functions

The file uses `<FindBugsFilter>` with `<Match><Package name="..."/></Match>` entries. It has no executable functions; its API is the XML contract consumed by the SpotBugs Maven plugin.

## Control flow

During Maven analysis, the module's SpotBugs plugin reads this filter and skips matching generated classes. That prevents generated protobuf code from dominating static-analysis output.

## State and persistence behavior

The file persists build configuration only. It does not affect runtime behavior or generated class contents.

## Dependencies and integration points

It is referenced by the module POM through `spotbugs-maven-plugin` `excludeFilterFile` configuration. The package names must match the Java packages emitted by protobuf generation.

## Risks and edge cases

The main risk is over-broad suppression: if hand-written classes are later placed under a suppressed generated package, SpotBugs will ignore them. A stale package name also creates noisy generated-code reports.

## Test signals

Run module SpotBugs or Maven verification and confirm generated protobuf packages are suppressed while hand-written package findings remain visible.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-server/pom.xml

## Purpose

Builds the hdds-interface-server jar containing generated Java protobuf classes for SCM server-side and inter-SCM protocols. It depends on hdds-interface-client for shared hdds.proto types.

## Important APIs, types, and functions

Artifact: `hdds`. Modules: none in this POM. Key dependencies include `com.google.protobuf:protobuf-java`, `org.apache.ozone:hdds-interface-client`, `org.apache.ratis:ratis-thirdparty-misc`. Key plugins include `com.salesforce.servicelibs:proto-backwards-compatibility`, `org.apache.maven.plugins:maven-compiler-plugin`, `org.xolstice.maven.plugins:protobuf-maven-plugin`, `org.apache.maven.plugins:maven-antrun-plugin`.

## Control flow

The protobuf plugin compiles server protocol files into Java, with compiler annotation processing disabled and tests/SpotBugs skipped because output is generated.

## State and persistence behavior

The POM persists no runtime state. It controls generated source directories, module membership, dependency resolution, native build outputs under `target`, and test/runtime packaging artifacts.

## Dependencies and integration points

It integrates with the parent Ozone Maven reactor, generated protobuf sources, SpotBugs exclude files, rocksdbjni, CMake/JNI tooling for native builds where enabled, and downstream modules that consume the produced jars or test jars.

## Risks and edge cases

Server protocols rely on client common types. Dependency or generation-order errors show up as missing generated classes in SCM/server modules.

## Test signals

Useful signals are a module-level Maven compile, protobuf generation for interface modules, native-profile build on supported Linux agents for rocks-native, and downstream module tests that import generated classes or managed RocksDB wrappers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/InterSCMProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/InterSCMProtocol.proto

## Purpose

Defines inter-SCM checkpoint transfer messages used by a follower SCM to copy a leader's DB checkpoint.

## Important APIs, types, and functions

Package: `default`. Imports: none. Important declarations include `CopyDBCheckpointRequestProto, CopyDBCheckpointResponseProto, InterSCMProtocolService`. RPC methods: download(CopyDBCheckpointRequestProto -> stream CopyDBCheckpointResponseProto).

## Control flow

The CopyDBCheckpoint RPC accepts a request and returns a response with checkpoint location/status data; actual filesystem transfer and persistence occur in the server implementation.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

Checkpoint copy must coordinate with leadership, snapshot consistency, and secure peer authentication. The proto does not encode those guarantees.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/InterSCMProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/SCMRatisProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/SCMRatisProtocol.proto

## Purpose

Defines the Ratis replication request/response envelope used for SCM HA state-machine commands.

## Important APIs, types, and functions

Package: `default`. Imports: none. Important declarations include `Method, MethodArgument, ListArgument, SCMRatisRequestProto, SCMRatisResponseProto, RequestType`. RPC methods: none.

## Control flow

SCM serializes state-changing commands into SCMRatisRequestProto and receives SCMRatisResponseProto after the replicated state machine applies them.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

All persisted SCM HA mutations depend on deterministic serialization and replay. Adding fields requires careful default handling so old log entries still apply.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/SCMRatisProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/SCMUpdateProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/SCMUpdateProtocol.proto

## Purpose

Defines a streaming update service where clients subscribe to SCM update channels, receive update events, and unsubscribe when no longer interested.

## Important APIs, types, and functions

Package: `hadoop.hdds.scm`. Imports: none. Important declarations include `CRLInfoProto, ClientId, SubscribeRequest, SubscribeResponse, UpdateRequest, UpdateResponse, CRLUpdateRequest, CRLUpdateResponse, UnsubscribeRequest, UnsubscribeResponse, Type, SCMUpdateService`. RPC methods: subscribe(SubscribeRequest -> SubscribeResponse), updateStatus(stream UpdateRequest -> stream UpdateResponse), unsubscribe(UnsubscribeRequest -> UnsubscribeResponse).

## Control flow

The service exposes subscribe, updateStatus, and unsubscribe style messages. It is a transport contract for server-pushed SCM state rather than persistent state itself.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

Streaming protocols need backpressure, subscriber cleanup, and versioned payload handling. Missing unsubscribe or failed status handling can leak server-side subscriber state.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/SCMUpdateProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmSecretKeyProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmSecretKeyProtocol.proto

## Purpose

Defines SCM secret-key management RPCs for current key retrieval, specific key lookup, key listing, and check-and-rotate operations.

## Important APIs, types, and functions

Package: `hadoop.hdds.security.symmetric`. Imports: `hdds.proto`. Important declarations include `SCMSecretKeyRequest, SCMSecretKeyResponse, ManagedSecretKey, SCMGetSecretKeyRequest, SCMGetCheckAndRotateRequest, SCMGetCurrentSecretKeyResponse, SCMGetSecretKeyResponse, SCMSecretKeysListResponse, SCMGetCheckAndRotateResponse, Type, Status, SCMSecretKeyProtocolService`. RPC methods: submitRequest(SCMSecretKeyRequest -> SCMSecretKeyResponse).

## Control flow

Requests use SCMSecretKeyRequest with a Type enum and response envelope with Status. ManagedSecretKey embeds SecretKeyProto from hdds.proto for durable key metadata.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

Secret-key material is security-sensitive. Rotation races, stale current-key reads, and over-broad list access are server-side risks that need integration tests.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmSecretKeyProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmServerDatanodeHeartbeatProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmServerDatanodeHeartbeatProtocol.proto

## Purpose

Defines SCM's datanode heartbeat protocol, including heartbeat request/response envelopes, node/container/pipeline/incremental reports, commands sent from SCM to datanodes, and command status feedback.

## Important APIs, types, and functions

Package: `hadoop.hdds`. Imports: `hdds.proto`. Important declarations include `SCMDatanodeRequest, SCMDatanodeResponse, LayoutVersionProto, SCMVersionRequestProto, SCMVersionResponseProto, SCMRegisterRequestProto, SCMRegisteredResponseProto, SCMHeartbeatRequestProto, CommandQueueReportProto, SCMHeartbeatResponseProto, SCMNodeAddressList, NodeReportProto, StorageReportProto, MetadataStorageReportProto, ContainerReportsProto, IncrementalContainerReportProto, ContainerReplicaProto, CommandStatusReportsProto, CommandStatus, ContainerActionsProto, ContainerAction, PipelineReport, PipelineReportsProto, PipelineActionsProto, ClosePipelineInfo, PipelineAction, SCMCommandProto, ReregisterCommandProto, ...`. RPC methods: submitRequest(SCMDatanodeRequest -> SCMDatanodeResponse).

## Control flow

Datanodes send SCMHeartbeatRequestProto with reports and command status; SCM replies with SCMHeartbeatResponseProto containing commands such as reregister, delete blocks, close containers, replicate, delete container, finalize upgrade, refresh volume usage, and other operational directives.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

This is a high-volume operational protocol. Risks include oversized reports, command-id correlation bugs, stale layout/version information, replayed command status, and compatibility of new command payloads with older datanodes.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmServerDatanodeHeartbeatProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmServerProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmServerProtocol.proto

## Purpose

Defines the client-facing SCM server protocol for SCM info, block allocation/deletion, container queries, pipeline operations, safe mode, replication manager status, and related storage-control requests.

## Important APIs, types, and functions

Package: `hadoop.hdds.block`. Imports: `hdds.proto`. Important declarations include `SCMBlockLocationRequest, SCMBlockLocationResponse, UserInfo, AllocateScmBlockRequestProto, DeleteScmKeyBlocksRequestProto, KeyBlocks, DeleteScmKeyBlocksResponseProto, DeleteKeyBlocksResultProto, DeleteScmBlockResult, AllocateBlockResponse, AllocateScmBlockResponseProto, SortDatanodesRequestProto, SortDatanodesResponseProto, GetClusterTreeRequestProto, GetClusterTreeResponseProto, Type, Status, Result, ScmBlockLocationProtocolService`. RPC methods: send(SCMBlockLocationRequest -> SCMBlockLocationResponse).

## Control flow

A request envelope selects the command type and carries the matching request. The server returns a response envelope with status and matching payload, backed by SCM managers that persist container, block, pipeline, and node metadata.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

Envelope-field mismatches, optional field absence, and enum compatibility are the main protocol risks. Block/container operations also depend on SCM state machines and must avoid issuing stale pipeline or container information.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmServerProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmServerSecurityProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmServerSecurityProtocol.proto

## Purpose

Defines the SCM security service for certificate signing, certificate retrieval, CRL lookup, datanode/OM certificate renewal, and token or secret related security material exchange.

## Important APIs, types, and functions

Package: `hadoop.hdds.security`. Imports: `hdds.proto`. Important declarations include `SCMSecurityRequest, SCMSecurityResponse, SCMGetDataNodeCertRequestProto, SCMGetOMCertRequestProto, SCMGetCertRequestProto, SCMGetSCMCertRequestProto, SCMGetCertificateRequestProto, SCMGetCACertificateRequestProto, SCMListCertificateRequestProto, SCMGetCertResponseProto, SCMListCertificateResponseProto, SCMGetAllRootCaCertificatesResponseProto, SCMRemoveExpiredCertificatesResponseProto, SCMGetRootCACertificateRequestProto, SCMListCACertificateRequestProto, SCMGetCrlsRequestProto, SCMGetCrlsResponseProto, SCMGetLatestCrlIdRequestProto, SCMGetLatestCrlIdResponseProto, SCMRevokeCertificatesRequestProto, SCMGetAllRootCaCertificatesRequestProto, SCMRevokeCertificatesResponseProto, SCMRemoveExpiredCertificatesRequestProto, Type, Status, ResponseCode, ResponseCode, Reason, ...`. RPC methods: submitRequest(SCMSecurityRequest -> SCMSecurityResponse).

## Control flow

Requests are wrapped in SCMGetCertRequestProto or service-specific request messages and served through a protobuf RPC service. Responses carry PEM/certificate material, CRL IDs and lists, and status/error information.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

Security risk is high: CSR validation, identity binding, serial/CRL monotonicity, and authorization are enforced outside the proto but are required for safe use. Wire compatibility must preserve certificate and CRL fields exactly.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmServerSecurityProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/dev-support/findbugsExcludeFile.xml

## Purpose

This SpotBugs/FindBugs exclude filter suppresses findings for generated protobuf packages in `managed-rocksdb`. The matched packages are .

## Important APIs, types, and functions

The file uses `<FindBugsFilter>` with `<Match><Package name="..."/></Match>` entries. It has no executable functions; its API is the XML contract consumed by the SpotBugs Maven plugin.

## Control flow

During Maven analysis, the module's SpotBugs plugin reads this filter and skips matching generated classes. That prevents generated protobuf code from dominating static-analysis output.

## State and persistence behavior

The file persists build configuration only. It does not affect runtime behavior or generated class contents.

## Dependencies and integration points

It is referenced by the module POM through `spotbugs-maven-plugin` `excludeFilterFile` configuration. The package names must match the Java packages emitted by protobuf generation.

## Risks and edge cases

The main risk is over-broad suppression: if hand-written classes are later placed under a suppressed generated package, SpotBugs will ignore them. A stale package name also creates noisy generated-code reports.

## Test signals

Run module SpotBugs or Maven verification and confirm generated protobuf packages are suppressed while hand-written package findings remain visible.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/pom.xml

## Purpose

Builds the hdds-managed-rocksdb jar, a Java wrapper layer around rocksdbjni that adds close tracking, metrics, and safer lifecycle helpers for RocksDB native resources.

## Important APIs, types, and functions

Artifact: `hdds`. Modules: none in this POM. Key dependencies include `com.google.guava:guava`, `commons-io:commons-io`, `jakarta.annotation:jakarta.annotation-api`, `org.apache.hadoop:hadoop-common`, `org.apache.ozone:hdds-common`, `org.apache.ratis:ratis-common`, `org.rocksdb:rocksdbjni`, `org.slf4j:slf4j-api`, `org.apache.commons:commons-lang3`. Key plugins include `org.apache.maven.plugins:maven-compiler-plugin`, `org.apache.maven.plugins:maven-jar-plugin`.

## Control flow

The module compiles Java wrappers and a test jar. It depends on rocksdbjni, hdds-common, Ratis common utilities, Hadoop common, and test-only commons-lang3.

## State and persistence behavior

The POM persists no runtime state. It controls generated source directories, module membership, dependency resolution, native build outputs under `target`, and test/runtime packaging artifacts.

## Dependencies and integration points

It integrates with the parent Ozone Maven reactor, generated protobuf sources, SpotBugs exclude files, rocksdbjni, CMake/JNI tooling for native builds where enabled, and downstream modules that consume the produced jars or test jars.

## Risks and edge cases

Native-resource wrappers need tests on platforms where rocksdbjni loads correctly. Dependency upgrades can change RocksDB ownership semantics and invalidate close-tracking assumptions.

## Test signals

Useful signals are a module-level Maven compile, protobuf generation for interface modules, native-profile build on supported Linux agents for rocks-native, and downstream module tests that import generated classes or managed RocksDB wrappers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/RocksDatabaseException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/RocksDatabaseException.java

## Purpose

Wraps RocksDBException as an IOException-facing database exception and prefixes messages with the RocksDB status code when the cause is a RocksDBException.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db`. Main type: `RocksDatabaseException`. Notable methods: `getStatus`, `getMessage`. Key imports include `java.io.IOException`, `org.rocksdb.RocksDBException`.

## Control flow

Constructors call a private formatter that extracts `getStatus().getCodeString()` or `NULL_STATUS`, then delegate to IOException.

## State and persistence behavior

No mutable state beyond inherited exception message/cause.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Only Exception causes are accepted by the formatted constructor, not arbitrary Throwable. Null status is handled, but callers must preserve the original cause for diagnostics.

## Test signals

Test with RocksDBException containing real and null statuses, ordinary Exception causes, empty messages, and default constructor serialization/logging behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/RocksDatabaseException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/JniLibNamePropertyWriter.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/JniLibNamePropertyWriter.java

## Purpose

Small build-time utility that writes the platform-specific RocksDB JNI library name into a properties file for the native rocks-tools Maven profile.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `JniLibNamePropertyWriter`. Notable methods: `main`. Key imports include `java.io.IOException`, `java.io.OutputStreamWriter`, `java.io.Writer`, `java.nio.charset.StandardCharsets`, `java.nio.file.Files`, `java.nio.file.Paths`.

## Control flow

`main` takes the output path from `args[0]`, asks ManagedRocksObjectUtils for the RocksDB JNI file name, and writes `rocksdbLibName=...` as UTF-8.

## State and persistence behavior

Writes one build artifact file; no runtime persistence.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

No argument validation is present, and IO failures are printed rather than propagated, so Maven must detect missing/invalid property files.

## Test signals

Invoke with a temporary path and assert the property is written; test missing args and unwritable paths if build failure semantics matter.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/JniLibNamePropertyWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedBlockBasedTableConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedBlockBasedTableConfig.java

## Purpose

Managed BlockBasedTableConfig that owns child filter/cache resources and prevents overwriting an unclosed block cache.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedBlockBasedTableConfig`. Notable methods: `closeAndSetBlockCache`, `setBlockCache`, `isClosed`, `close`. Key imports include `java.util.concurrent.atomic.AtomicBoolean`, `org.rocksdb.BlockBasedTableConfig`, `org.rocksdb.Cache`.

## Control flow

`setBlockCache` rejects replacing an owning unclosed cache. `closeAndSetBlockCache` closes the previous cache first. `close` closes filter policy and block cache once.

## State and persistence behavior

Tracks blockCacheHolder and an AtomicBoolean closed flag.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

The class only tracks the cache assigned through this object. External owners can still close or reuse the cache unexpectedly.

## Test signals

Verify close closes filter/cache, overwriting without close throws, closeAndSetBlockCache succeeds, and double close is harmless.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedBlockBasedTableConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedBloomFilter.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedBloomFilter.java

## Purpose

Managed wrapper around RocksDB `BloomFilter` that adds close-time leak tracking to a native RocksDB resource.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedBloomFilter`. Notable methods: `close`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.BloomFilter`.

## Control flow

The class constructs or inherits the RocksDB object, registers a leak tracker at construction, and overrides close or wrapping methods so the native resource closes before the tracker is released.

## State and persistence behavior

Owns a RocksDB native handle and a leak-tracker token. It has no durable state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Safety depends on try-with-resources by callers and on RocksDB ownership semantics remaining stable across rocksdbjni upgrades.

## Test signals

Use try-with-resources in representative RocksDB operations and assert ManagedRocksObjectMetrics reports no leaks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedBloomFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedCheckpoint.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedCheckpoint.java

## Purpose

Managed wrapper around RocksDB `Checkpoint` that adds close-time leak tracking to a native RocksDB resource.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedCheckpoint`. Notable methods: `create`. Key imports include `org.rocksdb.Checkpoint`.

## Control flow

The class constructs or inherits the RocksDB object, registers a leak tracker at construction, and overrides close or wrapping methods so the native resource closes before the tracker is released.

## State and persistence behavior

Owns a RocksDB native handle and a leak-tracker token. It has no durable state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Safety depends on try-with-resources by callers and on RocksDB ownership semantics remaining stable across rocksdbjni upgrades.

## Test signals

Use try-with-resources in representative RocksDB operations and assert ManagedRocksObjectMetrics reports no leaks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedCheckpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedColumnFamilyOptions.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedColumnFamilyOptions.java

## Purpose

Managed ColumnFamilyOptions with leak tracking and deep-close support for managed table-format configs.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedColumnFamilyOptions`. Notable methods: `setTableFormatConfig`, `closeAndSetTableFormatConfig`, `setReused`, `isReused`, `close`, `closeDeeply`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.BlockBasedTableConfig`, `org.rocksdb.ColumnFamilyOptions`, `org.rocksdb.TableFormatConfig`.

## Control flow

`setTableFormatConfig` rejects overwriting an unclosed ManagedBlockBasedTableConfig and unsupported non-block configs. `closeAndSetTableFormatConfig` closes the previous managed config. `closeDeeply` closes child table config then options.

## State and persistence behavior

Tracks a reused flag and native options handle.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

The reused flag is advisory; callers must honor it. Table configs loaded from ini may be plain BlockBasedTableConfig and are treated specially.

## Test signals

Cover overwrite rejection, closeAndSet behavior, closeDeeply, copied options, and reused flag call sites.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedColumnFamilyOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedCompactRangeOptions.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedCompactRangeOptions.java

## Purpose

Managed wrapper around RocksDB `CompactRangeOptions` that adds close-time leak tracking to a native RocksDB resource.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedCompactRangeOptions`. Notable methods: `close`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.CompactRangeOptions`.

## Control flow

The class constructs or inherits the RocksDB object, registers a leak tracker at construction, and overrides close or wrapping methods so the native resource closes before the tracker is released.

## State and persistence behavior

Owns a RocksDB native handle and a leak-tracker token. It has no durable state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Safety depends on try-with-resources by callers and on RocksDB ownership semantics remaining stable across rocksdbjni upgrades.

## Test signals

Use try-with-resources in representative RocksDB operations and assert ManagedRocksObjectMetrics reports no leaks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedCompactRangeOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedConfigOptions.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedConfigOptions.java

## Purpose

Managed wrapper around RocksDB `ConfigOptions` that adds close-time leak tracking to a native RocksDB resource.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedConfigOptions`. Notable methods: `close`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.ConfigOptions`.

## Control flow

The class constructs or inherits the RocksDB object, registers a leak tracker at construction, and overrides close or wrapping methods so the native resource closes before the tracker is released.

## State and persistence behavior

Owns a RocksDB native handle and a leak-tracker token. It has no durable state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Safety depends on try-with-resources by callers and on RocksDB ownership semantics remaining stable across rocksdbjni upgrades.

## Test signals

Use try-with-resources in representative RocksDB operations and assert ManagedRocksObjectMetrics reports no leaks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedConfigOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedDBOptions.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedDBOptions.java

## Purpose

Managed DBOptions that tracks and closes a RocksDB Logger assigned through setLogger.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedDBOptions`. Notable methods: `setLogger`, `close`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.LOG`, `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `java.util.concurrent.atomic.AtomicReference`, `org.apache.hadoop.hdds.utils.IOUtils`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.DBOptions`, `org.rocksdb.Logger`.

## Control flow

`setLogger` atomically swaps the logger and closes the previous one. `close` closes the current logger, then DBOptions, then leak tracker.

## State and persistence behavior

Holds an AtomicReference to the current Logger.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Only loggers set through this override are tracked. External logger sharing can cause premature close.

## Test signals

Set multiple loggers, assert previous/current close behavior, and verify leak metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedDBOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedDirectSlice.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedDirectSlice.java

## Purpose

Defines `is` in package `org.apache.hadoop.hdds.utils.db.managed`.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `is`. Notable methods: `getNativeHandle`, `disposeInternal`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `java.nio.ByteBuffer`, `java.util.Objects`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.DirectSlice`.

## Control flow

Control flow is limited to the methods listed below.

## State and persistence behavior

State follows the fields declared in the class.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Review call sites for lifecycle and concurrency assumptions.

## Test signals

Compile and targeted unit tests should cover normal and exceptional paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedDirectSlice.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedEnvOptions.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedEnvOptions.java

## Purpose

Managed wrapper around RocksDB `EnvOptions` that adds close-time leak tracking to a native RocksDB resource.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedEnvOptions`. Notable methods: `close`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.EnvOptions`.

## Control flow

The class constructs or inherits the RocksDB object, registers a leak tracker at construction, and overrides close or wrapping methods so the native resource closes before the tracker is released.

## State and persistence behavior

Owns a RocksDB native handle and a leak-tracker token. It has no durable state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Safety depends on try-with-resources by callers and on RocksDB ownership semantics remaining stable across rocksdbjni upgrades.

## Test signals

Use try-with-resources in representative RocksDB operations and assert ManagedRocksObjectMetrics reports no leaks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedEnvOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedFlushOptions.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedFlushOptions.java

## Purpose

Managed wrapper around RocksDB `FlushOptions` that adds close-time leak tracking to a native RocksDB resource.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedFlushOptions`. Notable methods: `close`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.FlushOptions`.

## Control flow

The class constructs or inherits the RocksDB object, registers a leak tracker at construction, and overrides close or wrapping methods so the native resource closes before the tracker is released.

## State and persistence behavior

Owns a RocksDB native handle and a leak-tracker token. It has no durable state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Safety depends on try-with-resources by callers and on RocksDB ownership semantics remaining stable across rocksdbjni upgrades.

## Test signals

Use try-with-resources in representative RocksDB operations and assert ManagedRocksObjectMetrics reports no leaks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedFlushOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedIngestExternalFileOptions.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedIngestExternalFileOptions.java

## Purpose

Managed wrapper around RocksDB `IngestExternalFileOptions` that adds close-time leak tracking to a native RocksDB resource.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedIngestExternalFileOptions`. Notable methods: `close`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.IngestExternalFileOptions`.

## Control flow

The class constructs or inherits the RocksDB object, registers a leak tracker at construction, and overrides close or wrapping methods so the native resource closes before the tracker is released.

## State and persistence behavior

Owns a RocksDB native handle and a leak-tracker token. It has no durable state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Safety depends on try-with-resources by callers and on RocksDB ownership semantics remaining stable across rocksdbjni upgrades.

## Test signals

Use try-with-resources in representative RocksDB operations and assert ManagedRocksObjectMetrics reports no leaks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedIngestExternalFileOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedLRUCache.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedLRUCache.java

## Purpose

Managed wrapper around RocksDB `LRUCache` that adds close-time leak tracking to a native RocksDB resource.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedLRUCache`. Notable methods: `close`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.LRUCache`.

## Control flow

The class constructs or inherits the RocksDB object, registers a leak tracker at construction, and overrides close or wrapping methods so the native resource closes before the tracker is released.

## State and persistence behavior

Owns a RocksDB native handle and a leak-tracker token. It has no durable state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Safety depends on try-with-resources by callers and on RocksDB ownership semantics remaining stable across rocksdbjni upgrades.

## Test signals

Use try-with-resources in representative RocksDB operations and assert ManagedRocksObjectMetrics reports no leaks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedLRUCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedLogger.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedLogger.java

## Purpose

Managed wrapper around RocksDB `Logger` that adds close-time leak tracking to a native RocksDB resource.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedLogger`. Notable methods: `log`, `close`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `java.util.function.BiConsumer`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.InfoLogLevel`, `org.rocksdb.Logger`.

## Control flow

The class constructs or inherits the RocksDB object, registers a leak tracker at construction, and overrides close or wrapping methods so the native resource closes before the tracker is released.

## State and persistence behavior

Owns a RocksDB native handle and a leak-tracker token. It has no durable state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Safety depends on try-with-resources by callers and on RocksDB ownership semantics remaining stable across rocksdbjni upgrades.

## Test signals

Use try-with-resources in representative RocksDB operations and assert ManagedRocksObjectMetrics reports no leaks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedObject.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedObject.java

## Purpose

Package-private generic AutoCloseable wrapper for RocksDB AbstractNativeReference instances with leak tracking.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedObject`. Notable methods: `get`, `close`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.AbstractNativeReference`.

## Control flow

Construction stores the original object and registers with ManagedRocksObjectUtils.track. `get` exposes the underlying object. `close` closes the original in a try block and always closes the leak tracker.

## State and persistence behavior

Holds the native reference and its leak-tracker handle. It does not guard double-close beyond the wrapped RocksDB object's behavior.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Callers can still use `get()` after close, and duplicate close semantics depend on RocksDB classes. Every subclass must ensure close is called.

## Test signals

Use fake/real native references to verify original close, leak tracker closure, and no leak metrics after try-with-resources.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedObject.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedOptions.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedOptions.java

## Purpose

Managed wrapper around RocksDB `Options` that adds close-time leak tracking to a native RocksDB resource.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedOptions`. Notable methods: `close`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.Options`.

## Control flow

The class constructs or inherits the RocksDB object, registers a leak tracker at construction, and overrides close or wrapping methods so the native resource closes before the tracker is released.

## State and persistence behavior

Owns a RocksDB native handle and a leak-tracker token. It has no durable state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Safety depends on try-with-resources by callers and on RocksDB ownership semantics remaining stable across rocksdbjni upgrades.

## Test signals

Use try-with-resources in representative RocksDB operations and assert ManagedRocksObjectMetrics reports no leaks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedReadOptions.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedReadOptions.java

## Purpose

Managed wrapper around RocksDB `ReadOptions` that adds close-time leak tracking to a native RocksDB resource.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedReadOptions`. Notable methods: `close`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.ReadOptions`.

## Control flow

The class constructs or inherits the RocksDB object, registers a leak tracker at construction, and overrides close or wrapping methods so the native resource closes before the tracker is released.

## State and persistence behavior

Owns a RocksDB native handle and a leak-tracker token. It has no durable state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Safety depends on try-with-resources by callers and on RocksDB ownership semantics remaining stable across rocksdbjni upgrades.

## Test signals

Use try-with-resources in representative RocksDB operations and assert ManagedRocksObjectMetrics reports no leaks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedReadOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksDB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksDB.java

## Purpose

Managed wrapper around RocksDB with factory methods for open/openReadOnly/openWithLatestOptions, synchronized live-file deletion, and live SST metadata lookup.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedRocksDB`. Notable methods: `openReadOnly`, `openReadOnly`, `openReadOnly`, `open`, `openWithLatestOptions`, `deleteFile`, `getLiveMetadataForSSTFiles`, `getLiveMetadataForSSTFiles`. Key imports include `java.io.File`, `java.time.Duration`, `java.util.List`, `java.util.Map`, `java.util.stream.Collectors`, `org.apache.commons.io.FilenameUtils`, `org.apache.hadoop.hdds.utils.db.RocksDatabaseException`, `org.rocksdb.ColumnFamilyDescriptor`, `org.rocksdb.ColumnFamilyHandle`, `org.rocksdb.DBOptions`.

## Control flow

Static open methods delegate to RocksDB APIs and wrap the result. `openWithLatestOptions` first loads persisted options into supplied DB/CF descriptors. `deleteFile` calls RocksDB.deleteFile and waits up to 60 seconds for the file to disappear.

## State and persistence behavior

Owns a RocksDB native handle through ManagedObject. Column family handles passed to open methods remain caller-owned.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Callers must close DB and all column-family handles. `deleteFile` relies on filesystem deletion timing and can block; live-file maps key by basename, which can collide if paths differ.

## Test signals

Open temp DBs with multiple column families, verify latest-options loading, delete live files under compaction-safe conditions, and assert close/leak metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksDB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksIterator.java

## Purpose

Managed RocksIterator wrapper that can also hold an acquired database reference for the iterator lifetime.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedRocksIterator`. Notable methods: `close`, `managed`, `managed`. Key imports include `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.RocksIterator`.

## Control flow

Constructors store an optional dbRef. `close` closes the iterator through ManagedObject, then closes dbRef so database shutdown can proceed.

## State and persistence behavior

Owns iterator native handle and optionally a database reference token.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Forgetting to close the iterator can keep DB references alive. Passing null dbRef is allowed for older call sites but offers no shutdown-race protection.

## Test signals

Verify iterator use in try-with-resources, dbRef release on close, and wait-and-close behavior with open iterators.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksObjectMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksObjectMetrics.java

## Purpose

Registers Hadoop metrics counters for total managed RocksDB objects and leaked managed objects.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedRocksObjectMetrics`. Notable methods: `assertNoLeaks`, `create`. Key imports include `com.google.common.annotations.VisibleForTesting`, `org.apache.hadoop.hdds.annotation.InterfaceAudience`, `org.apache.hadoop.metrics2.annotation.Metric`, `org.apache.hadoop.metrics2.annotation.Metrics`, `org.apache.hadoop.metrics2.lib.DefaultMetricsSystem`, `org.apache.hadoop.metrics2.lib.MutableCounterLong`, `org.apache.hadoop.ozone.OzoneConsts`.

## Control flow

A singleton registers with DefaultMetricsSystem. ManagedRocksObjectUtils increments counters and tests can call assertNoLeaks.

## State and persistence behavior

Maintains mutable metrics counters in the process-wide metrics system.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Global singleton state can leak between tests; counter-only metrics cannot identify which object leaked without log stack traces.

## Test signals

Assert counter increments for tracked objects and leak reporting, with metrics-system isolation in repeated test runs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksObjectMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksObjectUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksObjectUtils.java

## Purpose

Central utility for RocksDB wrapper leak tracking, leak reporting, RocksDB native library loading, RocksDB JNI library-name lookup, and polling for file deletion.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedRocksObjectUtils`. Notable methods: `waitForFileDelete`, `loadRocksDBLibrary`, `getRocksDBLibFileName`. Key imports include `jakarta.annotation.Nullable`, `java.io.File`, `java.time.Duration`, `org.apache.hadoop.hdds.HddsUtils`, `org.apache.hadoop.hdds.ratis.RatisHelper`, `org.apache.hadoop.hdds.utils.LeakDetector`, `org.apache.hadoop.hdds.utils.db.RocksDatabaseException`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.RocksDB`, `org.rocksdb.util.Environment`.

## Control flow

`track` registers a closeable with LeakDetector and captures a shortened stack trace. `waitForFileDelete` polls through RatisHelper until a path disappears. `loadRocksDBLibrary` delegates to RocksDB.loadLibrary.

## State and persistence behavior

Holds a static LeakDetector and uses process-wide metrics. It does not persist runtime state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Stack capture depends on logging configuration. File deletion polling can make tests slow or flaky on busy filesystems.

## Test signals

Exercise tracking/reportLeak counters, file-delete timeout and success paths, and RocksDB library-name resolution on supported platforms.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksObjectUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedSlice.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedSlice.java

## Purpose

Managed Slice wrapper that tracks RocksDB native slice resources; ManagedDirectSlice builds a DirectSlice over the remaining region of a ByteBuffer slice.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedSlice`. Notable methods: `getNativeHandle`, `disposeInternal`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.Slice`.

## Control flow

Constructors pass byte data or a sliced ByteBuffer to RocksDB. Because RocksMutableObject.close is final, disposeInternal is decorated to close the leak tracker after native disposal.

## State and persistence behavior

Owns native slice memory/reference and exposes synchronized getNativeHandle for JNI consumers.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

ByteBuffer position/limit semantics are critical for ManagedDirectSlice. Using non-direct or mutated buffers can cause unexpected slice contents.

## Test signals

The included ManagedDirectSlice test compares direct slices across sizes and offsets; add tests for empty, non-direct, and lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedSlice.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedSstFileReader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedSstFileReader.java

## Purpose

Managed wrapper around RocksDB `SstFileReader` that adds close-time leak tracking to a native RocksDB resource.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedSstFileReader`. Notable methods: `close`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.Options`, `org.rocksdb.SstFileReader`.

## Control flow

The class constructs or inherits the RocksDB object, registers a leak tracker at construction, and overrides close or wrapping methods so the native resource closes before the tracker is released.

## State and persistence behavior

Owns a RocksDB native handle and a leak-tracker token. It has no durable state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Safety depends on try-with-resources by callers and on RocksDB ownership semantics remaining stable across rocksdbjni upgrades.

## Test signals

Use try-with-resources in representative RocksDB operations and assert ManagedRocksObjectMetrics reports no leaks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedSstFileReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedSstFileReaderIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedSstFileReaderIterator.java

## Purpose

Managed wrapper around RocksDB `SstFileReaderIterator` that adds close-time leak tracking to a native RocksDB resource.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedSstFileReaderIterator`. Notable methods: `managed`. Key imports include `org.rocksdb.SstFileReaderIterator`.

## Control flow

The class constructs or inherits the RocksDB object, registers a leak tracker at construction, and overrides close or wrapping methods so the native resource closes before the tracker is released.

## State and persistence behavior

Owns a RocksDB native handle and a leak-tracker token. It has no durable state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Safety depends on try-with-resources by callers and on RocksDB ownership semantics remaining stable across rocksdbjni upgrades.

## Test signals

Use try-with-resources in representative RocksDB operations and assert ManagedRocksObjectMetrics reports no leaks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedSstFileReaderIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedSstFileWriter.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedSstFileWriter.java

## Purpose

Managed wrapper around RocksDB `SstFileWriter` that adds close-time leak tracking to a native RocksDB resource.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedSstFileWriter`. Notable methods: `close`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.EnvOptions`, `org.rocksdb.Options`, `org.rocksdb.SstFileWriter`.

## Control flow

The class constructs or inherits the RocksDB object, registers a leak tracker at construction, and overrides close or wrapping methods so the native resource closes before the tracker is released.

## State and persistence behavior

Owns a RocksDB native handle and a leak-tracker token. It has no durable state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Safety depends on try-with-resources by callers and on RocksDB ownership semantics remaining stable across rocksdbjni upgrades.

## Test signals

Use try-with-resources in representative RocksDB operations and assert ManagedRocksObjectMetrics reports no leaks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedSstFileWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedStatistics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedStatistics.java

## Purpose

Managed wrapper around RocksDB `Statistics` that adds close-time leak tracking to a native RocksDB resource.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedStatistics`. Notable methods: `close`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.Statistics`.

## Control flow

The class constructs or inherits the RocksDB object, registers a leak tracker at construction, and overrides close or wrapping methods so the native resource closes before the tracker is released.

## State and persistence behavior

Owns a RocksDB native handle and a leak-tracker token. It has no durable state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Safety depends on try-with-resources by callers and on RocksDB ownership semantics remaining stable across rocksdbjni upgrades.

## Test signals

Use try-with-resources in representative RocksDB operations and assert ManagedRocksObjectMetrics reports no leaks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedTransactionLogIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedTransactionLogIterator.java

## Purpose

Managed wrapper around RocksDB `TransactionLogIterator` that adds close-time leak tracking to a native RocksDB resource.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedTransactionLogIterator`. Notable methods: `managed`. Key imports include `org.rocksdb.TransactionLogIterator`.

## Control flow

The class constructs or inherits the RocksDB object, registers a leak tracker at construction, and overrides close or wrapping methods so the native resource closes before the tracker is released.

## State and persistence behavior

Owns a RocksDB native handle and a leak-tracker token. It has no durable state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Safety depends on try-with-resources by callers and on RocksDB ownership semantics remaining stable across rocksdbjni upgrades.

## Test signals

Use try-with-resources in representative RocksDB operations and assert ManagedRocksObjectMetrics reports no leaks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedTransactionLogIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedWriteBatch.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedWriteBatch.java

## Purpose

Managed wrapper around RocksDB `WriteBatch` that adds close-time leak tracking to a native RocksDB resource.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedWriteBatch`. Notable methods: `close`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.WriteBatch`.

## Control flow

The class constructs or inherits the RocksDB object, registers a leak tracker at construction, and overrides close or wrapping methods so the native resource closes before the tracker is released.

## State and persistence behavior

Owns a RocksDB native handle and a leak-tracker token. It has no durable state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Safety depends on try-with-resources by callers and on RocksDB ownership semantics remaining stable across rocksdbjni upgrades.

## Test signals

Use try-with-resources in representative RocksDB operations and assert ManagedRocksObjectMetrics reports no leaks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedWriteBatch.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedWriteOptions.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedWriteOptions.java

## Purpose

Managed wrapper around RocksDB `WriteOptions` that adds close-time leak tracking to a native RocksDB resource.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedWriteOptions`. Notable methods: `close`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.WriteOptions`.

## Control flow

The class constructs or inherits the RocksDB object, registers a leak tracker at construction, and overrides close or wrapping methods so the native resource closes before the tracker is released.

## State and persistence behavior

Owns a RocksDB native handle and a leak-tracker token. It has no durable state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Safety depends on try-with-resources by callers and on RocksDB ownership semantics remaining stable across rocksdbjni upgrades.

## Test signals

Use try-with-resources in representative RocksDB operations and assert ManagedRocksObjectMetrics reports no leaks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedWriteOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/package-info.java

## Purpose

Documents the managed RocksDB wrapper package and its rule that RocksDB native resources should be wrapped and closed through managed classes to avoid leaks.

## Important APIs, types, and functions

Package declaration: `contains RocksObject decorators and utilities to catch track RocksObject's
 * lifecycle to ensure they're properly closed before being GCed.
 */
package org.apache.hadoop.hdds.utils.db.managed`. This file provides package-level documentation and has no executable methods.

## Control flow

No runtime control flow exists. Javadoc/package metadata is consumed by documentation and compiler tooling.

## State and persistence behavior

No state is stored or persisted.

## Dependencies and integration points

The package groups related Java classes for HDDS RocksDB wrappers or native JNI support and affects generated Javadoc/package annotations.

## Risks and edge cases

The risk is documentation drift: package-level guidance must stay aligned with actual resource ownership rules in the wrapper classes.

## Test signals

Compile/Javadoc generation and consistency with nearby wrapper tests are sufficient signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/package-info.java

## Purpose

Declares the base HDDS RocksDB utility package for managed RocksDB exception and wrapper support.

## Important APIs, types, and functions

Package declaration: `org.apache.hadoop.hdds.utils.db`. This file provides package-level documentation and has no executable methods.

## Control flow

No runtime control flow exists. Javadoc/package metadata is consumed by documentation and compiler tooling.

## State and persistence behavior

No state is stored or persisted.

## Dependencies and integration points

The package groups related Java classes for HDDS RocksDB wrappers or native JNI support and affects generated Javadoc/package annotations.

## Risks and edge cases

The risk is documentation drift: package-level guidance must stay aligned with actual resource ownership rules in the wrapper classes.

## Test signals

Compile/Javadoc generation and consistency with nearby wrapper tests are sufficient signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/test/java/org/apache/hadoop/hdds/utils/db/managed/TestManagedDirectSlice.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/test/java/org/apache/hadoop/hdds/utils/db/managed/TestManagedDirectSlice.java

## Purpose

JUnit test suite for ManagedDirectSlice ByteBuffer slicing semantics.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `TestManagedDirectSlice`. Notable methods: `testManagedDirectSlice`. Key imports include `static org.junit.jupiter.api.Assertions.assertEquals`, `java.nio.ByteBuffer`, `java.util.Random`, `org.apache.hadoop.hdds.utils.db.CodecBuffer`, `org.junit.jupiter.api.Test`.

## Control flow

Loads RocksDB native library once, then tests many sizes and buffer positions by comparing ManagedDirectSlice against a ManagedSlice built from the expected bytes.

## State and persistence behavior

Uses static Random and count for generated cases and logging. It creates only temporary direct buffers/native slices inside try-with-resources.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Randomized sizes improve coverage but make exact failing cases less reproducible unless the printed count/size/position is captured.

## Test signals

This file is itself the test signal for direct slice offset, size, equality, and close behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/test/java/org/apache/hadoop/hdds/utils/db/managed/TestManagedDirectSlice.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/test/java/org/apache/hadoop/hdds/utils/db/managed/TrackingUtilManagedWriteBatchForTesting.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/test/java/org/apache/hadoop/hdds/utils/db/managed/TrackingUtilManagedWriteBatchForTesting.java

## Purpose

Defines `extends` in package `org.apache.hadoop.hdds.utils.db.managed`.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `extends`. Notable methods: `equals`, `hashCode`, `toString`, `getOperations`, `convert`, `delete`, `delete`, `delete`, `delete`, `deleteRange`, `deleteRange`, `merge`, `merge`, `put`, `put`, `put`, `put`, `close`. Key imports include `static org.apache.hadoop.hdds.StringUtils.bytes2String`, `java.nio.ByteBuffer`, `java.util.ArrayList`, `java.util.Arrays`, `java.util.HashMap`, `java.util.List`, `java.util.Map`, `org.rocksdb.ColumnFamilyHandle`, `org.rocksdb.RocksDBException`.

## Control flow

Control flow is limited to the methods listed below.

## State and persistence behavior

State follows the fields declared in the class.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Review call sites for lifecycle and concurrency assumptions.

## Test signals

Compile and targeted unit tests should cover normal and exceptional paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/test/java/org/apache/hadoop/hdds/utils/db/managed/TrackingUtilManagedWriteBatchForTesting.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/pom.xml

## Purpose

Aggregator POM for the HDDS subproject. It lists all HDDS modules, creates a test jar, configures remote ASF resources, and defines a parallel-tests profile that controls surefire fork directories and shared test paths.

## Important APIs, types, and functions

Artifact: `ozone-main`. Modules: `annotations`, `cli-common`, `client`, `common`, `config`, `container-service`, `crypto-api`, `crypto-default`, `docs`, `erasurecode`, `framework`, `hadoop-dependency-client`, `interface-admin`, `interface-client`, `interface-server`, `managed-rocksdb`, `rocks-native`, `rocksdb-checkpoint-differ`, `server-scm`, `test-utils`. Key dependencies include `org.apache.ozone:ozone-dev-support`. Key plugins include `org.apache.maven.plugins:maven-jar-plugin`, `org.apache.maven.plugins:maven-remote-resources-plugin`, `org.apache.hadoop:hadoop-maven-plugins`, `org.apache.maven.plugins:maven-surefire-plugin`.

## Control flow

Maven enters this POM from the parent ozone-main build, then builds the listed modules in dependency order. Profiles add test fork isolation and shared coordination directories for concurrent JUnit execution.

## State and persistence behavior

The POM persists no runtime state. It controls generated source directories, module membership, dependency resolution, native build outputs under `target`, and test/runtime packaging artifacts.

## Dependencies and integration points

It integrates with the parent Ozone Maven reactor, generated protobuf sources, SpotBugs exclude files, rocksdbjni, CMake/JNI tooling for native builds where enabled, and downstream modules that consume the produced jars or test jars.

## Risks and edge cases

Module ordering and profile properties affect the whole HDDS reactor. Changes can break downstream module builds, test isolation, or source-release resource processing.

## Test signals

Useful signals are a module-level Maven compile, protobuf generation for interface modules, native-profile build on supported Linux agents for rocks-native, and downstream module tests that import generated classes or managed RocksDB wrappers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/dev-support/findbugsExcludeFile.xml

## Purpose

This SpotBugs/FindBugs exclude filter suppresses findings for generated protobuf packages in `rocks-native`. The matched packages are .

## Important APIs, types, and functions

The file uses `<FindBugsFilter>` with `<Match><Package name="..."/></Match>` entries. It has no executable functions; its API is the XML contract consumed by the SpotBugs Maven plugin.

## Control flow

During Maven analysis, the module's SpotBugs plugin reads this filter and skips matching generated classes. That prevents generated protobuf code from dominating static-analysis output.

## State and persistence behavior

The file persists build configuration only. It does not affect runtime behavior or generated class contents.

## Dependencies and integration points

It is referenced by the module POM through `spotbugs-maven-plugin` `excludeFilterFile` configuration. The package names must match the Java packages emitted by protobuf generation.

## Risks and edge cases

The main risk is over-broad suppression: if hand-written classes are later placed under a suppressed generated package, SpotBugs will ignore them. A stale package name also creates noisy generated-code reports.

## Test signals

Run module SpotBugs or Maven verification and confirm generated protobuf packages are suppressed while hand-written package findings remain visible.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/pom.xml

## Purpose

Builds the hdds-rocks-native module, which provides JNI wrappers and optional native build support for RocksDB raw SST tooling.

## Important APIs, types, and functions

Artifact: `hdds`. Modules: none in this POM. Key dependencies include `com.google.guava:guava`, `commons-io:commons-io`, `org.apache.commons:commons-lang3`, `org.apache.ozone:hdds-common`, `org.apache.ozone:hdds-managed-rocksdb`, `org.rocksdb:rocksdbjni`, `org.slf4j:slf4j-api`, `org.apache.ozone:hdds-test-utils`. Key plugins include `com.github.spotbugs:spotbugs-maven-plugin`, `org.apache.maven.plugins:maven-compiler-plugin`, `org.codehaus.mojo:build-helper-maven-plugin`, `org.codehaus.mojo:exec-maven-plugin`, `org.codehaus.mojo:properties-maven-plugin`, `org.apache.maven.plugins:maven-dependency-plugin`, `com.googlecode.maven-download-plugin:download-maven-plugin`, `org.apache.maven.plugins:maven-patch-plugin`, `org.apache.maven.plugins:maven-antrun-plugin`, `org.apache.maven.plugins:maven-compiler-plugin`.

## Control flow

The normal build compiles Java. The rocks_tools_native profile writes the RocksDB JNI library name, unpacks/downloads RocksDB artifacts, applies a patch, generates JNI headers, runs CMake, links ozone_rocksdb_tools, and packages native resources.

## State and persistence behavior

The POM persists no runtime state. It controls generated source directories, module membership, dependency resolution, native build outputs under `target`, and test/runtime packaging artifacts.

## Dependencies and integration points

It integrates with the parent Ozone Maven reactor, generated protobuf sources, SpotBugs exclude files, rocksdbjni, CMake/JNI tooling for native builds where enabled, and downstream modules that consume the produced jars or test jars.

## Risks and edge cases

The native profile is platform and toolchain sensitive. CMake variables, RocksDB version, ABI flags, JNI headers, and bundled dependent libraries must stay aligned with rocksdbjni.

## Test signals

Useful signals are a module-level Maven compile, protobuf generation for interface modules, native-profile build on supported Linux agents for rocks-native, and downstream module tests that import generated classes or managed RocksDB wrappers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/CMakeLists.txt -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/CMakeLists.txt

## Purpose

Configures the CMake build for the `ozone_rocksdb_tools` shared JNI library used by Ozone's raw SST reader support.

## Important APIs, types, and functions

Important build commands include `find_package(JNI REQUIRED)`, `include_directories(${JNI_INCLUDE_DIRS})`, optional inclusion of RocksDB headers and `rocks_tools`, `add_library(ozone_rocksdb_tools SHARED ...)`, and `target_link_libraries` against RocksDB and rocks_tools.

## Control flow

CMake requires `GENERATED_JAVAH`, includes generated JNI headers, optionally configures SST dump sources when `SST_DUMP_INCLUDE` is set, imports the static `librocksdb_tools.a`, builds a shared library, and sets rpath/link flags.

## State and persistence behavior

Build state is contained in CMake/Maven target directories. The output shared library becomes a runtime resource loaded by NativeLibraryLoader.

## Dependencies and integration points

Depends on JNI headers, generated javah/javac headers, RocksDB headers and libraries, the RocksDB tools static library, and Maven properties passed by the rocks-native profile.

## Risks and edge cases

The `_GLIBCXX_USE_CXX11_ABI=0` flag, C++ standard, RocksDB version, and linked static library must match rocksdbjni. Missing `GENERATED_JAVAH` fails the configure step by design.

## Test signals

Run the rocks_tools_native Maven profile on a Linux builder, inspect the packaged shared object, and execute ManagedRawSSTFileReader integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/NativeConstants.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/NativeConstants.java

## Purpose

Central constants for the rocks-native library name and system property key used by native RocksDB tooling.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils`. Main type: `NativeConstants`. Notable methods: constructor/overrides only. Key imports include none.

## Control flow

No control flow; consumers import constants.

## State and persistence behavior

No mutable state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Changing the constant breaks resource names, Maven native packaging, and NativeLibraryLoader lookup.

## Test signals

Compile-time usage and NativeLibraryLoader tests pin the values indirectly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/NativeConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/NativeLibraryLoader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/NativeLibraryLoader.java

## Purpose

Loads Ozone native libraries from the system library path or from jar resources copied to a temporary directory, tracking loaded status per library name.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils`. Main type: `NativeLibraryLoader`. Notable methods: `initNewInstance`, `getInstance`, `getJniLibraryFileName`, `getJniLibraryFileName`, `isMac`, `isWindows`, `isLinux`, `appendLibOsSuffix`, `isLibraryLoaded`, `isLibraryLoaded`, `loadLibrary`, `copyResourceFromJarToTemp`. Key imports include `static org.apache.hadoop.hdds.utils.NativeConstants.ROCKS_TOOLS_NATIVE_LIBRARY_NAME`, `com.google.common.annotations.VisibleForTesting`, `java.io.File`, `java.io.IOException`, `java.io.InputStream`, `java.nio.file.Files`, `java.nio.file.Path`, `java.nio.file.StandardCopyOption`, `java.util.ArrayList`, `java.util.List`.

## Control flow

`loadLibrary` first tries System.loadLibrary. If that fails, it copies the OS-suffixed library and dependent files from classpath resources to a temp directory, calls System.load, schedules temp cleanup with ShutdownHookManager, records success/failure, and returns loaded state.

## State and persistence behavior

Maintains a singleton ConcurrentHashMap of library-name to loaded boolean and creates temporary native-library directories.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

A failed first load is cached as false but future calls still retry. Dependent resource streams are not null-checked before copy. OS detection is simple prefix matching, and temp cleanup depends on shutdown hooks.

## Test signals

The included tests mock resources and properties; also test unsupported OS suffixes, missing dependent files, repeated load calls, and custom native.lib.tmp.dir.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/NativeLibraryLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/NativeLibraryNotLoadedException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/NativeLibraryNotLoadedException.java

## Purpose

Checked exception indicating that a named native library could not be loaded.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils`. Main type: `NativeLibraryNotLoadedException`. Notable methods: constructor/overrides only. Key imports include none.

## Control flow

Constructor formats a message from the library name.

## State and persistence behavior

Inherited exception message only.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Callers must not swallow this when native functionality is required; tryLoadLibrary intentionally converts it to false.

## Test signals

Assert message content and propagation from ManagedRawSSTFileReader.loadLibrary.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/NativeLibraryNotLoadedException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/db/ManagedRawSSTFileIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/db/ManagedRawSSTFileIterator.java

## Purpose

Closable Java iterator over native RocksDB RawIterator records, transforming raw key/sequence/type/value tuples into caller-defined objects.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db`. Main type: `ManagedRawSSTFileIterator`. Notable methods: `hasNext`, `next`, `getKey`, `getValue`, `getSequenceNumber`, `getType`, `hasNext`, `next`, `closeInternal`, `close`, `getKey`, `getSequence`, `getType`, `getValue`, `toString`. Key imports include `com.google.common.primitives.UnsignedLong`, `java.nio.ByteBuffer`, `java.util.NoSuchElementException`, `java.util.function.Function`, `org.apache.hadoop.ozone.util.ClosableIterator`.

## Control flow

`next` checks native hasNext, pulls key/value into dynamically sized CodecBuffers according to IteratorType, reads unsigned sequence and type, advances the native iterator, and applies the transformer.

## State and persistence behavior

Owns a native iterator pointer, key/value buffers, transformer, IteratorType, and closed flag.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

hasNext does not check `closed`, so using after close can touch freed native memory. Buffer sizing depends on native copy methods returning full source lengths. Transformer owns returned CodecBuffers and must release if required.

## Test signals

Native integration tests should cover keys/values larger than initial buffers, key-only/value-only iterator types, close behavior, and NoSuchElementException.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/db/ManagedRawSSTFileIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/db/ManagedRawSSTFileReader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/db/ManagedRawSSTFileReader.java

## Purpose

Java JNI facade for RocksDB RawSstFileReader, allowing Ozone to iterate raw SST entries including tombstones through the native ozone_rocksdb_tools library.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db`. Main type: `ManagedRawSSTFileReader`. Notable methods: `tryLoadLibrary`, `loadLibrary`, `newIterator`, `newRawSSTFileReader`, `newIterator`, `disposeInternal`, `close`. Key imports include `static org.apache.hadoop.hdds.utils.NativeConstants.ROCKS_TOOLS_NATIVE_LIBRARY_NAME`, `java.io.Closeable`, `java.util.Arrays`, `java.util.function.Function`, `org.apache.hadoop.hdds.utils.NativeLibraryLoader`, `org.apache.hadoop.hdds.utils.NativeLibraryNotLoadedException`, `org.apache.hadoop.hdds.utils.db.managed.ManagedOptions`, `org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils`, `org.apache.hadoop.hdds.utils.db.managed.ManagedSlice`, `org.slf4j.Logger`.

## Control flow

`loadLibrary` loads rocksdbjni and ozone_rocksdb_tools with the RocksDB JNI library as a dependent file. The constructor creates a native reader from ManagedOptions, file path, and read-ahead size. `newIterator` passes optional lower/upper ManagedSlice handles to native code and wraps the native iterator.

## State and persistence behavior

Holds fileName and a native RawSstFileReader pointer. close deletes the native reader.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

The constructor assumes the native library is already loaded. Slice handles must outlive iterator creation. Native handle double-close and missing close can crash or leak.

## Test signals

Use real SST fixtures under the native profile to read full and bounded ranges, verify tombstone visibility, and ensure close is idempotent or guarded by callers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/db/ManagedRawSSTFileReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/db/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/db/package-info.java

## Purpose

Declares the rocks-native DB package containing raw SST reader Java JNI facades.

## Important APIs, types, and functions

Package declaration: `org.apache.hadoop.hdds.utils.db`. This file provides package-level documentation and has no executable methods.

## Control flow

No runtime control flow exists. Javadoc/package metadata is consumed by documentation and compiler tooling.

## State and persistence behavior

No state is stored or persisted.

## Dependencies and integration points

The package groups related Java classes for HDDS RocksDB wrappers or native JNI support and affects generated Javadoc/package annotations.

## Risks and edge cases

The risk is documentation drift: package-level guidance must stay aligned with actual resource ownership rules in the wrapper classes.

## Test signals

Compile/Javadoc generation and consistency with nearby wrapper tests are sufficient signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/db/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/package-info.java

## Purpose

Declares the rocks-native utility package containing native library loading support.

## Important APIs, types, and functions

Package declaration: `contains util classes related to loading native rocksdb library.
 */
package org.apache.hadoop.hdds.utils`. This file provides package-level documentation and has no executable methods.

## Control flow

No runtime control flow exists. Javadoc/package metadata is consumed by documentation and compiler tooling.

## State and persistence behavior

No state is stored or persisted.

## Dependencies and integration points

The package groups related Java classes for HDDS RocksDB wrappers or native JNI support and affects generated Javadoc/package annotations.

## Risks and edge cases

The risk is documentation drift: package-level guidance must stay aligned with actual resource ownership rules in the wrapper classes.

## Test signals

Compile/Javadoc generation and consistency with nearby wrapper tests are sufficient signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/native/ManagedRawSSTFileIterator.cpp -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/native/ManagedRawSSTFileIterator.cpp

## Purpose

JNI implementation for RawIterator operations used by ManagedRawSSTFileIterator: validity, advance, key/value copy, sequence number, record type, and close.

## Important APIs, types, and functions

Exports JNI functions `Java_org_apache_hadoop_hdds_utils_db_ManagedRawSSTFileIterator_hasNext`, `Java_org_apache_hadoop_hdds_utils_db_ManagedRawSSTFileIterator_next`, `Java_org_apache_hadoop_hdds_utils_db_ManagedRawSSTFileIterator_getKey`, `Java_org_apache_hadoop_hdds_utils_db_ManagedRawSSTFileIterator_getValue`, `Java_org_apache_hadoop_hdds_utils_db_ManagedRawSSTFileIterator_getSequenceNumber`, `Java_org_apache_hadoop_hdds_utils_db_ManagedRawSSTFileIterator_getType`, `Java_org_apache_hadoop_hdds_utils_db_ManagedRawSSTFileIterator_closeInternal`. Uses RocksDB raw SST/iterator classes and the pointer conversion helper.

## Control flow

Each JNI method casts the jlong handle to RawIterator. Key/value methods copy RocksDB Slice data into a Java direct ByteBuffer through copyToDirect and return the full source length. closeInternal deletes the iterator.

## State and persistence behavior

Native state consists of heap-allocated RocksDB C++ reader/iterator objects whose addresses are returned to Java as `long` handles. Java close methods must call the matching delete function to release native memory.

## Dependencies and integration points

Depends on generated JNI headers, RocksDB `raw_sst_file_reader.h`, `raw_iterator.h`, `options.h`, and Java classes in `org.apache.hadoop.hdds.utils.db`.

## Risks and edge cases

GetDirectBufferAddress must return non-null and capacity must cover offset plus requested length; otherwise an IllegalArgumentException is thrown. Java use after close can dereference a freed iterator.

## Test signals

Native-profile integration tests should open real SST files, iterate with and without bounds, read large keys/values, verify sequence/type metadata, and stress close/error paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/native/ManagedRawSSTFileIterator.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/native/ManagedRawSSTFileReader.cpp -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/native/ManagedRawSSTFileReader.cpp

## Purpose

JNI implementation for creating/deleting RocksDB RawSstFileReader instances and creating bounded RawIterator instances from optional lower and upper Slice handles.

## Important APIs, types, and functions

Exports JNI functions `Java_org_apache_hadoop_hdds_utils_db_ManagedRawSSTFileReader_newRawSSTFileReader`, `Java_org_apache_hadoop_hdds_utils_db_ManagedRawSSTFileReader_newIterator`, `Java_org_apache_hadoop_hdds_utils_db_ManagedRawSSTFileReader_disposeInternal`. Uses RocksDB raw SST/iterator classes and the pointer conversion helper.

## Control flow

newRawSSTFileReader casts the Java options handle, obtains the UTF-8 file path, constructs RawSstFileReader with read-ahead and checksum options, releases the Java string, and returns the pointer handle. newIterator casts optional slice handles and calls raw_sst_file_reader->newIterator. disposeInternal deletes the reader.

## State and persistence behavior

Native state consists of heap-allocated RocksDB C++ reader/iterator objects whose addresses are returned to Java as `long` handles. Java close methods must call the matching delete function to release native memory.

## Dependencies and integration points

Depends on generated JNI headers, RocksDB `raw_sst_file_reader.h`, `raw_iterator.h`, `options.h`, and Java classes in `org.apache.hadoop.hdds.utils.db`.

## Risks and edge cases

If RawSstFileReader construction throws or env string acquisition fails, the current code has no Java exception translation. It assumes slice handles are valid and owned elsewhere.

## Test signals

Native-profile integration tests should open real SST files, iterate with and without bounds, read large keys/values, verify sequence/type metadata, and stress close/error paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/native/ManagedRawSSTFileReader.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/native/cplusplus_to_java_convert.h -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/native/cplusplus_to_java_convert.h

## Purpose

Provides the `GET_CPLUSPLUS_POINTER` macro used by JNI code to safely convert C++ pointers to Java `jlong` handles on both 32-bit and 64-bit platforms.

## Important APIs, types, and functions

The single API is `GET_CPLUSPLUS_POINTER(_pointer)`, implemented as `static_cast<jlong>(reinterpret_cast<size_t>(_pointer))`.

## Control flow

There is no runtime control flow; JNI C++ code includes the header and uses the macro when returning native pointer handles to Java.

## State and persistence behavior

No state is stored. Java objects persist returned handles as long fields and pass them back to native methods.

## Dependencies and integration points

Included by ManagedRawSSTFileReader.cpp and ManagedRawSSTFileIterator.cpp. It depends on JNI code treating the reverse cast from jlong to pointer consistently.

## Risks and edge cases

Incorrect pointer conversion can make handles negative on 32-bit systems or truncate pointers. The macro addresses the return path, but callers must still avoid using handles after native deletion.

## Test signals

Native tests on 32-bit-compatible and 64-bit platforms, plus handle lifecycle tests that create and close readers/iterators repeatedly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/native/cplusplus_to_java_convert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/test/java/org/apache/hadoop/hdds/utils/TestNativeLibraryLoader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/test/java/org/apache/hadoop/hdds/utils/TestNativeLibraryLoader.java

## Purpose

Defines `for` in package `org.apache.hadoop.hdds.utils`.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils`. Main type: `for`. Notable methods: `nativeLibraryDirectoryLocations`, `testNativeLibraryLoader`, `testDummyLibrary`. Key imports include `static org.apache.hadoop.hdds.utils.NativeConstants.ROCKS_TOOLS_NATIVE_LIBRARY_NAME`, `static org.apache.hadoop.hdds.utils.NativeConstants.ROCKS_TOOLS_NATIVE_PROPERTY`, `static org.apache.hadoop.hdds.utils.NativeLibraryLoader.NATIVE_LIB_TMP_DIR`, `static org.apache.hadoop.hdds.utils.NativeLibraryLoader.getJniLibraryFileName`, `static org.assertj.core.api.Assertions.assertThat`, `static org.junit.jupiter.api.Assertions.assertTrue`, `static org.mockito.Mockito.CALLS_REAL_METHODS`, `static org.mockito.Mockito.anyString`, `static org.mockito.Mockito.mockStatic`, `static org.mockito.Mockito.same`.

## Control flow

Control flow is limited to the methods listed below.

## State and persistence behavior

State follows the fields declared in the class.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Review call sites for lifecycle and concurrency assumptions.

## Test signals

Compile and targeted unit tests should cover normal and exceptional paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/test/java/org/apache/hadoop/hdds/utils/TestNativeLibraryLoader.java -->
