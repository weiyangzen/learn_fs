# Research: subset-b-008232

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/existing_object_tag_policy_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/existing_object_tag_policy_test.rs

Purpose: this E2E module verifies IAM, bucket-policy, and STS session-policy evaluation for `s3:ExistingObjectTag` conditions, plus per-key authorization for `DeleteObjects`. It starts a real RustFS server, uses admin APIs through signed `awscurl`, creates temporary users/policies/buckets, and checks that tag changes immediately affect `GetObject` authorization.

Important APIs, types, and functions: `user_client()` and `sts_session_client()` build path-style AWS SDK S3 clients with static or session credentials. `assume_role_with_session_policy()` posts form-encoded STS `AssumeRole` requests through `awscurl_post_sts_form_urlencoded()`, then `parse_assume_role_credentials()` extracts temporary credentials from XML. Admin helpers wrap `/rustfs/admin/v3/add-user`, `/add-canned-policy`, `/set-user-or-group-policy`, and delete endpoints. Object helpers set initial tags through `PutObject.tagging()` and mutate tags through `PutObjectTagging`.

Control flow: each `#[tokio::test]` initializes logging, skips when `awscurl` is unavailable, starts `RustFSTestEnvironment`, creates unique names with `Uuid`, applies identity or bucket/session policy JSON, writes tagged objects, verifies allowed reads, flips `security=public` to `security=private`, and asserts denial. The delete-objects regression creates two keys, assumes a session with an allowed-prefix `s3:DeleteObject` policy, calls one `DeleteObjects` request containing both keys, and validates one `Deleted` entry plus one `AccessDenied` error.

State and persistence: state is stored in RustFS IAM users, canned policies, bucket policy documents, STS session credentials, object tags, and object data. Cleanup removes objects, buckets, users, and canned policies best-effort, but failure before cleanup can leave temporary server-side IAM state in the test environment.

Dependencies and integration points: depends on `crate::common` server/admin helpers, `aws_sdk_s3`, `awscurl`, STS SigV4 form POST support, `serial_test`, `uuid`, and RustFS IAM/policy/tagging internals. The tests exercise the S3 data plane, admin control plane, and STS endpoint together.

Risks: XML parsing is string-based and assumes un-namespaced STS response tags. `denied.is_err()` does not validate exact error code except in the multi-delete path. Tests are serial because they mutate global IAM-like state, and they require external `awscurl`. Cleanup is not guarded by a `Drop` helper, so early assertions can skip teardown.

Test signals: passing tests prove existing object tag conditions are re-evaluated for IAM, bucket, and STS session policies; bucket policies can grant tag-gated reads to a user without identity policy; STS inline policies restrict credentials; and multi-object delete reports mixed per-key success/failure without deleting denied keys.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/existing_object_tag_policy_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/group_delete_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/group_delete_test.rs

Purpose: this module contains ignored, real-server E2E regression tests for RustFS group management around issue #2028. It verifies group deletion rules, propagation of group-attached policies to users without explicit user policies, and cache/backend consistency after deleting a group member user.

Important APIs, types, and functions: `create_user_s3_client()` builds an AWS SDK S3 client for a created IAM user. Tests call admin endpoints through `awscurl_put()`, `awscurl_delete()`, and `awscurl_get()`: `/add-user`, `/update-group-members`, `/set-user-or-group-policy`, `/group/{name}`, `/group?group=...`, and `/remove-user`.

Control flow: `test_delete_group_requires_empty_membership()` creates a user, adds it to a group, asserts deleting the non-empty group fails, removes the member, deletes the empty group, and verifies lookup fails. `test_user_with_only_group_gets_group_policies()` creates a canned ListAllMyBuckets policy, creates a user with no direct policy, adds the user to a group, attaches the policy to that group, and confirms the user can list buckets. `test_delete_group_after_deleting_user()` creates a sole member, deletes the user, then verifies deleting the now-empty group succeeds.

State and persistence: the tests mutate IAM users, groups, group membership indexes, group policy attachments, and cached membership state inside a temporary RustFS server. They do not perform comprehensive cleanup because each test uses isolated server state, but names are static inside the module and require serial execution.

Dependencies and integration points: depends on `RustFSTestEnvironment`, awscurl admin helpers, AWS SDK S3 list-buckets, and `serial_test`. The tests integrate directly with RustFS admin API semantics, group membership persistence, policy evaluation, and any in-memory membership cache.

Risks: all tests are `#[ignore]`, so normal `cargo test` will not run them. Static user/group/policy names are safe only because the environment is isolated and tests are serial. The group-policy test asserts one positive action but not negative controls for unauthorized actions. Failure paths can leave admin state alive until environment cleanup.

Test signals: useful signals are non-empty group deletion rejection, empty group deletion success, failed group lookup after deletion, group-only user authorization through group policy, and successful group deletion after deleting the sole member without stale-cache rejection.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/group_delete_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/head_object_consistency_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/head_object_consistency_test.rs

Purpose: this E2E regression test verifies that `HeadObject` is consistent after both simple `PutObject` and completed multipart uploads, and that presigned HEAD URLs succeed against the local RustFS server.

Important APIs, types, and functions: `list_contains_key()` scans `ListObjectsV2Output.contents()` for a key. The test uses `RustFSTestEnvironment`, AWS SDK S3 `put_object`, `get_object`, `list_objects_v2`, `head_object`, multipart builders `CompletedMultipartUpload` and `CompletedPart`, `PresigningConfig`, and `local_http_client()` for a raw HEAD request to the presigned URI.

Control flow: the test starts a server, creates a fixed bucket, writes a normal object, confirms `GetObject` and `ListObjectsV2` can see it, then calls `HeadObject`. It creates a multipart upload for another key, uploads one part, completes it using the returned ETag, confirms `GetObject` and `ListObjectsV2` see the completed key, then calls `HeadObject` for that key. Finally it presigns a HEAD request for the first key and verifies the raw HTTP status is success before deleting objects and bucket.

State and persistence: persistent state is limited to two objects and multipart upload metadata in the test bucket. The test intentionally checks data-plane/listing visibility before HEAD, so a HEAD failure after those checks indicates a metadata lookup path inconsistency rather than write failure.

Dependencies and integration points: depends on AWS SDK presigning, local reqwest client support, RustFS S3 object, multipart, list, head, and SigV4 presigned request handling. `serial_test` avoids shared fixed bucket conflicts.

Risks: fixed bucket/key names require serial isolation. Multipart uses a single small part, which may not cover all multi-part layout behavior even though it covers completed MPU metadata. The presigned check only validates success status, not headers.

Test signals: success demonstrates HEAD visibility after simple writes and completed MPU, list/head consistency for both key types, and working presigned HEAD authentication over the raw HTTP path.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/head_object_consistency_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/head_object_range_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/head_object_range_test.rs

Purpose: this compact E2E regression test ensures `HeadObject` advertises byte-range support through the `Accept-Ranges: bytes` response metadata.

Important APIs, types, and functions: the test uses `RustFSTestEnvironment`, AWS SDK S3 `put_object`, `head_object`, `delete_object`, and the constants `RANGE_HEAD_BUCKET`, `RANGE_HEAD_KEY`, and `ACCEPT_RANGES_BYTES`.

Control flow: the test starts a RustFS server, creates a bucket, uploads a small binary object, issues `HeadObject`, asserts `head.accept_ranges() == Some("bytes")`, deletes the object, deletes the bucket, and stops the server.

State and persistence: state is one bucket and one object. No long-lived state should remain after cleanup. The tested behavior is response-header metadata derived from object capability rather than object content.

Dependencies and integration points: depends on AWS SDK S3 head response mapping, RustFS HEAD object implementation, and the common environment helpers. `serial_test` protects the fixed bucket name.

Risks: the test checks only positive behavior for an existing object and does not inspect raw HTTP casing or other HEAD headers. Fixed names require isolation. A missing cleanup on assertion failure can leave the temporary bucket until environment teardown.

Test signals: a passing run confirms AWS SDK observes `AcceptRanges` as `bytes`, which means RustFS emits the expected range-advertisement header for normal objects.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/head_object_range_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/heal_erasure_disk_rebuild_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/heal_erasure_disk_rebuild_test.rs

Purpose: this module tests erasure-set healing by deliberately wiping or replacing disk directories and verifying RustFS rebuilds object metadata and preserves readable object bodies. It covers single-node runtime wipe auto-heal, single-node restart plus admin deep heal, and multi-node remote disk replacement.

Important APIs, types, and functions: `has_file_under()` recursively detects any file in a disk path. `object_metadata_exists_on_disk()` checks `bucket/key/xl.meta`. `assert_object_body()` reads an object through S3 and compares bytes. Tests use `RustFSTestEnvironment`, `RustFSTestClusterEnvironment`, `start_rustfs_server_with_env()`, cluster node stop/start helpers, `execute_awscurl()` for admin heal/status, `HashSet` tracking of rebuilt keys, and `tokio::time::{sleep, timeout}`.

Control flow: the runtime-wipe test creates four disk dirs, starts RustFS with three explicit paths and one implicit path plus a short heal interval, uploads several objects, wipes `disk0` while the server keeps running, then polls until every `xl.meta` reappears and `format.json` is restored. The deep-heal test writes objects including non-ASCII/symbol keys, stops the server, wipes `disk0`, restarts, posts a recursive heal request, and polls for metadata rebuild before final body checks. The cluster test starts four nodes, writes one object, stops node 1, wipes its data dir, writes another object while the node is down, restarts it, checks background-heal status accepts no explicit content length, posts admin heal, and polls until both keys are rebuilt on the replaced remote disk.

State and persistence: these tests manipulate real filesystem state under temporary disk roots, RustFS erasure metadata (`xl.meta`), `.rustfs.sys/format.json`, object shards, and cluster/node lifecycle. Environment variables tune bypass disk checks, heal intervals, scanner/heal enablement, object counts, and timeouts.

Dependencies and integration points: depends on local filesystem permissions, RustFS erasure coding layout, admin heal API, cluster harness, AWS SDK object operations, and `awscurl` execution. It integrates scanner/background heal, foreground admin heal, disk-format restoration, and object read quorum.

Risks: tests are slow and timing-sensitive, with default polling windows of 45, 60, and 90 seconds. Directly checking `xl.meta` couples the tests to storage layout. Runtime disk removal can race with background IO. Non-ASCII key coverage is valuable but depends on platform path handling. Admin heal acceptance is checked, but detailed heal progress response semantics are not parsed.

Test signals: passing tests show objects remain readable during/after disk loss, wiped disks regain `xl.meta` for every expected key, format metadata is restored after runtime wipe, admin deep heal can rebuild after restart, remote replacement heals both pre-outage and outage-written objects, and background-heal status does not fail with `MissingContentLength`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/heal_erasure_disk_rebuild_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/bucket_default_encryption_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/bucket_default_encryption_test.rs

Purpose: this KMS E2E module verifies bucket default encryption behavior for SSE-S3 and SSE-KMS, including normal `PutObject`, multipart upload inheritance, explicit request overrides, and default KMS key population when a bucket encryption rule omits a key ID.

Important APIs, types, and functions: tests use `LocalKMSTestEnvironment`, `ServerSideEncryptionConfiguration`, `ServerSideEncryptionRule`, `ServerSideEncryptionByDefault`, `ServerSideEncryption`, S3 bucket encryption APIs, object APIs, multipart APIs, and `TEST_BUCKET`.

Control flow: each test starts RustFS with local KMS and a generated default key, sleeps briefly for initialization, creates the test bucket, installs a bucket encryption configuration, performs an object or multipart operation without explicit encryption where inheritance is expected, and validates response/get/head encryption metadata. The override test configures default SSE-S3 but uploads with explicit SSE-KMS and asserts the explicit key wins. The no-key-ID test writes an SSE-KMS rule with an empty key ID and verifies `GetBucketEncryption` returns the configured default key.

State and persistence: state includes local KMS key files, bucket encryption configuration, object encryption metadata, KMS key IDs, and multipart upload metadata. Cleanup mostly relies on temporary environment drop; explicit bucket deletion is not consistently called in this file.

Dependencies and integration points: depends on KMS startup flags from `LocalKMSTestEnvironment`, AWS SDK bucket-encryption model types, RustFS bucket encryption persistence, KMS default key resolution, object encryption pipeline, and multipart completion metadata propagation.

Risks: the fixed `TEST_BUCKET` and serial execution are required. Initialization uses fixed sleeps instead of readiness polling. One TODO notes explicit “no encryption” override is skipped. Some assertions use `unwrap()` for KMS key IDs, so missing headers produce panics rather than diagnostic errors.

Test signals: success means bucket defaults are applied to PUT and create-multipart paths, SSE-KMS key IDs survive PUT/GET and multipart completion, explicit SSE-KMS overrides bucket SSE-S3, and empty SSE-KMS bucket rules are normalized to the local default key.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/bucket_default_encryption_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/common.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/common.rs

Purpose: this is the shared support library for RustFS KMS E2E tests. It manages local and Vault KMS test environments, admin KMS API calls, key-file creation, common SSE-S3/SSE-KMS/SSE-C assertions, multipart encryption workflows, and utility constants.

Important APIs, types, and functions: constants define `TEST_BUCKET`, Vault address/token/transit path/default key, and `RUSTFS_TEST_VAULT_BIN`. Admin helpers include `configure_kms()`, `start_kms()`, `get_kms_status()`, `create_default_key()`, and `test_kms_key_management()`. Encryption helpers include `sse_customer_key_md5_base64()`, `test_sse_c_encryption()`, `test_sse_s3_encryption()`, `test_sse_kms_encryption()`, `test_error_scenarios()`, `EncryptionType`, `MultipartTestConfig`, `test_multipart_upload_with_config()`, `create_sse_c_config()`, and `test_all_multipart_encryption_types()`. Environment types are `VaultTestEnvironment` and `LocalKMSTestEnvironment`.

Control flow: local KMS tests create a temp key directory, write a JSON `.key` file with generated AES-256 material, and start RustFS with `--kms-enable --kms-backend local --kms-key-dir --kms-default-key-id`. Vault tests spawn `vault server -dev`, wait for TCP plus health readiness, enable transit, create the transit key, start RustFS, configure the Vault backend via admin API, and start KMS. Multipart helper builds deterministic data, creates an upload with the selected encryption mode, uploads all parts with SSE-C headers when needed, completes the upload, downloads it, checks encryption headers, and byte-compares content.

State and persistence: persistent test state is local KMS key JSON under the environment temp directory, spawned Vault process state, RustFS KMS runtime configuration, bucket/object metadata, multipart upload IDs and ETags, and customer key/MD5 values. `VaultTestEnvironment::drop()` kills the Vault child process.

Dependencies and integration points: depends on `crate::common` awscurl and HTTP helpers, `aws_sdk_s3`, `base64`, `md5`, `rand`, `chrono`, `tokio::fs`, `reqwest`, a Vault binary when Vault tests are run, and RustFS admin KMS endpoints.

Risks: local key-file format is manually constructed and coupled to backend internals. Vault uses a hard-coded dev token and fixed port, so parallel runs conflict. Several helpers skip when `awscurl` is absent, hiding KMS admin coverage in normal environments. Fixed sleeps and readiness loops may be flaky under load. Log strings include non-ASCII symbols while most source is ASCII.

Test signals: this file enables most KMS coverage; signals include successful KMS configure/start/status, create/describe/list keys, correct SSE headers, wrong SSE-C key rejection, Vault process readiness, multipart data integrity across encryption modes, and environment cleanup through process termination.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/common.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/encryption_metadata_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/encryption_metadata_test.rs

Purpose: this module validates externally visible metadata and physical storage behavior for managed encryption. It ensures SSE-S3/SSE-KMS headers appear on HEAD/GET, internal RustFS encryption metadata is not exposed as user metadata, copies preserve encryption, multipart encrypted uploads decrypt correctly, and plaintext is not visible in stored files.

Important APIs, types, and functions: `assert_managed_encryption_metadata_hidden()` checks user metadata for hidden internal keys such as `x-rustfs-encryption-key` and IV/context fields. `assert_storage_encrypted()` walks the storage root with a `VecDeque`, reads candidate files whose paths contain bucket/key fragments, and fails if plaintext bytes appear. Tests use `LocalKMSTestEnvironment`, bucket encryption builders, `ByteStream`, multipart builders, `copy_object`, `head_object`, and `get_object`.

Control flow: the SSE-S3 test sets bucket default AES256, uploads without explicit encryption, heads the object, checks the SSE header, hides internal metadata, and scans disk. The SSE-KMS/copy test sets bucket default KMS key, uploads, heads source, copies to a new key, heads destination, downloads the copy, and scans both source and destination storage. The multipart test configures SSE-KMS default encryption, uploads two 5 MiB patterned parts, completes the upload, checks HEAD metadata, downloads combined bytes, and scans storage for plaintext.

State and persistence: state includes local KMS keys, bucket encryption config, object metadata, copied-object metadata, multipart metadata, and files under the temporary RustFS storage root. The disk scanner observes implementation storage files directly.

Dependencies and integration points: depends on local KMS, AWS SDK S3 encryption headers, RustFS copy semantics, metadata projection, multipart encryption persistence, and the on-disk object layout.

Risks: scanning for plaintext is heuristic and path-filtered; compressed, chunked, or differently named storage could evade or falsely fail the scan. It couples tests to temp-dir storage internals. Fixed sleeps for KMS readiness can be flaky. It does not validate exact internal metadata contents, only that selected keys are absent from user metadata.

Test signals: passing tests show managed encryption metadata remains internal, HEAD reports expected SSE mode/key ID, copy preserves SSE-KMS configuration and payload, multipart encrypted data decrypts correctly, and plaintext bytes are not found in relevant stored files.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/encryption_metadata_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/kms_comprehensive_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/kms_comprehensive_test.rs

Purpose: this module composes broad KMS workflows over the local KMS backend: all single-object encryption modes, key management APIs, multipart encryption modes, mixed workloads, stress-size multipart uploads, key isolation, concurrent operations, and a simple performance benchmark.

Important APIs, types, and functions: it imports common helpers `test_sse_s3_encryption()`, `test_sse_kms_encryption()`, `test_sse_c_encryption()`, `test_kms_key_management()`, `test_all_multipart_encryption_types()`, `test_multipart_upload_with_config()`, `MultipartTestConfig`, `EncryptionType`, `create_sse_c_config()`, and `sse_customer_key_md5_base64()`. Local setup uses `LocalKMSTestEnvironment`.

Control flow: each `#[tokio::test]` starts local KMS, sleeps for initialization, creates `TEST_BUCKET`, and runs a scenario. The full workflow runs single-object helpers, admin key management, all multipart modes, and mixed multipart sizes/modes. Stress uploads 60 MiB-class objects for SSE-S3/SSE-KMS/SSE-C. Key isolation uploads with distinct SSE-C keys and verifies a wrong key fails. Concurrent operations spawn multiple multipart encrypted uploads with cloned S3 clients. The performance benchmark times representative small/medium/large SSE-S3 multipart uploads and logs throughput.

State and persistence: state is temporary local KMS key material, bucket/object data, multipart uploads and ETags, SSE-C customer keys, spawned tasks, and timing measurements. Tests delete the bucket after success, but failures rely on environment teardown.

Dependencies and integration points: depends heavily on the shared KMS common module, AWS SDK S3, tokio task scheduling, KMS admin endpoints, local KMS backend, and RustFS multipart encryption/decryption paths.

Risks: these tests are expensive and serial, and fixed sleeps can cause flakiness. Performance benchmark logs throughput but has no threshold, so it is informational rather than a regression gate. Concurrent tests run under `serial` at the test level but perform internal parallel uploads, stressing shared local KMS state. Large allocations may be memory-heavy.

Test signals: useful signals are end-to-end success across all encryption types, key API success, byte-exact multipart downloads for mixed sizes, wrong-key rejection, successful concurrent encrypted uploads, and no panics under larger object sizes.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/kms_comprehensive_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/kms_edge_cases_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/kms_edge_cases_test.rs

Purpose: this module exercises KMS encryption boundary conditions and security checks: zero-byte and single-byte objects, exact 5 MiB multipart part size, invalid SSE-C inputs, concurrent encrypted uploads, and customer-key isolation.

Important APIs, types, and functions: uses `LocalKMSTestEnvironment`, `sse_customer_key_md5_base64()`, `ServerSideEncryption`, base64 encoding, `md5::compute`, `Arc`, `Semaphore`, tokio spawned tasks, and direct AWS SDK S3 calls.

Control flow: zero-byte and single-byte tests upload/download with SSE-S3/SSE-KMS/SSE-C and assert headers/body length. The multipart boundary test creates an SSE-S3 multipart upload, uploads one exact 5 MiB part, completes it, and verifies bytes. Invalid-key testing rejects a short SSE-C key, mismatched MD5, and GET of an SSE-C object without the key. Concurrent encryption spawns five uploads alternating SSE-S3, SSE-KMS, and SSE-C, requiring most to succeed. Key validation uploads the same plaintext under two SSE-C keys, verifies both decrypt with their own key, and rejects a cross-key read.

State and persistence: state includes temporary local KMS key files, bucket objects, multipart upload state, generated SSE-C keys/MD5 values, and concurrent task outcomes. Buckets are deleted after successful tests.

Dependencies and integration points: depends on AWS SDK SSE-C header behavior, RustFS SSE-C validation, local KMS availability, multipart minimum-size enforcement, tokio concurrency, and error mapping for bad encryption requests.

Risks: the invalid short-key MD5 uses hex MD5 rather than base64, so that assertion may fail for multiple reasons. The concurrent test permits one failure, reducing strictness. Fixed sleeps gate KMS readiness. Tests check error existence more often than precise S3 error code.

Test signals: passing tests indicate small/empty encrypted object handling works, exact minimum multipart part encryption succeeds, invalid SSE-C inputs are rejected, SSE-C keys are required for reads, concurrent mixed encryption is mostly stable, and wrong customer keys cannot decrypt data.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/kms_edge_cases_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/kms_fault_recovery_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/kms_fault_recovery_test.rs

Purpose: this module tests local KMS resilience under key-directory/key-file faults, multipart interruption, and rapid request load. It focuses on graceful failure/recovery rather than exact failure modes when keys may be cached.

Important APIs, types, and functions: uses `LocalKMSTestEnvironment`, local filesystem `fs::rename`, `fs::copy`, `fs::write`, `fs::remove_file`, AWS SDK `ServerSideEncryption`, multipart create/upload/abort/complete APIs, tokio sleeps/spawns, and `TEST_BUCKET`.

Control flow: the directory-unavailable test uploads an encrypted object, renames the key directory away, attempts another upload expecting failure or cached success, restores the directory, uploads again, and verifies the original object remains readable. The corrupted-key test backs up the default key file, overwrites it with invalid bytes, attempts encrypted upload, restores the key, and verifies new uploads work. The multipart-interruption test uploads two encrypted parts, aborts the upload, asserts completion of the aborted upload fails, then starts and completes a new encrypted multipart upload with all parts. The resource-constraints test launches ten rapid SSE-S3 uploads and requires at least seven successes.

State and persistence: state includes local KMS key directory contents, backup key files, bucket objects, aborted multipart upload records, completed multipart object data, and task results. Fault tests mutate files under the temp KMS directory while RustFS is running.

Dependencies and integration points: depends on local KMS file-backed key loading/cache behavior, RustFS encryption paths, multipart abort semantics, and S3 object readability after KMS faults.

Risks: comments explicitly allow cached keys to make “failure” attempts succeed, so these are recovery smoke tests more than deterministic negative tests. Filesystem rename behavior may differ across platforms. Fixed waits may not match cache invalidation or watcher timing. Rapid upload threshold allows partial failure.

Test signals: useful signals are server responsiveness during key material faults, successful encrypted upload after restoration, original encrypted object readability, inability to complete aborted uploads, successful retry with a fresh upload ID, byte-exact final multipart data, and acceptable success rate under bursts.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/kms_fault_recovery_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/kms_local_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/kms_local_test.rs

Purpose: this file provides local-backend KMS E2E tests for admin status/key APIs, SSE-C key isolation, SSE-S3 large object upload, and multipart uploads under SSE-S3/SSE-KMS/SSE-C.

Important APIs, types, and functions: tests use `LocalKMSTestEnvironment`, `get_kms_status()`, `skip_if_kms_admin_tool_unavailable()`, `test_kms_key_management()`, `test_sse_c_encryption()`, `sse_customer_key_md5_base64()`, and local helper functions `test_multipart_upload_with_sse_s3()`, `test_multipart_upload_with_sse_kms()`, `test_multipart_upload_with_sse_c()`, and disabled `test_large_multipart_upload()`.

Control flow: `test_local_kms_end_to_end()` starts local KMS, checks KMS status, creates a bucket, runs key management and SSE-C only, then exits after a debugging-era early path with SSE-S3/SSE-KMS/error scenarios commented out. Key isolation uploads two SSE-C objects with different keys and verifies wrong-key access fails. Large-file test uploads/downloads a 1 MiB SSE-S3 object. Multipart test runs 2-part 5 MiB uploads for SSE-S3, SSE-KMS, and SSE-C, verifying headers and byte equality; the larger 30 MiB streaming helper remains dead code.

State and persistence: state includes local key files, KMS status/configuration, bucket objects, SSE-C key material, multipart upload IDs/ETags, and object metadata. Successful tests delete `TEST_BUCKET`.

Dependencies and integration points: depends on local KMS startup flags, admin KMS API availability through `awscurl`, AWS SDK S3 encryption headers, multipart encryption/decryption, and common test environment cleanup.

Risks: the main end-to-end test is intentionally incomplete, with SSE-S3/SSE-KMS/error checks commented out. Several log messages include “CLAUDE TEST DEBUG”, indicating temporary diagnostics in committed tests. Large multipart streaming coverage is disabled. Some tests use panic-style `expect()` instead of returning structured errors.

Test signals: current passing signals cover local KMS startup/status, key management, SSE-C single-object encryption, customer-key isolation, 1 MiB SSE-S3 object integrity, and two-part multipart encryption for SSE-S3/SSE-KMS/SSE-C. They do not fully signal local KMS SSE-S3/SSE-KMS single-object behavior from the nominal end-to-end test.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/kms_local_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/kms_vault_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/kms_vault_test.rs

Purpose: this module mirrors KMS E2E coverage against a Vault Transit backend. It validates Vault bootstrap, RustFS KMS configuration/startup, encryption modes, multipart behavior, key isolation, and Vault-backed key CRUD semantics.

Important APIs, types, and functions: `VaultKmsTestContext` wraps `VaultTestEnvironment` and exposes `base_env()` and `s3_client()`. Tests use shared helpers `get_kms_status()`, `start_kms()`, `test_kms_key_management()`, `test_sse_c_encryption()`, `test_sse_s3_encryption()`, `test_sse_kms_encryption()`, `test_error_scenarios()`, `test_all_multipart_encryption_types()`, and `sse_customer_key_md5_base64()`. `test_vault_kms_key_crud()` directly calls admin KMS key create/describe/list/delete endpoints.

Control flow: context creation starts a dev Vault process, enables transit, creates the default transit key, starts RustFS, configures Vault Transit KMS, starts the KMS service, and waits briefly. The end-to-end test checks status, creates a bucket, runs key management plus SSE-C/SSE-S3/SSE-KMS/error helpers, and deletes the bucket. Other tests cover SSE-C key isolation, 1 MiB SSE-S3 upload/download, all multipart encryption types, and CRUD including tag preservation, pending-deletion state, force delete, and final not-found behavior.

State and persistence: state spans a child Vault dev process, Vault transit mount/key state, RustFS KMS config, temporary bucket/object data, KMS key metadata/tags/deletion state, and SSE-C keys. The Vault process is killed by `VaultTestEnvironment::drop()`.

Dependencies and integration points: requires a Vault binary (`vault` or `RUSTFS_TEST_VAULT_BIN`), fixed localhost port 8200, awscurl for admin calls, RustFS Vault Transit backend support, AWS SDK S3, and serial execution.

Risks: fixed Vault port and dev token prevent parallel Vault tests. Tests skip when awscurl is absent but not when Vault is absent; missing Vault fails context setup. Fixed sleeps may be insufficient under slow startup. Key CRUD asserts exact response shape and state names, which is valuable but tightly coupled to admin API schema.

Test signals: passing tests show Vault Transit can be configured and started, KMS status is queryable, encryption modes work over Vault-backed keys, SSE-C isolation remains enforced, multipart encryption works across modes, key tags survive create/list/describe, delete transitions to `PendingDeletion`, and force delete removes the key.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/kms_vault_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/mod.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/mod.rs

Purpose: this module is the test-only KMS module registry for the RustFS E2E crate. It documents that KMS tests cover both Local and Vault backends and conditionally includes all KMS test submodules under `#[cfg(test)]`.

Important APIs, types, and functions: it exposes `pub mod common` for test helpers and includes private modules `kms_local_test`, `kms_vault_test`, `kms_comprehensive_test`, `multipart_encryption_test`, `kms_edge_cases_test`, `kms_fault_recovery_test`, `test_runner`, `bucket_default_encryption_test`, and `encryption_metadata_test`.

Control flow: there is no runtime logic. During test builds, Rust compiles the shared KMS helpers and every listed test module; in non-test builds, none of these modules are included.

State and persistence: no state is stored here. It controls compilation reachability for KMS test state owned by child modules.

Dependencies and integration points: integrates with the crate root `lib.rs`, Rust `#[cfg(test)]` conditional compilation, and Rust module resolution. `common` is public only within the test build so sibling and possibly external test code can reuse it.

Risks: adding a KMS test file without listing it here excludes it from test compilation. Conversely, listing a module with expensive tests means it is compiled even when tests are filtered. This file does not apply feature flags for Vault/local availability; runtime tests must handle skips.

Test signals: successful compilation of this module proves all named KMS test files resolve. Actual behavioral signals come from child module tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/multipart_encryption_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/multipart_encryption_test.rs

Purpose: this module provides stepwise local-KMS tests for multipart encryption, starting with simple single-object encryption, then unencrypted multipart baseline, SSE-S3 multipart, large streaming-style SSE-S3 multipart, and SSE-KMS/SSE-C multipart modes.

Important APIs, types, and functions: it uses `LocalKMSTestEnvironment`, `sse_customer_key_md5_base64()`, `TEST_BUCKET`, AWS SDK multipart builders, `ServerSideEncryption`, and local `EncryptionType` enum with `SSEKMS` and `SSEC`. `test_multipart_encryption_type()` is the shared helper for SSE-KMS and SSE-C multipart uploads.

Control flow: each step starts local KMS and a bucket. Step 1 writes a small SSE-S3 object and verifies PUT/GET headers and bytes. Step 2 performs a two-part unencrypted upload as a baseline. Step 3 creates a two-part SSE-S3 upload, optionally validates create response SSE header, checks HEAD metadata, downloads, and compares data. Step 4 uploads three 6 MiB SSE-S3 parts to cross encryption chunk boundaries, then validates every byte. Step 5 uses the helper to test two-part SSE-KMS and SSE-C multipart uploads; SSE-C adds customer headers on create, every part, and GET.

State and persistence: state includes local KMS key files, temporary bucket data, multipart upload IDs, part ETags, encryption headers, and deterministic byte patterns. Buckets are deleted after successful steps.

Dependencies and integration points: depends on local KMS, RustFS multipart upload state, AWS SDK S3 streaming bodies, SSE-S3/SSE-KMS/SSE-C metadata propagation, and serial execution over `TEST_BUCKET`.

Risks: many tests duplicate coverage from `common.rs` and `kms_local_test.rs`, increasing runtime. Fixed initialization sleep can be flaky. Step 5 covers only SSE-KMS and SSE-C because SSE-S3 is covered in earlier steps. The code includes non-ASCII log icons, and large byte-by-byte validation can be slow.

Test signals: passing tests show baseline multipart works, SSE-S3 metadata and decryption work for normal and larger multi-part objects, encryption chunk boundaries do not corrupt data, SSE-KMS multipart returns `AwsKms`, and SSE-C multipart requires and accepts customer headers across all phases.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/multipart_encryption_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/test_runner.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/test_runner.rs

Purpose: this file defines a metadata-driven unified KMS test-suite runner with categories, criticality flags, estimated durations, result reporting, and two suite tests. It is intended to orchestrate KMS coverage but currently does not dispatch real tests.

Important APIs, types, and functions: `TestCategory` enumerates core, multipart, edge, fault, comprehensive, and performance categories. `TestDefinition` stores name, description, category, duration, and critical flag. `TestResult` records success/failure, duration, and error. `TestSuiteConfig` filters categories and critical-only mode. `KMSTestSuite` owns definitions and provides `filter_by_category()`, `filter_critical_tests()`, `get_category_summary()`, `run_test_suite()`, `run_single_test()`, and `print_test_summary()`. Tests are `test_kms_critical_suite()` and `test_kms_full_suite()`.

Control flow: `KMSTestSuite::new()` builds a static catalog of KMS test names matching other modules. `run_test_suite()` filters by config, logs a plan, loops through definitions, calls `run_single_test()`, records duration, sleeps two seconds between entries, and prints summaries. `run_single_test()` only logs a warning that dispatch is not implemented and returns success. The suite tests therefore validate the runner plumbing but not actual KMS functionality.

State and persistence: in-memory state is the test catalog, filter config, generated result list, durations, and summaries. No RustFS server or KMS state is created by the runner because dispatch is a placeholder.

Dependencies and integration points: depends on tracing, tokio sleep, `serial_test`, and KMS test naming conventions. Intended integration point is future dispatch to actual test functions or subprocess-driven cargo filters.

Risks: the biggest risk is false confidence: both suite tests pass even though every listed test is skipped by placeholder dispatch. `max_duration` and `parallel_execution` config fields are not enforced. Success-rate math divides by `results.len()`, which would be problematic if filters produce zero tests.

Test signals: current signals are limited to runner catalog/filter/summary behavior. They do not prove any KMS feature works until `run_single_test()` is implemented.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/test_runner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/lib.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/lib.rs

Purpose: this is the crate root for RustFS E2E tests. It registers common helpers and a broad set of test modules covering object semantics, IAM/policy behavior, KMS, listing/versioning, object lock, cluster behavior, checksums, healing, replication, object lambda, and other regressions.

Important APIs, types, and functions: `pub mod common` exposes shared E2E utilities under `#[cfg(test)]`, and `pub mod tls_gen` is always public. Most entries are `#[cfg(test)] mod ...;` declarations, including the files in this subset: `kms`, `existing_object_tag_policy_test`, `group_delete_test`, `head_object_range_test`, `head_object_consistency_test`, `heal_erasure_disk_rebuild_test`, and `list_object_versions_metadata_extension_test`.

Control flow: there is no executable control flow beyond Rust module compilation. In test builds, all listed modules are compiled and their `#[tokio::test]` cases become discoverable by the Rust test harness. Non-test builds exclude nearly all E2E modules and common helpers.

State and persistence: no runtime state is stored here. It controls which test modules can create state in their own environments. Ordering in this file does not order test execution; serial behavior is controlled inside individual tests.

Dependencies and integration points: integrates with Cargo/Rust module resolution, the Rust test harness, and every declared source file. It is the top-level inclusion point that makes E2E regression tests part of the crate.

Risks: a missing module declaration silently prevents a test file from compiling/running. Broad unconditional `#[cfg(test)]` inclusion means expensive or environment-dependent tests are compiled for test builds, with runtime skip/ignore handled per test. The always-public `tls_gen` differs from the test-only pattern and may affect non-test builds.

Test signals: successful test compilation indicates every declared module resolves. Behavioral signals come from the individual module tests; this file’s direct signal is coverage reachability.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/list_object_versions_metadata_extension_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/list_object_versions_metadata_extension_test.rs

Purpose: this E2E regression test validates RustFS’s `GET /{bucket}?versions&metadata=true` extension. It checks that version listing XML includes user metadata, user tags, and internal erasure metadata fields for a versioned object.

Important APIs, types, and functions: `signed_get()` constructs an `http::Request` with `x-amz-content-sha256: UNSIGNED-PAYLOAD`, signs it with `rustfs_signer::sign_v4()`, copies signed headers into `local_http_client().get()`, and returns the raw `reqwest::Response`. The test uses AWS SDK bucket versioning APIs, object metadata/tagging upload, `urlencoding`, `StatusCode`, and raw XML string assertions.

Control flow: the test starts a RustFS server, creates a bucket, enables versioning, uploads one object with user metadata `project=alpha`, `owner=ops` and tags `env=test&project=alpha`, then performs a manually signed GET to `?versions&metadata=true&prefix=<key>`. It asserts HTTP 200 and checks the XML body contains `ListVersionsResult`, a `Version`, `UserMetadata`, stripped metadata keys, escaped `UserTags`, `Internal`, and specific internal `<K>1</K>` and `<M>0</M>` elements.

State and persistence: state includes bucket versioning configuration, one object version, user metadata, tags, and RustFS internal metadata exposed by the extension. The test does not explicitly delete the bucket/object after assertions, relying on temporary environment teardown.

Dependencies and integration points: depends on RustFS S3 versioning, metadata/tag persistence, the custom metadata extension, raw SigV4 signing through `rustfs_signer`, reqwest local HTTP client, and XML response formatting.

Risks: XML validation is string-based and brittle to formatting, ordering, namespaces, or schema changes. It asserts exact internal `K` and `M` values, coupling the test to erasure metadata for the default environment. It does not parse XML or validate multiple versions/delete markers.

Test signals: passing test proves the signed extension endpoint accepts `versions&metadata=true`, returns version-list XML, strips `x-amz-meta-` style user metadata into user-facing XML tags, includes escaped tag data, and exposes expected internal metadata fields.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/list_object_versions_metadata_extension_test.rs -->
