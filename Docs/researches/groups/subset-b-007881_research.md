# subset-b-007881 Research

Grouped source research for SeaweedFS S3 API XML DTOs, S3 bucket/error helpers, and the lifecycle daily-run/bootstrap worker files in this work item.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_xsd_generated.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_xsd_generated.go

Purpose: generated `s3api` XML binding code for an older S3 SOAP/XML model. It defines request and response DTOs for bucket/object operations, ACLs, versioning, logging, notifications, copy, put/get/list/delete, and helper scalar encodings. The file is data-model heavy and intentionally has little business logic; it exists so handlers can marshal and unmarshal AWS-shaped XML.

Important APIs/types: `AccessControlPolicy`, `AccessControlList`, `Grant`, `CanonicalUser`, `BucketLoggingStatus`, `LoggingSettings`, request/response structs such as `CreateBucket`, `DeleteBucket`, `GetObject`, `GetObjectExtended`, `PutObject`, `PutObjectInline`, `CopyObject`, `ListBucket`, `ListBucketResult`, `ListVersionsResult`, `VersionEntry`, `DeleteMarkerEntry`, and `PostResponse`. Enum-like string aliases include `MetadataDirective`, `MfaDeleteStatus`, `Payer`, `Permission`, `StorageClass`, and `VersioningStatus`. Generated `Anon*` structs wrap operation-specific SOAP request/response shapes.

Control flow: most custom methods are `MarshalXML`/`UnmarshalXML` overlays that temporarily reinterpret `time.Time` as `xsdDateTime` and `[]byte` as `xsdBase64Binary`. This preserves generated struct field names while applying custom XML text behavior for timestamps and inline object data. `_unmarshalTime` first parses fractional seconds without timezone and then retries with a numeric timezone; `_marshalTime` always formats with timezone. `xsdDateTime.MarshalXML` and `MarshalXMLAttr` omit zero times.

State and persistence behavior: no durable state is owned here. The structs are transient wire payloads. Persistence risk is indirect: handlers may store values decoded through these DTOs, so XML tag and timestamp/base64 behavior becomes part of compatibility.

Dependencies and integration points: depends only on `bytes`, `encoding/base64`, `encoding/xml`, and `time`. Other S3 API code can use these DTOs with Go's XML encoder or the S3 error handler's XML response helpers. The namespace on `ListAllMyBucketsResult` is explicitly `http://s3.amazonaws.com/doc/2006-03-01/`, aligning with S3 XML responses.

Risks: this is generated but appears manually modified or generated from a schema with duplicate field issues: `Anon19` has duplicate `Metadata` fields and `PutObjectInline` has duplicate `ContentLength` fields, which would be a Go compile error if this file is in the active build. There is also a duplicate `overlay.T = (*T)(t)` assignment in one unmarshaler, harmless but suspicious. Regeneration must be validated by `go test`/`go test ./weed/s3api/...` because field tags and wrapper names are compatibility-sensitive. Time parsing does not parse every RFC3339 variant; it is bound to the generated XSD format. `xsdBase64Binary.MarshalText` ignores write/close errors, practically low risk with a bytes buffer but still generated-code style.

Test signals: no direct tests in this subset target this generated file. Coverage is likely indirect through S3 API XML response/request tests. Any change should be compile-tested first because generated duplicate fields would fail early, and behavior-tested around list/get/put/copy XML.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_xsd_generated.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_xsd_generated_helper.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_xsd_generated_helper.go

Purpose: adds a hand-written `Grantee` type to the generated `s3api` XML model. It fills a gap in the generated ACL model by representing the XML/XSI attributes and optional grantee identity fields used inside ACL grants.

Important APIs/types: `Grantee` has XML namespace/type attributes (`xmlns:xsi`, `xsi:type`), a `Type` element, and optional `ID`, `DisplayName`, and `URI` elements.

Control flow: no functions. Encoding/decoding is entirely driven by struct tags and the standard XML encoder.

State and persistence behavior: no persistent state. It affects ACL XML compatibility because `Grant` in the generated file embeds `Grantee`.

Dependencies and integration points: package-local companion for `s3api_xsd_generated.go`, particularly `Grant` and `AccessControlPolicy`. It is used wherever ACL XML is marshaled or unmarshaled.

Risks: because this helper supplies XML namespace attributes manually, tag changes can break ACL interoperability. It is not generated, so schema regeneration could conflict with or supersede it.

Test signals: no direct tests in this subset. ACL handler tests elsewhere should validate canonical user/group grantees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_xsd_generated_helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3bucket/s3api_bucket.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3bucket/s3api_bucket.go

Purpose: central S3 bucket name validator for SeaweedFS S3 API. It enforces AWS-like bucket naming constraints plus a SeaweedFS-specific reservation for `filemeta`, which collides with filer metadata storage on SQL backends.

Important APIs/types: `VerifyS3BucketName(name string) error` is the exported validator. `reservedBucketName` is the package constant for `filemeta`.

Control flow: validation checks length, reserved name, allowed runes, adjacent periods, starting and ending characters, reserved `xn--` prefix, reserved `-s3alias` suffix, and IP-address-like names via `net.ParseIP`. It returns the first validation error encountered.

State and persistence behavior: no state is persisted here, but the `filemeta` rejection protects persistent filer metadata tables/collections from bucket-name collisions that can make buckets undeletable and interfere with fsck.

Dependencies and integration points: uses `net`, `strings`, `unicode`, and `fmt`. Called by bucket creation paths before creating filer entries or bucket metadata.

Risks: AWS bucket naming rules evolve; this file implements a subset and has a TODO for transfer acceleration dot restrictions. Unicode number categories are accepted through `unicode.IsNumber`, not just ASCII digits, which may be broader than AWS DNS-style rules. Error messages are user-visible and may be asserted by clients only loosely.

Test signals: `s3api_bucket_test.go` covers invalid uppercase, IP address, adjacent dots, too short, leading dot, trailing hyphen, all hyphens, invalid character, and `filemeta`, plus several valid names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3bucket/s3api_bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3bucket/s3api_bucket_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3bucket/s3api_bucket_test.go

Purpose: regression tests for `VerifyS3BucketName`.

Important APIs/types: `Test_verifyBucketName` uses testify `assert` to check lists of invalid and valid names.

Control flow: the test iterates invalid names expecting non-nil errors, then valid names expecting nil errors.

State and persistence behavior: none. The `filemeta` invalid case indirectly protects the filer metadata collision rule.

Dependencies and integration points: imports `testing` and `github.com/stretchr/testify/assert`. It exercises only the local validator, not bucket creation integration.

Risks: the test does not cover newer reserved suffixes/prefixes beyond `filemeta` and does not cover `xn--` or `-s3alias` even though implementation rejects them. It also does not catch the potential non-ASCII digit allowance. Variable naming in the valid loop uses `invalidName`, a harmless readability issue.

Test signals: clear positive/negative smoke coverage for bucket naming, with room for table-driven expansion of reserved AWS names and boundary lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3bucket/s3api_bucket_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3err/audit_fluent.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3err/audit_fluent.go

Purpose: S3 access audit logging through fluent-logger, plus per-request audit tracking to avoid duplicate fallback logs. It builds AWS-style access records from HTTP requests and posts them asynchronously when configured.

Important APIs/types: `AccessLog`, `AccessLogHTTP`, and `AccessLogExtend` define audit payloads. `InitAuditLog` loads fluent config. `GetAccessLog` builds a record. `PostLog` and `PostAccessLog` emit records. `EnsureAuditTracking`, `MarkAuditLogged`, and `AuditAlreadyLogged` maintain an atomic per-request flag.

Control flow: `InitAuditLog` reads JSON config into `fluent.Config`, defaults `TagPrefix` from `ENVIRONMENT`, enables async posting, and installs a callback logger. `GetAccessLog` extracts bucket/key, error code, request id, requester identity from context, signature type, host, user-agent, remote IP, and operation name. Operation classification inspects query keys such as `delete`, `tagging`, `lifecycle`, `acl`, and `policy`. `PostLog` marks the request logged before checking whether `Logger` is nil, then posts if configured.

State and persistence behavior: global mutable state includes `Logger`, `hostname`, and `environment`. The per-request audit flag is an `atomic.Bool` stored in request context. Logs are externalized to fluent; no local persistence occurs.

Dependencies and integration points: integrates with `fluent-logger-golang`, SeaweedFS `glog`, S3 constants helpers, identity context helpers, and `request_id`. It is called by S3 response writers and likely middleware fallback paths.

Risks: forwarded headers are trusted as-is; the comment explicitly requires proxy-boundary sanitation to prevent spoofed remote IPs. Global `Logger` can be replaced without synchronization, which is typical for init-time config but risky for dynamic reconfiguration/tests. Operation selection returns on the first query key iteration, and Go map iteration is random; requests with multiple recognized subresources could classify nondeterministically. Marking logged before nil logger intentionally suppresses fallback logs even when fluent is disabled.

Test signals: `audit_fluent_test.go` covers request ID source, remote IP precedence including IPv6 and forwarded headers, identity fallback holder behavior, anonymous requester, and audit tracking idempotence/flag transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3err/audit_fluent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3err/audit_fluent_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3err/audit_fluent_test.go

Purpose: tests audit log field extraction and duplicate-log tracking.

Important APIs/types: test functions exercise `GetAccessLog`, `EnsureAuditTracking`, `MarkAuditLogged`, and `AuditAlreadyLogged`.

Control flow: tests create `httptest` requests, attach request IDs or identity holders, set forwarding headers, and assert the resulting `AccessLog` fields. The tracking test checks untracked, newly tracked, idempotently tracked, and marked states.

State and persistence behavior: no external fluent logger is used. Tests avoid global `Logger` and focus on pure request-derived state.

Dependencies and integration points: imports S3 constants and request-id context helpers, so it validates integration with authentication/fallback identity flow.

Risks: tests do not cover `InitAuditLog`, fluent posting errors, `PostLog` mark-before-nil semantics, or operation classification across multiple query keys. Remote IP tests intentionally document trusted-header behavior but cannot enforce proxy sanitation.

Test signals: strong unit coverage for recently risky audit correctness: request IDs, identity propagation across request copies, and forwarded IP extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3err/audit_fluent_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3err/error_handler.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3err/error_handler.go

Purpose: shared HTTP response writer for S3 XML success/error responses. It standardizes request IDs, content headers, CORS fallback behavior, XML encoding, audit logging, and the default not-found route behavior.

Important APIs/types: `WriteAwsXMLResponse`, `WriteXMLResponse`, `WriteEmptyResponse`, `WriteErrorResponse`, `WriteErrorResponseWithMessage`, `EncodeXMLResponse`, `WriteResponse`, and `NotFoundHandler`. `MimeXML` is exported as the XML content type; `mimeNone` suppresses content type.

Control flow: success helpers encode XML and call `WriteResponse`. Error helpers ensure a request ID, pull mux `bucket`/`object` vars, normalize a leading slash from object, look up `APIError`, build `RESTErrorResponse`, optionally override message, write XML, and post audit log. `setCommonHeaders` always sets `x-amz-request-id` and `Accept-Ranges`, and conditionally adds permissive CORS headers for service-level requests when an `Origin` header exists. `WriteResponse` sets content length/type, writes status/body, logs at verbosity 4, and flushes the writer.

State and persistence behavior: no local persistence. It mutates HTTP response headers and triggers audit emission through `PostLog`.

Dependencies and integration points: uses AWS SDK `xmlutil` for AWS XML building, Gorilla mux for URL vars, SeaweedFS `request_id`, and audit logging in this package. All S3 handlers rely on this layer for consistent client-visible error shape.

Risks: `WriteResponse` type-asserts `w.(http.Flusher)` and will panic for a ResponseWriter that does not implement `http.Flusher`; `httptest.ResponseRecorder` does implement it in modern Go, but wrappers may not. `EncodeXMLResponse` ignores encoder errors. Service-level CORS fallback is broad (`*` plus credentials), while bucket-level requests preserve middleware decisions. `GetAPIError` returns a zero `APIError` for unmapped codes, so new `ErrorCode` constants must be mapped.

Test signals: `error_handler_test.go` verifies that request IDs already in context are reused in both header and XML body for error responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3err/error_handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3err/error_handler_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3err/error_handler_test.go

Purpose: regression test for request-id consistency in S3 error responses.

Important APIs/types: `TestWriteErrorResponseReusesRequestID` calls `WriteErrorResponse`; `extractRequestIDFromBody` extracts `<RequestId>`.

Control flow: the test creates a mux-var request with `request_id.Set`, writes `ErrNoSuchKey`, and asserts the response header and XML body use `req-123`.

State and persistence behavior: none, except `WriteErrorResponse` will call `PostLog`; with nil logger this only affects request context if tracking is present.

Dependencies and integration points: tests Gorilla mux vars and SeaweedFS request-id context integration.

Risks: coverage is narrow. It does not verify status code, content type, CORS, flush behavior, custom message override, or audit flag behavior.

Test signals: important because S3 clients depend on request IDs for support/debugging, and mismatch between header/body would break traceability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3err/error_handler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3err/s3-error.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3err/s3-error.go

Purpose: static map of S3 error code strings to human-readable default messages, derived from MinIO/AWS S3 responses.

Important APIs/types: `s3ErrorResponseMap map[string]string` keyed by AWS code strings such as `AccessDenied`, `BadDigest`, `NoSuchBucket`, `SignatureDoesNotMatch`, and `NoSuchCORSConfiguration`.

Control flow: no functions. `RESTErrorResponse.Error()` in `s3api_errors.go` consults this map when the response has no explicit `Message`.

State and persistence behavior: immutable process-local map; no persistence.

Dependencies and integration points: imports SeaweedFS `constants` for shared checksum digest text. It complements the typed `errorCodeResponse` map.

Risks: it is non-exhaustive and can drift from `errorCodeResponse`. Adding a new `APIError.Code` without adding a message here is usually acceptable because `RESTErrorResponse.Error()` falls back to a generic message, but user-facing diagnostics may degrade.

Test signals: no direct tests in this subset. Error response tests indirectly exercise mapped descriptions through `GetAPIError`, not necessarily this map's fallback path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3err/s3-error.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3err/s3api_errors.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3err/s3api_errors.go

Purpose: central typed S3 API error catalog. It maps internal `ErrorCode` constants to AWS-compatible code strings, descriptions, and HTTP status codes, and defines the XML shape for error responses.

Important APIs/types: `APIError`, `RESTErrorResponse`, `ErrorCode`, the large `const` block from `ErrNone` through `ErrNoSuchConfiguration`, checksum message constants, `errorCodeResponse`, and `GetAPIError`.

Control flow: `RESTErrorResponse.Error()` returns explicit `Message` if present, otherwise looks up `Code` in `s3ErrorResponseMap`, otherwise returns a generic code message. `GetAPIError` performs a direct map lookup by `ErrorCode`; callers then write status and XML through `error_handler.go`.

State and persistence behavior: no persisted state. The map is process-global read-only after init. Its values are part of the public S3 protocol contract.

Dependencies and integration points: depends on `net/http`, XML tags, and shared constants. It is used by handlers, auth, multipart upload, object lock, SSE, lifecycle/configuration, listing validation, and error response writers.

Risks: `ErrNone` and any unmapped `ErrorCode` return the zero `APIError` if passed to `GetAPIError`, which can lead to HTTP status 0 and empty XML fields. The growing const block requires careful insertion because integer values are implicit. Some internal codes use non-AWS code strings like `ErrTooManyRequest`, which may not match client expectations. Drift between this map and `s3-error.go` is possible.

Test signals: no dedicated map completeness test in this subset. `error_handler_test.go` exercises `ErrNoSuchKey`; many other packages likely depend on specific constants. A useful future test would iterate all non-`ErrNone` constants expected to be public and assert non-empty code/status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3err/s3api_errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/action_kind.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/action_kind.go

Purpose: defines lifecycle action identity and stable action-kind expansion for compiled S3 lifecycle rules.

Important APIs/types: `ActionKey` scopes actions by `Bucket`, `RuleHash`, and `ActionKind`. `ActionKind` enum includes expiration by days/date, noncurrent expiration, newer-noncurrent retention, abort MPU, and expired delete marker. `ActionKind.String()` returns stable on-disk leaf names. `RuleActionKinds(rule *Rule)` expands one XML rule into deterministic action kinds.

Control flow: `RuleActionKinds` appends action kinds when the matching rule field is active. `NewerNoncurrentVersions` is only emitted as `ActionKindNewerNoncurrent` when `NoncurrentVersionExpirationDays` is absent, because together they define one noncurrent expiration action. The order is deterministic: expiration days, expiration date, expired delete marker, noncurrent/newer-noncurrent, abort MPU.

State and persistence behavior: `ActionKind.String()` is load-bearing for `/etc/s3/lifecycle/<bucket>/<rule_hash>/<action_kind>/` paths and cursor/dispatcher state. Renaming strings would orphan existing lifecycle state.

Dependencies and integration points: consumed by lifecycle engine, router, dispatcher proto conversion, bootstrap walker, daily-run partitions, metrics labels, and filer persistence paths.

Risks: adding a new action kind requires updates in proto mapping (`dispatch.go`, `walker_dispatcher.go` via shared helper), engine evaluation, routing, persistence naming, metrics expectations, and tests. The implicit iota values mirror proto concepts but are not themselves wire values.

Test signals: `action_kind_test.go` pins single-action and multi-action expansion, subsumption of `NewerNoncurrentVersions`, nil/empty behavior, and stable string names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/action_kind.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/action_kind_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/action_kind_test.go

Purpose: regression tests for lifecycle action-kind expansion and stable storage labels.

Important APIs/types: tests call `RuleActionKinds` and `ActionKind.String()`.

Control flow: table tests cover each standalone action. Separate tests validate multi-action rules, noncurrent/newer-noncurrent subsumption, nil/empty rules, and string labels.

State and persistence behavior: the string test is explicitly a persistence guard because labels are directory names on disk.

Dependencies and integration points: depends on the local `Rule` model and `mustTime` helper in the same package's tests.

Risks: tests do not cover proto conversion or engine compilation directly. A new action kind can pass this file if developers forget to update dispatch mappings elsewhere.

Test signals: strong coverage of a previous bug where multi-action XML rules collapsed into one action instead of producing independent action keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/action_kind_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/bootstrap/has_prefix_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/bootstrap/has_prefix_test.go

Purpose: pins coverage for the exported `bootstrap.HasPrefix` helper.

Important APIs/types: `TestHasPrefix` checks path/prefix combinations against `HasPrefix`.

Control flow: table-driven test compares expected booleans for matching, exact, non-matching, shorter path, empty prefix, both empty, and empty input.

State and persistence behavior: none.

Dependencies and integration points: uses testify `assert`. It documents the helper as a thin wrapper around `strings.HasPrefix`.

Risks: low. The helper is trivial; the main risk is that call sites might treat it as path-component aware, but it is byte-prefix only.

Test signals: complete behavioral coverage for the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/bootstrap/has_prefix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/bootstrap/walker.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/bootstrap/walker.go

Purpose: bucket-level lifecycle bootstrap walker. It scans existing bucket entries, evaluates active lifecycle actions against each entry, and dispatches currently due deletes. It handles cold-start/recovery coverage that meta-log replay alone cannot provide.

Important APIs/types: `Entry` is the walker input model, including logical path, MPU destination key, version metadata, delete marker state, tags, and noncurrent rank. `ListFunc` streams entries after a resume marker. `Dispatcher` executes deletes. `Checkpoint` records `LastScannedPath` and `Completed`. `WalkOptions` carries resume and current time. `Walk`, `walkEntry`, `EntryCallback`, and `HasPrefix` are core APIs.

Control flow: `Walk` initializes `now`, creates a checkpoint, calls the list function, skips nil/empty entries, skips ordinary directories, lets MPU init directories through, calls `walkEntry`, and advances `LastScannedPath` only after successful processing. `walkEntry` uses `DestKey` for MPU prefix matching, fetches matching active action keys from the engine snapshot, skips disabled actions, gates action/entry shape so MPU actions only fire on MPU init records and non-MPU actions only fire on object/version records, evaluates due status, dispatches, and increments bootstrap dispatch metrics.

State and persistence behavior: the walker itself returns `Checkpoint`; callers persist it outside this file. The checkpoint intentionally does not advance past a failing entry, allowing retry. It does not persist per-action state.

Dependencies and integration points: depends on lifecycle `EvaluateAction`, engine snapshots, `stats.S3LifecycleBootstrapDispatchCounter`, and a caller-provided list source/dispatcher. Daily-run uses this via `WalkBuckets` and `WalkerDispatcher`.

Risks: list functions must honor `Path <= start` skip semantics or resume can duplicate/delete incorrectly. Versioned siblings share paths, so resume granularity is logical-key level. MPU handling is subtle: match on `DestKey`, dispatch on `.uploads/<id>` path. Missing `DestKey` is skipped to avoid guessing. Date-based actions are processed by regular walks because a dedicated scan-at-date path was not wired.

Test signals: `walker_test.go` covers due/not-due dispatch, multi-action rules, date actions, directory skipping, disabled/inactive actions, dispatch failure checkpointing, resume, MPU destination matching, and shape gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/bootstrap/walker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/bootstrap/walker_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/bootstrap/walker_test.go

Purpose: broad unit/regression coverage for the lifecycle bootstrap walker.

Important APIs/types: local `recorder`, `dispatchCall`, `mustTime`, and `compileEvDriven` support tests of `Walk`.

Control flow: tests compile active snapshots, feed in-memory entries through `EntryCallback`, and assert dispatch calls/checkpoints. They cover normal due dispatch, multi-action shape-specific dispatch, not-yet-due skip, date action before/after rule date, directory skip, disabled mode skip, pending bootstrap inactivity, failure halt and checkpoint behavior, resume, MPU init destination-key matching, and MPU/noncurrent shape separation.

State and persistence behavior: checkpoint expectations are central: completed walks set `Completed` and last scanned path; failed dispatch leaves the checkpoint at the last successfully processed path.

Dependencies and integration points: exercises engine compilation/prior state, lifecycle action kinds, `EvaluateAction`, and bootstrap dispatcher contract with a fake.

Risks: uses in-memory list ordering rather than filer ordering, so pagination and version expansion risks are covered in dailyrun filer-list tests instead. Some tests use artificial entries that would not all appear together in production, intentionally to isolate action gates.

Test signals: strong signal for prior regressions around multi-action rules, date actions lacking a dedicated scheduler, and MPU/noncurrent dispatch crossing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/bootstrap/walker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/cursor.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/cursor.go

Purpose: persistent cursor model for the daily lifecycle replay worker. It records per-shard meta-log progress and rule-set partition hashes so workers can resume, detect rule changes, and throttle full-bucket walker runs.

Important APIs/types: `CursorDir` is `/etc/s3/lifecycle/daily-cursors`. `Cursor` stores `TsNs`, `RuleSetHash`, `PromotedHash`, and `LastWalkedNs`. `CursorPersister` abstracts load/save. `FilerCursorPersister` stores JSON cursor files through `dispatcher.FilerStore`. `cursorFileName`, `Load`, and `Save` implement the file contract.

Control flow: `Load` rejects nil store, reads `shard-%02d.json`, treats `filer_pb.ErrNotFound` as cold start, rejects empty files, decodes JSON, validates version, shard id, and exact 32-byte hashes, copies hashes into arrays, and returns found. `Save` builds an indented JSON `cursorFile` and writes it to the filer store.

State and persistence behavior: durable per-shard cursor files live under the filer. Strict validation is intentional to avoid silently converting corrupt/truncated state into plausible zero-padded hashes. `LastWalkedNs` is omitempty/backward-compatible; missing value means never walked.

Dependencies and integration points: uses `filer_pb.ErrNotFound` and `dispatcher.FilerStore`. `run.go` loads/saves cursors, publishes cursor gauges, and uses hashes to decide recovery.

Risks: save atomicity depends on `FilerStore.Save` implementation; this file detects empty/corrupt reads but cannot prevent partial writes. Hash length validation is critical; relaxing it risks masking corruption. Cursor filename format assumes shard counts below 100 for zero-padding readability but still formats larger values.

Test signals: `cursor_test.go` covers not-found, round trip, shard isolation, corrupt/empty/wrong-version/shard-mismatch/hash-length errors, and nil store errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/cursor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/cursor_summary_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/cursor_summary_test.go

Purpose: tests operator-facing summary output for daily-run cursor lag and walker freshness.

Important APIs/types: exercises `summarizeShardCursorLag` using `memPersister` and `Config.Shards`.

Control flow: tests cover all-cold-start output, worst-shard max selection, and partial cursor/walker populations. Assertions verify stable key tokens such as `cursor_lag_max=` and `walked_max_age=`.

State and persistence behavior: uses in-memory cursor persistence. It validates how persisted `TsNs` and `LastWalkedNs` are interpreted for heartbeat logs.

Dependencies and integration points: tied to `Run`'s final log line, which operator scripts and CI greps parse.

Risks: summary ignores load errors and missing cursors; tests document this by expecting cold markers only when no saved values exist. It does not test negative lag from future cursor timestamps.

Test signals: good coverage for observability semantics, especially distinguishing cold start from zero lag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/cursor_summary_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/cursor_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/cursor_test.go

Purpose: unit tests for `FilerCursorPersister`.

Important APIs/types: `fakeStore` implements `dispatcher.FilerStore`; tests call `Load` and `Save`.

Control flow: fake store stores files by `dir/name`, returns copies, and returns `filer_pb.ErrNotFound` when absent. Tests exercise save/load and malformed payload paths.

State and persistence behavior: validates one JSON cursor per shard, isolation by filename, and strict corruption rejection for empty, non-JSON, wrong version, wrong shard id, short hashes, and nil store.

Dependencies and integration points: uses `filer_pb.ErrNotFound`, testify `require/assert`, and the real cursor JSON encoder/decoder.

Risks: fake store does not model partial writes or filer consistency. Tests do not assert JSON indentation or exact filename beyond paths used in setup.

Test signals: strong guard for cursor validation, which is load-bearing for avoiding accidental cursor rewind or corruption masking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/cursor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/dispatch.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/dispatch.go

Purpose: daily-run delete RPC dispatch helper. It converts router matches into `LifecycleDelete` protobuf requests and retries transient transport errors with bounded jittered backoff.

Important APIs/types: `dispatchWithRetry`, `jitter`, `buildDeleteRequest`, `toProtoActionKind`, and `toProtoIdentity`. Constants define three transport attempts and 200ms-to-5s exponential backoff.

Control flow: `dispatchWithRetry` builds one request, calls `client.LifecycleDelete`, returns server outcomes immediately on successful RPC, short-circuits context cancellation/deadline, retries only transport errors, and sleeps with equal jitter between attempts. `buildDeleteRequest` copies bucket, object path, version id, rule hash bytes, action kind, and optional CAS identity witness.

State and persistence behavior: no persistence. It affects cursor advancement indirectly because callers halt on errors or unresolved outcomes.

Dependencies and integration points: depends on lifecycle proto, `router.Match`, action kind enum, and the `LifecycleClient` interface from `run.go`.

Risks: nil response is not checked here; a client returning `(nil, nil)` would panic when reading `resp.Outcome`. Walker dispatch has a nil-response guard, but daily replay dispatch does not. Random jitter uses package global `math/rand`, which is acceptable for backoff but not deterministic unless tests avoid exact timing. Server outcomes are intentionally not retried in-run.

Test signals: `dispatch_test.go` covers success, transport retries/exhaustion, non-retry of `RETRY_LATER`/`BLOCKED`, context cancellation, and request shape including identity. `jitter_test.go` covers jitter bounds and edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/dispatch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/dispatch_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/dispatch_test.go

Purpose: unit tests for daily-run dispatch retry behavior and protobuf request construction.

Important APIs/types: `fakeLifecycleClient`, `scriptedResp`, `sampleMatch`, and `dispatchWithRetryFast` support tests of `dispatchWithRetry` and `buildDeleteRequest`.

Control flow: fake client returns scripted outcomes/errors and counts calls. Tests assert exact retry counts, outcome propagation, context cancellation behavior, and identity/rule-hash fields.

State and persistence behavior: none. Results influence caller cursor semantics by distinguishing transport errors from server outcomes.

Dependencies and integration points: uses `s3_lifecycle_pb`, lifecycle action keys, and router match identity.

Risks: comments say tests are sped up, but constants are not overridden; retry-exhaustion can take production backoff time. No test covers `(nil, nil)` response panic risk.

Test signals: good guard that server `RETRY_LATER`/`BLOCKED` are surfaced without local retry, preserving daily-run halt/resume design.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/dispatch_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/filer_list_func.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/filer_list_func.go

Purpose: adapts the filer tree into the bootstrap walker's `ListFunc`. It recursively lists bucket contents, expands versioned object siblings with lifecycle-relevant metadata, emits MPU init records, paginates filer listings, and extracts object tags.

Important APIs/types: `FilerListFunc`, `walkBucketTree`, `versionItem`, `expandVersionsDir`, `lookupNullVersion`, `listAll`, `isVersionsDir`, `isMPUInitDir`, and `extractTags`. `listPageSize` is an atomic test-tunable page size defaulting to 1024.

Control flow: `FilerListFunc` builds a bucket root and calls `walkBucketTree`. Each directory is processed in two passes: first `.versions` directories to expand version siblings and mark bare null versions to skip, then regular files/directories. Version expansion lists child version entries, filters entries with version ids, optionally appends the bare null version, sorts newest-first with version-id tie-breaks, resolves latest by pointer/explicit null/newest fallback, computes successor mod time and noncurrent rank, and emits one `bootstrap.Entry` per version. Regular files become latest entries with tags. MPU init directories at `.uploads/<id>` with destination metadata emit `IsMPUInit` entries.

State and persistence behavior: no direct persistence, but it reads persistent filer metadata and shapes it into walker state. Resume skips entries with logical `Path <= start`; version siblings share one logical path, so a mid-group resume reprocesses the whole group.

Dependencies and integration points: depends on `filer_pb.SeaweedList`, `LookupEntry`, S3 extended metadata constants, lifecycle version helpers, `bootstrap.Entry`, and `util.NewFullPath`. Used by daily-run walker wiring.

Risks: this code must stay consistent with older scheduler/bootstrap listing semantics until that path is removed. The two-pass `.versions` handling is subtle; mistakes can duplicate bare null objects or mark the wrong latest version. `listAll` assumes a nonzero page size; a test setting it to zero could loop incorrectly depending on filer behavior. Lookup errors for null version are treated as absence, not fatal. Pagination correctness depends on sorted exclusive `StartFromFileName`.

Test signals: `filer_list_func_test.go` covers flat files, recursion, tags, MPU init detection/skipping, version pointer/latest rules including stale pointer and explicit null, user folders ending in `.versions`, delete marker propagation, resume start, nil client, and attribute propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/filer_list_func.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/filer_list_func_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/filer_list_func_test.go

Purpose: comprehensive unit tests for the filer-to-bootstrap listing adapter.

Important APIs/types: `fakeFilerStream`, `fakeFiler`, helpers `file`, `dir`, `fileWithExt`, `versionsDir`, and tests around `FilerListFunc`.

Control flow: fake filer implements sorted, exclusive, limited `ListEntries` and `LookupDirectoryEntry`. Tests build in-memory directory trees and collect emitted `bootstrap.Entry` values.

State and persistence behavior: fake tree models persisted filer entries, extended metadata, version folders, and bare null versions. Tests validate how that persistent shape becomes walker entry state.

Dependencies and integration points: uses filer protobufs, S3 metadata constants, bootstrap entries, grpc stream interfaces, and testify.

Risks: the fake models only ListEntries and LookupDirectoryEntry, not all filer edge cases. Pagination behavior is represented, but this subset of displayed tests does not explicitly shrink `listPageSize`; if present elsewhere, it would cover truncation. Tests use `time.Now` in several places but do not rely on exact due calculations.

Test signals: strong regression coverage for versioned listing semantics, MPU cleanup discovery, tag extraction, resume filtering, and nil-client guard.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/filer_list_func_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/jitter_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/jitter_test.go

Purpose: tests equal-jitter backoff helper used by daily-run dispatch retries.

Important APIs/types: `TestJitterBounds`, `TestJitterZeroAndNegative`, and `TestJitterTinyDuration` exercise `jitter`.

Control flow: repeated calls assert jitter is in `[d/2, d)` for normal durations, zero for zero/negative durations, and unchanged for 1ns to avoid `rand.Int63n(0)`.

State and persistence behavior: none.

Dependencies and integration points: validates retry timing helper from `dispatch.go`.

Risks: random tests can theoretically flake only if implementation violates bounds; they do not assert distribution quality or seeding.

Test signals: useful edge-case guard for retry backoff panics and thundering-herd mitigation bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/jitter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/process_matches_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/process_matches_test.go

Purpose: tests `processMatches`, the daily-run event match dispatcher and cursor-advance gate helper.

Important APIs/types: `recordingClient` captures `LifecycleDeleteRequest`s and scripted outcomes; `dispatchCounterValue` reads Prometheus counter values.

Control flow: tests feed multiple `router.Match` values into `processMatches` with controlled due times and outcomes. They assert future matches set `skippedAny` without suppressing due siblings, order does not matter, `BLOCKED` halts remaining dispatches, empty matches no-op, all-due matches do not set skip, and DONE increments dispatch metrics.

State and persistence behavior: no cursor is persisted here, but return flags control upstream cursor advancement. The metrics test mutates shared Prometheus counter state and deletes its label row afterward.

Dependencies and integration points: uses router matches, lifecycle action keys, reader events, lifecycle proto outcomes, and `stats.S3LifecycleDispatchCounter`.

Risks: the test does not cover transport errors because `recordingClient` only returns outcomes. It does not test limiter waits. Shared metrics can leak between tests if label cleanup fails.

Test signals: strong coverage for a subtle bug where one not-yet-due sibling for an action key could suppress due siblings on the same event.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/process_matches_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/run.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/run.go

Purpose: orchestrates the daily S3 lifecycle replay worker. It runs one bounded pass over meta-log events per shard, dispatches due lifecycle deletes, invokes full-bucket walker partitions for cold-start/recovery/walker-only rules, persists cursors, and publishes observability.

Important APIs/types: `LifecycleClient`, `WalkerFunc`, `Config`, `Run`, `summarizeShardCursorLag`, `computeGlobalStartTsNs`, `startSharedSubscription`, `validate`, `runShard`, `saveCursorAndPublish`, `walkerDue`, `drainShardEvents`, and `processMatches`.

Control flow: `Run` validates config, freezes `runNow`, snapshots the lifecycle engine, computes replay hash/max TTL, optionally starts one shared metadata subscription from the minimum shard cursor, fans out events by shard, runs all shard goroutines, cancels/drains the reader, logs a stable heartbeat, and returns the first shard error. `runShard` loads cursor, computes replay/promoted hashes, handles no replay rules with walker-only save, runs recovery/cold-start walker when hashes changed or cursor is absent, rewinds on recovery, optionally runs steady-state walker under `WalkerInterval`, drains shard events, saves cursor with a fresh timeout context, and publishes gauges.

State and persistence behavior: per-shard cursor state is authoritative. `TsNs` advances only through events with no skipped future-due matches; it freezes before not-yet-due work. `RuleSetHash` and `PromotedHash` detect rule edits and partition flips. `LastWalkedNs` throttles walker load and is updated only when a walker fires. Metrics include shard duration, scanned events, dispatch counts, limiter wait, cursor min timestamp, and last walked timestamp.

Dependencies and integration points: integrates lifecycle engine snapshots/partitioning, meta-log reader, router, filer client, lifecycle delete RPC client, cursor persister, sibling lister, bootstrap walker callback, SeaweedFS stats, glog, and rate limiter.

Risks: correctness relies on shared subscription fanout not blocking; every shard channel must be drained. `validate` requires fields even if direct `runShard` tests omit them, so embedded callers should use `Run`. `processMatches` treats transport errors as halted without returning an error, causing cursor persistence at last safe point. `dispatchWithRetry` nil response risk can panic. Negative `RetentionWindow` is treated as fallback because only `<=0` is checked; tests use this as a sentinel. Save uses a background timeout context to survive canceled pass contexts, but if save fails the next run replays.

Test signals: covered by multiple focused tests in this subset: cursor summary, process matches, walker recovery, walker interval, and walk buckets. Full shared-subscription behavior is not directly covered by the listed tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/run.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walk_buckets.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walk_buckets.go

Purpose: daily-run wrapper that runs bootstrap walks across buckets for one shard, filtering entries so each shard only processes its own logical object keys.

Important APIs/types: `WalkBuckets`, `perShardListFunc`, and `entryShardID`.

Control flow: `WalkBuckets` validates snapshot/list/dispatcher, wraps the list function with a shard filter, iterates buckets, checks context cancellation between buckets, calls `bootstrap.Walk`, records the first error, and logs additional bucket errors while continuing. `perShardListFunc` drops nil/out-of-shard entries. `entryShardID` hashes `DestKey` for MPU init entries and `Path` otherwise.

State and persistence behavior: no direct persistence. It relies on `bootstrap.Walk` checkpoint semantics internally but does not persist returned checkpoints in this implementation.

Dependencies and integration points: depends on lifecycle `ShardID`, bootstrap walker, engine snapshots, and glog. Intended to be used as the `WalkerFunc` implementation in `run.go`.

Risks: because checkpoints are not persisted here, a bucket walk error returns first error but next invocation starts over. Continuing after one bucket error improves coverage but can hide repeated failures if logs are missed. Correct shard filtering for MPU requires `DestKey`; missing dest falls back to `.uploads` path, but MPU entries without dest are normally skipped by `FilerListFunc`.

Test signals: `walk_buckets_test.go` covers shard filtering, nil guards, continuing after one bucket error, context cancellation, and MPU dest-key sharding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walk_buckets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walk_buckets_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walk_buckets_test.go

Purpose: unit tests for shard-filtered bucket walking.

Important APIs/types: `recordingDispatcher`, `fixedShardEntries`, `snapshotForBucketRule`, and tests for `WalkBuckets`/`entryShardID`.

Control flow: tests construct entries in target and non-target shards, compile active expiration rules, run `WalkBuckets`, and assert only target-shard paths dispatch. Additional tests assert nil guards, first-error-return while processing later buckets, pre-canceled context handling, and MPU `DestKey` shard selection.

State and persistence behavior: none directly; uses in-memory bootstrap entries.

Dependencies and integration points: exercises lifecycle shard hashing, engine snapshot activation, and bootstrap walker dispatch integration.

Risks: helper `fixedShardEntries` brute-forces names and could be slow if shard count/hash changes dramatically, but bounded attempts are generous. It does not model persisted checkpoints.

Test signals: good coverage for per-shard partitioning, which prevents duplicate lifecycle deletes across daily-run workers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walk_buckets_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walker_dispatcher.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walker_dispatcher.go

Purpose: adapts the lifecycle delete RPC client to the bootstrap walker's `Dispatcher` interface. It lets full-bucket walks drive the same server-side delete path as meta-log replay.

Important APIs/types: `WalkerDispatcher` with `Client` and optional shared `Limiter`; method `Delete(ctx, action, entry) error`.

Control flow: `Delete` validates receiver/client/action/entry, chooses `entry.Path` as RPC object path, verifies MPU init entries have `DestKey` but still dispatches `.uploads/<id>` path, builds `LifecycleDeleteRequest` without `ExpectedIdentity`, waits on limiter if present, calls `LifecycleDelete`, increments metrics, accepts DONE/NOOP_RESOLVED/SKIPPED_OBJECT_LOCK, and turns transport errors, nil responses, and unresolved outcomes into errors.

State and persistence behavior: no persistence. Returning errors is part of walker checkpoint semantics: the walk should halt and retry instead of silently skipping unresolved deletes.

Dependencies and integration points: uses bootstrap dispatcher contract, engine compiled actions, lifecycle proto, stats counters, and rate limiter. Shares `toProtoActionKind` with daily-run dispatch file.

Risks: no transport retry here, unlike meta-log dispatch. That may be intentional because walker checkpointing can retry later, but transient errors halt a full walk. Nil `ExpectedIdentity` relies on server-side semantics that treat it as bootstrap/no-CAS. MPU path handling is easy to break: matching uses destination key elsewhere, dispatch must use upload path.

Test signals: `walker_dispatcher_test.go` covers request shape for non-versioned/versioned/MPU, empty MPU dest guard, accepted/unresolved outcomes, transport/nil response errors, limiter waiting/cancel, and nil guards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walker_dispatcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walker_dispatcher_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walker_dispatcher_test.go

Purpose: unit tests for `WalkerDispatcher` request construction, outcome classification, limiter behavior, and guard errors.

Important APIs/types: `walkerStubClient`, `sampleAction`, and multiple `TestWalkerDispatcher_*` cases.

Control flow: fake client captures last request and returns scripted outcome/error/nil response. Tests call `Delete` with bootstrap entries and compiled actions.

State and persistence behavior: none. Tests validate error returns that upstream walker uses to halt/resume.

Dependencies and integration points: uses lifecycle proto outcomes, bootstrap entries, engine compiled actions, testify, and `rate.Limiter`.

Risks: no test asserts metric labels directly. Limiter timing test depends on wall-clock delay and may be sensitive on slow/loaded CI, though it uses a modest threshold.

Test signals: strong guard for the MPU anti-pattern of dispatching `DestKey` instead of `.uploads/<id>`, and for treating unresolved server outcomes as walker-stopping errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walker_dispatcher_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walker_interval_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walker_interval_test.go

Purpose: tests walker throttle semantics, validation of negative intervals, and prevention of double full-bucket walks in one shard pass.

Important APIs/types: `readerEventAlias`, `TestWalkerDue`, `TestRunShard_WalkerThrottle`, `validatableConfig`, stubs for config validation, `TestRunShard_ColdStartDoesNotDoubleWalk`, and `TestRunShard_RecoveryWalkerSetsLastWalkedAnchor`.

Control flow: `TestWalkerDue` covers pure throttle decisions. `TestRunShard_WalkerThrottle` pre-seeds matching cursors, forces a walk partition with tiny retention, runs two passes with closed event channels, and checks call counts/`LastWalkedNs`. Validation test constructs a minimal valid config and rejects negative intervals. Cold-start and recovery tests call `runShard` directly to assert one walker call and anchor updates.

State and persistence behavior: in-memory cursor state is central. Tests validate `LastWalkedNs` as the persisted throttle anchor and ensure cold-start/recovery walker fires update it.

Dependencies and integration points: uses engine snapshots, in-memory persister, lifecycle shard count, reader event channel typing, and config validation stubs.

Risks: direct `runShard` tests bypass `validate`, so configs omit fields that `Run` requires. Comments document some test sentinels (`RetentionWindow`) that rely on implementation details. Wall-clock is controlled by injected `runNow`, which is good.

Test signals: strong regression coverage for avoiding excessive filer load from repeated full walks while preserving default interval-zero behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walker_interval_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walker_recovery_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walker_recovery_test.go

Purpose: tests daily-run recovery branch behavior when persisted rule hashes differ from the current engine snapshot.

Important APIs/types: `memPersister`, `newMemPersister`, `snapshotWithRule`, and tests around `runShard`.

Control flow: tests seed stale cursors, inject walker functions, call `runShard`, and assert walker invocation, recovery view/shard id, cursor rewind to `runNow - maxTTL`, hash replacement, nil-walker compatibility, and error propagation without cursor advancement.

State and persistence behavior: validates recovery cursor rewrite and the guarantee that walker failure leaves old cursor untouched. This protects rule-change recovery from skipping already-due objects.

Dependencies and integration points: uses lifecycle engine, in-memory cursor persister, and direct `runShard` calls.

Risks: direct `runShard` invocation bypasses full `Run` setup and shared subscription. The matching-cursor/no-walker case is noted as implicit rather than fully tested here.

Test signals: strong focused coverage for rule-edit/partition-flip recovery, which is one of the riskiest cursor state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walker_recovery_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dispatcher/filer_persister.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dispatcher/filer_persister.go

Purpose: small storage abstraction over filer read/write operations, used by daily-run cursor persistence while keeping cursor code testable.

Important APIs/types: `FilerStore` interface exposes `Read(ctx, dir, name)` and `Save(ctx, dir, name, content)`. `NewFilerStoreClient` wraps a `filer_pb.SeaweedFilerClient`. `filerStoreClient` implements the interface through SeaweedFS filer helpers.

Control flow: `Read` calls `filer.ReadInsideFiler`; `Save` calls `filer.SaveInsideFiler`. No retries or validation are performed here.

State and persistence behavior: this is the persistence adapter for content stored inside the filer. For this subset, the main consumer is `dailyrun.FilerCursorPersister`, which stores cursor JSON under `/etc/s3/lifecycle/daily-cursors`.

Dependencies and integration points: depends on `weed/filer` helper functions and `filer_pb.SeaweedFilerClient`. Tests inject fake `FilerStore` implementations instead of using this concrete adapter.

Risks: nil client is not checked here; errors surface from filer helper calls. Atomicity, overwrite semantics, and directory creation behavior are delegated to `SaveInsideFiler`. Any change affects both dispatcher and daily-run cursor storage consumers.

Test signals: no direct tests for this adapter in the subset. `cursor_test.go` validates the consumer via a fake store, not actual filer I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dispatcher/filer_persister.go -->
