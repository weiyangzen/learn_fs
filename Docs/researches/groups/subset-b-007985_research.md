# subset-b-007985 research

Grouped research for the HDDS common Java files assigned to subset `subset-b-007985`. Each section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/Pipeline.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/Pipeline.java

## Purpose
`Pipeline` models the ordered set of datanodes used to store or read a container, together with replication configuration, pipeline lifecycle state, leader identity, optional suggested leader, creation time, state-entry time, replica indexes, and topology-based node order. SCM pipeline managers, container allocation, clients, and datanode protocol calls use it as the core transfer object for placement and routing.

## Important APIs and types
- `getCodec()` exposes a DB codec backed by `HddsProtos.Pipeline`. The codec intentionally does not round-trip equality because the delegated deserializer resets the creation timestamp to `Instant.now()`.
- Accessors expose `PipelineID`, `ReplicationType`, `ReplicationConfig`, `PipelineState`, datanode set/list, ordered read list, leader node, suggested leader, replica index map, and timestamps.
- `getFirstNode`, `getClosestNode`, and `getLeaderNode` choose datanodes for RPC routing. `getClosestNode` prefers `nodesInOrder` when present and falls back to insertion order.
- `copyForRead` converts non-standalone pipelines into standalone read pipelines while preserving factor where possible. `copyForReadFromNode` narrows a pipeline to one datanode and carries its EC replica index.
- `getProtobufMessage` and `toBuilder(HddsProtos.Pipeline)` preserve legacy and newer protobuf fields: string leader IDs, 128-bit UUIDs, `DatanodeID` proto, EC replication config, legacy factor, member replica indexes, and compact member order indexes.
- `Builder` constructs immutable-ish instances, regenerates pipeline ID when nodes change, reconstructs node order from protobuf member order indexes, and validates required fields.
- `PipelineState` maps between Java states `ALLOCATED`, `OPEN`, `DORMANT`, `CLOSED` and protobuf lifecycle values.

## Control flow and state
Most object fields are final and copied into immutable Guava collections, but `leaderId`, `creationTimestamp`, and `nodeStatus` values are mutable through package-visible or public methods. `reportDatanode` updates per-node last-report timestamps and accepts reports from a restarted datanode with matching node values even if the exact object key differs. `isHealthy` treats EC pipelines as healthy by definition, while non-EC pipelines require all nodes to have reported and a leader to be known.

Serialization builds member and replica-index lists in map iteration order and optionally serializes `nodesInOrder` as indexes into the member list. Deserialization rebuilds the member map first, then applies member-order indexes if present. Equality uses only ID, replication config, and node set, while hash code includes the `nodeStatus` map, which is risky because report timestamps can change after construction.

## Dependencies and integration points
The class integrates with `DatanodeDetails`, `DatanodeID`, replication config classes, SCM database codecs, protobufs, client-version-aware port filtering, Jackson JSON annotations, and Ratis preconditions. It is consumed by container protocol clients for datanode selection, by SCM pipeline management for lifecycle transitions, and by DB persistence.

## Risks and test signals
Tests should cover protobuf compatibility across leader ID encodings, EC replica index preservation, node-order round trips, empty/all-excluded node selection errors, ID regeneration on node changes, and health behavior for EC versus Ratis/standalone. The mutable `nodeStatus` versus hash-code behavior is a regression risk if `Pipeline` is used as a hash-map key after reports arrive. The codec timestamp reset is intentional and should be asserted rather than treated as a serialization bug.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/Pipeline.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineID.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineID.java

## Purpose
`PipelineID` is the immutable UUID-backed identifier for an SCM pipeline. It supplies conversion helpers for strings, UUIDs, database codecs, and protobuf transport.

## Important APIs and types
`randomId`, `valueOf(UUID)`, and `valueOf(String)` create IDs. `getCodec()` delegates to `UuidCodec` for DB persistence. `getProtobuf()` memoizes a protobuf containing both the legacy string ID and the newer 128-bit UUID form. `getFromProtobuf` prefers `uuid128` and falls back to string `id`.

## Control flow and state
The only state is the final UUID plus a memoized protobuf supplier. Equality and hash code are UUID-only. No persistence side effects occur in this class.

## Dependencies and integration points
It integrates with `HddsProtos.PipelineID`, HDDS DB codec APIs, Jackson's `JsonIgnore`, and Ratis `MemoizedSupplier`. `Pipeline` and pipeline manager code use it as the stable key.

## Risks and test signals
Tests should verify UUID/string/protobuf round trips and legacy protobuf fallback. A protobuf missing both `uuid128` and `id` throws `IllegalArgumentException`, so compatibility tests should keep that failure explicit.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineID.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineNotFoundException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineNotFoundException.java

## Purpose
Signals that a requested pipeline is missing from `PipelineManager`.

## Important APIs and types
It extends `SCMException` and always uses `ResultCodes.PIPELINE_NOT_FOUND`. Constructors support a default message-less exception and a message-bearing exception.

## Control flow and state
There is no mutable state beyond the superclass exception fields. The class exists to preserve typed catch sites and consistent SCM result coding.

## Dependencies and integration points
Pipeline manager and SCM client code can throw or catch this type while still using SCM's common result-code taxonomy.

## Risks and test signals
Tests should assert the result code when callers map SCM exceptions to protocol or client errors. Behavior is otherwise trivial.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineNotFoundException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/package-info.java

## Purpose
Package documentation for SCM pipeline support. It states that Ozone supports multiple pipeline kinds, such as Ratis and simple/standalone replication, and that pipeline managers live under this package.

## Important APIs and types
No executable APIs are declared. The package contains pipeline entities and managers; in this subset the important behavioral types are `Pipeline`, `PipelineID`, and `PipelineNotFoundException`.

## Control flow, state, and persistence
There is no runtime control flow or state.

## Dependencies and integration points
The package description frames integration between SCM, replication protocols, datanodes, and pipeline managers.

## Risks and test signals
No direct tests are needed for this file. Documentation should be updated if pipeline kinds or package ownership change.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/ContainerCommandResponseBuilders.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/ContainerCommandResponseBuilders.java

## Purpose
Centralizes construction of datanode container protocol responses. It keeps command type, trace ID, result code, and command-specific payloads consistent across server-side handlers and tests.

## Important APIs and types
- Generic helpers: `getContainerCommandResponse`, `getSuccessResponseBuilder`, `getSuccessResponse`, `malformedRequest`, and `unsupportedRequest`.
- Block and chunk helpers: `putBlockResponseSuccess`, `getBlockDataResponse`, `getListBlockResponse`, `getBlockLengthResponse`, `getCommittedBlockLengthResponseBuilder`, `getWriteChunkResponseSuccess`, `getReadChunkResponse`, `getReadBlockResponse`, and `getFinalizeBlockResponse`.
- Small-file helpers: `getPutFileResponseSuccess` and `getGetSmallFileResponseSuccess`.
- Container helpers: `getReadContainerResponse` and `getGetContainerMerkleTreeResponse`.
- `getEchoResponse` optionally sleeps, then returns random payload bytes of the requested response size.

## Control flow and state
The class is stateless and non-instantiable. Most methods copy `cmdType` and `traceID` from the request and set `Result.SUCCESS`. Read-chunk and get-small-file responses branch on `ClientCommandsUtils.getReadChunkVersion`: V0 concatenates buffers into a single `data` field; V1 returns `DataBuffers` with a list of buffers. Echo converts request payload-size units directly into the generated byte count used by `RandomUtils.secure().randomBytes`.

## Dependencies and integration points
It depends on `ContainerProtos`, checksum data, `ChunkBufferToByteString`, protobuf `ByteString` and unsafe wrapping, and the shared client read-version utility. Datanode command handlers use it to format responses consumed by `ContainerProtocolCalls`.

## Risks and test signals
Tests should cover trace propagation, success/error result mapping, V0 versus V1 read response shapes, committed-block-length embedding, null `BlockData` in write-chunk responses, and echo sleep/interruption behavior. The V0 concatenation path can allocate large buffers; V1 should be preferred for segmented data. `InterruptedException` in echo is wrapped in `RuntimeException` without restoring interrupt status.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/ContainerCommandResponseBuilders.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/OzonePBHelper.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/OzonePBHelper.java

## Purpose
Small protobuf conversion helper for token-related messages and low-allocation `ByteString` creation.

## Important APIs and types
`getFixedByteString(Text)` caches `Text` to UTF-8 `ByteString` for fixed, small string domains such as token kind. `getByteString(byte[])` returns `ByteString.EMPTY` for empty arrays. `tokenFromProto` and `protoFromToken` convert between Hadoop `Token<T>` and `HddsProtos.TokenProto`.

## Control flow and state
The only state is a static `ConcurrentHashMap` cache without eviction. Token conversion copies identifier/password bytes and preserves kind/service values.

## Dependencies and integration points
Used by protobuf-facing container token code. It depends on Hadoop `Token`, `TokenIdentifier`, `Text`, and unshaded protobuf `ByteString` to avoid Hadoop protobuf shading issues.

## Risks and test signals
Because the fixed-string cache is unbounded, callers should use it only for small finite domains. Tests should verify token round trips, empty byte handling, and service/kind byte encoding compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/OzonePBHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/package-info.java

## Purpose
Documents the package as containing client-side classes for the storage container protocol.

## Important APIs and types
No executable APIs are defined here. In this subset, `ContainerCommandResponseBuilders` and `OzonePBHelper` are the concrete protocol helper classes.

## Control flow, state, and persistence
There is no runtime behavior or persistence.

## Dependencies and integration points
The package sits at the boundary between SCM/client code and protobuf container protocol messages.

## Risks and test signals
No direct test requirements. Documentation should stay aligned with package contents if server-side-only helpers are added.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/storage/BlockLocationInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/storage/BlockLocationInfo.java

## Purpose
Represents one block location for a key segment: block ID, pipeline, length, offset, security token, creation version, multipart part number, and under-construction marker.

## Important APIs and types
The builder sets `BlockID`, `Pipeline`, length, offset, token, part number, and create version. Accessors expose container/local IDs and block commit sequence ID through `BlockID`. Mutators allow updating length, token, pipeline, part number, create version, and under-construction status.

## Control flow and state
This is a mutable value object. `hasSameBlockAs` compares block identity plus length, offset, and create version while ignoring token and pipeline. `equals` includes token and pipeline but omits part number and under-construction, so equality does not fully reflect all mutable fields.

## Dependencies and integration points
It connects key/block metadata to SCM pipelines and `OzoneBlockTokenIdentifier` Hadoop tokens. Client read/write paths use it to route block operations and carry auth material.

## Risks and test signals
Tests should cover equality semantics, `hasSameBlockAs`, mutable length/token/pipeline updates, and behavior when part number or under-construction changes are intentionally ignored. Mutable fields make it risky as a hash-map key.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/storage/BlockLocationInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/storage/ContainerProtocolCalls.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/storage/ContainerProtocolCalls.java

## Purpose
Static client-side facade for datanode container protocol RPCs. It builds `ContainerCommandRequestProto` messages, attaches tokens and trace IDs, chooses datanodes from a `Pipeline`, sends sync or async commands through `XceiverClientSpi`, and validates responses.

## Important APIs and types
- Read/list APIs: `listBlock`, `getBlock`, `getCommittedBlockLength`, `readChunk`, `readContainer`, `readSmallFile`, `getContainerChecksumInfo`, `getBlockFromAllNodes`, `readContainerFromAllNodes`, and `buildReadBlockCommandProto`.
- Write/modify APIs: `putBlockAsync`, `finalizeBlock`, `getPutBlockRequest`, `writeChunkAsync`, `writeSmallFile`, `createRecoveringContainer`, `createContainer`, `deleteContainer`, and `closeContainer`.
- Routing helpers: `tryEachDatanode`, `getDatanodeBlockID`, and error-message helpers.
- Validation helpers: `validateContainerResponse`, `toValidatorList`, and the default validator list.

## Control flow and state
The class is stateless with a static immutable default validator list. Most methods build command-specific request payloads, attach encoded block/container tokens when provided, optionally attach `TracingUtil.exportCurrentSpan()`, and call `sendCommand` or `sendCommandAsync`.

`tryEachDatanode` repeatedly selects the closest non-excluded datanode, runs the operation, and retries another datanode on `IOException`. It does not retry when the result is `BLOCK_TOKEN_VERIFICATION_FAILED`, because another datanode cannot fix an expired or invalid token. It records tracing events for failed datanode attempts.

Read paths differ by command. `getBlock` and `readChunk` retry across pipeline nodes and apply EC replica indexes to `DatanodeBlockID`. `readChunk` verifies the returned data length, supporting both legacy `data` and V1 `dataBuffers`. Several metadata-style calls use `getFirstNode` or `getClosestNode` without retry.

Write paths usually target the first pipeline node, relying on the underlying client/pipeline replication semantics. `writeSmallFile` builds a synthetic chunk with CRC32 checksum and overwrite metadata. Container create/delete/close/read APIs propagate trace ID and tokens and rely on validators for error conversion.

## Dependencies and integration points
The class integrates `XceiverClientSpi`, `XceiverClientReply`, `Pipeline`, `DatanodeDetails`, `BlockID`, `ContainerProtos`, checksum utilities, Hadoop tokens, OpenTelemetry spans, and SCM storage exceptions. It is the client counterpart to datanode command handlers that use `ContainerCommandResponseBuilders`.

## Risks and test signals
Tests should exercise request shape for every command type, token inclusion, trace propagation, EC replica-index handling, retry/exclusion logic, no-retry token failure, read length validation, V0/V1 data length calculation, all-node command response maps, and validator exception mapping. Watch for builder reuse in retry loops, commands that do not retry across nodes, and async write behavior when the first node is unavailable. `validateContainerResponse` maps only selected result codes to specialized exceptions; all others become generic `StorageContainerException`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/storage/ContainerProtocolCalls.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/storage/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/storage/package-info.java

## Purpose
Documents the package as containing StorageContainerManager storage classes.

## Important APIs and types
No executable API is declared here. In this subset, `BlockLocationInfo` and `ContainerProtocolCalls` are the relevant storage/client helpers.

## Control flow, state, and persistence
There is no runtime behavior.

## Dependencies and integration points
The package groups SCM storage metadata and datanode container protocol client helpers.

## Risks and test signals
No direct tests are needed. Package documentation is broad and should be refined if package ownership changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/storage/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/utils/ClientCommandsUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/utils/ClientCommandsUtils.java

## Purpose
Utility for interpreting optional read-chunk-version fields on container protocol requests.

## Important APIs and types
Two overloads of `getReadChunkVersion` accept `ReadChunkRequestProto` and `GetSmallFileRequestProto`. Both return the explicitly set version or default to `ReadChunkVersion.V0`.

## Control flow and state
The class is stateless and non-instantiable. Its only branch preserves backward compatibility for requests created before the read-chunk-version field existed.

## Dependencies and integration points
Used by response builders and datanode/client read paths to decide whether to return single-buffer V0 data or V1 data buffers.

## Risks and test signals
Tests should verify absent-field fallback and explicit V1 handling for both request types. Changing the default would break old clients.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/utils/ClientCommandsUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/utils/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/utils/package-info.java

## Purpose
Documents the package as utility classes for SCM and client protocols.

## Important APIs and types
No executable API. In this subset, `ClientCommandsUtils` is the concrete package utility.

## Control flow, state, and persistence
There is no runtime behavior.

## Dependencies and integration points
The package is shared by SCM and client protocol code.

## Risks and test signals
No direct tests are required for this file.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/utils/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/SecurityConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/SecurityConfig.java

## Purpose
Central typed view of HDDS/Ozone security configuration. It resolves key algorithms and providers, metadata/key/certificate locations, X.509 durations, block/container token settings, TLS options, external root CA paths, CA rotation settings, certificate polling intervals, and authorization enablement.

## Important APIs and types
Construction reads from `ConfigurationSource` and validates cross-field constraints. `initSecurityProvider` lazily loads the configured provider, dynamically adding Bouncy Castle for `"BC"` when needed. Accessors expose security flags, token flags and expiry, certificate durations, key/certificate paths, key codec creation, TLS provider/protocols/ciphers, external CA paths, CA rotation times/intervals, test-cert mode, and authorization mode.

## Control flow and state
The constructor computes immutable instance fields from config keys. It falls back from HDDS metadata dir to Ozone metadata dirs. Authorization is enabled only when Ozone security or test authorization is enabled and the authorization key is true. TLS test-cert mode is only considered when gRPC TLS is enabled. `validateCertificateValidityConfig` rejects zero/negative durations, default duration greater than max duration, renewal grace greater than default duration, invalid CA rotation intervals/timeouts when rotation is enabled, and block token lifetime exceeding renewal grace when token sanity checks are enabled.

The static security provider field is volatile and initialized under a synchronized method, so provider loading is process-global. `getGrpcTlsProtocols` returns a defensive array copy; cipher list is unmodifiable or null.

## Dependencies and integration points
The class pulls constants from `HddsConfigKeys` and `OzoneConfigKeys`, uses Netty/Ratis `SslProvider`, Java security providers, Bouncy Castle, `KeyCodec`, and `OzoneConsts`. Certificate clients, key storage/generation, token managers, gRPC services, and CA rotation managers depend on it.

## Risks and test signals
Tests should cover invalid duration combinations, CA rotation validation, provider lookup and Bouncy Castle registration, metadata dir fallback, authorization test mode, TLS protocol/cipher parsing, external root CA detection, null metadata directory failures in path getters, and token sanity checks. Since provider initialization is static, tests must isolate or reset provider assumptions carefully.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/SecurityConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/SecurityConstants.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/SecurityConstants.java

## Purpose
Defines RFC-7468 PEM boundary labels and pre/post encapsulation strings for public and private keys.

## Important APIs and types
Constants include `PEM_ENCAPSULATION_BOUNDARY_LABEL_PUBLIC_KEY`, `PEM_ENCAPSULATION_BOUNDARY_LABEL_PRIVATE_KEY`, and their full `-----BEGIN ...-----` / `-----END ...-----` forms.

## Control flow and state
There is no mutable state or control flow. The private constructor prevents instantiation.

## Dependencies and integration points
`KeyCodec` uses the labels when encoding PEM key objects. Other security code can use the full boundary strings for validation or parsing.

## Risks and test signals
Tests should only be needed where consumers depend on exact PEM labels. Changing these strings breaks compatibility with existing key files.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/SecurityConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/exception/OzoneSecurityException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/exception/OzoneSecurityException.java

## Purpose
Ozone-layer security exception carrying a domain result code.

## Important APIs and types
Constructors cover result-only, message/result, message/cause/result, and cause/result. `getResult()` returns `ResultCodes`, currently covering OM key-file absence, missing S3 secret, and secret-manager HMAC errors.

## Control flow and state
The exception is immutable after construction except for inherited throwable state.

## Dependencies and integration points
Callers can catch it as `IOException` while inspecting Ozone-specific result codes for protocol mapping or retries.

## Risks and test signals
Tests should assert result-code preservation in all constructors and mapping layers. Result-only construction has no detail message.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/exception/OzoneSecurityException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/exception/SCMSecretKeyException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/exception/SCMSecretKeyException.java

## Purpose
Exception for SCM secret key subsystem failures.

## Important APIs and types
The constructor accepts a message and `ErrorCode`. Codes include `OK`, `INTERNAL_ERROR`, `SECRET_KEY_NOT_ENABLED`, and `SECRET_KEY_NOT_INITIALIZED`.

## Control flow and state
It extends `IOException` and stores a final error code.

## Dependencies and integration points
Secret key managers and token/signature paths can use the error code to distinguish disabled, uninitialized, and internal states.

## Risks and test signals
Tests should verify code propagation and that callers distinguish disabled from uninitialized rather than treating all IO failures as transient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/exception/SCMSecretKeyException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/exception/SCMSecurityException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/exception/SCMSecurityException.java

## Purpose
Root `IOException` subtype for SCM security and certificate-related failures.

## Important APIs and types
Constructors support message, message/error code, message/cause, message/cause/error code, cause/error code, and cause-only. `ErrorCode` covers CSR errors, certificate issuance/fetch failures, PEM encoding, missing or failed block tokens, root CA fetch failures, and non-primary SCM errors.

## Control flow and state
The final error code defaults to `DEFAULT` unless explicitly supplied.

## Dependencies and integration points
Certificate utilities, token verification, SCM security APIs, and protocol mappers use this as the common checked exception.

## Risks and test signals
Tests should assert code preservation and defaulting behavior. Mapping code should not lose specific codes such as `BLOCK_TOKEN_VERIFICATION_FAILED`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/exception/SCMSecurityException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/exception/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/exception/package-info.java

## Purpose
Documents the package as containing exceptions thrown by SCM security classes.

## Important APIs and types
No executable APIs. The package includes `OzoneSecurityException`, `SCMSecretKeyException`, and `SCMSecurityException`.

## Control flow, state, and persistence
There is no runtime behavior.

## Dependencies and integration points
The package provides typed checked exceptions for SCM security, secret-key, token, and certificate layers.

## Risks and test signals
No direct tests required for this file.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/exception/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/package-info.java

## Purpose
Documents the package as containing HDDS security-related classes.

## Important APIs and types
No executable APIs. In this subset the package-level concrete classes are `SecurityConfig` and `SecurityConstants`.

## Control flow, state, and persistence
There is no runtime behavior.

## Dependencies and integration points
This package anchors configuration, constants, token, exception, and X.509 subpackages used across HDDS components.

## Risks and test signals
No direct tests required.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/token/OzoneBlockTokenIdentifier.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/token/OzoneBlockTokenIdentifier.java

## Purpose
Hadoop token identifier for short-lived HDDS block access tokens. It binds an owner, service/block ID, access modes, expiry, secret key ID, and maximum allowed length into a protobuf-serialized token payload.

## Important APIs and types
`KIND_NAME` is `HDDS_BLOCK_TOKEN`. Constructors accept owner, `BlockID` or block service string, access-mode set, expiry millis, and max length. `getTokenService(BlockID)` derives token service from the container block ID. Accessors expose service, expiry millis, access modes, max length, and kind. Serialization APIs are `readFields`, `readFromByteArray`, `readFieldsProtobuf`, `write`, and `getBytes`.

## Control flow and state
The default constructor supports Hadoop deserialization. `readFields` requires a mark-supported `DataInputStream`, parses `BlockTokenSecretProto`, and populates inherited owner/expiry/secret-key fields plus block ID, modes, and max length. `getBytes` writes the same fields back to protobuf. Null modes become an empty `EnumSet`.

## Dependencies and integration points
It extends `ShortLivedTokenIdentifier`, uses `HddsProtos.BlockTokenSecretProto`, `AccessModeProto`, `BlockID`, Hadoop `Text`, and `ProtobufUtils` for UUID conversion. `OzoneBlockTokenSelector`, `BlockLocationInfo`, and container protocol calls carry or select tokens of this kind.

## Risks and test signals
Tests should cover protobuf round trips, empty access-mode handling, owner fallback through inherited `getUser`, secret-key ID preservation, equality/hash code, and invalid input streams. `EnumSet.copyOf(token.getModesList())` fails for an empty list, so deserialization tests should verify expected behavior for tokens without modes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/token/OzoneBlockTokenIdentifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/token/OzoneBlockTokenSelector.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/token/OzoneBlockTokenSelector.java

## Purpose
Selects an HDDS block token matching a requested Hadoop token service.

## Important APIs and types
Implements `TokenSelector<OzoneBlockTokenIdentifier>`. `selectToken(Text service, Collection<Token<? extends TokenIdentifier>> tokens)` returns the first token whose kind is `HDDS_BLOCK_TOKEN` and service equals the requested service.

## Control flow and state
The selector is stateless. It returns null for null service or no match. It performs an unchecked cast after matching token kind.

## Dependencies and integration points
Used by Hadoop security token lookup paths for block operations. It depends on `OzoneBlockTokenIdentifier.KIND_NAME`, Hadoop `Token`, `Text`, and `TokenSelector`.

## Risks and test signals
Tests should cover null service, empty token collections, kind mismatch, service mismatch, first-match behavior, and successful typed return.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/token/OzoneBlockTokenSelector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/token/ShortLivedTokenIdentifier.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/token/ShortLivedTokenIdentifier.java

## Purpose
Abstract base class for short-lived HDDS token identifiers, shared by block and similar token types.

## Important APIs and types
Subclasses must implement `getService()` and `readFromByteArray(byte[])`. The base stores owner ID, expiry `Instant`, and secret key UUID. `getUser()` returns a remote user for owner ID, or the token service when owner is empty. `isExpired(Instant)` checks expiry against a supplied time.

## Control flow and state
Fields are mutable through protected setters and public `setSecretKeyId`, allowing deserializers to populate default-constructed tokens. Equality and hash code include owner, expiry, and secret-key ID.

## Dependencies and integration points
It extends Hadoop `TokenIdentifier` and returns Hadoop `UserGroupInformation`. Concrete identifiers integrate with token managers and protocol serialization.

## Risks and test signals
Tests should cover owner-present and owner-empty user derivation, expiry boundary behavior, equality, and deserialization setter paths. Null expiry would cause `isExpired` to throw, so callers should only check fully initialized tokens.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/token/ShortLivedTokenIdentifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/token/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/token/package-info.java

## Purpose
Documents the package as containing block-token-related classes, though the text says "test classes" despite production token classes living here.

## Important APIs and types
No executable APIs. The package includes `ShortLivedTokenIdentifier`, `OzoneBlockTokenIdentifier`, and `OzoneBlockTokenSelector`.

## Control flow, state, and persistence
There is no runtime behavior.

## Dependencies and integration points
The package supports HDDS block token authentication for client-to-datanode operations.

## Risks and test signals
No direct tests. The package comment may be misleading and should be corrected if documentation cleanup is in scope.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/token/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/CAType.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/CAType.java

## Purpose
Enumerates certificate authority types and their certificate filename prefixes.

## Important APIs and types
Values are `NONE("")`, `SUBORDINATE("CA-")`, and `ROOT("ROOTCA-")`. `getFileNamePrefix()` returns the prefix.

## Control flow and state
Enum state is immutable.

## Dependencies and integration points
Certificate authority and certificate lifecycle code can use it to name CA certificate files consistently.

## Risks and test signals
Tests should assert exact prefixes if file naming compatibility matters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/CAType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/package-info.java

## Purpose
Documents the package as containing certificate lifecycle and certificate authority server classes.

## Important APIs and types
No executable APIs. In this subset, `CAType` is the concrete authority-related type.

## Control flow, state, and persistence
No runtime behavior.

## Dependencies and integration points
The package belongs to the HDDS X.509 identity and CA management subsystem.

## Risks and test signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/CACertificateProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/CACertificateProvider.java

## Purpose
Functional interface for supplying trusted CA certificates.

## Important APIs and types
`provideCACerts()` returns a `List<X509Certificate>` and can throw `IOException`.

## Control flow and state
No implementation state exists. Implementations decide whether certificates come from disk, SCM, memory, or another service.

## Dependencies and integration points
Certificate clients and TLS/trust-store setup code can depend on this interface without knowing certificate source details.

## Risks and test signals
Tests for consumers should cover provider IO failure, empty certificate lists, and multiple CA certificates. Implementations should document ordering expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/CACertificateProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/package-info.java

## Purpose
Documents the package as classes for creating and using certificates.

## Important APIs and types
No executable APIs. This subset includes the `CACertificateProvider` trust-anchor interface.

## Control flow, state, and persistence
No runtime behavior.

## Dependencies and integration points
The package is part of HDDS certificate client and trust management.

## Risks and test signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/utils/CertificateCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/utils/CertificateCodec.java

## Purpose
Reads and writes X.509 certificates and certificate paths in PEM format for HDDS components.

## Important APIs and types
Static helpers encode `X509Certificate` or `CertPath` to PEM, parse a leading certificate from PEM bytes/string, parse full `CertPath`, return the first cert from a path, and obtain a Bouncy Castle X.509 `CertificateFactory`. Instance methods resolve a certificate location from `SecurityConfig`, write certificates using configured or explicit filenames, read certificate paths, prepend certificates to paths, and read target certificates.

## Control flow and state
Each instance stores `SecurityConfig`, a location path, and owner-only POSIX permissions. Writes create the base directory if missing, write UTF-8 PEM data, log the path and PEM string, and set owner read/write/execute permissions on the certificate file. Reads verify the base directory, require the named file to exist, and parse it as a PEM certificate path.

## Dependencies and integration points
Depends on Bouncy Castle `JcaPEMWriter` and provider `"BC"`, Java certificate APIs, `SecurityConfig`, and `SCMSecurityException`. Certificate clients, CA servers, and key/cert bootstrap code use it for PEM persistence.

## Risks and test signals
Tests should cover single-certificate and chain PEM parsing, prepend order, missing file errors, directory creation failure, permission setting on POSIX filesystems, behavior without Bouncy Castle provider, and error-code mapping for PEM encode failure. Logging full PEM certificates may be acceptable for public certs but should be reviewed for operational verbosity.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/utils/CertificateCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/utils/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/utils/package-info.java

## Purpose
Documents the package as certificate helper utilities.

## Important APIs and types
No executable APIs. `CertificateCodec` is the concrete helper in this subset.

## Control flow, state, and persistence
No runtime behavior.

## Dependencies and integration points
The package supports certificate encoding, decoding, and persistence for HDDS X.509 workflows.

## Risks and test signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/utils/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/exception/CertificateException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/exception/CertificateException.java

## Purpose
SCM security exception subtype for X.509 certificate client/server failures.

## Important APIs and types
Constructors accept message, cause, message/cause, message/error code, and message/cause/error code. `errorCode()` returns a certificate-specific `ErrorCode` such as keystore, crypto signing, CSR, bootstrap, renew, rollback, or signature verification errors.

## Control flow and state
It extends `SCMSecurityException` but stores its own mutable-looking package-private `errorCode` field rather than using the superclass error-code taxonomy.

## Dependencies and integration points
Certificate client, CA, CSR, and rotation code can throw this type for X.509-specific failure handling.

## Risks and test signals
Tests should verify certificate-specific code propagation. Callers must use `errorCode()` rather than `getErrorCode()` from `SCMSecurityException` if they need the certificate-specific enum.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/exception/CertificateException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/exception/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/exception/package-info.java

## Purpose
Documents the package as containing exceptions thrown by X.509 security classes.

## Important APIs and types
No executable APIs. `CertificateException` is the concrete exception in this subset.

## Control flow, state, and persistence
No runtime behavior.

## Dependencies and integration points
The package supports certificate, CSR, key store, and rotation error reporting.

## Risks and test signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/exception/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/keys/HDDSKeyGenerator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/keys/HDDSKeyGenerator.java

## Purpose
Generates Java `KeyPair` instances for HDDS certificates using security configuration defaults or caller-specified size/algorithm/provider.

## Important APIs and types
`generateKey()` uses configured size, key algorithm, and provider. `generateKey(int)` overrides size only. `generateKey(int, String, String)` calls `KeyPairGenerator.getInstance(algorithm, provider)`, initializes with the requested size, and generates the pair.

## Control flow and state
Instances hold a `SecurityConfig`. No keys are persisted here; generation is in-memory only.

## Dependencies and integration points
Depends on Java security APIs and `SecurityConfig`. Generated pairs are typically persisted by `KeyStorage` and used by certificate bootstrap/CSR code.

## Risks and test signals
Tests should cover configured defaults, unsupported algorithm/provider exceptions, non-default key sizes, and provider initialization via `SecurityConfig`. There is no explicit `SecureRandom` override, so provider defaults apply.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/keys/HDDSKeyGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/keys/KeyCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/keys/KeyCodec.java

## Purpose
Encodes and decodes public/private keys in PEM format using RFC-7468-compatible ASCII text and Java key factories.

## Important APIs and types
The constructor creates a `KeyFactory` for the configured algorithm. `encodePublicKey` and `encodePrivateKey` wrap key bytes in Bouncy Castle `PemObject`s with `PUBLIC KEY` or `PRIVATE KEY` labels. `decodePrivateKey` and `decodePublicKey` parse a PEM object and generate Java key instances.

## Control flow and state
The only state is the `KeyFactory`. Encoding writes ASCII PEM through `PemWriter`. Decoding reads one PEM object, wraps content in `PKCS8EncodedKeySpec`, and applies a generator function. Public key decoding adapts the content into an `X509EncodedKeySpec` for `generatePublic`.

## Dependencies and integration points
Uses `SecurityConstants` PEM labels, Bouncy Castle PEM reader/writer, Java key specs, and Ratis `CheckedFunction`. `SecurityConfig.keyCodec()` and `KeyStorage` use it for key persistence.

## Risks and test signals
Tests should cover private/public round trips for configured algorithms, invalid PEM, mismatched algorithm, empty input, and compatibility with existing key files. The decode helper assumes `readPemObject()` returns non-null and that public-key content can be represented from the PKCS8 wrapper; malformed inputs can produce null dereferences or `IOException`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/keys/KeyCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/keys/KeyStorage.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/keys/KeyStorage.java

## Purpose
Persists and reads component key pairs in PEM format with strict POSIX permissions, while also supporting externally supplied root CA keys.

## Important APIs and types
Constructors resolve key paths from `SecurityConfig` and component name, optional suffix, or an internal path. `readPrivateKey`, `readPublicKey`, and `readKeyPair` decode existing PEM files. `storePrivateKey`, `storePublicKey`, and `storeKeyPair` encode and write keys. Permission constants are `rwx------` for directories and `rw-------` for key files.

## Control flow and state
During construction, if `SecurityConfig.useExternalCACertificate(component)` is true, paths are taken from external root CA config and must be readable; store operations later throw `UnsupportedOperationException`. Otherwise the key directory is created or sanitized to owner-only permissions, and key file paths are resolved from configured names. Store creates a new file with owner-only permissions then writes encoded bytes.

## Dependencies and integration points
Depends on `SecurityConfig`, `KeyCodec`, Java NIO files, POSIX file permissions, and Java key classes. Certificate clients, root CA setup, and rotation managers use it for local and staged key material.

## Risks and test signals
Tests should cover new directory creation, existing directory permission reset, read/write round trips, external key read paths, unreadable external path failures, store rejection for external keys, and behavior when target files already exist. Because `Files.createFile` fails if the file exists, overwrite/rotation behavior must be explicitly handled by callers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/keys/KeyStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/keys/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/keys/package-info.java

## Purpose
Documents the package as utilities for private and public keys.

## Important APIs and types
No executable APIs. In this subset, `HDDSKeyGenerator`, `KeyCodec`, and `KeyStorage` provide generation, PEM conversion, and persistence.

## Control flow, state, and persistence
No runtime behavior in the package file.

## Dependencies and integration points
The package supports HDDS X.509 key lifecycle, storage, and rotation.

## Risks and test signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/keys/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/package-info.java

## Purpose
Documents the package as common routines for creating an X.509-based identity framework for HDDS.

## Important APIs and types
No executable APIs. Subpackages in this subset cover certificate authority metadata, certificate clients, certificate utilities, exceptions, and key utilities.

## Control flow, state, and persistence
No runtime behavior.

## Dependencies and integration points
This package is the root for HDDS certificate identity, trust, key, and CA workflows.

## Risks and test signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/server/JsonUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/server/JsonUtils.java

## Purpose
Shared Jackson JSON utility for HDDS/Ozone server code, including pretty printing, streaming sequence IO, tree creation, file read/write, and checksum serialization.

## Important APIs and types
`toJsonStringWithDefaultPrettyPrinter`, `toJsonString`, and `toJsonStringWIthIndent` serialize objects. `getSequenceWriter` writes JSON arrays to an output stream and closes it; `getStdoutSequenceWriter` avoids closing `System.out`. `createArrayNode`, `createObjectNode`, `readTree`, `readFromReader`, `getDefaultMapper`, `writeToFile`, and `readFromFile` expose Jackson operations. `ChecksumSerializer` serializes long checksums through `HddsUtils.checksumToString`.

## Control flow and state
Static mappers are initialized once, omit nulls, register `JavaTimeModule`, and write Java time values as ISO strings rather than timestamps. `toJsonStringWIthIndent` catches `JsonProcessingException`, logs, and returns `{}`. `NonClosingOutputStream` delegates writes/flushes but ignores close.

## Dependencies and integration points
Depends on Jackson core/databind/JSR310, `HddsUtils`, and SLF4J. CLI, admin, web, and persistence helpers can use it for consistent JSON formatting.

## Risks and test signals
Tests should cover Java time serialization, null omission, sequence writer close behavior, stdout non-close behavior, file streaming round trips, checksum string formatting, and the typo-preserved method name `toJsonStringWIthIndent`. Returning `{}` on serialization errors can mask failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/server/JsonUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/server/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/server/package-info.java

## Purpose
Documents the package as server utility classes.

## Important APIs and types
No executable APIs. `JsonUtils` is the concrete server utility in this subset.

## Control flow, state, and persistence
No runtime behavior.

## Dependencies and integration points
The package groups helpers shared by HDDS server components.

## Risks and test signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/server/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/GrpcClientInterceptor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/GrpcClientInterceptor.java

## Purpose
gRPC client interceptor that propagates the current tracing context in outbound metadata.

## Important APIs and types
Defines metadata key `TRACING_HEADER` named `"Tracing"`. `interceptCall` wraps the client call and merges a metadata entry containing `TracingUtil.exportCurrentSpan()` before starting the call.

## Control flow and state
The interceptor is stateless. It sends an empty string when no valid span exists because `exportCurrentSpan` returns the null-span sentinel.

## Dependencies and integration points
Uses shaded Ratis gRPC APIs and `TracingUtil`. It pairs with `GrpcServerInterceptor`, which reads the same header.

## Risks and test signals
Tests should verify header insertion with valid and invalid current spans, merge behavior with existing metadata, and compatibility with the server interceptor. Header name changes break propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/GrpcClientInterceptor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/GrpcServerInterceptor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/GrpcServerInterceptor.java

## Purpose
gRPC server interceptor that imports a propagated tracing context and creates an active span for message handling.

## Important APIs and types
`interceptCall` wraps the server listener. `onMessage` calls `TracingUtil.importAndCreateSpan` with the full method name and the client tracing header, makes the span current while delegating to the real listener, and ends the span.

## Control flow and state
The interceptor is stateless. It creates one span per received message rather than per call lifecycle event.

## Dependencies and integration points
Pairs with `GrpcClientInterceptor` and uses OpenTelemetry `Span`/`Scope` plus shaded Ratis gRPC server APIs.

## Risks and test signals
Tests should cover propagated and absent headers, span closure when delegate throws, and multi-message RPC behavior. Exceptions from `super.onMessage` still end the span because of `finally`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/GrpcServerInterceptor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/LoopSampler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/LoopSampler.java

## Purpose
Independent probability sampler for named spans.

## Important APIs and types
Constructor accepts a ratio, rejects negative values, and caps values above one. `shouldSample()` returns false for zero, true for one, and otherwise compares a `ThreadLocalRandom` double to the probability.

## Control flow and state
Instances are immutable after construction.

## Dependencies and integration points
Used by `SpanSampler` for per-span sampling overrides parsed from tracing config.

## Risks and test signals
Tests should cover negative rejection, zero, one, values above one, and probabilistic behavior with enough sampling tolerance.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/LoopSampler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/SkipTracing.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/SkipTracing.java

## Purpose
Runtime method annotation marking methods that should not be traced by proxy-based tracing.

## Important APIs and types
The annotation targets methods and is retained at runtime.

## Control flow and state
No runtime behavior by itself. `TraceAllMethod` inspects it on delegate methods.

## Dependencies and integration points
Used with `TracingUtil.createProxy` and `TraceAllMethod`.

## Risks and test signals
Tests should ensure annotations on implementation methods are honored by the proxy. Interface-method annotations alone may not be enough because `TraceAllMethod` scans delegate class methods.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/SkipTracing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/SpanSampler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/SpanSampler.java

## Purpose
OpenTelemetry sampler that combines root trace sampling with per-span sampling overrides for child spans.

## Important APIs and types
Constructor accepts a root `Sampler` and map of span names to `LoopSampler`. `shouldSample` delegates root spans to the root sampler, drops children of unsampled parents, applies a matching per-span sampler when present, and otherwise records sampled children. `getDescription` lists configured span names.

## Control flow and state
The sampler is immutable but uses the provided map reference. Parent sampling controls child eligibility before per-span sampling is considered, preventing orphaned sampled spans.

## Dependencies and integration points
Built by `TracingUtil.initialize` when `TracingConfig` supplies per-span sampling config. It uses OpenTelemetry SDK sampling APIs.

## Risks and test signals
Tests should cover root-span delegation, unsampled parent drop, sampled parent with explicit span rate zero/one, default child sampling, and description content. Span-name matching is exact.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/SpanSampler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/TraceAllMethod.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/TraceAllMethod.java

## Purpose
Java dynamic-proxy invocation handler that traces calls to all delegate methods except methods annotated with `SkipTracing`.

## Important APIs and types
The constructor scans public delegate methods, skips `Object` methods, records parameter-type signatures, and marks methods with `SkipTracing`. `invoke` finds the matching delegate method, optionally creates a span named `<interfaceName>.<methodName>`, invokes the delegate, and unwraps reflection causes.

## Control flow and state
The handler caches a nested map from method name to parameter types to `(shouldSkip, Method)`. Skipped methods invoke directly. Non-skipped methods run inside `TracingUtil.createActivatedSpan`, which ends the span on close. A missing method produces `NoSuchMethodException`.

## Dependencies and integration points
Created by `TracingUtil.createProxy` when tracing is enabled. It depends on reflection, Apache Commons `Pair`, and `SkipTracing`.

## Risks and test signals
Tests should cover overloaded methods, exception unwrapping, skip annotation behavior, missing method failure, and Object method behavior. Parameter-type arrays are used as map keys but searched by array equality, so direct map lookup is intentionally avoided.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/TraceAllMethod.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/TracingConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/TracingConfig.java

## Purpose
Reconfigurable OpenTelemetry tracing configuration object for Ozone services.

## Important APIs and types
Config fields define enablement, OTLP endpoint, root trace sampler ratio, and per-span sampling string under the `ozone.tracing` group. `validate()` applies environment fallbacks and defaults. Getters expose final values.

## Control flow and state
`validate` fills an empty endpoint from `OTEL_EXPORTER_OTLP_ENDPOINT`, defaulting to `http://localhost:4317`. If sampler ratio is negative, it tries `OTEL_TRACES_SAMPLER_ARG`; invalid or out-of-range values become `1.0`. Empty span sampling can be filled from `OTEL_SPAN_SAMPLING_ARG`.

## Dependencies and integration points
Consumed by `TracingUtil.initTracing` and `isTracingEnabled`. It uses HDDS config annotations and `ReconfigurableConfig` to support runtime updates.

## Risks and test signals
Tests should cover config value priority, environment fallback, invalid env parsing, out-of-range sampler clamping, blank endpoint defaulting, and reconfigurable metadata. Defaulting invalid sampler ratios to `1.0` can unexpectedly increase tracing volume.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/TracingConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/TracingUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/TracingUtil.java

## Purpose
Central OpenTelemetry utility for initializing tracing, exporting/importing span context, proxy tracing, span execution helpers, and HTTP/gRPC header extraction helpers.

## Important APIs and types
Initialization APIs are `initTracing`, `reconfigureTracing`, and internal `initialize`/`shutdownTracing`. Context propagation APIs are `exportCurrentSpan`, `importAndCreateSpan`, `TextExtractor`, and `HttpHeaderGetter`. Execution APIs are `executeInNewSpan`, `executeAsChildSpan`, `createActivatedSpan`, `createActivatedSpanFromW3cHttpHeaders`, and `getActiveSpan`. `createProxy` wraps interfaces with `TraceAllMethod` when tracing is enabled.

## Control flow and state
Static state tracks initialization, current `Tracer`, and `SdkTracerProvider`. Initialization is synchronized and no-ops when disabled or already initialized. It creates an OTLP gRPC exporter, simple span processor, service-name resource, and either a trace-ratio sampler or `SpanSampler` with parsed per-span settings. Reconfigure shuts down the old provider first.

`exportCurrentSpan` returns an empty string when no valid span exists, otherwise injects W3C trace context into a semicolon-separated `key=value;` carrier. `importAndCreateSpan` starts a root span for null/empty carriers or extracts a parent context using `TextExtractor`. Execution helpers mark spans error on exceptions and always end spans. HTTP header activation uses W3C HTTP headers and returns a no-op closeable when config is null or disabled.

## Dependencies and integration points
Depends on OpenTelemetry API/SDK/exporter, HDDS configuration, Ratis checked functional interfaces, dynamic proxies, and tracing config/sampler classes. Used by container protocol calls, gRPC interceptors, and service implementations.

## Risks and test signals
Tests should cover idempotent initialization, disabled tracing no-op behavior, reconfiguration shutdown, exporter construction failure cleanup, context export/import, malformed carrier parsing, span sampling config parsing, exception status marking, no-op HTTP activation, and proxy creation. `TextExtractor` caches parsed carrier data in an instance, so it should not be reused across different carriers. Simple span processing exports synchronously and may affect latency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/TracingUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/package-info.java

## Purpose
Documents the package as helper classes for distributed tracing in Ozone components.

## Important APIs and types
No executable APIs. The package includes gRPC interceptors, sampling helpers, proxy tracing, tracing config, and `TracingUtil`.

## Control flow, state, and persistence
No runtime behavior in this file.

## Dependencies and integration points
The package integrates Ozone/HDDS services with OpenTelemetry context propagation and exporting.

## Risks and test signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/upgrade/BelongsToHDDSLayoutVersion.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/upgrade/BelongsToHDDSLayoutVersion.java

## Purpose
Runtime annotation marking a class or field as belonging to a specific HDDS layout feature.

## Important APIs and types
The annotation targets types and fields, is retained at runtime, and has one value of type `HDDSLayoutFeature`.

## Control flow and state
No behavior by itself. Upgrade and layout introspection code can read it via reflection.

## Dependencies and integration points
Used with `HDDSLayoutFeature` to bind code or schema elements to layout versions.

## Risks and test signals
Tests should verify consumers discover the annotation on both classes and fields. Renaming enum values would affect source annotations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/upgrade/BelongsToHDDSLayoutVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/upgrade/HDDSLayoutFeature.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/upgrade/HDDSLayoutFeature.java

## Purpose
Enumerates HDDS layout features and versions used by upgrade/finalization logic.

## Important APIs and types
Enum values define layout versions from `INITIAL_VERSION` through `STORAGE_SPACE_DISTRIBUTION`. It implements Ozone `LayoutFeature`, exposing `layoutVersion()` and `description()`. Optional SCM and datanode upgrade actions can be registered with `addScmAction` and `addDatanodeAction`, and retrieved with `scmAction()`/`datanodeAction()`.

## Control flow and state
Each enum value stores layout version, description, and at most one SCM and datanode action. Add methods only set the action when the current field is null, preserving first registration.

## Dependencies and integration points
Used by HDDS upgrade framework, datanode/SCM layout version managers, and `BelongsToHDDSLayoutVersion` annotations.

## Risks and test signals
Tests should assert monotonic layout version ordering, descriptions, action first-wins behavior, and optional absence/presence. Enum fields are mutable, so parallel tests registering actions must avoid cross-test contamination.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/upgrade/HDDSLayoutFeature.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/upgrade/HDDSUpgradeAction.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/upgrade/HDDSUpgradeAction.java

## Purpose
Marker interface for HDDS SCM and datanode upgrade actions.

## Important APIs and types
It extends `LayoutFeature.UpgradeAction<T>` and adds no methods.

## Control flow and state
No implementation behavior.

## Dependencies and integration points
`HDDSLayoutFeature` stores optional actions of this type. Concrete upgrade actions implement it to plug into the shared Ozone upgrade framework.

## Risks and test signals
No direct tests beyond ensuring concrete actions satisfy the inherited `UpgradeAction` contract.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/upgrade/HDDSUpgradeAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/upgrade/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/upgrade/package-info.java

## Purpose
Documents the package as containing SCM upgrade-related classes.

## Important APIs and types
No executable APIs. This subset contains layout feature annotations, feature enum, and upgrade action marker interface.

## Control flow, state, and persistence
No runtime behavior in the package file.

## Dependencies and integration points
The package integrates HDDS with the Ozone layout upgrade framework.

## Risks and test signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/upgrade/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/Cache.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/Cache.java

## Purpose
Minimal generic cache abstraction.

## Important APIs and types
Methods are `get`, `put`, `remove`, `removeIf`, and `clear`. `put` can throw `InterruptedException`.

## Control flow and state
No implementation state; behavior is defined by implementers.

## Dependencies and integration points
Shared utility interface for components needing cache implementations with predicate-based removal.

## Risks and test signals
Consumer tests should verify implementation-specific concurrency, interruption, removal, and clear semantics. The interface does not specify null handling or eviction behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/Cache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/CompositeKey.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/CompositeKey.java

## Purpose
Efficient composite map key that avoids allocating concatenated string keys for multiple key components.

## Important APIs and types
`combineKeys(Object[] components)` returns the sole component directly for length one, otherwise creates a `CompositeKey`. Equality and hash code are based on `Arrays.equals` and `Arrays.hashCode` of the component array.

## Control flow and state
The constructor stores the component array reference and precomputes hash code. There is no defensive copy.

## Dependencies and integration points
Used wherever volume/bucket/key or similar multi-part keys need hash-map lookup without string concatenation.

## Risks and test signals
Tests should cover one-component passthrough, multi-component equality, hash code consistency, null components, and mutation of the input array or mutable component objects. Because no copy is made, callers must not mutate the array after construction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/CompositeKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/GlobPattern.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/GlobPattern.java

## Purpose
POSIX-style glob pattern compiler with brace expansion, using shaded-compatible `com.google.re2j.Pattern`.

## Important APIs and types
Constructor and `set` compile a glob string. `compile` is a static shortcut. `matches` tests a candidate string. `compiled` exposes the RE2/J pattern. `hasWildcard` reports whether glob wildcard constructs were seen.

## Control flow and state
`set` translates glob syntax into regex: `*` and `?` become dot-based wildcards, braces become non-capturing groups with commas as alternation, character classes are tracked, selected regex metacharacters are escaped, and `[!` becomes `[^`. It rejects missing escaped characters, unclosed character classes, and unclosed groups. The compiled regex uses `Pattern.DOTALL`.

## Dependencies and integration points
Copied from Hadoop to avoid shaded/non-shaded RE2/J signature mismatch. Used by utilities needing glob matching without Java regex backtracking risk.

## Risks and test signals
Tests should cover literal escaping, star/question semantics, brace alternatives, nested or unclosed braces, character classes, negated classes, trailing backslash, wildcard detection, and invalid pattern exceptions. The `*` translation appends `.` before the original `*`, producing regex `.*`; this is intentional through fall-through.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/GlobPattern.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/HddsVersionInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/HddsVersionInfo.java

## Purpose
Command-line and programmatic access to HDDS build/version metadata.

## Important APIs and types
Static `HDDS_VERSION_INFO` is a `VersionInfo("hdds")`. `main` prints version, source URL/revision, protoc versions, source checksum, compile platform, and debug containing jar.

## Control flow and state
No mutable state. Output is written to `System.out`; containing jar is logged only at debug level.

## Dependencies and integration points
Uses HDDS annotations for public/stable API, Hadoop `ClassUtil`, SLF4J, and the local `VersionInfo` class.

## Risks and test signals
Tests can assert output contains expected fields when build metadata resources are present. CLI output format may be consumed by scripts, so changes should be deliberate.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/HddsVersionInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/IOUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/IOUtils.java

## Purpose
Static IO and closeable helpers for cleanup, quiet/error logging close operations, atomic properties persistence, file inode lookup, and chunk-size rounding.

## Important APIs and types
`cleanupWithLogger` catches `Throwable` and logs debug for exception-handler cleanup. `close` logs `Exception` at error level. `closeQuietly` delegates with no logger. `writePropertiesToFile` uses `AtomicFileOutputStream`. `readPropertiesFromFile` loads Java properties. `getINode` returns `BasicFileAttributes.fileKey()`. `roundUp` rounds a required size to a chunk multiple and asserts bounds.

## Control flow and state
All methods are stateless. Close helpers tolerate null collections and null elements. `writePropertiesToFile` truncates via atomic-file semantics provided by Ratis. `roundUp` computes `(requiredSize - 1) / chunkSize`, so zero or invalid chunk sizes require caller discipline.

## Dependencies and integration points
Depends on Java IO/NIO, Jakarta `Nonnull`, Ratis `AtomicFileOutputStream` and `Preconditions`, and SLF4J `Logger`.

## Risks and test signals
Tests should cover close exception logging behavior, null handling, atomic property round trips, inode availability differences by filesystem, and `roundUp` boundaries including exact multiples. `cleanupWithLogger` catches `Throwable`, so use only in cleanup paths as documented.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/IOUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/LeakDetector.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/LeakDetector.java

## Purpose
General resource leak detector using weak references and a reference queue to report resources that are garbage-collected before their tracker is closed.

## Important APIs and types
The constructor names and starts a daemon detector thread. `track(Object leakable, Runnable reportLeak)` creates a `LeakTracker`, stores it in a concurrent set, and returns it as an `UncheckedAutoCloseable` for resource close paths.

## Control flow and state
Each detector owns a daemon thread blocking on `ReferenceQueue.remove()`. When a tracked referent is GCed, the detector removes its tracker from the active set; if it was still present, it invokes the leak reporter. Closing the tracker removes it from the set and suppresses reporting.

## Dependencies and integration points
Uses `LeakTracker`, Java reference APIs, concurrent sets, atomic naming, Ratis `UncheckedAutoCloseable`, and SLF4J. Resource classes can keep the returned tracker and close it during cleanup.

## Risks and test signals
Tests should cover leak reporting after GC, no report after close, detector thread naming/daemon status, and interruption behavior. Leak reporter must not capture the original resource, or it may prevent GC and defeat detection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/LeakDetector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/LeakTracker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/LeakTracker.java

## Purpose
Weak-reference token used by `LeakDetector` to track whether a resource was closed before garbage collection.

## Important APIs and types
It extends `WeakReference<Object>` and implements `UncheckedAutoCloseable`. `close()` removes the tracker from the active leak set. `reportLeak()` runs the supplied leak reporter.

## Control flow and state
The tracker keeps references to the shared active set and reporter, but only a weak reference to the resource. It is package-private and final, forcing use through `LeakDetector`.

## Dependencies and integration points
Used exclusively by `LeakDetector`. Depends on Java reference queues and Ratis `UncheckedAutoCloseable`.

## Risks and test signals
Tests should verify close suppression and reporter invocation through `LeakDetector`. The reporter should avoid strong references to the tracked object.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/LeakTracker.java -->
