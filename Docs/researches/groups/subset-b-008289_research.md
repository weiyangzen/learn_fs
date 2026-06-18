# subset-b-008289 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/tests/lifecycle_integration_test.rs -->
# sources/object-store/rustfs/crates/scanner/tests/lifecycle_integration_test.rs

## Purpose
This is an integration test suite for RustFS scanner lifecycle behavior over a local four-disk `ECStore`. It exercises zero-day lifecycle expiry, current and noncurrent version transitions, delete marker cleanup, free-version cleanup, and restore from a transitioned warm tier. Most tests are serial and many are ignored because they depend on isolated global object-layer state or long-running scanner timing.

## Important APIs, Types, and Helpers
The setup helpers construct either a cached global test store (`setup_test_env`) or a fresh store (`setup_isolated_test_env`) by creating four `/tmp/rustfs_scanner_lifecycle_test_*` disk directories, converting them to `Endpoint`s, calling `init_local_disks`, building an `ECStore`, initializing bucket metadata, and optionally starting background expiry workers.

Bucket and object helpers wrap store operations: `create_test_bucket`, `create_test_lock_bucket`, `upload_test_object`, and `modeled_versioned_delete_opts`. Lifecycle helpers write XML directly to `metadata_sys::update` under `BUCKET_LIFECYCLE_CONFIG`: current expiry, expired-object-delete-marker cleanup, `DelMarkerExpiration`, transition rules, and transition rules with an arbitrary tier.

Scanner helpers open a single local disk with `new_disk`, locate the object `xl.meta` path (`STORAGE_FORMAT_FILE`), build a `ScannerItem`, and call `ScannerIODisk::get_size` with or without lifecycle metadata. Poll helpers observe object absence, remote-tier object counts, object version counts, and completed transition state. `MockWarmBackend` implements `WarmBackend` in memory and preserves bytes plus selected metadata derived through `build_transition_put_options`.

## Control Flow and State
Tests create buckets, install lifecycle XML, mutate object state through `put_object`, multipart upload, `copy_object`, `delete_object`, or `restore_transitioned_object`, then trigger either `enqueue_transition_for_existing_objects`, `init_background_expiry`, manual scanner `get_size`, or `init_data_scanner`. Assertions poll with short timeouts to account for async lifecycle workers.

The file uses global state in several places: `GLOBAL_ENV` caches one `ECStore`; `GLOBAL_TierConfigMgr` is mutated to register test tiers and mock drivers; and `with_forced_immediate_enqueue_timeout` mutates `ENV_TEST_FORCE_IMMEDIATE_TRANSITION_ENQUEUE_TIMEOUT` under `#[serial]` tests. Persistent state is filesystem metadata on the temporary disks and in-memory warm-tier maps.

## Integration Points
The suite crosses `rustfs_ecstore`, `rustfs_scanner`, `rustfs_filemeta`, `rustfs_storage_api`, `rustfs_config`, and `s3s` restore DTOs. It verifies integration between bucket metadata lifecycle config, object versioning, erasure-store metadata, scanner item traversal, background expiry queues, warm-tier transition drivers, multipart restore, and object-lock/versioning options.

## Risks
The tests are timing-sensitive and rely on background async workers, process environment mutation, and global tier registry state. One ignored test sleeps for 1200 seconds, which is unsuitable for normal CI. Manual single-disk scanner calls may not exercise all erasure-set behavior. Because many important scenarios are ignored, regressions can pass default test runs unless the ignored integration suite is run in a controlled environment.

## Test Signals
Covered scenarios include immediate transition for normal put, multipart upload, copy, existing-object backfill, restore of transitioned multipart objects, stale free-version remote cleanup, idempotent backfill after compensation transition, noncurrent expiry/transition after compensation, modeled versioned delete marker creation and cleanup, immediate zero-day current and noncurrent expiry on put, scanner-driven zero-day expiry, and background scanner expiry for prefix and exact-key rules.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/tests/lifecycle_integration_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/security-governance/Cargo.toml -->
# sources/object-store/rustfs/crates/security-governance/Cargo.toml

## Purpose
Defines the `rustfs-security-governance` crate, a small contract crate for security governance metadata and validation. It is versioned, licensed, documented, linted, and rust-versioned through workspace settings.

## Dependencies and Integration
The only runtime dependency is workspace `thiserror`, matching the crate's role as pure value types plus validator error enums. Doctests are disabled. The crate exports governance contracts used by other RustFS crates without pulling in async runtimes, serde, storage, or network dependencies.

## Risks and Test Signals
The manifest keeps dependency surface intentionally narrow, which reduces build and security risk. Any future dependency added here should be justified because this crate is likely meant as a lightweight shared policy layer. Tests live in the module source files, not in manifest-level integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/security-governance/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/security-governance/src/admin_matrix.rs -->
# sources/object-store/rustfs/crates/security-governance/src/admin_matrix.rs

## Purpose
Models admin/public route authorization contracts and validates a route matrix. It provides const-friendly route specs that can be assembled statically and checked for empty paths, empty admin actions, and duplicate method/path pairs.

## Important APIs and Types
`HttpMethod` enumerates DELETE, GET, HEAD, POST, PUT with `as_str`. `AdminActionRef` wraps a static action string. `PublicRouteKind` classifies allowed public endpoints such as console assets, health, OIDC bootstrap, and STS form post. `RouteRiskLevel` classifies normal, sensitive, and high-risk routes. `AdminRouteAccess` distinguishes `AdminAction` from `Public` and exposes `admin_action`/`public_kind`. `AdminRouteSpec` stores method, path, access, and risk level with `admin`, `public`, and getter constructors.

`AdminRouteMatrixError` reports `EmptyPath`, `EmptyAdminAction`, and `DuplicateRoute`. `validate_admin_route_specs` iterates in order, trims path/action strings, and uses a `BTreeSet<(HttpMethod, &'static str)>` as the uniqueness index.

## Control Flow and State
There is no persistence or runtime mutable state beyond the local set inside validation. The API is entirely synchronous and works with borrowed static route specs.

## Integration Points
The module is re-exported by `security-governance/src/lib.rs` for admin route inventory code to consume. It likely backs control-plane route authorization audits or compile-time route manifest checks.

## Risks
Duplicate detection is exact on the literal path string and method; it does not normalize slashes, case, path parameters, or equivalent route patterns. Public routes do not require special validation beyond non-empty path. `AdminActionRef` permits any non-empty static string, so action existence must be validated elsewhere.

## Test Signals
Unit tests cover valid admin/public specs, duplicate method/path rejection, empty path rejection, and empty admin action rejection.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/security-governance/src/admin_matrix.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/security-governance/src/lib.rs -->
# sources/object-store/rustfs/crates/security-governance/src/lib.rs

## Purpose
Crate root for `rustfs-security-governance`. It exposes four policy modules: `admin_matrix`, `redaction`, `serde_policy`, and `supply_chain`.

## Important APIs
The root re-exports all public contract types and validators: admin route specs and validation, redaction rules and validation, serde unknown-field policy validation, and artifact integrity policy validation. This creates a compact public surface for downstream governance checks.

## Control Flow, State, and Integration
No code executes here beyond module declaration and re-export. The design keeps downstream crates from depending on individual module paths and provides a stable facade.

## Risks and Test Signals
Risk is API compatibility: changing re-exports can break downstream crates even if module internals remain. Tests are in the module files rather than the root.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/security-governance/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/security-governance/src/redaction.rs -->
# sources/object-store/rustfs/crates/security-governance/src/redaction.rs

## Purpose
Defines redaction classifications and validates static redaction rule tables for fields that appear in logs, diagnostics, admin output, or configuration surfaces.

## Important APIs and Types
`RedactionLevel` has `Public`, `Sensitive`, and `Secret`; helpers `requires_redaction` and `is_secret` encode policy semantics. `RedactionRule` stores a static field name, level, and reason with const constructor/getters. `RedactionPolicyError` reports empty field, empty reason, and duplicate field. `validate_redaction_rules` checks trimmed field/reason strings and uses a `BTreeSet<&'static str>` to enforce one rule per field.

## Control Flow and State
Validation is deterministic and side-effect free. There is no persistence or runtime registry; callers pass the policy table each time.

## Integration Points
Re-exported from the crate root, this module can be consumed by admin APIs, audit logging, diagnostics, or config serializers to assert that sensitive fields have explicit redaction metadata.

## Risks
Field identity is exact and case-sensitive, with no namespace awareness. The validator checks the existence and uniqueness of a rule but does not apply redaction itself. It also allows `Public` rules with arbitrary reasons, so enforcement depends on consumers respecting `RedactionLevel`.

## Test Signals
Unit tests cover valid public/secret rules and accessors, empty field, empty reason, and duplicate field rejection.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/security-governance/src/redaction.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/security-governance/src/serde_policy.rs -->
# sources/object-store/rustfs/crates/security-governance/src/serde_policy.rs

## Purpose
Defines governance rules for serde unknown-field handling. It lets the project declare whether a target schema is strict ingress, tolerant compatibility, or persistent legacy data, and validates that the unknown-field policy matches that role.

## Important APIs and Types
`UnknownFieldPolicy` is `Deny`, `Warn`, or `Preserve`. `SerdePolicyKind` is `StrictIngress`, `TolerantCompat`, or `PersistentLegacy`. `SerdePolicy` stores a static target, kind, and unknown-field policy with const constructor/getters. `SerdePolicyError` reports empty target, strict ingress not denying unknown fields, compatibility/legacy policy denying unknown fields, and duplicate target.

`validate_serde_policies` checks non-empty targets, then enforces kind/policy combinations: strict ingress must deny; tolerant compatibility and persistent legacy must not deny. A `BTreeSet` enforces one policy per target.

## Control Flow and State
The module has no runtime state. Validation is a simple ordered scan that returns the first detected policy error.

## Integration Points
This module supports code or CI checks around JSON/XML/config DTOs. It is re-exported from `lib.rs` for consumers that need to document or enforce serde compatibility posture.

## Risks
The policy table is advisory unless wired into actual serde attributes or test gates. Target matching is exact and unqualified. There is no severity level for `Warn`, and no way to express mixed behavior within a single target.

## Test Signals
Unit tests validate strict, legacy, and tolerant examples and reject empty targets, strict ingress without `Deny`, compat/legacy with `Deny`, and duplicate targets.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/security-governance/src/serde_policy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/security-governance/src/supply_chain.rs -->
# sources/object-store/rustfs/crates/security-governance/src/supply_chain.rs

## Purpose
Models supply-chain integrity requirements for build artifacts, third-party downloads, and generated release assets. It validates that artifact metadata requires digests, provenance, and signatures where appropriate.

## Important APIs and Types
`ArtifactSourceKind` is `WorkspaceBuild`, `ThirdPartyDownload`, or `GeneratedReleaseAsset`. Its helper methods require digest for third-party and generated assets, and provenance/signature for generated release assets. `ArtifactIntegrityPolicy` stores artifact name, source kind, and booleans for digest/signature/provenance requirements with const constructor/getters. `SupplyChainPolicyError` reports empty artifact names, missing digest/provenance/signature requirements, and duplicate artifact policies.

`validate_artifact_integrity_policies` scans policies, rejects empty artifacts, applies source-derived requirements, and uses a `BTreeSet<&'static str>` for artifact uniqueness.

## Control Flow and State
Validation is synchronous and stateless. It returns the first policy violation and does not inspect files, signatures, provenance documents, or actual release assets.

## Integration Points
Re-exported by the crate root, the policy can feed release validation, CI policy checks, or admin/reporting surfaces that describe artifact trust requirements.

## Risks
The model verifies declared requirements, not the presence or cryptographic validity of artifacts. Workspace builds may omit digest/provenance while still setting signature required, which may or may not match release policy. Artifact identity is exact and static.

## Test Signals
Unit tests cover valid workspace/generated policies, empty artifacts, missing digest for third-party and generated assets, missing provenance/signature for generated assets, and duplicate artifact rejection.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/security-governance/src/supply_chain.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/signer/Cargo.toml -->
# sources/object-store/rustfs/crates/signer/Cargo.toml

## Purpose
Defines the `rustfs-signer` crate for AWS/S3-style request signing and presigning. The manifest identifies cryptography, web programming, and MinIO compatibility as the package domain.

## Dependencies and Integration
Dependencies include `http`, `hyper`, `s3s::Body`, `time`, `bytes`, `serde_urlencoded`, `base64-simd`, `tracing`, `thiserror`, and `rustfs-utils` with crypto/hash helpers. Doctests are disabled and workspace lints apply.

## Risks and Test Signals
The crate depends on canonicalization-sensitive libraries (`http::Uri`, `HeaderValue`, URL encoding) and project crypto wrappers. Build risk is moderate because signing behavior must remain compatible with AWS and S3-compatible services. Unit tests live in the signer modules.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/signer/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/signer/src/constants.rs -->
# sources/object-store/rustfs/crates/signer/src/constants.rs

## Purpose
Holds shared signing constants: unsigned payload sentinels, worker count, SigV4 algorithm name, and a timestamp format.

## Important APIs
`UNSIGNED_PAYLOAD` and `UNSIGNED_PAYLOAD_TRAILER` are S3 signing sentinel strings. `SIGN_V4_ALGORITHM` is `AWS4-HMAC-SHA256`. `ISO8601_DATEFORMAT` is a `time` format item slice for millisecond-style UTC timestamps. `TOTAL_WORKERS` is a crate-level numeric constant set to 4.

## Integration and Risks
The constants are consumed by signer modules, especially SigV4 payload handling. Timestamp format includes subsecond output; other signer code uses compact `YYYYMMDDTHHMMSSZ` for AWS canonical strings, so callers should not assume this constant is valid for every SigV4 field. `TOTAL_WORKERS` is not visibly tied to signing logic in the read files and may be legacy.

## Test Signals
No local tests in this file; correctness is indirectly tested by SigV4 module examples.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/signer/src/constants.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/signer/src/lib.rs -->
# sources/object-store/rustfs/crates/signer/src/lib.rs

## Purpose
Crate root and public facade for request signing modules.

## Important APIs
It declares modules for constants, streaming SigV4, unsigned streaming trailer, SigV2, SigV4, and utilities. It re-exports `streaming_sign_v4`, `try_streaming_sign_v4`, SigV2 and SigV4 error types, legacy signing/presigning wrappers, and fallible `try_` variants including trailer signing.

## Control Flow and Integration
No runtime logic executes here. It stabilizes the public API so downstream ECStore clients and transition code can import signing functions from `rustfs_signer` directly.

## Risks and Test Signals
Any change to re-exports affects downstream compatibility. The crate root does not re-export `streaming_unsigned_v4`, so that remains module-addressed/internal. Tests are in implementation modules.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/signer/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/signer/src/request_signature_streaming.rs -->
# sources/object-store/rustfs/crates/signer/src/request_signature_streaming.rs

## Purpose
Adds headers for SigV4 streaming payload requests and contains helpers for chunk string-to-sign/signature derivation. It prepares requests for AWS chunked upload, including optional trailer metadata.

## Important APIs and Functions
`try_build_chunk_string_to_sign` builds a chunk string-to-sign from request time, region, previous signature, and chunk checksum. `_try_build_chunk_signature` derives the S3 signing key and hashes that string. `try_streaming_sign_v4` is the fallible public API; `streaming_sign_v4` is the legacy wrapper that logs and returns the original request on error.

`streaming_sign_v4_inner` mutates headers: `X-Amz-Content-Sha256` becomes either `STREAMING-AWS4-HMAC-SHA256-PAYLOAD` or `STREAMING-AWS4-HMAC-SHA256-PAYLOAD-TRAILER`; trailers become lower-cased `X-Amz-Trailer` entries; trailer use inserts `Transfer-Encoding: aws-chunked`; session tokens become `X-Amz-Security-Token`; `X-Amz-Date` is formatted from `req_time`; and `x-amz-decoded-content-length` is set to a zero-padded decimal length.

## Control Flow and State
The function consumes and returns an `http::Request<s3s::Body>`. Errors are wrapped in `StreamingSignFailure` to preserve the original request for legacy behavior. No body transformation or actual chunk signing happens here; this file primarily annotates headers.

## Integration Points
Uses `request_signature_v4` signing-key helpers, `rustfs_utils::hash::EMPTY_STRING_SHA256_HASH`, `http::HeaderMap`, `time`, and `s3s::Body`. It is re-exported by `lib.rs`.

## Risks
The main function ignores access key, secret key, and region parameters for header mutation, so callers expecting complete streaming authorization must ensure another layer signs the request. It appends rather than inserts some headers, which may create duplicate values. Date formatting includes subsecond (`YYYY-MM-DDTHH:MM:SS.subsecondZ`), while AWS SigV4 canonical timestamps normally use compact no-subsecond form. There are no tests in this file.

## Test Signals
No local unit tests. Behavior is only indirectly covered if downstream integration tests exercise streaming uploads.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/signer/src/request_signature_streaming.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/signer/src/request_signature_streaming_unsigned_trailer.rs -->
# sources/object-store/rustfs/crates/signer/src/request_signature_streaming_unsigned_trailer.rs

## Purpose
Mutates a request for unsigned SigV4-style chunked streaming with trailers. It is used by SigV4 trailer signing flow after the Authorization header is computed.

## Important APIs and Functions
`streaming_unsigned_v4` inserts `Transfer-Encoding: aws-chunked`, conditionally inserts a valid `X-Amz-Security-Token`, and conditionally inserts `X-Amz-Date` formatted from `req_time`. It accepts but does not use `_data_len`.

## Control Flow and State
The function mutates headers in place and returns the request. Invalid session-token or date header values are silently skipped through `if let Ok(...)` guards; it does not expose a fallible API.

## Integration Points
Called from `request_signature_v4::sign_v4_inner` when trailer headers are present. Uses `http`, `time`, and `s3s::Body`.

## Risks
Silent skipping preserves legacy non-panicking behavior but can leave a request missing expected security token/date headers. The timestamp format includes subsecond and punctuation, not the compact SigV4 timestamp. `_data_len` is unused.

## Test Signals
A unit test verifies that an invalid session token is not inserted, `Transfer-Encoding` is still set, and `X-Amz-Date` exists.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/signer/src/request_signature_streaming_unsigned_trailer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/signer/src/request_signature_v2.rs -->
# sources/object-store/rustfs/crates/signer/src/request_signature_v2.rs

## Purpose
Implements AWS Signature Version 2 signing and presigning for S3-compatible requests.

## Important APIs and Functions
`SignV2Error` captures invalid headers, time formatting/components, query encoding, URI parsing/building, canonical UTF-8 conversion, header value parsing, and host resolution failures. Public APIs are `try_pre_sign_v2`/`try_sign_v2` plus legacy `pre_sign_v2`/`sign_v2` wrappers that log and return the original request on failure.

`pre_sign_v2_inner` sets an `Expires` header if absent, builds a canonical string, computes an HMAC-SHA1 signature, appends query credentials (`AWSAccessKeyId` or `GoogleAccessId` for Google Storage hosts), `Expires`, and `Signature`, and rewrites the URI. `sign_v2_inner` ensures a default RFC2822 `Date`, builds the canonical string, and inserts `Authorization: AWS access_key:signature`.

Canonical helpers write method, `Content-Md5`, `Content-Type`, `Date` or `Expires`, canonicalized `x-amz*` headers, and canonicalized resource query components from a fixed allowlist (`acl`, `uploadId`, `versionId`, etc.).

## Control Flow and State
The module consumes and returns requests. It uses local buffers and maps only; no persistent state. Time is current UTC with time replaced by midnight for Date/Expires behavior.

## Integration Points
Uses `try_get_host_addr` from signer utils, `rustfs_utils::crypto::hmac_sha1` and `hex`, `serde_urlencoded`, `hyper::Uri`, `http::HeaderValue`, and `s3s::Body`.

## Risks
V2 signing is canonicalization-sensitive. Query parsing via `HashMap` in presign may drop duplicate query keys and can reorder output. `virtual_host` is passed through but `encode_url2path` ignores it, so virtual-host-style canonical resources may be incomplete. The signature in Authorization uses URL-safe no-pad base64, which may differ from standard AWS SigV2 base64 expectations. Header canonicalization only includes values convertible to UTF-8 and silently drops invalid values.

## Test Signals
Unit tests verify presign query population, Date/Authorization insertion, canonicalized `?acl`, Authorization signature matching the injected Date, and missing optional headers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/signer/src/request_signature_v2.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/signer/src/request_signature_v4.rs -->
# sources/object-store/rustfs/crates/signer/src/request_signature_v4.rs

## Purpose
Implements AWS Signature Version 4 signing, presigning, trailer signing, and shared canonicalization helpers for S3 and internal STS-style signing.

## Important APIs and Functions
`SignV4Error` reports invalid header values, time failures, query encoding, URI construction, canonical UTF-8 conversion, and header value parsing. Public APIs are `try_pre_sign_v4`, `pre_sign_v4`, `try_sign_v4`, `sign_v4`, `try_sign_v4_trailer`, and `sign_v4_trailer`.

Shared helpers include `get_signing_key` (AWS4 date/region/service/aws4_request HMAC chain), `get_signature`, `get_scope`, `format_yyyymmdd`, `format_amz_datetime`, `try_get_hashed_payload`, `try_get_canonical_headers`, `get_signed_headers`, `try_get_canonical_request`, and `try_get_string_to_sign_v4`. Ignored headers are `accept-encoding`, `authorization`, and `user-agent`.

`pre_sign_v4_inner` appends `X-Amz-*` query parameters, canonicalizes the resulting request, computes a signature, and rewrites the URI with `X-Amz-Signature`. `sign_v4_inner` inserts `X-Amz-Date`, optional security token, optional trailer metadata and decoded length, optionally removes payload hash for STS, canonicalizes the request, computes Authorization, and for trailer requests calls `streaming_unsigned_v4` after adding trailer headers.

## Control Flow and State
Everything is synchronous request mutation. Static state is limited to the lazy ignored-header set. The legacy wrappers preserve non-panicking behavior by logging and returning the original request if canonicalization/signing fails.

## Integration Points
Uses `http::Request`, `http::Uri`, `HeaderMap`, `s3s::Body`, `time`, `serde_urlencoded`, `rustfs_utils::crypto::{hmac_sha256, hex, hex_sha256}`, signer constants, signer utils for host resolution and whitespace trimming, and the unsigned streaming trailer module.

## Risks
Canonical query handling sorts by key only and performs a post-hoc `+` to `%20` replacement; full AWS percent-encoding and duplicate key ordering may be incomplete. Presign builds the canonical request after including `X-Amz-Signature`, which is unusual for SigV4 and reflected in tests. `sign_v4_inner` signs with current time but builds credential scope using midnight (`t2`), which is the same date but surprising. Relative URIs with a Host header are rejected by the fallible API because canonical host resolution requires a URI host. Trailer flow computes Authorization before `streaming_unsigned_v4` mutates date/token/transfer headers, so the final signed header set must be reviewed carefully.

## Test Signals
Tests include AWS-style canonical request/string/signature examples, RustFS example signatures with host override and empty region, presigned URL examples, invalid non-UTF8 header handling, missing URI host handling, legacy non-panicking wrappers for invalid headers, STS wrapper behavior, and zero-padded date formatting.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/signer/src/request_signature_v4.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/signer/src/utils.rs -->
# sources/object-store/rustfs/crates/signer/src/utils.rs

## Purpose
Provides signer utility functions for host resolution, SigV4 whitespace normalization, and pair sorting.

## Important APIs and Functions
`HostAddrError` distinguishes invalid UTF-8 Host header and missing URI host. `try_get_host_addr` gets the URI host:port and prefers a differing valid Host header. `get_host_addr` is a legacy string-returning wrapper that falls back to Host header for relative URIs or URI host when Host is invalid. `sign_v4_trim_all` collapses runs of whitespace to one space. `stable_sort_by_first` sorts pairs by the first element.

## Control Flow and State
No persistence or state. Host resolution reads headers and URI components, preserving ports when present.

## Integration Points
SigV2 uses `try_get_host_addr` for presign credential selection. SigV4 uses it to canonicalize the required `host` header. Tests rely on `http::request` and `s3s::Body`.

## Risks
`try_get_host_addr` requires a URI host even if a valid Host header exists; this is stricter than the legacy `get_host_addr` and can reject relative requests. Host comparison is exact and does not normalize case or default ports. `stable_sort_by_first` uses Rust's slice sort, which is stable, but the function name's stability property is inherited from std behavior.

## Test Signals
Unit tests cover preferring an explicit differing Host header, preserving host:port, legacy relative-URI fallback, invalid Host header rejection, URI fallback on invalid Host for legacy API, and relative URI rejection for the fallible API.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/signer/src/utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/storage-api/Cargo.toml -->
# sources/object-store/rustfs/crates/storage-api/Cargo.toml

## Purpose
Defines `rustfs-storage-api`, a lightweight contract crate for storage API traits, DTOs, and stable error codes.

## Dependencies and Integration
Runtime dependencies are `async-trait`, `serde`, and `time`. Dev dependencies are `serde_json` and `tokio` with macros/runtime for async trait tests. Doctests are disabled and workspace lints apply.

## Risks and Test Signals
The manifest keeps implementation dependencies out of the API crate, which supports broad reuse. Adding storage backend crates here would increase coupling. Module tests cover async trait usage, DTO serialization/defaults, and error-code round trips.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/storage-api/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/storage-api/src/admin.rs -->
# sources/object-store/rustfs/crates/storage-api/src/admin.rs

## Purpose
Defines the admin-facing storage API contract for backend info, storage info, local storage info, disk inventory, and set drive counts.

## Important APIs and Types
`DiskSetSelector` identifies a pool/set pair by `pool_idx` and `set_idx` and has a const constructor. `StorageAdminApi` is an async trait requiring `Send + Sync + Debug`; associated types cover backend info, storage info, disk representation, and error type. Required methods are `backend_info`, `storage_info`, `local_storage_info`, `disk_set_inventory`, and `set_drive_counts`.

## Control Flow and State
The trait defines behavior but stores no state. Implementations own persistence and locking. `disk_set_inventory` returns `Vec<Option<Self::Disk>>`, which can represent missing/offline disks at stable positions.

## Integration Points
Re-exported by `storage-api/src/lib.rs` and intended for storage backends such as `ECStore` to implement while keeping admin consumers decoupled from concrete disk types.

## Risks
Associated return types are unconstrained beyond debug/send/sync/static, so consumers need generic plumbing or adapter types. There are no semantic guarantees about whether info calls are cached or live. `DiskSetSelector` uses raw indexes without validation.

## Test Signals
The test implements a `FakeStorageAdmin` and verifies backend info, storage info, drive counts, and optional disk inventory behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/storage-api/src/admin.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/storage-api/src/bucket.rs -->
# sources/object-store/rustfs/crates/storage-api/src/bucket.rs

## Purpose
Defines bucket option and metadata DTOs shared by storage APIs.

## Important APIs and Types
`MakeBucketOptions` includes object-lock, versioning, force-create, optional creation time, and no-lock flags. `SRBucketDeleteOp` models site-replication delete behavior as `NoOp`, `MarkDelete`, or `Purge`. `DeleteBucketOptions` includes locking/recreate/force flags plus site-replication delete op. `BucketOptions` controls list/get behavior for deleted/cached/no-metadata variants. `BucketInfo` serializes bucket name, created/deleted timestamps, versioning, and object locking.

## Control Flow, State, and Persistence
These are passive DTOs. Persistence is via serde for `MakeBucketOptions`, `BucketOptions`, and `BucketInfo`; `DeleteBucketOptions` and `SRBucketDeleteOp` are currently not serde-enabled in this file.

## Integration Points
Re-exported by `storage-api/src/lib.rs` and used by scanner lifecycle tests through `MakeBucketOptions`. Storage crates use these values for bucket create/delete/list contracts.

## Risks
Most structs derive `Default`, so new boolean fields default to false; this must match storage semantics. `SRBucketDeleteOp` lacks `Eq`, `Serialize`, and `Deserialize`, which may limit wire/config use. Time serialization depends on workspace `time` serde configuration.

## Test Signals
Tests verify `BucketInfo` JSON round trip, default `BucketOptions` false flags, and default `DeleteBucketOptions` using `SRBucketDeleteOp::NoOp` with false flags.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/storage-api/src/bucket.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/storage-api/src/error.rs -->
# sources/object-store/rustfs/crates/storage-api/src/error.rs

## Purpose
Provides stable storage error codes and a default `StorageResult` alias for cross-crate storage contracts.

## Important APIs and Types
`StorageErrorCode` enumerates disk, volume, bucket, object, multipart, erasure quorum, decommission, rebalance, cancellation, and namespace lock errors. `as_u32` maps each variant to a stable hexadecimal code. `from_u32` decodes known codes to variants and returns `None` for unknown values. `StorageResult<T, E = StorageErrorCode>` defaults result errors to this code enum.

## Control Flow and State
The mapping is entirely const match logic with no persistence in this module. Stability of numeric codes is the core persistence contract because codes may be serialized or passed over boundaries elsewhere.

## Integration Points
Re-exported by `storage-api/src/lib.rs`. Backend and admin API crates can use numeric codes for wire-safe or storage-safe error representation without depending on concrete error types.

## Risks
There are gaps at `0x2B` and `0x2C`, and code assignments must not be reused accidentally. The enum does not implement `Display`, `Error`, or serde here, so adapters must add presentation/wire conversion. Adding variants requires updating both matches and tests.

## Test Signals
A complete table-driven unit test verifies round trips for every listed variant. Additional tests reject unknown/gap values and confirm the default `StorageResult` error type.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/storage-api/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/storage-api/src/lib.rs -->
# sources/object-store/rustfs/crates/storage-api/src/lib.rs

## Purpose
Crate root for storage API contracts.

## Important APIs
Declares modules `admin`, `bucket`, and `error`, then re-exports `DiskSetSelector`, `StorageAdminApi`, bucket DTOs, `StorageErrorCode`, and `StorageResult`.

## Control Flow and Integration
No runtime logic. The root acts as the public facade for storage consumers and implementations.

## Risks and Test Signals
Re-export changes are semver-sensitive. Tests are in submodules.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/storage-api/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/Cargo.toml -->
# sources/object-store/rustfs/crates/targets/Cargo.toml

## Purpose
Defines `rustfs-targets`, the notification/audit target abstraction and implementation crate.

## Dependencies and Integration
The manifest pulls in configuration, extension schema, TLS runtime, S3 types, async traits, network clients for AMQP, NATS, Pulsar, MQTT, Redis, Kafka, MySQL, PostgreSQL, HTTP/webhook, rustls/native certs, queue/serialization utilities, metrics, `arc-swap`, `parking_lot`, and Tokio. Dev dependencies include Criterion and tempfile. It declares the `queue_store_benchmark` Criterion bench.

## Risks and Test Signals
This is a broad integration crate with many optional-looking but direct dependencies, so build times and supply-chain surface are significant. The bench target focuses on queue-store raw read/write performance with and without compression. Workspace lints apply.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/benches/queue_store_benchmark.rs -->
# sources/object-store/rustfs/crates/targets/benches/queue_store_benchmark.rs

## Purpose
Criterion benchmark for `QueueStore` raw payload write/read throughput with compression off and on.

## Important APIs and Functions
`BenchEvent` is a representative serializable payload shape. `bench_dir` creates unique temp directories. `build_payload` creates JSON payloads of requested sizes with metadata and repeated content. `queue_store_write_benchmark` measures `QueueStore::put_raw` followed by `del`. `queue_store_read_benchmark` stores one payload and repeatedly measures `get_raw`. `criterion_group!` and `criterion_main!` register both groups.

## Control Flow and State
Each benchmark case creates a new queue store under a temp directory, opens it, runs Criterion iterations, and calls `store.delete()` afterward. Write cases delete each key inside the measured iteration, so the measurement includes delete overhead.

## Integration Points
Uses `rustfs_targets::store::{QueueStore, Store}`, serde JSON, UUIDs, Criterion throughput metadata, and `Arc` for shared read benchmark state.

## Risks
Temp cleanup is best-effort and may leave directories if a benchmark panics. Write benchmark measures put plus delete rather than pure put. Payload construction uses string slicing by byte count over ASCII content, which is safe here but would not be for arbitrary UTF-8. Compression is represented as snap on/off through `new_with_compression`.

## Test Signals
This is not a correctness test; it provides performance signals for 512 B, 8 KiB, and 64 KiB payloads, each with compression disabled/enabled for raw put/get.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/benches/queue_store_benchmark.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/arn.rs -->
# sources/object-store/rustfs/crates/targets/src/arn.rs

## Purpose
Defines target IDs and ARN representations for notification targets, including serde conversion and parsers.

## Important APIs and Types
`TargetID` stores `id` and `name`, formats as `id:name`, parses exactly one colon with `splitn(2, ':')`, serializes as a string, and can convert to an `ARN` for a region. `TargetIDError` reports invalid `ID:Name` strings.

`ARN` stores target ID, region, service, and partition. `ARN::new` uses default service/partition from `rustfs_config::notify`. `to_arn_string` formats with `ARN_PREFIX`. `ARN::parse` strictly accepts strings starting with `ARN_PREFIX` and exactly six colon-separated tokens, rejecting empty target id/name and returning `TargetError::InvalidARN`. `Display` emits `arn:partition:service:region:id:name`. `FromStr` is more general: it accepts any `arn` prefix with at least six tokens and rejoins remaining tokens into the name. Empty-string deserialization yields an empty default ARN.

## Control Flow and State
No persistence beyond serde string form. Parsers are synchronous and allocate token vectors.

## Integration Points
Uses `rustfs_config::notify::{ARN_PREFIX, DEFAULT_ARN_PARTITION, DEFAULT_ARN_SERVICE}`, `crate::TargetError`, serde traits, and `thiserror`. Target configuration and event routing likely use these IDs to match configured notification targets.

## Risks
There are two parsing paths with different strictness: `ARN::parse` requires exactly six tokens and RustFS prefix, while `FromStr` allows names containing colons and arbitrary partition/service. `to_arn_string` and `Display` may diverge if `ARN_PREFIX` changes from the displayed partition/service composition. `TargetID::from_str` permits empty id or name if a colon exists.

## Test Signals
No tests in this file. Behavior is likely exercised indirectly by target config tests elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/arn.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/catalog/builtin.rs -->
# sources/object-store/rustfs/crates/targets/src/catalog/builtin.rs

## Purpose
Builds built-in audit and notification target descriptors for all supported channel target types. These descriptors connect config subsystem names, request validators, valid config keys, config validation functions, argument builders, and concrete target constructors.

## Important APIs and Functions
`build_descriptor` constructs a generic `BuiltinTargetDescriptor<E>` from subsystem metadata, request validator, target type string, valid field list, validation callback, and target creation callback. `build_admin_descriptor` creates admin-facing descriptor metadata without instantiating targets.

`builtin_audit_target_admin_descriptors` and `builtin_notify_target_admin_descriptors` return descriptor metadata for AMQP, webhook, MQTT, NATS, Pulsar, Kafka, Redis, MySQL, and PostgreSQL. `builtin_audit_target_descriptors<E>` and `builtin_notify_target_descriptors<E>` return full descriptors that validate config and construct typed targets such as `AMQPTarget`, `WebhookTarget`, `MQTTTarget`, `NATSTarget`, `PulsarTarget`, `KafkaTarget`, `RedisTarget`, `MySqlTarget`, and `PostgresTarget`.

## Control Flow and State
All functions build vectors on demand. There is no registry mutation in this file. The descriptors capture closures that later validate configs and construct boxed target trait objects.

## Integration Points
This module joins `rustfs_config` audit/notify constants, `crate::config` validators/builders, `crate::plugin` descriptor types, `crate::target` concrete implementations, `TargetType`, and default queue directories (`AUDIT_DEFAULT_DIR`, `EVENT_DEFAULT_DIR`). It feeds both runtime target loading and extension catalog generation.

## Risks
The audit and notify descriptor lists are manually duplicated; missing one target in one list can cause inconsistent admin/runtime behavior. Generic event type `E` requires clone/serde bounds across all targets. Each closure encodes a default queue directory and target type, so copy-paste errors are plausible. The file has no local tests; uniqueness is partially checked by extension catalog tests that consume admin descriptors.

## Test Signals
No direct tests. Indirect signals come from catalog extension tests expecting nine unique built-in target extension schemas and from target-specific config/integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/catalog/builtin.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/catalog/extension.rs -->
# sources/object-store/rustfs/crates/targets/src/catalog/extension.rs

## Purpose
Builds extension-schema metadata for built-in target plugins, S3 post-auth hooks, and ops diagnostics. It maps target marketplace manifests and built-in capabilities into the shared `rustfs_extension_schema` contracts.

## Important APIs and Functions
Constants define API/capability names: `OPS_DIAGNOSTICS_EXTENSION_API_VERSION`, `S3_HOOK_EXTENSION_API_VERSION`, `TARGET_AUDIT_CAPABILITY`, and `TARGET_NOTIFY_CAPABILITY`.

`builtin_extension_schemas` combines target schemas, S3 hook schema, and ops diagnostics schema. `builtin_s3_hook_extension_schema` and `builtin_s3_hook_contract` describe a built-in post-auth hook registry that does not mutate object data or bypass IAM. `builtin_ops_diagnostics_extension_schema` and `builtin_ops_diagnostics_contract` expose metrics, trace, profile, health, and diagnostics surfaces requiring admin action.

`target_marketplace_extension_schema` maps `TargetPluginMarketplaceManifest` to `ExtensionSchema`, selecting runtime boundary, mapping supported domains to capabilities, and disabling external or boundary-required plugins by default. `builtin_target_extension_schemas` deduplicates built-in target types from audit and notify admin descriptors through a `BTreeMap`.

## Control Flow and State
Everything is pure vector/struct construction. Deduplication state is local to `builtin_target_extension_schemas`.

## Integration Points
Consumes built-in target admin descriptors, target domain and manifest types, and the extension schema crate's validation contracts. This file bridges target plugin metadata to a broader extension catalog.

## Risks
Capability ordering follows manifest `supported_domains`; consumers should not depend on more than documented order. Built-in target schemas depend on admin descriptors rather than runtime descriptors, so admin/runtime descriptor drift can affect catalog accuracy. External packaging is disabled by default even if entrypoint metadata says builtin, which is intentional but important.

## Test Signals
Unit tests validate builtin target marketplace mapping, external sidecar disabled mapping, external packaging disabled behavior, uniqueness and validation of nine built-in target schemas, combined catalog size of eleven, S3 post-auth hook contract semantics, and ops diagnostics admin/read-only semantics.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/catalog/extension.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/catalog/mod.rs -->
# sources/object-store/rustfs/crates/targets/src/catalog/mod.rs

## Purpose
Catalog module root plus an example installable external webhook sidecar plugin. It exposes built-in and extension catalog submodules and provides a fully populated example manifest/installation/runtime tuple for tests and documentation-like usage.

## Important APIs and Types
`ExampleInstallableTargetPlugin` groups a `TargetPluginMarketplaceManifest`, `TargetPluginInstallation`, `SidecarPluginRuntime`, and valid field names. `example_external_webhook_plugin` builds a `TargetPluginManifest` for `external:webhook-sidecar`, wraps it with an installable marketplace manifest and distribution artifact metadata, constructs a sidecar handshake with health/send/shutdown capabilities, creates a `SidecarPluginRuntime`, enables it with verified external policy/safety checks, and returns installation metadata marked installed.

## Control Flow and State
The function is deterministic except for no external I/O; it constructs in-memory metadata only. The hard-coded `last_verified` timestamp is `"2026-05-13T20:00:00Z"`.

## Integration Points
Uses control-plane installation helpers, target domain and manifest types, sidecar runtime policy and protocol types, and is consumed by `catalog/extension.rs` tests to verify external manifest mapping.

## Risks
The example includes placeholder URLs and digest/signature/provenance values; it must not be treated as a real install source. Hard-coded policy values and timestamp can become stale as protocol versions evolve. Because tests rely on this example, changes to sidecar safety policy validation may require updates here.

## Test Signals
A unit test verifies plugin id, installed state, healthy runtime, and valid field list. Extension catalog tests also consume this example to verify sidecar mapping and disabled-by-default behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/catalog/mod.rs -->
