# Research: subset-b-008060

Grouped source research for Apache Ozone OM HA proxy helpers, OM key/bucket metadata DTOs, tenant metadata DTOs, key-location serialization, and multipart upload helper types. Each section preserves the original source path in its title and is wrapped for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/ha/OMFailoverProxyProviderBase.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/ha/OMFailoverProxyProviderBase.java

Purpose: Abstract base for OM client failover proxy providers. It owns the ordered OM proxy set, creates Hadoop RPC proxies, and supplies the retry/failover policy used when an OM is not leader, not ready, inaccessible, or returning retryable failures.

Important APIs/types/functions: Implements `FailoverProxyProvider<T>` and `Closeable`. Subclasses provide `initOmProxiesFromConfigs`. `createOMProxy` configures protobuf RPC and a network-only retry policy. `getRetryPolicy` handles `OMNotLeaderException`, `OMLeaderNotReadyException`, access-control/token failures, and Ratis read exceptions. `performFailover`, `selectNextOmProxy`, `setNextOmProxy`, `getWaitTime`, and static exception unwrappers are the main behavioral APIs.

Control flow and state: `currentProxyIndex` is the active proxy and `nextProxyIndex` is the candidate chosen by retry logic; synchronized methods protect both. Not-leader responses can jump directly to a suggested leader if the node ID/address matches known proxies. Generic retryable failures rotate round-robin. Same-OM retries use linearly increasing waits, while full rounds across all OMs trigger `waitBetweenRetries`.

State and persistence behavior: No persistent state. Runtime state includes attempted OM IDs, last attempted OM, same-OM attempt count, access-control retry tracking, and `performFailoverDone`, which prevents multiple threads from advancing the next proxy repeatedly before Hadoop's retry handler calls `performFailover`.

Dependencies and integration points: Depends on Hadoop RPC/retry APIs, Ozone configuration keys, `OMProxyInfo.OrderedMap`, Hadoop security/UGI, OM exception types, and Ratis exceptions. It is the common base for protocol-specific OM proxy providers used by Ozone clients.

Risks: Suggested leader validation requires both node ID and address, so stale or incomplete leader hints fall back to round-robin. Access-control/token errors are retried across OMs once, which avoids stale auth state but can delay failure. Any unsynchronized future changes around proxy indices would risk duplicate failovers under concurrent retries.

Test signals: Unit coverage should exercise not-leader suggested leader selection, leader-not-ready same-node backoff, round-robin retry delay after all OMs are attempted, access-control retry exhaustion, no-failover exception filtering, and concurrent `selectNextOmProxy`/`performFailover` behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/ha/OMFailoverProxyProviderBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/ha/OMProxyInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/ha/OMProxyInfo.java

Purpose: Extends Hadoop `ProxyInfo<T>` with OM-specific node identity, RPC address, and delegation-token service metadata.

Important APIs/types/functions: `newInstance` builds an OM proxy record, defaulting null node IDs to `OM_DEFAULT_NODE_ID`. Accessors expose node ID, address string, socket address, token service, and proxy. `createProxyIfNeeded` lazily initializes the proxy with a checked address-to-proxy function. Nested `OrderedMap<P>` provides an immutable ordered list plus node ID to index lookup.

Control flow and state: The outer object is mostly immutable except the inherited proxy reference, which is synchronized for lazy creation. Unresolved RPC addresses log a warning and suppress delegation-token service creation. `OrderedMap` builds a `LinkedHashMap`, rejects duplicate node IDs through Ratis preconditions, and asserts ordering invariants.

State and persistence behavior: No persistence. `dtService` is derived from the resolved RPC socket address and is null for unresolved addresses.

Dependencies and integration points: Used by `OMFailoverProxyProviderBase` to order failover candidates, map leader node IDs to proxies, validate suggested leader addresses, and expose delegation-token service names. Integrates with Hadoop `NetUtils`, `SecurityUtil`, and Ratis precondition helpers.

Risks: Unresolved addresses leave `dtService` null, which can affect token selection. The proxy object is lazily created and wrapped in `IllegalStateException` on creation failure, so callers must treat lookup as potentially failing at first use. `OrderedMap` is immutable only if the input proxy objects are not externally mutated except intended proxy initialization.

Test signals: Tests should verify duplicate node rejection, iteration/index invariants, address/node `contains` matching, unresolved address handling, and lazy proxy creation only once.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/ha/OMProxyInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/ha/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/ha/package-info.java

Purpose: Package documentation for Ozone Client OM proxy classes.

Important APIs/types/functions: Declares `org.apache.hadoop.ozone.om.ha`.

Control flow and state: No runtime control flow or state.

State and persistence behavior: None.

Dependencies and integration points: Groups HA client proxy support such as `OMFailoverProxyProviderBase` and `OMProxyInfo`.

Risks: Minimal. The package comment is intentionally terse and does not document retry semantics.

Test signals: Compile/package validation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/ha/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/AclListBuilder.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/AclListBuilder.java

Purpose: Copy-on-write builder for immutable `OzoneAcl` lists. It avoids allocating a new list when no ACL mutation happens.

Important APIs/types/functions: Static constructors `empty`, `of(ImmutableList)`, `of(List)`, and `copyOf` seed the builder. `add`, `addAll`, `set`, and `remove` delegate ACL merge/removal semantics to `OzoneAclUtil`. `build` returns the original immutable list unless `changed` is true.

Control flow and state: `updatedList` is lazily created from `originalList` on first mutation. `changed` is updated only when an actual ACL operation changes list content, except `set`, which compares the supplied list against the active list.

State and persistence behavior: No direct persistence. It is used by persistent metadata objects before they convert ACLs to protobuf.

Dependencies and integration points: Used by builders for keys, buckets, directories, and multipart key metadata. The List overload preserves binary compatibility across Guava versions.

Risks: `set` accepts a caller-provided list and documents that future mutations require it to be modifiable. Passing an immutable list and then calling `add` or `remove` can fail. Not thread-safe.

Test signals: Cover no-change build identity, add/merge semantics, removal, null handling, `set` with equal and different lists, and Guava compatibility path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/AclListBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/BasicOmKeyInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/BasicOmKeyInfo.java

Purpose: Lightweight key metadata used by light/list-key responses where full block locations and rich `OmKeyInfo` state are unnecessary.

Important APIs/types/functions: Fields include volume, bucket, key, size, times, replication config, file flag, ETag, owner, and encryption flag. `Builder` constructs instances. `fromOmKeyInfo` extracts a light view from full metadata. `getProtobuf` serializes to `BasicKeyInfo`; overloaded `getFromProtobuf` methods reconstruct using either `ListKeysRequest` or explicit volume/bucket names.

Control flow and state: The object is mostly immutable after construction except `ownerName` is not final. Proto conversion writes EC replication config or legacy factor depending on replication type. When older protos lack `isFile`, parsing infers file status from whether the key name ends in `/`.

State and persistence behavior: This is a transport DTO, not the primary OM DB value. It preserves replication and encryption indicators needed by clients while omitting block lists.

Dependencies and integration points: Depends on `ReplicationConfig`, `ECReplicationConfig`, `QuotaUtil`, `OmKeyInfo`, and Ozone Manager protobuf `BasicKeyInfo`. Used by `ListKeysLightResult` and list-key RPC flows.

Risks: `equals` assumes non-null volume, bucket, key, replication config, and owner; partially built instances can throw. `hashCode` uses only names while `equals` includes more fields, which is legal but collision-prone.

Test signals: Round-trip proto tests should include EC and RATIS/STAND_ALONE replication, blank and nonblank ETag, missing `isFile`, encrypted flag, owner propagation, and replicated-size calculation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/BasicOmKeyInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/BucketEncryptionKeyInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/BucketEncryptionKeyInfo.java

Purpose: Immutable bucket encryption key descriptor containing crypto protocol version, cipher suite, and KMS key name.

Important APIs/types/functions: Constructor and nested `Builder` set `CryptoProtocolVersion`, `CipherSuite`, and key name. Accessors expose those values. `equals` and `hashCode` compare all fields.

Control flow and state: No runtime branching beyond equality. The builder does not validate nulls.

State and persistence behavior: Embedded in bucket arguments/info and converted to protobuf through `OMPBHelper`, making it part of persisted and RPC bucket metadata when encryption is enabled.

Dependencies and integration points: Used by `OmBucketArgs`, `OmBucketInfo`, and encryption-zone/bucket creation flows. Depends on Hadoop crypto types.

Risks: The class permits null fields; callers must validate before persisting or enforcing encryption. Deprecated setter paths in bucket builders skip entries whose key name is null.

Test signals: Builder equality/hash tests, protobuf conversion through bucket metadata, and null-key filtering in bucket builders.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/BucketEncryptionKeyInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/BucketLayout.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/BucketLayout.java

Purpose: Enumerates OM bucket namespace layouts: `FILE_SYSTEM_OPTIMIZED`, `OBJECT_STORE`, and `LEGACY`.

Important APIs/types/functions: `fromProto` and `toProto` convert to Ozone Manager protobuf values. `isFileSystemOptimized`, `isLegacy`, `isObjectStore`, and `shouldNormalizePaths` encapsulate layout behavior. `fromString` defaults blank values to `LEGACY`. `validateSupportedOperation` rejects non-legacy layouts for older client operations.

Control flow and state: Stateless enum methods. Legacy behavior depends on the `enableFileSystemPaths` flag: with filesystem paths disabled, legacy buckets behave like object-store buckets.

State and persistence behavior: Stored in bucket metadata protobuf and controls key table/path normalization semantics after deserialization.

Dependencies and integration points: Used by `OmBucketInfo`, multipart abort info, request validation, and upgrade compatibility logic.

Risks: Defaulting unknown proto values to `LEGACY` is compatibility-friendly but may hide bad input. `valueOf` in `fromString` still throws for nonblank invalid strings.

Test signals: Proto round trips, legacy path normalization under both filesystem-path settings, old-client rejection for FSO/OBS, and blank string fallback.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/BucketLayout.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/DBUpdates.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/DBUpdates.java

Purpose: Client-side container for incremental OM DB update batches.

Important APIs/types/functions: Holds a `List<byte[]>` of write batches, `currentSequenceNumber`, `latestSequenceNumber`, and success flag. `addWriteBatch` appends data and advances current sequence number to the maximum seen.

Control flow and state: Mutable holder with simple setters/getters. Default sequence numbers are `-1`, and update success defaults to true.

State and persistence behavior: Stores serialized DB batch bytes in memory for transfer/consumption; it does not persist them itself.

Dependencies and integration points: Used in OM DB checkpoint/update synchronization flows where clients or followers receive RocksDB write batches with sequence tracking.

Risks: `getData` returns the mutable internal list, and byte arrays are not copied. No validation enforces sequence monotonicity except max tracking in `addWriteBatch`.

Test signals: Add-batch sequence advancement, constructor copy of the list container, mutable data exposure expectations, latest/current sequence setters, and failure flag propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/DBUpdates.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/DeleteTenantState.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/DeleteTenantState.java

Purpose: Wrapper for tenant deletion response state, reporting the associated volume and remaining volume reference count.

Important APIs/types/functions: Constructor and builder set `volumeName` and `volRefCount`. `getProtobuf` emits `DeleteTenantResponse`; `fromProtobuf` reconstructs the object.

Control flow and state: Immutable after construction. Builder has no validation.

State and persistence behavior: Response/transport DTO only. It mirrors protobuf fields and is not itself a DB codec.

Dependencies and integration points: Used by tenant delete APIs that need to tell clients whether the tenant volume can be cleaned up or still has references.

Risks: Allows null volume names and negative counts unless upstream validation prevents them.

Test signals: Protobuf round trip and builder field propagation, especially zero and nonzero reference counts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/DeleteTenantState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/EncryptionBucketInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/EncryptionBucketInfo.java

Purpose: Public evolving descriptor for an encrypted bucket/encryption zone: path, ID, cipher suite, crypto protocol version, and key name.

Important APIs/types/functions: Constructor sets all fields. Accessors expose ID/path/crypto metadata. `equals`, `hashCode`, and `toString` cover all fields.

Control flow and state: Immutable value object with no branching other than equality.

State and persistence behavior: Represents listed encryption bucket state; persistence is external. The ID supports batched listing.

Dependencies and integration points: Integrates with Hadoop crypto types and Ozone encryption bucket listing APIs.

Risks: Constructor does not validate path, key name, or crypto fields. The class is public/evolving, so serialization expectations may exist outside this module.

Test signals: Equality/hash behavior, listing order around ID boundaries, and null field expectations if callers rely on permissive construction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/EncryptionBucketInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ErrorInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ErrorInfo.java

Purpose: Simple mutable error DTO containing an error code and message.

Important APIs/types/functions: Constructor, getters, and setters for `code` and `message`.

Control flow and state: No control flow. Both fields are mutable.

State and persistence behavior: No persistence behavior in this class. It is suitable for API/response error payloads.

Dependencies and integration points: Standalone helper type in OM helpers.

Risks: No validation or immutability. Callers must handle null/empty code or message.

Test signals: Basic accessor/mutator coverage if used in response serialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ErrorInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/KeyInfoWithVolumeContext.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/KeyInfoWithVolumeContext.java

Purpose: Wraps `OmKeyInfo` with optional volume context and optional user principal for client-side KMS work such as decrypting encrypted key material.

Important APIs/types/functions: Constructor stores `Optional<OmVolumeArgs>`, `Optional<String>`, and required key info. `fromProtobuf` parses `GetKeyInfoResponse`; `toProtobuf` emits volume info, user principal, and key info using the requested client version. Builder mirrors the fields.

Control flow and state: Optional volume/user fields are only written when present. Key info is always serialized.

State and persistence behavior: Transport wrapper only. It does not persist metadata but contains persistable `OmKeyInfo` and `OmVolumeArgs` protobufs.

Dependencies and integration points: Used by get-key-info RPC paths, especially encrypted-volume flows that require volume owner/KMS principal context. Depends on `OmVolumeArgs`, `OmKeyInfo`, and `GetKeyInfoResponse`.

Risks: Builder does not validate `keyInfo`; a null key causes `toProtobuf` failure. `proto.getUserPrincipal()` returns an empty string when absent, so the optional may be present with an empty value.

Test signals: Round trips with and without volume info, user principal handling, encrypted key path client-version serialization, and null key validation expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/KeyInfoWithVolumeContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/KeyValueUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/KeyValueUtil.java

Purpose: Utility for converting string maps to and from HDDS `KeyValue` protobuf lists.

Important APIs/types/functions: `getFromProtobuf(List<KeyValue>)` collects protobuf keys and values into a map. `toProtobuf(Map<String,String>)` emits a list of `KeyValue` protos in the map's iteration order.

Control flow and state: Stateless static utility. Duplicate keys during `getFromProtobuf` use `Collectors.toMap` default duplicate handling, which throws.

State and persistence behavior: Used heavily in persisted metadata/tag protobuf fields for keys, buckets, and directories.

Dependencies and integration points: Integrates with `HddsProtos.KeyValue` and helper classes extending `WithMetadata`.

Risks: Duplicate protobuf keys are fatal. Null keys or values will fail during protobuf build or map collection. Output list ordering depends on input map implementation.

Test signals: Round trip maps, duplicate-key rejection, empty maps/lists, and deterministic ordering when using `LinkedHashMap` or immutable maps.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/KeyValueUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/LeaseKeyInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/LeaseKeyInfo.java

Purpose: Small holder tying committed key metadata to open-key metadata for lease recovery or lease inspection operations.

Important APIs/types/functions: Constructor accepts `keyInfo` and `openKeyInfo`; getters expose both `OmKeyInfo` values.

Control flow and state: Immutable references after construction.

State and persistence behavior: No direct persistence. The contained `OmKeyInfo` objects may represent DB values in committed/open key tables.

Dependencies and integration points: Used by OM lease-related code that needs both the visible key and the open-key entry.

Risks: Allows null fields; callers must know which side may be absent.

Test signals: Lease recovery tests should verify the correct committed/open key pair is returned and not swapped.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/LeaseKeyInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ListKeysLightResult.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ListKeysLightResult.java

Purpose: Result container for lightweight key listing.

Important APIs/types/functions: Constructor stores `List<BasicOmKeyInfo>` and `isTruncated`. Getters expose both.

Control flow and state: No branching. The key list reference is mutable if the caller supplied a mutable list.

State and persistence behavior: Transport result only, not persisted.

Dependencies and integration points: Used by list-key APIs that return `BasicOmKeyInfo` instead of full `OmKeyInfo`.

Risks: No defensive copy or null validation.

Test signals: Listing tests should verify truncation and returned key order/contents for light-list paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ListKeysLightResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ListKeysResult.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ListKeysResult.java

Purpose: Result container for full key listing.

Important APIs/types/functions: Constructor stores `List<OmKeyInfo>` and `isTruncated`. Getters expose both.

Control flow and state: No branching. The key list is not defensively copied.

State and persistence behavior: Transport result only; contained `OmKeyInfo` values may be persisted OM key metadata.

Dependencies and integration points: Used by OM list-key APIs that need full key metadata and possibly block locations.

Risks: Mutable list exposure and no null validation.

Test signals: Listing tests should verify truncation, pagination marker behavior in caller code, and correct `OmKeyInfo` conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ListKeysResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ListOpenFilesResult.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ListOpenFilesResult.java

Purpose: Result container for listing open files/open keys, including total count, continuation token, `hasMore`, and `OpenKeySession` entries.

Important APIs/types/functions: One constructor accepts ready `OpenKeySession` objects; another accepts parallel client ID and protobuf `KeyInfo` lists and converts them through `getOpenKeySessionListFromPB`. JSON properties name `totalOpenKeyCount`, `hasMore`, and `contToken`.

Control flow and state: Conversion validates equal list sizes, parses each `KeyInfo` into `OmKeyInfo`, and sets session version from the latest key-location version.

State and persistence behavior: Transport/admin result only. The protobuf constructor reconstructs key metadata from serialized forms but does not write DB state.

Dependencies and integration points: Used by open-file listing/admin APIs. Depends on Guava preconditions, Jackson annotations, `OpenKeySession`, and `OmKeyInfo`.

Risks: If key info has no latest version locations, session version lookup can fail. No defensive copy of session list.

Test signals: Mismatched list size rejection, protobuf conversion with multiple open keys, JSON property names, continuation token/hasMore behavior, and empty result handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ListOpenFilesResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/MapBuilder.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/MapBuilder.java

Purpose: Copy-on-write builder for immutable maps, used for metadata and tags.

Important APIs/types/functions: Static constructors `empty`, `of`, and `copyOf` seed an immutable original. `put`, `putAll`, `remove`, `set`, `isChanged`, and `build` manage mutations. `initialValue` exposes the original within the package.

Control flow and state: `updated` is a `LinkedHashMap` created lazily. `build` returns the original immutable map if no change is recorded. `set` assumes reference inequality means change rather than deep equality.

State and persistence behavior: No direct persistence, but it builds maps that later serialize through `KeyValueUtil` into OM protobuf metadata/tag fields.

Dependencies and integration points: Used in `WithMetadata` descendants and request/metadata builders.

Risks: `put` marks changed with reference comparison (`prev != value`), so replacing an equal distinct value is still a change and replacing the same object is not. `set` can accept an immutable map, but later mutation requires modifiability. Not thread-safe.

Test signals: No-change identity, insertion order preservation, put/remove/set behavior, null rejection, and immutable build output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/MapBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OMNodeDetails.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OMNodeDetails.java

Purpose: OM-specific node descriptor extending generic `NodeDetails` with RPC port, decommission state, and Ratis listener status.

Important APIs/types/functions: Builder constructs from host/RPC/Ratis/HTTP/HTTPS/service/node data. `getOMDBCheckpointEndpointUrl` builds v1 or v2 DB checkpoint URLs with snapshot-data and flush query parameters. `getOMNodeDetailsFromConf` reads RPC, Ratis, HTTP, HTTPS, and listener config. `getProtobuf`/`getFromProtobuf` convert `OMNodeInfo`.

Control flow and state: Mutable flags mark decommissioned and Ratis listener state. Config loading returns null if the OM RPC address is missing, creates socket addresses with error wrapping, and determines listener status from configured listener node IDs.

State and persistence behavior: `OMNodeInfo` protobuf carries node state for admin/cluster APIs. DB checkpoint URL construction controls remote checkpoint download behavior but does not persist state.

Dependencies and integration points: Used by OM HA/admin code, checkpoint transfer, and decommission/listener workflows. Depends on `OzoneConfiguration`, `OmUtils`, `ConfUtils`, `URIBuilder`, and admin protobufs.

Risks: URL building passes address strings as hosts; address formatting must be compatible with `URIBuilder`. Missing config silently returns null. Protobuf conversion omits service ID/http/https, so round-tripped objects have reduced context.

Test signals: Config-derived node details for service/node suffixes, listener detection, v1/v2 checkpoint URL query parameters, decommission protobuf round trip, and malformed address handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OMNodeDetails.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OMRatisHelper.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OMRatisHelper.java

Purpose: Bridge between OM proto2 messages and Ratis proto3 `ByteString`/`Message` payloads.

Important APIs/types/functions: `convertRequestToByteString`, `convertByteStringToOMRequest`, `convertResponseToMessage`, and `convertByteStringToOMResponse` perform byte conversions using read-only byte buffers. `getOMResponseFromRaftClientReply` optionally stamps leader OM node ID into the response. `smProtoToString` creates a short debug string for Ratis log entries.

Control flow and state: Stateless utility. Parsing uses `ByteBufferInputStream`. Debug conversion catches `Throwable` to avoid log formatting failures.

State and persistence behavior: Handles serialized Ratis log and reply payloads but does not persist them. The exact bytes are OM request/response protobuf encodings.

Dependencies and integration points: Used by OM Ratis server/client paths and log/debug tooling. Depends on Ratis `Message`, `RaftClientReply`, `StateMachineLogEntryProto`, and Ozone Manager protocol protos.

Risks: Unsafe byte wrapping avoids copies, so correctness depends on immutable/read-only source buffers. Catching `Throwable` in debug conversion hides malformed log details but protects callers.

Test signals: Request/response byte round trips, leader ID injection, malformed bytes throwing `IOException` for parse methods, and `smProtoToString` fallback behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OMRatisHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmBucketArgs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmBucketArgs.java

Purpose: Request argument object for bucket create/modify operations, carrying bucket identity, versioning, storage type, quotas, encryption key, default replication, owner, metadata, tags, and audit fields.

Important APIs/types/functions: Extends `WithMetadata` and implements `Auditable`. Builder validates volume and bucket names and tracks whether quota fields were explicitly set. `toAuditMap` emits user-visible audit fields. `getProtobuf`, `builderFromProtobuf`, and `getFromProtobuf` map to `BucketArgs`.

Control flow and state: Quota values default to `QUOTA_RESET` unless their explicit-set flags are true. Proto serialization writes optional fields only when meaningful: version/storage/owner/encryption/default replication/tags, and quotas only when set to positive values or reset. The deprecated bucket encryption setter ignores non-null entries with null key names.

State and persistence behavior: Primarily RPC/request state. When accepted by OM, fields feed persisted `OmBucketInfo`.

Dependencies and integration points: Used by bucket create/set-property flows, audit logging, and protobuf request handling. Depends on `DefaultReplicationConfig`, `StorageType`, `BucketEncryptionKeyInfo`, `MapBuilder`, `KeyValueUtil`, and `OMPBHelper`.

Risks: Audit quota condition relies on operator precedence and can include reset values even when explicit flags are false. Builder requires tags object, but the field is always initialized. Null optional fields require downstream defaults.

Test signals: Proto round trips for optional quotas, reset quotas, encryption key, default replication, tags, metadata, owner, and audit map contents.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmBucketArgs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmBucketInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmBucketInfo.java

Purpose: Persisted bucket metadata model for OM DB and bucket RPC responses.

Important APIs/types/functions: Extends `WithObjectID`, implements `Auditable` and `CopyObject`. `CODEC` persists `BucketInfo` protobuf. Fields include volume/bucket, ACLs, versioning, storage type, creation/modification times, encryption, default replication, link source, used bytes/namespace, quotas, snapshot usage, bucket layout, owner, tags, metadata, object/update IDs. Builder supports copying and mutation. `getProtobuf` and `builderFromProtobuf` handle serialization.

Control flow and state: Usage counters are mutable. `incrUsedBytes`, `decrUsedBytes`, `incrUsedNamespace`, and `decrUsedNamespace` update live usage and optionally snapshot usage for pending deletes. `purgeSnapshotUsed*` reduces snapshot counters after cleanup. `isLink` is true when source volume and bucket are set.

State and persistence behavior: This is the authoritative bucket table value. Protobuf stores ACLs, metadata, tags, quotas, layout, usage, snapshot usage, object IDs, encryption, and link targets. `copyObject` uses the builder to produce a new metadata object.

Dependencies and integration points: Used by OM bucket table, quota accounting, snapshot accounting, S3 tagging, bucket links, audit logs, and replication defaults. Depends on `OzoneAclUtil`, `KeyValueUtil`, `BucketLayout`, `DefaultReplicationConfig`, `OMPBHelper`, and HDDS codecs.

Risks: Mutable usage fields mean shared references can observe accounting changes. Builder validation requires storage type and names but not semantic quota limits. Protobuf deserialization sets layout from either an override or proto; callers must pass overrides carefully during upgrades.

Test signals: Codec/protobuf round trips, quota and usage accounting including snapshot usage, bucket link serialization, layout defaults/upgrades, ACL/tag/metadata persistence, copy-object isolation, and audit map contents.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmBucketInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmDBAccessIdInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmDBAccessIdInfo.java

Purpose: Immutable persisted metadata for one tenant access ID, including tenant ID, user principal, admin flag, and delegated-admin flag.

Important APIs/types/functions: `CODEC` delegates to `ExtendedUserAccessIdInfo` protobuf. Constructor and builder set fields. `getProtobuf` and `getFromProtobuf` convert to/from DB representation.

Control flow and state: Immutable after construction. Delegated-admin is documented as effective only when admin is true but not enforced in the class.

State and persistence behavior: Persisted in OM tenant access-ID tables through the delegated protobuf codec.

Dependencies and integration points: Used by tenant/user access management and authorization checks.

Risks: No validation prevents delegated admin without admin, null tenant ID, or null principal. Codec copy type is shallow, acceptable because fields are immutable strings/booleans.

Test signals: Codec round trip, admin/delegated combinations, and tenant access authorization flows consuming persisted values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmDBAccessIdInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmDBTenantState.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmDBTenantState.java

Purpose: Immutable persisted state for an Ozone tenant and its backing volume/roles/policies.

Important APIs/types/functions: `CODEC` delegates to `TenantState` protobuf. Fields include tenant ID, bucket namespace name, user role, admin role, bucket namespace policy, and bucket policy. Implements `Comparable` by tenant ID. `getProtobuf` and `getFromProtobuf` round trip all fields.

Control flow and state: Immutable value object. Equality/hash include all fields; ordering includes only tenant ID.

State and persistence behavior: Persisted in OM tenant state table using protobuf codec. Empty bucket namespace name is documented as possible but should not normally happen.

Dependencies and integration points: Used by tenant creation/deletion, Ranger/ACL policy coordination, and tenant listing.

Risks: `compareTo` can report equality for distinct objects with the same tenant ID but different policy fields, which is suitable for tenant-keyed sorted sets but not total object ordering. Null tenant ID would break comparison.

Test signals: Codec round trips, equality/hash behavior, compare ordering, and tenant delete/list flows.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmDBTenantState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmDBUserPrincipalInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmDBUserPrincipalInfo.java

Purpose: Persisted mapping from a user principal to the tenant access IDs associated with that principal.

Important APIs/types/functions: `CODEC` delegates to `TenantUserPrincipalInfo`. Constructor copies the input set. `addAccessId`, `removeAccessId`, and `hasAccessId` mutate/query the set. `getProtobuf` writes all access IDs; `getFromProtobuf` rebuilds from the list.

Control flow and state: Mutable set holder. `getAccessIds` returns the internal set directly.

State and persistence behavior: Stored in OM tenant user principal table. Mutations must be followed by table updates by caller code.

Dependencies and integration points: Used by tenant user/access-ID management to answer which access IDs belong to a Kerberos principal.

Risks: Internal set exposure allows external mutation outside OM table update discipline. Builder with null access IDs causes construction failure.

Test signals: Codec round trip, add/remove idempotency, duplicate access IDs, and persistence after mutation in tenant manager tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmDBUserPrincipalInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmDeleteKeys.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmDeleteKeys.java

Purpose: Client-side DTO describing a bulk key delete request: volume, bucket, and key names.

Important APIs/types/functions: Constructor sets the three fields; getters expose them.

Control flow and state: No branching. Fields are mutable only within the class but no setters are exposed.

State and persistence behavior: Request helper only. Actual deletion state is handled by OM request processing and DB tables.

Dependencies and integration points: Used by client/OM delete-key flows.

Risks: No defensive copy of key names and no null validation.

Test signals: Bulk delete request tests should verify key list propagation and caller-side validation for empty/null lists.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmDeleteKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmDirectoryInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmDirectoryInfo.java

Purpose: Persisted directory metadata for file-system-optimized buckets, keyed by parent object ID and directory name.

Important APIs/types/functions: Extends `WithParentObjectId`. `CODEC` persists `DirectoryInfo` protobuf. Builder sets name, owner, creation/modification time, ACLs, metadata, object/update/parent IDs. Conversion helpers bridge to/from `OmKeyInfo` builders.

Control flow and state: Immutable after build. `getPath` constructs `parentObjectID/name`. `getProtobuf` writes ACLs, metadata, object/update/parent IDs, and optional owner. `builderFromProtobuf` parses all persisted fields.

State and persistence behavior: Stored in OM directory table for FSO layout. Metadata, ACLs, object IDs, and parent IDs are persisted through protobuf codec.

Dependencies and integration points: Integrates with FSO path resolution, directory table updates, key-to-directory conversion, `OzoneAclUtil`, and `KeyValueUtil`.

Risks: Builder from `OmKeyInfo` does not set owner from key info in the visible constructor path, so callers should verify owner expectations. `getPath` is object-ID based, not a user full path.

Test signals: Directory codec round trips, ACL/metadata persistence, conversion to/from `OmKeyInfo`, parent/object ID identity, and FSO path lookup behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmDirectoryInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmKeyArgs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmKeyArgs.java

Purpose: Request argument object for key operations such as create/open/commit/read/head, carrying key identity, replication, size, block locations, ACLs, metadata, tags, multipart fields, and conditional update fields.

Important APIs/types/functions: Extends `WithMetadata` and implements `Auditable`. Builder sets volume/bucket/key/owner/data size/replication/location info, multipart upload ID and part number, recursive/head flags, datanode sort flag, latest-version request flag, force container cache refresh, expected data generation, expected ETag, ACLs, tags, and metadata. `toAuditMap`, `toBuilder`, `addLocationInfo`, and `toProtobuf` are primary methods.

Control flow and state: `dataSize` and `locationInfoList` are mutable after build for commit/update flows. `toProtobuf` serializes only the subset needed by `KeyArgs`, including conditional generation/ETag and part number when nonzero; metadata, ACLs, tags, and replication are handled in higher-level request protos or server-side state.

State and persistence behavior: Request state only. It is transformed into `OmKeyInfo` and table updates by OM request handlers.

Dependencies and integration points: Used across OM key RPC request paths, audit logging, multipart commit, and optimistic concurrency checks. Depends on `ReplicationConfig`, `OmKeyLocationInfo`, `AclListBuilder`, `MapBuilder`, and Ozone constants.

Risks: Request object exposes mutable location list references. `toProtobuf` omits some local fields, so callers must not assume every builder field survives a `KeyArgs` round trip. Conditional update fields must be validated by request handlers.

Test signals: Audit map contents, `KeyArgs` serialization for flags and conditional fields, multipart part number handling, mutable location-list update paths, and builder copy behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmKeyArgs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmKeyInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmKeyInfo.java

Purpose: Authoritative key metadata model for OM key/open-key/deleted-key tables and key RPC responses.

Important APIs/types/functions: Extends `WithParentObjectId`, implements `Auditable` and `CopyObject`. `CODEC` persists `KeyInfo` protobuf with pipeline omitted for DB storage. Fields include volume, bucket, key name, size, key-location versions, times, replication config, encryption info, checksum, file flag/name, owner, ACLs, tags, metadata, object/update/parent IDs, and expected generation. Core methods include `updateLocationInfoList`, `appendNewBlocks`, `addNewVersion`, `getProtobuf`, `getNetworkProtobuf`, `builderFromProtobuf`, conversion to/from `OmDirectoryInfo`, and ETag helpers.

Control flow and state: Commit-time `updateLocationInfoList` verifies committed block IDs against allocated blocks unless explicitly skipped, returns uncommitted allocations for deletion, replaces latest-version blocks, and marks multipart status. `appendNewBlocks` mutates the latest version; `addNewVersion` appends a new version or clears old versions based on `keepOldVersions`. Several setters mutate key name, size, modification time, replication config, encryption info, and expected generation.

State and persistence behavior: Persisted as `KeyInfo` protobuf in OM RocksDB. DB serialization can ignore pipelines, while network serialization includes them and can include only latest version blocks. Metadata, tags, ACLs, object IDs, parent IDs, encryption info, checksums, and replication config round trip through protobuf.

Dependencies and integration points: Central to key create/commit/read/delete, FSO directories, snapshots, replication/quota accounting, block token/pipeline return, and multipart part conversion. Depends on HDDS block/location classes, Ozone ACL/protobuf helpers, replication configs, checksums, encryption, and codecs.

Risks: The class is mutable and often shared through table/cache layers; copy discipline matters. Block verification compares container block IDs only, intentionally ignoring pipeline/BCS differences. `equals`/`hashCode` are narrower than full metadata identity. Missing replication config or malformed location versions can fail serialization.

Test signals: Codec round trips with/without pipelines, EC and legacy replication, encrypted keys, ACL/tag/metadata persistence, block commit verification and uncommitted-block return, append/new-version behavior, latest-version network serialization, FSO directory conversion, ETag helpers, and copy-object isolation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmKeyInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmKeyLocationInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmKeyLocationInfo.java

Purpose: OM wrapper around HDDS `BlockLocationInfo` representing one block/subkey location for a key.

Important APIs/types/functions: Builder fluently sets block ID, pipeline, length, offset, block token, multipart part number, and create version. `getProtobuf` emits `KeyLocation`, optionally omitting pipeline/token fields. `getFromProtobuf` reconstructs block ID, length, offset, pipeline, token, create version, and part number.

Control flow and state: Serialization always writes block ID, length, offset, create version, and part number. When `ignorePipeline` is false, it includes token and pipeline if present. Pipeline can be null for older key versions.

State and persistence behavior: Embedded in `OmKeyInfo` and multipart part protobufs. DB codecs typically omit pipeline data to avoid persisting volatile pipeline state; network responses include it.

Dependencies and integration points: Used by key block allocation/commit/read responses, `OmKeyLocationInfoGroup`, and multipart part metadata. Depends on HDDS block/pipeline/token types and `OMPBHelper`.

Risks: Null block ID would fail serialization. Persisted data without pipeline must be refreshed or tolerated by clients depending on operation.

Test signals: Proto round trips with token/pipeline present and omitted, create-version/part-number preservation, and DB vs network serialization differences.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmKeyLocationInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmKeyLocationInfoGroup.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmKeyLocationInfoGroup.java

Purpose: Represents one key version's block-location lists, grouped by block create version.

Important APIs/types/functions: Constructors accept a version plus list or map of `OmKeyLocationInfo`. Accessors expose latest-version-only blocks, all blocks, collection views, counts, and multipart flag. `getProtobuf`/`getFromProtobuf` convert to `KeyLocationList`. Package methods `generateNextVersion`, `appendNewBlocks`, `removeBlocks`, and `addAll` are used by `OmKeyInfo`.

Control flow and state: Constructors group list entries by each block's create version and ensure the group version has at least an empty list. `generateNextVersion` creates a map containing only new blocks at `version + 1`. `appendNewBlocks` stamps incoming blocks with the current version.

State and persistence behavior: Embedded inside persisted `OmKeyInfo` and multipart part metadata. Protobuf stores the group version, multipart flag, and flattened key-location list; deserialization regroups by create version.

Dependencies and integration points: Used by key versioning, block commit, multipart keys, and read/list responses.

Risks: `getLocationVersionMap` exposes the mutable internal map. HashMap iteration can make serialized key-location ordering non-deterministic unless callers use ordering-insensitive comparisons. Deprecated version-specific getter can return null-backed copies if the version is absent.

Test signals: Grouping by create version, protobuf round trip, append/new-version semantics, multipart flag persistence, count/list methods, and mutation exposure expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmKeyLocationInfoGroup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartAbortInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartAbortInfo.java

Purpose: Aggregates the OM DB keys and metadata needed to abort a multipart upload.

Important APIs/types/functions: Builder sets multipart key, multipart open key, `OmMultipartKeyInfo`, and `BucketLayout`. Getters expose all fields. Equality/hash include all fields.

Control flow and state: Immutable after build. No validation in builder.

State and persistence behavior: Does not persist itself; it carries identifiers and persisted multipart metadata used by abort request processing to remove table entries and cleanup blocks.

Dependencies and integration points: Used by multipart abort logic across legacy/object-store/FSO layouts.

Risks: Equality assumes non-null fields and will throw if partially built objects are compared. Missing bucket layout can break caller table selection.

Test signals: Abort request tests should verify correct multipart key/open-key selection for each layout, metadata cleanup, and equality for complete objects.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartAbortInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartCommitUploadPartInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartCommitUploadPartInfo.java

Purpose: Response DTO for committing one multipart upload part.

Important APIs/types/functions: Constructor sets part name and ETag; getters expose both.

Control flow and state: Immutable after construction.

State and persistence behavior: Response only. The actual part metadata is persisted through multipart key/part tables.

Dependencies and integration points: Returned by commit-multipart-part request handling and used by S3 MPU APIs.

Risks: No validation of part name or ETag.

Test signals: Commit-part response tests should verify ETag and part name propagation, including overwrite/recommit cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartCommitUploadPartInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartInfo.java

Purpose: Response DTO for initiating a multipart upload.

Important APIs/types/functions: Constructor stores volume, bucket, key, and upload ID. Deprecated getters expose volume, bucket, and key; `getUploadID` is the main current accessor.

Control flow and state: Simple mutable-field DTO with no setters.

State and persistence behavior: Response only. Initiation state is persisted elsewhere as multipart metadata.

Dependencies and integration points: Used by initiate multipart upload APIs, including older clients that still read volume/bucket/key fields.

Risks: Deprecated fields remain for compatibility. No validation of upload ID or names.

Test signals: Initiate MPU response tests should verify upload ID and backward-compatible field values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartKeyInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartKeyInfo.java

Purpose: Persisted metadata for an in-progress multipart upload.

Important APIs/types/functions: Extends `WithObjectID`, implements `CopyObject`, and persists via `MultipartKeyInfo` protobuf `CODEC`. Fields include upload ID, optional volume/bucket/key/owner, ACLs, creation time, replication config, parent ID, schema version, and a sorted `PartKeyInfoMap`. `PartKeyInfoMap` keeps `PartKeyInfo` values sorted by part number with binary-search get/put. Builder sets all fields. `getProto` and `builderFromProto` handle serialization.

Control flow and state: Schema version controls part storage. Version 0 stores part info inline in `MultipartKeyInfo`; version 1 requires the inline map to be empty because parts are stored in the separate multipart parts table. `addPartKeyInfo` rejects schema version 1 and replaces/positions parts by part number for version 0.

State and persistence behavior: Stored in the OM multipart info table. Object/update/parent IDs and replication config persist with upload metadata. Copy construction reuses immutable ACL and part-map references safely.

Dependencies and integration points: Used by MPU initiate, commit part, complete, abort, and list operations. Depends on `PartKeyInfo` protobuf, replication config, ACL utilities, and object ID base class.

Risks: Equality/hash use upload ID only, so two entries with the same upload ID but different key context compare equal. Schema-version misuse throws at runtime. Builder for schema 1 intentionally drops inline part info from proto.

Test signals: Codec round trips for schema 0 and schema 1, sorted part insertion/replacement, part lookup, schema 1 rejection of inline parts, replication config serialization, object/update/parent ID persistence, and copy-object behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartKeyInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartPartInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartPartInfo.java

Purpose: Persisted metadata for one multipart upload part, used by the schema-version-1 multipart parts table and conversion from committed part `OmKeyInfo`.

Important APIs/types/functions: `CODEC` delegates to `MultipartPartInfo`. Builder sets part name/number, size, modification time, object/update IDs, key-location groups, ETag, encryption info, and checksum. `getProto`, `getFromProto`, and `from(partName, partNumber, OmKeyInfo)` are primary conversion APIs.

Control flow and state: `getProto` validates required fields: nonblank part name and ETag, positive part number and modification time, nonnegative size, and nonempty key locations. Parsing validates required proto fields and logs warnings for missing object/update IDs while still reading default values. Only the first key-location group is serialized for the part.

State and persistence behavior: Stored as protobuf in the multipart parts table. It persists block locations with pipeline omitted, object/update IDs, encryption info, checksum, size, time, and ETag.

Dependencies and integration points: Used by MPU commit/list/complete in newer schema. Depends on `OmKeyInfo`, `OmKeyLocationInfoGroup`, `OMPBHelper`, `ClientVersion`, and Ozone ETag metadata.

Risks: `from` requires the source `OmKeyInfo` to have an ETag or builder validation fails. Multiple key-location groups are reduced to the first during serialization. Missing object/update IDs are warning-only, preserving compatibility but risking weak identity data.

Test signals: Codec round trips, required-field validation, conversion from `OmKeyInfo`, encrypted/checksummed part persistence, object/update ID warnings, and part-number/ETag validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartPartInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartPartKey.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartPartKey.java

Purpose: Typed RocksDB key for multipart part rows and prefix scans.

Important APIs/types/functions: `of(uploadId, partNumber)` creates a full key; `prefix(uploadId)` creates an iteration prefix. `getCodec` returns a custom codec supporting `CodecBuffer`. Encoding is `uploadId` UTF-8 bytes, `/`, and optional big-endian int32 part number.

Control flow and state: Decode determines whether raw bytes are a full key or prefix by checking the separator before the 4-byte suffix first, then trailing separator. This avoids misclassifying part numbers whose low byte equals `/`. Invalid/missing separators throw `CodecException`.

State and persistence behavior: Used as persisted key bytes in the multipart parts table. Prefix keys are valid only for scans, not complete row identity.

Dependencies and integration points: Integrates with HDDS DB codec APIs, `CodecBuffer`, and `StringCodec`. Used by MPU schema version 1 part storage and prefix iteration.

Risks: Upload IDs containing `/` are supported because decode uses the last separator implied by suffix length, but malformed data can still throw. Big-endian integer ordering preserves numeric ordering only for positive part numbers in normal MPU range.

Test signals: Codec round trips for prefix and full keys, part number 47 low-byte separator case, invalid empty/missing separator data, CodecBuffer path, and RocksDB prefix scan ordering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartPartKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUpload.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUpload.java

Purpose: Listing/identity DTO for one initialized multipart upload.

Important APIs/types/functions: Constructors store volume, bucket, key, upload ID, optional creation time, and optional replication config. `from(String dbKey)` parses legacy DB key format. `getDbKey` and static `getDbKey` build `/volume/bucket/key/uploadId` keys. Equality/hash are based on upload ID.

Control flow and state: `from` splits the key on `/`, validates at least five segments, derives upload ID from the last segment, volume/bucket from leading segments, and reconstructs key name by substring to preserve embedded separators.

State and persistence behavior: Represents rows from multipart upload tables and list responses. DB key format is string-based with slash separators.

Dependencies and integration points: Used by list multipart uploads and legacy multipart DB key handling. Depends on `ReplicationConfig`.

Risks: Equality by upload ID ignores volume/bucket/key; uniqueness must be global for this to be safe. Parsing assumes a leading slash and enough segments; malformed keys throw.

Test signals: DB key build/parse round trips with keys containing slashes, creation time/replication config propagation, equality semantics, and malformed key rejection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUpload.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUploadCompleteInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUploadCompleteInfo.java

Purpose: Response DTO for completing a multipart upload.

Important APIs/types/functions: Constructor stores volume, bucket, key, and hash/ETag. Deprecated getters expose volume/bucket/key; setters allow mutation. `getHash`/`setHash` expose the completion ETag.

Control flow and state: Mutable response object with no validation.

State and persistence behavior: Response only. Completed key metadata is persisted through normal key tables.

Dependencies and integration points: Used by complete MPU APIs and S3 ETag response mapping.

Risks: Mutable fields and deprecated accessors remain for compatibility. No validation of ETag/hash.

Test signals: Complete MPU response should verify ETag/hash and backward-compatible name fields.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUploadCompleteInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUploadCompleteList.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUploadCompleteList.java

Purpose: Holds the client-supplied part list for a complete multipart upload request.

Important APIs/types/functions: Constructor copies the supplied part-number to ETag map into a `LinkedHashMap`. `getMultipartMap` exposes it. `getPartsList` converts entries to protobuf `Part` messages, setting both `partName` and `eTag` to the ETag for backward compatibility.

Control flow and state: Iterates insertion order of the linked map when building the part list.

State and persistence behavior: Request helper only. The generated `Part` list is consumed by OM MPU completion logic to validate and combine persisted parts.

Dependencies and integration points: Used by complete MPU request paths and Ozone Manager protocol `Part`.

Risks: `getMultipartMap` exposes mutable internal map. No sorting is applied, so caller-provided order matters unless downstream sorts/validates. Null ETags can fail protobuf construction.

Test signals: Part-list conversion order, backward-compatible partName equals ETag, mutable map expectations, and completion validation for sorted/unsorted part maps.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUploadCompleteList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUploadList.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUploadList.java

Purpose: Result container for listing in-flight multipart uploads.

Important APIs/types/functions: Builder sets uploads, next key marker, next upload ID marker, and truncation flag. Accessors expose all fields; `setUploads` can replace the upload list.

Control flow and state: Simple mutable result object. Marker defaults are empty strings.

State and persistence behavior: List response only. Upload entries are derived from multipart metadata tables.

Dependencies and integration points: Used by list multipart uploads APIs for pagination.

Risks: Upload list is not defensively copied and can be null. Mutable setter allows response mutation after construction.

Test signals: Pagination marker propagation, truncation flag, empty results, mutable list behavior, and list ordering from caller code.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUploadList.java -->
