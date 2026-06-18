# subset-b-008101 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tagging/S3PutObjectTaggingRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tagging/S3PutObjectTaggingRequest.java

Purpose: Handles S3 `PutObjectTagging` for non-FSO bucket layouts by validating the key path, resolving bucket links/ACLs, and replacing the `OmKeyInfo` tag map without changing object content metadata.

Important APIs and types: Extends `OMKeyRequest`; uses `PutObjectTaggingRequest`, `KeyArgs`, `KeyValueUtil.getFromProtobuf`, `OmKeyInfo`, `OMMetadataManager.getKeyTable`, `S3PutObjectTaggingResponse`, and `BUCKET_LOCK`.

Control flow: `preExecute` normalizes the key name, resolves bucket and write ACLs, and rewrites the request. `validateAndUpdateCache` increments metrics, takes the bucket write lock, validates volume and bucket, loads the key table entry by ozone key, throws `KEY_NOT_FOUND` when absent, builds a new `OmKeyInfo` with tags and update ID, adds it to the key-table cache, returns a success response, audits, and records failure metrics/logs on exceptions.

State and persistence behavior: The only persistent mutation is a key-table cache update at the Ratis transaction index. The key modification time is deliberately not changed because S3 last-modified tracks object content changes, not tag changes.

Dependencies and integration points: Integrates S3 gateway tagging RPCs with OM key metadata, ACL checks, audit logging, lock tracking, double-buffer response persistence, and `OMClientRequestUtils.shouldLogClientRequestFailure`.

Risks: Correctness depends on the resolved `KeyArgs` from `preExecute` matching the cache update path. Missing key handling is explicit, but tag-size or tag-count policy is assumed to have been validated before this handler. Tests should cover existing key, absent key, ACL rejection, audit/failure metric paths, and unchanged modification time.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tagging/S3PutObjectTaggingRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tagging/S3PutObjectTaggingRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tagging/S3PutObjectTaggingRequestWithFSO.java

Purpose: FSO-specific `PutObjectTagging` handler that updates tags on file entries in file-system-optimized buckets and rejects directory tagging.

Important APIs and types: Extends `S3PutObjectTaggingRequest`; uses `OMFileRequest.getOMKeyInfoIfExists`, `OzoneFileStatus`, `OzoneFSUtils.getFileName`, `OMMetadataManager.getOzonePathKey`, `S3PutObjectTaggingResponseWithFSO`, and FSO volume/bucket object IDs.

Control flow: It uses the inherited `preExecute`. In validation it takes the bucket write lock, validates volume/bucket, resolves the file status, rejects missing keys and directories, computes the FSO path-table DB key from volume ID, bucket ID, parent object ID, and file name, updates tags and update ID, writes the key-table cache entry, and returns the FSO response containing the object IDs.

State and persistence behavior: Persists a replacement `OmKeyInfo` in the FSO key table cache. It sets the `OmKeyInfo` key name back to the leaf file name before computing the DB key and leaves object modification time unchanged.

Dependencies and integration points: Integrates tagging with FSO path lookup, bucket object identity, file table response flushing, OM metrics, and bucket-level locking. It shares request normalization and ACL behavior with the base tagging class.

Risks: Directory rejection is a behavior boundary that clients may hit when S3 paths overlap Ozone directories. The method logs all failures as errors, unlike the base class's selective logging. Tests should cover nested file paths, directory input, missing parent/key, and correct cache key construction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tagging/S3PutObjectTaggingRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tagging/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tagging/package-info.java

Purpose: Declares the `org.apache.hadoop.ozone.om.request.s3.tagging` package as the home for S3 object tagging request handlers.

Important APIs and types: Contains package documentation only; no runtime types or methods are exported.

Control flow: No executable control flow.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Provides package-level documentation for handlers such as put/delete object tagging in regular and FSO layouts.

Risks and test signals: No direct tests are needed beyond compilation/Javadoc/package discovery; package moves would affect imports and documentation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tagging/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMSetRangerServiceVersionRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMSetRangerServiceVersionRequest.java

Purpose: Internal OM request used by `OMRangerBGSyncService` to persist the Ranger Ozone service version observed during background policy synchronization.

Important APIs and types: Extends `OMClientRequest`; uses `SetRangerServiceVersionRequest`, `SetRangerServiceVersionResponse`, `OzoneConsts.RANGER_OZONE_SERVICE_VERSION_KEY`, `metaTable`, and `OMSetRangerServiceVersionResponse`.

Control flow: `validateAndUpdateCache` builds a normal OK response, reads the proposed Ranger service version, stores it as a string in the metadata table cache at the transaction index, attaches an empty proto response, and returns a response object carrying the meta key/value for double-buffer commit.

State and persistence behavior: Mutates only the OM metadata table entry for the Ranger service version. It does not perform locking, metrics, ACL checks, or auditing because it is an internal sync request.

Dependencies and integration points: Couples the Ranger background sync service to OM DB replication so followers learn the last synchronized service version.

Risks: The handler trusts the caller and accepts any long value. Tests should verify meta-table cache update, response contents, and replay/idempotence for repeated version values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMSetRangerServiceVersionRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantAssignAdminRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantAssignAdminRequest.java

Purpose: Grants tenant admin status to an existing tenant access ID and records whether the admin is delegated.

Important APIs and types: Extends `OMClientRequest`; uses `TenantAssignAdminRequest/Response`, `OmDBAccessIdInfo`, `OMMultiTenantManager`, Ranger authorizer operations, `tenantAccessIdTable`, and `VOLUME_LOCK`.

Control flow: `preExecute` resolves a missing tenant ID from the access ID, checks tenant existence and tenant-admin privilege, verifies the access ID exists and belongs to the tenant, defaults `delegated` to true, takes the authorizer write lock, calls Ranger `assignTenantAdmin`, and rewrites the request with resolved fields. `validateAndUpdateCache` locks the tenant volume, reloads the access record, writes a new `OmDBAccessIdInfo` with admin flags, updates the multi-tenant cache, returns a response, releases both locks, audits, and increments failure metrics on error.

State and persistence behavior: Updates the tenant access ID table cache only; user-principal and S3-secret tables are unchanged. Ranger role membership is modified before Ratis DB mutation and guarded by the authorizer lock.

Dependencies and integration points: Integrates tenant CLI/API admin operations with OM DB, in-memory tenant cache, metrics, audit logging, and Ranger role changes.

Risks: Ranger side effects can happen before OM cache update failure, so background reconciliation must handle divergence. Assertions enforce tenant match in validation but production safety relies on preExecute checks. Tests should cover implicit tenant resolution, delegated defaulting, mismatched access ID, missing access ID, and failure cleanup/lock release.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantAssignAdminRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantAssignUserAccessIdRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantAssignUserAccessIdRequest.java

Purpose: Assigns a user principal to a tenant by creating the tenant-scoped access ID, generated S3 secret, principal mapping, Ranger membership, and in-memory tenant-cache entry.

Important APIs and types: Extends `OMClientRequest`; uses `TenantAssignUserAccessIdRequest/Response`, `UpdateGetS3SecretRequest`, `S3SecretValue`, `OmDBAccessIdInfo`, `OmDBUserPrincipalInfo`, `OMMultiTenantManager`, `S3SecretManager`, `tenantAccessIdTable`, `principalToAccessIdsTable`, and `VOLUME_LOCK`.

Control flow: `preExecute` checks tenant admin privilege, validates access ID length and delimiter rules, requires the default access ID format, verifies tenant existence, takes the Ranger authorizer write lock, assigns the user to the tenant role, generates a SHA-256 secret, and stores it in an embedded update-secret request. `validateAndUpdateCache` locks the tenant volume, verifies tenant/access ID absence and no same-user same-tenant duplicate, creates access ID metadata, updates principal mapping, updates the S3 secret manager under its own lock, updates tenant cache, builds a response containing the S3 secret, audits, and releases locks.

State and persistence behavior: Adds cache entries for tenant access ID, principal-to-access-ID, and S3 secret state at the Ratis transaction index. It also updates the multi-tenant manager cache and relies on response classes to flush DB changes.

Dependencies and integration points: Bridges tenant management, Ranger user-role membership, secret management, OM metadata tables, metrics, and audit logging.

Risks: Authorizer changes precede OM DB changes, so partial failure reconciliation matters. The duplicate check scans a user's existing access IDs and depends on all referenced access ID rows being present. Tests should cover custom access ID rejection, duplicate assignment, existing S3 secret, missing tenant, and principal mapping invalidation/creation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantAssignUserAccessIdRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantCreateRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantCreateRequest.java

Purpose: Creates a tenant and its backing volume while provisioning default tenant roles/policies in Ranger and OM tenant metadata.

Important APIs and types: Extends `OMVolumeRequest`; uses `CreateTenantRequest/Response`, `CreateVolumeRequest`, `OmDBTenantState`, `OmVolumeArgs`, user volume lists, `OMMultiTenantManager`, `VOLUME_LOCK`, `USER_LOCK`, and `@DisallowedUntilLayoutVersion(MULTITENANCY_SCHEMA)`.

Control flow: `preExecute` checks cluster-admin privilege, validates tenant and volume names, verifies tenant and optionally volume non-existence, performs volume create ACL checks, generates volume timestamps and default role names, takes the Ranger authorizer write lock, creates Ranger tenant roles/policies, and embeds a `CreateVolumeRequest`. `validateAndUpdateCache` locks volume and user, creates or reuses the backing volume with ref-count handling, updates owner volume list when needed, verifies tenant absence, writes tenant state, updates the tenant cache, builds the response, audits, updates tenant/volume metrics, and releases all locks.

State and persistence behavior: Adds or updates volume table, user table, and tenant state table cache entries at the transaction index. It increments volume ref count for pre-existing forced volumes and creates in-memory tenant cache state.

Dependencies and integration points: Reuses volume-create helpers, integrates with Ranger authorizer operations, OM multi-tenant cache, audit logging, object ID allocation, metrics, layout-version gating, and RPC user identity.

Risks: Ranger side effects are performed before Ratis cache mutation; failures rely on background sync cleanup. Forced creation assumes volume ref count becomes exactly one. Tests should cover invalid delimiters, existing tenant, forced existing volume, user-name resolution failure, ACL failure auditing, ref-count behavior, and authorizer lock release.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantCreateRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantDeleteRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantDeleteRequest.java

Purpose: Deletes an empty tenant, removes Ranger tenant policies/roles, invalidates tenant state, and decrements the backing volume ref count.

Important APIs and types: Extends `OMVolumeRequest`; uses `DeleteTenantRequest/Response`, `OmDBTenantState`, `OmVolumeArgs`, `OzoneTenant`, `OMMultiTenantManager`, `tenantStateTable`, `volumeTable`, and `VOLUME_LOCK`.

Control flow: `preExecute` checks cluster-admin privilege, verifies the tenant has no access IDs, loads tenant metadata and volume name, checks volume ACLs when enabled, takes the authorizer write lock, and calls Ranger `deleteTenant`. Validation verifies tenant existence, reads the backing volume name, locks the volume, invalidates tenant state in cache, decrements volume ref count when applicable, updates tenant cache, returns volume name/ref count, audits, and updates metrics.

State and persistence behavior: Adds a tombstone cache entry for tenant state and an updated volume table entry with decremented ref count. The tenant cache is updated immediately; Ranger state is changed before DB mutation.

Dependencies and integration points: Coordinates OM tenant metadata, volume metadata, Ranger authorizer cleanup, tenant cache, ACL framework, audit, and metrics.

Risks: Deleting non-empty tenants is blocked only by multi-tenant manager state, so stale cache/DB mismatches matter. Empty volume names are rejected in preExecute, but validation still has a `decVolumeRefCount` branch for empty values. Tests should cover non-empty tenants, missing tenant, ACL rejection audit, volume ref count decrement, and Ranger failure paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantDeleteRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantRevokeAdminRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantRevokeAdminRequest.java

Purpose: Removes tenant admin status from an access ID while leaving the user assigned to the tenant.

Important APIs and types: Extends `OMClientRequest`; uses `TenantRevokeAdminRequest/Response`, `OmDBAccessIdInfo`, `OMMultiTenantManager`, Ranger `revokeTenantAdmin`, `tenantAccessIdTable`, and `VOLUME_LOCK`.

Control flow: `preExecute` resolves tenant ID from access ID when absent, validates tenant existence/admin privilege, verifies the access ID exists and belongs to the tenant, takes the authorizer write lock, and removes the user from the Ranger admin role. Validation locks the tenant volume, reloads the access ID row, replaces it with admin/delegated flags set false, updates the tenant cache, builds the response, releases locks, audits, and records failure metrics.

State and persistence behavior: Writes a new tenant access ID table cache value at the transaction index. It does not modify principal mappings or secrets.

Dependencies and integration points: Integrates tenant authorization, Ranger admin roles, OM access ID metadata, metrics, and audit logging.

Risks: Ranger mutation before DB mutation can leave temporary divergence. The handler uses `assert` for tenant match in validation. Tests should cover inferred tenant ID, missing access ID, non-admin revocation idempotence expectations, and lock release on Ranger/DB errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantRevokeAdminRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantRevokeUserAccessIdRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantRevokeUserAccessIdRequest.java

Purpose: Revokes a tenant access ID, removing the principal mapping, access ID record, S3 secret cache entry, Ranger user-role membership, and tenant cache entry.

Important APIs and types: Extends `OMClientRequest`; uses `TenantRevokeUserAccessIdRequest/Response`, `OmDBAccessIdInfo`, `OmDBUserPrincipalInfo`, `S3SecretManager`, `OMMultiTenantManager`, `tenantAccessIdTable`, `principalToAccessIdsTable`, and `VOLUME_LOCK`.

Control flow: `preExecute` loads access ID info, resolves tenant ID if missing, checks tenant existence and admin privilege, rejects revoking tenant admins until admin privilege is revoked, takes the authorizer lock, and calls Ranger `revokeUserAccessId`. Validation locks the tenant volume, removes the access ID from the principal set or tombstones the principal row if empty, tombstones the tenant access ID row, invalidates the S3 secret manager cache entry, updates tenant cache, builds the response, audits, and tracks failures.

State and persistence behavior: Mutates principal-to-access-IDs and tenant-access-ID cache entries, plus S3 secret manager cache invalidation. Response carries enough data for DB deletion of associated secret state.

Dependencies and integration points: Coordinates Ranger, OM tenant metadata, secret management, audit, metrics, and tenant-volume locking.

Risks: Uses `Objects.requireNonNull` for DB invariants in validation, so inconsistent metadata produces runtime failure. Ranger updates precede DB updates. Tests should cover admin-protected revoke, last access ID principal tombstone, multi-access principal update, missing access ID, and S3 secret removal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantRevokeUserAccessIdRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/package-info.java

Purpose: Documents the package for OM tenant request handlers.

Important APIs and types: Package declaration only; no classes or functions are defined.

Control flow: No executable behavior.

State and persistence behavior: None.

Dependencies and integration points: Groups multi-tenancy request handlers for tenant creation/deletion, access ID assignment/revocation, admin role changes, and Ranger service-version persistence.

Risks and test signals: Compilation/package documentation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/security/OMCancelDelegationTokenRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/security/OMCancelDelegationTokenRequest.java

Purpose: Cancels an Ozone delegation token through leader-side authorization and replicated OM DB/cache removal.

Important APIs and types: Extends `OMClientRequest`; uses `CancelDelegationTokenRequestProto`, `Token<OzoneTokenIdentifier>`, `OMPBHelper`, `delegationTokenTable`, `OMCancelDelegationTokenResponse`, and `buildTokenAuditMap`.

Control flow: `preExecute` populates user info, converts the proto token, audits failures, and calls `ozoneManager.cancelDelegationToken` to perform authorization without removing persisted state. `validateAndUpdateCache` decodes the token identifier, removes it from the in-memory delegation token manager, writes a tombstone cache entry to the delegation token table, builds a cancel response, and audits.

State and persistence behavior: Removes token state from memory and schedules deletion from the token table via cache tombstone at the transaction index.

Dependencies and integration points: Integrates Hadoop token serialization, OM delegation token manager, OM metadata table persistence, audit logging, and response flushing.

Risks: Logger is initialized with `OMGetDelegationTokenRequest.class`, which affects log categorization. Tests should cover unauthorized cancel in `preExecute`, successful table tombstone, malformed token decoding, and audit contents.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/security/OMCancelDelegationTokenRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/security/OMGetDelegationTokenRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/security/OMGetDelegationTokenRequest.java

Purpose: Converts a client get-delegation-token request into a replicated update request containing the leader-generated token and renew interval.

Important APIs and types: Extends `OMClientRequest`; uses `GetDelegationTokenRequestProto`, `UpdateGetDelegationTokenRequest`, `OMPBHelper`, `OzoneTokenIdentifier`, `delegationTokenTable`, and `OMGetDelegationTokenResponse`.

Control flow: `preExecute` asks `OzoneManager.getDelegationToken` for a token, wraps it in `UpdateGetDelegationTokenRequest`, preserves command type/client ID/trace ID, and audits generation failures. Validation handles null-token responses when security is disabled, decodes the generated token, adds renewer audit data, updates the in-memory token manager to compute renew time, writes the renew time to the delegation token table cache, and returns the original token response.

State and persistence behavior: Adds/updates token state in memory and persists token renew time keyed by `OzoneTokenIdentifier` in the delegation token table cache.

Dependencies and integration points: Coordinates security manager token generation, Ratis replication of generated secrets, OM DB cache, audit logging, protocol version compatibility, and security-disabled behavior.

Risks: Token generation happens only on the leader before Ratis replication, so all followers depend on the update request payload. Tests should cover security disabled, token renewer audit field, trace ID preservation, cache update, and invalid token proto.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/security/OMGetDelegationTokenRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/security/OMRenewDelegationTokenRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/security/OMRenewDelegationTokenRequest.java

Purpose: Renews an existing delegation token on the leader and replicates the new expiry time to all OMs.

Important APIs and types: Extends `OMClientRequest`; uses `RenewDelegationTokenRequestProto`, `UpdateRenewDelegationTokenRequest`, `RenewDelegationTokenResponseProto`, `OzoneTokenIdentifier`, `delegationTokenTable`, and `OMRenewDelegationTokenResponse`.

Control flow: `preExecute` converts the token proto, builds audit metadata, decodes the identifier, calls `ozoneManager.renewDelegationToken`, embeds the original request and new expiry time into an update request, and preserves trace ID. Validation decodes the token, updates the in-memory delegation token manager with the new expiry, writes the expiry to the token table cache, returns the renewed response, and audits success/failure.

State and persistence behavior: Updates memory and DB cache renewal time for the token. No explicit lock is taken; ordering comes from OM state machine transaction sequencing.

Dependencies and integration points: Integrates Hadoop token protocol conversion, OM delegation token manager, audit logging, Ratis update conversion, and response persistence.

Risks: Renewal authorization is leader-only in `preExecute`; followers trust the embedded expiry. Tests should cover expired/unauthorized tokens, renewer audit map, table cache update, trace preservation, and interrupted/malformed token paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/security/OMRenewDelegationTokenRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/security/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/security/package-info.java

Purpose: Documents the package containing OM security request handlers.

Important APIs and types: Package-level documentation only.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: Covers delegation token get/renew/cancel handlers in this package.

Risks and test signals: Only package compilation/Javadoc signals apply.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/security/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotCreateRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotCreateRequest.java

Purpose: Creates filesystem snapshots for a bucket, including snapshot identity, chain linkage, referenced-size metadata, and snapshot table persistence.

Important APIs and types: Extends `OMClientRequest`; uses `CreateSnapshotRequest/Response`, `SnapshotInfo`, `SnapshotChainManager`, `OmMetadataManagerImpl`, `BUCKET_LOCK`, `SNAPSHOT_LOCK`, `@RequireSnapshotFeatureState`, and `@DisallowedUntilLayoutVersion(FILESYSTEM_SNAPSHOT)`.

Control flow: Constructor derives initial `SnapshotInfo`. `preExecute` validates name, resolves linked buckets, checks bucket owner/admin authorization, enforces snapshot limit, assigns UUID and creation time, and rewrites the request. Validation takes a bucket read lock and snapshot write lock, checks duplicate table key, sets create/last transaction info, estimates referenced sizes from bucket usage and replication config, atomically updates snapshot chain and snapshot info cache, returns snapshot info, decrements in-flight count, audits, and updates metrics.

State and persistence behavior: Adds a `SnapshotInfo` cache entry with transaction metadata and previous global/path snapshot IDs. It also mutates in-memory `SnapshotChainManager`; failure during cache update attempts to roll back the chain.

Dependencies and integration points: Integrates bucket link resolution, admin authorization, quota/replication sizing, snapshot limit accounting, chain management, OM metrics, audit, and double-buffered persistence.

Risks: Chain and table cache must remain atomic; the class contains explicit synchronization and rollback for that reason. `getBucketInfo` reads cache directly and can return null if bucket metadata is inconsistent. Tests should cover duplicate names, linked bucket resolution, owner/admin checks, chain predecessor fields, in-flight decrement on failure, and referenced-size estimation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotCreateRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotDeleteRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotDeleteRequest.java

Purpose: Marks an active bucket snapshot as deleted and records deletion time for later reclamation.

Important APIs and types: Extends `OMClientRequest`; uses `DeleteSnapshotRequest/Response`, `SnapshotInfo`, `BUCKET_LOCK`, `SNAPSHOT_LOCK`, snapshot feature/layout annotations, and `OMSnapshotDeleteResponse`.

Control flow: `preExecute` validates snapshot name, resolves linked buckets, checks bucket owner/admin authorization, and writes a leader-generated deletion timestamp into the request. Validation takes bucket and snapshot write locks, loads the snapshot info row, rejects missing/already-deleted/non-active snapshots, sets status to `SNAPSHOT_DELETED`, writes deletion time, updates the snapshot info cache, builds response, audits outside locks, and updates active/deleted/failure metrics.

State and persistence behavior: Mutates only the snapshot info table cache. It does not remove the snapshot from `SnapshotChainManager`; purge handles final chain cleanup.

Dependencies and integration points: Connects external snapshot delete API to snapshot deletion services, audit, metrics, linked bucket resolution, and authorization.

Risks: Delete is a mark phase, so clients may see `FILE_NOT_FOUND` for already-deleted snapshots pending reclamation. Tests should cover status transitions, timestamp preservation from `preExecute`, permission failures, linked buckets, and no chain removal before purge.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotDeleteRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotMoveDeletedKeysRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotMoveDeletedKeysRequest.java

Purpose: Internal request that moves deleted-key metadata from a deleted snapshot toward the next snapshot or active object store during snapshot cleanup.

Important APIs and types: Extends `OMClientRequest`; uses `SnapshotMoveDeletedKeysRequest`, `SnapshotMoveKeyInfos`, `SnapshotInfo`, `SnapshotChainManager`, `SnapshotUtils`, `OMSnapshotMoveUtils`, `OMSnapshotMoveDeletedKeysResponse`, and `FILESYSTEM_SNAPSHOT` layout gating.

Control flow: Validation reconstructs the source snapshot from protobuf, verifies it still exists, finds the next snapshot in the chain, reads lists of keys to move/reclaim/rename and deleted directories, updates source/next snapshot transaction info through `OMSnapshotMoveUtils.updateCache`, resolves bucket object ID, and returns a response carrying all move lists for response-side DB updates.

State and persistence behavior: Directly updates snapshot info cache transaction metadata for source and next snapshots. Actual table-entry movement is represented in the response object.

Dependencies and integration points: Called by internal snapshot cleanup services and integrates with snapshot chain lookup, bucket metadata, and response classes that apply deleted/renamed table mutations.

Risks: No `preExecute` validation of key prefixes or duplicates exists here, unlike `OMSnapshotMoveTableKeysRequest`. Tests should cover source missing, next snapshot absent, bucket ID propagation, cache transaction-info updates, and response-side DB movement.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotMoveDeletedKeysRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotMoveTableKeysRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotMoveTableKeysRequest.java

Purpose: Internal request that validates and moves deleted-key, deleted-directory, and rename-table entries from one snapshot to the next active snapshot or AOS.

Important APIs and types: Extends `OMClientRequest`; uses `SnapshotMoveTableKeysRequest`, `SnapshotMoveKeyInfos`, `HddsProtos.KeyValue`, `SnapshotUtils`, `SnapshotChainManager`, `OMSnapshotMoveUtils`, `OmSnapshotInternalMetrics`, and system audit logging.

Control flow: `preExecute` resolves the source snapshot by ID, filters empty deleted-key and invalid deleted-dir entries, validates each key starts with the expected table/bucket prefix, rejects duplicates per category, logs system audit failures in debug mode, and rewrites the request with sanitized lists. Validation reloads the source snapshot, finds the next snapshot, rejects a non-active next snapshot, updates source/next snapshot transaction metadata, returns a response containing move lists and bucket object ID, updates metrics, and emits debug system audit details.

State and persistence behavior: Updates snapshot info cache transaction metadata; actual key/dir/rename table movement is handled by `OMSnapshotMoveTableKeysResponse`.

Dependencies and integration points: Integrates snapshot diff/cleanup services, OM metadata table prefix conventions, FSO deleted-dir tables, system audit, metrics, and snapshot chain traversal.

Risks: Prefix validation is critical to prevent cross-bucket or cross-table moves. The method relies on debug-enabled audit for detailed lists. Tests should cover duplicate detection, prefix rejection, list filtering, non-active next snapshot rejection, no-next-snapshot AOS path, and metrics on success/failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotMoveTableKeysRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotMoveUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotMoveUtils.java

Purpose: Shared helper for snapshot move requests to update transaction metadata for source and destination snapshots.

Important APIs and types: Static utility class; uses `SnapshotInfo`, `TransactionInfo.valueOf(context.getTermIndex())`, `OmMetadataManagerImpl`, `snapshotInfoTable`, `CacheKey`, and `CacheValue`.

Control flow: `updateCache` loads the metadata manager, sets `lastTransactionInfo` on the source snapshot, adds it to snapshot info table cache, and repeats for the destination snapshot when non-null.

State and persistence behavior: Schedules snapshot info table cache updates at the current transaction index. It mutates the passed `SnapshotInfo` objects in place.

Dependencies and integration points: Used by deleted-key/table-key movement handlers so snapshot metadata reflects the move transaction.

Risks: Callers must ensure the `SnapshotInfo` objects are current and safe to mutate. Tests should verify source-only and source-plus-destination updates, correct term/index encoding, and cache keys.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotMoveUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotPurgeRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotPurgeRequest.java

Purpose: Internal final purge request that removes deleted snapshots from the snapshot table and chain while updating neighboring snapshots for deeper cleanup.

Important APIs and types: Extends `OMClientRequest`; uses `SnapshotPurgeRequest`, `SnapshotInfo`, `SnapshotChainManager`, `SnapshotUtils`, `TransactionInfo`, `updatedSnapshotInfos`, `OMSnapshotPurgeResponse`, `OmSnapshotInternalMetrics`, and system audit logging.

Control flow: For each requested snapshot DB key, validation loads the latest snapshot info from a local map/table, skips already-purged rows, finds next and next-to-next snapshots, clears deep-clean flags on them, updates chain predecessor links for next path/global snapshots, tombstones the purged snapshot row, removes it from local cache, then stamps all updated snapshots with the current transaction info and returns a purge response.

State and persistence behavior: Writes cache updates for affected neighbor snapshots, deletes purged snapshot rows via tombstone cache entries, mutates in-memory `SnapshotChainManager`, and carries updated snapshots in the response.

Dependencies and integration points: Called by snapshot deleting service and coordinates with chain state, deep-cleaning services, snapshot info table persistence, internal metrics, and system audit.

Risks: The request relies on serialized OM state machine execution rather than explicit locks. It tolerates `NoSuchElementException` when a snapshot was already removed from in-memory chain but not flushed. Tests should cover multi-snapshot purge ordering, chain predecessor rewrites, deep-clean flag resets, already-purged rows, and last-transaction-info updates.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotPurgeRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotRenameRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotRenameRequest.java

Purpose: Renames an active snapshot by moving its snapshot info table key and updating chain metadata.

Important APIs and types: Extends `OMClientRequest`; uses `RenameSnapshotRequest/Response`, `SnapshotInfo`, `BUCKET_LOCK`, two `SNAPSHOT_LOCK`s, snapshot rename config keys, feature/layout annotations, and `OMSnapshotRenameResponse`.

Control flow: `preExecute` checks server config allows rename, validates new snapshot name, resolves linked buckets, checks bucket owner/admin permission, and writes a leader-generated rename time. Validation locks the bucket and both old/new snapshot names, rejects new-name collision, loads old snapshot, rejects missing/deleted/non-active states, changes the name, tombstones the old table key, adds the new table key, updates `SnapshotChainManager`, builds a response, releases locks, and audits.

State and persistence behavior: Deletes the old snapshot info table row and adds the renamed row at the transaction index. The same `SnapshotInfo` object is also reflected in the in-memory snapshot chain.

Dependencies and integration points: Integrates snapshot feature flag/config, linked bucket resolution, authorization, snapshot locks, chain manager update, audit, and metrics.

Risks: `renameTime` is generated but not used in validation in this file. Lock ordering on old/new names must be consistent with other snapshot operations. Tests should cover config-disabled behavior, name collision, deleted snapshot rename, old/new table cache updates, and chain lookup after rename.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotRenameRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotSetPropertyRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotSetPropertyRequest.java

Purpose: Internal request that updates computed snapshot properties such as exclusive size, replicated size, deep-clean flags, and directory-deep-clean deltas.

Important APIs and types: Extends `OMClientRequest`; uses one or many `SetSnapshotPropertyRequest` protos, `SnapshotInfo`, `SnapshotSize`, `snapshotInfoTable`, `OMSnapshotSetPropertyResponse`, `OmSnapshotInternalMetrics`, and system audit logging.

Control flow: Validation collects singular and repeated property requests, rejects duplicate snapshot keys in one request, loads each snapshot info row, applies optional property fields via `updateSnapshotProperty`, records per-snapshot audit params, writes each updated snapshot to the cache, increments metrics per update, and returns a response containing updated snapshots. IO and unchecked IO failures produce an error response and failure metric.

State and persistence behavior: Mutates snapshot info table cache entries for existing snapshots. It updates snapshot objects in memory before cache insertion.

Dependencies and integration points: Used by background snapshot size/deep-clean computation services and integrates with OM metadata persistence, internal metrics, and system audit.

Risks: Duplicate snapshot keys are rejected to avoid conflicting updates in a single transaction. Error construction for missing snapshots has a malformed message but correct `FILE_NOT_FOUND` code. Tests should cover each optional field, batch updates, duplicate detection, missing snapshot, and audit payloads.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotSetPropertyRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/package-info.java

Purpose: Documents the snapshot request handler package.

Important APIs and types: Package documentation only.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: Groups external and internal snapshot request handlers for create/delete/rename/purge/move/property update.

Risks and test signals: Compilation/Javadoc only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/upgrade/OMCancelPrepareRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/upgrade/OMCancelPrepareRequest.java

Purpose: Cancels OM prepare mode by deleting the on-disk prepare marker after admin authorization.

Important APIs and types: Extends `OMClientRequest`; uses `CancelPrepareResponse`, `OMCancelPrepareResponse`, `OMPrepareResponse` for error response construction, `PrepareState.cancelPrepare`, `OMAction.UPGRADE_CANCEL`, and `Type.CancelPrepare`.

Control flow: Validation logs the request, builds a response, checks superuser privilege when admin authorization is enabled, creates the cancel response, calls `ozoneManager.getPrepareState().cancelPrepare()`, audits success/failure, and returns an error response on IO failure.

State and persistence behavior: Does not mutate OM DB/cache. It deletes local disk prepare marker state, which controls prepare mode across restarts.

Dependencies and integration points: Integrates upgrade/prepare state with OM admin authorization, audit logging, and response protocol.

Risks: The catch returns `OMPrepareResponse` rather than `OMCancelPrepareResponse` on error, which may be intentional reuse but is a type-specific review point. Tests should cover admin denial, marker deletion, no DB cache update, and audit action.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/upgrade/OMCancelPrepareRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/upgrade/OMFinalizeUpgradeRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/upgrade/OMFinalizeUpgradeRequest.java

Purpose: Handles upgrade finalization requests, invokes OM finalization logic, and persists the resulting metadata layout version.

Important APIs and types: Extends `OMClientRequest`; uses `FinalizeUpgradeRequest/Response`, `UpgradeFinalizationStatus`, `StatusAndMessages`, `LAYOUT_VERSION_KEY`, `metaTable`, and `OMFinalizeUpgradeResponse`.

Control flow: Validation checks admin authorization, reads the upgrade client ID, calls `ozoneManager.finalizeUpgrade`, converts finalization status into protobuf, reads the current metadata layout version, writes it to the metadata table cache, builds the finalize response, audits, and returns an error response with layout version `-1` on IO failure.

State and persistence behavior: Updates `LAYOUT_VERSION_KEY` in OM meta table cache at the transaction index. Finalization may also mutate version-manager state through `ozoneManager.finalizeUpgrade`.

Dependencies and integration points: Integrates layout-version manager, upgrade finalization subsystem, admin ACLs, OM metadata persistence, and audit.

Risks: Response status is coarse and only includes the status enum, not messages. Tests should cover admin denial, layout version cache value, status conversion, repeated finalization, and error response layout version.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/upgrade/OMFinalizeUpgradeRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/upgrade/OMPrepareRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/upgrade/OMPrepareRequest.java

Purpose: Prepares OM for upgrade/downgrade by ensuring committed transactions are flushed, taking a Ratis state-machine snapshot, purging logs, and writing prepare marker state.

Important APIs and types: Extends `OMClientRequest`; uses `PrepareRequestArgs`, `PrepareResponse`, `OMPrepareResponse`, `OzoneManagerDoubleBuffer`, `OzoneManagerRatisServer`, `OzoneManagerStateMachine`, `RaftServer.Division`, `RaftLog`, and `PrepareState.finishPrepare/cancelPrepare`.

Control flow: Validation builds a prepare response with the current transaction index, manually adds it to the double buffer, waits until OM DB and Ratis state machine have applied at least that index, takes a snapshot and purges logs via `takeSnapshotAndPurgeLogs`, writes the prepare marker, audits, and handles failures by returning `PREPARE_FAILED`, cancelling prepare state, and restoring interrupt status when needed.

State and persistence behavior: Mutates double-buffer state, Ratis snapshot/log state, and local prepare marker file. It intentionally bypasses normal cache mutation and manually enqueues its response before log purging.

Dependencies and integration points: Deeply integrates OM request processing with Ratis state machine, DB snapshot index tracking, log purge mechanics, prepare gate state, audit logging, and client-configured wait intervals.

Risks: Timing and ordering are critical; losing the prepare log or snapshot before DB flush could corrupt upgrade state. Concurrent prepare/cancel requests have documented limitations. Tests should cover timeout branches, snapshot index lower than prepare index, purge future failure, marker cleanup on error, and manual double-buffer insertion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/upgrade/OMPrepareRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/upgrade/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/upgrade/package-info.java

Purpose: Documents the OM upgrade finalization/preparation request package.

Important APIs and types: Package declaration only.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: Groups prepare, cancel-prepare, and finalize-upgrade request handlers.

Risks and test signals: Compilation/Javadoc only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/upgrade/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/AclOp.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/AclOp.java

Purpose: Provides a concise functional-interface alias for ACL list update operations.

Important APIs and types: Extends `BiPredicate<List<OzoneAcl>, AclListBuilder>`.

Control flow: No methods beyond inherited `test`; implementers/lambdas decide whether and how an ACL operation changes the builder.

State and persistence behavior: No direct persistence. It operates on supplied ACL lists/builders in callers.

Dependencies and integration points: Used by ACL request helpers to avoid repeating long generic types for add/remove/set operations.

Risks and test signals: Behavioral tests belong to callers/lambdas. Compilation ensures type compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/AclOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/OMEchoRPCWriteRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/OMEchoRPCWriteRequest.java

Purpose: Handles write-path EchoRPC requests by returning a generated payload of requested response size without mutating OM metadata.

Important APIs and types: Extends `OMClientRequest`; uses `EchoRPCRequest`, `EchoRPCResponse`, `PayloadUtils.generatePayloadProto2`, `OmResponseUtil`, and `OMEchoRPCWriteResponse`.

Control flow: Validation reads the echo request, generates a protobuf `ByteString` payload sized by `payloadSizeResp`, builds an echo response, wraps it in a standard OM response, and returns it.

State and persistence behavior: No DB/cache mutation. It is a write request only in the sense that it travels through write RPC/Ratis code paths.

Dependencies and integration points: Used for RPC benchmarking/testing and integrates with standard OM response construction.

Risks: Large requested payloads can stress memory/network. Tests should cover payload size accuracy and no metadata side effects.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/OMEchoRPCWriteRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/OMMultipartUploadUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/OMMultipartUploadUtils.java

Purpose: Shared utility methods for multipart upload ID generation, DB-key parsing, layout-aware open-key construction, and multipart flag checks.

Important APIs and types: Static utility class; uses `UUIDv7.randomUUID`, `UniqueId.next`, `OMMetadataManager.getMultipartKey`/`getMultipartKeyFSO`, `BucketLayout`, `OmKeyInfo`, `OM_KEY_PREFIX`, and `StringUtils`.

Control flow: `getMultipartUploadId` creates a UUIDv7 plus unique numeric suffix. `getUploadIdFromDbKey` splits a DB key on `/`, requires enough path components, validates the suffix shape as UUID plus unique ID, and returns it or null. `getMultipartOpenKey` dispatches to FSO or object-store key generation. `isMultipartKeySet` checks latest version locations and its multipart flag.

State and persistence behavior: No persistence; helpers derive IDs and keys used by request handlers that persist multipart state.

Dependencies and integration points: Used by multipart initiate/commit/complete/abort paths across regular and FSO layouts.

Risks: Upload ID parsing is shape-based and assumes six hyphen-delimited pieces. Key splitting depends on `OM_KEY_PREFIX`. Tests should cover malformed DB keys, FSO/non-FSO open-key generation, null latest locations, and UUIDv7 ID uniqueness/format.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/OMMultipartUploadUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/ObjectParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/ObjectParser.java

Purpose: Parses ACL object paths into volume, bucket, and key/prefix components according to requested object type.

Important APIs and types: Uses `OzoneObj.ObjectType`, `OZONE_URI_DELIMITER`, `StringUtils.split(path, delimiter, 3)`, and `OMException.ResultCodes.INVALID_PATH_IN_ACL_REQUEST`.

Control flow: Constructor rejects null paths, splits into at most three tokens, accepts exactly one token for volumes, two for buckets, and three for keys or prefixes; otherwise it throws `OMException`. Getters expose parsed components.

State and persistence behavior: Stores parsed fields in the parser instance only; no persistence.

Dependencies and integration points: Used by ACL request handling to translate `OzoneObj.getPath()` into OM metadata names.

Risks: Empty/multiple-delimiter paths are normalized by `StringUtils.split`, so callers must understand that empty tokens are discarded. Tests should cover legal volume/bucket/key/prefix paths and malformed/empty paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/ObjectParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/OmKeyHSyncUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/OmKeyHSyncUtil.java

Purpose: Provides helper logic to detect whether a key has already been hsync'ed by the same client and can avoid an extra open-key table update.

Important APIs and types: Static utility; uses `OmKeyInfo.getMetadata`, `OzoneConsts.HSYNC_CLIENT_ID`, and SLF4J logging.

Control flow: `isHSyncedPreviously` reads the previous hsync client ID metadata. It returns true when it matches the current client ID, logs a warning when a different previous client ID is found, and otherwise returns false.

State and persistence behavior: No direct mutation. It reads `OmKeyInfo` metadata that is persisted by key commit/hsync handlers.

Dependencies and integration points: Used by OM key write/hsync request paths to reduce redundant DB writes while preserving client ownership diagnostics.

Risks: Mismatched client IDs are only warned, not rejected, so callers must enforce any stronger semantics. Tests should cover no metadata, matching metadata, and mismatch logging/false result.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/OmKeyHSyncUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/OmResponseUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/OmResponseUtil.java

Purpose: Central helper for initializing successful OM response builders from requests.

Important APIs and types: Static `getOMResponseBuilder(OMRequest)` returns an `OMResponse.Builder` with request command type, `Status.OK`, trace ID, and success true.

Control flow: Single static method creates and configures the response builder.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Used broadly by OM request handlers as the common response baseline before adding operation-specific response protos or error conversion.

Risks: Assumes `request.getTraceID()` is safe for all callers; proto defaults apply when trace ID is absent. Tests should verify command type, status, success flag, and trace propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/OmResponseUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/package-info.java

Purpose: Documents the OM request utility package.

Important APIs and types: Package declaration only.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: Groups request helper classes for ACLs, response builders, multipart upload helpers, object parsing, hsync, and echo RPC handling.

Risks and test signals: Compilation/Javadoc only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/OMClientVersionValidator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/OMClientVersionValidator.java

Purpose: Annotation for validator methods that apply based on the client protocol version of an OM request.

Important APIs and types: Runtime method annotation targeted at methods, marked with `@RegisterValidator`; attributes are `processingPhase`, `requestType[]`, and `applyBefore` of type `ClientVersion`.

Control flow: No executable code in the annotation itself. Validator registry reflection discovers annotated static methods and applies them when request client version precedes the configured bound.

State and persistence behavior: No persistence. Annotation metadata is retained at runtime.

Dependencies and integration points: Integrates with `ValidatorRegistry`, `VersionExtractor`, `RequestProcessingPhase`, and request validation framework for older-client compatibility.

Risks: Annotated methods must follow fixed static signatures documented in Javadoc; misuse is detected at registry/runtime rather than compile time. Tests should cover registry discovery and version-bound selection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/OMClientVersionValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/OMLayoutVersionValidator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/OMLayoutVersionValidator.java

Purpose: Annotation for validator methods that apply based on OM metadata layout version and feature finalization state.

Important APIs and types: Runtime method annotation targeted at methods, marked with `@RegisterValidator`; attributes are `processingPhase`, `requestType[]`, and `applyBefore` of type `OMLayoutFeature`.

Control flow: The annotation contributes metadata consumed by validator discovery and dispatch; actual validation runs in annotated static methods.

State and persistence behavior: No direct state beyond runtime annotation metadata.

Dependencies and integration points: Connects request handlers and compatibility validators to the layout-version manager through `ValidatorRegistry`, `VersionExtractor`, and `ValidationContext`.

Risks: Multiple request types are discouraged for maintainability. Incorrect signatures or bounds can skip critical pre-finalization validation. Tests should cover discovery and dispatch around layout versions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/OMLayoutVersionValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/RequestFeatureValidator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/RequestFeatureValidator.java

Purpose: General annotation for request/response validators selected by runtime validation conditions and request type.

Important APIs and types: Runtime method annotation with `conditions`, `processingPhase`, and singular `requestType`; uses `ValidationCondition`, `RequestProcessingPhase`, and OM request `Type`.

Control flow: No executable code; reflection-based registry collects methods and later invokes them in pre- or post-processing phases when all selection criteria match.

State and persistence behavior: Runtime annotation metadata only.

Dependencies and integration points: Base annotation for validators that are not specifically client-version or layout-version bounded.

Risks: The annotation is not itself marked `@RegisterValidator` here, so discovery behavior depends on the broader validator registry implementation. Tests should verify annotated methods are found, signature-checked, and condition-filtered.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/RequestFeatureValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/RequestValidations.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/RequestValidations.java

Purpose: Configures and executes the OM request validation framework for pre-process request validators and post-process response validators.

Important APIs and types: Holds validation package name, `ValidationContext`, and `ValidatorRegistry`; uses `RequestProcessingPhase.PRE_PROCESS/POST_PROCESS`, reflection `Method.invoke`, `OMRequest`, `OMResponse`, `OMException`, and `ServiceException`.

Control flow: `fromPackage` sets scan root, `withinContext` sets context, `load` creates the registry. `validateRequest` finds matching pre-process validators for current conditions and command type, invokes them in order, unwraps `OMException` causes, and otherwise wraps reflection failures in `ServiceException`. `validateResponse` similarly invokes post-process validators and wraps reflection failures.

State and persistence behavior: Maintains in-memory registry/context only. It does not persist validation state.

Dependencies and integration points: Sits in the OM request pipeline between raw protocol handling and operation-specific request classes, using `ValidationCondition` to decide compatibility behaviors.

Risks: `context` and `registry` must be initialized before validation; otherwise null failures occur. Invocation order comes from registry. Tests should cover condition filtering, chained request mutation, OMException unwrapping, post-response mutation, and illegal access/invocation errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/RequestValidations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/ValidationCondition.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/ValidationCondition.java

Purpose: Enumerates runtime conditions under which request validators should apply.

Important APIs and types: Enum values `CLUSTER_NEEDS_FINALIZATION` and `OLDER_CLIENT_REQUESTS`; abstract method `shouldApply(OMRequest, ValidationContext)`.

Control flow: `CLUSTER_NEEDS_FINALIZATION` checks `ctx.versionManager().needsFinalization()`. `OLDER_CLIENT_REQUESTS` compares request version with `ClientVersion.CURRENT_VERSION`.

State and persistence behavior: No persisted state. Reads request version and layout-version-manager state.

Dependencies and integration points: Used by `RequestValidations.conditions` and validator registry selection to activate compatibility validators.

Risks: Null context will break finalization checks. The older-client check assumes integer version ordering remains monotonic. Tests should cover finalized/pre-finalized contexts and old/current/future request versions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/ValidationCondition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/ValidationContext.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/ValidationContext.java

Purpose: Supplies validators with OM layout-version state and bucket layout lookup without exposing full OzoneManager.

Important APIs and types: Interface annotated `@InterfaceStability.Evolving`; methods `versionManager()` and `getBucketLayout(volume, bucket)`; static factory `of(LayoutVersionManager, OMMetadataManager)`.

Control flow: The factory returns an anonymous implementation that delegates version access to the provided version manager and bucket layout resolution to `OzoneManagerUtils.getBucketLayout`, including linked bucket source layout behavior.

State and persistence behavior: Holds references to version manager and metadata manager; no persistence.

Dependencies and integration points: Used by validation annotations/methods to make layout-version and bucket-layout decisions during request pre/post processing.

Risks: Bucket layout lookup may throw IO exceptions and validators must handle or propagate them. Tests should cover factory delegation, linked bucket layout behavior through mocked metadata, and version-manager state exposure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/ValidationContext.java -->
