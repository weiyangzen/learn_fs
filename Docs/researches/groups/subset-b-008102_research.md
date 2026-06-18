# subset-b-008102 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/ValidatorRegistry.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/ValidatorRegistry.java

Purpose: `ValidatorRegistry` discovers OM request validator methods annotated with `RequestFeatureValidator` and indexes them by `ValidationCondition`, OM request `Type`, and `RequestProcessingPhase`. It is the reflection-backed lookup layer used by request validation code to decide which validators must run before or after request handling.

Important APIs and types: Constructors accept either a validator package or explicit `URL` collection. `validationsFor(List<ValidationCondition>, Type, RequestProcessingPhase)` returns unique `Method` instances. `initMaps(Collection<Method>)` reads annotation metadata and populates nested `EnumMap`s. It depends on `Reflections`, `Scanners.MethodsAnnotated`, `RequestFeatureValidator`, `ValidationCondition`, and `RequestProcessingPhase`.

Control flow: Construction scans the classpath, retrieves annotated methods, marks each method accessible, then stores each method under every declared condition. Lookup short-circuits on empty conditions or empty registry, then unions per-condition lists into a `HashSet` to avoid duplicate validator execution when several active conditions select the same method.

State and persistence behavior: State is purely in-memory: an `EnumMap<ValidationCondition, EnumMap<Type, EnumMap<RequestProcessingPhase, List<Method>>>>`. There is no DB persistence. Ordering is not guaranteed after unioning through `HashSet`, so validators should not rely on inter-validator order.

Dependencies and integration points: The class integrates OM-specific validation annotations with the generic Ozone request validation phase enum and protobuf request type enum. It depends on package/classpath scanning being configured to include all validator packages.

Risks and test signals: Risks include missing validators if classpath URLs are incomplete, nondeterministic ordering, and runtime failures from reflective invocation of incompatible method signatures elsewhere. Useful tests should cover duplicate condition unioning, pre/post separation, empty lookups, and package-scan discovery.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/ValidatorRegistry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/VersionExtractor.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/VersionExtractor.java

Purpose: `VersionExtractor` is an enum strategy for extracting a `Versioned` value from an `OMRequest` and validation context. It lets the validation framework use the same flow for metadata layout version validators and client protocol version validators.

Important APIs and types: `LAYOUT_VERSION_EXTRACTOR` returns the current `LayoutVersionManager` feature for the metadata layout version. `CLIENT_VERSION_EXTRACTOR` maps the request protobuf version to `ClientVersion`, using `FUTURE_VERSION` when the request advertises a newer version than the server. Each strategy exposes the validator annotation class through `getValidatorClass()`.

Control flow: The caller chooses an enum constant based on validator category, calls `extractVersion(req, ctx)`, then can compare that value against validator constraints. The client path is defensive against newer clients; the layout path reads from `ValidationContext.versionManager()`.

State and persistence behavior: The enum keeps no mutable state and persists nothing. It reflects runtime layout-manager state and request protobuf fields.

Dependencies and integration points: It bridges `OMLayoutVersionValidator`, `OMClientVersionValidator`, `ClientVersion`, `Versioned`, `OMRequest`, and `LayoutVersionManager`.

Risks and test signals: Tests should verify current layout feature extraction, exact protobuf-to-client-version mapping, and future-client fallback. A risk is that missing or stale version-manager state would make layout validation reject or allow requests incorrectly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/VersionExtractor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/package-info.java

Purpose: This package documentation defines the design intent for OM request feature validation: add condition-specific request behavior without cluttering core request handlers.

Important APIs and types: It documents `ValidationCondition`, `RequestFeatureValidator`, OM protobuf `Type`, and the expectation that validators are simple stateless methods tied to one request type.

Control flow: The package-level flow is reflection discovery of annotated methods, selection by condition, request type, and phase, and execution to reject or rewrite requests around upgrades or client-version compatibility.

State and persistence behavior: The documented validators should be stateless and do not persist data directly. Persistent effects happen later in normal request processing after validation succeeds.

Dependencies and integration points: The package integrates request classes, upgrade/layout state, client version checks, and the shared request validation framework.

Risks and test signals: The documentation warns against complex multi-request validators. Tests should confirm validators stay simple, have proper annotations, and are discovered for the intended condition and phase.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMQuotaRepairRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMQuotaRepairRequest.java

Purpose: `OMQuotaRepairRequest` handles an administrative repair operation that updates bucket used bytes/namespace counts and can migrate old quota sentinel values on buckets and volumes.

Important APIs and types: It extends `OMClientRequest`, reads `QuotaRepairRequest`, uses `BucketQuotaCount`, updates `OmBucketInfo` and `OmVolumeArgs`, returns `OMQuotaRepairResponse`, and uses `BUCKET_LOCK` and `VOLUME_LOCK`.

Control flow: `preExecute` creates the request user and rejects non-admin callers when admin authorization is enabled. `validateAndUpdateCache` iterates bucket count entries, calls `updateBucketInfo`, optionally calls `updateOldVolumeQuotaSupport`, builds a success response, and records updated bucket/volume maps for response batch persistence.

State and persistence behavior: Bucket repair increments used bytes and namespace, optionally rewrites `OLD_QUOTA_DEFAULT` to `QUOTA_RESET`, and writes bucket table cache entries at the transaction index. Volume migration scans the volume table and writes cache entries for volumes with old quota sentinels. The response persists the collected maps to DB.

Dependencies and integration points: It integrates quota repair RPC payloads, admin authorization, OM metadata tables, table iterators, cache values, and quota constants.

Risks and test signals: Risks include concurrent deletion during repair, partial progress across many buckets, and scanning the full volume table. Tests should cover admin denial, deleted bucket tolerance, old quota conversion, lock release, and response DB batch contents.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMQuotaRepairRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMVolumeCreateRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMVolumeCreateRequest.java

Purpose: `OMVolumeCreateRequest` validates and stages creation of an Ozone volume, including owner list updates, default ACLs, metrics, audit logging, and object/update IDs.

Important APIs and types: It extends `OMVolumeRequest`, consumes `CreateVolumeRequest` and `VolumeInfo`, builds `OmVolumeArgs`, updates `PersistedUserVolumeInfo`, and returns `OMVolumeCreateResponse`. It uses `USER_LOCK`, `VOLUME_LOCK`, `OmResponseUtil`, `OzoneAclUtil.getDefaultAclList`, and `OMMetrics`.

Control flow: `preExecute` validates the volume name, checks CREATE ACLs when enabled, and sets creation/modification time. `validateAndUpdateCache` builds volume args, acquires volume then user write locks, rejects existing volumes, updates or creates the owner volume list, merges default ACLs depending on `ignoreClientACLs`, stages volume and user table cache entries, and constructs the response.

State and persistence behavior: The request writes user-table and volume-table cache entries with the transaction index. The response later persists both. On success it increments volume counters; on failure it records a create failure metric and does not stage successful mutations.

Dependencies and integration points: It integrates OM ACL checks, volume naming rules, user volume limit enforcement, audit logging, lock tracking, metadata-manager key derivation, and volume response DB batching.

Risks and test signals: Risks include lock-order regressions, duplicate volume races, incorrect ACL merge behavior, and owner-list count limits. Tests should assert cache entries, default ACL behavior, audit on preExecute failure, metric increments, and proper lock release.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMVolumeCreateRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMVolumeDeleteRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMVolumeDeleteRequest.java

Purpose: `OMVolumeDeleteRequest` validates and stages deletion of an empty, unreferenced volume and removal of that volume from its owner list.

Important APIs and types: It handles `DeleteVolumeRequest`, uses `OMVolumeRequest.getVolumeInfo` and `delVolumeFromOwnerList`, returns `OMVolumeDeleteResponse`, and updates `PersistedUserVolumeInfo`.

Control flow: `preExecute` checks DELETE ACLs for the volume. `validateAndUpdateCache` increments delete metrics, acquires the volume lock, loads volume metadata, rejects nonzero reference count, acquires the owner user lock, checks `isVolumeEmpty`, removes the volume from owner state, stages user-table update and volume-table tombstone, and builds a delete response.

State and persistence behavior: Successful deletion writes a new owner volume list and a null cache value for the volume key. The response persists deletion from volume table and owner table update. Metrics decrement volume count only on success.

Dependencies and integration points: It integrates reference-count protection for tenant/features, volume emptiness checks, ACL/audit, user and volume locks, and metadata cache-to-response persistence.

Risks and test signals: A notable risk is owner-key consistency: the code obtains `dbUserKey` but reads `getUserTable().get(owner)`, so tests should ensure table API expectations match real keys. Other tests should cover referenced volume denial, nonempty volume denial, owner list mutation, tombstone persistence, and audit on ACL failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMVolumeDeleteRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMVolumeRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMVolumeRequest.java

Purpose: `OMVolumeRequest` is the base class for volume requests and centralizes owner-volume-list and volume-table helper logic.

Important APIs and types: It extends `OMClientRequest`. Key helpers are `addVolumeToOwnerList`, `delVolumeFromOwnerList`, `createVolume`, and `getVolumeInfo`. It uses `PersistedUserVolumeInfo`, `OmVolumeArgs`, `CacheKey`, `CacheValue`, and `OMException`.

Control flow: Add/delete owner-list helpers copy existing protobuf lists, enforce max volume count on add, preserve or initialize object IDs, and set update IDs. `createVolume` stages user and volume cache entries. `getVolumeInfo` resolves the volume DB key and throws `VOLUME_NOT_FOUND` if absent.

State and persistence behavior: Helpers only stage cache updates; persistence is completed by response classes during DB batch application. Owner list entries use transaction index as update ID and new-object ID when creating a first list.

Dependencies and integration points: All concrete volume create/delete/owner/quota/ACL requests reuse this class for consistent metadata-manager keying and exceptions.

Risks and test signals: Risks include unordered owner volume names because add uses `HashSet`, max count boundary behavior, and correct object/update ID preservation. Tests should cover null owner lists, deletion from missing owner, duplicate add idempotence, and cache key correctness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMVolumeRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMVolumeSetOwnerRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMVolumeSetOwnerRequest.java

Purpose: `OMVolumeSetOwnerRequest` stages changing a volume owner and moving the volume between per-user volume lists.

Important APIs and types: It handles `SetVolumePropertyRequest` with `ownerName`, returns `OMVolumeSetOwnerResponse`, uses `acquireMultiUserLock`, `OmVolumeArgs`, and `PersistedUserVolumeInfo`.

Control flow: `preExecute` stamps modification time and checks WRITE_ACL on the volume. `validateAndUpdateCache` rejects malformed requests without owner name, acquires the volume lock, loads the current owner, returns an OK-status/non-success no-op when the owner is unchanged, acquires both user locks, removes the volume from the old owner, adds it to the new owner, updates volume owner/modification/update ID, and stages all three cache writes.

State and persistence behavior: Successful changes stage old user, new user, and volume table entries. No-op same-owner responses intentionally avoid DB batch mutation. Audit logging happens after lock release.

Dependencies and integration points: It integrates owner-list helpers from `OMVolumeRequest`, OM lock multi-user ordering, volume update metrics, audit maps, and response-side persistence.

Risks and test signals: Risks include missing audit/logging on early same-owner return and correct lock release on partial failures. Tests should cover same-owner no-op, user volume limit on new owner, old/new owner list updates, modification time propagation, and response `success` semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMVolumeSetOwnerRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMVolumeSetQuotaRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMVolumeSetQuotaRequest.java

Purpose: `OMVolumeSetQuotaRequest` validates and stages updates to volume space and namespace quotas.

Important APIs and types: It handles `SetVolumePropertyRequest` quota fields, returns `OMVolumeSetQuotaResponse`, uses `OmVolumeArgs`, `OmBucketInfo`, `OzoneConsts.QUOTA_RESET`, and `OMException.ResultCodes.QUOTA_ERROR`/`QUOTA_EXCEEDED`.

Control flow: `preExecute` stamps modification time and checks WRITE ACL. `validateAndUpdateCache` rejects requests with neither quota field, acquires the volume lock, loads current volume info, validates byte quota against all non-link buckets and namespace quota against bucket count, applies valid fields, sets modification/update ID, and stages the volume-table cache entry.

State and persistence behavior: Only the volume table is updated. Invalid values below reset or equal zero are ignored by validation helpers; hard violations throw and produce error responses. The response persists the updated `OmVolumeArgs`.

Dependencies and integration points: It depends on `OMMetadataManager.listBuckets`, bucket quota semantics, volume ACL/audit, and request metrics.

Risks and test signals: Risks include expensive full bucket listing, behavior when one quota field is invalid but the other is valid, and link-bucket quota exclusion. Tests should cover quota reset, buckets without quota, total bucket quota exceeding volume quota, namespace lower than bucket count, and audit/metric failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMVolumeSetQuotaRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/acl/OMVolumeAclRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/acl/OMVolumeAclRequest.java

Purpose: `OMVolumeAclRequest` is the shared implementation for volume ACL add, remove, and set requests.

Important APIs and types: It extends `OMVolumeRequest`, accepts an `AclOp`, defines abstract callbacks for request-specific ACL extraction and response construction, and uses `OmVolumeArgs.Builder.acls()`.

Control flow: `preExecute` checks WRITE_ACL against the target volume and emits action-specific audit records on failure. `validateAndUpdateCache` increments volume update metrics, acquires the volume lock, loads volume metadata, applies the injected ACL operation, stamps modification time from the concrete protobuf request when a change occurs, stages a volume table cache entry, then calls subclass success/failure/completion callbacks.

State and persistence behavior: Successful changed ACLs update only the volume table with a new update ID. Add-existing or remove-missing cases can return success responses with `aclApplied=false` and no cache write.

Dependencies and integration points: It integrates `AclOp`, OM ACL authorization, volume metadata helpers, audit maps from `OzoneObj`, and `OMVolumeAclOpResponse`.

Risks and test signals: Risks include `getAddAclRequest()`/`getSetAclRequest()`/`getRemoveAclRequest()` access patterns depending on protobuf defaults and correct no-op handling. Tests should cover changed and unchanged ACLs, missing volume, audit maps, modification time, and metric failure increments.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/acl/OMVolumeAclRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/acl/OMVolumeAddAclRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/acl/OMVolumeAddAclRequest.java

Purpose: `OMVolumeAddAclRequest` specializes `OMVolumeAclRequest` to add one ACL to a volume.

Important APIs and types: The constructor reads `AddAclRequest`, converts the protobuf ACL with `OzoneAcl.fromProtobuf`, converts the object with `OzoneObjInfo.fromProtobuf`, and derives the volume name from `obj.getPath().substring(1)`.

Control flow: `preExecute` delegates authorization to the base class and stamps `modificationTime`. The injected `AclOp` calls `builder.add(acls.get(0))`. Success sets `AddAclResponse.response` to whether the ACL was applied; failure returns an error `OMVolumeAclOpResponse`. `validateAndUpdateCache` increments add-ACL metrics before delegating.

State and persistence behavior: When the ACL is newly added, the volume table cache gets updated through the base class and response persistence writes `OmVolumeArgs`.

Dependencies and integration points: It integrates volume ACL protobufs, `OzoneObjInfo` path handling, `OMAction.ADD_ACL` audit, and OzoneManager metrics.

Risks and test signals: Risks include path parsing assumptions and add idempotence. Tests should assert duplicate ACL no-op response, modification time propagation, audit action, and table update only when applied.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/acl/OMVolumeAddAclRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/acl/OMVolumeRemoveAclRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/acl/OMVolumeRemoveAclRequest.java

Purpose: `OMVolumeRemoveAclRequest` specializes the volume ACL base class to remove one ACL from a volume.

Important APIs and types: It reads `RemoveAclRequest`, stores a singleton `OzoneAcl`, stores an `OzoneObj`, and uses an `AclOp` that calls `builder.remove(acls.get(0))`.

Control flow: `preExecute` performs base ACL authorization and stamps modification time. On success it writes `RemoveAclResponse.response` with the applied/no-op result. Completion logs success or failure and audits with `OMAction.REMOVE_ACL`. It increments remove-ACL metrics before base validation.

State and persistence behavior: If the ACL was present, the base class stages an updated `OmVolumeArgs` in the volume table cache. Removing a non-existing ACL is a no-op response and avoids DB mutation.

Dependencies and integration points: It uses the common volume ACL flow, OM audit logger, metrics, and `OMVolumeAclOpResponse`.

Risks and test signals: Tests should cover removal of present and absent ACLs, modification time only on applied changes, path-derived volume names, and lock release on missing volume.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/acl/OMVolumeRemoveAclRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/acl/OMVolumeSetAclRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/acl/OMVolumeSetAclRequest.java

Purpose: `OMVolumeSetAclRequest` replaces the full ACL list on a volume.

Important APIs and types: It reads `SetAclRequest`, converts the protobuf ACL list to `List<OzoneAcl>`, converts the target object, and injects an `AclOp` that calls `builder.set(acls)`.

Control flow: `preExecute` delegates write-ACL authorization and stamps modification time. The shared base class applies the replacement under the volume lock and calls subclass callbacks. Success creates `SetAclResponse.response`; completion audits with `OMAction.SET_ACL`.

State and persistence behavior: A set operation normally updates the volume table with the new ACL list and transaction update ID. Response persistence writes the changed `OmVolumeArgs`.

Dependencies and integration points: It integrates protobuf ACL lists, `OzoneObjInfo`, shared `OMVolumeAclRequest`, audit logging, and set-ACL metrics.

Risks and test signals: Tests should verify replacing with empty/non-empty ACL lists, idempotent replacement behavior from the ACL builder, audit ACL rendering, and modification time propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/acl/OMVolumeSetAclRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/acl/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/acl/package-info.java

Purpose: This package documentation identifies the package as the volume ACL request/response area.

Important APIs and types: The package contains the abstract volume ACL request and add/remove/set concrete request implementations.

Control flow: Package flow follows OM request handling: preExecute authorization and normalization, lock-scoped cache mutation, response DB batching, and audit completion.

State and persistence behavior: State changes target `OmVolumeArgs` ACL lists in the volume table.

Dependencies and integration points: It integrates with volume request helpers, ACL authorizer, audit logger, and volume ACL response classes.

Risks and test signals: Package-level tests should cover all three operations and verify no-op versus applied behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/acl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/package-info.java

Purpose: This package documentation marks the package as containing volume request classes.

Important APIs and types: The package includes volume create, delete, owner, quota, quota repair, and shared volume request helper classes.

Control flow: Classes generally use `preExecute` for ACL/time/user normalization and `validateAndUpdateCache` for lock-protected cache mutation.

State and persistence behavior: State changes are staged in OM metadata caches and persisted by paired response classes.

Dependencies and integration points: The package integrates with OM locks, audit, metrics, metadata tables, and protobuf volume RPCs.

Risks and test signals: Broad tests should assert lock ordering, metrics/audit behavior, and source-table-aligned response persistence for every mutation type.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/CleanupTableInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/CleanupTableInfo.java

Purpose: `CleanupTableInfo` is a runtime annotation used on `OMClientResponse` classes to declare which OM metadata tables are affected and therefore eligible for cache cleanup after response processing.

Important APIs and types: It is `@Retention(RUNTIME)`, `@Target(TYPE)`, `@Inherited`, and exposes `cleanupTables()` plus `cleanupAll()`.

Control flow: Response classes annotate themselves with table constants from `OMDBDefinition`. Cleanup infrastructure can inspect annotations and clear affected caches without hard-coding every response class.

State and persistence behavior: The annotation itself stores metadata only. It does not mutate DB state, but incorrect metadata can leave stale table-cache entries.

Dependencies and integration points: It integrates response classes, OM table definitions, and cache-cleanup mechanisms.

Risks and test signals: Tests should verify every mutating response declares all affected tables, `cleanupAll` is mutually understood with an empty table list, and inherited annotations behave as intended for subclasses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/CleanupTableInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/DummyOMClientResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/DummyOMClientResponse.java

Purpose: `DummyOMClientResponse` is a no-op response implementation for paths that need an `OMClientResponse` wrapper but should not write anything to OM metadata.

Important APIs and types: It extends `OMClientResponse`, is annotated with default `@CleanupTableInfo`, and implements `addToDBBatch` as an empty method.

Control flow: `checkAndUpdateDB` inherited from the base class can call the no-op batch method on OK responses, making this safe where no persistence is expected.

State and persistence behavior: It stores only the `OMResponse`; no DB or cache state is changed.

Dependencies and integration points: It participates in normal response handling without special casing.

Risks and test signals: Tests should assert no batch writes occur and that using it for mutating operations would be a bug because cleanup metadata is empty.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/DummyOMClientResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/OMClientResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/OMClientResponse.java

Purpose: `OMClientResponse` is the abstract base for OM response-side persistence. It wraps the protobuf `OMResponse`, carries lock details, and defines the DB batch update contract.

Important APIs and types: `checkAndUpdateDB` calls `addToDBBatch` only when status is `OK`. `checkStatusNotOK` guards error constructors. `getBucketLayout` defaults to `BucketLayout.DEFAULT`. `setOmLockDetails` records lock acquisition/release metadata.

Control flow: Request classes produce concrete responses after cache mutation. Later OM transaction application calls `checkAndUpdateDB`, which gates persistence on success unless subclasses override for partial-success statuses.

State and persistence behavior: The base stores immutable `OMResponse` and mutable `OMLockDetails`. Actual persistence is delegated to subclasses using `BatchOperation`.

Dependencies and integration points: It links request handling, Ratis transaction replay/apply, OM metadata manager tables, bucket layout selection, and lock observability.

Risks and test signals: Subclasses with partial success must override `checkAndUpdateDB`. Tests should verify error constructors call `checkStatusNotOK`, OK responses write exactly once, and bucket-layout overrides route to correct tables.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/OMClientResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/OMBucketCreateResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/OMBucketCreateResponse.java

Purpose: `OMBucketCreateResponse` persists successful bucket creation and optional volume namespace usage updates.

Important APIs and types: It stores `OmBucketInfo` and optional `OmVolumeArgs`, annotates cleanup for `BUCKET_TABLE` and `VOLUME_TABLE`, and exposes `getOmBucketInfo`.

Control flow: On DB batch application it derives the bucket key and writes bucket info. If volume args are present, it also writes the volume table entry.

State and persistence behavior: It inserts a bucket-table row and may update volume-table quota/namespace state. Error constructor enforces non-OK status and stores null payloads.

Dependencies and integration points: It is paired with bucket create request logic and metadata-manager key derivation.

Risks and test signals: Tests should cover create with and without volume update, error no-op, cleanup table annotation, and correct volume/bucket keys.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/OMBucketCreateResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/OMBucketDeleteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/OMBucketDeleteResponse.java

Purpose: `OMBucketDeleteResponse` persists bucket deletion and optional volume namespace usage updates.

Important APIs and types: It stores volume and bucket names plus optional `OmVolumeArgs`, and cleans `BUCKET_TABLE` and `VOLUME_TABLE`.

Control flow: `addToDBBatch` deletes the bucket-table row by metadata-manager bucket key and writes updated volume args when provided.

State and persistence behavior: Successful response removes the bucket row and may persist volume quota counters. Error constructor stores no names and enforces non-OK.

Dependencies and integration points: It integrates bucket delete request validation, metadata-manager keying, and cache cleanup.

Risks and test signals: Tests should assert bucket deletion, volume update optionality, getters for names, and no writes on failed responses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/OMBucketDeleteResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/OMBucketSetOwnerResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/OMBucketSetOwnerResponse.java

Purpose: `OMBucketSetOwnerResponse` persists bucket owner changes.

Important APIs and types: It stores `OmBucketInfo`, annotates `BUCKET_TABLE`, and overrides `checkAndUpdateDB` to require both status `OK` and response `success=true`.

Control flow: Same-owner requests can produce status OK but success false; the override avoids persisting in that no-op case. Otherwise it writes the bucket table entry.

State and persistence behavior: Successful owner changes update only the bucket table. Error/no-op cases do not write.

Dependencies and integration points: It matches request semantics from bucket owner update logic and OM response status/success conventions.

Risks and test signals: Tests should cover OK/success true writes, OK/success false no-op, failed response no-op, and bucket key correctness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/OMBucketSetOwnerResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/OMBucketSetPropertyResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/OMBucketSetPropertyResponse.java

Purpose: `OMBucketSetPropertyResponse` persists bucket property changes such as quotas, versioning, layout-related fields, or metadata updated by the request.

Important APIs and types: It stores one `OmBucketInfo`, annotates cleanup for `BUCKET_TABLE`, and writes through `putWithBatch`.

Control flow: Successful constructor captures the updated bucket info. `addToDBBatch` derives the bucket key from volume/bucket names and writes the table row.

State and persistence behavior: Only bucket-table state changes. Error responses enforce non-OK status and do not carry bucket info.

Dependencies and integration points: It is paired with bucket property request validation and replay.

Risks and test signals: Tests should assert updated fields are persisted, failed responses are no-op, and cleanup metadata includes the bucket table.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/OMBucketSetPropertyResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/acl/OMBucketAclResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/acl/OMBucketAclResponse.java

Purpose: `OMBucketAclResponse` persists bucket ACL changes.

Important APIs and types: It stores updated `OmBucketInfo`, annotates `BUCKET_TABLE`, and checks `getOMResponse().getSuccess()` inside `addToDBBatch`.

Control flow: Base `checkAndUpdateDB` gates on OK status; this class adds a success flag check so no-op ACL responses do not write.

State and persistence behavior: Applied ACL changes update the bucket table. Failed or non-applied changes do not write.

Dependencies and integration points: It integrates bucket ACL request classes with metadata persistence.

Risks and test signals: Tests should cover add existing/remove missing no-op, applied ACL update, and failed response constructor behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/acl/OMBucketAclResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/acl/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/acl/package-info.java

Purpose: This package documentation identifies the package as containing bucket ACL response classes.

Important APIs and types: The package currently centers on `OMBucketAclResponse`, which persists ACL mutations to `OmBucketInfo`.

Control flow: Bucket ACL requests produce responses that rely on `OMClientResponse` success gating and then write updated bucket metadata.

State and persistence behavior: State changes target `BUCKET_TABLE` rows containing bucket ACL lists.

Dependencies and integration points: The package connects bucket ACL request handlers, response DB batching, cleanup annotations, and OM metadata manager bucket-key derivation.

Risks and test signals: Package-level tests should cover add/remove/set ACL success and no-op paths, ensuring unchanged ACL operations do not write table rows unnecessarily.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/acl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/package-info.java

Purpose: This package documentation marks the package as containing bucket response classes.

Important APIs and types: The package includes create, delete, owner, property, and ACL-related response implementations that persist `OmBucketInfo` and sometimes `OmVolumeArgs`.

Control flow: Request handlers validate and update cache, then response classes apply the same mutation to RocksDB batch operations during transaction replay/application.

State and persistence behavior: State changes primarily target `BUCKET_TABLE`, with create/delete also updating `VOLUME_TABLE` for namespace usage.

Dependencies and integration points: The package integrates bucket request handlers, `OMClientResponse`, cleanup annotations, and OM metadata table key helpers.

Risks and test signals: Tests should verify each response declares all touched tables, persists expected bucket/volume records, and handles OK-but-no-op responses where supported.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/OMDirectoryCreateResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/OMDirectoryCreateResponse.java

Purpose: `OMDirectoryCreateResponse` persists directory creation in non-FSO layouts using key-table directory marker entries.

Important APIs and types: It extends `OmKeyResponse`, stores `dirKeyInfo`, parent `OmKeyInfo` list, `Result`, `BucketLayout`, and `OmBucketInfo`, and cleans `KEY_TABLE`.

Control flow: On `Result.SUCCESS`, it writes parent directory marker keys, writes the target directory key, and updates the bucket table for namespace accounting. On `DIRECTORY_ALREADY_EXISTS`, it is an OK no-op.

State and persistence behavior: It writes key-table entries and bucket-table state, although cleanup annotation names only `KEY_TABLE`. Error/already-exists constructors avoid directory payloads.

Dependencies and integration points: It is paired with `OMDirectoryCreateRequest` and uses metadata-manager ozone dir/key naming helpers.

Risks and test signals: Tests should cover parent creation ordering, already-exists no-op, bucket namespace update, and cleanup metadata coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/OMDirectoryCreateResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/OMDirectoryCreateResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/OMDirectoryCreateResponseWithFSO.java

Purpose: `OMDirectoryCreateResponseWithFSO` persists directory creation for file-system-optimized buckets using directory table object-ID path keys.

Important APIs and types: It stores `OmDirectoryInfo`, parent directory infos, volume ID, bucket ID, result, bucket info, and cleans `DIRECTORY_TABLE`.

Control flow: `addToDBBatch` delegates to `addToDirectoryTable`. If `dirInfo` is present, it writes parent directories, writes the target directory, and updates bucket table. If absent, it logs an OK no-op for existing directories.

State and persistence behavior: It writes directory-table rows keyed by `(volumeId,bucketId,parentObjectId,name)` and updates bucket-table namespace state.

Dependencies and integration points: It integrates FSO directory request logic, metadata-manager path-key generation, and bucket quota accounting.

Risks and test signals: Tests should assert object-ID keying, parent directory creation, existing-directory no-op, bucket update, and cleanup table annotation completeness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/OMDirectoryCreateResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/OMFileCreateResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/OMFileCreateResponse.java

Purpose: `OMFileCreateResponse` is the file-create response for non-FSO layouts and reuses key-create persistence.

Important APIs and types: It extends `OMKeyCreateResponse`, passes file key info, parent key infos, open key session ID, and bucket info, and cleans `KEY_TABLE` plus `OPEN_KEY_TABLE`.

Control flow: Successful construction delegates all DB batch behavior to `OMKeyCreateResponse`: parent directory markers and open key insertion. Error constructor sets the bucket layout and enforces non-OK status.

State and persistence behavior: It writes parent key markers, bucket namespace state, and an open-key table entry.

Dependencies and integration points: It bridges file request code to key response persistence for non-FSO layouts.

Risks and test signals: Tests should cover inherited open-key naming, parent directory entries, error no-op, and bucket-layout routing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/OMFileCreateResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/OMFileCreateResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/OMFileCreateResponseWithFSO.java

Purpose: `OMFileCreateResponseWithFSO` persists file creation for FSO buckets, including parent directories and open-file table state.

Important APIs and types: It extends `OMFileCreateResponse`, stores parent `OmDirectoryInfo` list and volume ID, uses `OMFileRequest.addToOpenFileTable`, and returns `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

Control flow: It writes parent directories when present, updates bucket table for namespace changes, then adds the file to the open-file table using volume and bucket object IDs.

State and persistence behavior: It writes directory-table parent rows, bucket-table quota state, and open-file table entries. It does not write a committed file table row until commit.

Dependencies and integration points: It integrates file-create request data, FSO object-ID keying, and `OMFileRequest` helper methods.

Risks and test signals: Tests should verify parent directory persistence, open-file key format, bucket update, layout override, and no stale parent creation assumptions noted by the TODO.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/OMFileCreateResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/OMRecoverLeaseResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/OMRecoverLeaseResponse.java

Purpose: `OMRecoverLeaseResponse` persists recover-lease state by updating an open key/open file entry, especially for FSO lease recovery flows.

Important APIs and types: It extends `OmKeyResponse`, stores `openKeyName` and `openKeyInfo`, cleans `FILE_TABLE` and `OPEN_FILE_TABLE`, and overrides `getBucketLayout` to FSO.

Control flow: On success, `addToDBBatch` writes `openKeyInfo` to the open key table for the active bucket layout when `openKeyName` is non-null. Failure constructor enforces non-OK status.

State and persistence behavior: It updates open-key/open-file table state and does not modify committed file rows directly.

Dependencies and integration points: It integrates lease recovery request logic, bucket layout routing, and open file cleanup/commit behavior.

Risks and test signals: Tests should cover null open-key no-op, FSO layout routing, failed response no-op, and preservation of lease recovery metadata in `OmKeyInfo`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/OMRecoverLeaseResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/package-info.java

Purpose: This package documentation identifies the package as containing file response classes.

Important APIs and types: The package includes directory create, file create, FSO variants, and lease recovery responses, mostly extending key response infrastructure.

Control flow: File requests stage metadata changes, and these responses replay those changes into key/open-key tables for default layouts or directory/open-file/file tables for FSO layouts.

State and persistence behavior: State changes affect parent directory entries, open file/open key entries, committed directory markers, bucket namespace accounting, and lease metadata.

Dependencies and integration points: The package integrates `OMFileRequest` helpers, `OmKeyResponse`, bucket layout routing, and cleanup annotations.

Risks and test signals: Tests should cover FSO versus non-FSO table selection, parent directory creation, bucket quota updates, and no-op existing directory or failed response paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/AbstractOMKeyDeleteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/AbstractOMKeyDeleteResponse.java

Purpose: `AbstractOMKeyDeleteResponse` centralizes the DB-batch operation for deleting a key from one table and moving its block metadata to the deleted table.

Important APIs and types: It extends `OmKeyResponse` and provides two overloads of `addDeletionToBatch`, one for normal key names and one for FSO full delete-key names. It uses `OmKeyInfo.isKeyEmpty`, `OmUtils.prepareKeyForDelete`, `RepeatedOmKeyInfo`, and `Table<String, ?>`.

Control flow: The helper deletes the source table entry, skips empty keys, marks `OmKeyInfo` with committed-key-deleted flag, wraps it in `RepeatedOmKeyInfo`, builds the deleted-table key, and writes the deleted table.

State and persistence behavior: It performs batch mutations only; it does not commit. It deletes from key/open/file source tables and adds non-empty keys to the common deleted table for async block cleanup.

Dependencies and integration points: All single-key, multi-key, open-key, and FSO delete responses use this helper.

Risks and test signals: Tests should cover empty-key skip behavior, committed versus open-key deletion flag, FSO full-key deleted-table naming, duplicate object IDs, and source table deletion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/AbstractOMKeyDeleteResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMAllocateBlockResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMAllocateBlockResponse.java

Purpose: `OMAllocateBlockResponse` persists newly allocated block metadata for an open key.

Important APIs and types: It extends `OmKeyResponse`, stores `OmKeyInfo` and client ID, cleans `OPEN_KEY_TABLE` and `BUCKET_TABLE`, and writes to `getOpenKeyTable(getBucketLayout())`.

Control flow: `addToDBBatch` derives the open-key name from volume, bucket, key, and client ID, then writes updated open key info.

State and persistence behavior: It updates open-key table state with additional block locations. It does not commit the key or update deleted table.

Dependencies and integration points: It is used after allocate-block request validation and SCM block allocation.

Risks and test signals: Tests should assert open-key naming, bucket layout routing, block list persistence, and failed response no-op.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMAllocateBlockResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMAllocateBlockResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMAllocateBlockResponseWithFSO.java

Purpose: `OMAllocateBlockResponseWithFSO` persists allocated block metadata for an open FSO file.

Important APIs and types: It extends `OMAllocateBlockResponse`, stores volume and bucket IDs, and calls `OMFileRequest.addToOpenFileTable`.

Control flow: The FSO override bypasses string open-key naming and writes the open-file entry with object IDs and client ID.

State and persistence behavior: It updates `OPEN_FILE_TABLE` with the latest `OmKeyInfo` for the in-progress file.

Dependencies and integration points: It integrates FSO key allocation request logic, object-ID keying, and bucket layout routing.

Risks and test signals: Tests should verify open-file key format, volume/bucket ID use, layout-specific cleanup annotation, and inherited failure behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMAllocateBlockResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMDirectoriesPurgeResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMDirectoriesPurgeResponseWithFSO.java

Purpose: `OMDirectoriesPurgeResponseWithFSO` persists recursive purge work for deleted FSO directories, moving subdirectories and files through deleted tables and optionally operating against a snapshot DB.

Important APIs and types: It stores `PurgePathRequest` list, bucket update map, optional `SnapshotInfo`, and open-key info map. It uses snapshot manager, `SNAPSHOT_DB_CONTENT_LOCK`, `DBStore` batch operations, `DeletedDirTable`, `DeletedTable`, directory/file tables, and `OmUtils.prepareKeyForDelete`.

Control flow: `addToDBBatch` opens a snapshot DB and write batch when purging from a snapshot, otherwise uses active metadata. `processPaths` moves marked subdirectories to deleted-dir table, deletes directory entries, moves deleted subfiles to deleted table, rewrites open-key metadata, deletes the visited deleted-dir marker, and updates active bucket quota state.

State and persistence behavior: It can mutate both active DB and snapshot DB in one response path. It updates deleted-dir, deleted, directory, file, open-key/open-file, snapshot-info, and bucket tables depending on inputs.

Dependencies and integration points: It integrates directory deletion service, snapshot lifecycle, FSO object-ID keying, bucket quota updates, and asynchronous key deletion.

Risks and test signals: Risks include two-DB atomicity limits, lock acquisition failure, open-key map being applied for each path, and cleanup annotation coverage. Tests should cover active and snapshot purges, subdir/file movement, deleted-dir marker removal, bucket updates, and snapshot info persistence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMDirectoriesPurgeResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyCommitResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyCommitResponse.java

Purpose: `OMKeyCommitResponse` persists committing an open key into the committed key table and handles hsync/update/delete side effects.

Important APIs and types: It stores committed `OmKeyInfo`, ozone key name, open key name, bucket info, `keyToDeleteMap`, hsync flags, optional new open-key info, and optional open key to update. It cleans open key, key, deleted, and bucket tables.

Control flow: On commit it deletes the open key unless hsync requires keeping/updating it, writes the committed key, writes any overwritten keys to deleted table, optionally updates another open key, and writes bucket used-bytes state.

State and persistence behavior: It moves data from open-key table to key table and updates deleted table for overwritten versions. Hsync can leave or update open-key state rather than deleting it.

Dependencies and integration points: It integrates key commit requests, hsync behavior, bucket quota accounting, and deleted-key cleanup.

Risks and test signals: Tests should cover normal commit, hsync commit, overwritten key deletion, open-key-to-update handling, bucket usage update, and visible `getKeysToDelete`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyCommitResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyCommitResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyCommitResponseWithFSO.java

Purpose: `OMKeyCommitResponseWithFSO` commits an open FSO file into the file table using object-ID path keying.

Important APIs and types: It extends `OMKeyCommitResponse`, stores volume ID, calls `OMFileRequest.addToFileTable`, and returns `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

Control flow: The override deletes or updates the open-file entry depending on hsync, writes the committed file table entry, updates deleted table and any open key to update, then writes bucket used-bytes state.

State and persistence behavior: It mutates open-file, file, deleted, and bucket tables rather than legacy open-key/key tables.

Dependencies and integration points: It integrates FSO commit request logic, file-table helpers, hsync semantics, and quota accounting.

Risks and test signals: Tests should assert object-ID file-table keying, hsync open-file behavior, deleted-table updates, bucket layout override, and failure constructor no-op.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyCommitResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyCreateResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyCreateResponse.java

Purpose: `OMKeyCreateResponse` persists open-key creation for default-layout key creates and parent directory marker creation.

Important APIs and types: It extends `OmKeyResponse`, stores `OmKeyInfo`, open key session ID, parent key infos, and bucket info, and cleans open-key, key, and bucket tables.

Control flow: `addToDBBatch` writes each parent directory marker into the key table, updates bucket namespace state when parents were created, derives the open key with session ID, and writes the open-key table entry.

State and persistence behavior: It stages in-progress key state in open-key table, not committed key table. Parent directory markers and bucket quota state may also be persisted.

Dependencies and integration points: It supports key/file create request flows and later commit/abort operations.

Risks and test signals: Tests should cover parent marker creation, no-parent fast path, open-key naming, bucket update, and failure response no-op.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyCreateResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyCreateResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyCreateResponseWithFSO.java

Purpose: `OMKeyCreateResponseWithFSO` is the FSO key-create response and delegates to the FSO file-create implementation.

Important APIs and types: It extends `OMFileCreateResponseWithFSO`, accepts `OmKeyInfo`, parent `OmDirectoryInfo` list, open key session ID, bucket info, and volume ID, and cleans directory, open-file, and bucket tables.

Control flow: All DB behavior is inherited: write parent directories, update bucket namespace state, and add the open file entry.

State and persistence behavior: It writes open-file table state and directory-table parent entries, not committed file table state.

Dependencies and integration points: It bridges key create request variants to file-system-optimized persistence helpers.

Risks and test signals: Tests should confirm inherited FSO behavior, constructor parameter propagation, cleanup annotation, and error response handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyCreateResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyDeleteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyDeleteResponse.java

Purpose: `OMKeyDeleteResponse` persists deleting one committed key in default layouts and records non-empty key data for asynchronous block deletion.

Important APIs and types: It extends `AbstractOMKeyDeleteResponse`, stores `OmKeyInfo`, bucket info, and optional deleted open-key info for hsync cleanup metadata.

Control flow: It derives the committed key name, calls `addDeletionToBatch` on the key table, writes updated bucket state, and, when an hsync open key exists, writes its metadata back to the open-key table for cleanup service processing.

State and persistence behavior: It deletes from key table, writes deleted table for non-empty keys, updates bucket table, and may update open-key table.

Dependencies and integration points: It integrates key delete requests, hsync cleanup, bucket quota accounting, and key deletion service.

Risks and test signals: Tests should cover empty and non-empty key deletion, deleted-table key format, hsync metadata path, bucket update, and failed response no-op.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyDeleteResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyDeleteResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyDeleteResponseWithFSO.java

Purpose: `OMKeyDeleteResponseWithFSO` persists deleting a single FSO file or directory.

Important APIs and types: It extends `OMKeyDeleteResponse`, stores full key name, directory/file flag, volume ID, and uses directory, file, deleted-dir, deleted, open-file, and bucket tables.

Control flow: It builds the object-ID DB key. Directory deletes remove from directory table and add to deleted-dir table. File deletes set full key name on `OmKeyInfo`, delete from file table, and add to deleted table. It updates bucket state and optional hsync open-file metadata.

State and persistence behavior: Directory deletions are moved to deleted-dir table for recursive purge; file deletions move block metadata to deleted table. Bucket accounting and open-file cleanup metadata may change.

Dependencies and integration points: It integrates FSO delete request logic, directory purge service, open-key cleanup service, and bucket quota accounting.

Risks and test signals: Tests should cover file versus directory branches, full key-name mutation, deleted-dir key format, hsync cleanup, and layout override.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyDeleteResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyPurgeResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyPurgeResponse.java

Purpose: `OMKeyPurgeResponse` permanently removes deleted-table entries after block cleanup and handles snapshot-related movement/update metadata.

Important APIs and types: It stores purge key list, snapshot renamed key list, optional source `SnapshotInfo`, optional `SnapshotMoveKeyInfos`, and bucket infos to update. It uses snapshot manager, snapshot DB batches, deleted table, snapshot renamed table, and snapshot info table.

Control flow: With a source snapshot, it acquires a snapshot DB content read lock, opens the snapshot metadata DB batch, deletes purge keys and renamed entries there, writes replacement repeated key infos, commits the snapshot batch, and updates active snapshot info. Without a snapshot it performs the same key processing in active metadata. It then writes bucket updates.

State and persistence behavior: It deletes from deleted table, deletes snapshot rename markers, may rewrite deleted-table entries, updates snapshot info, and writes bucket quota state.

Dependencies and integration points: It integrates `OMKeyPurgeRequest`, key deleting service, snapshot move-deleted-keys logic, and bucket accounting.

Risks and test signals: Risks include cross-DB partial commits, snapshot lock failure, and null `keysToUpdateList`. Tests should cover active and snapshot purge, renamed marker deletion, bucket updates, and replacement repeated key info.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyPurgeResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyRenameResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyRenameResponse.java

Purpose: `OMKeyRenameResponse` persists renaming one key in non-FSO/default key tables and records snapshot rename metadata when needed.

Important APIs and types: It stores from/to key names and updated `OmKeyInfo`, cleans `KEY_TABLE` and `SNAPSHOT_RENAMED_TABLE`, and uses `OMClientRequestUtils.isSnapshotBucket`.

Control flow: `addToDBBatch` deletes the old key-table row, writes the new key-table row, then if the bucket is in snapshot scope and no rename marker exists, writes snapshot-renamed table entry keyed by object ID.

State and persistence behavior: It atomically moves the key-table entry and may persist snapshot rename provenance.

Dependencies and integration points: It integrates key rename requests, snapshot diff/cleanup tracking, and metadata-manager key helpers.

Risks and test signals: Tests should cover normal rename, snapshot bucket rename marker creation, existing marker preservation, and failed response no-op.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyRenameResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyRenameResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyRenameResponseWithFSO.java

Purpose: `OMKeyRenameResponseWithFSO` persists renaming an FSO file or directory and optional parent/bucket updates.

Important APIs and types: It extends `OMKeyRenameResponse`, tracks whether the target is a directory, optional from/to parent `OmKeyInfo`, bucket info, and uses `OMFileRequest.getDirectoryInfo`.

Control flow: It gets volume and bucket IDs, deletes the old directory or file row, writes the new directory or file row, writes snapshot-renamed metadata if needed, writes updated parent directory rows for source/target parents, and writes bucket table when provided.

State and persistence behavior: It mutates directory table or file table, snapshot renamed table, optional parent directory rows, and optional bucket quota state.

Dependencies and integration points: It integrates FSO rename request validation, object-ID keying, snapshot tracking, and quota updates.

Risks and test signals: Tests should cover file and directory rename branches, parent directory updates, snapshot marker behavior, bucket updates, and layout override.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyRenameResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeySetTimesResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeySetTimesResponse.java

Purpose: `OMKeySetTimesResponse` persists modification/access time changes for a key in non-FSO layouts.

Important APIs and types: It extends `OmKeyResponse`, stores `OmKeyInfo`, cleans `KEY_TABLE`, and supports an explicit `BucketLayout`.

Control flow: `addToDBBatch` derives the ozone key from volume, bucket, and key name, then writes the updated key info to the key table.

State and persistence behavior: Only key-table metadata changes; block data and bucket accounting are unchanged.

Dependencies and integration points: It is paired with set-times request validation and key-table layout routing.

Risks and test signals: Tests should verify timestamp fields persist, failed response no-op, and bucket layout selection for non-default layouts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeySetTimesResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeySetTimesResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeySetTimesResponseWithFSO.java

Purpose: `OMKeySetTimesResponseWithFSO` persists timestamp changes for FSO files or directories.

Important APIs and types: It extends `OMKeySetTimesResponse`, stores `isDirectory`, volume ID, bucket ID, and converts key info to `OmDirectoryInfo` for directory rows.

Control flow: It builds the FSO object-ID path key. Directory targets are written to directory table; file targets are written to the file/key table for the FSO bucket layout.

State and persistence behavior: It updates either `DIRECTORY_TABLE` or `FILE_TABLE` metadata and does not update quota counters.

Dependencies and integration points: It integrates FSO set-times request logic, `OMFileRequest.getDirectoryInfo`, and layout-specific table routing.

Risks and test signals: Tests should cover both directory and file branches, path-key generation, timestamp persistence, and error response no-op.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeySetTimesResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeysDeleteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeysDeleteResponse.java

Purpose: `OMKeysDeleteResponse` persists multi-key deletion in default layouts and supports partial-delete status.

Important APIs and types: It extends `AbstractOMKeyDeleteResponse`, stores a list of `OmKeyInfo`, bucket info, and open-key metadata map. It overrides `checkAndUpdateDB` to accept `OK` and `PARTIAL_DELETE`.

Control flow: For each key it derives the ozone key and calls `addDeletionToBatch` against the key table. It updates bucket state and writes any open-key info entries used by cleanup service.

State and persistence behavior: It deletes multiple key-table rows, writes deleted-table entries for non-empty keys, updates bucket table, and may write open-key table metadata.

Dependencies and integration points: It integrates bulk key delete request logic, partial success response status, bucket quota accounting, and hsync/open-key cleanup.

Risks and test signals: Tests should cover partial delete persistence, multiple deleted-table entries, bucket update, open-key info map, and failed statuses that must not write.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeysDeleteResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeysDeleteResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeysDeleteResponseWithFSO.java

Purpose: `OMKeysDeleteResponseWithFSO` persists bulk deletion of FSO files and directories.

Important APIs and types: It extends `OMKeysDeleteResponse`, stores directory delete list and volume ID, and uses directory, file, deleted-dir, deleted, open-file, and bucket tables.

Control flow: It removes each directory from directory table and writes deleted-dir table entries. It removes each file from file table and writes deleted-table entries using full delete keys. It updates bucket state and writes open-key info map entries.

State and persistence behavior: It mutates FSO directory/file namespace and queues file blocks/directories for asynchronous cleanup.

Dependencies and integration points: It integrates bulk delete requests, recursive directory purge service, FSO keying, and quota updates.

Risks and test signals: Tests should cover mixed file/directory deletes, object-ID deleted-dir keys, partial success inherited behavior, open-file metadata updates, and layout override.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeysDeleteResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeysRenameResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeysRenameResponse.java

Purpose: `OMKeysRenameResponse` persists batch key renames in default layouts and supports partial rename.

Important APIs and types: It extends `OMClientResponse`, stores `OmRenameKeys`, cleans `KEY_TABLE` and `SNAPSHOT_RENAMED_TABLE`, and accepts `OK` or `PARTIAL_RENAME` in `checkAndUpdateDB`.

Control flow: For each from-to mapping it deletes the old key-table row, writes the new key-table row, and records a snapshot-renamed entry when the bucket is snapshot-scoped and no marker exists.

State and persistence behavior: It performs multiple key-table moves and optional snapshot-renamed table writes in one batch.

Dependencies and integration points: It integrates bulk rename request logic, snapshot tracking, and metadata key helpers.

Risks and test signals: Tests should cover partial rename persistence, multiple mapping order, snapshot marker idempotence, failed response no-op, and object ID keying for rename markers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeysRenameResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMOpenKeysDeleteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMOpenKeysDeleteResponse.java

Purpose: `OMOpenKeysDeleteResponse` moves stale open keys/open files to the deleted table during open-key cleanup.

Important APIs and types: It extends `AbstractOMKeyDeleteResponse`, stores a map from open key name to `(bucketId, OmKeyInfo)`, and cleans open-key/open-file, deleted, and bucket tables.

Control flow: `addToDBBatch` gets the open-key table for the bucket layout and calls `addDeletionToBatch` for each open key with `isCommittedKey=false`.

State and persistence behavior: It deletes open-key/open-file rows and writes non-empty uncommitted key parts to deleted table for block cleanup.

Dependencies and integration points: It integrates open key cleanup service, bucket layout routing, and key deletion service.

Risks and test signals: Tests should cover stale open key deletion, empty open key skip, committed flag false, FSO/default layouts, and failed response no-op.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMOpenKeysDeleteResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OmKeyResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OmKeyResponse.java

Purpose: `OmKeyResponse` is the key-response base class that stores the bucket layout used by key/file table operations.

Important APIs and types: It extends `OMClientResponse`, has constructors with explicit `BucketLayout` or default layout, and overrides `getBucketLayout`.

Control flow: Concrete key responses call the appropriate constructor so inherited and helper methods can route to the correct metadata tables.

State and persistence behavior: It stores only a layout value and the inherited `OMResponse`; no direct DB writes occur.

Dependencies and integration points: It is the common base for key, file, directory, ACL, multipart, purge, and delete responses.

Risks and test signals: Tests should ensure each FSO response passes or overrides the correct layout and default constructors do not accidentally route FSO operations to legacy tables.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OmKeyResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/package-info.java

Purpose: This package documentation marks the package as containing key response classes.

Important APIs and types: The package covers create, allocate, commit, delete, purge, rename, set-times, open-key cleanup, and shared key response bases.

Control flow: Key responses translate validated request/cache mutations into DB batch operations, with subclasses overriding status gating for partial delete/rename or special multipart-like races.

State and persistence behavior: State changes span open-key/open-file, key/file, directory, deleted, deleted-dir, bucket, snapshot info, and snapshot renamed tables depending on operation and bucket layout.

Dependencies and integration points: The package integrates request handlers, bucket layout routing, snapshot support, deletion services, hsync/open-key cleanup, and cleanup table annotations.

Risks and test signals: Tests should emphasize table-selection correctness, partial-success persistence, snapshot side effects, deleted-table key formats, and bucket quota/accounting updates.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/acl/OMKeyAclResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/acl/OMKeyAclResponse.java

Purpose: `OMKeyAclResponse` persists ACL updates for keys in non-FSO layouts.

Important APIs and types: It extends `OmKeyResponse`, stores updated `OmKeyInfo`, cleans `KEY_TABLE`, and supports explicit bucket layout constructors.

Control flow: `addToDBBatch` derives the ozone key and writes updated key info to the key table.

State and persistence behavior: It updates key metadata ACL state only.

Dependencies and integration points: It is paired with key ACL request handlers and metadata-manager key routing.

Risks and test signals: Tests should cover add/remove/set ACL metadata persistence, failed response no-op behavior, and bucket layout selection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/acl/OMKeyAclResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/acl/OMKeyAclResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/acl/OMKeyAclResponseWithFSO.java

Purpose: `OMKeyAclResponseWithFSO` persists ACL updates for FSO files or directories.

Important APIs and types: It extends `OMKeyAclResponse`, stores `isDirectory`, volume ID, bucket ID, and converts key info to `OmDirectoryInfo` for directory updates.

Control flow: It builds the FSO path key. Directory ACL updates write directory table rows; file ACL updates write key/file table rows for the FSO layout.

State and persistence behavior: It updates ACL metadata in either directory table or file table.

Dependencies and integration points: It integrates FSO ACL request handling, `OMFileRequest.getDirectoryInfo`, and bucket layout table routing.

Risks and test signals: Tests should cover directory and file ACL branches, path key generation, layout override/inherited layout, and failed response no-op.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/acl/OMKeyAclResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/acl/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/acl/package-info.java

Purpose: This package documentation identifies the package as containing key ACL response classes.

Important APIs and types: The package includes `OMKeyAclResponse` and `OMKeyAclResponseWithFSO`, which persist ACL changes for keys, files, and directories.

Control flow: Key ACL request handlers produce updated `OmKeyInfo`; these responses route the write to default key table or FSO file/directory tables.

State and persistence behavior: State changes update ACL metadata in key/file/directory rows without changing block data or bucket accounting.

Dependencies and integration points: The package integrates key ACL request handling, `OmKeyResponse`, `OMFileRequest` directory conversion, and cleanup annotations.

Risks and test signals: Tests should cover FSO directory versus file branches, default-layout key ACL persistence, failed response no-op, and bucket layout propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/acl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/acl/prefix/OMPrefixAclResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/acl/prefix/OMPrefixAclResponse.java

Purpose: `OMPrefixAclResponse` persists ACL changes for prefix ACL entries.

Important APIs and types: It extends `OMClientResponse`, stores `OmPrefixInfo`, cleans `PREFIX_TABLE`, and checks whether the response has a remove-ACL response.

Control flow: On DB batch application, if the operation is remove ACL and the resulting ACL list is empty, it deletes the prefix row. Otherwise it writes the prefix info.

State and persistence behavior: It creates, updates, or deletes prefix-table ACL metadata.

Dependencies and integration points: It integrates prefix ACL request handlers, prefix table storage, and response success gating from `OMClientResponse`.

Risks and test signals: Tests should cover removing the last ACL deletes the row, removing one of many updates the row, add/set writes rows, and failed response no-op.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/acl/prefix/OMPrefixAclResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/acl/prefix/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/acl/prefix/package-info.java

Purpose: This package documentation marks the package as containing prefix ACL response classes.

Important APIs and types: The package centers on `OMPrefixAclResponse`, which persists `OmPrefixInfo` to `PREFIX_TABLE`.

Control flow: Prefix ACL request handlers compute the resulting prefix ACL state; the response writes or deletes the prefix table row during DB batch application.

State and persistence behavior: State changes are limited to prefix ACL metadata. Removing the last ACL deletes the prefix entry.

Dependencies and integration points: The package integrates prefix ACL requests, OM metadata prefix table, cleanup annotations, and standard response success gating.

Risks and test signals: Tests should cover add, set, remove-one, and remove-last behaviors, including failed response no-op.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/acl/prefix/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/AbstractS3MultipartAbortResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/AbstractS3MultipartAbortResponse.java

Purpose: `AbstractS3MultipartAbortResponse` centralizes abort persistence for multipart uploads, moving uploaded parts to the deleted table and removing MPU bookkeeping.

Important APIs and types: It extends `OmKeyResponse`, uses `OmMultipartAbortInfo`, `OmMultipartKeyInfo`, `PartKeyInfo`, `OmKeyInfo`, `RepeatedOmKeyInfo`, `OmUtils.prepareKeyForDelete`, and bucket layout-specific open-key tables.

Control flow: For each abort info, it deletes the multipart open key, deletes the multipart info row, iterates part key infos, converts each part to `OmKeyInfo`, wraps it for deletion, writes deleted-table entries, and finally updates bucket used bytes. A convenience overload builds a singleton `OmMultipartAbortInfo`.

State and persistence behavior: It mutates open-key/open-file table, multipart info table, deleted table, and bucket table in one batch.

Dependencies and integration points: It is reused by single abort and expired MPU cleanup responses across default and FSO layouts.

Risks and test signals: Tests should cover multiple parts, empty part maps, bucket layout routing, deleted-table key naming using multipart key/upload ID, and bucket quota update.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/AbstractS3MultipartAbortResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3ExpiredMultipartUploadsAbortResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3ExpiredMultipartUploadsAbortResponse.java

Purpose: `S3ExpiredMultipartUploadsAbortResponse` persists aborting multiple expired multipart uploads grouped by bucket.

Important APIs and types: It extends `AbstractS3MultipartAbortResponse`, stores `Map<OmBucketInfo, List<OmMultipartAbortInfo>>`, and cleans open-key, open-file, deleted, multipart info, and bucket tables.

Control flow: `addToDBBatch` iterates each bucket entry and delegates to the shared abort helper for the list of MPUs.

State and persistence behavior: It removes multiple MPU open rows and multipart info rows, queues all parts in deleted table, and updates each bucket's used bytes.

Dependencies and integration points: It integrates expired MPU cleanup service, bucket layout data carried in `OmMultipartAbortInfo`, and shared abort response behavior.

Risks and test signals: Tests should cover multiple buckets, mixed bucket layouts, bucket update per group, failed response no-op, and deleted-table entries for every part.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3ExpiredMultipartUploadsAbortResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3InitiateMultipartUploadResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3InitiateMultipartUploadResponse.java

Purpose: `S3InitiateMultipartUploadResponse` persists initial MPU state for default/non-FSO layouts.

Important APIs and types: It extends `OmKeyResponse`, stores `OmMultipartKeyInfo` and `OmKeyInfo`, cleans `OPEN_KEY_TABLE` and `MULTIPART_INFO_TABLE`, and exposes testing getters.

Control flow: It derives the multipart key from volume, bucket, key, and upload ID, writes open-key table state, and writes multipart info table state with the same key.

State and persistence behavior: It creates the in-progress MPU open key and multipart metadata but does not write committed key data.

Dependencies and integration points: It integrates S3 initiate MPU request handling, open key table, multipart info table, and later commit/abort/complete operations.

Risks and test signals: Tests should verify multipart key format, both table writes, bucket layout routing, failed response no-op, and getter payloads.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3InitiateMultipartUploadResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3InitiateMultipartUploadResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3InitiateMultipartUploadResponseWithFSO.java

Purpose: `S3InitiateMultipartUploadResponseWithFSO` persists MPU initiation for FSO buckets, including parent directory creation.

Important APIs and types: It extends `S3InitiateMultipartUploadResponse`, stores parent directory infos, MPU DB key, volume ID, bucket ID, and bucket info, and uses `OMFileRequest.addToOpenFileTableForMultipart`.

Control flow: It writes parent directories and bucket namespace state when parent dirs are present, writes the multipart open-file entry, then writes multipart info table using the precomputed MPU DB key.

State and persistence behavior: It mutates directory, bucket, open-file, and multipart info tables.

Dependencies and integration points: It integrates S3 MPU request handling with FSO object-ID keying and directory creation semantics.

Risks and test signals: Tests should cover parent creation, no-parent path, open-file multipart key format, multipart info key, bucket update, and failed response no-op.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3InitiateMultipartUploadResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadAbortResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadAbortResponse.java

Purpose: `S3MultipartUploadAbortResponse` persists aborting one MPU in default or layout-specific open-key storage.

Important APIs and types: It extends `AbstractS3MultipartAbortResponse`, stores multipart key, multipart open key, `OmMultipartKeyInfo`, bucket info, and bucket layout.

Control flow: `addToDBBatch` delegates to the singleton abort helper, which deletes open/multipart metadata, queues parts in deleted table, and updates bucket state.

State and persistence behavior: It removes one MPU's open-key and multipart-info entries and queues part blocks for deletion.

Dependencies and integration points: It is paired with S3 abort request handling and shared multipart abort logic.

Risks and test signals: Tests should cover aborting MPUs with multiple parts, empty parts, bucket used-byte update, failed response no-op, and correct open-key table selection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadAbortResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadAbortResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadAbortResponseWithFSO.java

Purpose: `S3MultipartUploadAbortResponseWithFSO` is the FSO-specific type for MPU abort responses.

Important APIs and types: It extends `S3MultipartUploadAbortResponse` and changes cleanup metadata to include `OPEN_FILE_TABLE` instead of `OPEN_KEY_TABLE`.

Control flow: It inherits abort DB behavior from the parent; constructor parameters provide the FSO multipart open key and bucket layout used by the shared helper.

State and persistence behavior: It deletes FSO open-file MPU state, deletes multipart info, queues parts in deleted table, and updates bucket table.

Dependencies and integration points: It integrates FSO abort request paths with common multipart abort persistence.

Risks and test signals: Tests should verify cleanup annotation, open-file table deletion, inherited failed response no-op, and part cleanup equivalence with default layout.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadAbortResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCommitPartResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCommitPartResponse.java

Purpose: `S3MultipartUploadCommitPartResponse` persists a committed MPU part and cleans obsolete part data.

Important APIs and types: It extends `OmKeyResponse`, stores multipart key, open part key, updated `OmMultipartKeyInfo`, optional `keyToDeleteMap`, optional open part key info to delete on abort race, bucket info, and bucket ID. It handles statuses `OK` and `NO_SUCH_MULTIPART_UPLOAD_ERROR`.

Control flow: `checkAndUpdateDB` has a special abort-race path: if the MPU no longer exists, it moves the open part to deleted table. On OK, `addToDBBatch` writes obsolete parts to deleted table, updates multipart info table, deletes the open part key, and updates bucket used bytes.

State and persistence behavior: It mutates multipart info, open-key/open-file, deleted, and bucket tables. It can write deleted-table state even for a non-OK abort-race status.

Dependencies and integration points: It integrates S3 commit-part request logic, overwrite handling, abort races, bucket layout routing, and key deletion service.

Risks and test signals: Tests should cover normal commit, overwrite part cleanup, no-such-upload abort race cleanup, bucket update, open-key deletion, and null optional maps.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCommitPartResponse.java -->
