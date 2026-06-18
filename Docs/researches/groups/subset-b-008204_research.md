# subset-b-008204 Research

Grouped research for MinIO Signature V4 parsing/verification and site-replication metric/resync files. Each section preserves its source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/signature-v4-parser.go -->
# sources/object-store/minio/cmd/signature-v4-parser.go

## Purpose
Implements parsers for AWS Signature Version 4 credential scopes, Authorization headers, and presigned-query parameters. The file converts raw S3/STS request authentication fields into structured `credentialHeader`, `signValues`, and `preSignValues` records that later verification code can canonicalize and compare.

## Important APIs, Types, And Functions
`credentialHeader` stores the parsed access key plus date, region, service, and `aws4_request` scope fields. Its `getScope()` method rebuilds the canonical credential scope string. `signValues` models an Authorization header with credential, signed headers, and signature. `preSignValues` embeds `signValues` and adds presign request time and expiry duration.

`getReqAccessKeyV4()` extracts credentials from form-style `X-Amz-Credential` first, then falls back to the Authorization header and returns `checkKeyValid()` results. `parseCredentialHeader()` accepts access keys containing `/`, validates key syntax through `auth.IsAccessKeyValid`, parses the date with `yyyymmdd`, validates the configured region via `isValidRegion`, enforces S3 vs STS service names, and requires `aws4_request`. `parseSignature()` and `parseSignedHeader()` validate individual `Signature=` and `SignedHeaders=` tags. `doesV4PresignParamsExist()` checks the required presign query keys. `parsePreSignV4()` validates algorithm, credential, ISO8601 date, non-negative and <= 7-day expiry, signed headers, and signature. `parseSignV4()` normalizes spacing while preserving spaces inside the credential/access key portion.

## Control Flow
Header parsing flows from raw input into tag-level validators, then into credential-scope validation, then into the final structured value. Presigned parsing first performs required-parameter presence checks, then rejects unsupported algorithm values before parsing the credential scope, date, expiry, signed headers, and signature. Authorization parsing strips `AWS4-HMAC-SHA256`, demands exactly three comma-separated fields, and delegates each field to the narrower parser.

## State And Persistence
This file is stateless. It reads `http.Request` headers/forms and global region/service context only through helper calls, and returns `APIErrorCode` values instead of mutating persistent storage.

## Dependencies And Integration Points
Depends on MinIO auth key validation, MinIO HTTP header constants, region/service constants from `signature-v4.go`, and `checkKeyValid()`/`isValidRegion()` from `signature-v4-utils.go`. Its outputs feed `doesSignatureMatch()`, `doesPresignedSignatureMatch()`, POST policy verification, and request access-key discovery for S3 and STS endpoints.

## Risks And Edge Cases
The parser is security-sensitive: permissive space removal, access keys containing separators, and fallback from form credential to Authorization header all affect compatibility and potential ambiguity. Expiry parsing appends `s`, so only second-based presign expiry strings are accepted. Region validation intentionally accepts request region when configured region is empty, which preserves ListBuckets compatibility but broadens accepted credential scopes.

## Test Signals
`signature-v4-parser_test.go` covers malformed credential tags, invalid keys/date/region/service/request version, access keys containing `/`, `=`, and spaces, signature/signed-header parsing, Authorization header parsing, required presign parameters, malformed presigned dates/expiries, negative expiry, and maximum 7-day expiry enforcement.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/signature-v4-parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/signature-v4-parser_test.go -->
# sources/object-store/minio/cmd/signature-v4-parser_test.go

## Purpose
Provides table-driven unit coverage for Signature V4 parser behavior in `signature-v4-parser.go`. The tests validate parser error mapping and successful extraction of credential scopes, signatures, signed headers, Authorization headers, and presigned query values.

## Important APIs, Types, And Functions
Helper functions include `generateCredentialStr()`, `joinWithSlash()`, `generateCredentials()`, and `validateCredentialfields()`. Test entry points are `TestParseCredentialHeader`, `TestParseSignature`, `TestParseSignedHeaders`, `TestParseSignV4`, `TestDoesV4PresignParamsExist`, and `TestParsePreSignV4`.

## Control Flow
Each test builds explicit raw strings or `url.Values`, invokes the parser under test, checks the returned `APIErrorCode`, and, on success, validates parsed fields. The presign tests construct query parameters from alternating key/value slices and compare normalized date and duration values rather than direct object identity.

## State And Persistence
The file has no persistent state. It uses `UTCNow()` to generate valid date strings, but all state is local to the test cases.

## Dependencies And Integration Points
Depends on the parser types/functions under test, MinIO error code constants, `UTCNow()`, and Signature V4 format constants. These tests are part of the `cmd` package, so they directly access unexported parser helpers.

## Risks And Edge Cases
The tests intentionally cover malformed fields and compatibility cases, including access keys with `/`, `=`, and spaces. They do not exercise `getReqAccessKeyV4()` fallback behavior or IAM validation directly. Time-sensitive cases use current time, which is safe for format parsing but not a full clock-skew verification test.

## Test Signals
Strong signal for parser branch coverage and error-code stability. Any change to accepted credential grammar, service validation, presign expiry semantics, or Authorization header field ordering should require updates here.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/signature-v4-parser_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/signature-v4-utils.go -->
# sources/object-store/minio/cmd/signature-v4-utils.go

## Purpose
Holds shared helper logic for Signature V4 verification: payload hash selection, region comparison, credential lookup, HMAC derivation support, signed-header extraction, whitespace normalization, and metadata-header signing checks.

## Important APIs, Types, And Functions
Constants `unsignedPayload` and `unsignedPayloadTrailer` encode S3 compatibility values for `x-amz-content-sha256`. `skipContentSha256Cksum()` decides whether request-body SHA256 validation can be skipped. `getContentSha256Cksum()` returns the canonical payload hash source, reading and restoring STS bodies when needed. `isValidRegion()` compares request and configured regions while translating legacy `US` to the default MinIO region.

`checkKeyValid()` resolves an access key against root credentials or `globalIAMSys`, handles uninitialized IAM, disabled credentials, token claims, root-access disablement, service-account owner semantics, and session-policy demotion. `sumHMAC()` is the low-level HMAC-SHA256 primitive used by signing-key code. `extractSignedHeaders()` collects all signed header/query values and reconstructs Go-stripped special headers such as `host`, `expect`, `transfer-encoding`, and `content-length`. `signV4TrimAll()` normalizes AWS canonical header whitespace. `checkMetaHeaders()` enforces that all `X-Amz-Meta-*` request headers are represented in the signed header map.

## Control Flow
Payload hash logic branches on presigned vs header-based Signature V4 and on STS service type. Credential validation first checks root credentials, then IAM storage, then session-token claims, then owner/root-access policy. Signed-header extraction requires `host`, resolves normal headers, query parameters, and compatibility special cases, returning `ErrUnsignedHeaders` for missing signed headers.

## State And Persistence
The helper functions mostly compute transient values, but `checkKeyValid()` reads global server state: `globalActiveCred`, `globalIAMSys`, `globalAPIConfig`, token claims, and root-access policy. `getContentSha256Cksum()` temporarily consumes and replaces `r.Body` for STS requests. No persistent writes occur.

## Dependencies And Integration Points
Depends on internal auth, hash, HTTP constants, logger, IAM subsystem globals, policy session claims, and request-classification helpers such as `isRequestPresignedSignatureV4()`. It is used by the parser and verifier files to build canonical requests and authorize request credentials before signature comparison.

## Risks And Edge Cases
Security-sensitive decisions include allowing `UNSIGNED-PAYLOAD`, compatibility skipping of broken empty-SHA256 clients when strict S3 compatibility is disabled, and reconstructing headers removed by Go's HTTP server. `checkMetaHeaders()` compares only the first header value for each metadata header, which matches much S3 metadata usage but can be brittle for multi-valued metadata. IAM initialization errors intentionally map to retryable-style API errors.

## Test Signals
`signature-v4-utils_test.go` covers owner vs IAM user credential validation, checksum-skip rules, region aliases, special signed-header extraction, whitespace trimming including Unicode input, canonical content SHA selection, and metadata-header signing checks.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/signature-v4-utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/signature-v4-utils_test.go -->
# sources/object-store/minio/cmd/signature-v4-utils_test.go

## Purpose
Tests Signature V4 helper behavior that depends on HTTP request shape, IAM initialization, region compatibility, header canonicalization, and metadata signing requirements.

## Important APIs, Types, And Functions
The file defines `TestCheckValid`, `TestSkipContentSha256Cksum`, `TestIsValidRegion`, `TestExtractSignedHeaders`, `TestSignV4TrimAll`, `TestGetContentSha256Cksum`, and `TestCheckMetaHeaders`.

## Control Flow
`TestCheckValid` builds a filesystem-backed test object layer, initializes config/IAM subsystems, signs a request with root credentials, validates root ownership, checks invalid access-key rejection, creates an IAM user, validates non-owner status, attaches a policy, and verifies policy propagation. Other tests are table-driven over header/query combinations and direct helper calls.

## State And Persistence
This test file creates temporary filesystem state with `prepareFS()`, initializes global MinIO config/IAM subsystems, creates a test IAM user, and attaches policy data. Other tests use in-memory `http.Request` values only. Temporary roots are removed at test cleanup.

## Dependencies And Integration Points
Depends on MinIO test infrastructure (`prepareFS`, `newTestConfig`, subsystem initialization), `madmin-go` user requests, internal auth credential creation, and Signature V4 helper functions. It exercises the integration boundary between request signing helpers and the IAM subsystem.

## Risks And Edge Cases
`TestCheckValid` is more integration-like than pure unit testing and may be sensitive to subsystem initialization timing; it sleeps to allow policy attachment visibility. The metadata test covers headers and query-form metadata, but not multi-valued metadata mismatches. The checksum tests cover presigned detection using `X-Amz-Credential` but not STS body hashing.

## Test Signals
Good regression signal for compatibility behavior around legacy `US` region, Go-stripped headers, broken SHA256 clients, and metadata-signing enforcement. Failures here often imply request authentication compatibility or IAM lookup regressions.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/signature-v4-utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/signature-v4.go -->
# sources/object-store/minio/cmd/signature-v4.go

## Purpose
Implements AWS Signature Version 4 canonicalization and signature verification for Authorization-header requests, presigned query requests, and form POST policies. It is the core verifier that reconstructs canonical requests, derives signing keys, and compares client signatures.

## Important APIs, Types, And Functions
Constants include `signV4Algorithm`, `iso8601Format`, and `yyyymmdd`. `serviceType` selects S3 or STS signing scope. Canonicalization helpers are `getCanonicalHeaders()`, `getSignedHeaders()`, `getCanonicalRequest()`, `getScope()`, and `getStringToSign()`. Cryptographic helpers are `getSigningKey()` and `getSignature()`, both backed by HMAC-SHA256.

`doesPolicySignatureMatch()` dispatches V2 vs V4 POST policy verification. `compareSignatureV4()` compares hex signature strings with constant-time comparison. `doesPolicySignatureV4Match()` parses form credentials, validates the access key, derives the policy signing key, and compares the form policy signature. `doesPresignedSignatureMatch()` parses presign query values, validates credentials and headers, checks metadata headers, enforces future-skew and expiry windows, rebuilds the canonical query string without the signature, verifies payload hash and session token consistency, compares signatures, and records `x-amz-signature-age`. `doesSignatureMatch()` verifies Authorization-header signatures using canonical headers, query string, request path, method, payload hash, and request date.

## Control Flow
Canonical request creation lowercases/sorts headers, encodes paths with S3 path rules, preserves canonical query encoding with `+` converted to `%20`, and joins the canonical request fields with newlines. Verification flows parse signature metadata, validate credentials through `checkKeyValid()`, extract signed headers, compute canonical request and string-to-sign, derive the scoped signing key from secret/date/region/service, then constant-time compare expected and provided signatures.

## State And Persistence
No durable state is written. The verifier reads global site region, active credentials, IAM, root-access settings, token/session claims, global clock helpers, and skew constants. `doesPresignedSignatureMatch()` mutates the request header by setting `x-amz-signature-age` after successful verification.

## Dependencies And Integration Points
Depends on MinIO S3 path encoding, set helpers, internal SHA256, auth credentials, MinIO HTTP constants, parser helpers, IAM validation helpers, metadata-header checks, and V2 policy verification. It integrates with S3 object APIs, STS APIs, POST policy upload handling, and request middleware that supplies payload hashes and parsed forms.

## Risks And Edge Cases
This file is security-critical. Query canonicalization must preserve every non-signature parameter exactly, including response override parameters. Presigned verification intentionally treats empty configured region as permissive. Session-token comparison uses constant-time comparison. Time-window checks depend on `UTCNow()` and `globalMaxSkewTime`; skew changes affect accepted future requests. Canonical header extraction delegates important compatibility behavior to `extractSignedHeaders()`.

## Test Signals
`signature-v4_test.go` covers POST policy signature success/failure and presigned-request failures for missing query params, invalid keys, unsigned host/content headers, expiry, future dates, invalid signatures, empty configured region, extra response parameters, and missing signed payload headers. Parser and utility tests cover lower-level canonicalization inputs.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/signature-v4.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/signature-v4_test.go -->
# sources/object-store/minio/cmd/signature-v4_test.go

## Purpose
Provides targeted regression coverage for Signature V4 policy and presigned URL verification paths in `signature-v4.go`.

## Important APIs, Types, And Functions
`niceError()` formats MinIO `APIErrorCode` values for readable assertion output. `TestDoesPolicySignatureMatch()` validates V4 POST policy handling. `TestDoesPresignedSignatureMatch()` validates presigned query verification error ordering and compatibility cases.

## Control Flow
The policy test prepares a temporary filesystem object layer, builds form headers, and asserts missing credential, invalid access key, bad signature, and valid policy outcomes. The presigned test prepares config, computes a fixed payload hash, constructs table-driven query/header maps, creates requests, parses forms, then calls `doesPresignedSignatureMatch()` and checks exact error codes.

## State And Persistence
Tests create temporary object-layer/config state through `prepareFS()` and `newTestConfig()`, then remove the filesystem root. Request state is local to each test case.

## Dependencies And Integration Points
Depends on active global test credentials, MinIO test object-layer setup, Signature V4 constants and signing helpers, `doesPolicySignatureMatch()`, and `doesPresignedSignatureMatch()`. It exercises integration between parser, canonicalizer, credential validation, and request time checks.

## Risks And Edge Cases
The table focuses on expected rejection paths and one valid policy case, but does not include a fully valid presigned request. Some expected errors depend on validation order, so refactors that change order may require careful review even if final rejection remains correct.

## Test Signals
Strong signal for error-code stability in authentication middleware. Covers common failure classes: missing auth fields, invalid credentials, unsigned headers, expired/future presigns, invalid signatures, empty region behavior, and extra non-auth query parameters.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/signature-v4_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/site-replication-metrics.go -->
# sources/object-store/minio/cmd/site-replication-metrics.go

## Purpose
Defines in-memory site-replication metric models and update/aggregation logic. It tracks replication counts, bytes, failures, latency, transfer-rate summaries, endpoint health, and summary DTOs exposed through admin/status APIs.

## Important APIs, Types, And Functions
`RStat` stores count and byte totals. `RTimedMetrics` combines last-minute, last-hour, since-uptime, and error-code counts; methods `String()`, `toMetric()`, `addsize()`, and `merge()` convert, update, and combine timed failure metrics. `SRStats` is the site-level mutable store with replica totals, deployment status map, ticker, and lock. `SRStatus` stores per-deployment replicated size/count, failures, latency, large/small transfer stats, and endpoint identity.

`SRStats.update()` applies `replStat` events, creating per-deployment status as needed and updating completed vs failed metrics. `SRStats.get()` snapshots per-deployment metrics and enriches them with endpoint health from `globalBucketTargetSys.healthStats()`. `SRStatus.updateXferRate()` classifies transfers by `minLargeObjSize`. `newSRStats()`, `trackEWMA()`, and `updateMovingAvg()` maintain EWMA transfer-rate measurements. `SRMetric` and `SRMetricsSummary` are admin-facing metric summaries.

## Control Flow
Replication events enter through `SRStats.update()`, which locks the map and updates counters based on `Completed`, `Failed`, or `Pending`. Readout flows through `get()`, which clones transfer stats, merges large and small transfer rates into totals, translates failure data to `madmin.TimedErrStats`, and overlays endpoint uptime/latency/online status. A background ticker periodically updates moving averages until `GlobalContext` is canceled.

## State And Persistence
State is in memory only in this file. Counters use a mix of mutex-protected map state and atomics inside timed metrics. The EWMA ticker is process-local. Generated msgp code can serialize these types, but this hand-written file does not perform disk writes itself.

## Dependencies And Integration Points
Depends on `madmin-go` admin DTOs, MinIO client error response translation, global bucket target health stats, replication latency/time-window types, queue/proxy/worker metric types, and transfer-stat helpers. It integrates with replication event reporting and admin site-replication metrics responses.

## Risks And Edge Cases
Concurrency correctness depends on callers using `SRStats` methods rather than mutating maps directly. `RTimedMetrics.addsize()` updates atomic totals but also mutates `ErrCounts` without an internal lock; current callers update it under `SRStats.lock`, so that locking contract matters. The generated codec omits some runtime-only fields by tag or structure, so serialization must not be assumed to preserve ticker/lock semantics.

## Test Signals
The generated codec test file covers msgp round trips for `RStat`, `RTimedMetrics`, `SRMetric`, `SRMetricsSummary`, `SRStats`, and `SRStatus`. There is no focused hand-written test here for update aggregation, EWMA behavior, endpoint health enrichment, or AccessDenied error counting.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/site-replication-metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/site-replication-metrics_gen.go -->
# sources/object-store/minio/cmd/site-replication-metrics_gen.go

## Purpose
Generated tinylib/msgp serialization code for site-replication metric structs declared in `site-replication-metrics.go`. It provides MessagePack encoding, decoding, marshaling, unmarshaling, skipping unknown fields, and size estimation for metrics persistence/transport paths.

## Important APIs, Types, And Functions
For each supported type, the generator emits `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize`. Covered types are `RStat`, `RTimedMetrics`, `SRMetric`, `SRMetricsSummary`, `SRStats`, and `SRStatus`.

`RStat` serializes `Count` and `Bytes`. `RTimedMetrics` serializes `LastHour`, `SinceUptime`, `LastMinute`, and `ErrCounts`. `SRMetric` serializes deployment ID, endpoint health, latency, replicated totals, and failure metrics, but not `XferStats`. `SRMetricsSummary` serializes active workers, replica totals, queue/proxy metrics, peer metric map, and uptime. `SRStats` serializes replica totals and the deployment status map. `SRStatus` serializes replicated totals, failures, latency, large/small transfer stats under compact `lt`/`st` keys, endpoint, and secure flag.

## Control Flow
Decode paths read a map header, switch on field names, decode known fields, and skip unknown fields. Map fields are allocated or cleared before filling to avoid stale entries. Pointer fields such as `*SRStatus`, `XferRateLrg`, and `XferRateSml` handle nil values explicitly. Encode/marshal paths write fixed map sizes and field keys in generated order. `Msgsize()` returns an upper-bound estimate used for buffer preallocation.

## State And Persistence
The file performs no storage I/O itself, but defines the binary wire/storage shape for these metric types. Deserialization mutates receiver structs and clears existing maps. Unknown fields are skipped, giving some forward/backward compatibility.

## Dependencies And Integration Points
Depends on `github.com/tinylib/msgp/msgp` and msgp implementations for nested MinIO types such as replication windows, latency, transfer stats, active workers, queue/proxy metrics, and `madmin` latency/timed stats. It is regenerated from `//go:generate msgp -file $GOFILE` in the hand-written metrics file.

## Risks And Edge Cases
Because this file is generated, manual edits would be fragile. Wire field names are a compatibility surface; renaming struct fields or msg tags changes persisted/transported data. `SRMetric` serialization does not include `XferStats`, so consumers relying on msgp round trips should not expect the transfer summary map to survive for that DTO. Map iteration order is nondeterministic for encoded maps, which should be acceptable for MessagePack semantics but not byte-for-byte fixtures.

## Test Signals
`site-replication-metrics_gen_test.go` exercises marshal/unmarshal, skip, encode/decode, size warning, and benchmarks for every generated type. These tests validate codec mechanics, not semantic correctness of metric aggregation.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/site-replication-metrics_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/site-replication-metrics_gen_test.go -->
# sources/object-store/minio/cmd/site-replication-metrics_gen_test.go

## Purpose
Generated test and benchmark coverage for MessagePack serialization of site-replication metric types.

## Important APIs, Types, And Functions
For each generated metric type, the file emits a marshal/unmarshal test, encode/decode test, marshal/append/unmarshal benchmarks, and encode/decode benchmarks. Covered types are `RStat`, `RTimedMetrics`, `SRMetric`, `SRMetricsSummary`, `SRStats`, and `SRStatus`.

## Control Flow
Each marshal/unmarshal test creates a zero-value instance, calls `MarshalMsg(nil)`, calls `UnmarshalMsg()`, asserts no leftover bytes, and verifies `msgp.Skip()` consumes the whole message. Each encode/decode test encodes into a `bytes.Buffer`, logs a warning if `Msgsize()` is smaller than actual encoded size, decodes into a new value, then verifies reader `Skip()`.

## State And Persistence
No persistent state. All values are zero-value in-memory structs and local buffers. Benchmarks reuse local buffers or endless readers for allocation/throughput measurement.

## Dependencies And Integration Points
Depends on the generated codec methods in `site-replication-metrics_gen.go` and `github.com/tinylib/msgp/msgp`. These tests are generated alongside codec code and should be regenerated rather than manually edited.

## Risks And Edge Cases
Generated tests only cover zero-value structs, so they do not validate non-empty maps, nested pointer combinations, transfer stats content, or backwards compatibility with older field sets. They are still useful for catching broken generated methods, invalid size estimates, and basic decode/skip failures.

## Test Signals
Good mechanical codec smoke tests and allocation benchmarks. Limited semantic signal for replication metric correctness or production-like encoded data.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/site-replication-metrics_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/site-replication-utils.go -->
# sources/object-store/minio/cmd/site-replication-utils.go

## Purpose
Manages site-replication resync status in memory and periodically persists it. It tracks resync state per peer deployment, per-bucket completion/failure, per-object progress, and admin-facing resync reports.

## Important APIs, Types, And Functions
`SiteResyncStatus` stores version, overall `ResyncStatusType`, peer deployment ID, per-bucket status map, total bucket count, and embedded `TargetReplicationResyncStatus`. `clone()` copies the bucket status map for safe readout. `siteResyncPrefix` defines the metadata storage prefix. `resyncState` maps a peer to a resync ID and last-save timestamp. `siteResyncMetrics` holds `resyncStatus` and `peerResyncMap` behind an RW mutex.

`newSiteResyncMetrics()` starts background `save()` and `init()` goroutines. `init()` retries `load()` with randomized sleeps until object layer/site-replication data is available. `load()` reads peer metadata via `loadSiteResyncMetadata()`. `report()` converts internal state to `madmin.SiteResyncMetrics`. `save()` periodically persists changed valid states via `saveSiteResyncMetadata()`. `updateState()`, `incBucket()`, `deleteBucket()`, `siteResyncStatus()`, `updateMetric()`, `status()`, and `siteStatus()` update and query resync progress.

## Control Flow
Initialization starts asynchronous load and save loops. Load waits for object-layer readiness and site-replication enablement, then imports peer resync metadata except for the local deployment. Save wakes on `siteResyncSaveInterval`, checks if site replication is enabled, finds statuses with valid states and newer `LastUpdate` than `LastSaved`, and saves them concurrently while holding the metrics lock. Runtime updates set state on resync start/end, update bucket statuses, delete removed buckets from active resyncs, aggregate object progress, and serve memory-first status queries with disk fallback.

## State And Persistence
State is both in-memory and persisted under the site-resync metadata path through `loadSiteResyncMetadata()` and `saveSiteResyncMetadata()`. In-memory maps are protected by `siteResyncMetrics` locks. Background goroutines run until the provided context is canceled. `LastSaved` prevents repeated saves of unchanged states.

## Dependencies And Integration Points
Depends on site-replication globals (`globalSiteReplicationSys`, `globalDeploymentID()`), object-layer access, metadata load/save helpers, `madmin-go` resync DTOs, `GlobalContext`, `UTCNow()`, resync option/status types, and target replication status types. It integrates with replication resync workflows, bucket deletion handling, admin status APIs, and metadata persistence.

## Risks And Edge Cases
Holding the metrics lock while launching and waiting for save goroutines serializes updates during persistence and can block hot paths if storage is slow. In `updateState()`, terminal state handling that misses an existing resync stores the zero value `st` and saves it, which deserves scrutiny because it may not persist the passed terminal status. `deleteBucket()` returns on the first missing/completed/failed status while iterating peers, so later peers may not be processed. The init retry loop sleeps without selecting on context during the sleep interval, delaying shutdown by up to roughly ten seconds.

## Test Signals
This hand-written file has no direct dedicated test in the listed sources. Generated codec tests cover `SiteResyncStatus` serialization only, not background load/save, status transitions, bucket deletion, or persistence error handling.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/site-replication-utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/site-replication-utils_gen.go -->
# sources/object-store/minio/cmd/site-replication-utils_gen.go

## Purpose
Generated tinylib/msgp serialization code for `SiteResyncStatus`, the persisted and transported site-replication resync status DTO from `site-replication-utils.go`.

## Important APIs, Types, And Functions
Implements `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` on `*SiteResyncStatus`. The encoded map uses compact msg field names from struct tags: `v` for version, `ss` for status, `did` for deployment ID, `bkts` for bucket statuses, `tb` for total buckets, and `cst` for embedded current target resync status.

## Control Flow
Decode and unmarshal read a map header, switch on field keys, decode known fields, allocate or clear `BucketStatuses`, and skip unknown fields. Encode and marshal write a fixed six-field map and delegate nested encoding to `ResyncStatusType` and `TargetReplicationResyncStatus`. `Msgsize()` estimates the encoded size including dynamic string/map entries.

## State And Persistence
No direct I/O occurs here. The generated methods define the binary representation used by site-resync metadata persistence and any msgp transport path. Deserialization mutates receiver state and clears existing bucket-status maps before loading new values.

## Dependencies And Integration Points
Depends on `github.com/tinylib/msgp/msgp` and msgp methods on nested resync status types. It is regenerated from `//go:generate msgp -file=$GOFILE` in `site-replication-utils.go` and supports `loadSiteResyncMetadata()`/`saveSiteResyncMetadata()` integration.

## Risks And Edge Cases
Manual edits would be overwritten and may diverge from struct tags. Field-name/tag changes are persistence-format changes. Unknown fields are skipped, which helps forward compatibility, but missing known fields leave zero values. Map iteration order for bucket statuses is nondeterministic in bytes.

## Test Signals
`site-replication-utils_gen_test.go` validates zero-value marshal/unmarshal, skip, encode/decode, size warning, and benchmarks for `SiteResyncStatus`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/site-replication-utils_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/site-replication-utils_gen_test.go -->
# sources/object-store/minio/cmd/site-replication-utils_gen_test.go

## Purpose
Generated test and benchmark coverage for `SiteResyncStatus` MessagePack serialization.

## Important APIs, Types, And Functions
Defines `TestMarshalUnmarshalSiteResyncStatus`, `BenchmarkMarshalMsgSiteResyncStatus`, `BenchmarkAppendMsgSiteResyncStatus`, `BenchmarkUnmarshalSiteResyncStatus`, `TestEncodeDecodeSiteResyncStatus`, `BenchmarkEncodeSiteResyncStatus`, and `BenchmarkDecodeSiteResyncStatus`.

## Control Flow
The marshal/unmarshal test serializes a zero-value `SiteResyncStatus`, deserializes it, asserts no leftover bytes, and checks that `msgp.Skip()` consumes the encoded message. The encode/decode test writes to a buffer, compares actual encoded length to `Msgsize()` as a warning, decodes into a new value, and verifies skip through a `msgp.Reader`. Benchmarks measure marshal, append, unmarshal, encode, and decode paths.

## State And Persistence
No persistent state. Tests operate only on zero-value structs and local buffers.

## Dependencies And Integration Points
Depends on generated codec methods in `site-replication-utils_gen.go` and `github.com/tinylib/msgp/msgp`. The file is generated and should remain synchronized with the source struct and codec generator.

## Risks And Edge Cases
The generated tests do not cover non-empty bucket-status maps, embedded target resync fields, or compatibility with older persisted metadata. They also do not exercise `siteResyncMetrics` load/save behavior. Their role is codec smoke testing and benchmark baselining.

## Test Signals
Useful mechanical signal that the generated `SiteResyncStatus` codec can round-trip zero values, skip encoded data, and maintain reasonable `Msgsize()` estimates. Limited semantic coverage for actual resync status workflows.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/site-replication-utils_gen_test.go -->
