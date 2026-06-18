# Research: subset-b-008235

Grouped research for RustFS E2E test sources. Each section preserves the original source path and is intended to be split into the mapped source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/object_lambda_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/object_lambda_test.rs

Purpose: end-to-end coverage for RustFS object-lambda webhook targets and listen-notification streaming. The file verifies admin target lifecycle, object-lambda GET transformations through configured webhook targets, target validation failures, response auth-header enforcement, event stream delivery, and cluster fan-in behavior.

Important APIs/types/functions: `CapturedWebhookRequest` stores lowercased webhook request headers plus JSON payload; `WebhookResponseSpec` drives synthetic webhook status/body/headers and route/token behavior. `spawn_object_lambda_webhook_server_with_response` binds an ephemeral TCP listener, parses one HTTP request with `read_http_request`, captures `getObjectContext.outputRoute`/`outputToken`, and writes a controlled HTTP response. `presigned_get_request` and `signed_request` use `rustfs_signer` to generate SigV4 and presigned calls. Admin helpers configure/list/delete webhook targets through `/rustfs/admin/v3/target/...`. `read_listen_notification_event` consumes newline-delimited event JSON from a streaming response until the expected object key appears.

Control flow: tests initialize logging, start a `RustFSTestEnvironment` or `RustFSTestClusterEnvironment`, create buckets and objects through the AWS S3 SDK, configure webhook notification targets with signed admin requests, then exercise S3 GET URLs carrying `lambdaArn`. Positive object-lambda tests assert transformed response bodies, content type, bearer auth sent to the webhook, payload fields, and source `inputS3Url` usability. Negative tests check unsupported target types, missing/disabled targets, invalid admin endpoint configuration, disallowed `response_header_timeout`, and malformed/missing route/token response headers. Listen-notification tests open a signed long-lived bucket GET with event filters, put an object, and await event JSON; the cluster variant listens on node 0 while writing via node 1.

State and persistence behavior: webhook target configuration includes a per-test queue directory under the environment temp dir and is expected to persist under `.rustfs.sys/config/config.json`; one test restarts RustFS without cleanup to prove target visibility survives restart and deletion also survives restart. Listen-notification tests depend on in-process event propagation and, for cluster mode, remote node event fan-in. Synthetic webhook servers use one-shot or bounded mpsc channels and abort spawned listener tasks after assertions.

Dependencies and integration points: depends on shared E2E environment helpers, `reqwest`, `tokio::net::TcpListener`, `rustfs_signer`, `s3s::Body`, `aws_sdk_s3`, `serde_json`, `urlencoding`, and admin API routes. Integration points include RustFS notification target registry, target ARN listing, object-lambda ARN parsing, HTTP webhook transport probing, SigV4 auth, and server-sent notification streaming.

Risks: raw HTTP parsing is intentionally minimal and assumes `Content-Length`; webhook tasks only handle the first successful parsed request; tests are serial because they start real RustFS processes and use fixed service state. Timing-sensitive waits use short polling/timeouts, so slow CI can fail despite correct behavior. Error assertions often check substrings, which may become brittle if S3 error formatting changes.

Test signals: strong coverage of target persistence, online status probing, signed and presigned lambda GETs, named webhook target ARNs, output-route/token validation, admin validation failures, listen-notification event delivery with prefix/suffix filters, disabled notify mode behavior, and two-node cluster fan-in.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/object_lambda_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/object_lock/common.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/object_lock/common.rs

Purpose: shared Object Lock E2E helper layer. It centralizes server setup, Object Lock bucket creation, default retention configuration, object writes with retention or legal hold, retention/legal-hold mutations, delete operations with governance bypass, and future retention date calculation.

Important APIs/types/functions: `ObjectLockTestEnvironment` wraps `RustFSTestEnvironment` and exposes `new`, `start_rustfs`, `s3_client`, and `create_object_lock_bucket`. `put_object_lock_configuration` builds `DefaultRetention`, `ObjectLockRule`, and `ObjectLockConfiguration` for bucket defaults. `put_object_with_retention` maps `ObjectLockRetentionMode` to `ObjectLockMode`, formats UTC retain-until timestamps for the AWS SDK, and returns the created version id. `put_object_with_legal_hold`, `put_object_retention`, `put_object_legal_hold`, `delete_object_with_bypass`, and `future_retain_until` are reusable test operations.

Control flow: tests create an environment, start RustFS, create an Object Lock enabled bucket, then call these helpers to exercise S3 Object Lock APIs. Helpers construct SDK builders, optionally add version ids, send the requests, and log operation details. Date helpers deliberately format timestamps as `YYYY-MM-DDTHH:MM:SSZ` before parsing into AWS SDK `DateTime`.

State and persistence behavior: the helpers create real buckets and versioned objects in a temporary RustFS data directory. Object Lock enabled bucket creation is expected to trigger versioning behavior in the server. Returned version ids are the primary state handles used by the test suite for version-specific deletion, retention reads, and legal-hold reads.

Dependencies and integration points: uses `aws_sdk_s3` Object Lock model types, `ByteStream`, `chrono` for UTC date arithmetic, shared RustFS E2E environment, and `tracing`. It is imported by `object_lock_test.rs` as the common test DSL.

Risks: `retention_mode_to_lock_mode` falls back to governance for unknown strings, which is fine for tests using SDK enum values but would mask unexpected modes if reused more broadly. Date formatting truncates subsecond precision. Helpers return boxed dynamic errors, convenient for tests but not rich for diagnostics.

Test signals: this file is not itself a test module, but all Object Lock E2E test signals flow through it. Correctness is indirectly validated by delete, copy, multipart, retention mutation, default retention, and permission tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/object_lock/common.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/object_lock/mod.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/object_lock/mod.rs

Purpose: module root for Object Lock E2E tests. It documents the suite scope and wires the helper module plus concrete test module into the crate.

Important APIs/types/functions: exports `pub mod common` for shared helper access and declares private `mod object_lock_test` for the test bodies. There are no runtime functions or types in this file.

Control flow: Rust's test harness compiles the nested modules; `object_lock_test.rs` contains the `#[tokio::test]` entries, while `common.rs` provides shared setup and S3 operations.

State and persistence behavior: none locally. State is created by the child modules in RustFS temp directories and S3 buckets.

Dependencies and integration points: integrates the Object Lock test namespace into the e2e crate. The public `common` visibility allows sibling tests or future modules to reuse Object Lock helpers.

Risks: very low. Any missing module declaration would remove tests from compilation. The private `object_lock_test` module keeps test bodies scoped to this module.

Test signals: test discovery signal only; the concrete signals are in `object_lock_test.rs`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/object_lock/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/object_lock/object_lock_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/object_lock/object_lock_test.rs

Purpose: comprehensive Tokio E2E suite for S3 Object Lock behavior in RustFS. It verifies compliance and governance retention, legal hold, delete marker semantics, copy and multipart paths, IAM permission checks, batch deletion, default bucket retention, versioning, and error message quality.

Important APIs/types/functions: local helpers include `put_bucket_deny_policy`, `retention_timestamp`, `assert_access_denied`, `assert_invalid_object_lock_retention_pair`, and `parse_s3_datetime`. The tests import `ObjectLockTestEnvironment` and operation helpers from `common.rs`, plus AWS SDK types for multipart uploads, retention modes, legal-hold status, delete batches, copy metadata directives, and Object Lock headers.

Control flow: every test starts a fresh Object Lock environment, starts RustFS, creates an Object Lock enabled bucket, and executes one scenario. Delete tests assert compliance blocks deletion even with bypass, governance blocks without bypass but allows with bypass, legal hold blocks regardless of bypass, and delete-without-version creates removable delete markers while protected versions remain protected. Read tests assert `GetObjectLegalHold` and `GetObjectRetention` reflect updates. Write-path tests cover put, copy, and multipart creation/completion with requested legal hold or retention, including races where a protected current version appears after multipart creation. Permission tests install bucket deny policies for `s3:PutObjectLegalHold` or `s3:PutObjectRetention` and assert put/copy/multipart paths fail. Later tests cover mixed `DeleteObjects`, retention shortening/extension rules, default retention application, incomplete header-pair validation, destination-policy retention on copy, multipart default retention fixed at create time, automatic versioning, and distinct legal-hold versus retention error messages.

State and persistence behavior: scenarios rely heavily on version ids, delete markers, bucket-level Object Lock configuration, and server-side retention metadata. Default retention tests verify persisted bucket policy affects new objects and is visible via both `GetObjectRetention` and `HeadObject`. Multipart tests assert metadata chosen at `CreateMultipartUpload` survives until completion and is not recomputed after bucket default changes. Copy tests assert destination bucket policy, not source retention, determines implicit copied retention.

Dependencies and integration points: integrates the AWS S3 SDK object-lock API surface with RustFS storage/versioning behavior. It depends on serial execution, shared E2E server setup, `chrono` for retention windows, and bucket policies to simulate permission denial. It exercises S3 APIs including `CreateBucket`, `PutObject`, `CopyObject`, `CreateMultipartUpload`, `UploadPart`, `CompleteMultipartUpload`, `DeleteObject`, `DeleteObjects`, `GetObjectRetention`, `GetObjectLegalHold`, `HeadObject`, `GetBucketVersioning`, and `PutBucketPolicy`.

Risks: many tests unwrap and panic on setup failures, so diagnostics can be noisy. Bucket names are fixed, making serial execution important. Time-window assertions allow a few days of tolerance but still depend on system clock consistency. Error tests use substring matching. The suite is broad and process-heavy, so runtime can be significant.

Test signals: high-value regression signals for Object Lock invariants: immutable compliance retention, governance bypass semantics, legal hold enforcement, version-specific deletion, default retention and copy policy precedence, permission gates for special Object Lock headers, multipart race handling, and S3-compatible error surface.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/object_lock/object_lock_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/policy/mod.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/policy/mod.rs

Purpose: module root for policy-specific RustFS E2E tests focused on AWS IAM policy variable expansion.

Important APIs/types/functions: declares private modules `policy_variables_test`, `test_env`, and `test_runner`. It exposes no public API from this root.

Control flow: Rust test discovery compiles the variable tests and the ignored runner harness through this module. The actual test control flow lives in the child files.

State and persistence behavior: none locally. Child modules create users, policies, buckets, and cleanup state against a RustFS admin/S3 endpoint.

Dependencies and integration points: integrates the policy test namespace into the e2e crate. The private module layout keeps helpers scoped to policy tests.

Risks: low; accidental removal of a module declaration would silently drop its tests from the crate.

Test signals: module discovery only; substantive signals are in `policy_variables_test.rs` and `test_runner.rs`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/policy/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/policy/policy_variables_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/policy/policy_variables_test.rs

Purpose: ignored full-E2E tests for AWS IAM policy variable substitution in RustFS authorization. The suite covers `${aws:username}` in single resources, multiple resources, concatenated strings, nested variable syntax, STS-style users, and explicit deny precedence.

Important APIs/types/functions: helpers `create_user`, `create_sts_user`, `create_and_attach_policy`, and `cleanup_user_and_policy` call RustFS admin APIs with `awscurl_put`/`awscurl_delete`. Each scenario has an ignored `#[tokio::test]` entry, a standalone `_impl`, and an `_impl_with_env` variant used by `PolicyTestSuite`. Tests create S3 clients with user credentials through `PolicyTestEnvironment`.

Control flow: each implementation creates a user and canned policy, attaches it, optionally waits briefly for propagation, performs allowed and denied S3 operations, then best-effort cleans up buckets, objects, user, and policy. Single-value tests allow bucket/object access under `${aws:username}-*` and deny unrelated bucket creation. Multi-value tests allow exactly three username-derived bucket names. Concatenation allows `prefix-${aws:username}-suffix`. Nested tests expect `arn:aws:s3:::${${aws:username}-test}` to resolve to `<user>-test` and reject unresolved variable strings. STS tests currently create a regular user via `create_sts_user` and validate `${aws:username}-sts-bucket` access. Deny tests combine allow rules with a deny on `*private*` and expect deny to win.

State and persistence behavior: creates persistent RustFS admin users and canned policies on an existing server at `127.0.0.1:9000`. Cleanup deletes known bucket patterns and admin resources, but is best-effort and only runs after certain error branches, so interrupted tests can leave state behind. The environment itself only removes a temp directory on drop and does not stop the server.

Dependencies and integration points: depends on shared admin curl helpers, AWS S3 SDK, `PolicyTestEnvironment`, `serial_test`, and RustFS admin routes `/rustfs/admin/v3/add-user`, `/add-canned-policy`, `/set-user-or-group-policy`, `/remove-user`, and `/remove-canned-policy`. It integrates IAM policy evaluation with S3 `ListBuckets`, `CreateBucket`, `ListObjectsV2`, `PutObject`, and `GetObject`.

Risks: all direct tests are ignored and assume an external RustFS server rather than starting one. Fixed usernames and policy names can collide with stale state. The STS path is only a regular-user approximation, not a real AssumeRole/temporary-credential flow. Nested variable behavior may be nonstandard and should be checked against intended policy semantics. Cleanup misses some object keys if tests add new keys.

Test signals: good authorization regression signals for variable expansion in resource ARNs, multi-resource matching, concatenation, deny precedence, and user-scoped bucket/object permissions when run in full E2E mode.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/policy/policy_variables_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/policy/test_env.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/policy/test_env.rs

Purpose: lightweight environment wrapper for policy variable tests that connect to an already-running RustFS server and intentionally do not stop it on drop.

Important APIs/types/functions: `PolicyTestEnvironment` stores `temp_dir`, `address`, `url`, and admin credentials. `with_address` creates a unique temp directory and endpoint URL. `create_s3_client` builds a path-style AWS S3 client with supplied credentials, us-east-1, and the environment endpoint. `wait_for_server_ready` polls TCP connectivity for up to 30 seconds. `Drop` removes only the temp directory.

Control flow: policy tests or the runner instantiate `with_address("127.0.0.1:9000")`, optionally wait for readiness, then create admin or user S3 clients. Drop cleanup is local filesystem only.

State and persistence behavior: no server process ownership. Admin users, policies, and buckets live on the external RustFS instance and must be cleaned by tests. The temp directory is unique per environment and deleted best-effort on drop.

Dependencies and integration points: uses `aws_sdk_s3` config/credentials, `TcpStream` readiness checks, Tokio sleep, `uuid` temp directory naming, and tracing. It is consumed by `policy_variables_test.rs` and `test_runner.rs`.

Risks: TCP readiness only proves the port accepts connections, not that admin/S3 APIs are ready. Default admin credentials are hardcoded. Drop uses blocking std filesystem removal from a test context. Because the environment does not own the server, stale global state can affect results.

Test signals: indirect; supports ignored policy E2E tests and the ignored critical-suite runner.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/policy/test_env.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/policy/test_runner.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/policy/test_runner.rs

Purpose: orchestration harness for running the policy variable tests as a suite against an existing RustFS server. It provides categorization, result aggregation, optional critical-only filtering, pacing between tests, and summary logging.

Important APIs/types/functions: `TestCategory` enumerates SingleValue, MultiValue, Concatenation, Nested, and DenyScenarios. `TestDefinition` describes test name, category, and criticality. `TestResult` records success or error. `TestSuiteConfig` carries `include_critical_only`. `PolicyTestSuite::new`, `with_config`, `run_test_suite`, `run_single_test`, and `print_summary` implement the suite runner. Ignored `test_policy_critical_suite` invokes the runner with critical-only filtering and fails if any result failed.

Control flow: `run_test_suite` initializes logging, creates `PolicyTestEnvironment` for `127.0.0.1:9000`, waits for TCP readiness, filters definitions, runs each named test by dispatching to the corresponding `_impl_with_env` function in `policy_variables_test.rs`, sleeps two seconds between tests, and logs pass/fail summary.

State and persistence behavior: shares one external-server environment across all policy variable cases, so users/policies/buckets are created and cleaned by each test. Results are in-memory only. The runner does not checkpoint progress or isolate server state beyond serial execution and per-test cleanup.

Dependencies and integration points: depends on `PolicyTestEnvironment`, policy variable implementation functions, `serial_test`, Tokio sleep, `Instant`, and tracing. It integrates multiple ignored test functions into one ignored aggregate test.

Risks: matching by test-name string is fragile; adding a test to `PolicyTestSuite::new` requires updating `run_single_test`. `print_summary` divides by `results.len()` and would be invalid for an empty suite. The environment readiness check is only TCP-level. The runner assumes fixed port 9000 and external server lifecycle.

Test signals: useful aggregate signal for the policy variable critical path, especially for CI jobs that intentionally start RustFS out of band and run ignored E2E suites.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/policy/test_runner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/protocols/ftps_core.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/protocols/ftps_core.rs

Purpose: core FTPS E2E test for RustFS protocol support. It starts RustFS with FTPS enabled, connects with a TLS-capable FTP client, and verifies bucket/object operations through FTPS map correctly to object-store semantics.

Important APIs/types/functions: constants `FTPS_PORT` and `FTPS_ADDRESS` fix the test endpoint. `AcceptAnyServerCertVerifier` implements rustls certificate and signature verification by accepting all certs for generated self-signed test certificates. `test_ftps_core_operations` is the exported async entry point. It generates default and domain-specific cert/key pairs with `rcgen`, starts RustFS via `tokio::process::Command`, builds a dangerous rustls client config, and uses `suppaftp::RustlsFtpStream` for FTP commands.

Control flow: create protocol temp environment and cert directory, write self-signed certificates, spawn RustFS with `RUSTFS_FTPS_ENABLE`, `RUSTFS_FTPS_ADDRESS`, and `RUSTFS_FTPS_CERTS_DIR`, wait for port readiness, install the aws-lc rustls provider, connect and upgrade to TLS, login with default credentials, then run a command walkthrough: `mkdir` bucket, `cwd`, upload, download and compare content, list relative/root/absolute paths, `cwd .`, `cwd /`, delete object, reject cwd to nonexistent bucket, remove bucket, verify final listing, and quit. The server process is killed and waited after the async test body completes.

State and persistence behavior: creates a temporary RustFS data directory and certificate files. FTPS operations create a bucket and object, then delete both before exit. The spawned RustFS process is manually owned by this test and killed on completion.

Dependencies and integration points: uses `ProtocolTestEnvironment`, shared binary resolution with features `ftps,webdav`, rustls/aws-lc, `rcgen`, `suppaftp`, default protocol credentials, and the RustFS FTPS listener. The test bridges FTP verbs to S3-like bucket/object behavior.

Risks: fixed port 9021 can conflict with other local runs. Accept-all certificate verification is correct for local generated certs but must remain test-only. `install_default` for the rustls crypto provider is global and can only succeed once per process, depending on rustls behavior. The test uses blocking suppaftp operations inside an async function, which is acceptable for E2E but can occupy a Tokio worker.

Test signals: validates FTPS TLS startup, authentication, bucket creation/removal, object upload/download/delete, path normalization for root/current/absolute paths, directory listings, and error handling for nonexistent buckets.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/protocols/ftps_core.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/protocols/mod.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/protocols/mod.rs

Purpose: module root for protocol E2E tests covering FTPS, SFTP, and WebDAV.

Important APIs/types/functions: publicly exposes `ftps_core`, `sftp_compliance`, `sftp_core`, `sftp_helpers`, `test_env`, `test_runner`, and `webdav_core`; declares private `sftp_compliance_tests` implementation modules.

Control flow: this root controls which protocol modules are compiled and which helpers are externally reusable inside the e2e crate. Public entry modules expose async suite functions, while private compliance case bodies stay internal.

State and persistence behavior: none locally. Child modules start RustFS protocol listeners, create temp data directories, seed S3 objects, and own process teardown.

Dependencies and integration points: ties protocol-specific test suites into the e2e crate. The public/private split lets high-level compliance entries call detailed cases without making every case module part of the public test API.

Risks: low, but module visibility changes can affect downstream test runner access. Missing declarations would drop whole protocol suites from compilation.

Test signals: module discovery and organization signal only; concrete protocol behavior is tested in child modules.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/protocols/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/protocols/sftp_compliance.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/protocols/sftp_compliance.rs

Purpose: public orchestration entry points for the SFTP compliance suite. It groups numbered CMPTST cases into read-write, read-only, and standalone-server suites with shared setup where possible.

Important APIs/types/functions: constants define non-overlapping SFTP/S3 addresses for read-write and read-only suites. `test_sftp_compliance_suite` runs CMPTST-01..14 plus CMPTST-34 against one read-write server/session. `test_sftp_compliance_readonly` seeds fixtures over S3, connects to a read-only SFTP server, and runs CMPTST-15..23. `test_sftp_compliance_standalone` runs CMPTST-24..29 and 32..33, with Linux-only cases 24..26. It imports case modules and helpers from `sftp_compliance_tests`, `sftp_helpers`, and `ProtocolTestEnvironment`.

Control flow: each shared-suite entry spawns RustFS via `spawn_compliance_rustfs`, waits for the SFTP port, opens an SFTP session, executes numbered case functions in order, drops the SFTP handle, disconnects the SSH session, kills the server process, and returns the case result. The read-write suite also builds an S3 client against the paired S3 endpoint to check multipart metadata propagation for CMPTST-34. The read-only suite seeds a bucket/object through S3 because SFTP mutations are expected to fail. The standalone suite delegates to cases that each manage their own server configuration.

State and persistence behavior: shared suites create temporary RustFS processes and protocol sessions. Read-only mode starts SFTP as read-only while leaving the S3 endpoint writable for fixture setup. Standalone tests isolate state per case because they require incompatible settings such as idle timeout, read-cache window, or console disabled state.

Dependencies and integration points: integrates SFTP protocol behavior with S3 fixture setup and RustFS process spawning. Depends on `russh` disconnect semantics through helper return values, AWS S3 `ByteStream`, `anyhow`, and Linux-only system state checks in selected cases.

Risks: fixed ports 9024/9300 and 9025/9301 can conflict with other protocol tests if teardown fails. Several cases are intentionally omitted from default suite for structural/runtime reasons, so full compliance requires separate ignored entries in `sftp_compliance_tests.rs`. Teardown errors are discarded by design, so only assertion results bind outcome.

Test signals: broad SFTP regression signal for binary and zero-byte round trips, path traversal/dotdot handling, cross-bucket rename, paths with spaces, readlink/setstat shapes, implicit directories, read-only mutation rejection and read allowance, kernel/session leak checks on Linux, concurrent/pipelined operations, EOF reads, read-cache behavior, and multipart metadata propagation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/protocols/sftp_compliance.rs -->
