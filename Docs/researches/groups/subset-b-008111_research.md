# Research Group: subset-b-008111

This grouped report covers Apache Ozone Ozone Manager request tests in the key, S3 multipart, S3 security, S3 tagging, S3 tenant, and security test packages. Each section is source-tree aligned and intended to be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMOpenKeysDeleteRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMOpenKeysDeleteRequest.java

Purpose: verifies `OMOpenKeysDeleteRequest`, the OM background cleanup request that deletes expired open keys from the open-key table cache. The class extends `TestOMKeyRequest` and parameterizes all behavioral tests across `BucketLayout.DEFAULT` and `BucketLayout.FILE_SYSTEM_OPTIMIZED`, so the same cleanup contract is tested for legacy open-key names and FSO open-file names.

Important APIs and types include `OMOpenKeysDeleteRequest.preExecute`, `validateAndUpdateCache`, `DeleteOpenKeysRequest`, `OpenKeyBucket`, `OpenKey`, `OmKeyInfo`, `OMMetrics`, `OMSystemAction.OPEN_KEY_CLEANUP`, and metadata-manager helpers such as `getOpenKeyTable`, `getOpenKey`, and `getOpenFileName`. Helper methods synthesize open keys, add them to the correct table variant, build delete requests from DB key names, and assert table presence through `isExist`.

Control flow: each test creates one or more volumes/buckets, materializes open keys in RocksDB-backed metadata tables, runs `preExecute` to add user info, then calls `validateAndUpdateCache` with a fixed transaction ID. The tests check missing-key deletion, subset deletion across multiple volume/bucket combinations, identical object names with different client IDs, and update-ID filtering where entries newer than the cleanup transaction must remain while equal-or-older entries are deleted.

State and persistence behavior centers on cache deletion markers over the open-key table rather than final batch commit. In DEFAULT layout the DB key is `volume/bucket/key/clientID`; in FSO it is derived from volume ID, bucket ID, parent object ID, file name, and client ID. The request also leaves bucket snapshot used bytes and namespace at zero after cleanup. Metrics tests distinguish submitted open keys from actually deleted keys.

Dependencies and integration points: `OMRequestTestUtils` creates volumes, buckets, open keys, file entries, and optional key-location data. The test relies on `OzoneManager` metrics and audit-message builders from the mocked test harness. It integrates with cleanup-service semantics: stale cleanup input must be idempotent and must not fail if keys were already committed or removed.

Risks covered: deleting by object name without client ID would corrupt concurrent open writes; deleting cache entries with a higher update ID would violate transaction ordering; FSO key-name construction can drift from production metadata paths; audit failures could hide cleanup errors. The explicit failure path spies `updateOpenKeyTableCache` to throw `IOException` and expects `Status.INTERNAL_ERROR` plus failure audit logging.

Test signals: success is `Status.OK`, absent table entries for deleted keys, present entries for kept/newer keys, correct OMMetrics counters, one success audit containing deleted-key counts, and one failure audit on injected cache-update failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMOpenKeysDeleteRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMPrefixAclRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMPrefixAclRequest.java

Purpose: tests prefix ACL request handling for `AddAcl`, `RemoveAcl`, and `SetAcl` OM requests targeting `OzoneObj.ResourceType.PREFIX`. It ensures prefix ACL mutations update both the in-memory `PrefixManagerImpl` prefix tree and the metadata-manager prefix table cache.

Important APIs and types: `OMPrefixAddAclRequest`, `OMPrefixRemoveAclRequest`, `OMPrefixSetAclRequest`, `PrefixManagerImpl`, `OmPrefixInfo`, `OzoneObjInfo`, `OzoneAcl`, and protobuf `AddAclRequest`, `RemoveAclRequest`, and `SetAclRequest`. Helper builders create prefix `OzoneObj` values using the current test volume and bucket, then embed ACL protobufs into `OMRequest` instances.

Control flow: each positive test wires a real `PrefixManagerImpl` into the mocked `OzoneManager`, creates volume/bucket metadata, builds a prefix path with trailing slash, runs request `preExecute`, and calls `validateAndUpdateCache` with monotonically increasing transaction IDs. Add ACL is exercised twice to verify idempotent ACL membership while still refreshing update ID. Remove ACL first removes a non-existent ACL from an existing prefix, then removes the existing ACL and validates prefix deletion, then attempts removal from a non-existent prefix. Set ACL creates or replaces the prefix ACL list and verifies repeated set updates the transaction ID.

State and persistence behavior: success paths read `prefixManager.getPrefixInfo`, `prefixManager.getAcl`, and `omMetadataManager.getPrefixTable().get(prefixObj.getPath())`. Add/set retain a prefix-table row with `name == prefix path` and transaction-aligned `updateID`. Removing the last ACL removes the prefix from both the tree and table, while removing a missing ACL from an existing prefix only updates the `updateID`.

Dependencies and integration points: validates path normalization expected by ACL code. Invalid requests without a trailing slash or with a malformed filesystem path (`/dir1//dir2/`) return `INVALID_PATH_IN_ACL_REQUEST`.

Risks covered: divergence between prefix manager and table cache, non-idempotent duplicate ACL behavior, stale update IDs after no-op ACL changes, and incorrect status for absent prefixes. The tests do not exercise batch commit, audit logs, or ACL authorization; they focus on cache/table mutation semantics.

Test signals: expected statuses are `OK`, `INVALID_PATH_IN_ACL_REQUEST`, and `PREFIX_NOT_FOUND`; ACL lists have exact sizes and entries; removed prefixes return null `OmPrefixInfo` and empty ACL lists.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMPrefixAclRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMSetTimesRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMSetTimesRequest.java

Purpose: verifies `OMKeySetTimesRequest` updates key modification time for the default key layout. It extends `TestOMKeyRequest` and provides reusable hooks overridden by the FSO subclass.

Important APIs and types: `OMKeySetTimesRequest`, protobuf `SetTimesRequest`, `KeyArgs`, `OMClientResponse`, `OMResponse`, and `OMRequestTestUtils.addKeyToTable`. The helper `createSetTimesKeyRequest` embeds volume, bucket, key, mtime, and atime into an `OMRequest` with command type `SetTimes`.

Control flow: `testKeySetTimesRequest` creates the volume/bucket, adds a closed key to the key table, invokes `executeAndReturn(2000)`, then reads the key table and checks `modificationTime == 2000`. It then calls `executeAndReturn(-1)` and asserts the previous mtime remains unchanged, documenting that negative mtime means no modification-time update.

State and persistence behavior: the request uses the key table for the active bucket layout. The test inspects `omMetadataManager.getKeyTable(getBucketLayout()).get(ozoneKey)` after `validateAndUpdateCache`; it does not call response batch persistence, so it validates cache-visible behavior in the request path.

Dependencies and integration points: `preExecute` is called before validation, then the returned request is wrapped in a new `OMKeySetTimesRequest`. `addKeyToTable` uses RATIS replication config and transaction ID `1L`.

Risks covered: accidentally treating `-1` as a literal timestamp, not setting a response, wrong command status, and failure to find the key under the selected bucket layout. The base class does not cover directories; the FSO subclass adds that path.

Test signals: response contains `SetTimesResponse`, status is `OK`, and key table modification time changes only for non-negative mtime.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMSetTimesRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMSetTimesRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMSetTimesRequestWithFSO.java

Purpose: specializes set-times coverage for `BucketLayout.FILE_SYSTEM_OPTIMIZED`, covering both files and directories. It extends `TestOMSetTimesRequest`, overrides key creation and request construction, and adds a directory timestamp test.

Important APIs and types: `OMKeySetTimesRequestWithFSO`, `OMFileRequest.getOMKeyInfoIfExists`, `OzoneFileStatus`, `OmKeyInfo`, `OMRequestTestUtils.addParentsToDirTable`, `addFileToKeyTable`, and `getOzonePathKey`. Constants model `c/d/e/file1` where `c/d/e` is the parent directory and `file1` is the stored leaf name.

Control flow: `addKeyToTable` creates parent directory rows, builds `OmKeyInfo` for `FILE_NAME` with object ID and parent object ID, writes it to the FSO key table, and returns the path-key. `testKeySetTimesRequest` sets mtime on `c/d/e/file1`, verifies `OMFileRequest` resolves a file status, and ensures the stored key name is the leaf `file1`. `testDirSetTimesRequest` changes `keyName` to the parent directory and validates directory status and mtime behavior.

State and persistence behavior: FSO resolution spans directory table and key table. The request must update the `OmKeyInfo` or `OmDirectoryInfo` resolved from path components rather than treating the full key string as the stored file name. Negative mtime again leaves the previous value unchanged.

Dependencies and integration points: uses the same `executeAndReturn` flow from the base class, but wraps requests with `OMKeySetTimesRequestWithFSO` and returns FSO bucket layout. It depends on the metadata manager’s volume and bucket numeric IDs for FSO key construction.

Risks covered: directory timestamp updates can be skipped if request code only searches key table; full path can be incorrectly persisted as file name; parent object IDs can be mishandled; negative mtime can overwrite valid timestamps. The test focuses on cache-visible metadata and not final DB batch mechanics.

Test signals: resolved `OzoneFileStatus` is non-null and is directory/file as expected, mtime equals the positive value after update, remains unchanged after `-1`, and key-table row keeps leaf file name.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMSetTimesRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/package-info.java

Purpose: package descriptor for `org.apache.hadoop.ozone.om.request.key` tests. It documents that the package contains test classes for key requests.

Important APIs and types: no executable APIs, classes, methods, or fields are defined. The only Java declaration is the package statement.

Control flow: none. This file participates only in package-level Javadoc generation and source organization.

State and persistence behavior: none. It does not touch OM metadata tables, caches, metrics, or request classes.

Dependencies and integration points: its value is documentation and package grouping for key-request tests such as open key deletion, prefix ACLs, and set-times request coverage.

Risks and test signals: no runtime risk or direct test signal. Changes here would only affect documentation/package metadata unless the package declaration were made inconsistent with the directory.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/package-info.java

Purpose: package descriptor for `org.apache.hadoop.ozone.om.request` tests. It states that the package contains tests for OM requests.

Important APIs and types: none beyond the Java package declaration. It does not define classes, methods, constants, imports, or annotations.

Control flow: none. The file is passive package documentation.

State and persistence behavior: none. It has no effect on OM request validation, metadata-manager state, RocksDB tables, cache entries, metrics, or audit behavior.

Dependencies and integration points: helps organize package-level generated documentation for the broad OM request test namespace. Child packages provide concrete request tests.

Risks and test signals: only documentation/package naming risk. A wrong package declaration would break compilation, but the current file has no direct executable test signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3ExpiredMultipartUploadsAbortRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3ExpiredMultipartUploadsAbortRequest.java

Purpose: tests `S3ExpiredMultipartUploadsAbortRequest`, the background cleanup request that aborts expired multipart uploads. It is parameterized over DEFAULT and FSO bucket layouts and extends `TestS3MultipartRequest` for OM/multipart helper setup.

Important APIs and types: `S3ExpiredMultipartUploadsAbortRequest`, `MultipartUploadsExpiredAbortRequest`, `ExpiredMultipartUploadsBucket`, `ExpiredMultipartUploadInfo`, `OmMultipartKeyInfo`, `OmMultipartUpload`, `OMMultipartUploadUtils`, `OMMetrics`, `UniqueId`, `BucketLayout`, and multipart initiate/commit request classes. Helpers create real MPU rows with committed parts, create non-existent mock MPU keys, and remove related open keys to simulate orphan state.

Control flow: tests create volumes/buckets, generate MPUs via initiate followed by per-part commits, build an expired-abort request from DB keys, call `preExecute`, and then run `validateAndUpdateCache`. Covered scenarios include missing MPU rows, subset deletion across volume/bucket combinations, update-ID filtering, orphan MPUs whose open keys were already cleaned, and metric accounting.

State and persistence behavior: successful abort removes entries from `multipartInfoTable` and the corresponding MPU open key from the layout-specific open-key table. In FSO, open keys are derived from volume ID, bucket ID, parent ID, file name, and upload ID; `multipartInfoTable` still uses the logical multipart key. The cleanup tolerates absent rows and orphaned open-key rows. Update IDs newer than the request transaction are retained.

Dependencies and integration points: integrates with production multipart initiate and commit request paths to seed realistic multipart state. It uses `OMMultipartUploadUtils.getMultipartOpenKey` to map multipart DB keys back to open-key table rows. The tests model the MPU cleanup service and older orphan conditions referenced around HDDS-9098.

Risks covered: cleanup must be idempotent, must not delete newer transaction data, must not fail on orphaned state, and must correctly count parts aborted. FSO path mapping is high risk because multipart table keys and open-file keys differ.

Test signals: `Status.OK`, expected existence/non-existence in `multipartInfoTable` and open-key table, metric counters for requests/submitted/aborted/parts/failures, and retention of higher-update-ID MPU rows.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3ExpiredMultipartUploadsAbortRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3InitiateMultipartUploadRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3InitiateMultipartUploadRequest.java

Purpose: tests default-layout `S3InitiateMultipartUploadRequest`, including pre-execution mutation, cache updates, error handling, metadata/tag propagation, and ACL inheritance from bucket default ACLs.

Important APIs and types: `S3InitiateMultipartUploadRequest`, `OmMultipartKeyInfo`, `OmKeyInfo`, `OmBucketInfo`, `OzoneAcl`, `OMRequestTestUtils.createInitiateMPURequest`, `getMultipartKey`, `getOpenKeyTable`, and `getMultipartInfoTable`. It inherits helper `doPreExecuteInitiateMPU` from `TestS3MultipartRequest`.

Control flow: `testPreExecute` only asserts that pre-execution adds upload ID and modification time. The success test creates a volume/bucket, sends custom metadata and tags, pre-executes, validates, and then reads the open-key table and multipart-info table for the multipart DB key. Negative tests add only a volume or neither volume nor bucket and expect not-found status with no state created.

State and persistence behavior: success creates an open MPU key in the layout-specific open-key table and a matching `multipartInfoTable` entry. `OmKeyInfo.latestVersionLocations` must be marked multipart, metadata and tags must match request input, creation and modification time must be the pre-execute modification time, and the multipart row upload ID must match the response request ID.

Dependencies and integration points: bucket default ACL inheritance is checked by creating an `OmBucketInfo` with DEFAULT and ACCESS ACLs. The new key must inherit only parent DEFAULT ACLs, converted to ACCESS scope; existing parent ACCESS ACLs must not be inherited.

Risks covered: missing metadata/tag carryover, writing multipart rows on failed volume/bucket lookup, wrong upload ID, timestamps not aligned with pre-execute, and ACL scope confusion.

Test signals: `Status.OK`, `BUCKET_NOT_FOUND`, `VOLUME_NOT_FOUND`, non-null open/multipart table entries on success, null entries on failure, `isMultipartKey == true`, and exact ACL containment/exclusion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3InitiateMultipartUploadRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3InitiateMultipartUploadRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3InitiateMultipartUploadRequestWithFSO.java

Purpose: extends initiate-MPU tests for `BucketLayout.FILE_SYSTEM_OPTIMIZED`. It verifies parent directory creation, FSO open-file key construction, multipart table parent ID, metadata/tag propagation, and default ACL inheritance through generated directories.

Important APIs and types: `S3InitiateMultipartUploadRequestWithFSO`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `OmDirectoryInfo`, `OmMultipartKeyInfo`, `OmKeyInfo`, `UserGroupInformation`, and metadata-manager methods `getOzonePathKey`, `getMultipartKey(volumeId,bucketId,parentId,fileName,uploadId)`, and logical `getMultipartKey(volume,bucket,key,uploadId)`.

Control flow: the success test creates volume/bucket metadata, uses key path `a/b/c/<file>`, pre-executes through FSO helpers, validates the request, then walks the expected `a`, `b`, `c` directory rows. It compares the logical multipart key in `multipartInfoTable` with the FSO open-file multipart key in `openKeyTable`.

State and persistence behavior: request validation creates directory-table entries for missing parents, writes an FSO open MPU file under the resolved parent object ID, and records `parentID` in `OmMultipartKeyInfo`. The stored file name is the leaf file name, not the full path. Metadata/tags and creation/modification times match the pre-executed request.

Dependencies and integration points: overrides `getS3InitiateMultipartUploadReq` to instantiate the FSO request and set a login UGI. ACL inheritance checks that each created directory inherits parent DEFAULT ACLs as DEFAULT ACLs, while the leaf file inherits final parent DEFAULT ACLs converted to ACCESS scope.

Risks covered: wrong split between logical MPU table keys and FSO open-file table keys, missing parent directory creation, incorrect `parentID`, failure to preserve tags/metadata, and ACL inheritance drift across directory levels.

Test signals: `Status.OK`, non-null directory/open/multipart rows, expected directory paths like `parentID/name`, matching parent object IDs, leaf file name equality, timestamp equality, and exact inherited ACL lists.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3InitiateMultipartUploadRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartRequest.java

Purpose: shared base fixture for S3 multipart request unit tests. It builds a mocked `OzoneManager` with real `OmMetadataManagerImpl`, metrics, audit logger, bucket-link resolution, and helper methods for pre-executing initiate, commit-part, abort, and complete MPU requests.

Important APIs and types: `OzoneManager`, `OMMetadataManager`, `OmMetadataManagerImpl`, `OMMetrics`, `AuditLogger`, `OzoneNativeAuthorizer`, `ResolvedBucket`, `OMLayoutVersionManager`, `OMRequestTestUtils`, `KeyValueUtil`, `S3InitiateMultipartUploadRequest`, `S3MultipartUploadCommitPartRequest`, `S3MultipartUploadAbortRequest`, and `S3MultipartUploadCompleteRequest`.

Control flow: `setup` configures a temp OM DB directory, constructs metadata manager and metrics, stubs `getOmMetadataReader`, access authorizer, audit logger, default replication config, bucket-link resolver, layout version manager, and OM config. `stop` unregisters metrics and clears inline mocks. Helper methods create protobuf requests, invoke request-specific `preExecute`, and assert expected mutation such as user info, multipart upload ID, modification time, metadata, and tags.

State and persistence behavior: no domain test state is asserted directly here, but the fixture defines all later tests' table environment. The real metadata manager means helper-created volumes, buckets, keys, open keys, multipart info, deleted table entries, and directory rows behave like OM tables rather than pure mocks.

Dependencies and integration points: request factory methods centralize request subclass selection. Subclasses override methods for FSO variants while reusing higher-level test flows. Bucket-link resolution always maps source and resolved volume/bucket to the same names with DEFAULT layout unless subclass-specific request constructors drive FSO behavior.

Risks covered: base helper assertions catch missing pre-execute mutations early. A misconfigured mock could invalidate many multipart tests, especially audit logging, authorizer state, and layout-version gates.

Test signals: pre-execute assertions on changed `OMRequest`, `hasInitiateMultiPartUploadRequest`, non-empty upload ID, positive modification time, and metadata/tag preservation; cleanup clears metrics/mocks between tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadAbortRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadAbortRequest.java

Purpose: tests default-layout `S3MultipartUploadAbortRequest`, including normal abort, missing multipart upload, orphan multipart-info cleanup, and volume/bucket errors.

Important APIs and types: `S3MultipartUploadAbortRequest`, `S3InitiateMultipartUploadRequest`, `CacheKey`, `CacheValue`, `OMRequestTestUtils`, and metadata manager `getMultipartInfoTable` and `getOpenKeyTable`. Helper hooks (`getKeyName`, `createParentPath`, `getMultipartOpenKey`) are overridden by FSO subclass.

Control flow: the success test creates volume/bucket, optionally creates parent path, initiates an MPU, validates initiate to obtain upload ID, pre-executes abort, validates abort, and asserts both `multipartInfoTable` and open-key table rows are gone. Negative tests build abort requests for non-existent MPU, missing volume, and missing bucket. The orphan test deletes the open-key row via a cache tombstone while keeping multipart info, then aborts.

State and persistence behavior: normal abort removes the logical multipart info row and layout-specific MPU open key. The orphan case confirms abort can succeed with `OmKeyInfo` absent in open-key table, cleaning multipart metadata without requiring the open key. Missing volume/bucket or upload must not create or delete unrelated state.

Dependencies and integration points: relies on initiate request to seed legitimate multipart state. The orphan scenario models interaction with `OpenKeyCleanupService`, which may remove open keys before MPU abort cleanup.

Risks covered: abort failing when open-key state is already gone, leaving dangling multipart rows, confusing missing MPU with missing key, and layout-specific open-key name errors. Default variant has no parent hierarchy.

Test signals: expected statuses are `OK`, `NO_SUCH_MULTIPART_UPLOAD_ERROR`, `VOLUME_NOT_FOUND`, and `BUCKET_NOT_FOUND`; table reads return null after successful or orphan abort.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadAbortRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadAbortRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadAbortRequestWithFSO.java

Purpose: adapts the abort-MPU tests to FSO layout. It inherits all behavioral tests from `TestS3MultipartUploadAbortRequest` and changes only request classes and key derivation.

Important APIs and types: `S3MultipartUploadAbortRequestWithFSO`, `S3InitiateMultipartUploadRequestWithFSO`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `OMRequestTestUtils.addParentsToDirTable`, `StringUtils.substringAfter`, `getOpenFileName`-style multipart key construction through metadata manager, and `UserGroupInformation`.

Control flow: inherited tests call overridden hooks. `getKeyName` returns `a/b/c/<uuid>`. `createParentPath` creates the directory hierarchy and stores `parentID`. `getMultipartOpenKey` strips the configured directory prefix, resolves volume and bucket IDs, and builds the FSO multipart open-file key from numeric IDs, parent ID, file name, and upload ID.

State and persistence behavior: logical `multipartInfoTable` rows still use volume/bucket/full-key/upload ID, while open-key table rows use FSO identity. The parent ID captured during directory creation is essential for locating the MPU open key during abort validation.

Dependencies and integration points: mirrors production FSO request subclasses and user context setup. It depends on the base class to seed and validate MPU state and on `OMRequestTestUtils` to make parent directories.

Risks covered: incorrect FSO open-key lookup during abort, mismatched parent IDs, and failure to delete FSO open-file rows. The class is intentionally small but important because inherited tests exercise success, missing, and orphan paths under FSO.

Test signals: inherited assertions pass with `BucketLayout.FILE_SYSTEM_OPTIMIZED`, including null multipart/open table rows after abort and correct error statuses for missing state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadAbortRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadCommitPartRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadCommitPartRequest.java

Purpose: tests default-layout `S3MultipartUploadCommitPartRequest`, including successful part commit, missing MPU/key/bucket errors, overwrites, uncommitted block deletion, and empty-part handling.

Important APIs and types: `S3MultipartUploadCommitPartRequest`, `S3MultipartUploadCommitPartResponse`, `S3InitiateMultipartUploadRequest`, `OmMultipartKeyInfo`, `PartKeyInfo`, `OmKeyInfo`, `RepeatedOmKeyInfo`, `OmKeyLocationInfo`, protobuf `KeyLocation`, `RatisReplicationConfig`, and `Time`.

Control flow: success creates volume/bucket, initiates MPU, creates a part open key, pre-executes commit with part number 1, validates, then checks multipart info and open-key tables. Negative tests skip creating MPU or open part key or bucket and verify the expected error. Overwrite tests first commit a part, then commit the same part number again with different client ID and block locations. Uncommitted-block tests create an open part key with more allocated locations than committed locations.

State and persistence behavior: commit adds/updates a `PartKeyInfo` in `multipartInfoTable`, keeps the MPU open key marked multipart, and removes the individual part open key. When overwriting a part, the response carries old part key data in `getKeyToDelete`. When allocated blocks exceed committed blocks, the response carries only uncommitted locations for deletion. Combining overwrite with uncommitted blocks returns two deletion entries. Empty part commits intentionally do not return a delete map for uncommitted blocks.

Dependencies and integration points: uses base initiate/commit preExecute helpers and `OMRequestTestUtils.addKeyToTable` to simulate data upload through key-create before commit. `getKeyLocation` creates deterministic block IDs for assertions.

Risks covered: block leak on overwrite or partial commit, accidental deletion for empty parts, wrong status when parent/key state is absent, and failure to remove part open keys. FSO subclass reuses these tests with different key naming.

Test signals: statuses `OK`, `NO_SUCH_MULTIPART_UPLOAD_ERROR`, `KEY_NOT_FOUND` or `DIRECTORY_NOT_FOUND` for FSO, and `BUCKET_NOT_FOUND`; table sizes and null/present rows; equality of committed block lists; deletion-map size and location counts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadCommitPartRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadCommitPartRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadCommitPartRequestWithFSO.java

Purpose: adapts commit-part coverage to FSO layout by overriding request factories, parent-path creation, and open-key derivation while inheriting the comprehensive commit-part tests from the default class.

Important APIs and types: `S3MultipartUploadCommitPartRequestWithFSO`, `S3InitiateMultipartUploadRequestWithFSO`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `OmKeyInfo`, `OmKeyLocationInfoGroup`, `OzoneFSUtils`, `StringUtils`, `OMRequestTestUtils.addFileToKeyTable`, and metadata manager `getOpenFileName` and FSO multipart key helpers.

Control flow: inherited tests create keys under `a/b/c/<uuid>`. `createParentPath` creates parent directories and stores `parentID`. Overridden `addKeyToOpenKeyTable` builds an `OmKeyInfo` with parent/object IDs and optional location list, stores it in the FSO open-file table, and returns the FSO open-file key when needed. Request factory overrides instantiate FSO initiate and commit classes and set current-user UGI.

State and persistence behavior: part open keys and MPU open keys are addressed by numeric volume ID, bucket ID, parent ID, file name, and client ID or upload ID. The logical multipart-info row remains keyed by volume/bucket/full key/upload ID. The same inherited assertions validate deletion of part open keys, retained MPU open key, and multipart part map updates under FSO identity.

Dependencies and integration points: custom `doPreExecuteInitiateMPU` ensures FSO pre-execution assertions still hold. `OzoneFSUtils.getFileName` and `StringUtils.substringAfter` are path-splitting dependencies.

Risks covered: storing full paths as file names, wrong parent ID for committed parts, mismatched logical versus FSO keys, and broken inherited block deletion behavior under FSO. The class also exposes a risk if fixed `dirName` state and `parentID` are reused incorrectly across tests.

Test signals: inherited success/error/deletion-map assertions pass with FSO bucket layout and FSO key construction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadCommitPartRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadCompleteRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadCompleteRequest.java

Purpose: tests default-layout `S3MultipartUploadCompleteRequest`, from pre-execution through final key-table materialization, multipart/open cleanup, overwrite accounting, invalid part ordering, and not-found statuses.

Important APIs and types: `S3MultipartUploadCompleteRequest`, `S3MultipartUploadCommitPartRequest`, `S3InitiateMultipartUploadRequest`, `BatchOperation`, `Table`, `CacheKey`, `RepeatedOmKeyInfo`, `OmBucketInfo`, protobuf `Part`, `OzoneConsts.ETAG`, and metadata tables for open keys, multipart info, closed keys, deleted keys, and buckets.

Control flow: success helper initiates MPU with metadata/tags, commits one part, extracts the ETag from commit request metadata, builds a complete request with a matching part, validates, then explicitly calls `omClientResponse.checkAndUpdateDB` in a batch and commits it. The test repeats the whole flow for the same key with different metadata/tags to exercise overwrite. Separate tests submit unordered parts, missing volume, missing bucket, and no-such upload.

State and persistence behavior: successful complete removes the multipart open key and multipart-info row, inserts the completed object into the key table with multipart locations, preserves metadata and tags from initiate, and updates bucket used namespace. On overwrite, the old key is represented in the deleted table; `checkDeleteTableCount` validates deleted-key accounting. The explicit batch commit means this class validates response persistence as well as cache updates.

Dependencies and integration points: commit-part request must produce the ETag consumed by complete. Bucket namespace expectations are layout-dependent through `getNamespaceCount`, overridden by FSO. `getPartName` uses production static part-name construction for invalid-order test setup.

Risks covered: completing with wrong part order, losing metadata/tags, leaving stale multipart/open rows, failing overwrite cleanup, incorrect namespace accounting, and not applying response DB updates. Empty/missing MPU paths must return precise statuses.

Test signals: statuses `OK`, `INVALID_PART_ORDER`, `VOLUME_NOT_FOUND`, `BUCKET_NOT_FOUND`, and `NO_SUCH_MULTIPART_UPLOAD_ERROR`; null open/multipart rows; non-null closed key row marked multipart; deleted-table count after overwrite; bucket used namespace equals expected.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadCompleteRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadCompleteRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadCompleteRequestWithFSO.java

Purpose: specializes complete-MPU tests for FSO layout. It inherits default complete-MPU scenarios and overrides key generation, parent directory handling, final key-table lookup, request factories, and namespace expectations.

Important APIs and types: `S3MultipartUploadCompleteRequestWithFSO`, `S3MultipartUploadCommitPartRequestWithFSO`, `S3InitiateMultipartUploadRequestWithFSO`, `OMFileRequest.getParentID`, `OzoneFSUtils`, `OmKeyInfo`, `OmKeyLocationInfoGroup`, `OMRequestTestUtils.addFileToKeyTable`, and FSO metadata-manager path-key methods.

Control flow: `getKeyName` returns a random parent directory plus `a/b/c/file1`. `addKeyToTable` resolves/creates the parent directory through `getParentID`, builds open-file `OmKeyInfo` with leaf file name and parent/object IDs, and writes it to the FSO open-file table. Inherited tests then initiate, commit, and complete MPU. `getOzoneDBKey` resolves the final key-table row using volume ID, bucket ID, parent ID, and file name.

State and persistence behavior: final completed object lands in the FSO key table under an ozone path key, not the legacy ozone key. Namespace count is expected to be `5L`, reflecting the file plus parent directories created by the FSO workflow. Open multipart and multipart-info cleanup still occurs through inherited assertions.

Dependencies and integration points: request factory overrides instantiate FSO subclasses and set current-user UGI. Parent resolution depends on `OMFileRequest.getParentID` after directories are created by initiate or helper setup.

Risks covered: wrong final key table key, lost parent ID, full path stored as file name, namespace undercount for created parent directories, and mismatch between FSO commit and complete request classes.

Test signals: inherited complete-MPU statuses and table assertions, plus FSO namespace count `5L` and final closed key lookup via `getOzonePathKey`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartUploadCompleteRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/package-info.java

Purpose: package descriptor for `org.apache.hadoop.ozone.om.request.s3.multipart` tests. It documents that the package contains test classes for S3 MPU requests.

Important APIs and types: none beyond the package declaration. No classes or methods are defined.

Control flow: none; the file is passive package-level Javadoc.

State and persistence behavior: none. It does not interact with multipart tables, open-key tables, key tables, metrics, audit logs, or request validation.

Dependencies and integration points: provides package documentation for the multipart test suite covering initiate, commit-part, complete, abort, and expired cleanup requests.

Risks and test signals: no executable behavior or direct test signal. The main risk is documentation/package mismatch causing compile or Javadoc confusion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/security/TestS3GetSecretRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/security/TestS3GetSecretRequest.java

Purpose: tests `S3GetSecretRequest` and related S3 secret lifecycle behavior, including secret creation, repeated fetches, revocation, admin authorization, secret-manager failure, transaction-index caching, and tenant access-ID integration.

Important APIs and types: `S3GetSecretRequest`, `S3RevokeSecretRequest`, `S3GetSecretResponse`, `S3RevokeSecretResponse`, `S3SecretLockedManager`, `S3SecretManagerImpl`, `S3SecretCache`, `S3SecretValue`, `S3Secret`, `OMMultiTenantManager`, `OMTenantCreateRequest`, `OMTenantAssignUserAccessIdRequest`, `OmDBAccessIdInfo`, `AuthorizerLockImpl`, Kerberos `UserGroupInformation`, and Hadoop RPC `Server.Call`.

Control flow: setup configures Kerberos name rules, creates Alice and Carol UGIs, installs Alice as current RPC user, builds a real metadata manager and real locked S3 secret manager, and mocks multi-tenant manager behavior. Helper `processSuccessSecretRequest` wraps original and pre-executed requests, calls `validateAndUpdateCache`, and checks response content depending on whether a new secret is expected. `processFailedSecretRequest` verifies unauthorized pre-execute rejects with `USER_MISMATCH`.

State and persistence behavior: successful first fetch creates a secret in metadata/cache and returns it; repeated fetch for an existing secret returns null `S3SecretValue` to avoid overwriting existing DB entry. Cache entries record transaction log index. Revocation removes the old secret; a later get creates a different secret. Tenant test creates tenant metadata, assigns Bob access ID, creates a secret during assignment, then verifies `GetS3Secret` for that access ID returns success but no replacement secret value.

Dependencies and integration points: exercises S3 admin and Ozone admin distinctions, current RPC user, Kerberos short names, tenant manager access-ID mapping, layout-version manager for tenant feature checks, and secret manager locking. It also tests injected `IOException` from `storeSecret`.

Risks covered: privilege escalation for another user's secret, Ozone admin incorrectly acting as S3 admin, stale secret reuse after revocation, cache transaction index loss, overwriting tenant-assigned secrets, and unhandled secret-manager failures.

Test signals: instance checks for response classes, `OMResponse.success`, returned or null `S3SecretValue`, equality of Kerberos IDs, non-null generated AWS secret, cache transaction indexes, changed secret after revoke, `USER_MISMATCH` exceptions, and thrown exception on failing secret manager.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/security/TestS3GetSecretRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/security/TestS3SecretRequestHelper.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/security/TestS3SecretRequestHelper.java

Purpose: tests `S3SecretRequestHelper.getOrCreateUgi`, the helper that resolves a `UserGroupInformation` for S3 secret requests from either the current RPC call or an access ID string.

Important APIs and types: `S3SecretRequestHelper`, `Server.getCurCall`, `ExternalCall`, `UserGroupInformation`, `KerberosName`, and SASL `KERBEROS` auth method. A private `StubCall` extends `ExternalCall<String>` and returns a predefined UGI.

Control flow: setup installs Kerberos name rules and creates expected/test remote users for `access/server@EXAMPLE.COM` with Kerberos auth. One test sets current RPC call to `StubCall` and checks helper returns equivalent UGI. Another leaves call absent and checks helper creates UGI from access ID. A third passes null and expects null. Teardown clears `Server.getCurCall`.

State and persistence behavior: no OM metadata state. The only mutable global state is the thread-local current RPC call and Kerberos name rules.

Dependencies and integration points: supports S3 secret request authorization paths that need a UGI for tenant access IDs or current callers. Correct auth method preservation matters for downstream admin checks and audit identity.

Risks covered: null access IDs, leaking current RPC call between tests, ignoring current caller when available, and creating UGI with wrong user/auth method.

Test signals: equality of user name and authentication method, and null result for null access ID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/security/TestS3SecretRequestHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tagging/TestS3DeleteObjectTaggingRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tagging/TestS3DeleteObjectTaggingRequest.java

Purpose: tests default-layout `S3DeleteObjectTaggingRequest`, which removes all tags from an existing key without changing other key identity fields.

Important APIs and types: `S3DeleteObjectTaggingRequest`, protobuf `DeleteObjectTaggingRequest`, `KeyArgs`, `OMResponse`, `Type.DeleteObjectTagging`, `OmKeyInfo`, `RatisReplicationConfig`, and `OMRequestTestUtils`.

Control flow: pre-execute test builds a delete-tagging request and verifies the request retains volume, bucket, key, and tags list while not setting modification time. Success test creates volume/bucket, inserts a key with random tags, pre-executes, validates, and reads the key table. Negative tests cover missing volume, missing bucket, and missing key.

State and persistence behavior: success mutates the key-table cache entry so `OmKeyInfo.getTags()` becomes empty while volume, bucket, and key name remain unchanged. The request does not set modification time during pre-execute.

Dependencies and integration points: extends `TestOMKeyRequest` for common OM metadata fixture. Uses key-table lookup via `omMetadataManager.getOzoneKey` and supports bucket layout override by FSO subclass.

Risks covered: deleting the key instead of tags, changing modification time unexpectedly, writing tags on failed lookup, returning the wrong command type, or losing key identity fields.

Test signals: `DeleteObjectTaggingResponse` present, status `OK`, command type `DeleteObjectTagging`, empty tags after success, and statuses `VOLUME_NOT_FOUND`, `BUCKET_NOT_FOUND`, and `KEY_NOT_FOUND` for failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tagging/TestS3DeleteObjectTaggingRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tagging/TestS3DeleteObjectTaggingRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tagging/TestS3DeleteObjectTaggingRequestWithFSO.java

Purpose: adapts delete-object-tagging tests to FSO buckets. It inherits default delete-tagging tests and overrides key insertion, bucket layout, and request class.

Important APIs and types: `S3DeleteObjectTaggingRequestWithFSO`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `OmKeyInfo`, `OMRequestTestUtils.addParentsToDirTable`, `addFileToKeyTable`, `getOzonePathKey`, and `RatisReplicationConfig`.

Control flow: `addKeyToTable` changes the test `keyName` to `c/d/e/file1`, creates parent directories, builds an `OmKeyInfo` for leaf file name `file1` with parent/object IDs and tags, writes it to the FSO key table, and returns the FSO path key. Inherited tests then delete tags and assert state.

State and persistence behavior: the key table entry is addressed by volume ID, bucket ID, parent object ID, and file name. The request should clear tags for the FSO file row while preserving file identity and parent relationship.

Dependencies and integration points: the subclass uses the FSO production request class and returns FSO bucket layout, so inherited missing-volume/bucket/key tests exercise FSO validation path.

Risks covered: full path versus file-name mismatch, wrong parent ID lookup, and delete-tagging support divergence between default and FSO layouts.

Test signals: inherited success and error status assertions pass; after success the FSO key row exists and has zero tags.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tagging/TestS3DeleteObjectTaggingRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tagging/TestS3PutObjectTaggingRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tagging/TestS3PutObjectTaggingRequest.java

Purpose: tests default-layout `S3PutObjectTaggingRequest`, which replaces object tags on an existing key. It covers pre-execute stability, success, empty tag set, and not-found errors.

Important APIs and types: `S3PutObjectTaggingRequest`, protobuf `PutObjectTaggingRequest`, `KeyArgs`, `KeyValueUtil`, `OMResponse`, `Type.PutObjectTagging`, `OmKeyInfo`, `RatisReplicationConfig`, and `OMRequestTestUtils`.

Control flow: success creates volume/bucket, inserts an untagged key, builds a put-tagging request with random tags, pre-executes, validates, and reads the key table. The empty-tag test sends an empty tag map and expects success with an empty stored tag set. Negative tests cover absent volume, bucket, and key.

State and persistence behavior: success updates the key-table cache entry's tag map to exactly match request tags while preserving volume, bucket, and key name. Pre-execute must not set modification time for object tagging and must not alter key args. Empty tag input is a valid replacement, not a validation failure.

Dependencies and integration points: extends `TestOMKeyRequest` and uses `KeyValueUtil.toProtobuf` when building request tags. The FSO subclass reuses most tests by overriding table insertion and request class.

Risks covered: accidental mtime mutation, partial tag merge instead of replacement, rejecting empty tag sets, updating state on not-found paths, and losing key identity fields.

Test signals: `PutObjectTaggingResponse` present, status `OK`, command type `PutObjectTagging`, exact tag key/value matches, empty tag success, and statuses `VOLUME_NOT_FOUND`, `BUCKET_NOT_FOUND`, and `KEY_NOT_FOUND`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tagging/TestS3PutObjectTaggingRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tagging/TestS3PutObjectTaggingRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tagging/TestS3PutObjectTaggingRequestWithFSO.java

Purpose: adapts put-object-tagging coverage to FSO layout and adds a directory-specific unsupported-operation test.

Important APIs and types: `S3PutObjectTaggingRequestWithFSO`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `OmKeyInfo`, `OMRequestTestUtils.addParentsToDirTable`, `addFileToKeyTable`, `getOzonePathKey`, and `RatisReplicationConfig`.

Control flow: inherited tests use `addKeyToTable` to create `c/d/e/file1` in FSO key table with parent directories and leaf file name. `testValidateAndUpdateCachePutObjectTaggingToDir` creates the file/parents, then sends a put-tagging request against the parent directory path `c/d/e` and validates the response.

State and persistence behavior: file tagging updates the FSO key table row keyed by numeric parent identity. Directory tagging is rejected with `NOT_SUPPORTED_OPERATION`; the request must not treat a directory entry as a taggable object key.

Dependencies and integration points: returns the FSO request subclass and FSO bucket layout so default success and not-found tests run through FSO validation. Directory resolution depends on the parent rows created by `addParentsToDirTable`.

Risks covered: allowing tags on directories, resolving full path incorrectly, wrong file name in `OmKeyInfo`, and divergence in tag semantics between FSO and default layout.

Test signals: inherited put-tagging success/error assertions plus explicit `Status.NOT_SUPPORTED_OPERATION` when tagging a directory path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tagging/TestS3PutObjectTaggingRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tenant/TestOMTenantCreateRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tenant/TestOMTenantCreateRequest.java

Purpose: tests `OMTenantCreateRequest`, including happy-path tenant/volume creation, existing-volume force flag behavior, S3-compliant tenant ID validation under strict S3 mode, non-strict acceptance, and ACL-denied pre-execute behavior.

Important APIs and types: `OMTenantCreateRequest`, `CreateTenantRequest`, `OMMultiTenantManager`, `TenantOp`, `AuthorizerLock`, `OMLayoutVersionManager`, `OMRequestTestUtils.createTenantRequest`, `OMException`, `Status`, `OzoneObj`, and `IAccessAuthorizer`.

Control flow: setup creates a mocked `OzoneManager`, real metadata manager, metrics, layout version manager that allows features, audit logger, and mocked multi-tenant manager with no-op admin/authorizer/cache operations. Happy path spies the request to return username, pre-executes, validates, and checks response/table. Existing-volume test seeds volume table, verifies `preExecute` throws when force is false, succeeds when force is true, then crafts a post-preExecute request with force false to test validate-time `VOLUME_ALREADY_EXISTS`.

State and persistence behavior: successful tenant creation creates a volume table entry for the tenant ID and returns `CreateTenantResponse`. Existing volume with force true allows tenant creation over the pre-existing volume. Strict S3 validation happens during pre-execute via volume-name constraints.

Dependencies and integration points: integrates with multi-tenant admin checks, authorizer locks, Ranger/tenant operations, OM layout feature gating, audit logging, max user volume count, and ACL checks. ACL test subclasses `checkAcls` to throw `PERMISSION_DENIED` when ACLs are enabled.

Risks covered: bypassing existing-volume safeguards, rejecting valid S3 names, accepting invalid names in strict mode, ignoring ACL denial, and failing to create required volume state. The tests mock external tenant/Ranger operations rather than validating side effects there.

Test signals: response contains `CreateTenantResponse`, status `OK` or `VOLUME_ALREADY_EXISTS`, volume table entry exists after success, exception result `VOLUME_ALREADY_EXISTS` or `PERMISSION_DENIED`, and strict-mode invalid-name message.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tenant/TestOMTenantCreateRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tenant/TestOMTenantDeleteRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tenant/TestOMTenantDeleteRequest.java

Purpose: tests ACL-denied pre-execute behavior for `OMTenantDeleteRequest`. The class focuses on authorization failure rather than full tenant deletion success.

Important APIs and types: `OMTenantDeleteRequest`, `OMMultiTenantManager`, `OzoneTenant`, `OmDBTenantState`, `TenantOp`, `AuthorizerLock`, `OMRequestTestUtils.deleteTenantRequest`, `OMException`, `OzoneObj`, and `IAccessAuthorizer`.

Control flow: setup configures a mocked `OzoneManager`, real metadata manager and metrics, layout version manager, audit logger, and multi-tenant manager that reports tenants empty and returns an `OzoneTenant`. The test enables ACLs, creates a tenant state row in the tenant-state table, builds a delete request, and instantiates an anonymous `OMTenantDeleteRequest` whose `checkAcls` throws `PERMISSION_DENIED`. It then asserts `preExecute` throws that result.

State and persistence behavior: the test seeds `tenantStateTable` with `OmDBTenantState` so pre-execute has realistic tenant metadata available. Because the failure happens during pre-execute, no deletion cache/table mutation should occur.

Dependencies and integration points: models the interaction among tenant metadata, multi-tenant manager emptiness checks, authorizer locks, tenant operations, and OM ACL enforcement. External authorizer/cache operations are mocked as no-op.

Risks covered: tenant deletion bypassing ACL checks when ACLs are enabled, or permission failures being converted to wrong exception types. It does not validate successful delete cleanup or non-empty tenant errors.

Test signals: `assertThrows(OMException.class)` from `preExecute` and result code `PERMISSION_DENIED`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tenant/TestOMTenantDeleteRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tenant/TestSetRangerServiceVersionRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tenant/TestSetRangerServiceVersionRequest.java

Purpose: tests `OMSetRangerServiceVersionRequest`, the OM request that records the Ranger service version synchronized to OM.

Important APIs and types: `OMSetRangerServiceVersionRequest`, `OMSetRangerServiceVersionResponse`, protobuf `SetRangerServiceVersionRequest`, `Type.SetRangerServiceVersion`, `OMPerformanceMetrics`, `OMLayoutVersionManager`, and `OmMetadataManagerImpl`.

Control flow: setup creates a mocked `OzoneManager`, layout version manager, real metadata manager, and mocked performance metrics. The test builds an OM request with Ranger service version `10L`, wraps it through `preExecute`, calls `validateAndUpdateCache` with transaction index `1`, casts the response, and reads the new service version string.

State and persistence behavior: the test validates response-level cache/update behavior by checking `getNewServiceVersion`; it does not inspect a DB table directly or batch-commit a response. The request is expected to store or expose the service version for later persistence by the response path.

Dependencies and integration points: integrates with OM metadata manager and performance metrics. It is part of the S3 tenant package because Ranger service version relates to tenant/Ranger synchronization.

Risks covered: request not preserving the provided long version, response class mismatch, and layout/metadata setup regressions causing validation failure.

Test signals: response is an `OMSetRangerServiceVersionResponse` and `Long.parseLong(getNewServiceVersion()) == 10L`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tenant/TestSetRangerServiceVersionRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/security/TestOMDelegationTokenRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/security/TestOMDelegationTokenRequest.java

Purpose: base fixture for OM delegation-token request tests. It is not itself a test method container beyond setup/teardown, but provides common mocked OM and real metadata manager state to subclasses in the security request package.

Important APIs and types: `OzoneManager`, `OMMetadataManager`, `OmMetadataManagerImpl`, `ConfigurationSource`, `OzoneConfiguration`, `OZONE_OM_DB_DIRS`, JUnit `@TempDir`, and Mockito `framework().clearInlineMocks`.

Control flow: `setup` creates a mocked `OzoneManager`, constructs an `OzoneConfiguration` with OM DB dir pointing to a temp folder, builds `OmMetadataManagerImpl`, and stubs `ozoneManager.getMetadataManager()`. `stop` clears inline Mockito mocks.

State and persistence behavior: creates an isolated real OM metadata store rooted under the JUnit temp directory. Subclasses can use the metadata manager to validate delegation token persistence or cache behavior without sharing state across tests.

Dependencies and integration points: supports request tests for OM delegation token operations by centralizing metadata-store setup. It does not create metrics, audit logger, security managers, or token-specific state; subclasses are expected to add those as needed.

Risks covered: mostly fixture risk: wrong DB directory setup or stale mocks would make delegation-token tests flaky. There are no direct assertions in this file.

Test signals: no direct test methods; indirect signal is successful setup/teardown for subclasses that extend this fixture.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/security/TestOMDelegationTokenRequest.java -->
