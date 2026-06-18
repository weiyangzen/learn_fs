# subset-b-008199 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-deleteobject_test.go -->
# sources/object-store/minio/cmd/object-api-deleteobject_test.go

## Purpose
This test file verifies `ObjectLayer.DeleteObject` behavior through the common `ExecObjectLayerTest` harness, so the same behavioral contract is exercised against the supported object layer implementations. The focus is simple object deletion and directory-marker cleanup semantics rather than versioned deletes or replication deletes.

## Important APIs, types, and functions
`TestDeleteObject` delegates to `testDeleteObject`. The test uses `ObjectLayer.MakeBucket`, `ObjectLayer.PutObject`, `ObjectLayer.DeleteObject`, and `ObjectLayer.ListObjects`. Test inputs are encoded in the local `objectUpload` type and a table containing bucket name, objects to upload, target path, and expected remaining objects. Uploads are built with `mustGetPutObjReader` and MD5 values computed from the in-memory content.

## Control flow
For each table case the test creates a fresh bucket, uploads all objects, deletes one path, lists the bucket, and compares the resulting object names to the expected ordered list. Delete errors are tolerated only when `isErrObjectNotFound` is true; all other errors fail the case. The cases cover deleting a normal object, deleting a child that leaves its parent directory empty, deleting one child while a sibling remains, attempting to delete a non-empty directory marker, and deleting an explicit empty directory object.

## State and persistence behavior
The test mutates real object-layer state in temporary test backends: buckets are created, object data is persisted through `PutObject`, and delete operations must update the persisted namespace seen by subsequent `ListObjects`. It indirectly verifies cleanup of synthetic/empty directory entries when the last child is removed, while preserving directory-like prefixes that still have contents.

## Dependencies and integration points
The test depends on the object-layer test harness, object reader helpers, MD5/hex encoding, and `isErrObjectNotFound` from the object API error helpers. It integrates with listing semantics because deletion correctness is asserted through `ListObjects`, not through filesystem inspection.

## Risks and test signals
The main regression signal is namespace drift after deletes: accidental removal of siblings, failure to remove explicit empty directory objects, or incorrectly deleting non-empty directory prefixes. The test is intentionally small and does not cover versioned deletes, object lock, delete-marker replication, prefix-forced deletes, or multi-delete batch behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-deleteobject_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-errors.go -->
# sources/object-store/minio/cmd/object-api-errors.go

## Purpose
This file defines the object API error taxonomy and the conversion bridge from low-level storage/erasure errors into typed object-layer errors. Its central role is to keep backend storage failures, validation failures, replication failures, multipart failures, and S3-facing object state errors distinguishable to higher API layers.

## Important APIs, types, and functions
`toObjectErr` unwraps an incoming error with `unwrapAll`, preserves `context.Canceled`, and maps known storage sentinel errors into typed errors such as `BucketNotFound`, `BucketNotEmpty`, `BucketExists`, `StorageFull`, `SlowDown`, `PrefixAccessDenied`, `ObjectExistsAsDirectory`, `VersionNotFound`, `MethodNotAllowed`, `ObjectNotFound`, `InvalidUploadID`, `ObjectNameInvalid`, `ObjectTooLarge`, `ObjectTooSmall`, `InsufficientReadQuorum`, `InsufficientWriteQuorum`, and `IncompleteBody`. It accepts optional bucket/object/version/upload ID parameters and decodes directory-object names through `decodeDirObject`.

The file defines many error types with `Error()` methods: generic bucket/object errors backed by `GenericError`, quorum errors, object lock and conditional errors, bucket configuration errors, replication remote-target errors, lifecycle/transition errors, object-name errors, range errors, multipart errors, backend and unimplemented errors, metadata errors, replication permission errors, and data movement overwrite errors. Helper predicates include `isErrBucketNotFound`, `isErrReadQuorum`, `isErrWriteQuorum`, `isErrObjectNotFound`, `isErrVersionNotFound`, `isErrSignatureDoesNotMatch`, `isErrPreconditionFailed`, `isErrMethodNotAllowed`, `isErrInvalidRange`, `isReplicationPermissionCheck`, and `isDataMovementOverWriteErr`.

## Control flow
Most control flow is table-like dispatch in `toObjectErr`: after unwrapping, it switches on the underlying error string and constructs the higher-level error with as much contextual data as was passed. Error predicates use `errors.Is` for sentinel compatibility and `errors.As` for typed wrapper compatibility. Some types implement `Unwrap`, allowing callers to use Go error chains while still preserving object API context.

## State and persistence behavior
The file has no persistent state. Its state behavior is encoded in error values, especially bucket/object/version/upload fields and quorum reason fields. The correctness of these values matters because later HTTP translation, audit logging, replication, healing, and tests inspect the concrete type and rendered message.

## Dependencies and integration points
It depends on `context`, `errors`, `fmt`, and `io`, plus package-level sentinels from storage, erasure, typed error, and utility files. It is integrated broadly by object API implementations, HTTP error translation (`toAPIError` paths), tests that compare error messages or types, and replication/data movement code that needs specific classifications.

## Risks and test signals
The highest-risk area is string-based matching in `toObjectErr`; if a sentinel error message changes, conversion can silently fall through. Another risk is incomplete context in variadic parameters, producing typed errors with empty bucket/object fields. The helper predicates reduce risk by using `errors.Is` and `errors.As`, but some helpers still use direct type assertions and can miss wrapped values. Test signals are spread across object API tests that expect exact error strings/types for invalid buckets, missing objects, invalid upload IDs, invalid ranges, multipart failures, and quorum behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-getobjectinfo_test.go -->
# sources/object-store/minio/cmd/object-api-getobjectinfo_test.go

## Purpose
This file tests `ObjectLayer.GetObjectInfo` for validation, missing resources, and metadata returned for normal objects and explicit directory objects. It uses the common object-layer harness so the contract applies to erasure and single-node style backends.

## Important APIs, types, and functions
`TestGetObjectInfo` delegates to `testGetObjectInfo`. The test creates a bucket, uploads `Asia/asiapics.jpg` and `Asia/empty-dir/`, then exercises `ObjectLayer.GetObjectInfo` with `ObjectOptions{}`. Expected outputs are expressed as `ObjectInfo` values containing `Bucket`, `Name`, `ContentType`, and `IsDir`. Expected failures use typed object errors such as `BucketNameInvalid`, `BucketNotFound`, `ObjectNameInvalid`, and `ObjectNotFound`.

## Control flow
The setup creates a bucket and uploads a non-empty JPEG-like object plus an empty directory marker. A table then covers invalid bucket names, valid but missing buckets, empty object names in an existing bucket, missing object names under an existing bucket, and valid objects. Each case calls `GetObjectInfo`, checks pass/fail expectations, compares error messages for failing cases, and verifies selected `ObjectInfo` fields for passing cases.

## State and persistence behavior
The test depends on persisted bucket metadata and object metadata produced by `PutObject`. It expects MIME/content-type inference or metadata handling to identify `Asia/asiapics.jpg` as `image/jpeg`, while the empty directory marker is reported as `application/octet-stream` and `IsDir: true`.

## Dependencies and integration points
Dependencies include the test harness, `bytes.Buffer`, `mustGetPutObjReader`, `ObjectOptions`, and the object API error types. The test integrates with object name validation, bucket lookup, metadata persistence, and directory marker handling.

## Risks and test signals
The strongest signal is that `GetObjectInfo` must fail early and consistently for invalid buckets/object names, must distinguish missing buckets from missing objects, and must preserve directory-marker status. The test does not verify object size, ETag, version IDs, checksums, encryption metadata, retention/legal hold metadata, or range-related behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-getobjectinfo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-input-checks.go -->
# sources/object-store/minio/cmd/object-api-input-checks.go

## Purpose
This file centralizes argument validation for object API operations before those calls reach storage implementations. It turns invalid bucket names, object names, prefixes, and multipart upload ID markers into typed object API errors.

## Important APIs, types, and functions
Simple wrappers `checkCopyObjArgs`, `checkGetObjArgs`, and `checkDelObjArgs` call `checkBucketAndObjectNames`. `checkBucketAndObjectNames` validates bucket names with `s3utils.CheckValidBucketNameStrict`, except for MinIO metadata buckets, then requires a non-empty valid object prefix. `checkListObjsArgs` validates bucket and prefix for listing. `checkListMultipartArgs` extends listing validation with upload ID marker checks: an upload ID marker cannot be paired with a key marker ending in `/`, and non-empty upload ID markers must decode as raw URL base64. `checkNewMultipartArgs`, `checkPutObjectPartArgs`, `checkListPartsArgs`, `checkCompleteMultipartArgs`, and `checkAbortMultipartArgs` delegate to `checkObjectArgs` or `checkMultipartObjectArgs`. `checkObjectArgs` uses stricter object-name validation, while `checkPutObjectArgs` allows valid object prefixes but still rejects empty names.

## Control flow
Validation proceeds from bucket to object/prefix to multipart-specific markers. The bucket checks intentionally happen before object/prefix checks in most functions, which controls which error callers observe when multiple inputs are invalid. Multipart object operations validate the upload ID's raw URL base64 shape before object validation.

## State and persistence behavior
This file has no persistent state and does not check actual bucket existence. It only validates syntactic and platform-sensitive constraints before object-layer methods perform stateful bucket/object lookups.

## Dependencies and integration points
It depends on `s3utils`, base64 raw URL decoding, runtime OS detection, string helpers, MinIO metadata-bucket recognition, object-name helpers from `object-api-utils.go`, and typed errors from `object-api-errors.go`. It is used by object-layer implementations and handlers to keep validation behavior consistent across get, put, copy, delete, list, and multipart operations.

## Risks and test signals
Risks include subtle differences between prefix and object validation, especially around empty strings and trailing slash directory markers. Windows-specific rejection of backslashes in `checkBucketAndObjectNames` and broader invalid characters in lower helpers can create platform-specific behavior. Multipart upload ID validation depends on raw URL base64 and intentionally rejects padded IDs. The listed test files provide indirect signals through expected `BucketNameInvalid`, `ObjectNameInvalid`, `MalformedUploadID`, and `InvalidUploadIDKeyCombination` outcomes.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-input-checks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-interface.go -->
# sources/object-store/minio/cmd/object-api-interface.go

## Purpose
This file defines the central `ObjectLayer` interface and option structs used by MinIO object API implementations. It is the contract between S3/API handlers and backend object storage implementations for bucket, object, multipart, healing, metadata, tagging, health, and lifecycle/transition operations.

## Important APIs, types, and functions
`ObjectOptions` is the main cross-operation carrier. It includes server-side encryption, versioning state, version ID, modification/expiration time, delete marker and delete replication state, tagging and object attribute request data, precondition and metadata callbacks, transition/expiration options, checksum requests, decryption flags, ETag preservation, proxy/replication flags, source timestamps for replicated metadata, prefix deletion flags, speedtest flags, parity/encryption callbacks, decommission/rebalance routing flags, data movement flags, versioning prefix callback, index callback, free-version controls, retention bypass callback, fast head/get flag, and audit suppression.

`WalkOptions`, `ExpirationOptions`, `TransitionOptions`, `MakeBucketOptions`, `DeleteBucketOptions`, and `BucketOptions` define narrower option sets. Helper methods on `ObjectOptions` maintain replication state: `SetReplicaStatus`, `DeleteMarkerReplicationStatus`, `VersionPurgeStatus`, `SetDeleteReplicationState`, `PutReplicationState`, `SetEvalMetadataFn`, and `SetEvalRetentionBypassFn`.

`ObjectLayer` includes namespace locking, scanner/backend/storage info, bucket CRUD and listing, object get/info/put/copy/delete/transition/restore, multipart lifecycle, disk access, healing, health, metadata update, tiered decommission, and object tag operations. `GetObject` is a compatibility adapter around `GetObjectNInfo` that copies the returned reader to an `io.Writer`.

## Control flow
The interface itself has no implementation flow, but it defines expected operation sequencing. `GetObject` builds an HTTP range spec and optional ETag header, calls `GetObjectNInfo`, returns immediately on error, closes the reader with `defer`, and copies data via `xioutil.Copy`. The interface comment requires implementations to return a nil reader when returning an error from `GetObjectNInfo`.

## State and persistence behavior
State is represented as options and backend mutations rather than stored in this file. The interface covers persistent bucket/object namespace changes, multipart metadata, object versioning/delete-marker state, replication metadata, healing state, object tags, and tier transition state. Option fields such as `NoLock`, `SkipDecommissioned`, `SkipRebalancing`, `SrcPoolIdx`, and `DataMovement` affect how implementations coordinate persistent writes across pools and disks.

## Dependencies and integration points
The file imports `madmin-go`, MinIO encryption and tag packages, internal hash/checksum and replication packages, HTTP types, and internal I/O helpers. It is a high fan-in integration point for S3 handlers, replication, lifecycle, scanner/healing, metadata systems, object-lock enforcement, and tests. The `go:generate msgp` directive and `msgp:ignore` annotations connect this source to the generated serialization companion.

## Risks and test signals
`ObjectOptions` is broad and easy to misuse; many fields are valid only for specific operations. Regressions can arise when handlers forget to set versioning or replication flags, when backend implementations ignore callback fields, or when generated serialization falls out of sync for serializable option types. The tests in this subset exercise portions of the interface through delete, get info, list, multipart, option parsing, and object attributes, but many interface methods require coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-interface_gen.go -->
# sources/object-store/minio/cmd/object-api-interface_gen.go

## Purpose
This generated file implements MessagePack serialization helpers for selected option types defined in `object-api-interface.go`. It is produced by `github.com/tinylib/msgp` and should not be hand-edited.

## Important APIs, types, and functions
The file provides `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` methods for `BucketOptions`, `ExpirationOptions`, `MakeBucketOptions`, `WalkOptions`, and `WalkVersionsSortOrder`. Each struct method emits a map with stable field names, reads maps by key, skips unknown fields, wraps decode errors with field context, and returns an upper-bound serialized size. `WalkOptions` serialization intentionally includes only serializable fields (`Marker`, `LatestOnly`, `AskDisks`, `VersionsSort`, and `Limit`) and excludes the function-valued `Filter`.

## Control flow
Marshal methods allocate/extend output buffers with `msgp.Require`, append a fixed map header and fields in generated order, and return the buffer. Unmarshal methods read the map header, loop over keys, decode recognized fields, skip unknown fields, and return the unread suffix. Enum serialization for `WalkVersionsSortOrder` is a direct uint8 conversion.

## State and persistence behavior
The file has no runtime state, but it defines wire/storage compatibility for option values that may cross process or RPC boundaries. Unknown-field skipping gives limited forward/backward compatibility, while field-name changes or type changes are compatibility-sensitive.

## Dependencies and integration points
It depends only on `github.com/tinylib/msgp/msgp` and the option types from the same package. It integrates with the `go:generate msgp` directive in `object-api-interface.go`. Because `ObjectOptions`, `TransitionOptions`, and `DeleteBucketOptions` are ignored by msgp annotations, this file does not serialize the largest option carrier.

## Risks and test signals
The main risk is stale generated code after changing option structs. Adding a serializable field to one of these types requires regenerating this file or the field will not be transported. Function-valued and intentionally ignored fields must remain excluded. Tests for generated code are disabled in the directive, so coverage is mostly indirect through code paths that marshal these options.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-interface_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-listobjects_test.go -->
# sources/object-store/minio/cmd/object-api-listobjects_test.go

## Purpose
This file provides broad regression coverage for object listing behavior: classic `ListObjects`, versioned listing, continuation behavior, versioned delete-marker handling, listing under lifecycle expiration, and a benchmark for large listings.

## Important APIs, types, and functions
Entry points include `TestListObjectsVersionedFolders`, `TestListObjectsOnVersionedBuckets`, `TestListObjects`, `TestDeleteObjectVersionMarker`, `TestListObjectVersions`, `TestListObjectsContinuation`, `BenchmarkListObjects`, and `TestListObjectsWithILM`. Core object-layer APIs exercised are `MakeBucket`, `PutObject`, `DeleteObject`, `ListObjects`, `ListObjectVersions`, and `ListObjectsV2`. Helpers include `objInfoNames`, `initFSObjectsB`, lifecycle parsing, bucket metadata updates, and global expiry state setup.

## Control flow
The tests create buckets with and without versioning, upload deterministic object sets, and compare listing results against table-driven `ListObjectsInfo` or `ListObjectVersionsInfo` expectations. The non-versioned and versioned listing tests share much of the same object corpus and cover invalid bucket names, missing buckets, empty buckets, negative/zero/large `maxKeys`, truncation, `NextMarker`, markers before and after result ranges, prefix filtering, delimiter grouping, custom delimiters, trailing slash object lookups, empty directory markers, and prefix matches around `xl.meta`-like paths.

`testListObjectsVersionedFolders` specifically checks that delete markers on directory objects are represented correctly in versioned listings and hidden or exposed appropriately in normal listings. `testDeleteObjectVersion` modifies bucket metadata to suspend versioning, then verifies delete behavior with and without the null version ID. `testListObjectsContinuation` pages through results using `NextMarker`, including a branch that deliberately resumes from the last object name rather than the returned marker to guard continuation robustness. `testListObjectsWithILM` installs a lifecycle expiration rule and verifies `ListObjectsV2` does not expose expired objects while still paginating without infinite loops.

## State and persistence behavior
These tests exercise persisted object namespace state, bucket versioning metadata, delete markers, lifecycle metadata, global metadata system updates, and global expiry state. They rely on lexicographic ordering and stable directory-prefix projection from the backend. The ILM test uses older modification times to make some persisted objects logically expired even though they were just written by the test.

## Dependencies and integration points
Dependencies include the object-layer test harness, MD5/hex helpers, lifecycle parsing, global bucket metadata and notification systems, global versioning and expiry systems, and benchmark initialization through `initObjectLayer`, `newTestConfig`, and `initAllSubsystems`. The file integrates listing behavior with delete, versioning, lifecycle, and metadata subsystems.

## Risks and test signals
This file is a major regression signal for S3-compatible listing semantics. It can catch off-by-one marker handling, wrong truncation state, missing `NextMarker`, incorrect prefix grouping, directory-marker visibility bugs, version/delete-marker ordering regressions, lifecycle filtering loops, and max-keys normalization errors. Gaps include ListObjectsV2 continuation-token semantics beyond ILM, owner/fetch-owner fields, encoding type, and detailed version ID marker assertions.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-listobjects_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-multipart_test.go -->
# sources/object-store/minio/cmd/object-api-multipart_test.go

## Purpose
This file is the main multipart object API test suite for creating uploads, aborting uploads, uploading parts, listing multipart uploads, listing parts under normal and degraded storage conditions, completing uploads, and benchmarking part uploads.

## Important APIs, types, and functions
Entry points include `TestObjectNewMultipartUpload`, `TestObjectAbortMultipartUpload`, `TestObjectAPIIsUploadIDExists`, `TestObjectAPIPutObjectPart`, `TestListMultipartUploads`, `TestListObjectPartsStale`, `TestListObjectPartsDiskNotFound`, `TestListObjectParts`, `TestObjectCompleteMultipartUpload`, and benchmark functions for FS and erasure part sizes. Object-layer APIs exercised are `MakeBucket`, `DeleteBucket`, `NewMultipartUpload`, `AbortMultipartUpload`, `PutObjectPart`, `ListMultipartUploads`, `ListObjectParts`, and `CompleteMultipartUpload`.

## Control flow
The new-upload and abort tests validate invalid buckets, missing buckets, successful upload initialization, invalid upload IDs, and abort behavior. The put-part test sets up valid and invalid uploads, then checks invalid bucket/object names, missing buckets, mismatched bucket/object/upload ID combinations, MD5 mismatch, SHA256 mismatch, reader overread/underread behavior, and successful part ETag responses.

`testListMultipartUploads` creates multiple buckets with one upload, multiple upload IDs for the same object, and uploads for multiple object names. It uploads parts, then verifies listing by prefix, key marker, upload ID marker, delimiter, max uploads, truncation, next key marker, and next upload ID marker. `testListObjectParts`, `testListObjectPartsStale`, and `testListObjectPartsDiskNotFound` verify part listing fields and pagination. The stale test deletes a part from quorum-majority disks and expects that part to disappear from listings; the disk-not-found test wraps a random disk as faulty and expects degraded listing to remain correct. `testObjectCompleteMultipartUpload` verifies invalid part metadata, ETag mismatch, part-too-small checks, valid completion ETag calculation, and cleanup of the upload ID after successful completion.

## State and persistence behavior
The suite creates real multipart metadata, part objects, and final completed objects in the test backend. It inspects behavior after state mutations such as deleting a bucket used by an upload, aborting an upload, forcing stale part data on erasure disks, injecting faulty disk behavior, and completing an upload. Successful completion must consume multipart state so later operations on the same upload ID fail.

## Dependencies and integration points
Dependencies include the extended object-layer harness, disk-altered harness, erasure server pool internals, storage class parity configuration, naughty disk wrappers, MinIO hash and ioutil errors, `go-humanize` sizes, and multipart MD5 helpers. The tests integrate multipart state with validation, checksum verification, erasure quorum behavior, listing pagination, and final object assembly.

## Risks and test signals
This file catches many high-risk multipart regressions: accepting invalid upload IDs, losing checksum validation, mishandling short/long readers, incorrect multipart listing markers, stale part visibility after disk divergence, degraded-read failures, allowing too-small completed parts, wrong final multipart ETag, and failure to clean temporary multipart state. Some assertions compare error strings while others compare types, so changes to error rendering can break tests even if behavior is otherwise equivalent. Gaps include encrypted multipart paths, checksum algorithms beyond MD5/SHA256 cases shown here, object lock interactions, and replication-specific multipart behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-multipart_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-options.go -->
# sources/object-store/minio/cmd/object-api-options.go

## Purpose
This file translates HTTP request headers, query parameters, and metadata maps into `ObjectOptions` for get/head, get-object-attributes, delete, put, copy, and complete-multipart operations. It is the bridge between S3/MinIO request syntax and backend object-layer semantics.

## Important APIs, types, and functions
`getDefaultOpts` parses encryption/proxy/replication/speedtest signals and builds the base `ObjectOptions`, including SSE-C, SSE-C copy source, SSE-S3, and encrypted metadata handling. `getOpts` parses GET/HEAD options such as `partNumber`, `versionId`, delete-marker flags, delete-marker replication-ready checks, tag directive, and bucket versioning/suspension state. `getAndValidateAttributesOpts` builds options for GetObjectAttributes and writes an XML error response on invalid arguments. `parseObjectAttributes`, `parseIntHeader`, and `parseBoolHeader` are reusable parsers.

`delOpts` extends `getOpts` for delete requests by parsing force-delete prefix behavior, adjusting versioning suspension at bucket level, forcing null version IDs for directory objects, parsing source delete marker state, and parsing source modification time. `putOptsFromReq`, `putOpts`, `putOptsFromHeaders`, `copyDstOpts`, and `copySrcOpts` parse PUT and copy options, including version IDs, versioning enablement, source modification time, replication source timestamps, SSE-KMS, SSE-C/SSE-S3, user metadata, and ETag preservation. `completeMultipartOpts` parses source modification time, requested content checksum, SSEC encryption function, replication request metadata, and replication SSEC checksum metadata.

## Control flow
The control flow is layered. Operation-specific functions validate operation-specific query/header values, then delegate to common encryption/default parsers. Version ID parsing trims whitespace and accepts the null version ID but otherwise requires UUID syntax. Attribute validation defers error-response writing until all parsing has failed or succeeded, allowing it to report S3-style argument names and values.

## State and persistence behavior
The file does not persist state itself, but it reads global bucket versioning state and populates options that directly control persistent behavior: whether writes create versions, whether deletes create delete markers, whether directory objects use null versions, whether replication metadata/timestamps are preserved, whether ETags are preserved, and whether multipart completion records checksums or replication actual-size metadata.

## Dependencies and integration points
It depends on HTTP requests/headers, UUID parsing, MinIO crypto and encryption packages, internal checksum parsing, internal HTTP header constants, global bucket versioning state, API error conversion and response writers, metadata constants, and object attribute response types. It is integrated with S3 handlers before they call the `ObjectLayer`.

## Risks and test signals
Risks are concentrated in header parsing and option defaults: permissive or strict bool parsing can change replication/delete behavior, wrong versioning checks can allow invalid version ID writes, and encryption header parsing failures are wrapped differently by PUT paths. `getAndValidateAttributesOpts` writes the HTTP response itself on invalid options, so callers must respect the returned `valid` flag. The local options test covers only object attribute parsing; broader signals come from API handler and object-layer tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-options_test.go -->
# sources/object-store/minio/cmd/object-api-options_test.go

## Purpose
This file provides focused unit coverage for object-attribute option parsing in `getAndValidateAttributesOpts`, currently limited to how `x-amz-object-attributes` header values are split and deduplicated.

## Important APIs, types, and functions
`TestGetAndValidateAttributesOpts` initializes `globalBucketVersioningSys`, constructs `httptest` requests and response recorders, and calls `getAndValidateAttributesOpts`. It asserts the resulting `ObjectOptions.ObjectAttributes` map using `reflect.DeepEqual`. Header constants come from `internal/http`.

## Control flow
The test table covers an empty header, a single comma-delimited header line, and multiple header lines with duplicate values. For each case it builds a GET request to `/test`, assigns the case headers, calls the option parser using the MinIO metadata bucket and a test object name, and compares the parsed attribute set.

## State and persistence behavior
There is no persistent storage interaction. The only global state mutation is assigning `globalBucketVersioningSys = &BucketVersioningSys{}` so `getOpts` can query versioning state safely. The response recorder may receive error XML for invalid attribute names, but this test ignores the `valid` flag and focuses on the parsed map.

## Dependencies and integration points
The test depends on `net/http`, `httptest`, `reflect`, the object option parser, MinIO metadata bucket naming, and HTTP header constants. It integrates with the same parsing path used by GetObjectAttributes handlers, though it avoids a full HTTP handler test.

## Risks and test signals
The signal is narrow but useful: attribute parsing must trim header lines, split comma-separated values, merge repeated headers, and deduplicate duplicates. It does not assert validity filtering, API error response shape, max-parts parsing, part-number marker parsing, version ID errors, or allowed S3 attribute names. The comment explicitly states that coverage is minimal and expected to grow when the function is modified.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-options_test.go -->
