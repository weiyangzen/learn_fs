# Research: subset-b-008056

This grouped report covers the Apache Ozone client object-store API, checksum helpers, and selected block stream output entries. Each section is bounded for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/ObjectStore.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/ObjectStore.java

### Purpose
`ObjectStore` is the top-level object-store facade exposed from `OzoneClient`. It owns a `ClientProtocol` proxy and offers volume, S3 bucket, tenant, ACL, delegation-token, snapshot, compaction DAG, and snapshot-diff operations. The class is deliberately thin: it converts client-facing operations into `ClientProtocol` calls, adds paged iterators for list APIs, and handles a few compatibility or error-mapping cases.

### Important APIs and Types
- Construction captures `ClientProtocol`, list cache size from `HddsClientUtils`, and S3 default bucket layout from `OzoneConfigKeys.OZONE_S3G_DEFAULT_BUCKET_LAYOUT_KEY`.
- Volume APIs: `createVolume`, `getVolume`, `listVolumes`, `listVolumesByUser`, `deleteVolume`.
- S3 APIs: `createS3Bucket`, `getS3Bucket`, `deleteS3Bucket`, S3 secret getters/setters/revoke, and `getS3VolumeContext`.
- Tenant APIs: create/delete tenant, assign/revoke user access IDs, assign/revoke tenant admins, list users, get user info, list tenants.
- ACL APIs delegate `addAcl`, `removeAcl`, `setAcl`, and `getAcl` for generic `OzoneObj`.
- Snapshot APIs cover create/rename/delete/get/list snapshots and sync or async snapshot-diff operations.
- Nested iterators: `VolumeIterator`, `SnapshotIterator`, and `SnapshotDiffJobIterator` implement paged remote listing.

### Control Flow
Most methods are one-hop delegations to `proxy`. `createS3Bucket` first resolves the S3 volume, then creates the bucket with the configured S3 bucket layout; if OM reports `NOT_SUPPORTED_OPERATION_PRIOR_FINALIZATION`, it retries with `BucketLayout.LEGACY` for pre-finalized clusters. `deleteS3Bucket` maps a missing S3 volume to `BUCKET_NOT_FOUND`, matching bucket-level semantics for S3 clients. The list iterators fetch an initial page in the constructor, then call the appropriate proxy list method again when the current page is exhausted and a last value or continuation marker exists.

### State and Persistence Behavior
The only local mutable state is `listCacheSize` and `s3BucketLayout`; durable state is maintained by Ozone Manager through `ClientProtocol`. Iterator state is in-memory and includes the last returned volume, snapshot, or snapshot-diff job marker. Delegation tokens and S3 secrets are returned from server-side security services and are not cached locally here.

### Dependencies and Integration Points
This class integrates with `ClientProtocol`, `OzoneVolume`, `OzoneBucket`, OM helper DTOs, Hadoop security token classes, `UserGroupInformation`, `OzoneAcl`, snapshot response types, and S3/tenant helper types. It is the primary bridge from external client code into OM RPC behavior. The default S3 bucket layout is validated through `OmUtils.validateBucketLayout`.

### Risks and Edge Cases
Iterator `hasNext()` wraps `IOException` in `RuntimeException` for volumes but logs and suppresses next-page errors for snapshots and snapshot diff jobs, which can hide remote failures behind short iteration. `createS3Bucket` has intentionally broad compatibility behavior but only handles the specific pre-finalization result code. `listVolumesByUser` resolves an empty user to the current short user name, so tests need a controlled UGI context.

### Test Signals
Useful tests cover paged list iteration across cache boundaries, S3 bucket layout fallback, S3 volume-not-found mapping, tenant delegation paths, snapshot list pagination, snapshot-diff job pagination, and delegation-token proxy forwarding. Mock `ClientProtocol` tests are sufficient for most behavior because the class has limited local logic.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/ObjectStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneBucket.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneBucket.java

### Purpose
`OzoneBucket` is the client-side representation and operation facade for a bucket inside a volume. It exposes bucket metadata, ACLs, quota and replication configuration, key CRUD, stream-key creation, multipart upload, file-system style APIs, object tagging, owner updates, and key listing for both object-store and file-system-optimized bucket layouts.

### Important APIs and Types
- Core state: `volumeName`, `name`, `defaultReplication`, `storageType`, `versioning`, usage/quota counters, timestamps, encryption key name, link source fields, `BucketLayout`, owner, pending-delete counters, and an `OzoneObj` for ACL operations.
- Mutating bucket APIs: `setStorageType`, `setVersioning`, `clearSpaceQuota`, `clearNamespaceQuota`, `setQuota`, `setReplicationConfig`, `setEncryptionKey`, `setOwner`.
- Key write APIs: `createKey`, deprecated type/factor overloads, conditional `rewriteKey`, `createKeyIfNotExists`, `rewriteKeyIfMatch`, stream variants, and multipart-part stream creation.
- Key read/list/delete APIs: `readKey`, `getKey`, `headObject`, `listKeys`, `deleteKey`, `deleteDirectory`, `deleteKeys`, `renameKey`, deprecated `renameKeys`.
- File-system APIs: `getFileStatus`, `createDirectory`, `readFile`, `createFile`, `createStreamFile`, `listStatus`, and `listStatusLight`.
- Multipart APIs: initiate, create part, complete with optional conditional generation/ETag, abort, list parts, and list uploads.
- Nested types: `Builder`, `KeyIterator`, `KeyIteratorWithFSO`, and `KeyIteratorFactory`.

### Control Flow
Most public operations directly delegate to `ClientProtocol`, then update local cached fields only after successful mutations. Quota clear methods first fetch fresh bucket details to preserve the quota dimension that is not being cleared. Key creation defaults to bucket replication unless explicit replication is provided; stream creation normalizes null replication back to the bucket default.

`listKeys` chooses a normal `KeyIterator` or FSO-aware `KeyIteratorWithFSO` based on `bucketLayout.isFileSystemOptimized()`. The normal iterator pages through `proxy.listKeys`, and its shallow mode uses `listStatusLight` to avoid recursively listing all descendants. It calculates a delimiter prefix, fetches a first key by `listKeys` when needed, includes the prefix object for delimiter semantics, and converts `OzoneFileStatusLight` to `OzoneKey`.

`KeyIteratorWithFSO` implements depth-first traversal over file-system-optimized directory metadata. It builds a stack of `(prefix,startKey)` pairs from the requested prefix and previous key, calls `listStatusLight` for immediate children, pushes sibling and child paths back onto the stack, and removes internal placeholder start keys so list-key semantics match object-store expectations. Its shallow mode additionally adjusts the start key to an immediate child and checks whether a prefix exists when no first start key is found.

### State and Persistence Behavior
`OzoneBucket` caches bucket metadata at construction and updates a subset of fields after successful proxy mutations. Actual bucket, key, multipart, ACL, tag, and file-system state persists in OM and DataNodes. Iterator state is local: current page iterator, last current value, delimiter prefix flags, DFS stack, and internal `removeStartKey`. Link buckets track `sourceVolume`, `sourceBucket`, and `sourcePathExist`; utility code may set `sourcePathExist` to false for orphan links.

### Dependencies and Integration Points
The class depends heavily on `ClientProtocol`, OM helper types (`OmKeyInfo`, `OmMultipartInfo`, `OzoneFileStatus`, `OzoneFileStatusLight`, `ErrorInfo`), HDDS replication/storage types, `OzoneDataStreamOutput`, `OzoneInputStream`, `OzoneOutputStream`, `OzoneObjInfo`, and `OzoneFSUtils`. It is a central integration point for object-store users, S3 gateway semantics, Ozone FS APIs, and multipart upload flows.

### Risks and Edge Cases
The FSO and shallow list algorithms are complex and rely on lexicographic path comparisons, normalized keys, trailing slash handling, and `listStatusLight` including or excluding start keys in specific ways. Regressions can cause duplicates, skipped prefixes, infinite pagination, or incorrect directory marker behavior. Local cached fields may become stale if other clients mutate bucket settings. `setOwner` updates local owner regardless of the boolean result from the proxy. The public constructors/builders do little validation beyond requiring a non-null proxy in `newBuilder`.

### Test Signals
High-value tests include normal and FSO `listKeys` pagination, shallow delimiter listing with prefixes ending with and without `/`, previous-key continuation inside nested directories, prefix-as-directory inclusion, file-vs-directory conversion to `OzoneKey`, quota clear preserving the other quota dimension, conditional write delegation, multipart completion with conditions, object tagging round trips, and stale-cache expectations after external mutation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneBucket.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneClient.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneClient.java

### Purpose
`OzoneClient` is the closeable client root that binds a `ClientProtocol` proxy, `ConfigurationSource`, and `ObjectStore` facade. It is normally created by `OzoneClientFactory` and gives callers access to object-store operations and the underlying proxy.

### Important APIs and Types
The public constructor accepts `ConfigurationSource` and `ClientProtocol`, creates a new `ObjectStore`, and registers leak tracking through `OzoneClientFactory.track(this)`. Public APIs are `getObjectStore`, `getConfiguration`, `close`, and `getProxy`. A protected testing constructor injects an `ObjectStore` and `ClientProtocol`.

### Control Flow
Construction is straightforward: store the proxy, create the `ObjectStore`, store the configuration, and initialize leak tracking. `close()` closes the proxy and always closes the leak tracker in a `finally` block.

### State and Persistence Behavior
The class owns local references only. It does not persist data itself. Correct lifecycle behavior matters because the proxy owns RPC/network resources and the leak detector reports clients not closed by callers.

### Dependencies and Integration Points
It integrates `ClientProtocol`, `ObjectStore`, `OzoneConfiguration`, and Ratis `UncheckedAutoCloseable`. It is the root type returned by factory methods and used by application code.

### Risks and Edge Cases
If clients do not call `close`, the leak detector should report creation stack traces. If `proxy.close()` throws, leak tracking is still closed. The testing constructor creates a default `OzoneConfiguration`, which may hide configuration-sensitive behavior in tests that use it.

### Test Signals
Tests should verify object-store/proxy identity, close ordering with failing proxy close, leak-tracker close behavior indirectly, and factory-created clients wiring `ObjectStore` to the same proxy.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneClientException.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneClientException.java

### Purpose
`OzoneClientException` is a client-specific checked exception that extends `IOException`. It provides constructors matching the common Java exception shapes.

### Important APIs and Types
Constructors support no-arg, message-only, message-plus-cause, and cause-only initialization. No extra fields or behavior are added.

### Control Flow
There is no operational control flow beyond superclass constructor calls.

### State and Persistence Behavior
The exception stores standard `Throwable` state only. It has no persistence effects.

### Dependencies and Integration Points
It integrates with Java I/O exception handling and can be used by Ozone client APIs without forcing a non-IO checked exception hierarchy.

### Risks and Edge Cases
The class has no `serialVersionUID`, which can trigger serialization warnings but is common for simple exceptions. Because it adds no structured result code, callers needing OM-specific causes must inspect wrapped exceptions.

### Test Signals
Constructor tests can verify message and cause propagation, although coverage value is low unless serialization or public API compatibility is under review.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneClientException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneClientFactory.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneClientFactory.java

### Purpose
`OzoneClientFactory` centralizes construction of RPC-based `OzoneClient` instances, HA service-id resolution, token renewal/cancel client routing, and client leak tracking.

### Important APIs and Types
- `track(AutoCloseable)` registers objects with `LeakDetector` and captures stack traces through `HddsUtils`.
- `getRpcClient()` creates a client using a new `OzoneConfiguration`.
- `getRpcClient(String omHost, Integer omRpcPort, MutableConfigurationSource)` validates and writes `ozone.om.address`.
- `getRpcClient(String omServiceId, ConfigurationSource)` creates a HA client only when the service ID is configured.
- `getRpcClient(ConfigurationSource)` selects no service ID, the single configured service ID, or errors when multiple service IDs require caller disambiguation.
- `getOzoneClient(Configuration, Token<OzoneTokenIdentifier>)` decodes a token identifier and routes token renew/cancel clients based on token OM service ID and local HA configuration.
- Private `getClientProtocol` creates `RpcClient` and unwraps `RemoteException` or `IOException` causes.

### Control Flow
Factory methods validate required parameters with `Objects.requireNonNull`, inspect OM service-id settings, and construct `RpcClient` before wrapping it in `OzoneClient`. Token routing handles four key cases: token with default service ID on non-HA/single-node Ratis HA, token service ID matching configured HA, token service ID mismatching configured HA, and old tokens without service IDs. Mismatches produce explicit `IOException`s to avoid renewing against the wrong OM cluster.

### State and Persistence Behavior
The factory has static leak-detector state only. It mutates provided mutable configuration in the host/port overload by setting `OZONE_OM_ADDRESS_KEY`; otherwise it creates clients without persistent local state.

### Dependencies and Integration Points
It depends on `RpcClient`, OM config keys, `OmUtils`, Hadoop `Configuration`, `OzoneConfiguration`, `Token<OzoneTokenIdentifier>`, `RemoteException`, and HDDS leak utilities. It is the canonical entry point for creating `OzoneClient`.

### Risks and Edge Cases
Multiple configured HA service IDs require explicit caller selection; this avoids ambiguity but may break clients expecting fallback. Token renewal for old tokens without service IDs is intentionally rejected in local HA configurations. The host/port overload mutates the caller-provided configuration, so tests and callers should account for side effects. Error unwrapping preserves remote IO causes but wraps other exceptions in a generic message.

### Test Signals
Tests should cover service-id selection, multiple-service-id errors, host/port config mutation, token routing for default/matching/mismatched/no-service-id tokens, `RpcClient` exception unwrapping, and leak tracking registration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneClientFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneClientUtils.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneClientUtils.java

### Purpose
`OzoneClientUtils` collects shared client helpers for link-bucket layout resolution, replication config selection, checksum dispatch, key property checks, list limit clamping, and best-effort snapshot cleanup.

### Important APIs and Types
- `resolveLinkBucketLayout` recursively follows link buckets to the source bucket layout and detects loops with a visited pair set.
- `resolveClientSideReplicationConfig` chooses effective replication for file-system APIs from API short replication, client config, and bucket defaults.
- `getClientConfiguredReplicationConfig` and `validateAndGetClientReplicationConfig` parse replication settings from Ozone configuration and explicit user parameters.
- `getFileChecksumWithCombineMode` builds `OmKeyArgs`, looks up `OmKeyInfo`, selects a checksum helper via `ChecksumHelperFactory`, computes, and returns `FileChecksum`.
- `isKeyErasureCode`, `isKeyEncrypted`, `limitValue`, and `deleteSnapshot` provide focused utility behavior.

### Control Flow
Link resolution checks `bucket.isLink()`, records visited `(volume,bucket)` pairs, fetches source volume/bucket through `ObjectStore`, handles missing source volume/bucket as an orphan link by marking `sourcePathExist=false`, and recurses if the source is also a link. Replication resolution gives EC bucket defaults priority because file-system APIs cannot express EC replication, otherwise honors supported short replication values of ONE or THREE, client defaults, and server-side fallback. Checksum calculation forces latest version locations and sorted datanodes, then delegates to EC or replicated helpers.

### State and Persistence Behavior
The utility class is stateless. It can mutate the passed `OzoneBucket` only in the orphan link case by setting `sourcePathExist` false. `deleteSnapshot` attempts a server-side delete and logs failures without rethrowing.

### Dependencies and Integration Points
It integrates with `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `ClientProtocol`, OM lookup types, HDDS replication config parsing, `OzoneClientConfig.ChecksumCombineMode`, and checksum helper implementations.

### Risks and Edge Cases
Loop detection depends on the caller-supplied visited set and must be initialized correctly. Orphan links return the link bucket's layout, which keeps clients functioning but can mask source deletion until callers inspect `sourcePathExist`. `limitValue` enforces a minimum of two to avoid list-status infinite loops when start keys are echoed. Replication parsing can throw if configuration values are invalid enum names.

### Test Signals
Tests should cover link chains, link loops, orphan link handling, EC bucket default precedence, supported/unsupported short replication values, user-vs-client replication priority, checksum helper selection, encrypted/EC predicates, and `limitValue` max/min clamping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneClientUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneKey.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneKey.java

### Purpose
`OzoneKey` is a client-visible value object for key metadata: volume, bucket, key name, owner, size, timestamps, replication config, metadata, tags, and whether the key represents a file.

### Important APIs and Types
Constructors accept primitive key fields and optionally metadata/tags. Getters expose all fields. Deprecated `getReplicationType` and `getReplicationFactor` adapt `ReplicationConfig` to legacy client APIs. `fromKeyInfo` converts OM `OmKeyInfo` into `OzoneKey`.

### Control Flow
Construction converts epoch-millis timestamps to `Instant`, stores final identity fields, and copies metadata/tags into mutable internal maps. `fromKeyInfo` pulls all public fields from OM key info.

### State and Persistence Behavior
This is an in-memory DTO. Metadata and tags maps returned by getters are mutable, so callers can alter local object state after construction. No changes persist to OM unless passed through separate APIs.

### Dependencies and Integration Points
It depends on HDDS `ReplicationConfig`, legacy replication types, Jackson `JsonIgnore` for deprecated compatibility getters, and OM `OmKeyInfo`. It is returned by `OzoneBucket.headObject`, list-key paths, and conversion helpers.

### Risks and Edge Cases
Mutable metadata/tag getters can surprise callers expecting immutable DTO behavior. Deprecated replication getters assume `replicationConfig` is non-null. Consumers should prefer `getReplicationConfig`.

### Test Signals
Tests should verify `fromKeyInfo` conversion, metadata/tag copying, legacy replication getter behavior for replicated and EC configs, and JSON serialization exclusion of deprecated getters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneKeyDetails.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneKeyDetails.java

### Purpose
`OzoneKeyDetails` extends `OzoneKey` with block location details, file encryption information, a lazy content stream supplier, and optional generation used for atomic rewrite/conditional commit semantics.

### Important APIs and Types
The constructors accept key metadata plus `List<OzoneKeyLocation>`, `FileEncryptionInfo`, `CheckedSupplier<OzoneInputStream, IOException>`, tags, owner, and optional generation. Getters expose locations, encryption info, generation, and `getContent()`. `hasEtag` and `isEtagEquals` implement ETag checks.

### Control Flow
`getContent()` calls the checked supplier each time it is invoked, allowing content stream creation to be lazy. `isEtagEquals` returns false when the current ETag is missing, treats expected `"*"` as a wildcard when an ETag exists, and otherwise performs string equality.

### State and Persistence Behavior
This is an in-memory detail DTO. The content supplier may create network-backed streams, but this class does not own their lifecycle beyond returning them. Generation and ETag metadata represent server state at lookup time and may become stale.

### Dependencies and Integration Points
It integrates with `OzoneInputStream`, Hadoop `FileEncryptionInfo`, Ratis checked suppliers, and `OzoneConsts.ETAG`. It is returned by `OzoneBucket.getKey` and used by conditional rewrite APIs.

### Risks and Edge Cases
The location list is returned directly, so callers can mutate local representation if the supplied list is mutable. ETag wildcard behavior requires an existing ETag; absent metadata never matches. The content supplier can throw `IOException` and may return a new stream or fail after key state has changed.

### Test Signals
Tests should cover lazy supplier invocation, supplier exception propagation, generation presence/absence, ETag wildcard and missing cases, and preservation of encryption/location details.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneKeyDetails.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneKeyLocation.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneKeyLocation.java

### Purpose
`OzoneKeyLocation` is a small immutable DTO describing one block location for a key: container ID, local block ID, length, block offset, and key offset.

### Important APIs and Types
The constructor sets `containerID`, `localID`, `length`, `offset`, and `keyOffset`. Getters expose each value.

### Control Flow
There is no behavior beyond construction and getters.

### State and Persistence Behavior
The object is immutable and local-only. It reflects OM block-location metadata at the time a key detail response was built.

### Dependencies and Integration Points
It is used by `OzoneKeyDetails` to expose data placement information to clients and diagnostic tools.

### Risks and Edge Cases
No validation prevents negative or inconsistent offsets/lengths; correctness depends on conversion code that builds the DTO from OM metadata.

### Test Signals
Tests are simple constructor/getter checks or conversion tests from OM location info in the code that creates `OzoneKeyDetails`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneKeyLocation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneMultipartUpload.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneMultipartUpload.java

### Purpose
`OzoneMultipartUpload` represents one in-flight multipart upload, including its volume, bucket, key, upload ID, creation time, and replication configuration.

### Important APIs and Types
It has a deprecated constructor for legacy replication type/factor and a current constructor taking `ReplicationConfig`. Getters expose identifiers, creation time, and replication config. Deprecated getters adapt replication config back to legacy type/factor.

### Control Flow
Construction stores values directly or converts legacy type/factor with `ReplicationConfig.fromTypeAndFactor`. `setCreationTime` allows updating creation time after construction.

### State and Persistence Behavior
This is a mutable local DTO because `creationTime` can be set. Upload state itself persists in OM and is manipulated through `OzoneBucket` multipart APIs.

### Dependencies and Integration Points
It integrates with HDDS replication types and is held by `OzoneMultipartUploadList`, returned by `listMultipartUploads`.

### Risks and Edge Cases
Legacy replication getters assume non-null replication config. Mutable creation time can desynchronize from server state if changed by callers.

### Test Signals
Tests should verify legacy conversion, current replication config preservation, and list-response serialization/compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneMultipartUpload.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneMultipartUploadList.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneMultipartUploadList.java

### Purpose
`OzoneMultipartUploadList` is the client-visible response wrapper for listing in-flight multipart uploads.

### Important APIs and Types
The constructor requires a non-null upload list and stores `nextKeyMarker`, `nextUploadIdMarker`, and `isTruncated`. Getters expose all fields, and `setUploads` can replace the list.

### Control Flow
The only validation is `Objects.requireNonNull(uploads)`. Pagination markers are passive values supplied by the server-side conversion path.

### State and Persistence Behavior
This is a mutable local DTO. Replacing uploads does not affect OM multipart state.

### Dependencies and Integration Points
It contains `OzoneMultipartUpload` objects and is returned from `OzoneBucket.listMultipartUploads` as S3-style pagination state.

### Risks and Edge Cases
`setUploads` does not enforce non-null after construction. The upload list is exposed directly, so callers can mutate it.

### Test Signals
Tests should verify null-constructor rejection, marker propagation, truncation flag propagation, and mutability expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneMultipartUploadList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneMultipartUploadPartListParts.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneMultipartUploadPartListParts.java

### Purpose
`OzoneMultipartUploadPartListParts` represents the response for listing parts of a multipart upload, including replication config, pagination marker, truncation flag, and per-part metadata.

### Important APIs and Types
Constructors accept legacy type/factor or current `ReplicationConfig`. `addAllParts`, `addPart`, and getters manage `partInfoList`. Deprecated replication getters expose legacy compatibility. Nested immutable `PartInfo` stores part number, part name, modification time, size, and ETag.

### Control Flow
Parts are appended to an initially empty `ArrayList`. No sorting or duplicate checks are performed locally; ordering and validity are expected from the server response.

### State and Persistence Behavior
This is a mutable response DTO. It does not persist part state; multipart part lifecycle is controlled by OM through bucket APIs.

### Dependencies and Integration Points
It uses HDDS replication types and is returned by `OzoneBucket.listParts`.

### Risks and Edge Cases
The exposed part list is mutable. Deprecated replication factor conversion relies on `ReplicationConfig.getLegacyFactor`, which may be less meaningful for EC configs. No validation prevents duplicate part numbers.

### Test Signals
Tests should cover add/addAll behavior, truncation and marker fields, ETag preservation, legacy and current replication getters, and response ordering as produced by conversion code.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneMultipartUploadPartListParts.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneSnapshot.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneSnapshot.java

### Purpose
`OzoneSnapshot` is a client-visible immutable snapshot metadata DTO for a bucket snapshot, including identity, status, UUID, paths, checkpoint directory, and referenced/exclusive size accounting.

### Important APIs and Types
The constructor stores volume, bucket, name, creation time, `SnapshotStatus`, `UUID`, snapshot path, checkpoint directory, referenced sizes, and exclusive sizes. `fromSnapshotInfo` converts OM `SnapshotInfo` and folds directory deep-cleaning deltas into exclusive sizes. It implements `equals`, `hashCode`, and `toString`.

### Control Flow
`fromSnapshotInfo` reads all fields from OM metadata and calls `getCheckpointDirName(0)`. Exclusive size getters represent base exclusive size plus deep-cleaning delta at conversion time.

### State and Persistence Behavior
The object is immutable and local-only. Snapshot metadata and size counters persist in OM and can change after this DTO is created, especially while deletion/deep-cleaning work progresses.

### Dependencies and Integration Points
It depends on `SnapshotInfo` and `SnapshotStatus` from OM helpers. It is returned by `ObjectStore.getSnapshotInfo` and `ObjectStore.listSnapshot`.

### Risks and Edge Cases
`getSnapshotStatus` returns the enum name as a string rather than the enum. `fromSnapshotInfo` hardcodes checkpoint directory index `0`. Equality includes all size fields, so two objects for the same snapshot can compare unequal if accounting changes.

### Test Signals
Tests should verify conversion from `SnapshotInfo`, inclusion of deep-cleaning deltas, equality/hash behavior, checkpoint directory selection, and status string compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneSnapshotDiff.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneSnapshotDiff.java

### Purpose
`OzoneSnapshotDiff` is a small DTO representing one snapshot diff job for a bucket.

### Important APIs and Types
Fields include volume, bucket, from snapshot, to snapshot, and `SnapshotDiffResponse.JobStatus`. `fromSnapshotDiffJob` converts OM `SnapshotDiffJob` into the client DTO.

### Control Flow
There is no behavior beyond storing constructor values and converting from OM job fields.

### State and Persistence Behavior
The object is immutable and local. Job status is a snapshot of OM state at list time and may change as async diff jobs progress.

### Dependencies and Integration Points
It is used by `ObjectStore.listSnapshotDiffJobs` and maps from `SnapshotDiffJob`.

### Risks and Edge Cases
There is no equality/hash implementation, so list comparisons need field assertions. Status staleness is expected for async jobs.

### Test Signals
Tests should verify conversion from OM job, field getters, and iterator integration in `ObjectStore`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneSnapshotDiff.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneVolume.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneVolume.java

### Purpose
`OzoneVolume` is the client-side representation and operation facade for an Ozone volume. It exposes volume metadata, ACL and quota mutations, owner changes, bucket create/get/list/delete operations, and ref-count information used by multi-tenancy or other locking features.

### Important APIs and Types
Core state includes `ClientProtocol`, name, admin, owner, quota bytes/namespace, used namespace, timestamps, ACL list, list cache size, `OzoneObj`, and `refCount`. Public methods expose getters, ACL mutation, owner/quota mutation, bucket operations, and `listBuckets`. The nested `Builder` constructs instances from OM data. `BucketIterator` pages through `proxy.listBuckets`.

### Control Flow
Mutating methods delegate to `ClientProtocol` and update local cached fields when successful. Quota clear methods fetch current volume details first so clearing one quota dimension preserves the other. `listBuckets` returns a `BucketIterator`, which fetches an initial page and then uses the last returned bucket name as the next `prevBucket` marker.

### State and Persistence Behavior
The object caches metadata locally but durable state is in OM. ACL changes update the local list only if the server reports success. `modificationTime` defaults to now when the builder supplies zero but is clamped not to precede creation time.

### Dependencies and Integration Points
It depends on `ClientProtocol`, `OzoneAcl`, `OzoneQuota`, `OzoneObjInfo`, `BucketArgs`, `OzoneBucket`, and `WithMetadata`. It is produced by `ObjectStore.getVolume` and used as the parent facade for bucket operations.

### Risks and Edge Cases
Cached state can become stale after external mutations. `setOwner` updates local owner regardless of the boolean result. `BucketIterator` wraps `IOException` in `RuntimeException`, so listing errors can surface outside checked-exception signatures. Builder fields such as ACL list should be populated by conversion paths; null ACLs would fail in constructor copy.

### Test Signals
Tests should cover ACL local cache updates, quota clear preserving the other quota, bucket listing across page boundaries, snapshot-filtered bucket listing, modification-time defaulting, ref-count getter, and owner update behavior when proxy returns false.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneVolume.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/TenantArgs.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/TenantArgs.java

### Purpose
`TenantArgs` encapsulates optional arguments for tenant creation: the backing volume name and whether creation should be forced when the volume already exists.

### Important APIs and Types
The immutable outer class exposes `getVolumeName` and `getForceCreationWhenVolumeExists`. `newBuilder` returns a mutable `Builder` with setters for both fields and `build`.

### Control Flow
`Builder.build()` requires `volumeName` to be non-null and constructs the immutable value.

### State and Persistence Behavior
This is an immutable client argument object. Tenant creation persistence occurs later through `ObjectStore.createTenant`.

### Dependencies and Integration Points
It is passed to `ObjectStore.createTenant(String, TenantArgs)` and then to `ClientProtocol.createTenant`.

### Risks and Edge Cases
Only null is rejected; empty or invalid volume names are left to lower layers. The force flag defaults to false.

### Test Signals
Tests should verify required volume name, default force flag, setter behavior, and propagation into tenant-create request conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/TenantArgs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/VolumeArgs.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/VolumeArgs.java

### Purpose
`VolumeArgs` is an immutable argument object for creating volumes with optional admin, owner, byte quota, namespace quota, ACLs, and metadata.

### Important APIs and Types
Fields include admin, owner, quota bytes, quota namespace, immutable ACL list, and immutable metadata map. The builder defaults both quotas to `OzoneConsts.QUOTA_RESET`, accumulates metadata and ACLs, and builds a `VolumeArgs`.

### Control Flow
The private constructor copies ACLs and metadata into Guava immutable collections, using empty immutable collections for null inputs. Builder setters simply record values; `addAcl` lazily creates the mutable list and can throw `IOException` because `OzoneAcl` APIs historically expose IO-shaped parsing/creation behavior.

### State and Persistence Behavior
The built object is immutable and local. Volume creation persistence is done by `ObjectStore.createVolume`.

### Dependencies and Integration Points
It integrates with `OzoneAcl`, `OzoneConsts`, Guava immutable collections, and `ObjectStore.createVolume`.

### Risks and Edge Cases
No validation is done for quota values, names, metadata keys, or ACL semantics. Builder remains mutable and can be reused after `build`; previous built instances are protected by immutable copies.

### Test Signals
Tests should verify default quotas, immutable collection behavior, metadata/ACL copy isolation, and propagation into create-volume request conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/VolumeArgs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/AbstractBlockChecksumComputer.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/AbstractBlockChecksumComputer.java

### Purpose
`AbstractBlockChecksumComputer` defines the minimal contract for computing a block-level checksum from chunk checksums under a selected checksum combine mode.

### Important APIs and Types
Subclasses implement `compute(OzoneClientConfig.ChecksumCombineMode)`. The base stores an output `ByteBuffer`, exposed by `getOutByteBuffer`, and provides `setOutBytes` to wrap result bytes.

### Control Flow
The base class has no checksum algorithm; callers invoke `compute`, then read the output buffer.

### State and Persistence Behavior
The only state is the computed output buffer. It is local and overwritten when subclasses call `setOutBytes`.

### Dependencies and Integration Points
It is used by `BaseFileChecksumHelper` and implemented by `ReplicatedBlockChecksumComputer` and `ECBlockChecksumComputer`.

### Risks and Edge Cases
The API does not enforce that `compute` was called before `getOutByteBuffer`. `setOutBytes` wraps the provided array without copying, so later array mutation could alter the buffer content if callers kept a reference.

### Test Signals
Tests should focus on subclass behavior and verify output buffer is set for each combine mode and rejected for unsupported modes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/AbstractBlockChecksumComputer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/BaseFileChecksumHelper.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/BaseFileChecksumHelper.java

### Purpose
`BaseFileChecksumHelper` orchestrates Ozone file checksum computation across key blocks. It fetches block locations, retrieves chunk checksum data through subclass hooks, computes per-block checksums, combines them into Hadoop-compatible file checksum results, and reuses cached OM checksums when possible.

### Important APIs and Types
Important fields include `OmKeyInfo`, `OzoneVolume`, `OzoneBucket`, key name, requested length, `ClientProtocol`, combine mode, checksum type, `DataOutputBuffer` for block checksums, `XceiverClientFactory`, `FileChecksum`, key location list, remaining requested bytes, bytes per CRC, and CRCs per block. Abstract hooks are `getBlockChecksumComputer` and `getChunkInfos`. Public `compute` and `getFileChecksum` drive the lifecycle.

### Control Flow
Construction stores context, obtains `XceiverClientFactory` by casting `ClientProtocol` to `RpcClient`, and fetches blocks when length is positive. `fetchBlocks` looks up latest key locations if no `OmKeyInfo` was provided, reuses `keyInfo.getFileChecksum()` for full-length reads, and stores latest-version block locations. `compute` returns cached checksum if available, returns the Hadoop empty-file MD5/CRC checksum for no blocks, otherwise calls `checksumBlocks` and creates the final result. `checksumBlock` gets chunk infos, determines checksum type and bytes-per-checksum from the first chunk, truncates by requested remaining length, delegates block checksum computation, and appends raw block checksum bytes according to the combine mode.

`makeFinalResult` supports `MD5MD5CRC` and `COMPOSITE_CRC`. MD5 mode digests the per-block MD5s and returns gzip or Castagnoli Hadoop checksum based on checksum type. Composite CRC mode composes block CRCs using `CrcComposer` and returns `CompositeCrcFileChecksum`.

### State and Persistence Behavior
The helper is stateful for one compute operation: remaining length decreases as blocks are processed, checksum buffer accumulates, and `fileChecksum` is set once. It does not persist server state. It reads OM metadata and DataNode block metadata.

### Dependencies and Integration Points
It integrates with OM lookup (`OzoneManagerProtocol.lookupKey`), DataNode checksum retrieval via subclasses, Hadoop `FileChecksum` classes, `MD5Hash`, `DataChecksum`, `CrcComposer`, `CrcUtil`, and `ChecksumHelperFactory`.

### Risks and Edge Cases
The direct cast to `RpcClient` means non-RPC `ClientProtocol` implementations are unsupported for checksum computation. `crcPerBlock` is never updated in this class, so MD5MD5CRC results may rely on legacy assumptions or subclass side effects that are not present here. The loop condition `remaining >= 0` allows processing when remaining is zero before early length checks stop future work. Composite CRC assumes four bytes per block checksum in the buffer. Cached OM checksum is reused only for full-length reads.

### Test Signals
Tests should cover cached full-length checksum reuse, zero-length/empty-key checksum result, partial length computation, MD5MD5CRC for CRC32 and CRC32C, composite CRC composition across multiple blocks, failure on empty chunk infos, unsupported checksum/combine modes, and behavior with mocked/non-RPC `ClientProtocol`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/BaseFileChecksumHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/ChecksumHelperFactory.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/ChecksumHelperFactory.java

### Purpose
`ChecksumHelperFactory` selects the file-checksum helper implementation based on replication type.

### Important APIs and Types
`getChecksumHelper` accepts replication type, volume, bucket, key name, length, combine mode, client protocol, and `OmKeyInfo`. It returns `ECFileChecksumHelper` for `HddsProtos.ReplicationType.EC` and `ReplicatedFileChecksumHelper` otherwise.

### Control Flow
The factory performs a single conditional on replication type and constructs the appropriate helper.

### State and Persistence Behavior
The class is stateless and has a private constructor.

### Dependencies and Integration Points
It is called by `OzoneClientUtils.getFileChecksumWithCombineMode` after OM key lookup. It integrates EC and replicated checksum implementations behind the common `BaseFileChecksumHelper` abstraction.

### Risks and Edge Cases
All non-EC replication types are treated as replicated. New replication types would need review to ensure this fallback is correct.

### Test Signals
Tests should verify EC selection, RATIS/STANDALONE replicated selection, and constructor argument propagation through helper behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/ChecksumHelperFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/ECBlockChecksumComputer.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/ECBlockChecksumComputer.java

### Purpose
`ECBlockChecksumComputer` computes block checksums for erasure-coded blocks from stripe checksum metadata, excluding parity checksum bytes so the file checksum reflects only data bytes.

### Important APIs and Types
It stores chunk info list, `OmKeyInfo`, and block length. `compute` dispatches to `computeMd5Crc` or `computeCompositeCrc`. `getParityBytes` derives parity checksum byte count from `ECReplicationConfig.getParity()`, chunk length, and bytes per CRC.

### Control Flow
MD5 mode iterates chunk stripe checksums, verifies byte count alignment, limits each stripe checksum buffer to exclude parity bytes, and updates an MD5 digest. Composite CRC mode determines Hadoop checksum type from the first chunk, creates a `CrcComposer`, strips parity bytes, then feeds checksum ints with lengths bounded by bytes-per-CRC and remaining block length, with special handling for the last stripe's shorter chunk.

### State and Persistence Behavior
The object computes a local output byte buffer only. It reads EC replication configuration from `OmKeyInfo`.

### Dependencies and Integration Points
It depends on EC replication config, container `ChunkInfo` stripe checksums, Hadoop `DataChecksum`, `CrcComposer`, protobuf `ByteString`, and `MD5Hash`. It is created by `ECFileChecksumHelper`.

### Risks and Edge Cases
`computeMd5Crc` calls `digester.digest()` twice: once assigned to `fileMD5` and again in `setOutBytes`, so the stored output can become the digest of an already-reset digest rather than the intended digest. Parity byte calculation assumes four-byte CRC values and stripe checksum layout. Missing stripe checksums or unsupported checksum types fail at runtime. Composite CRC block length accounting is subtle for final partial stripes.

### Test Signals
Tests should include EC MD5 output correctness, composite CRC with partial final stripe, parity stripping for different data/parity layouts, null stripe checksum rejection, unsupported checksum types, and regression coverage for the double-digest behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/ECBlockChecksumComputer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/ECFileChecksumHelper.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/ECFileChecksumHelper.java

### Purpose
`ECFileChecksumHelper` specializes file checksum computation for erasure-coded keys by retrieving the chunk metadata needed to compute EC stripe checksums.

### Important APIs and Types
It extends `BaseFileChecksumHelper`, returns `ECBlockChecksumComputer`, and overrides `getChunkInfos`. It uses `ECReplicationConfig`, `StandaloneReplicationConfig`, `Pipeline`, `ContainerProtocolCalls.getBlock`, and block tokens.

### Control Flow
For each `OmKeyLocationInfo`, it selects DataNodes whose replica index is `1` or greater than the EC data count, because stripe checksum information needed for file checksum is stored on replica index 1 and parity nodes. It rebuilds the pipeline as a standalone factor-three pipeline over those nodes, acquires an xceiver client for read, calls `getBlock` with block ID, token, and replica indexes, then releases the client in a `finally` block.

### State and Persistence Behavior
The helper has the state inherited from `BaseFileChecksumHelper`. It does not persist data; it reads block metadata from DataNodes.

### Dependencies and Integration Points
It integrates with HDDS pipelines, EC replication config, block tokens, xceiver client factory, and container protocol calls. It is selected by `ChecksumHelperFactory` for EC keys.

### Risks and Edge Cases
The node selection assumes stripe checksum placement on replica index 1 and parity nodes. Rebuilding the pipeline as standalone factor-three over a variable node set is specialized behavior that can break if EC pipeline semantics change. Client acquisition must always be released; the current `finally` covers that.

### Test Signals
Tests should verify selected replica indexes, rebuilt pipeline properties, token propagation to `getBlock`, client release on success and failure, and integration with `ECBlockChecksumComputer`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/ECFileChecksumHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/ReplicatedBlockChecksumComputer.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/ReplicatedBlockChecksumComputer.java

### Purpose
`ReplicatedBlockChecksumComputer` computes a block checksum for replicated blocks from per-chunk checksum data.

### Important APIs and Types
It stores a list of container `ChunkInfo`. `compute` dispatches by combine mode. Static `digest(ByteBuffer)` returns an `MD5Hash`. `computeMd5Crc` creates the MD5 of all chunk checksum bytes. `computeCompositeCrc` composes per-chunk CRCs into a block CRC.

### Control Flow
MD5 mode concatenates all checksum `ByteString`s from every chunk and digests the concatenated bytes. Composite CRC mode determines checksum type from the first chunk, creates a block-level composer with chunk length as the stripe size, then for each chunk creates a chunk-level composer using bytes-per-CRC and feeds each checksum int with the remaining chunk byte count. The resulting chunk CRC is fed into the block composer with the chunk length.

### State and Persistence Behavior
The object only sets the inherited output buffer. It does not mutate input chunk metadata or persist state.

### Dependencies and Integration Points
It depends on container chunk checksum metadata, Hadoop `DataChecksum`, `MD5Hash`, `CrcComposer`, and protobuf `ByteString`. It is created by `ReplicatedFileChecksumHelper`.

### Risks and Edge Cases
Composite CRC has a suspicious precondition: `remainingChunkSize <= checksums.size() * chunkSize`, which uses chunk length where bytes-per-CRC would usually be expected. Unsupported checksum types throw. Building a concatenated `ByteString` repeatedly can be inefficient for many chunks.

### Test Signals
Tests should cover MD5 for multiple chunks/checksums, composite CRC for CRC32 and CRC32C, partial final checksum length handling, unsupported checksum type rejection, empty chunk list rejection in composite mode, and performance-sensitive large chunk lists if relevant.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/ReplicatedBlockChecksumComputer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/ReplicatedFileChecksumHelper.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/ReplicatedFileChecksumHelper.java

### Purpose
`ReplicatedFileChecksumHelper` specializes `BaseFileChecksumHelper` for replicated keys by retrieving chunk metadata from the DataNode pipeline for each block.

### Important APIs and Types
It provides constructors with and without pre-fetched `OmKeyInfo`, returns `ReplicatedBlockChecksumComputer`, and overrides `getChunkInfos`. It uses `Pipeline.copyForRead`, `ContainerProtocolCalls.getBlock`, block tokens, and xceiver client acquisition/release.

### Control Flow
For each block, it copies the pipeline for read regardless of container state, acquires an xceiver client, calls `getBlock` with the block ID, token, and replica indexes, extracts chunks from the response, and releases the read client in `finally`.

### State and Persistence Behavior
The helper has inherited per-computation state and performs read-only container metadata requests.

### Dependencies and Integration Points
It integrates `BaseFileChecksumHelper` with HDDS container protocol calls for RATIS/STANDALONE-style replicated data. It is the default helper for all non-EC replication types.

### Risks and Edge Cases
Failures in DataNode reads bubble as `IOException`. Correctness depends on `copyForRead` choosing an appropriate readable replica set. The helper assumes returned chunk metadata includes checksum data.

### Test Signals
Tests should verify read pipeline copying, token and replica-index propagation, client release on errors, empty chunk response handling via base class, and final checksum integration for replicated keys.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/ReplicatedFileChecksumHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/package-info.java

### Purpose
`package-info.java` documents the `org.apache.hadoop.ozone.client.checksum` package as containing Ozone client checksum classes.

### Important APIs and Types
It declares the package and contains package-level documentation only.

### Control Flow
No runtime control flow.

### State and Persistence Behavior
No state or persistence behavior.

### Dependencies and Integration Points
It gives package documentation for Javadocs and source organization.

### Risks and Edge Cases
The description is generic and does not mention EC versus replicated helper split or combine modes, so package docs may be less informative than implementation.

### Test Signals
No functional tests are needed. Documentation checks may verify package Javadocs build cleanly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockDataStreamOutputEntry.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockDataStreamOutputEntry.java

### Purpose
`BlockDataStreamOutputEntry` is a lazy wrapper around `BlockDataStreamOutput` for byte-buffer based key writes. It represents one allocated block stream, tracks position, and exposes retry/cleanup/status helpers used by data-stream output pools.

### Important APIs and Types
Fields include config, lazy `ByteBufferStreamOutput`, block ID, key, xceiver client factory, pipeline, intended length, current position, block token, and shared buffer list. It implements `ByteBufferStreamOutput` methods `write`, `flush`, `hflush`, `hsync`, and `close`. Additional APIs expose closed state, failed servers, written/acknowledged lengths, cleanup, retry writes, builder, and testing getters.

### Control Flow
`checkStream` lazily creates `BlockDataStreamOutput` on first write, cleanup, or retry; preallocated blocks do not open xceiver clients until needed. `write` delegates and increments current position. `close` closes the underlying stream and refreshes `blockID` from the stream so BCSID updates are retained. Ack/written length methods return zero when the stream was never initialized.

### State and Persistence Behavior
The entry tracks local write position and current block ID. Durable block data is written by the underlying `BlockDataStreamOutput` to DataNodes. Closing or ack queries can update the local block ID from the underlying stream.

### Dependencies and Integration Points
It integrates with HDDS `BlockDataStreamOutput`, `ByteBufferStreamOutput`, `StreamBuffer`, `XceiverClientFactory`, `Pipeline`, block tokens, and `BlockDataStreamOutputEntryPool`.

### Risks and Edge Cases
`cleanup` initializes the stream even if no data was written, which may create a client only to clean it up. `write` does not locally bound `len` by remaining capacity; callers must enforce block limits. Shared `bufferList` coordination depends on the pool/stream implementation.

### Test Signals
Tests should verify lazy initialization, position increments, zero ack/written lengths before initialization, block ID refresh on close/ack, hflush-to-hsync behavior, cleanup and retry initialization, and failed-server reporting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockDataStreamOutputEntry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockDataStreamOutputEntryPool.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockDataStreamOutputEntryPool.java

### Purpose
`BlockDataStreamOutputEntryPool` manages the list of byte-buffer block stream entries for a key write, handles preallocated and newly allocated blocks, tracks metadata, commits or hsyncs keys with OM, and manages excluded pipelines/nodes after failures.

### Important APIs and Types
State includes `streamEntries`, config, current stream index, `OzoneManagerProtocol`, `OmKeyArgs.Builder`, metadata map, `XceiverClientFactory`, multipart commit info, open ID, `ExcludeList`, shared buffer list, and `lastUpdatedBlockId`. Important methods include `addPreallocateBlocks`, `getLocationInfoList`, `hsyncKey`, `discardPreallocatedBlocks`, `allocateBlockIfNeeded`, `commitKey`, `cleanup`, `computeBufferData`, `getDataSize`, and `getMetadata`.

### Control Flow
Construction seeds `OmKeyArgs.Builder` from the open key info and multipart parameters. `addPreallocateBlocks` filters an `OmKeyLocationInfoGroup` to blocks for the current open version before creating stream entries. `allocateBlockIfNeeded` advances past closed entries, calls OM `allocateBlock` when entries are exhausted, and returns the current entry. `getLocationInfoList` converts non-empty stream entries into OM location info for commit. `hsyncKey` updates data size and locations, rejects multipart hsync, and calls OM only when no locations exist or the last block ID changed since the previous hsync. `commitKey` verifies caller offset equals accumulated length, populates key args, and commits either a multipart upload part or a normal key.

### State and Persistence Behavior
The pool is stateful for one open key. It tracks which block entry is current, accumulated metadata, buffered data, excluded nodes, and last hsynced block. Persistent effects occur through OM calls: allocate block, hsync key, commit key, or commit multipart upload part. `cleanup` clears local entries and exclude list but does not itself abort OM state.

### Dependencies and Integration Points
It integrates with `OzoneManagerProtocol`, `OmKeyArgs`, `OmKeyInfo`, `OmKeyLocationInfo`, `OmKeyLocationInfoGroup`, `OmMultipartCommitUploadPartInfo`, `ExcludeList`, `PipelineID`, `StreamBuffer`, and `BlockDataStreamOutputEntry`.

### Risks and Edge Cases
`buildKeyArgs` adds all metadata to the builder on every call; repeated calls rely on builder behavior to avoid unintended duplication/overwrites. `hsyncKey` only sends updates when the last block ID changes, so appended data within the same block may not trigger another hsync. `discardPreallocatedBlocks` asserts unused blocks have position zero. `commitKey` requires offset exactly equal to local length and will fail fast on mismatch.

### Test Signals
Tests should cover preallocated block filtering by open version, allocation when current entry is closed or absent, non-empty location reporting only, multipart hsync rejection, hsync suppression/reissue based on last block ID, commit normal vs multipart behavior, discard of unused blocks by pipeline/container, metadata propagation, and cleanup clearing local state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockDataStreamOutputEntryPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockOutputStreamEntry.java -->
## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockOutputStreamEntry.java

### Purpose
`BlockOutputStreamEntry` wraps an output stream for writing one allocated block through DataNode pipelines. The base implementation creates a `RatisBlockOutputStream`, tracks attempted write position, handles flush/hsync/close, and supports retry handoff coordination.

### Important APIs and Types
State includes config, lazy `BlockOutputStream`, block ID, key, xceiver client factory, pipeline, intended length, current position, block token, buffer pool, metrics, stream buffer args, executor supplier, retry-handling flag, and inflight call count. APIs include `write`, `flush`, `hsync`, `close`, `cleanup`, `writeOnRetry`, ack/written length queries, failed-server query, position management, retry wait/finish methods, and a builder.

### Control Flow
`checkStream` lazily calls `createOutputStream`, which constructs `RatisBlockOutputStream`. Writes delegate to the underlying stream and increment current position. `hsync` requires the underlying stream to implement `Syncable` and records latency via metrics. `close` closes the stream and refreshes block ID to capture updated BCSID. Retry coordination uses `isHandlingRetry`, a `Condition`, and inflight call counters so a replacement entry can finish replay before normal writes resume.

### State and Persistence Behavior
The entry stores local write position and block ID while the underlying stream persists data to DataNodes. `resetToAckedPosition` rolls local position back to acknowledged bytes after failure. Cleanup delegates to the underlying block stream and may invalidate the xceiver client.

### Dependencies and Integration Points
It integrates with HDDS `BlockOutputStream`, `RatisBlockOutputStream`, `BufferPool`, `ContainerClientMetrics`, `StreamBufferArgs`, `XceiverClientFactory`, `Pipeline`, block tokens, Java executor services, Hadoop `Syncable`, and higher-level key output streams.

### Risks and Edge Cases
Current position records successful write-call bytes, not necessarily fully acknowledged bytes; retry paths must use ack length correctly. `waitForRetryHandling` depends on callers holding the associated lock for the condition. `cleanup` initializes the stream if needed, similar to the data-stream entry. Hsync on a non-`Syncable` implementation throws `UnsupportedOperationException`.

### Test Signals
Tests should verify lazy stream creation, position increments, block ID refresh on close/ack, `resetToAckedPosition`, retry wait/signal behavior, inflight call accounting, hsync metrics and unsupported stream handling, failed-server propagation, cleanup invalidation, and builder propagation of retry mode and stream dependencies.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockOutputStreamEntry.java -->
