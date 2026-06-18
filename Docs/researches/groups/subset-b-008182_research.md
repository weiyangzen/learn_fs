# subset-b-008182 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/api-errors.go -->
# sources/object-store/minio/cmd/api-errors.go

## Purpose
Defines MinIO's S3/Admin API error surface: stable `APIErrorCode` constants, wire-format `APIError`/`APIErrorResponse` structs, the central `errorCodes` HTTP/XML mapping, and translation from internal errors to client-facing S3-compatible failures.

## Important APIs, types, and functions
- `APIError`, `APIErrorResponse`, and `APIErrorCode` are the primary error contract used by response writers and handlers.
- `errorCodeMap.ToAPIErrWithErr`/`ToAPIErr`, `getAPIError`, and `getAPIErrorResponse` produce response-ready values and inject region/request metadata.
- `toAPIErrorCode` classifies context, auth, crypto, KMS, object-layer, bucket-metadata, replication, notification, DNS, and S3 Select errors into stable codes.
- `toAPIError` adds richer descriptions for internal errors, SDK errors, XML syntax, invalid ranges, lifecycle/versioning/replication/tag/policy errors, and cloud backends.

## Control flow
Handlers pass low-level errors through `toAPIErrorCode` or `toAPIError`, then response helpers serialize them. Translation first checks nil, deadline/client-disconnect cases, unwraps nested errors, matches sentinel errors, handles known typed errors, falls back to content-length heuristics, and finally returns `ErrInternalError`. Internal errors get a second interpretation pass in `toAPIError` before being logged if still unclassified.

## State and persistence behavior
This file has no persistence of its own. It reads global site region and request logger context to shape messages and error-response fields. The constant order is persistent API state because `apierrorcode_string.go` and tests depend on it.

## Dependencies and integration points
Integrated with object-layer error types, IAM/auth, crypto/KMS, lifecycle, replication, object lock, tags, policy parsing, DNS, notification/lambda config, hash readers, Azure/GCS/minio-go SDK errors, logger request info, and response serialization in `api-response.go`.

## Risks and edge cases
Adding an error code requires updating `errorCodes` and regenerating the stringer file. Unknown errors expose cause text in `InternalError` descriptions after logging. Context cancellation is intentionally reported as client disconnect only when the request context itself is canceled. Region-specific auth errors rewrite descriptions dynamically.

## Test signals
`api-errors_test.go` verifies representative internal-to-API translations and asserts every non-sentinel `APIErrorCode` has a table entry, non-empty wire code, and HTTP status.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/api-errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/api-errors_test.go -->
# sources/object-store/minio/cmd/api-errors_test.go

## Purpose
Unit tests for the API error translation registry in `api-errors.go`.

## Important APIs, types, and functions
- `toAPIErrorTests` maps representative Go/internal errors to expected `APIErrorCode` values.
- `TestAPIErrCode` calls `toAPIErrorCode` against each table entry.
- `TestAPIErrCodeDefinition` iterates from `ErrNone + 1` to `apiErrCodeEnd` to validate table completeness.

## Control flow
The translation test runs a simple table loop using `t.Context()`, comparing returned codes with expected codes for hash, object-layer, bucket, multipart, quorum, SSE-C, signature, nil, and unknown errors. The definition test walks the whole enum range and fails immediately if an error code is absent from `errorCodes`, has an empty XML code, or has a zero HTTP status.

## State and persistence behavior
No durable state is modified. The tests enforce `APIErrorCode` enum order and `errorCodes` table completeness as source-level invariants.

## Dependencies and integration points
Depends on `internal/crypto`, `internal/hash`, object-layer error structs from the cmd package, and the generated enum sentinel `apiErrCodeEnd`. It indirectly guards response generation because missing status/code fields would produce invalid API responses.

## Risks and edge cases
Coverage is representative rather than exhaustive for the large table. The completeness test catches missing mappings for new constants but does not validate semantic correctness of every HTTP status/message. Unknown errors are expected to map to `ErrInternalError`.

## Test signals
Failures indicate either a changed error classification, an unmapped new `APIErrorCode`, or an incomplete wire-facing table entry.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/api-errors_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/api-headers.go -->
# sources/object-store/minio/cmd/api-headers.go

## Purpose
Builds common S3 response headers, XML/JSON encoders, event-stream headers, multipart part-count headers, and object metadata/range headers for object responses.

## Important APIs, types, and functions
- `mustGetRequestID` formats nanosecond timestamps as uppercase hex request ids.
- `setEventStreamHeaders` disables buffering for event streams.
- `setCommonHeaders` sets server, region, accept-ranges, and removes sensitive crypto headers.
- `encodeResponse`, `encodeResponseList`, and `encodeResponseJSON` serialize XML, control-character-safe list XML, and JSON.
- `setObjectHeaders` is the main object response header builder.
- `needsMimeEncoding` decides whether user metadata values require RFC 2047 encoding.

## Control flow
`setObjectHeaders` first applies common headers, last-modified, ETag, content type/encoding/expires, tag count, optional tag echoing, and user metadata. It filters internal/reserved metadata and the unencrypted length/MD5 headers from a security advisory. User metadata values with non-ASCII/control bytes are MIME encoded. It computes actual object size, derives range from explicit range or part number, sets content length/range, version and replication headers, transitioned storage class, lifecycle prediction headers, and compression metadata.

## State and persistence behavior
No persistent writes. It reads `globalSite.Region()` and `globalLifecycleSys`, and derives response state from `ObjectInfo`, `HTTPRangeSpec`, and `ObjectOptions`.

## Dependencies and integration points
Used by object GET/HEAD and listing paths. Integrates with crypto metadata filtering, object tags parsing, MinIO HTTP header constants, lifecycle prediction, multipart part metadata, and range helpers.

## Risks and edge cases
Header behavior is security-sensitive: leaking reserved metadata, unencrypted length/MD5, or incorrect SSE headers can expose internal state. Range/part-number conversion can return errors that must be propagated. MIME encoding intentionally differs from some AWS bugs while trying to preserve compatibility.

## Test signals
`api-headers_test.go` only checks request-id shape, so most object-header behavior relies on broader object API tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/api-headers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/api-headers_test.go -->
# sources/object-store/minio/cmd/api-headers_test.go

## Purpose
Minimal unit test for request-id generation in `api-headers.go`.

## Important APIs, types, and functions
- `TestNewRequestID` calls `mustGetRequestID(UTCNow())`.

## Control flow
The test generates one id, asserts it has length 16, and verifies every rune is an uppercase alphanumeric character in `0-9` or `A-Z`.

## State and persistence behavior
No state is written. The test depends on the current timestamp returned by `UTCNow()` and on `UnixNano` formatting staying within the expected width for present-era timestamps.

## Dependencies and integration points
Guards a low-level value consumed by response headers and audit/request tracking.

## Risks and edge cases
This does not test uniqueness, monotonicity, request-header propagation, or behavior for arbitrary historical/future times. Because the id is hex, the alphanumeric assertion is broader than necessary but still catches punctuation/lowercase changes.

## Test signals
Failure means request-id formatting changed in a way that could affect client-visible headers or log correlation.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/api-headers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/api-resources.go -->
# sources/object-store/minio/cmd/api-resources.go

## Purpose
Parses S3 query parameters for bucket/object list and multipart resource APIs into typed values plus `APIErrorCode` parse results.

## Important APIs, types, and functions
- `getListObjectsV1Args` parses `prefix`, `marker`, `delimiter`, `max-keys`, and `encoding-type`.
- `getListBucketObjectVersionsArgs` parses version-list markers, version marker, delimiter, max keys, and encoding.
- `getListObjectsV2Args` parses V2 list parameters, `fetch-owner`, max keys, and base64 continuation tokens.
- `getBucketMultipartResources` parses bucket-level multipart upload listing parameters.
- `getObjectResources` parses object-level multipart part listing parameters.

## Control flow
Each parser starts with `ErrNone`, reads optional numeric limits with defaults (`maxObjectList`, `maxUploadsList`, `maxPartsList`), and returns specific invalid-argument codes when conversion fails. V2 listing rejects an explicitly present empty continuation token and decodes non-empty continuation tokens from base64 before returning them to callers.

## State and persistence behavior
Stateless pure parsing over `url.Values`; no global state or persistence.

## Dependencies and integration points
Feeds S3 list-object, list-version, list-multipart-upload, and list-parts handlers. Uses constants from `api-response.go` and error codes from `api-errors.go`.

## Risks and edge cases
The functions parse integers but do not enforce semantic bounds beyond parse success; downstream handlers must clamp or validate negative/large values. Empty V2 continuation tokens are rejected only when the key is present. Invalid base64 maps to `ErrIncorrectContinuationToken`.

## Test signals
`api-resources_test.go` covers V1/V2 defaults, valid token decoding, empty token rejection, and object multipart parameter extraction.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/api-resources.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/api-resources_test.go -->
# sources/object-store/minio/cmd/api-resources_test.go

## Purpose
Unit tests for S3 query parser helpers in `api-resources.go`.

## Important APIs, types, and functions
- `TestListObjectsV2Resources` validates V2 list parsing, base64 token decoding, defaults, and empty-token rejection.
- `TestListObjectsV1Resources` validates V1 list parsing and default max keys.
- `TestGetObjectsResources` validates multipart object-resource parsing.

## Control flow
Each test defines table cases with `url.Values`, calls the corresponding parser, and compares all returned fields. V2 includes both explicit and default max-key cases plus an error case where a present empty `continuation-token` returns `ErrIncorrectContinuationToken`.

## State and persistence behavior
No persistent state. Tests are deterministic and only inspect returned parser values.

## Dependencies and integration points
Exercise parser behavior used by list-object and multipart handlers. They depend on shared constants such as `SlashSeparator`, `maxObjectList`, and `ErrNone`.

## Risks and edge cases
Tests do not cover malformed numeric values, invalid base64 continuation tokens, versions-list parsing, bucket multipart parsing, negative limits, or multiple query values. They verify the happy paths used most often and one V2 continuation-token edge case.

## Test signals
Failures indicate changed request-query semantics, especially around defaults and continuation token decoding.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/api-resources_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/api-response.go -->
# sources/object-store/minio/cmd/api-response.go

## Purpose
Defines the XML/JSON response models and builders for S3 bucket, object, version, multipart, copy, delete, POST, success, redirect, and error responses.

## Important APIs, types, and functions
- Response structs include `ListVersionsResponse`, `ListObjectsResponse`, `ListObjectsV2Response`, `ListPartsResponse`, `ListMultipartUploadsResponse`, `ListBucketsResponse`, `Object`, `ObjectVersion`, `Metadata`, and delete/copy/multipart result types.
- Builders include `generateListBucketsResponse`, `generateListVersionsResponse`, `generateListObjectsV1Response`, `generateListObjectsV2Response`, multipart/copy/delete response generators, `cleanReservedKeys`, `getObjectLocation`, and `getURLScheme`.
- Writers include `writeResponse`, success helpers, XML/JSON/string error writers, `headersAlreadyWritten`, and `trackingResponseWriter`.

## Control flow
Listing builders transform object-layer listing structs into AWS-compatible XML models, applying URL encoding, ETag quoting, owner fields, storage-class filtering, optional metadata/tag visibility through `metaCheckFn`, encryption metadata reconstruction, reserved metadata stripping, and continuation marker encoding. `writeResponse` refuses to write if a `trackingResponseWriter` already observed headers, normalizes invalid/zero status codes, applies common headers, content type/length, and writes the body.

## State and persistence behavior
Stateless response assembly. Reads global owner id, TLS/default scheme, site region, deployment id, lifecycle/security metadata, and request logger context. No persistence.

## Dependencies and integration points
Central to S3 handlers registered by `api-router.go`. Integrates with MinIO object metadata types, hash checksums, crypto metadata, request scheme handlers, logger request info, xxml encoders, gzip wrappers, and `api-errors.go`.

## Risks and edge cases
Response compatibility is delicate: ETag quoting, base64 continuation tokens, virtual-host locations, metadata filtering, SSE metadata reconstruction, already-written-header suppression, and nonstandard status codes all affect clients. Metadata exposure is policy-gated and security-sensitive.

## Test signals
`api-response_test.go` covers object locations, scheme selection, tracking writer unwrap/header state, and write suppression after headers are already written.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/api-response.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/api-response_test.go -->
# sources/object-store/minio/cmd/api-response_test.go

## Purpose
Unit tests for selected response utility behavior in `api-response.go`.

## Important APIs, types, and functions
- `TestObjectLocation` validates `getObjectLocation`.
- `TestGetURLScheme` validates `getURLScheme`.
- `TestTrackingResponseWriter`, `TestHeadersAlreadyWritten`, and `TestHeadersAlreadyWrittenWrapped` validate response-writer tracking and unwrapping.
- `TestWriteResponseHeadersNotWritten` and `TestWriteResponseHeadersWritten` validate `writeResponse` suppression behavior.

## Control flow
Object-location tests construct requests with host and forwarded scheme variations, including virtual-host bucket domains, then compare exact generated URLs. Writer tests wrap `httptest.ResponseRecorder`, optionally through gzip response wrappers, write headers/bodies, inspect status/body, and confirm later writes are skipped when headers were already marked written.

## State and persistence behavior
No persisted state. Some expected URLs depend on default `globalIsTLS` behavior when no forwarded scheme is present.

## Dependencies and integration points
Uses Go HTTP test utilities and `klauspost/compress/gzhttp` wrappers to represent real middleware wrapping. It guards behavior used by router middleware and response helpers.

## Risks and edge cases
Does not test XML/list response models, metadata filtering, error response body content, invalid status correction, or range headers. The writer tests specifically prevent regressions where a late error response overwrites an already-started response.

## Test signals
Failures show location URL compatibility changes or response-header double-write regressions.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/api-response_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/api-router.go -->
# sources/object-store/minio/cmd/api-router.go

## Purpose
Registers the S3-compatible HTTP API surface, shared object-layer/server accessors, rejected/not-implemented APIs, per-handler middleware flags, and CORS behavior.

## Important APIs, types, and functions
- `newHTTPServerFn`, `setHTTPServer`, `newConsoleServerFn`, `setConsoleSrv`, `newObjectLayerFn`, and `setObjectLayer` guard global pointers with `globalObjLayerMutex`.
- `objectAPIHandlers` stores an `ObjectAPI` accessor.
- `s3HFlag` controls gzip, trace-body, and throttling behavior.
- `s3APIMiddleware` wraps handlers with tracking writer, trace, gzip, max-client throttling, and API stats.
- `registerAPIRouter` wires virtual-host and path-style S3 routes.
- `corsHandler` configures CORS allowed/exposed headers and methods.

## Control flow
Router registration builds host-based routers for configured domains, with a Kubernetes exception for `minio.<domain>`, then appends a path-style bucket router. For each bucket router it registers rejected object APIs, object operations, multipart operations, tagging, retention/legal-hold, select, lambda GET, bucket configuration APIs, listing variants, delete, replication extensions, rejected bucket APIs, and legacy ListObjects V1. Root routes cover bucket listing and event listening, with default not-found/method-not-allowed handlers.

## State and persistence behavior
No durable state. It reads and writes global in-memory server/object-layer references and reads global domain/API CORS config.

## Dependencies and integration points
Depends on `minio/mux`, MinIO HTTP constants, tracing, gzip, max-client throttling, stats collection, object API handlers implemented in other files, global domain/Kubernetes config, and wildcard CORS matching.

## Risks and edge cases
Route order matters because many methods share paths and differ only by headers/query parameters. Forgetting `traceHdrsS3HFlag` on large-body handlers risks high memory usage. Host-style routing can conflict with Kubernetes service names or reserved bucket names.

## Test signals
No direct tests in this subset; behavior is exercised by higher-level S3 API tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/api-router.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/api-utils.go -->
# sources/object-store/minio/cmd/api-utils.go

## Purpose
Small S3 API utilities for AWS-compatible URL encoding of response names and for deriving handler names from reflected function values.

## Important APIs, types, and functions
- `shouldEscape` identifies bytes requiring percent-encoding, preserving alphanumerics plus `-`, `_`, `.`, `/`, and `*`.
- `s3URLEncode` encodes names for S3 `encoding-type=url`, using `+` for spaces, uppercase hex, preserving `/` and `*`, and encoding `~`.
- `s3EncodeName` conditionally applies URL encoding when encoding type is `url`.
- `getHandlerName` strips cmd package/type receiver suffixes from reflected handler function names.

## Control flow
`s3URLEncode` first counts spaces and hex escapes to avoid allocation when unnecessary and to use a stack buffer for small outputs. It then either replaces spaces only or emits `%XX` escapes for every byte requiring escaping. `getHandlerName` calls `runtime.FuncForPC` and trims package/type and method-wrapper suffixes.

## State and persistence behavior
Stateless; no global reads except package-name assumptions embedded in string trimming.

## Dependencies and integration points
Used by list-response builders for S3 key/prefix encoding and by `s3APIMiddleware` for API stats/log names. Depends on Go reflection/runtime and MinIO handler naming conventions.

## Risks and edge cases
Encoding is byte-oriented and intentionally differs from `url.QueryEscape` for S3 compatibility. Handler-name extraction is brittle if package paths, receiver types, or compiler wrapper suffixes change.

## Test signals
`api-utils_test.go` checks URL encoding for spaces, percent, slash, tilde, asterisk, plus, underscore, and dot.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/api-utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/api-utils_test.go -->
# sources/object-store/minio/cmd/api-utils_test.go

## Purpose
Unit tests for S3 response-name encoding in `api-utils.go`.

## Important APIs, types, and functions
- `TestS3EncodeName` table-drives inputs through `s3EncodeName`.

## Control flow
Each case supplies input text, encoding type, and expected output. The test verifies no encoding when `encodingType` is empty and S3-specific URL encoding when it is `url`.

## State and persistence behavior
No state is modified.

## Dependencies and integration points
Guards encoding behavior consumed by list-object, list-version, multipart, and common-prefix response generators.

## Risks and edge cases
The test covers representative ASCII characters but not non-ASCII UTF-8, control characters, long strings, or lowercase/mixed-case `encoding-type` values. It also has a duplicate `p/` case, which is harmless but redundant.

## Test signals
Failures indicate changed S3 key/prefix URL encoding, which can break clients relying on `encoding-type=url`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/api-utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/apierrorcode_string.go -->
# sources/object-store/minio/cmd/apierrorcode_string.go

## Purpose
Generated `stringer` implementation for `APIErrorCode`, providing stable string names for every enum value in `api-errors.go`.

## Important APIs, types, and functions
- The compile-time `_()` function indexes every `APIErrorCode` constant at its expected ordinal.
- `_APIErrorCode_name` concatenates all trimmed enum names.
- `_APIErrorCode_index` stores string boundaries.
- `func (i APIErrorCode) String() string` returns the generated name or `APIErrorCode(<n>)` for out-of-range values.

## Control flow
At compile time, array-index expressions fail if any constant value no longer matches the generated ordinal. At runtime, `String` bounds-checks the code and slices the concatenated name table using the generated index array.

## State and persistence behavior
No runtime state or persistence. The file is generated source state and must be regenerated whenever `APIErrorCode` constants change.

## Dependencies and integration points
Generated from `api-errors.go` via `go generate stringer -type=APIErrorCode -trimprefix=Err`. Used for diagnostics, tests, and any code that formats `APIErrorCode` values.

## Risks and edge cases
Manual edits are unsafe. If new error constants are added without regenerating this file, compilation can fail or string output can become stale. The generated name table is large and ordinal-sensitive.

## Test signals
Compilation itself is the main signal. `api-errors_test.go` complements this by checking the error table, not the string names.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/apierrorcode_string.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/auth-handler.go -->
# sources/object-store/minio/cmd/auth-handler.go

## Purpose
Classifies request authentication type, validates S3/Admin signatures and session tokens, checks IAM/bucket-policy authorization, and installs early auth middleware for S3 requests.

## Important APIs, types, and functions
- Request classifiers: `isRequestJWT`, `isRequestSignatureV4`, `isRequestSignatureV2`, presign detectors, post-policy detector, and streaming/trailer V4 detectors.
- `authType` enum and `getRequestAuthType`.
- Admin auth: `validateAdminSignature`, `checkAdminRequestAuth`.
- Token/claims: `getSessionToken`, `getClaimsFromTokenWithSecret`, `checkClaimsFromToken`.
- S3 auth/authorization: `authenticateRequest`, `authorizeRequest`, `checkRequestAuthType*`, `checkRequestAuthTypeCredential`, `isReqAuthenticated`, `isReqAuthenticatedV2`.
- Middleware/helpers: `setAuthMiddleware`, `isPutRetentionAllowed`, `isPutActionAllowed`.

## Control flow
`getRequestAuthType` parses the raw query into `r.Form` and prioritizes V2, presigned V2, streaming V4, signed V4, presigned V4, JWT, post policy, STS action, anonymous, then unknown. `setAuthMiddleware` rejects unsupported auth and enforces date/skew checks for signed requests before handlers run. `authenticateRequest` verifies signatures, extracts credentials, sets request logger info, and parses create-bucket location payloads. `authorizeRequest` applies anonymous bucket policy or authenticated IAM policy checks, with ListBucketVersions fallback to ListBucket and special delete-version deny handling.

## State and persistence behavior
No persistence, but it mutates request state (`r.Form`, `r.Body`) and request logger context. It reads global credentials, IAM/policy systems, site replication signing key, authz plugin, active site region, skew configuration, and HTTP stats counters.

## Dependencies and integration points
Integrates with SigV2/SigV4 signing helpers, IAM policy engine, bucket policy engine, JWT/auth credentials, object-lock retention policy, hash readers for MD5/SHA256 validation, logger/audit, trace context, and S3/Admin handlers.

## Risks and edge cases
Auth ordering is security-critical. Query parsing errors become unknown auth. Temporary/service-account token rules differ, site-replication signing can change token secret selection, and request body is wrapped for checksum validation. Middleware date rejection increments rejection counters and must audit with claims where possible.

## Test signals
`auth-handler_test.go` covers auth-type classification, supported S3 auth types, presign detection, V4 body/MD5 validation, admin auth acceptance/rejection, and admin signature credential cases.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/auth-handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/auth-handler_test.go -->
# sources/object-store/minio/cmd/auth-handler_test.go

## Purpose
Unit/integration-style tests for auth classification, supported auth modes, presign detection, request signature validation, and admin authentication.

## Important APIs, types, and functions
- `nullReader` and request factories build signed, presigned, V2, V4, and bad-MD5 requests.
- `TestGetRequestAuthType`, `TestS3SupportedAuthType`, `TestIsRequestPresignedSignatureV2`, and `TestIsRequestPresignedSignatureV4` test lightweight classification.
- `TestIsReqAuthenticated` initializes a filesystem object layer and IAM/config subsystems to test signed request validation.
- `TestCheckAdminRequestAuthType` and `TestValidateAdminSignature` test admin-specific signature rules.

## Control flow
The classification tests build synthetic requests and inspect returned auth types/booleans. The authentication tests create temporary FS-backed object-layer state, initialize config/IAM, install test active credentials, sign requests with helper functions, then compare returned `APIErrorCode` values for unsigned, malformed digest, bad digest, valid signed, V2, presigned, and invalid admin credential cases.

## State and persistence behavior
Tests create and remove a temporary filesystem backend via `prepareFS`, write test config, initialize global subsystems, and mutate `globalActiveCred`. Cleanup removes the temp FS directory.

## Dependencies and integration points
Exercise signing helpers, active credentials, object-layer setup, IAM initialization, hash readers, admin policy action checks, and S3 auth verification.

## Risks and edge cases
These tests depend on global subsystem initialization and can be sensitive to test ordering if globals leak. They do not cover JWT, STS action routing, site-replication token signing, object-lock authorization, bucket-policy anonymous authorization, or middleware skew rejection.

## Test signals
Failures show auth-type classification changes, request checksum/signature validation regressions, or admin auth compatibility changes.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/auth-handler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/authtype_string.go -->
# sources/object-store/minio/cmd/authtype_string.go

## Purpose
Generated `stringer` implementation for the `authType` enum in `auth-handler.go`.

## Important APIs, types, and functions
- Compile-time ordinal assertions cover `authTypeUnknown` through `authTypeStreamingUnsignedTrailer`.
- `_authType_name` and `_authType_index` encode trimmed auth type names.
- `func (i authType) String() string` returns a stable name or `authType(<n>)` for out-of-range values.

## Control flow
Compilation verifies enum ordinals by indexing a one-element array with each expected offset. Runtime string conversion bounds-checks and slices the generated concatenated name table.

## State and persistence behavior
No runtime state or persistence. It is generated source that must track `authType` constants exactly.

## Dependencies and integration points
Generated by `go generate stringer -type=authType -trimprefix=authType auth-handler.go`. Useful in diagnostics, logs, and tests that format auth types.

## Risks and edge cases
Adding or reordering `authType` constants without regeneration makes the file stale or uncompilable. Out-of-range values intentionally format numerically.

## Test signals
Compilation is the key guard; `auth-handler_test.go` validates behavior of the underlying enum classification, not generated names.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/authtype_string.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/background-heal-ops.go -->
# sources/object-store/minio/cmd/background-heal-ops.go

## Purpose
Implements background healing task dispatch for disk format, bucket, and object healing, including worker sizing and optional throttling based on active HTTP IO.

## Important APIs, types, and functions
- `healTask` carries bucket/object/version/options and an optional response channel.
- `healResult` carries a `madmin.HealResultItem` plus error.
- `healRoutine` owns the task channel and worker count.
- `activeListeners`, `currentHTTPIO`, `waitForLowIO`, and `waitForLowHTTPReq` support IO-aware throttling.
- `initBackgroundHealing`, `(*healRoutine).AddWorker`, `newHealRoutine`, and `healDiskFormat` run the background healer.

## Control flow
`newHealRoutine` defaults worker count to half of `GOMAXPROCS`, allows `_MINIO_HEAL_WORKERS` override, and falls back to four if the result is zero. `initBackgroundHealing` creates a background heal sequence, starts worker goroutines, and launches a new global heal sequence. Each worker selects on tasks or context cancellation, dispatches `nopHeal`, disk-format heal, bucket heal, or object heal, sends synchronous results when `respCh` is present, and otherwise updates background sequence metrics.

## State and persistence behavior
This file mutates in-memory healing metrics/state through `globalBackgroundHealRoutine` and `globalBackgroundHealState`. Actual repair persistence happens in `ObjectLayer.HealFormat`, `HealBucket`, and `HealObject`.

## Dependencies and integration points
Integrated with `ObjectLayer`, admin heal options/results from `madmin-go`, global HTTP listen/trace subscriber counts, global heal config, background heal sequence metrics, and environment configuration.

## Risks and edge cases
Worker count override can oversubscribe resources. `waitForLowIO` depends on external callers and current HTTP count excluding listeners. Async tasks without `respCh` rely on metrics for observability. `healDiskFormat` suppresses `errNoHealRequired` but returns other format-heal errors.

## Test signals
No direct tests in this subset; coverage likely comes from heal/admin integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/background-heal-ops.go -->
