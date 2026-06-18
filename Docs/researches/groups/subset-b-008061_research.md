# subset-b-008061 Apache Ozone OM helper/protocol research

This grouped report covers the requested Apache Ozone OM helper, multitenant, protocol, and protocol transport files. Each source-tree-aligned section is delimited for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUploadListParts.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUploadListParts.java

## Purpose

`OmMultipartUploadListParts` is the OM-side response model for listing the parts of one multipart upload. It carries the upload replication configuration, pagination marker state, truncation state, and an ordered mutable list of `OmPartInfo` entries.

## Important APIs, Types, And Functions

The public API is the constructor, `addPart`, `addPartList`, `addProtoPartList`, and getters for `nextPartNumberMarker`, `truncated`, `partInfoList`, and `replicationConfig`. `addProtoPartList` is the conversion boundary from protobuf `PartInfo` to helper objects.

## Control Flow, State, And Persistence

The class is an in-memory DTO. OM handlers create it with the replication config and pagination state, append Java or protobuf part records, and return it through protocol translators. It does not persist itself; persistence belongs to multipart upload metadata tables and the `PartInfo` protobuf fields.

## Dependencies And Integration Points

It depends on `ReplicationConfig`, `OmPartInfo`, and `OzoneManagerProtocolProtos.PartInfo`. It integrates with `OzoneManagerProtocol.listParts`, S3 multipart list-parts responses, and translator code that maps OM helper results back into protobuf or REST responses.

## Risks And Test Signals

The internal list is returned directly, so callers can mutate it. Pagination correctness depends on the caller setting the marker and truncation flag consistently with the part list. Test with empty uploads, exact page-size boundaries, truncated listings, eTag propagation, and both RATIS and EC replication configs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUploadListParts.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmPartInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmPartInfo.java

## Purpose

`OmPartInfo` is the immutable Java representation of one multipart upload part. It records the part number, backing part key/name, modification time, logical size, and optional eTag.

## Important APIs, Types, And Functions

The constructor initializes all fields, getters expose each value, and `getProto()` converts to `OzoneManagerProtocolProtos.PartInfo`. The eTag field is optional and is only set in protobuf when non-null.

## Control Flow, State, And Persistence

This is a value object with final fields. OM multipart list code constructs it from persisted multipart metadata or protobuf responses, and protocol code serializes it with `getProto()`. The object itself has no mutation or storage side effects.

## Dependencies And Integration Points

It depends only on the multipart `PartInfo` protobuf. It is consumed by `OmMultipartUploadListParts`, complete-multipart responses, and S3 gateway translation logic that must preserve AWS-compatible part number, size, modified time, and eTag data.

## Risks And Test Signals

There is no validation of part number range, name, or size, so invalid data must be rejected upstream. Test signals are protobuf round trips with and without eTag, ordered part listings, large part sizes, and boundary part numbers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmPartInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmRangerSyncArgs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmRangerSyncArgs.java

## Purpose

`OmRangerSyncArgs` carries the target Ranger service version for a manual or background Ranger synchronization request.

## Important APIs, Types, And Functions

The class exposes `getNewSyncServiceVersion()` and a nested `Builder` with `setNewSyncServiceVersion()` and `build()`. `newBuilder()` is the construction entry point used by protocol or command code.

## Control Flow, State, And Persistence

Instances are immutable after construction and are request arguments only. The builder stores a primitive long, then creates the final object. No persistence occurs in this class; OM/Ranger sync state is maintained by the service that consumes the version.

## Dependencies And Integration Points

It depends on `java.util.Objects` and integrates with `OzoneManagerProtocol.triggerRangerBGSync`-adjacent request handling and any OM internal Ranger sync executor that needs a service-version target.

## Risks And Test Signals

`Objects.requireNonNull(newServiceVersion, ...)` boxes a primitive long and therefore never rejects an unset builder value; omitted values become `0`. Tests should cover default builder behavior, explicit version propagation, and rejection or interpretation of version zero by the consuming layer.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmRangerSyncArgs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmRenameKeys.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmRenameKeys.java

## Purpose

`OmRenameKeys` packages a batch key-rename request for one volume and bucket. It carries a map from old key names to new key names and a map from old key names to the already-computed destination `OmKeyInfo`.

## Important APIs, Types, And Functions

The constructor accepts `volume`, `bucket`, `fromAndToKey`, and `fromKeyAndToKeyInfo`. Getters expose those fields to OM request handlers.

## Control Flow, State, And Persistence

The class is a mutable-field DTO, but it has no mutator methods after construction. Rename logic consumes the maps while updating OM key tables through the normal write path. The object is not itself persisted.

## Dependencies And Integration Points

It depends on `Map`, `HashMap`, and `OmKeyInfo`. It integrates with `OzoneManagerProtocol.renameKeys`, file-system optimized rename handling, and audit/request conversion code that needs both names and destination metadata.

## Risks And Test Signals

The constructor stores caller-supplied map references directly, so later external mutation can alter request content. Tests should cover empty batches, missing destination `OmKeyInfo`, duplicate target names, atomicity of partial failures, and FSO versus object-store bucket behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmRenameKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmTenantArgs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmTenantArgs.java

## Purpose

`OmTenantArgs` stores arguments for creating an Ozone tenant: tenant id, backing volume name, and whether creation should proceed when the volume already exists.

## Important APIs, Types, And Functions

It has direct constructors and a nested `Builder` with `setTenantId`, `setVolumeName`, `setForceCreationWhenVolumeExists`, and `build`. Getters expose `tenantId`, `volumeName`, and the force flag.

## Control Flow, State, And Persistence

The object is immutable after construction. The one-argument constructor defaults the volume name to the tenant id; the builder applies the same default when `volumeName` is unset. Tenant creation persistence happens in OM tenant tables and Ranger policy setup, not in this class.

## Dependencies And Integration Points

It depends on `Objects` and is consumed by `OzoneManagerProtocol.createTenant` and client-side translator code for multitenancy commands.

## Risks And Test Signals

Only `tenantId` is null-checked; validation of legal tenant and volume names is upstream. Tests should cover default volume selection, custom volume selection, force flag propagation, invalid names, and existing-volume behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmTenantArgs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmTenantUserArgs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmTenantUserArgs.java

## Purpose

`OmTenantUserArgs` is a small request DTO for tenant-user operations. The source comment notes it is currently unused.

## Important APIs, Types, And Functions

The constructor stores `tenantUsername` and `tenantId`; getters return those fields.

## Control Flow, State, And Persistence

It is immutable after construction and contains no serialization or persistence hooks. If adopted by a request path, persistence would occur in OM tenant access-id tables.

## Dependencies And Integration Points

The class has no external dependencies beyond Java `String`. It is in the helpers package near active tenant DTOs such as `OmTenantArgs`, `TenantUserInfoValue`, and `TenantUserList`.

## Risks And Test Signals

There is no validation or null checking. If this type is wired into a live API, tests should cover null principal, null tenant, invalid principal syntax, and conversion to any corresponding protobuf request.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmTenantUserArgs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmVolumeArgs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmVolumeArgs.java

## Purpose

`OmVolumeArgs` is the main persisted and protocol-facing metadata object for an Ozone volume. It stores admin, owner, volume name, creation/modification time, quota values, namespace usage, ACLs, object/update IDs, metadata, and a reference count used to track mounts or links.

## Important APIs, Types, And Functions

The class extends `WithObjectID` and implements `CopyObject`. Important methods include `getCodec`, getters, `getDefaultAcls`, equality by object ID, `getProtobuf`, `builderFromProtobuf`, `getFromProtobuf`, `toAuditMap`, and `copyObject`. The nested `Builder` supports quota, namespace, ACL, object/update ID, metadata, and ref-count mutation with validation.

## Control Flow, State, And Persistence

OM builds instances for create/update/read volume paths. `CODEC` delegates RocksDB persistence through `VolumeInfo` protobuf. `getProtobuf` writes all durable fields and fills zero creation time with current time. `builderFromProtobuf` reconstructs metadata and ACL lists. Builder validation rejects missing admin/owner/volume and negative ref counts while inherited `WithObjectID.Builder` guards object ID immutability and update ID monotonicity.

## Dependencies And Integration Points

It depends on Ozone constants, audit interfaces, `OzoneAcl`, `AclListBuilder`, `OzoneAclUtil`, `KeyValueUtil`, HDDS DB codecs, and `VolumeInfo` protobuf. It is central to volume APIs, S3 volume context, quota repair, ACL enforcement, OM metadata tables, audit logging, and service/client protocol translators.

## Risks And Test Signals

`copyObject()` returns `this`, relying on immutability of the object and immutable ACL list. Incorrect quota sentinel handling or creation-time defaults can affect upgrade compatibility. Tests should cover protobuf/codec round trips, ACL preservation, ref-count increment/decrement validation, object/update ID validation, audit map fields, and volume equality semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmVolumeArgs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OpenKeySession.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OpenKeySession.java

## Purpose

`OpenKeySession` represents an active client session for an opened key. It lets OM and clients associate a client ID with the `OmKeyInfo` being written and the key version opened by that session.

## Important APIs, Types, And Functions

The constructor stores `id`, `keyInfo`, and `openVersion`. Getters expose the session ID, key info, and open version. The ID is annotated with Jackson `@JsonProperty("clientId")`.

## Control Flow, State, And Persistence

The object is returned by open/create-file APIs and later referenced by commit, hsync, recover, or allocate-block calls using the client ID. It is not the authoritative persisted open-key row, but it mirrors state stored in OM open key tables.

## Dependencies And Integration Points

It depends on `OmKeyInfo` and Jackson. It integrates with `OzoneManagerProtocol.openKey`, `createFile`, `allocateBlock`, `commitKey`, `hsyncKey`, and lease recovery.

## Risks And Test Signals

`openVersion` is mutable but has no setter, and `keyInfo` may itself contain mutable block metadata. Tests should cover open-create-commit round trips, JSON field compatibility, multipart/open-version behavior, and recovery of sessions with pending blocks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OpenKeySession.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneAclUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneAclUtil.java

## Purpose

`OzoneAclUtil` centralizes ACL helper logic for OM metadata objects: default ACL creation, filtering, access checks, default ACL inheritance, protobuf conversion, and list mutation.

## Important APIs, Types, And Functions

Key methods are `getDefaultAclList`, `getAclList`, `filterAclList`, `checkAclRights`, `inheritDefaultAcls`, `fromProtobuf`, `toProtobuf`, `addAcl`, `addAllAcl`, `removeAcl`, and `setAcl`. `checkAccessInAcl` implements user/group/other matching against `RequestContext`.

## Control Flow, State, And Persistence

The class is stateless. Default ACL methods build new lists from UGI and OM default-right configuration. Mutation methods operate in place on supplied lists, merging ACL bitsets for matching identity/type/scope and removing empty entries. Persistence occurs when mutated ACL lists are serialized by volume, bucket, or key metadata classes.

## Dependencies And Integration Points

It depends on `OzoneAcl`, `OmConfig`, `IAccessAuthorizer`, `RequestContext`, UGI, and ACL protobufs. It is used by volume/bucket/key builders, authorization checks, default ACL inheritance during directory/key creation, and protocol translators.

## Risks And Test Signals

The raw `List retList` in `filterAclList` loses generic type safety. Group lookup failures are logged but do not fail default ACL creation. Tests should cover ACL merge/remove semantics, `ALL` and `NONE` behavior through `OzoneAcl.checkAccess`, default ACL inheritance with scope conversion, protobuf round trips, and user primary-group lookup failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneAclUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneFSUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneFSUtils.java

## Purpose

`OzoneFSUtils` contains path, key, bucket-layout, snapshot-name, depth, and hsync feature helpers for Ozone file-system semantics.

## Important APIs, Types, And Functions

Important methods include `pathToKey`, `getParent`, `getImmediateChild`, `addTrailingSlashIfNeeded`, `isFile`, `isValidName`, `isValidKeyPath`, `validateBucketLayout`, `getFileName`, `isSibling`, `isAncestorPath`, `isImmediateChild`, `getParentDir`, `appendFileNameToKeyPath`, `getFileCount`, `removeTrailingSlashIfNeeded`, `generateUniqueTempSnapshotName`, `trimPathToDepth`, and `canEnableHsync`.

## Control Flow, State, And Persistence

The utility is stateless. Path validation rejects leading slashes for key paths, missing leading slashes for absolute names, `.`, `..`, `:`, embedded slash elements, and mid-path empty components. Bucket layout validation rejects object-store buckets for FS APIs. `canEnableHsync` gates hsync on both the hsync flag and HBase-enhancement allowance.

## Dependencies And Integration Points

It depends on Hadoop `Path`, Java NIO `Paths`, Ozone constants/config keys, `BucketLayout`, `SnapshotInfo`, `Time`, and `OMException`. It integrates with OzoneFS, FSO bucket operations, snapshot temp directory handling, list-status path trimming, and client/server hsync configuration.

## Risks And Test Signals

Java NIO path handling is platform-sensitive; tests should run path validation with slashes, trailing slashes, root, empty paths, and Windows-like colon inputs. Also test object-store bucket rejection, immediate child/sibling logic for root and relative paths, temp snapshot name uniqueness, and hsync gating when enhancement config differs client-side versus server-side.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneFSUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneFileStatus.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneFileStatus.java

## Purpose

`OzoneFileStatus` is the full file-status model returned by Ozone FS list and lookup APIs. It wraps `OmKeyInfo`, directory/file state, and block size.

## Important APIs, Types, And Functions

The class exposes `getKeyInfo`, `getBlockSize`, `getTrimmedName`, `getPath`, `isDirectory`, `isFile`, `getProtobuf`, `getFromProtobuf`, `equals`, `hashCode`, and `toString`. A null `keyInfo` represents the synthetic root directory.

## Control Flow, State, And Persistence

Instances are transient protocol results. `getProtobuf` serializes block size, directory flag, and optional key info using the caller's client version. `getFromProtobuf` rebuilds status from `OzoneFileStatusProto`.

## Dependencies And Integration Points

It depends on `OmKeyInfo`, Ozone URI delimiter constants, and `OzoneFileStatusProto`. It is returned by `IOmMetadataReader`/`OzoneManagerProtocol.listStatus` and consumed by OzoneFS clients.

## Risks And Test Signals

`getTrimmedName`, `equals`, and `hashCode` assume non-null `keyInfo`; root status can throw if compared or hashed through those paths. Tests should cover root status, trailing slash trimming, protobuf round trips by client version, directory/file flags, and equality for same key name with different block metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneFileStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneFileStatusLight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneFileStatusLight.java

## Purpose

`OzoneFileStatusLight` is a lightweight version of `OzoneFileStatus` that carries `BasicOmKeyInfo` instead of full block/key metadata to reduce list-status response size.

## Important APIs, Types, And Functions

It provides the same high-level API shape as `OzoneFileStatus`: key info and block-size getters, path/name helpers, `isDirectory`, `isFile`, `getProtobuf`, `getFromProtobuf`, equality/hash/toString, and static `fromOzoneFileStatus`.

## Control Flow, State, And Persistence

Instances are transient list-status results. Protobuf conversion uses `OzoneFileStatusProtoLight`, storing basic key info plus volume and bucket names. `fromOzoneFileStatus` extracts a `BasicOmKeyInfo` from full key info when possible.

## Dependencies And Integration Points

It depends on `BasicOmKeyInfo`, Ozone URI delimiter constants, and lightweight status protobufs. It integrates with `OzoneManagerProtocol.listStatusLight` and clients that need directory listings without block locations.

## Risks And Test Signals

Like the full status class, root handling can be fragile in equality and trimmed-name paths when `keyInfo` is null. Tests should cover conversion from full status, protobuf round trips, root and directory entries, trailing slash trimming, and preservation of volume/bucket names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneFileStatusLight.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneIdentityProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneIdentityProvider.java

## Purpose

`OzoneIdentityProvider` supplies identity strings to Hadoop's decay RPC scheduler. It prefers OM-provided S3 caller context over raw RPC user identity so S3 gateway traffic can be attributed to the authenticated S3 principal.

## Important APIs, Types, And Functions

The only behavior is `makeIdentity(Schedulable)`. It reads UGI, attempts to read `CallerContext`, checks for `OM_S3_CALLER_CONTEXT_PREFIX`, and otherwise returns the UGI short user name.

## Control Flow, State, And Persistence

The class is stateless. If the schedulable implementation does not support caller context, it logs an error and falls back to UGI. No state is persisted; the returned identity affects runtime scheduling and fairness.

## Dependencies And Integration Points

It depends on Hadoop `IdentityProvider`, `Schedulable`, `CallerContext`, UGI, and Ozone S3 caller-context constants. It integrates with OM RPC server scheduling, especially S3 gateway requests where the gateway service user differs from the end user.

## Risks And Test Signals

Only caller contexts with the trusted OM prefix are accepted; user-supplied contexts are ignored. Tests should cover S3-prefixed context, non-prefixed context, null context, unsupported schedulable implementations, and null short user names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneIdentityProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/QuotaUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/QuotaUtil.java

## Purpose

`QuotaUtil` calculates logical, replicated, and per-replica sizes for quota accounting across RATIS and erasure-coded replication.

## Important APIs, Types, And Functions

It exposes `getReplicatedSize`, `getSizePerReplica`, and `getDataSize`. RATIS uses replication factor multiplication/division. EC uses data/parity chunk geometry and required-node counts.

## Control Flow, State, And Persistence

The class is stateless. `getReplicatedSize` computes EC full stripes plus parity for a partial first chunk; `getDataSize` estimates the inverse because exact partial stripe layout is not knowable from replicated size alone. Unknown replication types log warnings and return the original size.

## Dependencies And Integration Points

It depends on `ReplicationConfig`, `RatisReplicationConfig`, `ECReplicationConfig`, and HDDS replication type enums. It integrates with volume/bucket quota usage, deleted-key accounting, snapshot size accounting, and quota repair.

## Risks And Test Signals

EC reverse sizing is approximate and partial-stripe math must match container layout expectations. Tests should cover RATIS factors, EC exact stripes, small partial writes, zero size, unknown replication type, and `requiredNodes <= 0` fallback in per-replica calculation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/QuotaUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ReadConsistency.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ReadConsistency.java

## Purpose

`ReadConsistency` defines read-consistency modes for OM client requests, including whether a request must be linearizable and whether follower reads are allowed.

## Important APIs, Types, And Functions

Enum values are `DEFAULT`, `LOCAL_LEASE`, `LINEARIZABLE_LEADER_ONLY`, and `LINEARIZABLE_ALLOW_FOLLOWER`. Methods include `isLinearizable`, `allowFollowerRead`, `toProto`, `toReadConsistencyHint`, and static `fromProto`.

## Control Flow, State, And Persistence

The enum is immutable. It caches protobuf `ReadConsistencyHint` instances and maps between Java and protobuf enums. These hints travel with requests; they are not persisted metadata.

## Dependencies And Integration Points

It depends on `ReadConsistencyProto` and `ReadConsistencyHint` protobufs. It is used by `Hadoop3OmTransport` follower-read failover configuration and by request builders/translators that need to select leader-only, follower-allowed, or local-lease reads.

## Risks And Test Signals

`valueOf` use in configuration paths is case-sensitive and will fail for invalid strings. Tests should cover all enum-protobuf round trips, hint object mapping, follower-read routing decisions, and invalid config values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ReadConsistency.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/RepeatedOmKeyInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/RepeatedOmKeyInfo.java

## Purpose

`RepeatedOmKeyInfo` stores multiple deleted incarnations of the same key name in OM's deleted table. It supports GDPR-style verification and quota accounting when the same URI is recreated and deleted repeatedly.

## Important APIs, Types, And Functions

Important methods are `getCodec(boolean ignorePipeline)`, constructors, `addOmKeyInfo`, `getOmKeyInfoList`, `cloneOmKeyInfoList`, `getTotalSize`, `builderFromProto`, `getFromProto`, `getProto`, `getBucketId`, and `copyObject`. The builder stores the key-info list and bucket ID.

## Control Flow, State, And Persistence

The class persists through delegated codecs backed by `RepeatedKeyInfo` protobuf. Two codecs differ by whether pipeline data is compacted/ignored. `getProto` clones the key list before serialization to avoid concurrent modification, serializes each `OmKeyInfo`, and records `bucketId`.

## Dependencies And Integration Points

It depends on HDDS DB codecs, `OmKeyInfo`, `ClientVersion`, `RepeatedKeyInfo`, `KeyInfo`, and Apache Commons `ImmutablePair`. It integrates with OM deleted-key tables, key deletion services, quota repair, and snapshot/deleted data cleanup.

## Risks And Test Signals

The returned `getOmKeyInfoList()` is mutable, and builder can build with null lists. Tests should cover codec round trips with and without compact pipeline data, total size accounting, bucket ID preservation, concurrent serialization safety, and copy behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/RepeatedOmKeyInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/S3SecretValue.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/S3SecretValue.java

## Purpose

`S3SecretValue` is the persisted value for an S3 access ID and secret pair, historically named with `kerberosID`.

## Important APIs, Types, And Functions

The class exposes `getCodec`, factory methods `of`, `deleted`, getters for Kerberos/access ID, secret, deletion flag, and transaction log index, `fromProtobuf`, `getProtobuf`, `equals`, `hashCode`, and `toString`.

## Control Flow, State, And Persistence

Instances are immutable. `CODEC` persists through the `S3Secret` protobuf. `deleted()` returns a tombstone-like value with an empty secret and deletion flag set, but `getProtobuf` does not encode `isDeleted` or `transactionLogIndex`; `fromProtobuf` recreates a non-deleted value with index zero.

## Dependencies And Integration Points

It depends on HDDS DB codecs and `OzoneManagerProtocolProtos.S3Secret`. It integrates with OM S3 secret tables, tenant access ID assignment, S3 gateway authentication, and `OzoneManagerProtocol.getS3Secret`/`setS3Secret`.

## Risks And Test Signals

`toString()` prints the secret, which is sensitive. Deletion/index fields are not preserved by protobuf conversion. Tests should cover secret persistence, tombstone semantics in the surrounding table code, equality including deletion/index, and log redaction expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/S3SecretValue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/S3VolumeContext.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/S3VolumeContext.java

## Purpose

`S3VolumeContext` wraps the S3 volume's `OmVolumeArgs` plus the user principal piggybacked for client-side KMS operations.

## Important APIs, Types, And Functions

The class exposes getters, static `fromProtobuf`, `getProtobuf`, `newBuilder`, and a nested builder with setters for `OmVolumeArgs` and user principal.

## Control Flow, State, And Persistence

It is a transient response wrapper for `GetS3VolumeContextResponse`. `getProtobuf` serializes volume info through `OmVolumeArgs.getProtobuf` and includes the principal. It does not persist independently.

## Dependencies And Integration Points

It depends on `OmVolumeArgs` and `GetS3VolumeContextResponse`. It integrates with S3 gateway key lookup, encryption/KMS paths, and `OzoneManagerProtocol.getS3VolumeContext`.

## Risks And Test Signals

The builder does not validate null fields. Tests should cover protobuf round trips, principal propagation for encrypted S3 keys, missing volume info, and compatibility with volume ACL/quota metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/S3VolumeContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ServiceInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ServiceInfo.java

## Purpose

`ServiceInfo` describes an Ozone service endpoint discovered from OM: node type, hostname, service ports, OM protocol version, optional OM role, and optional filesystem server defaults.

## Important APIs, Types, And Functions

Important methods are getters, `getPort`, `getServiceAddress`, `getOmRoleInfo`, `getServerDefaults`, `getProtobuf`, `getFromProtobuf`, and the nested `Builder` with node, host, port, OM version, role, and defaults setters.

## Control Flow, State, And Persistence

Instances are service-discovery DTOs. Construction copies protobuf `ServicePort` entries into a map. `getProtobuf` converts the map back to port messages and conditionally writes OM version, OM role, and server defaults. This information is returned by OM, not persisted by this class.

## Dependencies And Integration Points

It depends on HDDS `NodeType`, Ozone manager version, `OzoneFsServerDefaults`, and service-info protobuf types. It integrates with `OzoneManagerProtocol.getServiceList`, client discovery, OM HA role display, HTTP/RPC endpoint lookup, and OzoneFS defaults.

## Risks And Test Signals

`getPort` unboxes a nullable map value and throws if the port type is absent. Builder validation relies on constructor null checks for node and host only. Tests should cover port map round trips, missing port handling, OM role inclusion only for OM nodes, server-default compatibility, and JSON deserialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ServiceInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ServiceInfoEx.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ServiceInfoEx.java

## Purpose

`ServiceInfoEx` extends service discovery with CA certificate data so clients can discover service endpoints and TLS trust material together.

## Important APIs, Types, And Functions

The class implements `CACertificateProvider`. It exposes `getServiceInfoList`, `getCaCertificate`, `getCaCertPemList`, and `provideCACerts`.

## Control Flow, State, And Persistence

The object is an immutable-ish response wrapper. `provideCACerts` prefers the PEM list; if the list is empty, it falls back to the single PEM string, rejecting the case where both are unavailable. It then converts PEM strings to `X509Certificate` objects.

## Dependencies And Integration Points

It depends on `ServiceInfo`, HDDS `CACertificateProvider`, `OzoneSecurityUtil`, and Java certificate APIs. It integrates with secure OM clients, gRPC transport CA setup, and service discovery responses.

## Risks And Test Signals

An empty single PEM is intentionally ignored for tests, which can leave `caCertPems` null before conversion depending on inputs. Tests should cover multiple CA certs, legacy single cert, null/empty cert data, malformed PEM, and secure client bootstrap.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ServiceInfoEx.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/SnapshotDiffJob.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/SnapshotDiffJob.java

## Purpose

`SnapshotDiffJob` is the persisted status record for asynchronous snapshot diff jobs. It records job identity, snapshot pair, options, status/sub-status, progress, entry counts, largest key, and failure reason.

## Important APIs, Types, And Functions

Important methods include `codec`, getters/setters, `toString`, `equals`, `hashCode`, `toProtoBuf`, `getFromProtoBuf`, and the private `SnapshotDiffJobCodec`. The codec writes protobuf and falls back to old Jackson JSON when protobuf parsing fails.

## Control Flow, State, And Persistence

OM creates and updates this object as diff jobs move through queued/in-progress/done/failed states. The codec persists to the snapshot diff job table as `SnapshotDiffJobProto`. Fallback JSON decoding preserves upgrade compatibility with older persisted rows.

## Dependencies And Integration Points

It depends on Jackson, protobuf, HDDS `Codec`, `SnapshotDiffJobProto`, and snapshot diff `JobStatus`/`SubStatus`. It integrates with `OzoneManagerProtocol.submitSnapshotDiff`, `cancelSnapshotDiff`, `listSnapshotDiffJobs`, background diff services, and diff progress reporting.

## Risks And Test Signals

`copyObject` returns the same object despite mutability. `toString` calls `status.equals(...)`, so null status can fail. Tests should cover protobuf and legacy JSON decode, all status/sub-status combinations, progress formatting, failure reason persistence, equality/hash changes, and concurrent updates in DB cache paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/SnapshotDiffJob.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/SnapshotInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/SnapshotInfo.java

## Purpose

`SnapshotInfo` is the persisted metadata model for a bucket snapshot. It stores snapshot UUID, volume/bucket/name, status, creation/deletion time, previous snapshot links, checkpoint path, cleanup flags, size accounting, and transaction markers.

## Important APIs, Types, And Functions

Important methods include `getCodec`, setters/getters, `toBuilder`, nested `Builder`, `getProtobuf`, `builderFromProtobuf`, `getFromProtobuf`, `toAuditMap`, `getCheckpointDirName`, `getTableKey`, `generateName`, `newInstance`, `copyObject`, and `SnapshotStatus` enum conversions.

## Control Flow, State, And Persistence

The delegated codec persists `SnapshotInfo` through `OzoneManagerProtocolProtos.SnapshotInfo`. `newInstance` creates default active snapshots with generated names when needed, invalid deletion time, initial previous-snapshot IDs, and bucket snapshot path. Serialization conditionally includes optional previous IDs and transaction info while writing cleanup/size fields.

## Dependencies And Integration Points

It depends on HDDS UUID protobuf helpers, DB codecs, `ByteString`, Ozone constants, auditing, and snapshot protobufs. It integrates with OM snapshot tables, checkpoint directory naming, snapshot cleanup/deep-clean services, snapshot diff, audit logging, and list/get snapshot APIs.

## Risks And Test Signals

`INITIAL_SNAPSHOT_ID` is randomly generated at class load, so tests should verify intended sentinel behavior across process restarts if persisted. Equality omits the two delta size fields while `toString` includes them. Tests should cover protobuf round trips for optional fields, generated UTC names, table keys, checkpoint versions, status enum conversion, size accounting, cleanup flags, and copy isolation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/SnapshotInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/TenantStateList.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/TenantStateList.java

## Purpose

`TenantStateList` wraps a list of tenant state protobuf messages returned by tenant listing APIs.

## Important APIs, Types, And Functions

It exposes `getTenantStateList`, static `fromProtobuf`, `getProtobuf`, `toString`, `equals`, and `hashCode`. `getProtobuf` is deliberately not implemented and throws `NotImplementedException`.

## Control Flow, State, And Persistence

The class is a transient response wrapper. It stores the protobuf list directly and relies on upstream code to construct the list response. It does not persist or convert to a full list response.

## Dependencies And Integration Points

It depends on `TenantState` protobuf and Apache Commons `NotImplementedException`. It is returned by `OzoneManagerProtocol.listTenant`.

## Risks And Test Signals

Calling `getProtobuf` will fail. The list reference is stored directly. Tests should cover tenant listing response handling, equality for list content, no accidental call to `getProtobuf`, and mutation safety expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/TenantStateList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/TenantUserInfoValue.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/TenantUserInfoValue.java

## Purpose

`TenantUserInfoValue` wraps the access IDs associated with one user across tenants for tenant user-info responses.

## Important APIs, Types, And Functions

It stores a `List<ExtendedUserAccessIdInfo>`, exposes `getAccessIdInfoList`, static `fromProtobuf(TenantGetUserInfoResponse)`, `getProtobuf`, `toString`, `equals`, and `hashCode`.

## Control Flow, State, And Persistence

The class is a protocol response wrapper. `fromProtobuf` takes the repeated list from a response; `getProtobuf` builds a new `TenantGetUserInfoResponse` and adds each access-id info entry. Persistence is handled by OM tenant/access-id DB tables.

## Dependencies And Integration Points

It depends on tenant user-info protobuf messages. It integrates with `OzoneManagerProtocol.tenantGetUserInfo`, tenant administration CLI output, and S3 access-id management.

## Risks And Test Signals

The list is stored and returned directly. Tests should cover empty users, multiple access IDs, admin/delegated admin flags inside entries, protobuf round trips, and mutation expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/TenantUserInfoValue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/TenantUserList.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/TenantUserList.java

## Purpose

`TenantUserList` wraps the list of user principal to access ID pairs for users assigned to a tenant.

## Important APIs, Types, And Functions

It exposes the constructor, `getUserAccessIds`, static `fromProtobuf(TenantListUserResponse)`, `toString`, `equals`, and `hashCode`.

## Control Flow, State, And Persistence

The class is a transient response object for tenant listing. It stores the protobuf repeated field directly. It does not provide a reverse `getProtobuf`; translators build list responses elsewhere.

## Dependencies And Integration Points

It depends on `TenantListUserResponse` and `UserAccessIdInfo` protobufs. It integrates with `OzoneManagerProtocol.listUsersInTenant` and tenant management clients.

## Risks And Test Signals

Direct list exposure can allow accidental mutation. Tests should cover empty tenant, prefix-filtered results, multiple users/access IDs, equality/hash behavior, and client display ordering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/TenantUserList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithMetadata.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithMetadata.java

## Purpose

`WithMetadata` is a base mixin for OM metadata objects that need immutable custom key-value metadata.

## Important APIs, Types, And Functions

The abstract class stores an `ImmutableMap<String,String>` and exposes final `getMetadata`. The nested `Builder` supports `addMetadata`, `addAllMetadata`, `setMetadata`, and direct access to the `MapBuilder`.

## Control Flow, State, And Persistence

Subclasses call the builder constructor to snapshot metadata into an immutable map. Metadata persistence is implemented by subclasses that serialize the map into their protobuf fields, such as volume, bucket, and key info.

## Dependencies And Integration Points

It depends on Guava `ImmutableMap`, `MapBuilder`, and JCIP `@Immutable`. It is inherited by `WithObjectID` and many OM helper metadata classes.

## Risks And Test Signals

The builder remains mutable until build time, and null key/value handling depends on `MapBuilder`. Tests should cover metadata copy construction, replacing maps, null/empty maps, immutability of built objects, and subclass protobuf preservation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithMetadata.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithObjectID.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithObjectID.java

## Purpose

`WithObjectID` is a base class for OM metadata objects with immutable object IDs and monotonically increasing update IDs, in addition to metadata inherited from `WithMetadata`.

## Important APIs, Types, And Functions

It exposes final `getObjectID`, final `getUpdateID`, overridable `getObjectInfo`, and the abstract nested `Builder<T>`. The builder supports `setObjectID`, `setUpdateID`, validation, abstract `buildObject`, and final `build`.

## Control Flow, State, And Persistence

Subclasses use the builder to enforce object-ID immutability after initial assignment and prevent update IDs from moving backwards. A special reclaim-block object ID is allowed as an exception. Persistence is done by subclasses that include object/update IDs in protobuf records.

## Dependencies And Integration Points

It depends on Ozone object ID constants and `WithMetadata`. It is used by volume, bucket, key, and directory metadata classes where object identity and transaction update ordering are central to OM tables and FSO traversal.

## Risks And Test Signals

`validate()` calls `buildObject().getObjectInfo()` when reporting update ID errors, which can instantiate an object during validation. Tests should cover initial ID assignment, rejected object ID changes, reclaim-block exception, update ID monotonicity, and subclass error messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithObjectID.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithParentObjectId.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithParentObjectId.java

## Purpose

`WithParentObjectId` extends `WithObjectID` with a parent object ID used for filesystem-optimized bucket path traversal.

## Important APIs, Types, And Functions

It adds final `getParentObjectID` and a nested abstract `Builder<T>` with `setParentObjectID` and protected `getParentObjectID`.

## Control Flow, State, And Persistence

Subclasses set the parent ID during build. In FSO buckets, each path component has an object ID and links to its parent, allowing table lookups by parent/child rather than full string paths. The base class itself does not serialize; subclasses include parent ID in their protobuf state.

## Dependencies And Integration Points

It depends on `WithObjectID` and is used by directory/key metadata that participate in FSO namespace traversal, rename, delete, and list-status operations.

## Risks And Test Signals

There is no validation that parent IDs are non-negative or correspond to real parents. Tests should cover root/bucket parent IDs, nested directory creation, rename parent changes, protobuf round trips in subclasses, and invalid parent handling upstream.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithParentObjectId.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithTags.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithTags.java

## Purpose

`WithTags` is a marker-style interface for OM objects that expose S3 object or bucket tags.

## Important APIs, Types, And Functions

It declares one method: `Map<String, String> getTags()`.

## Control Flow, State, And Persistence

The interface has no implementation or state. Implementing metadata classes decide how tags are stored, validated, serialized, and copied.

## Dependencies And Integration Points

It depends on Java `Map`. It integrates with object tagging APIs in `OzoneManagerProtocol` and S3-compatible tag retrieval/mutation paths.

## Risks And Test Signals

Implementations may return mutable maps unless they protect them. Tests belong on implementers and should cover tag immutability, UTF-8/key validation, protocol conversion, and delete-object-tagging behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithTags.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/package-info.java

## Purpose

This package descriptor marks `org.apache.hadoop.ozone.om.helpers` as the package for OM helper models, utilities, and protocol DTOs.

## Important APIs, Types, And Functions

The file declares only the package and contains no types or functions.

## Control Flow, State, And Persistence

There is no runtime control flow or persisted state.

## Dependencies And Integration Points

The package groups helper classes used by OM metadata tables, client/server protocol translators, S3 gateway integration, filesystem APIs, ACL handling, snapshots, quotas, tenants, and service discovery.

## Risks And Test Signals

No direct tests are required for this file. Package-level changes should be checked through compilation, Javadocs, and import/package consistency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/AccountNameSpace.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/AccountNameSpace.java

## Purpose

`AccountNameSpace` defines the account-side isolation boundary for an Ozone tenant: account namespace ID, aggregate space usage, and quota settings.

## Important APIs, Types, And Functions

The interface declares `getAccountNameSpaceID`, `getSpaceUsage`, `setQuota`, and `getQuota`. It is annotated as limited-private and evolving.

## Control Flow, State, And Persistence

The interface contains no implementation. Implementations decide how usage and quota are calculated or enforced; comments allow lazy Recon aggregation or direct enforcement.

## Dependencies And Integration Points

It depends on `OzoneQuota`, `SpaceUsageSource`, and HDDS audience/stability annotations. It is used by the tenant abstraction and `AccountNameSpaceImpl`.

## Risks And Test Signals

The contract is broad and leaves enforcement semantics unspecified. Implementation tests should cover quota set/get, usage aggregation behavior, tenant isolation, and access ID naming conventions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/AccountNameSpace.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/BucketNameSpace.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/BucketNameSpace.java

## Purpose

`BucketNameSpace` defines the bucket-side namespace boundary for an Ozone tenant. It can map a tenant namespace to one or more top-level Ozone objects such as volumes.

## Important APIs, Types, And Functions

The interface declares `getBucketNameSpaceID`, `getBucketNameSpaceObjects`, `addBucketNameSpaceObject`, `getSpaceUsage`, `setQuota`, and `getQuota`.

## Control Flow, State, And Persistence

There is no implementation in the interface. Implementations decide how namespace objects are represented, how usage is measured, and how quotas are enforced.

## Dependencies And Integration Points

It depends on `OzoneQuota`, `SpaceUsageSource`, `OzoneObj`, and HDDS annotations. `SingleVolumeTenantNamespace` is the concrete implementation in this subset.

## Risks And Test Signals

The interface permits multi-volume future implementations, so callers should not assume exactly one object. Tests should cover namespace object addition, quota usage, public bucket naming expectations, and tenant bucket isolation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/BucketNameSpace.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/OzoneOwnerPrincipal.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/OzoneOwnerPrincipal.java

## Purpose

`OzoneOwnerPrincipal` is a Java `Principal` representing the special Ozone owner identity.

## Important APIs, Types, And Functions

It implements `Principal`, has an empty constructor, `getName`, and `toString`. `toString` delegates to `getName`.

## Control Flow, State, And Persistence

The class is stateless and immutable. It is used as an identity token in authorization contexts rather than persisted metadata.

## Dependencies And Integration Points

It depends on `java.security.Principal`. It integrates with multitenant or Ranger policy code where owner-based principals are represented distinctly from users and roles.

## Risks And Test Signals

Because the name is constant, tests should verify exact principal name expected by policy code and serialization/display paths that call `toString`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/OzoneOwnerPrincipal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/OzoneTenant.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/OzoneTenant.java

## Purpose

`OzoneTenant` is an in-memory representation of a tenant, including tenant ID, role names, access policies, account namespace, and bucket namespace.

## Important APIs, Types, And Functions

It implements `Tenant` and exposes tenant name, account namespace, bucket namespace, access policy list, role list, mutators for policies and roles, and `toString`.

## Control Flow, State, And Persistence

Construction creates an `AccountNameSpaceImpl` and `SingleVolumeTenantNamespace` with the tenant ID. Policy and role lists are mutable `ArrayList`s. The class comment points to DB state elsewhere (`OmDBTenantState`); this object is not the authoritative persisted record.

## Dependencies And Integration Points

It depends on `Tenant`, `AccountNameSpaceImpl`, and `SingleVolumeTenantNamespace`. It integrates with tenant-management logic and Ranger role/policy setup.

## Risks And Test Signals

Getters expose mutable lists directly, so external callers can alter tenant state. Tests should cover add/remove role and policy behavior, namespace IDs, default single-volume namespace mapping, and consistency with persisted tenant DB state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/OzoneTenant.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/OzoneTenantRolePrincipal.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/OzoneTenantRolePrincipal.java

## Purpose

`OzoneTenantRolePrincipal` is a Java `Principal` wrapper for a tenant Ranger role name.

## Important APIs, Types, And Functions

It stores `tenantRoleName`, implements `getName`, and returns the name from `toString`.

## Control Flow, State, And Persistence

The object is immutable and carries no persistence behavior. It is used as a principal identity in authorization or policy construction.

## Dependencies And Integration Points

It depends on `java.security.Principal` and integrates with Ozone multitenancy and Ranger role assignment code.

## Risks And Test Signals

There is no null or format validation. Tests should cover exact name propagation, string conversion, and policy code behavior for invalid or missing role names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/OzoneTenantRolePrincipal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/Tenant.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/Tenant.java

## Purpose

`Tenant` defines the high-level contract for Ozone tenant objects: name, account namespace, bucket namespace, access policies, and tenant roles.

## Important APIs, Types, And Functions

The interface declares getters plus mutators for adding/removing access policies and roles. It is limited-private and evolving.

## Control Flow, State, And Persistence

The interface has no implementation. Concrete classes decide how lists are stored and whether changes are persisted or only in memory.

## Dependencies And Integration Points

It depends on HDDS audience/stability annotations and the account/bucket namespace interfaces. `OzoneTenant` is the implementation in this subset.

## Risks And Test Signals

The API returns mutable `List<String>` in current implementation, so callers need clear ownership. Tests should cover tenant lifecycle code using this interface, policy/role mutation, and namespace coupling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/Tenant.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/impl/AccountNameSpaceImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/impl/AccountNameSpaceImpl.java

## Purpose

`AccountNameSpaceImpl` is the simple concrete account namespace implementation for Ozone tenants.

## Important APIs, Types, And Functions

It implements `AccountNameSpace`, stores an account namespace ID, and implements `getAccountNameSpaceID`, `getSpaceUsage`, `setQuota`, and `getQuota`.

## Control Flow, State, And Persistence

Only the ID is stored. Usage and quota methods are placeholders returning null or doing nothing, so no quota or usage state is persisted by this implementation.

## Dependencies And Integration Points

It depends on `AccountNameSpace`, `OzoneQuota`, and `SpaceUsageSource`. It is constructed by `OzoneTenant`.

## Risks And Test Signals

Quota APIs are no-ops, which is important for callers expecting enforcement. Tests should assert current placeholder behavior, and future implementations should add quota set/get and usage aggregation coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/impl/AccountNameSpaceImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/impl/SingleVolumeTenantNamespace.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/impl/SingleVolumeTenantNamespace.java

## Purpose

`SingleVolumeTenantNamespace` implements a tenant bucket namespace as one backing Ozone volume.

## Important APIs, Types, And Functions

It defines `BUCKET_NS_PREFIX`, stores `bucketNameSpaceID`, and a list of namespace `OzoneObj`s. Constructors initialize by tenant ID or by tenant ID plus volume name. Methods implement namespace ID, object list, object addition, space usage, quota set/get.

## Control Flow, State, And Persistence

The volume constructor creates an `OzoneObjInfo` with store type OZONE, resource type VOLUME, and the supplied volume name. Object additions mutate an in-memory list. Usage and quota methods are placeholders returning null/no-op.

## Dependencies And Integration Points

It depends on `BucketNameSpace`, `OzoneObj`, `OzoneObjInfo`, `OzoneQuota`, and `SpaceUsageSource`. It is constructed by `OzoneTenant` and is used by tenant bucket namespace policy logic.

## Risks And Test Signals

The object list is returned directly and quota methods do nothing. Tests should cover namespace ID prefixing, default volume mapping, added objects, volume `OzoneObj` construction, and placeholder quota/usage behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/impl/SingleVolumeTenantNamespace.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/impl/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/impl/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.ozone.om.multitenant.impl` as containing Ozone multitenant implementation classes.

## Important APIs, Types, And Functions

It declares only the package.

## Control Flow, State, And Persistence

There is no runtime behavior or persisted state.

## Dependencies And Integration Points

The package contains concrete namespace implementations used by `OzoneTenant`.

## Risks And Test Signals

Compilation and package documentation checks are sufficient for this file.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/impl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.ozone.om.multitenant` as containing Ozone multitenancy interfaces and identity objects.

## Important APIs, Types, And Functions

It declares only the package.

## Control Flow, State, And Persistence

There is no runtime behavior or persisted state.

## Dependencies And Integration Points

The package groups tenant, namespace, owner principal, and role principal abstractions used by OM and Ranger integration.

## Risks And Test Signals

Compilation and Javadoc/package checks cover this file.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/package-info.java

## Purpose

This package descriptor declares the base `org.apache.hadoop.ozone.om` package for common Ozone Manager classes.

## Important APIs, Types, And Functions

It declares only the package.

## Control Flow, State, And Persistence

There is no executable logic or state.

## Dependencies And Integration Points

The package is the parent namespace for OM protocol, helper, metadata, and multitenancy APIs in the common module.

## Risks And Test Signals

No direct behavioral tests are needed; compilation and package consistency checks are enough.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OMAdminProtocol.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OMAdminProtocol.java

## Purpose

`OMAdminProtocol` defines administrative RPCs for Ozone Manager metadata and maintenance operations.

## Important APIs, Types, And Functions

It extends `Closeable` and declares `getOMConfiguration`, `decommission`, `compactOMDB`, and `triggerSnapshotDefrag`. It is annotated with Kerberos server principal configuration.

## Control Flow, State, And Persistence

This is an RPC interface only. Implementations read OM HA configuration, mutate HA membership during decommission, compact RocksDB column families, or trigger snapshot defragmentation. State changes occur in OM implementation and metadata stores, not here.

## Dependencies And Integration Points

It depends on `OMConfiguration`, `OMNodeDetails`, `OMConfigKeys`, and Hadoop `KerberosInfo`. It integrates with admin clients and server-side OM admin protocol translators.

## Risks And Test Signals

Admin operations are high-impact. Tests should cover Kerberos binding, HA config responses, decommission validation, invalid column family compaction requests, no-wait and wait defrag paths, and close behavior in client translators.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OMAdminProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OMConfiguration.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OMConfiguration.java

## Purpose

`OMConfiguration` is a transfer object for OM HA configuration, separating nodes currently in memory from nodes reloaded from the latest on-disk configuration.

## Important APIs, Types, And Functions

The nested `Builder` adds nodes to in-memory and new-config lists. Public methods are `getCurrentPeerList`, `getActiveOmNodesInNewConf`, and `getDecommissionedNodesInNewConf`.

## Control Flow, State, And Persistence

The constructor copies supplied node lists into internal lists. Query methods stream over those lists, returning current peer node IDs, active reloaded nodes, and decommissioned reloaded nodes. It does not store OM configuration itself; it transports snapshots through `OMAdminProtocol`.

## Dependencies And Integration Points

It depends on HDDS `NodeDetails` and OM `OMNodeDetails`. It is returned by admin protocol implementations and consumed by CLI/admin workflows for OM decommissioning and configuration reload checks.

## Risks And Test Signals

Duplicate node IDs are resolved by keeping the later stream value in map collectors. Tests should cover empty configs, duplicate node IDs, decommissioned filtering, current peer list excluding decommissioned in-memory nodes by construction, and builder copy isolation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OMConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OMInterServiceProtocol.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OMInterServiceProtocol.java

## Purpose

`OMInterServiceProtocol` defines RPCs used between OM services, currently for bootstrapping a new OM node.

## Important APIs, Types, And Functions

It extends `Closeable` and declares `bootstrap(OMNodeDetails newOMNode)`.

## Control Flow, State, And Persistence

The interface has no implementation. Server implementations handle bootstrap flow, likely transferring metadata or configuration required to join the OM HA ring. State changes occur in OM storage and Ratis/HA configuration layers.

## Dependencies And Integration Points

It depends on `OMNodeDetails` and IO close/exception types. It integrates with OM HA add-node workflows and inter-service protocol translators.

## Risks And Test Signals

Bootstrap is sensitive to node identity and cluster membership. Tests should cover valid new node details, duplicate node IDs, network failures, idempotent retries, and client translator close behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OMInterServiceProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OzoneManagerProtocol.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OzoneManagerProtocol.java

## Purpose

`OzoneManagerProtocol` is the main Java client/server contract for OM metadata operations. It spans volume, bucket, key, multipart upload, S3 secret, tenant, snapshot, filesystem, ACL, DB update, prepare, lease, safe mode, tagging, quota repair, and upgrade-finalization APIs.

## Important APIs, Types, And Functions

The interface extends `IOmMetadataReader`, `OzoneManagerSecurityProtocol`, and `Closeable`, and carries Kerberos/token annotations. Abstract read-style methods include volume/bucket listing and info, key lookup/info, service discovery, open-file listing, tenant reads, list status, DB updates, echo RPC, lease recovery, safe mode, object tagging read, and quota repair status. Many write APIs are default methods throwing `UnsupportedOperationException` because write requests use newer request-submission paths.

## Control Flow, State, And Persistence

This file defines protocol shape rather than implementation. Implementations route read methods directly and write methods through OM request/Ratis paths. The API exposes pagination tokens, snapshot diff jobs, prepare-state queries, upgrade progress, and DB update streams; durable state lives in OM metadata tables, Ratis logs, delegation token state, snapshot checkpoints, tenant tables, and secret tables.

## Dependencies And Integration Points

It depends on nearly every common OM helper model plus HDDS SCM allocation types, ACLs, protobuf response/request types, snapshot response types, upgrade finalization, safe mode, and security token annotations. It integrates with client-side translators, server-side translators, S3 gateway, OzoneFS, admin/CLI tooling, Recon/DB sync, HA failover, and OM metadata readers.

## Risks And Test Signals

The interface mixes old direct methods with newer default unsupported write methods; translators must choose the correct path. Tests should cover every translator mapping, unsupported defaults, pagination boundaries, tenant/snapshot/multipart flows, follower-read consistency, prepare/finalize transitions, DB update streaming, safe mode actions, ACL/tagging semantics, and backward compatibility for deprecated methods.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OzoneManagerProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OzoneManagerSecurityProtocol.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OzoneManagerSecurityProtocol.java

## Purpose

`OzoneManagerSecurityProtocol` defines delegation token operations supported by OM.

## Important APIs, Types, And Functions

It declares `getDelegationToken(Text renewer)`, `renewDelegationToken(Token<OzoneTokenIdentifier>)`, and `cancelDelegationToken(Token<OzoneTokenIdentifier>)`.

## Control Flow, State, And Persistence

The interface has no implementation. Implementations issue, renew, and cancel tokens through OM security/token managers. Token state may be persisted or replicated by OM security infrastructure.

## Dependencies And Integration Points

It depends on Hadoop `Token`, `Text`, and Ozone token identifier classes. It is inherited by `OzoneManagerProtocol` and used by secure clients and delegation token selectors.

## Risks And Test Signals

Security behavior depends on authentication and token manager state. Tests should cover authorized issuance, renewer validation, renewal expiry, cancellation, invalid token handling, HA/failover behavior, and insecure cluster behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OzoneManagerSecurityProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/S3Auth.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/S3Auth.java

## Purpose

`S3Auth` carries S3 signature authentication data from gateway/client layers to OM request handling.

## Important APIs, Types, And Functions

The class stores the string-to-sign, signature, access ID, and user principal. It exposes getters and a setter for `userPrincipal`, which can be filled after access ID resolution.

## Control Flow, State, And Persistence

Instances are transient per-request authentication context. OM or gateway code resolves the access ID to a user principal and may place this object in thread-local client protocol state. It is not persisted.

## Dependencies And Integration Points

It integrates with `OzoneManagerClientProtocol` thread-local S3 auth, S3 secret lookup, request signing, and `OzoneIdentityProvider` caller-context attribution.

## Risks And Test Signals

The object is mutable only for user principal, so thread-local cleanup is critical. Tests should cover signature/access ID propagation, principal resolution, failed auth, thread-local clear behavior, and concurrent S3 requests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/S3Auth.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/package-info.java

## Purpose

This package descriptor declares `org.apache.hadoop.ozone.om.protocol` for OM Java protocol interfaces and request context objects.

## Important APIs, Types, And Functions

It declares only the package.

## Control Flow, State, And Persistence

There is no runtime behavior or persisted state.

## Dependencies And Integration Points

The package contains OM client/admin/security/inter-service protocol contracts and configuration transfer models.

## Risks And Test Signals

Compilation and package documentation checks are sufficient for this descriptor.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/GrpcOmTransport.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/GrpcOmTransport.java

## Purpose

`GrpcOmTransport` is the gRPC implementation of `OmTransport`, primarily for S3 gateway to OM communication with HA failover support and optional TLS.

## Important APIs, Types, And Functions

Important methods are static `setCaCerts`, constructor, `start`, `submitRequest`, `unwrapException`, `shouldRetry`, `getDelegationTokenService`, `shutdown`, `close`, `startClient`, and nested `GrpcOmTransportConfig`. It maintains gRPC blocking stubs and managed channels per OM node.

## Control Flow, State, And Persistence

Construction builds a `GrpcOMFailoverProxyProvider`, initializes host state, channel/stub maps, max response size, and retry policy. `submitRequest` injects local client IP/hostname into gRPC context, invokes the current stub, unwraps status exceptions, and uses the retry policy to fail over by updating the current host. `shutdown` closes channels and waits up to a bounded timeout. The transport keeps runtime connection/failover state only.

## Dependencies And Integration Points

It depends on gRPC, Netty TLS, `SecurityConfig`, OM failover proxy provider, retry policies, gRPC client interceptors, OM request/response protobufs, UGI, and Ozone config keys. It integrates with `GrpcOmTransportFactory`, S3 gateway protocol clients, secure service discovery CA material, and OM gRPC service implementations.

## Risks And Test Signals

TLS setup logs errors but may continue with a channel builder; `getDelegationTokenService` returns empty text; exception unwrapping uses reflective class loading and fragile status descriptions. Tests should cover TLS with CA certs, SSL handshake failure mapping, failover on unavailable OM, resource-exhausted/data-loss propagation, client-address metadata, shutdown timeout, concurrent failover, and injected test channels.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/GrpcOmTransport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/GrpcOmTransportFactory.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/GrpcOmTransportFactory.java

## Purpose

`GrpcOmTransportFactory` creates gRPC-backed OM transports.

## Important APIs, Types, And Functions

It implements `OmTransportFactory.createOmTransport(ConfigurationSource, UserGroupInformation, String)` and returns a new `GrpcOmTransport`.

## Control Flow, State, And Persistence

The factory is stateless. Each call constructs a transport, which immediately initializes its failover provider and gRPC channels.

## Dependencies And Integration Points

It depends on `OmTransportFactory`, `GrpcOmTransport`, configuration, UGI, and IO exceptions. It is selected by the configurable OM transport factory mechanism.

## Risks And Test Signals

Failures are constructor/channel setup failures from `GrpcOmTransport`. Tests should cover factory selection, service ID propagation, UGI propagation, and error handling when gRPC endpoints are misconfigured.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/GrpcOmTransportFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/Hadoop3OmTransport.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/Hadoop3OmTransport.java

## Purpose

`Hadoop3OmTransport` is the Hadoop RPC implementation of `OmTransport` with OM HA failover and optional follower-read routing.

## Important APIs, Types, And Functions

Important methods are the constructor, `submitRequest`, `getDelegationTokenService`, testing getters for failover providers, and `close`. The constructor configures protobuf RPC engine, leader failover provider, follower-read proxy provider, max failovers, and default read-consistency modes.

## Control Flow, State, And Persistence

`submitRequest` delegates one `OMRequest` to the protobuf RPC proxy. It unwraps `ServiceException` into remote exceptions, and maps unresolved not-leader handling to a generic leader connection failure. The transport holds runtime proxy/failover state; no OM metadata is persisted here.

## Dependencies And Integration Points

It depends on Hadoop RPC/protobuf engine, Ozone configuration keys, OM failover providers, `ReadConsistency`, OM protobuf protocol, UGI, and delegation token text. It is the default full-featured client transport used by OM protocol translators.

## Risks And Test Signals

Configuration strings are converted with `ReadConsistency.valueOf`, so invalid values fail at startup. Tests should cover leader failover, follower-read enabled/disabled routing, read consistency defaults, remote exception unwrapping, not-leader handling, delegation token service updates, and close behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/Hadoop3OmTransport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/Hadoop3OmTransportFactory.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/Hadoop3OmTransportFactory.java

## Purpose

`Hadoop3OmTransportFactory` creates Hadoop RPC-backed OM transports.

## Important APIs, Types, And Functions

It implements `OmTransportFactory.createOmTransport(ConfigurationSource, UserGroupInformation, String)` and returns a new `Hadoop3OmTransport`.

## Control Flow, State, And Persistence

The factory has no state. Each invocation constructs a transport configured with the supplied configuration, user, and OM service ID.

## Dependencies And Integration Points

It depends on `OmTransportFactory`, `Hadoop3OmTransport`, configuration, UGI, and IO exceptions. It integrates with the transport factory selection path used by OM protocol clients.

## Risks And Test Signals

Factory behavior is simple, so most risk is constructor propagation. Tests should cover default factory selection, HA service ID propagation, UGI propagation, and startup failures for invalid follower-read consistency config.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/Hadoop3OmTransportFactory.java -->
