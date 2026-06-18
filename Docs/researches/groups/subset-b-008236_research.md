# Grouped Research: subset-b-008236

This grouped report covers RustFS e2e protocol and quota test sources. Each file section is bounded with reconciliation markers so it can be split into the mapped source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/protocols/sftp_compliance_tests.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/protocols/sftp_compliance_tests.rs

## Purpose

This file is the implementation body for RustFS SFTP compliance regression coverage. It contains one module per CMPTST case, plus shared process-spawn, fixture, stream-wrapper, log-capture, hashing, and socket-state helpers. The companion dispatcher `sftp_compliance.rs` wires these modules into three public suite entries: shared read-write compliance, read-only compliance, and standalone server regressions. The file is intentionally broad: it tests SFTP protocol semantics, S3-backed persistence behavior, pathological client transport patterns, large object reads, pipelining, read-cache modes, and metadata preservation across multipart uploads.

The top-level module documentation is a load-bearing case index. It maps CMPTST-01 through CMPTST-34 to concrete regression properties. CMPTST-01..14 use a shared read-write SFTP server, CMPTST-15..23 use a read-only SFTP server seeded through S3, and CMPTST-24..33 are standalone process-level regressions. CMPTST-34 is implemented here but invoked by the shared read-write dispatcher after CMPTST-14 because it needs both the same SFTP session and an S3 client against the same process.

## Important APIs, Types, And Functions

`spawn_compliance_rustfs(sftp_address, s3_address, read_only)` is the externally used spawn helper. It creates a `ProtocolTestEnvironment`, generates an ed25519 host key, starts the RustFS binary with `ENV_SFTP_ENABLE`, `ENV_SFTP_ADDRESS`, `ENV_SFTP_HOST_KEY_DIR`, `ENV_SFTP_READ_ONLY`, `ENV_SFTP_PART_SIZE`, and `ENV_RUSTFS_ADDRESS`, then returns the environment plus `ServerProcess`.

`spawn_pipelining_rustfs` and `spawn_pipelining_rustfs_with_extras` are local variants for long-running or diagnostic standalone cases. They disable the console listener, set bounded SFTP protocol logging via `RUSTFS_OBS_LOGGER_LEVEL` and `RUST_LOG`, pipe stdout for diagnostic capture, and optionally inject extra environment variables such as `ENV_SFTP_READ_CACHE_WINDOW_BYTES`.

Fixture helpers include `seed_pipelining_fixture`, `seed_large_via_multipart`, `calculate_pattern_sha256`, and `streaming_sha256_download`. Together they support deterministic byte-pattern seeding through S3 multipart upload and bounded-memory SHA256 verification through SFTP. This matters for multi-GiB reads because the tests do not materialize the entire expected payload in memory.

`capture_server_stdout` keeps a bounded in-memory tail of spawned server stdout for failure dumps. `SessionCounters` and `watch_session_lifecycle_events` scrape "SFTP session task entered/finished/panicked" log lines for lifecycle assertions in socket-regression cases. On Linux, `count_close_wait_on_port` shells out to `ss -tn state CLOSE-WAIT` and returns a best-effort socket count for a specific local port.

The case modules expose descriptive `pub(crate) async fn run_*` entries. Semantics cases cover medium and zero-byte round trips, rm/rmdir rejection, path traversal and `/..` handling, cross-bucket rename, paths with spaces, readlink rejection, SETSTAT/FSETSTAT behavior, same-path rename, implicit directories, WinSCP write-handle FSETSTAT, read-only mutation rejection, and read-only reads. Transport and performance cases define custom stream wrappers: `HalfClosableStream`, `WedgeStream`, and `PausableStream` implement `AsyncRead`/`AsyncWrite` around split `TcpStream` halves and atomics to simulate half-closed, wedged, or paused-drain clients while keeping the russh client task alive.

## Control Flow

The normal read-write compliance flow is: spawn RustFS, wait for SFTP port readiness, connect with `connect_sftp_to`, run CMPTST-01..14 over one SFTP session, create an S3 client to the same process, run CMPTST-34, disconnect, then `kill_and_wait` the server. The read-only flow is similar but starts with `read_only=true`, seeds a bucket/object through S3, then runs CMPTST-15..23 to prove SFTP mutations fail while listing and reading still work.

Standalone flows each own their process lifecycle because they depend on dedicated ports and environment. CMPTST-24 and CMPTST-25 create multiple custom-stream russh sessions, force FIN/CLOSE_WAIT or server-channel wedge states, wait for watchdog or idle-timeout behavior, tickle the accept loop with short TCP connects so task completions are drained, then assert task-counter balance and zero CLOSE_WAIT entries when `ss` is available. CMPTST-26 is the inverse: it keeps a healthy idle session alive past the fast-kill threshold and asserts it was not false-killed. CMPTST-27 seeds a multi-GiB fixture and downloads it concurrently on four SFTP sessions under a one-hour no-progress deadline. CMPTST-28 runs a 5 MiB download while parallel sessions issue hundreds of metadata and readdir operations. CMPTST-29 opens many handles and issues 10,000 reads past EOF, expecting fast EOF responses. CMPTST-30 measures metadata handler latency under pipelined load but is ignored by default. CMPTST-31 pauses client-side reads mid-transfer, resumes, and verifies byte-exact completion. CMPTST-32 and CMPTST-33 share `run_read_cache_byte_correctness` with cache window enabled and disabled.

## State And Persistence Behavior

All persistent storage under test is the RustFS data directory created by `ProtocolTestEnvironment` and the S3 object store surfaced by the spawned RustFS process. Tests create buckets and objects through SFTP and S3, then validate persistence through the opposite protocol or through metadata APIs. Directory state is modeled through buckets, object prefixes, and RustFS directory markers such as `__XLDIR__` in related core tests; this file focuses on compliance behavior such as implicit directory listing and non-empty rmdir rejection.

Multipart state is important in `seed_large_via_multipart` and CMPTST-34. Large fixtures are written part by part with S3 multipart APIs and completed only after all parts have ETags. CMPTST-34 specifically asserts that SFTP `OPEN` attributes survive the SFTP buffering-to-streaming multipart path and become object metadata visible through S3 `HeadObject`.

Process state is guarded with `ServerProcess`, which kills children even on panic paths. Temp directories are cleaned by `ProtocolTestEnvironment` drop. Several tests intentionally hold russh handles, SFTP sessions, channels, and stream controls in vectors so client sockets remain in the intended pathological state until the server-side assertion window completes.

## Dependencies And Integration Points

Major dependencies are `russh`, `russh_sftp`, `tokio`, `aws_sdk_s3`, `sha2`, `futures::stream::FuturesUnordered`, `anyhow`, and RustFS config constants from `rustfs_config`. The file relies on local helpers from `sftp_helpers.rs` for host-key generation, SFTP connection, S3 client construction, and full-file reads. It uses `ProtocolTestEnvironment` from `test_env.rs` for temp directories and TCP readiness polling.

The public integration point is indirect: `sftp_compliance.rs` imports the `cmptst_*` modules and `spawn_compliance_rustfs`, then `test_runner.rs` schedules those public suite functions under the `sftp` feature. Linux-specific cases are guarded with `#[cfg(target_os = "linux")]`; CMPTST-30 is `#[ignore]`, and CMPTST-31 has a direct `#[tokio::test]` but is intentionally omitted from the default standalone dispatcher for runtime cost.

## Risks And Edge Cases

The file is highly integration-heavy and port-bound. Fixed local ports from 9024 through 9035 and S3 ports around 9300 can conflict with leaked servers or local development processes. Several cases have long waits or large fixtures: CMPTST-25 and CMPTST-26 wait 90 seconds, CMPTST-27 defaults to 5 GiB, and CMPTST-31 seeds 200 MiB and pauses 25 seconds. These are strong regression signals but expensive in CI.

Socket-state assertions are platform-sensitive. `count_close_wait_on_port` skips when `ss` is unavailable, so Linux without `ss` loses part of the signal. Log-scraped counters depend on exact server log messages. If logging text changes, lifecycle tests may fail or undercount despite correct runtime behavior.

The custom stream wrappers intentionally return `Poll::Pending` in unusual situations. That makes them useful for reproducing real client pathologies, but small russh behavior changes can alter how reliably they hold sockets in the desired state. The read-cache e2e tests assert byte correctness only; backend request-count behavior is left to lower-level unit tests.

## Test Signals

This file is itself a dense test source. Signals include SHA256 equality, byte-count equality, S3 `HeadObject` metadata checks, expected errors for unsupported or forbidden SFTP operations, directory listing contents, watchdog lifecycle counter balance, CLOSE_WAIT counts, timeout-enforced completion, EOF semantics, and ignored latency ceiling checks. The small unit test `cmptst29_eof_status_matches_protocol_constant` pins `StatusCode::Eof as u32 == 1` so dependency changes in `russh_sftp` surface before the high-volume EOF regression runs.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/protocols/sftp_compliance_tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/protocols/sftp_core.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/protocols/sftp_core.rs

## Purpose

This file defines core SFTP e2e tests for RustFS. It verifies the basic SFTP surface against a spawned RustFS binary, then checks cross-protocol consistency between SFTP and the same server's S3 endpoint. A second public function verifies idle-timeout disconnect behavior on dedicated ports.

## Important APIs, Types, And Functions

`connect_sftp()` is a tiny wrapper around `connect_sftp_to(SFTP_ADDRESS)`. `assert_cross_protocol_sha_match` is the key reusable assertion: it computes an expected SHA256, reads the object through S3 `GetObject`, reads the same object through SFTP via `sftp_read_full`, and verifies both length and digest.

`test_sftp_core_operations()` is the main exported async test body. It generates a host key, spawns RustFS with SFTP enabled, read-only disabled, `ENV_SFTP_PART_SIZE` pinned to 5 MiB, and the S3 address on port 9200. It exercises subsystem negotiation, bucket mkdir/listing, small file write/read, stat, setstat, rename, multipart-sized write/read, negative SFTP operations, bad password handling, cross-protocol SFTP-to-S3 and S3-to-SFTP byte identity, directory marker visibility, and cleanup.

`test_sftp_idle_timeout_disconnects()` spawns a separate RustFS process on SFTP port 9023 and S3 port 9100, sets `ENV_SFTP_IDLE_TIMEOUT` to 5 seconds, confirms the session is live, sleeps 10 seconds, and expects the next SFTP request to fail.

## Control Flow

Both public functions follow a similar pattern: create `ProtocolTestEnvironment`, generate host keys, spawn RustFS with feature-gated binary path, wait for the SFTP port, connect using the shared russh helper, run assertions inside an async block, then kill and wait for the child with `ServerProcess`.

The main core flow starts with a canary `canonicalize(".")`, creates a bucket through SFTP `create_dir`, lists root, writes `small.txt`, reads it back, compares SHA256, stats file and bucket, performs no-op SETSTAT, renames to `renamed.txt`, and lists to confirm the old name is gone. It then writes a deterministic `MULTIPART_SIZE` buffer just over two 5 MiB parts and checks the multipart round trip. Negative cases assert errors for symlink, nonexistent open, nonexistent directory listing, traversal, append, create-exclude on an existing key, write-only open, write-create without truncate, and bad password auth.

After S3 readiness, cross-protocol checks write through SFTP and read through both protocols, then write through S3 and read through both protocols. Directory visibility checks ensure SFTP-created directories are visible to S3 listing and S3-created `__XLDIR__` markers are decoded as SFTP directories.

## State And Persistence Behavior

The test creates and removes real buckets, files, and directory markers in the spawned RustFS data directory. Payloads are deterministic so byte corruption is caught by SHA256. The multipart branch is made deterministic by pinning `ENV_SFTP_PART_SIZE` and using `MULTIPART_SIZE = part_size * 2 + 1024`.

The file repeats `XLDIR_SUFFIX` locally because this e2e crate does not depend on `rustfs-utils`. That suffix is part of the persistence contract between S3 object keys and SFTP directory views.

## Dependencies And Integration Points

The file integrates local helpers from `sftp_helpers.rs` and `test_env.rs`, RustFS config constants, `aws_sdk_s3`, `russh`, `russh_sftp`, `tokio`, and `sha2`. `test_runner.rs` schedules `test_sftp_core_operations` and `test_sftp_idle_timeout_disconnects` when the `sftp` feature is requested. The spawned binary path comes from `rustfs_binary_path_with_features(Some("ftps,webdav,sftp"))`.

## Risks And Edge Cases

Fixed ports 9022/9200 and 9023/9100 can conflict with other local processes. The cross-protocol section requires both SFTP and S3 stacks to be healthy in the same RustFS process; port readiness alone is not enough, so `wait_for_s3_ready` is used. Some negative assertions only check `is_err`, not exact status codes, which is robust to client error type changes but less precise for protocol-status regressions.

## Test Signals

Signals include SFTP session negotiation, root and bucket listings, file stat metadata, SHA256 checks for small and multipart payloads, unsupported operation errors, auth failure, S3/SFTP byte identity in both write directions, directory marker interoperability, and post-timeout request failure.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/protocols/sftp_core.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/protocols/sftp_helpers.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/protocols/sftp_helpers.rs

## Purpose

This file provides shared SFTP e2e utilities: permissive host-key verification for ephemeral test servers, host-key generation, RustFS child-process cleanup, russh SFTP connection setup, full-file SFTP reads, S3 client construction, and S3 readiness polling.

## Important APIs, Types, And Functions

`AcceptAnyServerKey` implements `russh::client::Handler` and always accepts the server key. This is scoped to tests because each RustFS process generates a fresh host key and the suite exercises authentication and protocol behavior rather than host-key trust.

`generate_host_key(host_key_dir)` creates an ed25519 key pair in OpenSSH format using `russh::keys`, writes private and public files, and on Unix forces both to mode `0600`. The comment explains that the RustFS config loader scans every entry and rejects insecure permissions.

`ServerProcess` wraps `tokio::process::Child` in an `Option`. `kill_and_wait` asynchronously kills and reaps the child and is idempotent. `Drop` calls `start_kill` synchronously if the async cleanup path was skipped, preventing leaked RustFS listeners after panics.

`connect_sftp_to(address)` creates a russh client with `AcceptAnyServerKey`, authenticates with `DEFAULT_ACCESS_KEY` and `DEFAULT_SECRET_KEY`, opens a session channel, requests the `sftp` subsystem, and returns both the russh handle and `SftpSession`. Returning the handle is required to keep the SSH transport alive for the SFTP session.

`sftp_read_full` opens a file with `OpenFlags::READ`, reads it into a `Vec<u8>`, then shuts down the handle. `build_test_s3_client(endpoint_url)` constructs an AWS SDK S3 client with default test credentials, us-east-1, path-style addressing, and an HTTP client override for `http://` endpoints. `wait_for_s3_ready` polls `ListBuckets` until it succeeds or the attempt budget expires.

## Control Flow

The helper flow is intentionally simple and reusable. Tests create an environment, call `generate_host_key`, spawn RustFS, wait for ports, call `connect_sftp_to`, then use SFTP and S3 helpers for assertions. Cleanup is either explicit through `ServerProcess::kill_and_wait` or panic-path best effort through `Drop`.

## State And Persistence Behavior

The only durable files this helper writes are ephemeral host-key files inside the per-test temp directory. It also controls child-process state and prevents leaked listeners. S3 and SFTP helpers do not maintain caches; they create fresh clients and sessions.

## Dependencies And Integration Points

This file depends on `russh`, `russh_sftp`, `aws_sdk_s3`, `aws_smithy_http_client`, `tokio`, `anyhow`, and test credential constants from `test_env.rs`. It is used by SFTP core and compliance tests and indirectly by the protocol runner. It bridges RustFS test credentials to both SFTP password auth and S3 signed client calls.

## Risks And Edge Cases

The host-key handler is intentionally insecure and must remain test-only. `ServerProcess::Drop` cannot await `wait`, so panic cleanup may leave a zombie until the runtime or parent process reaps it, but it still releases the listening port. `sftp_read_full` reads the whole object into memory and is not appropriate for multi-GiB fixtures; the compliance file uses streaming SHA256 for those cases. `wait_for_s3_ready` treats any successful `ListBuckets` as readiness and does not validate bucket-specific state.

## Test Signals

There are no direct unit tests in this file, but nearly all SFTP e2e tests depend on these helpers. Failures in key generation, permissions, auth, subsystem negotiation, child cleanup, S3 client config, or readiness polling surface quickly in SFTP core and compliance suites.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/protocols/sftp_helpers.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/protocols/test_env.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/protocols/test_env.rs

## Purpose

This file defines the minimal protocol-test environment shared by FTPS, SFTP, and WebDAV e2e tests. It owns a unique temporary data directory, exposes default credentials, and provides TCP port readiness polling without owning server shutdown.

## Important APIs, Types, And Functions

`DEFAULT_ACCESS_KEY` and `DEFAULT_SECRET_KEY` are both `rustfsadmin` and are shared by protocol tests and SFTP/S3 helper clients.

`ProtocolTestEnvironment { temp_dir: String }` creates a directory under the system temp directory named with a UUID. `new()` creates that directory and converts the path to UTF-8, returning an error if conversion fails.

`wait_for_port_ready(port, max_attempts)` tries to connect to `127.0.0.1:<port>` once per second until success or the attempt budget is exhausted. It logs success and returns an error naming the timeout when the server never listens.

`Drop` removes `temp_dir` and logs a warning if cleanup fails. It deliberately does not stop any server process.

## Control Flow

Tests call `ProtocolTestEnvironment::new()` before generating host keys or spawning RustFS. The temp directory is passed as the RustFS data path. After the process is started, tests call `wait_for_port_ready` for the protocol listener before opening protocol clients. Server shutdown is handled outside this struct by direct child process handling or `ServerProcess`.

## State And Persistence Behavior

The environment creates a real temporary filesystem directory and deletes it on drop. RustFS uses that directory for its backend state during e2e tests, so bucket and object persistence lasts only for the environment lifetime. Because this struct does not own child processes, dropping it before killing RustFS could remove data while a server is still running; existing tests keep environment and server process in the same scope and kill the child before leaving.

## Dependencies And Integration Points

The file uses `uuid`, `std::net::TcpStream`, `tokio::time::sleep`, and `tracing`. It is consumed by SFTP core/compliance and WebDAV tests. The credentials are also used in `sftp_helpers.rs` and WebDAV basic auth helpers.

## Risks And Edge Cases

Readiness is TCP-level only. Some tests also need service-level readiness such as S3 `ListBuckets`, so they must call additional helpers. `temp_dir` is stored as `String`, so non-UTF-8 temp paths are rejected. Cleanup is best effort and can fail if a child process still holds files.

## Test Signals

No direct tests exist here. Its behavior is exercised indirectly by every protocol e2e test that creates a temp environment or waits for a spawned listener.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/protocols/test_env.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/protocols/test_runner.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/protocols/test_runner.rs

## Purpose

This file is the orchestration layer for protocol e2e tests. It builds a feature-filtered test list, runs the selected protocol suites serially, records pass/fail results, logs a summary, and exposes one `#[tokio::test]` entry that fails if any selected suite fails.

## Important APIs, Types, And Functions

`TestResult` records `test_name`, `success`, and optional `error_message`, with constructors `success` and `failure`.

`ProtocolTestSuite` stores `Vec<TestDefinition>`. `new()` reads requested RustFS build features through `requested_rustfs_build_features()` and delegates to `with_requested_features`. The latter filters `all_protocol_tests()` through `rustfs_build_feature_enabled`.

`run_test_suite()` initializes logging, logs the scheduled count, iterates tests in order, emits descriptive start messages, awaits `run_single_test`, records duration and result, sleeps two seconds between tests, then calls `print_summary`.

`run_single_test()` maps stable string names to imported async functions: FTPS core, WebDAV core, SFTP core, SFTP compliance suite, SFTP read-only compliance, SFTP idle timeout, and SFTP standalone compliance. `all_protocol_tests()` defines the stable order and required features.

The `test_protocol_core_suite` `#[tokio::test]` is marked `#[serial]`; it runs the suite and returns an error if any result failed.

## Control Flow

Runtime control is linear and conservative. The feature filter is applied before execution. Each selected test is awaited to completion before the next begins, reducing fixed-port conflicts between protocol suites. Failures are captured into `TestResult` rather than aborting the full loop immediately, so the summary can report every failed selected suite. The final Tokio test converts any failures into one aggregate error.

## State And Persistence Behavior

This file owns no persistent data. It coordinates child-process-owning test bodies in other modules. The only state it maintains is in-memory test definitions, results, and timings. The two-second inter-test delay is a process/port stabilization mechanism rather than persistent state.

## Dependencies And Integration Points

The runner imports public protocol suite functions from FTPS, WebDAV, SFTP core, and SFTP compliance modules. It depends on `common::init_logging`, `requested_rustfs_build_features`, and `rustfs_build_feature_enabled` for logging and feature filtering. `serial_test::serial` ensures the top-level protocol suite does not run concurrently with other serial tests.

## Risks And Edge Cases

The dispatch uses string matching, so names in `all_protocol_tests`, description logging, and `run_single_test` must stay synchronized. Unknown names produce an explicit "not implemented" error. Tests are serial, which reduces interference but makes the full suite expensive, especially when SFTP standalone compliance includes long-running cases. Feature filtering is only as correct as `rustfs_build_feature_enabled`.

## Test Signals

The module has focused unit tests for scheduling behavior: all tests without a filter, non-SFTP feature subsets, SFTP-only scheduling, case-insensitive feature names, `full` scheduling, and no protocol tests for unrelated features. The integration signal is `test_protocol_core_suite`, which fails on any protocol suite failure.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/protocols/test_runner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/protocols/webdav_core.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/protocols/webdav_core.rs

## Purpose

This file defines the core WebDAV e2e suite for RustFS. It starts a RustFS process with WebDAV enabled, exercises authenticated WebDAV collection and object operations, validates directory move behavior, checks authorization failure atomicity, and verifies failed authentication.

## Important APIs, Types, And Functions

`create_client()` builds a reqwest client accepting invalid certs, although this test disables WebDAV TLS. `basic_auth_header` and `basic_auth_header_for` build Basic auth headers from default or supplied credentials.

`signed_admin_request` builds and signs RustFS admin API requests with AWS Signature V4 using `rustfs_signer`. It sets `Host`, `x-amz-content-sha256: UNSIGNED-PAYLOAD`, optional content type, signs with default admin credentials, then sends through the local HTTP client. `admin_create_user`, `admin_add_canned_policy`, and `admin_attach_policy_to_user` wrap specific admin API endpoints and bail with response status/body on failure.

`test_webdav_core_operations()` is the main exported async test body. It spawns RustFS with `--address` for the S3/admin endpoint, `RUSTFS_WEBDAV_ENABLE=true`, `RUSTFS_WEBDAV_ADDRESS=127.0.0.1:9080`, and TLS disabled. The direct `#[tokio::test]` entry simply calls this function and is marked serial.

## Control Flow

The suite waits for the WebDAV port, creates a reqwest client and Basic auth header, then runs a sequential workflow. It starts with `PROPFIND` at root, `MKCOL` to create a bucket, `PUT`/`GET`/`PROPFIND` for a file, `DELETE` of that file, and a 404 check for the deleted object. It then tests file `MOVE` and verifies source deletion and destination content.

Directory behavior follows: `MKCOL` creates a directory, `PUT` writes inside it, `PROPFIND` lists it, `GET` on the collection is expected to return 405, `MOVE` renames the directory, and nested directory creation plus nested `MOVE` preserve contained file content.

The authorization regression creates a restricted bucket and source directory, writes a file, creates a limited user with `ListBucket`, `GetObject`, and `PutObject` but no `DeleteObject`, then attempts a directory `MOVE`. It asserts the move is rejected, no destination object is created, and the source remains byte-identical. Finally it deletes the main bucket and checks invalid Basic auth returns 401.

## State And Persistence Behavior

The test writes real buckets, objects, and directory-shaped prefixes into the spawned RustFS temp directory. MOVE operations are validated as copy/delete behavior from the WebDAV view, and the restricted MOVE check is specifically about atomicity: denied delete permission must not leave partial destination writes. Admin users and canned policy state are created through RustFS admin APIs within the same process.

## Dependencies And Integration Points

The file depends on `reqwest`, `base64`, `http`, `rustfs_signer`, `s3s::Body`, `serde_json`, `tokio`, and local common/test environment helpers. `test_runner.rs` schedules `test_webdav_core_operations` when the `webdav` feature is enabled. It uses `ProtocolTestEnvironment` only for temp storage and port readiness, while child process cleanup is handled directly with `kill` and `wait`.

## Risks And Edge Cases

The suite uses fixed WebDAV and S3/admin ports 9080 and 9010. It assumes admin API paths and SigV4 signing behavior stay compatible with the JSON payloads used here. Cleanup is focused on killing the process; not all created buckets/users/policies are explicitly removed before process teardown. Some status assertions accept several success codes to accommodate WebDAV variations, but exact failure cases are pinned for 404, 405, and 401.

## Test Signals

Signals include WebDAV status codes for `PROPFIND`, `MKCOL`, `PUT`, `GET`, `DELETE`, and `MOVE`; body content equality after GET and MOVE; PROPFIND response contents; collection GET returning 405; authorization-denied directory MOVE leaving no destination and preserving source; successful admin user/policy calls; and invalid auth returning 401.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/protocols/webdav_core.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/quota_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/quota_test.rs

## Purpose

This file implements RustFS bucket quota integration tests. It starts a RustFS test environment, uses S3 APIs for object operations, uses `awscurl` helpers for signed admin quota endpoints, and validates quota setting, clearing, usage accounting, operation checks, permissions, copy, batch delete, and multipart completion behavior.

## Important APIs, Types, And Functions

`skip_without_awscurl()` gates every integration test. If the external `awscurl` dependency is unavailable, tests log and return `Ok(())` rather than failing.

`QuotaTestEnv` groups `RustFSTestEnvironment`, an AWS SDK S3 `Client`, and a generated bucket name. `new()` starts a RustFS server and creates an S3 client. Methods wrap common operations: `create_bucket`, `cleanup_bucket`, `set_bucket_quota`, `get_bucket_quota`, `clear_bucket_quota`, `get_bucket_quota_stats`, `check_bucket_quota`, `upload_object`, `object_exists`, `get_bucket_usage`, bucket-specific quota/stats setters, and bucket-specific upload.

Admin quota calls use endpoints under `/rustfs/admin/v3/quota/<bucket>`, `/quota-stats/<bucket>`, and `/quota-check/<bucket>` with JSON bodies. Object operations use AWS SDK S3 calls such as `put_object`, `head_object`, `delete_object`, `delete_objects`, `copy_object`, multipart create/upload/complete, and bucket management through the common test environment.

## Control Flow

Each `#[tokio::test]` is serial. The typical flow initializes logging, skips if `awscurl` is unavailable, constructs `QuotaTestEnv`, creates one or more buckets, sets a hard quota, performs S3 operations, checks admin quota APIs, then cleans up buckets. Error-path tests intentionally expect failed S3 or admin calls.

The basic operations test sets a 1 MiB quota, uploads two 512 KiB objects, then expects an extra 1 KiB upload to fail and not create an object. Update/clear changes quota from 512 KiB to 2 MiB, clears it, and confirms large upload succeeds without a quota. Delete operations and batch delete verify freed quota permits later uploads. Usage/statistics tests assert exact current usage, remaining quota, and percentage fields. The quota-check test checks PUT and DELETE decision responses without necessarily performing the operation.

Multi-bucket tests assert quotas and usage are independent between buckets. Error-handling and HTTP endpoint tests cover invalid quota type `SOFT` and nonexistent bucket errors. The normal-user permissions test creates a user, attaches `readwrite`, confirms reads of quota and stats succeed, and confirms set/clear are denied. Copy and multipart tests validate quota enforcement for S3 copy and multipart complete paths.

## State And Persistence Behavior

Quota config is persisted in the RustFS test environment through admin APIs. Usage state is derived from actual S3 objects in buckets. Tests mutate buckets by uploading, deleting, copying, and completing multipart uploads, then query stats to ensure quota accounting reflects those changes. `cleanup_bucket` lists and deletes objects before deleting the bucket, but some multi-bucket cleanup paths delete buckets directly and assume test objects or bucket-delete semantics allow cleanup.

Multipart behavior is important: parts may upload successfully, but quota enforcement is expected at complete time for an over-quota object. The test verifies the completed object does not exist after a failed complete.

## Dependencies And Integration Points

The file depends on local `common` helpers including `RustFSTestEnvironment`, `awscurl_*`, `awscurl_available`, and logging. It uses `aws_sdk_s3::Client`, AWS SDK S3 types for copy, delete, and multipart, `serde_json`, `uuid`, `serial_test`, and `tracing`. It is not part of the protocol runner; it is a separate integration-test module for admin quota and S3 behavior.

## Risks And Edge Cases

The tests are skipped silently when `awscurl` is missing, so CI environments without that binary lose quota admin coverage. Several helper methods detect admin errors by checking whether the response string contains `"error"`, which may be brittle if successful payloads include that substring or error payload shapes change. `object_exists` falls back to string matching for 404/NotFound and then service-error inspection, which is pragmatic but broad.

Fixed exact usage assertions assume no compression, metadata overhead, or delayed accounting; they validate logical object byte counts. Multipart tests upload two 5 MiB parts after a 5 MiB existing object under a 10 MiB quota, expecting complete failure. If enforcement moves earlier to part upload, the test shape may need adjustment while preserving the quota property.

## Test Signals

Signals include exact quota values from GET, S3 upload success/failure, object existence after failed writes/copies/completes, exact usage and remaining quota stats, quota-check `allowed` and `remaining_quota` fields, independent per-bucket usage, admin error codes for invalid type and nonexistent bucket, normal-user read-versus-write permission boundaries, copy quota enforcement, batch-delete freeing quota, and multipart complete enforcement.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/quota_test.rs -->
