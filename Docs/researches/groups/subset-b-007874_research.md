# subset-b-007874 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_config.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_config.go

Purpose: Implements SeaweedFS S3 bucket configuration state: cached bucket entries, structured bucket metadata, CORS conversion, versioning/ownership helpers, Object Lock and bucket policy cache hydration, lifecycle TTL fast-path derivation, and per-bucket KMS data-key caching.

Important APIs/types/functions: `BucketConfig`, `BucketConfigCache`, `BucketKMSCache`, `BucketMetadata`, `getBucketConfig`, `populateBucketConfigDerivedFields`, `updateBucketConfig`, `patchBucketEntry`, `getBucketMetadata`, `setBucketMetadata`, `UpdateBucketTags`, `UpdateBucketCORS`, `UpdateBucketEncryption`, lifecycle/CORS conversion helpers, and versioning/object-lock helpers.

Control flow: reads first consult negative cache, then positive cache, then filer bucket entry lookup. `populateBucketConfigDerivedFields` is the central mapper from `Entry.Extended` and `Entry.Content` into cached fields, then syncs bucket policy into the policy engine. Updates clone the cached config, apply the caller mutation, compute extended-attribute set/delete deltas, persist through `ObjectTransaction`, then invalidate cache instead of trusting a potentially stale clone.

State and persistence: extended attributes store versioning, ownership, ACL, owner, Object Lock, lifecycle XML/header values, public-read derivation source, and policy JSON. Protobuf `Entry.Content` stores structured `s3_pb.BucketMetadata` for tags, CORS, and encryption. `patchBucketEntry` uses a lock/route key to serialize bucket config writes through the owning filer; structured metadata remains read-modify-write with documented last-write-wins semantics.

Dependencies and integration: depends on filer protobufs, `proto`, AWS S3 grant types, KMS data key responses, CORS/lifecycle/policy packages, S3 constants/errors, `objectWriteLockClient`, and the bucket policy engine. It is consumed by bucket handlers, CORS/tagging/encryption handlers, Object Lock, lifecycle, ACL/public-read auth, and write-path lifecycle TTL resolution.

Risks: structured metadata updates can overwrite concurrent changes to different fields. Negative cache staleness can briefly hide newly created buckets until invalidated. Policy storage here and policy handlers both manipulate `BUCKET_POLICY_METADATA_KEY`, so whole-entry updates elsewhere can lose unrelated extended keys. KMS cache zeroing only knows the concrete `*kms.GenerateDataKeyResponse` type. CORS `MaxAgeSeconds` nil becomes zero in protobuf round trips.

Test signals: covered by bucket metadata tests, update-failure cache immutability test, lifecycle response tests, CORS/tagging/handler tests indirectly, and policy/ACL behavior tests. High-risk concurrency and filer transaction failure paths are mostly integration-tested rather than unit-tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_config_stubs.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_config_stubs.go

Purpose: Provides AWS-compatible stub endpoints for bucket subresources SeaweedFS does not persist: analytics, inventory, intelligent-tiering, and metrics.

Important APIs/types/functions: `s3XMLNamespace`, XML response structs for list operations, `stubBucketGuard`, `GetAnalyticsConfiguration`, `ListBucketAnalyticsConfigurations`, `GetInventoryConfiguration`, `ListBucketInventoryConfigurations`, `GetIntelligentTieringConfiguration`, `ListBucketIntelligentTieringConfigurations`, `GetMetricsConfiguration`, and `ListBucketMetricsConfigurations`.

Control flow: every handler first runs `stubBucketGuard`, which extracts the bucket and delegates to `checkBucket`. Missing/inaccessible buckets return the normal S3 bucket error before any subresource behavior. `Get*Configuration` endpoints return `NoSuchConfiguration`; `List*Configurations` endpoints return empty, well-formed XML with `IsTruncated=false`.

State and persistence: no persistent state is read or written except normal bucket existence/access checks through bucket config. The response structs encode only namespace and truncation status.

Dependencies and integration: uses `s3_constants` for bucket extraction, `s3err` for S3 error mapping, and common XML response helpers. These routes support SDKs and tools that probe optional bucket configuration APIs during discovery.

Risks: intentionally incomplete feature support can surprise clients that expect to create or mutate these subresources. The guard preserves bucket precedence, but it does not distinguish unsupported get by ID versus absent configuration beyond `NoSuchConfiguration`.

Test signals: `s3api_bucket_config_stubs_test.go` verifies successful empty list XML for all four list endpoints and 404 `NoSuchConfiguration` for all get endpoints against a cached existing bucket.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_config_stubs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_config_stubs_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_config_stubs_test.go

Purpose: Unit-tests stub bucket configuration endpoints for analytics, inventory, intelligent-tiering, and metrics.

Important APIs/types/functions: `TestBucketConfigStubs` creates an `S3ApiServer` with enabled IAM and a prefilled `BucketConfigCache`, then exercises the list and get handlers through mux bucket variables and `httptest`.

Control flow: list cases call each `List*Configurations` handler and assert HTTP 200, expected XML root element, and `<IsTruncated>false</IsTruncated>`. get cases call each `Get*Configuration` handler and assert HTTP 404 plus `<Code>NoSuchConfiguration</Code>`.

State and persistence: the test avoids filer I/O by placing a synthetic bucket config into cache. No persistent mutation is expected.

Dependencies and integration: depends on `gorilla/mux`, `httptest`, `filer_pb.Entry`, and `NewBucketConfigCache`. It validates that `stubBucketGuard` can succeed from cache and that XML/error response helpers produce AWS-shape payloads.

Risks: does not test missing bucket precedence, IAM denial, XML namespace on list responses, or request IDs/logging. Since it relies on cache, it does not cover filer-backed `checkBucket`.

Test signals: strong regression signal for SDK compatibility probes: list endpoints remain non-failing empty responses while get endpoints report absent configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_config_stubs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_config_update_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_config_update_test.go

Purpose: Verifies `updateBucketConfig` does not mutate cached bucket state when persistence fails.

Important APIs/types/functions: `TestUpdateBucketConfigDoesNotMutateCacheOnPersistFailure`, `newTestS3ApiServerWithMemoryIAM`, `NewBucketConfigCache`, `updateBucketConfig`, `BucketConfig`, and `s3_constants.ExtVersioningKey`.

Control flow: the test seeds a bucket config with empty versioning and no filer connection. It calls `updateBucketConfig` with a callback that sets versioning to `Enabled`. Persistence through `patchBucketEntry` fails, returning `ErrInternalError`; the test reloads the cached config and asserts versioning and extended attributes are unchanged.

State and persistence: deliberately simulates persistence failure before cache invalidation. The important state contract is copy-on-write: mutation happens on a cloned config, so failed writes cannot corrupt the live cache.

Dependencies and integration: integrates with the bucket config cache and filer-free in-memory IAM test server. It directly protects bucket versioning/ACL/Object Lock update paths that share `updateBucketConfig`.

Risks: does not simulate partial filer transaction success, concurrent updates, or mutation of nested pointer fields not deeply cloned. It also does not cover successful cache invalidation.

Test signals: high-value regression test for cache correctness and failed write isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_config_update_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_cors_handlers.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_cors_handlers.go

Purpose: Implements bucket CORS middleware adapters and S3 `GET/PUT/DELETE ?cors` handlers.

Important APIs/types/functions: fallback method/header variables, `S3BucketChecker`, `S3CORSConfigGetter`, `getCORSMiddleware`, `createFallbackCORSConfig`, `GetBucketCorsHandler`, `PutBucketCorsHandler`, and `DeleteBucketCorsHandler`.

Control flow: middleware wiring adapts `S3ApiServer.checkBucket` and `getCORSConfiguration` to the `cors` package. Bucket handlers first call `checkBucket`; GET loads cached CORS from bucket config and returns `NoSuchCORSConfiguration` when nil. PUT XML-decodes the request, validates via `cors.ValidateConfiguration`, then persists through `updateCORSConfiguration`. DELETE clears persisted CORS and returns 204.

State and persistence: bucket-specific CORS is stored in structured bucket metadata protobuf in `Entry.Content` through `UpdateBucketCORS`/`ClearBucketCORS`; cache is invalidated by the metadata write. Fallback CORS is in-memory from global `AllowedOrigins` and is not persisted.

Dependencies and integration: depends on `cors` package for validation/middleware, bucket config helpers, and S3 error/constant packages. Integrated into request handling for preflight/origin validation and bucket subresource API.

Risks: XML decoder reads directly from body without explicit size cap here. CORS storage shares the last-write-wins structured metadata path with tags/encryption. Fallback rules are broad (`AllowedHeaders: *`, many methods) and must be understood as a global compatibility mode.

Test signals: direct tests are not in this file, but bucket config conversion and CORS behavior are exercised through metadata tests and likely CORS package tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_cors_handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_handlers.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_handlers.go

Purpose: Main bucket API implementation: list, create, delete, head, ACL, lifecycle, location, request payment, ownership controls, versioning, access helpers, auto-create, public-read auth, and bucket ARN helpers.

Important APIs/types/functions: `ListBucketsHandler`, `PutBucketHandler`, `DeleteBucketHandler`, `bucketHasUserObjects`, `checkBucket`, `existingBucketError`, `autoCreateBucket`, `AuthWithPublicRead`, ACL handlers, lifecycle handlers, ownership controls handlers, versioning handlers, `buildResourceARN`, and `isBucketOwnedByIdentity`.

Control flow: bucket listing filters hidden dirs and uses IAM identity/ownership or list permission. creation validates names, parses ACLs, rejects table-bucket conflicts, detects existing collections/directories, atomically stores owner/ACL/Object Lock/versioning in the created entry, and removes negative cache. deletion checks access, Object Lock active locks, non-empty rules, removes bucket directory before best-effort collection deletion, invalidates caches/metrics, and prunes IAM bucket-scoped actions. lifecycle PUT validates XML and rejects transition rules, cleans legacy day-TTL filer.conf entries, then stores canonical XML in bucket extended attributes.

State and persistence: bucket directories live under `option.BucketsPath`; collection names map to bucket storage. Extended attrs store owner, ACL, versioning, ownership controls, Object Lock, and lifecycle XML/header. Lifecycle also interacts with legacy filer.conf TTL entries. Metrics and bucket config caches are invalidated on delete/update. Some paths still use whole-entry `updateEntry` while newer config paths use `updateBucketConfig`.

Dependencies and integration: integrates IAM, bucket registry, filer RPC/list/update/delete, lifecycle XML, AWS SDK XML types, stats, object-lock utilities, public-read bucket policy evaluation, and S3 response helpers. It is the central route target for S3 bucket management.

Risks: mixed persistence styles can race if whole-entry updates overwrite concurrent extended mutations. `PutBucketAclHandler` includes a short sleep for propagation, indicating cache/subscription timing sensitivity. Delete treats collection deletion failure as non-fatal, leaving reusable/orphan cleanup state. Lifecycle transition support is explicitly rejected; lifecycle volume TTL stamping has irreversible semantics handled elsewhere.

Test signals: covered by misc handler tests, lifecycle response tests, policy ARN tests, metadata/config update tests, Object Lock tests elsewhere, and likely broader S3 integration tests. Edge cases for concurrent create/delete and collection orphan recovery need integration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_handlers_misc.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_handlers_misc.go

Purpose: Implements smaller bucket subresource handlers for policy status, request payment, acceleration, and logging.

Important APIs/types/functions: `putBucketRequestPaymentMaxBodyBytes`, `policyStatusResponse`, `accelerateConfigurationResponse`, `bucketLoggingStatusResponse`, `GetBucketPolicyStatusHandler`, `isPolicyPublic`, `PutBucketRequestPaymentHandler`, `GetBucketAccelerateConfigurationHandler`, and `GetBucketLoggingHandler`.

Control flow: all bucket-dependent handlers call `checkBucket`. Policy status loads the stored bucket policy and reports public when an unconditional `Allow` has `Principal="*"`. Request payment caps body size at 64 KiB, XML-decodes `RequestPaymentConfiguration`, accepts only `BucketOwner`, and rejects `Requester` as malformed. Acceleration returns static `Suspended`; logging returns empty `BucketLoggingStatus`.

State and persistence: no new persistent state is written. Policy status reads policy metadata through `getBucketPolicy`; request payment intentionally does not store requester-pays configuration because only bucket-owner mode is supported. Acceleration/logging are static compatibility responses.

Dependencies and integration: depends on policy engine document types, S3 constants/errors, XML helpers, and core bucket access checks. It fills compatibility gaps for SDKs expecting these subresources.

Risks: public policy detection is intentionally conservative and treats conditional public policies as non-public. Request payment error mapping uses `MalformedXML` for unsupported payer values, which may differ from some clients' expectations but is tested. Static acceleration/logging can hide unsupported feature state.

Test signals: `s3api_bucket_handlers_misc_test.go` exercises explicit ACL detection, policy public classification, request payment accept/reject, and static acceleration/logging XML responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_handlers_misc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_handlers_misc_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_handlers_misc_test.go

Purpose: Unit-tests miscellaneous bucket helpers and compatibility handlers.

Important APIs/types/functions: `newMiscTestServer`, `newBucketRequest`, `TestHasExplicitBucketACL`, `TestGetBucketPolicyStatusIsPublic`, `TestPutBucketRequestPaymentBucketOwner`, `TestPutBucketRequestPaymentRequesterRejected`, `TestPutBucketOwnershipControlsRejectsRuleWithoutObjectOwnership`, `TestGetBucketAccelerateConfiguration`, and `TestGetBucketLogging`.

Control flow: tests construct cached bucket configs to avoid filer I/O, then call handlers with mux bucket vars. Assertions cover status codes and key XML/error snippets.

State and persistence: test state is in-memory only. The ownership-controls negative test uses bucket registry metadata with owner account data to reach validation before persistence.

Dependencies and integration: uses AWS S3 grant/policy types, `policy_engine`, `s3_constants`, `gorilla/mux`, and `httptest`. It protects compatibility response formats and helper classification behavior.

Risks: does not cover missing buckets, IAM denial, successful ownership-control persistence, request-payment oversized body behavior, or policy status handler response end-to-end. XML assertions are substring-based.

Test signals: good focused regression coverage for utility behavior that SDK compatibility depends on.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_handlers_misc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_handlers_object_lock_config.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_handlers_object_lock_config.go

Purpose: Implements S3 bucket Object Lock configuration get/put handlers.

Important APIs/types/functions: `PutObjectLockConfigurationHandler` and `GetObjectLockConfigurationHandler`.

Control flow: PUT checks Object Lock availability via `isObjectLockAvailable`, maps missing bucket to `NoSuchBucket` and unavailable state to `InvalidBucketState`, parses XML, validates retention configuration, then persists by setting `BucketConfig.ObjectLockConfig` through `updateBucketConfig`. GET loads bucket config; if cached Object Lock exists it marshals it with S3 namespace. If absent, it reloads the fresh bucket entry from filer, attempts to load Object Lock extended attrs, refreshes the full cache from that entry, and returns XML. If still absent, it returns `ObjectLockConfigurationNotFoundError`.

State and persistence: Object Lock state is stored in bucket entry extended attributes via shared Object Lock helpers called by `updateBucketConfig` and bucket creation. Metrics record bucket active time on success. Cache refresh is deliberately whole-config to avoid updating just Object Lock while other fields stay stale.

Dependencies and integration: depends on Object Lock parsing/validation/storage helpers, bucket config cache, filer entry lookup, S3 errors/constants, and stats. It integrates with bucket creation/versioning semantics: Object Lock availability implies versioning.

Risks: PUT cannot enable Object Lock on buckets not created with Object Lock support. GET mutates the returned cached config's `XMLNS` field before marshaling, which is harmless but worth noting. Fresh reload compensates for cache timing, indicating subscription consistency sensitivity.

Test signals: direct tests are elsewhere in Object Lock files; this file relies on shared validation helper coverage and integration tests for AWS-compatible object-lock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_handlers_object_lock_config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_lifecycle_config.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_lifecycle_config.go

Purpose: Defines bucket lifecycle storage keys and helpers for persisted lifecycle XML and transition minimum object size metadata.

Important APIs/types/functions: `bucketLifecycleConfigurationXMLKey`, `bucketLifecycleTransitionMinimumObjectSizeKey`, `bucketLifecycleTransitionMinimumObjectSizeHeader`, `defaultLifecycleTransitionMinimumObjectSize`, `maxBucketLifecycleConfigurationSize`, `normalizeBucketLifecycleTransitionMinimumObjectSize`, `getStoredBucketLifecycleConfiguration`, `storeBucketLifecycleConfiguration`, and `clearStoredBucketLifecycleConfiguration`.

Control flow: get reads `BucketConfig.Entry.Extended`, returns copied XML bytes plus normalized header value when present, or `found=false`. store and clear wrap `updateBucketConfig`, editing only lifecycle-related extended attributes. Normalization trims whitespace and defaults empty values to `all_storage_classes_128K`.

State and persistence: lifecycle XML is persisted directly in bucket extended attributes, not in structured protobuf metadata. This allows `populateBucketConfigDerivedFields` to build `LifecycleTTLResolver` from canonical XML when the fast-path opt-in flag is set.

Dependencies and integration: used by `GetBucketLifecycleConfigurationHandler`, `PutBucketLifecycleConfigurationHandler`, and `DeleteBucketLifecycleHandler` in the main bucket handlers file. Depends on `s3err` and shared bucket config mutation.

Risks: stores raw XML bytes; validation is performed by callers, so direct helper misuse could persist invalid XML. Lifecycle data shares extended-attribute namespace and update semantics with versioning/Object Lock/ACL/policy.

Test signals: lifecycle response tests cover stored XML retrieval, default header behavior, oversized PUT body, and read error mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_lifecycle_config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_lifecycle_response_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_lifecycle_response_test.go

Purpose: Tests lifecycle handler responses for stored lifecycle XML and request body error mapping.

Important APIs/types/functions: `TestGetBucketLifecycleConfigurationHandlerUsesStoredLifecycleConfig`, `TestGetBucketLifecycleConfigurationHandlerDefaultsTransitionMinimumObjectSize`, `TestPutBucketLifecycleConfigurationHandlerRejectsOversizedBody`, `TestPutBucketLifecycleConfigurationHandlerMapsReadErrorsToInvalidRequest`, and `failingReadCloser`.

Control flow: GET tests seed bucket config cache with lifecycle extended attributes and call the GET handler, asserting 200, exact XML body preservation, and transition-minimum header value/default. PUT tests call the handler with an oversized body and a failing body reader, asserting `EntityTooLarge` and `InvalidRequest` respectively.

State and persistence: tests avoid filer I/O by using cache entries. PUT tests stop before persistence due to request-body failures.

Dependencies and integration: uses mux URL vars, `httptest`, in-memory IAM test server, bucket config cache, and S3 error registry. It guards lifecycle storage contract in extended attributes.

Risks: does not test successful lifecycle PUT/DELETE persistence, transition-rule rejection, legacy filer.conf cleanup, or cache invalidation after storing/clearing.

Test signals: strong coverage for AWS response shape of stored lifecycle config and for body-size/read error mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_lifecycle_response_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_metadata_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_metadata_test.go

Purpose: Unit-tests the `BucketMetadata` value object and update pattern.

Important APIs/types/functions: `TestBucketMetadataStruct`, `TestBucketMetadataUpdatePattern`, and `TestBucketMetadataHelperFunctions`.

Control flow: tests create metadata with `NewBucketMetadata`, add tags/encryption/CORS, and assert `IsEmpty`, `HasTags`, `HasEncryption`, and `HasCORS` behavior. The update-pattern test simulates the callback used by `UpdateBucketMetadata`.

State and persistence: all state is local Go structs; there is no filer or cache persistence. The test validates logical state transitions before serialization into `s3_pb.BucketMetadata`.

Dependencies and integration: uses `s3_pb.EncryptionConfiguration` and `cors.CORSConfiguration`. It supports tagging, CORS, and bucket encryption handlers that share the structured metadata API.

Risks: does not test protobuf marshal/unmarshal, nil maps returned from protobuf, concurrent updates, cache interactions, or persistence failure handling.

Test signals: basic but useful guard that helper predicates remain aligned with default empty metadata semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_metadata_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_policy_arn_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_policy_arn_test.go

Purpose: Tests AWS-compatible ARN construction for bucket resources and principals.

Important APIs/types/functions: `TestBuildResourceARN` and `TestBuildPrincipalARN`.

Control flow: resource tests cover bucket-only, slash-only object, normal object, and leading-slash object cases. principal tests cover nil/anonymous principals, explicit `PrincipalArn`, anonymous identity/account IDs, normal account/name, missing account defaulting, and missing name defaulting to `unknown`.

State and persistence: no persistent state; only pure helper behavior.

Dependencies and integration: depends on `Identity`, `Account`, `s3_constants.AccountAnonymousId`, `defaultAccountID`, `buildResourceARN`, and `buildPrincipalARN`. These helpers feed bucket policy evaluation and IAM-compatible principal/resource matching.

Risks: does not test URL-escaped object names, wildcard resource construction beyond object strings, STS/JWT-derived principals, or account aliases.

Test signals: good regression protection for policy engine interoperability with AWS-style `arn:aws:s3:::` and `arn:aws:iam::` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_policy_arn_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_policy_engine.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_policy_engine.go

Purpose: Wraps the generic policy engine with bucket-specific loading, caching, resource ARN building, action resolution, request-condition extraction, and multipart SSE inheritance.

Important APIs/types/functions: `BucketPolicyEngine`, `NewBucketPolicyEngine`, `LoadBucketPolicy`, `LoadBucketPolicyFromCache`, `DeleteBucketPolicy`, `HasPolicyForBucket`, `GetBucketPolicy`, `ListBucketPolicies`, and `EvaluatePolicy`.

Control flow: load methods read policy JSON from bucket extended attributes or cached `PolicyDocument`, marshal as needed, and call `policy_engine.SetBucketPolicy`; missing policy deletes the engine entry. `EvaluatePolicy` validates bucket/action, resolves SeaweedFS action to S3 action, builds a resource ARN, extracts request condition values and principal variables, injects JWT claims when provided, optionally inherits multipart SSE algorithm by upload ID, then maps engine result to `(allowed, evaluated, error)`.

State and persistence: this wrapper holds in-memory policy engine state only. Durable policy JSON is stored in bucket extended attributes by policy handlers and hydrated here from cache or filer entry.

Dependencies and integration: depends on `policy_engine`, bucket policy metadata key, filer entries, S3 action resolver, request condition extraction, and optional `MultipartSSELookup` installed by `S3ApiServer`. Used by auth paths such as public-read evaluation and IAM authorization.

Risks: policy engine staleness is possible if subscription/cache hydration misses updates, though handlers load/delete immediately after changes. `EvaluatePolicy` fails on empty bucket/action and should be called after routing. Multipart SSE inheritance depends on upload ID and lookup availability.

Test signals: ARN tests indirectly protect resource construction; policy handler and auth tests likely cover evaluation. Direct unit coverage of multipart condition inheritance is not in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_policy_engine.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_policy_handlers.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_policy_handlers.go

Purpose: Implements S3 bucket policy GET/PUT/DELETE APIs, policy validation/storage, IAM synchronization hooks, and not-implemented public access block endpoints.

Important APIs/types/functions: `BUCKET_POLICY_METADATA_KEY`, `ErrPolicyNotFound`, `GetBucketPolicyHandler`, `PutBucketPolicyHandler`, `DeleteBucketPolicyHandler`, `getBucketPolicy`, `setBucketPolicy`, `deleteBucketPolicy`, `validateBucketPolicy`, `validateResourceForBucket`, `updateBucketPolicyInIAM`, and public-access-block handlers.

Control flow: GET validates bucket existence then reads policy JSON from bucket extended attributes. PUT reads body, unmarshals JSON, validates core policy and bucket-specific constraints, stores policy, immediately loads it into the policy engine, and best-effort updates IAM integration. DELETE validates bucket and policy existence, removes metadata, immediately deletes engine entry, and best-effort removes IAM integration.

State and persistence: policy JSON is stored under `s3-bucket-policy` in bucket entry extended attributes. Storage uses filer `LookupDirectoryEntry` plus whole-entry `UpdateEntry`, preserving current entry content but potentially overwriting concurrent extended changes if stale. Policy engine and IAM updates are secondary in-memory/external side effects.

Dependencies and integration: uses filer RPCs, `policy_engine.ValidatePolicy`, S3 constants/errors, IAM integration (`S3IAMIntegration` and IAM manager), and bucket policy engine. Public access block APIs currently always return `NotImplemented`.

Risks: whole-entry update path is weaker than `patchBucketEntry` and can race with other extended-attribute writes. `removeBucketPolicyFromIAM` is a TODO-style no-op. PUT does not explicitly cap body size in this file. Validation permits simplified non-ARN resource forms but requires bucket match and `s3:` actions.

Test signals: policy public/status tests and ARN tests cover parts of behavior. End-to-end policy persistence, concurrent mutation, IAM sync, and public access block behavior need broader tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_policy_handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_tagging_handlers.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_tagging_handlers.go

Purpose: Implements S3 bucket tagging GET/PUT/DELETE handlers.

Important APIs/types/functions: `GetBucketTaggingHandler`, `PutBucketTaggingHandler`, and `DeleteBucketTaggingHandler`.

Control flow: all handlers check bucket access. GET loads structured bucket metadata and returns `NoSuchTagSet` when the tags map is empty. PUT reads the request body limited by `ContentLength`, unmarshals XML into `Tagging`, converts to a map, validates tags, and persists via `UpdateBucketTags`. DELETE clears tags via `ClearBucketTags` and returns 204.

State and persistence: tags are stored in structured protobuf `BucketMetadata` in bucket entry content. Updates share `UpdateBucketMetadata` read-modify-write semantics with CORS/encryption.

Dependencies and integration: depends on XML tag helpers (`Tagging`, `FromTags`, `ValidateTags`), bucket metadata API, S3 constants/errors, and access checks. Integrated with lifecycle/object policy paths that may reference tags indirectly elsewhere.

Risks: using `io.LimitReader(r.Body, r.ContentLength)` can behave poorly when `ContentLength` is negative or absent. Structured metadata last-write-wins can lose concurrent CORS/encryption changes. GET maps metadata load failures to internal error rather than absent tag set.

Test signals: no direct tests in this subset; bucket metadata tests cover underlying data object, and broader S3 tagging tests likely cover XML behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_tagging_handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_circuit_breaker.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_circuit_breaker.go

Purpose: Provides request concurrency/bytes limiting for S3 API actions, plus upload-specific in-flight throttling and metrics.

Important APIs/types/functions: `CircuitBreaker`, `NewCircuitBreaker`, `LoadS3ApiConfigurationFromBytes`, `loadCircuitBreakerConfig`, `Limit`, `limit`, and `loadCounterAndCompare`.

Control flow: construction reads circuit breaker config from filer with multi-filer failover. Config loading builds a limitations map from global and bucket-specific action count/bytes limits. `Limit` wraps HTTP handlers: for write actions it optionally waits on server-level in-flight upload byte/file limits, increments gauges, then if circuit breaker is enabled calls `limit`. `limit` checks bucket count, bucket bytes, global count, and global bytes in order, collecting rollback functions for increments; wrapper defers rollback after handler or error.

State and persistence: config is persisted in filer under the circuit breaker config path. Runtime counters are in-memory atomic int64 pointers keyed by bucket/action/type. Upload in-flight counters live on `S3ApiServer`; Prometheus-style gauges are updated on increment/decrement.

Dependencies and integration: depends on filer config parsing, mux bucket variables, S3 constants/errors, stats, `sync/atomic`, and `S3ApiServerOption`. It wraps registered S3 routes.

Risks: `ContentLength` can be negative for unknown-length requests, which could reduce byte counters if not guarded in the circuit-breaker byte path. Counter creation uses double-checked locking and atomics; rollback must run for all successful partial increments. Limits are local to the process, not cluster-wide.

Test signals: `s3api_circuit_breaker_test.go` stresses concurrent `limit` calls for bucket/global count and byte limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_circuit_breaker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_circuit_breaker_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_circuit_breaker_test.go

Purpose: Tests circuit breaker limit enforcement under concurrent access.

Important APIs/types/functions: `TestLimitCase`, `TestLimitCases`, `TestLimit`, and `doLimit`.

Control flow: each case builds an `s3_pb.S3CircuitBreakerConfig` with global and bucket limits for either count or bytes, loads it into a fresh `CircuitBreaker`, then launches multiple goroutines calling `limit`. Successful calls record rollback functions, and after all goroutines finish the test runs rollbacks and asserts expected success count.

State and persistence: no filer persistence. Tests in-memory `limitations` and `counters` maps plus atomic counter increments/decrements.

Dependencies and integration: uses S3 constants for action/limit key concatenation, `s3err` to detect success, and `http.Request{ContentLength:fileSize}` for byte tests.

Risks: test uses a bucket string with slash and duplicate map assignment in global actions, but it still exercises the intended key shapes. It does not verify wrapper-level upload throttling, metrics, rollback after handler panic, or unknown content length.

Test signals: useful concurrency regression signal for the core atomic counter path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_circuit_breaker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_copy_size_calculation.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_copy_size_calculation.go

Purpose: Calculates expected target and actual sizes for S3 copy operations across encryption/compression scenarios and copy strategies.

Important APIs/types/functions: `CopySizeCalculator`, `EncryptionType`, `NewCopySizeCalculator`, `CalculateTargetSize`, `CalculateActualSize`, `getSourceEncryptionType`, `getDestinationEncryptionType`, `isCompressedEntry`, `SizeTransitionInfo`, `GetSizeTransitionInfo`, `OptimizedSizeCalculation`, and `CalculateOptimizedSizes`.

Control flow: construction reads source file size and compression indicators from `filer_pb.Entry`, detects source encryption from entry metadata, and destination encryption from request headers. Size calculation returns source size for all encryption transitions because IV/encryption metadata is stored outside object bytes; compressed entries return `-1` target size to force streaming/unknown sizing. Strategy-specific optimized calculation adjusts preallocation/streaming flags.

State and persistence: read-only helper; no persistence. It consumes object entry attributes/extended metadata and request headers.

Dependencies and integration: depends on filer entry attributes, SSE helper functions (`IsSSECEncrypted`, `IsSSEKMSRequest`, etc.), and `UnifiedCopyStrategy` constants from the copy implementation. Used by copy paths to choose direct/preallocated versus streaming behavior.

Risks: compressed detection is heuristic (`Extended["compression"]` and a small MIME list). Future encryption formats with actual byte overhead would need updates. Nil entry/attributes are not guarded here. Unknown compressed target size can force less efficient streaming.

Test signals: no direct tests in this subset. Copy integration tests should validate behavior across encrypted and compressed objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_copy_size_calculation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_copy_validation.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_copy_validation.go

Purpose: Validates copy-source/destination paths and encryption headers for S3 copy operations.

Important APIs/types/functions: `CopyValidationError`, `ValidateCopyEncryption`, `validateSSECCopyRequirements`, `validateSSEKMSCopyRequirements`, `validateEncryptionCompatibility`, SSE-C header completeness helpers, `validateEncryptionContext`, `ValidateCopySource`, `validateCopySource`, `ValidateCopyDestination`, and `MapCopyValidationError`.

Control flow: encryption validation requires SSE-C copy-source headers when source metadata says SSE-C, forbids copy-source SSE-C headers for non-SSE-C sources, validates destination SSE-C completeness, checks KMS key format and context constraints, and rejects multiple destination encryption modes. Copy source validation rejects empty bucket/object/header, invalid bucket/object names, unsafe path segments via `IsValidObjectKey`, and invalid version IDs. Destination validation requires non-empty bucket/object.

State and persistence: pure validation; no state mutation or persistence.

Dependencies and integration: depends on S3 encryption header constants, S3 error codes, object key validators, KMS/version ID validators, and SSE metadata helpers. Copy handlers can map returned errors to S3 error codes with `MapCopyValidationError`.

Risks: `validateEncryptionContext` currently only checks non-empty despite comments about base64/JSON validation. KMS validation depends on `isValidKMSKeyID` elsewhere. Validation does not check that `copySource` string itself matches parsed bucket/object; callers must parse consistently.

Test signals: no direct tests in this subset. Security-sensitive path traversal and SSE-C/KMS combinations should have dedicated tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_copy_validation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_domain_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_domain_test.go

Purpose: Tests domain classification for mixed virtual-host and path-style S3 access, especially issue #7356.

Important APIs/types/functions: `TestClassifyDomainNames`, `TestClassifyDomainNamesOrder`, `TestClassifyDomainNamesEdgeCases`, and `TestClassifyDomainNamesUseCases`.

Control flow: tests call `classifyDomainNames` with lists containing parent domains and subdomains. Expected behavior: a configured domain with a configured parent is classified path-style, while parent/base domains remain virtual-host style. Additional tests verify input order independence, duplicates, long domains, similar domains, IP addresses, localhost, and multi-environment setups.

State and persistence: pure classification tests; no server state or persistence.

Dependencies and integration: depends on `testify/assert` and the production `classifyDomainNames` helper used by S3 domain routing. It protects host-header routing for virtual-host-style bucket names and path-style deployments.

Risks: tests do not cover IDNA/punycode, ports in hostnames, trailing dots, uppercase normalization, wildcard domains, or IPv6 literals. Duplicate handling is asserted only loosely with contains checks.

Test signals: strong regression coverage for mixed parent/child domain configurations and order-insensitive classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_domain_test.go -->
