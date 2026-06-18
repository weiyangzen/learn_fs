# subset-b-007878 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_list_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_list_test.go

Purpose: this test file exercises S3 ListObjects/ListObjectsV2 XML rendering, prefix and marker normalization, recursive filer traversal, delimiter/common-prefix behavior, permission matching for list requests, and regressions around marker echo and prefix paths ending in `/`. It is a broad regression harness for listing behavior implemented elsewhere in the `s3api` package.

Important APIs/types/functions: `testListEntriesStream` implements the gRPC streaming client shape expected by `SeaweedFilerClient.ListEntries`; `testFilerClient` supplies directory-scoped synthetic `filer_pb.Entry` slices; `markerEchoFilerClient` simulates a backend that incorrectly echoes `StartFromFileName`; `ensureEntryAttributes` protects tests from nil attributes. Tests directly call `normalizePrefixMarker`, `buildTruncatedNextMarker`, `getListObjectsV1Args`, `getListObjectsV2Args`, `sanitizeV1MarkerEcho`, `Identity.CanDo`, and `S3ApiServer.doListFilerEntries`.

Control flow: the tests bypass HTTP for most cases and drive internal listing helpers with mock filer clients. `TestDoListFilerEntries_BucketRootPrefixSlashDelimiterSlash_ListsDirectories` proves prefix `/` and delimiter `/` at bucket root still lists directories. Marker echo tests set a cursor, pass an exclusive marker, and verify echoed markers are skipped without losing following entries. Prefix-ending-with-slash tests model `prefixEndsOnDelimiter` so traversal descends into only the exact directory and does not match sibling directories like `1000` when the prefix is `1/`.

State and persistence behavior: no persistent state is written; all state is in test-local maps keyed by filer directory. The tests model persisted SeaweedFS metadata through `filer_pb.Entry` fields such as `Name`, `IsDirectory`, `Attributes`, `Extended`, and callback-collected list results.

Dependencies and integration points: the test depends on `filer_pb`, `s3err.EncodeXMLResponse`, `httptest`, gRPC stream interfaces, and `testify/assert`. Its strongest integration points are the filer listing stream contract, S3 XML response structs (`ListBucketResult`, `ListEntry`, `PrefixEntry`), and auth wildcard matching for object-level `List` actions.

Risks: several subtests are documentation-style assertions using `assert.True(t, true)` rather than executable coverage of production delimiter grouping. Mock clients ignore some real filer semantics, especially ordering, limit, and start behavior, so regressions in production pagination may not be fully caught. Still, the marker echo mock intentionally stresses a real no-progress risk.

Test signals: strong signals cover XML namespace output, invalid `max-keys`, allow-unordered parsing, marker echo no-progress protection, root prefix slash listing, exact directory prefix traversal, and object-level list permissions for issue-style scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_list_versioned_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_list_versioned_test.go

Purpose: this file validates listing behavior when objects are represented by SeaweedFS `.versions` directories. It checks that versioned objects project as normal current objects in ordinary listings, delete-marker latest versions are hidden, `.versions` directories are not recursively traversed, XML for `ListObjectVersions` preserves interleaved ordering, and key-marker traversal starts from the correct directory component.

Important APIs/types/functions: tests reuse `testFilerClient` and introduce `customTestFilerClient` to track traversed directories. They exercise `doListFilerEntries`, `S3ListObjectVersionsResult` XML marshaling, `VersionListEntry`, `VersionEntry`, `DeleteMarkerEntry`, `PrefixEntry`, `versionCollector.computeStartFrom`, and logic equivalent to version-directory prefix filtering.

Control flow: synthetic filer entries include directory names ending in `s3_constants.VersionsFolder` plus `Extended` fields such as `ExtLatestVersionIdKey`, latest size, latest mtime, latest ETag, and latest delete-marker flag. Ordinary listing tests call `doListFilerEntries` with callbacks that collect projected keys. XML tests build `S3ListObjectVersionsResult.Entries` in expected order and assert that marshaling emits `DeleteMarker`, `Version`, and `CommonPrefixes` in the same interleaved stream. Marker tests verify `computeStartFrom` chooses the local component to pass to filer listing and that directories before a marker are skipped unless the marker descends into them.

State and persistence behavior: version state is modeled as `filer_pb.Entry.Extended` metadata on `.versions` directory entries rather than live version files. The tests assert the production contract that latest-version cached metadata on the directory is enough for normal ListObjects projection without reading the version directory contents.

Dependencies and integration points: relies on `s3_constants` version metadata keys, `encoding/xml`, `filer_pb`, gRPC stream interfaces, and listing helpers in the S3 API package. It integrates with the versioned write path indirectly: `putVersionedObject` and `versionedFinalize` are expected to maintain the cached latest metadata this test consumes.

Risks: callback logic in some tests mirrors production behavior rather than invoking the HTTP response path, so XML/list accumulator regressions outside `doListFilerEntries` may need separate tests. The file is strong on directory traversal safety but less strong on real filer pagination because the mock is in-memory and simplified.

Test signals: clear regression signals cover no duplicate projection of `.versions` objects, delete-marker suppression, `maxKeys` truncation state, `.versions` traversal avoidance, leading-slash prefix normalization for version listings, XML interleaving, and key-marker start computation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_list_versioned_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_multipart.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_multipart.go

Purpose: this file implements HTTP handlers and small helpers for S3 multipart upload initiation, part upload, completion, abort, listing active uploads, and listing parts. It is the request-facing layer over lower-level multipart persistence functions in `filer_multipart.go` and the shared write pipeline in `putToFiler`.

Important APIs/types/functions: handlers include `NewMultipartUploadHandler`, `CompleteMultipartUploadHandler`, `AbortMultipartUploadHandler`, `ListMultipartUploadsHandler`, `ListObjectPartsHandler`, and `PutObjectPartHandler`. Helpers include `genUploadsFolder`, `getMultipartSSEAlgorithm`, `genPartUploadPath`, `generateUploadID`, `checkUploadId`, `isLowerHex`, `getBucketMultipartResources`, `getObjectResources`, `xmlDecoder`, `CompleteMultipartUpload`, `CompletedPart`, and `handleSSES3MultipartHeaders`.

Control flow: initiation validates key length, bucket existence or auto-create, table bucket path restrictions, versioning/object-lock headers, cache-control and expires formatting, and request metadata before delegating to `createMultipartUpload`. Completion validates bucket and object path, decodes the XML parts list under the request content length, validates `uploadId`, checks conditional headers against the target object, calls `completeMultipartUpload`, then returns version and checksum response headers when present. Part upload validates Content-MD5, bucket, upload ID binding, part number range, request data reader setup, upload existence, inherited SSE settings, and then stores the part through `putToFiler` with lifecycle TTL forced to `0`.

State and persistence behavior: active multipart upload state lives under `bucketDir(bucket)/.uploads/<uploadID>`, while parts are stored as unique files under that upload directory using `genPartUploadPath`. `uploadID` is cryptographically/path-bound by a SHA-1 object hash plus optional lowercase hex UUID suffix. SSE-KMS and SSE-S3 metadata required for parts is persisted on the upload entry and rehydrated into request headers for `putToFiler`. MPU parts deliberately do not receive lifecycle Expiration.Days volume TTL, because the transient part key is not the user-visible object.

Dependencies and integration points: integrates with AWS SDK `s3` input structs, SeaweedFS filer protobuf entries, shared S3 error handling, cache-control parsing, UUIDs, statistics counters, and SSE helpers. The lower-level `createMultipartUpload`, `completeMultipartUpload`, `abortMultipartUpload`, `listMultipartUploads`, and `listObjectParts` functions provide actual filer operations.

Risks: SSE metadata correctness is critical; missing or malformed base IV/key metadata causes hard internal errors for encrypted MPUs. Completion condition checks happen before final assembly, so races with concurrent object writes rely on `checkConditionalHeaders` and downstream finalization. Query parsing uses `Atoi` defaults and negative checks; malformed non-negative-looking values may collapse to zero in helper functions.

Test signals: this file has no local tests in the assignment, but nearby tests cover shared checksum detection, lifecycle TTL exclusion for MPU paths by code comments and TTL resolver tests, and version/list behavior affected by complete multipart writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_multipart.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_postpolicy.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_postpolicy.go

Purpose: this file implements browser-style S3 POST Object policy uploads. It parses multipart forms, validates policy signatures and conditions, normalizes the target key, forwards allowed form fields to the underlying write path, stores the uploaded file with `putToFiler`, and emits the S3 success response or redirect behavior.

Important APIs/types/functions: `PostPolicyBucketHandler` is the main handler. Helpers are `postPolicyReservedFormFields`, `applyPostPolicyFormHeaders`, `extractPostPolicyFormValues`, `validateFormFieldSize`, `getRedirectPostRawQuery`, and `IdentityAccessManagement.doesPolicySignatureMatch`.

Control flow: the handler obtains the bucket from mux vars, reads the multipart form with a 5 MiB field-memory limit, extracts exactly the canonical form headers and file part, substitutes `${filename}` in the key, validates and normalizes the key, validates table bucket restrictions, parses optional redirect URL, verifies V2 or V4 policy signature, decodes and checks policy conditions, enforces content-length range against the actual file part size, resolves content type, forwards selected form fields as request headers, computes lifecycle TTL using file size rather than multipart wire length, and calls `putToFiler`. On success it either redirects with bucket/key/etag query parameters or returns 201 XML, 200, or 204 depending on `success_action_status`.

State and persistence behavior: persistence is delegated to `putToFiler`, so POST uploads share chunk storage, ETag, SSE, ACL-derived file mode, tags, metadata, owner, and lifecycle TTL behavior with PUT. `extractPostPolicyFormValues` canonicalizes form fields into `http.Header`, validates individual field size, supports a text `file` form value when no file part exists, and uses `io.Seeker` to compute file size before rewinding the file part.

Dependencies and integration points: integrates with Gorilla mux, policy parsing/checking, IAM signature verification, `s3_constants.NormalizeObjectKey`, `validateTableBucketObjectPath`, lifecycle TTL resolver, and the shared PUT pipeline. Header forwarding maps `acl` to `x-amz-acl`, forwards cache/content metadata and all `x-amz-*` fields, and skips auth, target, and success-action fields.

Risks: only the first matching file part is used; unusual multipart implementations need compatible seekable file parts. Forwarding arbitrary `x-amz-*` fields is necessary for S3 compatibility but makes policy validation and reserved-field filtering security-sensitive. The handler validates policy before upload, which prevents redirect masking of access failures.

Test signals: the paired test file covers key normalization, filename substitution, form extraction, path construction, allowed/reserved header forwarding, traversal rejection, and a signed policy-violation path returning 403 without redirect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_postpolicy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_postpolicy_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_postpolicy_test.go

Purpose: this file tests the POST policy upload path, especially object-key normalization, multipart form extraction, safe path construction, forwarding of policy-approved form fields into PUT headers, traversal rejection, and correct error response ordering for policy failures.

Important APIs/types/functions: tests call `s3_constants.NormalizeObjectKey`, `extractPostPolicyFormValues`, `applyPostPolicyFormHeaders`, and `PostPolicyBucketHandler`. `canonicalFormValues` mirrors handler canonicalization with `http.CanonicalHeaderKey`. The end-to-end policy test initializes `IdentityAccessManagement`, signs a V4 POST policy using `getSigningKey`/`getSignature`, and drives the handler through `httptest`.

Control flow: early tests verify that keys with leading slash, duplicate slash, backslash, Windows-style separators, and `${filename}` substitution normalize to source-relative object keys. Form extraction tests build multipart bodies, parse them with `multipart.NewReader`, then confirm file name/content type/size and canonical `Key`. Header tests show `acl` becomes `X-Amz-Acl`, content metadata survives, arbitrary `x-amz-*` fields are forwarded, reserved signature/target/success fields are skipped, and resolved `Content-Type` is not overwritten by the helper. Handler tests build mux-vars requests for key extraction, traversal rejection, and signed policy mismatch.

State and persistence behavior: most tests do not write to filer; they exercise pre-persistence transformations. The policy-violation test pre-populates `BucketRegistry.metadataCache` to avoid live filer access and ensures failure occurs before upload. That test verifies no `Location` header is set on access denial.

Dependencies and integration points: depends on multipart form handling, `httptest`, Gorilla mux vars, IAM protobuf configuration, S3 signature helpers, bucket registry metadata, and S3 constants. It integrates directly with the POST handler and indirectly with PUT semantics by validating the request headers that will be seen by `putToFiler`.

Risks: many tests validate reconstructed path logic instead of instrumenting `putToFiler`, so they do not prove bytes are persisted at the expected filer path. Header forwarding tests are strong for canonicalized keys but should be maintained when new POST policy fields are added. Time-dependent signing uses current UTC with one-hour expiration, which is stable but still tied to clock correctness.

Test signals: strong signals cover issue-class path bugs, traversal defense returning `InvalidRequest`, reserved field leakage prevention, preservation of cache/content metadata, object-lock/SSE/tag forwarding through `x-amz-*`, and policy condition failure producing `403 AccessDenied` instead of a redirect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_postpolicy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_put.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_put.go

Purpose: this file is the central S3 object write implementation. It handles `PutObject`, directory markers, versioned and suspended-versioning writes, shared filer persistence, additional checksums, server-side encryption, object ownership, tags, storage class, object-lock metadata/default retention, conditional headers, routed write locking, orphan chunk cleanup, and read/write conditional helper logic.

Important APIs/types/functions: key exported or package-level pieces include object-lock validation sentinel errors, `hasExplicitEncryption`, `BucketDefaultEncryptionResult`, `SSEResponseMetadata`, `PutObjectHandler`, `withObjectWriteLock`, `putFinalize`, `putToFiler`, checksum maps and `detectRequestedChecksumAlgorithm`, `lookupHeaderOrQuery`, `parseRequestQuery`, `resolveFileMode`, `setEtag`, `setSSEResponseHeaders`, `filerErrorToS3Error`, `setObjectOwnerFromRequest`, `putSuspendedVersioningObject`, `updateIsLatestFlagsForSuspendedVersioning`, `putVersionedObject`, `updateLatestVersionInDirectory`, `extractObjectLockMetadataFromRequest`, default encryption/retention helpers, conditional header helpers, `deleteOrphanedChunks`, and storage-class helpers.

Control flow: `PutObjectHandler` validates digest, key length, table bucket path, conditional headers, bucket policy, cache/expires headers, and request body decoding. Small trailing-slash writes are treated as explicit directory markers via `mkdir`, with ETag and owner metadata. Other writes inspect versioning state and object-lock status, enforce overwrite protections for never-versioned buckets, then choose enabled versioning, suspended versioning, or regular write. All object-byte paths eventually call `putToFiler`.

State and persistence behavior: `putToFiler` streams data through MD5/additional checksum readers and SSE encryption, assigns volumes through filer, uploads chunks with 8 MiB chunking, verifies Content-MD5 and additional checksums, then creates a `filer_pb.Entry` containing chunks, attributes, TTL, MD5, and extended metadata. Extended metadata stores ETag, checksum name/value, owner, version ID, object lock fields, S3 expiry flag, user metadata, cache/content headers, storage class, object tags, and SSE metadata. Creation can be routed to the owner filer with transaction mutations or guarded by `withObjectWriteLock`; failures clean orphaned chunks when no entry was created.

Dependencies and integration points: this file connects HTTP requests, SeaweedFS operation chunk upload, filer gRPC `CreateEntry`, bucket config cache, bucket registry ownership, lifecycle TTL, object lock enforcement, route-write infrastructure, SSE helpers, lifecycle version metadata, and stats counters. Versioned writes store data under `<object>.versions/<versionFileName>` and finalize `.versions` latest metadata; suspended writes store the null version as the regular object and clear latest version pointers.

Risks: this is high-blast-radius code. Critical risks include races between conditional checks and create, inconsistent version metadata if finalize partially fails, irreversible volume TTL if lifecycle resolver is stale, SSE metadata corruption, orphan chunk leakage, and divergent behavior between routed and lock paths. The code mitigates with write locks/routed preconditions, best-effort version noncurrent stamps, default-retention validation, checksum verification, and orphan cleanup.

Test signals: assigned tests cover checksum algorithm detection from headers/query, lifecycle TTL resolver safety, object-lock config edge behavior, and list/version behavior that depends on version metadata. Broader coverage should include live filer integration for routed writes, SSE variants, object lock overwrite denial, suspended versioning, and failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_put.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_put_checksum_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_put_checksum_test.go

Purpose: this focused test file validates S3 additional checksum algorithm detection for PUT-style requests, including presigned URL behavior where AWS SDKs hoist checksum headers into query parameters.

Important APIs/types/functions: tests call `detectRequestedChecksumAlgorithm`, `parseRequestQuery`, and `lookupHeaderOrQuery`. They assert `ChecksumAlgorithm` enum values and canonical header names from `s3_constants`, plus `s3err.ErrInvalidRequest` for unsupported algorithms.

Control flow: `TestDetectRequestedChecksumAlgorithm` builds `httptest` PUT requests and mutates either headers or query parameters. Cases cover `x-amz-sdk-checksum-algorithm`, `x-amz-checksum-algorithm`, presigned query variants with mixed/lowercase keys, individual checksum value presence, unsupported `MD5`, and no checksum. `TestLookupHeaderOrQueryCaseInsensitive` verifies fallback query matching uses case-insensitive key comparison.

State and persistence behavior: no persistence is performed. The tests protect the pre-write detection phase that controls whether `putToFiler` wraps the data reader in a checksum hash and later stores `ExtChecksumAlgorithm` and `ExtChecksumValue` in filer entry metadata.

Dependencies and integration points: depends on `net/http/httptest`, S3 checksum constants, and S3 error codes. It integrates directly with `putToFiler` because that function parses the request query once, calls `detectRequestedChecksumAlgorithmQ`, verifies expected checksums, stores checksum metadata, and returns checksum response headers through `SSEResponseMetadata`.

Risks: the tests cover detection but not the full body checksum verification path or storage of checksum metadata. They also do not cover `x-amz-trailer` comma-separated values, CRC64NVME, CRC32C, or precedence when multiple checksum hints are present. Detection order is deterministic in production; tests should be expanded if API compatibility requires detailed precedence guarantees.

Test signals: strong regression signal for issue-style presigned URL checksum support and for case-insensitive query lookup. It ensures unsupported requested algorithms fail before upload rather than silently falling back to no checksum.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_put_checksum_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_retention.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_retention.go

Purpose: this file implements S3 Object Lock retention get/put handlers. It is a thin HTTP layer over object-lock availability checks, XML parsing/validation, governance bypass evaluation, and lower-level retention metadata update/read functions.

Important APIs/types/functions: `PutObjectRetentionHandler` parses and writes retention, while `GetObjectRetentionHandler` reads retention. Both use `s3_constants.GetBucketAndObject`, `handleObjectLockAvailabilityCheck`, query `versionId`, `evaluateGovernanceBypassRequest`, `parseObjectRetention`, `ValidateRetention`, `setObjectRetention`, `getObjectRetention`, `mapValidationErrorToS3Error`, and stats collection.

Control flow: PUT verifies object lock availability for the bucket, reads optional version ID, determines whether governance bypass is allowed, parses XML retention from the request body, validates mode and retain-until values, then calls `setObjectRetention`. Not-found variants map to `NoSuchKey`; active compliance/governance protection maps to access denied; success sets `x-amz-version-id` when provided and returns HTTP 200. GET performs the same availability/version lookup, calls `getObjectRetention`, maps missing object/version to `NoSuchKey`, missing retention config to `ObjectLockConfigurationNotFoundError`, marshals retention XML, and writes an XML response.

State and persistence behavior: this file itself does not manipulate filer entries directly. Persistence is delegated to object-lock helpers that store retention metadata in object/version extended attributes. The handlers enforce that retention APIs are only exposed for object-lock capable buckets, which implies versioning semantics.

Dependencies and integration points: depends on object-lock validation helpers defined across the S3 API package, XML encoding/decoding, S3 error mapping, and stats. It integrates with `put.go` because object writes also set explicit or default object-lock retention metadata, and with governance bypass permission checks used for overwrite/delete protection.

Risks: error mapping is compatibility-sensitive; clients expect distinct `MalformedXML`, `InvalidRetentionPeriod`, `AccessDenied`, `NoSuchKey`, and object-lock-configuration errors. Governance bypass depends on both a request header and permission evaluation outside this file. XML marshal/write errors after status headers can only be logged, so response-body write failures cannot be converted to S3 errors.

Test signals: no local test file is assigned for these handlers, but object-lock validation and bugfix tests in this subset exercise adjacent metadata availability logic. Additional integration tests should cover version-specific retention updates, missing retention response codes, and governance bypass denial.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_retention.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_tagging.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_tagging.go

Purpose: this file implements GET, PUT, and DELETE object tagging handlers for regular and versioned objects. It converts between S3 tagging XML and SeaweedFS extended attributes using the shared `S3TAG_PREFIX` convention.

Important APIs/types/functions: handlers are `GetObjectTaggingHandler`, `PutObjectTaggingHandler`, and `DeleteObjectTaggingHandler`. They use `Tagging`, `FromTags`, `ValidateTags`, `isVersioningConfigured`, `getSpecificObjectVersion`, `getLatestObjectVersion`, `getTags`, `setTags`, `rmTags`, `filer_pb.UpdateEntry`, and table bucket path validation.

Control flow: all handlers parse bucket/object and reject invalid table-bucket paths. GET checks versioning configuration; for versioned buckets it resolves a specific or latest version, rejects delete markers, extracts `S3TAG_PREFIX` extended attributes, and returns XML. For non-versioned buckets it delegates to `getTags`. PUT reads and XML-unmarshals a bounded body, validates tags, resolves versioning, then either delegates to `setTags` for non-versioned objects or mutates the resolved entry's extended attributes and updates the correct filer directory. DELETE follows the same version resolution and either calls `rmTags` or removes prefixed extended attributes and updates the entry.

State and persistence behavior: non-versioned tag state is managed through helper functions over the regular object entry. Versioned tag state is embedded in the target version entry's `Extended` map and persisted with `UpdateEntry`; version ID `null` maps to the bucket directory, while real version IDs map to `<bucketDir>/<object>.versions`. Latest-version operations infer storage location from `ExtVersionIdKey`.

Dependencies and integration points: integrates with versioned object resolution, delete-marker semantics, filer gRPC updates, XML tag parsing, and `s3_constants.AmzObjectTagging` used by `putToFiler` when tags arrive during upload. It shares the same tag prefix storage convention as `filer_util_tags.go`.

Risks: update-directory derivation uses the object string directly; callers rely on normalized object paths from routing. Concurrent tag updates can overwrite unrelated extended attribute mutations because the handler updates the whole entry returned earlier. The versioned path has duplicated directory-selection logic in PUT and DELETE, increasing maintenance risk. DELETE returns success when no tags exist, which matches S3-style idempotence.

Test signals: this subset does not include a direct tagging test file, but `put.go` stores upload-time tags and post-policy tests ensure `x-amz-tagging` can be forwarded to the write path. Dedicated tests should cover versioned tag update/delete, delete-marker rejection, and concurrent extended-metadata preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_tagging.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_lifecycle_ttl.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_lifecycle_ttl.go

Purpose: this file implements a conservative fast path that converts eligible S3 lifecycle `Expiration.Days` rules into SeaweedFS volume TTL seconds for new non-versioned object writes. It avoids per-write lifecycle XML evaluation by storing a compact resolver on bucket configuration.

Important APIs/types/functions: `secondsPerDay`, `LifecycleTTLResolver`, `ttlRule`, `NewLifecycleTTLResolver`, `(*LifecycleTTLResolver).Resolve`, and `S3ApiServer.lifecycleTTLForObjectWrite`.

Control flow: resolver construction returns nil for versioned buckets or empty rules. It filters out nil, disabled, non-Expiration.Days, tag-filtered, and int32-overflowing rules. Eligible rules keep prefix, TTL seconds, and optional size bounds, then are stable-sorted by ascending TTL seconds so the shortest applicable expiration wins. `Resolve` walks rules, checks prefix and size predicates, skips unknown-size objects for size-filtered rules, and returns the first TTL seconds match or zero. The S3 server wrapper fetches bucket config and resolves against cached `LifecycleTTL`.

State and persistence behavior: this file does not persist lifecycle config; it derives hot-path state from parsed bucket config. The TTL value is later written into `filer_pb.Entry.Attributes.TtlSec` and `AssignVolumeRequest.TtlSec` by `putToFiler`, and `SeaweedFSExpiresS3` is recorded in extended metadata when TTL is applied.

Dependencies and integration points: depends on `s3lifecycle.Rule` and bucket config loading. It integrates with `populateBucketConfigDerivedFields`, `PutObjectHandler`, `PostPolicyBucketHandler`, and `putToFiler`. MPU parts and copy parts intentionally pass zero TTL and bypass this resolver.

Risks: volume TTL is irreversible and applies at storage level, so eligibility must stay conservative. Tag-filtered rules are excluded because tags can change after write. Versioned/object-lock buckets are excluded because TTL volumes could delete noncurrent versions together. Overflowing long policies are deferred to the lifecycle worker rather than capped. Size filters require accurate object size; POST policy explicitly passes file part size instead of multipart wire size.

Test signals: the paired tests cover nil/versioned behavior, tag-filter exclusion, disabled/non-expiration filtering, prefix match, overlapping shortest-expiration precedence, overflow deferral, size filters, nil receiver safety, cache-derived resolver refresh, object-lock-as-versioned, and explicit fast-path opt-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_lifecycle_ttl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_lifecycle_ttl_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_lifecycle_ttl_test.go

Purpose: this file validates the lifecycle TTL fast-path resolver and the bucket-config derived-field wiring that enables or disables it. It documents safety constraints around versioning, object lock, mutable tags, overflow, size filters, and stale cache refresh.

Important APIs/types/functions: helper `enabledRule` builds enabled `s3lifecycle.Rule` values, `mustResolver` constructs non-versioned resolvers, and tests call `NewLifecycleTTLResolver`, `Resolve`, and `populateBucketConfigDerivedFields`. Benchmarks measure nil, one-rule, and five-rule no-match resolver paths.

Control flow: constructor tests assert nil for empty rules and versioned buckets, exclusion of tag-filtered/disabled/non-expiration rules, and preservation of plain eligible rules. Resolve tests check prefix matching, overlapping shortest-expiration precedence, overflow deferral to the worker, overflow skipping while shorter rules still fire, size greater-than behavior, unknown-size skip, and nil receiver zero. Derived-field tests mutate `BucketConfig.Entry.Extended` lifecycle XML and opt-in flags across add/replace/delete transitions to ensure resolver state refreshes and does not linger after lifecycle removal.

State and persistence behavior: tests simulate persisted bucket config through `filer_pb.Entry.Extended` keys: lifecycle XML, object lock enabled flag, and `ExtLifecycleTtlFastPathKey`. They do not write filer state, but they validate the in-memory cache object (`BucketConfig.LifecycleTTL`) that later determines persisted object TTL on writes.

Dependencies and integration points: depends on `s3lifecycle`, `filer_pb`, `s3_constants`, and bucket config parsing in `populateBucketConfigDerivedFields`. The tests directly protect `PutObjectHandler` and `PostPolicyBucketHandler` from applying stale or unsafe volume TTL.

Risks: benchmarks are micro-level and do not cover bucket-config cache invalidation under concurrent metadata subscription updates. XML parsing coverage is narrow but targets the derived resolver transitions most likely to cause irreversible stale TTL application. Time is not used directly in resolver tests, making them deterministic.

Test signals: strong safety signal for no fast path unless explicitly opted in, no fast path for object-lock/versioned buckets, no tag-filter TTL, shortest expiration wins, long retention policies are not capped, and stale resolver removal after lifecycle XML deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_lifecycle_ttl_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_lock_fix_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_lock_fix_test.go

Purpose: this regression test documents a Veeam interoperability fix for Object Lock configuration detection. The bug was that a bucket entry with nil extended attributes could be treated as missing Object Lock configuration before checking whether Object Lock was actually enabled, causing clients to conclude Object Lock was unsupported.

Important APIs/types/functions: `TestVeeamObjectLockBugFix` builds `BucketConfig` values around `filer_pb.Entry.Extended` and checks the same enabled-flag logic used by object-lock configuration handling. It relies on `s3_constants.ExtObjectLockEnabledKey` and `s3_constants.ObjectLockEnabled`.

Control flow: the first subtest models a bucket with `Extended: nil` and verifies the enabled calculation safely returns false rather than panicking or misclassifying. The second sets the extended flag to string `"true"` and expects enabled. The third sets the flag to the canonical `ObjectLockEnabled` constant and expects enabled.

State and persistence behavior: the test models bucket-level persisted metadata as extended attributes on the bucket entry. It does not call the actual handler or mutate storage. The persistence contract under test is that both legacy boolean `"true"` and canonical enabled values are recognized, while nil metadata means not enabled.

Dependencies and integration points: this test is adjacent to `GetObjectLockConfigurationHandler`, bucket config parsing, `isObjectLockEnabled`/availability helpers, object-lock write validation in `put.go`, and retention handlers. It is specifically motivated by backup software probing bucket object-lock support.

Risks: because the test duplicates detection logic instead of invoking the production handler/helper, it can drift if production logic changes. It is useful as documentation of expected semantics but weaker than an integration test that calls the handler with bucket cache entries for nil, false, true, and canonical enabled cases.

Test signals: focused signal for nil extended attributes and dual accepted enabled encodings. It protects against reintroducing `NoSuchObjectLockConfiguration` behavior for enabled buckets whose metadata representation is sparse or legacy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_lock_fix_test.go -->
