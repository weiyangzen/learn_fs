# subset-b-007984 Research

Grouped research for Apache Ozone HDDS SCM, Recon, container, HA, network-topology, and client support files. Each section preserves its source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/recon/ReconConfigKeys.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/recon/ReconConfigKeys.java

## Purpose
Defines string and primitive constants for Recon service configuration shared by SCM, datanodes, and Recon clients. The class centralizes keys for Recon DB location and permissions, Recon RPC/HTTP/HTTPS addresses, datanode bind host and port, Prometheus endpoint, heatmap provider and enablement, administrator users/groups, and Recon task safemode wait threshold.

## Important APIs, Types, And Functions
`ReconConfigKeys` is a final constants holder with a private constructor. There are no methods beyond construction prevention. Important constants include `RECON_SCM_CONFIG_PREFIX`, `OZONE_RECON_DB_DIR`, `OZONE_RECON_ADDRESS_KEY`, `OZONE_RECON_HTTP_ADDRESS_KEY`, `OZONE_RECON_HTTPS_ADDRESS_KEY`, `OZONE_RECON_DATANODE_ADDRESS_KEY`, `OZONE_RECON_PROMETHEUS_HTTP_ENDPOINT`, and admin ACL keys.

## Control Flow
There is no runtime control flow. Consumers import constants to read or document configuration values through Ozone's configuration framework.

## State And Persistence
The class persists no state. The constants name external configuration persisted in XML/env/config sources and interpreted by Recon, SCM, datanode, and web-service startup code.

## Dependencies And Integration Points
It integrates with `OzoneConfigKeys` for administrator semantics in Javadocs and with any code that binds Recon ports, initializes Recon databases, or gates admin-only Recon APIs.

## Risks And Test Signals
Risk is compatibility drift: renaming values or defaults changes deployed config behavior. Test signals are configuration-key lookup tests, web/RPC bind tests, Recon DB permission tests, and admin ACL coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/recon/ReconConfigKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/recon/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/recon/package-info.java

## Purpose
Declares the `org.apache.hadoop.hdds.recon` package and documents that it contains Recon-related classes.

## Important APIs, Types, And Functions
There are no Java APIs in this file; it is package-level documentation only.

## Control Flow
No executable control flow exists.

## State And Persistence
No state is held or persisted.

## Dependencies And Integration Points
The package comment is consumed by Javadoc and source readers. It groups Recon configuration and shared Recon support types under the HDDS common module.

## Risks And Test Signals
Risk is limited to documentation drift. Compile/Javadoc generation is the relevant signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/recon/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/AddSCMRequest.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/AddSCMRequest.java

## Purpose
Models an HA bootstrap request for adding an SCM node to an existing SCM Ratis ring. It carries the cluster ID, SCM ID, and Ratis address of the joining SCM.

## Important APIs, Types, And Functions
`AddSCMRequest` exposes constructor/getters, `getProtobuf()`, static `getFromProtobuf(HddsProtos.AddScmRequestProto)`, and nested `Builder` with setters for cluster ID, SCM ID, and Ratis address.

## Control Flow
Callers either build the object directly, through `Builder`, or from protobuf. `getProtobuf()` serializes all three fields into `AddScmRequestProto` for SCM-to-SCM RPC.

## State And Persistence
The instance is immutable after construction. Persistent behavior is limited to protobuf transport and any later storage done by the HA bootstrap path.

## Dependencies And Integration Points
Depends on `HddsProtos.AddScmRequestProto` and integrates with SCM HA bootstrap APIs and Ratis membership management.

## Risks And Test Signals
There is no validation for null/empty IDs or malformed addresses, so upstream validation must be covered. Tests should verify protobuf round trips and rejection behavior in the receiving SCM service.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/AddSCMRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ByteStringConversion.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ByteStringConversion.java

## Purpose
Provides a configurable conversion strategy from `ByteBuffer` to Ratis-shaded protobuf `ByteString`, selecting safe copying or unsafe wrapping based on Ozone configuration.

## Important APIs, Types, And Functions
`createByteBufferConversion(boolean unsafeEnabled)` returns either `UnsafeByteOperations::unsafeWrap` or `ByteStringConversion::safeWrap`. `safeWrap(ByteBuffer)` copies bytes with `ByteString.copyFrom(buffer)`, then flips the buffer.

## Control Flow
Callers create a reusable `Function<ByteBuffer, ByteString>` at configuration time, then apply it when constructing protobuf messages.

## State And Persistence
The class is stateless. It affects memory ownership: safe mode copies data, while unsafe mode shares the buffer with the resulting `ByteString`.

## Dependencies And Integration Points
References `OzoneConfigKeys.OZONE_UNSAFEBYTEOPERATIONS_ENABLED`, Ratis-shaded `ByteString`, and `UnsafeByteOperations`. It is relevant to container and pipeline RPC serialization paths.

## Risks And Test Signals
Unsafe wrapping can expose mutable-buffer corruption if callers reuse buffers before protobuf consumption. `safeWrap` flips the buffer after copy, which is an unusual side effect. Tests should cover buffer position/limit behavior and corruption resistance with unsafe enabled/disabled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ByteStringConversion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ContainerPlacementStatus.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ContainerPlacementStatus.java

## Purpose
Defines the contract used to report whether a container's replicas satisfy placement policy, independent of under- or over-replication.

## Important APIs, Types, And Functions
The interface declares `isPolicySatisfied()`, `misReplicatedReason()`, `misReplicationCount()`, `expectedPlacementCount()`, and `actualPlacementCount()`.

## Control Flow
Implementations compute rack/node-group or topology placement state. Callers inspect satisfaction first, then use reason/count fields for replication manager decisions and diagnostics.

## State And Persistence
The interface stores no state. Implementations normally derive transient state from replica locations and topology.

## Dependencies And Integration Points
It integrates with SCM placement policies and replication-manager health checks that mark containers as mis-replicated.

## Risks And Test Signals
The interface does not define nullability or exact semantics for count when placement and replication both fail. Tests should cover placement-satisfied, mis-replicated, and under-replicated-but-placement-valid cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ContainerPlacementStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/DatanodeAdminError.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/DatanodeAdminError.java

## Purpose
Small DTO for returning datanode administration failures as a hostname plus error message.

## Important APIs, Types, And Functions
`DatanodeAdminError(String host, String error)` stores two strings. `getHostname()` and `getError()` expose them.

## Control Flow
No logic exists beyond construction and access.

## State And Persistence
Instances are mutable internally but have no setters. They are transient result objects for admin commands or APIs.

## Dependencies And Integration Points
Used by SCM datanode admin/decommission/maintenance command surfaces to report per-node failures.

## Risks And Test Signals
Risk is minimal; lack of null validation means callers may emit incomplete API responses. Tests should verify command/API serialization of failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/DatanodeAdminError.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/PipelineRequestInformation.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/PipelineRequestInformation.java

## Purpose
Carries request metadata used by pipeline selection, currently just requested size.

## Important APIs, Types, And Functions
`PipelineRequestInformation` is final with `getSize()`. Nested `Builder` has `getBuilder()`, `setSize(long)`, and `build()`.

## Control Flow
Callers build a value and pass it to pipeline-selection logic that may consider requested allocation size.

## State And Persistence
The value is immutable and transient. No serialization is defined in this class.

## Dependencies And Integration Points
Integrates with SCM pipeline choose policies and block/container allocation paths.

## Risks And Test Signals
There is no validation for negative size. Tests should cover policy behavior for zero, positive, and invalid sizes at the consuming layer.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/PipelineRequestInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/RemoveSCMRequest.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/RemoveSCMRequest.java

## Purpose
Models an HA request to remove an SCM from the SCM Ratis membership ring. It carries cluster ID, SCM ID, and the SCM Ratis address to remove.

## Important APIs, Types, And Functions
`RemoveSCMRequest` has constructor/getters and `getProtobuf()` producing `HddsProtos.RemoveScmRequestProto`.

## Control Flow
Callers construct a request and serialize it for RPC. Unlike `AddSCMRequest`, this file has no `getFromProtobuf` helper.

## State And Persistence
The object is immutable. Persistence is external to the HA removal service or Ratis membership log.

## Dependencies And Integration Points
Depends on `HddsProtos.RemoveScmRequestProto` and integrates with SCM HA administrative membership changes.

## Risks And Test Signals
Missing validation and missing parse helper can lead to asymmetry in call sites. Tests should cover protobuf creation and receiver-side validation for IDs/address and cluster mismatch.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/RemoveSCMRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ScmConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ScmConfig.java

## Purpose
Defines annotated configuration fields for the SCM service that are loaded through HDDS's typed configuration framework. It covers Kerberos identity, unknown-container handling, Ratis and EC pipeline choose policy classes, block deletion rate/interval, and deletion transaction map limit.

## Important APIs, Types, And Functions
`ScmConfig` extends `ReconfigurableConfig` and is annotated with `@ConfigGroup(prefix = "hdds.scm")`. `@Config` fields include `principal`, `keytab`, `action`, `pipelineChoosePolicyName`, `ecPipelineChoosePolicyName`, `blockDeletionLimit`, `blockDeletionInterval`, and `transactionToDNsCommitMapLimit`. Getters/setters expose each value. Nested `ConfigStrings` preserves legacy Kerberos key constants for `KerberosInfo`.

## Control Flow
The configuration framework instantiates and populates this class from keys/defaults, then runtime services read getters or update reconfigurable values such as block deletion limit.

## State And Persistence
Instances hold in-memory configuration. Values originate from persisted configuration files or dynamic reconfiguration state; this class itself does not write persistence.

## Dependencies And Integration Points
Depends on `org.apache.hadoop.hdds.conf` annotations and integrates with SCM security login, pipeline policy factory loading, block deleting service scheduling, and dynamic configuration.

## Risks And Test Signals
Class-name values are free-form strings and fail later at policy instantiation. Unknown-container action is also unvalidated here. Tests should cover config default binding, dynamic reconfiguration, invalid policy class handling, and block deletion interval/limit behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ScmConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ScmConfigKeys.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ScmConfigKeys.java

## Purpose
Centralizes SCM and container-service configuration key constants and defaults. It spans SCM HA, Ratis, container layout/chunking, RPC/HTTP addresses, datanode directories, heartbeat and node liveness, pipeline placement/limits, block deletion, network topology, balancer/admin monitors, event queues, audit logging, and SCM HA Ratis tuning.

## Important APIs, Types, And Functions
`ScmConfigKeys` is a public unstable constants holder. Notable groups include `OZONE_SCM_HA_PREFIX`, `OZONE_SCM_DB_DIRS`, Ratis container keys (`HDDS_CONTAINER_RATIS_*`), SCM service ports and bind hosts, liveness intervals, `OZONE_SCM_NAMES`, HA service/node ID keys, pipeline placement and timeout keys, topology schema keys, Ratis HA keys, and `HDDS_SCM_HTTP_AUTH_TYPE`.

## Control Flow
There is no executable logic beyond a private constructor. Runtime services import constants when reading configuration.

## State And Persistence
No state is stored here. The string constants define externally persisted Ozone configuration names and default values.

## Dependencies And Integration Points
Depends on HDDS audience/stability annotations and Ratis `TimeDuration`. It is widely integrated by SCM, datanode, clients, HA bootstrap, Ratis server setup, topology loading, admin services, and tests.

## Risks And Test Signals
Changing constants or defaults is a compatibility risk for deployed clusters. Some defaults are intentionally high or workaround-driven, such as Ratis log purge gap. Tests should cover config key resolution, address/port fallback, HA suffix handling, and upgrade compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ScmConfigKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ScmInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ScmInfo.java

## Purpose
DTO returned by SCM info calls, containing cluster ID, SCM ID, and HA peer role/address strings.

## Important APIs, Types, And Functions
`ScmInfo` is final with getters for `clusterId`, `scmId`, and unmodifiable `peerRoles`. Nested `Builder` accumulates fields and copies peer roles with `setPeerRoles(List<String>)`.

## Control Flow
Callers build `ScmInfo` from SCM runtime metadata and expose it via client/admin APIs.

## State And Persistence
Instances are immutable after construction except the builder's list before build. The constructor wraps the passed list, so later builder mutation can affect the instance if the same list object is reused internally.

## Dependencies And Integration Points
Integrates with SCM client/admin service responses and HA role reporting.

## Risks And Test Signals
The constructor uses `Collections.unmodifiableList(peerRoles)` without copying; builder mutation after build could leak. Tests should verify immutability expectations and peer role output for single-node and HA clusters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ScmInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ScmRatisServerConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ScmRatisServerConfig.java

## Purpose
Defines typed config for one SCM HA Ratis server option: minimum wait time between appendEntries calls.

## Important APIs, Types, And Functions
`ScmRatisServerConfig` is annotated with `@ConfigGroup(prefix = ScmConfigKeys.OZONE_SCM_HA_PREFIX + "." + RaftServerConfigKeys.PREFIX)`. It has `logAppenderWaitTimeMin`, `getLogAppenderWaitTimeMin()`, and setter.

## Control Flow
The configuration framework binds the time value from `ozone.scm.ha.raft.server.log.appender.wait-time.min`.

## State And Persistence
The object stores in-memory config derived from external configuration; no direct persistence.

## Dependencies And Integration Points
Depends on HDDS config annotations and Ratis `RaftServerConfigKeys`. Integrated by SCM Ratis server initialization/performance tuning.

## Risks And Test Signals
Risk is unit mismatch because the field is a `long` configured as `ConfigType.TIME`. Tests should verify default conversion and that the value is applied to Ratis properties.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ScmRatisServerConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/StreamingReadResponse.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/StreamingReadResponse.java

## Purpose
Holds the datanode and gRPC request observer for a streaming read connection and gives it a compact diagnostic name.

## Important APIs, Types, And Functions
Constructor accepts `DatanodeDetails` and `ClientCallStreamObserver<ContainerCommandRequestProto>`. Getters expose both. `toString()` returns a name derived from the datanode UUID suffix.

## Control Flow
Streaming read setup creates this value and passes it to a `StreamingReaderSpi`; callers use the observer to send read requests over the established stream.

## State And Persistence
The object is immutable and transient. It represents an active client-side gRPC stream and does not persist data.

## Dependencies And Integration Points
Depends on datanode details, datanode container protobufs, and Ratis-shaded gRPC. Integrated by `XceiverClientSpi` streaming read hooks.

## Risks And Test Signals
`toString()` assumes the UUID string contains `-`; normal UUIDs do, but tests should cover name generation and observer wiring for stream setup/teardown.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/StreamingReadResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/StreamingReaderSpi.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/StreamingReaderSpi.java

## Purpose
SPI for streaming read response consumers. It extends gRPC `StreamObserver` for container command responses and adds a hook to receive the `StreamingReadResponse` request-side handle.

## Important APIs, Types, And Functions
The interface inherits `onNext`, `onError`, and `onCompleted` for `ContainerCommandResponseProto`, and declares `setStreamingReadResponse(StreamingReadResponse)`.

## Control Flow
An `XceiverClientSpi` implementation initializes streaming read, obtains a request observer, wraps it in `StreamingReadResponse`, and injects it into the reader before response callbacks arrive.

## State And Persistence
The interface stores no state. Implementations typically maintain transient stream state and buffers.

## Dependencies And Integration Points
Depends on Ratis-shaded gRPC and datanode container protobufs. Integrated by container client streaming reads.

## Risks And Test Signals
Ordering of `setStreamingReadResponse` versus `onNext` matters for implementations. Tests should cover unsupported clients, setup ordering, response callback handling, and stream completion/error paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/StreamingReaderSpi.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientReply.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientReply.java

## Purpose
Represents the asynchronous result of an Xceiver client command, including the response future, Ratis log index, and datanodes that produced replies or failures.

## Important APIs, Types, And Functions
`getResponse()`/`setResponse()` manage a `CompletableFuture<ContainerCommandResponseProto>`. `getLogIndex()`/`setLogIndex()` track commit/log index. `addDatanode()` records datanodes and `getDatanodes()` returns an unmodifiable view.

## Control Flow
Client implementations create a reply when sending commands asynchronously. Synchronous `XceiverClientSpi.sendCommand` waits on the response future and validators can inspect the resulting response.

## State And Persistence
All state is in-memory and mutable. The datanode list is not synchronized, so it is expected to be populated in a controlled async path.

## Dependencies And Integration Points
Depends on datanode details and container response protobufs. Integrated by Ratis/standalone Xceiver clients and commit-watch logic.

## Risks And Test Signals
Concurrent mutation can race with readers, and `setResponse` can replace futures after construction. Tests should cover async completion, failed futures, datanode reporting, and log index propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientReply.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientSpi.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientSpi.java

## Purpose
Abstract base for storage container protocol clients. It manages cache reference counting/eviction and defines synchronous, asynchronous, streaming, commit-watch, and all-node command APIs for concrete clients.

## Important APIs, Types, And Functions
Key methods include `connect`, `close`, `getPipeline`, `sendCommand`, `sendCommandAsync`, `getPipelineType`, `watchForCommit`, `getReplicatedMinCommitIndex`, and `sendCommandOnAllNodes`. Nested `Validator` validates request/response pairs. Package-private `incrementReference`, `decrementReference`, and `setEvicted` drive lifecycle cleanup.

## Control Flow
Managers increment references when lending clients and decrement on release. If a client has been evicted and refcount reaches zero, `cleanup()` calls `close()`. Synchronous `sendCommand` waits for `sendCommandAsync`, re-interrupts on `InterruptedException`, wraps execution errors with debug-formatted request context, and optionally runs validators.

## State And Persistence
The class holds transient `AtomicInteger referenceCount` and eviction flag. It does not persist data; concrete clients communicate with datanodes and Ratis.

## Dependencies And Integration Points
Depends on `HddsUtils`, container protobufs, `BlockID`, `Pipeline`, datanode details, and Ratis checked consumers. Integrated by `XceiverClientManager`, block I/O, replication, and container operations.

## Risks And Test Signals
`isEvicted` is not volatile, so lifecycle access relies on manager discipline. Default streaming methods throw unsupported exceptions. Tests should cover refcount/eviction close timing, interrupt handling, validator failures, all-node fanout, and commit-watch behavior in concrete clients.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientSpi.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/client/ClientTrustManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/client/ClientTrustManager.java

## Purpose
Implements a refreshable client-side `X509ExtendedTrustManager` for gRPC and Ratis clients. It starts from in-memory CA certificates and refreshes from a remote provider when server certificate validation fails, supporting CA rotation for long-lived clients.

## Important APIs, Types, And Functions
Constructor accepts remote and in-memory `CACertificateProvider` instances and requires at least one. `initialize(List<X509Certificate>)` builds a `KeyStore` and delegates to `TrustManagerFactory`. `checkServerTrusted` overloads delegate and retry once after remote reload. `checkClientTrusted` overloads reject server-side use.

## Control Flow
On construction, certs are loaded and a delegate trust manager is selected. During server verification, a certificate failure logs, reloads certificates from the remote provider, reinitializes the delegate, and retries verification.

## State And Persistence
State is an in-memory delegate trust manager and providers. No keystore is written to disk; each reload builds an ephemeral keystore keyed by certificate serial number.

## Dependencies And Integration Points
Depends on Java SSL APIs and HDDS `CACertificateProvider`. Integrated by client factories that connect to SCM/OM/datanode endpoints with TLS and CA rotation.

## Risks And Test Signals
Remote provider security is critical because failed validation triggers trust-root refresh. The delegate field is not synchronized during reload. Tests should cover initial load, null provider combinations, refresh on failure, accepted issuers after reload, and rejection of client-trust methods.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/client/ClientTrustManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/client/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/client/package-info.java

## Purpose
Package documentation for SCM client classes.

## Important APIs, Types, And Functions
No APIs are declared; the package groups SCM client support such as trust-manager behavior.

## Control Flow
No executable flow.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Used by Javadoc/source organization for `org.apache.hadoop.hdds.scm.client`.

## Risks And Test Signals
Only documentation drift; compile/Javadoc generation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/client/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerChecksums.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerChecksums.java

## Purpose
Immutable wrapper for container data and metadata checksums. It gives SCM/client code a typed value for checksum comparison and display, with zero meaning unknown/unset.

## Important APIs, Types, And Functions
Factories are `unknown()`, `of(long dataChecksum)`, and `of(long dataChecksum, long metadataChecksum)`. Getters expose both checksum values. `equals`, `hashCode`, and `toString` support map/set use and hex rendering.

## Control Flow
There is no complex flow; callers create values from reported checksums and compare or render them.

## State And Persistence
Instances are immutable. The singleton `UNKNOWN` avoids repeated zero/zero allocations. Persistence is external if checksums are stored in metadata or reports.

## Dependencies And Integration Points
Depends only on Java `Objects`. Integrated by container replica/report surfaces that need checksum identity.

## Risks And Test Signals
No validation distinguishes an actual zero checksum from unknown. Tests should cover equality, unknown singleton, hex `toString`, and JSON/API serialization where used.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerChecksums.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerException.java

## Purpose
Base exception for ContainerManager failures, specializing `SCMException` with container-oriented result codes.

## Important APIs, Types, And Functions
Constructors accept a message alone for remote-exception unwrapping or a message plus `ResultCodes`.

## Control Flow
Callers throw this or subclasses when container operations fail; RPC layers can unwrap by constructor signature.

## State And Persistence
State is the inherited message/cause and `SCMException.ResultCodes`. No persistence.

## Dependencies And Integration Points
Depends on `SCMException` and integrates with container manager APIs, Hadoop RPC remote exception handling, and client error decoding.

## Risks And Test Signals
The message-only constructor sets a null result, so callers expecting result codes must handle null. Tests should cover subclass result propagation and remote exception unwrap behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerHealthState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerHealthState.java

## Purpose
Enumerates SCM container health states used by `ContainerInfo`, ReplicationManager reporting, and metrics. It includes individual states and observed combined states.

## Important APIs, Types, And Functions
Constants include `HEALTHY`, `UNDER_REPLICATED`, `MIS_REPLICATED`, `OVER_REPLICATED`, `MISSING`, `UNHEALTHY`, `EMPTY`, `OPEN_UNHEALTHY`, `QUASI_CLOSED_STUCK`, `OPEN_WITHOUT_PIPELINE`, and combined states such as `UNHEALTHY_UNDER_REPLICATED`. Each has a short value, description, and metric name. `fromValue(short)` maps serialized values to enum constants.

## Control Flow
Static initialization fills a lookup map. Runtime code increments metrics, sets `ContainerInfo` health, and decodes short values from persisted/serialized forms.

## State And Persistence
Enum values are stable serialization identifiers; unknown values decode to `HEALTHY`. Descriptions and metric names feed reports/metrics.

## Dependencies And Integration Points
Integrated by `ReplicationManagerReport`, `ContainerInfo`, and replication handlers referenced in comments.

## Risks And Test Signals
Defaulting unknown values to `HEALTHY` can hide forward-incompatible states. Tests should cover value uniqueness, metric names, round trips, and behavior for unknown values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerHealthState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerID.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerID.java

## Purpose
Immutable typed wrapper around a numeric container ID. It prevents accidental mixing of container IDs with unrelated longs and provides codecs/protobuf conversion.

## Important APIs, Types, And Functions
`valueOf(long)`, `getBytes(long)`, `getProtobuf()`, `getFromProtobuf`, `getCodec()`, `compareTo`, `equals`, `hashCode`, and `toString` are the key APIs. The class memoizes protobuf and hash values with Ratis `MemoizedSupplier`.

## Control Flow
Factory construction validates non-negative IDs. Consumers serialize through `LongCodec`/`DelegatedCodec` or `HddsProtos.ContainerID`.

## State And Persistence
Instances hold a final `long id`. The codec persists IDs as longs in SCM metadata DBs. `MIN` is `0`.

## Dependencies And Integration Points
Depends on Guava preconditions, HDDS DB codecs, HddsProtos, and JCIP immutability annotation. Used throughout container manager, replication, exclude lists, and reports.

## Risks And Test Signals
The deprecated `getId()` still exposes raw longs for compatibility. Tests should cover negative rejection, codec/protobuf round trip, ordering, memoized hash consistency, and map/set behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerID.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerInfo.java

## Purpose
Primary SCM metadata model for a container. It tracks ID, lifecycle state and transition time, previous state for rollback, pipeline, replication config, size/key counters, owner, delete transaction ID, sequence ID, health state, and suppression flag.

## Important APIs, Types, And Functions
Important APIs include `fromProtobuf`, `getProtobuf`, `getCodec`, state getters/setters, `revertState`, `isOpen`, `isDeleted`, update methods for delete transaction/sequence IDs, JSON-facing getters, and nested `Builder`. The DB codec delegates to `ContainerInfoProto`.

## Control Flow
Builders construct instances from runtime allocation or protobuf. `setState` snapshots previous state and uses the configured clock for state-enter time; `revertState` restores the prior state once. `getProtobuf` serializes replication config as EC or legacy factor and includes optional pipeline/suppressed fields.

## State And Persistence
Container metadata is mutable in memory. `usedBytes` is volatile; other fields require external synchronization. The protobuf codec persists the metadata in SCM DBs. `previousState` is transient and JSON-ignored.

## Dependencies And Integration Points
Depends on Jackson annotations, HDDS replication configs, `PipelineID`, `ContainerID`, DB codecs, and HddsProtos. Integrated by container manager, replication manager, Recon/API JSON, and block deletion.

## Risks And Test Signals
Equality ignores many fields, sequence updates rely on assertions, and health state is not serialized in this protobuf path. Tests should cover protobuf/codec round trips, state transition/revert, EC versus RATIS serialization, suppressed JSON behavior, and concurrent used-byte updates.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerListResult.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerListResult.java

## Purpose
Wrapper for paginated container-list responses, carrying the current page of `ContainerInfo` objects and the total matching count.

## Important APIs, Types, And Functions
Constructor takes `List<ContainerInfo>` and `long totalCount`. Getters expose both fields.

## Control Flow
SCM list APIs create this object after querying container metadata and counting total matches.

## State And Persistence
The wrapper is transient and does not copy the list, so list mutability is inherited from the caller.

## Dependencies And Integration Points
Depends on `ContainerInfo`. Integrated by SCM client/admin APIs and pagination consumers.

## Risks And Test Signals
List aliasing can surprise callers. Tests should cover total-count correctness, empty pages, and response serialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerListResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerNotFoundException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerNotFoundException.java

## Purpose
Specific `ContainerException` indicating that a requested container is absent from ContainerManager.

## Important APIs, Types, And Functions
Constructors support unknown ID, explicit message for remote unwrap, and `ContainerID`-formatted message. `newInstanceForTesting()` provides a fixed test exception.

## Control Flow
Thrown by lookup paths when container metadata is missing. Clients inspect `ResultCodes.CONTAINER_NOT_FOUND`.

## State And Persistence
No persistent state beyond inherited exception fields.

## Dependencies And Integration Points
Depends on `ContainerID` and `ContainerException`. Integrated by SCM RPC error mapping and tests.

## Risks And Test Signals
Default message is generic; tests should assert result code and message formats for lookup failures and remote unwrapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerNotFoundException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerReplicaInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerReplicaInfo.java

## Purpose
Client-facing container replica DTO populated from SCM replica protobufs. It exposes container ID, replica state, datanode, origin datanode, sequence ID, key count, bytes used, replica index, and checksum.

## Important APIs, Types, And Functions
`fromProto(HddsProtos.SCMContainerReplicaProto)` maps protobuf fields into a builder. Getters expose all fields. Nested `Builder` mutates a private subject and returns it from `build()`. `dataChecksum` uses `JsonUtils.ChecksumSerializer`.

## Control Flow
SCM/API code converts replica protobufs to this DTO before JSON or client responses. Optional `replicaIndex` defaults to `-1` when absent.

## State And Persistence
The object is mutable during builder use and then conventionally immutable. It is a transient API view, not the authoritative persisted replica state.

## Dependencies And Integration Points
Depends on datanode details/ID, HddsProtos, Jackson serializer, and HDDS JSON utilities. Integrated by SCM container report/list APIs and Recon/admin clients.

## Risks And Test Signals
The builder returns the same subject object and does not validate required fields. Tests should cover protobuf mapping, absent replica index, checksum JSON formatting, and place-of-birth UUID parsing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerReplicaInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerReplicaNotFoundException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerReplicaNotFoundException.java

## Purpose
Specific `ContainerException` indicating a container replica is missing for a container/datanode pair.

## Important APIs, Types, And Functions
Constructors include no-arg, message-only for remote unwrap, and `ContainerID` plus `DatanodeDetails` for formatted messages. All result-bearing constructors use `CONTAINER_REPLICA_NOT_FOUND`.

## Control Flow
Thrown by replica lookup or mutation paths when expected replica metadata cannot be found.

## State And Persistence
Only inherited exception state is kept.

## Dependencies And Integration Points
Depends on `DatanodeDetails`, `ContainerID`, and `ContainerException`. Integrated by container manager and client error handling.

## Risks And Test Signals
No-arg constructor yields null message components through delegation. Tests should cover result code, formatted message, and remote unwrap constructor behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerReplicaNotFoundException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ReplicationManagerReport.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ReplicationManagerReport.java

## Purpose
Aggregates ReplicationManager run statistics: lifecycle counts, health-state counts, bounded samples of affected container IDs, and completion timestamp.

## Important APIs, Types, And Functions
`increment`, `incrementAndSample`, `getStats`, `getSamples`, `getStat`, `getSample`, `setComplete`, `toProtobuf`, and `fromProtobuf` are key. Stats are keyed by lifecycle-state strings and `ContainerHealthState.name()`, backed by `LongAdder`. Samples are stored in a concurrent map of synchronized lists.

## Control Flow
A manager run creates a report, increments lifecycle and health counters while scanning containers, samples up to `sampleLimit`, then calls `setComplete`. Reports can be serialized to `ReplicationManagerReportProto` and reconstructed, ignoring unknown stat keys.

## State And Persistence
The report is mutable and transient during a scan. Serialized protobufs can be persisted or served through APIs. `containerHealthState` tracks the most recent sampled health state and can be reset.

## Dependencies And Integration Points
Depends on HddsProtos and `ContainerID`/`ContainerInfo`/`ContainerHealthState`. Integrated by ReplicationManager metrics, Recon, and admin diagnostics.

## Risks And Test Signals
`containerHealthState` represents last incremented health state, not aggregate status. Unknown protobuf stats are ignored. Tests should cover concurrent increments, sample limits, serialization round trip, unknown-stat handling, and timestamp completion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ReplicationManagerReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerConfiguration.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerConfiguration.java

## Purpose
Typed configuration model for Container Balancer. It validates and serializes thresholds, iteration limits, datanode/container include-exclude filters, movement byte limits, timeouts, network-topology behavior, DU refresh trigger, and non-standard container inclusion.

## Important APIs, Types, And Functions
Annotated `@Config` fields bind balancer keys. APIs include threshold percentage/ratio getters, setters with validation for threshold, iteration count, and datanode percentage, include/exclude container parsers, include/exclude node parsers, duration getters/setters, `toString`, `toProtobufBuilder`, and static `fromProtobuf`.

## Control Flow
The configuration framework populates defaults from `OzoneConfiguration`. Runtime/admin input can update fields through setters. Protobuf conversion exports active config and applies provided fields over a fresh configuration object.

## State And Persistence
The object holds mutable in-memory config. Persistent sources are Ozone config files and optional protobuf command/API payloads. Include/exclude containers are stored as comma-separated strings and parsed on access.

## Dependencies And Integration Points
Depends on HDDS config annotations, `OzoneConfiguration`, `ContainerID`, `OzoneConsts`, and `ContainerBalancerConfigurationProto`. Integrated by SCM ContainerBalancer scheduling and admin APIs.

## Risks And Test Signals
Container list parsing can throw on blanks or invalid IDs. Size limits lack setter validation. `fromProtobuf` is package-private, limiting external use. Tests should cover validation boundaries, string parsing, protobuf round trip, duration units, and `toString` output for defaults/non-defaults.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/package-info.java

## Purpose
Package documentation for SCM container balancer classes.

## Important APIs, Types, And Functions
No APIs are declared.

## Control Flow
No executable flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Documents the `org.apache.hadoop.hdds.scm.container.balancer` package for Javadoc/source navigation.

## Risks And Test Signals
Only documentation drift; compile/Javadoc generation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/AllocatedBlock.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/AllocatedBlock.java

## Purpose
Return value for SCM block allocation, pairing the selected pipeline with the allocated `ContainerBlockID`.

## Important APIs, Types, And Functions
`AllocatedBlock` exposes `getPipeline`, `getBlockID`, static `newBuilder`, and `toBuilder`. Nested `Builder` sets `Pipeline` and `ContainerBlockID`.

## Control Flow
Block allocation code builds an `AllocatedBlock` after selecting/creating a container and pipeline; callers use the pipeline for writes and block ID for metadata.

## State And Persistence
The object is immutable after construction and transient. Persistence of the block ID occurs in OM/key metadata and container state outside this class.

## Dependencies And Integration Points
Depends on `ContainerBlockID` and `Pipeline`. Integrated by SCM allocate-block APIs and client write paths.

## Risks And Test Signals
Builder does not validate null fields. Tests should cover allocation responses, `toBuilder`, and downstream handling of missing pipeline/block IDs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/AllocatedBlock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/BlockNotCommittedException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/BlockNotCommittedException.java

## Purpose
Storage-container exception for operations on blocks that are not committed.

## Important APIs, Types, And Functions
Constructor accepts a message and passes `ContainerProtos.Result.BLOCK_NOT_COMMITTED` to `StorageContainerException`.

## Control Flow
Thrown by container/block read or metadata paths when a block has not reached committed state.

## State And Persistence
Only inherited exception state is kept.

## Dependencies And Integration Points
Depends on datanode `ContainerProtos` result codes and `StorageContainerException`. Integrated by datanode container protocol error responses.

## Risks And Test Signals
Tests should assert result mapping and client translation for uncommitted block reads.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/BlockNotCommittedException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/ContainerNotOpenException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/ContainerNotOpenException.java

## Purpose
Storage-container exception for operations requiring an open container when the target container is not open.

## Important APIs, Types, And Functions
Constructor maps the message to `ContainerProtos.Result.CONTAINER_NOT_OPEN`.

## Control Flow
Thrown by write/update paths when lifecycle state disallows mutation.

## State And Persistence
Only inherited exception fields.

## Dependencies And Integration Points
Depends on `StorageContainerException` and datanode protobuf result codes. Integrated by container state validation in datanode handlers.

## Risks And Test Signals
Tests should cover write attempts on closed/quasi-closed/deleting containers and verify wire result codes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/ContainerNotOpenException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/ContainerWithPipeline.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/ContainerWithPipeline.java

## Purpose
Combines a `ContainerInfo` and its `Pipeline` for allocation/list responses, with protobuf conversion and ordering by container recency comparator.

## Important APIs, Types, And Functions
`fromProtobuf`, `getProtobuf(int clientVersion)`, getters, `equals`, `hashCode`, `compare`, and `compareTo` are key. Serialization uses `Pipeline.getProtobufMessage(clientVersion, Name.IO_PORTS)`.

## Control Flow
SCM APIs return this when clients need both metadata and connection pipeline. Protobuf conversion reconstructs both parts from HddsProtos.

## State And Persistence
The wrapper is immutable and transient. It serializes for RPC/API transport but does not persist authoritative state.

## Dependencies And Integration Points
Depends on `ContainerInfo`, `Pipeline`, HddsProtos, and datanode port-name selection. Integrated by allocate/list container APIs and client write paths.

## Risks And Test Signals
Comparison delegates to `ContainerInfo.compareTo`, not ID order. Tests should cover protobuf round trip with client versions, equality/hash, and sorted allocation results.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/ContainerWithPipeline.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/ExcludeList.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/ExcludeList.java

## Purpose
Tracks datanodes, container IDs, and pipeline IDs a client wants SCM to avoid during allocation, optionally with automatic datanode expiry.

## Important APIs, Types, And Functions
APIs include `addDatanode(s)`, `addConatinerId` (misspelled but public), `addPipeline`, getters, `getProtoBuf`, `getFromProtoBuf`, `isEmpty`, `clear`, and `getExpiryTime`. Datanodes are held in a concurrent map to expiry timestamps; containers/pipelines are sets.

## Control Flow
Clients add failed or unsuitable targets. `getDatanodes()` prunes expired entries before returning. Protobuf conversion serializes container IDs, datanode UUID strings, and pipeline IDs.

## State And Persistence
State is mutable and transient per allocation/retry flow. Protobuf transport can carry it between client and SCM.

## Dependencies And Integration Points
Depends on `DatanodeDetails`, `ContainerID`, `PipelineID`, and HddsProtos. Integrated by SCM block allocation and retry logic.

## Risks And Test Signals
Container/pipeline sets are not concurrent, and protobuf deserialization reuses a datanode builder. The misspelled method is API surface. Tests should cover expiry pruning, protobuf round trip, empty/clear, and concurrent datanode access.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/ExcludeList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/InvalidContainerStateException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/InvalidContainerStateException.java

## Purpose
Storage-container exception for invalid lifecycle state transitions or operations.

## Important APIs, Types, And Functions
Constructor maps a message to `ContainerProtos.Result.INVALID_CONTAINER_STATE`.

## Control Flow
Thrown when container state validation fails before executing an operation or transition.

## State And Persistence
Only inherited exception state.

## Dependencies And Integration Points
Depends on `StorageContainerException` and datanode protobuf result codes. Integrated by container state machine and protocol handlers.

## Risks And Test Signals
Tests should cover invalid state transitions and verify result-code propagation over container protocol RPC.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/InvalidContainerStateException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/StorageContainerException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/StorageContainerException.java

## Purpose
Base `IOException` subtype for storage-container protocol failures with a datanode `ContainerProtos.Result` code.

## Important APIs, Types, And Functions
Constructors cover result-only, message/result, message/cause/result, and cause/result. `getResult()` exposes the protocol result.

## Control Flow
Datanode handlers throw this or subclasses; RPC layers translate result codes into container command responses.

## State And Persistence
Only exception message/cause and final result code are stored. No persistence.

## Dependencies And Integration Points
Depends on datanode `ContainerProtos.Result`. Integrated by container command handlers, clients, and tests that assert wire errors.

## Risks And Test Signals
The result-only constructor leaves message null. Tests should cover every constructor, result-code preservation, and client-side translation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/StorageContainerException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/package-info.java

## Purpose
Package documentation for storage-container helper classes.

## Important APIs, Types, And Functions
No APIs are declared; helper classes include allocation DTOs, exclude lists, and storage-container exceptions.

## Control Flow
No executable flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Used for Javadoc grouping under `org.apache.hadoop.hdds.scm.container.common.helpers`.

## Risks And Test Signals
Documentation drift only; compile/Javadoc generation is the signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/package-info.java

## Purpose
Package documentation for SCM container metadata classes.

## Important APIs, Types, And Functions
No APIs are declared. The package contains container IDs, metadata, health/report DTOs, and container exceptions.

## Control Flow
No executable flow.

## State And Persistence
No state in this file.

## Dependencies And Integration Points
Javadoc/source organization for `org.apache.hadoop.hdds.scm.container`.

## Risks And Test Signals
Documentation drift only; compile/Javadoc generation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/exceptions/SCMException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/exceptions/SCMException.java

## Purpose
General SCM `IOException` carrying an SCM-specific `ResultCodes` enum for client and RPC error decoding.

## Important APIs, Types, And Functions
Constructors support message-only remote unwrap, result-only, message/result, message/cause/result, and cause/result. `getResult()` returns the code. `ResultCodes` enumerates allocation, pipeline, container, safe mode, leadership, CA rotation, timeout, and unsupported-operation failures.

## Control Flow
SCM services throw this or subclasses; Hadoop RPC can unwrap via required constructors; clients inspect result codes to decide retry or user-facing errors.

## State And Persistence
State is transient exception data. Enum ordinals are compatibility-sensitive, as comments warn not to delete removed revocation codes.

## Dependencies And Integration Points
Integrated by container, pipeline, SCM HA, security, and admin services. Subclasses in this group map specific errors to result codes.

## Risks And Test Signals
Null result from message-only constructor must be handled. Enum ordinal stability is an upgrade risk. Tests should cover remote exception unwrapping, retry classification, and result mapping for subclasses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/exceptions/SCMException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/exceptions/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/exceptions/package-info.java

## Purpose
Package documentation for SCM exception classes.

## Important APIs, Types, And Functions
No APIs are declared.

## Control Flow
No executable control flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Javadoc grouping for `org.apache.hadoop.hdds.scm.exceptions`.

## Risks And Test Signals
Documentation drift only; compile/Javadoc generation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/exceptions/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ha/NonRetriableException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ha/NonRetriableException.java

## Purpose
IOException marker indicating an SCM HA client request should not be retried.

## Important APIs, Types, And Functions
Constructors accept a message for remote unwrap or an `IOException` cause wrapper.

## Control Flow
HA client/proxy code can classify this exception and stop retry loops.

## State And Persistence
Only inherited exception state; no persistence.

## Dependencies And Integration Points
Depends on `IOException`. Integrated by SCM HA retry policies and Hadoop RPC unwrapping.

## Risks And Test Signals
Cause-wrapping constructor uses `super(exception)`, so message is derived from cause. Tests should cover retry policy classification and remote unwrap.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ha/NonRetriableException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ha/RetriableWithFailOverException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ha/RetriableWithFailOverException.java

## Purpose
IOException marker indicating a request can be retried on another SCM server, triggering failover.

## Important APIs, Types, And Functions
Single constructor wraps an `IOException` cause.

## Control Flow
Client retry/failover policy catches this type and moves to the next SCM endpoint.

## State And Persistence
Transient exception state only.

## Dependencies And Integration Points
Integrated by SCM HA client proxies and retry policies.

## Risks And Test Signals
No message-only constructor may limit remote unwrap behavior compared with `NonRetriableException`. Tests should cover failover retry classification and cause preservation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ha/RetriableWithFailOverException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ha/RetriableWithNoFailoverException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ha/RetriableWithNoFailoverException.java

## Purpose
IOException marker indicating a request is retriable, but only against the same SCM server and without failover.

## Important APIs, Types, And Functions
Single constructor wraps an `IOException`.

## Control Flow
Retry policy should repeat the call on the current endpoint rather than rotating to another SCM.

## State And Persistence
Transient exception state only.

## Dependencies And Integration Points
Integrated by SCM HA client retry policy.

## Risks And Test Signals
No explicit delay/backoff is encoded; policy must supply it. Tests should distinguish no-failover retries from failover and non-retriable errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ha/RetriableWithNoFailoverException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMNodeInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMNodeInfo.java

## Purpose
Builds immutable SCM node endpoint information from configuration for clients, OzoneManager, and admin commands. It supports HA service/node-suffixed config and non-HA fallback config.

## Important APIs, Types, And Functions
`buildNodeInfo(ConfigurationSource)` is the main API. `getPort` resolves node-specific address-port deprecations and port keys. `buildAddress` joins host and port. Getters expose service ID, node ID, block client, SCM client, security, and datanode addresses.

## Control Flow
If `HddsUtils.getScmServiceId` returns an HA service, node IDs are required. For each node, the base SCM address is required and endpoint ports are resolved from address keys or suffixed/global port keys. Without HA, dummy service/node IDs are used and hostnames fall back from client address to `ozone.scm.names`.

## State And Persistence
Instances are immutable snapshots of external configuration. No state is written.

## Dependencies And Integration Points
Depends on `ConfigurationSource`, `HddsUtils`, `ConfUtils`, SCM config keys, and Ozone dummy constants. Integrated by SCM clients, OM, admin commands, and HA discovery.

## Risks And Test Signals
`buildAddress` appends ports to the base address even if it already contains a port in HA path, relying on host extraction in config. Non-HA can produce null addresses. Tests should cover HA missing nodes/address, suffixed ports, deprecated address-port parsing, and non-HA fallbacks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMNodeInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ha/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ha/package-info.java

## Purpose
Package documentation for SCM HA support classes.

## Important APIs, Types, And Functions
No APIs are declared. Package includes retry marker exceptions and SCM node-info discovery.

## Control Flow
No executable flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Javadoc grouping for `org.apache.hadoop.hdds.scm.ha`.

## Risks And Test Signals
Documentation drift only; compile/Javadoc generation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ha/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/InnerNode.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/InnerNode.java

## Purpose
Interface for non-leaf network topology nodes such as racks, datacenters, regions, or logical groups.

## Important APIs, Types, And Functions
Nested `Factory` constructs inner nodes. Main APIs add/remove nodes, find nodes by path, count/list nodes at relative levels, select leaves by index with excluded scopes/nodes and ancestor generation, and serialize to `HddsProtos.NetworkNode`.

## Control Flow
Implementations maintain a tree. SCM placement code adds datanodes, removes them, and chooses leaves while respecting topology exclusions.

## State And Persistence
The interface has no state; implementations hold topology tree state. Protobuf serialization supports transport/inspection.

## Dependencies And Integration Points
Extends `Node` and integrates with `NetworkTopology`, placement policies, and datanode topology protobufs.

## Risks And Test Signals
Relative level semantics and exclusion interactions are easy to implement incorrectly. Tests should cover add/remove, leaf indexing, excluded scopes, ancestor generation, equality, and protobuf output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/InnerNode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/NetConstants.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/NetConstants.java

## Purpose
Defines constants and default `NodeSchema` instances for SCM network topology paths, costs, levels, and standard layers.

## Important APIs, Types, And Functions
Constants include path separator, reverse-scope prefix, root/default rack/nodegroup/datacenter/region strings, default costs, root level, and reusable schemas for root, region, datacenter, rack, nodegroup, and leaf.

## Control Flow
No executable flow beyond static initialization of schemas through `NodeSchema.Builder`.

## State And Persistence
Static constants only. Defaults influence runtime topology construction but are not persisted here.

## Dependencies And Integration Points
Depends on `NodeSchema.LayerType` and `StringWithByteString`. Integrated by topology normalization, placement policy, and schema loaders.

## Risks And Test Signals
Changing defaults alters placement compatibility. Tests should verify default schema order/costs, root/rack constants, and path separator assumptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/NetConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/NetUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/NetUtils.java

## Purpose
Utility functions for topology path normalization, depth calculation, duplicate exclusion cleanup, ancestor-list derivation, and path suffix handling.

## Important APIs, Types, And Functions
`normalize`, `locationToDepth`, `removeDuplicate`, `getAncestorList`, and `addSuffix` are the public static APIs.

## Control Flow
`normalize` rejects paths not starting with `/` and strips trailing slash except root. `removeDuplicate` mutates excluded node/scope collections to remove redundant exclusions based on ancestor generation. `getAncestorList` gathers unique ancestors for nodes. `addSuffix` appends `/` if absent.

## State And Persistence
Stateless. It mutates caller-provided exclusion collections in `removeDuplicate`.

## Dependencies And Integration Points
Depends on Apache Commons collection/string utilities and SLF4J. Integrated by topology implementations and placement policies.

## Risks And Test Signals
Mutating inputs can surprise callers, and invalid paths throw. Tests should cover null/empty/root paths, invalid relative paths, depth, duplicate exclusion cases, ancestor missing logs, and suffix behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/NetUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/NetworkTopology.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/NetworkTopology.java

## Purpose
Defines the top-level interface for SCM network topology operations used by placement and node management.

## Important APIs, Types, And Functions
APIs include `add`, `update`, `remove`, `contains`, parent/ancestor comparisons, `getAncestor`, `getMaxLevel`, path lookup, leaf/node counts, node listing, random selection with scopes/exclusions/affinity, index-based selection, distance/cost calculation, and sort-by-distance. Nested `InvalidTopologyException` signals schema/topology errors.

## Control Flow
Implementations maintain topology state as datanodes enter/update/leave and serve placement queries that choose eligible nodes by scope, exclusion, and affinity.

## State And Persistence
Interface stores no state. Implementations are in-memory views derived from datanode registration and network schema.

## Dependencies And Integration Points
Works with `Node` and collections. Integrated by SCM placement policies, replication, and pipeline allocation.

## Risks And Test Signals
Scope syntax with `~`, affinity generation, and exclusion behavior are complex. Tests should cover random/index choice, invalid topology detection, distance sorting, update semantics, and concurrency in concrete implementations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/NetworkTopology.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/Node.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/Node.java

## Purpose
Base interface for any node in SCM network topology, whether an inner node or datanode leaf.

## Important APIs, Types, And Functions
Methods expose and mutate network location/name, full path, parent, ancestor, level, cost, leaf count, ancestor/descendant checks, and optional protobuf conversion via default `toProtobuf`.

## Control Flow
Topology implementations set parent/level/location as nodes are inserted. Placement code uses ancestor/descendant checks and cost/leaf counts.

## State And Persistence
Interface has no state. Implementations usually represent in-memory topology nodes and may serialize to HddsProtos.

## Dependencies And Integration Points
Depends on HddsProtos. Extended by `InnerNode` and implemented by `NodeImpl` and datanode detail classes.

## Risks And Test Signals
The default `toProtobuf` returns null, so callers must account for implementations that do not override it. Tests should cover path/name mutation and ancestor semantics in concrete classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/Node.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/NodeImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/NodeImpl.java

## Purpose
Concrete leaf implementation of `Node` for network topology. It stores name, location, full path, level, parent, and traffic cost, and implements path/ancestor/descendant behavior.

## Important APIs, Types, And Functions
Constructors accept string or `StringWithByteString` name/location with optional parent/level. Getters/setters update cached full path. `getAncestor`, `isAncestor`, `isDescendant`, static `toProtobuf`, `equals`, `hashCode`, and `toString` are key.

## Control Flow
Construction validates names do not contain `/` and normalizes string locations. Mutating name/location recomputes path. Ancestor traversal follows parent links; path checks use case-insensitive equality and slash-suffixed prefix comparisons.

## State And Persistence
State is mutable in memory except final cost. No direct persistence; protobuf helper can serialize basic topology fields.

## Dependencies And Integration Points
Depends on Guava preconditions, HddsProtos, `StringWithByteString`, and `NetUtils`. Used by topology trees and placement code.

## Risks And Test Signals
Comments claim thread safety but mutable fields are unsynchronized. `getPath` can include `StringWithByteString.toString()` for non-root name concatenation. Tests should cover normalization, equality, root behavior, path mutation, ancestor/descendant edge cases, and protobuf helper output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/NodeImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/NodeSchema.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/NodeSchema.java

## Purpose
Represents one layer in a network topology schema, including layer type, cost, path prefix, default name, and optional sublayers.

## Important APIs, Types, And Functions
Nested `Builder` validates `type`, defaults cost from type, and builds `NodeSchema`. Fields have standard getters/setters for YAML binding. `matchPrefix` checks case-insensitive prefix match. `LayerType` defines `ROOT`, `INNER_NODE`, and `LEAF_NODE` with descriptions and default costs plus `getType(String)`.

## Control Flow
Schema loaders can instantiate via no-arg constructor then setters, or code can use the builder. Placement/topology creation uses prefix/default name/cost to map network paths.

## State And Persistence
Instances are mutable to support YAML deserialization. Schema configuration is external; this class models it in memory.

## Dependencies And Integration Points
Depends on `NetConstants`. Integrated by network topology schema loading and default schemas.

## Risks And Test Signals
No validation in setters means YAML can produce inconsistent schemas. `getType` returns null for unknown strings. Tests should cover builder validation/defaults, YAML setter path, prefix matching, sublayers, and unknown layer types.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/NodeSchema.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/package-info.java

## Purpose
Package documentation for Ozone network topology classes.

## Important APIs, Types, And Functions
No APIs are declared. Package contains topology interfaces, node implementation, constants, utilities, and schema model.

## Control Flow
No executable flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Javadoc grouping for `org.apache.hadoop.hdds.scm.net`.

## Risks And Test Signals
Documentation drift only; compile/Javadoc generation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/package-info.java

## Purpose
Package documentation for storage container protocol client classes.

## Important APIs, Types, And Functions
No APIs are declared. The package contains SCM shared DTOs, config classes, Xceiver client contracts, and helper interfaces.

## Control Flow
No executable flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Javadoc grouping for `org.apache.hadoop.hdds.scm`.

## Risks And Test Signals
Documentation drift only; compile/Javadoc generation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/DuplicatedPipelineIdException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/DuplicatedPipelineIdException.java

## Purpose
Specific SCM exception indicating a duplicate pipeline ID was detected.

## Important APIs, Types, And Functions
Constructor accepts a message and passes `SCMException.ResultCodes.DUPLICATED_PIPELINE_ID`.

## Control Flow
Thrown by pipeline creation/load paths when a pipeline ID collision is found.

## State And Persistence
Only inherited exception state.

## Dependencies And Integration Points
Depends on `SCMException`. Integrated by pipeline manager and client error handling.

## Risks And Test Signals
Tests should cover duplicate pipeline detection and result-code propagation over RPC.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/DuplicatedPipelineIdException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/InvalidPipelineStateException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/InvalidPipelineStateException.java

## Purpose
Specific SCM exception indicating a pipeline is in a state invalid for the requested operation.

## Important APIs, Types, And Functions
Constructor accepts a message and maps to `SCMException.ResultCodes.INVALID_PIPELINE_STATE`.

## Control Flow
Thrown by pipeline manager/state-machine operations before illegal transitions or actions.

## State And Persistence
Only inherited exception state.

## Dependencies And Integration Points
Depends on `SCMException`. Integrated by pipeline lifecycle management, allocation, and close/destroy paths.

## Risks And Test Signals
Tests should cover invalid state transitions, user-facing messages, and result-code mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/InvalidPipelineStateException.java -->
