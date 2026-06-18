# subset-b-008098 Research

Grouped source research for Apache Ozone OM request classes. Each section preserves the original source path and is delimited for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/OMClientRequestUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/OMClientRequestUtils.java

## Purpose

`OMClientRequestUtils` is a small static utility class used by Ozone Manager client request handlers. It centralizes request precondition checks that are shared across request implementations: bucket-layout compatibility, snapshot-bucket detection, and selective failure logging.

## Important APIs, Types, And Functions

- `checkClientRequestPrecondition(BucketLayout dbBucketLayout, BucketLayout reqClassBucketLayout)` verifies that a request handler selected for filesystem-optimized or non-FSO handling matches the actual bucket layout. It throws `OMException(INTERNAL_ERROR)` on mismatch.
- `isSnapshotBucket(OMMetadataManager, OmKeyInfo)` builds the bucket snapshot key prefix from the key's volume and bucket, then checks both snapshot table cache and persisted table.
- `shouldLogClientRequestFailure(IOException)` suppresses client-request failure logs for `OMException.ResultCodes.KEY_NOT_FOUND` and logs all other exception classes/result codes.

## Control Flow And State

The layout check is pure validation. Snapshot detection first scans the in-memory table cache for non-null `SnapshotInfo` entries with the bucket prefix, then seeks the RocksDB-backed `snapshotInfoTable` and tests the next key prefix. This cache-then-DB pattern catches unflushed snapshot creates while avoiding false positives for cache tombstones. No table is mutated by this class.

## Dependencies And Integration Points

The utility depends on `OMMetadataManager`, Ozone metadata table iterators/cache iterators, `BucketLayout`, `OmKeyInfo`, `SnapshotInfo`, and `OMException`. It is an integration guard for request dispatch logic and snapshot-aware operations elsewhere in `om.request`.

## Risks And Test Signals

Important risk is prefix correctness: snapshot keys append `OM_KEY_PREFIX` to the bucket DB key to avoid matching buckets with common prefixes. Tests should cover cache-only snapshots, DB-only snapshots, tombstoned cache values, non-snapshot buckets with similar names, and bucket-layout mismatch behavior. Logging tests should confirm `KEY_NOT_FOUND` failures are intentionally quiet while other failures remain visible.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/OMClientRequestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/RequestAuditor.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/RequestAuditor.java

## Purpose

`RequestAuditor` is the audit-map contract implemented by OM request classes. It defines how request handlers build `OMAuditLogger` messages and provides default helpers for common volume and key audit fields.

## Important APIs, Types, And Functions

- `buildAuditMessage(AuditAction, Map<String,String>, Throwable, UserInfo)` is the main implementor hook for audit logging.
- `buildVolumeAuditMap(String)` is an implementor hook for volume-scoped operations.
- `buildLightKeyArgsAuditMap(KeyArgs)` emits volume, bucket, and key only.
- `buildKeyArgsAuditMap(KeyArgs)` extends the light map with data size, replication type/factor/config, rewrite generation, and the `ETAG` metadata item when present.

## Control Flow And State

The default helpers are null-safe and return empty maps for null `KeyArgs`. They use `LinkedHashMap` for populated key audit maps so audit output remains ordered. The implementation intentionally excludes most metadata and only promotes `ETAG`, keeping audit records useful without dumping arbitrary user metadata.

## Dependencies And Integration Points

The interface depends on Ozone protocol `KeyArgs` and `UserInfo`, audit abstractions, `OzoneConsts`, `HddsProtos`, and `ECReplicationConfig`. Request classes call these helpers when logging after lock release, usually with operation-specific `OMAction` values and captured exceptions.

## Risks And Test Signals

Risk centers on missing audit context after protocol changes. Tests should verify EC replication config is serialized, factor `ZERO` is omitted, rewrite generation and etag are included, null inputs are safe, and audit maps remain stable enough for log parsing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/RequestAuditor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/OMBucketCreateRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/OMBucketCreateRequest.java

## Purpose

`OMBucketCreateRequest` handles `CreateBucket` requests. It validates bucket naming, ACLs, encryption, replication defaults, bucket links, bucket-count limits, quotas, default ACL inheritance, bucket layout compatibility, and metadata-table cache updates.

## Important APIs, Types, And Functions

- `preExecute(OzoneManager)` validates the requested bucket name, performs create ACL checks, enforces `ozone.om.max.bucket`, resolves bucket encryption key info via KMS, validates source volume/bucket link fields, rejects encryption on bucket links, validates default replication config, and stamps creation/modification time.
- `validateAndUpdateCache(OzoneManager, ExecutionContext)` is the state mutation path.
- `checkQuotaBytesValid(...)` ensures bucket space quota is compatible with volume quota and existing bucket quotas.
- `checkQuotaInNamespace(...)` checks volume namespace quota before consuming one namespace entry for the new bucket.
- `addDefaultAcls(...)` merges configured user defaults and inherited volume default ACLs.
- Request validators reject EC bucket defaults before EC finalization, handle bucket layout before finalization, and force old clients to create `LEGACY` buckets.

## Control Flow And State

Validation acquires a volume read lock and bucket write lock, checks volume existence and bucket absence, validates quota, assigns object ID from transaction index, sets update ID, inherits ACLs, increments volume used namespace, and writes both volume and bucket cache entries. The response is `OMBucketCreateResponse`, which later persists the cache mutations through the double buffer. Auditing happens after locks are released.

## Dependencies And Integration Points

This class integrates with `OMMetadataManager` volume and bucket tables, OM locks, `OMMetrics`, KMS/BekInfo resolution, default replication validation, bucket layout upgrade validators, `OmBucketInfo`, `OmVolumeArgs`, ACL utilities, and `OMBucketCreateResponse`.

## Risks And Test Signals

High-risk areas are quota accounting, default bucket layout behavior for old clients, source bucket link validation, EC pre-finalization rejection, and ACL inheritance when `ignoreClientACLs` is enabled. Tests should assert table cache entries, object/update IDs, volume namespace increments, EC metrics, FSO bucket metrics, audit behavior on preExecute ACL failures, and errors for duplicate buckets, missing volumes, invalid quotas, and too many buckets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/OMBucketCreateRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/OMBucketDeleteRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/OMBucketDeleteRequest.java

## Purpose

`OMBucketDeleteRequest` deletes an empty bucket and updates volume namespace accounting. It protects buckets that contain keys, incomplete multipart uploads, or snapshots, and blocks old clients from deleting bucket layouts they cannot understand.

## Important APIs, Types, And Functions

- `validateAndUpdateCache(OzoneManager, ExecutionContext)` performs ACL validation, lock acquisition, existence checks, emptiness checks, snapshot checks, cache tombstone writes, and response construction.
- `bucketContainsSnapshot(...)` checks snapshot presence in both cache and persisted table using the bucket snapshot prefix.
- `blockBucketDeleteWithBucketLayoutFromOldClient(...)` validates bucket-layout support for older clients.

## Control Flow And State

The request increments delete metrics, checks bucket delete ACLs, then acquires volume read and bucket write locks. It loads `OmBucketInfo`, rejects missing/non-empty buckets, rejects incomplete MPUs, and rejects snapshot-containing buckets. On success it writes a tombstone cache entry to the bucket table, decrements the in-memory bucket metric, decrements the volume's used namespace, writes the updated volume cache entry, and returns `OMBucketDeleteResponse`. Locks are released before audit logging.

## Dependencies And Integration Points

It depends on `OMMetadataManager` bucket, volume, MPU, and snapshot APIs; `OzoneManagerLock` bucket/volume lock levels; `SnapshotInfo`; `OMBucketDeleteResponse`; and request validation infrastructure for old-client layout guards.

## Risks And Test Signals

Important edge cases include cache-only snapshots, tombstoned snapshots, incomplete MPU detection, volume namespace decrement, and bucket emptiness across layouts. Tests should cover snapshot prefix collisions, bucket recreation with same name, FSO delete metrics, lock detail propagation, and error responses for missing bucket, non-empty bucket, incomplete MPU, snapshot containment, and old-client layout rejection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/OMBucketDeleteRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/OMBucketSetOwnerRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/OMBucketSetOwnerRequest.java

## Purpose

`OMBucketSetOwnerRequest` handles the owner-change variant of `SetBucketProperty`. It updates only the owner and modification/update metadata for an existing bucket.

## Important APIs, Types, And Functions

- `preExecute(OzoneManager)` stamps the set-bucket-property request with current modification time and user info.
- `validateAndUpdateCache(OzoneManager, ExecutionContext)` validates the owner field, checks `WRITE_ACL`, loads the bucket, handles no-op same-owner requests, updates `OmBucketInfo.owner`, and emits `OMBucketSetOwnerResponse`.

## Control Flow And State

The method rejects requests without `ownerName` as `INVALID_REQUEST` before acquiring locks. For valid input it increments bucket-update metrics, acquires the bucket write lock, reads the bucket row, rejects missing buckets, compares old owner, and either returns a no-op response with `success=false` but status `OK`, or writes a new bucket cache entry with updated owner, modification time, and update ID. Audit logging occurs outside the lock.

## Dependencies And Integration Points

It uses `SetBucketPropertyRequest/BucketArgs`, `OmBucketArgs` audit conversion, bucket table cache writes, OM ACL checks, `OMBucketSetOwnerResponse`, and OM metrics.

## Risks And Test Signals

The unusual same-owner path returns status OK while marking response false, so client behavior should be tested. Other tests should cover missing owner, missing bucket, ACL denial, null old owners from pre-HDDS-6171 metadata, modification time propagation from preExecute, cache update IDs, and failure metric increments.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/OMBucketSetOwnerRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/OMBucketSetPropertyRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/OMBucketSetPropertyRequest.java

## Purpose

`OMBucketSetPropertyRequest` updates mutable bucket properties: metadata, storage type, versioning, byte and namespace quotas, default replication config, and encryption key info. It deliberately rejects property updates on bucket links.

## Important APIs, Types, And Functions

- `preExecute(OzoneManager)` stamps modification time and resolves bucket encryption key info through the KMS provider when requested.
- `validateAndUpdateCache(OzoneManager, ExecutionContext)` performs authorization, loads bucket/volume state, applies requested fields to an `OmBucketInfo.Builder`, validates quotas, and writes a bucket cache update.
- `checkAclPermission(...)` uses native admin/owner semantics for native ACLs and `WRITE` ACL for Ranger/external authorizers.
- `checkQuotaBytesValid(...)` and `checkQuotaNamespaceValid(...)` enforce reset rules and prevent setting quotas below existing usage.
- `disallowSetBucketPropertyWithECReplicationConfig(...)` rejects EC defaults before EC finalization.

## Control Flow And State

The request increments bucket-update metrics, resolves `OmBucketArgs`, acquires the bucket write lock, rejects missing buckets and links, merges metadata, updates modification/update IDs, conditionally updates storage type/versioning/quotas/default replication/encryption, and writes the new `OmBucketInfo` to the bucket table cache. It reads volume state for quota validation but does not mutate volume state. Audit logging is outside the lock.

## Dependencies And Integration Points

The class integrates with KMS/BekInfo, `OMMetadataManager` bucket and volume tables, quota constants, `DefaultReplicationConfig`, native and external ACL authorizers, `OMBucketSetPropertyResponse`, and upgrade validation.

## Risks And Test Signals

Risks include quota reset semantics when volume quota is still set, quota reductions below used bytes/namespace, metadata overwrite/merge behavior, encryption key resolution, and ACL differences between native and Ranger paths. Tests should cover link rejection, EC pre-finalization rejection, all optional property fields, volume quota aggregation across buckets, successful cache update IDs, and failure metric increments.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/OMBucketSetPropertyRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/acl/OMBucketAclRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/acl/OMBucketAclRequest.java

## Purpose

`OMBucketAclRequest` is the abstract base for add, remove, and set ACL operations on buckets. It contains shared parsing, link resolution, authorization, locking, ACL mutation, cache update, response callback, and completion/audit flow.

## Important APIs, Types, And Functions

- Constructor accepts an `AclOp`, a functional operation that mutates the bucket ACL builder.
- `validateAndUpdateCache(OzoneManager, ExecutionContext)` implements the shared request lifecycle.
- Abstract hooks `getAcls`, `getPath`, `getObject`, `onInit`, `onSuccess`, and `onComplete` let concrete operations supply protocol-specific behavior.
- `onFailure(...)` defaults to an `OMBucketAclResponse` error response.

## Control Flow And State

The method parses the requested object path as a bucket object, resolves bucket links to the real bucket, checks `WRITE_ACL`, acquires the real bucket write lock, loads `OmBucketInfo`, applies the `AclOp`, and only writes a cache update when the operation actually changes ACL state. The update includes transaction update ID and a modification time extracted from the concrete ACL request. It then builds success/failure responses through callbacks, releases locks, and calls completion hooks with audit data that includes the ACL list.

## Dependencies And Integration Points

It depends on `ObjectParser`, `ResolvedBucket`, `AclOp`, `OzoneAcl`, `OzoneObj`, bucket-table cache APIs, `OMBucketAclResponse`, and OM ACL enforcement. Link resolution means ACL updates target the underlying real bucket, not merely a link facade.

## Risks And Test Signals

Risks include wrong request-field probing for modification time, ACL no-op behavior, link resolution correctness, and null volume/bucket lock release if parsing fails before assignment. Tests should cover add duplicate, remove missing, set same list, set different list, bucket link targets, missing bucket, ACL denial, audit ACL contents, and lock detail propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/acl/OMBucketAclRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/acl/OMBucketAddAclRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/acl/OMBucketAddAclRequest.java

## Purpose

`OMBucketAddAclRequest` is the concrete bucket ACL add operation. It wraps the shared `OMBucketAclRequest` flow with single-ACL extraction, `AddAclResponse`, add-specific metrics, and add-specific audit/logging.

## Important APIs, Types, And Functions

- Constructor converts the protobuf object to `OzoneObjInfo`, stores its path, and converts the protobuf ACL to a singleton `OzoneAcl` list.
- `preExecute(OzoneManager)` stamps current modification time and user info.
- `onSuccess(...)` writes `AddAclResponse.response` and sets top-level success to the operation result.
- `validateAndUpdateCache(...)` increments `incNumAddAcl()` before delegating to the base implementation.

## Control Flow And State

The actual mutation is provided to the base class as `builder.add(acls.get(0))`. If the ACL is new, the base class writes an updated bucket cache entry. If the ACL already exists, no cache entry is written, the response carries `response=false`, and completion increments bucket update failure metrics.

## Dependencies And Integration Points

It integrates with protobuf `AddAclRequest/AddAclResponse`, `OzoneAcl`, `OzoneObjInfo`, `OMBucketAclResponse`, and `OMAction.ADD_ACL` audit logging.

## Risks And Test Signals

Tests should verify modification time is used only on successful mutations, duplicate adds return false without state changes, add metrics increment independently from bucket update metrics, audit output includes the ACL string, and link/missing-bucket/ACL-denied cases inherit base behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/acl/OMBucketAddAclRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/acl/OMBucketRemoveAclRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/acl/OMBucketRemoveAclRequest.java

## Purpose

`OMBucketRemoveAclRequest` is the concrete bucket ACL remove operation. It supplies the shared base class with a single ACL removal operation and returns protocol-specific remove responses.

## Important APIs, Types, And Functions

- Constructor parses `RemoveAclRequest.obj` and `acl`, stores the path, object, and singleton ACL list.
- `preExecute(OzoneManager)` adds modification time and user info.
- `onSuccess(...)` emits `RemoveAclResponse.response`.
- `onComplete(...)` audits `OMAction.REMOVE_ACL`, logs missing-ACL/no-op failures distinctly, and increments failure metrics when operation result is false.
- `validateAndUpdateCache(...)` increments remove-ACL metrics, then delegates.

## Control Flow And State

The mutation lambda is `builder.remove(acls.get(0))`. A true result causes the base class to update bucket ACLs, modification time, and update ID in the bucket table cache. A false result represents removing a non-existent ACL and returns a successful protocol envelope with `response=false` but no metadata mutation.

## Dependencies And Integration Points

The class depends on `OzoneAcl`, `OzoneObjInfo`, protobuf remove ACL messages, OM metrics, audit logger, and `OMBucketAclResponse`.

## Risks And Test Signals

Tests should exercise removal of existing and missing ACLs, response boolean semantics, metric increments, audit map ACL formatting, modification time stamping, and inherited behavior for link resolution, lock release, and bucket-not-found errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/acl/OMBucketRemoveAclRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/acl/OMBucketSetAclRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/acl/OMBucketSetAclRequest.java

## Purpose

`OMBucketSetAclRequest` replaces the full ACL list on a bucket. It adapts the shared `OMBucketAclRequest` lifecycle for multi-ACL set semantics.

## Important APIs, Types, And Functions

- Constructor converts `SetAclRequest.aclList` into a `List<OzoneAcl>`.
- `preExecute(OzoneManager)` stamps modification time and user info.
- The supplied `AclOp` calls `builder.set(acls)`.
- `onSuccess(...)` writes `SetAclResponse.response`.
- `validateAndUpdateCache(...)` increments set-ACL metrics before base validation/update.

## Control Flow And State

When the new ACL list differs from the current bucket ACL builder state, the base class writes a new `OmBucketInfo` cache entry with updated ACLs, modification time, and update ID. If no effective change is made, response boolean is false and bucket update failure metrics are incremented.

## Dependencies And Integration Points

The request integrates with protobuf `SetAclRequest/SetAclResponse`, `OzoneObjInfo`, stream conversion from protobuf ACLs, `OMBucketAclResponse`, and `OMAction.SET_ACL`.

## Risks And Test Signals

Risk is mostly around set semantics and idempotency. Tests should compare empty, identical, reordered, and changed ACL lists; verify response booleans and cache writes; ensure modification time comes from preExecute; and cover inherited bucket link, authorization, and missing-bucket cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/acl/OMBucketSetAclRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/acl/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/acl/package-info.java

## Purpose

This `package-info.java` documents `org.apache.hadoop.ozone.om.request.bucket.acl` as the package containing bucket ACL request handlers.

## Important APIs, Types, And Functions

The file declares only the package and contains no classes or executable APIs.

## Control Flow And State

There is no control flow or persistent state. Its value is package-level documentation for generated Javadocs and source organization.

## Dependencies And Integration Points

It has no imports or runtime dependencies. It groups `OMBucketAclRequest`, `OMBucketAddAclRequest`, `OMBucketRemoveAclRequest`, and `OMBucketSetAclRequest`.

## Risks And Test Signals

No direct runtime tests are needed. Build/Javadoc checks are sufficient to catch syntax or package declaration drift.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/acl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/package-info.java

## Purpose

This `package-info.java` documents `org.apache.hadoop.ozone.om.request.bucket` as the package containing bucket request handlers.

## Important APIs, Types, And Functions

The file declares only the package and contains no executable APIs.

## Control Flow And State

There is no runtime control flow or state mutation.

## Dependencies And Integration Points

It has no imports. It is the package-level documentation anchor for bucket create, delete, owner, property, and ACL request subpackages.

## Risks And Test Signals

No functional test is required beyond compilation/Javadoc generation. The main signal is that the package declaration matches the directory path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMDirectoryCreateRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMDirectoryCreateRequest.java

## Purpose

`OMDirectoryCreateRequest` handles directory creation for non-FSO bucket layouts by representing directories as key-table entries. It creates missing parent directories when needed and enforces filesystem path conflict rules.

## Important APIs, Types, And Functions

- `preExecute(OzoneManager)` normalizes request metadata, rejects snapshot reserved words, sets modification time, resolves bucket links, and checks `CREATE` ACLs.
- `validateAndUpdateCache(OzoneManager, ExecutionContext)` validates bucket/volume, rejects root directory creation, verifies files/directories in path, creates missing parent `OmKeyInfo` entries, creates the leaf directory key, checks namespace quota, and returns `OMDirectoryCreateResponse`.
- `Result` captures `SUCCESS`, `DIRECTORY_ALREADY_EXISTS`, and `FAILURE`.
- Validators reject EC configs before finalization and block old clients from operating on unsupported bucket layouts.

## Control Flow And State

The request acquires the bucket write lock, calls `OMFileRequest.verifyFilesInPath`, rejects file conflicts, treats existing directory as idempotent `DIRECTORY_ALREADY_EXISTS`, and for missing paths builds directory key info plus missing parent info using inherited `OMKeyRequest` helpers. It increments bucket used namespace by missing parents plus leaf directory and writes key-table cache entries through `OMFileRequest.addKeyTableCacheEntries`. Auditing and metric logging occur after lock release.

## Dependencies And Integration Points

The class integrates with `OMKeyRequest` helpers for key info, ACL inheritance and quota checks, `OMFileRequest` path verification/cache utilities, `OMDirectoryCreateResponse`, OM metadata tables, bucket layout validators, and OM metrics/audit.

## Risks And Test Signals

Tests should cover root path rejection, file-in-path conflicts, existing directory idempotency, recursive missing-parent creation, namespace quota accounting, ACL inheritance, FSO/legacy layout validator behavior, EC pre-finalization rejection, and cache entries for parent directories and leaf directory.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMDirectoryCreateRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMDirectoryCreateRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMDirectoryCreateRequestWithFSO.java

## Purpose

`OMDirectoryCreateRequestWithFSO` is the filesystem-optimized directory-create implementation. It stores path components in the directory table using volume, bucket, parent object ID, and name keys instead of legacy key-table directory marker entries.

## Important APIs, Types, And Functions

- Overrides `validateAndUpdateCache(OzoneManager, ExecutionContext)`.
- Uses `OMFileRequest.verifyDirectoryKeysInPath(...)` to walk the FSO directory and file tables.
- Builds missing parent `OmDirectoryInfo` objects and the leaf `OmDirectoryInfo`.
- Writes directory cache entries with `OMFileRequest.addDirectoryTableCacheEntries(...)`.
- Returns `OMDirectoryCreateResponseWithFSO` carrying volume/bucket IDs and created directory info.

## Control Flow And State

After rejecting root creation, the request acquires the bucket write lock, validates bucket/volume, traverses the FSO path, rejects file conflicts, and either reports already-existing directory or creates missing parents plus the leaf directory. It computes `volumeId` and `bucketId`, quota-checks the number of created entries, increments bucket namespace usage, writes directory table cache entries, and returns a double-buffer response with copied bucket info.

## Dependencies And Integration Points

It relies on `OMDirectoryCreateRequest` for preExecute and shared result enum, `OMFileRequest` FSO traversal/cache helpers, `OmDirectoryInfo`, `OMDirectoryCreateResponseWithFSO`, and bucket/object ID conventions in `OMMetadataManager`.

## Risks And Test Signals

FSO correctness depends on parent object IDs and leaf object IDs. Tests should cover file conflicts in intermediate and leaf positions, existing leaf directory, missing parent creation, namespace quota, ACL inheritance from closest parent/bucket, response volume/bucket IDs, and no legacy key-table directory marker writes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMDirectoryCreateRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMFileCreateRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMFileCreateRequest.java

## Purpose

`OMFileCreateRequest` handles filesystem-style file creation for non-FSO layouts. It allocates initial blocks during preExecute, validates path semantics, creates missing parent directory markers when recursive, writes the file to the open-key table, and defers final key-table materialization until commit.

## Important APIs, Types, And Functions

- `preExecute(OzoneManager)` validates key name, resolves replication config from request/bucket/OM defaults, allocates initial blocks, sets modification time/data size/type/factor/key locations, generates encryption info, checks create ACLs, and assigns a unique client ID.
- `validateAndUpdateCache(OzoneManager, ExecutionContext)` validates bucket and path conflicts, checks recursive parent requirements, prepares `OmKeyInfo`, appends allocated blocks, enforces byte and namespace quota, writes open-key and missing-parent key-table cache entries, and returns `OMFileCreateResponse`.
- `checkDirectoryResult(...)` rejects existing files without overwrite, directory leaf conflicts, and file-in-path conflicts.
- `checkAllParentsExist(...)` enforces non-recursive parent existence.
- Request validators reject EC pre-finalization and old-client unsupported layouts.

## Control Flow And State

PreExecute allocates blocks before full DB validation, a known tradeoff called out in comments. Validate acquires the bucket write lock, gets existing key state, walks legacy key-table path state with `OMFileRequest.verifyFilesInPath`, creates missing parent directory key infos, appends the new allocated block list to open key info, quota-checks replicated preallocated size, increments namespace only for missing parents, writes the open-key table cache entry keyed by client ID, writes parent directory cache entries, and returns block/key info to the client.

## Dependencies And Integration Points

The class integrates with SCM block allocation, block token secret manager, replication config resolution, encryption metadata generation, prefix manager, `OMFileRequest`, `OMKeyRequest`, `OMFileCreateResponse`, OM metadata open-key/key tables, and create-file protocol messages.

## Risks And Test Signals

Risks include leaked preallocated blocks on later validation failure, overwrite semantics, recursive parent handling, quota calculation using required replication nodes, encryption validation, key name validation, and old-client/EC gates. Tests should cover empty root key rejection, overwrite true/false, parent file conflicts, recursive and non-recursive creates, namespace and byte quota failures, open-key cache contents, missing parent creation, block token/key location propagation, and metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMFileCreateRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMFileCreateRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMFileCreateRequestWithFSO.java

## Purpose

`OMFileCreateRequestWithFSO` is the FSO variant of file creation. It stores parent directories in the directory table and stores the open file under an object-ID-based open-file key while keeping the user-visible full key path in the response.

## Important APIs, Types, And Functions

- Overrides `validateAndUpdateCache(...)` while inheriting block allocation, key normalization, encryption, and ACL preExecute behavior from `OMFileCreateRequest`.
- Uses `OMFileRequest.verifyDirectoryKeysInPath(...)` for FSO traversal.
- Uses `prepareFileInfo(...)` to create file `OmKeyInfo` with leaf object ID and parent object ID.
- Writes open-file entries with `OMFileRequest.addOpenFileTableCacheEntry(...)`.
- Writes missing parents with `OMFileRequest.addDirectoryTableCacheEntries(...)`.
- Returns `OMFileCreateResponseWithFSO`.

## Control Flow And State

The method rejects empty key names, locks the bucket, validates bucket/volume, calculates volume and bucket IDs, traverses the directory/file tables, loads existing file info for overwrite, validates conflicts and parent existence, prepares missing parent directory infos, resolves replication, prepares file info, appends allocated blocks, checks byte and namespace quotas, writes the open-file cache entry, writes missing directory cache entries, and returns network key info using the original full key path.

## Dependencies And Integration Points

It depends on `OMFileRequest` FSO helpers, `OmDirectoryInfo`, `OmKeyInfo`, `OzoneConfigUtil`, `OMFileCreateResponseWithFSO`, FSO metadata manager key builders, and `OMKeyRequest` helpers for quota/encryption/file info preparation.

## Risks And Test Signals

Tests should validate parent object ID use, leaf-name versus full-path key-name handling, overwrite existing file lookup, recursive missing directory creation, namespace metric count for missing parents only, no final file-table entry before commit, open-file cache key composition, quota failures, and file/directory conflict detection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMFileCreateRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMFileRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMFileRequest.java

## Purpose

`OMFileRequest` is the static utility hub for Ozone filesystem request semantics. It implements legacy and FSO path traversal, directory/file conflict detection, cache and batch writes for file/directory/open-file tables, conversion between directory and key info, child detection, parent lookup, and volume/bucket validation.

## Important APIs, Types, And Functions

- `verifyFilesInPath(...)` walks legacy key-table paths from leaf upward, detecting files/directories in the requested path and collecting missing parents plus inheritable ACLs.
- `verifyDirectoryKeysInPath(...)` walks FSO path components from the bucket object ID through directory and key tables.
- `OMPathInfo`, `OMPathInfoWithFSO`, and `OMDirectoryResult` communicate traversal result, missing parents, ACLs, leaf name, parent ID, object ID, and file-conflict path.
- Cache helpers: `addKeyTableCacheEntries`, `addDirectoryTableCacheEntries`, `addOpenFileTableCacheEntry`, `addFileTableCacheEntry`.
- Batch helpers: `addToOpenFileTable`, `addToOpenFileTableForMultipart`, `addToFileTable`.
- Lookup/conversion helpers: `getOmKeyInfoFromFileTable`, `getOMKeyInfoIfExists`, `getKeyInfoWithFullPath`, `getOmKeyInfo`, `getDirectoryInfo`, `getAbsolutePath`.
- Rename/delete helpers: `verifyToDirIsASubDirOfFromDirectory`, `getKeyParentDir`, `hasChildren`, `getParentID`, `getParentId`, `validateBucket`.

## Control Flow And State

The class itself has no mutable global state. Its methods read and write OM metadata tables. Legacy traversal uses ozone key and dir-key encodings in the key table. FSO traversal uses volume ID, bucket ID, parent object ID, and node name against directory and file tables. Cache write helpers add either values or tombstones at the transaction index, while batch helpers persist rows during double-buffer flush. Child detection scans cache first, then seeks DB by parent path key prefix and ignores DB rows tombstoned in cache.

## Dependencies And Integration Points

`OMFileRequest` is shared by directory create, file create, commit, rename, multipart, delete, and lease-recovery paths. It depends on `OMMetadataManager`, `OmBucketInfo`, `OmDirectoryInfo`, `OmKeyInfo`, `OzoneFileStatus`, `OzoneFSUtils`, RocksDB table iterators/cache, bucket layout resolution, and Ozone exception result codes.

## Risks And Test Signals

This is a high-blast-radius utility. Tests should cover legacy and FSO path traversal, trailing slash behavior, ACL inheritance from bucket or closest parent, file-versus-directory conflicts, cache tombstone masking, immediate child detection, parent ID errors, absolute path construction, full-path restoration for FSO file info, multipart/open-file key composition, and volume-not-found versus bucket-not-found error selection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMFileRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMRecoverLeaseRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMRecoverLeaseRequest.java

## Purpose

`OMRecoverLeaseRequest` starts recovery for an hsync/open FSO file lease. It marks the open key as under recovery, refreshes last-block pipeline/token information, and returns both closed key and open key metadata for recovery clients.

## Important APIs, Types, And Functions

- Constructor extracts volume, bucket, key, and force flag from `RecoverLeaseRequest`.
- `preExecute(OzoneManager)` is disallowed until `HBASE_SUPPORT`, normalizes the key, and checks key `WRITE` ACL.
- `validateAndUpdateCache(...)` locks the bucket, validates bucket/volume, delegates to `doWork`, writes an `OMRecoverLeaseResponse`, and audits `RECOVER_LEASE`.
- `doWork(...)` locates the FSO key, validates hsync metadata, resolves the open-file key by writer ID, enforces soft lease limit unless forced, marks `LEASE_RECOVERY`, updates the open-key cache, refreshes block pipeline/token data, and builds `RecoverLeaseResponse`.
- `updateBlockInfo(...)` refreshes block token and SCM pipeline for relevant last blocks.

## Control Flow And State

The request targets only `FILE_SYSTEM_OPTIMIZED` layout. It uses `OmFSOFile` to derive file/open-file DB keys. The closed key table row must exist and carry `HSYNC_CLIENT_ID`; otherwise the file is treated as closed or missing. The open-key row must exist and not be deleted. If already under recovery, the operation is idempotent; otherwise it checks the configured lease soft limit, adds `LEASE_RECOVERY=true`, updates modification time/update ID, and writes the open-key table cache entry.

## Dependencies And Integration Points

It integrates with FSO metadata key builders, open-key/key tables, hsync metadata constants, SCM container pipeline lookup, gRPC block token generation, layout feature gating, OM metrics, and `OMRecoverLeaseResponse`.

## Risks And Test Signals

Tests should cover forced and non-forced soft-limit behavior, missing closed key, already closed key, missing open key, deleted open key, already-under-recovery idempotency, token generation when enabled, pipeline refresh, metadata mutation, lock/audit behavior, and layout-feature gating.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMRecoverLeaseRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/package-info.java

## Purpose

This `package-info.java` documents `org.apache.hadoop.ozone.om.request.file` as the package containing file request handlers and helpers.

## Important APIs, Types, And Functions

The file declares only the package and no executable APIs.

## Control Flow And State

There is no runtime behavior or state.

## Dependencies And Integration Points

It has no imports. It groups directory create, file create, lease recovery, and shared filesystem request utilities.

## Risks And Test Signals

Compilation/Javadoc generation is sufficient. The package declaration should remain aligned with the directory path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMAllocateBlockRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMAllocateBlockRequest.java

## Purpose

`OMAllocateBlockRequest` allocates an additional block for an open key. It is used by streaming writes after initial key/file creation and updates the open-key table with the new block location while enforcing bucket quota and lease-recovery constraints.

## Important APIs, Types, And Functions

- `preExecute(OzoneManager)` normalizes the key, rebuilds an `ExcludeList`, allocates one SCM block with tokens if configured, stamps modification time, checks open-key write ACLs, preserves client ID/exclude list, and embeds the allocated block in the request.
- `validateAndUpdateCache(OzoneManager, ExecutionContext)` validates volume/bucket, locates open key, rejects missing/deleted/overwritten/lease-recovery open keys, quota-checks existing plus newly allocated space, appends the block, updates modification time/update ID, writes open-key cache, and returns `OMAllocateBlockResponse`.
- Protected methods `getOpenKeyInfo`, `getOpenKeyName`, `addOpenTableCacheEntry`, and response factories are overridden by FSO.
- Validators reject EC requests before finalization and old-client operations on unsupported bucket layouts.

## Control Flow And State

PreExecute allocates from SCM before full metadata validation, a documented tradeoff. Validate initially avoids locks while locating the open key, then acquires the bucket write lock for quota and cache mutation. It computes total allocated space from existing and new block counts using `QuotaUtil` and the open key's replication config, appends one block, writes a cache entry to the open-key table, and audits outside the lock.

## Dependencies And Integration Points

The class depends on SCM block allocation, block tokens, `ExcludeList`, open-key table APIs, quota utilities, hsync metadata constants, `OMAllocateBlockResponse`, request validation, OM metrics, and ACL checks against the open key.

## Risks And Test Signals

Tests should cover missing open key, lease recovery, deleted/overwritten hsync metadata, quota failures, modification time/update ID updates, block-token/exclude-list propagation, old-client/EC gates, response block location, and lock detail propagation. Race behavior with bucket delete/rename is intentionally deferred to commit and should be documented in tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMAllocateBlockRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMAllocateBlockRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMAllocateBlockRequestWithFSO.java

## Purpose

`OMAllocateBlockRequestWithFSO` adapts block allocation to filesystem-optimized open-file table addressing and response persistence.

## Important APIs, Types, And Functions

- `getOpenKeyInfo(...)` loads open-file info from the FSO open-key table and restores the leaf file name via `OMFileRequest.getOmKeyInfoFromFileTable(true, ...)`.
- `getOpenKeyName(...)` uses `OmFSOFile` to derive the object-ID-based open-file DB key for the client ID.
- `addOpenTableCacheEntry(...)` delegates to `OMFileRequest.addOpenFileTableCacheEntry`, preserving the full user key path in the cached `OmKeyInfo`.
- `getOmClientResponse(...)` returns `OMAllocateBlockResponseWithFSO` with volume ID and bucket object ID.
- `getOmClientErrorResponse(...)` returns the FSO error response variant.

## Control Flow And State

The superclass owns validation, quota checking, block append, and audit flow. This subclass only changes lookup/cache key construction and the response object so FSO double-buffer persistence can update the open-file row correctly.

## Dependencies And Integration Points

It integrates with `OmFSOFile`, `OzoneFSUtils`, `OMFileRequest`, `OMAllocateBlockResponseWithFSO`, `OMMetadataManager` volume ID lookup, and bucket object ID semantics.

## Risks And Test Signals

Tests should ensure open-file keys are derived from parent object ID and leaf file name, full key path is preserved in cached `OmKeyInfo`, response carries correct volume/bucket IDs, and inherited lease/quota/error behavior matches the non-FSO class.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMAllocateBlockRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMDirectoriesPurgeRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMDirectoriesPurgeRequestWithFSO.java

## Purpose

`OMDirectoriesPurgeRequestWithFSO` is an internal/system request used by OM deletion services to purge deleted FSO directories and their subpaths from metadata tables. It also updates bucket usage, snapshot transaction metadata, open hsync keys, deletion metrics, and system audit logs.

## Important APIs, Types, And Functions

- `validateAndUpdateCache(OzoneManager, ExecutionContext)` processes `PurgeDirectoriesRequest` batches.
- Snapshot validation uses `SnapshotUtils.getSnapshotInfo(...)` and `validatePreviousSnapshotId(...)` when expected previous snapshot ID is present.
- `ProcessedKeyInfo` holds reconstructed `OmKeyInfo`, delete-table key, volume, bucket, and pair key.
- `processDeleteKey(...)` converts protobuf key info into table keys and bucket identifiers.
- `getBucketLockKeySet(...)` computes distinct bucket write-lock keys either from explicit `BucketNameInfo` entries or from purged subfile/subdir key infos.

## Control Flow And State

The request optionally resolves a source snapshot and validates snapshot-chain expectations before acquiring all affected bucket write locks. It iterates each `PurgePathRequest`: marked-deleted subdirectories are tombstoned in the directory table and decrement key metrics/namespace; deleted subfiles are tombstoned in the file table, decrement bytes/namespace, and if they carry `HSYNC_CLIENT_ID`, their open-file entry is marked with `DELETED_HSYNC_KEY`; deleted root directory entries update snapshot namespace accounting. It updates deletion-service metrics, stores snapshot last transaction info or AOS last purge transaction info, copies bucket info for response persistence, releases locks, and returns `OMDirectoriesPurgeResponseWithFSO`.

## Dependencies And Integration Points

This class integrates with `OmMetadataManagerImpl`, directory/file/open-key/snapshot tables, snapshot chain manager, bucket locks over multiple buckets, `DeletingServiceMetrics`, `OMMetrics`, system audit logger, `TransactionInfo`, and `OMDirectoriesPurgeResponseWithFSO`. It is tightly coupled to FSO path-key formats and snapshot-aware deleted-directory cleanup.

## Risks And Test Signals

High-risk areas include multi-bucket lock acquisition, snapshot-chain invalidation, bucket recreation/object ID checks, hsync open-key deletion marking, byte/namespace decrement accuracy, duplicate deleted directory/subdir accounting, cache tombstones, and response persistence ordering. Tests should cover AOS and snapshot purge paths, expected previous snapshot mismatch, explicit and inferred bucket lock sets, deleted hsync files, bucket missing or recreated with different object ID, metrics increments, system audit only in debug mode, and open-key metadata returned in the response.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMDirectoriesPurgeRequestWithFSO.java -->
