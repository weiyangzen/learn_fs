# subset-b-008109 research

Grouped research report for 20 Apache Ozone OM request test sources. Each file section preserves the source path in its title and is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/TestOMClientRequestWithUserInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/TestOMClientRequestWithUserInfo.java

## Purpose
Tests how `OMClientRequest` subclasses attach and reconstruct request user information for both Hadoop RPC and gRPC/S3 credential transports. The class focuses on server-side identity propagation rather than metadata mutation.

## Important APIs, Types, And Functions
- `TestOMClientRequestWithUserInfo` uses a mocked `OzoneManager`, real temporary `OmMetadataManagerImpl`, `OMMetrics`, and `OzoneConfiguration`.
- `testUserInfoInCaseOfHadoopTransport` exercises `OMBucketCreateRequest.preExecute`, `getRemoteAddress`, `createUGI`, and `getHostName`.
- `testUserInfoInCaseOfGrpcTransport` exercises `OMClientRequest.getUserInfo` through an `OMKeyCommitRequest` built from S3 credentials.
- Static helpers from `OMRequestTestUtils` build bucket create requests and S3 credential requests.

## Control Flow
Setup creates a temporary OM DB, wires metrics and configuration, mocks `OmConfig.isFileSystemPathEnabled` as false, and supplies a minimal `OMLayoutVersionManager`. The Hadoop transport test statically mocks `Server.getRemoteUser`, `Server.getRemoteIp`, and `Server.getRemoteAddress`, builds a create-bucket `OMRequest`, asserts it initially lacks `UserInfo`, calls `preExecute`, then reconstructs UGI, host name, and address from the modified request. The gRPC test statically mocks `Context.key("CLIENT_HOSTNAME")` and `Context.key("CLIENT_IP_ADDRESS")`, builds an S3-signed request, and asserts `getUserInfo` combines gRPC host/IP data with the S3 access ID.

## State And Persistence Behavior
The test creates an `OmMetadataManagerImpl` only to satisfy request preExecute dependencies. It does not validate persisted rows. The observable state is the immutable protobuf request: preExecute returns a new request with `UserInfo`, preserving the original request as user-info-free.

## Dependencies And Integration Points
This test binds identity capture to Hadoop IPC `Server`, gRPC `Context`, S3 credential parsing, `OMBucketCreateRequest`, `OMKeyCommitRequest`, `BucketLayout`, and OM config/version manager plumbing. Static mocking is central and is cleared by try-with-resources.

## Risks And Edge Cases
The coverage is sensitive to static context key names and to request subclasses that call `getUserInfo`. It does not cover missing remote user/IP, malformed IP strings, or simultaneous Hadoop and gRPC metadata. A regression could silently break auditing if preExecute stops attaching user info or if S3 access ID stops mapping to user name.

## Test Signals
Positive signals are `hasUserInfo`, matching host address, matching Hadoop username, matching host name, and matching gRPC/S3 fields. The tests are unit-level and rely on mocks rather than a real transport stack.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/TestOMClientRequestWithUserInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestBucketRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestBucketRequest.java

## Purpose
Provides the shared JUnit fixture for bucket request tests. It centralizes mocked `OzoneManager` wiring, temporary OM metadata storage, metrics, audit logging, replication validation, default bucket layout, layout version manager, and bucket-link resolution.

## Important APIs, Types, And Functions
- `setup` creates `OzoneConfiguration`, `OMMetrics`, `OmMetadataManagerImpl`, and the main `OzoneManager` mock behavior.
- `setupReplicationConfigValidation` prepares replication config validation for bucket create/set-property paths.
- `ResolvedBucket` is returned from `ozoneManager.resolveBucketLink(Pair)` with default layout.
- `stop` unregisters metrics and clears Mockito inline mocks.

## Control Flow
Each subclass gets a temporary OM DB directory. The fixture configures `OZONE_OM_DB_DIRS`, returns `OmConfig` from configuration, sets `getOMDefaultBucketLayout` to the default configured layout, attaches a no-op audit logger, and mocks `OMLayoutVersionManager.getMetadataLayoutVersion`. Bucket link resolution returns the original pair as the resolved target.

## State And Persistence Behavior
The class creates a real metadata manager, so subclass tests exercise in-memory/cache-backed OM tables rather than pure mocks. The state includes bucket, volume, user, multipart, and other OM metadata tables depending on the subclass helper calls. Metrics are real and unregistered after each test.

## Dependencies And Integration Points
Subclasses depend on this fixture for `ozoneManager`, `omMetrics`, `omMetadataManager`, and `auditLogger`. It integrates with `OMRequestTestUtils`, audit interfaces, layout version checks, replication validation, and symlink bucket resolution.

## Risks And Edge Cases
Because the fixture resolves all links to the input bucket and default layout, tests that need link-specific semantics must override or construct explicit link rows. The default bucket layout mock can hide config-dependent behavior unless subclasses override it, as the FSO create/delete tests do.

## Test Signals
The fixture itself has no assertions. Its correctness is signaled indirectly by subclass tests that can call `preExecute` and `validateAndUpdateCache` without null pointer failures and with real table/metric effects.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestBucketRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestOMBucketCreateRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestOMBucketCreateRequest.java

## Purpose
Tests `OMBucketCreateRequest` for normal bucket creation, preExecute mutation, strict S3 bucket naming, ACL authorization failure, default replication validation, quota enforcement, object-store versus FSO layout naming rules, and client ACL handling.

## Important APIs, Types, And Functions
- `doPreExecute` inserts a volume, builds `CreateBucketRequest`, calls `OMBucketCreateRequest.preExecute`, and verifies preserved fields plus new creation time.
- `doValidateAndUpdateCache` calls `validateAndUpdateCache`, checks `bucketTable`, and verifies response status.
- `verifySuccessCreateBucketResponse` validates the protobuf response envelope.
- `addCreateVolumeToTable` seeds `volumeTable` using `OmVolumeArgs`.
- Tests use `OmBucketInfo`, `OmVolumeArgs`, `BucketLayout`, `DefaultReplicationConfig`, `ECReplicationConfig`, `OMException`, `OzoneAcl`, and `UserGroupInformation`.

## Control Flow
The class follows a preExecute then validateAndUpdateCache pattern. Successful tests add the volume first, preExecute the request, instantiate a fresh request object from the modified protobuf, set the current UGI, and validate cache update. Failure tests omit the volume, duplicate the bucket, simulate ACL denial by overriding `checkAcls`, use invalid EC replication, exceed configured maximum bucket count, or request invalid quotas/names.

## State And Persistence Behavior
Successful validation writes an `OmBucketInfo` entry to `bucketTable` under `omMetadataManager.getBucketKey(volume, bucket)`. The persisted bucket is compared against the request-derived `OmBucketInfo`: creation/modification time, ACLs, version flag, storage type, metadata, and encryption key info. Volume quota tests seed `volumeTable` with constrained quota and assert request rejection when bucket quota exceeds volume quota or when a bucket lacks quota under a quota-enabled volume. `ignoreClientACLs` toggles whether client-provided ACLs remain in the persisted bucket.

## Dependencies And Integration Points
The test integrates with the base bucket fixture, `OMRequestTestUtils` builders and DB seeders, OM config keys such as `OZONE_OM_MAX_BUCKET` and `OZONE_OM_NAMESPACE_STRICT_S3`, bucket layout conversion, ACL authorizer types, and replication config validation. It also validates that object-store buckets reject non-S3-compliant names even when strict S3 namespace is disabled, while helper coverage allows such names for explicitly FSO buckets.

## Risks And Edge Cases
High-risk areas are policy interactions: strict S3 versus layout-specific naming, bucket quota versus volume quota, default replication validation, ACL bypass through `ignoreClientACLs`, and bucket-count limits. The test uses random UUID names heavily, so deterministic failure reproduction relies on assertion messages/statuses rather than fixed names.

## Test Signals
Expected success is `Status.OK` and a non-null bucket table row. Expected failures include `VOLUME_NOT_FOUND`, `BUCKET_ALREADY_EXISTS`, `QUOTA_EXCEEDED`, `QUOTA_ERROR`, `INVALID_REQUEST`, `PERMISSION_DENIED`, and `INVALID_BUCKET_NAME`. The tests assert both response status and persisted table contents.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestOMBucketCreateRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestOMBucketCreateRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestOMBucketCreateRequestWithFSO.java

## Purpose
Specializes bucket create tests for `FILE_SYSTEM_OPTIMIZED` layout. It verifies FSO bucket creation through explicit CLI metadata and through OM default bucket layout, FSO-specific metrics, persisted layout, and non-S3 bucket names when strict namespace validation is disabled.

## Important APIs, Types, And Functions
- Extends `TestOMBucketCreateRequest` and overrides `doValidateAndUpdateCache`.
- `setupWithFSO` sets `OZONE_DEFAULT_BUCKET_LAYOUT` to `FILE_SYSTEM_OPTIMIZED`.
- `doPreExecute` optionally sets `BucketLayoutProto.FILE_SYSTEM_OPTIMIZED` and adds FSO metadata.
- `testValidateAndUpdateCacheWithFSO` and `testValidateAndUpdateCacheVerifyBucketLayoutWithFSO` inspect `omMetrics.getNumFSOBucketCreates`.
- `testNonS3BucketNameAllowedForFSOWhenStrictDisabled` verifies layout-specific naming relaxation.

## Control Flow
The test first adjusts OM configuration, then mocks `getOMDefaultBucketLayout` when necessary. Requests are preExecuted, verified against their original protobuf, and validated. The override creates `OmBucketInfo` from protobuf using the configured bucket layout so the expected object includes FSO layout semantics.

## State And Persistence Behavior
Successful validation writes a bucket row whose `BucketLayout` is `FILE_SYSTEM_OPTIMIZED`. The test compares timestamps, ACLs, version flag, storage type, metadata, encryption key info, and bucket layout. It also asserts that FSO bucket create metrics increment from 0 to 1.

## Dependencies And Integration Points
This class depends on superclass helpers, `OMConfigKeys.OZONE_DEFAULT_BUCKET_LAYOUT`, `OMRequestTestUtils.fsoMetadata`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, and `UserGroupInformation`. It validates the contract between CLI-specified layout metadata and OM default layout lookup.

## Risks And Edge Cases
The important regression risk is a divergence between configured default layout and layout stored in bucket metadata. Naming validation is also subtle: object-store buckets still reject underscores, while FSO buckets may allow them with strict S3 disabled.

## Test Signals
Success signals are `Status.OK`, persisted FSO bucket layout, and `getNumFSOBucketCreates == 1`. The non-S3 FSO path asserts no exception from validateAndUpdateCache.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestOMBucketCreateRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestOMBucketDeleteRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestOMBucketDeleteRequest.java

## Purpose
Tests `OMBucketDeleteRequest` for preExecute mutation, successful bucket removal, missing-bucket failure, and protection against deleting buckets that contain incomplete multipart uploads.

## Important APIs, Types, And Functions
- `createDeleteBucketRequest` builds `DeleteBucketRequest` wrapped in `OMRequest`.
- `testValidateAndUpdateCache` seeds volume and bucket rows, validates deletion, and checks the bucket row is absent.
- `testValidateAndUpdateCacheFailure` verifies `BUCKET_NOT_FOUND`.
- `testBucketContainsIncompleteMPUs` uses `OMMultipartUploadUtils`, `OmMultipartKeyInfo`, `OmKeyInfo`, and `multipartInfoTable`.

## Control Flow
PreExecute is expected to return a different request because user info is added. The success path inserts volume and bucket rows, calls `validateAndUpdateCache`, and observes the bucket removal. The MPU path inserts an incomplete multipart entry, verifies the delete request fails with bucket-not-empty, then deletes the multipart entry from cache and DB and retries successfully.

## State And Persistence Behavior
The primary state transition is deletion of the bucket table row. The MPU test also writes to `multipartInfoTable` through helper APIs and explicitly removes the multipart key. When MPUs exist, the bucket table remains populated; after removal, deletion succeeds and the bucket table row disappears.

## Dependencies And Integration Points
This class depends on `TestBucketRequest`, `OMRequestTestUtils` volume/bucket/MPU helpers, HDDS replication protos, cache key/value APIs, multipart upload utilities, and OM response status codes.

## Risks And Edge Cases
The main risk is accidentally allowing deletion while incomplete MPUs remain. Another subtle point is cache and DB consistency: the test deletes the multipart cache entry and table row before retrying, which covers the request's scan against current metadata.

## Test Signals
Success is a null bucket table row and `Status.OK` after MPU cleanup. Failure signals are `BUCKET_NOT_FOUND` for absent buckets and `BUCKET_NOT_EMPTY` while an incomplete MPU is present.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestOMBucketDeleteRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestOMBucketDeleteRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestOMBucketDeleteRequestWithFSO.java

## Purpose
Extends bucket delete coverage for FSO buckets, specifically verifying that deletion removes the FSO-layout bucket row and increments the FSO bucket delete metric.

## Important APIs, Types, And Functions
- Extends `TestOMBucketDeleteRequest`.
- `testValidateAndUpdateCacheWithFSO` seeds a bucket with `BucketLayout.FILE_SYSTEM_OPTIMIZED`.
- A local `createDeleteBucketRequest` builds the delete `OMRequest`.
- Uses `omMetrics.getNumFSOBucketDeletes`.

## Control Flow
The test starts with FSO delete metrics at 0, builds a delete request, seeds an FSO bucket, calls `validateAndUpdateCache`, checks the row is deleted, and checks the metric increments.

## State And Persistence Behavior
The test writes an FSO bucket row to `bucketTable` and expects the row at `getBucketKey(volume, bucket)` to become null. It also observes the metrics object state changing from 0 to 1 for FSO bucket deletes.

## Dependencies And Integration Points
It reuses the bucket fixture and delete request implementation but depends on `OMRequestTestUtils.addVolumeAndBucketToDB(..., BucketLayout.FILE_SYSTEM_OPTIMIZED)` to mark the layout. It validates the metrics integration specific to FSO buckets.

## Risks And Edge Cases
The test does not add FSO directory/key children, so it does not validate non-empty FSO tree deletion semantics. Its risk focus is metric classification and layout-aware delete accounting.

## Test Signals
Assertions are null bucket table row and `getNumFSOBucketDeletes == 1`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestOMBucketDeleteRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestOMBucketSetPropertyRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestOMBucketSetPropertyRequest.java

## Purpose
Tests `OMBucketSetPropertyRequest` for versioning, quota, replication config, encryption-key preservation, owner preservation, link-bucket rejection, FSO layout preservation, and preExecute modification time/user-info behavior.

## Important APIs, Types, And Functions
- `createSetBucketPropertyRequest` builds `SetBucketPropertyRequest` with `BucketArgs`.
- Tests operate on `OmBucketInfo`, `OmBucketArgs`, `BucketEncryptionKeyInfo`, `DefaultReplicationConfig`, and `ECReplicationConfig`.
- Uses `CacheKey` and `CacheValue` to mutate bucket used bytes and namespace counts before quota tests.
- `LogCapturer` checks error logging for quota exceed.

## Control Flow
The preExecute test verifies the modification time is advanced and user info changes the request. The normal success path seeds a bucket, validates, and checks versioning. Failure paths omit the bucket, set a quota above volume quota, set quota below used bytes or namespace, or attempt to set properties on a link bucket. Replication and encryption tests build `BucketArgs` with EC default replication and assert existing encryption metadata survives.

## State And Persistence Behavior
Successful validation updates the existing bucket row in `bucketTable`, preserving fields that are not being changed. The tests explicitly verify FSO `BucketLayout` remains FSO, encryption key info is retained, owner is retained, quota values are written, and default replication config is either set or preserved. Quota-used tests mutate cached `OmBucketInfo` usage counters before validation and expect rejection without accepting invalid lower quotas.

## Dependencies And Integration Points
The tests depend on `OMRequestTestUtils` DB seeders, `OzoneConsts.GB`, protobuf `BucketArgs`, EC replication config classes, link bucket metadata via `sourceVolume/sourceBucket`, OM response statuses, and bucket property logging.

## Risks And Edge Cases
The main risk is losing unrelated bucket metadata when applying partial property updates, especially encryption, owner, and default replication. Quota enforcement must account for volume quota, current bucket usage, namespace usage, and link-bucket restrictions. Another risk is accidentally changing bucket layout during property updates.

## Test Signals
Success signals are response success, updated bucket table fields, retained encryption/owner/replication, and `Status.OK`. Failure signals include `BUCKET_NOT_FOUND`, `QUOTA_EXCEEDED`, `QUOTA_ERROR`, and `NOT_SUPPORTED_OPERATION`, plus expected diagnostic message content.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestOMBucketSetPropertyRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/acl/TestOMBucketAddAclRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/acl/TestOMBucketAddAclRequest.java

## Purpose
Tests bucket ACL addition through `OMBucketAddAclRequest`, including preExecute modification time changes, successful ACL persistence, and missing-bucket failure.

## Important APIs, Types, And Functions
- Uses `OMRequestTestUtils.createBucketAddAclRequest` and `OzoneAcl.parseAcl`.
- Extends `TestBucketRequest` for OM fixture state.
- Validates `OMClientResponse`, `OMResponse.getAddAclResponse`, and `bucketTable` ACL list.

## Control Flow
The preExecute path builds an add-ACL request, records the original modification time, calls preExecute, and asserts a different request with greater modification time. The success path seeds user, volume, and bucket rows, validates the request, then reads the bucket ACL list. The failure path validates without creating the bucket and expects a not-found status.

## State And Persistence Behavior
Successful validation updates the `OmBucketInfo` in `bucketTable` by adding the ACL. The test expects exactly one ACL in the row and equality with the requested `user:newUser:rw` ACL.

## Dependencies And Integration Points
The test integrates with OM ACL helpers, bucket metadata table mutation, response protobufs, and audit-capable base fixture. It depends on `OMRequestTestUtils.addUserToDB` and `addVolumeAndBucketToDB`.

## Risks And Edge Cases
The test covers the basic add path but not duplicate ACL insertion, ACL scope conversion, ACL authorization, or link buckets. Regressions would surface as stale modification time, missing response submessage, or ACL list not being updated.

## Test Signals
Signals are increased modification time, `Status.OK` with `AddAclResponse`, one persisted ACL on success, and `BUCKET_NOT_FOUND` when the bucket is absent.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/acl/TestOMBucketAddAclRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/acl/TestOMBucketRemoveAclRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/acl/TestOMBucketRemoveAclRequest.java

## Purpose
Tests bucket ACL removal through `OMBucketRemoveAclRequest`, including preExecute mutation, add-then-remove persistence behavior, and missing-bucket failure.

## Important APIs, Types, And Functions
- Uses `OMRequestTestUtils.createBucketRemoveAclRequest` and `createBucketAddAclRequest`.
- Uses `OMBucketAddAclRequest` to seed the ACL through production request logic before removal.
- Reads `bucketTable` ACL list to validate state transitions.

## Control Flow
The preExecute test checks modification time advancement. The success test seeds user, volume, and bucket rows; adds an ACL using the add request; verifies it exists; then removes it using the remove request and verifies an empty ACL list. The missing-bucket path calls remove without seed state and checks the status.

## State And Persistence Behavior
The bucket row is mutated twice: first to contain one ACL and then to contain zero ACLs. Transaction log indexes differ between add and remove (`1` then `2`), exercising cache update ordering.

## Dependencies And Integration Points
This test depends on the add-ACL request implementation, bucket fixture setup, `OzoneAcl`, OM response submessages, and bucket metadata persistence.

## Risks And Edge Cases
It validates the common removal path but not removal of absent ACLs from an existing bucket, duplicate ACLs, or ACL inheritance. A regression could leave stale ACLs in `OmBucketInfo` or return success without changing the table.

## Test Signals
Signals are greater preExecute modification time, `Status.OK` for add and remove, ACL list size 1 then 0, and `BUCKET_NOT_FOUND` for absent buckets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/acl/TestOMBucketRemoveAclRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/acl/TestOMBucketSetAclRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/acl/TestOMBucketSetAclRequest.java

## Purpose
Tests bucket ACL replacement through `OMBucketSetAclRequest`, including preExecute modification time changes, successful replacement with multiple ACLs, and missing-bucket failure.

## Important APIs, Types, And Functions
- Uses `OMRequestTestUtils.createBucketSetAclRequest`.
- Uses Guava `Lists.newArrayList` to build ACL lists.
- Reads `bucketTable` ACLs after validateAndUpdateCache.

## Control Flow
The preExecute test builds a set-ACL request with one ACL and verifies a newer modification time. The success path seeds owner/user plus bucket rows, builds a set request with user and group ACLs, validates it, and checks both order and content in the persisted list. The failure path validates against missing bucket state and expects `BUCKET_NOT_FOUND`.

## State And Persistence Behavior
Successful validation replaces the bucket ACL list with the requested list. The test checks the ACL list size and exact first/second entries, implying ordering is preserved through persistence.

## Dependencies And Integration Points
The test integrates with Ozone ACL parsing, bucket metadata table, response protobufs, and the shared bucket fixture. It relies on `OMRequestTestUtils` for request creation and DB setup.

## Risks And Edge Cases
Set ACL semantics differ from add/remove because it replaces the full ACL list. Risks include appending instead of replacing, changing ACL order, or not updating modification time. The test does not cover empty set requests or duplicate ACLs.

## Test Signals
Signals are greater modification time, `Status.OK`, non-null `SetAclResponse`, exact persisted ACL list, and `BUCKET_NOT_FOUND` for absent bucket.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/acl/TestOMBucketSetAclRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/acl/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/acl/package-info.java

## Purpose
Declares package-level documentation for bucket ACL request tests in `org.apache.hadoop.ozone.om.request.bucket.acl`.

## Important APIs, Types, And Functions
- Contains only Javadoc and the package declaration.
- No executable classes, methods, or fields are defined.

## Control Flow
There is no runtime control flow. The file contributes documentation during source compilation/Javadoc processing.

## State And Persistence Behavior
No state is read or written. It has no direct persistence behavior.

## Dependencies And Integration Points
The package declaration groups tests for bucket ACL add, remove, and set request classes. It integrates only through Java package metadata.

## Risks And Edge Cases
Risk is limited to stale or incorrect package documentation. A wrong package declaration would break compilation or package-level documentation, but the current declaration matches the directory path.

## Test Signals
There are no direct tests. Compilation of package-level metadata is the signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/acl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/package-info.java

## Purpose
Declares package-level documentation for bucket request tests in `org.apache.hadoop.ozone.om.request.bucket`.

## Important APIs, Types, And Functions
- Contains package Javadoc and a package declaration.
- No test methods or helper APIs are defined.

## Control Flow
No runtime control flow exists. The file is consumed by Java compilation/Javadoc tooling.

## State And Persistence Behavior
No metadata table, configuration, or request state is touched.

## Dependencies And Integration Points
The file documents the package containing bucket create, delete, property, and fixture tests.

## Risks And Edge Cases
Risk is only documentation drift or package mismatch. The package declaration aligns with the folder.

## Test Signals
Successful compilation is the only signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/file/TestOMDirectoryCreateRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/file/TestOMDirectoryCreateRequest.java

## Purpose
Tests default-layout `OMDirectoryCreateRequest` behavior: preExecute mutation, reserved snapshot path rejection, successful directory creation, namespace quota, missing volume/bucket, existing directories/files in path, metrics, default ACL inheritance, and client ACL filtering.

## Important APIs, Types, And Functions
- Local fixture builds mocked `OzoneManager`, real `OmMetadataManagerImpl`, `OMMetrics`, audit logger, bucket link resolution, and layout version manager.
- `createDirectoryRequest` builds `CreateDirectoryRequest` with `KeyArgs` and optional ACLs.
- `verifyDirectoriesInheritAcls` walks created path components through `keyTable`.
- `genRandomKeyName` creates a 4-component directory path.
- Uses `OMDirectoryCreateRequest`, `OzoneFSUtils`, `OmBucketInfo`, `OmKeyInfo`, `CacheKey`, `OzoneAcl`, and `RatisReplicationConfig`.

## Control Flow
Each test builds a create-directory request, calls `preExecute`, constructs a new request object from the modified protobuf, optionally sets UGI, and calls `validateAndUpdateCache`. Failure cases seed no volume, only volume, preexisting directory, or conflicting file entries. ACL tests create bucket default ACLs or request ACLs and then inspect persisted key ACLs.

## State And Persistence Behavior
Default layout stores directories as key-table entries using `getOzoneDirKey(volume, bucket, key)`, commonly with trailing slash normalization. Successful creation adds entries for each missing directory component and updates bucket `usedNamespace` to `OzoneFSUtils.getFileCount(keyName)`. Existing-directory failure leaves the entry outside cache for the new transaction. File-conflict failures do not add the requested directory. Metrics `numKeys` increments by the number of directory entries created.

## Dependencies And Integration Points
The tests integrate with OM metadata tables, filesystem path utilities, ACL inheritance rules, namespace quota in `OmBucketInfo`, bucket link resolution, audit logger, and layout version checks. They are default-layout tests, so FSO-specific directory table behavior is covered separately.

## Risks And Edge Cases
High-risk edges are `.snapshot` reserved path handling, distinguishing existing directories from files, parent path handling under non-FSO layout, quota counting for multi-component directories, and conversion of default ACLs into inherited ACL state. The ignore-client-ACL branch protects deployments that disallow client-supplied ACLs.

## Test Signals
Expected statuses include `OK`, `QUOTA_EXCEEDED`, `VOLUME_NOT_FOUND`, `BUCKET_NOT_FOUND`, `DIRECTORY_ALREADY_EXISTS`, and `FILE_ALREADY_EXISTS`. Persistence signals are non-null or null `keyTable` entries, cache presence/absence, bucket namespace usage, ACL containment, and `omMetrics.getNumKeys`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/file/TestOMDirectoryCreateRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/file/TestOMDirectoryCreateRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/file/TestOMDirectoryCreateRequestWithFSO.java

## Purpose
Tests FSO/prefix-layout `OMDirectoryCreateRequestWithFSO`. It validates directory creation through object-id parent chains, directory table persistence, quota and missing parent failures, file conflicts, 255-level depth limits, metrics, default ACL inheritance, and client ACL filtering.

## Important APIs, Types, And Functions
- Local setup enables FSO paths with `OMRequestTestUtils.configureFSOptimizedPaths`.
- `createDirKey` builds a path and records each component.
- `verifyDirectoriesInDB` validates `directoryTable` rows via `getOzonePathKey(volumeId, bucketId, parentId, dirName)`.
- `verifyDirectoriesNotInCache` confirms existing directories were not re-cached.
- `verifyDirectoriesInheritAcls` checks inherited default ACLs along object-id parent chains.
- Uses `OMDirectoryCreateRequestWithFSO`, `OmDirectoryInfo`, `OmKeyInfo`, `OmBucketInfo`, and FSO bucket layout.

## Control Flow
Tests build FSO create-directory requests, call preExecute, instantiate the FSO request with the modified protobuf, and validate cache updates. Some tests preseed parent directories in `directoryTable`; others insert files into FSO key table at specific parent IDs to trigger conflicts. Depth-limit tests generate 255 or 256 component paths. ACL tests seed bucket default ACLs or request ACLs before validation.

## State And Persistence Behavior
FSO directories are persisted in `directoryTable`, not as trailing-slash key-table rows. Each directory row has a name, object ID, parent object ID, and path derived from the parent ID/name. Successful creation updates bucket namespace usage and `omMetrics.numKeys` by directory count. Existing-directory failure leaves existing rows out of the current cache. File conflicts preserve existing key-table rows and do not add conflicting directory rows.

## Dependencies And Integration Points
The test integrates FSO path configuration, bucket/object IDs, directory table, key table, namespace quota, ACL inheritance, audit logger, resolved bucket handling, and OM layout version manager. It provides coverage complementary to the default-layout directory test.

## Risks And Edge Cases
FSO correctness depends on object ID parent traversal. Risks include creating duplicate rows for existing directories, accepting paths deeper than 255 levels, confusing files with directories at either leaf or intermediate components, and failing to propagate default ACLs with correct scope. One test's ignore-client-ACL path uses `OMDirectoryCreateRequest` with FSO layout, which still exercises the layout-dependent table behavior through the layout argument.

## Test Signals
Statuses include `OK`, `QUOTA_EXCEEDED`, `VOLUME_NOT_FOUND`, `BUCKET_NOT_FOUND`, `DIRECTORY_ALREADY_EXISTS`, `FILE_ALREADY_EXISTS`, and `INVALID_KEY_NAME`. Table signals include directory table count, non-null directory rows, absent cache entries for preexisting directories, preserved key-table file rows, bucket namespace usage, ACL containment, and metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/file/TestOMDirectoryCreateRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/file/TestOMFileCreateRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/file/TestOMFileCreateRequest.java

## Purpose
Tests default-layout `OMFileCreateRequest` for preExecute block allocation, open key table insertion, namespace quota, encryption metadata, missing volume/bucket, recursive and non-recursive path behavior, overwrite behavior, ACL inheritance, client ACL filtering, reserved snapshot names, and block allocation for zero/unspecified data size.

## Important APIs, Types, And Functions
- Extends `TestOMKeyRequest`, inheriting volume/key names, SCM block location mock, replication config, and open-key verification behavior.
- `createFileRequest` builds `CreateFileRequest` with `KeyArgs`, replication type/factor, overwrite, recursive flag, data size, and optional ACLs.
- `getOMFileCreateRequest` sets current UGI on `OMFileCreateRequest`.
- `testNonRecursivePath` is the main reusable success/failure harness.
- `createFileWithInheritAcls` and `verifyInheritAcls` validate ACL propagation.
- Uses KMS `KeyProviderCryptoExtension`, `BucketEncryptionKeyInfo`, `OzoneLockProvider`, SCM `AllocatedBlock`, `Pipeline`, and `ExcludeList`.

## Control Flow
PreExecute requests SCM block allocation, sets a positive client ID and modification time, and writes key locations unless the key name is blank. Validation inserts the key into the open key table for successful creates. Path tests seed parent directory markers or child keys, toggle recursive and overwrite flags, and assert either success or statuses such as `NOT_A_FILE`, `FILE_ALREADY_EXISTS`, or `DIRECTORY_NOT_FOUND`.

## State And Persistence Behavior
Successful file creation writes an `OmKeyInfo` to the open key table keyed by key name and client ID. The row includes modification/creation time, replication config, and allocated block location info. Recursive creation can create parent directory entries and increments bucket namespace usage. Encryption tests seed a bucket encryption key and verify the create-file response contains file encryption info. ACL tests verify inherited default ACLs become access ACLs on the file when appropriate and that `ignoreClientACLs` filters client ACLs.

## Dependencies And Integration Points
The class integrates OM key request infrastructure, SCM block allocation, KMS encryption, OM metadata manager tables, filesystem path normalization, snapshot reserved names, quota accounting, ACL inheritance, and lock provider behavior. It is the base class for the FSO file-create subclass.

## Risks And Edge Cases
High-risk behaviors include not allocating blocks for empty/default-sized files, accepting `.snapshot` reserved roots, mishandling overwrite flags, misclassifying directories as files, failing quota accounting during recursive parent creation, and dropping encryption or ACL metadata. The tests use broad failure acceptance in `testNonRecursivePath` for some cases, so exact status regressions within the accepted set may need additional focused coverage.

## Test Signals
Signals include populated key locations after preExecute, `Status.OK` responses, open key table rows with expected block IDs, response key name match, namespace usage, inherited ACLs, filtered client ACLs, KMS file encryption info, and SCM `allocateBlock` verification for zero or missing data size.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/file/TestOMFileCreateRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/file/TestOMFileCreateRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/file/TestOMFileCreateRequestWithFSO.java

## Purpose
Specializes file create tests for FSO layout. It verifies non-recursive parent handling through directory table rows, recursive parent creation metrics, overwrite behavior against FSO key table rows, namespace quota, snapshot reserved word handling inside valid path components, and FSO open-file key lookup.

## Important APIs, Types, And Functions
- Extends `TestOMFileCreateRequest`.
- Overrides `getOMFileCreateRequest` to instantiate `OMFileCreateRequestWithFSO`.
- Overrides `getBucketLayout` to return `FILE_SYSTEM_OPTIMIZED`.
- Overrides `verifyPathInOpenKeyTable` to traverse `directoryTable` object IDs and read `getOpenFileName(volumeId, bucketId, parentId, fileName, clientId)`.
- `getDirInfo` resolves a directory path through object-id parent traversal.

## Control Flow
The subclass reuses superclass harnesses but pre-seeds FSO parent directories with `addParentsToDirTable` and files with `addFileToKeyTable`. Non-recursive tests first fail when parents are absent or a same-name directory exists, then succeed after valid parents exist. Recursive tests create missing parent directories, then test overwrite true/false against an existing key table file. Snapshot tests ensure `.snapshot` is allowed when it is not a reserved root segment.

## State And Persistence Behavior
FSO file creation uses the open key table with object-id-qualified open file names. Parent directories are persisted in `directoryTable`, and file rows are persisted in FSO key/open-key tables with parent object IDs. Metrics and bucket used namespace track created parent directories. Namespace quota tests seed a bucket with quota 1 and expect rejection.

## Dependencies And Integration Points
The class depends on FSO variants of create-file request and metadata helper methods, `OmDirectoryInfo`, `OmKeyInfo`, `OzoneFSUtils`, object-id path APIs, and inherited SCM/KMS/ACL helper behavior from the base class.

## Risks And Edge Cases
FSO-specific risks are wrong parent ID traversal, stale directory table rows after deleting key table rows, treating directories as files, and incorrectly rejecting valid `.snapshot` substrings. Overwrite behavior must target the exact object-id-qualified key, not just the string path.

## Test Signals
Signals include success/failure from inherited `testNonRecursivePath`, `omMetrics.getNumKeys`, bucket namespace usage, non-null FSO open-key rows, expected quota failure, and correct object-id traversal in verification helpers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/file/TestOMFileCreateRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/file/TestOMRecoverLeaseRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/file/TestOMRecoverLeaseRequest.java

## Purpose
Tests `OMRecoverLeaseRequest` for FSO files, including recovery initiation, idempotency, recovery commit behavior, new file length/client ID handling, rejection of allocate block and hsync during recovery, closed/open/absent file cases, and lease soft-limit enforcement.

## Important APIs, Types, And Functions
- Extends `TestOMKeyRequest` and forces `BucketLayout.FILE_SYSTEM_OPTIMIZED`.
- `populateNamespace` seeds volume/bucket, parent directories, key table rows, open key table rows, block locations, and optional `HSYNC_CLIENT_ID` metadata.
- `validateAndUpdateCache` preExecutes and validates `OMRecoverLeaseRequest`.
- `validateAndUpdateCacheForCommit` uses `OMKeyCommitRequestWithFSO` with recovery flags.
- `createAllocateBlockRequest` is used with `OMAllocateBlockRequestWithFSO` to ensure allocation is blocked during lease recovery.
- `getNewKeyArgs` rebuilds commit `KeyArgs` from recovered `OmKeyInfo` and optionally adjusts final block length.

## Control Flow
Recovery tests seed an hsync file in both key table and open key table, call recover lease, inspect returned key info, then commit through the FSO commit request. Idempotency calls recovery twice and expects both to return matching key names. Commit idempotency commits twice and expects the second commit to fail as already closed. Soft-limit tests vary `forceRecovery`, set `OZONE_OM_LEASE_SOFT_LIMIT`, call recovery inside and after the limit, and check status changes.

## State And Persistence Behavior
FSO closed file rows live in `keyTable`; open file rows live in `openKeyTable` under object-id-qualified open file names. Recovery marks a file under recovery and returns key info. Successful recovery commit moves state to the key table, removes the open key row, updates data size/final block length, and removes `HSYNC_CLIENT_ID` and `LEASE_RECOVERY` metadata. During recovery, allocate block and non-recovery hsync/commit are rejected.

## Dependencies And Integration Points
The test integrates lease recovery with FSO key commit, FSO block allocation, OM metadata tables, key location groups, client version protobuf conversion, replication config serialization, `OzoneConfigKeys.OZONE_OM_LEASE_SOFT_LIMIT`, and constants such as `HSYNC_CLIENT_ID` and `LEASE_RECOVERY`.

## Risks And Edge Cases
Critical risks are idempotency at the recovery-init stage but non-idempotency at commit, stale open key rows after successful recovery, accepting writes while recovery is active, enforcing soft limits incorrectly, and mishandling recovered block lengths. The `Thread.sleep(2000)` soft-limit test is timing-sensitive but directly covers the configured 2-second lease limit.

## Test Signals
Expected statuses include `OK`, `KEY_ALREADY_CLOSED`, `KEY_NOT_FOUND`, `KEY_UNDER_LEASE_RECOVERY`, and `KEY_UNDER_LEASE_SOFT_LIMIT_PERIOD`. Table verification checks key/open-key row presence, metadata cleanup, data size and block length preservation, non-null response key info, and user info from preExecute.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/file/TestOMRecoverLeaseRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/file/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/file/package-info.java

## Purpose
Declares package-level documentation for file request tests in `org.apache.hadoop.ozone.om.request.file`.

## Important APIs, Types, And Functions
- Contains only package Javadoc and the package declaration.
- No classes, helpers, or test methods are defined.

## Control Flow
No runtime control flow exists. The file is processed by Java compilation/Javadoc tooling.

## State And Persistence Behavior
No request state, metadata table, or configuration is accessed.

## Dependencies And Integration Points
The declaration groups directory-create, file-create, and lease-recovery tests under the file request test package.

## Risks And Edge Cases
Risk is limited to documentation drift or mismatched package declaration. The current package matches the source path.

## Test Signals
Successful compilation is the only signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/file/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMAllocateBlockRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMAllocateBlockRequest.java

## Purpose
Tests default-layout `OMAllocateBlockRequest` for preExecute block allocation, successful open-key update, and failure statuses when volume, bucket, or open key are missing.

## Important APIs, Types, And Functions
- Extends `TestOMKeyRequest`.
- `createAllocateBlockRequest` builds `AllocateBlockRequest` with `KeyArgs`, client ID, replication type/factor, and command type.
- `doPreExecute` verifies modification time, key location, container/local IDs, and pipeline.
- `getOmAllocateBlockRequest` returns `OMAllocateBlockRequest` with default layout.
- `addKeyToOpenKeyTable` seeds open key state through `OMRequestTestUtils.addKeyToTable`.

## Control Flow
The success path seeds volume/bucket and an open key, preExecutes the allocate-block request to attach a new block, verifies the open key initially has no locations, validates cache update, and re-reads the open key to confirm the new block. Failure paths preExecute the request but omit volume, bucket, or open key state before validation.

## State And Persistence Behavior
Successful validation updates an existing open key table row by appending one `OmKeyLocationInfo` to latest version locations and setting modification time from the request. The test confirms creation time remains less than or equal to modification time. Missing metadata paths do not create rows and return failure statuses.

## Dependencies And Integration Points
The class integrates with SCM block allocation behavior inherited from `TestOMKeyRequest`, OM metadata open key table, replication config, `OMRequestTestUtils`, and protobuf key location structures. It is subclassed by the FSO allocate-block test.

## Risks And Edge Cases
Risks include appending blocks to the wrong open key, not updating modification time, losing existing creation time semantics, or returning the wrong status when volume/bucket/key state is absent. The test validates one-block append only and does not cover multiple block allocation in one request.

## Test Signals
Signals are preExecute key location presence, `Status.OK` on success, open key location list size changing from 0 to 1, matching container/local IDs, and statuses `VOLUME_NOT_FOUND`, `BUCKET_NOT_FOUND`, and `KEY_NOT_FOUND` for missing state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMAllocateBlockRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMAllocateBlockRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMAllocateBlockRequestWithFSO.java

## Purpose
Specializes allocate-block tests for FSO layout by overriding open-key seeding, request construction, bucket layout, and open-key verification to use directory/object-id-qualified file paths.

## Important APIs, Types, And Functions
- Extends `TestOMAllocateBlockRequest`.
- `addKeyToOpenKeyTable` creates parent directory rows with `addParentsToDirTable`, builds an `OmKeyInfo` with object ID and parent object ID, and writes it to the open file table.
- `getOmAllocateBlockRequest` returns `OMAllocateBlockRequestWithFSO`.
- `verifyPathInOpenKeyTable` traverses `directoryTable` with `StringUtils.split` and reads open key table via `getOpenFileName(volumeId, bucketId, parentId, fileName, clientId)`.
- `getBucketLayout` returns `FILE_SYSTEM_OPTIMIZED`.

## Control Flow
The inherited tests call the overridden methods. Before validation, the subclass rewrites `keyName` into a parent directory plus file leaf, seeds parent directories, and places an open file row under the FSO open file name. Verification traverses each path component to find the correct parent object ID before reading the open key row.

## State And Persistence Behavior
FSO open-file state is keyed by volume ID, bucket ID, parent object ID, file name, and client ID. Parent directories live in `directoryTable`, and the open file row has explicit object and parent object IDs. Successful inherited validation appends the allocated block to that FSO open file row.

## Dependencies And Integration Points
The subclass depends on FSO request implementation, OM metadata object ID APIs, `OmDirectoryInfo`, `OmKeyInfo`, `RatisReplicationConfig`, Ozone path key generation, and inherited SCM/block assertion logic.

## Risks And Edge Cases
The main risks are incorrect parent ID traversal and writing to the default open key table key format instead of the FSO open file name. Because it mutates `keyName` in `addKeyToOpenKeyTable`, inherited tests depend on this method being called before later verification.

## Test Signals
Signals come from inherited allocate-block assertions plus FSO-specific non-null directory and open file lookups. Any wrong object ID or open-file key construction causes `assertNotNull` or inherited block assertions to fail.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMAllocateBlockRequestWithFSO.java -->
