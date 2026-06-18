# subset-b-008234 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/multipart_auth_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/multipart_auth_test.rs

## Purpose

This Rust end-to-end test module is a broad S3 compatibility regression suite for RustFS request handling around anonymous multipart-related APIs, browser-style POST object uploads, unsupported write-offset PUTs, and signed PUT archive auto-extraction. The opening module comment names anonymous multipart control API coverage, but the file has grown into a larger object-ingest conformance suite. It verifies that RustFS:

- Rejects anonymous multipart control operations such as AbortMultipartUpload, ListParts, CompleteMultipartUpload, and UploadPartCopy with HTTP 403.
- Rejects unauthenticated POST object uploads unless bucket policy explicitly grants anonymous `s3:PutObject`.
- Enforces POST policy coverage and exact/starts-with/content-length conditions for form fields that map to S3 object metadata, response behavior, storage class, encryption, checksum, object lock, tagging, bucket, and SigV4-like form fields.
- Persists accepted POST object fields into object state observable through `head_object`, `get_object`, `get_object_tagging`, `get_object_retention`, and `get_object_legal_hold`.
- Rejects unsupported headers such as `x-amz-write-offset-bytes` with MinIO-compatible `NotImplemented` XML without creating objects.
- Expands uploaded tar-family archives when snowball auto-extract headers are present, preserving or rejecting object attributes according to RustFS support.

The tests are integration tests rather than library code: they start a RustFS server, create buckets, mutate bucket policy/configuration, make SDK and raw HTTP requests, and assert on wire-level status codes, XML error codes, response headers, persisted object bytes, metadata, tags, encryption state, object lock state, version IDs, and archive-extracted keys.

## Important APIs, Helpers, and Types

- `RustFSTestEnvironment`, `init_logging`, and `local_http_client` come from `crate::common`. Each test starts an isolated RustFS server with `env.start_rustfs_server(vec![]).await?`, creates an AWS SDK S3 client with `env.create_s3_client()`, and uses the local reqwest client for raw unauthenticated or form requests.
- `encode_post_policy(conditions)` creates a base64 JSON POST policy with an expiration one hour in the future and the provided policy condition list. It is the shared setup for tests that need form-level policy validation.
- `sse_customer_key_md5_base64(key)` computes the base64 MD5 for SSE-C customer keys, used by POST and archive-extraction tests that need SSE-C headers.
- `make_tar(files, dirs)` builds in-memory tar archives using `tokio_tar`, supporting both file entries and directory entries.
- `build_pax_record` and `make_tar_with_pax_entry` construct PAX extended headers, including `minio.metadata.*`, `minio.versionId`, and file modification timestamps, for archive extraction tests.
- `gzip_bytes`, `zstd_bytes`, `bzip2_bytes`, and `xz_bytes` generate compressed tar payloads for `.tar.gz`, `.tgz`, `.tzst`, `.tbz2`, and `.txz` extraction coverage.
- `assert_s3_error_code(result, code)` normalizes AWS SDK `SdkError` assertions to service error metadata codes.
- `signed_raw_request` manually builds an HTTP request, sets `Host` and `x-amz-content-sha256: UNSIGNED-PAYLOAD`, signs it with `rustfs_signer::sign_v4`, then sends it through reqwest. It is used where the test must inspect the raw HTTP body instead of relying on AWS SDK error mapping.
- `allow_anonymous_put_object(client, bucket)` installs a bucket policy that grants public `s3:PutObject` on `arn:aws:s3:::bucket/*`, enabling anonymous POST/PUT tests to isolate form policy behavior from authorization denial.

Major imported dependencies include `aws_sdk_s3` request builders and S3 types, `reqwest::multipart` for browser POST forms, `rustfs_signer` for raw SigV4 signing, `tokio_tar` for archive creation, compression crates for archive formats, `chrono` for policy expiration, `base64` and `md5` for policy/SSE values, `uuid` for version ID checks, and `serial_test::serial` to keep tests from racing over local server resources.

## Control Flow

All tests follow a consistent integration-test flow:

1. Initialize logging.
2. Create and start a fresh `RustFSTestEnvironment`.
3. Create an S3 bucket through the admin SDK client.
4. Optionally configure bucket policy, bucket default encryption, bucket versioning, or object lock.
5. Build either an SDK request, a reqwest multipart form, or a raw signed HTTP request.
6. Send the request to RustFS.
7. Assert the immediate response status/error code.
8. When the request is expected to succeed, verify persisted object state through read-side S3 APIs.
9. When the request is expected to fail, often verify that no object was created.

The first test, `test_anonymous_multipart_control_apis_require_auth`, seeds a source object for copy, then sends raw anonymous DELETE, GET, POST XML, and PUT-with-copy-source requests with a dummy upload ID. Its control flow deliberately avoids creating a real multipart session, because the regression under test is auth gating before multipart state handling.

The POST object tests form the largest control-flow matrix. Basic cases verify required authorization, `success_action_status` 201 XML responses, `success_action_redirect` 303 responses with location query parameters, and the default 204 empty-body response. The policy tests then vary one form field at a time:

- A matching exact condition generally succeeds and is verified through persisted object state.
- A submitted `x-amz-*` or response-control field missing from policy conditions generally returns 403 `AccessDenied`.
- A submitted field covered by an exact policy condition but with a conflicting value generally returns 400 `InvalidPolicyDocument` and a diagnostic mentioning the field.
- `starts-with` and `content-length-range` conditions test prefix acceptance/rejection and object size limits.
- Invalid storage class values return `InvalidStorageClass`, not merely a policy mismatch.
- Certain fields are intentionally exempt or special-cased, such as ignored `x-ignore-*` fields and SSE-C fields accepted outside policy coverage.

The signed PUT/write-offset tests split into SDK and raw HTTP paths. SDK calls assert service metadata code `NotImplemented`; raw signed and anonymous HTTP calls assert the wire status and XML body, then verify rejected writes do not create objects. A follow-up anonymous plain PUT validates that the bucket policy remains capable of allowing normal unauthenticated writes when the unsupported header is absent.

The archive-extraction tests upload tar or compressed-tar payloads with snowball auto-extract headers. Their control flow is: synthesize an archive, put the archive object with metadata headers that request extraction, then fetch or head extracted objects under the requested or default key prefix. Negative cases assert `InvalidStorageClass`, `NotImplemented`, or `InvalidArgument` from the PUT itself.

## State and Persistence Behavior

This file heavily verifies persisted object metadata and bucket state:

- Anonymous POST success writes object bytes exactly as supplied in the `file` multipart part.
- POST response behavior does not replace object persistence: tests fetch the object after 201, 204, and redirect responses.
- SSE-S3 POST uploads persist `server_side_encryption = AES256`; bucket default SSE-S3 and default SSE-KMS are also observed on uploaded objects.
- SSE-KMS form fields are accepted through policy validation in some cases but ultimately rejected with `NotImplemented`, while default SSE-KMS for normal POST succeeds in the tested environment and archive extraction with bucket-default KMS is rejected.
- SSE-C POST and extraction paths require customer algorithm, key, and MD5 on subsequent `head_object`/`get_object` calls, proving encrypted object state is created.
- Storage class, cache control, content type, content disposition, content language, content encoding, website redirect location, `Expires`, user metadata, object tags, legal hold, retention mode/date, and version ID are read back from S3 APIs.
- Object lock tests create buckets with `object_lock_enabled_for_bucket(true)` before verifying retention and legal hold state.
- Archive extraction creates separate objects for tar entries and, by default, directory marker objects. The ignore-dirs option skips directory markers; ignore-errors skips invalid entries while retaining valid extracted keys.
- PAX metadata extraction maps `minio.metadata.project` and `minio.metadata.x-amz-meta-owner` onto S3 user metadata and preserves `minio.versionId` when bucket versioning is enabled.
- Rejected write-offset PUTs explicitly leave no object at the target key, while later normal PUTs can create the object.

The tests do not inspect RustFS internals or disk layout. Persistence is observed entirely through S3 API behavior against the local test server.

## Dependencies and Integration Points

The module integrates with:

- The e2e test harness in `crate::common` for server lifecycle, credentials, endpoint URL, and HTTP client construction.
- AWS SDK S3 operation builders for bucket creation, policy, encryption, versioning, PUT/GET/HEAD, tagging, object lock, and customized request mutation.
- Raw HTTP endpoints for anonymous multipart control API calls and browser-compatible POST forms.
- RustFS authorization and bucket policy evaluation through anonymous `s3:PutObject` policies.
- RustFS POST object policy parsing and validation, including exact-match JSON object conditions, array conditions like `starts-with` and `content-length-range`, field coverage requirements, duplicate field detection, and error mapping.
- RustFS object write pipeline for encryption, object lock, metadata, tags, storage class, redirect metadata, and checksum-related form fields.
- RustFS unsupported-feature mapping for SSE-KMS archive extraction and write-offset PUT headers.
- RustFS snowball/archive auto-extract support triggered by metadata headers including `x-amz-meta-snowball-auto-extract`, `x-amz-snowball-auto-extract`, `x-amz-meta-acme-snowball-prefix`, `x-amz-meta-rustfs-snowball-prefix`, `x-amz-meta-snowball-prefix`, `x-amz-meta-acme-snowball-ignore-dirs`, and `x-amz-meta-acme-snowball-ignore-errors`.

Because the tests use both SDK-level assertions and raw HTTP/body assertions, they exercise both high-level S3 compatibility and exact MinIO-compatible XML response shapes.

## Risks and Edge Cases

- The file is very large and has repeated setup logic. Adding new POST policy fields can easily miss one of the expected categories: allowed exact match, missing condition denial, mismatch invalid-policy error, and persisted readback.
- Tests are all marked `#[serial]`, which avoids shared local server contention but makes the suite expensive; failures may be time-consuming to reproduce.
- Some behavior is intentionally nuanced: SSE-C fields are allowed outside policy coverage, `x-ignore-*` fields are ignored, SSE-KMS may pass policy validation before runtime `NotImplemented`, and missing-vs-mismatched fields map to different error classes. These are compatibility traps for refactors.
- Raw signed requests depend on correct `Host`, unsigned payload handling, region string, and local credentials. Changes to signer behavior or endpoint URI formatting could break tests without any server behavior regression.
- Archive extraction relies on extension-based format detection; missing extensions and invalid compressed payloads are expected `InvalidArgument` cases.
- PAX metadata ordering comes from a `HashMap`, but the generated PAX records are independent key/value records, so the tests do not assert on archive byte determinism except in the archive ETag test, which uses a simple tar from `make_tar`.
- The archive ETag test expects the PUT response ETag to be the MD5 of the original archive upload, not a derived ETag for extracted objects.
- Bucket names are hard-coded and numerous. The fresh environment and serial execution are important to avoid bucket-name collisions.
- Several assertions accept multiple missing-object codes (`NoSuchKey`, `NoSuchVersion`, or `NotFound`) where the server may differ from AWS SDK normalization.

## Test Signals

Strong positive test signals include:

- HTTP status assertions for forbidden anonymous multipart controls, POST auth failures, POST policy failures, unsupported features, redirects, and successful 204/201 responses.
- XML body checks for `AccessDenied`, `InvalidPolicyDocument`, `InvalidStorageClass`, `NotImplemented`, `EntityTooLarge`, and `InvalidArgument`.
- Persisted object body equality after successful POST and extraction.
- `head_object` checks for encryption, storage class, content headers, website redirect, expiration, custom metadata, last-modified from tar mtime, and version ID from PAX.
- `get_object_tagging`, `get_object_retention`, and `get_object_legal_hold` checks for secondary object state.
- Negative persistence checks after rejected write-offset requests.
- ListObjects verification that ignore-errors extraction only stores the valid entry.

Notable coverage gaps visible from the file:

- Multipart initiation and authenticated multipart upload success paths are not covered here, only anonymous control API rejection with a dummy upload ID.
- POST policy expiration, malformed base64/JSON policy, and signed POST credential validation are not comprehensively covered beyond form-field mismatch conditions.
- Archive extraction is covered for several formats and attributes, but not for path traversal, symlink/hardlink handling, extremely large archives, or concurrent extraction.
- The tests verify local single-server behavior except where the shared harness itself may simulate more; cluster namespace lock behavior is covered separately in `namespace_lock_quorum_test.rs`.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/multipart_auth_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/namespace_lock_quorum_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/namespace_lock_quorum_test.rs

## Purpose

This Rust end-to-end test module is a cluster regression suite for namespace lock quorum behavior under concurrent same-key PUT overwrites. It verifies that RustFS does not surface false namespace-lock quorum failures during contention and that lock timeout/conflict failures are mapped to S3-compatible 503 `ServiceUnavailable` responses rather than 500 `InternalError`.

The tests start a four-node `RustFSTestClusterEnvironment`, create a bucket, seed an object, then issue simultaneous overwrites against the same key from multiple clients. They use a `tokio::sync::Barrier` to create real contention and classify results through AWS SDK service error metadata.

## Important APIs, Helpers, and Types

- `RustFSTestClusterEnvironment` from `crate::common` manages a multi-node RustFS test cluster, starts nodes, configures environment variables, creates buckets, and returns one S3 `Client` per node.
- `aws_sdk_s3::Client` is cloned into worker tasks and used for PUT/GET/DELETE operations.
- `bytes::Bytes` converts in-memory payloads into S3 request bodies.
- `tokio::sync::Barrier` synchronizes spawned writers so the PUT requests race on the same namespace lock.
- `serial_test::serial` keeps the cluster tests from running concurrently with other serial e2e tests.
- `tracing::{info, warn}` emits diagnostics for cluster setup, regression counts, and unexpected writer failures.
- `TestResult` is a local alias for `Result<(), Box<dyn std::error::Error + Send + Sync>>`.
- `put_object(client, payload, writer_id)` wraps `client.put_object().bucket(BUCKET).key(KEY).body(...).send()` and maps failures through `format_s3_error`.
- `format_s3_error(err, writer_id)` extracts service error code/message from `SdkError::ServiceError`; non-service SDK errors are formatted with debug output.

The constants under test are `BUCKET = "namespace-lock-quorum-bucket"` and `KEY = "thumb/79/concurrent-overwrite.jpg"`, giving both tests a shared path-like object key.

## Control Flow

`test_concurrent_cluster_overwrites_do_not_fail_namespace_lock_quorum`:

1. Initializes logging and creates a four-node cluster.
2. Sets `RUSTFS_OBJECT_LOCK_ACQUIRE_TIMEOUT` to `20`, intentionally focusing the regression on false quorum-loss errors rather than normal lock wait exhaustion.
3. Starts the cluster and creates the test bucket.
4. Creates clients for all cluster nodes and seeds an initial object.
5. Computes `writer_count = clients.len() * 2`, so a four-node cluster runs eight concurrent overwriters.
6. Builds a shared barrier and spawns one task per writer, rotating clients by `writer_id % clients.len()`.
7. Each task waits on the barrier, then overwrites the same key with a writer-specific payload.
8. The test joins all tasks, collects any service/SDK/join failures, logs them, and asserts that the failure list is empty.
9. It reads the final object and asserts that the body starts with `replacement payload from writer `, proving the final state is one of the successful concurrent writes.
10. It deletes the object before returning.

`test_concurrent_put_same_key_never_returns_500`:

1. Initializes logging and starts a four-node cluster.
2. Sets `RUSTFS_OBJECT_LOCK_ACQUIRE_TIMEOUT` to `3` to induce lock contention errors quickly.
3. Creates the bucket and seeds an initial object.
4. Runs `writer_count = clients.len() * 4`, so a four-node cluster runs sixteen concurrent PUTs.
5. Each spawned task waits on the barrier and then sends a direct `put_object`.
6. Results are classified into four atomic counters: successful writes, 503/service-unavailable errors, 500/internal errors, and unexpected errors.
7. Join failures count as unexpected errors.
8. The test logs total classified results and asserts that every writer was classified.
9. It asserts that unexpected errors are zero and, critically, that 500/InternalError count is zero.
10. It deletes the object before returning.

The two tests intentionally use different expectations: the first disallows all concurrent overwrite failures with a long timeout; the second allows successful writes or 503 contention failures but forbids 500s.

## State and Persistence Behavior

The tests mutate only S3-visible cluster state:

- A bucket is created in the test cluster.
- An initial object is written at the shared key.
- Multiple concurrent PUT operations overwrite that same key.
- The first test verifies final persisted body content after all overwrites complete.
- Both tests delete the key at the end.

No direct filesystem, lock-table, or quorum metadata is inspected. The namespace lock subsystem is validated through externally observable S3 results: absence of errors, final object contents, and service error codes under contention.

The cluster environment variable `RUSTFS_OBJECT_LOCK_ACQUIRE_TIMEOUT` is the key stateful configuration input. A longer timeout should let contended writers wait long enough to succeed, while a shorter timeout should surface lock contention as 503 without leaking internal 500s.

## Dependencies and Integration Points

This file integrates with:

- Cluster startup and lifecycle code in `RustFSTestClusterEnvironment`.
- RustFS namespace locking and distributed lock quorum logic.
- RustFS object PUT path for overwrites to an existing key.
- RustFS error mapping from namespace lock acquisition failures to S3 service errors.
- AWS SDK S3 service error metadata normalization.
- Tokio task scheduling and barriers to produce concurrent requests.

The comment above the second test documents the specific regression: `map_namespace_lock_error` previously wrapped lock timeout/conflict errors as a generic storage/IO error path, which fell through to `S3ErrorCode::InternalError` HTTP 500. This test locks in the expected mapping to 503 `ServiceUnavailable`.

## Risks and Edge Cases

- These are timing-sensitive concurrency tests. The barrier maximizes simultaneous start, but actual contention depends on runtime scheduling, machine load, and cluster performance.
- The first test sets a longer lock timeout to avoid ordinary contention failures, but a slow or overloaded environment could still make it flaky if PUTs exceed the timeout.
- The second test does not require at least one 503; if all writes succeed, the no-500 regression still passes. That is acceptable for error-mapping regression but weaker as a contention-generation signal.
- Both tests share fixed bucket/key constants and rely on serial execution plus fresh cluster state to avoid collisions.
- Error classification accepts both numeric and named codes for 500 and 503, which makes it robust to SDK/server metadata differences but assumes the service error metadata is populated.
- Cleanup only deletes the object, not the bucket; the cluster environment likely owns bucket cleanup when torn down.
- The tests do not verify which writer wins, only that the final body is from some writer payload.

## Test Signals

Strong signals:

- Multi-node cluster coverage with four nodes rather than a single embedded server.
- Same-key overwrite contention across multiple S3 clients.
- Barrier-synchronized start to increase lock collision probability.
- Explicit failure collection and logging for each writer in the no-failure quorum test.
- Atomic classification of success, 503, 500, and unexpected outcomes in the error-mapping test.
- Final object body readback proving successful overwrite persistence.

Coverage gaps:

- No assertion that 503 actually occurs in the second test, so a run with no lock contention still passes the no-500 check.
- No tests for concurrent deletes, multipart writes, copy operations, or cross-key lock independence.
- No direct validation of quorum repair/retry internals, only external S3 semantics.
- No bucket cleanup in the test body, relying on the cluster test harness for environment teardown.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/namespace_lock_quorum_test.rs -->
