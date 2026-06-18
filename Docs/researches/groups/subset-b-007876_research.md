# subset-b-007876 Research

Grouped research for SeaweedFS S3 API handler and regression-test files. Each section preserves its source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_handlers.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_handlers.go

## Purpose
Provides shared S3 API server helpers for filer gRPC access, HTTP success/error responses, data-center reporting, URL adjustment, and `Content-Md5` validation. The central behavior is `S3ApiServer.WithFilerClient`, which gives S3 handlers a `filer_pb.SeaweedFilerClient` while hiding direct gRPC connection setup and multi-filer failover.

## Important APIs, Types, And Functions
`WithFilerClient(streamingMode, fn)` is the package-level filer access facade used by many S3 handlers and helper routines. `withFilerClientFailover(preferred, streamingMode, fn)` orders preferred, current, healthy, then unhealthy filer addresses and calls `pb.WithGrpcClient` for each candidate. `AdjustedUrl`, `GetDataCenter`, `writeSuccessResponseXML`, `writeSuccessResponseXMLBytes`, `writeSuccessResponseEmpty`, `writeFailureResponse`, and `validateContentMd5` are small common helpers. The compile-time `var _ = filer_pb.FilerClient(&S3ApiServer{})` asserts that `S3ApiServer` satisfies the filer client interface expected by `filer_pb.List`.

## Control Flow
`WithFilerClient` uses the newer `s3a.filerClient` path when initialized, otherwise falls back to a direct connection to `s3a.getFilerAddress()` for tests or startup. Failover builds a de-duplicated candidate list from a preferred address, the current filer, and all configured filers. Preferred is always tried first, even if health tracking says it is unhealthy, because routed read-after-write requests need an authoritative answer from the key owner. Non-preferred candidates are split into healthy and unhealthy using `ShouldSkipUnhealthyFiler` and owner-reachability state, then tried in that order. A successful non-preferred failover records success and can promote the current filer. `filer_pb.ErrNotFound` is treated as authoritative and stops failover, while transport-like failures are recorded and wrapped after all candidates fail.

## State And Persistence
The helper mutates only in-memory client state: current filer selection, filer health records, and recently-unreachable owner tracking. It does not write persistent configuration. Response helpers write HTTP response headers/bodies and S3 access logs through `s3err.PostLog`.

## Dependencies And Integration Points
This file connects S3 handlers to `pb.WithGrpcClient`, `filer_pb.NewSeaweedFilerClient`, `S3ApiServer.filerClient`, glog, and S3 XML/error response utilities. It is a core integration point for any S3 path that needs filer metadata or entry mutation.

## Risks And Test Signals
The main risks are failover masking authoritative not-found responses, stale current-filer promotion, inconsistent behavior between initialized and direct fallback modes, and candidate ordering when preferred owners are outside the static filer list. Tests should cover `ErrNotFound` no-fanout semantics, preferred-first routing, current-filer promotion after successful failover, unhealthy deferral, and empty or invalid `Content-Md5` handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_iam_oidc_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_iam_oidc_test.go

## Purpose
Tests the embedded IAM API's OpenID Connect provider actions against an in-memory IAM manager. It verifies provider listing, lookup, creation, mutation, deletion, read-only filtering, and persistence-like behavior through the configured IAM stores.

## Important APIs, Types, And Functions
`stubIntegration` supplies only `GetIAMManager`, deliberately panicking through embedded `IAMIntegration` for unexpected integration calls. `newOIDCTestAPI` creates an `integration.IAMManager` with STS OIDC providers for Google and GitHub, memory policy and role stores, and wires it into `EmbeddedIamApiForTest`. The tests exercise `ExecuteAction` with IAM query actions such as `ListOpenIDConnectProviders`, `GetOpenIDConnectProvider`, `CreateOpenIDConnectProvider`, `DeleteOpenIDConnectProvider`, `AddClientIDToOpenIDConnectProvider`, `RemoveClientIDFromOpenIDConnectProvider`, `UpdateOpenIDConnectProviderThumbprint`, `TagOpenIDConnectProvider`, and `UntagOpenIDConnectProvider`.

## Control Flow
Each test constructs IAM-style `url.Values`, calls `api.ExecuteAction(context, values, true, requestID)`, type-checks the returned response, and inspects response fields or IAM errors. Creation tests then fetch the created provider by ARN to confirm client IDs, thumbprints, and tags were stored. Mutation tests modify an existing static provider, fetch it, and verify idempotent add/remove behavior. Read-only tests set `api.readOnly` and confirm list is allowed while mutating OIDC actions are denied.

## State And Persistence
State is memory-backed but flows through the IAM manager and embedded API stores as production code would. Static provider configuration is initialized from `STSConfig.Providers`; dynamically-created providers and mutated client IDs, thumbprints, and tags are stored through the manager's configured in-memory stores.

## Dependencies And Integration Points
The tests integrate `weed/iam`, `weed/iam/integration`, STS provider configuration, policy engine defaults, embedded IAM API dispatch, and AWS-style IAM XML/query action response types. They indirectly validate ARN formatting using the configured account id `111122223333`.

## Risks And Test Signals
These tests signal regressions in action dispatch, read-only action classification, provider ARN parsing, duplicate conflict detection, required input validation, thumbprint format validation, tag round-tripping, and idempotency. Remaining risk is that they use memory stores and synthetic config, so external persistence backends, real OIDC discovery, and XML wire formatting are not covered here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_iam_oidc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_implicit_directory_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_implicit_directory_test.go

## Purpose
Documents and tests the logic behind `HeadObjectHandler` implicit-directory compatibility. The goal is to make clients such as s3fs and PyArrow treat directory markers with children as directories instead of zero-byte files.

## Important APIs, Types, And Functions
The tests model `HeadObjectHandler` logic and `hasChildren` behavior without booting a full S3 server. `TestImplicitDirectoryBehaviorLogic` covers the boolean decision matrix for versioning state, trailing slash, file size, directory flag, and child presence. `TestHasChildrenLogic` models the list-one-child helper. `TestImplicitDirectoryEdgeCases`, `TestImplicitDirectoryIntegration`, and `BenchmarkHasChildrenCheck` record expected manual/integration scenarios.

## Control Flow
The main table-driven test computes `isZeroByteFile`, `isActualDirectory`, and `shouldReturn404` using the same rules described in the handler: for non-versioned buckets and paths without trailing slash, actual directories return 404, and zero-byte files with children return 404. Explicit trailing-slash requests and versioned buckets skip the implicit-directory 404 path. The `hasChildren` logic table treats a successful list response as true and `io.EOF` as false.

## State And Persistence
No persistent state is created. Test data simulates filer entry attributes and list results. The skipped integration test points to `test/s3/parquet` for a full-server workflow.

## Dependencies And Integration Points
The file depends only on Go testing, `io`, and `filer_pb.ListEntriesResponse`. Its behavioral target is `s3api_object_handlers.go`, especially `HeadObjectHandler` and `hasChildren`.

## Risks And Test Signals
The tests are lightweight logic guards rather than end-to-end handler tests, so they will not catch drift in actual filer listing, HTTP status writing, or versioning lookup. They do provide clear signals for the intended s3fs/PyArrow behavior: directory markers with children must force 404 on bare `HEAD`, legitimate empty files remain 200, and explicit `dataset/` requests remain accessible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_implicit_directory_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_inline_policy_condition_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_inline_policy_condition_test.go

## Purpose
Regression tests inline IAM policy condition enforcement for S3 authorization, especially `aws:SourceIp` conditions on user and group inline policies. The file exists to prevent inline policies from being flattened into legacy action lists that lose condition blocks.

## Important APIs, Types, And Functions
`inlineCondPolicyDoc(cidr)` builds an S3 allow policy on `inline-cond-bucket` with an `IpAddress` condition. `inlineCondRequest` creates a synthetic HTTP request with `RemoteAddr` set to loopback. `seedInlineCondUser` adds user `alice` and a credential to `api.mockConfig`, saves it through the credential manager, reloads IAM, and returns the loaded identity. Tests call `PutUserPolicy`, `PutGroupPolicy`, `ListGroupPolicies`, `GetGroupPolicy`, `DeleteGroupPolicy`, `credentialManager.PutUserInlinePolicy`, `refreshIAMConfiguration`, and `VerifyActionPermission`.

## Control Flow
The user-policy tests install a nonmatching CIDR and expect `ErrAccessDenied`, then install a matching loopback CIDR and expect `ErrNone`. A discriminator test replaces a matching policy with a nonmatching one for the same user and action to prove the condition, not the legacy action list, controls the decision. The group test creates group `devs`, adds `alice`, puts a group inline policy, verifies deny and allow after CIDR replacement, confirms list/get round-trip includes the condition block, deletes the policy, and confirms access is revoked. The reload test writes a parsed `policy_engine.PolicyDocument` directly to the credential manager and reloads IAM to simulate process restart.

## State And Persistence
State is stored in the embedded test credential manager and in-memory IAM indexes. The tests exercise reload boundaries so persisted inline policies must be re-registered into the policy engine after `LoadS3ApiConfigurationFromCredentialManager`.

## Dependencies And Integration Points
The file integrates the embedded IAM test API, protobuf S3 configuration, policy-engine parsing, S3 action constants, S3 error constants, group credential APIs, HTTP request source-IP extraction, and identity authorization.

## Risks And Test Signals
Strong signals include condition-aware allow/deny decisions, group inline policy implementation, list/get/delete round-trips, and reload behavior. Risks not covered include other condition keys, IPv6, forwarded source headers, managed policies, concurrent IAM updates, and non-memory stores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_inline_policy_condition_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_internal_lifecycle.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_internal_lifecycle.go

## Purpose
Implements the internal lifecycle delete executor called by lifecycle workers. It re-fetches live object state, verifies an expected identity witness, enforces object-lock protections, dispatches expiration/noncurrent/delete-marker/abort-MPU actions, and classifies results into worker outcomes.

## Important APIs, Types, And Functions
`LifecycleDelete` is the gRPC-facing entry point for `s3_lifecycle_pb.LifecycleDeleteRequest`. `lifecycleDispatch` handles expiration, noncurrent, newer-noncurrent, expired-delete-marker, and defensive unknown action paths. `lifecycleAbortMPU` validates and removes multipart upload init directories. `checkSoleSurvivorMarker` prevents unsafe expired-delete-marker deletion if the marker is not the sole/latest surviving version or if a null version exists. `isCurrentLatestVersion`, `computeEntryIdentity`, `identityMatches`, `entryUsesMetadataOnlyDelete`, `recordMetadataOnlyIf`, `done`, `noopResolved`, `blocked`, and `retryLater` are supporting helpers.

## Control Flow
`LifecycleDelete` rejects empty requests as `BLOCKED`, routes `ABORT_MPU` before object fetch, then fetches the object/version. Not-found variants become `NOOP_RESOLVED`; other fetch errors become `RETRY_LATER`. If the live entry identity differs from `ExpectedIdentity`, the request is stale and becomes `NOOP_RESOLVED`. Object lock is enforced without bypass. Expiration of current versions branches on bucket versioning: enabled creates a delete marker, suspended best-effort deletes the null version then creates a delete marker, and unversioned deletes the regular object. Noncurrent and expired-marker actions require `VersionId`, guard against deleting the current latest version, optionally re-check sole-survivor marker state, then delete the specific version. Metadata-only TTL-stamped entries increment a Prometheus counter instead of forcing per-chunk delete accounting.

## State And Persistence
The executor mutates filer state by creating delete markers, deleting unversioned objects, deleting specific version files, and recursively removing `.uploads/<upload_id>` directories. It reads versioning state, `.versions/` directory metadata, `ExtLatestVersionIdKey`, object-lock extended attributes, object chunks, object attributes, and extended metadata. It updates only metrics locally.

## Dependencies And Integration Points
It depends on `filer_pb`, `s3_lifecycle_pb`, S3 versioning constants, lifecycle hashing, object-lock enforcement, versioned object helpers, delete marker helpers, filer listing, `rm`, `exists`, and stats collection. It is the server side of the lifecycle worker contract: worker retries and budgets depend on the returned outcome and reason strings.

## Risks And Test Signals
Key risks are stale event deletion, current-version deletion from a noncurrent action, path traversal during abort-MPU, object-lock bypass, delete-marker races while `.versions/` latest-pointer metadata is being updated, and metadata-only counter drift. Tests should verify outcome classification, malformed MPU path blocking, identity CAS fields, latest-pointer guards, sole-survivor marker checks, object-lock skips, and metadata-only metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_internal_lifecycle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_internal_lifecycle_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_internal_lifecycle_test.go

## Purpose
Unit tests lifecycle delete helper invariants that do not require a live filer. Coverage focuses on identity witnesses, extended-metadata hashing, defensive blocked outcomes, abort-MPU path validation, metadata-only detection, and Prometheus metric increments.

## Important APIs, Types, And Functions
Tests directly call `computeEntryIdentity`, `s3lifecycle.HashExtended`, `identityMatches`, `LifecycleDelete`, `lifecycleDispatch`, `entryUsesMetadataOnlyDelete`, `recordMetadataOnlyIf`, and local `contains`. They use `filer_pb.Entry`, `FuseAttributes`, `FileChunk`, `s3_lifecycle_pb.EntryIdentity`, `LifecycleDeleteRequest`, and `testutil.ToFloat64` for metrics.

## Control Flow
Identity tests construct entries with mtimes, sizes, chunks, and extended metadata and assert exact fields and comparison behavior. Hash tests ensure map order does not affect hashes, delimiter-like payloads do not collide, and nil/empty maps produce empty hashes. Lifecycle dispatch tests assert empty requests, malformed MPU paths, routed-after-fetch `ABORT_MPU`, unknown action kinds, and missing version ids all produce `BLOCKED` without gRPC errors. Metadata-only tests check nil safety, `TtlSec > 0`, negative TTL rejection, counter increments for enabled calls, no-op when disabled, nil request safety, and empty rule-hash labeling.

## State And Persistence
No filer state is persisted. The only shared state touched is the global `S3LifecycleMetadataOnlyCounter`; tests isolate series by unique bucket labels to avoid cross-test interference.

## Dependencies And Integration Points
These tests tie lifecycle executor behavior to `s3lifecycle.HashExtended`, Prometheus stats, lifecycle protobuf outcomes, and filer entry attribute semantics. They are guardrails for worker-facing classification rather than integration tests of actual deletes.

## Risks And Test Signals
Strong signals include CAS field completeness, hash stability, safe nil handling, path traversal rejection, and metadata-only metric behavior. Missing coverage includes real versioning state, filer errors, object-lock enforcement, successful delete marker creation, and sole-survivor marker races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_internal_lifecycle_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_list_normalization_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_list_normalization_test.go

## Purpose
Tests that list prefixes and object keys use consistent normalization, preventing mismatches when clients send leading slashes, duplicate slashes, or backslashes.

## Important APIs, Types, And Functions
`TestPrefixNormalizationInList` calls `s3_constants.NormalizeObjectKey` for table-driven prefixes. `TestListPrefixConsistency` checks that a normalized object key starts with a normalized list prefix. The local `startsWithPrefix` helper normalizes the prefix and handles the empty-prefix case.

## Control Flow
The first test verifies simple prefix preservation, leading slash stripping, duplicate slash cleanup, and backslash conversion to forward slash. The second test normalizes a representative parquet object key and asserts it matches a conventional prefix.

## State And Persistence
No state is persisted. The file is pure normalization logic.

## Dependencies And Integration Points
The tests depend on `weed/s3api/s3_constants.NormalizeObjectKey`, which is used by S3 write/list code to map external S3 keys onto filer paths.

## Risks And Test Signals
The tests catch regressions that would make objects written under one normalized form disappear from list results using another form. `startsWithPrefix` slices by prefix length without first checking length, so the test helper assumes the object key is at least as long as the prefix; adding shorter-key cases would need a safer helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_list_normalization_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_multipart_path_validation_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_multipart_path_validation_test.go

## Purpose
Tests multipart upload id validation for object-bound generated IDs and path traversal rejection.

## Important APIs, Types, And Functions
`TestCheckUploadIDRequiresGeneratedFormat` calls `S3ApiServer.generateUploadID(object)` and `S3ApiServer.checkUploadId(object, uploadID)`. It covers the legacy hash-only format and the newer `hash_randomhex` format.

## Control Flow
For object `dir/object`, the test accepts the generated hash and the current hash plus a 32-character lowercase hex suffix. It rejects wrong object hashes, arbitrary suffixes, uppercase suffixes, short/long suffixes, slash and backslash traversal, suffix traversal, and NUL-containing input.

## State And Persistence
No state is persisted. The test validates local string/path checks before any multipart upload directory access can happen.

## Dependencies And Integration Points
The file targets multipart upload handlers that derive paths below `.uploads` from user-supplied upload ids. It protects callers that later pass upload ids through path-cleaning helpers.

## Risks And Test Signals
The main signal is that upload id validation remains object-bound and traversal-safe. Additional coverage could include URL-escaped traversal, Unicode separators, and direct handler tests for abort/complete multipart requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_multipart_path_validation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_multipart_ssekms_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_multipart_ssekms_test.go

## Purpose
Regression tests multipart SSE-KMS reader preparation. They pin the contract that malformed per-chunk metadata is rejected before any volume-server fetch starts, and that chunks are ordered by object offset before lazy streaming.

## Important APIs, Types, And Functions
Tests call `buildMultipartSSEKMSReader`, `SerializeSSEKMSMetadata`, and inspect the returned `*lazyMultipartChunkReader`. They construct `SSEKMSKey` values with `KeyID`, `EncryptedDataKey`, and `IV`, and `filer_pb.FileChunk` values with `SSEType_SSE_KMS` and `SseMetadata`.

## Control Flow
Bad-IV cases create metadata with nil, empty, short, or long IV values and assert an error containing `invalid` while a mock fetch function remains uncalled. Missing metadata uses a valid first chunk and an invalid second chunk to ensure preparation validates all chunks before fetching even the first. Malformed JSON metadata similarly must fail without fetch. The ordering test builds chunks in shuffled offset order, uses a fetch function that must not run during prep, type-asserts the returned reader, and checks the prepared chunk file ids are `c0`, `c1`, `c2`.

## State And Persistence
No persistent state is written. The test observes in-memory booleans and maps to prove fetch functions are not invoked prematurely.

## Dependencies And Integration Points
This file targets the SSE-KMS branch in `s3api_object_handlers.go`, especially the lazy multipart reader and upfront metadata validation added to avoid opening HTTP bodies for chunks that cannot be decrypted.

## Risks And Test Signals
Strong signals include no network fetch before metadata validation, IV length validation, JSON deserialization errors surfacing at preparation time, and stable offset ordering without mutating the caller's chunk order. It does not verify real KMS unwrapping or decrypted byte correctness, which are covered elsewhere or require provider setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_multipart_ssekms_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_nextmarker_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_nextmarker_test.go

## Purpose
Tests marker construction for S3 list continuation when requests use nested prefixes. It guards a regression where `NextMarker` lost intermediate prefix components.

## Important APIs, Types, And Functions
`TestNextMarkerWithNestedPrefix` and `TestNextMarkerWithCommonPrefix` simulate the string-building logic used by list operations. They use `requestDir`, `prefix`, `nextMarkerFromDoList`, and `lastCommonPrefixName` inputs and compare against expected final markers via `testify/assert`.

## Control Flow
Object marker tests prepend `requestDir` and, when present, `prefix` before the marker returned by lower-level listing. Common-prefix tests perform the same reconstruction but add the trailing slash required for prefix markers. Cases cover requestDir plus prefix, requestDir only, prefix without requestDir, and deeper nesting.

## State And Persistence
No state is persisted. These are pure string construction regression tests.

## Dependencies And Integration Points
The behavior corresponds to marker assembly inside S3 list handling, particularly `listFilerEntries`/`doList` interactions where lower layers may return names relative to the listed directory.

## Risks And Test Signals
The tests catch continuation-token/marker drift that can cause clients to skip, repeat, or fail pages under nested prefixes. They are simulations, so a direct handler test with actual filer entries would provide stronger coverage for delimiter and encoding interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_nextmarker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers.go

## Purpose
Implements core S3 object read metadata and streaming behavior: `GET Object`, `HEAD Object`, range handling, directory marker compatibility, direct volume-server streaming, server-side encryption decryption, multipart part selection, response headers, remote object caching, and shared object metadata helpers.

## Important APIs, Types, And Functions
Primary handlers are `GetObjectHandler` and `HeadObjectHandler`. Streaming paths are `streamFromVolumeServers`, `streamFromVolumeServersWithSSE`, `streamDecryptedRangeFromChunks`, `getEncryptedStreamFromVolumes`, `fetchFullChunk`, `fetchChunkViewData`, and `createEncryptedChunkReader`. SSE helpers include `detectPrimarySSEType`, `addSSEResponseHeadersFromEntry`, `createMultipartSSECDecryptedReaderDirect`, `createMultipartSSEKMSDecryptedReaderDirect`, `buildMultipartSSEKMSReader`, `createMultipartSSES3DecryptedReaderDirect`, `buildMultipartSSES3Reader`, `decryptSSECChunkView`, `decryptSSEKMSChunkView`, `decryptSSES3ChunkView`, `preparedMultipartChunk`, and `lazyMultipartChunkReader`. Metadata helpers include `parseAndValidateRange`, `adjustRangeForPart`, `newListEntry`, `setResponseHeaders`, `addObjectLockHeadersToResponse`, `getMultipartInfo`, `fetchObjectEntry`, and remote-cache helpers.

## Control Flow
`GetObjectHandler` validates table-bucket object paths, serves SOSAPI virtual objects, handles explicit directory-object requests, evaluates conditional headers, resolves versioned or null-version entries, reuses conditional-check entries when possible, caches remote-only entries, rechecks tag-based policies against the resolved entry, rewrites `Range` for `partNumber`, detects SSE type, and streams from volume servers. `HeadObjectHandler` follows similar version and metadata resolution but writes headers only, applies implicit-directory 404 behavior for non-versioned zero-byte markers or directories without trailing slash, validates SSE-C headers when required, adds SSE/object-lock headers, and supports multipart `x-amz-mp-parts-count`.

`streamFromVolumeServers` validates range and chunk availability before writing headers, serves inline content, handles empty objects, triggers remote caching when entries are remote-only and chunkless, resolves chunk manifests, builds `ChunkReadAt` from `readerCache`, writes range or full-response headers, then copies through a counting writer. `streamFromVolumeServersWithSSE` validates range and decryption key metadata, sets headers, then uses range-aware per-chunk decryption for range requests or full-object readers for non-range requests. Multipart SSE readers validate per-chunk metadata and IVs upfront, then lazily fetch and decrypt one chunk at a time to avoid holding many idle HTTP bodies.

## State And Persistence
The handlers primarily read filer entries and chunks, but remote-cache helpers can mutate filer state through `CacheRemoteObjectToLocalCluster` and by installing returned chunks into the in-memory entry used for the request. Response state includes headers such as `ETag`, `Last-Modified`, `Content-Length`, `Content-Range`, SSE headers, object-lock headers, tag count, checksum headers when requested, and passthrough response overrides. Traffic and TTFB metrics are recorded. No object metadata is updated by GET/HEAD themselves.

## Dependencies And Integration Points
This file integrates S3 routing constants, conditional-header logic, bucket policy rechecks, versioning helpers, object-lock metadata, SOSAPI virtual objects, `filer` chunk resolution and reader cache, volume-server JWTs, shared HTTP client pooling, SSE-C/SSE-KMS/SSE-S3 crypto helpers, remote storage cache gRPC, IAM owner display lookup for list entries, and S3 XML/error response helpers.

## Risks And Test Signals
Major risks include double-writing error responses after headers are sent, range edge cases on empty or inline objects, chunk-manifest resolution failures, SSE metadata corruption causing mid-stream failures, mixed encryption chunk types, remote-only cache timeouts, stale version/null-version resolution, tag-policy recheck drift, and implicit-directory compatibility regressions. Existing tests in this subset cover implicit directories, multipart upload id validation, SSE-KMS upfront validation, list normalization, and next-marker construction; related tests elsewhere cover SSE-S3 lazy readers, remote storage, stats, and integration behavior. Additional high-value tests would directly exercise GET/HEAD with versioned delete markers, encrypted ranged reads across chunk boundaries, partNumber plus Range, checksum headers on ranged versus full GET, and remote-cache 503 retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_acl.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_acl.go

## Purpose
Implements S3 object ACL retrieval and update handlers. It resolves regular or versioned object entries, formats ACL responses from entry metadata, enforces owner/admin/WRITE_ACP permissions, parses canned/XML ACL requests, and persists ACL metadata back to the filer entry.

## Important APIs, Types, And Functions
`GetObjectAclHandler` handles `GET Object acl`; `PutObjectAclHandler` handles `PUT Object acl`. They use `s3_constants.GetBucketAndObject`, `validateTableBucketObjectPath`, `checkBucket`, `isVersioningConfigured`, `getSpecificObjectVersion`, `getLatestObjectVersion`, `fetchObjectEntryRequired`, `GetAcpGrants`, `buildAccessControlList`, `ExtractAcl`, `AssembleEntryWithAcp`, `getBucketConfig`, `isUserAdmin`, `iam.authRequest`, `Identity.CanDo`, and filer `UpdateEntry`.

## Control Flow
Both handlers validate path and bucket existence, read optional `versionId`, check bucket versioning, then resolve either the specific version, latest version, or non-versioned entry. Delete markers are treated as missing keys. `GetObjectAclHandler` extracts owner id from `ExtAmzOwnerKey`, falls back to the request account id, resolves display name through IAM, builds `AccessControlPolicy`, and writes XML.

`PutObjectAclHandler` resolves the same target entry, determines the current object owner, and if the caller is not admin requires both ownership and a specific `WriteAcp:<bucket>/<object>` authorization. It reads bucket ownership config, extracts and validates ACL grants, assembles ACL metadata into the entry, calculates the correct update directory for versioned, null, or non-versioned entries, and calls `UpdateEntry`.

## State And Persistence
GET is read-only. PUT mutates the target entry's extended ACL metadata and owner metadata via `AssembleEntryWithAcp`, then persists the whole entry to either the bucket directory or the object's `.versions` directory. It relies on existing `Entry.Name` remaining valid for the target directory.

## Dependencies And Integration Points
The file integrates ACL XML models, IAM account display lookup and auth, bucket ownership controls, versioning layout, delete-marker metadata, S3 account headers, and filer metadata updates.

## Risks And Test Signals
Risks include incorrect update directory selection for latest version versus null version, insufficient WRITE_ACP authorization modeling, stale entry overwrites through whole-entry `UpdateEntry`, delete marker handling differences from AWS, and fallback owner behavior when metadata is missing. Tests should cover ACL GET/PUT for non-versioned objects, versioned specific versions, latest null versions, delete markers, admin override, non-owner denial, bucket-owner-enforced modes, and XML/canned ACL parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_acl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_attributes.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_attributes.go

## Purpose
Implements `GetObjectAttributes`, returning selected object metadata such as ETag, storage class, object size, and multipart part information. It supports versioned object resolution, delete marker handling, conditional read headers, and object-parts pagination.

## Important APIs, Types, And Functions
Response model types are `GetObjectAttributesResponse`, `ObjectAttributesChecksum`, `ObjectAttributesParts`, and `ObjectAttributesPart`. Helpers are `parseObjectAttributes`, `validateObjectAttributes`, `GetObjectAttributesHandler`, and `buildObjectAttributesParts`. The handler uses `isVersioningConfigured`, `getSpecificObjectVersion`, `getLatestObjectVersion`, `getEntry`, `fetchObjectEntry`, `parseConditionalHeaders`, `validateConditionalHeadersForReads`, `getObjectETag`, and multipart `PartBoundaryInfo` metadata.

## Control Flow
The handler parses `X-Amz-Object-Attributes` values into a set and rejects empty or unknown attributes. It parses `X-Amz-Max-Parts` and `X-Amz-Part-Number-Marker`, clamps max parts to 1000, and rejects negative or malformed values. It resolves requested `versionId`, latest version, or null version using the same `.versions` quick-check pattern as GET/HEAD. Delete markers set `x-amz-delete-marker: true` and return `NoSuchKey`; successful versioned lookups set `x-amz-version-id`. Conditional headers are evaluated against the resolved entry. The response includes only requested attributes: ETag without quotes, storage class defaulting to `STANDARD`, object size from attributes, and object parts from stored boundaries. Checksum is accepted but intentionally omitted because S3 checksum storage is not yet represented here.

## State And Persistence
The handler is read-only. It reads entry attributes, chunks, and extended metadata including storage class, delete marker, version id, multipart part boundaries, and multipart part count. It writes HTTP headers, clears `Content-Type`, and emits XML.

## Dependencies And Integration Points
This file integrates S3 object attributes API constants, versioning layout, conditional-header evaluation, multipart upload metadata stored in entry `Extended`, and common success/error writers.

## Risks And Test Signals
Risks include divergent version resolution from GET/HEAD, part-size calculation errors when boundary indexes drift from chunks, accepting checksum requests without values, and pagination edge cases for `NextPartNumberMarker` when truncation occurs. Useful tests should cover invalid attributes, malformed pagination headers, delete markers, null versions, conditional failures, storage class metadata, multipart boundaries spanning multiple chunks, and marker/max-parts truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_attributes.go -->
