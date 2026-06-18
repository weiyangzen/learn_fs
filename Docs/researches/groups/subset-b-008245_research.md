# Research: subset-b-008245

Grouped research for RustFS ecstore disk boundary files. Each section preserves the source path and is bounded for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/disk_store.rs -->
# sources/object-store/rustfs/crates/ecstore/src/disk/disk_store.rs

## Purpose
`disk_store.rs` wraps a concrete local disk implementation with health tracking, stale disk-id checks, timeout policy, active monitoring, recovery probing, and `DiskAPI` delegation. It is the local-drive equivalent of the remote disk health boundary used by RPC disks, and it is intentionally stateful: every operation can update health state, waiting-operation metrics, and recovery state.

## Important APIs, Types, And Functions
- `DriveTimeoutProfile` and `TimeoutHealthPolicy` parse env-backed timeout behavior. The profile chooses default versus high-latency timeout defaults; the health policy controls whether scanner/listing timeouts mark a drive unhealthy.
- `get_max_timeout_duration`, `get_drive_metadata_timeout`, `get_drive_disk_info_timeout`, `get_drive_list_dir_timeout`, `get_drive_walkdir_timeout`, `get_drive_walkdir_stall_timeout`, `get_drive_active_check_interval`, and `get_drive_active_check_timeout` centralize disk timeout configuration via `rustfs_config` and `rustfs_utils`.
- `DiskHealthTracker` stores atomics for last success/start timestamps, current binary health status, waiting count, runtime state, failure/success streaks, offline timestamps, and last capacity probe.
- `DiskHealthTracker::mark_failure`, `mark_offline`, `mark_recovery_success`, `record_operation_success`, and `reset_for_store_init_retry` implement the runtime state machine.
- `LocalDiskWrapper` owns an `Arc<LocalDisk>`, a shared `DiskHealthTracker`, a `CancellationToken`, a cached disk id, and the timeout health policy.
- `LocalDiskWrapper::track_disk_health_with_op_and_timeout_action` is the core wrapper around local disk futures; it rejects faulty/stale disks, increments waiting counters, applies timeout, records success, and optionally marks timeout as a health failure.
- The `DiskAPI for LocalDiskWrapper` implementation delegates every disk operation to `LocalDisk` while applying operation-specific timeout and health policy.

## Control Flow
Wrapper construction combines the caller's `health_check` flag with `RUSTFS_DRIVE_ACTIVE_MONITORING`; it records the drive as online. `enable_health_check` spawns `monitor_disk_writable`, which periodically skips recently successful drives, writes and reads a test object under `.rustfs.sys/tmp`, deletes it, and marks failures. Once a drive becomes offline, `monitor_disk_status` probes at the configured returning interval until enough consecutive successes move the drive from `Offline` to `Returning` to `Online`.

Normal operations flow through `track_disk_health_with_op_and_timeout_action`: first fail fast on a faulty drive, then call `check_disk_stale`, update `last_started`, increment `waiting`, and execute either directly or under `tokio::time::timeout`. Successes update `last_success` or advance recovery. Timeouts decrement `waiting`, emit `rustfs_drive_op_timeout_total`, log structured warnings, and return `DiskError::Timeout`; depending on `TimeoutHealthAction`, the timeout may also advance the health state and spawn a recovery monitor.

The `DiskAPI` delegation is not uniform. Metadata, disk-info, list-dir, and walk-dir use dedicated timeout getters. `walk_dir` always ignores timeout failures for health marking because writer backpressure and scanner stalls should not poison a drive. `read_metadata`, `list_dir`, and `disk_info` use the scanner-sensitive timeout policy, so an env policy can also avoid marking scanner timeouts as disk failures. Many file/data operations use the max timeout, while append/create/list/delete/verify paths sometimes use `Duration::ZERO`, meaning no total timeout but still health and stale checks. `delete_versions` is custom because it returns per-item errors instead of one `Result`.

## State And Persistence Behavior
The persistent state guarded here is not written directly by this file, but it validates and caches the disk id read from `LocalDisk::get_disk_id`, and updates `GLOBAL_LOCAL_DISK_ID_MAP` for local disk ids. Health state is in-memory atomics and exported through metrics. Capacity probe state is also in-memory and records total/used/free plus timestamp. `reset_health_for_store_init_retry` exists because store initialization reuses disk handles across format-load retries; without clearing transient faulty marks, later retries would fail before issuing disk I/O.

The active health check writes temporary test objects and deletes them, so it has real filesystem side effects under the system bucket. The wrapper's `close` cancels monitoring before closing the underlying disk, but spawned monitors use shared cancellation and may otherwise continue until cancellation or recovery.

## Dependencies And Integration Points
The wrapper depends on `crate::disk::local::LocalDisk` for actual storage, `DiskAPI` for the trait boundary, `health_state.rs` for runtime-state classification and metrics helpers, `GLOBAL_LOCAL_DISK_ID_MAP` for local id lookup, `rustfs_config`/`rustfs_utils` for env configuration, `metrics` for counters, `tracing` for structured events, `uuid` for disk/test ids, and Tokio for async locking, timing, and task spawning.

This file is re-exported through `disk/mod.rs`, where `new_disk` constructs `Disk::Local(Box<LocalDiskWrapper>)`. `set_disk/lock.rs` uses runtime state and reset hooks during membership and init retry. `store/init.rs` calls disk health reset before retrying format load. `rpc/remote_disk.rs` and `rpc/peer_s3_client.rs` reuse `DiskHealthTracker` and timeout getters for remote health monitoring, keeping local and remote behavior aligned.

## Risks And Edge Cases
- The state machine relies on atomics but not a single synchronized transition lock; concurrent failures and successes may race, especially around consecutive counters and `offline_since`.
- `monitor_disk_writable` increments `waiting` before spawning a recovery monitor and comments that it balances a failed operation; mismatches could skew `total_waiting`.
- Health checks write into `.rustfs.sys/tmp`; delete failures are treated as operation failures unless `check_faulty_only` suppresses non-faulty errors, so system-bucket permission or cleanup issues can affect health signals.
- `Duration::ZERO` disables timeout entirely. That is intentional for streaming or immediate operations, but hung futures still hold waiting counts until they complete.
- Scanner/listing timeout policy is subtle. A default or env change can decide whether slow metadata/listing marks a drive unhealthy.
- The disk-id stale check allows a missing stored disk id during initialization; callers must ensure later formatted disks get validated.

## Test Signals
The in-file tests cover timeout env fallback and precedence, high-latency profile selection, invalid policy fallback, active-check interval/timeout env reads, online/suspect/offline/returning transitions, operation success recovery from suspect state, ignored timeout behavior, walk-dir writer backpressure, `skip_total_timeout`, follow-up operations after walk timeout, default timeout health marking, timeout health policy parsing, and store-init health reset. Integration tests in `set_disk.rs`, `set_disk/lock.rs`, `disk/mod.rs`, and `remote_disk.rs` exercise runtime health membership, reset delegation, and local/remote parity.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/disk_store.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/endpoint.rs -->
# sources/object-store/rustfs/crates/ecstore/src/disk/endpoint.rs

## Purpose
`endpoint.rs` defines RustFS disk endpoints as either local filesystem paths or HTTP(S) URL endpoints. It normalizes path/url input, rejects unsupported endpoint forms, tracks whether URL endpoints resolve to the local server, and exposes host/path helpers used by setup, local disk creation, remote RPC routing, and notification paths.

## Important APIs, Types, And Functions
- `EndpointType` distinguishes `Path` endpoints backed by `file://` URLs from remote-style `Url` endpoints.
- `Endpoint` stores the parsed `Url`, `is_local`, and pool/set/disk indices. The indices start at `-1` and are populated by the endpoint layout code.
- `impl TryFrom<&str> for Endpoint` performs validation and normalization for both local paths and URL endpoints.
- `Endpoint::get_type`, `set_pool_index`, `set_set_index`, and `set_disk_index` provide layout metadata.
- `Endpoint::update_is_local` calls `rustfs_utils::is_local_host` for URL endpoints to decide if the target host/port is local.
- `grid_host` returns scheme plus host and optional port for grid/RPC clients, while `host_port` omits the scheme for uniqueness and host matching.
- `get_file_path` decodes the URL path and, on Windows, strips the leading slash from `file://` drive paths.
- `url_parse_from_file_path` converts local paths to `file://` URLs and rejects socket-address-looking values without a scheme.

## Control Flow
Parsing rejects empty, root slash, and root backslash endpoints up front. If `Url::parse` succeeds with a host, the endpoint must be `http` or `https`, must not have username, fragment, or query, and must have a non-root path. Non-Windows URL paths are absolutized before being written back to the URL. Windows has special handling for `/C:/...` URL paths so actual drive paths are not mistaken for relative current-drive paths.

If `Url::parse` succeeds without a host, or fails with `RelativeUrlWithoutBase`, the value is treated as a local path and passed to `url_parse_from_file_path`. If parsing fails due to invalid port or empty host, user-facing error messages are specialized. `url_parse_from_file_path` first checks whether the pre-slash prefix resembles a socket address; if so, it refuses it as a missing-scheme URL rather than silently creating a local path.

Display is intentionally asymmetric: `file://` endpoints display as decoded local file paths, while URL endpoints display as URL strings. This matches user-facing endpoint config and logging expectations.

## State And Persistence Behavior
This file does not persist data. It constructs normalized endpoint values that later become durable identity context in format layouts and runtime maps. The pool/set/disk indices are mutable fields on the endpoint instance and are used as metric labels and layout identity in other modules.

Path normalization can affect persisted or compared values indirectly: local paths are absolutized, spaces and special characters are percent-encoded internally, and `get_file_path` decodes them when passed to local disk code.

## Dependencies And Integration Points
`Endpoint` is consumed by `endpoints.rs` for server layout parsing, setup-type inference, local-path uniqueness, remote host grouping, and grid host construction. `disk/local.rs` uses `get_file_path` to create local disk roots. `rpc/remote_disk.rs` uses `grid_host`, `host_port`, and `get_file_path` for remote disk behavior. `sets.rs`, `store/peer.rs`, `notification_sys.rs`, and tests throughout ecstore compare endpoint hosts and local paths. Metrics in `health_state.rs` and `disk_store.rs` use endpoint display plus indices as labels.

The module depends on `path_absolutize` for normalization, `url` for parsing and `file://` conversion, `urlencoding` for decoded file-path presentation, and `rustfs_utils::{is_local_host,is_socket_addr}` for host classification.

## Risks And Edge Cases
- Absolutizing URL paths means configured remote paths may be normalized according to the local platform, which is intentional but can surprise when comparing configs across OSes.
- The `http://server:/path` case parses as a URL without a numeric port and is accepted by tests. Callers relying on explicit port validation must handle that elsewhere.
- `get_file_path` for URL endpoints returns only the URL path; it is useful for remote disk path fields but should not be confused with a local filesystem path unless `is_local` and endpoint type are considered.
- The socket-address heuristic in `url_parse_from_file_path` only checks the prefix before `/`; unusual path names that resemble `host:port` can be rejected.
- Windows path parsing has separate fallback code and synthetic leading slash handling; regressions here can break local endpoints on Windows even if Unix tests pass.

## Test Signals
Tests cover path and URL endpoint creation, empty/root rejection, unsupported schemes, URL query rejection, empty host and invalid port errors, root URL path rejection, missing scheme for socket addresses, display formatting, type detection, pool/set/disk index setters, `grid_host`, `host_port`, decoded `get_file_path`, Windows drive URL behavior, clone/equality/hash behavior, paths with spaces and special characters, percent-encoding round trips, `update_is_local`, and file-path URL conversion.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/endpoint.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/error.rs -->
# sources/object-store/rustfs/crates/ecstore/src/disk/error.rs

## Purpose
`error.rs` defines the disk-layer error taxonomy, result aliases, conversions to and from external error carriers, stable numeric codes for internode protobuf transport, equality/hash behavior, and a small bitrot/context wrapper surface. It is the central error contract for local disks, remote disks, erasure quorum reduction, metadata parsing, and store initialization.

## Important APIs, Types, And Functions
- `pub type Error = DiskError` and `pub type Result<T> = core::result::Result<T, Error>` establish the module-wide result shape.
- `DiskError` enumerates storage conditions such as format corruption, disk/volume/object absence, access denied, faulty disks, disk full, short writes, bitrot invalidity, quorum failures, source stalls, timeout, and invalid path.
- `DiskError::other` wraps arbitrary errors in `DiskError::Io(std::io::Error::other(...))`.
- `is_all_not_found`, `is_err_object_not_found`, and `is_err_version_not_found` classify common object-not-found cases.
- `is_retryable_internode_write_failure` and `internode_http_error_kind` downcast nested `InternodeHttpError` from an `Io` variant for retry/quorum metrics.
- `to_u32` and `from_u32` map variants to stable numeric codes for `rustfs_protos::proto_gen::node_service::Error`.
- `BitrotErrorType` and `FileAccessDeniedWithContext` provide additional wrapped error contexts.

## Control Flow
Conversions preserve disk errors when possible. `From<std::io::Error>` first attempts to downcast an `io::Error` containing a `DiskError`; if successful, it recovers the original variant, otherwise stores the original I/O error in `DiskError::Io`. The reverse conversion unwraps `DiskError::Io` or wraps non-I/O variants as `io::Error::other`, enabling a later downcast back to `DiskError`.

File metadata errors are mapped to disk-level object errors for not-found, version-not-found, corrupt, and method-not-allowed cases; other metadata errors become `Io`. Tonic statuses are converted into generic `Io` errors with the status message. Node-service protobuf errors use the numeric code; `Io` codes and unknown codes preserve `error_info` as a generic error.

Clone and equality are custom because `std::io::Error` is not cloneable or structurally comparable by default. Cloning an `Io` recreates an error with the same kind and message. Equality compares `Io` kind plus message, while non-I/O variants compare by numeric code. Hashing only hashes the numeric code, which means distinct `Io` messages hash the same even though equality can differ.

## State And Persistence Behavior
The enum itself is not persistent, but its `to_u32`/`from_u32` mapping is a wire-compatibility contract. Changing numeric assignments would break remote disk and node-service error interpretation. Error strings also propagate to logs, user messages, and protobuf `error_info`.

Because non-I/O `DiskError` values are embedded inside `io::Error::other`, the system can move disk errors through APIs that only accept `std::io::Error` and recover them later. That behavior is relied on by `error_conv.rs`, local filesystem wrappers, and tests.

## Dependencies And Integration Points
`rustfs_filemeta::Error` conversions connect metadata decode/read failures to disk errors. `rustfs_rio::{InternodeHttpError, InternodeHttpErrorKind}` integration enables retryable internode write detection and metric labels used by `error_reduce.rs` and erasure encode logic. Protobuf conversions integrate with `rpc/remote_disk.rs` and node service RPCs. `error_conv.rs` returns `std::io::Error` values that often contain `DiskError` instances and are later converted back into this enum.

Most ecstore modules depend on these variants directly: `disk/local.rs` maps filesystem failures, `disk_store.rs` emits `FaultyDisk` and `Timeout`, `store_init.rs` handles `UnformattedDisk`, `set_disk` read/write code reduces `ErasureReadQuorum` and `ErasureWriteQuorum`, and remote code distinguishes `FaultyRemoteDisk`.

## Risks And Edge Cases
- The `Hash` implementation for `Io` ignores the I/O error message while equality includes it. This is allowed only if equal values hash the same, but it can create many hash collisions for distinct I/O errors.
- `DiskError::from_u32(0x24)` creates an empty `Io` error; protobuf conversion treats incoming `Io` specially to preserve `error_info`, but direct `from_u32` callers receive little context.
- `is_all_not_found` returns false on any `None`, so callers must pass only concrete per-disk errors when checking complete not-found failure.
- `tonic::Status` conversion loses status code and structured metadata, keeping only the message.
- Adding a variant requires updating `Clone`, `to_u32`, `from_u32`, tests, and possibly conversion/reduction logic.

## Test Signals
Tests validate variant display and numeric round trips, `other`, I/O conversion and downcast recovery, not-found classifiers, equality/clone/hash behavior, JSON conversion, bitrot wrapping, access-denied context display, debug formatting, error source expectations, nested disk-error through `io::Error`, preservation of original I/O kind/message, and display preservation when converting to `io::Error`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/error_conv.rs -->
# sources/object-store/rustfs/crates/ecstore/src/disk/error_conv.rs

## Purpose
`error_conv.rs` translates generic `std::io::Error` values from filesystem operations into disk-layer semantic errors. It provides context-specific mappings for file, volume, whole-disk, access-check, and unformatted-disk paths while still returning `std::io::Error` so callers can use existing `map_err` flows and later recover `DiskError` via downcast.

## Important APIs, Types, And Functions
- `to_file_error` maps file-level errors to object/file semantics: `NotFound` to `FileNotFound`, permission and path-shape problems to `FileAccessDenied` or `IsNotRegular`, `UnexpectedEof` to `FaultyDisk`, invalid data to `FileCorrupt`, and storage-full to `DiskFull`.
- `to_volume_error` maps volume/bucket operations, converting not-found to `VolumeNotFound`, permission to `DiskAccessDenied`, directory-not-empty to `VolumeNotEmpty`, and embedded file errors to volume equivalents.
- `to_disk_error` maps disk-root access, converting not-found or embedded file/volume not-found to `DiskNotFound`, and access failures to `DiskAccessDenied`.
- `to_access_error` maps filesystem access checks to a caller-supplied permission error while preserving volume-not-found and faulty-disk signals.
- `to_unformatted_disk_error` is used while probing `format.json`; most absence, EOF, invalid data, or unknown errors become `UnformattedDisk`, but access denied remains `DiskAccessDenied`.

## Control Flow
Each function first matches the outer `io::ErrorKind`. For `Other`, it attempts to downcast the `io::Error` into `DiskError`. If downcast succeeds, selected variants are remapped according to the context; otherwise the embedded disk error passes through or falls back to the next broader converter. If downcast fails, conversion usually delegates downward (`disk` to `volume` to `file`) or, for unformatted probing, collapses to `UnformattedDisk`.

This layered flow allows local disk code to call `map_err(to_file_error)` or `map_err(to_volume_error)` close to the filesystem operation, while preserving higher-level operation semantics. For example, a raw `NotFound` during `stat_volume` should report `VolumeNotFound`, not `FileNotFound`.

## State And Persistence Behavior
This file is stateless and has no persistence. Its behavior affects durable control flow indirectly: during startup, `to_unformatted_disk_error` determines whether a disk is treated as unformatted and eligible for format creation or migration; during deletes and writes, `DiskFull`, access-denied, or volume-not-empty mappings influence quorum decisions and healing.

## Dependencies And Integration Points
The module depends only on `DiskError`. It is heavily used by `disk/local.rs` around format loading, metadata reads/writes, file opens, renames, deletes, volume creation/listing/stat, path access, and data part handling. `disk/os.rs` also uses `to_file_error` for OS disk checks. The converted errors then flow into `error_reduce.rs`, `disk_store.rs`, store initialization, and remote error transport.

## Risks And Edge Cases
- The converters return `std::io::Error`, not `DiskError`, so callers must consistently use `.into()` or `DiskError::from` later. A missed conversion can leave a generic I/O error at higher layers.
- Some mappings are intentionally broad, such as `InvalidInput` to `FileNotFound` and `UnexpectedEof` to `FaultyDisk`; this may hide malformed-path versus missing-file distinctions.
- `to_unformatted_disk_error` collapses most errors to `UnformattedDisk`, which is useful for init but risky if used outside format probing.
- Platform-specific `ErrorKind` variants such as `TooManyLinks` and `StorageFull` are guarded in tests but may behave differently across OSes.

## Test Signals
Tests cover all basic mappings for file, volume, disk, access, and unformatted contexts; embedded `DiskError` remapping through `ErrorKind::Other`; fallback delegation; passthrough of unknown interrupted errors where appropriate; no-recursion behavior for unformatted conversion; conversion chains such as file-not-found to volume-not-found; and Unix-specific error kinds for too many links and storage full.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/error_conv.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/error_reduce.rs -->
# sources/object-store/rustfs/crates/ecstore/src/disk/error_reduce.rs

## Purpose
`error_reduce.rs` reduces per-disk operation results into quorum-level success or failure. It encodes which disk errors should be ignored for object, bucket, and base operations, picks dominant non-ignored errors, returns read/write quorum errors when not enough matching success/error votes exist, and builds write-quorum failure summaries for logging and metrics.

## Important APIs, Types, And Functions
- `WriteQuorumFailureSummary` captures required quorum, achieved successes, failed count, total disks, offline disk count, ignored failures, retryable internode failures, dominant error, and a stable label for the dominant error.
- `OBJECT_OP_IGNORED_ERRS`, `BUCKET_OP_IGNORED_ERRS`, and `BASE_IGNORED_ERRS` define context-specific errors excluded from dominant-error voting.
- `reduce_write_quorum_errs` and `reduce_read_quorum_errs` call `reduce_quorum_errs` with `ErasureWriteQuorum` or `ErasureReadQuorum`.
- `reduce_quorum_errs` returns the dominant error if it reaches quorum; otherwise it returns the supplied quorum error.
- `reduce_errs` counts `None` as successful nil results, ignores configured errors, counts cloned `DiskError` values, and prefers nil on ties.
- `build_write_quorum_failure_summary` computes richer diagnostics around a failed or marginal write.
- `is_ignored_err`, `count_errs`, `count_retryable_failures`, and `is_all_buckets_not_found` are small helpers used by set, bucket, and healing code.

## Control Flow
The reduction model treats the input slice as one result per disk. `None` means success. `Some(error)` means that disk failed with a specific error. `reduce_errs` first counts successes, then builds a frequency map of non-ignored errors. It picks the most frequent non-ignored error, then compares it with the success count. If success count is greater, or tied and nonzero, the reduced result is success (`None`). Otherwise the dominant error wins.

`reduce_quorum_errs` then compares the winning count with the required quorum. If the winning count reaches quorum, it returns the winning error, which can be `None` for quorum success. If not, the operation fails with a generic read/write quorum error. This means ignored errors can reduce the available vote pool without becoming the dominant returned error.

`build_write_quorum_failure_summary` recomputes success/failure counts and uses `dominant_error_label` to produce labels such as `nil_dominated`, `disk_not_found`, `short_write`, an internode HTTP metric label, or `other_error`.

## State And Persistence Behavior
This file is stateless. Its decisions directly affect persisted object/write behavior because quorum reduction decides whether multi-disk writes, deletes, reads, metadata updates, bucket operations, multipart operations, and erasure encoding are accepted or rolled back/reported as failed.

## Dependencies And Integration Points
The module depends on `DiskError` and its internode HTTP helpers. `set_disk.rs`, `set_disk/read.rs`, `set_disk/write.rs`, `set_disk/metadata.rs`, and `set_disk/multipart.rs` call read/write reducers for object operations. `erasure_coding/encode.rs` uses `build_write_quorum_failure_summary` to log write-quorum diagnostics and retryable internode failures. `rpc/peer_s3_client.rs` uses bucket ignored errors and `is_all_buckets_not_found` for bucket healing, make/list/delete flows. `store_init.rs` uses count/reduce helpers while initializing disks.

## Risks And Edge Cases
- The parameter is named `quorun` in several functions; it is harmless but can obscure intent.
- `HashMap::into_iter().max_by` does not define deterministic tie-breaking among different non-nil errors with equal counts. Nil ties are deterministic, but non-nil ties may produce whichever the map iteration yields.
- Ignored errors are excluded from dominant voting but still counted as failed in summaries, so callers must choose ignored sets carefully.
- `DiskError::Hash` collapses all I/O errors to one numeric code, while equality distinguishes kind/message. Frequency counting for many distinct I/O errors may have high collision cost.
- `is_all_buckets_not_found` returns false if any disk succeeded (`None`), so it only means every reported result is a not-found style error.

## Test Signals
Tests cover basic dominant-error reduction, ignored errors, quorum success versus generic quorum failure, counting errors, ignored-error matching, write-quorum summary fields, preservation of internode retry labels such as `connection_reset`, and nil tie-breaking.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/error_reduce.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/format.rs -->
# sources/object-store/rustfs/crates/ecstore/src/disk/format.rs

## Purpose
`format.rs` models the `format.json` metadata stored on RustFS erasure disks. It defines versioned metadata enums, backend kind, erasure set layout, deployment id, disk id membership, JSON parsing/serialization, and validation helpers used during store initialization and disk membership checks.

## Important APIs, Types, And Functions
- `FormatMetaVersion` currently supports `"1"` plus `Unknown`.
- `FormatBackend` supports `"xl"` erasure and `"xl-single"` single-disk erasure, plus `Unknown`.
- `FormatErasureV3` stores erasure format version, this disk's UUID, the two-dimensional set/disk UUID layout, and distribution algorithm.
- `FormatErasureVersion` recognizes `"1"`, `"2"`, and `"3"`.
- `DistributionAlgoVersion` recognizes `"CRCMOD"`, `"SIPMOD"`, and `"SIPMOD+PARITY"`.
- `FormatV3` is the top-level format document with metadata version, backend, deployment id, erasure section, and skipped runtime `disk_info`.
- `TryFrom<&[u8]>` and `TryFrom<&str>` parse JSON into `FormatV3`.
- `FormatV3::new` creates a new deployment format with generated UUIDs and V3 distribution.
- `drives`, `to_json`, `find_disk_index_by_disk_id`, and `check_other` provide layout utility and validation.

## Control Flow
`FormatV3::new` chooses `xl-single` when `set_len == 1`, otherwise `xl`. It generates a deployment id, nil `this` id, and `num_sets * set_len` random disk UUIDs. The caller later assigns each disk's `erasure.this` before saving.

Parsing is direct Serde JSON parsing. Unknown tagged enum values deserialize to `Unknown` rather than failing, but required fields and UUID formats still must parse. `find_disk_index_by_disk_id` rejects nil as `DiskNotFound`, rejects max UUID as an offline placeholder, then scans the `sets` matrix for a matching disk id and returns `(set_idx, disk_idx)`.

`check_other` validates that another disk's format has the same set count, same set sizes, and identical UUIDs in every position. It temporarily ignores `other.erasure.this` while comparing layout, then confirms that `this` exists somewhere in the layout. This makes it a membership check against a reference format, not just schema validation.

## State And Persistence Behavior
This file describes persistent disk state. `FormatV3` is serialized into `format.json` under the RustFS metadata bucket. Its fields identify deployment membership, erasure set geometry, disk position, and object distribution algorithm. `disk_info` is skipped during serialization and is runtime-only.

Changing enum serialization names, field names, or layout semantics would affect compatibility with existing disks and MinIO/RustFS migration paths. The code already parses older erasure versions and distribution algorithms in tests, while new format creation emits V3 and `SIPMOD+PARITY`.

## Dependencies And Integration Points
`disk/local.rs` reads `format.json`, parses `FormatV3`, calls `find_disk_index_by_disk_id`, and maps malformed/missing format through `error_conv.rs`. `store_init.rs` creates new formats, migrates existing formats, finds quorum format, validates erasure values, loads all formats, and saves format files. `set_disk.rs`, `sets.rs`, and `set_disk/lock.rs` store and compare `FormatV3` to connect endpoints and identify disk positions. `config/com.rs` and tests use `FormatV3::new` to build fake layouts.

The module depends on `serde`, `serde_json`, `uuid`, `DiskInfo`, and `DiskError`.

## Risks And Edge Cases
- Unknown enum variants deserialize without immediate failure. That helps forward compatibility, but callers must validate if unknown versions/backends are unacceptable.
- `check_other` error messages include a Go-style `(%w)` fragment in a formatted string without wrapping semantics.
- `find_disk_index_by_disk_id` treats nil and max UUID specially; misuse of those sentinels could misclassify an actual layout issue as disk not found or offline.
- `FormatV3::new` creates random UUIDs for every layout position, so tests or callers needing stable layouts must override generated IDs explicitly.
- Any change to serialized field names such as `distributionAlgo` or `xl` is persistent-format sensitive.

## Test Signals
Tests cover creation of single and multi-disk formats, drive counts, JSON serialization content, parsing from string and bytes for older and current erasure versions, invalid JSON, disk-index lookup success and nil/max/not-found failures, reference-format comparison for identical and mismatched layouts, enum serialization/deserialization including `Unknown`, distribution algorithm serialization, and round-trip serialization.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/format.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/fs.rs -->
# sources/object-store/rustfs/crates/ecstore/src/disk/fs.rs

## Purpose
`fs.rs` is a small filesystem shim for the disk layer. It provides cached Tokio `OpenOptions`, Unix-like open mode constants, async and sync wrappers for metadata/access/remove/rename/read operations, cross-platform `same_file` comparison, and directory-aware remove helpers that compensate for platform-specific remove-file behavior.

## Important APIs, Types, And Functions
- `get_readonly_options`, `get_writeonly_options`, and `get_readwrite_options` lazily initialize shared base `tokio::fs::OpenOptions`.
- `same_file` compares metadata differently on Unix and Windows.
- `FileMode` constants `O_RDONLY`, `O_WRONLY`, `O_RDWR`, `O_CREATE`, `O_TRUNC`, and `O_APPEND` mimic common POSIX flags used by local disk code.
- `open_file` maps the mode flags to Tokio open options and clones base options when create/append/truncate modifiers are needed.
- `access`, `access_std`, `lstat`, `lstat_std`, `make_dir_all`, `mkdir`, `rename`, `rename_std`, and `read_file` wrap common filesystem calls.
- `remove`, `remove_all`, `remove_std`, and `remove_all_std` delete files or directories with file-first behavior and directory fallback.

## Control Flow
`open_file` chooses a base options object by masking access mode bits. If create, append, or truncate bits are set, it clones the base options and mutates the clone before opening; otherwise it reuses the cached options directly. Because `O_RDONLY` is zero, the mode mask defaults to read-only unless write bits are set.

`remove` and `remove_all` try `remove_file` first. If the error indicates a directory (`EISDIR`, `IsADirectory`, or macOS `EPERM` for remove-file on directory), `remove` falls back to `remove_dir` and `remove_all` falls back to `remove_dir_all`. The sync `remove_std` mirrors that behavior. `remove_all_std` checks metadata first and dispatches to `remove_dir_all` or `remove_file`.

`same_file` is stricter on Unix, comparing device, inode, size, permissions, and mtime. On Windows it compares permissions, file type, and length because Unix inode/device metadata is unavailable.

## State And Persistence Behavior
The file has process-local static `OnceLock` state for reusable open options. Its operations directly mutate filesystem state through create/open/truncate/append, directory creation, rename, and delete calls. It does not perform disk-layer error conversion itself; callers such as `disk/local.rs` map raw I/O errors through `error_conv.rs`.

The `open_file` flags can truncate or append persisted object/part files, so call sites must choose mode bits carefully. Remove helpers can delete either files or directories depending on the target and function.

## Dependencies And Integration Points
`disk/local.rs` imports this module for file opens, metadata checks, removal, renames, and reads. `disk/os.rs` provides complementary OS-specific helpers. Higher layers receive errors after `disk/local.rs` maps these raw I/O errors with `to_file_error`, `to_volume_error`, or `to_unformatted_disk_error`.

The module depends on Tokio filesystem APIs, standard filesystem metadata, `OnceLock`, `Arc`, and `libc` constants for directory-error detection.

## Risks And Edge Cases
- `O_RDONLY` is zero, so invalid or missing access bits silently select read-only behavior.
- `open_file` does not expose create-new/exclusive or sync flags, even though commented constants suggest POSIX parity was considered.
- Reusing cached `OpenOptions` is efficient, but callers must not mutate the cached base options. The functions return private references only, keeping that contained.
- `remove_all_std` calls `metadata` first, so a missing path returns an error before any remove attempt; async `remove_all` directly attempts removal and can return the original remove error.
- Unix `same_file` compares mtime and permissions in addition to inode/device, so the same inode after metadata changes may be considered different.

## Test Signals
Tests cover constants, open read-only/write-only/read-write/append/truncate modes, async and sync access, metadata calls, recursive directory creation, file and directory removal, recursive removal, sync removal, mkdir, async and sync rename, file read, missing-file read failure, and same/different file metadata comparisons.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/fs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/health_state.rs -->
# sources/object-store/rustfs/crates/ecstore/src/disk/health_state.rs

## Purpose
`health_state.rs` defines runtime drive health states, recovery classes, health threshold getters, metric-recording helpers, and membership snapshots for choosing disks based on health. It is the policy vocabulary used by local and remote disk health trackers, scanner/healing membership, and admin/metrics views.

## Important APIs, Types, And Functions
- `RuntimeDriveHealthState` is a `repr(u32)` enum with `Online`, `Suspect`, `Offline`, and `Returning`.
- `as_str`, `from_u32`, `is_snapshot_eligible`, `is_strictly_online`, and `should_probe_for_admin` expose state labels and policy checks.
- `DriveRecoveryClass` classifies recovery durations as `ShortOffline`, `MediumOffline`, or `LongOffline`.
- `get_drive_suspect_failure_threshold`, `get_drive_returning_success_threshold`, `get_drive_returning_probe_interval`, `get_drive_offline_grace_period`, and `get_drive_long_offline_threshold` read env-backed thresholds from `rustfs_config`.
- `classify_drive_recovery` maps offline duration to a recovery class using grace-period and long-offline thresholds.
- `record_drive_runtime_state`, `record_drive_state_transition`, `record_drive_recovery_class`, and `record_drive_offline_duration` emit metrics.
- `DriveMembershipSnapshot` groups `DiskStore` handles by runtime state and exposes scanner and strict-online candidate lists.

## Control Flow
State conversion is tolerant: unknown numeric values map to `Online`. Runtime metrics are recorded as one gauge per possible state, setting the current state to `1.0` and all others to `0.0` for a given endpoint/pool/set/disk label set. Transitions and recovery classes are counters, while offline duration is a gauge.

Recovery classification is threshold-based: durations up to the offline grace period are short, durations greater than or equal to the long-offline threshold are long, and everything between is medium. Membership snapshots iterate optional disks, skip `None`, query each disk's runtime state, and clone the `DiskStore` into the corresponding vector. Scanner/heal candidates include online, suspect, and returning disks. Strict online candidates include only online disks, with a local-only variant for local-disk operations.

## State And Persistence Behavior
This file does not persist data. It records metrics and constructs in-memory snapshots. Its threshold getters read environment variables each call, so tests and runtime changes can influence policy unless higher layers cache values. Runtime state itself is stored in `DiskHealthTracker` in `disk_store.rs` and remote disk equivalents; this module defines interpretation and metric emission.

## Dependencies And Integration Points
`disk_store.rs`, `rpc/remote_disk.rs`, and `rpc/peer_s3_client.rs` use the state enum, thresholds, recovery classification, and metric recorders while marking failures and recoveries. `disk/mod.rs` exposes `runtime_state` through the `Disk` abstraction. `set_disk/lock.rs` uses `DriveMembershipSnapshot` to choose scanner/heal candidates and strict online disks, and to reset offline disks before store-init retries. `set_disk.rs` and tests use state values for info reporting and behavior checks.

The module depends on `DiskAPI`/`DiskStore` for membership filtering, `Endpoint` for metric labels, `metrics` for counters/gauges, `rustfs_config`, and `rustfs_utils`.

## Risks And Edge Cases
- `from_u32` maps unknown values to `Online`, which is fail-open. That is convenient for default atomics but risky if memory corruption or incompatible states appear.
- Environment threshold getters cast `u64` to `u32` for counts. Very large env values can truncate.
- Metric labels include endpoint strings, which may have high cardinality in dynamic environments.
- Snapshot methods clone `DiskStore` handles; they are cheap if handles are Arcs/boxed wrappers, but candidate lists may become stale immediately after construction as health changes.
- `should_probe_for_admin` differs from scanner eligibility: suspect is snapshot eligible but not admin-probe eligible.

## Test Signals
The in-file test verifies snapshot eligibility policy: online, suspect, and returning are eligible, while offline is not. Broader behavior is covered by `disk_store.rs` tests for transitions, recovery thresholds, offline duration, and reset behavior, plus `set_disk/lock.rs` tests for membership candidate selection.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/health_state.rs -->
