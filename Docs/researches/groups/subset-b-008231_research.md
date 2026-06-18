# subset-b-008231 Research

Grouped research report for the subset B work item. Each source file below has its own source-path-titled section, bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/jwt/tests.rs -->
# sources/object-store/rustfs/crates/crypto/src/jwt/tests.rs

## Purpose
This file is the unit-test suite for the crypto crate's JWT wrapper. It validates that `super::encode::encode` and `super::decode::decode` interoperate for JSON claims signed with a shared secret, and that decoding rejects malformed, expired, or incorrectly signed tokens. The tests document the intended JWT behavior exposed later as `rustfs_crypto::jwt_encode` and `rustfs_crypto::jwt_decode`.

## Important APIs, Types, and Functions
The suite uses `serde_json::json!` to build arbitrary claim payloads and `time::OffsetDateTime::now_utc().unix_timestamp()` for time-sensitive `exp`, `iat`, and `nbf` claims. It exercises the opaque `encode(secret, &claims) -> Result<String, _>` API and `decode(&jwt_token, secret) -> Result<TokenData<Value>, _>`, then checks `decoded.claims` and `decoded.header`.

## Control Flow
Most tests follow a common flow: create claims, sign them with a byte-slice secret, decode with either the same or a different secret, and assert success or failure. Negative tests iterate invalid token strings, use expired `exp` claims, or change the secret. Header tests split the token into three dot-separated segments and assert the decoded algorithm is `jsonwebtoken::Algorithm::HS512`.

## State and Persistence
The file has no persistent state. It depends on wall-clock time, so tokens with `exp` close to `now` could be flaky if the clock changes, but the chosen offsets are large enough for normal test execution. Deterministic encoding is asserted only with fixed integer timestamps.

## Dependencies and Integration Points
The tests depend on the local `jwt` module, `serde_json`, `time`, and the `jsonwebtoken` header type. They are compiled as child module tests of `crypto/src/jwt.rs`, not through the public crate re-exports directly, but they protect the same implementation that `crypto/src/lib.rs` exports.

## Risks and Edge Cases
The suite confirms expiration validation but explicitly documents that future `iat` is not rejected by the current implementation. It does not test `aud`, `iss`, clock skew, missing `exp`, non-object claims, or algorithm-confusion attempts. The acceptance of very short secrets is tested, which is useful compatibility coverage but also shows no minimum HMAC secret strength is enforced here.

## Test Signals
Strong positive signals include round trips for nested JSON, arrays, booleans, numeric values, special characters, unicode strings, and a 10 KB payload. Negative signals include wrong-secret rejection, malformed token rejection, and expired token rejection. The file itself is the test signal for JWT signing and validation behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/jwt/tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/lib.rs -->
# sources/object-store/rustfs/crates/crypto/src/lib.rs

## Purpose
This is the public facade for the `rustfs-crypto` crate. It wires internal encryption, error, JWT, and license-token modules into a small crate API and enforces `#![deny(clippy::unwrap_used)]` at crate level.

## Important APIs, Types, and Functions
The file declares private modules `encdec`, `error`, and `jwt`, plus public module `license_token`. It publicly re-exports `decrypt_data`, `encrypt_data`, the `Error` type, JWT helpers as `jwt_decode` and `jwt_encode`, and license helpers `Token`, `sign_license_token`, `parse_signed_license_token`, and `parse_license_with_public_key`. Stream I/O encryption helpers are exported only when the `crypto` feature is enabled.

## Control Flow
There is no runtime control flow beyond module resolution and conditional compilation. The file decides which lower-level functions become part of the stable crate surface and which remain implementation details.

## State and Persistence
No state is stored here. Persistence and cryptographic state are delegated to the re-exported modules. The feature-gated stream I/O exports can change available API shape depending on Cargo features.

## Dependencies and Integration Points
Downstream crates should import crypto behavior through this file rather than reaching into internal modules. `jwt_encode` and `jwt_decode` integrate with the JWT submodule, while license verification integrates with RSA signing code in `license_token.rs`.

## Risks and Edge Cases
The facade can accidentally expose or hide APIs through re-export changes. Deprecation of legacy license encryption helpers is enforced in `license_token.rs`, but this facade does not re-export the deprecated `gencode` and `parse`, which nudges callers toward public-key verification.

## Test Signals
There are no tests in this file. Behavior is covered indirectly by tests in `jwt/tests.rs`, `license_token.rs`, and any downstream crate tests using the public re-exports.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/license_token.rs -->
# sources/object-store/rustfs/crates/crypto/src/license_token.rs

## Purpose
This module defines RustFS license-token encoding and verification. It keeps legacy RSA encryption/decryption helpers for compatibility but marks them deprecated, while the preferred flow signs a JSON token with a private key and verifies it with only a public key.

## Important APIs, Types, and Functions
`Token` is a serializable structure with `name` and `expired` fields. Deprecated `gencode` encrypts serialized token JSON with an RSA public key using PKCS#1 v1.5 encryption, and deprecated `parse` decrypts with a PKCS#8 private key. `sign_license_token` serializes `Token`, signs the JSON payload using RSA-PSS with SHA-256 via `BlindedSigningKey`, concatenates `signature || payload`, and base64url-encodes without padding. `parse_signed_license_token` decodes, determines signature length from the RSA public key size, verifies the RSA-PSS signature, and deserializes the payload. `parse_license_with_public_key` is a compatibility alias for signed parsing.

## Control Flow
Signing parses the private PEM, signs the JSON payload with randomness, appends payload bytes after the signature, then encodes the combined bytes. Verification decodes the outer token, parses the public PEM, splits the buffer by the key's signature length, rejects missing payloads, verifies before deserializing, and returns a `Token` only after signature validation succeeds.

## State and Persistence
The module is stateless. Token persistence is external and represented as an encoded string. The `expired` timestamp is stored but not enforced by the parser; callers must check expiration after verification.

## Dependencies and Integration Points
The module depends on `rsa`, `serde`, `serde_json`, `rand`, and `base64_simd`. It is re-exported by `crypto/src/lib.rs` for consumers that need license issuance or verification. Runtime services can use public-key parsing without private key material.

## Risks and Edge Cases
The signed format has no explicit version, key id, algorithm marker, or payload length field, so future format migration would need out-of-band handling. RSA-PSS signing is randomized, so repeated signing of the same token will produce different strings. Legacy `gencode`/`parse` use PKCS#1 v1.5 encryption and require private-key parsing at verification time, which is why they are deprecated. Expiration is not checked inside verification.

## Test Signals
Unit tests generate 2048-bit keys, verify signed round trips, verify legacy encrypted round trips, reject tampered payloads, reject invalid base64-like tokens, reject invalid signing keys, and assert the source file does not embed a private key marker. Tests cover integrity and key parsing, but not expiration enforcement or cross-key rejection.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/license_token.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/data-usage/Cargo.toml -->
# sources/object-store/rustfs/crates/data-usage/Cargo.toml

## Purpose
This manifest defines the `rustfs-data-usage` crate, which provides shared data-usage models and cache algorithms for RustFS storage usage reporting.

## Important APIs, Types, and Functions
The manifest identifies the crate as a library with doctests disabled. Its package metadata is workspace-driven for version, edition, license, repository, rust version, and homepage. The description, keywords, and categories position it as a data-structure and filesystem-oriented crate.

## Control Flow
There is no runtime control flow in the manifest. It controls compilation by selecting workspace dependencies and applying workspace lint settings.

## State and Persistence
Persistence support is implied by dependencies on `serde` and `rmp-serde`, which are used by `data_usage.rs` for serializing `DataUsageCache` and usage models. No build script or generated state is declared.

## Dependencies and Integration Points
The crate depends on `serde`, `path-clean`, `rmp-serde`, `async-trait`, and `rustfs-filemeta`. These map directly to path normalization, MessagePack cache serialization, async storage traits, and object metadata conversion in the source.

## Risks and Edge Cases
Because versions and dependency settings are inherited from the workspace, compatibility depends on workspace-level changes. Disabling doctests is appropriate for a model crate without examples, but it means documentation snippets would not be validated if added later.

## Test Signals
The manifest has no direct tests. Test coverage comes from `src/data_usage.rs` unit tests and e2e tests that deserialize `rustfs_data_usage::DataUsageInfo` from admin APIs.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/data-usage/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/data-usage/src/data_usage.rs -->
# sources/object-store/rustfs/crates/data-usage/src/data_usage.rs

## Purpose
This file contains the shared data-usage domain model and cache algorithms for RustFS. It represents capacity, bucket usage, object/version/delete-marker counts, histograms, replication summaries, per-disk status, and a hierarchical cache that can be merged, flattened, compacted, serialized, and converted into admin-facing `DataUsageInfo`.

## Important APIs, Types, and Functions
Core serializable types include `TierStats`, `AllTierStats`, `BucketTargetUsageInfo`, `BucketUsageInfo`, `DataUsageInfo`, and `DiskUsageStatus`. Cache types include `DataUsageHash`, `DataUsageEntry`, `DataUsageCacheInfo`, and `DataUsageCache`. Histogram types `SizeHistogram` and `VersionsHistogram` bucket object size and version-count distributions. Replication types include `ReplicationStats` and `ReplicationAllStats`. Important methods include `DataUsageCache::replace`, `replace_hashed`, `find`, `flatten`, `copy_with_children`, `delete_recursive`, `size_recursive`, `search_parent`, `force_compact`, `reduce_children_of`, `merge`, `dui`, `marshal_msg`, and `unmarshal`. `DataUsageInfo` exposes compatibility helpers such as `add_object`, `add_object_from_file_meta`, `update_capacity`, `add_bucket_usage`, `calculate_totals`, and `merge`.

## Control Flow
Cache writes hash cleaned paths and attach child hashes to parent entries. Read paths either find direct entries or recursively flatten children into aggregate usage. Compaction walks internal nodes, estimates descendant count, chooses candidates sorted by object count, flattens selected subtrees, marks them compacted, deletes descendants, and reinserts compacted summaries. `merge` combines roots, preserves the newest `last_update`, and merges or inserts flattened direct children from the other cache. `dui` flattens the requested path and each requested bucket into a `DataUsageInfo` response.

## State and Persistence
The cache persists as a `HashMap<String, DataUsageEntry>` plus `DataUsageCacheInfo`; `marshal_msg` and `unmarshal` use MessagePack via `rmp-serde`. Storage-specific load/save is intentionally abstracted behind the async `DataUsageCacheStorage` trait and implemented elsewhere. `SystemTime` is stored in info and admin responses. `failed_objects` and `disk_usage_status` are serde-defaulted for backward-compatible deserialization.

## Dependencies and Integration Points
The file depends on `path-clean` for canonical path keys, `serde` for API and cache serialization, `rmp-serde` for compact persistence, `async-trait` for backend storage integration, and `rustfs-filemeta` for converting object metadata and versions. E2e admin data-usage tests deserialize `DataUsageInfo` directly, so field names are part of a wire contract.

## Risks and Edge Cases
`DataUsageHash` uses cleaned path strings rather than cryptographic hashes, despite the type name. Some histogram naming differs between cache histograms and compatibility helpers (`LESS_THAN_1024_B` versus `0-1KB`), which can surprise consumers if both code paths feed the same UI. `DataUsageEntry::merge` clears existing replication target maps before adding other stats, which requires care when merging multiple sources. `extract_bucket_from_path` returns an empty string for paths beginning with `/`, because it only checks `parts.is_empty()`. Recursive flattening and deletion can be expensive for very large trees, hence compaction logic.

## Test Signals
Unit tests cover capacity updates, bucket merge totals, `SizeSummary::add`, cache merge inserting missing children, cache merge accumulating existing children, compaction candidate selection, leaf exclusion, subtree compaction, and saturating subtraction to prevent underflow during compaction. Broader behavioral coverage is supplied by admin data-usage e2e tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/data-usage/src/data_usage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/data-usage/src/lib.rs -->
# sources/object-store/rustfs/crates/data-usage/src/lib.rs

## Purpose
This is the public entry point for `rustfs-data-usage`. It exposes the `data_usage` module and re-exports all of its public items for downstream crates.

## Important APIs, Types, and Functions
The file declares `pub mod data_usage;` and `pub use data_usage::*;`. This makes `DataUsageInfo`, `BucketUsageInfo`, `DataUsageCache`, histogram types, replication stats, storage traits, and helper functions available directly under `rustfs_data_usage`.

## Control Flow
There is no runtime flow. The file controls namespace shape and avoids requiring callers to import through `rustfs_data_usage::data_usage::*`.

## State and Persistence
No state is stored here. Serialization and cache persistence behavior live in `data_usage.rs`.

## Dependencies and Integration Points
E2e tests import `rustfs_data_usage::DataUsageInfo`, relying on this re-export. Other RustFS crates can use shared usage models without knowing the internal module layout.

## Risks and Edge Cases
The glob re-export exposes every public item from `data_usage.rs`; adding a new public item there automatically becomes part of the crate-level API. That is convenient but increases semver surface.

## Test Signals
No local tests are present. Coverage is indirect through `data_usage.rs` unit tests and crates that import the re-exported types.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/data-usage/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/Cargo.toml -->
# sources/object-store/rustfs/crates/e2e_test/Cargo.toml

## Purpose
This manifest defines the RustFS `e2e_test` crate, a test-support and integration-test crate used to run S3, admin, protocol, checksum, compression, TLS, and cluster behavior tests against local RustFS binaries.

## Important APIs, Types, and Functions
The manifest enables optional features `ftps` and `sftp` plus an empty default feature set. It declares dependencies needed by the requested tests: AWS S3 SDK, `reqwest`, `tokio`, `serial_test`, `rustfs-signer`, `rustfs-madmin`, `rustfs-data-usage`, `rustfs-rio`, compression crates, hash crates, `zip`, `rcgen`, `rustls`, `clap`, and `anyhow`.

## Control Flow
The manifest controls test compilation and binary availability. The `src/bin/tls_gen.rs` binary is built from this crate and links to `e2e_test::tls_gen`. Test modules in `src/lib.rs` are gated by `#[cfg(test)]`, so they compile as integration-test support.

## State and Persistence
No runtime state is stored in the manifest. Dependencies enable tests to create temporary RustFS data directories, run child processes, generate TLS bundles, and serialize/deserialize admin responses.

## Dependencies and Integration Points
The crate integrates heavily with the workspace: `rustfs-config`, `rustfs-ecstore`, `rustfs-data-usage`, `rustfs-rio`, `rustfs-madmin`, `rustfs-filemeta`, and `rustfs-signer` are workspace crates. External dependencies provide S3 clients, HTTP clients, signing helpers, archive generation, TLS certificate generation, and async runtime support.

## Risks and Edge Cases
Because e2e tests spawn real RustFS binaries, dependency changes can affect compile time and runtime reliability. Optional protocol features must match binary build features through helper logic in `common.rs`. Tools like `awscurl` are external and skipped when absent in some tests.

## Test Signals
The manifest itself is not tested, but it is the dependency contract for all requested e2e files. Missing dependencies would break compilation of the corresponding modules or the `tls_gen` binary.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/admin_timeout_regression_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/admin_timeout_regression_test.rs

## Purpose
This e2e regression test verifies that a single slow or suspended peer in a four-node cluster does not cause admin `/info` or `/storageinfo` endpoints to synthesize offline disks or offline servers. It targets an issue where one admin timeout could incorrectly mark healthy cluster state as degraded.

## Important APIs, Types, and Functions
`signed_admin_get` manually signs admin GET requests with `rustfs_signer::sign_v4` and `UNSIGNED_PAYLOAD`. `fetch_info` and `fetch_storage_info` parse admin JSON into `rustfs_madmin::InfoMessage` and `StorageInfo`. `offline_server_count` counts servers whose state is `ITEM_OFFLINE`. The test uses `RustFSTestClusterEnvironment` for cluster lifecycle and AWS S3 SDK for an object put/get during the peer suspension window.

## Control Flow
The test starts a four-node cluster, creates a bucket, verifies warm admin state has zero offline disks, sends `SIGSTOP` to node 1, schedules `SIGCONT` after six seconds, and concurrently fetches admin info, storage info, and writes an object through node 0 under a 20-second timeout. After the peer resumes, it asserts admin responses showed no offline state and the object remains readable.

## State and Persistence
State includes temporary cluster data directories, child RustFS processes, one test bucket, and one object key. Process suspension is OS-level state controlled by `kill -STOP` and `kill -CONT`.

## Dependencies and Integration Points
The test integrates admin HTTP endpoints, RustFS distributed storage state, process management, SigV4 signing, and S3 object I/O. It is registered from `e2e_test/src/lib.rs` under `#[cfg(test)]`.

## Risks and Edge Cases
The test is Linux/Unix-specific because it shells out to `kill` with signals. Timing can be sensitive on slow machines, although generous admin and readiness timeouts help. It asserts a single suspended node should not become offline during the narrow admin timeout window, not long-term node failure behavior.

## Test Signals
Positive signals are zero offline disks before suspension, zero offline disks and zero offline servers during suspension, successful concurrent `PutObject`, zero offline disks after resume, and exact object body readback.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/admin_timeout_regression_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/anonymous_access_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/anonymous_access_test.rs

## Purpose
This regression suite verifies anonymous `GetObject` access behavior when a bucket policy allows public reads and PublicAccessBlock configuration is missing, enabled, or explicitly disabled. It covers issue #2036 around missing PublicAccessBlock config incorrectly blocking anonymous policy access.

## Important APIs, Types, and Functions
`setup_public_bucket` creates a bucket, installs an allow-anonymous `s3:GetObject` policy for `bucket/*`, uploads `test.txt`, and returns the admin S3 client. `anonymous_get_object` uses `reqwest` without credentials through `local_http_client`. Tests use AWS SDK `PublicAccessBlockConfiguration`.

## Control Flow
Each test starts a single RustFS server, prepares a public bucket, sets or deletes PublicAccessBlock state, performs an unsigned HTTP GET, and asserts the status code. Missing config and `restrict_public_buckets(false)` expect 200; `restrict_public_buckets(true)` expects 403.

## State and Persistence
The tests create temporary RustFS storage, buckets, one object, bucket policies, and optional PublicAccessBlock configuration. State is cleaned when `RustFSTestEnvironment` drops or `stop_server` runs.

## Dependencies and Integration Points
The file integrates bucket policy authorization, PublicAccessBlock evaluation, AWS SDK S3 control APIs, and raw anonymous HTTP reads. It depends on `common.rs` for server lifecycle and proxy-free HTTP.

## Risks and Edge Cases
Bucket names are fixed per test, so `serial` is required to avoid conflicts. The tests validate only `RestrictPublicBuckets`, not all PublicAccessBlock flags. They assert status codes but do not inspect error XML codes.

## Test Signals
The status-code matrix is the main signal: 200 when configuration is absent, 403 when public buckets are restricted, and 200 when restriction is explicitly disabled.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/anonymous_access_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/archive_download_integrity_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/archive_download_integrity_test.rs

## Purpose
This file provides archive-content integrity and content-encoding regression coverage for ZIP uploads and downloads, including multipart archives, SigV4 presigned downloads, reverse proxy forwarding, HTTP response compression interaction, and strict rejection of unsafe archive `Content-Encoding`.

## Important APIs, Types, and Functions
Helpers build stored ZIP bytes with `zip::ZipWriter`, generate deterministic random bytes, start RustFS with environment overrides, make signed PUT/GET requests with `rustfs_signer`, pre-sign GET URLs, and run a one-shot reverse proxy over `tokio::net::TcpListener`. `complete_archive_multipart_upload_with_content_encoding` creates a multipart ZIP object and returns the exact expected bytes. `assert_archive_object_content_encoding` checks HEAD, GET, and body equality.

## Control Flow
Tests start RustFS in different env modes, create buckets, upload ZIP objects by signed raw PUT or AWS SDK multipart APIs, then assert status codes, metadata, and exact bytes. Strict mode is toggled by `RUSTFS_REJECT_ARCHIVE_CONTENT_ENCODING`. HTTP compression is toggled with `RUSTFS_COMPRESS_ENABLE`, MIME type, and minimum-size variables. Presigned tests compare direct and proxied downloads against the original multipart ZIP bytes.

## State and Persistence
State includes temporary server data, buckets for regular and multipart archive tests, multipart upload ids and parts, content-encoding metadata, and generated archive bytes. The reverse proxy is transient and serves a single forwarded request.

## Dependencies and Integration Points
The file exercises S3 PutObject, CreateMultipartUpload, UploadPart, CompleteMultipartUpload, GetObject, HeadObject, conditional headers, SigV4 signing, presigned URLs, reqwest decompression controls, response compression configuration, and RustFS archive/content-encoding policy.

## Risks and Edge Cases
The tests are relatively expensive because they spawn servers and upload multi-megabyte data. They rely on fixed 5 MiB multipart thresholds and exact content-length behavior. Strict-mode behavior is archive-specific and tests ZIP content type rather than all archive MIME variants. Raw reverse proxy code is deliberately minimal and intended for a one-request path only.

## Test Signals
Signals include allowing normal archive content encoding by default, rejecting effective archive encodings in strict mode, stripping `aws-chunked` while preserving effective encodings, disabling HTTP compression for archive downloads, exact SHA-256/body equality for multipart downloads, ignoring empty conditional ETag headers, and preserving bytes through presigned direct and reverse-proxied downloads.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/archive_download_integrity_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/bin/tls_gen.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/bin/tls_gen.rs

## Purpose
This binary is the command-line entry point for generating a RustFS TLS bundle for local TLS and mTLS tests.

## Important APIs, Types, and Functions
It imports `clap::Parser` and `e2e_test::tls_gen::{Args, run}`. `main` parses CLI arguments into `Args`, calls `run`, prints the generated output directory, and returns `anyhow::Result<()>`.

## Control Flow
The flow is a thin wrapper: parse arguments, generate the bundle through the library module, print success output, and propagate any error via `?`.

## State and Persistence
The binary writes no files directly. Persistence is delegated to `tls_gen::run`, which returns the output directory path. The only local side effect is stdout.

## Dependencies and Integration Points
This file depends on the `e2e_test` library exporting `pub mod tls_gen` from `src/lib.rs`, plus the manifest's `clap` and `anyhow` dependencies. It provides a reusable CLI around the same library code that tests can call directly.

## Risks and Edge Cases
There is little logic here, so risk is mostly argument-surface mismatch with `tls_gen::Args`. Errors are not customized at the CLI wrapper layer.

## Test Signals
No direct tests are in this file. The underlying `tls_gen` module has tests for writing a full bundle and rejecting non-positive validity days, which indirectly cover the CLI's called function.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/bin/tls_gen.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/bucket_logging_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/bucket_logging_test.rs

## Purpose
This file tests S3-compatible "dummy" bucket control APIs: bucket logging, accelerate configuration, request payment, and website configuration. It verifies both AWS SDK behavior and raw HTTP/XML contracts.

## Important APIs, Types, and Functions
Helpers locate and invoke `awscurl`, parse HTTP status lines, extract bodies, and extract headers from raw output. Tests use AWS SDK types such as `BucketLoggingStatus`, `LoggingEnabled`, `AccelerateConfiguration`, `BucketAccelerateStatus`, `RequestPaymentConfiguration`, `Payer`, `WebsiteConfiguration`, and `IndexDocument`.

## Control Flow
The main existing-bucket test creates a bucket, checks default logging, persists logging, checks default accelerate and request-payment settings, writes accelerate and request-payment settings, writes website config, verifies website config, deletes it, and checks the expected missing-config error. The missing-bucket test calls every relevant get/put/delete path and expects `NoSuchBucket`. The HTTP-contract test uses awscurl to assert raw status codes and XML bodies for query-string APIs.

## State and Persistence
The tests persist bucket-level subresource configuration in the temporary RustFS server: logging target/prefix, accelerate status, request payer, and website config. Website config deletion is verified.

## Dependencies and Integration Points
The suite integrates AWS SDK S3 subresource APIs, raw SigV4 HTTP requests via awscurl, XML response formatting, and RustFS bucket metadata persistence. It uses `RustFSTestEnvironment` for lifecycle.

## Risks and Edge Cases
The HTTP-contract test is skipped if awscurl is unavailable, leaving only SDK-level coverage. These are compatibility endpoints and may not implement full AWS semantics beyond dummy/default behavior. Fixed bucket names require serial execution.

## Test Signals
Signals include default empty logging, persisted logging target/prefix, default `BucketOwner` payer, persisted `Requester`, default empty accelerate status, persisted `Suspended`, `NoSuchWebsiteConfiguration` after website deletion, `NoSuchBucket` for missing buckets, HTTP 200/204/404 status contracts, and XML content checks.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/bucket_logging_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/bucket_policy_check_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/bucket_policy_check_test.rs

## Purpose
This regression test verifies that bucket policies granting an authenticated user access are honored for list, put, get, and delete operations. It targets issue #1423 around authenticated-user policy evaluation.

## Important APIs, Types, and Functions
`create_user` calls the admin add-user endpoint using `awscurl_put` with JSON containing `secretKey` and enabled status. `create_user_client` builds an AWS S3 client with the new user's credentials. The test applies a bucket policy with `Principal: {"AWS": [user_access]}` and actions `s3:ListBucket`, `s3:GetObject`, `s3:PutObject`, and `s3:DeleteObject`.

## Control Flow
The test skips if awscurl is unavailable, starts RustFS, creates a bucket as admin, creates a user through the admin API, verifies the user cannot list before policy installation, installs the policy as admin, then verifies the user can put, list, get, and delete the target object.

## State and Persistence
State includes the temporary server data, an IAM-style user credential, a bucket, a bucket policy, and one object. User and policy metadata are persisted inside the test server's data directory.

## Dependencies and Integration Points
The test integrates admin user-management APIs, awscurl SigV4 requests, AWS SDK S3 clients with non-admin credentials, bucket policy authorization, and S3 object operations.

## Risks and Edge Cases
The test checks a single allow policy and does not cover deny precedence, wildcard principals, ARNs with account ids, policy variables, or conditions. It only asserts the initial no-policy call fails, not a specific error code.

## Test Signals
The strongest signal is the transition from denied list access before policy to successful put/list/get/delete after policy. Skipping when awscurl is unavailable is an explicit test-environment signal.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/bucket_policy_check_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/checksum_upload_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/checksum_upload_test.rs

## Purpose
This e2e suite verifies S3 checksum handling for direct uploads and multipart uploads. It covers `Content-MD5`, `x-amz-checksum-sha256`, multipart per-part SHA-256 checksums, and CRC64NVME full-object checksum consistency between direct and multipart uploads.

## Important APIs, Types, and Functions
Helpers create an S3 client, create buckets idempotently, calculate base64 Content-MD5, calculate base64 SHA-256, and calculate CRC64NVME using `rustfs_rio::Checksum`. Tests use AWS SDK types `ChecksumAlgorithm`, `ChecksumMode`, `CompletedMultipartUpload`, and `CompletedPart`.

## Control Flow
Direct-upload tests compute the checksum, upload an object with the corresponding checksum header, then GET and compare bytes. The SHA-256 multipart test creates a multipart upload with checksum algorithm, uploads two 6 MiB parts with part checksums, carries returned checksum values into completed parts, completes the upload, and verifies concatenated bytes. The CRC64NVME test uploads the same full content directly and as two multipart parts, then HEADs both objects with checksum mode enabled and expects the same full-object checksum.

## State and Persistence
Each test starts a RustFS server, creates a bucket, and writes one or two objects. Multipart tests persist upload state until completion and then persisted object metadata/checksum state.

## Dependencies and Integration Points
The suite integrates RustFS checksum validation, AWS SDK checksum fields, multipart upload assembly, `rustfs-rio` checksum implementation, object metadata reporting via HEAD, and body retrieval via GET.

## Risks and Edge Cases
The tests mainly cover successful checksum paths; they do not assert rejection of incorrect checksums. Large 6 MiB parts make the tests slower but satisfy S3 multipart minimums. CRC64NVME correctness depends on `rustfs-rio` being the same algorithm expected by the server.

## Test Signals
Signals include successful Content-MD5 put/get, successful SHA-256 put/get, successful multipart upload with SHA-256 part checksums and exact body assembly, and equal CRC64NVME reported for direct and multipart objects.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/checksum_upload_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/cluster_concurrency_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/cluster_concurrency_test.rs

## Purpose
This file tests cluster-wide correctness for conditional `PutObject` requests using `If-None-Match: *`. It ensures concurrent writers to different nodes do not all win the same object creation race.

## Important APIs, Types, and Functions
`conditional_put` sends `put_object().if_none_match("*")` and maps `PreconditionFailed` service errors to `Ok(false)`. `run_race_iteration` deletes the object, confirms it is absent, synchronizes client tasks with a `tokio::sync::Barrier`, and counts successful writes. `cleanup_object` best-effort deletes between iterations.

## Control Flow
The race test starts a four-node cluster, creates a shared bucket, builds one S3 client per node, and runs five race iterations. Each iteration launches one task per client after a barrier and records if more than one write succeeded. The basic test verifies a first conditional put succeeds and a second on the same key fails with `PreconditionFailed`.

## State and Persistence
State includes a temporary four-node cluster, one bucket, and short-lived race-test object keys. The race test cleans each key before and after the iteration.

## Dependencies and Integration Points
The file integrates cluster process management, distributed namespace locking or quorum behavior, AWS S3 conditional write semantics, SDK error metadata, and async task scheduling.

## Risks and Edge Cases
Race tests can be timing-sensitive; the barrier increases contention but cannot prove every possible interleaving. The race suite treats any iteration error as failure to avoid hiding cluster readiness issues. Fixed bucket names require serial tests.

## Test Signals
The primary signal is zero race detections across five iterations, exactly one success per healthy race, zero iteration errors, and explicit `PreconditionFailed` on the second basic conditional put.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/cluster_concurrency_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/common.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/common.rs

## Purpose
This is the shared support module for e2e tests. It manages RustFS server and cluster lifecycles, builds S3 and HTTP clients, finds/builds the RustFS binary, signs admin calls through awscurl, normalizes build-feature requests, initializes logging, and cleans temporary test storage.

## Important APIs, Types, and Functions
Constants define default credentials and a common bucket. `build_test_s3_config`, `local_http_client`, and S3 client factory methods configure path-style AWS SDK clients. `workspace_root`, `rustfs_binary_path`, `rustfs_binary_path_with_features`, feature normalization, source freshness checks, and binary feature stamps coordinate binary reuse/builds. `RustFSTestEnvironment` manages one server. `RustFSTestClusterEnvironment` manages multiple nodes and cluster volumes. Awscurl helpers cover GET, POST, PUT, DELETE, and STS form posts.

## Control Flow
Single-server startup optionally kills existing matching processes, builds command args, spawns the RustFS binary, and waits for readiness by requiring both TCP connectivity and successful `list_buckets`. Cluster startup allocates per-node ports and directories, builds a shared `RUSTFS_VOLUMES` string, spawns each node, waits for TCP readiness, then waits for S3 readiness on each node. Drops stop child processes and remove temp directories.

## State and Persistence
The module creates temporary directories under `/tmp`, stores child process handles, records cluster node address/data-dir state, writes binary feature stamp files next to the RustFS binary, and can build the RustFS binary into workspace `target`. Awscurl helpers do not persist state themselves.

## Dependencies and Integration Points
It integrates `aws-sdk-s3`, `aws-smithy-http-client`, `reqwest`, `tokio`, `tracing`, `uuid`, `walkdir`, local RustFS binaries, environment variables, and external `awscurl`. Almost every requested e2e file depends on this module.

## Risks and Edge Cases
`cleanup_existing_processes` uses `pkill -f` against address and temp-dir patterns, which is powerful and Unix-specific. Binary freshness scanning can be expensive over large workspaces. Readiness loops rely on `list_buckets`, so auth or routing regressions surface as startup failures. Feature stamp correctness matters when tests require optional protocol features.

## Test Signals
Inline unit tests cover feature normalization, `full` feature matching, and normalized binary feature-stamp matching. All e2e tests indirectly exercise server startup, readiness, client creation, process cleanup, and temp-dir cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/common.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/compression_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/compression_test.rs

## Purpose
This integration test verifies object compression round-trip behavior: RustFS stores a compressible object physically smaller than its logical content while HEAD and GET preserve the original object size and bytes.

## Important APIs, Types, and Functions
`generate_compressible_data` repeats a pattern to make a compressible byte vector. `find_part_files` recursively scans the bucket directory for physical `part.*` files containing the object key. `start_rustfs_with_compression` starts RustFS with `RUSTFS_COMPRESSION_ENABLED=true` and waits for TCP readiness.

## Control Flow
The test starts a compression-enabled server, creates a bucket, uploads a compressible object larger than `MIN_COMPRESSIBLE_SIZE`, checks HEAD `Content-Length`, scans physical part file sizes, asserts physical size is smaller than logical size, downloads the object, and checks length and byte equality.

## State and Persistence
State includes temporary RustFS object storage, a bucket, one object, and physical compressed part files under the temp directory. The test directly inspects on-disk storage layout.

## Dependencies and Integration Points
It integrates server environment configuration, S3 PutObject/HeadObject/GetObject, RustFS compression persistence, and local filesystem layout of object parts.

## Risks and Edge Cases
The test depends on current disk layout and `part.*` naming, so storage-layout refactors can break it even if S3 behavior remains correct. `start_rustfs_with_compression` waits for TCP only, unlike the stronger common readiness check. The environment variable name differs from archive compression tests, so config naming should be watched.

## Test Signals
Signals are original HEAD length, smaller summed physical part size, exact downloaded length, and byte-for-byte equality with uploaded data.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/compression_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/content_encoding_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/content_encoding_test.rs

## Purpose
This suite verifies S3 `Content-Encoding` metadata handling. It ensures normal encodings round-trip through PUT/GET/HEAD, and SigV4 streaming marker `aws-chunked` is stripped rather than persisted.

## Important APIs, Types, and Functions
The tests use `RustFSTestEnvironment`, AWS SDK `ByteStream`, and S3 `put_object`, `get_object`, and `head_object`. There are no custom helpers beyond logging and environment setup.

## Control Flow
The first test uploads text with `content_type("text/plain")` and `content_encoding("zstd")`, then asserts GET and HEAD both return `zstd` and the original content. The second uploads with `content_encoding("aws-chunked")` and asserts GET and HEAD return no content encoding. The third uploads with `content_encoding("aws-chunked,gzip")` and asserts only `gzip` is returned by GET and HEAD.

## State and Persistence
Each test creates a fresh server, bucket, object, and content-encoding metadata. Metadata normalization is persisted by the server and observed through GET/HEAD.

## Dependencies and Integration Points
The file integrates AWS SDK metadata fields, RustFS upload metadata normalization, S3 response metadata reporting, and issue-specific handling for SigV4 streaming uploads.

## Risks and Edge Cases
Only a few encoding values are tested. The parser behavior for whitespace, multiple effective encodings, case differences, and malformed encodings is not covered here. The tests use AWS SDK upload calls, not raw chunked streaming bodies.

## Test Signals
Signals include exact `zstd` roundtrip, `aws-chunked` being absent in GET/HEAD, `aws-chunked,gzip` becoming exactly `gzip`, and body integrity after metadata normalization.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/content_encoding_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/copy_object_metadata_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/copy_object_metadata_test.rs

## Purpose
This regression test verifies that self-copying an object with `MetadataDirective::Replace` updates metadata without losing or corrupting object data. It targets issue #2789.

## Important APIs, Types, and Functions
The test uses S3 `put_object`, `copy_object`, `head_object`, and `get_object`, with AWS SDK `MetadataDirective::Replace`. It relies on `RustFSTestEnvironment` for server lifecycle.

## Control Flow
The test uploads a JavaScript object with content type and two metadata keys, self-copies the object with replacement metadata that changes `mtime` and omits `stale`, verifies HEAD content length and metadata, verifies GET body equality, then self-copies again with empty replacement metadata and verifies omitted metadata stays absent while data remains readable.

## State and Persistence
State includes one bucket, one object, object body bytes, content type, and user metadata. CopyObject mutates metadata in place while preserving the underlying object payload.

## Dependencies and Integration Points
The test integrates CopyObject source handling, metadata replacement semantics, object metadata persistence, and read-after-copy data retrieval.

## Risks and Edge Cases
The test covers self-copy only, not cross-key or cross-bucket copies. It uses a small single-part object, so multipart copy behavior is not covered. It checks metadata removal and body preservation but not ETag/versioning interactions.

## Test Signals
Signals include content length equal to original length, updated `mtime`, removed `stale`, exact body after metadata replacement, absent metadata after empty replacement, and exact body after the second replacement.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/copy_object_metadata_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/data_usage_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/data_usage_test.rs

## Purpose
This ignored e2e regression test checks data-usage accuracy for issue #1012 by uploading 1000 objects and verifying the admin data-usage API reports at least that many objects globally and per bucket.

## Important APIs, Types, and Functions
The test imports `rustfs_data_usage::DataUsageInfo` to deserialize the admin response, uses AWS SDK `ByteStream` for uploads, and uses `awscurl_get` to call `/rustfs/admin/v3/datausageinfo`.

## Control Flow
When explicitly enabled, the test starts RustFS, creates `TEST_BUCKET`, uploads keys `obj-0000` through `obj-0999`, fetches admin data usage JSON, deserializes it, obtains the bucket usage entry, and asserts both total and bucket object counts are at least 1000.

## State and Persistence
State includes a test bucket with 1000 small objects and whatever data-usage snapshot/cache the server maintains. The test reads admin usage state rather than directly scanning storage.

## Dependencies and Integration Points
The file connects S3 object writes, admin API signing through awscurl, and the shared `rustfs-data-usage` response model. It is registered in `src/lib.rs` but marked `#[ignore]`.

## Risks and Edge Cases
Because it is ignored by default and requires awscurl, it is not part of normal test runs. The assertions allow counts greater than 1000, which tolerates extra accounting but would not detect overcounting. It does not wait or force a scanner cycle, so runtime behavior may depend on when data usage is updated.

## Test Signals
The key signal is absence of truncation: `objects_total_count >= 1000` and `bucket_usage.objects_count >= 1000` after uploading 1000 objects.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/data_usage_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/delete_object_no_content_length_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/delete_object_no_content_length_test.rs

## Purpose
This regression test verifies that a signed raw `DELETE Object?versionId` request with no request body and no `Content-Length` header succeeds. It protects against regressions returning `MissingContentLength` for valid empty DELETE requests.

## Important APIs, Types, and Functions
`signed_delete_without_content_length` constructs a SigV4-signed HTTP DELETE request with `UNSIGNED_PAYLOAD`, manually omits any `Content-Length`, writes raw bytes to a `TcpStream`, and reads the raw response with a timeout. Helpers parse status and body from raw HTTP text.

## Control Flow
The test starts RustFS, creates a bucket, uploads an object, enables versioning, lists versions to obtain the version id, sends the raw signed DELETE for that version, asserts HTTP 204 and empty body, then verifies the explicitly deleted version is no longer readable.

## State and Persistence
State includes a versioned bucket, a pre-versioning object version, the version id, and the delete operation that removes that specific version. Raw network state is controlled through a manually opened TCP stream.

## Dependencies and Integration Points
The test integrates S3 versioning, list-object-versions, raw HTTP parsing, SigV4 signing, request-body handling, and DeleteObject version semantics.

## Risks and Edge Cases
The raw response parser is intentionally simple and assumes a complete response after connection close. The test focuses on DELETE with version id; unversioned deletes or delete-marker creation without Content-Length are not separately covered here.

## Test Signals
Signals include raw request validation that no `Content-Length` header is present, HTTP 204 response, absence of `MissingContentLength`, empty response body, and failure to GET the deleted version id.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/delete_object_no_content_length_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/delete_objects_versioning_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/delete_objects_versioning_test.rs

## Purpose
This regression suite verifies that `DeleteObjects` on a versioned bucket creates delete markers that are immediately visible through `ListObjectVersions`. It targets issue #1878, where metadata updates could be temporarily invisible and listings could still report the old object version as latest.

## Important APIs, Types, and Functions
The tests use AWS SDK S3 `put_bucket_versioning`, `put_object`, `delete_objects`, and `list_object_versions`, with `BucketVersioningStatus::Enabled`, `VersioningConfiguration`, `Delete`, and `ObjectIdentifier`.

## Control Flow
The single-key test creates a bucket, enables versioning, uploads an object, verifies one latest version and no markers, calls plural `delete_objects` without a version id, captures the returned delete-marker version id, immediately lists versions, and checks one latest delete marker plus the original non-latest version. The multiple-key test uploads three keys, deletes all in a single request, immediately lists versions, and asserts every key has a latest delete marker.

## State and Persistence
State includes versioned bucket metadata, object versions, delete markers, and `xl.meta` visibility in the RustFS backend. The tests intentionally do not sleep between delete and list, making immediate metadata visibility the persistence property under test.

## Dependencies and Integration Points
The file integrates versioned delete semantics, batch delete response generation, metadata write/rename visibility, file-cache invalidation, and list-object-versions consistency.

## Risks and Edge Cases
The tests do not cover quiet delete mode, partial failures, explicit version-id deletes, suspended versioning, or many-key pagination. They use fixed bucket names and require serial execution.

## Test Signals
Signals include returned `delete_marker=true`, returned delete-marker version id, exactly one marker immediately after delete, marker `is_latest=true`, original version `is_latest=false`, and all three markers visible after a multi-key delete.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/delete_objects_versioning_test.rs -->
