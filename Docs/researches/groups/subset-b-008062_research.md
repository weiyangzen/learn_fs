# subset-b-008062 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OMAdminProtocolClientSideImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OMAdminProtocolClientSideImpl.java

Purpose: Client-side implementation of `OMAdminProtocol` for Ozone Manager administrative RPCs. It supports both targeted single-OM calls, used for node-local metadata/configuration queries, and HA failover calls, used for leader-routed operations such as OM decommissioning.

Important APIs and types: Factory methods `createProxyForSingleOM` and `createProxyForOMHA` build Hadoop protobuf RPC proxies. Public operations are `getOMConfiguration`, `decommission`, `compactOMDB`, `triggerSnapshotDefrag`, and `close`. It converts `OMNodeInfo` protos to `OMNodeDetails`, builds `OMConfiguration`, and uses admin protocol protobuf request/response types.

Control flow: Proxy creation registers `ProtobufRpcEngine`, configures retry policy from OM admin config keys, and either connects directly to one OM RPC address or wraps a `HadoopRpcOMFailoverProxyProvider` in a `RetryProxy`. Each admin method builds one protobuf request, invokes `rpcProxy`, checks success flags, and throws `IOException` with contextual OM print info on failure. Leader-related service exceptions are decoded into `OMNotLeaderException` or `OMLeaderNotReadyException` before falling back to `ProtobufHelper`.

State and persistence behavior: This class holds only an RPC proxy and printable target description. It does not persist state; persistent effects are entirely server-side: OM configuration reads, OM decommission metadata changes, RocksDB compaction, and snapshot defragmentation triggering.

Dependencies and integration points: Integrates Hadoop RPC, OM HA failover providers, `OmUtils` address resolution, OM admin protobuf service, Kerberos-authenticated PB protocol interfaces, and admin CLI flows. `close` delegates to `RPC.stopProxy`.

Risks: `getOMConfiguration` logs `ServiceException` and returns `null`, unlike most methods that throw, so callers must handle null. HA max failovers scale by OM count, so misconfigured OM addresses affect retry duration. `triggerSnapshotDefrag` treats missing `result` as a server error even when `success` is true, which is a useful protocol invariant.

Test signals: Tests should cover direct and HA proxy construction, retry policy configuration, not-leader/leader-not-ready translation, unsuccessful response error messages, null behavior on configuration query failure, and `close` stopping the proxy.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OMAdminProtocolClientSideImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OMAdminProtocolPB.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OMAdminProtocolPB.java

Purpose: Hadoop RPC protobuf binding for OM admin operations. It exposes the generated `OzoneManagerAdminService.BlockingInterface` under Hadoop's protocol metadata.

Important APIs and types: The interface is annotated with `@ProtocolInfo`, `@KerberosInfo`, and `@InterfaceAudience.Private`, and extends `OzoneManagerAdminService.BlockingInterface`.

Control flow: There is no executable logic. Hadoop RPC uses the annotations to identify the protocol name/version and OM Kerberos principal when client and server create proxies.

State and persistence behavior: Stateless interface. Persistence is handled by server implementations of the generated admin service.

Dependencies and integration points: Consumed by `OMAdminProtocolClientSideImpl`, OM admin server-side translator code, Hadoop RPC, and security setup using `OMConfigKeys.OZONE_OM_KERBEROS_PRINCIPAL_KEY`.

Risks: Protocol name and version are compatibility contracts. Changing either can break RPC negotiation. The class comment says communication between OMs, but the protocol name is admin protocol; docs should not be treated as behavioral authority.

Test signals: RPC integration tests should confirm clients can create proxies, authenticate with the configured OM principal, and invoke generated admin service methods through this PB interface.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OMAdminProtocolPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OMInterServiceProtocolClientSideImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OMInterServiceProtocolClientSideImpl.java

Purpose: Client-side `OMInterServiceProtocol` implementation for inter-OM bootstrap communication. It sends bootstrap metadata for a new OM node to the current OM leader through the HA RPC ring.

Important APIs and types: Constructor builds a `HadoopRpcOMFailoverProxyProvider<OMInterServiceProtocolPB>` and retry proxy. `bootstrap(OMNodeDetails)` sends `BootstrapOMRequest`; `close` closes the failover provider. It uses `BootstrapOMResponse.ErrorCode` for structured failure messages.

Control flow: Construction registers the protobuf RPC engine and uses `OZONE_CLIENT_FAILOVER_MAX_ATTEMPTS` for max failovers. `bootstrap` maps `OMNodeDetails` fields to node ID, host address, Ratis port, and listener flag, invokes `rpcProxy.bootstrap`, translates not-leader and leader-not-ready service exceptions into bootstrap-specific `IOException`s, then checks response success.

State and persistence behavior: Runtime state is the failover provider and retry proxy. The client does not persist state; successful bootstrap mutates OM cluster membership/bootstrap state on the server.

Dependencies and integration points: Integrates OM HA proxy selection, Hadoop RPC, `UserGroupInformation`, inter-service protobufs, and OM reconfiguration/bootstrap workflows.

Risks: `throwException` wraps all bootstrap failures as generic `IOException`, so callers relying on typed exceptions only get message text. Failure behavior depends on `HadoopRpcOMFailoverProxyProvider` correctly detecting leader exceptions.

Test signals: Exercise bootstrap request field mapping, failover to leader, failure response error-code propagation, leader-not-ready/not-leader handling, and provider cleanup on close.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OMInterServiceProtocolClientSideImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OMInterServiceProtocolPB.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OMInterServiceProtocolPB.java

Purpose: Hadoop RPC protobuf binding for OM inter-service operations.

Important APIs and types: Private interface annotated with protocol name `org.apache.hadoop.ozone.om.protocol.OMInterServiceProtocol`, protocol version 1, OM Kerberos principal, and generated `OzoneManagerInterService.BlockingInterface`.

Control flow: No runtime logic in the interface. Hadoop RPC reads annotations and dispatches generated blocking methods implemented by server-side OM inter-service code.

State and persistence behavior: Stateless type declaration. Any cluster membership or bootstrap persistence occurs in server code.

Dependencies and integration points: Used by `OMInterServiceProtocolClientSideImpl`, Hadoop PB RPC server registration, and OM HA/security configuration.

Risks: The protocol metadata is a wire compatibility boundary. Generated service method changes must remain aligned with the Java interface and server translator.

Test signals: Proxy construction and successful `bootstrap` invocation over Hadoop RPC are the main integration signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OMInterServiceProtocolPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OmTransport.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OmTransport.java

Purpose: Transport abstraction used by the OM client-side translator to submit already-built `OMRequest` messages and receive `OMResponse` messages without hard-coding Hadoop RPC or gRPC.

Important APIs and types: Defines `submitRequest(OMRequest)`, `getDelegationTokenService()`, and `close()`. The token service is returned as Hadoop `Text`.

Control flow: Interface only. Implementations decide serialization, retry/failover, channel lifecycle, and delegation-token service address formatting.

State and persistence behavior: No state in the interface. Implementations generally own RPC channels, failover counters, and service-address metadata; server-side OM owns persistent request effects.

Dependencies and integration points: Consumed by `OzoneManagerProtocolClientSideTranslatorPB` and produced by `OmTransportFactory`. Implementations include Hadoop RPC and gRPC transport classes elsewhere in the package.

Risks: All client protocol behavior flows through this narrow contract. Implementations must preserve request ordering, exception semantics, token service compatibility, and close behavior expected by the translator.

Test signals: Mock transports should verify request construction in translator tests. Transport implementation tests should assert response propagation, IO exception behavior, token service text, and idempotent cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OmTransport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OmTransportFactory.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OmTransportFactory.java

Purpose: Factory SPI for constructing OM client transports. It allows a transport implementation to be discovered by `ServiceLoader` or loaded from OM transport class configuration.

Important APIs and types: Instance method `createOmTransport(ConfigurationSource, UserGroupInformation, String)` and static methods `create` and `createFactory`. It uses `OZONE_OM_TRANSPORT_CLASS` and `OZONE_OM_TRANSPORT_CLASS_DEFAULT`.

Control flow: `create` delegates to `createFactory`, then calls the instance factory method. `createFactory` first checks `ServiceLoader<OmTransportFactory>` and returns the first implementation found. If none exists, it loads the configured class from this interface's class loader and instantiates it via `newInstance`. Any error is wrapped in `IOException`.

State and persistence behavior: No persistent state. Runtime choice can vary by classpath service entries or configuration.

Dependencies and integration points: Integrates Java SPI, Ozone configuration, UGI, OM service IDs, and client translator construction. This is the extension point for switching Hadoop RPC/gRPC/custom transports.

Risks: First service-loader result wins, which can be surprising when multiple providers are present. Reflective `newInstance` requires a public no-arg constructor and wraps details. Classpath order can alter transport behavior.

Test signals: Cover SPI discovery precedence, configured-class fallback, failure wrapping for bad classes, and correct propagation of conf/UGI/service ID into created transport.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OmTransportFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OzoneManagerClientProtocol.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OzoneManagerClientProtocol.java

Purpose: Client-side extension of `OzoneManagerProtocol` that adds thread-local S3 authentication management needed by the S3 Gateway while it builds OM requests.

Important APIs and types: Methods `setThreadLocalS3Auth`, `getThreadLocalS3Auth`, `clearThreadLocalS3Auth`, and `getS3CredentialsProvider` expose a `ThreadLocal<S3Auth>`.

Control flow: Interface only. Implementations attach S3 auth to each generated OM request, typically in the shared submit path.

State and persistence behavior: No persistence. The intended state is per-thread and per-request; callers must clear credentials after S3 request handling to avoid leakage across reused worker threads.

Dependencies and integration points: Implemented by `OzoneManagerProtocolClientSideTranslatorPB`; consumed by S3 Gateway request handlers and OM protocol clients.

Risks: Thread-local credentials are easy to leak in pools. `getS3CredentialsProvider` exposes the mutable `ThreadLocal`, so callers can bypass setter/clearer conventions.

Test signals: Verify S3 credentials are inserted into requests only for the active thread, are absent after clear, and strict auth-check paths fail when credentials are missing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OzoneManagerClientProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OzoneManagerProtocolClientSideTranslatorPB.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OzoneManagerProtocolClientSideTranslatorPB.java

Purpose: Main client-side translator from the high-level `OzoneManagerProtocol` Java API to `OzoneManagerProtocolProtos.OMRequest` messages submitted through an `OmTransport`. It is the broad compatibility layer for volume, bucket, key, filesystem, multipart, snapshot, tenant, ACL, token, upgrade, quota, and utility OM operations.

Important APIs and types: Constructor accepts `OmTransport` and client ID. Shared helpers are `createOMRequest`, `submitRequest`, `handleError`, `handleSubmitRequestAndSCMSafeModeRetry`, `setReplicationConfig`, S3 thread-local accessors, and safe-mode conversion. Public methods implement the full OM client API, including `createVolume`, `setOwner`, `setQuota`, bucket CRUD/listing, `openKey`, `allocateBlock`, `commitKey`/`hsyncKey`/`recoverKey`, key lookup/list/delete/rename, S3 secret and tenant APIs, snapshot APIs, multipart APIs, service discovery, upgrade finalization, delegation-token lifecycle, file APIs, ACL APIs, DB update fetch, prepare/cancel prepare, echo RPC, lease recovery, safe mode, quota repair, and object tagging.

Control flow: Each method builds the relevant protobuf request, wraps it in an `OMRequest` with command type, current client version, client ID, and trace ID, submits it through `transport`, checks status, and converts response protos back to helper objects. `submitRequest` injects thread-local S3 authentication and caller context when present and can enforce `s3AuthCheck`. `handleError` maps non-OK protobuf statuses to `OMException` using ordinal-aligned result codes. Key/file creation and block allocation use `handleSubmitRequestAndSCMSafeModeRetry`, retrying `SCM_IN_SAFE_MODE` for 90 one-second sleeps.

State and persistence behavior: Runtime state is client ID, non-reusable transport, per-thread S3 auth, and an `s3AuthCheck` flag. It does not persist local state. Persistent effects occur on OM/Ratis metadata and SCM block allocation through server-side handling. `getDBUpdates` streams OM DB write batches into a `DBUpdates` wrapper for follower/bootstrap consumers.

Dependencies and integration points: Integrates `OmTransport`, Ozone helper model classes, protobuf request/response classes, tracing, Hadoop caller context, delegation token protos through `OMPBHelper`, EC and legacy replication config conversion, snapshot DTOs, upgrade finalization, OM prepare, SCM safe-mode status, S3 Gateway auth, tenant management, ACL object conversion, and file-system-style Ozone status classes.

Risks: The class is very broad, so protobuf enum/status ordinal alignment is critical. Quiet multi-key delete reads error details without calling `handleError`; callers must opt into the semantics intentionally. S3 auth uses thread local storage and must be cleared by callers. SCM safe-mode retry writes to stderr and sleeps synchronously, which can block application threads for up to about 90 seconds. Some methods manually build `KeyArgs` instead of using `OmKeyArgs.toProtobuf`, so new fields can be missed unless every path is updated. `createDirectory` suppresses `DIRECTORY_ALREADY_EXISTS` because the API cannot return a boolean.

Test signals: Mock-transport tests should assert command type, request payload fields, S3 auth injection, trace/caller context, and helper-object response conversion for each API family. Integration tests should cover non-OK status mapping, token error wrapping, SCM safe-mode retry and interruption, EC versus replicated config encoding, snapshot pagination compatibility, tenant/S3 secret flows, DB update redaction/streaming, file-status light/heavy differences, and `close` delegating to transport.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OzoneManagerProtocolClientSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OzoneManagerProtocolPB.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OzoneManagerProtocolPB.java

Purpose: Hadoop RPC protobuf binding for the main Ozone Manager client protocol.

Important APIs and types: Extends generated `OzoneManagerService.BlockingInterface`, declares protocol and Kerberos metadata, and advertises `OzoneDelegationTokenSelector` through `@TokenInfo`. Static `newProxy` helpers wrap OM failover providers in Hadoop `RetryProxy`.

Control flow: No request logic is implemented here. The two static helpers build retrying proxies using either a general OM failover provider or a follower-read failover provider with provider-supplied retry policies.

State and persistence behavior: Stateless interface. Persistent behavior is server-side OM request handling.

Dependencies and integration points: Used by Hadoop RPC transport, OM failover providers, client translator construction, delegation token selection, and secure RPC negotiation.

Risks: Protocol metadata and token selector are compatibility-sensitive. The static proxy helpers centralize retry wrapping; provider retry policies must remain compatible with read/write/follower-read semantics.

Test signals: Validate proxy creation for normal and follower-read providers, delegation-token service lookup, secure RPC principal use, and generated service method invocation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OzoneManagerProtocolPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/grpc/ClientAddressClientInterceptor.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/grpc/ClientAddressClientInterceptor.java

Purpose: gRPC client interceptor that propagates caller hostname and IP address from gRPC `Context` into request metadata headers.

Important APIs and types: Implements `ClientInterceptor.interceptCall`, wraps the call in `ForwardingClientCall.SimpleForwardingClientCall`, and writes `GrpcClientConstants` metadata keys during `start`.

Control flow: On call start, it reads `CLIENT_HOSTNAME_CTX_KEY` and `CLIENT_IP_ADDRESS_CTX_KEY`; when values are present it puts them into the corresponding metadata headers before delegating to the original call.

State and persistence behavior: Stateless interceptor. Metadata is per-RPC and not persisted locally.

Dependencies and integration points: Paired with `ClientAddressServerInterceptor`, gRPC channel construction, and any OM/Ranger/audit code that reads client address from server context.

Risks: Local variable names are swapped (`ipAddress` stores hostname and `hostname` stores IP), but the values are written to matching metadata keys. This is confusing and could cause future maintenance mistakes. Missing context values simply omit headers.

Test signals: gRPC interceptor tests should set each context key independently and assert exact metadata header population and absence when null.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/grpc/ClientAddressClientInterceptor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/grpc/ClientAddressServerInterceptor.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/grpc/ClientAddressServerInterceptor.java

Purpose: gRPC server interceptor that reads client hostname/IP metadata and places it into the current gRPC `Context` for downstream service handlers.

Important APIs and types: Implements `ServerInterceptor.interceptCall`, reads `Metadata.Key<String>` constants, uses `Context.current().withValue`, and delegates via `Contexts.interceptCall`.

Control flow: For each RPC, it extracts both metadata headers, creates a derived context containing both values, and continues the call under that context.

State and persistence behavior: No persistent state. The derived context is scoped to the server call.

Dependencies and integration points: Paired with the client interceptor and consumed by server-side authorization/auditing layers that consult `GrpcClientConstants` context keys.

Risks: Null metadata is stored as null context values. Tests should ensure downstream code handles missing client address values. Header names are ASCII and case-sensitive through gRPC metadata conventions.

Test signals: Verify server handlers see the expected context values when headers are present and null values when absent.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/grpc/ClientAddressServerInterceptor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/grpc/GrpcClientConstants.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/grpc/GrpcClientConstants.java

Purpose: Defines shared gRPC context and metadata keys for client hostname and client IP address propagation.

Important APIs and types: `CLIENT_HOSTNAME_CTX_KEY`, `CLIENT_HOSTNAME_METADATA_KEY`, `CLIENT_IP_ADDRESS_CTX_KEY`, and `CLIENT_IP_ADDRESS_METADATA_KEY`. The metadata keys use `Metadata.ASCII_STRING_MARSHALLER`.

Control flow: No logic beyond constant initialization and private constructor.

State and persistence behavior: Stateless constants. Values are per gRPC context or metadata instance.

Dependencies and integration points: Used by client and server interceptors and any downstream service code reading client address context.

Risks: Key names are protocol-level strings; changing them breaks propagation. Context key identity must be shared from this class rather than recreated elsewhere.

Test signals: Header round-trip tests through both interceptors validate these constants.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/grpc/GrpcClientConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/grpc/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/grpc/package-info.java

Purpose: Package documentation for gRPC interceptors and related classes that provide specific gRPC headers.

Important APIs and types: Documents package `org.apache.hadoop.ozone.om.protocolPB.grpc`.

Control flow: No executable code.

State and persistence behavior: None.

Dependencies and integration points: Applies to client/server address interceptors and constants in the same package.

Risks: Documentation only; it can become stale if additional gRPC transport support is added beyond header propagation.

Test signals: No direct tests needed beyond package-level doc lint/compile.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/grpc/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/package-info.java

Purpose: Package documentation for Ozone OM transport/protocolPB classes.

Important APIs and types: Documents package `org.apache.hadoop.ozone.om.protocolPB`.

Control flow: No executable logic.

State and persistence behavior: None.

Dependencies and integration points: Covers PB protocol interfaces, client translators, and transport abstractions in the package.

Risks: Documentation is broad and may not reflect the full set of modern transport implementations unless maintained with package evolution.

Test signals: Compile/package-doc generation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/package-info.java

Purpose: Top-level package documentation for Ozone REST-interface-related classes.

Important APIs and types: Documents package `org.apache.hadoop.ozone`.

Control flow: No executable logic.

State and persistence behavior: None.

Dependencies and integration points: Package-level documentation for common Ozone classes in this source root.

Risks: The comment is narrow relative to the package's broader modern contents, so it may be stale.

Test signals: Compile/package-doc generation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/protocolPB/OMPBHelper.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/protocolPB/OMPBHelper.java

Purpose: Utility class for converting common OM protocol values between Hadoop/Ozone Java objects and protobuf representations, plus safe debug rendering of OM messages.

Important APIs and types: Token conversion `tokenFromProto`/`protoFromToken`; bucket and file encryption conversions; file checksum conversions for `MD5MD5CRC32FileChecksum` and `CompositeCrcFileChecksum`; cipher suite and crypto protocol version enum conversions; `processForDebug(OMRequest/OMResponse)`. `REDACTED` is used to hide DB update payloads.

Control flow: Conversion methods validate nulls where required, build protobuf messages or Java helper objects, and switch over checksum/cipher/protocol enum types. MD5 checksum conversion reads the serialized Hadoop checksum layout to extract bytes-per-CRC, CRC-per-block, and MD5. Response debug rendering clones DB update responses and replaces data entries with a redacted marker before formatting.

State and persistence behavior: Stateless static helper. It does not persist data but affects serialized wire/storage forms for tokens, encryption info, and checksums.

Dependencies and integration points: Used by OM client translator token APIs, block/delegation token code, encrypted bucket/key handling, checksum APIs, and debug logging. It depends on Hadoop crypto/checksum classes, Ozone checksum helpers, protobuf classes, and SCM PB helper ByteString utilities.

Risks: Checksum conversion is wire-compatibility-sensitive. There is explicit compatibility handling for a fixed HDDS-12954 bug where proto MD5 could be stored in a 20-byte buffer. Unsupported checksum runtime types log warnings and return null, which callers must tolerate. Enum conversions return `null` for unknown Java enum defaults in some directions.

Test signals: Round-trip tests for tokens, bucket/file encryption info, MD5 CRC32/CRC32C checksums, composite CRC checksums, unknown cipher/protocol handling, legacy oversized MD5 proto input, null validation, and DB update redaction in debug strings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/protocolPB/OMPBHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/protocolPB/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/protocolPB/package-info.java

Purpose: Package documentation for Protocol Buffers bindings of Ozone protocols.

Important APIs and types: Documents package `org.apache.hadoop.ozone.protocolPB`.

Control flow: No executable logic.

State and persistence behavior: None.

Dependencies and integration points: Applies to helper/converter classes and PB protocol bindings under this package.

Risks: Documentation only; package contents should remain aligned with protobuf binding purpose.

Test signals: Compile/package-doc generation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/protocolPB/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/request/validation/RegisterValidator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/request/validation/RegisterValidator.java

Purpose: Meta-annotation for registering request validator annotations. It identifies annotations that a reflection or annotation-processing system should treat as validator descriptors.

Important APIs and types: Runtime-retained annotation targeting annotation types. Constants define required method names: `applyBefore`, `requestType`, and `processingPhase`.

Control flow: No direct logic. `RegisterValidatorProcessor` or runtime discovery scans annotations annotated with `@RegisterValidator` and expects the named methods with documented return types.

State and persistence behavior: Annotation metadata is stored in class files and retained at runtime; no application persistence.

Dependencies and integration points: Tied to Ozone layout-version-aware request validation, `Versioned`, `RequestProcessingPhase`, and server request handling code that discovers validators.

Risks: The contract is name-based, so typos or signature mismatches in downstream validator annotations can fail at processing/discovery time. Runtime retention has reflection cost but enables dynamic discovery.

Test signals: Annotation processor tests should reject invalid validator annotations and accept valid annotations with the three required methods.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/request/validation/RegisterValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/request/validation/RequestProcessingPhase.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/request/validation/RequestProcessingPhase.java

Purpose: Enum describing when a registered request validator should run relative to generic request processing.

Important APIs and types: Values are `PRE_PROCESS` and `POST_PROCESS`.

Control flow: No logic. Validation dispatchers use the enum to choose hook points before or after request handling.

State and persistence behavior: Stateless enum; values may appear in generated metadata or reflected annotation values.

Dependencies and integration points: Used by `RegisterValidator`-annotated annotations and validation registries in OM request processing.

Risks: Adding or renaming values affects annotations, generated validator indexes, and dispatch logic.

Test signals: Validator discovery tests should route methods into the expected pre/post buckets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/request/validation/RequestProcessingPhase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/request/validation/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/request/validation/package-info.java

Purpose: Package documentation for Ozone request validation support.

Important APIs and types: Describes `RegisterValidator`, expected validator annotation methods, and reflection-based discovery for situation-specific request handling behavior.

Control flow: No executable logic, but the documentation outlines the discovery flow: annotated annotations describe request type, processing phase, and layout version before which a validator applies.

State and persistence behavior: None.

Dependencies and integration points: Documents request handler extension points for server code and layout-version-aware validators.

Risks: Documentation has long lines and can drift from actual annotation processor behavior; processor tests are more authoritative.

Test signals: Package docs compile; validation framework tests should match the documented contract.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/request/validation/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/GDPRSymmetricKey.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/GDPRSymmetricKey.java

Purpose: Encapsulates a symmetric encryption key and cipher parameters used for GDPR-related Ozone metadata.

Important APIs and types: `newDefaultInstance`, `randomSecret`, constructors from `SecureRandom` or explicit secret/algorithm, `getSecretKey`, `getCipher`, and `acceptKeyDetails`. It stores `SecretKeySpec`, `Cipher`, algorithm, and secret string.

Control flow: The default factory uses a thread-local `SecureRandom` to generate a random alphanumeric secret of the configured default length, then constructs a key with the default GDPR algorithm. Explicit construction validates non-null secret/algorithm and currently requires a 16-character secret before creating `SecretKeySpec` and `Cipher`.

State and persistence behavior: Holds secret material in memory as a `String`, a key spec, and a cipher object. `acceptKeyDetails` exposes the secret and algorithm to a consumer, typically for attaching metadata or persisting key details elsewhere.

Dependencies and integration points: Uses `OzoneConsts` for GDPR constants/charset, Java crypto APIs, Guava preconditions, and Apache Commons random string generation.

Risks: Secret length is hard-coded to 16 characters, so algorithm customization is constrained. Secrets are retained as immutable strings and can be emitted via `acceptKeyDetails`; callers must protect metadata/logging. `Cipher` instances are stateful and not generally thread-safe, so key instances should not be shared for concurrent cipher operations without care.

Test signals: Validate default generation length/algorithm, rejection of null or wrong-length secrets, deterministic construction with explicit secret, `acceptKeyDetails` keys, and cipher/key algorithm compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/GDPRSymmetricKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/OzoneDelegationTokenSelector.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/OzoneDelegationTokenSelector.java

Purpose: Hadoop delegation token selector specialized for Ozone tokens.

Important APIs and types: Extends `AbstractDelegationTokenSelector<OzoneTokenIdentifier>` with `OzoneTokenIdentifier.KIND_NAME`. Overrides `selectToken` and uses `getSelectedTokens` to scan token collections.

Control flow: If the requested service is null it returns null. Otherwise it returns the first token whose kind is `OzoneToken` and whose service string contains the requested service string. Trace/debug logging records lookup and result.

State and persistence behavior: Stateless selector. It reads in-memory token collections; token persistence is handled by Hadoop credentials.

Dependencies and integration points: Referenced by `@TokenInfo` on `OzoneManagerProtocolPB` and used by secure OM clients when selecting credentials for RPC services.

Risks: Service matching uses substring containment rather than exact equality, which supports multi-address service strings but can accidentally match overlapping service names. The method uses an unchecked cast after kind filtering.

Test signals: Cover null service, empty tokens, exact and multi-address service matching, non-Ozone token rejection, first-match behavior, and overlapping service-name cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/OzoneDelegationTokenSelector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/OzoneTokenIdentifier.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/OzoneTokenIdentifier.java

Purpose: Token identifier for Ozone Manager delegation tokens and S3 authentication tokens. It extends Hadoop's delegation token identifier with OM-specific secret-key/certificate identity, S3 auth fields, and OM service ID.

Important APIs and types: Constants and fields include `KIND_NAME`, deprecated `omCertSerialId`, `secretKeyId`, token `Type`, S3 access/signature/string-to-sign, and `omServiceId`. Key methods are constructors, `getKind`, `fromUniqueSerializedKey`, `toProtoBuf`, `write`, `readFields`, `readProtoBuf`, factories, equality/hash, accessors, and nested `TokenInfo`.

Control flow: Current serialization writes the `OMTokenProto` bytes directly and reads them back from a `DataInputStream`. `readProtoBuf` constructs identifiers from proto fields. `fromUniqueSerializedKey` supports explicit legacy deserialization: it reads superclass fields and a VInt token type, then either S3 fields or delegation token key identity plus service ID. For delegation tokens it treats a UUID-looking value as `secretKeyId`, otherwise as deprecated certificate serial ID.

State and persistence behavior: This class is serialized into token identifiers stored in Hadoop credentials and OM token databases. `TokenInfo` stores renew date, password copy, and optional tracking ID. Setters enforce that `omCertSerialId` and `secretKeyId` are not both valid.

Dependencies and integration points: Used by OM token managers, Hadoop security token framework, `OzoneDelegationTokenSelector`, OM protobuf token messages, S3 authentication flows, and secret-key/certificate migration compatibility.

Risks: `readFields` casts `DataInput` to `DataInputStream`, so non-stream inputs would fail. `toString` includes signature, string-to-sign, and access key ID, which is sensitive if logged. `equals` does not compare S3-specific fields or token type, so equality is delegation-token oriented. Serialization compatibility is high-risk because stored tokens must survive upgrades.

Test signals: Round-trip protobuf serialization for delegation and S3 tokens, legacy unique-key parsing for UUID and non-UUID key IDs, mutual exclusion of certificate and secret key IDs, `TokenInfo` password defensive copy, equality semantics, and secure logging review for `toString`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/OzoneTokenIdentifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/AssumeRoleRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/AssumeRoleRequest.java

Purpose: Immutable data carrier for authorizing an S3 STS AssumeRole request through `IAccessAuthorizer`.

Important APIs and types: Fields include host, IP, client UGI, target role name, and optional grants. Nested immutable `OzoneGrant` encapsulates object set, ACL permission set, and optional S3 action restrictions.

Control flow: Constructors assign fields; getters expose them; equality/hash cover all fields. `OzoneGrant` with S3 actions defensively wraps a `LinkedHashSet` in an unmodifiable set. The two-argument grant constructor uses an empty action set to mean no S3 action restriction.

State and persistence behavior: Immutable request object with in-memory authorization inputs. It does not persist grants or session policies itself.

Dependencies and integration points: Passed to `IAccessAuthorizer.generateAssumeRoleSessionPolicy`; ties together `UserGroupInformation`, `IOzoneObj`, ACL types, and S3 action names parsed from session policies.

Risks: The outer `grants` set is not defensively copied, so immutability depends on caller discipline. `null` grants means no extra limitation beyond role, while an empty set means no access; tests and callers must preserve this distinction.

Test signals: Cover equality/hash, S3 action immutability, null versus empty grant semantics in authorizers, and mutation behavior for caller-provided grant sets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/AssumeRoleRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/IAccessAuthorizer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/IAccessAuthorizer.java

Purpose: Public extension interface for Ozone ACL authorization providers, including native and external systems such as Ranger.

Important APIs and types: Core method `checkAccess(IOzoneObj, RequestContext)` returns authorization decision or throws `OMException`. Default `generateAssumeRoleSessionPolicy` rejects STS support with `NOT_SUPPORTED_OPERATION`. Default `isNative` returns false. Nested enums `ACLType` and `ACLIdentityType` define permissions and identity classes.

Control flow: `ACLType` maps compact string rights from `OzoneConsts` to enum values and back, renders `BitSet` ACLs, parses comma-separated enum names, and enforces a maximum of 16 ACLs because other encoding code assumes that width. `ACLIdentityType` maps user/group/world/anonymous/client-IP identity categories to string constants.

State and persistence behavior: Interface is stateless, but enum names, ordinals, and string encodings are persisted in ACL metadata and external policies. `ASSUME_ROLE` extends the permission model for STS token creation.

Dependencies and integration points: Used by OM ACL checks, Ranger plugin integration, native authorizer, request contexts, Ozone ACL protobuf/model conversion, and tenant/S3 STS workflows.

Risks: `getAclTypeFromOrdinal` condition appears intended to reject ordinal `< 0` or `>= length`, but the `&&` expression only rejects values greater than length and positive; negative ordinals can still reach array indexing. Adding ACL values beyond 16 triggers assertion and requires encoding changes. String parsing with `Enum.valueOf` in `parseList` expects enum names, not short ACL letters.

Test signals: Exhaustive string-to-enum and enum-to-string mapping, BitSet rendering, invalid/negative ordinal behavior, parse-list whitespace handling, default STS rejection, and provider-specific `checkAccess` contracts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/IAccessAuthorizer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/IOzoneObj.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/IOzoneObj.java

Purpose: Marker interface for objects that can participate in Ozone authorization.

Important APIs and types: Empty interface implemented by `OzoneObj`.

Control flow: No logic.

State and persistence behavior: None.

Dependencies and integration points: Used by `IAccessAuthorizer.checkAccess` and AssumeRole grants to accept Ozone object abstractions without depending on a concrete implementation.

Risks: Marker-only design means authorizers often need casts or reflective knowledge of supported implementations.

Test signals: No direct tests beyond authorizer compatibility with concrete `OzoneObj` implementations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/IOzoneObj.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneAccessAuthorizer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneAccessAuthorizer.java

Purpose: No-op native `IAccessAuthorizer` implementation that allows every access check.

Important APIs and types: Singleton instance returned by `get`; `checkAccess` always returns true; `isNative` returns true.

Control flow: No branching beyond returning the singleton and unconditional authorization.

State and persistence behavior: Stateless singleton. It does not read ACL metadata or persist decisions.

Dependencies and integration points: Used when ACL enforcement is disabled or when a permissive native authorizer is configured. It satisfies code paths that require an authorizer instance.

Risks: If accidentally configured in a secured deployment, all ACL checks pass. Its `isNative` true can affect code that treats native authorizers specially even though it is permissive.

Test signals: Verify singleton identity, unconditional success, and configuration tests that distinguish permissive authorizer from enforcing native/Ranger authorizers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneAccessAuthorizer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneObj.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneObj.java

Purpose: Abstract base for ACL-addressable Ozone resources. It carries resource type and store type and defines the path/name accessors required by authorizers and audit logic.

Important APIs and types: Fields `ResourceType` and `StoreType`; static `toProtobuf`; abstract getters for volume, bucket, key, prefix, prefix path viewer, and full path; `toAuditMap`; equality/hash over type fields. Resource types are VOLUME, BUCKET, KEY, PREFIX; store types are OZONE and S3.

Control flow: Construction validates non-null types. `toProtobuf` maps enum names to protocol enums and includes `getPath`. `toAuditMap` emits resource/storage/volume/bucket/key fields in a linked map.

State and persistence behavior: Stores only object identity metadata in memory. Protobuf conversion creates the serialized form used in OM ACL requests and potentially persisted metadata.

Dependencies and integration points: Used by `OzoneObjInfo`, OM ACL APIs, client translator ACL methods, authorizers, audit logs, and protobuf object representation.

Risks: Base equality only compares resource and store type; subclasses must include path fields, as `OzoneObjInfo` does. Enum name alignment with protobuf enums is required by `valueOf`.

Test signals: Protobuf round-trip through `OzoneObjInfo`, audit map contents, enum alignment, and subclass equality including path data.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneObj.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneObjInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneObjInfo.java

Purpose: Concrete immutable Ozone ACL object for volume, bucket, key, and prefix resources.

Important APIs and types: Stores volume name, bucket name, and a shared `name` field for key or prefix. Methods implement full path construction, protobuf parsing, getters, builder helpers, and equality/hash. Builder supports `fromKeyArgs`, `fromOzoneObj`, and field setters.

Control flow: `getPath` builds slash-delimited paths based on resource type. `fromProtobuf` splits the protobuf path into at most three tokens and validates the number of components required for each resource type before building an object. Builder does not validate required fields at build time beyond `OzoneObj` type null checks.

State and persistence behavior: In-memory object identity used for ACL checks and ACL RPC payloads. Protobuf path strings are the serialized boundary.

Dependencies and integration points: Used by client ACL APIs, OM ACL metadata, authorizers, `OmKeyArgs`, and `OzonePrefixPath` viewers for recursive prefix checks.

Risks: Path parsing depends on delimiter normalization and paths with missing components throw `IllegalArgumentException`. Builder allows inconsistent states such as key resource with null name. Key and prefix share the same `name` slot, so callers must set the correct setter for clarity.

Test signals: Path generation for each resource type, protobuf round-trip, malformed path rejection, builder helpers from key args/object, equality including prefix path viewer, and null-field behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneObjInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/OzonePrefixPath.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/OzonePrefixPath.java

Purpose: Interface for viewing an Ozone key prefix as a path tree during ACL checks, especially recursive prefix authorization.

Important APIs and types: `getOzoneFileStatus()` returns status for the represented path. `getChildren(String keyPrefix)` returns immediate child `OzoneFileStatus` entries for a directory-like prefix and may throw `IOException`.

Control flow: Interface only. Implementations should list only immediate children and avoid recursive traversal; the Javadoc gives examples for nested paths.

State and persistence behavior: No state in the interface. Implementations typically read OM key/table state to synthesize file statuses.

Dependencies and integration points: Referenced by `OzoneObj`/`OzoneObjInfo` and authorizers that need to recursively evaluate ACLs over prefix subpaths.

Risks: Recursive ACL behavior depends on implementations honoring immediate-child semantics. Returned iterators may represent live server-side state and throw during traversal depending on implementation.

Test signals: Implementation tests should cover file status retrieval, immediate child listing, directory versus file behavior, empty prefixes, and IOException propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/OzonePrefixPath.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/RequestContext.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/RequestContext.java

Purpose: Immutable authorization context carrying caller identity, network address, requested ACL right, owner, recursive flag, STS session policy, and S3 action.

Important APIs and types: Fields include host, IP, client UGI, service ID, ACL identity type, ACL right, owner name, recursive-access flag, session policy, and S3 action. `Builder` provides setters, `build`, and a getter for current ACL right; `toBuilder` clones a context.

Control flow: Callers assemble contexts with `RequestContext.newBuilder()`. Authorizers read fields to decide access. `toBuilder` copies every field for mutation.

State and persistence behavior: In-memory per-request object. Session policy string can be a serialized authorization policy produced by `generateAssumeRoleSessionPolicy`; this class does not parse or persist it.

Dependencies and integration points: Used by all `IAccessAuthorizer.checkAccess` implementations, recursive prefix checks, owner privilege logic, Ranger STS session policy handling, and S3 Gateway action restrictions.

Risks: Builder performs no validation, so null ACL rights, UGI, or owner can reach authorizers. Session policy and S3 action are plain strings; format validation is provider-specific. Recursive flag has meaning only when the target object is directory-like.

Test signals: Verify builder/toBuilder field preservation, authorizer behavior for missing optional fields, recursive check behavior, and STS/S3 action propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/RequestContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/package-info.java

Purpose: Package documentation for Ozone ACL-related classes.

Important APIs and types: Documents package `org.apache.hadoop.ozone.security.acl`.

Control flow: No executable logic.

State and persistence behavior: None.

Dependencies and integration points: Applies to authorizer interfaces, object descriptors, request contexts, and STS request DTOs.

Risks: Very brief documentation; package behavior is defined by the individual types.

Test signals: Compile/package-doc generation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/package-info.java

Purpose: Package documentation for Ozone security-related classes.

Important APIs and types: Documents package `org.apache.hadoop.ozone.security`.

Control flow: No executable logic.

State and persistence behavior: None.

Dependencies and integration points: Applies to token identifiers, delegation token selection, GDPR symmetric key utilities, and other security support classes.

Risks: Documentation is broad and intentionally minimal.

Test signals: Compile/package-doc generation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/CancelSnapshotDiffResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/CancelSnapshotDiffResponse.java

Purpose: Simple response DTO for cancel-snapshot-diff calls.

Important APIs and types: Stores a message string exposed by `getMessage` and `toString`. Nested `CancelMessage` enum defines canonical user-facing messages for cancel outcomes.

Control flow: Constructor assigns the message; enum constants each carry a message retrievable by `getMessage`.

State and persistence behavior: In-memory response object. Message values may cross client/server API boundaries but this class does not persist state.

Dependencies and integration points: Returned by `OzoneManagerProtocolClientSideTranslatorPB.cancelSnapshotDiff` after reading the server response reason.

Risks: Message strings are user-facing and may be asserted by CLI tests. Some enum messages encode state transitions and should remain synchronized with server cancel logic.

Test signals: Verify response/toString returns server reason and enum messages match expected CLI output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/CancelSnapshotDiffResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/ListSnapshotDiffJobResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/ListSnapshotDiffJobResponse.java

Purpose: DTO for paginated list-snapshot-diff-job API responses.

Important APIs and types: Final class with `List<SnapshotDiffJob>` and optional `lastSnapshotDiffJob` continuation marker. Provides getters and `toString`.

Control flow: Constructor assigns fields; no transformation or validation.

State and persistence behavior: In-memory response wrapper. Snapshot diff job persistence is maintained server-side.

Dependencies and integration points: Built by the OM client translator from `ListSnapshotDiffJobResponse` protobufs and consumed by CLI/client code for pagination.

Risks: The list is not defensively copied, so caller mutations can alter the response object. Continuation marker null means no explicit next page.

Test signals: Verify protobuf-to-DTO conversion in translator, continuation marker behavior, and string rendering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/ListSnapshotDiffJobResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/ListSnapshotResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/ListSnapshotResponse.java

Purpose: DTO for paginated snapshot listing responses.

Important APIs and types: Holds `List<SnapshotInfo>` and optional `lastSnapshot` marker, with getters and `toString`.

Control flow: Constructor assigns fields. Pagination compatibility logic is in the client translator, not this class.

State and persistence behavior: In-memory wrapper over server-provided snapshot info. It does not persist snapshot state.

Dependencies and integration points: Returned by `OzoneManagerProtocolClientSideTranslatorPB.listSnapshot` and used by clients/CLI to continue listing from `lastSnapshot`.

Risks: Snapshot list is not defensively copied. Null `lastSnapshot` must be interpreted as no continuation marker.

Test signals: Translator tests should cover explicit marker, fallback marker generation when server lacks marker and page is full, and no marker when list is short.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/ListSnapshotResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/SnapshotDiffReportOzone.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/SnapshotDiffReportOzone.java

Purpose: Ozone-specific snapshot diff report extending Hadoop HDFS `SnapshotDiffReport` with volume, bucket, and pagination token metadata.

Important APIs and types: Fields `volumeName`, `bucketName`, `token`; static `Codec<DiffReportEntry>`; getters; `toString`; `toProtobuf`/`fromProtobuf`; diff type and entry conversion helpers; `getDiffReportEntry`; and `aggregate`.

Control flow: Construction delegates core diff data to the HDFS parent class and stores Ozone metadata. Protobuf conversion maps diff type enum names and UTF-8 path bytes. `fromProtobuf` reconstructs the snapshot root as an OFS path for `/volume/bucket`. `toString` renders human-readable entries and optional next token. `aggregate` appends another report's diff entries to the current list for paginated aggregation.

State and persistence behavior: The class claims immutability, but `aggregate` mutates the inherited diff list. The delegated codec serializes individual diff entries for DB or protocol storage. Full report persistence is via protobufs in OM snapshot diff APIs.

Dependencies and integration points: Used by snapshot diff server/client responses, OM translator, CLI report rendering, Ozone/HDFS diff model compatibility, and metadata codecs.

Risks: Enum name alignment with protobuf is required. Path conversion assumes UTF-8 and uses raw byte arrays inherited from HDFS. `aggregate` mutability conflicts with immutable documentation and can surprise shared references. `fromProtobuf` creates a fresh `OzoneConfiguration` for OFS path formatting.

Test signals: Round-trip report and entry protobuf conversions, codec encode/decode, token rendering, aggregate behavior, rename entries with target paths, UTF-8 path handling, and OFS snapshot root formatting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/SnapshotDiffReportOzone.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/SnapshotDiffResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/SnapshotDiffResponse.java

Purpose: Client-facing response wrapper for snapshot diff status and report retrieval.

Important APIs and types: Stores `SnapshotDiffReportOzone`, `JobStatus`, wait time, reason, optional `SubStatus`, progress percentage, and report-only flag. `JobStatus` maps to protobuf job status; `SubStatus` maps to protobuf substatus.

Control flow: Constructors support status with or without reason and report-only semantics. `toString` renders report content for DONE, failure/retry guidance for FAILED/REJECTED/NOT_FOUND, and generic status with optional substatus/progress for active states.

State and persistence behavior: Mutable fields are `subStatus`, `progressPercent`, and `isReportOnly` set through constructors/setters. Persistent job state lives in OM snapshot diff job tables, not this DTO.

Dependencies and integration points: Produced by OM client translator and consumed by CLI/client snapshot diff commands. It wraps `SnapshotDiffReportOzone` and protobuf enum values.

Risks: User-facing strings encode CLI behavior and may be brittle. Progress percentage is appended only for selected substatuses. `snapshotDiffReport` may be null for non-DONE statuses depending on server response assumptions.

Test signals: String rendering for each job status, report-only variants, reason fallback, substatus/progress output, and enum protobuf round-trips.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/SnapshotDiffResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/SubmitSnapshotDiffResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/SubmitSnapshotDiffResponse.java

Purpose: Client-facing response wrapper for submit-snapshot-diff calls.

Important APIs and types: Stores a response string. One constructor formats status-aware guidance from wait time, previous job status, and previous reason; another accepts a server-provided response string.

Control flow: If a previous status exists and is not QUEUED, the formatted constructor mentions it and optional reason. DONE and IN_PROGRESS guide the user to `--get-report`; other statuses state that a new job was submitted and provide retry timing.

State and persistence behavior: In-memory immutable string wrapper. Snapshot diff job state is server-side.

Dependencies and integration points: Returned by the OM client translator for `submitSnapshotDiff` and rendered by CLI code.

Risks: User-facing command guidance is embedded in the DTO and can drift from CLI options. The translator currently uses the raw server response constructor, so the formatting constructor is for server/client compatibility paths.

Test signals: Formatting tests for null/QUEUED/DONE/IN_PROGRESS/FAILED statuses, reason inclusion, wait time rendering, and server response passthrough.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/SubmitSnapshotDiffResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/package-info.java

Purpose: Package documentation for Ozone snapshot-related classes.

Important APIs and types: Documents package `org.apache.hadoop.ozone.snapshot`.

Control flow: No executable logic.

State and persistence behavior: None.

Dependencies and integration points: Applies to snapshot diff/list response DTOs and diff report conversion classes.

Risks: Documentation is broad and minimal.

Test signals: Compile/package-doc generation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/util/OzoneVersionInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/util/OzoneVersionInfo.java

Purpose: Public utility entry point that prints Ozone, protobuf, source, platform, Ratis, and HDDS build/version information.

Important APIs and types: Static `OZONE_VERSION_INFO`, `RATIS_VERSION_INFO`, ASCII `LOGO`, and `main(String[])`. It uses `VersionInfo`, `RatisVersionInfo`, `HddsVersionInfo`, and `ClassUtil`.

Control flow: `main` prints logo/version/release, repository URL and revision, protoc versions, source checksum, Ratis build version, compile platform, logs containing jar at debug level, then delegates to `HddsVersionInfo.main`.

State and persistence behavior: No state mutation or persistence. Reads build metadata from version-info resources/classes.

Dependencies and integration points: Used by command-line version output and diagnostics. Integrates Ozone and HDDS version metadata.

Risks: Output formatting is user-visible and may be asserted by scripts. Missing build metadata resources would produce incomplete version output through `VersionInfo`.

Test signals: CLI/version tests should assert key fields are present and delegation to HDDS version info does not fail.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/util/OzoneVersionInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/util/PayloadUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/util/PayloadUtils.java

Purpose: Utility for generating deterministic-sized payload buffers for RPC/testing/benchmark requests.

Important APIs and types: Static `MAX_SIZE`, random 1024-byte `SEED`, `generatePayload`, `generatePayloadProto2`, and `generatePayloadProto3`.

Control flow: `generatePayload` allocates a byte array capped at `MAX_SIZE`, repeatedly copies the seed into it, asserts the final index, and returns the array. Proto helpers unsafe-wrap the generated array into either protobuf v2 or Ratis-shaded protobuf ByteString.

State and persistence behavior: Static seed is generated once per JVM. No persistence. Returned unsafe-wrapped ByteStrings share the generated array contents.

Dependencies and integration points: Used by echo/RPC payload tools or tests that need bounded payload generation across protobuf variants.

Risks: Negative payload sizes cause `NegativeArraySizeException` because there is no explicit validation. Large sizes allocate up to roughly 2 GiB, which can pressure memory. Unsafe wrapping assumes callers do not mutate arrays after wrapping; here arrays are not exposed except through the wrapper path.

Test signals: Verify exact size for small/zero/max-overflow requests, repeated seed-copy pattern, proto2/proto3 empty behavior, and negative-size failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/util/PayloadUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/util/RadixNode.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/util/RadixNode.java

Purpose: Node wrapper for a slash-delimited prefix radix tree used by Ozone ACL prefix path lookup.

Important APIs and types: Stores node name, child map, and optional generic value. Methods are constructor, `getName`, `hasChildren`, `getChildren`, `setValue`, and `getValue`.

Control flow: Constructor initializes an empty `HashMap`. `hasChildren` currently returns `children.isEmpty()`, so despite its name it is true when the node has no children.

State and persistence behavior: In-memory tree node only; no persistence. Values can hold ACL or other metadata in `RadixTree`.

Dependencies and integration points: Used directly by `RadixTree`.

Risks: `hasChildren` is semantically inverted by name, and `RadixTree` relies on it as "is leaf/has no children". Raw `HashMap<String, RadixNode>` loses generic type safety and can produce unchecked warnings.

Test signals: Node construction, value set/get, child map mutation, and explicit coverage of `hasChildren` behavior to avoid accidental semantic changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/util/RadixNode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/util/RadixTree.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/util/RadixTree.java

Purpose: In-memory radix/prefix tree for Ozone slash-delimited prefix path lookup, used primarily by ACL APIs.

Important APIs and types: Root `RadixNode`, `isEmpty`, `insert`, `getLastNodeInPrefixPath`, `removePrefixPath`, `getLongestPrefixPath`, `radixPathToString`, and `getLongestPrefix`.

Control flow: `insert` normalizes input with `Paths.get`, walks each path component, creates missing child nodes, and optionally stores a value on the terminal node. Exact lookup compares longest-prefix length to path name count plus root. Removal recursively deletes the non-overlapping suffix when a removed node has no children. Longest-prefix methods traverse until a missing component or leaf is hit and return either nodes or a string path.

State and persistence behavior: Pure in-memory tree. No persistence or synchronization. Root is named `/` and may hold a value if extended later.

Dependencies and integration points: Used by ACL prefix matching code to find exact or longest prefix ACL metadata. Uses `OzoneConsts.OZONE_URI_DELIMITER` and Java NIO `Path`.

Risks: Because `RadixNode.hasChildren` is inverted, removal and empty checks are easy to misread. Java `Paths.get` behavior is platform-sensitive for separators and path normalization; Ozone paths assume `/`. Raw node/map types reduce generic safety. No concurrency protection is provided.

Test signals: Insert exact paths, longest-prefix lookup, root-only empty state, removal of leaf and overlapping prefixes, trailing slash rendering, value retrieval, and platform-independent slash behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/util/RadixTree.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/util/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/util/package-info.java

Purpose: Package documentation for Ozone utility classes.

Important APIs and types: Documents package `org.apache.hadoop.ozone.util`.

Control flow: No executable logic.

State and persistence behavior: None.

Dependencies and integration points: Applies to utility classes such as version info, payload generation, and radix tree helpers.

Risks: Documentation is broad and minimal.

Test signals: Compile/package-doc generation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/util/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/web/utils/OzoneUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/web/utils/OzoneUtils.java

Purpose: Common Ozone web/client utility functions for encoding, date formatting/parsing, request IDs, host names, resource-name validation, and time-duration config lookup.

Important APIs and types: Constants `ENCODING` and thread-local `DATE_FORMAT`; methods `verifyMaxKeyLength`, `getRequestID`, `getHostName`, `formatTime`, `formatDate`, `verifyResourceName`, `getTimeDuration`, and `getTimeDurationInMS`.

Control flow: `verifyMaxKeyLength` parses a string as positive integer and throws descriptive `IllegalArgumentException`s. Hostname lookup falls back to `localhost` on `UnknownHostException`. Date formatting/parsing uses a thread-local `SimpleDateFormat` configured with Ozone date format, US locale, and Ozone timezone. Time-duration lookup asks `ConfigurationSource` for the key in the default value's unit, then returns a Ratis `TimeDuration`.

State and persistence behavior: Holds a thread-local formatter; no persistence. Generated request IDs are random UUID strings.

Dependencies and integration points: Used by REST/web utilities and older client paths. Delegates resource-name validation to `HddsClientUtils`, uses `OzoneConsts`, configuration source, and Ratis time duration.

Risks: Error text says "digital" rather than "numeric", which may be user-visible. `verifyMaxKeyLength` takes a string and does not trim before parse. Date parsing is strict only to `SimpleDateFormat` defaults unless configured elsewhere; timezone is fixed by Ozone constants.

Test signals: Valid/invalid max key length, UUID format uniqueness, hostname fallback with mocked DNS failure, date format/parse round-trip in configured timezone, resource-name validation delegation, and duration unit conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/web/utils/OzoneUtils.java -->
