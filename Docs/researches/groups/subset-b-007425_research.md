# subset-b-007425 Research

Grouped source research for Hadoop HDFS client protocol translators, protobuf conversion helpers, reconfiguration RPC wrappers, token identifiers/selectors, block metadata helpers, caching strategy state, corrupt metadata exceptions, and disk balancer progress serialization. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ClientNamenodeProtocolTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ClientNamenodeProtocolTranslatorPB.java

## Purpose

`ClientNamenodeProtocolTranslatorPB.java` is the HDFS client-side adapter from the public `ClientProtocol` Java interface to the protobuf-backed `ClientNamenodeProtocolPB` RPC service. It owns no NameNode logic itself; it builds request protos, invokes the blocking RPC proxy, unwraps protobuf responses, and delegates object conversion to `PBHelperClient`. It is the compatibility layer that lets DFS clients use the Java `ClientProtocol` API while the wire protocol stays protobuf/RPC based.

## Important APIs, Types, and Functions

The class implements `ProtocolMetaInterface`, `ClientProtocol`, `Closeable`, and `ProtocolTranslator`. It stores a final `ClientNamenodeProtocolPB rpcProxy` and exposes `close()`, `getUnderlyingProxyObject()`, and `isMethodSupported()`. The method surface mirrors `ClientProtocol`: block lookup and mutation (`getBlockLocations`, `addBlock`, `complete`, `abandonBlock`, `updatePipeline`), namespace operations (`create`, `append`, `truncate`, `rename`, `delete`, `mkdirs`, `concat`, `getListing`, `getBatchedListing`), admin/status calls (`getStats`, `setSafeMode`, `rollEdits`, `saveNamespace`, `restoreFailedStorage`, `refreshNodes`, `finalizeUpgrade`, `rollingUpgrade`), token/security calls (`getDelegationToken`, `renewDelegationToken`, `cancelDelegationToken`, `getDataEncryptionKey`), snapshot/cache/ACL/xattr/encryption-zone/erasure-coding/storage-policy APIs, inotify edit streaming, open-file listing, HA state, and `getEnclosingRoot`.

Nested wrappers `BatchedCacheEntries` and `BatchedCachePoolEntries` adapt protobuf list responses to `BatchedEntries`. `setAsyncReturnValue()` bridges async protobuf RPC results into Hadoop's `AsyncCallHandler` for void-returning async operations. The file defines many reusable default/empty request protos for no-argument RPCs.

## Control Flow

The standard method flow is: assemble a protobuf builder from Java arguments, conditionally set optional fields only when Java values are non-null or non-empty, call `ipc(() -> rpcProxy.method(null, request))`, and convert the response field back to a Java type. Boolean/long/string methods return response scalars directly. Object-returning methods test `has*` response fields and return `null` where the historical `ClientProtocol` contract permits absence.

Some methods have special control paths. `setPermission`, `setOwner`, `rename2`, `setAcl`, and `getAclStatus` detect `Client.isAsynchronousMode()` and install a lower-layer `AsyncGet` so upper layers can wait on async RPC completion. `getBatchedListing` converts per-parent protobuf exceptions into `RemoteException` instances embedded in `HdfsPartialListing`. Cache, encryption-zone, reencryption, and open-file listings wrap lists plus `hasMore` into batch abstractions. `getHAServiceState` maps protobuf enum values through an explicit switch and defaults to `INITIALIZING`. A few methods (`getAclStatus`, `getEnclosingRoot`) call the proxy directly and translate `ServiceException` with `getRemoteException`; most rely on `ipc`.

## State and Persistence Behavior

The translator is mostly stateless beyond the proxy reference. It does not persist filesystem metadata, tokens, or namespace state locally. Static empty request protos are immutable reusable constants. Async methods store wait handles in `AsyncCallHandler`, not in this class. All durable state changes happen remotely in the NameNode via RPC.

## Dependencies and Integration Points

Primary dependencies are generated HDFS protobuf classes, `ClientNamenodeProtocolPB`, `PBHelperClient`, Hadoop RPC utilities (`RPC`, `RpcClientUtil`, `ProtobufRpcEngine2`, shaded protobuf helpers), HDFS protocol model classes, security token classes, ACL/xattr/encryption/cache/snapshot/EC APIs, and `AsyncCallHandler`. Integration points are DFS client code calling `ClientProtocol`, NameNode protobuf RPC servers, protocol feature probing through `isMethodSupported`, and compatibility handling for optional response fields across Hadoop versions.

## Risks and Edge Cases

The main risks are wire/API drift and optional-field semantics. Every new `ClientProtocol` method or new protobuf field must preserve Java defaults, nullability, enum mapping, and server compatibility. Array/list fields can fail if caller-provided parallel arrays differ in size, for example block locations, storage IDs, storage types, favored nodes, and batch listings. Async handling is subtle because the method may return `null` while the actual result or exception arrives later. Methods that bypass `ipc` must continue translating `ServiceException` correctly. Request builders that pass `null` lists into `addAll*` would fail if a caller violates expected invariants.

## Test Signals

Useful tests include client-protocol translator round trips against a mocked `ClientNamenodeProtocolPB`, MiniDFSCluster integration tests for create/append/list/delete/snapshot/cache/ACL/xattr/EC flows, async RPC tests for void and non-void operations, compatibility tests where optional proto fields are absent, method-support probing tests, and negative tests for remote exceptions embedded in batched listings and direct `ServiceException` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ClientNamenodeProtocolTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/PBHelperClient.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/PBHelperClient.java

## Purpose

`PBHelperClient.java` is the central HDFS client-side conversion library between generated protobuf messages and Hadoop/HDFS Java model objects. It supports the NameNode client translator, DataNode protocol helpers, token serialization, encryption metadata, snapshots, inotify, cache directives, erasure coding, xattrs, ACLs, storage reports, and many compatibility fields. It is intentionally static and stateless apart from a bounded ByteString cache.

## Important APIs, Types, and Functions

The public surface is a large family of overloaded `convert(...)` methods. Major families include blocks and located blocks (`ExtendedBlock`, `Block`, `LocatedBlock`, `LocatedStripedBlock`, `LocatedBlocks`), datanodes and storage (`DatanodeID`, `DatanodeInfo`, `DatanodeStorage`, `StorageReport`, `DatanodeStorageReport`, `StorageType`), checksums and checksum options, block/delegation tokens, `DataEncryptionKey`, file status/listings/server defaults/content summaries/quota usage, ACLs, xattrs, cache pools/directives, snapshots and snapshot diff listings, encryption zones and reencryption state, inotify events, erasure-coding schemas/policies/codecs/responses/topology verification, open-file entries, provided storage locations, add-block/open-file flags, and enum mappings for safe mode, rolling upgrade, reencryption, block type, admin state, datanode report type, crypto protocol, cipher suites, and permissions.

Supporting helpers include `getByteString(byte[])`, `getFixedByteString(String)`, `vintPrefixed(InputStream)`, enum `castEnum`, flag bitmask encoders/decoders, quota storage-type builders, and `bytestringCache` for string-to-`ByteString` reuse.

## Control Flow

Most methods are direct bidirectional mappers: inspect optional proto fields with `has*`, choose Java defaults for absent legacy fields, fill builders with present Java values, and return immutable protos or Java value objects. More complex flows include `convertLocatedBlockProto`, which reconstructs targets, storage types, storage IDs, cached locations, striped block indices, per-internal-block tokens, and corruption/offset state; `convert(GetEditsFromTxidResponseProto)` and `convertEditsResponse`, which parse or build typed inotify event payloads from nested protobuf bytes; snapshot diff conversion, which filters unknown diff labels; and erasure-coding conversion, which resolves built-in policies by ID but requires name/schema/cell size for custom policies.

## State and Persistence Behavior

The class does not persist data. It creates transient Java objects/protobufs and reuses immutable `ByteString` instances through `ShadedProtobufHelper` and a 10,000-entry Guava `LoadingCache`. Serialization behavior is important because many returned protos are written to RPC streams, fsimage/edit-log paths, or token identifiers by callers, but this class itself owns no durable state.

## Dependencies and Integration Points

Dependencies span Hadoop common (`FsPermission`, `AclEntry`, `XAttr`, `ContentSummary`, `QuotaUsage`, `Path`), HDFS protocol classes, generated `HdfsProtos`, `ClientNamenodeProtocolProtos`, encryption-zone and inotify protos, token/security classes, erasure-coding classes, Guava cache/collections, shaded protobuf `ByteString`/`CodedInputStream`, and utility classes like `DFSUtilClient`, `Preconditions`, `Shorts`, and `DataChecksum`. It is integrated by protocol translators, block token code, NameNode/DataNode RPC code, WebHDFS/token flows, and tests that need stable conversion behavior.

## Risks and Edge Cases

Risks cluster around compatibility and enum/flag drift. Many conversions assume enum ordinal or numeric proto values line up with Java enums; adding enum values can break `castEnum`, switch defaults, or bitmask handling. Optional fields must preserve old-wire defaults, for example missing storage types default to `StorageType.DEFAULT`, missing `nonDfsUsed` is derived from capacity/used/remaining, older file status flags are inferred from permission extension bits, and unknown crypto enum values are preserved in `UNKNOWN`. Some conversions return `null` for null internal values even though the header comment says protobuf converters should not be called with null. Parallel arrays/lists must stay aligned for located blocks and storage metadata. Inotify conversion throws for old response formats and unexpected event types.

## Test Signals

Strong signals are round-trip tests for each conversion family, compatibility tests with protos missing newer optional fields, enum/bitmask tests for every flag value, located striped block tests with storage IDs/types/indices/tokens, inotify encode/decode tests for all event types, erasure-coding built-in/custom policy tests, encryption and reencryption state tests, and property-style tests that Java object to proto to Java preserves public fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/PBHelperClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ReconfigurationProtocolPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ReconfigurationProtocolPB.java

## Purpose

`ReconfigurationProtocolPB.java` is the protobuf RPC interface marker for live reconfiguration calls to NameNode/DataNode services. It extends the generated `ReconfigurationProtocolService.BlockingInterface` and adds Hadoop RPC/security annotations.

## Important APIs, Types, and Functions

The interface has no methods of its own; it inherits generated blocking RPC methods such as start reconfiguration, list reconfigurable properties, and get reconfiguration status. Annotations define Kerberos principal lookup via `CommonConfigurationKeys.HADOOP_SECURITY_SERVICE_USER_NAME_KEY`, protocol name `org.apache.hadoop.hdfs.protocol.ReconfigurationProtocol`, and protocol version `1`. Audience is public and stability is evolving.

## Control Flow

There is no executable control flow. Hadoop RPC uses the annotations and inherited generated service methods to bind clients and servers to the protobuf implementation.

## State and Persistence Behavior

The interface owns no state. It participates in RPC registration and security metadata only.

## Dependencies and Integration Points

Dependencies are Hadoop classification annotations, RPC `ProtocolInfo`, `KerberosInfo`, `CommonConfigurationKeys`, and generated `ReconfigurationProtocolService`. It is consumed by `ReconfigurationProtocolTranslatorPB` and corresponding server-side PB implementations.

## Risks and Edge Cases

Changing protocol name/version or security annotations would break RPC compatibility or authentication. Because it extends generated protobuf code, proto service signature changes must be coordinated with translators and servers.

## Test Signals

Compile and RPC binding tests are the main signal, along with secure-cluster tests that verify the Kerberos server principal is discovered correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ReconfigurationProtocolPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ReconfigurationProtocolTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ReconfigurationProtocolTranslatorPB.java

## Purpose

`ReconfigurationProtocolTranslatorPB.java` adapts the Java `ReconfigurationProtocol` client interface to the protobuf `ReconfigurationProtocolPB` RPC service. It is the client-side wrapper used to start live reconfiguration, query status, and list mutable properties over Hadoop RPC.

## Important APIs, Types, and Functions

The class implements `ProtocolMetaInterface`, `ReconfigurationProtocol`, `ProtocolTranslator`, and `Closeable`. It exposes a public constructor that creates the PB proxy from address, ticket, configuration, and socket factory; static `createReconfigurationProtocolProxy`; `close`; `getUnderlyingProxyObject`; `startReconfiguration`; `getReconfigurationStatus`; `listReconfigurableProperties`; and `isMethodSupported`. It uses immutable empty request protos for all no-argument RPCs.

## Control Flow

Proxy creation installs `ProtobufRpcEngine2` for `ReconfigurationProtocolPB` and calls `RPC.getProxy` with protocol version and socket timeout. Each RPC method sends a prebuilt empty request through `ipc`: `startReconfiguration` ignores the empty response, `getReconfigurationStatus` converts the response through `ReconfigurationProtocolUtils`, and `listReconfigurableProperties` returns `response.getNameList()`. Method support probing delegates to `RpcClientUtil`.

## State and Persistence Behavior

The only instance state is the final RPC proxy. No reconfiguration state is stored locally; start/status results are remote service state. `close()` stops the proxy.

## Dependencies and Integration Points

Dependencies include Hadoop RPC (`RPC`, `RpcClientUtil`, `ProtobufRpcEngine2`), `UserGroupInformation`, `Configuration`, generated reconfiguration protos, `ReconfigurationTaskStatus`, and `ReconfigurationProtocolUtils`. It integrates HDFS clients/admin tools with NameNode/DataNode services implementing live reconfiguration.

## Risks and Edge Cases

Risks are mostly RPC compatibility: wrong protocol engine/version, missing method support on older servers, and response conversion drift. The static helper accepts a socket timeout but the public constructor passes `0`, so timeout behavior is inherited from Hadoop RPC defaults unless alternate construction is used.

## Test Signals

Tests should cover proxy creation against a mock or MiniDFS service, start/list/status RPC translation, method-support checks against servers with and without methods, exception translation through `ipc`, and close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ReconfigurationProtocolTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ReconfigurationProtocolUtils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ReconfigurationProtocolUtils.java

## Purpose

`ReconfigurationProtocolUtils.java` contains shared client-side conversion logic for reconfiguration status responses. It turns `GetReconfigurationStatusResponseProto` into the common `ReconfigurationTaskStatus` model.

## Important APIs, Types, and Functions

The class is `final` with a private constructor. Its single public method, `getReconfigurationStatus(GetReconfigurationStatusResponseProto response)`, extracts start/end time and converts each `GetReconfigurationStatusConfigChangeProto` into a `ReconfigurationUtil.PropertyChange` mapped to an optional error message.

## Control Flow

The method initializes `statusMap` to `null`, always reads `startTime`, sets `endTime` only when present, and creates a Guava hash map only if the response contains changes. For each change, it builds a `PropertyChange(name, newValue, oldValue)`, reads `errorMessage` only when present, stores `Optional.ofNullable(errorMessage)`, and returns a `ReconfigurationTaskStatus`.

## State and Persistence Behavior

No state is stored. The returned task status is a snapshot of remote reconfiguration state at response time. A `null` status map means there were no change entries.

## Dependencies and Integration Points

Dependencies are Hadoop `ReconfigurationTaskStatus`, `PropertyChange`, generated reconfiguration protos, Java `Optional`, and shaded Guava `Maps`. It is used by `ReconfigurationProtocolTranslatorPB` and any client-side code needing the same conversion.

## Risks and Edge Cases

The distinction between `null` status map and an empty map is part of the status contract and may matter to callers. Missing end time is normalized to `0`, representing an in-progress task. Duplicate property changes would overwrite earlier entries because the map key is `PropertyChange`.

## Test Signals

Tests should cover in-progress responses without end time, completed responses with end time, empty changes, changes with and without error messages, and duplicate property-change behavior if that is a supported server case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ReconfigurationProtocolUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/block/BlockTokenIdentifier.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/block/BlockTokenIdentifier.java

## Purpose

`BlockTokenIdentifier.java` defines the HDFS block access token identifier. It describes who may access a block, which block pool/block ID it covers, permitted access modes, optional storage-type/storage-ID restrictions, expiry/key metadata, and an optional handshake secret. It supports both legacy Writable serialization and newer protobuf serialization for upgrade compatibility.

## Important APIs, Types, and Functions

The class extends `TokenIdentifier`, declares `KIND_NAME` as `HDFS_BLOCK_TOKEN`, and defines `AccessMode` values `READ`, `WRITE`, `COPY`, and `REPLACE`. Important methods include constructors, `getKind`, `getUser`, getters/setters for expiry/key/handshake, `equals`, `hashCode`, `toString`, `readFields`, `readFieldsLegacy`, `readFieldsProtobuf`, `write`, `writeLegacy`, `writeProtobuf`, `getBytes`, and nested `Renewer`.

## Control Flow

`readFields` caches the raw input bytes, peeks at the first byte, and chooses legacy decoding for first bytes `<= 0` or protobuf decoding otherwise. Legacy decoding reads VLong/VInt/String fields, access modes, and then attempts newer storage type, storage ID, and handshake fields inside an EOF-tolerant block so older tokens still parse. Protobuf decoding parses `BlockTokenSecretProto` and maps modes/storage types through `PBHelperClient`. `write` dispatches to protobuf or legacy based on `useProto`. Mutators invalidate the cached byte representation.

## State and Persistence Behavior

State is the token identity fields and a `cache` of serialized bytes. The cache preserves unknown protobuf bytes after reading so unchanged tokens can return original bytes for password lookup and upgrade compatibility. Mutating expiry, key ID, or handshake invalidates the cache. The object serializes to token identifier bytes that are stored in Hadoop `Token` instances and used by DataTransferProtocol authorization.

## Dependencies and Integration Points

Dependencies include Hadoop token APIs, `UserGroupInformation`, Writable utilities, `StorageType`, `BlockTokenSecretProto`, `PBHelperClient`, and IO utilities. It integrates with block token secret managers, DataNode block access checks, client block tokens in located blocks, and `PBHelperClient` token conversion.

## Risks and Edge Cases

Serialization detection depends on first-byte conventions and requires a mark-supported `DataInputStream`; passing another `DataInput` shape fails. Legacy `writeLegacy` writes storage/handshake sections only when arrays/messages are non-null/non-empty, while legacy reads tolerate EOF for older tokens. `equals` and `hashCode` do not include `useProto`, `handshakeMsg`, or cache, which is intentional for identity but important for tests. `setHandshakeMsg` does not defensively copy the input byte array.

## Test Signals

Tests should cover legacy and protobuf round trips, parsing older legacy tokens without storage/handshake fields, raw-byte cache preservation after protobuf reads, cache invalidation on mutators, access-mode conversion, user fallback to `blockPoolId:blockId`, equality/hash behavior, and invalid/non-mark-supported input streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/block/BlockTokenIdentifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/block/BlockTokenSelector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/block/BlockTokenSelector.java

## Purpose

`BlockTokenSelector.java` selects an HDFS block token from a collection of Hadoop security tokens. It is used by security code that needs a `BlockTokenIdentifier` token for block-level DataNode operations.

## Important APIs, Types, and Functions

The class implements `TokenSelector<BlockTokenIdentifier>`. Its only method is `selectToken(Text service, Collection<Token<? extends TokenIdentifier>> tokens)`.

## Control Flow

If `service` is `null`, the method returns `null`. Otherwise it iterates the token collection and returns the first token whose kind equals `BlockTokenIdentifier.KIND_NAME`, casting it to `Token<BlockTokenIdentifier>`. It does not compare the token service to the requested service.

## State and Persistence Behavior

The selector is stateless and does not mutate tokens.

## Dependencies and Integration Points

Dependencies are Hadoop token interfaces and `Text`. It integrates with client/DataNode authentication flows that search available credentials for block access tokens.

## Risks and Edge Cases

The service argument is only used as a null guard; if multiple block tokens exist for different services, the first block token wins. The unchecked cast relies on token kind correctness. A null token collection would throw.

## Test Signals

Tests should cover null service, empty collection, collection with non-block tokens, first matching block token selection, and multiple block-token ordering behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/block/BlockTokenSelector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/block/DataEncryptionKey.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/block/DataEncryptionKey.java

## Purpose

`DataEncryptionKey.java` is a small immutable value holder for the key material needed to encrypt HDFS DataTransferProtocol traffic.

## Important APIs, Types, and Functions

The class exposes final fields `keyId`, `blockPoolId`, `nonce`, `encryptionKey`, `expiryDate`, and `encryptionAlgorithm`. It has one constructor and a `toString()` that reports key ID, block pool ID, nonce length, and encryption-key length.

## Control Flow

There is no behavioral flow beyond construction and string formatting. Callers construct it from key manager/protobuf responses and pass it to transfer/encryption code.

## State and Persistence Behavior

Instances are immutable by field assignment, but byte arrays are not defensively copied, so callers retaining references can mutate `nonce` or `encryptionKey`. The object itself has no persistence; it is serialized by `PBHelperClient` when needed.

## Dependencies and Integration Points

The only direct dependency is `InterfaceAudience`. It integrates with NameNode key generation responses, `ClientNamenodeProtocolTranslatorPB.getDataEncryptionKey`, `PBHelperClient` conversions, and DataNode/client data-transfer encryption setup.

## Risks and Edge Cases

The constructor accepts null arrays and strings, but `toString()` dereferences `nonce.length` and `encryptionKey.length`, so partially populated instances can throw. Lack of defensive copies is important because the fields contain secret material.

## Test Signals

Tests should cover protobuf round trips, null algorithm preservation, expected `toString()` shape, expiry propagation, and defensive handling by callers that receive mutable key arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/block/DataEncryptionKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/block/InvalidBlockTokenException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/block/InvalidBlockTokenException.java

## Purpose

`InvalidBlockTokenException.java` is the checked exception used when HDFS block access token verification fails.

## Important APIs, Types, and Functions

The class extends `IOException`, declares `serialVersionUID = 168L`, and provides a no-argument constructor plus a message constructor.

## Control Flow

There is no internal flow. DataNode/client security paths throw it to signal token verification failure.

## State and Persistence Behavior

It carries normal exception message/cause state inherited from `IOException`. No custom persistence behavior exists.

## Dependencies and Integration Points

Dependencies are `IOException` and Hadoop audience/stability annotations. It integrates with block token validators and DataTransferProtocol error handling.

## Risks and Edge Cases

The class has no cause-taking public constructor, so callers that need to preserve a lower-level cause must wrap differently or lose direct cause chaining. It is marked evolving, so consumers should not assume more than `IOException` semantics.

## Test Signals

Tests are generally indirect: invalid/expired/wrong-mode block token tests should assert this exception type or its remote translation. Constructor tests can verify message propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/block/InvalidBlockTokenException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/delegation/DelegationTokenIdentifier.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/delegation/DelegationTokenIdentifier.java

## Purpose

`DelegationTokenIdentifier.java` defines the HDFS-specific delegation token identifier. It specializes Hadoop's abstract delegation token identifier with HDFS token kind values, cached user lookup, stable string formatting, token stringification, and WebHDFS/SWebHDFS token-kind subclasses.

## Important APIs, Types, and Functions

The class extends `AbstractDelegationTokenIdentifier`. It declares `HDFS_DELEGATION_KIND`, a synchronized LRU `ugiCache`, constructors for empty/read and owner/renewer/real-user creation, `getKind`, cached `getUser`, `toString`, `toStringStable`, static `stringifyToken(Token<?>)`, and nested `WebHdfsDelegationTokenIdentifier` and `SWebHdfsDelegationTokenIdentifier`.

## Control Flow

`getUser` checks the static cache by token identifier instance and falls back to `super.getUser()` on a miss. `stringifyToken` creates a fresh identifier, reads token identifier bytes from a `DataInputStream`, and appends the token service when present. The nested WebHDFS classes override only `getKind`.

## State and Persistence Behavior

Token fields are inherited from `AbstractDelegationTokenIdentifier` and serialized by that superclass. The local static `ugiCache` stores up to 64 token-identifier to `UserGroupInformation` mappings to reduce repeated UGI construction; `clearCache` is visible for tests. The stable string form is intentionally frozen for CLI compatibility.

## Dependencies and Integration Points

Dependencies include Hadoop token APIs, UGI, `Text`, `WebHdfsConstants`, Apache Commons `LRUMap`, and Java IO streams. It integrates with HDFS delegation token secret managers, DFS/WebHDFS authentication, token display/CLI code, and `DelegationTokenSelector`.

## Risks and Edge Cases

The static synchronized LRU cache depends on correct `equals`/`hashCode` from the superclass and can retain UGI objects until eviction. `toString()` calls `getUser()`, so formatting can populate the cache. `stringifyToken` trusts token bytes to match this identifier format and throws `IOException` on malformed identifiers. `toStringStable` must not change except for major compatibility breaks.

## Test Signals

Tests should cover HDFS/WebHDFS/SWebHDFS kind values, serialization round trip through superclass fields, cache hit and `clearCache`, `stringifyToken` with and without service, stable string formatting, and malformed token identifier bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/delegation/DelegationTokenIdentifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/delegation/DelegationTokenSelector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/delegation/DelegationTokenSelector.java

## Purpose

`DelegationTokenSelector.java` selects HDFS delegation tokens, including from non-HDFS filesystems such as WebHDFS that need to map a URI-facing service to the NameNode RPC token service.

## Important APIs, Types, and Functions

The class extends `AbstractDelegationTokenSelector<DelegationTokenIdentifier>`, declares `SERVICE_NAME_KEY = "hdfs.service.host_"`, has a constructor fixed to `HDFS_DELEGATION_KIND`, and provides `selectToken(URI nnUri, Collection<Token<?>> tokens, Configuration conf)`.

## Control Flow

The URI-based selector builds an initial token service from the URI, checks configuration key `hdfs.service.host_<service>` for an override host/port, defaults to `DFS_NAMENODE_RPC_PORT_DEFAULT`, rebuilds the token service using the original URI host and resolved RPC port, and delegates to the superclass `selectToken(Text, tokens)`.

## State and Persistence Behavior

The selector is stateless. Configuration can supply per-service host/port overrides but no state is stored in the object.

## Dependencies and Integration Points

Dependencies include `Configuration`, `HdfsClientConfigKeys`, `SecurityUtil`, `NetUtils`, URI, Hadoop tokens, and delegation token selector base class. It integrates with WebHDFS and other clients that acquire or search HDFS delegation tokens without directly using the NameNode RPC URI.

## Risks and Edge Cases

The code intentionally avoids resolving the original URI hostname when building the final service. Misconfigured `hdfs.service.host_*` values can select the wrong port and fail to find a token. It assumes the remote cluster RPC port matches local defaults unless configured. Null URI host, null token collections, or missing configuration can surface through lower-level utilities.

## Test Signals

Tests should cover default RPC-port selection, configured service host overrides, preservation of original hostname, token match/miss behavior, WebHDFS URI examples, and malformed override addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/delegation/DelegationTokenSelector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockMetadataHeader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockMetadataHeader.java

## Purpose

`BlockMetadataHeader.java` reads and writes the fixed header at the start of HDFS DataNode block metadata files. That header records a metadata version and the `DataChecksum` definition used for block CRC chunks.

## Important APIs, Types, and Functions

The class declares `VERSION = 1`, stores final `version` and `DataChecksum checksum`, and exposes `getVersion`, `getChecksum`, `readDataChecksum(FileInputStream,int,File)`, `readDataChecksum(DataInputStream,Object)`, `preadHeader(FileChannel)`, `readHeader(DataInputStream)`, `readHeader(FileInputStream)`, `readHeader(RandomAccessFile)`, testing constructor, testing `writeHeader(DataOutputStream, BlockMetadataHeader)`, public `writeHeader(DataOutputStream, DataChecksum)`, and `getHeaderSize`.

## Control Flow

Sequential readers wrap streams as buffered `DataInputStream`, read the version short, parse a checksum header using `DataChecksum.newDataChecksum`, and wrap EOF or invalid checksum-size failures as `CorruptMetaHeaderException`. `readDataChecksum` warns if the on-disk version differs from `VERSION` but still returns the checksum. `preadHeader` reads exactly the header size from a `FileChannel` at positional offsets without changing channel position, then decodes version bytes and checksum bytes. `readHeader(RandomAccessFile)` seeks to zero and reads the fixed header buffer.

## State and Persistence Behavior

Instances are immutable holders for header data. Persistent behavior is the on-disk metadata header: two bytes of version plus the checksum header size reported by `DataChecksum`. Writers emit version `1` by default and then delegate checksum header serialization to `DataChecksum`.

## Dependencies and Integration Points

Dependencies include Java file/stream/channel APIs, `DataChecksum`, `InvalidChecksumSizeException`, SLF4J logging, and `CorruptMetaHeaderException`. It integrates with DataNode block metadata file readers/writers and client short-circuit read paths that need metadata header parsing without disturbing file-channel position.

## Risks and Edge Cases

Truncated or corrupt metadata files must throw `CorruptMetaHeaderException` rather than generic EOF/checksum-size failures. `preadHeader` loops while the buffer has remaining bytes and treats non-positive reads as corruption. Version mismatch is only a warning, so later code must tolerate checksum formats. `RandomAccessFile` reading changes file position by seeking to zero. Header size must stay aligned with `DataChecksum.getChecksumHeaderSize()`.

## Test Signals

Tests should cover valid header write/read round trips, short/truncated files for each read path, invalid checksum type/size bytes, version mismatch logging behavior, positional read preserving channel position, and header-size expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockMetadataHeader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/CachingStrategy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/CachingStrategy.java

## Purpose

`CachingStrategy.java` is a small value object describing read/write cache hints for HDFS DataNode operations: whether to drop data behind and how much readahead to request.

## Important APIs, Types, and Functions

The class stores nullable `Boolean dropBehind` and nullable `Long readahead`, where `null` means use server defaults. It exposes factories `newDefaultStrategy()` and `newDropBehind()`, a nested `Builder` initialized from a previous strategy, builder setters for both fields, `build`, constructor, getters, and `toString`.

## Control Flow

There is no complex control flow. Callers choose a factory or builder, optionally override hints, and pass the resulting strategy to lower-level IO paths.

## State and Persistence Behavior

Instances are immutable after construction because fields are private final. No persistence exists. The builder is mutable and copies initial values from a previous strategy.

## Dependencies and Integration Points

There are no external imports beyond the package. It integrates with HDFS client/DataNode read and write paths that decide OS cache drop-behind and readahead behavior.

## Risks and Edge Cases

Null is semantically meaningful for both fields and must not be collapsed to false or zero. The builder requires a non-null previous strategy. No validation prevents negative readahead values, so validation must happen in consumers if needed.

## Test Signals

Tests should cover default/null semantics, drop-behind factory, builder copy/update behavior, negative or zero readahead consumer behavior, and `toString` representation for null and non-null fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/CachingStrategy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/CorruptMetaHeaderException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/CorruptMetaHeaderException.java

## Purpose

`CorruptMetaHeaderException.java` is the package-local exception used when a DataNode block metadata file header is corrupt or truncated.

## Important APIs, Types, and Functions

The class extends `IOException` and provides package-private constructors for message-only and message-plus-cause creation.

## Control Flow

There is no internal flow. `BlockMetadataHeader` throws it from header parsing paths.

## State and Persistence Behavior

It carries standard exception message and cause state. No custom persistence behavior exists.

## Dependencies and Integration Points

The only dependency is `IOException`. It integrates directly with `BlockMetadataHeader` and indirectly with block metadata read paths that need to distinguish corrupt metadata headers from other IO failures.

## Risks and Edge Cases

Constructors are package-private, limiting creation to the datanode package. Callers outside the package can catch it only if they import the public class. No `serialVersionUID` is declared, which can matter for Java serialization warnings but is usually irrelevant for local IO exceptions.

## Test Signals

Tests are mostly through `BlockMetadataHeader`: truncated header and invalid checksum bytes should throw this type and preserve the underlying cause where supplied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/CorruptMetaHeaderException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/DiskBalancerWorkItem.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/DiskBalancerWorkItem.java

## Purpose

`DiskBalancerWorkItem.java` is a JSON-serializable progress and limit record for a disk balancer copy step. It tracks how much data and how many blocks have been copied, elapsed time, error state, and balancing limits such as tolerated disk errors, tolerance percent, and bandwidth.

## Important APIs, Types, and Functions

The class is annotated `@JsonInclude(JsonInclude.Include.NON_DEFAULT)` and uses static Jackson `ObjectMapper`/`ObjectReader`. It has an empty constructor for JSON, a constructor accepting `bytesToCopy` and `bytesCopied`, static `parseJson(String)`, `toJson()`, getters/setters for all fields, and increment helpers `incErrorCount`, `incCopiedSoFar`, and `incBlocksCopied`.

## Control Flow

`parseJson` checks the input JSON is non-null and deserializes it with the typed reader. Runtime update flow is expected to mutate counters as work proceeds: increment copied bytes/blocks/errors, set elapsed seconds and error message, then serialize status to JSON for reporting or persistence. `toJson` writes the current object through Jackson.

## State and Persistence Behavior

All fields are mutable bean properties. JSON serialization omits default-valued fields, so absent fields deserialize back to Java defaults. This compact JSON is the persistence/interchange format used by disk balancer status paths. The elapsed time is explicitly stored instead of derived from client time to avoid client/server clock skew.

## Dependencies and Integration Points

Dependencies include Jackson annotations/databind, Hadoop `Preconditions`, and audience/stability annotations. It integrates with DataNode disk balancer planning/execution/status code that reports work-item progress and enforces bandwidth/error/tolerance limits.

## Risks and Edge Cases

There is no validation for negative counters, decreasing copied bytes, overflow, or nonsensical bandwidth/tolerance values. Static mapper instances are shared and should remain thread-safe for normal Jackson read/write usage. Omitting default fields means consumers must distinguish absent from explicit zero only by contract, not JSON shape.

## Test Signals

Tests should cover JSON parse/write round trips, omission of default fields, null JSON rejection, counter increment behavior, elapsed-time field preservation, error message/count updates, and compatibility when older JSON lacks newer fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/DiskBalancerWorkItem.java -->
