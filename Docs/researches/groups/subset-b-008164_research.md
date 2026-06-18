# sources/object-store/garage subset-b-008164 research

Grouped research report for `subset-b-008164`. Each section preserves the original source path in its title and is wrapped for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/admin/openapi.rs -->
## sources/object-store/garage/src/api/admin/openapi.rs

Purpose: defines the utoipa OpenAPI surface for Garage's v2 administration API. The file is mostly documentation metadata and schema glue: `#[utoipa::path]` functions are zero-body marker functions used by the `#[derive(OpenApi)]` block on `ApiDoc`.

Important APIs/types/functions: marker functions cover special endpoints (`Metrics`, `Health`, `CheckDomain`), cluster status/statistics/connect, admin token CRUD, layout operations, access key CRUD, bucket operations, permissions, aliases, node, worker, and block maintenance APIs. `UpdateClusterLayoutRequestOpenapi` and `NodeRoleChangeOpenapi` replace the runtime request shape for generator compatibility with flattened untagged enums. `BucketAliasEnumOpenapi` similarly documents global/local alias request alternatives. `SecurityAddon` injects the `bearerAuth` HTTP security scheme.

Control flow: there is no runtime request handling here. Utoipa macros collect marker functions into `ApiDoc`, apply global bearer security, and register a local server URL. Security is overridden for public special endpoints where declared with `security(())`.

State/persistence: none directly. The documented endpoints map to handlers elsewhere that mutate cluster layout, keys, buckets, workers, repair state, or block metadata.

Dependencies/integration: depends on `crate::api::*` request/response schemas, `serde`, `utoipa::{OpenApi, ToSchema, Modify}`, and feeds admin API documentation generation.

Risks: documentation can drift from `router_v2.rs` and handler semantics because paths and request bodies are manually enumerated. Workaround schema types must remain equivalent to runtime types. The OpenAPI version string is hard-coded as `v2.3.0`.

Test signals: no local tests. Validation is compile-time macro expansion and downstream OpenAPI generation; route parity should be checked against `AdminApiRequest::from_request`.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/admin/openapi.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/admin/repair.rs -->
## sources/object-store/garage/src/api/admin/repair.rs

Purpose: implements admin-triggered local repair operations for tables, object/version/block references, stored blocks, scrub/rebalance commands, aliases, and resync queue cleanup.

Important APIs/types/functions: `RequestHandler for LocalLaunchRepairOperationRequest` dispatches by `RepairType`. `TableRepair` abstracts table-specific repair scans. `TableRepairWorker<T>` implements `garage_util::background::Worker` and scans the local underlying table store by byte cursor. `RepairVersions`, `RepairBlockRefs`, and `RepairMpu` implement consistency fixes for orphaned versions, block refs, and multipart uploads. `BlockRcRepair` recalculates block reference counters by walking both rc-table and block-ref-table keys.

Control flow: repair requests either schedule background workers through `admin.background.spawn_worker`, call full table syncers, send scrub commands to `BlockManager`, run foreground alias repair, or clear the resync queue in `spawn_blocking`. Table workers call `get_gt(&pos)`, decode entries, run `process`, count changed entries, advance cursor, and finish when no later key exists. `BlockRcRepair` processes up to `RC_REPAIR_ITER_COUNT` hashes per work tick.

State/persistence: mutates Garage metadata tables by inserting tombstoned or corrected entries, schedules block repair/rebalance workers, sends scrub control messages, recalculates persistent block reference counters, and may clear block resync queues.

Dependencies/integration: ties admin API request types to `Garage`, `garage_table`, `garage_model::s3::*` tables, `garage_block::manager::BlockManager`, and the background worker system.

Risks: repair operations are powerful and can delete metadata references when backlink checks fail. Local store scans depend on decode success and table key ordering. `wait_for_work` is unreachable, so these workers are expected to be continuously busy until done. `ClearResyncQueue` is foreground-triggered and destructive for retry state.

Test signals: no local tests; confidence comes from table schema invariants and operational logs reporting counts and repairs.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/admin/repair.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/admin/router_v0.rs -->
## sources/object-store/garage/src/api/admin/router_v0.rs

Purpose: declares the legacy v0 admin endpoint enum and request parser.

Important APIs/types/functions: `Endpoint` variants cover special, cluster, layout, key, bucket, bucket-key permission, and bucket alias endpoints. `Endpoint::from_request<T>` parses method, path, and query into an endpoint. `generateQueryParameters!` creates the local `QueryParameters` parser for `id`, `search`, `globalAlias`, `alias`, and `accessKeyId`.

Control flow: `from_request` extracts `uri.path()` and query, builds `QueryParameters`, then uses `router_match!(@gen_path_parser ...)` to match hard-coded `/v0/...` paths and required query fields. It logs unused known query parameters but still returns the parsed endpoint.

State/persistence: none; this is routing-only.

Dependencies/integration: used by compatibility code in `router_v1.rs`, which maps supported v0 requests into v1 equivalents. It depends on `garage_api_common::router_macros`.

Risks: v0 uses older semantics and response shapes. Several routes are differentiated only by required query fields, so duplicated or empty query fields can affect route selection. Unknown query parameters are only debug logged except for duplicate known fields.

Test signals: no file-local tests. Behavior is macro-generated and should be covered by admin compatibility/integration tests if present.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/admin/router_v0.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/admin/router_v1.rs -->
## sources/object-store/garage/src/api/admin/router_v1.rs

Purpose: declares v1 admin endpoints, parses `/v1/...` routes, and provides a compatibility bridge from selected v0 endpoints.

Important APIs/types/functions: `Endpoint` is v0-like but `GetKeyInfo` adds `show_secret_key`. `Endpoint::from_request<T>` parses `/v1/...` paths. `Endpoint::from_v0` maps compatible `router_v0::Endpoint` variants into v1, injecting `show_secret_key: Some("true")` for legacy key-info behavior.

Control flow: route parsing mirrors v0 with `/v1/` prefixes. Compatibility mapping explicitly permits endpoints whose request/response semantics remained compatible and rejects others with `Error::bad_request("v0/ endpoint is no longer supported...")`.

State/persistence: none.

Dependencies/integration: used by `router_v2.rs::AdminApiRequest::from_v1` for v1-to-v2 compatibility. Relies on the common router macros and admin error type.

Risks: compatibility is manually curated. Any endpoint listed as compatible must preserve body syntax and response semantics expected by old clients. `showSecretKey` is parsed as a string in v1 and later interpreted as `== "true"`, so other truthy strings are false.

Test signals: no local tests. The main signal is compiler coverage of enum matches and integration coverage through compatibility endpoints.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/admin/router_v1.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/admin/router_v2.rs -->
## sources/object-store/garage/src/api/admin/router_v2.rs

Purpose: parses the current v2 admin API into typed `AdminApiRequest` values and provides selected v1 compatibility mapping.

Important APIs/types/functions: `AdminApiRequest::from_request` uses `router_match!(@gen_path_parser_v2 ...)` to parse method/path/query/body into typed request wrappers. `AdminApiRequest::from_v1` maps compatible `router_v1::Endpoint` values by parsing legacy JSON bodies into v2 request types. `authorization_type` classifies requests as public, metrics-token, or admin-token.

Control flow: special non-`/v2/` paths `/check`, `/health`, `/metrics`, and any `OPTIONS` are matched first. Other paths are generated from v2 operation names such as `/v2/GetClusterStatus`. Parameter modes include empty request structs, whole JSON body, JSON body plus query field, bearer-token extraction for `GetCurrentAdminTokenInfo`, query defaults, and parsed booleans.

State/persistence: none directly; it constructs requests that handlers later execute against cluster state.

Dependencies/integration: central bridge between hyper requests and `crate::api::*` request types. Uses common helpers for JSON body parsing, admin `Authorization`, and router macros.

Risks: the macro-driven mapping must stay in sync with OpenAPI and handler impls. Compatibility intentionally excludes changed delete semantics and changed layout/status/update endpoints. Public authorization for `CheckDomain` and `Health` is explicit; adding sensitive endpoints to that arm would be a security bug.

Test signals: no local tests. Compile-time type construction catches many request-shape mismatches; route behavior should be covered at API/integration level.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/admin/router_v2.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/admin/special.rs -->
## sources/object-store/garage/src/api/admin/special.rs

Purpose: implements public/special admin endpoints: CORS-ish `OPTIONS`, Prometheus metrics, basic health, and static website domain check.

Important APIs/types/functions: `RequestHandler` impls for `OptionsRequest`, `MetricsRequest`, `HealthRequest`, and `CheckDomainRequest`; private `check_domain`.

Control flow: `OptionsRequest` returns `200 OK` with `ALLOW`, `ACCESS_CONTROL_ALLOW_*`, and wildcard origin. `MetricsRequest` gathers from `admin.exporter.registry()` inside an OpenTelemetry span when the `metrics` feature is enabled; otherwise it returns bad request. `HealthRequest` maps `ClusterHealthStatus` to status/message, returning `503` only for unavailable quorum. `CheckDomainRequest` resolves a domain against S3 API root, S3 website root, or direct bucket name, then optionally requires bucket website config to exist.

State/persistence: read-only access to cluster health, config, bucket helper, and bucket website config.

Dependencies/integration: uses `Garage`, admin exporter, Prometheus feature gates, `host_to_bucket`, and admin request/response body aliases.

Risks: domain checking intentionally treats direct domains as website domains and requires website config. Metrics availability depends on build features. `OptionsRequest` is permissive and admin-specific, not bucket CORS-aware.

Test signals: no local tests. Functional confidence should come from health/metrics endpoint integration tests and config-driven website domain checks.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/admin/special.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/admin/worker.rs -->
## sources/object-store/garage/src/api/admin/worker.rs

Purpose: exposes local background worker inspection and runtime worker-variable get/set APIs.

Important APIs/types/functions: `RequestHandler` impls for `LocalListWorkersRequest`, `LocalGetWorkerInfoRequest`, `LocalGetWorkerVariableRequest`, and `LocalSetWorkerVariableRequest`; helper `worker_info_to_api`.

Control flow: listing obtains `admin.background.get_worker_info()`, filters by `busy_only` and `error_only`, maps worker state and status into API response structs. Get-by-id looks up a worker ID or returns `NoSuchWorker`. Variable reads query one named variable or all `garage.bg_vars`; writes call `garage.bg_vars.set`.

State/persistence: reads background worker runtime state and mutable background variables. Variables may influence worker behavior outside this file.

Dependencies/integration: depends on `garage_util::background::{WorkerInfo, WorkerState}`, `garage.bg_vars`, and admin API response types.

Risks: setting arbitrary worker variables is an operational control surface and must remain admin-token protected upstream. Worker IDs are runtime indices and may change. `last_error.secs_ago` uses saturating time arithmetic from `now_msec`.

Test signals: no local tests; behavior is straightforward mapping over background manager state.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/admin/worker.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/common/Cargo.toml -->
## sources/object-store/garage/src/api/common/Cargo.toml

Purpose: Cargo manifest for the `garage_api_common` library crate that provides shared API server, routing, error, XML, CORS, encoding, and SigV4 utilities.

Important APIs/types/functions: declares package metadata, `lib.rs` path, workspace lint inheritance, and dependencies needed by all common modules.

Control flow: build configuration only. The `hyper` dependency disables default features and enables server/http1, matching the generic server implementation.

State/persistence: none.

Dependencies/integration: internal workspace crates include `garage_model`, `garage_table`, and `garage_util`. External crates include crypto/checksum/signature dependencies (`hmac`, `sha1`, `sha2`, `md-5`, `crc-fast`, `crypto-common`, `hex`, `base64`), async/server stack (`futures`, `tokio`, `http`, `http-body-util`, `hyper`, `hyper-util`, `url`), serialization/docs (`serde`, `serde_json`, `quick-xml`, `utoipa`), and telemetry (`opentelemetry`, `tracing`).

Risks: feature choices and workspace dependency versions affect all API crates. SigV4 and checksum correctness rely on crypto crate behavior; hyper version/API changes affect `generic_server`.

Test signals: no manifest-specific tests; crate tests in common modules exercise code compiled under this manifest.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/common/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/common/common_error.rs -->
## sources/object-store/garage/src/api/common/common_error.rs

Purpose: defines shared API error taxonomy and helper traits used by S3/K2V/admin-derived errors.

Important APIs/types/functions: `CommonError` variants map internal, hyper/http, auth, bad request, unsupported, bucket, and header errors. `commonErrorDerivative!` implements conversions for wrapper error enums. `http_status_code`, `aws_code`, `bad_request`, `TryFrom<HelperError>`, `pass_helper_error`, `helper_error_as_internal`, `CommonErrorDerivative`, `OkOrBadRequest`, and `OkOrInternalError` are reused throughout handlers.

Control flow: error mapping classifies Garage quorum/timeout/remote errors as `503`, most internals as `500`, client bad inputs as `400`, auth as `403`, missing buckets as `404`, and conflicts as `409`. Helper errors are either passed through when representable or wrapped as internal messages.

State/persistence: none.

Dependencies/integration: consumed by signature, S3, K2V, CORS, XML validation, and helper code. It bridges `garage_model::helper::error::Error` and `garage_util::error::Error` into API surfaces.

Risks: `pass_helper_error` panics if called with an unrepresentable helper error; callers must only use it where variants are known. AWS error code mapping is shared externally visible behavior.

Test signals: no local tests. It is indirectly exercised by handler tests and error response generation in API crates.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/common/common_error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/common/cors.rs -->
## sources/object-store/garage/src/api/common/cors.rs

Purpose: implements CORS rule matching and header/preflight response generation for S3-compatible bucket APIs.

Important APIs/types/functions: `find_matching_cors_rule`, `cors_rule_matches`, `add_cors_headers`, `handle_options_api`, and `handle_options_for_bucket`.

Control flow: normal response CORS reads bucket params, validates `Origin`, optional requested headers, and returns the first matching rule. `add_cors_headers` emits wildcard origin or reflects the request origin and adds `Vary: Origin` when reflecting. `handle_options_api` resolves global buckets for unauthenticated preflight; unknown/local bucket names receive permissive wildcard handling. `handle_options_for_bucket` validates required preflight headers, matches configured rules, emits preflight `Vary`, or returns `Forbidden`.

State/persistence: read-only access to bucket CORS config through `BucketParams` and optional global bucket resolution.

Dependencies/integration: used by S3 and K2V API servers before/after auth. Depends on `garage_model::bucket_table::CorsRule`, common helpers, and common error traits.

Risks: unauthenticated OPTIONS cannot resolve local aliases, so fallback is intentionally permissive. Header names and methods are string-matched against stored config; case normalization depends on prior validation. Caches rely on correct `Vary` behavior.

Test signals: local tests cover reflected origin for single/multiple origins, wildcard origin, and preflight `Vary` behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/common/cors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/common/encoding.rs -->
## sources/object-store/garage/src/api/common/encoding.rs

Purpose: provides AWS-style URI percent encoding for canonical signatures and response/query handling.

Important APIs/types/functions: `uri_encode(string, encode_slash)`.

Control flow: iterates Unicode scalar values, leaves alphanumeric plus `_`, `-`, `~`, `.` untouched, optionally encodes `/` as `%2F`, and percent-encodes UTF-8 bytes of all other characters with uppercase hex.

State/persistence: none.

Dependencies/integration: used by SigV4 canonical request generation. Slash handling differs between canonical path and query string needs.

Risks: incorrect encoding breaks signature interoperability. The function works by `char` then UTF-8 bytes, so it assumes valid Rust `&str`; invalid path bytes must be handled before this layer.

Test signals: local tests cover URLs, spaces, non-ASCII characters, slash-preserving mode, and output growth beyond double input length.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/common/encoding.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/common/generic_server.rs -->
## sources/object-store/garage/src/api/common/generic_server.rs

Purpose: generic HTTP/1 API server framework shared by S3, K2V, and admin-like API handlers.

Important APIs/types/functions: traits `ApiEndpoint`, `ApiError`, `ApiHandler`, struct `ApiServer<A>`, `run_server`, request `handler`, `handler_stage2`, `Accept`, `UnixListenerOn`, and `server_loop`.

Control flow: `ApiServer::new` registers OpenTelemetry metrics. `run_server` binds TCP or Unix sockets, sets Unix permissions, and enters `server_loop`. Each connection is served by hyper HTTP/1. `handler` logs source/key/method/URI, creates a trace span, calls `handler_stage2`, converts API errors to HTTP responses, and logs server errors at warn level. `handler_stage2` parses endpoint, annotates span, measures handler duration, increments counters, and counts error responses.

State/persistence: no domain state, but holds metrics instruments and API handler state. Unix socket path may be removed/recreated and permissions set.

Dependencies/integration: uses hyper/http-body-util/hyper-util, tokio listeners, OpenTelemetry, forwarded-header parsing, and Garage error/metrics utilities.

Risks: only HTTP/1 is served. Error body construction trusts `ApiError`. Shutdown allows 10 seconds for active connections then aborts remaining tasks. Forwarded header parsing affects access logs. Admin `/health` and `/metrics` are logged at debug to reduce noise.

Test signals: no local tests. Integration should verify graceful shutdown, Unix socket permissions, metrics, and error response mapping.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/common/generic_server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/common/helpers.rs -->
## sources/object-store/garage/src/api/common/helpers.rs

Purpose: shared request parsing, response body, authorization classification, and utility helpers for bucket APIs.

Important APIs/types/functions: `Authorization`, `ReqCtx`, `host_to_bucket`, `authority_to_host`, `parse_bucket_key`, `key_after_prefix`, body aliases (`EmptyBody`, `ErrorBody`, `BoxBody`), `string_body`, `bytes_body`, `empty_body`, `error_body`, `parse_json_body`, `json_ok_response`, `body_stream`, `is_default`, and `CustomApiErrorBody`.

Control flow: host parsing handles root domains and IPv6 authorities; bucket/key parsing supports virtual-hosted and path-style access; `key_after_prefix` computes exclusive upper bounds for prefix scans; body helpers box hyper bodies, collect JSON, and map streaming frames into data bytes.

State/persistence: `ReqCtx` carries per-request Garage, bucket, params, and API key state to handlers, but helpers do not mutate state.

Dependencies/integration: used by S3/K2V/admin handlers, range scans, CORS, generic error bodies, and route compatibility parsing.

Risks: `parse_json_body` collects whole body in memory. `body_stream` rejects non-data frames. `authority_to_host` must handle IPv6 correctly. Prefix upper-bound logic is subtle around maximum Unicode scalar values.

Test signals: local tests cover bucket/key parsing, virtual-host parsing, authority host extraction with IPv6/ports, root-domain bucket extraction, and prefix successor edge cases.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/common/helpers.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/common/lib.rs -->
## sources/object-store/garage/src/api/common/lib.rs

Purpose: crate root for `garage_api_common`.

Important APIs/types/functions: imports tracing macros with `#[macro_use] extern crate tracing;` and publicly exposes `common_error`, `cors`, `encoding`, `generic_server`, `helpers`, `router_macros`, `signature`, and `xml`.

Control flow: module wiring only.

State/persistence: none.

Dependencies/integration: every API crate imports shared modules through this root. Public module layout is part of the workspace's internal API contract.

Risks: changing visibility or module names has broad compile-time impact across S3, K2V, and admin crates.

Test signals: no direct tests; compile-time module imports are the primary signal.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/common/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/common/router_macros.rs -->
## sources/object-store/garage/src/api/common/router_macros.rs

Purpose: centralizes repetitive route and query parsing macros for S3/K2V/admin routers.

Important APIs/types/functions: exported macros `router_match!` and `generateQueryParameters!`. `router_match!` supports endpoint variant matching/extraction, legacy path parsers, v2 admin path/body parser generation, generic method/key/keyword parsers, parameter extraction modes, and endpoint `name()`. `generateQueryParameters!` creates `Keyword`, `QueryParameters`, `from_query`, and `nonempty_message`.

Control flow: generated parsers match `(method, path)` or `(keyword, has_key)` and construct endpoint/request variants. Query parameter parsing rejects duplicate known fields and multiple keywords, ignores empty known values, and logs unknown non-AWS/response query parameters.

State/persistence: none.

Dependencies/integration: all routers depend on generated names and parsing conventions. Admin v2 macro also relies on `paste!` and caller imports such as `parse_json_body`, `Error`, `AdminApiRequest`, and request type names.

Risks: macro errors can be hard to debug and affect multiple APIs. Empty query values are ignored by design/FIXME. `@gen_path_parser_v2` assumes route names match request struct names. Unknown query parameters may not fail requests.

Test signals: no local tests; behavior is indirectly compiled and exercised through router tests/integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/common/router_macros.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/common/signature/body.rs -->
## sources/object-store/garage/src/api/common/signature/body.rs

Purpose: wraps request bodies after signature parsing so handlers can consume JSON, collected bytes, or streams while checksums are computed and verified.

Important APIs/types/functions: `ReqBody`, `StreamingChecksumReceiver`, `add_expected_checksums`, `add_md5`, `json`, `collect`, `collect_with_checksums`, and `streaming_with_checksums`.

Control flow: non-streaming `collect_with_checksums` consumes the boxed frame stream, updates checksummer with collected bytes, finalizes, and verifies expected checksums. Streaming mode creates an mpsc side channel: data/trailer frames are forwarded to a checksum task while the returned stream yields only data bytes to the caller. Trailer checksum values are extracted when a trailer frame appears.

State/persistence: per-request in-memory checksum state and expected checksum metadata. No durable state.

Dependencies/integration: created by `signature::streaming::parse_streaming_body`, consumed by S3/K2V handlers. Uses checksum helpers and common error traits.

Risks: `Mutex::into_inner().unwrap()` assumes uncontended ownership during consumption. Streaming checksum verification completes asynchronously through a join handle that callers must await when they need final checksums. Trailer algorithm unwrap assumes trailer frames only when configured.

Test signals: no local tests in this file; streaming parser tests exercise some body error paths indirectly.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/common/signature/body.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/common/signature/checksum.rs -->
## sources/object-store/garage/src/api/common/signature/checksum.rs

Purpose: implements Content-MD5 and AWS `x-amz-checksum-*` parsing, calculation, verification, and response header emission.

Important APIs/types/functions: checksum header constants; `ExpectedChecksums`, `Checksummer`, `Checksums`; CRC constructors; `Checksummer::{init, add_md5, add_expected, add_algorithm, update, finalize}`; `Checksums::{verify, extract}`; `parse_checksum_algorithm`; request extraction helpers; `add_checksum_response_headers`.

Control flow: expected checksums initialize only needed digest calculators. Body bytes feed active calculators. Final verification compares base64 MD5, raw sha256 hash, and exactly one extra checksum value. Request parsing accepts one concrete `x-amz-checksum-*` header or a trailer algorithm declared via `x-amz-trailer`.

State/persistence: per-request digest state only. Re-exports model `ChecksumAlgorithm` and `ChecksumValue`, which may be stored with object metadata elsewhere.

Dependencies/integration: used by signature body parsing, S3 put/multipart operations, and response generation. Uses `crc-fast`, `md5`, `sha1`, `sha2`, and base64.

Risks: multiple checksum headers are rejected. Missing requested calculated checksum returns bad request. Trailer algorithm parsing currently expects exactly one supported trailer header name. Digest endian/base64 choices are externally visible S3 compatibility behavior.

Test signals: no local tests here; expected to be covered through upload/checksum API paths.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/common/signature/checksum.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/common/signature/error.rs -->
## sources/object-store/garage/src/api/common/signature/error.rs

Purpose: signature-specific error enum layered on top of `CommonError`.

Important APIs/types/functions: `Error::{Common, AuthorizationHeaderMalformed, InvalidUtf8Str, InvalidDigest}`, blanket `From<T>` for `CommonError`-convertible types, and `CommonErrorDerivative` impl.

Control flow: lower-level parsing/crypto/checksum helpers convert common errors into signature errors; API-specific error types later map this enum into S3/K2V errors.

State/persistence: none.

Dependencies/integration: used by all modules under `signature`; converted by K2V and S3 error layers.

Risks: variants must stay aligned with downstream `From<SignatureError>` matches. Authorization scope errors carry expected/unexpected strings that become client-visible.

Test signals: no local tests; compile-time exhaustive matches in downstream error conversions are useful signals.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/common/signature/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/common/signature/mod.rs -->
## sources/object-store/garage/src/api/common/signature/mod.rs

Purpose: top-level AWS SigV4 signature module and public entry point for authenticated request verification.

Important APIs/types/functions: submodules `body`, `checksum`, `error`, `payload`, `streaming`; constants for SigV4 date/header names and streaming modes; `ContentSha256Header`; `VerifiedRequest`; `verify_request`; `signing_hmac`; `compute_scope`.

Control flow: `verify_request` calls `payload::check_payload_signature`, wraps the incoming body with `streaming::parse_streaming_body`, requires an authenticated key, and returns `Request<ReqBody>` plus access key and content-sha256 mode. `signing_hmac` derives the SigV4 signing key through date, region, service, and `aws4_request`.

State/persistence: reads Garage config region and key table via payload verification; no mutations.

Dependencies/integration: used by S3 and K2V servers with service names `s3` and `k2v`. Depends on Garage model key table and crypto HMAC/SHA256.

Risks: anonymous access is currently rejected after body wrapping decision. Region/service scope must match clients exactly. Any bug here affects authentication for multiple APIs.

Test signals: no local tests in this root; payload and streaming behavior is partially tested in submodules and integration clients.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/common/signature/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/common/signature/payload.rs -->
## sources/object-store/garage/src/api/common/signature/payload.rs

Purpose: verifies standard Authorization-header and presigned-query AWS SigV4 payload signatures and builds canonical request strings.

Important APIs/types/functions: `QueryMap`, `QueryValue`, `CheckedSignature`, `check_payload_signature`, `parse_query_map`, `string_to_sign`, `canonical_request`, `parse_date`, `verify_v4`, and `Authorization::{parse_header, parse_form}` plus private `parse_presigned`.

Control flow: query auth is preferred when `X-Amz-Algorithm` exists; otherwise Authorization header is used; otherwise request is unsigned. Standard auth parses header fields, validates signed headers, canonicalizes request, builds string-to-sign, verifies HMAC, and parses `x-amz-content-sha256`. Presigned auth excludes `X-Amz-Signature` from canonical query, validates expiry up to 7 days, verifies HMAC, and injects signed `x-amz-*` query values as headers while detecting signed header/query conflicts.

State/persistence: reads local key table, rejects deleted or expired keys, and reads configured S3 region. Does not mutate.

Dependencies/integration: core of S3/K2V auth. Uses `uri_encode`, Garage key params, table lookup, chrono, hmac, sha256, and hyper headers.

Risks: canonicalization is subtle: S3 avoids double URI encoding while other services encode differently; paths are not normalized. Date freshness is enforced for 24h header auth and query expiry for presigned URLs. Duplicate query parameters are rejected because `HeaderMap` stores one value.

Test signals: no local tests in this file; must be exercised by SigV4 compatibility tests and AWS/minio client interop.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/common/signature/payload.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/common/signature/streaming.rs -->
## sources/object-store/garage/src/api/common/signature/streaming.rs

Purpose: parses AWS aws-chunked streaming request bodies, verifies per-chunk signatures, handles trailer checksums, and produces `ReqBody`.

Important APIs/types/functions: `parse_streaming_body`, `StreamingPayloadError`, `StreamingPayloadChunk`, `StreamingPayloadStream<S>`, private payload parsers for chunk/trailer headers, `compute_streaming_payload_signature`, and `compute_streaming_trailer_signature`.

Control flow: streaming content modes remove `aws-chunked` from `Content-Encoding`, validate trailer and signing combinations, prepare trailer checksum calculation, and build signing state from seed signature/key/date/scope. `StreamingPayloadStream::poll_next` buffers incoming bytes, parses chunk headers/data/trailers with nom, verifies signatures against the previous signature, emits data frames, emits trailer frames, and stops on zero-sized chunk or trailer.

State/persistence: per-request buffer, signing state, checksummer, and trailer metadata only.

Dependencies/integration: called by `signature::verify_request`; output consumed by body/checksum handlers. Depends on `body_stream`, checksum header parsing, HMAC, SHA256, nom, and hyper frames.

Risks: parser correctness is security-sensitive. Content-Encoding cleanup tolerates absent headers for minio compatibility but rejects non-aws-chunked streaming encodings if a header was present. Unexpected EOF and bad signatures become bad requests. Only a single trailer header is represented in the emitted trailer map.

Test signals: local async test covers interrupted signed payload stream returning `Unexpected EOF`.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/common/signature/streaming.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/common/xml/cors.rs -->
## sources/object-store/garage/src/api/common/xml/cors.rs

Purpose: serializes/deserializes S3 CORS XML configuration and converts it to/from Garage bucket CORS model rules.

Important APIs/types/functions: `CorsConfiguration`, `CorsRule`, schema helper structs `AllowedMethod`, `AllowedHeader`, `ExposeHeader`, `CorsConfiguration::{validate, into_garage_cors_config}`, and `CorsRule::{validate, to_garage_cors_rule, from_garage_cors_rule}`.

Control flow: XML maps `CORSConfiguration`/`CORSRule` child elements into vectors of `Value`/`IntValue`. Validation parses allowed methods as HTTP methods and allowed/exposed headers as `HeaderName`. Conversion copies strings into `GarageCorsRule`.

State/persistence: no direct state; resulting Garage CORS rules are stored in bucket params by callers.

Dependencies/integration: used by S3 bucket CORS handlers and OpenAPI schema generation. Depends on quick-xml-compatible serde attributes and common XML helpers.

Risks: wildcard values are allowed by conversion and may not parse as `HeaderName` for exposed/allowed headers if validation is too strict or too loose; method/header validation must match accepted S3 semantics. Empty CORS rule list is explicitly supported.

Test signals: local tests deserialize sample XML, compare structured values, serialize back, and cover empty configurations.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/common/xml/cors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/common/xml/lifecycle.rs -->
## sources/object-store/garage/src/api/common/xml/lifecycle.rs

Purpose: serializes/deserializes S3 lifecycle XML and validates/converts it into Garage lifecycle rules.

Important APIs/types/functions: `LifecycleConfiguration`, `LifecycleRule`, `Filter`, `Expiration`, `AbortIncompleteMpu`; conversion methods `validate_into_garage_lifecycle_config`, `from_garage_lifecycle_config`, `validate_into_garage_lifecycle_rule`, `Filter::validate_into_garage_lifecycle_filter`, and `Expiration::validate_into_garage_lifecycle_expiration`.

Control flow: rule status maps `Enabled`/`Disabled` to boolean. Filters may contain one simple condition or multiple conditions wrapped in a non-nested `And`; invalid combinations return string errors. Expiration accepts exactly one of `Days` or `Date`, validating dates through the model helper. Reverse conversion emits `And` when multiple filter conditions exist.

State/persistence: no direct persistence; converted `GarageLifecycleRule` values are stored in bucket configuration by callers.

Dependencies/integration: used by S3 lifecycle handlers. Depends on `garage_model::bucket_table` lifecycle types and XML helper wrappers.

Risks: errors are `&'static str`, so callers must map them into API errors consistently. Numeric casts from `i64` to unsigned/usize can accept negative XML values incorrectly if upstream validation does not reject them. Nested `And` is explicitly rejected.

Test signals: local test covers XML round-trip, validation into Garage rules, and conversion back to equivalent XML.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/common/xml/lifecycle.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/common/xml/mod.rs -->
## sources/object-store/garage/src/api/common/xml/mod.rs

Purpose: XML module root and shared XML utility wrappers for S3-compatible config documents.

Important APIs/types/functions: public submodules `cors`, `lifecycle`, `website`; `to_xml_with_header`, `unprettify_xml`, `xmlns_tag`, `xmlns_xsi_tag`, `Value`, and `IntValue`.

Control flow: `to_xml_with_header` prefixes quick-xml serialization with the XML declaration. `unprettify_xml` trims each line for test comparisons. Namespace serializer helpers write S3 XML namespace values. `Value` and `IntValue` wrap element `$value` content and provide `From<&str>` for `Value`.

State/persistence: none.

Dependencies/integration: used by CORS/lifecycle/website XML modules and S3 config handlers.

Risks: pretty/whitespace handling is test-only and not a general XML canonicalizer. Namespace strings are hard-coded to AWS S3 namespaces.

Test signals: no direct tests here, but helper functions are used by XML module round-trip tests.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/common/xml/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/common/xml/website.rs -->
## sources/object-store/garage/src/api/common/xml/website.rs

Purpose: serializes/deserializes and validates S3 static website XML configuration, then converts routing rules into Garage's website model.

Important APIs/types/functions: `WebsiteConfiguration`, `RoutingRules`, `RoutingRule`, `Key`, `Suffix`, `Target`, `Condition`, `Redirect`; validation methods on each; `WebsiteConfiguration::into_garage_website_config`; `RoutingRule::{from_garage_routing_rule, into_garage_routing_rule}`.

Control flow: validation forbids `RedirectAllRequestsTo` together with index/error/routing fields, validates non-empty error key, index suffix without slash, HTTP/HTTPS protocols, <=1000 routing rules, condition status code currently only 404, and redirect code constraints. Conversion currently rejects `RedirectAllRequestsTo` as not implemented and builds `WebsiteConfig` with default `index.html`, optional error doc, and routing rules with default 302 redirect code.

State/persistence: no direct persistence; produces `WebsiteConfig` stored in bucket state by callers.

Dependencies/integration: used by S3 website configuration handlers and admin domain checks. Depends on `garage_model::bucket_table` website/routing types.

Risks: `RedirectAllRequestsTo` is documented by XML shape but intentionally not implemented. The validation permits Netlify-like 200/404 rewrite semantics with restrictions. `Suffix::validate` uses bitwise `|` on booleans, which works but does not short-circuit.

Test signals: local tests cover deserialization/serialization of full and empty website configurations.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/common/xml/website.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/k2v/Cargo.toml -->
## sources/object-store/garage/src/api/k2v/Cargo.toml

Purpose: Cargo manifest for the `garage_api_k2v` library crate.

Important APIs/types/functions: package metadata, library path `lib.rs`, workspace lints, and dependencies for K2V HTTP API handling.

Control flow: build configuration only.

State/persistence: none.

Dependencies/integration: internal workspace dependencies include `garage_model`, `garage_table`, `garage_util`, and `garage_api_common`. External dependencies include base64, thiserror, tracing, futures, tokio, http, http-body-util, hyper server/http1, serde, serde_json, and OpenTelemetry.

Risks: K2V API relies on common SigV4/server dependencies and hyper feature selection; workspace version changes affect route/auth/body behavior.

Test signals: no manifest-specific tests.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/k2v/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/k2v/api_server.rs -->
## sources/object-store/garage/src/api/k2v/api_server.rs

Purpose: wires the K2V API into the shared generic server, including route parsing, SigV4 auth, bucket permission checks, CORS, and endpoint dispatch.

Important APIs/types/functions: `K2VApiServer`, `K2VApiEndpoint`, `K2VApiServer::run`, `ApiHandler for K2VApiServer`, and `ApiEndpoint for K2VApiEndpoint`.

Control flow: `parse_endpoint` delegates to `Endpoint::from_request`. `handle` processes `OPTIONS` before auth, then verifies SigV4 with service `k2v`, resolves the bucket against the access key, checks read/write/owner permissions from endpoint authorization type, looks up applicable CORS for GET/HEAD/POST, builds `ReqCtx`, dispatches to item/index/batch/range handlers, and adds CORS headers to successful responses. `key_id_from_request` parses Authorization headers for access logging.

State/persistence: reads Garage bucket/key state and delegates mutations to K2V RPC handlers. No local persistence.

Dependencies/integration: integrates `garage_api_common::{generic_server,cors,helpers,signature}`, K2V handler modules, and Garage model.

Risks: only GET/HEAD/POST success responses receive CORS decoration; other methods should be preflighted. OPTIONS is unauthenticated and uses bucket-name parsing. Permission mapping in router is security-critical.

Test signals: no local tests; should be covered by K2V API integration tests for auth, CORS, and dispatch.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/k2v/api_server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/k2v/batch.rs -->
## sources/object-store/garage/src/api/k2v/batch.rs

Purpose: implements K2V batch insert/read/delete and range-poll handlers.

Important APIs/types/functions: `handle_insert_batch`, `handle_read_batch`, `handle_delete_batch`, `handle_poll_range`, private query handlers, and JSON structs `InsertBatchItem`, `ReadBatchQuery/Response/Item`, `DeleteBatchQuery/Response`, `PollRangeQuery/Response`.

Control flow: insert batch parses JSON, decodes optional base64 values, maps absent value to tombstone, parses causality tokens, and calls `k2v.rpc.insert_batch`. Read batch runs queries concurrently with `join_all`; single-item mode forbids range params and direct-gets one sort key, otherwise uses `read_range`. Delete batch either deletes a single matched item with its causal context or range-deletes all non-tombstones using batch insert of deleted values. Poll range parses body, clamps timeout to 1-600 seconds, calls subscription RPC, returns changed items/marker or `304`.

State/persistence: writes K2V values/tombstones through RPC and reads item table ranges. Batch delete mutates many sort keys in a partition.

Dependencies/integration: uses K2V model item table, causality parser from `item.rs`, common JSON/body helpers, and `range::read_range`.

Risks: batch read has unbounded query count in the body. Non-single delete reads all matching items with no explicit limit, which can be expensive. Values are base64 JSON strings; invalid base64 is client error.

Test signals: no local tests. Integration should cover conflict/tombstone handling, range pagination, and long polling.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/k2v/batch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/k2v/error.rs -->
## sources/object-store/garage/src/api/k2v/error.rs

Purpose: K2V API error type and HTTP/JSON error response implementation.

Important APIs/types/functions: `Error` enum, `commonErrorDerivative!(Error)`, `From<SignatureError>`, `Error::code`, and `ApiError for Error`.

Control flow: signature errors are converted variant-by-variant. `http_status_code` maps common errors through `CommonError`, missing keys to `404`, not acceptable to `406`, and malformed auth/base64/UTF8/digest/causality to `400`. `http_body` emits `CustomApiErrorBody` as pretty JSON. `add_http_headers` always adds JSON content type and wildcard CORS origin.

State/persistence: none.

Dependencies/integration: consumed by `generic_server::ApiError`; used throughout K2V route handlers.

Risks: wildcard CORS on error responses may expose error details cross-origin by design. `InvalidCausalityToken` code string is `"CausalityToken"`, which may be a compatibility contract. Pretty JSON serialization fallback omits region/path fields.

Test signals: no local tests; compile-time conversions and API error integration are primary signals.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/k2v/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/k2v/index.rs -->
## sources/object-store/garage/src/api/k2v/index.rs

Purpose: implements K2V partition index listing and statistics response.

Important APIs/types/functions: `handle_read_index`, `ReadIndexResponse`, and `ReadIndexResponseEntry`.

Control flow: resolves all non-gateway node IDs from cluster layout, calls `read_range` over `garage.k2v.counter_table.table` with optional prefix/start/end/limit/reverse and a not-deleted filter scoped to those nodes, then maps per-partition counters (`entries`, `conflicts`, `values`, `bytes`) from filtered values into JSON response fields with pagination flags.

State/persistence: read-only access to K2V counter table and cluster layout.

Dependencies/integration: depends on K2V counter constants (`ENTRIES`, `CONFLICTS`, `VALUES`, `BYTES`), table range utility, and common JSON response helper.

Risks: cluster layout lookup can fail and affects filtered counter values. Counter names are stringified constants; mismatches would silently return zero defaults. Pagination semantics are inherited from `read_range`.

Test signals: no local tests; range utility and K2V API integration should cover response shape and pagination.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/k2v/index.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/k2v/item.rs -->
## sources/object-store/garage/src/api/k2v/item.rs

Purpose: implements single-item K2V read/insert/delete/poll operations and content negotiation.

Important APIs/types/functions: `X_GARAGE_CAUSALITY_TOKEN`, `ReturnFormat::{Json,Binary,Either}`, `parse_causality_token`, `ReturnFormat::{from, make_response, make_binary_response, make_json_response}`, `handle_read_item`, `handle_insert_item`, `handle_delete_item`, and `handle_poll_item`.

Control flow: reads fetch an item from `k2v.item_table`, choose response format from `Accept`, and return binary, JSON base64 array, conflict status, no-content tombstone, or `NoSuchKey`. Inserts/deletes parse optional causality token header and write value/tombstone through `k2v.rpc.insert`. Poll parses query causality token, clamps timeout to 1-600 seconds, calls `rpc.poll_item`, and returns item response or `304 Not Modified`.

State/persistence: writes K2V values/tombstones and reads K2V item table. Causality contexts preserve conflict resolution semantics.

Dependencies/integration: used by API server dispatch; depends on K2V DVVS model, common body helpers, and K2V error mappings.

Risks: insert collects entire body in memory. Binary reads with conflicts return `409` with only causality token and empty body, requiring clients to retry with JSON. Accept parsing is simple comma trimming and does not parse q-values.

Test signals: no local tests; needs API tests for content negotiation, causality conflict cases, tombstones, and polling.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/k2v/item.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/k2v/lib.rs -->
## sources/object-store/garage/src/api/k2v/lib.rs

Purpose: crate root for K2V API module wiring.

Important APIs/types/functions: public `api_server`; private `error`, `router`, `batch`, `index`, `item`, and `range` modules. Imports tracing macros with `#[macro_use] extern crate tracing;`.

Control flow: module declaration only.

State/persistence: none.

Dependencies/integration: establishes which pieces are public to other crates. Only server entry point is exported; route/error internals remain crate-private.

Risks: changing module visibility affects embedding of K2V server in Garage daemon.

Test signals: compile-time module wiring.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/k2v/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/k2v/range.rs -->
## sources/object-store/garage/src/api/k2v/range.rs

Purpose: shared K2V table range pagination utility for index, read-batch, and delete-batch endpoints.

Important APIs/types/functions: `read_range<F>`.

Control flow: calculates initial `start` and whether to ignore that start depending on prefix/start/reverse. It rejects starts outside prefix. Reverse prefix scans start at `key_after_prefix(prefix)` and ignore the synthetic boundary. It repeatedly calls `table.get_range` with bounded batch size, applies prefix/end/limit checks, sets `more` and `nextStart` when limit is exceeded, and advances by last returned sort key while avoiding duplicates.

State/persistence: read-only table access through `garage_table`.

Dependencies/integration: generic over `TableSchema<S=String>` with sharded replication. Used by K2V index and batch handlers.

Risks: pagination correctness depends on table sort order and `EnumerationOrder`. Reverse prefix scans can fail for prefixes without a successor. The computed `n_get` uses limit minus entries plus two; very small/large limits should be carefully tested.

Test signals: no local tests; endpoint pagination tests should cover prefix/start/end/reverse interactions.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/k2v/range.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/k2v/router.rs -->
## sources/object-store/garage/src/api/k2v/router.rs

Purpose: parses HTTP K2V API requests into typed endpoint variants and declares endpoint authorization requirements.

Important APIs/types/functions: `Endpoint` enum, `Endpoint::from_request`, method parsers `from_get/from_search/from_post/from_put/from_delete`, `get_partition_key`, `get_sort_key`, `authorization_type`, and generated query parameters.

Control flow: path first segment is bucket name; remainder is URL-decoded partition key. `OPTIONS` returns early. GET with partition key reads/polls item; GET without key reads index. SEARCH and POST keyword variants map to batch or poll-range operations. PUT inserts item requiring `sort_key`; DELETE deletes item. Query macro parses keywords `delete`, `search`, `poll_range` and fields like `prefix`, `start`, `sort_key`, `timeout`.

State/persistence: none.

Dependencies/integration: used by `K2VApiServer::parse_endpoint`; uses common router macros and authorization enum.

Risks: custom HTTP method `SEARCH` is supported through `Method::from_bytes`. Path splitting treats empty partition key as no-key operation. Unknown methods and malformed UTF-8 are bad requests. Authorization mapping marks read-only endpoints as read and everything else as write.

Test signals: no local tests; route matrix should be integration-tested.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/k2v/router.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/s3/Cargo.toml -->
## sources/object-store/garage/src/api/s3/Cargo.toml

Purpose: Cargo manifest for the `garage_api_s3` library crate.

Important APIs/types/functions: package metadata, library path, workspace lint inheritance, and dependencies for Garage's S3-compatible API server and handlers.

Control flow: build configuration only. `hyper` is server/http1 with default features disabled.

State/persistence: none.

Dependencies/integration: internal workspace dependencies include model/table/block/net/util/rpc/common crates. External dependencies include crypto/checksum, async streams, HTTP/form/multipart/range/XML/JSON parsing, compression, percent encoding, and OpenTelemetry.

Risks: broad dependency surface reflects S3 feature breadth; version changes can affect multipart parsing, range handling, XML compatibility, checksums, and Hyper body behavior.

Test signals: manifest itself has no tests; S3 module tests compile under this dependency set.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/s3/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/s3/api_server.rs -->
## sources/object-store/garage/src/api/s3/api_server.rs

Purpose: wires the S3-compatible API into the shared generic server, including endpoint parsing, host bucket resolution, SigV4 auth, bucket authorization, CORS, and dispatch to S3 operation modules.

Important APIs/types/functions: `S3ApiServer`, `S3ApiEndpoint`, `S3ApiServer::run`, `handle_request_without_bucket`, `ApiHandler for S3ApiServer`, and `ApiEndpoint for S3ApiEndpoint`.

Control flow: `parse_endpoint` requires Host, normalizes authority to host, extracts virtual-host bucket from configured root domain, and delegates to S3 router. `handle` processes `PostObject` and `Options` before SigV4. Authenticated requests are verified with service `s3`; bucketless requests only support `ListBuckets`; `CreateBucket` has a special path before bucket resolution. Other requests resolve bucket for the key, check endpoint authorization against key permissions, find matching CORS, build `ReqCtx`, dispatch across object, multipart, bucket, CORS, lifecycle, and website handlers, then applies CORS to successful responses.

State/persistence: reads key/bucket config and delegates object/bucket mutations to handler modules. No local durable state.

Dependencies/integration: integrates most S3 handler modules, common server/auth/CORS/helpers, Garage model key table, and route endpoint metadata.

Risks: early `PostObject` bypasses standard `verify_request` path and must perform its own auth. `bucket_name.unwrap()` for PostObject assumes router always supplies a bucket. Permission classification in the router is security-critical. Only implemented endpoints are dispatched; unknown supported-looking endpoints return `NotImplemented`.

Test signals: no local tests; S3 integration tests should cover host parsing, auth, bucket permissions, preflight, list pagination, multipart, lifecycle/CORS/website, and unimplemented paths.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/s3/api_server.rs -->
