# Research Group subset-b-008103

Grouped source-tree-aligned research for subset B work item `subset-b-008103`. Each section is wrapped for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCommitPartResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCommitPartResponseWithFSO.java

Purpose: FSO-specialized response for committing one S3 multipart upload part. It inherits all mutation behavior from `S3MultipartUploadCommitPartResponse` and exists to bind the response to the file-system-optimized bucket layout and the correct cleanup table metadata.

Important APIs/types/functions: The only public API is the constructor accepting `OMResponse`, multipart DB key, open key, optional `OmMultipartKeyInfo`, optional delete map, optional open part key, `OmBucketInfo`, bucket object ID, and `BucketLayout`. `@CleanupTableInfo` names `OPEN_FILE_TABLE`, `DELETED_TABLE`, `MULTIPART_INFO_TABLE`, and `BUCKET_TABLE`.

Control flow and persistence: Construction passes all request-derived state to the superclass. Runtime DB updates are therefore the superclass flow: update multipart metadata with the committed part, delete the FSO open-file entry, move replaced or pseudo part key versions to the deleted table, and update bucket accounting when supplied.

Dependencies and integration: Integrated by S3 multipart commit-part requests for FSO buckets. It depends on OM helper models (`OmMultipartKeyInfo`, `OmKeyInfo`, `RepeatedOmKeyInfo`, `OmBucketInfo`) and on the superclass implementation for actual batch writes.

Risks and test signals: The risk is constructor parameter mismatch because the class itself adds no validation. Tests should cover FSO commit-part replacing an existing part, deleting the open-file row, preserving multipart info, and updating deleted table and bucket usage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCommitPartResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCompleteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCompleteResponse.java

Purpose: Applies the OM metadata changes for successful S3 multipart upload completion in non-FSO layouts. It converts an MPU from open multipart state into a committed key and schedules unused part versions for deletion.

Important APIs/types/functions: Extends `OmKeyResponse`. The success constructor stores `multipartKey`, `multipartOpenKey`, final `OmKeyInfo`, `allKeyInfoToRemove`, `BucketLayout`, optional `OmBucketInfo`, and `bucketId`; the failure constructor calls `checkStatusNotOK()`. `addToDBBatch` is the main API. `addToKeyTable`, `getOmKeyInfo`, `getOmBucketInfo`, and `getMultiPartKey` support subclass specialization.

Control flow and persistence: `addToDBBatch` deletes the multipart open key from the open-key table for the layout, deletes the MPU entry from `MultipartInfoTable`, writes the completed `OmKeyInfo` to the key table, writes unused part `OmKeyInfo` instances to `DeletedTable` under `getOzoneDeletePathKey(objectID, multipartKey)`, and updates `BucketTable` if bucket usage changed.

Dependencies and integration: Used by complete-MPU request handling after validation and final key assembly. It depends on `OMMetadataManager` table accessors, `BatchOperation`, `RepeatedOmKeyInfo`, and cleanup table declarations for replay/cache cleanup.

Risks and test signals: Completion is atomic only through the enclosing batch, so partial or out-of-order writes would corrupt MPU state. Tests should verify open key and MPU table deletion, committed key insertion, unused-part cleanup, bucket usage updates, overwrite behavior, and failure-response no-op semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCompleteResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCompleteResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCompleteResponseWithFSO.java

Purpose: FSO variant of complete-MPU response. It commits the final object into the file table and creates any missing parent directory entries required by S3 path semantics over an FSO bucket.

Important APIs/types/functions: Extends `S3MultipartUploadCompleteResponse`. The success constructor adds `volumeId`, `bucketId`, `missingParentInfos`, and `multipartKeyInfo`. It overrides `addToDBBatch` and `addToKeyTable`. It uses `OMFileRequest.addToFileTable`, `OMFileRequest.addToOpenFileTableForMultipart`, and `OMFileRequest.getOmKeyInfoFromFileTable`.

Control flow and persistence: If parent directories are missing, it writes each `OmDirectoryInfo` to `DirectoryTable` under an object-ID path key, updates bucket table namespace accounting, and, when an existing file table entry is detected for the multipart key, re-adds multipart open-file metadata. It then delegates to the base class to delete open-file and MPU entries, add the final file, schedule unused parts, and update bucket accounting.

Dependencies and integration: Integrated by complete-MPU requests for `FILE_SYSTEM_OPTIMIZED` buckets. It depends on FSO object IDs, directory-table semantics, and the base completion flow for common MPU cleanup.

Risks and test signals: Parent directory creation and open-file restoration are subtle because they interact with overwrite and missing-parent flows. Tests should cover nested S3 keys in FSO buckets, overwrite of existing files, deleted unused parts, bucket namespace/bytes changes, and failure constructor no-op behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCompleteResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/package-info.java

Purpose: Declares the `org.apache.hadoop.ozone.om.response.s3.multipart` package and documents that it contains S3 multipart upload response classes.

Important APIs/types/functions: No executable API is defined. The package groups response classes for initiating, committing, aborting, completing, and expiring multipart uploads, including object-store and FSO layout variants.

Control flow and persistence: None directly. Persistence behavior lives in the response classes in this package, which mutate open-key/open-file, multipart-info, key/file, deleted, directory, and bucket tables through OM batch operations.

Dependencies and integration: The package belongs to OM response handling and is consumed by S3 multipart request implementations and double-buffer replay.

Risks and test signals: Package metadata risk is limited to stale documentation. Tests should focus on the concrete response classes and on package-level cleanup table coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/security/OMSetSecretResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/security/OMSetSecretResponse.java

Purpose: Persists an explicitly set S3 secret for an access ID through `S3SecretManager`.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor accepts nullable `accessId`, nullable `S3SecretValue`, required `S3SecretManager`, and `OMResponse`; the failure constructor calls `checkStatusNotOK()`. `addToDBBatch` writes the secret only when the response status is `OK` and a value is present.

Control flow and persistence: On success, it chooses between `secretManager.batcher().addWithBatch(batchOperation, accessId, s3SecretValue)` for batch-capable stores and `secretManager.storeSecret(accessId, s3SecretValue)` for non-batch stores. `@CleanupTableInfo` identifies `S3_SECRET_TABLE`, although the manager may abstract the concrete backend.

Dependencies and integration: Used by S3 secret set request handling. It integrates OM double-buffer batching with the pluggable secret manager/store path.

Risks and test signals: Non-batch stores are mutated outside the OM RocksDB batch, so replay/idempotency and failure ordering need attention. Tests should cover batch and non-batch managers, null secret no-op, status-not-OK no-op, and access ID consistency with `S3SecretValue`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/security/OMSetSecretResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/security/S3GetSecretResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/security/S3GetSecretResponse.java

Purpose: Handles persistence side effects for get-or-create S3 secret responses. It records a generated secret when needed and when the configured secret store supports OM batch updates.

Important APIs/types/functions: Extends `OMClientResponse`. The constructor stores nullable `S3SecretValue`, required `S3SecretManager`, and `OMResponse`. `addToDBBatch` writes through `s3SecretManager.batcher().addWithBatch` when status is `OK` and a secret exists. `getS3SecretValue` is exposed for tests.

Control flow and persistence: A successful get response with a newly generated value batches the secret under `s3SecretValue.getKerberosID()`. If the secret manager is not batch capable, no response write occurs because the request path already stored the secret.

Dependencies and integration: Integrates with S3 secret retrieval request logic and `S3SecretManager`. Cleanup metadata names `S3_SECRET_TABLE`.

Risks and test signals: The class relies on request-side behavior for non-batch stores, so tests should verify no duplicate writes and correct persistence across both storage modes. Status failure and null-value cases should leave the DB untouched.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/security/S3GetSecretResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/security/S3RevokeSecretResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/security/S3RevokeSecretResponse.java

Purpose: Applies S3 secret revocation by deleting the secret associated with a Kerberos ID/access identity through `S3SecretManager`.

Important APIs/types/functions: Extends `OMClientResponse`. The constructor stores nullable `kerberosID`, required `S3SecretManager`, and `OMResponse`. `addToDBBatch` is the only behavior and is guarded by non-null ID plus `Status.OK`.

Control flow and persistence: For batch-capable secret storage, the delete is added to the OM batch with `s3SecretManager.batcher().deleteWithBatch`. Otherwise it invokes `s3SecretManager.revokeSecret(kerberosID)` directly. Cleanup table metadata identifies `S3_SECRET_TABLE`.

Dependencies and integration: Used by revoke-secret request handling and abstracted secret storage implementations.

Risks and test signals: Direct non-batch deletion is outside RocksDB atomicity. Tests should cover batch and non-batch stores, repeated revoke idempotency, status-not-OK no-op, and null Kerberos ID behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/security/S3RevokeSecretResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/security/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/security/package-info.java

Purpose: Declares the `org.apache.hadoop.ozone.om.response.s3.security` package for S3 secret/security response classes.

Important APIs/types/functions: No executable API. The package groups responses for get, set, and revoke S3 secret operations.

Control flow and persistence: None directly. Concrete classes coordinate OM response status with `S3SecretManager` and `S3_SECRET_TABLE` updates.

Dependencies and integration: Integrated by S3 secret request classes and the OM double-buffer response pipeline.

Risks and test signals: Documentation-only file. Test signals belong to the concrete response classes, especially batch versus non-batch secret-store behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/security/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3DeleteObjectTaggingResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3DeleteObjectTaggingResponse.java

Purpose: Persists an object key after S3 object tags have been removed in non-FSO layouts.

Important APIs/types/functions: Extends `OmKeyResponse`. The success constructor accepts `OMResponse` and updated `OmKeyInfo`; the failure constructor accepts `BucketLayout` and calls `checkStatusNotOK()`. `addToDBBatch` writes the supplied key info to the layout-specific key table using `getOzoneKey`.

Control flow and persistence: The request layer mutates the tag metadata inside `OmKeyInfo`. The response batches a `putWithBatch` to `getKeyTable(getBucketLayout())` under `volume/bucket/key` DB key. Cleanup table metadata names `KEY_TABLE`.

Dependencies and integration: Used by S3 delete-object-tagging request handling. It depends on `OMMetadataManager`, `BatchOperation`, and key-table layout selection from `OmKeyResponse`.

Risks and test signals: The response overwrites the whole `OmKeyInfo`, so stale request-side fields can regress unrelated metadata. Tests should verify tag removal, retention of ACL/version/block fields, failure no-op behavior, and correct key table for non-FSO bucket layouts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3DeleteObjectTaggingResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3DeleteObjectTaggingResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3DeleteObjectTaggingResponseWithFSO.java

Purpose: FSO-specific response for deleting S3 object tags by updating the file-table entry addressed by object IDs.

Important APIs/types/functions: Extends `S3DeleteObjectTaggingResponse`. The success constructor adds `volumeId` and `bucketId`; the failure constructor delegates to the base failure path. It overrides `addToDBBatch` and `getBucketLayout`.

Control flow and persistence: Builds the FSO DB key with `getOzonePathKey(volumeId, bucketId, parentObjectID, fileName)` and writes updated `OmKeyInfo` to `getKeyTable(FILE_SYSTEM_OPTIMIZED)`, which maps to the file table. Cleanup table metadata names `FILE_TABLE`.

Dependencies and integration: Used by delete-object-tagging requests for FSO buckets. It relies on `OmKeyInfo` carrying correct parent object ID and file name.

Risks and test signals: Incorrect object ID or file name would update the wrong file-table row. Tests should cover nested FSO objects, tag removal on files with shared names under different parents, layout override behavior, and failure response no-op behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3DeleteObjectTaggingResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3PutObjectTaggingResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3PutObjectTaggingResponse.java

Purpose: Persists updated S3 object tag metadata for non-FSO key-table layouts.

Important APIs/types/functions: Extends `OmKeyResponse`. The success constructor stores updated `OmKeyInfo`; the failure constructor stores layout and calls `checkStatusNotOK()`. `addToDBBatch` writes the complete `OmKeyInfo` back to the layout-specific key table under `getOzoneKey`.

Control flow and persistence: The response has no tag parsing logic. It assumes the request path has already validated and updated tags in `OmKeyInfo`, then performs a single batched key-table put. Cleanup metadata names `KEY_TABLE`.

Dependencies and integration: Integrated by S3 put-object-tagging requests. Depends on `BucketLayout`, `OMMetadataManager`, and `BatchOperation`.

Risks and test signals: The whole key record is rewritten, so tests should check preservation of existing object metadata while tags change. Include invalid-request failure no-op, overwrite of existing tags, and non-FSO layout table selection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3PutObjectTaggingResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3PutObjectTaggingResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3PutObjectTaggingResponseWithFSO.java

Purpose: FSO variant of S3 put-object-tagging response. It persists updated tag state to the file table using FSO object-ID addressing.

Important APIs/types/functions: Extends `S3PutObjectTaggingResponse`. The success constructor adds `volumeId` and `bucketId`; `addToDBBatch` writes via `getOzonePathKey`; `getBucketLayout` returns `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

Control flow and persistence: The request-mutated `OmKeyInfo` is stored under `(volumeId, bucketId, parentObjectID, fileName)` in the file table through `getKeyTable(getBucketLayout())`. Cleanup metadata names `FILE_TABLE`.

Dependencies and integration: Used by S3 tagging APIs on FSO buckets. Depends on `OmKeyInfo` path identity fields and the base class for common constructors and test access.

Risks and test signals: Main risk is addressing the wrong file-table row or dropping unrelated key metadata. Tests should cover nested paths, same file name under different directories, tag replacement, and failure-constructor no-op behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3PutObjectTaggingResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/package-info.java

Purpose: Declares the `org.apache.hadoop.ozone.om.response.s3.tagging` package for S3 object tagging response classes.

Important APIs/types/functions: No executable API. The package groups put/delete tagging response variants for key-table and FSO file-table layouts.

Control flow and persistence: None directly. Concrete classes rewrite `OmKeyInfo` in the key or file table after request-side tag mutation.

Dependencies and integration: Integrated by S3 tagging request classes and OM response batching.

Risks and test signals: Documentation-only risk. Concrete tests should emphasize layout-specific DB keys and metadata preservation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMSetRangerServiceVersionResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMSetRangerServiceVersionResponse.java

Purpose: Persists the Ranger service version string used by S3 tenant/Ranger synchronization state.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores a metadata table key and version string. The failure constructor calls `checkStatusNotOK()`. `addToDBBatch` writes the string to `MetaTable`; `getNewServiceVersion` is test-visible.

Control flow and persistence: A successful request performs one `putWithBatch(batchOperation, serviceVersionKey, serviceVersionValueStr)` on `META_TABLE`. There is no explicit status check inside `addToDBBatch`; correctness depends on the response lifecycle invoking it only for successful responses.

Dependencies and integration: Used by OM tenant/Ranger service version update request handling and likely consumed by background Ranger sync logic.

Risks and test signals: Wrong key or stale version can desynchronize Ranger policy state. Tests should cover successful meta-table write, failure no-op through `checkStatusNotOK`, and accessor returning the stored version.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMSetRangerServiceVersionResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantAssignAdminResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantAssignAdminResponse.java

Purpose: Persists an updated tenant access ID record after assigning tenant-admin privileges.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores `accessId` and updated `OmDBAccessIdInfo`; the failure constructor calls `checkStatusNotOK()`. `addToDBBatch` writes to `TenantAccessIdTable`. `getOmDBAccessIdInfo` is test-visible.

Control flow and persistence: Performs a single batched put of the access-ID record. The record is expected to contain the updated admin flag/role state prepared by the request layer. Cleanup metadata names `TENANT_ACCESS_ID_TABLE`.

Dependencies and integration: Used by `OMTenantAssignAdminRequest` and the tenant metadata model.

Risks and test signals: Because it rewrites the whole access-ID info, stale request data could overwrite other tenant-user fields. Tests should verify admin flag changes, retained tenant/user metadata, failure no-op, and table key equal to the access ID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantAssignAdminResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantAssignUserAccessIdResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantAssignUserAccessIdResponse.java

Purpose: Applies tenant user assignment by creating/updating the access ID record, principal-to-access-ID mapping, and associated S3 secret.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores `S3SecretValue`, principal, access ID, `OmDBAccessIdInfo`, `OmDBUserPrincipalInfo`, and `S3SecretManager`. `addToDBBatch` writes secret state when response status is `OK`, then writes tenant access ID and principal mapping. Test-visible accessors expose access-ID info and secret.

Control flow and persistence: Secret persistence uses `S3SecretManager` batcher when available or `storeSecret` for non-batch stores. It then puts `TenantAccessIdTable[accessId]` and `PrincipalToAccessIdsTable[principal]`. Cleanup metadata covers `S3_SECRET_TABLE`, `TENANT_ACCESS_ID_TABLE`, and `PRINCIPAL_TO_ACCESS_IDS_TABLE`.

Dependencies and integration: Used by tenant user assignment request handling. Integrates tenant metadata and S3 credential storage.

Risks and test signals: Non-batch secret writes are not atomic with table updates. Tests should cover batch and non-batch secret managers, principal mapping accumulation, access ID table content, status-not-OK secret no-op, and replay/idempotency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantAssignUserAccessIdResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantCreateResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantCreateResponse.java

Purpose: Persists tenant creation metadata and, when needed, the backing volume and owner user-volume mapping.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores `OmVolumeArgs`, optional `PersistedUserVolumeInfo`, and `OmDBTenantState`; the failure constructor calls `checkStatusNotOK()`. `addToDBBatch` writes tenant state, volume state, and optional user table state. `getOmDBTenantState` is test-visible.

Control flow and persistence: Writes `TenantStateTable[tenantId]`, `VolumeTable[getVolumeKey(volume)]`, and, if volume creation was not skipped, `UserTable[getUserKey(owner)]`. Cleanup metadata names tenant and volume tables, while user table mutation is also performed.

Dependencies and integration: Used by tenant create request flow and reuses volume-create style metadata updates.

Risks and test signals: The optional user-volume info path is important for existing volumes. Tests should cover new-volume tenant creation, skipped volume creation, tenant state fields, owner mapping, and failure no-op.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantCreateResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantDeleteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantDeleteResponse.java

Purpose: Removes tenant state and optionally updates the backing volume metadata after tenant deletion.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores volume name, nullable `OmVolumeArgs`, and tenant ID. The failure constructor calls `checkStatusNotOK()`. `addToDBBatch` deletes tenant state and conditionally writes volume args.

Control flow and persistence: Deletes `TenantStateTable[tenantId]`. If `volumeName` is non-empty, it requires `omVolumeArgs` to be non-null and to match the volume name, then writes `VolumeTable[getVolumeKey(volumeName)]` with updated volume metadata. Cleanup metadata names tenant and volume tables.

Dependencies and integration: Used by delete-tenant request handling, including flows where volume deletion or retained volume metadata has already been decided.

Risks and test signals: Preconditions intentionally fail on inconsistent volume metadata. Tests should cover tenant-only deletion, retained-volume update, mismatched volume-name assertion, null volume args when required, and failure no-op.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantDeleteResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantRevokeAdminResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantRevokeAdminResponse.java

Purpose: Persists an updated tenant access ID record after revoking admin privileges.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores `accessId` and `OmDBAccessIdInfo`; the failure constructor calls `checkStatusNotOK()`. `addToDBBatch` writes to `TenantAccessIdTable`; `getOmDBAccessIdInfo` supports tests.

Control flow and persistence: A single batched put replaces the access-ID info with request-prepared data that removes admin state. Cleanup metadata names `TENANT_ACCESS_ID_TABLE`.

Dependencies and integration: Used by tenant admin revoke request handling. The class mirrors assign-admin persistence with different request semantics.

Risks and test signals: Risk is overwriting unrelated fields in the access-ID record. Tests should verify admin flag removal, retained tenant/principal data, failure no-op, and table key correctness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantRevokeAdminResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantRevokeUserAccessIdResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantRevokeUserAccessIdResponse.java

Purpose: Applies tenant user access-ID revocation by deleting the secret and access-ID record and updating or removing the principal mapping.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores access ID, principal, updated `OmDBUserPrincipalInfo`, and `S3SecretManager`. `addToDBBatch` deletes secret state on `OK`, deletes `TenantAccessIdTable[accessId]`, and updates or deletes `PrincipalToAccessIdsTable[principal]`.

Control flow and persistence: Secret deletion uses the batcher when supported or direct `revokeSecret` otherwise. Principal mapping is retained only if the updated access-ID set is non-empty. Cleanup metadata covers secret, tenant access ID, and principal mapping tables.

Dependencies and integration: Used by tenant revoke-user request handling and S3 credential storage.

Risks and test signals: Non-batch secret deletion is not atomic with table changes. The method asserts non-null access ID and contains a TODO about status checking. Tests should cover last-access-ID removal, multi-access-ID update, batch/non-batch secret managers, failure behavior, and idempotent retries.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/OMTenantRevokeUserAccessIdResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/package-info.java

Purpose: Declares the `org.apache.hadoop.ozone.om.response.s3.tenant` package for OM tenant response classes.

Important APIs/types/functions: No executable API. The package groups responses for tenant create/delete, user access ID assignment/revocation, admin assignment/revocation, and Ranger service version updates.

Control flow and persistence: None directly. Concrete classes update tenant state, access ID, principal mapping, S3 secret, volume, user, and meta tables.

Dependencies and integration: Integrated by OM tenant request handling and Ranger/S3 tenant features.

Risks and test signals: Documentation-only risk. Test signals should focus on multi-table atomicity and secret-manager storage mode differences in the concrete responses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tenant/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/OMCancelDelegationTokenResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/OMCancelDelegationTokenResponse.java

Purpose: Removes a delegation token from OM metadata after a successful cancel-delegation-token request.

Important APIs/types/functions: Extends `OMClientResponse`. The constructor stores nullable `OzoneTokenIdentifier` and `OMResponse`. `addToDBBatch` obtains `getDelegationTokenTable()` and deletes the token only when response status is `OK`.

Control flow and persistence: A successful cancel batches `deleteWithBatch(batchOperation, ozoneTokenIdentifier)` against `DELEGATION_TOKEN_TABLE`. There is no null guard inside the OK branch, so request construction must provide the identifier on success.

Dependencies and integration: Used by OM security token cancellation request handling. Depends on `OzoneTokenIdentifier` as the table key and OM response status for gating.

Risks and test signals: Null token on OK would produce table-layer failure or undefined behavior. Tests should cover successful deletion, status-not-OK no-op, missing token defensive behavior if supported by table implementation, and replay idempotency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/OMCancelDelegationTokenResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/OMGetDelegationTokenResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/OMGetDelegationTokenResponse.java

Purpose: Persists a newly issued delegation token and its renewal time.

Important APIs/types/functions: Extends `OMClientResponse`. The constructor stores nullable `OzoneTokenIdentifier`, `renewTime`, and `OMResponse`. `addToDBBatch` writes to `DelegationTokenTable` only when token is non-null and status is `OK`.

Control flow and persistence: Performs `putWithBatch(batchOperation, ozoneTokenIdentifier, renewTime)` under `DELEGATION_TOKEN_TABLE`. The renew time defaults to `-1L` but is expected to be supplied for successful tokens.

Dependencies and integration: Used by get-delegation-token request handling and OM security token manager state.

Risks and test signals: Renewal time correctness controls token validity. Tests should cover successful table insert, null-token no-op, status failure no-op, and persisted value matching request-calculated renewal time.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/OMGetDelegationTokenResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/OMRenewDelegationTokenResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/OMRenewDelegationTokenResponse.java

Purpose: Updates the renewal time for an existing delegation token after a successful renew request.

Important APIs/types/functions: Extends `OMClientResponse`. The constructor stores nullable `OzoneTokenIdentifier`, new renew time, and `OMResponse`. `addToDBBatch` writes the token key and renew time to `DelegationTokenTable` when status is `OK`.

Control flow and persistence: Performs a batched put on `DELEGATION_TOKEN_TABLE`. Unlike get-token response, there is no null guard in the OK branch, so request validation must guarantee the identifier exists on success.

Dependencies and integration: Used by renew-delegation-token request handling and OM token persistence.

Risks and test signals: Null token on success and incorrect renew time are primary risks. Tests should verify update of existing token, failure no-op, replay idempotency, and boundary renewal times.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/OMRenewDelegationTokenResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/package-info.java

Purpose: Declares the `org.apache.hadoop.ozone.om.response.security` package for general OM security request responses.

Important APIs/types/functions: No executable API. The package groups delegation-token get, renew, and cancel response classes.

Control flow and persistence: None directly. Concrete responses mutate `DELEGATION_TOKEN_TABLE`.

Dependencies and integration: Integrated by OM security request handling and delegation token management.

Risks and test signals: Documentation-only risk. Concrete tests should emphasize status-gated token table writes and null token handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotCreateResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotCreateResponse.java

Purpose: Persists new snapshot metadata and creates the corresponding OM snapshot checkpoint.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores `SnapshotInfo`; the failure constructor calls `checkStatusNotOK()`. `addToDBBatch` writes snapshot info then invokes `OmSnapshotManager.createOmSnapshotCheckpoint`.

Control flow and persistence: The method intentionally writes `SnapshotInfoTable[tableKey]` before checkpoint creation so RocksDB checkpoint differ listeners can track compaction changes around snapshot creation. The checkpoint creation also cleans selected tables. Cleanup metadata covers deleted, snapshot-renamed, and snapshot-info tables.

Dependencies and integration: Used by snapshot create request handling. Integrates active OM metadata, snapshot metadata, RocksDB checkpoint creation, and snapshot diff support.

Risks and test signals: Ordering is correctness-sensitive for SnapDiff performance. Tests should verify snapshot info persistence, checkpoint directory creation, relevant table cleanup, failure no-op, and behavior under compaction/listener timing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotCreateResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotDeleteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotDeleteResponse.java

Purpose: Persists an updated `SnapshotInfo` record for a delete-snapshot request, typically marking snapshot lifecycle state rather than immediately purging physical data.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores snapshot table key and updated `SnapshotInfo`; the failure constructor calls `checkStatusNotOK()`. `addToDBBatch` writes the updated snapshot info.

Control flow and persistence: Performs one batched put to `SnapshotInfoTable[tableKey]`. Actual checkpoint deletion and chain cleanup are handled later by purge/deleting services.

Dependencies and integration: Used by snapshot delete request handling and feeds `SnapshotDeletingService`/purge flows that consume snapshot state.

Risks and test signals: The response must not remove snapshot metadata prematurely. Tests should verify state transition fields, table key correctness, later purge eligibility, and failure no-op behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotDeleteResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotMoveDeletedKeysResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotMoveDeletedKeysResponse.java

Purpose: Moves deleted-key, renamed-key, and deleted-directory records from one snapshot toward the next snapshot or active DB, and updates the originating snapshot after reclaim processing.

Important APIs/types/functions: Extends `OMClientResponse` and is built with `Builder`. Key fields are `fromSnapshot`, optional `nextSnapshot`, `nextDBKeysList`, `reclaimKeysList`, `renamedKeysList`, `movedDirs`, and `bucketId`. Helpers include `processKeys`, `processDirs`, `processReclaimKeys`, `deleteDirsFromSnapshot`, and static `createRepeatedOmKeyInfo`.

Control flow and persistence: It obtains `OmSnapshotManager` from `OmMetadataManagerImpl`, opens the from snapshot, optionally opens the next snapshot and writes to its RocksDB store in a dedicated batch, or writes to active OM batch when there is no next snapshot. It moves renamed keys to `SnapshotRenamedTable`, merges deleted entries into `DeletedTable`, moves deleted dirs, updates from-snapshot deleted entries or deletes them, flushes snapshot DB WAL/data, and finally writes updated `SnapshotInfo` records to active `SnapshotInfoTable`.

Dependencies and integration: Used by snapshot deleted-key movement requests and snapshot deep-cleaning. Depends on `OmSnapshot`, `RDBStore`, `SnapshotUtils.createMergedRepeatedOmKeyInfoFromDeletedTableEntry`, and snapshot-local metadata managers.

Risks and test signals: This crosses multiple RocksDB instances, so atomicity is not a single OM batch. Tests should cover next-snapshot and active-DB targets, empty reclaimed key lists, moved directory deletion, snapshot info updates, WAL flush behavior, and retry/idempotency after partial snapshot DB writes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotMoveDeletedKeysResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotMoveTableKeysResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotMoveTableKeysResponse.java

Purpose: Moves deleted keys, renamed entries, and deleted directory entries from one snapshot table set into the next snapshot or active DB, while removing the moved records from the source snapshot.

Important APIs/types/functions: Extends `OMClientResponse`. Constructor stores `fromSnapshot`, optional `nextSnapshot`, `bucketId`, deleted key list, deleted dir list, and renamed key list. Main helpers are `addKeysToNextSnapshot` and `deleteKeysFromSnapshot`.

Control flow and persistence: Acquires read locks on `SNAPSHOT_DB_CONTENT_LOCK` for source and optional next snapshot IDs. It opens snapshot RocksDB instances, writes moved records to the next snapshot store or active batch, commits and flushes snapshot DB batches, deletes moved records from the source snapshot DB, releases locks, then updates `SnapshotInfoTable` for source and next snapshots.

Dependencies and integration: Used by snapshot move-table-keys request handling. Depends on `OmSnapshotManager`, `OmSnapshot`, `RDBStore`, `IOzoneManagerLock`, and snapshot utility merge logic.

Risks and test signals: Lock ordering, null next snapshot handling, and multi-store commit/flush boundaries are critical. Tests should cover lock failure, no-next-snapshot active writes, deleted-dir protobuf conversion, rename deletion, snapshot info updates, and retry safety after partial movement.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotMoveTableKeysResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotPurgeResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotPurgeResponse.java

Purpose: Finalizes snapshot purge by updating related snapshot metadata, invalidating snapshot cache state, recording local purge transaction info, deleting checkpoint directories, and removing purged snapshot info rows.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores snapshot DB keys to purge, updated snapshot infos, and `TransactionInfo`; failure constructor initializes fields to null after `checkStatusNotOK()`. Helpers are `updateSnapInfo` and `updateLocalData`.

Control flow and persistence: It first writes `updatedSnapInfos` to `SnapshotInfoTable`. For each purge key, it reads snapshot info with `getSkipCache`, skips missing entries, invalidates `OmSnapshotManager` cache, removes snapshot ID mapping from chain manager, writes purge transaction info to snapshot local data through `WritableOmSnapshotLocalDataProvider`, deletes checkpoint directories, and batches deletion of the snapshot info row.

Dependencies and integration: Used by snapshot purge requests, snapshot deletion service, snapshot cache, chain manager, local data manager, and checkpoint directory management.

Risks and test signals: Purge has filesystem side effects plus DB state updates. Tests should cover missing snapshot info, cache invalidation, chain map removal, local data transaction update, checkpoint directory deletion, updated neighboring snapshot info, and retry after partially deleted directories.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotPurgeResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotRenameResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotRenameResponse.java

Purpose: Renames a snapshot by moving its snapshot-info table row from the old table key to the new table key with updated `SnapshotInfo`.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores old name/key, new name/key, and renamed info; the failure constructor calls `checkStatusNotOK()`. `addToDBBatch` performs a put then delete.

Control flow and persistence: Batches `SnapshotInfoTable.put(newName, renamedInfo)` followed by `SnapshotInfoTable.delete(oldName)`. Cleanup metadata names `SNAPSHOT_INFO_TABLE`.

Dependencies and integration: Used by snapshot rename request handling and consumed by snapshot chain lookup code that uses table keys.

Risks and test signals: The field names represent table keys rather than only display names, so request code must pass canonical keys. Tests should verify old row deletion, new row content, no orphan/duplicate snapshot info, chain lookup behavior, and failure no-op.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotRenameResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotSetPropertyResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotSetPropertyResponse.java

Purpose: Persists property changes for one or more snapshots, including size/deep-clean metadata submitted by background services.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores a collection of updated `SnapshotInfo`; the failure constructor calls `checkStatusNotOK()` and sets the collection to null. `addToDBBatch` iterates updated snapshots and writes each row.

Control flow and persistence: Performs `SnapshotInfoTable.put(tableKey, updatedSnapInfo)` for every updated snapshot. Cleanup metadata names `SNAPSHOT_INFO_TABLE`.

Dependencies and integration: Used by explicit snapshot property requests and by deletion services through `submitSetSnapshotRequests`.

Risks and test signals: Multiple snapshot rows may be updated in one batch; stale entries can regress size or deep-clean flags. Tests should cover multiple updates, exclusive size deltas, deep-clean flags, empty collection handling if allowed, and failure no-op behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotSetPropertyResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/package-info.java

Purpose: Declares the `org.apache.hadoop.ozone.om.response.snapshot` package for OM snapshot response classes.

Important APIs/types/functions: No executable API. The package groups create, delete, purge, rename, set-property, and snapshot key/table movement responses.

Control flow and persistence: None directly. Concrete classes update active OM snapshot info plus snapshot checkpoint RocksDB stores, local data, cache mappings, and checkpoint directories.

Dependencies and integration: Integrated by snapshot request handling, snapshot background services, snapshot chain management, and SnapDiff support.

Risks and test signals: Documentation-only risk. Concrete tests should emphasize multi-store atomicity, snapshot locks, and checkpoint filesystem side effects.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/OMCancelPrepareResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/OMCancelPrepareResponse.java

Purpose: Response object for cancel-prepare upgrade requests.

Important APIs/types/functions: Extends `OMClientResponse`. Constructor accepts `OMResponse`. `addToDBBatch` is overridden as an intentional no-op. Cleanup metadata names `TRANSACTION_INFO_TABLE`.

Control flow and persistence: The comment explains that cancel prepare deletes the prepare marker file and updates in-memory state outside this response, so no DB/cache update is needed here.

Dependencies and integration: Used by upgrade prepare cancellation flow. It relies on request-side or manager-side logic for marker-file deletion and state transition.

Risks and test signals: Risk is assuming DB mutation happens here when it does not. Tests should verify cancel prepare removes marker/in-memory state through the owning request path and that response replay does not change transaction info.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/OMCancelPrepareResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/OMFinalizeUpgradeResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/OMFinalizeUpgradeResponse.java

Purpose: Persists the finalized OM layout version during upgrade finalization.

Important APIs/types/functions: Extends `OMClientResponse`. Constructor stores `layoutVersionToWrite`; `addToDBBatch` writes it if not `-1`. Uses `LAYOUT_VERSION_KEY` and `META_TABLE`.

Control flow and persistence: On valid version, logs the layout version and batches `MetaTable.put(LAYOUT_VERSION_KEY, String.valueOf(layoutVersionToWrite))`. `-1` is treated as no-op.

Dependencies and integration: Used by finalize-upgrade request handling and OM layout feature finalization.

Risks and test signals: Persisting the wrong layout version can break restart compatibility. Tests should cover valid version write, sentinel no-op, log/state expectations, and replay behavior across OM restart.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/OMFinalizeUpgradeResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/OMPrepareResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/OMPrepareResponse.java

Purpose: Persists the prepare marker transaction index for OM upgrade prepare.

Important APIs/types/functions: Extends `OMClientResponse`. One constructor stores `prepareIndex`; another leaves it at `-1`. `addToDBBatch` writes `TransactionInfo` under `PREPARE_MARKER_KEY` when the index is valid.

Control flow and persistence: For a valid prepare index, writes `TransactionInfo.valueOf(TransactionInfo.DEFAULT_VALUE.getTerm(), prepareIndex)` to `TransactionInfoTable`. Cleanup metadata names `TRANSACTION_INFO_TABLE`.

Dependencies and integration: Used by prepare request handling and upgrade state checks that determine whether OM is in prepared mode.

Risks and test signals: The term is taken from `DEFAULT_VALUE`, so this marker is index-focused. Tests should verify marker write, sentinel no-op, restart detection of prepared state, and cancel-prepare interoperability.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/OMPrepareResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/package-info.java

Purpose: Declares the `org.apache.hadoop.ozone.om.response.upgrade` package for upgrade finalization and prepare responses.

Important APIs/types/functions: No executable API. The package groups prepare, cancel-prepare, and finalize-upgrade response classes.

Control flow and persistence: None directly. Concrete classes update `TRANSACTION_INFO_TABLE` or `META_TABLE`, or intentionally perform no response-side DB work.

Dependencies and integration: Integrated by OM upgrade request handling and layout-version management.

Risks and test signals: Documentation-only risk. Concrete tests should cover restart-visible prepare/finalize state and no-op cancel response semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/upgrade/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/util/OMEchoRPCWriteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/util/OMEchoRPCWriteResponse.java

Purpose: Write-path response for EchoRPC benchmarking that intentionally avoids DB/cache mutations.

Important APIs/types/functions: Extends `OMClientResponse`. Constructor stores `OMResponse`. `addToDBBatch` is overridden to return without touching metadata. `@CleanupTableInfo` has no table list.

Control flow and persistence: No persistent state is written. The request can still travel through the write/Ratis/double-buffer path, allowing latency or throughput measurement without backend metadata cost.

Dependencies and integration: Used by EchoRPC write utility or benchmark request handling.

Risks and test signals: It must remain side-effect free; adding DB writes would invalidate benchmark semantics. Tests should verify no table changes, successful response propagation, and Ratis path execution if benchmarked.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/util/OMEchoRPCWriteResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/util/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/util/package-info.java

Purpose: Declares the `org.apache.hadoop.ozone.om.response.util` package for helper/utility response classes.

Important APIs/types/functions: No executable API. The package currently includes utility responses such as EchoRPC write handling.

Control flow and persistence: None directly. Utility responses may intentionally be no-ops or support specialized benchmarking/control-plane flows.

Dependencies and integration: Integrated by OM utility request paths.

Risks and test signals: Documentation-only risk. Tests should validate the concrete utility response side-effect contract.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/util/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMQuotaRepairResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMQuotaRepairResponse.java

Purpose: Persists repaired quota/accounting state for volumes and buckets produced by `OMQuotaRepairRequest`.

Important APIs/types/functions: Extends `OMClientResponse`. One constructor handles failure/update-only response with only `OMResponse`; the success constructor stores maps of volume names to `OmVolumeArgs` and `(volume,bucket)` pairs to `OmBucketInfo`. `addToDBBatch` rewrites bucket and volume rows.

Control flow and persistence: Iterates `volBucketInfoMap.values()` and writes each bucket under `getBucketKey(volumeName, bucketName)`, then iterates `volumeArgsMap.values()` and writes each volume to `VolumeTable` using `volArgs.getVolume()` as key. Cleanup metadata names `VOLUME_TABLE` and `BUCKET_TABLE`.

Dependencies and integration: Used by quota repair request processing after recalculating usage.

Risks and test signals: Volume-table keying should be verified because most volume responses use `getVolumeKey`. Null maps in the failure-style constructor would fail if `addToDBBatch` ran. Tests should cover multi-volume/bucket repair, empty maps, failure no-op lifecycle, and repaired quota values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMQuotaRepairResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeAclOpResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeAclOpResponse.java

Purpose: Persists updated volume ACL metadata after add/remove/set ACL operations.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores updated `OmVolumeArgs`; the failure constructor calls `checkStatusNotOK()`. `addToDBBatch` writes to `VolumeTable`; `getOmVolumeArgs` is test-visible.

Control flow and persistence: Performs `VolumeTable.put(getVolumeKey(volume), omVolumeArgs)` in the OM batch. Cleanup metadata names `VOLUME_TABLE`.

Dependencies and integration: Used by volume ACL request handling. The request layer computes the ACL mutation and supplies the full volume args.

Risks and test signals: Whole-volume rewrite can overwrite owner/quota fields if stale. Tests should cover ACL add/remove/set, retained non-ACL fields, failure no-op, and correct volume DB key.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeAclOpResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeCreateResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeCreateResponse.java

Purpose: Persists a new volume and updates the owner's user-volume list.

Important APIs/types/functions: Extends `OMClientResponse`. Success constructor stores `OmVolumeArgs` and `PersistedUserVolumeInfo`; failure constructor calls `checkStatusNotOK()`. `addToDBBatch` writes volume and user rows. `getOmVolumeArgs` is test-visible.

Control flow and persistence: Computes `dbVolumeKey = getVolumeKey(volume)` and `dbUserKey = getUserKey(owner)`, then batches `VolumeTable.put` and `UserTable.put`. Cleanup metadata names `VOLUME_TABLE`, though user table is also mutated.

Dependencies and integration: Used by create-volume request handling and owner volume-list management.

Risks and test signals: Atomicity between volume and user table is required to avoid orphan volumes or missing owner listings. Tests should verify both rows, duplicate volume failure no-op, owner list content, and ACL/quota fields in `OmVolumeArgs`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeCreateResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeDeleteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeDeleteResponse.java

Purpose: Deletes a volume row and updates or removes the owner's user-volume list.

Important APIs/types/functions: Extends `OMClientResponse`. Success constructor stores volume name, owner, and updated `PersistedUserVolumeInfo`; failure constructor calls `checkStatusNotOK()`. `addToDBBatch` updates user table then deletes volume table row.

Control flow and persistence: If the updated owner volume list is empty, it deletes `UserTable[getUserKey(owner)]`; otherwise it writes the updated list. Then it deletes `VolumeTable[getVolumeKey(volume)]`. Cleanup metadata names `VOLUME_TABLE`.

Dependencies and integration: Used by delete-volume request handling after validation that the volume can be deleted.

Risks and test signals: Owner mapping and volume deletion must be atomic. Tests should cover deleting the last owner volume, deleting one of several volumes, failure no-op, and retry idempotency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeDeleteResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeSetOwnerResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeSetOwnerResponse.java

Purpose: Persists a volume owner change by updating old/new owner volume lists and the volume's owner field.

Important APIs/types/functions: Extends `OMClientResponse`. Success constructor stores old owner, old owner list, new owner list, and updated `OmVolumeArgs`. The alternate constructor allows the no-change case where status is `OK` but success is false. It overrides `checkAndUpdateDB` to write only when status is `OK` and response success is true.

Control flow and persistence: Deletes or rewrites the old owner's user row depending on whether its list is empty, writes the new owner user row, and writes updated volume args to `VolumeTable[getVolumeKey(volume)]`.

Dependencies and integration: Used by set-volume-owner request handling.

Risks and test signals: The no-op same-owner case is special and must not mutate DB. Tests should cover same owner, old owner last volume, old owner with remaining volumes, new owner list update, volume owner field update, and failure no-op.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeSetOwnerResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeSetQuotaResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeSetQuotaResponse.java

Purpose: Persists updated volume quota settings.

Important APIs/types/functions: Extends `OMClientResponse`. Success constructor stores updated `OmVolumeArgs`; failure constructor calls `checkStatusNotOK()`. `addToDBBatch` writes the volume row.

Control flow and persistence: Performs `VolumeTable.put(getVolumeKey(volume), omVolumeArgs)`. Cleanup metadata names `VOLUME_TABLE`.

Dependencies and integration: Used by set-volume-quota request handling after validation of quota values and existing usage.

Risks and test signals: Whole-volume rewrite can regress ACL/owner fields if stale. Tests should verify quota bytes/namespace changes, retained owner/ACL metadata, invalid quota failure no-op, and correct DB key.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeSetQuotaResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/package-info.java

Purpose: Declares the `org.apache.hadoop.ozone.om.response.volume` package for volume response classes.

Important APIs/types/functions: No executable API. The package groups volume create/delete, ACL, owner, quota, and quota-repair responses.

Control flow and persistence: None directly. Concrete classes mutate volume, user, and bucket metadata tables.

Dependencies and integration: Integrated by OM volume request handling and quota repair logic.

Risks and test signals: Documentation-only risk. Concrete tests should cover cross-table consistency between volume, user, and bucket rows.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/LocalS3StoreProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/LocalS3StoreProvider.java

Purpose: Provides the local OM metadata manager as the S3 secret store implementation.

Important APIs/types/functions: Implements `S3SecretStoreProvider`. Constructor stores an `OmMetadataManagerImpl`; `get(Configuration)` returns that metadata manager as `S3SecretStore`.

Control flow and persistence: No independent persistence. The returned `OmMetadataManagerImpl` owns local `S3_SECRET_TABLE` storage and related batching.

Dependencies and integration: Used as `S3SecretStoreConfigurationKeys.DEFAULT_SECRET_STORAGE_TYPE`. Integrates S3 secret manager configuration with local OM RocksDB-backed storage.

Risks and test signals: This provider ignores the passed configuration, which is appropriate for local storage but should be explicit in tests. Tests should verify default provider instantiation, returned object identity, and compatibility with `S3SecretStore` methods.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/LocalS3StoreProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/S3SecretCacheProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/S3SecretCacheProvider.java

Purpose: Factory interface for constructing S3 secret cache implementations from Ozone configuration.

Important APIs/types/functions: Declares `S3SecretCache get(Configuration conf)`. Provides built-in `IN_MEMORY` provider that returns a new `S3InMemoryCache`.

Control flow and persistence: No persistent state in the interface. The in-memory provider creates runtime cache state only.

Dependencies and integration: Used by S3 secret manager setup to decouple cache choice from manager code. Depends on Hadoop `Configuration`, `S3SecretCache`, and `S3InMemoryCache`.

Risks and test signals: Cache provider instances can affect secret lookup freshness and memory usage. Tests should verify configured provider loading, default in-memory behavior, cache expiration/capacity integration, and that a new cache instance is created as expected.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/S3SecretCacheProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/S3SecretStoreConfigurationKeys.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/S3SecretStoreConfigurationKeys.java

Purpose: Defines configuration keys and defaults for S3 secret store provider and cache behavior.

Important APIs/types/functions: Final utility class with private constructor. Constants include `S3_SECRET_STORAGE_TYPE`, `DEFAULT_SECRET_STORAGE_TYPE` (`LocalS3StoreProvider.class`), `CACHE_PREFIX`, `CACHE_LIFETIME`, `DEFAULT_CACHE_LIFETIME` (600), `CACHE_MAX_SIZE`, and `DEFAULT_CACHE_MAX_SIZE` (`Long.MAX_VALUE`).

Control flow and persistence: No runtime control flow or persistence. Values are consumed by configuration loading elsewhere.

Dependencies and integration: Integrated by S3 secret manager/provider initialization and cache setup. Uses the `ozone.secret.s3.store.` prefix.

Risks and test signals: Key spelling and default values form operator-facing compatibility. Tests should verify default local provider selection, cache lifetime unit interpretation, max-size default behavior, and configuration override parsing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/S3SecretStoreConfigurationKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/S3SecretStoreProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/S3SecretStoreProvider.java

Purpose: Factory interface for S3 secret store implementations.

Important APIs/types/functions: Declares `S3SecretStore get(Configuration conf) throws IOException`. Implementations can construct local or external secret stores from Hadoop configuration.

Control flow and persistence: No persistence in the interface. Implementations decide whether returned stores are local RocksDB-backed, external, batch-capable, or direct-write.

Dependencies and integration: Used by S3 secret manager initialization. `LocalS3StoreProvider` is the default implementation.

Risks and test signals: Store provider behavior affects atomicity of secret responses. Tests should cover provider class loading, IOException propagation, batch capability differences, and compatibility with secret manager methods.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/S3SecretStoreProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/package-info.java

Purpose: Declares the `org.apache.hadoop.ozone.om.s3` package for S3 secret store related support classes.

Important APIs/types/functions: No executable API. The package groups secret store providers, cache providers, and configuration keys.

Control flow and persistence: None directly. Concrete providers connect S3 secret manager code to local or configured stores and caches.

Dependencies and integration: Integrated by OM S3 secret management and tenant/security responses.

Risks and test signals: Documentation-only risk. Concrete tests should cover provider selection, cache configuration, and secret store persistence mode.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/AbstractKeyDeletingService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/AbstractKeyDeletingService.java

Purpose: Shared base for OM deletion background services such as key, directory, and snapshot deletion. It centralizes leader readiness checks, bootstrap locking, request submission through Ratis, metrics access, suspension, and snapshot-property request submission.

Important APIs/types/functions: Extends `BackgroundService` and implements `BootstrapStateHandler`. Important methods are abstract `getTasks`, `submitRequest`, `shouldRun`, `isPreviousPurgeTransactionFlushed`, `suspend`, `resume`, `isBufferLimitCrossed`, accessors for OM/metrics/client/call ID, `getBootstrapStateLock`, and `submitSetSnapshotRequests`. Nested `DeletingServiceTaskQueue` wraps every task in a bootstrap read lock.

Control flow and persistence: `shouldRun` requires OM leader readiness unless OM is null for tests. `submitRequest` uses `OzoneManagerRatisUtils.submitRequest` with a stable random `ClientId` and incrementing call ID. `isPreviousPurgeTransactionFlushed` compares deletion metrics' last AOS transaction against disk-flushed transaction info to avoid processing before previous purge metadata is durable. `submitSetSnapshotRequests` builds an OM request of type `SetSnapshotProperty`.

Dependencies and integration: Base class for services that submit purge or snapshot property OM requests. It depends on OM locks, Ratis utils, deletion/perf metrics, transaction info, and bootstrap state handling.

Risks and test signals: Lock wrapping and flush gating prevent races with bootstrap and unflushed purges. Tests should cover suspension waiting for futures, leader gating, bootstrap read lock acquisition for queued tasks, call ID increments, previous-purge flush blocking, and snapshot-property request submission errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/AbstractKeyDeletingService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/CompactDBUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/CompactDBUtil.java

Purpose: Utility for manual full compaction of OM RocksDB column families.

Important APIs/types/functions: Final utility class with private constructor. `compactTable(OMMetadataManager, String)` performs synchronous compaction. `compactTableAsync` wraps it in a `CompletableFuture`.

Control flow and persistence: `compactTable` creates `ManagedCompactRangeOptions`, forces bottommost-level compaction, requests exclusive manual compaction, obtains the `RocksDatabase` from `RDBStore`, resolves the column family by table name, throws `IOException` if missing, and calls `compactRange`. Async mode logs and rethrows failures through `CompletionException`.

Dependencies and integration: Used by `CompactionService` and on-demand compaction paths. Depends on OM metadata store being an `RDBStore`.

Risks and test signals: Manual compaction can be expensive and table-name sensitive. Tests should cover valid table compaction, missing column family error, async failure propagation, and option settings for forced bottommost compaction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/CompactDBUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/CompactionService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/CompactionService.java

Purpose: Background service that periodically compacts configured OM RocksDB tables.

Important APIs/types/functions: Extends `BackgroundService`. Constructor validates configured table names and uses a single compactor thread. Important methods are `validateTables`, `suspend`, `resume`, `getCompactableTables`, `getNumCompactions`, `getTasks`, `compactTableAsync`, `compactFully`, and nested `CompactTask`.

Control flow and persistence: `validateTables` intersects configured names with `omMetadataManager.listTableNames`, skips invalid names with warnings, and fails initialization if none remain. `getTasks` creates a compaction task per valid table. Each task checks `suspended`, calls `CompactDBUtil.compactTable`, increments `numCompactions`, and returns a one-item task result.

Dependencies and integration: Integrated by OM service startup or admin compaction configuration. Uses `CompactDBUtil`, `OzoneManager`, and `OMMetadataManager`.

Risks and test signals: Bad configuration can fail startup when no tables are valid; compaction can affect IO latency. Tests should cover invalid table filtering, all-invalid failure, suspend/resume behavior, per-table task creation, compaction count, and async on-demand compaction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/CompactionService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/DirectoryDeletingService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/DirectoryDeletingService.java

Purpose: Background service that purges FSO deleted directories and moves child files/directories into deletion tables, for both the active object store and optionally deep-clean-enabled snapshots.

Important APIs/types/functions: Extends `AbstractKeyDeletingService`. Important state includes Ratis byte limit, snapshot chain manager, deep-clean flag, reconfigurable deletion thread pool, per-run metrics, and `pathLimitPerTask`. Key methods include `registerReconfigCallbacks`, `updateAndRestart`, `getTasks`, `execTaskCompletion`, `shutdown`, `start`, `optimizeDirDeletesAndSubmitRequest`, `prepareDeleteDirRequest`, `wrapPurgeRequest`, `submitPurgePathsWithBatching`, and `submitPurgeRequest`. Nested `DirDeletingTask` handles AOS or one snapshot.

Control flow and persistence: Each run queues an AOS deletion task and, if configured, one task per snapshot. Tasks skip non-leader states, already deep-cleaned snapshots, unflushed snapshot changes, and AOS work whose previous purge transaction is not flushed. Processing uses `ReclaimableDirFilter` and `ReclaimableKeyFilter`, scans deleted directory entries, discovers subdirectories and subfiles, strips ACLs from moved records, builds `PurgeDirectories` requests under a Ratis size budget, includes expected previous snapshot ID and bucket-name info, and submits through OM Ratis. When all snapshot entries are processed it submits `SetSnapshotProperty` updates for exclusive size deltas and deep-clean flags.

Dependencies and integration: Depends on `KeyManager` pending-deletion scans, snapshot chain utilities, OM locks, Ratis request submission, deletion/performance metrics, reconfiguration callbacks, and protobuf purge request types.

Risks and test signals: Race protection around snapshot chain changes and request size batching is critical. Tests should cover AOS and snapshot paths, deep-clean skip flags, unflushed snapshot gating, reconfiguration restart without deadlock, recursive directory deletion limits, Ratis batch splitting, expected-previous-snapshot validation, exclusive size updates, and retry after failed submit.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/DirectoryDeletingService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/KeyDeletingService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/KeyDeletingService.java

Purpose: Background service that reclaims deleted key blocks through SCM and then purges or updates OM deleted-key metadata, including snapshot deep-cleaning flows.

Important APIs/types/functions: Extends `AbstractKeyDeletingService`. Important state includes `ScmBlockLocationProtocol`, key limit, deleted-key counter, deep-clean flag, snapshot chain manager, Ratis byte limit, and per-run `DeletionStats`. Key methods include `processKeyDeletes`, `submitPurgeKeysRequest`, `getPurgeKeysRequest`, `submitPurgeRequest`, `execTaskCompletion`, `resetMetrics`, `getTasks`, and nested `KeyDeletingTask`.

Control flow and persistence: Tasks run only on leader-ready OM. They process AOS plus optional snapshots, skipping already deep-cleaned snapshots, snapshots whose DB changes are unflushed, snapshots whose directory deep-clean is incomplete, and AOS when the previous purge transaction is not flushed. `processDeletedKeysForStore` filters reclaimable deleted keys and rename entries, validates expected previous snapshot ID, sends non-empty block groups to SCM, treats empty files as successfully deleted without SCM calls, then submits `PurgeKeys` requests. The purge request batches deleted key names, key-version updates, renamed-key deletions, and per-bucket purged byte/namespace deltas under the Ratis byte budget.

Dependencies and integration: Integrates OM `KeyManager`, SCM block deletion, snapshot filters, snapshot chain manager, metrics, tracing, and OM Ratis purge request handling.

Risks and test signals: Block deletion must precede OM purge to avoid orphan blocks, and failed block groups must prevent metadata purge for all versions of that key. Tests should cover empty-file deletion, partial SCM failures, keys-to-modify versions, renamed entries, Ratis splitting, bucket purge size accounting, snapshot deep-clean sequencing after directory cleanup, exclusive size updates, and retry/idempotency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/KeyDeletingService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/MultipartUploadCleanupService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/MultipartUploadCleanupService.java

Purpose: Background service that finds expired incomplete multipart uploads and submits OM requests to abort them.

Important APIs/types/functions: Extends `BackgroundService`. Constructor reads `OZONE_OM_MPU_EXPIRE_THRESHOLD` and `OZONE_OM_MPU_PARTS_CLEANUP_LIMIT_PER_TASK`, stores OM/key manager, creates a random client ID, and initializes counters. Important methods are `getRunCount`, `suspend`, `resume`, `getSubmittedMpuInfoCount`, `getTasks`, and nested `MultipartUploadCleanupTask`.

Control flow and persistence: The task runs only when not suspended and OM leader-ready. It calls `keyManager.getExpiredMultipartUploads(expireThreshold, mpuPartsLimitPerTask)`, counts expired MPUs, builds `MultipartUploadsExpiredAbortRequest` with bucket-grouped expired upload data, wraps it in an OM request of type `AbortExpiredMultiPartUploads`, and submits it through `OzoneManagerRatisUtils`. It increments submitted count after submission attempt; actual metadata deletion is handled by the abort request/response path.

Dependencies and integration: Depends on `KeyManager` MPU scanning, OM config keys, Ratis submission, and S3 multipart abort-expired request handling.

Risks and test signals: Expired uploads may be completed or aborted between scan and request processing, so downstream handling must be idempotent. Tests should cover leader gating, suspension, threshold filtering, per-task part limit, grouped request construction, submission failure retry behavior, and submitted count metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/MultipartUploadCleanupService.java -->
