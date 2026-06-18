# subset-b-008279 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/dlo.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/dlo.rs

## Purpose
`dlo.rs` implements Swift Dynamic Large Object support. A DLO manifest object is a zero-byte marker with `x-object-manifest` metadata whose value is `container/prefix`; downloads discover matching segment objects at request time, sort them lexicographically, and stream them as one logical object.

## Important APIs, Types, And Functions
`ObjectInfo` is the local segment listing shape with name, size, content type, and etag. `is_dlo_object` detects manifests by `object::head_object`. `list_dlo_segments` delegates prefix listing to `container::list_objects` and sorts by object name. `handle_dlo_get` parses the manifest, lists segments, computes total size, handles optional Range, builds Swift response headers, and streams segment bodies. `handle_dlo_register` validates the manifest and stores marker metadata via `object::put_object_with_metadata`. Private helpers include `parse_dlo_manifest`, `parse_range_header`, `calculate_dlo_segments_for_range`, `create_dlo_stream`, and UUID-based `generate_trans_id`.

## Control Flow
GET flow is metadata detection in `handler.rs`, parse `container/prefix`, list segment container, compute total size, select full or partial segment byte spans, then lazily call `object::get_object` per segment and flatten `ReaderStream`s into one response body. PUT registration flow is triggered by `X-Object-Manifest`, creates marker metadata, and returns `201 Created`.

## State, Persistence, And Dependencies
DLO state is persisted only as object user metadata plus the segment objects already stored in Swift/S3-backed buckets. Segment enumeration depends on the container listing module, while segment reads and marker writes depend on the object module and RustFS credentials. The DLO code itself holds no durable local state.

## Integration Points
`handler.rs` calls `is_dlo_object` and `handle_dlo_get` for regular and symlink-resolved object reads, and calls `handle_dlo_register` for PUTs with `x-object-manifest`. It shares range behavior with `object.rs` and handler-local parsing, and returns `x-object-manifest`, `x-trans-id`, and `x-openstack-request-id` headers.

## Risks And Test Signals
Range parsing is duplicated here and in other Swift modules, so edge cases may diverge. `parse_range_header` can underflow for zero total size because it computes `total_size - 1`; current DLO GET rejects empty segment sets but not zero-byte segment totals. Large DLOs require full segment listing before streaming, and missing segments are discovered only when streaming reaches them. Unit tests cover manifest parsing, range parsing, segment span calculation, transaction ID shape, and `ObjectInfo`; no integration test verifies real object-store streaming or manifest lifecycle.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/dlo.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/encryption.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/encryption.rs

## Purpose
`encryption.rs` defines the Swift server-side encryption configuration, metadata format, and placeholder encrypt/decrypt APIs. It documents AES-256-GCM as the intended default and stores crypto metadata under `x-object-meta-crypto-*` headers.

## Important APIs, Types, And Functions
`EncryptionAlgorithm` supports `Aes256Gcm` and legacy `Aes256Cbc`, with `as_str` and a custom `from_str`. `EncryptionConfig` carries `enabled`, algorithm, key id, and a 32-byte key, with `new` and `from_env` for `SWIFT_ENCRYPTION_ENABLED`, `SWIFT_ENCRYPTION_KEY_ID`, and hex `SWIFT_ENCRYPTION_KEY`. `EncryptionMetadata` serializes/deserializes metadata headers and decodes IV/auth tags. `should_encrypt` honors global enablement and `x-object-meta-crypto-disable`. `generate_iv`, `encrypt_data`, and `decrypt_data` are public but explicitly stubbed.

## Control Flow
Callers would load config, decide whether headers require encryption, call `encrypt_data` before storing bytes, persist metadata from `EncryptionMetadata::to_headers`, then call `decrypt_data` after reading bytes and parsing metadata. The current implementation logs state transitions but returns the original input bytes unchanged.

## State, Persistence, And Dependencies
Persistent state is expected to be object metadata: algorithm, key id, IV, and optional auth tag. Configuration is process/environment state. Dependencies include base64, hex decoding, tracing, and Swift error/result types. There is no KMS integration or key registry, and only one current key id is accepted for decryption.

## Integration Points
The module is exported by `mod.rs`, but repository search in the Swift folder shows no active handler/object integration for `should_encrypt`, `encrypt_data`, or `decrypt_data`. As written, enabling the environment variable does not make `object::put_object` encrypt data.

## Risks And Test Signals
This is security-sensitive scaffolding, not functioning encryption. `generate_iv` uses timestamp-derived bytes and is not cryptographically secure; `encrypt_data`/`decrypt_data` warn that they are unimplemented and pass plaintext through; metadata may therefore misleadingly mark plaintext as encrypted if wired in prematurely. Tests validate config parsing, metadata header round trips, opt-out behavior, IV length/difference, and a passthrough round trip, but they do not assert real confidentiality or authenticated decryption failure.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/encryption.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/errors.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/errors.rs

## Purpose
`errors.rs` centralizes Swift-specific error variants and HTTP response conversion. It provides the `SwiftError` enum and `SwiftResult<T>` alias used across the Swift protocol modules.

## Important APIs, Types, And Functions
`SwiftError` models common Swift/HTTP failures: bad request, unauthorized, forbidden, not found, conflict, payload too large, unprocessable entity, too many requests, internal server error, not implemented, and service unavailable. `fmt::Display` formats plain text messages. `status_code` maps variants to `StatusCode`. `generate_trans_id` creates timestamp-based transaction IDs. The `IntoResponse` implementation builds text responses with `x-trans-id` and `x-openstack-request-id`, and adds rate-limit headers for `TooManyRequests`.

## Control Flow
Protocol modules return `SwiftResult<T>`. When an error reaches Axum-compatible response conversion, it becomes a plain text response with Swift/OpenStack request IDs. Rate limit errors are special-cased to include `x-ratelimit-limit`, `x-ratelimit-remaining`, `x-ratelimit-reset`, and `retry-after`.

## State, Persistence, And Dependencies
There is no persisted state. The only dynamic value is a transaction id derived from current Unix microseconds. Dependencies are Axum HTTP/status/response traits and standard formatting.

## Integration Points
Every listed Swift module imports `SwiftError` directly or through `SwiftResult`. `handler.rs` also has a separate `swift_error_to_response` function that duplicates most mapping logic instead of using `IntoResponse`; this means rate-limit headers can be lost on handler errors because the handler-local converter maps `TooManyRequests` to a generic body.

## Risks And Test Signals
The timestamp transaction id can collide under high concurrency and differs from DLO's UUID-based id. Error bodies include internal strings from callers, so modules must sanitize storage errors before constructing `SwiftError::InternalServerError`. There are no local tests in this file; coverage is indirect through callers and rate-limit tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/errors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/expiration.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/expiration.rs

## Purpose
`expiration.rs` implements parsing and validation for Swift object expiration request headers. It converts `X-Delete-After` relative durations and `X-Delete-At` absolute Unix timestamps into metadata-ready expiration timestamps.

## Important APIs, Types, And Functions
`parse_delete_at` parses an unsigned Unix timestamp. `parse_delete_after` parses seconds from now and adds current Unix time. `extract_expiration` checks lowercase `x-delete-after` first, then `x-delete-at`, returning `Option<u64>`. `is_expired` compares a timestamp to current time. `validate_expiration` permits future timestamps and a 60-second clock skew, while logging far-future values more than ten years away.

## Control Flow
`object::put_object` calls `extract_expiration`, then `validate_expiration`, then stores `x-delete-at` in user metadata. Handler GET/HEAD helper paths surface stored `x-delete-at` as a direct `X-Delete-At` response header. `X-Delete-After` intentionally takes precedence over `X-Delete-At`.

## State, Persistence, And Dependencies
This module itself is stateless. Expiration state is persisted by `object.rs` as object user metadata. It depends only on system time, tracing, and Swift error/result types.

## Integration Points
The metadata written here is the intended input for `expiration_worker.rs`, although current worker storage integration is not wired to actual object scanning/deletion. Handler helper paths preserve the direct Swift header shape for `x-delete-at`; some older inline handler GET/HEAD code emits generic `x-object-meta-*` headers, creating a potential response inconsistency.

## Risks And Test Signals
Invalid non-UTF-8 header values are silently ignored by `extract_expiration` because it only parses when `to_str` succeeds. `parse_delete_after` uses unchecked `now + seconds`, so very large values can overflow in debug builds or wrap in release. The module validates syntax and timing but does not schedule deletion itself. Tests cover valid/invalid parsing, precedence, expiration comparison, clock-skew validation, far-future allowance, and no-header behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/expiration.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/expiration_worker.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/expiration_worker.rs

## Purpose
`expiration_worker.rs` sketches a background cleanup worker for objects with `X-Delete-At` metadata. It maintains an in-memory priority queue ordered by expiration time and periodically processes expired entries.

## Important APIs, Types, And Functions
`ExpirationWorkerConfig` controls scan interval, batch size, distributed worker count, and worker id. `ExpirationMetrics` records scanned/deleted counts, iterations, duration, queue size, and errors. `ExpirationWorker` owns config, `BinaryHeap<Reverse<ExpirationEntry>>`, metrics, and a running flag behind async locks. Public methods include `new`, `start`, `stop`, `get_metrics`, `track_object`, `untrack_object`, and `scan_all_objects`. Internal helpers implement worker assignment hashing, cleanup iterations, and placeholder deletion.

## Control Flow
`start` sets `running`, logs startup, and spawns a Tokio loop that ticks every configured interval. Each cleanup iteration peeks expired entries from the heap up to batch size, parses `account/container/object`, calls `delete_expired_object`, updates metrics, and logs summary. `track_object` hashes the path for distributed ownership before pushing into the heap. `untrack_object` only logs because arbitrary heap removal is not implemented.

## State, Persistence, And Dependencies
The queue and metrics are process-local only; they are lost on restart. Distributed assignment is deterministic per process but not coordinated through shared storage. Dependencies are Tokio locks/tasks/timers, a binary heap, tracing, and Swift result types.

## Integration Points
The worker is exported by `mod.rs`, but search within the Swift folder shows no call from `object::put_object` to `track_object` and no service startup call. `scan_all_objects` and `delete_expired_object` contain TODOs rather than object-store integration.

## Risks And Test Signals
This is not yet an enforcing expiration service: expired objects are never really deleted, startup recovery is unimplemented, and queued entries are not durable. `untrack_object` does not remove heap entries, so stale entries rely on deletion-time verification that is also placeholder. The distributed test asserts exactly one of workers 0 and 1 handles a path when max_workers is 4, which is not generally guaranteed because assignment could be worker 2 or 3 for other paths. Tests cover heap ordering, hashing determinism, lifecycle flags, and tracking metrics, but not real deletion or recovery.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/expiration_worker.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/formpost.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/formpost.rs

## Purpose
`formpost.rs` implements Swift FormPost uploads: browser-based multipart uploads authorized by a TempURL key and HMAC-SHA1 signature instead of exposing Keystone credentials to the browser.

## Important APIs, Types, And Functions
`FormPostRequest` holds redirect URLs, max file size/count, expiration, and signature, with `from_form_fields` and `error_redirect_url`. `generate_signature` signs `path`, redirect, size limit, count limit, and expiry. `validate_formpost` checks expiration and signature. `UploadedFile` stores parsed file fields. `build_redirect_url`, `parse_boundary`, `parse_multipart_form`, `extract_field_name`, `extract_filename`, and `handle_formpost` implement parsing, validation, object uploads, and `303 See Other` responses.

## Control Flow
`handler.rs` detects container POST requests with `multipart/form-data`, fetches the account TempURL key, collects the full request body, and calls `handle_formpost`. The handler parses fields/files, validates the signed request, enforces count and per-file size, uploads each file via `object::put_object`, accumulates upload errors, and redirects to success or error URL with status/message query parameters.

## State, Persistence, And Dependencies
No local state is persisted. Uploaded objects are stored through `object.rs`; authorization depends on TempURL key metadata from the account module. Dependencies include HMAC-SHA1, hex, URL encoding, HTTP response types, and credentials.

## Integration Points
The path signed by the form is constructed in `handler.rs` as `/v1/{account}/{container}`. Object names are derived directly from client filenames and passed to `object::put_object`, so object validation and container mapping remain centralized in object storage code.

## Risks And Test Signals
The multipart parser converts the entire body to UTF-8-lossy text, splits on boundary strings, joins lines with `\n`, trims trailing content, and stores each file fully in memory; binary files, CRLF preservation, embedded boundary bytes, and large uploads are risky. Signature comparison is a normal string comparison rather than constant-time verification. Redirect URL construction always appends `?status=...`, ignoring existing query strings. Tests cover signature sensitivity, expiration validation, redirect construction, and field parsing, but not multipart binary correctness or end-to-end upload.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/formpost.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/handler.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/handler.rs

## Purpose
`handler.rs` is the Swift HTTP integration layer. It wraps an underlying S3 Tower service, recognizes Swift routes, retrieves Keystone credentials, handles TempURL bypasses, dispatches account/container/object operations, and falls back to S3 for non-Swift requests.

## Important APIs, Types, And Functions
`SwiftService<S>` owns a `SwiftRouter` and fallback S3 service and implements `tower::Service`. `handle_swift_request` performs TempURL detection and normal authentication. `handle_authenticated_request` is the main route dispatcher. Helper functions include `handle_tempurl_object_request`, symlink resolution, `handle_object_get`, `handle_object_head`, `handle_object_put`, `check_container_acl`, a local `parse_range_header`, CORS injection, `swift_error_to_response`, and `generate_trans_id`.

## Control Flow
Request flow is route match, credential extraction from `KEYSTONE_CREDENTIALS`, body normalization to `s3s::Body`, optional TempURL validation for object GET/HEAD/PUT, then authenticated dispatch. Account routes list containers, update account metadata, and support bulk delete. Container routes create/delete containers, list objects with query filters, return metadata/ACL/versioning headers, update metadata/ACL/versioning, handle bulk extract, FormPost, and CORS preflight. Object routes enforce ACLs, handle SLO/DLO/versioning/staticweb/symlink paths, stream regular PUT/GET/HEAD/POST/DELETE, and support COPY.

## State, Persistence, And Dependencies
The handler persists no state directly. It coordinates durable state through account, container, object, ACL, CORS, DLO/SLO, versioning, staticweb, symlink, tempurl, bulk, quota, and formpost modules. It depends on Tower, Axum HTTP types, Tokio stream readers, Keystone task-local credentials, and RustFS body wrappers.

## Integration Points
This file is the only listed module that actively wires DLO, FormPost, quota, expiration metadata through object PUT, symlink resolution, CORS, and versioning. It does not wire `encryption.rs` or `ratelimit.rs`. TempURL detection calls account TempURL key lookup before requiring normal auth, but helper object access still fails when credentials are absent.

## Risks And Test Signals
The dispatcher is large and contains duplicated regular object GET logic and duplicated range parsing. Handler-local `swift_error_to_response` drops special `TooManyRequests` headers from `errors.rs`. TempURL GET/HEAD/PUT currently routes to helpers that return "not fully implemented" without credentials, despite successful TempURL signature validation. Some headers are parsed case-sensitively by string prefix checks even though HTTP headers are case-insensitive. Tests only cover handler-local range parsing; route dispatch, TempURL, ACLs, CORS, DLO/SLO, copy, and versioning need integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/handler.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/mod.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/mod.rs

## Purpose
`mod.rs` is the Swift protocol module root. It documents the OpenStack Swift URL model, authentication expectations, and re-exports the shared router and error/result types.

## Important APIs, Types, And Functions
The file declares Swift submodules for account, ACL, bulk, container, CORS, DLO, encryption, errors, expiration, expiration worker, FormPost, handler, object, quota, ratelimit, router, SLO, static web, symlink, sync, TempURL, types, and versioning. It publicly re-exports `SwiftError`, `SwiftResult`, `SwiftRoute`, `SwiftRouter`, and selected type structs `Container`, `Object`, and `SwiftMetadata`.

## Control Flow
There is no runtime control flow in this file. Its role is compile-time organization and public API exposure for the protocols crate.

## State, Persistence, And Dependencies
No state is held here. The module-level docs describe the mapping `/v1/{account}/{container}/{object}`, where Swift containers map to S3 buckets and object names map to S3 keys. Authentication is described as Keystone token middleware storing credentials in task-local storage.

## Integration Points
Consumers import the Swift router/service/errors through this root. The breadth of declared modules shows the Swift implementation is intended to cover common compatibility features, but the root does not indicate maturity or whether a feature is wired into `handler.rs`.

## Risks And Test Signals
Because all feature modules are exported equally, scaffolded modules such as encryption, expiration worker, and ratelimit can look production-ready even when not integrated. The file has no tests; validation comes from compilation and downstream module tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/object.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/object.rs

## Purpose
`object.rs` implements Swift object CRUD and server-side copy on top of the RustFS S3/object-store layer. It handles Swift object-name validation, tenant-aware bucket mapping, metadata extraction, expiration metadata, symlink metadata, streaming PUT/GET, HEAD, DELETE, POST metadata replacement, COPY, and Range parsing.

## Important APIs, Types, And Functions
`ObjectKeyMapper` validates and maps Swift object names to S3 keys, decodes/encodes URL names, detects directory markers, and normalizes paths. `put_object` streams uploads from `AsyncRead` through `HashReader` and `PutObjReader`. `put_object_with_metadata` is used for DLO/SLO marker or manifest writes. `get_object`, `head_object`, `delete_object`, `update_object_metadata`, and `copy_object` wrap RustFS storage operations. Header parsers include `parse_destination_header`, `parse_copy_from_header`, `parse_range_header`, and `format_content_range`. Private helpers validate metadata and sanitize storage errors.

## Control Flow
Most operations validate account access, validate object name, map container to tenant-prefixed bucket through `ContainerMapper`, resolve the object store handle, build `ObjectOptions`, and call bucket/object APIs. Upload extracts `x-object-meta-*`, content type, expiration headers, and symlink target before metadata validation and storage upload. Copy verifies source and destination, chooses source or replacement metadata, then calls storage-layer `copy_object`.

## State, Persistence, And Dependencies
Object bytes and metadata persist in the RustFS object store. Metadata includes user-defined Swift headers, content type, `x-delete-at`, and symlink targets. Dependencies include account access validation, container mapping, symlink and expiration helpers, RustFS object-store traits, `HashReader`, `BucketOptions`, Axum headers, and tracing.

## Integration Points
`handler.rs`, `dlo.rs`, `formpost.rs`, SLO/versioning modules, and symlink resolution all call this module. DLO registration uses `put_object_with_metadata`; regular object operations use streaming APIs from the handler. Quota is checked in `handler.rs` before calling `put_object` when content length is available.

## Risks And Test Signals
Storage error classification relies on matching error strings such as "does not exist" or "not found". Metadata header extraction lowercases the whole header name and strips `x-object-meta-`, so stored key names are normalized but remove-header semantics are absent. Unknown content length uses `-1`, which may weaken quota and size enforcement. Encryption is not integrated. Range parsing here differs from handler-local range calculation and DLO range parsing. Tests cover object-name validation, URL encoding, path normalization, destination/copy header parsing, range parsing, and content-range formatting, but not live storage behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/object.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/quota.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/quota.rs

## Purpose
`quota.rs` enforces Swift container quota metadata during uploads. It supports byte quotas and object-count quotas configured through container metadata.

## Important APIs, Types, And Functions
`QuotaConfig` stores optional `quota_bytes` and `quota_count`. `QuotaConfig::load` fetches container metadata and parses `x-container-meta-quota-bytes` and `x-container-meta-quota-count`. `is_enabled` checks whether either limit exists. `check_quota` uses saturating arithmetic to reject uploads that exceed byte or count limits with `RequestEntityTooLarge`. `check_upload_quota` loads config and current usage before enforcing. The module-level `is_enabled` helper suppresses metadata lookup errors and reports false.

## Control Flow
`handler.rs` calls `check_upload_quota` only for object PUT requests with a parseable `Content-Length`. The quota check loads container metadata twice: once for quota metadata and once for current usage. If enabled, it compares current bytes/count plus the new object size/count against configured limits before object storage upload starts.

## State, Persistence, And Dependencies
Quota configuration and usage are stored in container metadata and container stats maintained by the container/storage modules. This module persists nothing directly. It depends on Swift container metadata APIs, credentials, tracing, and `SwiftError`.

## Integration Points
The handler integrates quota on regular object PUT before version archiving and object upload. FormPost uploads call `object::put_object` directly from `formpost.rs`, so quota enforcement depends on whether they pass through handler checks; in this code path they do not. Unknown-size streaming uploads are also not quota checked because there is no content-length.

## Risks And Test Signals
Quota enforcement is best-effort and race-prone: concurrent uploads can pass checks against stale usage, and count quotas increment by one even for overwrites. Invalid quota metadata silently disables the malformed limit because parsing uses `.ok()`. Content-length absence bypasses enforcement. Tests thoroughly cover quota arithmetic, exact limits, zero limits, both dimensions, and overflow saturation, but not metadata loading or concurrent upload races.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/quota.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/ratelimit.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/ratelimit.rs

## Purpose
`ratelimit.rs` defines Swift account/container request rate limiting using an in-memory token bucket. Metadata values are expected in `limit/window_seconds` format.

## Important APIs, Types, And Functions
`RateLimit` stores limit and window seconds, with `parse` and `refill_rate`. Internal `TokenBucket` stores capacity, current tokens, refill rate, and last-refill time, with `try_consume`, `remaining`, and `reset_timestamp`. `RateLimiter` wraps a mutex-protected `HashMap<String, TokenBucket>` and exposes `check_rate_limit` and `get_status`. `extract_rate_limit` reads account or container metadata keys. `build_rate_limit_key` creates account or container scope keys.

## Control Flow
Callers are expected to parse metadata, build a key, and call `check_rate_limit` per request. The bucket refills based on whole elapsed seconds, consumes one token on success, and returns `SwiftError::TooManyRequests` with retry/reset data on exhaustion.

## State, Persistence, And Dependencies
Limiter state is process-local in memory and protected by a standard `Mutex`. It is not distributed across RustFS nodes, not durable across restart, and not backed by metadata or Redis. Configuration is read from metadata maps supplied by callers. Dependencies are standard time/collections/sync, tracing, and Swift error/result types.

## Integration Points
The module is exported by `mod.rs` and `errors.rs` knows how to render `TooManyRequests` with rate-limit headers. However, search within the Swift folder shows no active handler integration, so configured metadata does not currently throttle requests.

## Risks And Test Signals
The in-memory design cannot enforce cluster-wide fairness, can leak buckets for unbounded keys, and uses a blocking mutex inside request paths if integrated. `RateLimit::parse` permits `limit=0`, producing a zero refill rate and potential infinite/invalid retry calculations when consuming an empty bucket. Handler-local error conversion would drop detailed rate-limit headers if this module were called from `handler.rs`. Tests cover parsing, token consumption, remaining counts, extraction, and key construction, but not distributed behavior, cleanup, or handler responses.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/ratelimit.rs -->
