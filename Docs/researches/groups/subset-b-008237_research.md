# subset-b-008237 research

Grouped research for the RustFS e2e test files listed in work item `subset-b-008237`. Each section is delimited for deterministic reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/conditional_writes.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/reliant/conditional_writes.rs

Purpose: regression coverage for S3 conditional writes against a live RustFS server at `http://localhost:9000`. The tests validate `If-Match` and `If-None-Match` behavior for ordinary `PutObject` requests and `CompleteMultipartUpload`, including object-exists and object-missing cases.

Important APIs and functions: `create_aws_s3_client` builds an AWS SDK S3 client with static RustFS credentials, path-style addressing, and local endpoint override. `setup_test_bucket` creates `api-test` and tolerates `BucketAlreadyExists`. `generate_test_data` creates deterministic byte payloads; `upload_object_with_metadata` uploads and returns the response ETag; `cleanup_objects` best-effort deletes test keys; `generate_test_key` produces timestamped object keys.

Control flow: each ignored serial Tokio test creates the client and bucket, seeds object state, performs conditional write calls through AWS SDK builders, and checks either success or `SdkError::ServiceError` metadata. `test_conditional_put_okay` verifies matching `If-Match` and nonmatching `If-None-Match` succeed. `test_conditional_put_failed` verifies nonmatching `If-Match` and matching `If-None-Match` fail with `PreconditionFailed`. `test_conditional_put_when_object_does_not_exist` expects wildcard `If-Match` to fail with `NoSuchKey` but wildcard `If-None-Match` to create the object. `test_conditional_multi_part_upload` starts a multipart upload, sends three 5 MiB parts, and validates conditional completion failures before a matching `If-Match` success.

State and persistence: state is external S3 bucket/object data in a local RustFS instance. Most keys are unique except `some_key`, so `cleanup_objects` is used before and after. Multipart state persists through the upload ID until completion; the test does not abort after failed completion attempts, so server-side handling must keep the upload reusable.

Dependencies and integration points: AWS SDK S3, `bytes::Bytes`, `serial_test`, Tokio, RustFS S3 API, conditional request headers, ETag semantics, and multipart completion.

Risks: all tests are ignored and require a pre-running server, so CI will not catch regressions unless ignored tests are explicitly enabled. Bucket reuse can leak prior data if cleanup fails. The multipart test reuses the same `CompletedMultipartUpload` after failed completion calls, which depends on the server preserving upload state after precondition failure. `setup_test_bucket` does not accept `BucketAlreadyOwnedByYou`, unlike nearby tests.

Test signals: positive and negative assertion coverage for precondition matching, wildcard semantics for missing objects, `PreconditionFailed` error metadata, and multipart conditional completion.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/conditional_writes.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/get_deleted_object_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/reliant/get_deleted_object_test.rs

Purpose: live-server regression tests for deleted or nonexistent object reads. The file documents a prior failure mode where `GetObject` on a deleted object surfaced as a networking error instead of a structured S3 `NoSuchKey`.

Important APIs and functions: `create_aws_s3_client` creates a path-style AWS SDK client for localhost RustFS. `setup_test_bucket` creates `test-get-deleted-bucket` and accepts both `BucketAlreadyExists` and `BucketAlreadyOwnedByYou`. Tests use `put_object`, `get_object`, `delete_object`, and `head_object`, then inspect `SdkError::ServiceError` and S3 error metadata.

Control flow: `test_get_deleted_object_returns_nosuchkey` uploads a key, verifies it can be fetched, deletes it, then asserts `get_object` returns a service error whose S3 error is `NoSuchKey`. `test_head_deleted_object_returns_nosuchkey` uploads and deletes, then accepts either `NoSuchKey` or `NotFound` for `HeadObject`. `test_get_nonexistent_object_returns_nosuchkey` calls `GetObject` for a never-created key. `test_multiple_gets_deleted_object` repeats the post-delete `GetObject` path five times to catch unstable state or race behavior.

State and persistence: object state lives in the local RustFS bucket. Tests use fixed keys in a fixed bucket, so serial execution and cleanup reduce interference but do not fully isolate between interrupted runs. Deletes are normal S3 deletes without explicit versioning.

Dependencies and integration points: AWS SDK S3 error classification, RustFS object deletion path, HTTP error serialization, `tracing` test logging, and `serial_test` for live-server serialization.

Risks: tests are ignored and depend on a manually running RustFS server. Several tests do not delete the bucket or ensure fixed keys are absent before setup, so stale state could affect the initial existence path. The code checks exact SDK service-error classification and will intentionally fail if transport/protocol errors leak out of RustFS.

Test signals: verifies deleted-object and never-existed-object reads return S3 service errors, not networking errors; verifies repeated reads remain stable after deletion; separately covers `GET` and `HEAD` behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/get_deleted_object_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/grpc_lock_client.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/reliant/grpc_lock_client.rs

Purpose: a no-auth gRPC lock client used by distributed lock e2e tests. It adapts RustFS `node_service` lock RPCs to the `rustfs_lock::LockClient` trait so `NamespaceLock` can be exercised over real tonic channels without production auth plumbing.

Important APIs and types: `GrpcLockClient { addr }` stores a remote endpoint. `new` constructs it. `get_client` uses `rustfs_ecstore::rpc::node_service_time_out_client_no_auth`. `create_unlock_request` reconstructs a minimal `LockRequest` from a `LockId` for unlock-like RPCs. `build_lock_info` deserializes server-provided `LockInfo` JSON or synthesizes fallback lock info from the request.

Control flow: `acquire_lock` serializes a `LockRequest` to JSON in `GenerallyLockRequest.args`, calls `lock`, and maps success or server error text to `LockResponse`. `acquire_locks_batch` serializes many requests, calls `lock_batch`, and aligns returned results by index, producing explicit failures for missing entries. `release`, `refresh`, and `force_release` serialize the minimal request and call `un_lock`, `refresh`, or `force_un_lock`, turning `error_info` into `LockError`. `release_locks_batch` calls `un_lock_batch` and returns booleans aligned to input lock IDs. `check_status` has no direct remote status endpoint; it probes by attempting an exclusive lock and immediately releasing it if successful, otherwise returns generic acquired lock info. `get_stats` returns default stats with `last_updated`; `is_online` sends `PingRequest`; `is_local` is always false.

State and persistence: the client owns no lock state beyond the endpoint string. Remote lock state lives in the server-side `LockClient` implementation reached through gRPC. Fallback `LockInfo` timestamps are local approximations, not persisted facts.

Dependencies and integration points: `rustfs_lock` trait and types, `rustfs_protos::node_service`, tonic `Request`, serde JSON serialization, no-auth RPC connection helper, and `tracing`.

Risks: status probing can briefly acquire and release a lock, which can perturb state and is only approximate. Unlock/refresh/force-release requests use default owner/type/TTL fields because the RPC interface requires a full `LockRequest`; server behavior must rely on `lock_id`. Batch response length mismatches degrade to failures but may hide server-side ordering bugs. Fallback lock info can mask serialization incompatibility.

Test signals: consumed by `lock.rs` tests for quorum behavior, batch acquire/release, lock-id preservation, missing release errors, and health checks over live gRPC channels.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/grpc_lock_client.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/grpc_lock_server.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/reliant/grpc_lock_server.rs

Purpose: a minimal tonic `NodeService` implementation for lock tests. It exposes only ping and lock-related RPCs backed by an injected `Arc<dyn LockClient>`, while every unrelated storage/admin RPC returns `Status::unimplemented("lock-only test server")`.

Important APIs and types: `ResponseStream<T>` is the stream type required by generated service methods. `lock_result_from_response`, `lock_result_from_error`, and `lock_result_from_release` normalize `rustfs_lock::LockResponse` or booleans into protobuf `GenerallyLockResult`. `MinimalLockNodeService` owns a lock client and implements `node_service_server::NodeService`. `spawn_lock_server` binds `127.0.0.1:0`, wraps the service in `NodeServiceServer`, serves a `TcpListenerStream`, and returns an HTTP endpoint string plus Tokio task handle.

Control flow: `ping` returns a flatbuffer payload containing `pong`. `lock`, `un_lock`, `force_un_lock`, and `refresh` decode JSON `LockRequest` from `GenerallyLockRequest.args`, call the corresponding `LockClient` method, and return a `GenerallyLockResponse` with success, error text, and optional serialized `LockInfo`. Decode failures are represented as successful gRPC responses with `success=false` rather than tonic errors. `lock_batch` and `un_lock_batch` prefill per-input failure results, decode valid JSON entries, call batch trait methods once for valid requests, then map batch results back to original indices.

State and persistence: server state is delegated entirely to the injected `LockClient`, normally a `LocalClient` with a `GlobalLockManager` or a test `FailingClient`. The server itself only owns the trait object and listener task. Lock state is in-memory and lives until the spawned task is aborted or the backing manager drops.

Dependencies and integration points: generated `rustfs_protos::proto_gen::node_service`, `rustfs_lock`, serde JSON, flatbuffers ping model, tonic server, Tokio TCP listener, and `tokio_stream`.

Risks: the implementation must satisfy the full generated `NodeService` trait, so protocol additions may break compilation until new methods are stubbed. Returning application errors inside OK gRPC responses mirrors existing node-service behavior but can obscure transport failures. Batch methods depend on returned result ordering from the backing client. The server has no graceful shutdown handle beyond aborting the task.

Test signals: enables local multi-node gRPC lock tests without full RustFS nodes. The unimplemented methods also ensure accidental non-lock RPC use fails clearly.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/grpc_lock_server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/head_deleted_object_versioning_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/reliant/head_deleted_object_versioning_test.rs

Purpose: live-server regression coverage for `HeadObject` when bucket versioning is enabled and the latest version is a delete marker. It addresses a prior behavior where RustFS returned `200 OK` instead of a missing-object response.

Important APIs and functions: `create_aws_s3_client` builds the localhost AWS SDK client. `setup_test_bucket` creates `test-head-deleted-versioning-bucket`, accepts existing-bucket errors, then enables versioning with `put_bucket_versioning` and `VersioningConfiguration { status: Enabled }`. The single test uses `put_object`, `delete_object`, and `head_object`.

Control flow: the test initializes tracing, creates/enables the bucket, uploads `test-head-deleted-versioning.txt`, deletes it to create a delete marker, then performs `HeadObject` without an explicit version ID. It asserts a service error and accepts `NoSuchKey`, `NotFound`, or raw `404` error codes.

State and persistence: the important persisted state is bucket versioning plus the delete marker produced by the delete operation. Because the bucket and key are fixed and versioning is never suspended or cleaned up, previous runs can leave historical versions behind. The test relies on latest-version semantics, so historical versions should not make the unversioned `HEAD` succeed if delete-marker handling is correct.

Dependencies and integration points: AWS SDK S3 versioning types, RustFS versioned object metadata/delete-marker logic, error metadata mapping for `HEAD`, `serial_test`, and live localhost server setup.

Risks: ignored by default and dependent on external RustFS. The broad accepted error-code set improves compatibility but reduces precision. The fixed bucket can accumulate versions across runs.

Test signals: validates unversioned `HEAD` observes the current delete marker and reports missing-object semantics instead of exposing an older live version.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/head_deleted_object_versioning_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/head_tls_bodyless_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/reliant/head_tls_bodyless_test.rs

Purpose: regression coverage for wire-level `HEAD` responses over TLS/HTTP2. It verifies missing-object `HEAD` returns `404` with no body bytes, preventing HTTP/2 DATA frames after headers that clients report as protocol errors.

Important APIs and functions: `generate_tls_bundle` writes self-signed cert/key files into the test TLS directory. `local_https_h2_client` creates a reqwest client with compression disabled and invalid certs accepted. `signed_empty_request` constructs an HTTP request, signs it with RustFS SigV4 using `UNSIGNED_PAYLOAD`, and sends it through reqwest. `ensure_bucket_exists` uses signed `HEAD` and `PUT` bucket requests. `wait_for_tls_server_ready` polls the root endpoint. `start_tls_rustfs_server` launches the RustFS binary with `RUSTFS_TLS_PATH` and explicit address/credentials.

Control flow: the test creates a temporary `RustFSTestEnvironment`, generates TLS material, starts RustFS as HTTPS, waits for readiness, ensures the bucket exists, then performs a signed `GET` and signed `HEAD` for the same missing object. The `GET` path must return `404` with an XML body containing `NoSuchKey` or `NoSuchObject`. The `HEAD` path must return `404`, use HTTP/2, and yield an empty byte body.

State and persistence: state is confined to the temporary RustFS environment, temp storage, generated TLS files, and child process stored on the environment. No object is created for the missing key.

Dependencies and integration points: test harness common utilities, RustFS binary launch, rcgen, reqwest, HTTP/2, SigV4 signer, S3 body type, Tokio fs/time, and RustFS TLS configuration.

Risks: this is not ignored, but it requires a buildable RustFS binary and local process spawning. The client currently accepts invalid certs even though a CA PEM is produced. Readiness polling treats any successful root `GET` as ready, which depends on root endpoint behavior. It explicitly asserts HTTP/2 for `HEAD`, so client/server protocol negotiation changes can fail the test.

Test signals: compares `GET` error body behavior with `HEAD` bodylessness for the same missing object and validates the actual transport protocol version.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/head_tls_bodyless_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/lifecycle.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/reliant/lifecycle.rs

Purpose: live-server tests for S3 bucket lifecycle configuration acceptance and expiration behavior.

Important APIs and functions: `create_aws_s3_client` builds the localhost AWS SDK S3 client. `setup_test_bucket` creates `test-basic-bucket` and tolerates existing-bucket strings. `test_bucket_lifecycle_configuration` uses `BucketLifecycleConfiguration`, `LifecycleRule`, `LifecycleRuleFilter`, and `LifecycleExpiration`. `test_bucket_lifecycle_accepts_zero_days` verifies lifecycle rules with `days(0)` are accepted.

Control flow: the expiration test uploads a target object and an untouched object, confirms both exist, creates an enabled lifecycle rule with a prefix matching only the target key and an expiration date set to yesterday midnight UTC, stores the config, verifies the rule can be read back, then polls up to 150 seconds for the target object to become `NoSuchKey`. It finally asserts the nonmatching key still exists. The zero-days test writes a rule with prefix `zero-days/` and expiration `days=0`, expecting the server to accept the configuration without immediate object assertions.

State and persistence: lifecycle rules persist on `test-basic-bucket`, objects persist until lifecycle scanner deletes them or manual cleanup occurs. The first test relies on RustFS background scanner timing and comments that default scanner interval is 60 seconds plus jitter.

Dependencies and integration points: AWS SDK lifecycle types, chrono UTC date handling, Tokio time polling, RustFS lifecycle scanner, bucket metadata persistence, and `serial_test`.

Risks: ignored by default and needs live server plus background lifecycle processing. Fixed bucket and keys can interact with prior lifecycle config. Polling for 150 seconds is expensive and still timing-sensitive. String-based existing-bucket error detection is less precise than service-error code checks.

Test signals: confirms lifecycle config round trip, immediate expiration via past date, prefix scoping, and acceptance of zero-day expiration rules.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/lifecycle.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/lock.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/reliant/lock.rs

Purpose: local async tests for distributed namespace locking over gRPC-backed lock clients. They verify quorum behavior, health reporting, batch lock operations, lock-ID preservation, and split read/write quorum semantics.

Important APIs and types: `test_resource` returns a stable `ObjectKey`. `FailingClient` implements `rustfs_lock::LockClient` by failing acquisitions and reporting offline. `failing_grpc_client` wraps `FailingClient` behind `spawn_lock_server` and `GrpcLockClient`. Tests exercise `GlobalLockManager`, `LocalClient::with_manager`, `NamespaceLock::with_clients`, `NamespaceLock::with_clients_and_quorum`, lock guards, `LockRequest`, `LockType`, and gRPC helper modules.

Control flow: `test_distributed_lock_4_nodes_grpc` starts four in-memory lock managers behind four gRPC servers, acquires a write lock with owner A, verifies owner B cannot get the lock, releases A, verifies B can acquire, and checks health shows four connected nodes. `test_distributed_lock_2_nodes_grpc_read_survives_failed_node` combines one healthy and one failing gRPC node with quorum two, expecting read lock success but write lock failure. `test_grpc_lock_client_batch_acquire_and_release` validates batch acquisition and release for two resources. `test_grpc_lock_client_uses_request_lock_id_and_reports_missing_unlock` ensures the server preserves request lock IDs and reports a second release as missing. `test_distributed_lock_4_nodes_grpc_read_write_quorum_split_with_two_failed_nodes` expects read success and write failure with two healthy/two failed nodes.

State and persistence: lock state is in-memory inside `GlobalLockManager` instances. gRPC servers are bound to ephemeral ports and aborted at test end. Guards own release state and are dropped or explicitly released.

Dependencies and integration points: `rustfs_lock`, local and gRPC lock client/server test shims, Tokio tasks/time, async trait implementation, and in-memory lock managers.

Risks: tests use fixed sleeps for server startup. Aborting server handles is abrupt. The quorum expectations encode read/write quorum policy details that may change with lock algorithm changes. `FailingClient` only simulates acquisition failure and offline health in a narrow way.

Test signals: strong unit/e2e hybrid signal for distributed lock quorum, contention, release, batch RPC shape, request lock ID semantics, and degraded-node behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/lock.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/mod.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/reliant/mod.rs

Purpose: module aggregator for the `reliant` test suite. It declares the child test modules that depend on live RustFS services, local lock shims, or specialized e2e harness behavior.

Important APIs and functions: this file exposes no functions or types. It contains `mod` declarations for `conditional_writes`, `get_deleted_object_test`, `grpc_lock_client`, `grpc_lock_server`, `head_deleted_object_versioning_test`, `head_tls_bodyless_test`, `lifecycle`, `lock`, `node_interact_test`, and `sql`.

Control flow: Rust module loading pulls these files into the test crate. Each child file gates itself with `#![cfg(test)]` or defines tests, so this module is a compile-time integration point rather than a runtime dispatcher.

State and persistence: no runtime state or persistence. The presence of module declarations controls compilation and availability of test helpers, including the gRPC lock client/server modules used by `lock.rs`.

Dependencies and integration points: the e2e test crate module tree. It is the bridge between the crate root and the reliant tests.

Risks: adding a source file under `reliant` without updating this file means it will not compile or run. Removing or renaming child files without updating declarations breaks the test crate. It intentionally includes helper modules (`grpc_lock_client`, `grpc_lock_server`) that are not standalone tests but are required by `lock.rs`.

Test signals: no direct assertions; its signal is compile-time inclusion of the listed test modules.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/node_interact_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/reliant/node_interact_test.rs

Purpose: ignored live-server tests for direct RustFS node-service gRPC interactions. The tests exercise lower-level cluster RPCs such as ping, volume operations, directory walking, file reads, and storage info.

Important APIs and functions: each test creates a `node_service_time_out_client` for `http://localhost:9000` with `TonicInterceptor::Signature(gen_tonic_signature_interceptor())`. `ping` constructs and decodes flatbuffer `PingBody`. `make_volume`, `list_volumes`, `read_all`, and `storage_info` call generated node-service RPCs. `walk_dir` serializes `WalkDirOptions` with MessagePack and consumes a streaming `WalkDirResponse` into `MetacacheWriter`/`MetacacheReader` via a Tokio duplex stream.

Control flow: tests are independent and ignored. `ping` validates the request flatbuffer then prints decoded response details. Volume tests send simple requests and print success/error or decoded `VolumeInfo`. `walk_dir` computes a disk path from `RUSTFS_DISK_PATH` or workspace target data, sends a `WalkDirRequest`, spawns one task to convert streaming JSON `MetaCacheEntry` responses into metacache format, and another to read/print entries. `read_all` prints response data for `format.json`; `storage_info` deserializes response bytes with `rmp_serde`.

State and persistence: server-side disk/volume state is external to the tests and addressed by disk names or filesystem paths. `make_volume` mutates the server by creating volume `dandan`. `walk_dir` reads from the configured data directory. No cleanup is performed.

Dependencies and integration points: RustFS ecstore RPC client, generated node-service protos, flatbuffers models, rmp-serde, filemeta metacache reader/writer, workspace test common path helper, tonic streaming, and Tokio tasks.

Risks: heavily environment-dependent and ignored. Hard-coded disk/volume names and lack of cleanup make tests unsuitable for isolated repeatability. Many assertions are weak or absent, with output printed for manual inspection. `walk_dir` unwraps JSON decoding in a spawned task and only joins tasks without inspecting panic results deeply.

Test signals: primarily smoke/manual diagnostics for signed node-service connectivity and serialization formats rather than strict automated assertions.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/node_interact_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/sql.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/reliant/sql.rs

Purpose: ignored live-server tests for S3 SelectObjectContent over CSV and JSON objects. The suite checks basic filtering, projected output, limit/order behavior, and failure modes.

Important APIs and functions: `create_aws_s3_client` and `setup_test_bucket` provide local S3 setup. `upload_test_csv` and `upload_test_json` write deterministic fixture objects. `process_select_response` drains the AWS SDK `SelectObjectContentOutput` event stream, concatenating `Records` payload bytes until `End` and ignoring stats/progress/continuation events.

Control flow: CSV tests upload the fixture, build `InputSerialization::csv` with `FileHeaderInfo::Use`, build default CSV output serialization, call `select_object_content`, and inspect the concatenated record text. The basic test filters `age > 28`; the aggregation-named test projects `name, age` for `age >= 25`; the limit test expects exactly two non-empty output lines; the order-by test checks the top two age records. The JSON test uses `JsonInput` of type `Document`, projects fields from alias `s`, and checks matching names/ages. Error tests assert SDK send failure for an invalid column and nonexistent object.

State and persistence: fixture objects persist in `test-sql-bucket` under fixed keys. Tests are serial but do not clean up, so later runs overwrite the same fixtures. Select processing is streaming and does not persist state.

Dependencies and integration points: AWS SDK S3 select-object types, RustFS select SQL parser/executor, event-stream framing, CSV/JSON input and output serializers, Tokio multi-thread runtime, and `serial_test`.

Risks: ignored by default and requires a live server with S3 Select support. Assertions use substring matching and do not fully validate row order or exact serialization for most tests. `JsonType::Document` is used with newline-delimited JSON-like content, which may depend on RustFS interpretation. Error handling only checks that failures occur, not exact error codes.

Test signals: validates end-to-end select query execution and event-stream decoding for common CSV/JSON paths plus invalid-query and missing-object failure paths.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/sql.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/replication_extension_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/replication_extension_test.rs

Purpose: comprehensive e2e coverage for RustFS bucket replication and site replication admin extensions. It starts real single-node or dual-node `RustFSTestEnvironment` instances and validates remote target management, replication-check behavior, bucket object replication, site replication state propagation, IAM policy/user/group replication, and service-account replication.

Important APIs and types: `signed_request` and `signed_request_with_session_token` create SigV4-signed reqwest calls to S3/admin APIs. `ReplicationResetStatusResponse` and `ReplicationResetStatusTarget` parse replication reset status. Helpers cover XML credential parsing (`extract_xml_tag`, `parse_assume_role_credentials`), remote target setup/list/remove, bucket replication XML generation, versioning enablement, admin user/group/policy calls, service-account creation/listing/account info, site replication add/info/edit/status/remove/state-edit/resync, polling waiters, and `build_replication_pair`.

Control flow: tests create isolated RustFS environments, create buckets, enable versioning, add remote targets, install replication configs, mutate objects/admin state, and poll until remote state matches expectations. Validation tests reject missing versioning, missing replication configs, invalid buckets, same-deployment targets, invalid target URLs, missing ARN/update targets, list/remove misuse, and object-lock incompatibility. Functional tests cover replication-check success, target removal after replication deletion, fan-out to multiple targets, sequential multi-bucket replication, runtime target cache refresh through `BucketTargetSys::delete`, site resync start/cancel/restart and reset IDs, site edit/status peer state and ILM expiry replication flags, remove-all, fresh-versus-stale state edit timestamps, bucket versioning object replication, policy-backed user and group access on replicated sites, accountinfo policy round-trip for service accounts, multiple service-account propagation, and STS-session-created service accounts when `awscurl` is available.

State and persistence: state is mostly temporary but real: RustFS processes, bucket metadata, versioning configs, replication targets, bucket replication XML, object data, site replication peer records, reset status, users, groups, policies, service accounts, and in-memory target cache. Pollers generally use 250 ms sleeps up to 40 attempts or 30-second object waits.

Dependencies and integration points: `crate::common` process harness and HTTP helpers, AWS SDK S3, reqwest, `rustfs_madmin` admin models, `rustfs_signer`, S3 XML/JSON admin APIs, STS via optional `awscurl`, `BucketTargetSys`, Tokio timing, and `serial_test`.

Risks: tests are integration-heavy, serial, and can be slow/flaky if background replication timing changes. Many assertions inspect response-body substrings, so error wording changes can fail tests. `extract_xml_tag` is intentionally simple and not a robust XML parser. Direct `BucketTargetSys::get().delete` reaches into global runtime cache and is appropriate only in tests. The STS service-account test silently skips when `awscurl` is absent, reducing coverage in minimal environments.

Test signals: this file provides high-value end-to-end signal across replication validation, replication data plane, admin API behavior, peer-state convergence, stale update rejection, identity/policy propagation, and service-account hierarchy replication.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/replication_extension_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/snowball_auto_extract_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/snowball_auto_extract_test.rs

Purpose: e2e tests for Snowball auto-extract behavior during S3 `PutObject` tar uploads. The suite validates MinIO-compatible metadata headers, standard `x-amz-meta-*` headers, prefix normalization, directory marker handling, invalid-entry tolerance, path traversal rejection, and header precedence.

Important APIs and functions: `build_test_archive` creates an in-memory tar with directories, an empty directory, a nested file, and a root file. `build_archive_with_invalid_entry` appends a valid file followed by an entry with an overlong name. `build_archive_with_parent_dir_entry` manually constructs a tar record for `../{victim_bucket}/evil-injected.txt` to test traversal protection. Tests use `RustFSTestEnvironment`, AWS SDK S3 `ByteStream`, `tokio_tar`, and `ProvideErrorMetadata` for error-code assertions.

Control flow: each serial test starts a temporary RustFS server, creates buckets, uploads tar data with extraction metadata, then uses `GetObject`, `HeadObject`, or `ListObjectsV2` to verify extracted results. Prefix tests confirm `/tenant-a/`, `tenant-b`, and standard `/tenant-standard/` prefixes normalize into object keys. Directory tests assert markers are created by default but skipped when ignore-dirs is true. Invalid-entry tests assert valid files extract while invalid entries are ignored when ignore-errors is true. The traversal test expects `InvalidArgument` and confirms the victim bucket has no injected object. Header precedence verifies exact `x-amz-meta-minio-snowball-prefix` wins over a suffix-matching fallback header.

State and persistence: state is isolated to per-test temporary RustFS servers and buckets. Auto-extraction mutates object storage by creating objects from tar entries; directory markers are zero-length objects unless ignored. Tests explicitly stop the server at the end.

Dependencies and integration points: test harness common utilities, AWS SDK S3, tar archive parsing path, Snowball metadata option parsing, object namespace safety checks, list/head/get APIs, and serial execution.

Risks: tests rely on actual server process startup and tar parsing behavior. Some invalid archive construction depends on tar header details. Manual traversal archive crafting is valuable but narrow: it tests parent directory traversal across buckets, not every path normalization edge. Error-code assertions expect `InvalidArgument` or `NotFound` exactly.

Test signals: strong e2e signal for auto-extract compatibility, safety, option parsing, prefix precedence, and partial extraction behavior under ignored errors.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/snowball_auto_extract_test.rs -->
