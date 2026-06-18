<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/tests/integrations/test_cdc.rs -->
# sources/storage-engines/tikv/components/cdc/tests/integrations/test_cdc.rs

## Purpose
This is the broad CDC integration regression suite for TiKV's change-data service. It drives a simulated Raftstore cluster through transactional KV, raw KV, region topology, timestamp, old-value, filter, flashback, and overlapped-write scenarios, then asserts the `ChangeData` gRPC stream emits the expected `cdcpb::Event` rows, resolved-ts messages, and region errors. The same core tests are run against `ApiVersion::V1` and `ApiVersion::V2` through `test_kv_format_impl!`, with ApiV2 keys deliberately using the txn/raw key prefixes required by the test format.

## Important APIs, Types, And Functions
The file consumes `TestSuite`, `TestSuiteBuilder`, `new_event_feed`, and `new_event_feed_v2` from the CDC test module. It uses TiKV RPC requests and protobuf event types such as `ChangeDataRequest`, `Event_oneof_event`, `EventLogType`, `EventRowOpType`, `ExtraOp`, `ChangeDataRequestKvApi`, `Mutation`, `PrewriteRequest`, `CommitRequest`, and `BatchRollbackRequest`. It also uses cluster control helpers from `test_raftstore`, PD TSO access through `PdClient`, `ConcurrencyManager` memory locks, `Task::Validate`/`Validate` hooks into the CDC endpoint, and `CDC_RESOLVED_TS_ADVANCE_METHOD` for resolved-ts mode verification.

The tests cover these major behaviors:

- Subscription lifecycle: `test_cdc_basic`, `test_cdc_not_leader`, `test_region_split`, `test_duplicate_subscribe`, `test_cdc_cluster_id_mismatch`, and `test_cdc_stale_epoch_after_region_ready`.
- Initial/incremental scans: `test_cdc_scan`, `test_cdc_rawkv_scan`, `test_cdc_scan_ignore_gc_fence`, and `test_prewrite_without_value`.
- Event streaming for txn/raw operations: basic prewrite/commit/rollback, raw put/CAS/delete, batch-size splitting, and 1PC committed events.
- Old-value extraction: `test_old_value_basic`, multi-changefeed old-value behavior, cache-hit counters, pessimistic old-value reads, and 1PC old values.
- Resolved timestamp behavior: TSO failures, concurrency-manager locks, cluster upgrading, learner peers, partial subscriptions, region creation, term changes, and flashback blocking.
- Filtering: `filter_loop`, key-range filtering, txn-source rollback behavior, and v2 stream multiplexing.
- Edge cases around missing writes, GC fences, overlapped rollback/write records, and stale CDC lock-tracker state.

## Control Flow
Most tests follow the same structure. A simulated cluster is built, a `ChangeDataRequest` is created with region epoch and TiCDC feature headers, the request is sent through a duplex gRPC stream, and the first event is usually asserted to be `Initialized`. The test then mutates the store through TiKV RPCs or cluster topology operations and repeatedly calls the `receive_event` closure until the relevant row or resolved-ts signal appears. Region leadership and split tests use `Task::Validate(Validate::Region(...))` to inspect the endpoint delegate after stream registration or after an error.

The scan tests preload MVCC versions before subscription, then assert CDC backfill order and batching before `Initialized`. `checkpoint_ts` is varied to make only later versions appear. RawKV tests set `kv_api` to `RawKv`, flush causal timestamps when needed, and assert `Committed` rows rather than transactional prewrite/commit pairs. Old-value tests enable `ExtraOp::ReadOldValue` even though some assertions document that the field is now effectively ignored for downstream behavior, then check `old_value` on prewrite or committed rows. Resolved-ts tests keep resolved-ts events instead of filtering them out and assert monotonicity, blocking at memory locks or flashback, and eventual advancement after unblock.

Several late-file tests are bug reproductions. They construct overlapping timestamp relationships where one transaction's `commit_ts` equals another transaction's `start_ts`, rollback a secondary key so no CF_WRITE rollback is generated, then ensure CDC remains active when a later prewrite encounters a stale lock-tracker entry. `test_verify_overlapped_write_skips_cf_write` is a minimal storage-side confirmation of that skipped CF_WRITE behavior.

## State And Persistence Behavior
The suite mutates real in-memory test engines through TiKV RPC paths, so state exists in MVCC lock/write/default column families, Raftstore metadata, PD region metadata, and CDC endpoint delegate state. Persistent behaviors under test include lock insertion/removal, committed writes, rollback writes or omitted rollback writes, GC fence effects, raw KV entries, flashback deletes, and resolved-ts advancement derived from PD TSO and concurrency manager state. CDC-specific state includes registered downstreams, per-region delegates, old-value cache counters, lock tracking, feature-gated resolved-ts strategy, request key ranges, and stream multiplexing request IDs.

## Dependencies And Integration Points
The file is tightly integrated with the simulated Raftstore stack, TiKV client protobufs, CDC endpoint scheduler, PD mock client, causal timestamp provider, concurrency manager, and API-version key encoders. The gRPC stream is the public integration surface, while `Task::Validate` is an internal test-only inspection path. Several tests rely on exact behavior from the storage transaction layer, including pessimistic lock/prewrite semantics, `check_txn_status`, async-commit-like overlapped rollback handling, 1PC responses, and flashback RPCs.

## Risks
The suite is timing sensitive. It uses sleeps, receive timeouts, and retry loops around registration and resolved-ts movement, so raft scheduling delays can cause flakiness if intervals change. Many assertions depend on test cluster defaults such as batch scan size set in `TestSuiteBuilder`, feature gate versions, generated TSO ordering, and key prefixes under ApiV2. Some tests use direct timestamps like `10`, `15`, or relationships like `start_ts == commit_ts`; changing timestamp allocation or transaction validation can break them in non-obvious ways. The overlapped-write bug tests are especially subtle because the expected storage behavior is absence of a rollback write, so the CDC signal is mostly "delegate remains active".

## Test Signals
This file is itself an integration test signal for CDC. It verifies event types, keys, values, old values, commit/start timestamps, region errors (`not_leader`, `epoch_not_match`, `cluster_id_mismatch`, duplicate request), resolved-ts monotonicity and region sets, cache hit/miss counters, downstream delegate lifecycle, and active/failed delegate status. Coverage is broad across V1/V2 transactional CDC and RawKV, but it is still a simulated-cluster suite rather than a real multi-node deployment test.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/tests/integrations/test_cdc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/tests/integrations/test_flow_control.rs -->
# sources/storage-engines/tikv/components/cdc/tests/integrations/test_flow_control.rs

## Purpose
This integration test verifies CDC flow control when the endpoint's memory quota is too small for a pending event. It proves normal events are delivered while under quota, oversized events produce a congested error, and the affected region delegate is removed.

## Important APIs, Types, And Functions
The test uses `TestSuiteBuilder::memory_quota`, `new_event_feed`, `Task::Validate`, `Validate::Region`, `MemoryQuota` indirectly through the CDC service, and transactional KV RPC helpers from `TestSuite`. The event assertions inspect `Event_oneof_event::Entries`, `Event_oneof_event::Error`, `EventLogType::Initialized`, `EventLogType::Prewrite`, and the `congested` error field.

## Control Flow
`test_cdc_congest` starts a single-node server cluster with a 1 KiB CDC memory quota and subscribes to region 1. It first receives the mandatory `Initialized` event. It then prewrites a value of half the quota and expects a normal `Prewrite` row. A second prewrite with a value twice the quota is expected to return one CDC error event with `has_congested()`. Finally it schedules `Validate::Region` and checks the delegate is gone.

## State And Persistence Behavior
The test writes MVCC locks through real prewrite RPCs. The key persistent signal is not the written data itself but the CDC endpoint's memory-accounted event path: under-quota events remain deliverable, while an over-quota event causes endpoint-side subscription cleanup. The delegate removal is checked through endpoint scheduler state.

## Dependencies And Integration Points
It depends on the same simulated Raftstore and CDC gRPC service setup as the rest of the CDC tests. `configure_for_lease_read` is used to make timing reliable. The test integrates CDC txn-extra scheduling, memory quota enforcement, gRPC event delivery, and internal endpoint validation.

## Risks
The test assumes the encoded CDC prewrite event size tracks the chosen value size closely enough that half quota succeeds and double quota fails. Changes in event overhead, memory accounting, or quota semantics could make the threshold brittle. The delegate cleanup assertion is asynchronous and guarded by a one-second channel timeout.

## Test Signals
A passing run signals that CDC still sends `Initialized`, still allows normal prewrite delivery below quota, converts congestion to a structured CDC congested error, and removes the region delegate after congestion.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/tests/integrations/test_flow_control.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/tests/mod.rs -->
# sources/storage-engines/tikv/components/cdc/tests/mod.rs

## Purpose
This module is the shared harness for CDC integration tests. It wires CDC endpoints into simulated TiKV server clusters, exposes helpers for opening CDC event streams, and wraps common transactional/raw KV RPCs with assertions so integration tests can focus on event expectations.

## Important APIs, Types, And Functions
`init` runs CI test setup once. `ClientReceiver` wraps an optional `ClientDuplexReceiver<ChangeDataEvent>` in `Arc<Mutex<...>>` and allows tests to swap or drop streams with `replace`. `new_event_feed` opens the classic CDC duplex stream and `new_event_feed_v2` opens stream multiplexing by attaching the `features: stream-multiplexing` metadata header. Both delegate to `create_event_feed`, which returns a request sender, a `ClientReceiver`, and a `receive_event` closure that polls with `cdc::recv_timeout`, skips resolved-ts events unless requested, and restores the receiver into the mutex.

`TestSuiteBuilder` owns optional `Cluster<ServerCluster>` and memory quota settings. Its `build_with_cluster_runner` installs CDC gRPC services, txn-extra schedulers, CDC observers, memory quotas, endpoint workers, raft routers, local tablet handles, concurrency managers, and causal timestamp providers for every store. `TestSuite` exposes the built cluster, endpoint workers, observers, clients, concurrency managers, and a gRPC environment.

The helper methods include `new_changedata_request`, `must_kv_prewrite`, `must_kv_prewrite_with_source`, `must_kv_put`, `must_kv_compare_and_swap`, `must_kv_compare_and_delete`, `must_kv_commit`, `must_kv_commit_with_source`, `must_kv_rollback`, `must_check_txn_status`, pessimistic lock/prewrite/rollback helpers, `must_kv_txn_heartbeat`, async commit helpers, client lookup helpers, region context helpers, TSO/causal timestamp helpers, and flashback helpers.

## Control Flow
The builder creates one lazy CDC worker per simulated store before the cluster is run. It registers a closure in `pending_services` so each server exposes `create_change_data(cdc::Service::new(...))`, installs `CdcTxnExtraScheduler` into simulated transaction schedulers, and registers `CdcObserver` with each coprocessor host. After the cluster runner starts the cluster, it constructs `cdc::Endpoint` values with the default cluster ID, CDC/resolved-ts config, API version, PD client, raft router, local tablet, observer, store metadata, concurrency manager, security manager, memory quota, and causal-ts provider. It applies a smaller `min_ts_interval` and scan batch size for deterministic tests, then starts each endpoint worker.

The receive closure temporarily takes ownership of the gRPC receiver so only one read happens at a time. If resolved-ts filtering is disabled, it loops past resolved-ts messages until a non-resolved event is found or the stream times out.

## State And Persistence Behavior
The harness itself does not implement persistence, but all helper RPCs mutate the cluster's real test engines and assert there are no region or key errors. It stores runtime state for CDC endpoint workers, observers, per-store memory quotas, client caches, concurrency managers, and the event receiver wrapper. `stop` drains and stops endpoint workers before shutting down the cluster to avoid leaked worker threads.

## Dependencies And Integration Points
This module bridges CDC, raftstore, TiKV storage config, gRPC, PD, concurrency manager, causal timestamp, and test utilities. It depends on `OnlineConfig` behavior for config diffs, `LocalTablets::Singleton` for engine binding, `CdcRaftRouter` for raft messages, and protobuf clients for both CDC and TiKV KV APIs. Tests integrate with it through public helpers rather than constructing CDC endpoints directly.

## Risks
The harness is intentionally opinionated: it forces `min_ts_interval` to 100 ms and max scan batch size to 2, which many tests rely on. Changes here can ripple through event batching and resolved-ts assertions across the integration suite. The `receive_event` closure returns a default event on timeout or after receiver removal, so callers must distinguish default events from legitimate empty responses. The builder assumes simulated node IDs are `1..=count`.

## Test Signals
This module is exercised by every CDC integration test in the directory. Its assertions catch failed KV RPCs immediately, and its endpoint validation hooks give tests direct visibility into CDC delegates, old-value cache counters, and worker lifecycle.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/tests/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/Cargo.toml -->
# sources/storage-engines/tikv/components/cloud/Cargo.toml

## Purpose
This manifest defines the workspace `cloud` component, which provides provider-neutral cloud storage and KMS abstractions used by concrete provider crates such as AWS and Azure.

## Important APIs, Types, And Functions
As a Cargo manifest it declares package metadata and dependency surfaces rather than Rust functions. The dependencies indicate that the crate exposes async traits, structured errors, protobuf-backed config integration, futures-based streaming, metrics, URL handling, UUIDs, and TiKV utility integration. Dev dependencies include `pin-project` and a Tokio runtime for tests.

## Control Flow
Cargo uses this file to compile the `cloud` crate with Rust 2021 edition and no publishing. There are no features in this manifest. Downstream crates depend on the traits and error types exported by this crate through workspace dependency wiring.

## State And Persistence Behavior
The manifest has no runtime state. Its dependency set controls what runtime state the library can model: blob config URLs, streaming resources, metrics counters/histograms, protobuf configuration, and KMS error types.

## Dependencies And Integration Points
The most important integration points are `kvproto` for BR/cloud protobuf configuration, `prometheus` for `CLOUD_*` metrics, `tikv_util` for common utilities, `futures`/`futures-io` for async object streams, and `error_code`/`thiserror`/`derive_more` for structured errors. Provider crates import these common traits and types.

## Risks
Because this is the abstraction crate, dependency version or feature changes affect every cloud backend. `prometheus` is built with `nightly`; removing or changing that feature can affect metrics compilation. The crate uses `protobuf` 2.x with bytes support, which must stay compatible with `kvproto`.

## Test Signals
This manifest's direct test signal is compilation of the `cloud` crate and provider crates that depend on it. Dev dependencies suggest unit tests exercise async streams under Tokio.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/aws/Cargo.toml -->
# sources/storage-engines/tikv/components/cloud/aws/Cargo.toml

## Purpose
This manifest defines the TiKV AWS cloud provider crate. It implements S3 blob storage and AWS KMS support on top of the shared `cloud` abstractions.

## Important APIs, Types, And Functions
The manifest exposes one feature, `failpoints`, which enables the `fail/failpoints` dependency path used by AWS credential and S3 timeout/error tests. It pins AWS SDK crates: `aws-config = 1.8.15`, `aws-sdk-kms = 1.103.0`, and `aws-sdk-s3 = 1.126.0`, with default features disabled and selected runtime/client features. The dependency list also includes Smithy runtime crates, static credential support, Hyper/TLS transport, `cloud`, `kvproto`, metrics, logging, Tokio time, UUIDs, MD5, and futures adapters.

## Control Flow
Cargo resolves this crate as a non-published Rust 2021 workspace package. The pinned AWS SDK versions intentionally freeze transitive behavior. Tests add Smithy test utilities, HTTP body support, Tokio macros, and base64/futures utilities.

## State And Persistence Behavior
The manifest has no runtime state. It determines the available runtime capabilities of the AWS implementation: HTTPS client construction, default credential chain, hardcoded credentials, STS assume-role, KMS client, S3 multipart/object operations, MD5 checksums for object lock, and failpoint injection in tests.

## Dependencies And Integration Points
The crate integrates with the shared `cloud` crate, AWS SDK/Smithy stack, TiKV logging and metrics, `kvproto::brpb::S3` configuration, and Hyper 0.14. The `grpcio` dependency is explicitly retained to vendor/link OpenSSL consistently with TiKV's build environment even though it is not part of AWS logic.

## Risks
The AWS SDK family is pinned because unbounded transitive updates have historically changed behavior. Default features are disabled, so adding new AWS SDK usage may require explicit features. Transport versions are tied to Hyper 0.14 and Smithy connector features. The `failpoints` feature changes test behavior and should not leak into normal builds.

## Test Signals
The manifest supports unit tests in `kms.rs`, `s3.rs`, and `util.rs`, including Smithy static replay tests and failpoint-driven credential/S3 timeout tests. Successful `cargo test -p aws` validates both dependency resolution and mocked AWS protocol requests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/aws/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/aws/src/kms.rs -->
# sources/storage-engines/tikv/components/cloud/aws/src/kms.rs

## Purpose
This file implements the shared `cloud::kms::KmsProvider` trait for AWS KMS. It creates an AWS KMS client from TiKV cloud KMS config, supports either explicit AWS access keys or the default credential chain, generates AES-256 data keys, decrypts encrypted data keys, and maps AWS SDK failures into TiKV cloud error categories.

## Important APIs, Types, And Functions
`AwsKms` stores an `aws_sdk_kms::Client`, current `KeyId`, region, and endpoint. `ENCRYPTION_VENDOR_NAME_AWS_KMS` returns the provider name `"AWS"`. `new` constructs the provider using a shared HTTP client and either static credentials from `config.aws` or `util::DefaultCredentialsProvider`. `new_with_creds_client` is the injectable constructor used by tests.

The `KmsProvider` implementation exposes `name`, `decrypt_data_key`, and `generate_data_key`. `generate_data_key` calls AWS `GenerateDataKey` with `DataKeySpec::Aes256` and returns `DataKeyPair { encrypted, plaintext }`, validating plaintext as `CryptographyType::AesGcm256`. `decrypt_data_key` calls AWS `Decrypt` with the configured key ID and ciphertext blob.

Error translation is handled by `classify_generate_data_key_error`, `classify_decrypt_error`, and `classify_error`. Service errors such as not found, incorrect key, timeout, and internal errors become `ApiNotFound`, `WrongMasterKey`, `ApiTimeout`, `ApiInternal`, or generic `KmsError::Other`. Dispatch failures sourced from `CredentialsError` become `ApiAuthentication`; other dispatch failures become `ApiTimeout`; retryable SDK errors become `ApiInternal`.

## Control Flow
Construction starts from `aws_config::defaults(BehaviorVersion::latest())`, installs credentials and HTTP client, applies region and endpoint via `util`, synchronously waits for config loading through `block_on`, and builds the KMS client. Runtime operations are async KMS SDK calls followed by immediate error classification and response field extraction. The code assumes successful AWS responses contain `plaintext`/`ciphertext_blob` and unwraps those fields.

## State And Persistence Behavior
`AwsKms` is stateless apart from the configured client, key ID, region, and endpoint. It does not persist keys locally. Generated plaintext keys are returned to callers in memory, while encrypted keys are AWS ciphertext blobs suitable for persistence by higher layers. There is no local retry loop in KMS operations; retry classification is used to choose TiKV error categories, while AWS SDK retry behavior depends on SDK config.

## Dependencies And Integration Points
The file integrates AWS KMS SDK types, shared AWS util helpers, `cloud::kms` abstractions, TiKV cloud errors, and AWS credential provider traits. Tests use Smithy `StaticReplayClient` to verify request bodies and mocked JSON responses. The public re-export from `lib.rs` makes `AwsKms` the AWS KMS provider surface for the crate.

## Risks
Successful responses unwrap optional AWS fields, so malformed or partial SDK responses panic rather than returning an error. Credential-error detection reaches through dispatch connector error sources and may miss new SDK error wrapping. Wrong-master-key classification intentionally treats KMS `NotFoundException` during decrypt as `WrongMasterKey`, which is correct for restore safety but conflates missing key and incorrect key from an operator perspective.

## Test Signals
`test_aws_kms` verifies generate/decrypt requests with a static replay KMS client and validates encrypted/plaintext key content. `test_kms_wrong_key_id` verifies `IncorrectKeyException` maps to `KmsError::WrongMasterKey`. A localstack test exists but is ignored because no reliable AWS KMS backend is available in the normal test environment.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/aws/src/kms.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/aws/src/lib.rs -->
# sources/storage-engines/tikv/components/cloud/aws/src/lib.rs

## Purpose
This is the AWS provider crate root. It wires private implementation modules and re-exports the public AWS KMS and S3 types used by the rest of TiKV.

## Important APIs, Types, And Functions
The crate declares `mod kms`, `mod s3`, and `mod util`. It publicly re-exports `AwsKms` and `ENCRYPTION_VENDOR_NAME_AWS_KMS` from `kms`, and `Config`, `S3Storage`, `STORAGE_NAME`, and `STORAGE_VENDOR_NAME_AWS` from `s3`. `util` remains private implementation support.

## Control Flow
There is no runtime control flow in this file. Rust module loading compiles the three modules, and downstream code imports the re-exported provider types from the crate root.

## State And Persistence Behavior
The file has no state. Its re-export decisions define the external API boundary: callers can construct S3 storage and KMS providers but cannot directly access HTTP/credential helper functions.

## Dependencies And Integration Points
`lib.rs` is the integration point between the AWS crate and workspace consumers. It keeps the AWS utility module private while exposing only provider implementations and provider/vendor names.

## Risks
Changing re-exports is a semver-like workspace API change even though the crate is unpublished. Hiding `util` means tests or other crates must use public constructors rather than shared helpers unless they are inside this crate.

## Test Signals
The crate-root behavior is tested indirectly by compiling downstream imports and the unit tests in `kms.rs`, `s3.rs`, and `util.rs`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/aws/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/aws/src/s3.rs -->
# sources/storage-engines/tikv/components/cloud/aws/src/s3.rs

## Purpose
This file implements TiKV's AWS S3 blob storage backend. It converts `kvproto::brpb::S3` input into a typed config, constructs an AWS S3 client with static/default/assumed-role credentials, implements `BlobStorage`, `DeletableStorage`, and `IterableStorage`, and provides small-object and multipart upload support with retries, metrics, timeouts, optional MD5 checksums, SSE, ACL, storage class, prefixes, and path-style/virtual-host addressing.

## Important APIs, Types, And Functions
`Config` stores bucket config, SSE/ACL/KMS/storage-class options, optional `AccessKeyPair`, path-style flag, multipart size, object-lock MD5 flag, role ARN, and external ID. `Config::from_input` validates required bucket and secret-key fields and maps optional protobuf strings to `StringNonEmpty`. `BlobConfig::url` returns the backend URL through `BucketConf::url`.

`S3Storage` stores `Config` and `aws_sdk_s3::Client`. Public constructors are `from_input`, `new`, and `set_multi_part_size`; internal constructors include `new_with_client`, `maybe_assume_role`, `load_sdk_config`, `new_with_creds_client`, and async equivalent. Key helpers are `maybe_prefix_key`, `strip_prefix_if_needed`, and `get_range`.

`S3Uploader` owns a multipart upload session: client, bucket/key, ACL/SSE/KMS/storage-class settings, effective part size, object-lock flag, upload ID, and completed parts. Its methods include `run`, `begin`, `complete`, `abort`, `upload_part`, `upload`, and `get_timeout`. Upload errors use `UploadError`, which implements `RetryError`. Utility helpers include `try_read_exact`, `get_content_md5`, and `create_error_stream`.

Trait implementations:

- `BlobStorage::put` prefixes keys and delegates to `S3Uploader::run`; `get` and `get_part` return async blob streams.
- `DeletableStorage::delete` sends `DeleteObject` and records metrics.
- `IterableStorage::iter_prefix` paginates `ListObjectsV2`, strips configured prefixes, and yields `BlobObject` values.

## Control Flow
Construction chooses credentials first. Explicit access keys build `Credentials::from_keys`; otherwise `util::new_credentials_provider` is used. If a role ARN is configured, `maybe_assume_role` builds an STS `AssumeRoleProvider`, using current epoch seconds as session name and optional external ID/region, then creates the final S3 client from assumed-role credentials. `load_sdk_config` disables stalled stream protection, applies region/endpoint, credentials, and HTTP client, then the S3 builder applies `force_path_style`.

Reads call `GetObject`, optionally with a byte range, then convert the AWS byte stream into a `futures` async reader. `NoSuchKey` becomes an `io::ErrorKind::NotFound` stream; other SDK failures become error streams. Writes call `S3Uploader::run`: if `content_length` is no larger than the effective multipart size, the full reader is buffered and uploaded with one `PutObject`. Larger objects start multipart upload, repeatedly fill a part buffer with `try_read_exact`, retry each part upload, collect part numbers/eTags, then complete. If any part read/upload fails, it attempts an abort and returns the original error. For extremely large estimated lengths, the effective part size is increased so the part count stays under S3's 10000-part limit.

## State And Persistence Behavior
S3 object data and metadata are persisted externally in AWS S3 or compatible backends. Local state is per-client config and transient upload session state. Multipart upload state is external after `create_multipart_upload`; the local `upload_id` and `parts` vector must stay coherent until completion or abort. Object lock support adds base64 MD5 headers for puts and parts. Prefix handling is local string transformation: configured prefixes are prepended for operations and stripped from iterator results.

## Dependencies And Integration Points
The module integrates the shared `cloud::blob` traits, `kvproto::brpb::S3`, AWS config/credential/S3/STS SDKs, Smithy error types via `util::SdkError`, TiKV cloud metrics, `tikv_util::stream::retry_ext`, Tokio timeouts, `ReaderStream`, failpoints, and `md5`/`base64`. It is re-exported from `lib.rs` and is the concrete `s3` provider behind BR/cloud backup object storage.

## Risks
Small uploads buffer the entire input in memory, so callers must provide an accurate `content_length` and set multipart thresholds appropriately. `get_part` computes `off + len - 1`, so a zero-length request would underflow. Multipart abort errors are intentionally ignored after a failed upload, which can leave remote orphaned parts if abort fails. `set_multi_part_size` enforces the AWS minimum but tests bypass it by mutating config directly. Timeouts are fixed at 15 minutes unless failpoints override them. The code preserves `"failed to put object"` in error strings for external retry logic, so refactoring messages can break callers.

## Test Signals
Unit tests cover MD5 generation, config and multipart-size clamping, multipart success and abort request sequences with Smithy static replay, put/get with prefixes under failpoints, virtual-host addressing, disabled stalled stream protection for slow reads, backend URL rendering, `try_read_exact`, and multipart part-size adjustment for large files. A real S3/minio-style test is present but ignored.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/aws/src/s3.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/aws/src/util.rs -->
# sources/storage-engines/tikv/components/cloud/aws/src/util.rs

## Purpose
This module provides private AWS SDK plumbing shared by the AWS S3 and KMS implementations: HTTP client construction, default credential and region providers, retryability classification, endpoint/region configuration helpers, and a retry wrapper that records TiKV cloud error metrics.

## Important APIs, Types, And Functions
`new_http_client` builds a Smithy shared HTTP client backed by Hyper 0.14 and `hyper_tls::HttpsConnector`. `new_credentials_provider` constructs `DefaultCredentialsProvider`, using the current Tokio runtime with `block_in_place` if present or TiKV's external-IO blocking helper otherwise. `is_retryable` classifies AWS `SdkError` variants: timeout, dispatch failure, response/service 5xx, and HTTP 408 are retryable; construction failures and normal 4xx are not.

`configure_endpoint` applies a non-empty endpoint URL to an AWS config loader. `configure_region` either uses an explicit region or installs `DefaultRegionProvider`, whose chain checks environment variables, then AWS profile files, then defaults to `us-east-1`. `retry_and_count` wraps an async action in TiKV `retry_ext`, logs failures with a UUID/context string, and increments `CLOUD_ERROR_VEC` with provider `aws`.

`DefaultCredentialsProvider` wraps AWS `DefaultCredentialsChain`. Its `ProvideCredentials` implementation retries all provider errors through `retry_and_count` and normalizes the final error into a `CredentialsError::provider_error` with a message that includes the underlying source string.

## Control Flow
Credential construction is async internally but exposed through a synchronous function for the provider constructors. At credential lookup time, the provider calls the AWS default chain inside the retry wrapper. If the `cred_err` failpoint is enabled in tests, the provider injects a retryable wrapped credentials error before the real chain call. After retries are exhausted, it rewrites the error message to "Couldn't find AWS credentials in sources (...)".

## State And Persistence Behavior
The module has no durable state. Runtime state includes the AWS default credential chain, region provider chain, HTTP client handles, and Prometheus metric counters incremented on retry failures. The retry wrapper creates a UUID per operation to correlate warning logs.

## Dependencies And Integration Points
Both `kms.rs` and `s3.rs` use these helpers for consistent AWS config loading and retry classification. The module integrates AWS config providers, Smithy runtime error types, Hyper/TLS transport, TiKV retry utilities, TiKV metrics, and failpoints. `SdkError` is aliased to the Smithy orchestrator result type used throughout the AWS crate.

## Risks
All credential provider errors are treated as retryable because the code cannot distinguish their exact causes. This can delay permanent misconfiguration failures. `is_retryable` is HTTP-status based for response/service errors and may miss AWS modeled retry traits. `new_credentials_provider` blocks on async setup and must be used carefully inside Tokio runtimes; it uses `block_in_place` to avoid deadlocks in supported contexts.

## Test Signals
Tests cover retryability for response and service 5xx, 4xx, 408, timeout errors, and construction failures. With the `failpoints` feature, `test_default_provider` injects credential errors and verifies the normalized provider error message.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/aws/src/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/azure/Cargo.toml -->
# sources/storage-engines/tikv/components/cloud/azure/Cargo.toml

## Purpose
This manifest defines the TiKV Azure cloud provider crate. It supplies Azure Blob Storage and Azure Key Vault support over the shared `cloud` crate abstractions.

## Important APIs, Types, And Functions
As a manifest, it declares dependencies rather than code APIs. The dependency set shows the crate uses Azure SDK crates (`azure_core`, `azure_identity`, `azure_security_keyvault`, `azure_storage`, `azure_storage_blobs`), shared `cloud` types, `kvproto` config, async traits and futures, OAuth2, OpenSSL-backed HMAC, serde/JSON, TiKV logging/utilities, Tokio time, URL parsing, and UUID v4.

## Control Flow
Cargo compiles this non-published Rust 2021 workspace package with the selected Azure SDK crates and disabled default features on several Azure packages. There are no features declared in this manifest.

## State And Persistence Behavior
The manifest has no runtime state. It enables runtime behaviors implemented elsewhere in the Azure crate: token/identity handling, Key Vault calls, blob operations, signed storage requests, JSON parsing, and time-aware credential handling.

## Dependencies And Integration Points
The crate integrates the shared `cloud` abstraction layer with Azure SDKs, `kvproto`, TiKV logging/util, OpenSSL, OAuth2, and Tokio. `azure_core` is built with `hmac_openssl`, so OpenSSL is part of the request signing path.

## Risks
The Azure SDK versions are all `0.18`, so updating one package likely requires updating the family together. Default features are disabled for several SDK crates, which keeps builds smaller but can surprise new code that expects default transports or crypto. UUID is version `1.0` here while the root cloud crate uses `0.8`, so cross-crate UUID types should not be shared directly.

## Test Signals
Compilation of the Azure crate validates dependency compatibility. Runtime tests live in the Azure source files rather than this manifest; this manifest's signal is that Azure storage/KMS code can resolve the required SDK, crypto, logging, and async dependencies.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cloud/azure/Cargo.toml -->
