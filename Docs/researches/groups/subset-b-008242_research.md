# Research: subset-b-008242

Grouped source-tree-aligned research for RustFS ecstore bucket replication, bucket metadata helpers, metacache listing, and transition-client object APIs.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/replication/replication_state.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/replication/replication_state.rs

## Purpose
This file owns in-memory replication telemetry for buckets, site replication, queue depth, proxy calls, failures, transfer rates, latency, and active replication workers. It is a metrics/state aggregation layer rather than persistent configuration: callers update counters when replication events happen, background tasks age rolling samples, and read APIs expose bucket/node summaries for monitoring and admin surfaces.

## Important APIs, Types, and Functions
- `ExponentialMovingAverage` stores a floating-point rate in an `AtomicU64` bit pattern plus a `Mutex<SystemTime>` update timestamp. It provides `add_value`, `get_current_average`, `update_exponential_moving_average`, `merge`, `Clone`, `Default`, and custom serde.
- `XferStats` tracks `avg`, `curr`, `peak`, and a moving-average measure. `add_size` converts bytes over duration into bytes/second and splits later into small/large transfer channels.
- `ReplStat` is a transient normalized replication event with ARN, status booleans, operation type, transfer size/duration, endpoint, TLS flag, and optional error.
- `SRStats` is global site-replication size/count via atomics.
- `InQueueStats`, `InQueueMetric`, `QueueCache`, and `QueueSample` track queue byte/count current values and rolling 60-second avg/max snapshots.
- `ProxyMetric` and `ProxyStatsCache` count proxied S3 operations by API and failure state.
- `FailStats`, `FailureSample`, and `FailedMetric` track cumulative failure count/size plus a one-hour recent sample deque.
- `LatencyStats`, `BucketReplicationStat`, `BucketReplicationStats`, `BucketStats`, and `SRMetricsSummary` are the exported report shapes.
- `ActiveWorkerStat` samples active worker counts over a 60-second window.
- `ReplicationStats` is the top-level holder with `Arc<SRStats>`, mutexes for workers/queue/proxy, an async `RwLock` bucket cache, and recent bucket stats.

## Control Flow and State Behavior
`ReplicationStats::start_background_tasks` launches three infinite tokio tasks: every 5 seconds it decays transfer EMAs in the bucket cache, every 2 seconds it samples the global replication pool active worker counts, and every 2 seconds it samples queue counters into rolling queue metrics. The tasks are fire-and-forget and are not cancellable through this API.

`ReplicationStats::update` builds a `ReplStat` from `ReplicatedTargetInfo` only for selected transitions: pending data replication when status changes, completed data replication, failed data replication after pending, and replica object status. Completed and failed updates also feed site-replication stats. Bucket stats are keyed by bucket and replication ARN. Completed events increment replicated size/count and update latency and small/large xfer rate; failed events append to `FailStats`; pending events currently do not mutate additional state.

Queue state is maintained through `inc_q` and `dec_q`. They mutate per-bucket and site-wide `AtomicI64` current bytes/count under the queue-cache mutex. `QueueCache::update` snapshots those atomics into rolling samples. Negative queue counts are possible if decrement calls are unbalanced.

Read paths include `get`, `get_all`, `get_sr_metrics_for_node`, `get_latest_replication_stats`, `get_proxy_stats`, `active_workers`, and `has_replication_usage`. `get_all` merges the main replication cache with queue-only and proxy-only buckets so monitoring can see buckets that only have queue/proxy signals.

## Dependencies and Integration Points
The code integrates with `rustfs_filemeta::{ReplicatedTargetInfo, ReplicationStatusType, ReplicationType}`, the global replication pool via `get_global_replication_pool`, the global bucket bandwidth monitor via `get_global_bucket_monitor`, and crate error types. It uses tokio locks and background intervals for async runtime integration, serde for metrics serialization, and standard atomics for high-frequency counters.

## Persistence
All state is in memory. Serde derives/custom serialization allow report structures to be encoded for API responses or diagnostics, but this file does not write state to disk. Rolling sample deques are skipped by serde in queue/failure/worker structures, so serialized/deserialized metrics lose recent-window history.

## Risks and Edge Cases
- `update_moving_avg_static` mutates only the internal EMA atomics while holding a read lock over the bucket cache. This works because the EMA has interior mutability, but the public `avg` fields in `XferStats` are not refreshed there.
- EMA float updates use relaxed load/store with no compare-and-swap; concurrent writers can lose updates.
- `try_lock`/`try_read` paths silently return stale/default values if locks are contended.
- Background tasks run forever and have no idempotence guard; starting them multiple times duplicates samplers.
- `get_sr_metrics_for_node` uses `UNIX_EPOCH` as boot time, producing process uptime that is really wall-clock seconds since 1970.
- `FailStats::merge` drops recent-window samples, so merged cluster stats cannot answer recent failure windows.
- Queue decrements can underflow below zero logically because atomics use signed integers without floor checks.

## Test Signals
Inline tests cover construction, queue rolling averages, recent failure windows, active worker avg/max, deletion, replica-stat updates, completed replication updates, proxy-only bucket visibility, and `SRStats` initial values. They validate important in-memory behavior but do not exercise background task duplication, bandwidth-monitor integration, lock contention, serialization round trips, or distributed aggregation correctness.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/replication/replication_state.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/replication/rule.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/replication/rule.rs

## Purpose
This file extends the S3 `ReplicationRule` DTO with RustFS-specific convenience logic for extracting a rule prefix and deciding whether replica metadata changes should be replicated.

## Important APIs, Types, and Functions
- `ReplicationRuleExt` defines `prefix(&self) -> &str` and `metadata_replicate(&self, obj: &ObjectOpts) -> bool`.
- `prefix` reads `rule.filter.prefix` first, then `rule.filter.and.prefix`, and defaults to an empty string.
- `metadata_replicate` returns true for non-replica objects and for replica objects only when source-selection criteria enables replica modifications.

## Control Flow and State Behavior
The implementation is pure and stateless. It walks optional nested DTO fields and compares `ReplicaModificationsStatus` to `ENABLED`. No mutation or I/O occurs.

## Dependencies and Integration Points
It depends on `s3s::dto::{ReplicationRule, ReplicaModificationsStatus}` and local replication `ObjectOpts`. Replication rule matching and replication admission code can use it to keep DTO interpretation centralized.

## Persistence
No persistence. It interprets an in-memory replication configuration object.

## Risks and Edge Cases
Empty string is both the default and the representation for no prefix, so callers must distinguish whole-bucket rules by convention. The `metadata_replicate` path clones `replica_modifications`; that is low risk but unnecessary. The function only checks replica modification enablement and does not validate destination, status, delete-marker behavior, tags, or other filter constraints.

## Test Signals
No inline tests. Useful tests would cover filter prefix precedence, `and.prefix` fallback, absent filters, replica/non-replica objects, and disabled or absent replica-modification criteria.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/replication/rule.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/tagging/mod.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/tagging/mod.rs

## Purpose
This module provides helpers to parse and format S3 tag query strings using URL form encoding.

## Important APIs, Types, and Functions
- `decode_tags(tags: &str) -> Vec<Tag>` parses `k=v&...`, skips empty keys, creates `s3s::dto::Tag` values, and sorts by key.
- `decode_tags_to_map(tags: &str) -> HashMap<String, String>` parses into a map, also skipping empty keys. Duplicate keys keep the last parsed value.
- `encode_tags(tags: Vec<Tag>) -> String` form-encodes tags with both key and value present, skipping incomplete DTOs.

## Control Flow and State Behavior
All functions are pure conversions. Parsing delegates to `url::form_urlencoded::parse`; encoding delegates to `form_urlencoded::Serializer`. Sorting in `decode_tags` gives deterministic vector order.

## Dependencies and Integration Points
It depends on `s3s::dto::Tag`, `url::form_urlencoded`, and `HashMap`. This module is likely used by bucket/object tagging APIs and replication/lifecycle code that needs deterministic tag matching.

## Persistence
No persistence. It converts between wire query-string form and DTO/map shapes.

## Risks and Edge Cases
`decode_tags_to_map` loses duplicate tag keys silently. `encode_tags` preserves caller-provided order rather than sorting, so round-trip string equality is not guaranteed. Empty values are preserved; empty keys are dropped. No S3 tag limits, character constraints, or maximum encoded length validation are enforced here.

## Test Signals
No inline tests. Good coverage would include URL escaping, duplicate keys, empty key/value handling, sort ordering, and encode/decode round trips.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/tagging/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/utils.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/utils.rs

## Purpose
This file centralizes bucket/object name validation, XML serialization helpers, and argument validation for object, list, and multipart APIs. It translates invalid input into crate `Error` or `StorageError` variants before storage-layer operations touch the filesystem.

## Important APIs, Types, and Functions
- `is_meta_bucketname` identifies internal metadata buckets using `RUSTFS_META_BUCKET` and `MIGRATING_META_BUCKET`.
- `check_bucket_name_common`, `check_valid_bucket_name`, and `check_valid_bucket_name_strict` enforce length, reserved name, IP-address rejection, dot/dash adjacency, and regex rules.
- `check_valid_object_name_prefix` and `check_valid_object_name` provide simple ASCII/length/non-empty checks.
- `deserialize`, `serialize_content`, and `serialize` wrap `s3s::xml` deserialization/serialization.
- `has_bad_path_component`, `is_valid_object_prefix`, and `is_valid_object_name` reject `.`/`..` path segments, double slashes, NULs, invalid UTF-8, and oversized paths.
- Argument validators include `check_copy_obj_args`, `check_get_obj_args`, `check_del_obj_args`, `check_bucket_and_object_names`, `check_list_objs_args`, `check_list_multipart_args`, `check_object_args`, `check_new_multipart_args`, `check_multipart_object_args`, `check_put_object_part_args`, `check_list_parts_args`, `check_complete_multipart_args`, `check_abort_multipart_args`, and `check_put_object_args`.

## Control Flow and State Behavior
Bucket validation first trims and checks basic constraints, then applies strict or relaxed regexes. Object prefix validation scans path bytes manually for bad path components, treating `/` and `\` as separators, trimming whitespace inside each segment. Higher-level API validators compose bucket validation, length/slash checks, prefix/object checks, and upload-id base64 decoding.

## Dependencies and Integration Points
The file depends on disk metadata bucket constants, crate error types, `regex`, `rustfs_utils::path::SLASH_SEPARATOR`, `s3s::xml`, `base64_simd`, and tracing instrumentation. It is a common precondition layer for bucket, object, and multipart handlers.

## Persistence
No persistence. It prevents invalid names from reaching persistence layers where path traversal, filesystem incompatibility, or ambiguous object paths could occur.

## Risks and Edge Cases
- `check_valid_object_name_prefix` rejects non-ASCII despite its error message saying non-UTF-8; `is_valid_object_prefix` accepts broader valid UTF-8. Callers using different validators may get inconsistent behavior.
- Empty upload IDs decode successfully with `URL_SAFE_NO_PAD`; the tests currently document that `check_multipart_object_args` accepts an empty upload ID after decode, which may conflict with S3 expectations.
- Relaxed bucket regex allows uppercase, underscore, and colon; strict validation is used in most external object validators.
- `serialize_content` unwraps UTF-8 conversion, assuming XML serializer output is valid UTF-8.
- Prefix validation rejects double slashes and dot path components even though some S3-compatible clients may expect arbitrary byte-like keys.

## Test Signals
Inline tests cover object names, prefixes, bucket/object argument validation, list validation, multipart upload-id validation, and put-object validation. They explicitly cover path traversal, double slash, NUL, long paths, and the current empty-upload-id behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/versioning/mod.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/versioning/mod.rs

## Purpose
This module adds behavior methods to the S3 `VersioningConfiguration` DTO, including whole-bucket status and prefix-specific enable/suspend decisions with RustFS excluded-prefix and folder-exclusion support.

## Important APIs, Types, and Functions
- `VersioningApi` defines `enabled`, `prefix_enabled`, `prefix_suspended`, `versioned`, and `suspended`.
- `enabled` and `suspended` compare `status` to S3 `Enabled` or `Suspended`.
- `prefix_enabled` requires bucket status enabled, allows empty prefix, rejects folder markers when `exclude_folders` is true, and rejects prefixes matching any configured excluded prefix pattern.
- `prefix_suspended` treats globally suspended buckets as suspended and also treats excluded folders/prefixes under enabled buckets as prefix-suspended.
- `versioned` is true when a prefix is either enabled or suspended.

## Control Flow and State Behavior
The code is pure DTO interpretation. Excluded prefixes are expanded into simple wildcard patterns (`sprefix*`) and matched with `rustfs_utils::string::match_simple`.

## Dependencies and Integration Points
It depends on `s3s::dto::{BucketVersioningStatus, VersioningConfiguration}` and RustFS wildcard matching. `versioning_sys.rs` uses this trait after reading bucket metadata.

## Persistence
No persistence in this file. It interprets persisted versioning configuration loaded elsewhere.

## Risks and Edge Cases
`prefix_enabled("")` returns true for any enabled bucket before checking exclusions, so root/list operations behave differently from concrete object prefixes. `versioned` returning true for suspended prefixes is semantically important because suspended buckets may still need null-version behavior. No inline validation exists for malformed excluded prefixes.

## Test Signals
No inline tests. Tests should cover enabled/suspended/absent statuses, folder exclusions, wildcard excluded prefixes, and the distinction between empty prefix and object prefix.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/versioning/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/versioning_sys.rs -->
# sources/object-store/rustfs/crates/ecstore/src/bucket/versioning_sys.rs

## Purpose
`BucketVersioningSys` is the async access facade for bucket versioning configuration. It reads bucket metadata and exposes convenient boolean checks for enabled/suspended state.

## Important APIs, Types, and Functions
- `BucketVersioningSys::new` and `Default` construct the empty facade.
- `enabled`, `prefix_enabled`, `suspended`, and `prefix_suspended` call `get` and return false on errors after logging.
- `get(bucket)` returns a default `VersioningConfiguration` for internal metadata buckets, otherwise locks the global bucket metadata system and calls `get_versioning_config`.

## Control Flow and State Behavior
All public checks are async static methods. They centralize error-to-false fallback, which keeps callers simple but hides metadata failures. `get` obtains the metadata system with `get_bucket_metadata_sys`, takes a write lock, fetches config and ignores the second tuple element.

## Dependencies and Integration Points
It depends on `metadata_sys::get_bucket_metadata_sys`, `VersioningApi`, `RUSTFS_META_BUCKET`, crate `Result`, S3 DTOs, and tracing warnings. It is an integration point between bucket metadata persistence and object operation policy decisions.

## Persistence
This file does not persist itself; it reads persisted bucket metadata via the metadata subsystem. Internal metadata buckets are treated as unversioned/default without hitting metadata storage.

## Risks and Edge Cases
Error fallback to false may make transient metadata-store failures look like disabled versioning. `bucket.starts_with(RUSTFS_META_BUCKET)` treats any bucket with that prefix as internal. The metadata system is acquired with a write lock even though this path appears read-only, which may reduce concurrency.

## Test Signals
No inline tests. Useful tests would mock metadata config fetches, metadata errors, internal bucket bypass, and prefix-specific delegated behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/versioning_sys.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/cache_value/metacache_set.rs -->
# sources/object-store/rustfs/crates/ecstore/src/cache_value/metacache_set.rs

## Purpose
This file implements raw distributed metacache listing over erasure disks. It launches per-disk producers that walk directory metadata into async duplex streams, then a merge consumer compares `MetaCacheEntry` heads across disks, emits agreed entries, emits partial disagreement sets, handles fallback disks, enforces read quorum, and avoids hangs from stalled producers.

## Important APIs, Types, and Functions
- `AgreedFn`, `PartialFn`, and `FinishedFn` are async callback types for agreed entries, partial entries with error state, and final error summaries.
- `ListPathRawOptions` carries disks, fallback disks, bucket/path, recursion and filtering options, quorum (`min_disks`), reporting and limit flags, callbacks, and test-only reader behavior/timeout controls.
- `list_path_raw(rx, opts)` is the main async function.
- `peek_with_timeout` wraps `MetacacheReader::peek` in a timeout and returns `PeekOutcome::{Ready, Error, TimedOut}`.
- `record_producer_error` and `producer_error` share producer failures with the merge consumer through per-disk `OnceLock<DiskError>`.
- Test-only `TestReaderBehavior` simulates EOF, stalls, ignored cancellation, producer errors, and partial output followed by timeout.

## Control Flow and State Behavior
`list_path_raw` rejects an empty disk list with `ErasureReadQuorum`, builds one duplex stream and spawned producer per disk, and creates a shared cancellation token. Each producer calls `walk_dir` with `WalkDirOptions`; if the primary disk is missing or fails, it tries online fallback disks from a local queue clone. Producer failures are recorded for the corresponding disk.

The merge job loops over all readers. For each reader without a stored error, it peeks with a drive stall timeout. EOF-like conditions increase `at_eof`; file/volume not found also count specific not-found counters; timeouts mark that disk failed, increment `rustfs_list_path_raw_stall_total`, log a structured warning, and detach the reader so the loop can continue. Producer-recorded errors are preferred over generic EOF when a writer closes after an error.

The merge logic chooses the lexicographically smallest current entry name. Exact matches across all readers increment `agree`; same-name non-matching entries are partial; greater names wait for later rounds; lower names reset previously selected top entries. If all readers agree, it skips one entry on every reader and calls `agreed`. Otherwise it skips readers that had the selected top entry and calls `partial`.

Quorum exits are explicit. Too many volume-not-found or file-not-found signals return those errors. Too many other errors call `finished`, prefer `Timeout` if any timeout occurred, return a single error if only one exists, or build a combined drive error string. If all readers are EOF or tolerated failures, listing succeeds.

After a successful merge, remaining producers are cancelled and unfinished jobs are aborted before join. Producer join errors and producer disk errors are logged; final producer errors fail only if their count exceeds `disks.len() - min_disks`.

## Dependencies and Integration Points
It depends on disk abstractions (`DiskStore`, `DiskAPI`, `WalkDirOptions`, `DiskError`), `rustfs_filemeta::{MetaCacheReader, MetaCacheWriter in tests, MetaCacheEntry, MetaCacheEntries}`, tokio spawn/duplex/timeout, cancellation tokens, metrics counters, and structured tracing. Higher-level object-listing code can use callbacks to assemble list results from agreed and partial metadata entries.

## Persistence
The code reads persisted object metadata listings from disks through `walk_dir`; it does not write object metadata. Runtime state is in memory: producer tasks, reader buffers, error arrays, and callback invocations.

## Risks and Edge Cases
- Each producer receives its own clone of the fallback disk queue, so multiple failed primaries can select the same fallback disk concurrently.
- `min_disks` drives all quorum math; misconfiguration can either tolerate too much corruption/stall or fail healthy listings.
- Callback errors are impossible because callback futures return `()`, so failures in consumer aggregation cannot be propagated unless encoded externally.
- Lexicographic merge correctness relies on each disk stream being sorted consistently by `MetaCacheEntry.name`.
- Aborting producer tasks is intentional, but disk `walk_dir` implementations must tolerate cancellation/abort.
- Timeouts detach the reader and continue; this avoids hangs but can hide slow-drive data if quorum is still satisfied.

## Test Signals
Inline async tests cover empty disk list, timeout when quorum cannot be met, tolerated stalled reader after quorum EOF, aborting an unresponsive producer, producer timeout after partial output, `peek_with_timeout` timeout/read success, and propagation of producer access denied. These tests strongly signal recent hardening around stalled drives and partial producer failures.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/cache_value/metacache_set.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/cache_value/mod.rs -->
# sources/object-store/rustfs/crates/ecstore/src/cache_value/mod.rs

## Purpose
This module exposes cache-value submodules and a process-global cancellation token for raw list-path operations.

## Important APIs, Types, and Functions
- `pub mod metacache_set` exports the distributed listing implementation.
- `LIST_PATH_RAW_CANCEL_TOKEN: Arc<CancellationToken>` is initialized with `lazy_static`.

## Control Flow and State Behavior
There is no function control flow here. The cancellation token is allocated at first static access and can be cloned by callers that need a shared cancellation signal.

## Dependencies and Integration Points
Depends on `lazy_static`, `Arc`, and `tokio_util::sync::CancellationToken`. It is the module-level integration point for consumers of `metacache_set`.

## Persistence
No persistence. The token is process-local runtime state.

## Risks and Edge Cases
A single global cancellation token, once cancelled, remains cancelled. If used as a reusable global for multiple independent listings, cancellation could permanently affect future operations unless callers create child tokens or the process recreates state elsewhere.

## Test Signals
No inline tests in this file. Behavior is mostly covered indirectly by `metacache_set` tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/cache_value/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/admin_handler_utils.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/admin_handler_utils.rs

## Purpose
Defines the simple `AdminError` type used by admin client utilities to carry a code, human-readable message, and HTTP status code.

## Important APIs, Types, and Functions
- `AdminError { code, message, status_code }` derives `thiserror::Error`, `Debug`, `Clone`, and `PartialEq`.
- `Display` renders only the message.
- `AdminError::new` constructs an arbitrary code/message/status.
- `AdminError::msg` constructs an `InternalError` with status 500.

## Control Flow and State Behavior
The type is a data container with constructors. No I/O or mutation beyond construction.

## Dependencies and Integration Points
Depends on `http::StatusCode`, `std::fmt`, and `thiserror`. It can be wrapped in `std::io::Error::other` or returned directly by admin APIs.

## Persistence
No persistence.

## Risks and Edge Cases
`Display` omits code and status, so logs or wrapped errors may lose structured context if only formatted as a string. `Default` gives an empty code/message with default status, which may be ambiguous.

## Test Signals
No inline tests. Simple tests could validate constructors and display behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/admin_handler_utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_bucket_policy.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/api_bucket_policy.rs

## Purpose
Implements transition-client bucket policy operations: set, put, remove, and get policy through S3-compatible `?policy` requests.

## Important APIs, Types, and Functions
- `set_bucket_policy` deletes the policy when passed an empty string, otherwise delegates to `put_bucket_policy`.
- `put_bucket_policy` sends `PUT` with `?policy`, policy bytes as body, and content length set to policy length; success is `204 No Content` or `200 OK`.
- `remove_bucket_policy` sends `DELETE ?policy` with an empty SHA256 hash and expects `204 No Content`.
- `get_bucket_policy` delegates to `get_bucket_policy_inner`.
- `get_bucket_policy_inner` sends `GET ?policy`, buffers the full body, and returns it as lossy UTF-8.

## Control Flow and State Behavior
Every method builds `RequestMetadata` for `TransitionClient::execute_method`. Error responses are converted with `http_resp_to_error_response`, but `get_bucket_policy_inner` does not check status before returning the body.

## Dependencies and Integration Points
Uses `TransitionClient`, `RequestMetadata`, `ReaderImpl`, `http`, `hyper::Bytes`, `http_body_util::BodyExt`, `HeaderMap`, and `EMPTY_STRING_SHA256_HASH`. It is part of the client API surface for bucket policy migration/transition operations.

## Persistence
The client does not persist locally. Successful requests mutate bucket policy on the remote endpoint.

## Risks and Edge Cases
`get_bucket_policy_inner` ignores non-OK statuses and may return an XML error body as a policy string. Bodies are fully buffered without using `MAX_S3_CLIENT_RESPONSE_SIZE` despite importing it. Empty policy as delete is convenient but prevents setting a deliberately empty policy document if such a thing were ever meaningful.

## Test Signals
No inline tests. Tests should cover status handling, non-UTF-8 body behavior, empty policy delete behavior, and response body limits.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_bucket_policy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_error_response.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/api_error_response.rs

## Purpose
Provides S3-style client error response structures and helpers to convert HTTP responses or local upload validation errors into `ErrorResponse` values.

## Important APIs, Types, and Functions
- `ErrorResponse` stores S3 error code, message, bucket/key/resource, request/host IDs, region, server, and local `StatusCode`.
- Custom serde keeps `RequestId` PascalCase and maps error-code strings to `S3ErrorCode`.
- `to_error_response` extracts an embedded `ErrorResponse` from `std::io::Error`.
- `http_resp_to_error_response` parses XML error bodies or synthesizes errors from HTTP status, then overlays headers such as `Server`, `x-minio-error-code`, `x-minio-error-desc`, `x-amz-request-id`, `x-amz-id-2`, and `x-amz-bucket-region`.
- Constructors include `err_transfer_acceleration_bucket`, `err_entity_too_large`, `err_entity_too_small`, `err_unexpected_eof`, `err_invalid_argument`, and `err_api_not_supported`.

## Control Flow and State Behavior
HTTP conversion first turns the body into lossy UTF-8. If headers are empty or the status is client/server error, the function immediately returns `ResponseInterrupted` with "Invalid HTTP response"; otherwise it tries to parse XML and falls back to status-based S3 codes. Header-derived overrides are applied after parsing/fallback.

## Dependencies and Integration Points
Uses `http`, `serde`, `quick_xml`, `thiserror`, and `s3s::S3ErrorCode`. Most client API modules wrap this response in `std::io::Error::other`.

## Persistence
No persistence. This is wire-error translation.

## Risks and Edge Cases
- The early return on `resp_status.is_client_error()` or server error prevents parsing normal S3 XML error bodies for most error statuses. That likely collapses useful remote errors into `ResponseInterrupted`.
- `serialize_code` serializes every code as an empty string, so JSON serialization loses the actual error code.
- Several messages use curly quotes, which can be awkward for exact S3 compatibility.
- `to_error_response` only extracts when the inner error reference is exactly `ErrorResponse`; string-wrapped errors become default responses.

## Test Signals
One inline test validates that JSON serialization uses `RequestId` and does not expose `request_id`. There are no tests for XML parsing, header overrides, status fallback mapping, or code serialization fidelity.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_error_response.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_get_object.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/api_get_object.rs

## Purpose
Contains the transition-client object GET path and a placeholder `Object` reader abstraction. The implemented async path fetches an object and buffers its body into a `ReadCloser`; the public `get_object` and `Object` read machinery are currently unsupported placeholders.

## Important APIs, Types, and Functions
- `TransitionClient::get_object` returns `Unsupported`.
- `TransitionClient::get_object_inner` sends `GET`, builds `ObjectInfo` from response headers with `to_object_info`, buffers all body frames into memory, and returns `(ObjectInfo, HeaderMap, BufReader<Cursor<Vec<u8>>>)`.
- `GetRequest`, `GetResponse`, and `Object` model a stateful reader with offset/seek/read/stat fields.
- `Object::{do_get_request, read, read_at, seek, stat, close}` mirror a lazy ranged-reader design, but `do_get_request` returns `Unsupported`.

## Control Flow and State Behavior
`get_object_inner` builds `RequestMetadata` from bucket, object, option query values, and option headers, then delegates to `execute_method`. It does not inspect HTTP status before parsing headers/body, relying on `execute_method` or `to_object_info` to fail. `Object` methods mutate offsets and state flags conceptually, but no real request path exists.

## Dependencies and Integration Points
Uses `GetObjectOptions`, `TransitionClient`, `RequestMetadata`, `ReaderImpl`, `ObjectInfo`, `ReadCloser`, `to_object_info`, `http_body_util`, `hyper::Bytes`, `EMPTY_STRING_SHA256_HASH`, and tokio readers. `fget_object` depends on `get_object`, so it inherits the unsupported behavior.

## Persistence
No local persistence. It reads object bytes from the remote endpoint and materializes them in memory.

## Risks and Edge Cases
The main public `get_object` API is not implemented. The implemented `get_object_inner` buffers whole objects, which is risky for large objects and defeats streaming. It does not enforce imported response-size limits. Lack of explicit status handling may mis-handle error bodies depending on `execute_method` behavior. `Object` methods ignore some internal errors (`oerr` is unused) and are dead/private placeholders.

## Test Signals
No inline tests. Needed tests include non-OK status behavior, range option propagation, large object streaming or limits, header-to-object-info mapping, and public `get_object` implementation once completed.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_get_object.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_get_object_acl.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/api_get_object_acl.rs

## Purpose
Implements `GET ?acl` for an object and maps returned ACL grants into object metadata, especially canned ACL headers.

## Important APIs, Types, and Functions
- DTOs: `Grantee`, `Grant`, `AccessControlList`, and `AccessControlPolicy`.
- `TransitionClient::get_object_acl` sends `GET` with `acl` query, buffers the body, converts non-OK responses through `http_resp_to_error_response`, parses XML ACL, fetches `stat_object`, copies owner fields, and inserts `X-Amz-Acl` for recognized canned ACLs.
- `get_canned_acl` detects `private`, `authenticated-read`, `public-read`, `bucket-owner-read`, and `public-read-write` from grant patterns.
- `get_amz_grant_acl` maps grant permissions to `X-Amz-Grant-*` header value lists.

## Control Flow and State Behavior
The method fetches ACL first, then fetches object stat and enriches the returned `ObjectInfo`. Grant-header mapping is computed but currently not inserted because that loop is commented out.

## Dependencies and Integration Points
Depends on `TransitionClient`, `GetObjectOptions`, `ObjectInfo`, request metadata, `http_body_util`, `quick_xml`, S3 `Owner`, and `http` headers. It integrates ACL results with object stat metadata.

## Persistence
No local persistence. It reads remote ACL state.

## Risks and Edge Cases
`AccessControlPolicy.owner` is marked `serde(skip)`, so parsed owner fields will remain default; copying owner into `obj_info` is likely ineffective. `get_canned_acl` calls `ac_policy.owner.id.clone().unwrap()` and can panic if owner ID is absent in the two-grant bucket-owner-read case. Full grant ACL headers are computed but discarded. XML parsing uses `String::from_utf8(...).unwrap()`, so invalid UTF-8 panics.

## Test Signals
No inline tests. Tests should cover XML owner parsing, canned ACL detection, grant header insertion, malformed UTF-8/XML, and non-OK error conversion.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_get_object_acl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_get_object_attributes.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/api_get_object_attributes.rs

## Purpose
Implements a client call for S3 `GetObjectAttributes`, including request option headers and response parsing into object attributes, checksum, and parts structures.

## Important APIs, Types, and Functions
- `ObjectAttributesOptions` carries `max_parts`, `version_id`, and `part_number_marker`.
- `ObjectAttributes` stores response version ID, last-modified time, and `ObjectAttributesResponse`.
- DTOs: `Checksum`, `ObjectParts`, `ObjectAttributesResponse`, and private `ObjectAttributePart`.
- `ObjectAttributes::parse_response` reads `Last-Modified`, `x-amz-version-id`, and XML body.
- `TransitionClient::get_object_attributes` builds `?attributes`, headers for requested attributes/max parts/part marker, sends a request, checks endpoint support, handles non-OK, and parses the response.

## Control Flow and State Behavior
The client uses `HEAD` with `?attributes` and `x-amz-object-attributes` headers, then reads the body. It treats a non-empty `ETag` header as evidence that the endpoint does not support object attributes and returns an unsupported error. Non-OK bodies are parsed as `AccessControlPolicy` and return its permission field as an error.

## Dependencies and Integration Points
Depends on constants such as `GET_OBJECT_ATTRIBUTES_MAX_PARTS`, S3 attribute headers, `TransitionClient`, request metadata, `quick_xml`, `time`, and `AccessControlPolicy` from the ACL module.

## Persistence
No local persistence. It reads remote object metadata.

## Risks and Edge Cases
Many header reads use `unwrap`, so missing `ETag`, `Last-Modified`, or version ID can panic. The use of `HEAD` while expecting a body is suspicious for S3 `GetObjectAttributes`, which is normally a `GET` operation. The endpoint-support check appears inverted or brittle: a normal object `ETag` header causes unsupported. Non-OK error parsing as ACL policy is likely wrong. Imported response-size limits are not enforced.

## Test Signals
No inline tests. Tests should cover supported and unsupported endpoint responses, missing headers, versionless objects, XML body parsing, non-OK S3 error parsing, and correct HTTP method expectations.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_get_object_attributes.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_get_object_file.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/api_get_object_file.rs

## Purpose
Intended to implement `fget_object`, downloading an object to a local file through a temporary `.part.rustfs` path with resume support.

## Important APIs, Types, and Functions
- `TransitionClient::fget_object(bucket, object, file_path, opts)` validates the target path, creates parent directories, stats the object, computes a part path, opens the part file, optionally sets a range on Windows, calls `get_object`, and renames the part file to the final path.

## Control Flow and State Behavior
The method first requires `std::fs::metadata(file_path)` to succeed; if the file does not exist it returns an error. It creates a directory from `parent.file_name()` rather than the full parent path. It opens the temp part path without create/write options, then calls the currently unsupported `get_object`. The actual copy from object reader to file is commented out, as is cleanup logic.

## Dependencies and Integration Points
Depends on `GetObjectOptions`, `TransitionClient::stat_object`, `TransitionClient::get_object`, local filesystem APIs, platform-specific metadata extensions, and `err_invalid_argument`.

## Persistence
This is the only file in the subset that directly mutates local filesystem state. Intended persistence is a downloaded object file via temp-file rename, but the copy path is currently disabled.

## Risks and Edge Cases
The function is not operational: it errors if the destination does not already exist, opens the part file without creating it, does not copy bytes, relies on unsupported `get_object`, and may rename an empty/old part file. Parent directory creation uses only the last path component. Cleanup is commented out, so partial files may remain. Permissions are set on a copied metadata object without writing them back with `set_permissions`.

## Test Signals
No inline tests. Tests should cover new-file downloads, existing-directory errors, parent directory creation, temp-file cleanup, resume behavior, and integration after `get_object` is implemented.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_get_object_file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_get_options.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/api_get_options.rs

## Purpose
Defines GET/HEAD option structures for object operations and helpers for conditional headers, ranges, checksum mode, versioning, part-number selection, and query parameters.

## Important APIs, Types, and Functions
- `AdvancedGetOptions` carries internal replication flags.
- `GetObjectOptions` stores arbitrary headers, request parameters, version ID, part number, checksum mode, and internal options.
- `StatObjectOptions` aliases `GetObjectOptions`.
- `header` validates stored headers into `HeaderMap` and adds `x-amz-checksum-mode: ENABLED` when requested.
- `set` validates a header name/value before storing it.
- `set_req_param`/`add_req_param`, `set_match_etag`, `set_match_etag_except`, `set_unmodified`, `set_modified`, `set_range`, and `to_query_values` build request metadata.

## Control Flow and State Behavior
The struct is mutable caller-owned state. Header setters validate via `http` types and store canonical header-name strings. `header()` is tolerant of invalid prepopulated values: it logs and skips them. `to_query_values` combines version ID, part number, and arbitrary request params.

## Dependencies and Integration Points
Uses `http::{HeaderMap, HeaderName, HeaderValue}`, `time::OffsetDateTime`, tracing warnings, and `err_invalid_argument`. All GET/stat/list-adjacent client methods consume this option type.

## Persistence
No persistence. It shapes outgoing request metadata.

## Risks and Edge Cases
Date headers use `OffsetDateTime::to_string()` rather than an HTTP-date/RFC7231 formatter, which may not match S3 expectations. Suffix range behavior for `set_range(0, negative)` emits `bytes=-N` only when `end < 0`; the sign convention should be documented. Invalid headers inserted directly into `headers` are skipped only at `header()` time.

## Test Signals
Inline tests cover normal range header creation, rejection of invalid header values in `set`, and skipping invalid prepopulated header values.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_get_options.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_list.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/api_list.rs

## Purpose
Provides transition-client list APIs, with only ListObjectsV2 query implemented. Other bucket/list/version/multipart listing entry points are explicit unsupported placeholders.

## Important APIs, Types, and Functions
- `list_buckets` returns `Unsupported`.
- `list_objects_v2_query` builds `list-type=2` requests with prefix, delimiter, continuation token, owner, metadata, start-after, encoding, max-keys, and custom headers. It parses `ListBucketV2Result`.
- Unsupported placeholders include `list_object_versions_query`, `list_objects_query`, `list_multipart_uploads_query`, `list_object_parts`, `find_upload_ids`, and `list_object_parts_query`.
- `ListObjectsOptions` stores version/list option flags and basic list parameters.
- `ListObjectsOptions::set` accepts string keys for prefix/start-after/max-keys/delimiter and boolean-like flags.
- `decode_s3_name` currently returns names unchanged, even for `encoding-type=url`.

## Control Flow and State Behavior
The V2 query path builds `RequestMetadata`, executes `GET`, checks for `200 OK`, buffers the full XML response, deserializes it, checks truncated responses have a continuation token, then decodes object names and common prefixes. State is local to the call.

## Dependencies and Integration Points
Depends on client S3 datatype DTOs, `TransitionClient`, `RequestMetadata`, credentials error types for placeholders, `BucketInfo`, HTTP/hyper body utilities, `quick_xml`, and `EMPTY_STRING_SHA256_HASH`.

## Persistence
No persistence. It reads remote bucket listing state.

## Risks and Edge Cases
Most list APIs are not implemented. `decode_s3_name` does not URL-decode despite requesting `encoding-type=url`, so keys containing escaped characters may be returned incorrectly. Full response buffering ignores imported size limits. `String::from_utf8(...).unwrap()` can panic on invalid XML bytes. Boolean parsing in `ListObjectsOptions::set` has unusual `vtrue` handling.

## Test Signals
No inline tests. Needed tests include V2 XML parsing, non-OK error conversion, truncated-without-token validation, URL decoding, invalid XML/UTF-8 handling, and behavior of unsupported methods.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_list.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_put_object.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/api_put_object.rs

## Purpose
Defines put-object options and the top-level routing logic that chooses single PUT, multipart with known size, multipart without length, or parallel stream multipart based on object size, signer, and options.

## Important APIs, Types, and Functions
- `AdvancedPutOptions` carries replication source/version/etag/status/time metadata and internal replication flags.
- `PutObjectOptions` carries user metadata/tags, content headers, object lock settings, storage class, redirect, part size, checksum settings, multipart flags, and custom headers.
- `PutObjectOptions::header` converts options and user metadata into HTTP headers.
- `PutObjectOptions::validate` is currently a no-op.
- `TransitionClient::put_object` rejects unknown size with disabled multipart, then delegates.
- `put_object_common` enforces max size, sets default auto checksum, decides between `put_object_gcs`, `put_object_multipart`, `put_object_multipart_stream_parallel`, `put_object_multipart_stream_no_length`, or `put_object_multipart_stream`.
- `put_object_multipart_stream_no_length` initiates multipart upload for unknown-size input and uploads sequential parts.

## Control Flow and State Behavior
The route depends on `size`, `disable_multipart`, `concurrent_stream_parts`, `num_threads`, signer type, and computed/default part size. Unknown-size uploads require multipart unless parallel stream mode is selected. The no-length multipart path reads from `ReaderImpl`, computes MD5 or checksum headers, uploads parts, builds `CompleteMultipartUpload`, completes, and sets uploaded size.

## Dependencies and Integration Points
Depends on S3 DTOs and headers, checksum helpers, client constants, multipart APIs, `ReaderImpl`, `TransitionClient`, `UploadInfo`, `SignatureType`, and header classification helpers for user metadata.

## Persistence
No local persistence. Successful calls create/replace remote objects and multipart upload state on the target endpoint.

## Risks and Edge Cases
- The no-length multipart loop reads the entire `ReaderImpl` into `buf` on every iteration; with `Body` it reuses the whole body for every part rather than slicing by `part_size`.
- `total_parts_count` for unknown size is computed as maximum possible parts, so without EOF-aware reading the loop can over-upload or repeat data.
- `PutObjectOptions::header` unwraps metadata header values, so invalid user metadata values panic.
- Tags are stored but not emitted as tagging headers/query here.
- `validate` does not enforce checksum/signer/trailing-header constraints.

## Test Signals
No inline tests. Tests should cover routing decisions, header generation, invalid metadata values, unknown-size multipart EOF behavior, checksum header behavior, and integration with multipart completion.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_put_object.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_put_object_common.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/api_put_object_common.rs

## Purpose
Contains shared put-object helpers, especially multipart part-size calculation and upload-id creation.

## Important APIs, Types, and Functions
- `is_object(&ReaderImpl)` and `is_read_at(ReaderImpl)` classify `ReaderImpl::ObjectBody`.
- `optimal_part_info(object_size, configured_part_size)` returns `(total_parts_count, part_size, last_part_size)` while enforcing S3 multipart limits.
- `TransitionClient::new_upload_id` delegates to `initiate_multipart_upload` and returns its `upload_id`.

## Control Flow and State Behavior
`optimal_part_info` treats `object_size == -1` as unknown and substitutes `MAX_MULTIPART_PUT_OBJECT_SIZE`. Configured part sizes are validated against object size, min/max part sizes, and max part count. Without a configured size, it computes the smallest aligned part size that keeps parts within `MAX_PARTS_COUNT`.

## Dependencies and Integration Points
Depends on put options, multipart constants, error constructors, `ReaderImpl`, and `TransitionClient::initiate_multipart_upload`. All multipart upload paths use this function.

## Persistence
No local persistence. `new_upload_id` creates remote multipart-upload state.

## Risks and Edge Cases
Configured part size larger than object size is rejected, although single-part multipart uploads with a part larger than object data can be acceptable if only bytes read are uploaded; this design is stricter. Unknown-size mode sets effective object size to max multipart size, producing max-part loops unless caller has separate EOF handling. `is_read_at` consumes its reader argument and currently duplicates `is_object`.

## Test Signals
No inline tests in this file. Tests should cover boundary sizes, unknown size, configured part size min/max, too many parts, and single small objects.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_put_object_common.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_put_object_multipart.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/api_put_object_multipart.rs

## Purpose
Implements non-streaming multipart upload primitives: initiate, upload part, complete, and a fallback wrapper for access-denied multipart attempts.

## Important APIs, Types, and Functions
- `put_object_multipart` calls `put_object_multipart_no_stream`; on access denied it may fall back to single PUT if the object fits single PUT limits.
- `put_object_multipart_no_stream` computes part info, initiates upload, reads parts, hashes them, uploads each part, builds `CompleteMultipartUpload`, completes, and returns `UploadInfo`.
- `initiate_multipart_upload` sends `POST ?uploads`, validates internal source version UUID, and should parse `InitiateMultipartUploadResult`.
- `upload_part` validates size/part number/upload ID, sends `PUT ?partNumber&uploadId`, and returns `ObjectPart` from response headers.
- `complete_multipart_upload` sends `POST ?uploadId` with marshalled completion XML and returns `UploadInfo`.
- `UploadPartParams` bundles upload-part request fields.

## Control Flow and State Behavior
Multipart state lives remotely: initiate returns an upload ID, upload-part calls create part state, complete finalizes object state. Locally, parts are stored in a `HashMap<i64, ObjectPart>` then converted into sorted completion parts.

## Dependencies and Integration Points
Depends on checksum modes, hash utilities, S3 multipart DTOs, client constants, `RequestMetadata`, `ReaderImpl`, `UploadInfo`, `trim_etag`, UUID validation, and error-response helpers.

## Persistence
No local persistence. It mutates remote multipart upload and object state.

## Risks and Edge Cases
- `initiate_multipart_upload` returns `InitiateMultipartUploadResult::default()` instead of parsing the response body, so `upload_id` is likely empty and later calls fail.
- `complete_multipart_upload` sets `content_length: 100` instead of the actual XML length and returns a default `CompleteMultipartUploadResult` without parsing response body.
- Upload loops read the entire reader for every part instead of slicing by part size.
- `hash_sums["md5"]` and `hash_sums["sha256"]` indexing can panic if those keys are absent.
- There is no abort-multipart cleanup on part upload or complete failure.

## Test Signals
No inline tests. High-priority tests are initiate response parsing, completion body length/parsing, part slicing, upload-id validation, error cleanup/abort, and checksum combinations.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_put_object_multipart.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_put_object_streaming.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/api_put_object_streaming.rs

## Purpose
Implements streaming and single-PUT object upload paths: known-size multipart streaming, optional checksum mode, parallel streaming, Google/single PUT style upload, and the low-level `put_object_do`.

## Important APIs, Types, and Functions
- `UploadedPartRes` and `UploadPartReq` are small part-result/request structs.
- `put_object_multipart_stream` routes to parallel, read-at, or optional-checksum multipart stream path.
- `put_object_multipart_stream_from_readat` adjusts checksum options then delegates.
- `put_object_multipart_stream_optional_checksum` uploads parts sequentially with MD5 or auto-checksum headers, completes multipart, and validates total uploaded size.
- `put_object_multipart_stream_parallel` attempts concurrent part uploads using buffer and error channels, an `RwLock<HashMap>` for parts, and `join_all`.
- `put_object_gcs` is the single PUT wrapper.
- `put_object_do` builds and executes the final `PUT` request and maps response headers to `UploadInfo`.

## Control Flow and State Behavior
Known-size streaming computes part count/size, initiates upload, removes checksum-algorithm metadata, reads part buffers from `ReaderImpl`, uploads parts, builds completion XML, applies aggregate checksum metadata, completes, and sets uploaded size. Parallel mode preallocates buffers through a channel, spawns async upload futures, collects results, and completes once all futures resolve. Single PUT sends the provided reader directly through `execute_method`.

## Dependencies and Integration Points
Depends on checksum helpers (`add_auto_checksum_headers`, `apply_auto_checksum`), multipart primitives (`UploadPartParams`, `upload_part`, `complete_multipart_upload`), constants, request metadata, UUID validation for source version IDs, cancellation tokens, channels, and response header parsing for version/expiration/checksums.

## Persistence
No local persistence. It writes remote object data and multipart upload state.

## Risks and Edge Cases
- Multiple loops use `for i in 1..part_number` where `part_number == total_parts_count`, which omits the final part from completion.
- Sequential and parallel paths read the entire reader into each part buffer rather than bounded `part_size` chunks.
- Parallel preallocated buffers are created with capacity but length zero, then code expects `buf.len() == part_size`, causing immediate errors before reading.
- `join_all` results are not inspected; errors are expected through a side channel and can be missed.
- No abort-multipart cleanup on failure.
- Expiration header parsing uses `unwrap`, so malformed expiration headers panic.
- `put_object_do` only accepts `200 OK`; S3 PUT Object commonly returns `200 OK`, but compatibility with other success statuses should be explicit.

## Test Signals
No inline tests. Tests should cover part inclusion, actual chunked reads, parallel buffer behavior, error propagation from futures, multipart abort on failure, checksum aggregation, and single-PUT response header parsing.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_put_object_streaming.rs -->
