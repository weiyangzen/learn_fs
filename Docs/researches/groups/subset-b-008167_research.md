# subset-b-008167 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/structs.rs -->
# sources/object-store/garage/src/garage/cli/structs.rs

Purpose: This file is the command-line schema for the `garage` binary. It uses `structopt` to define the top-level command tree, subcommands, flags, positional arguments, environment-backed options, version strings, hidden commands, and safety confirmation switches. It is declarative rather than executable; runtime dispatch happens in `main.rs` and the local/remote CLI modules.

Important APIs and types: The central public type is `Command`, with variants for `server`, `health`, `status`, `node`, `layout`, `bucket`, `key`, `admin-token`, `repair`, `offline-repair`, `stats`, `worker`, `block`, `meta`, `convert-db`, `admin-api-schema`, `json-api`, and shell completions. Supporting types include `ServerOpt`, `HealthOpt`, `NodeOperation`, `LayoutOperation`, `BucketOperation`, `KeyOperation`, `AdminTokenOperation`, `RepairOpt`, `RepairWhat`, `ScrubCmd`, `OfflineRepairOpt`, `WorkerOperation`, `WorkerListOpt`, `BlockOperation`, and `MetaOperation`.

Control flow: `structopt` derives generate clap parsing and validation. Nested enums model dispatch boundaries: for example `Command::Bucket(BucketOperation::SetQuotas(...))` and `Command::Repair(RepairOpt { what: RepairWhat::Scrub { cmd } })`. Required arguments, defaults, feature gates, and confirmation flags are enforced at parse time before `main.rs` matches on `Command`.

State and persistence behavior: This file does not persist state. It describes operations that later mutate cluster layout, bucket/key/admin-token metadata, worker parameters, block resync queues, metadata snapshots, and local database conversion. Safety state is represented in the CLI surface through `--yes` flags for destructive operations and by requiring specific version numbers for layout apply/skip operations.

Dependencies and integration points: It depends on `structopt`, clap shell completion support, `bytesize::ByteSize`, `garage_util::version::garage_version`, and the local database conversion option type. It integrates with remote admin RPC handlers, local initialization/repair/conversion code, the admin OpenAPI schema generator, and feature-gated K2V offline repair.

Risks: CLI compatibility is encoded here; renaming flags, changing defaults, or moving variants can break scripts and admin automation. Some high-risk operations are only guarded by flags rather than interactive prompts. Feature-gated variants mean documentation/tests must account for build features. The file is large enough that adding a new command in the wrong enum branch can silently change whether it is handled locally or remotely.

Test signals: Integration tests in this group exercise several CLI paths indirectly: bucket creation/permission changes, key permission changes, layout bootstrap, node ID lookup, website enable/disable, and `json-api CreateKey`. Parse-level coverage is otherwise implicit through successful test harness startup and command invocation.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/structs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/main.rs -->
# sources/object-store/garage/src/garage/main.rs

Purpose: This is the `garage` binary entrypoint. It initializes build/version metadata, installs a panic-aborting hook, parses CLI arguments, configures logging, initializes sodiumoxide, creates a Tokio runtime, and dispatches server, local, schema, completion, and remote admin commands.

Important APIs and types: `Opt` combines `rpc_host`, flattened `Secrets`, `config_file`, and `Command`. `main`, `run`, `init_logging`, and `cli_command` are the key functions. Remote command setup uses `NetworkKey`, `NetApp`, `parse_and_resolve_peer_addr`, `AdminRpc`/`ADMIN_RPC_PATH`, local node ID reading, and `cli::remote::Cli`.

Control flow: `main` validates compile-time feature combinations, initializes version/features, sets a panic hook that prints version and backtrace before aborting, then parses clap matches with the computed version string. `run` dispatches server/offline repair/convert-db/node-id/schema/completion locally and sends all other commands through `cli_command`. `cli_command` reads config only when RPC host or secret is missing, resolves and validates the RPC secret, builds a temporary signing keypair, connects to the target node, creates an admin proxy endpoint, and calls the remote CLI handler.

State and persistence behavior: Persistent state is read from the config file, metadata directory node ID, and optional secret files. Runtime state includes environment variables for logging defaults, the global tracing subscriber, a sodiumoxide initialization, and a transient NetApp client. The panic hook deliberately aborts the process to avoid continuing after a Tokio task panic.

Dependencies and integration points: It integrates `structopt`, `tracing_subscriber`, optional syslog/journald logging, `garage_rpc`, `garage_net`, admin API RPC proxying, OpenAPI generation, local CLI modules, and secret loading from `secrets.rs`. It is also the test harness binary invoked by integration tests through `CARGO_BIN_EXE_garage`.

Risks: Logging setup mutates `RUST_LOG` before runtime construction and exits if requested syslog/journald support is absent at compile time. RPC host fallback uses local config and may warn on default localhost failure. Secret validation is strict on hex and key length. The abort-on-panic policy is operationally safe but can make tests or development runs fail hard.

Test signals: The integration harness depends on this path for starting the server, running `status`, `node id`, `layout`, `bucket`, `key`, and `json-api`. Secret-specific unit tests live in `secrets.rs`; remote command connectivity is implicitly tested by every CLI-backed integration setup step.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/secrets.rs -->
# sources/object-store/garage/src/garage/secrets.rs

Purpose: This file centralizes secret injection for CLI/server operation. It lets RPC, admin API, and metrics tokens be supplied either directly or through files from config, CLI flags, or environment variables, while enforcing mutual exclusion and optional Unix permission checks.

Important APIs and types: `Secrets` is a `StructOpt`-derived CLI/env struct for `rpc_secret`, `rpc_secret_file`, `admin_token`, `admin_token_file`, `metrics_token`, `metrics_token_file`, and `allow_world_readable_secrets`. `fill_secrets` applies all secret overrides to a `Config`. `fill_secret` resolves one secret value. `read_secret_file` performs permission checks and trims trailing whitespace.

Control flow: `fill_secrets` chooses the effective `allow_world_readable` policy from CLI/env override or config default, then calls `fill_secret` for each supported secret. `fill_secret` first rejects simultaneous direct and file values from CLI/env, then overrides config if a CLI/env value exists, otherwise reads the config file path if present. If both config direct value and config file path are present it errors. Secret files are read as text and `trim_end` is applied.

State and persistence behavior: No persistent writes occur. The function mutates the in-memory `Config` so downstream code sees resolved secret strings rather than file paths. On Unix, the permission check refuses any group/world permission bits unless explicitly allowed.

Dependencies and integration points: It depends on `garage_util::config::Config`, `garage_util::error::Error`, `structopt`, and Unix `MetadataExt`. `main.rs` uses `fill_secret` for remote CLI RPC secrets, while `server.rs` uses `fill_secrets` before constructing `Garage`.

Risks: Direct CLI/env secrets override config values and may hide deployment mistakes. The world-readable check is Unix-only; behavior differs on non-Unix. `trim_end` is convenient for newline-terminated secret files but would also remove intended trailing whitespace if a secret format allowed it. Error messages name `*_file` even when paths came from environment variables, which is accurate to the logical option but not always the source.

Test signals: Unit tests create temporary config and secret files, verify secret file reading, override precedence for direct/file CLI values, Unix permission failures and overrides, and rejection when both `rpc_secret` and `rpc_secret_file` are configured.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/secrets.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/server.rs -->
# sources/object-store/garage/src/garage/server.rs

Purpose: This file launches and coordinates a Garage daemon. It reads config with resolved secrets, initializes the core `Garage` object, optionally applies single-node/default-key/default-bucket bootstrap, starts background workers, tracing, internal RPC, public S3/K2V/Web/Admin servers, and then handles graceful shutdown.

Important APIs and types: `run_server` is the main async entrypoint. `initial_config` implements `--single-node`, `--default-access-key`, and `--default-bucket`. `watch_shutdown_signal` has Unix and Windows implementations. The file uses `Garage`, `BackgroundRunner`, `AdminApiServer`, `S3ApiServer`, optional `K2VApiServer`, `WebServer`, and `tokio::sync::watch`.

Control flow: `run_server` reads config, initializes metrics exporter when enabled, creates `Garage`, runs bootstrap config, creates shutdown watch channel and background runner, spawns workers, initializes OTLP tracing if configured, constructs API servers, starts the RPC system, pushes enabled public servers into a join list, and waits until either shutdown-only or all server tasks finish. Shutdown deregisters RPC handlers, shuts down OpenTelemetry, awaits NetApp, cleans up system references, drops `Garage`, and waits for background tasks.

State and persistence behavior: Persistent metadata/data are managed by `Garage::new` and tables created by bootstrap. `initial_config` can write cluster layout, imported access keys, buckets, aliases, and bucket-key permissions. Runtime state includes worker tasks, server tasks, watch cancellation, metrics exporter, tracing provider, and RPC handlers.

Dependencies and integration points: It integrates configuration, background task scheduling, RPC system run loop, S3/K2V/Admin/Web API crates, model tables, layout manager, bucket/key helpers, metrics, and tracing setup. It is the daemon side exercised by all integration tests in `garage/tests`.

Risks: Single-node bootstrap refuses non-replication-factor-1 configs, existing multi-node knowledge, and layout versions greater than one, so operational flags can prevent startup. Default access key/bucket setup depends on environment variables and existing table state. Server task errors are logged after join, but the daemon continues shutdown. K2V config without a K2V-enabled build only logs an error.

Test signals: Integration harness startup validates server launch, layout application, API binding, Admin JSON API, S3, Web, and optional K2V paths. Specific tests exercise default runtime surfaces: bucket/key metadata, website config, S3 object operations, and K2V table behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/admin.rs -->
# sources/object-store/garage/src/garage/tests/admin.rs

Purpose: This integration test verifies that admin CLI bucket permission changes affect S3 authorization as expected for a live Garage instance.

Important APIs and types: `test_admin_bucket_perms` uses `common::context`, `aws_sdk_s3::Client::head_bucket`, and `CommandExt` on the Garage CLI. It exercises `bucket create`, `bucket allow --read`, `bucket deny --read`, and `bucket delete --yes`.

Control flow: The test starts with `head_bucket` failing for a missing bucket, creates the bucket, verifies it still fails before permission is granted, grants read permission to the test key, verifies success, denies read, verifies failure, grants read again, verifies success, deletes the bucket, and verifies failure again.

State and persistence behavior: The test mutates bucket metadata, bucket-key permission state, and bucket deletion state through CLI commands. S3 `head_bucket` observes those persisted table changes through the running daemon.

Dependencies and integration points: It bridges CLI admin operations, model permission tables, and S3 API authorization. It depends on the shared real-process integration harness and a single default test key.

Risks: The assertions are coarse because they only check success versus error, not exact S3 error codes. The bucket name is constant, so test isolation relies on the harness using a fresh test instance directory.

Test signals: Strong signals are the alternating `head_bucket` success/failure results after each permission or deletion operation, proving that admin metadata changes propagate to S3 authorization.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/admin.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/bucket.rs -->
# sources/object-store/garage/src/garage/tests/bucket.rs

Purpose: This integration test exercises basic bucket lifecycle and create-bucket permission behavior through the AWS S3 SDK against a live Garage instance.

Important APIs and types: `test_bucket_all` uses AWS SDK operations `create_bucket`, `list_buckets`, `get_bucket_location`, `get_bucket_versioning`, and `delete_bucket`, plus CLI `key deny/allow --create-bucket`. It asserts `DeleteBucketOutput` equality for the delete result.

Control flow: The test first denies the key create-bucket capability and expects S3 bucket creation to fail. It then grants create-bucket, creates `hello`, checks the returned location, lists buckets to find it, reads bucket location, checks the versioning stub returns no status, deletes the bucket, and confirms it disappears from listing.

State and persistence behavior: The test mutates key-level create-bucket permissions and bucket alias/object-store metadata. No objects are written, so deletion is expected to succeed without non-empty-bucket handling.

Dependencies and integration points: It ties key permission state from the admin CLI to S3 CreateBucket authorization and validates the bucket listing/location/versioning API surface provided by Garage.

Risks: The test does not assert exact error codes for unauthorized creation and leaves TODOs for invalid names, duplicate bucket creation, and non-empty bucket deletion. Constant bucket names require a clean integration instance.

Test signals: CreateBucket failure before permission, success after permission, `/hello` location, region `garage-integ-test`, empty versioning status, and absence from `ListBuckets` after deletion.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/bucket.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/common/client.rs -->
# sources/object-store/garage/src/garage/tests/common/client.rs

Purpose: This helper builds the AWS S3 SDK client used by Garage integration tests.

Important APIs and types: `build_client` takes a test `garage::Key` and returns `aws_sdk_s3::Client`. It constructs `Credentials`, `Config::builder`, endpoint URL using `DEFAULT_PORT`, shared test region, and `BehaviorVersion::latest`.

Control flow: The function creates static credentials from the generated test key, sets endpoint `http://127.0.0.1:{DEFAULT_PORT}`, assigns `garage-integ-test` region, sets credentials provider, chooses the latest SDK behavior version, builds config, and returns a client from that config.

State and persistence behavior: There is no persistence. The function captures connection/authentication state in an SDK client object that later signs S3 requests against the test daemon.

Dependencies and integration points: It depends on `aws_sdk_s3`, shared `REGION`, `garage::Key`, and `DEFAULT_PORT`. It is used by `Context::new` so almost every S3 integration test goes through it.

Risks: The endpoint is tied to `DEFAULT_PORT` rather than the instance's selected port, while `garage::Instance` can read `GARAGE_TEST_INTEGRATION_PORT`. If tests run with a non-default port, this helper can become inconsistent with the server instance unless the default remains aligned.

Test signals: All AWS SDK integration tests implicitly validate that credentials, region, endpoint, and behavior version interoperate with Garage's S3 API.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/common/client.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/common/custom_requester.rs -->
# sources/object-store/garage/src/garage/tests/common/custom_requester.rs

Purpose: This helper sends manually constructed S3 and K2V HTTP requests that the AWS SDK cannot easily express, especially for unusual SigV4 payload modes, unsigned headers, virtual-host style hosts, presigned-like edge cases, and K2V-specific requests.

Important APIs and types: `CustomRequester`, `RequestBuilder`, `BodySignature`, `query_param_to_string`, `to_streaming_body`, and `to_streaming_unsigned_trailer_body` are key. `BodySignature` supports `Unsigned`, `Classic`, AWS streaming signed chunks, and streaming unsigned payload trailers. Requests use Hyper, `garage_api_common::signature`, HMAC-SHA256, and collected full bodies.

Control flow: `CustomRequester::new_s3/new_k2v` bind a key, base URI, service name, and Hyper client. `RequestBuilder` accumulates method, path, query params, signed/unsigned headers, body, body signature type, and path-style versus vhost-style host. `send` constructs host/path, computes canonical SigV4 headers and body hash marker, signs the canonical request, optionally rewrites the body into AWS chunked streaming format, sends the request, collects the response body, and returns a full response.

State and persistence behavior: The helper has no persistent state. It uses the test key to sign requests and can cause server-side object/K2V mutations depending on the request. It keeps no cookies or connection state beyond Hyper's client.

Dependencies and integration points: It integrates with Garage's internal SigV4 canonicalization code, Hyper HTTP client, `chrono`, HMAC/SHA-256, and test `Instance` endpoints. It is essential for K2V tests, streaming signature tests, CORS preflights, and custom S3 requests.

Risks: The helper comments note that path and query parameters are not URL-encoded in builder input before URI assembly, so tests involving reserved/control characters may be impossible or misleading through this path. Streaming content length is computed by generating a dummy body first, which is acceptable for tests but inefficient. Header handling splits signed and unsigned headers, so misuse can accidentally test an unsigned header path.

Test signals: K2V API tests, streaming SigV4 tests, S3 CORS direct tests, and presigned request execution all rely on this helper. Passing tests validate both Garage's server behavior and the helper's request signing fidelity.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/common/custom_requester.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/common/ext/mod.rs -->
# sources/object-store/garage/src/garage/tests/common/ext/mod.rs

Purpose: This tiny module re-exports extension traits used by integration tests.

Important APIs and types: It declares `mod process;` and `pub use process::*;`, exposing `CommandExt` to sibling test modules.

Control flow: There is no runtime control flow beyond Rust module loading. Importing `common::ext::*` makes process command helper methods available.

State and persistence behavior: No state or persistence is present.

Dependencies and integration points: It integrates the test common module with `ext/process.rs`, allowing CLI command invocations in tests to use `.quiet()`, `.expect_success_status()`, and `.expect_success_output()`.

Risks: Because it re-exports everything from `process`, changes to `process.rs` become part of the public helper surface for all tests.

Test signals: Every integration test that invokes the Garage binary with `common::ext::*` depends on this re-export compiling and resolving correctly.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/common/ext/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/common/ext/process.rs -->
# sources/object-store/garage/src/garage/tests/common/ext/process.rs

Purpose: This file defines ergonomic assertion helpers for running Garage CLI commands from integration tests.

Important APIs and types: `CommandExt` is implemented for `std::process::Command`. It provides `quiet`, `expect_success_status`, and `expect_success_output`.

Control flow: `quiet` redirects stdout and stderr to null and returns the command for chaining. `expect_success_output` executes the command, panics if spawning fails, and if the exit status is nonzero panics with command debug data, status code, stdout, and stderr. `expect_success_status` delegates to `expect_success_output` and returns just the status.

State and persistence behavior: The helper itself has no persistent state but executes commands that mutate the integration Garage instance. It may suppress process output when `.quiet()` is used.

Dependencies and integration points: It is used by the test harness for setup and by tests that exercise CLI admin operations. It integrates process execution with assertion-style error reporting.

Risks: `quiet` can hide useful output unless `expect_success_output` is called without it. The helper panics on nonzero status, so tests cannot inspect expected failures through it. Commands are executed synchronously and can block if the invoked binary hangs.

Test signals: Harness startup and admin/bucket/website tests rely on this helper for layout assignment, key/bucket permissions, and website configuration.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/common/ext/process.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/common/garage.rs -->
# sources/object-store/garage/src/garage/tests/common/garage.rs

Purpose: This file owns the real Garage process used by integration tests. It creates a temporary config/runtime directory, starts the binary, waits for boot, configures single-node layout, creates test keys, exposes endpoint URIs, and terminates the process at test shutdown.

Important APIs and types: `DEFAULT_PORT`, `GARAGE_TEST_SECRET`, `Key`, `Instance`, `instance`, and `command` are central. `Instance` stores the child process, runtime path, default key, S3/K2V/Web/Admin ports, and helper methods `setup`, `wait_for_boot`, `setup_layout`, `terminate`, `node_id`, `s3_uri`, `k2v_uri`, and `key`.

Control flow: `Instance::new` chooses a port/path/db engine from environment or defaults, deletes and recreates the runtime directory, writes a full config file, opens stdout/stderr logs, and spawns `garage server`. `setup` polls `garage status`, assigns/apply layout for one node, and creates a default key via `json-api CreateKey`. A global `OnceLock` initializes one instance lazily, and a `static_init` destructor kills the child process.

State and persistence behavior: Persistent test state lives under the runtime directory: config, metadata, data, stdout, and stderr. The server process persists cluster layout, keys, buckets, and objects there for the duration of the integration run. The harness aggressively removes any previous directory for the selected port.

Dependencies and integration points: It depends on `serde_json`, the Garage binary path from `GARAGE_TEST_INTEGRATION_EXE` or `CARGO_BIN_EXE_garage`, process helpers, and CLI commands. It is the root integration point for all tests in `garage/tests`.

Risks: The destructor uses `kill` rather than graceful SIGTERM. Port allocation is fixed by default and can conflict with other runs. `wait_for_boot` loops for up to two minutes but does not explicitly fail if status never succeeds before layout commands run. Removing the runtime path can delete user-provided `GARAGE_TEST_INTEGRATION_PATH` content if misconfigured.

Test signals: Every integration test's ability to create buckets, sign requests, and talk to S3/K2V/Web/Admin confirms that this harness successfully bootstrapped a usable single-node Garage cluster.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/common/garage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/common/macros.rs -->
# sources/object-store/garage/src/garage/tests/common/macros.rs

Purpose: This file defines a small async assertion macro for comparing a response body stream against expected bytes.

Important APIs and types: `assert_bytes_eq!` takes a stream expression and expected byte slice/expression. It uses `collect().await`, `into_bytes`, and `assert_eq!`.

Control flow: At expansion sites, the macro awaits body collection, panics on read error, converts to bytes, and compares the byte content to the expected value.

State and persistence behavior: It has no state and no persistence. It consumes the body stream passed into it.

Dependencies and integration points: It relies on `http_body_util::BodyExt` being in scope in the test crate and is imported through `#[macro_use]` in the common module. It is used widely by S3 object, multipart, streaming, SSE-C, and website tests.

Risks: The macro collects full bodies into memory, which is fine for current integration payload sizes but unsuitable for very large streaming tests. It consumes the body, so callers cannot inspect it again.

Test signals: Exact object body comparisons throughout the S3 suites depend on this macro.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/common/macros.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/common/mod.rs -->
# sources/object-store/garage/src/garage/tests/common/mod.rs

Purpose: This module ties the integration-test harness together. It exposes shared modules, test region, `Context`, K2V-specific context, and helper methods for creating buckets and clients.

Important APIs and types: `Context` contains the static `garage::Instance`, current key, AWS S3 client, custom S3 requester, and optional `K2VContext`. `K2VContext` wraps a custom requester. `context()` creates a fresh `Context` view over the singleton instance. `Context::create_bucket` and `Context::k2v_client` are the main helper methods.

Control flow: `Context::new` retrieves the singleton Garage instance, creates a fresh key, builds an AWS SDK client, creates custom S3 and optional K2V requesters, and returns the context. `create_bucket` runs CLI `bucket create` and `bucket allow --owner --read --write` for the current key. `k2v_client` builds a typed `K2vClient` against the K2V endpoint.

State and persistence behavior: Context construction can create new access keys. `create_bucket` persists bucket metadata and permissions. The module itself holds only lightweight references and clients.

Dependencies and integration points: It integrates the AWS SDK, custom request signer, Garage process harness, CLI helpers, optional K2V client crate, and shared region `garage-integ-test`. All integration test modules depend on it.

Risks: `create_bucket` uses the exact provided name without adding a random suffix despite the comment, so tests must use unique names. Each call to `context()` creates a new key, which is useful for isolation but can leave many keys in the test metadata. Optional K2V fields are gated by the `k2v` feature.

Test signals: Successful bucket creation and permission grants in nearly every test validate this module's integration wiring.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/common/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/k2v/batch.rs -->
# sources/object-store/garage/src/garage/tests/k2v/batch.rs

Purpose: This K2V integration test exercises batch insertion, range search, pagination markers, reverse scans, prefix filtering, concurrent values, tombstones, and batch deletion through raw signed K2V HTTP requests.

Important APIs and types: `test_batch` uses `CustomRequester`, Hyper methods/statuses, `serde_json::json`, `assert_json_diff::assert_json_eq`, base64 encoding, `json_body`, and K2V query modes `search` and `delete`. It tracks causality tokens in a `HashMap`.

Control flow: The test creates a bucket, posts an insert batch of six items, reads each item back to capture causality tokens, then posts multiple search operations in one request covering full range, start/end, reverse, limit, and prefix. It updates selected items with and without causality tokens to create deletion, replacement, and conflict states, searches again, deletes ranges/prefixes in batch, refreshes tombstone tokens, and finally searches normal/reverse/tombstone-inclusive views.

State and persistence behavior: The test persists K2V entries under partition key `root` and multiple sort keys. It validates causality-token-driven overwrite versus concurrent insertion, null values as tombstones, range deletion counts, `more`/`nextStart`, and base64-encoded value arrays.

Dependencies and integration points: It integrates the K2V API server, bucket permissions, request signing, JSON protocol shape, causality metadata, and underlying K2V table/index behavior.

Risks: Expected JSON is very detailed and can be brittle if field names, default booleans, ordering, or pagination semantics change. It assumes deterministic sort order and immediate visibility after writes.

Test signals: Strong signals include 204 batch insert/update, exact read bodies and causality headers, exact batch search JSON for range/prefix/reverse/limit cases, delete counts, tombstone representation as `null`, and omission of tombstones from default search.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/k2v/batch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/k2v/errorcodes.rs -->
# sources/object-store/garage/src/garage/tests/k2v/errorcodes.rs

Purpose: This test verifies that malformed K2V requests return client errors instead of being accepted or misclassified.

Important APIs and types: `test_error_codes` uses `common::context`, `CustomRequester`, Hyper `Method`, and `StatusCode`. It covers PUT, POST search, POST batch insert, and poll-style GET parameters.

Control flow: The test first performs a valid insert and expects 204. It then sends requests with an invalid causality token, missing partition key in search body, start outside prefix, invalid JSON, invalid causality token in batch insert, invalid base64 value in batch insert, and invalid poll causality token. Each invalid request must return 400 Bad Request.

State and persistence behavior: Only the initial valid item is persisted. The invalid operations should not mutate data and are focused on validation/error response behavior.

Dependencies and integration points: It exercises K2V request parsing, causality token decoding, range filter validation, JSON parsing, base64 decoding, and error-to-status mapping.

Risks: It only checks status codes, not response bodies or error codes. The search JSON uses `partition_key` in invalid examples, while other tests use camelCase `partitionKey`, so part of the signal depends on deserialization behavior.

Test signals: Status 204 for the control insert and 400 for every malformed request.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/k2v/errorcodes.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/k2v/item.rs -->
# sources/object-store/garage/src/garage/tests/k2v/item.rs

Purpose: This file tests individual K2V item semantics and index counters, plus response content negotiation for single values, conflicts, and tombstones.

Important APIs and types: `test_items_and_indices` and `test_item_return_format` use `CustomRequester`, causality headers, `ReadIndex`, base64 JSON values, Hyper status/content types, and `assert_json_eq`. `test_items_and_indices` is marked ignored as flaky.

Control flow: The ignored index test writes values for sort keys `a` through `d`, reads tokens, checks partition index counters after each write, overwrites with causality, creates concurrent values using stale causality, verifies conflict JSON output, then deletes each key and checks counters shrink. `test_item_return_format` writes a single value, reads it with `*/*`, no Accept, binary Accept, and JSON Accept; then creates a concurrent value and tests conflict behavior; then creates a concurrent tombstone and finally deletes everything.

State and persistence behavior: The tests validate K2V's causal value set: single values, concurrent values, tombstones, and causality tokens. Index state tracks entries, conflicts, values, and bytes. Response state changes based on Accept headers: binary for single values, JSON arrays for conflicts or unspecified/json accept, 409 for binary conflict, 204 for no-content binary/tombstone cases.

Dependencies and integration points: They exercise K2V table storage, index maintenance, causality resolution, content negotiation, and async visibility of index updates.

Risks: The main index test is ignored because it is flaky and includes sleeps, indicating eventual index update timing or background propagation sensitivity. Exact byte counters and JSON ordering are brittle to implementation changes.

Test signals: Exact content types, causality-token presence, response statuses 200/204/409, value arrays with base64 or null entries, and partition index counters after writes/deletes.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/k2v/item.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/k2v/mod.rs -->
# sources/object-store/garage/src/garage/tests/k2v/mod.rs

Purpose: This module declares the raw K2V integration test submodules.

Important APIs and types: It exports `batch`, `errorcodes`, `item`, `poll`, and `simple` modules when the parent test crate enables the `k2v` feature.

Control flow: Rust's test harness discovers tests from these child modules through normal module inclusion. There is no additional runtime logic here.

State and persistence behavior: This file has no state. Its child modules create buckets and mutate K2V data through the shared integration context.

Dependencies and integration points: It is included from `tests/lib.rs` under `#[cfg(feature = "k2v")]`, tying K2V tests to feature-enabled builds.

Risks: Adding a K2V test file without declaring it here will leave it uncompiled. Feature gating can hide K2V regressions in builds that do not enable `k2v`.

Test signals: Successful compilation and discovery of the listed K2V modules.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/k2v/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/k2v/poll.rs -->
# sources/object-store/garage/src/garage/tests/k2v/poll.rs

Purpose: This file contains K2V long-polling integration tests for individual items and ranges. Both tests are currently ignored as broken.

Important APIs and types: `test_poll_item` uses GET with `causality_token` and `timeout`. `test_poll_range` uses POST with `poll_range`, `seenMarker`, and range response JSON. They use `tokio::spawn`, `tokio::select!`, `Duration`, base64 JSON assertions, and causality headers.

Control flow: The item test writes an initial value, reads its causality token, starts a polling request waiting for changes, writes a superseding value with that token, and expects the poll to return the new body before timeout. The range test writes an initial value, obtains a seen marker from `poll_range`, starts a second poll with that marker, writes an updated value, expects one changed item, then repeats with a second sort key.

State and persistence behavior: The intended behavior is that K2V stores seen markers and causality tokens sufficient for blocking until a newer value appears. Poll responses include changed items and updated markers.

Dependencies and integration points: These tests exercise K2V's notification/waiting path, request timeout handling, causal item updates, and range-change detection.

Risks: Both tests are ignored with "currently broken", so they document desired behavior but are not active regression guards. They use 10-second timeout races and spawned tasks, so even when enabled they are timing-sensitive.

Test signals: If re-enabled, signals would be poll completion before timeout, 200 status, expected binary/JSON bodies, and marker progression across changes.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/k2v/poll.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/k2v/simple.rs -->
# sources/object-store/garage/src/garage/tests/k2v/simple.rs

Purpose: This is the smoke test for the raw K2V API.

Important APIs and types: `test_simple` uses `common::context`, `CustomRequester`, Hyper `PUT`/`GET`, `StatusCode`, `BodyExt`, and an `Accept: application/octet-stream` header.

Control flow: The test creates a bucket, PUTs `Hello, world!` at partition key `root` and sort key `test1`, expects 204 No Content, then GETs the same key as octet-stream, expects 200 OK, collects the body, and compares bytes.

State and persistence behavior: It persists one K2V item and reads it back. It does not inspect causality or index state.

Dependencies and integration points: It validates the minimal path through bucket permissions, K2V endpoint routing, SigV4 signing, item insertion, and item retrieval.

Risks: As a smoke test it does not cover content negotiation, conflicts, tombstones, or error bodies. It assumes immediate read-after-write in the single-node integration instance.

Test signals: 204 on insert, 200 on read, exact body equality.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/k2v/simple.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/k2v_client/mod.rs -->
# sources/object-store/garage/src/garage/tests/k2v_client/mod.rs

Purpose: This module declares integration tests for the typed `k2v-client` crate.

Important APIs and types: It contains only `pub mod simple;`, exposing the client smoke and special-character tests.

Control flow: Rust test discovery compiles and runs the child module when the parent `tests/lib.rs` includes `k2v_client` under the `k2v` feature.

State and persistence behavior: No state is stored here. The child module creates buckets and writes K2V data through `K2vClient`.

Dependencies and integration points: It connects the Garage integration test crate with the `k2v-client` crate's public API tests.

Risks: Additional K2V client tests must be declared here or they will not run. Feature gating can exclude this module from default builds.

Test signals: Compilation of this module ensures the typed client tests are part of the feature-enabled integration suite.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/k2v_client/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/k2v_client/simple.rs -->
# sources/object-store/garage/src/garage/tests/k2v_client/simple.rs

Purpose: These tests verify that the public `k2v-client` crate works against a live Garage K2V endpoint, including Unicode/special-character key encoding.

Important APIs and types: `test_simple` and `test_special_chars` use `K2vClient`, `K2vValue`, `BatchReadOp`, `Default` filters, and `Context::k2v_client`.

Control flow: The simple test inserts one item with `insert_item`, reads it with `read_item`, and checks a single binary value. The special-character test inserts under partition key `root@plépp` and sort key `≤≤««`, reads it back, waits briefly for index visibility, reads the index to confirm the partition key, and performs a batch read to confirm the sort key.

State and persistence behavior: The tests persist K2V items through the typed client rather than raw HTTP. They validate percent-encoding of non-ASCII/reserved characters and index/batch-read visibility.

Dependencies and integration points: They integrate the `k2v-client` library, Garage K2V API, signed HTTP transport, test bucket permissions, and index maintenance.

Risks: The special-character test sleeps one second before reading the index, indicating asynchronous index propagation. It checks only one value and one batch operation, so broader client behavior is covered by library code and raw K2V tests.

Test signals: Successful insert/read, exact `K2vValue::Value`, index containing the Unicode partition key, and batch read containing the Unicode sort key.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/k2v_client/simple.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/lib.rs -->
# sources/object-store/garage/src/garage/tests/lib.rs

Purpose: This is the integration test crate root for the Garage binary/API tests.

Important APIs and types: It imports `common` with macros, declares `admin`, `bucket`, `s3`, and feature-gated `k2v` and `k2v_client` modules. It also defines async helper `json_body` for collecting Hyper responses into `serde_json::Value`.

Control flow: Module declarations determine test discovery. `json_body` consumes a response body, collects it, parses JSON, and returns the parsed value.

State and persistence behavior: The root has no persistent state. Its modules create and mutate live Garage state through the common context.

Dependencies and integration points: It depends on `http_body_util::BodyExt`, Hyper `Body`/`Response`, `serde_json`, and the common harness. It is the top-level integration point for all tests in `garage/tests`.

Risks: Feature-gated K2V tests are absent unless the `k2v` feature is enabled. `json_body` unwraps collection and parsing, so malformed responses panic rather than producing richer diagnostics.

Test signals: Successful compilation of this root wires all child modules and shared helpers into the Rust test runner.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/cors.rs -->
# sources/object-store/garage/src/garage/tests/s3/cors.rs

Purpose: This test verifies direct S3 API CORS behavior, specifically that Garage reflects the request origin when multiple origins are configured rather than returning the wrong allowed origin.

Important APIs and types: Helpers `send_preflight`, `send_put`, and `apply_bucket_cors` use `CustomRequester`, AWS SDK `CorsConfiguration`/`CorsRule`, Hyper `Method`/`StatusCode`, and fixed origin/header constants.

Control flow: The test creates a bucket, applies CORS allowing one origin, sends an OPTIONS preflight and a signed PUT with that origin, and checks `access-control-allow-origin`. It then updates CORS to allow two origins and repeats the preflight and PUT for the first origin.

State and persistence behavior: It persists bucket CORS configuration and writes the probe object on PUT. The relevant state is the response header chosen from configured allowed origins and request origin.

Dependencies and integration points: It ties S3 bucket CORS configuration, custom signed requests, preflight request handling, object PUT, and response header generation.

Risks: The test only covers PUT and a fixed set of request headers. It does not test wildcard origins, disallowed origins, deletion, max-age, or S3 SDK CORS requests.

Test signals: 200 OK responses and exact `access-control-allow-origin` equal to the request origin before and after adding a second allowed origin.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/cors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/list.rs -->
# sources/object-store/garage/src/garage/tests/s3/list.rs

Purpose: This file tests S3 object listing and multipart-upload listing semantics, including V1/V2 pagination, delimiters, prefixes, markers, continuation tokens, multipart upload markers, and multi-character delimiters.

Important APIs and types: Tests are `test_listobjectsv2`, `test_listobjectsv1`, `test_listmultipart`, and `test_multichar_delimiter`. They use AWS SDK `put_object`, `list_objects_v2`, `list_objects`, `create_multipart_upload`, and `list_multipart_uploads` with constant key sets.

Control flow: The object tests upload a fixed set of keys, then list with default settings, max keys, one-item pagination loops, delimiter, delimiter plus pagination, prefix, prefix plus delimiter, prefix plus max keys, and marker/start-after edge cases. The multipart test creates uploads for duplicate and nested keys and performs equivalent listing checks using key/upload markers. The multi-character delimiter test uploads nested keys and compares delimiter `/` with delimiter `b/`.

State and persistence behavior: The tests persist objects and incomplete multipart uploads. They validate list response contents, common prefixes, pagination continuation fields, and truncation behavior against stored key order.

Dependencies and integration points: They exercise S3 metadata indexing, object key ordering, delimiter/prefix grouping, ListObjects V1 and V2 differences, multipart upload metadata, and AWS SDK response decoding.

Risks: The comments note AWS SDK prevents some max-key edge cases, so zero or >1000 values are not tested here. V1 delimiter pagination intentionally returns repeated common prefixes because Garage does not optimize prefix skipping, which is compliant but easy to change accidentally.

Test signals: Exact counts for contents/common prefixes, continuation/marker presence, expected first key under constrained prefix, empty results after markers beyond the last key, multipart upload counts, and exact multi-character delimiter prefix results.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/list.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/mod.rs -->
# sources/object-store/garage/src/garage/tests/s3/mod.rs

Purpose: This module declares the S3 integration test suite.

Important APIs and types: It includes submodules `cors`, `list`, `multipart`, `objects`, `presigned`, `signature_encoding`, `simple`, `ssec`, `streaming_signature`, and `website`.

Control flow: Normal Rust module inclusion makes the child tests visible to the integration test crate.

State and persistence behavior: This file has no state. Child modules create buckets, objects, multipart uploads, CORS/website configs, and encrypted objects.

Dependencies and integration points: It is included from `tests/lib.rs` and is the aggregator for S3 API coverage against the live Garage daemon.

Risks: New S3 test files must be declared here. Because all children share the singleton integration instance, child tests should use unique bucket names to avoid cross-test contamination.

Test signals: Successful compilation ensures all listed S3 test modules participate in the integration suite.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/multipart.rs -->
# sources/object-store/garage/src/garage/tests/s3/multipart.rs

Purpose: This file tests multipart upload lifecycle, checksummed multipart parts, part listing pagination, completion cleanup, `GetObject` by part number, and `UploadPartCopy` from single-part and multipart source objects.

Important APIs and types: Tests are `test_multipart_upload`, `test_multipart_with_checksum`, `test_uploadlistpart`, and `test_uploadpartcopy`. They use AWS SDK `create_multipart_upload`, `upload_part`, `list_parts`, `complete_multipart_upload`, `head_object`, `get_object`, `upload_part_copy`, `ChecksumAlgorithm::Sha1`, `CompletedMultipartUpload`, `CompletedPart`, and helper `calculate_sha1`.

Control flow: The basic test uploads parts out of order, overwrites part 1, completes with selected parts, confirms the upload is gone, checks final length, full body, and per-part reads. The checksum test starts a SHA1 MPU, rejects a wrong part checksum, validates listed part checksums, computes the multipart checksum-of-checksums, and verifies completion response. The list-part test checks empty lists, ordering, ETags, sizes, pagination markers, and final completion. The copy test builds source objects, copies byte ranges from them into target MPU parts, completes, and verifies exact concatenated bytes.

State and persistence behavior: The tests persist multipart upload metadata, individual part bodies, checksums, final object versions, and source objects. Completion should remove upload state and publish the assembled object.

Dependencies and integration points: They cover Garage's multipart metadata tables, block/object storage, checksum validation, range copy handling, S3 XML/SDK response mapping, and object read path.

Risks: Payloads are 5-10 MiB and can be slow or memory-heavy. Exact ETags assume MD5 behavior for the fixed data. The tests do not cover abort MPU or invalid completion ordering/error cases beyond checksum rejection.

Test signals: Upload IDs, part counts, expected ETags, checksum fields, wrong checksum failure, content lengths, object body equality, list-parts pagination fields, upload disappearance after completion, and exact assembled copy output.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/multipart.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/objects.rs -->
# sources/object-store/garage/src/garage/tests/s3/objects.rs

Purpose: This file tests core S3 object operations: PUT, GET, HEAD metadata, conditional reads, byte ranges, response header overrides, custom metadata, Unicode/control-character keys, and object deletion.

Important APIs and types: Tests are `test_putobject`, `test_precondition`, `test_getobject`, `test_metadata`, and `test_deleteobject`. They use AWS SDK `put_object`, `get_object`, `head_object`, `delete_object`, `delete_objects`, byte streams, `SdkError`, `DateTime`, `Delete`, and `ObjectIdentifier`.

Control flow: `test_putobject` uploads empty and non-empty objects under ordinary, control-character, and Unicode keys and verifies ETags/content metadata. `test_precondition` validates `If-Match`, `If-None-Match`, `If-Modified-Since`, and `If-Unmodified-Since` status behavior. `test_getobject` checks three byte-range forms. `test_metadata` verifies stored headers/metadata and response overrides. `test_deleteobject` uploads ten objects, deletes two individually and eight in batch, verifies empty listing, and tolerates deleting a missing key.

State and persistence behavior: The tests persist object versions, content bytes, user metadata, HTTP metadata, last-modified timestamps, and delete markers/state sufficient for list results to become empty.

Dependencies and integration points: They exercise the S3 object API, metadata storage, range reader, conditional request evaluator, multi-delete handling, key encoding, and AWS SDK error mapping.

Risks: Some comments note Garage behavior around version IDs differs or is not compared to AWS. Exact ETags are tied to MD5 of known payloads. Timestamp comparisons use derived seconds and assume stable server rounding behavior.

Test signals: Exact ETags, content lengths, body bytes, content types, last-modified presence, status 304/412 for preconditions, exact content-range headers, metadata round-trips including Unicode metadata, deleted count 8, empty list after deletion, and successful delete of a non-existent object.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/objects.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/presigned.rs -->
# sources/object-store/garage/src/garage/tests/s3/presigned.rs

Purpose: This file tests presigned S3 request compatibility, including normal PUT/GET and canonical header whitespace normalization for user metadata.

Important APIs and types: `test_presigned_url` and `test_presigned_put_with_user_metadata` use AWS SDK `PresigningConfig`, Hyper `Request`, `Bytes`, `Full`, and the shared custom Hyper client.

Control flow: The first test creates a presigning config with a start time in the past, presigns PUT and GET for one key, executes them through Hyper without SDK send logic, checks status/ETag, and verifies body bytes. The second test presigns a PUT with metadata value containing internal sequential spaces, copies presigned headers into a Hyper request, sends it, and expects 200.

State and persistence behavior: The tests persist one ordinary object and one metadata-bearing object through presigned requests. The key state is Garage's SigV4 validation of query-signed URLs and canonical request construction.

Dependencies and integration points: They bridge AWS SDK presigning, Garage signature verification, Hyper execution, object PUT/GET, ETag generation, and metadata header canonicalization.

Risks: The tests do not cover expired URLs, wrong signatures, signed payload hashes, or all response override parameters. They rely on current SDK presigner behavior for URL/header construction.

Test signals: HTTP 200 from Hyper-executed presigned PUT/GET, expected ETag, exact GET body, and acceptance of metadata headers with collapsible whitespace.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/presigned.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/signature_encoding.rs -->
# sources/object-store/garage/src/garage/tests/s3/signature_encoding.rs

Purpose: This test verifies that Garage's SigV4 verification accepts equivalent URI percent-encoding forms for special characters in presigned URLs.

Important APIs and types: `test_signature_encoding` uses AWS SDK `put_object`, `get_object`, presigning, Hyper `Request`, `StatusCode`, and manual URI string replacement.

Control flow: The test uploads and reads an object with key `key@good~.txt`, presigns a GET, alters the generated URL by replacing `%40` with `@` and `~` with `%7E`, sends the modified request with the original signed headers, and expects 200 OK.

State and persistence behavior: It persists one object and tests signature verification against a modified request URI that should be canonically equivalent.

Dependencies and integration points: It exercises object key encoding, AWS SDK presigning, Garage canonical URI normalization, and Hyper request execution.

Risks: It covers only two character transformations and one key. The altered URL remains semantically equivalent; it does not test invalid encodings or double-encoding attacks.

Test signals: Successful upload/read control path and 200 OK for the altered presigned URL.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/signature_encoding.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/simple.rs -->
# sources/object-store/garage/src/garage/tests/s3/simple.rs

Purpose: This is the basic S3 smoke test for object write/read.

Important APIs and types: `test_simple` uses `common::context`, AWS SDK `put_object`/`get_object`, `ByteStream`, and `assert_bytes_eq!`.

Control flow: The test creates a bucket, uploads `Hello world!` under key `test`, reads the object back, and compares the response body bytes.

State and persistence behavior: It persists one object in a new bucket and reads it back immediately.

Dependencies and integration points: It validates the minimal path through bucket creation/permission setup, AWS SDK signing, S3 PUT object storage, and S3 GET object retrieval.

Risks: It is intentionally narrow and does not inspect headers, ETags, metadata, ranges, or error behavior. It assumes immediate consistency in the single-node test setup.

Test signals: Successful PUT, successful GET, and exact body equality.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/simple.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/ssec.rs -->
# sources/object-store/garage/src/garage/tests/s3/ssec.rs

Purpose: This file tests SSE-C object encryption behavior for normal objects, copy operations, multipart uploads, and upload-part-copy across encrypted and non-encrypted sources/targets.

Important APIs and types: Constants define two base64 SSE-C keys and MD5s. Tests `test_ssec_object` and `test_multipart_upload` use AWS SDK SSE-C fields, `copy_object`, `create_multipart_upload`, `upload_part`, `upload_part_copy`, `complete_multipart_upload`, and helper `test_read_encrypted`.

Control flow: The object test writes encrypted objects for small and larger data, verifies reads fail without or with wrong key and succeed with the right key, copies encrypted to plaintext, plaintext to encrypted, encrypted to encrypted with different keys, and encrypted to encrypted with same key. The MPU test creates an encrypted multipart object, reads it back through SSE-C, then creates another encrypted MPU that mixes uploaded parts and copied ranges from encrypted sources before verifying assembled content.

State and persistence behavior: The tests persist encrypted object data, encryption metadata, copied object versions, multipart part state, and assembled objects. They validate that plaintext is only exposed when correct SSE-C headers are supplied.

Dependencies and integration points: They exercise Garage's SSE-C encryption/decryption layer, metadata propagation, copy-source SSE-C validation, MPU storage, byte-range copy, and S3 SDK header mapping.

Risks: Fixed test keys are hard-coded for reproducibility. The tests assert access failure generally but do not inspect exact error codes. Payload sizes are moderate but still memory-collected. They do not cover invalid key MD5 separately from wrong keys.

Test signals: SSE-C algorithm/key-MD5 response headers, failed reads without/wrong keys, exact body reads with correct keys, plaintext copy readability, encrypted copy protection, and correct assembled bytes for encrypted multipart copy.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/ssec.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/streaming_signature.rs -->
# sources/object-store/garage/src/garage/tests/s3/streaming_signature.rs

Purpose: This file tests AWS SigV4 streaming upload modes against S3 operations, including signed chunked payloads, unsigned payload trailers, trailer checksum validation, streaming bucket creation, and streaming website configuration upload.

Important APIs and types: Tests use `CustomRequester`, `BodySignature::Streaming`, `BodySignature::StreamingUnsignedTrailer`, CRC32 from `crc_fast`, base64 encoding, Hyper `Method`, CLI key permission helper, and AWS SDK reads/checksum mode.

Control flow: `test_putobject_streaming` uploads an empty object and a checksum-bearing object through signed streaming chunks, then reads them with the SDK. `test_putobject_streaming_unsigned_trailer` uploads empty and non-empty objects with unsigned trailer checksums, first verifying a wrong checksum fails. `test_create_bucket_streaming` grants create-bucket and creates a bucket using a streaming request body, then verifies object operations work. `test_put_website_streaming` sends XML website configuration in a streaming PUT with `?website` and verifies the stored config through the SDK.

State and persistence behavior: The tests persist objects, checksums, a created bucket, and website configuration. The key state is request-body decoding and checksum/signature verification before data is committed.

Dependencies and integration points: They integrate Garage SigV4 streaming parser, checksum validation, object storage, bucket creation authorization, website configuration parsing, and the custom request builder.

Risks: The custom requester cannot currently URL-encode control-character paths, noted in comments. Streaming body generation is test-only and may not represent all client implementations. Wrong trailer checksum is checked only as a generic client error.

Test signals: Successful streaming PUTs, failed wrong trailer checksum, exact object bytes, ETags, content length, stored CRC32 checksum, successful streaming bucket creation, and website config fields `home.html` and `err/error.html`.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/streaming_signature.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/website.rs -->
# sources/object-store/garage/src/garage/tests/s3/website.rs

Purpose: This large integration file tests Garage's S3 website hosting and related Admin API domain check behavior. Coverage includes CLI and S3-API website enablement, index/error documents, CORS, redirect metadata, routing rules, punycode domains, invalid redirects, and default not-found pages.

Important APIs and types: Tests include `test_website`, `test_website_s3_api`, `test_website_check_domain`, `test_website_redirect_full_bucket`, `test_website_redirect`, `test_redirect_helper`, `test_website_invalid_redirect`, `test_website_puny`, and `test_website_object_not_found`. They use AWS SDK website/CORS types, Hyper direct requests to the web/admin ports, `LOCATION`, JSON body assertions, and CLI `bucket website --allow/--deny`.

Control flow: The CLI website test verifies web access denied before enablement, admin `/check` failure, enablement via CLI, successful serving and domain checks for plain/web/s3 host forms, then disablement and failure again. The S3 API test stores index/error objects, configures website and CORS through S3 APIs, validates direct web GET, error document, object redirect metadata, allowed/forbidden preflights, CORS deletion, and website deletion. Redirect tests validate full-bucket and rule-based redirects/rewrites, including conditional rules that only apply on 404. Additional tests check missing `domain`, invalid domains, invalid redirect config, punycode host serving, and default HTML 404 content.

State and persistence behavior: The file persists objects, website configurations, CORS configurations, bucket website exposure state, routing rules, redirect metadata, and admin domain-management state. It validates that disabling/deleting configs changes web serving immediately in the single-node instance.

Dependencies and integration points: It exercises the S3 Web server, S3 bucket website API, bucket metadata, admin API `/check`, CORS evaluation, object metadata redirects, routing rule evaluator, bucket alias/domain matching, and CLI admin commands.

Risks: Tests use direct Hyper requests with explicit Host headers and fixed bucket names, so they rely on test instance isolation. Some edge cases are commented out, such as empty domain handling. The redirect helper has repeated `stream-404` assertions and does not separately inspect the `stream-missing` path despite configuring it.

Test signals: HTTP statuses 200/302/307/301/403/404/400, exact `Location` headers, exact served bodies for index/error/static files, JSON admin error bodies, CORS headers and deletion errors, round-tripped website config, invalid config rejection, punycode host success, and default not-found content type/body.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tests/s3/website.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/tracing_setup.rs -->
# sources/object-store/garage/src/garage/tracing_setup.rs

Purpose: This file abstracts optional OpenTelemetry tracing initialization behind a single exported `init_tracing` function.

Important APIs and types: It re-exports `telemetry::init_tracing`. The non-`telemetry-otlp` implementation logs an error and returns `Ok(())`. The feature-enabled implementation builds an OTLP tracing pipeline with tonic exporter, timeout, trace config, sampler, ID generator, and resource labels.

Control flow: When `telemetry-otlp` is disabled, calling `init_tracing` emits that the admin trace sink is ignored. When enabled, it shortens the node UUID to an instance ID, builds an always-on tracing pipeline to the configured endpoint, installs it with Tokio batch runtime, and returns an error if initialization fails.

State and persistence behavior: There is no persistence. Runtime state is the global OpenTelemetry tracer provider installed by the pipeline; `server.rs` later calls global shutdown during daemon shutdown.

Dependencies and integration points: It integrates `garage_util::data::Uuid`, `garage_util::error`, `opentelemetry`, `opentelemetry_otlp`, and server config `admin.trace_sink`.

Risks: Without the feature, configuring a trace sink only logs an error but does not fail startup. With the feature, sampler is always-on, so trace volume can be high. Initialization timeout is fixed at three seconds.

Test signals: No direct tests in this group. Server startup with trace sink would exercise it; default integration config does not set a trace sink.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/tracing_setup.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/k2v-client/Cargo.toml -->
# sources/object-store/garage/src/k2v-client/Cargo.toml

Purpose: This manifest defines the `k2v-client` crate, a Rust library and optional CLI for Garage's K2V protocol.

Important APIs and types: Package metadata sets name `k2v-client`, version `0.0.4`, AGPL license, repository, and readme. The library path is `lib.rs`; binary `k2v-cli` uses `bin/k2v-cli.rs` and requires feature `cli`. Feature `cli` enables `clap`, `tokio/fs`, `tokio/io-std`, `tracing-subscriber`, and `format_table`.

Control flow: Cargo uses this manifest to resolve workspace dependencies and feature-gated binary compilation. Without `cli`, only the library and its non-CLI dependencies are built.

State and persistence behavior: The manifest itself has no runtime state. It controls which dependencies and code paths are available, including filesystem/stdin support for the CLI feature.

Dependencies and integration points: Core dependencies include base64, sha2, hex, http, http-body-util, log, aws-sigv4, aws-sdk-config, percent-encoding, hyper/hyper-util/hyper-rustls, serde, serde_json, thiserror, and tokio. It inherits workspace lint settings.

Risks: The crate uses edition 2018 while the wider workspace may contain newer editions. CLI behavior is absent unless the feature is selected. Dependency versions are workspace-controlled, so API changes in shared dependencies can affect both library and CLI.

Test signals: The Garage integration tests under `tests/k2v_client` compile and exercise the library when the `k2v` feature is enabled; CLI-specific code has no direct test in this group.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/k2v-client/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/k2v-client/bin/k2v-cli.rs -->
# sources/object-store/garage/src/k2v-client/bin/k2v-cli.rs

Purpose: This file implements the `k2v-cli` command-line utility on top of the `k2v-client` library. It supports inserting, reading, polling, deleting, indexing, range reading, and range deletion with human or JSON output.

Important APIs and types: `Args` holds region, endpoint, key ID, secret, bucket, and `Command`. `Command` variants are `Insert`, `Read`, `PollItem`, `PollRange`, `Delete`, `ReadIndex`, `ReadRange`, and `DeleteRange`. Helpers include `Value`, `ReadOutputKind`, `BatchOutputKind`, `Filter`, `main`, and `run`.

Control flow: `main` sets a default `RUST_LOG`, initializes tracing subscriber, parses clap args, constructs `K2vClientConfig` and `K2vClient`, creates a current-thread Tokio runtime, and runs command dispatch. `Value::to_data` reads text, base64, file, or stdin. Output helpers either print JSON, raw bytes, base64, human text, or table output and then call `exit`. `run` maps each CLI command to the corresponding client call and validates unsupported filter combinations for poll-range/read-index/delete-range.

State and persistence behavior: The CLI persists data only through remote K2V operations. Local state includes parsed args, input file/stdin bytes, and formatted output. It can exit with distinct raw-output error codes for conflict/tombstone cases.

Dependencies and integration points: It depends on `clap`, `tokio`, `tracing-subscriber`, `format_table`, `base64`, and the `k2v-client` public API. Environment variables `AWS_REGION`, `K2V_ENDPOINT`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `K2V_BUCKET` can supply connection options.

Risks: The displayed code constructs a `client` in `main` but `run(args)` as shown does not receive it, while `run` references `client`; this suggests either a compile issue in this snapshot or reliance on missing context not present in the file. Output helpers use `exit`, making them hard to unit test. Error strings contain misspellings like `conlicts-only`. Raw mode refuses concurrent/tombstone results.

Test signals: No direct CLI integration tests are in this group. Library behavior is tested through `garage/tests/k2v_client/simple.rs`; CLI compileability would be covered only by building with the `cli` feature.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/k2v-client/bin/k2v-cli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/k2v-client/error.rs -->
# sources/object-store/garage/src/k2v-client/error.rs

Purpose: This file defines the error type returned by the `k2v-client` crate.

Important APIs and types: `Error` is a `thiserror::Error` enum with variants for remote HTTP errors, invalid responses, not found, IO, HTTP construction, Hyper and Hyper client errors, header conversion, JSON deserialization, SigV4 signing parameter/build errors, signing request errors, timeout, and generic messages.

Control flow: There is no active control flow beyond `From` conversions generated by `#[from]` and display formatting generated by `thiserror`. Library code constructs `Remote`, `InvalidResponse`, `Timeout`, `NotFound`, and `Message` explicitly as needed.

State and persistence behavior: It holds error data such as status code, code/message/path strings, or wrapped source errors. It does not persist state.

Dependencies and integration points: It integrates with `http::StatusCode`, `hyper`, `hyper_util`, `serde_json`, `aws_sigv4`, and standard IO. The CLI and library both use this type as their result error.

Risks: Remote error strings are stored as `Cow<'static, str>`; constructing them from response bodies requires owned strings converted into `Cow`. `NotFound` discards response body details. Timeout is client-side and does not imply server cancellation.

Test signals: K2V client integration tests unwrap successful results; malformed/error cases are primarily exercised by raw K2V tests rather than this typed error surface.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/k2v-client/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/k2v-client/lib.rs -->
# sources/object-store/garage/src/k2v-client/lib.rs

Purpose: This library implements a typed async client for Garage's K2V HTTP API. It builds signed requests, percent-encodes K2V paths and query parameters, dispatches via Hyper/Rustls, decodes response status/content types, and exposes ergonomic item, range, batch, index, delete, and poll methods.

Important APIs and types: Public API includes `K2vClientConfig`, `K2vClient`, `CausalityToken`, `K2vValue`, `CausalValue`, `PaginatedRange`, `Filter`, `PollRangeFilter`, `PollRangeResult`, `PartitionInfo`, `BatchInsertOp`, `BatchReadOp`, `BatchDeleteOp`, and `Error`. Major methods are `new`, `new_with_client`, `read_item`, `poll_item`, `poll_range`, `insert_item`, `delete_item`, `read_index`, `insert_batch`, `read_batch`, `delete_batch`, `dispatch`, and `build_url`.

Control flow: Client construction creates a native-root HTTPS connector supporting HTTP and HTTPS. Public methods build URLs and JSON or binary bodies for one K2V operation, then call `dispatch`. `dispatch` adds User-Agent and `x-amz-content-sha256`, signs the request using `aws-sigv4` service name `k2v`, sends it with an operation-specific timeout, extracts causality/content-type headers, handles known status codes, parses remote error JSON, and returns a compact `Response`. Decoding methods then map binary/json/tombstone responses into typed values.

State and persistence behavior: The client stores endpoint, region, credentials, bucket, user-agent, and an HTTP client. Remote K2V state is mutated by insert/delete/batch calls; local state is otherwise stateless between requests. Causality tokens are opaque strings used by callers to serialize or branch updates.

Dependencies and integration points: It depends on Hyper, Hyper-Rustls, AWS SigV4, AWS SDK credentials type, percent-encoding, serde, base64, sha2, hex, tokio, and Garage's K2V HTTP protocol conventions. It is used by integration tests and by `k2v-cli`.

Risks: `dispatch` unwraps header values when building the signable request, so non-UTF8 headers would panic. Timeouts are implemented with `tokio::select!` sleep around the request future. `build_url` always emits `key=value` query pairs even for empty query markers. Poll methods depend on server long-poll behavior, which raw tests mark as currently broken. The client treats 404 as `NotFound` without body details.

Test signals: `k2v_client/simple.rs` validates simple insert/read and Unicode key percent-encoding through `read_index` and `read_batch`. Raw K2V tests indirectly validate protocol expectations that this client encodes/decodes.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/k2v-client/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/Cargo.toml -->
# sources/object-store/garage/src/model/Cargo.toml

Purpose: This manifest defines the `garage_model` crate, the core data model layer for Garage's object store.

Important APIs and types: Package metadata sets name `garage_model`, version `2.3.0`, AGPL license, repository, and readme. The library path is `lib.rs`. Features include default `lmdb` and `sqlite`, optional `k2v`, `fjall`, and `arbitrary`.

Control flow: Cargo resolves this crate's dependencies and feature flags from the manifest. Feature selection controls database backend support and optional K2V/arbitrary code paths in the model crate.

State and persistence behavior: The manifest does not execute persistence itself, but it selects dependencies responsible for metadata tables, RPC integration, block references, database engines, compression, hashing, and serialization used by Garage's persisted model state.

Dependencies and integration points: It depends on internal crates `garage_db`, `garage_rpc`, `garage_table`, `garage_block`, `garage_util`, and `garage_net`, plus argon2, async-trait, blake2, chrono, thiserror, hex, http, base64, parse_duration, tracing, rand, zstd, serde, serde_bytes, futures, and tokio.

Risks: Default-enabling both LMDB and SQLite increases build surface. Backend feature combinations must remain aligned with top-level binary compile checks. The `k2v` feature only enables `garage_util/k2v` here, so related crates must coordinate feature flags.

Test signals: All Garage integration tests exercise `garage_model` indirectly through bucket/key/object/K2V/website state. This manifest itself is validated by workspace builds and feature-enabled test compilation.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/Cargo.toml -->
