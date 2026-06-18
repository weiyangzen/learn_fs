# subset-b-007513 Research

Grouped source research for WebHDFS JSON/resource utilities and HDFS server-side protobuf contracts. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/JsonUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/JsonUtil.java

## Purpose

`JsonUtil.java` is the WebHDFS JSON serialization utility for turning HDFS protocol objects, filesystem status objects, quota objects, ACL/XAttr objects, snapshots, block locations, checksums, storage policies, server defaults, and exceptions into the response shape expected by WebHDFS and related HTTP clients. The source was read as a complete 800-line file for this report.

## Important APIs, Types, and Functions

The class is a static utility around a shared Jackson `ObjectMapper`. Public entry points include overloaded `toJsonString(...)` methods for `Token`, `Exception`, `HdfsFileStatus`, `DirectoryListing`, `LocatedBlocks`, `ContentSummary`, `QuotaUsage`, `MD5MD5CRC32FileChecksum`, `AclStatus`, XAttr lists, `BlockStoragePolicy`, `FsServerDefaults`, snapshot reports, `SnapshottableDirectoryStatus[]`, `SnapshotStatus[]`, `BlockLocation[]`, `FsStatus`, `ErasureCodingPolicyInfo[]`, and trash-path `Collection<FileStatus>`. Important map helpers include `toJsonMap(HdfsFileStatus)`, `getEcPolicyAsMap(ErasureCodingPolicy)`, datanode/location/block conversion helpers, quota/type-quota conversion, erasure-coding policy conversion, and the visible-for-testing `toJsonMap(BlockLocation)`.

## Control Flow

Each public serializer performs a null check, builds Java `Map`, `Object[]`, or list structures with stable key names, then calls either `toJsonString(String,Object)` or `ObjectMapper.writeValueAsString`. Nested HDFS objects are flattened recursively: located blocks contain block tokens, block metadata, storage types, datanode locations, and cached locations; directory listings wrap arrays under `FileStatuses.FileStatus`; ACL entries are converted to stable strings; XAttrs are encoded according to the requested `XAttrCodec`; snapshot diff reports walk entry lists and convert byte paths to strings. For several older WebHDFS contracts the method wraps data under a top-level class-like key such as `FileStatus`, `LocatedBlocks`, `AclStatus`, or `RemoteException`.

## State and Persistence Behavior

The class owns no durable state. The only long-lived runtime state is the static `ObjectMapper` and the reusable `EMPTY_OBJECT_ARRAY`. All serialized data is derived from caller-supplied in-memory protocol/model objects. It indirectly exposes persisted HDFS state such as inode metadata, quotas, block locations, erasure-coding policy, snapshot data, cache information, and token/checksum bytes, so field names and omitted/null fields are part of the WebHDFS compatibility surface.

## Dependencies and Integration Points

Direct dependencies include Hadoop filesystem classes, HDFS protocol types, ACL/XAttr helpers, datanode/block metadata types, `RemoteException`, token classes, Guava `ImmutableMap`, Jackson `ObjectMapper`, and utility converters such as `DFSUtilClient` and `StringUtils`. The main integration point is WebHDFS/HttpFS response generation and exception handling, especially `ExceptionHandler`, WebHDFS operations returning file status/listing/block/checksum/quota/snapshot data, and clients that parse Hadoop's documented JSON field names.

## Risks and Edge Cases

Compatibility is the primary risk: changing wrapper names, key names, null-versus-empty-array behavior, octal permission formatting, symlink/path encoding, or erasure-coding fields can break clients. Several `writeValueAsString` calls swallow `IOException` and return `null`, so serialization failures can become ambiguous empty responses. The static mapper is safe only because it is configured before use and not mutated in request paths. `ParamFilter` can alter request parameter casing, but this class must preserve response key casing. Large directory listings, block reports, or snapshot diff arrays can allocate large object arrays before serialization.

## Test Signals

Useful tests include golden JSON tests for WebHDFS status/listing/checksum/quota/ACL/XAttr/snapshot responses, null and empty-array behavior tests, erasure-coding policy round-trip checks, exception JSON shape checks through `ExceptionHandler`, and compatibility tests against documented WebHDFS examples. Existing visible test hook `toJsonMap(BlockLocation)` signals direct unit coverage for block location conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/JsonUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/ParamFilter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/ParamFilter.java

## Purpose

`ParamFilter.java` is a servlet filter that makes HTTP request parameter names case-insensitive for WebHDFS by wrapping `HttpServletRequest` and lower-casing every parameter name. The source was read as a complete 96-line file for this report.

## Important APIs, Types, and Functions

The public type is `ParamFilter implements Filter`. The key runtime method is `doFilter(ServletRequest, ServletResponse, FilterChain)`, which wraps only `HttpServletRequest` instances. The private nested `CustomHttpServletRequestWrapper` extends `HttpServletRequestWrapper` and overrides `getParameter`, `getParameterMap`, `getParameterNames`, and `getParameterValues`.

## Control Flow

`init` and `destroy` are no-ops. During `doFilter`, non-HTTP requests pass through unchanged. HTTP requests are wrapped before being passed to the rest of the filter chain. The wrapper snapshots `request.getParameterMap()` in its constructor, inserts each entry under `entry.getKey().toLowerCase()`, then answers all parameter lookups through that lower-case map. `getParameter` delegates to `getParameterValues` and returns the first value.

## State and Persistence Behavior

The filter has no persistent state. Each request wrapper owns a per-request `HashMap<String,String[]>` of lower-cased parameter names to the original value arrays. The map returned to callers is unmodifiable, but the underlying arrays are the original arrays from the servlet container and are not copied.

## Dependencies and Integration Points

It depends on the servlet `Filter` API and `HttpServletRequestWrapper`. It integrates with WebHDFS resource parameter parsing so parameters like `OP`, `op`, and mixed-case names are accepted as the same logical parameter.

## Risks and Edge Cases

If a request contains two parameters whose names differ only by case, the later iteration order from the servlet container overwrites the earlier entry in `lowerCaseParams`; that order is not guaranteed. `String.toLowerCase()` uses the default JVM locale, so unusual locales can theoretically affect ASCII parameter names; using `Locale.ROOT` would be more deterministic. The wrapper lowercases lookup names without null checks, so `getParameterValues(null)` throws `NullPointerException`.

## Test Signals

Tests should cover mixed-case WebHDFS operation parameters, duplicate case-colliding parameters, non-HTTP pass-through behavior, unmodifiable parameter maps, and locale-sensitive lower-casing behavior under a non-English default locale.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/ParamFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/resources/ExceptionHandler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/resources/ExceptionHandler.java

## Purpose

`ExceptionHandler.java` is the Jersey `ExceptionMapper<Exception>` used by WebHDFS resources to translate Java exceptions into HTTP status codes and JSON `RemoteException`-style response bodies. The source was read as a complete 132-line file for this report.

## Important APIs, Types, and Functions

The exported provider is `ExceptionHandler`, annotated with `@Provider`. The main API is `toResponse(Exception)`. The private `toCause(Exception)` peels selected wrapper exceptions while preserving special `SecurityException -> InvalidToken -> StandbyException` behavior. `initResponse(HttpServletResponse)` is visible for testing and injects the servlet response when unit tests do not use Jersey context injection.

## Control Flow

`toResponse` trace-logs the exception, clears the servlet response content type, normalizes Jersey `ParamException` into an `IllegalArgumentException` with the parameter name, unwraps `ContainerException`, `RemoteException`, `SecurityException`, and `MultiException`, then maps the normalized exception to a JAX-RS `Response.Status`. Security and authorization errors become 403, missing files become 404, generic `IOException` becomes 403, unsupported operations and illegal arguments become 400, and unknown exceptions become 500 with a warning log. The response entity is generated by `JsonUtil.toJsonString(e)` and emitted as `application/json`.

## State and Persistence Behavior

The class has no durable state. It relies on Jersey to inject a request-scoped `HttpServletResponse` into the `response` field. The only side effect is clearing the content type on the servlet response before building the final JAX-RS response.

## Dependencies and Integration Points

Dependencies include JAX-RS `ExceptionMapper`, `Response`, and `@Provider`, servlet `HttpServletResponse`, Jersey `ParamException` and `ContainerException`, HK2 `MultiException`, Hadoop `RemoteException`, `StandbyException`, `AuthorizationException`, `InvalidToken`, and `JsonUtil`. It sits on the WebHDFS boundary between resource methods, authentication/authorization layers, NameNode/DataNode RPC failures, and HTTP clients.

## Risks and Edge Cases

Mapping all `IOException` to 403 can hide server-side I/O failures as authorization-like errors. `response.setContentType(null)` assumes the context field is injected; tests must initialize it. The `ParamException` path assumes `e.getCause()` and its message are non-null. Wrapper unwrapping is intentionally conservative for token/standby failures, but changes can affect HA failover semantics and client retry behavior. The log message has a typo, which is harmless but visible.

## Test Signals

Tests should assert status and JSON body for `FileNotFoundException`, `AuthorizationException`, `IOException`, `IllegalArgumentException`, `UnsupportedOperationException`, remote exceptions, Jersey parameter exceptions, and invalid-token standby chains. Test coverage should also verify that unknown exceptions log and return 500 and that the response content type is reset before the JSON response is built.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/resources/ExceptionHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/resources/NamenodeAddressParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/resources/NamenodeAddressParam.java

## Purpose

`NamenodeAddressParam.java` defines the WebHDFS string parameter for a NameNode RPC address, named `namenoderpcaddress`. The source was read as a complete 49-line file for this report.

## Important APIs, Types, and Functions

The class extends `StringParam`. Constants are `NAME = "namenoderpcaddress"` and `DEFAULT = ""`. It owns a `StringParam.Domain` with no regex constraint. Constructors accept either a raw string or a `NameNode`, and `getName()` returns the parameter name.

## Control Flow

The string constructor normalizes null and empty-string defaults to a null value; otherwise it parses the supplied string through the domain. The `NameNode` constructor stores `namenode.getTokenServiceName()`, binding the parameter to the NameNode's advertised token/RPC service. There is no further behavior beyond base `StringParam` conversion.

## State and Persistence Behavior

Instances are immutable parameter objects after construction and do not persist data. They carry a single request/query parameter value used by WebHDFS delegation and redirect flows.

## Dependencies and Integration Points

The class depends on `StringParam` and `org.apache.hadoop.hdfs.server.namenode.NameNode`. It integrates with WebHDFS resource parameter injection and token-service/Namenode address propagation for clients that need to address the correct NameNode RPC endpoint.

## Risks and Edge Cases

The domain does not validate address syntax, so malformed values are accepted until a downstream consumer attempts to use them. Empty string becomes null, which must remain consistent with URL generation and request parsing. The `NameNode` constructor assumes a non-null NameNode with a usable token service name.

## Test Signals

Tests should cover null, empty, and non-empty values; generated parameters from a mock or test NameNode; and WebHDFS URL/query round-trips that include HA or non-default RPC addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/resources/NamenodeAddressParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/resources/TokenKindParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/resources/TokenKindParam.java

## Purpose

`TokenKindParam.java` defines the WebHDFS string parameter named `kind`, used to carry a token kind through HTTP resource calls. The source was read as a complete 42-line file for this report.

## Important APIs, Types, and Functions

The class extends `StringParam`. Constants are `NAME = "kind"` and `DEFAULT = NULL`, where `NULL` comes from the base parameter class. The constructor stores null for absent/default values or the raw string for explicit values. `getName()` returns `kind`.

## Control Flow

Construction is the only logic: if the input is null or equal to the base null sentinel, the parameter value is null; otherwise it is accepted as-is by the unconstrained `StringParam.Domain`. The resource framework later calls the base parameter conversion/accessors.

## State and Persistence Behavior

The object stores one request-scoped token-kind string and has no persistent state. It influences token handling only through request parsing and downstream resource logic.

## Dependencies and Integration Points

It depends on `StringParam` and the WebHDFS resource parameter framework. Integration points are token retrieval, renewal, cancellation, or delegation-token compatibility paths that need to distinguish token kinds.

## Risks and Edge Cases

There is no local validation of supported token kinds. Invalid or unexpected values must be rejected downstream. Compatibility depends on preserving the literal parameter name `kind` and null-sentinel handling.

## Test Signals

Tests should cover null/default inputs, arbitrary non-empty token-kind strings, URL query parsing through Jersey injection, and downstream behavior when unsupported token kinds are supplied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/resources/TokenKindParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/resources/TokenServiceParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/resources/TokenServiceParam.java

## Purpose

`TokenServiceParam.java` defines the WebHDFS string parameter named `service`, used to carry a token service identifier in HTTP requests. The source was read as a complete 42-line file for this report.

## Important APIs, Types, and Functions

The class extends `StringParam`. Constants are `NAME = "service"` and `DEFAULT = NULL`. A static unconstrained `StringParam.Domain` provides base parsing. The constructor normalizes null/default sentinel values to null, and `getName()` returns `service`.

## Control Flow

The constructor accepts any explicit non-default string as the value. No runtime control flow exists beyond base parameter handling by WebHDFS resources.

## State and Persistence Behavior

Instances hold one request-scoped string and do not persist data. The value participates in token service matching and delegation-token handling, but this class does not resolve or authenticate the service itself.

## Dependencies and Integration Points

Dependencies are limited to `StringParam` and the WebHDFS resource parameter framework. It integrates with token request/renew/cancel flows and parameters generated from NameNode service names.

## Risks and Edge Cases

The absence of syntax validation allows malformed service strings to reach later security/token code. Changing the parameter name or null handling would break clients that encode token service in WebHDFS URLs.

## Test Signals

Tests should cover null/default handling, non-empty values, generated URLs with `service`, and token operations against valid and invalid service identifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/resources/TokenServiceParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/resources/UriFsPathParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/resources/UriFsPathParam.java

## Purpose

`UriFsPathParam.java` defines the WebHDFS URI path parameter named `path` and converts Jersey's stripped path value back into an absolute HDFS path. The source was read as a complete 45-line file for this report.

## Important APIs, Types, and Functions

The class extends `StringParam`. It defines `NAME = "path"`, an unconstrained `StringParam.Domain`, a string constructor, `getName()`, and `getAbsolutePath()`.

## Control Flow

The constructor stores the raw URI path fragment through the base parameter class. `getAbsolutePath()` fetches `getValue()` and returns null for null input or prepends `/` because the first slash has been stripped by URI matching.

## State and Persistence Behavior

The class stores a request-scoped path string and does not persist data. Its output controls which HDFS path a WebHDFS operation will target.

## Dependencies and Integration Points

It depends on `StringParam` and integrates with Jersey resource path binding for WebHDFS operations. Downstream integration is broad: file status, open/create, ACL/XAttr, snapshot, content summary, and other path-oriented WebHDFS endpoints consume the absolute path.

## Risks and Edge Cases

The class only prepends a slash and does not normalize dot segments, repeated slashes, encoding, or empty relative path values. It assumes the URI router stripped exactly one leading slash. Path validation and authorization must occur downstream.

## Test Signals

Tests should cover null path, empty path, ordinary nested paths, encoded characters, root-path behavior, and WebHDFS resource methods that use the resulting absolute path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/resources/UriFsPathParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/resources/UserProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/resources/UserProvider.java

## Purpose

`UserProvider.java` is a Jersey provider that supplies the request `UserGroupInformation` for WebHDFS operations. It bridges servlet context/request state into Hadoop authentication logic. The source was read as a complete 53-line file for this report.

## Important APIs, Types, and Functions

The class is annotated with `@Provider` and implements `Supplier<UserGroupInformation>`. Jersey injects `HttpServletRequest` and `ServletContext` with `@Context`. The only public behavior is `get()`.

## Control Flow

`get()` retrieves the Hadoop `Configuration` from the servlet context attribute `JspHelper.CURRENT_CONF`, then calls `JspHelper.getUGI(servletcontext, request, conf, AuthenticationMethod.KERBEROS, false)`. Any `IOException` is wrapped in `SecurityException` with `SecurityUtil.FAILED_TO_GET_UGI_MSG_HEADER`, allowing `ExceptionHandler` to map the failure to a security response.

## State and Persistence Behavior

The provider has no durable state. The injected servlet fields are request/context references managed by Jersey. The returned UGI represents request authentication and proxy-user state, but this class does not cache it.

## Dependencies and Integration Points

Dependencies include servlet context/request, JAX-RS provider/context injection, Hadoop `Configuration`, `JspHelper`, `SecurityUtil`, `UserGroupInformation`, and `AuthenticationMethod.KERBEROS`. It integrates with all WebHDFS resource operations that need a caller identity and with Hadoop's SPNEGO/Kerberos and delegation-token authentication flows.

## Risks and Edge Cases

If the servlet context lacks `JspHelper.CURRENT_CONF`, authentication may fail or behave unexpectedly. Wrapping `IOException` as `SecurityException` intentionally routes failures to security handling, but can hide configuration or network causes. The hard-coded Kerberos authentication method must match the surrounding WebHDFS authentication setup.

## Test Signals

Tests should cover successful UGI extraction, missing or invalid configuration, token/proxy-user requests, IOException wrapping, and integration with `ExceptionHandler` status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/resources/UserProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/AliasMapProtocol.proto -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/AliasMapProtocol.proto

## Purpose

`AliasMapProtocol.proto` defines the protobuf RPC contract for the HDFS alias map, which maps HDFS blocks to provided-storage locations. The source was read as a complete 68-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs`, Java outer class `AliasMapProtocolProtos`, generic services, and imports `hdfs.proto`. Data messages include `KeyValueProto` (`BlockProto` key and `ProvidedStorageLocationProto` value), `WriteRequestProto`, `WriteResponseProto`, `ReadRequestProto`, `ReadResponseProto`, `ListRequestProto`, `ListResponseProto`, `BlockPoolRequestProto`, and `BlockPoolResponseProto`. The service `AliasMapProtocolService` exposes `write`, `read`, `list`, and `getBlockPoolId`.

## Control Flow

The protocol models a simple key/value service. Clients write a block-to-location pair, read by block key, list from an optional marker for pagination, and fetch the block pool ID. `nextMarker` in `ListResponseProto` is the continuation state for list traversal.

## State and Persistence Behavior

The proto itself has no state, but it describes persistent alias map entries used by provided storage. Implementations must persist `BlockProto -> ProvidedStorageLocationProto` mappings consistently with the namespace/block pool they serve.

## Dependencies and Integration Points

It depends on common HDFS block and provided-storage message definitions from `hdfs.proto`. Generated Java is consumed by alias map RPC translators, server implementations, and clients that resolve externally provided block storage locations.

## Risks and Edge Cases

Because this is a stable RPC contract, field numbers and required/optional semantics are compatibility-sensitive. `ReadResponseProto.value` is optional, so callers must distinguish not-found from an empty or missing location. Pagination depends on correct marker ordering and block-pool consistency.

## Test Signals

Tests should cover write/read round trips, not-found reads, list pagination with and without markers, block-pool ID validation, generated protobuf compatibility, and rolling-upgrade behavior when optional fields are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/AliasMapProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/DatanodeLifelineProtocol.proto -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/DatanodeLifelineProtocol.proto

## Purpose

`DatanodeLifelineProtocol.proto` defines the private stable RPC used by DataNodes to send a lightweight lifeline to the NameNode. The source was read as a complete 43-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs.datanodelifeline`, Java outer class `DatanodeLifelineProtocolProtos`, and imports `DatanodeProtocol.proto`. It defines an empty `LifelineResponseProto` and service `DatanodeLifelineProtocolService` with `sendLifeline(hadoop.hdfs.datanode.HeartbeatRequestProto)`.

## Control Flow

The service deliberately reuses `HeartbeatRequestProto` as its request payload but returns an empty response. Unlike a full heartbeat, lifeline responses do not dispatch NameNode commands. The flow lets a DataNode signal liveness and storage/report context without invoking normal command handling.

## State and Persistence Behavior

The proto has no persisted state. Implementations update in-memory NameNode liveness/health tracking based on heartbeat-like data. It indirectly affects failure detection timing but does not journal namespace changes.

## Dependencies and Integration Points

It depends on `DatanodeProtocol.proto` for heartbeat schema. Integration points include DataNode-to-NameNode RPC translators, NameNode heartbeat/lifeline managers, and HA/slow-node monitoring that consumes heartbeat-style metrics.

## Risks and Edge Cases

Compatibility risk is concentrated in the reused heartbeat message: new heartbeat fields may appear in lifeline requests even though no commands are returned. Implementations must not accidentally treat lifeline as a full heartbeat or issue commands on its empty response path.

## Test Signals

Tests should verify that lifelines update liveness, return no commands, tolerate older heartbeat messages without newer optional fields, and do not interfere with normal heartbeat command delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/DatanodeLifelineProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/DatanodeProtocol.proto -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/DatanodeProtocol.proto

## Purpose

`DatanodeProtocol.proto` defines the private stable protobuf RPC contract from DataNodes to the NameNode. It covers registration, heartbeats, block reports, cache reports, incremental block notifications, error reports, bad block reports, version requests, and lease-recovery block synchronization. The source was read as a complete 484-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs.datanode`, Java outer class `DatanodeProtocolProtos`, generic services, and imports `hdfs.proto`, `erasurecoding.proto`, and `HdfsServer.proto`. Major messages include `DatanodeRegistrationProto`, `DatanodeCommandProto` with command-type one-of-style optional fields, `BlockCommandProto`, `BlockIdCommandProto`, `BlockRecoveryCommandProto`, `BlockECReconstructionCommandProto`, registration request/response, `VolumeFailureSummaryProto`, `HeartbeatRequestProto`, `HeartbeatResponseProto`, block report context/report messages, cache report messages, received/deleted block info, error report, bad block report, slow peer/disk reports, and `CommitBlockSynchronizationRequestProto`. The service `DatanodeProtocolService` exposes nine RPCs.

## Control Flow

A DataNode registers with identity, storage info, block keys, and software version. It then sends periodic heartbeats carrying storage reports, transfer counts, cache usage, volume failures, full block report lease requests, slow peer reports, and slow disk reports. The NameNode replies with zero or more typed commands, HA state, rolling-upgrade status, full block report lease ID, and slow-node flag. Separate block report and cache report RPCs send bulk block state. Incremental `blockReceivedAndDeleted` reports communicate newly receiving, received, or deleted blocks. Error and bad block RPCs notify exceptional conditions. `commitBlockSynchronization` finalizes lease recovery with new generation stamp/length and target storage metadata.

## State and Persistence Behavior

The proto defines the wire state that drives NameNode in-memory block maps, datanode descriptors, cache state, liveness, and recovery state. Some received information leads to persistent namespace or block-map effects through NameNode edit logging and metadata updates, but the proto file itself is only a generated-code schema.

## Dependencies and Integration Points

It integrates with NameNode block management, DataNode registration, block-token key distribution, erasure-coding reconstruction commands, storage reports, HA status, rolling upgrades, full block report leasing, and slow-node/disk diagnostics. It shares common server messages from `HdfsServer.proto` and block/storage definitions from `hdfs.proto`.

## Risks and Edge Cases

Required fields make old/new compatibility sensitive; optional defaults preserve rolling-upgrade behavior for fields like `minBlockSize` in related protocols and heartbeat counters here. The command union is not enforced by protobuf, so translators must keep `cmdType` consistent with the matching optional command body. Packed block arrays and block buffers are performance-critical and easy to misinterpret. Typos in field names such as `registartion` and `newTaragets` are part of the generated API and cannot be casually renamed.

## Test Signals

Tests should cover generated translator round trips, DataNode registration and heartbeat command handling, full block report leasing, incremental block reports, cache reports, block synchronization, erasure-coding reconstruction commands, slow peer/disk fields, and protobuf compatibility with missing optional fields during rolling upgrade.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/DatanodeProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/HAZKInfo.proto -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/HAZKInfo.proto

## Purpose

`HAZKInfo.proto` defines the protobuf payload stored or exchanged for NameNode high-availability ZooKeeper failover metadata. The source was read as a complete 36-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs`, Java package `org.apache.hadoop.hdfs.server.namenode.ha.proto`, and outer class `HAZKInfoProtos`. It defines one message, `ActiveNodeInfo`, with required `nameserviceId`, `namenodeId`, `hostname`, `port`, and `zkfcPort`.

## Control Flow

There is no service or executable flow. HA failover code serializes `ActiveNodeInfo` when advertising the active NameNode and deserializes it when fencing, monitoring, or resolving the active node.

## State and Persistence Behavior

This schema represents HA coordination state, commonly backed by ZooKeeper znodes. All fields are required, so missing identity or address data makes the payload invalid to proto2 readers.

## Dependencies and Integration Points

It integrates with HDFS HA, ZooKeeper Failover Controller, and NameNode service discovery/fencing. Generated Java lives under the NameNode HA package rather than the general HDFS protocol package.

## Risks and Edge Cases

Changing field numbers, required fields, or package/outer class names risks breaking persistent ZooKeeper data and rolling upgrades. Hostname/port correctness is critical for fencing the right process. Multi-nameservice clusters depend on both nameservice and namenode IDs being preserved.

## Test Signals

Tests should cover serialization/deserialization of active node records, HA failover with multiple nameservices, stale znode handling, and compatibility with existing persisted active-node data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/HAZKInfo.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/HdfsServer.proto -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/HdfsServer.proto

## Purpose

`HdfsServer.proto` defines shared server-side HDFS protobuf messages used by multiple private stable protocols, including block keys, block locations, edit-log manifests, namespace/storage information, replica recovery state, checkpoint commands, NameNode registration, and HA heartbeat status. The source was read as a complete 219-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs`, Java outer class `HdfsServerProtos`, and imports `hdfs.proto` and `HAServiceProtocol.proto`. Important messages include `BlockKeyProto`, `ExportedBlockKeysProto`, `BlockWithLocationsProto`, `BlocksWithLocationsProto`, `RemoteEditLogProto`, `RemoteEditLogManifestProto`, `NamespaceInfoProto`, `RecoveringBlockProto`, `CheckpointSignatureProto`, `CheckpointCommandProto`, `NamenodeCommandProto`, `VersionRequestProto`, `VersionResponseProto`, `StorageInfoProto`, `NamenodeRegistrationProto`, and `NNHAStatusHeartbeatProto`. It also defines `ReplicaStateProto`.

## Control Flow

This is a shared schema file rather than a service. Other RPC protocols import these messages to exchange version information, edit-log availability, block-token keys, block replica recovery data, checkpoint commands, storage identity, and HA state. For example, DataNode heartbeats return `NNHAStatusHeartbeatProto`, inter-datanode recovery uses `RecoveringBlockProto` and `ReplicaStateProto`, and journal/name-node protocols return `RemoteEditLogManifestProto`.

## State and Persistence Behavior

The messages describe important persistent or semi-persistent cluster state: storage layout version, namespace/cluster IDs, block pool IDs, block-token keys, edit-log segment ranges, checkpoint signatures, and recovery generation stamps. They are wire schemas, but their field layout constrains generated Java and upgrade compatibility.

## Dependencies and Integration Points

Integration points span DataNode protocol, inter-datanode protocol, NameNode protocol, journal protocol, qjournal protocol, checkpointing, block-token security, HA state reporting, rolling upgrade, erasure-coded block recovery, and remote edit-log transfer.

## Risks and Edge Cases

The misspelled `namespceID` field in `StorageInfoProto` is part of the generated API and must not be renamed without compatibility handling. Required fields in storage/namespace messages can break mixed-version nodes if changed. Optional HA state and capabilities fields must be handled when absent. Edit-log range and checkpoint signature correctness is critical to avoid namespace divergence.

## Test Signals

Tests should cover translator round trips for storage/namespace info, exported block keys, remote edit-log manifests, recovery blocks, checkpoint signatures, HA status, and mixed-version decoding when optional fields are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/HdfsServer.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/InterDatanodeProtocol.proto -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/InterDatanodeProtocol.proto

## Purpose

`InterDatanodeProtocol.proto` defines the private stable RPC contract used between DataNodes for block replica recovery. The source was read as a complete 91-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs`, Java outer class `InterDatanodeProtocolProtos`, generic services, and imports `hdfs.proto` and `HdfsServer.proto`. Messages include `InitReplicaRecoveryRequestProto`, `InitReplicaRecoveryResponseProto`, `UpdateReplicaUnderRecoveryRequestProto`, and `UpdateReplicaUnderRecoveryResponseProto`. The service `InterDatanodeProtocolService` exposes `initReplicaRecovery` and `updateReplicaUnderRecovery`.

## Control Flow

During lease/block recovery, a coordinating DataNode asks peers to initialize recovery for a `RecoveringBlockProto`. A peer replies whether a replica exists and, if so, provides its replica state and block metadata. The coordinator can then request an update under recovery with the recovery ID/new generation stamp, new length, and optional new block ID for truncate/copy recovery. The response may include the storage UUID that holds the updated replica.

## State and Persistence Behavior

The schema drives DataNode replica state transitions from write/recovery states to updated finalized or under-recovery metadata. It does not persist by itself, but implementations update on-disk block metadata and replica generation stamps/lengths.

## Dependencies and Integration Points

It integrates with lease recovery, DataNode replica maps, block metadata files, NameNode recovery orchestration, and shared recovery messages from `HdfsServer.proto`.

## Risks and Edge Cases

Recovery correctness depends on matching generation stamps, lengths, optional truncate block IDs, and replica state. Missing optional response fields are valid when no replica is found. Changing required request fields risks recovery protocol incompatibility.

## Test Signals

Tests should cover successful recovery, no-replica responses, generation-stamp updates, truncate/new-block-ID recovery, storage UUID propagation, and mixed-version decoding of optional fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/InterDatanodeProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/InterQJournalProtocol.proto -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/InterQJournalProtocol.proto

## Purpose

`InterQJournalProtocol.proto` defines JournalNode-to-JournalNode or internal qjournal RPCs used to fetch edit-log manifests and storage information. The source was read as a complete 44-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs.qjournal`, Java outer class `InterQJournalProtocolProtos`, generic services, and imports `HdfsServer.proto` and `QJournalProtocol.proto`. It defines `GetStorageInfoRequestProto` with `JournalIdProto jid` and optional `nameServiceId`. The service `InterQJournalProtocolService` exposes `getEditLogManifestFromJournal(GetEditLogManifestRequestProto)` and `getStorageInfo(GetStorageInfoRequestProto)`.

## Control Flow

The service reuses the qjournal manifest request/response schema for manifest retrieval and adds a storage-info lookup. Callers identify a journal and optionally a nameservice, then receive either the manifest of edit-log segments or `StorageInfoProto`.

## State and Persistence Behavior

The proto describes access to JournalNode storage state and edit-log segment metadata. Implementations read local journal storage, but this schema does not itself persist data.

## Dependencies and Integration Points

It depends on qjournal request types and shared HDFS server storage information. It integrates with JournalNode synchronization, recovery, bootstrap, and remote manifest inspection.

## Risks and Edge Cases

Because it imports and reuses `QJournalProtocol.proto` types, compatibility changes in qjournal manifest messages affect this internal protocol too. Optional nameservice IDs must be handled correctly for federated or multi-nameservice journal directories.

## Test Signals

Tests should cover manifest retrieval from a journal, storage info retrieval, absent nameservice IDs, federated journal IDs, and compatibility when optional qjournal fields are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/InterQJournalProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/JournalProtocol.proto -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/JournalProtocol.proto

## Purpose

`JournalProtocol.proto` defines the private stable RPC used by an active NameNode to stream edit-log records to a remote journal receiver, historically a BackupNode, and to fence a journal receiver. The source was read as a complete 130-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs`, Java outer class `JournalProtocolProtos`, generic services, and imports `hdfs.proto` and `HdfsServer.proto`. Messages include `JournalInfoProto`, `JournalRequestProto`, `JournalResponseProto`, `StartLogSegmentRequestProto`, `StartLogSegmentResponseProto`, `FenceRequestProto`, and `FenceResponseProto`. The service `JournalProtocolService` exposes `journal`, `startLogSegment`, and `fence`.

## Control Flow

The active NameNode sends `journal` requests containing journal identity, first transaction ID, transaction count, serialized edit-log bytes, and epoch. It sends `startLogSegment` when rolling to a new edit-log segment. A fencing request supplies journal info, epoch, and optional debug info; the receiver replies with previous epoch, last transaction ID, and whether it is in sync.

## State and Persistence Behavior

The protocol carries serialized edit-log records that are persisted by the receiver. Epoch fields fence stale writers and protect against split-brain edit-log streams. Journal identity ties the stream to cluster/layout/namespace information.

## Dependencies and Integration Points

It integrates with NameNode edit log output streams, BackupNode/checkpointing infrastructure, journal receivers, storage layout information, and failover fencing. It shares storage and edit-log manifest types through `HdfsServer.proto`.

## Risks and Edge Cases

Incorrect epoch handling can allow stale writes. `records` is opaque serialized edit-log data, so sender and receiver must agree on edit-log layout. Optional fields in `JournalInfoProto` and `FenceResponseProto` require careful default handling. Transaction ID and count mismatches can corrupt or reject journal streams.

## Test Signals

Tests should cover streaming edits, starting new log segments, fencing stale writers, transaction count validation, epoch monotonicity, receiver restart recovery, and mixed-version behavior for optional journal info fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/JournalProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/NamenodeProtocol.proto -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/NamenodeProtocol.proto

## Purpose

`NamenodeProtocol.proto` defines the private stable RPC contract used by subordinate NameNodes, checkpointing nodes, balancers, and related internal clients to communicate with the active/primary NameNode. The source was read as a complete 327-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs.namenode`, Java outer class `NamenodeProtocolProtos`, generic services, and imports `hdfs.proto` and `HdfsServer.proto`. Messages cover block selection (`GetBlocksRequestProto`, `GetBlocksResponseProto`), block-token keys, transaction IDs, edit-log rolling, checkpoint transaction IDs, NameNode-file transaction IDs, error reports, subordinate NameNode registration, checkpoint start/end, edit-log manifests, upgrade state, rolling-upgrade state, file path lookup, and Storage Policy Satisfier path retrieval. `NamenodeProtocolService` exposes RPCs for those operations.

## Control Flow

Clients request blocks for balancing or movement, fetch block keys, query the latest edit-log/checkpoint transaction IDs, roll edit logs for checkpointing, get version information, report subordinate errors, register subordinate NameNodes, begin and end checkpoints using checkpoint signatures, fetch edit-log manifests since a transaction ID, query upgrade/rolling-upgrade state, and fetch the next SPS path. Some messages, such as `GetFilePathRequestProto`, are defined without a corresponding service method in this file segment, which may indicate use by translators elsewhere or legacy/dead schema.

## State and Persistence Behavior

The protocol observes and drives NameNode metadata state: block maps, block-token keys, edit-log transaction IDs, checkpoint signatures, upgrade flags, and SPS queues. Checkpoint and edit-log operations affect persistent namespace recovery material through NameNode implementation code.

## Dependencies and Integration Points

It integrates with balancer/block movement, block-token secret management, checkpointing, BackupNode/secondary NameNode workflows, edit-log rolling, storage upgrade/rolling-upgrade logic, and SPS. It imports shared server structures from `HdfsServer.proto`.

## Risks and Edge Cases

Defaults such as `minBlockSize = 10485760` in `GetBlocksRequestProto` are explicitly for rolling upgrades and should not be changed casually. Required checkpoint/edit-log fields must match NameNode persistent state exactly. Missing optional SPS path means no path is available, not necessarily an error. Unused or unmatched messages need caution because generated APIs may still be consumed elsewhere.

## Test Signals

Tests should cover balancer get-block requests with defaults and optional filters, block-key retrieval, transaction/checkpoint ID queries, edit-log rolling, checkpoint start/end signatures, manifest retrieval, upgrade/rolling-upgrade flags, SPS path behavior, and mixed-version request decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/NamenodeProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/QJournalProtocol.proto -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/QJournalProtocol.proto

## Purpose

`QJournalProtocol.proto` defines the private stable quorum journal protocol used by NameNodes and JournalNodes for high-availability edit-log storage. It covers journal identity, epochs, formatting, upgrade/rollback, writing edits, segment lifecycle, manifest retrieval, tailing journaled edits, and Paxos-style recovery. The source was read as a complete 390-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs.qjournal`, Java outer class `QJournalProtocolProtos`, generic services, and imports `hdfs.proto` and `HdfsServer.proto`. Important messages include `JournalIdProto`, `RequestInfoProto`, `SegmentStateProto`, `PersistedRecoveryPaxosData`, journal/heartbeat/start/finalize/purge messages, format and upgrade messages, rollback messages, journal state and epoch messages, edit-log manifest and journaled-edits messages, and `PrepareRecovery`/`AcceptRecovery` messages. `QJournalProtocolService` exposes operations from `isFormatted` through `acceptRecovery`.

## Control Flow

The qjournal lifecycle starts with format or storage inspection, then `newEpoch` establishes a writer epoch. A NameNode sends `journal` requests with request info, first transaction ID, transaction count, serialized records, and segment transaction ID. It starts and finalizes log segments, purges old logs, heartbeats to maintain writer state, queries manifests, tails journaled edits, and uses `prepareRecovery`/`acceptRecovery` to converge on a valid segment after failures. Upgrade, finalize, rollback, and discard RPCs manage JournalNode storage across software/layout changes.

## State and Persistence Behavior

This schema is persistence-critical. `PersistedRecoveryPaxosData` is explicitly the on-disk format for accepted recovery decisions. JournalNodes persist edit-log records, segment state, epochs/promises, storage info, and recovery metadata. `RequestInfoProto` carries epoch and IPC serial number to reject stale or replayed writers, and optionally carries committed transaction ID and nameservice ID.

## Dependencies and Integration Points

It integrates with QuorumJournalManager, JournalNode storage, NameNode edit log writing/tailing, HA failover, edit-log segment recovery, shared `RemoteEditLogManifestProto`, and storage upgrade logic. It is also imported by `InterQJournalProtocol.proto`.

## Risks and Edge Cases

Epoch, IPC serial number, and committed transaction ID semantics are central to split-brain protection. Required fields in recovery and segment messages must remain compatible. Deprecated `httpPort` fields are still required in some responses, so translators must populate them even when `fromURL` is preferred. Nameservice ID spelling differs between `nameServiceId` and `nameserviceId` in one rollback request, which is generated API surface. Recovery acceptance depends on fetching logs from `fromURL` safely.

## Test Signals

Tests should cover epoch fencing, journal writes and segment finalization, manifest and tail retrieval, purge/discard behavior, format/upgrade/rollback/finalize flows, prepare/accept recovery, persisted Paxos data compatibility, deprecated `httpPort`/`fromURL` behavior, and federated nameservice IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/QJournalProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/editlog.proto -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/editlog.proto

## Purpose

`editlog.proto` defines protobuf payloads used for ACL and XAttr edit-log operations in HDFS. The source was read as a complete 35-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs`, Java outer class `EditLogProtos`, and imports `acl.proto` and `xattr.proto`. It defines `AclEditLogProto` with required `src` and repeated `AclEntryProto entries`, and `XAttrEditLogProto` with optional `src` and repeated `XAttrProto xAttrs`.

## Control Flow

There is no RPC service. NameNode edit-log code serializes these messages when recording ACL or XAttr changes and deserializes them during edit-log replay.

## State and Persistence Behavior

This file defines persistent edit-log record payloads. The `src` path and repeated ACL/XAttr entries are replayed to reconstruct namespace metadata. Compatibility of field numbers and message semantics is critical for reading existing edit logs.

## Dependencies and Integration Points

It depends on shared ACL and XAttr protobuf schemas. It integrates with NameNode edit logging, FSImage/edit-log replay, ACL commands, XAttr commands, and namespace recovery.

## Risks and Edge Cases

`AclEditLogProto.src` is required while `XAttrEditLogProto.src` is optional, so replay logic must handle absent XAttr paths according to the operation type. Repeated entries may be empty for operations that clear metadata. Any field renumbering or type change would break edit-log compatibility.

## Test Signals

Tests should cover ACL and XAttr edit-log write/read round trips, replay after restart, empty entry lists, absent optional XAttr source handling, and compatibility with edit logs generated by older versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/editlog.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/fsimage.proto -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/fsimage.proto

## Purpose

`fsimage.proto` defines the protobuf on-disk layout for HDFS filesystem image files. It describes the file summary, namesystem metadata, inode records, under-construction files, directory children, inode references, snapshots and snapshot diffs, string table, delegation-token secret manager state, cache manager state, and erasure-coding policy state. The source was read as a complete 353-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs.fsimage`, Java outer class `FsImageProto`, and imports `hdfs.proto`, `acl.proto`, and `xattr.proto`. Top-level messages include `FileSummary`, `NameSystemSection`, `INodeSection`, `FilesUnderConstructionSection`, `INodeDirectorySection`, `INodeReferenceSection`, `SnapshotSection`, `SnapshotDiffSection`, `StringTableSection`, `SecretManagerSection`, `CacheManagerSection`, and `ErasureCodingSection`. Nested inode messages model files, directories, symlinks, ACL features, compact XAttrs, quotas by storage type, under-construction features, references, snapshots, and diffs.

## Control Flow

The file comment defines the FSImage grammar: magic header, repeated sections, file summary, and trailing summary length. Sections contain delimited protobuf messages, and large/repeated entities are streamed within section boundaries rather than always held in one top-level message. Loaders read the summary/index, seek to sections, then decode each section according to its declared name. Savers write sections and finish with `FileSummary`.

## State and Persistence Behavior

This schema is the persistent HDFS namespace image format. It stores namespace IDs, generation stamps, block IDs, transaction ID, rolling upgrade time, inode IDs, inode type-specific metadata, block lists, ACL/XAttr compact encodings, quotas, directory child relationships, references for snapshots, snapshot metadata/diffs, string interning table, delegation keys/tokens, cache directives/pools, and erasure-coding policies. The file uses compact fixed-width encodings for permissions, ACL entries, and XAttr names to keep images small and tied to the string table.

## Dependencies and Integration Points

It integrates with NameNode FSImage save/load code, edit-log replay, namespace recovery, snapshot subsystem, ACL/XAttr features, delegation token secret manager, cache manager, erasure coding, and the string table. It depends on common block/storage, ACL, and XAttr protobuf definitions.

## Risks and Edge Cases

This is a durable on-disk compatibility contract. Field number changes, required/optional changes, compact bit-layout mistakes, section-name changes, or summary/index corruption can make a namespace image unreadable. Large directory entries must stay within protobuf message size limits, noted explicitly for `DirEntry`. Snapshot diff sections combine fixed metadata with variable repeated records, so section-boundary parsing must match writer counts. Permission/ACL/XAttr compact encodings depend on exact bit allocation and string table IDs.

## Test Signals

Tests should cover FSImage save/load round trips across files, directories, symlinks, ACLs, XAttrs, snapshots, under-construction files, quotas, cache directives, delegation tokens, erasure coding, and rolling upgrades. Compatibility tests should load older FSImage files, validate section indexes and compression codecs, exercise large directories near message-size limits, and compare namespace checksums before and after save/load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/fsimage.proto -->
