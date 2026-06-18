# subset-b-008252 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rpc/remote_disk.rs -->
# sources/object-store/rustfs/crates/ecstore/src/rpc/remote_disk.rs

## Purpose

`remote_disk.rs` implements the remote-node `DiskAPI` adapter for RustFS erasure-coded storage. A `RemoteDisk` presents a disk-like interface to the rest of `ecstore`, but every operation is executed against another node through either the node-service gRPC API or the configured internode data transport. Small control and metadata operations are mostly unary gRPC calls; data streams for object reads, object writes, and directory walks are delegated to `InternodeDataTransport`.

The file also owns runtime remote-drive health tracking. It converts timeouts and network-like failures into `DiskHealthTracker` state transitions, evicts cached gRPC channels, records metrics, and starts recovery probes that require the remote disk RPC path to be healthy before a disk is restored to online state.

## Important APIs, Types, and Functions

- `RemoteDisk`: stores the local view of a remote disk: optional disk UUID, base node address, full `Endpoint`, scan counter, health-check enablement, shared `DiskHealthTracker`, cancellation token, and `Arc<dyn InternodeDataTransport>`.
- `RemoteDisk::new`: builds the base node address from the endpoint scheme, host, and optional port, applies the `DiskOption` health flag plus `ENV_RUSTFS_DRIVE_ACTIVE_MONITORING`, initializes health state as online, and stores the transport dependency.
- `DiskAPI for RemoteDisk`: maps the disk trait to remote calls. It covers volume lifecycle, metadata reads and writes, object version operations, data file streaming, directory walking, deletes, part checks, bulk reads, whole-file read/write, disk info, disk location, scan tracking, and close.
- `execute_with_timeout`, `execute_with_timeout_for_op`, and `execute_with_timeout_for_op_and_health_action`: centralized operation wrapper that enforces per-operation timeouts, short-circuits faulty disks, tracks in-flight health counters, records timeout/network metrics, evicts failed connections, and optionally ignores failure-induced health transitions for selected operations.
- `FailureHealthAction`: controls whether timeout-like or network-like failures should mark the disk suspect/offline. `walk_dir` uses `IgnoreFailure` to avoid allowing listing stalls to poison the drive health state.
- `monitor_remote_disk_health` and `monitor_remote_disk_recovery`: background tasks that probe connectivity and recovery. Active health checks use a TCP connectivity probe; recovery requires a successful noop `disk_info` gRPC call and evicts stale cached connections on probe failures.
- `open_write_with_retry`: retries `InternodeDataTransport::open_write` once for retryable internode write failures, records retry/success metrics by backend and error classification, and keeps non-retryable errors single-shot.
- `copy_stream_with_buffer`: copies an async reader to an async writer with a configurable buffer and flushes at EOF. It is used for streamed `walk_dir` output.
- `encode_msgpack` and `decode_msgpack_or_json`: compatibility helpers for request/response payloads where newer binary msgpack fields coexist with older JSON string fields.

## Control Flow

Construction records the remote disk as online, keeps the endpoint path for disk identity, and keeps the node base address for gRPC channel lookup. `disk_ref()` returns the disk UUID once set, otherwise it falls back to the endpoint string. Many RPCs that can address disks by durable UUID call `disk_ref()`, while older or endpoint-shaped APIs still pass `self.endpoint.to_string()`.

Most unary methods follow a common sequence:

1. Log a structured `remote_disk_rpc` start event with endpoint, operation name, and relevant volume/path fields.
2. Serialize request data, often JSON plus msgpack when the protobuf has binary compatibility fields.
3. Call `execute_with_timeout*` with an operation-specific timeout from `disk_store` configuration.
4. Get a signed tonic node-service client through `node_service_time_out_client` and `gen_tonic_signature_interceptor`.
5. Build a protobuf request, call the matching node-service RPC, check `response.success`, convert `response.error` to `DiskError` when needed, and decode the success payload.

Volume methods (`make_volume`, `make_volumes`, `list_volumes`, `stat_volume`, `delete_volume`) use node-service protobufs and JSON `VolumeInfo` decoding. Metadata and version methods (`write_metadata`, `read_metadata`, `update_metadata`, `read_version`, `read_xl`, `rename_data`) serialize `FileInfo`, `RawFileInfo`, `ReadOptions`, and update options, preferring msgpack response fields when present. Delete methods include single-version delete, batch version delete, delete paths, and generic delete; the batch version path returns a `Vec<Option<Error>>` instead of a single `Result` and manually fans out serialization/RPC errors across all requested versions.

Stream-oriented data operations bypass unary gRPC payloads:

- `read_file` delegates to `read_file_stream`.
- `read_file_stream` checks the health state, resolves `disk_ref()`, and calls `data_transport.open_read` with endpoint grid host, disk, volume, path, offset, and length.
- `read_file_zero_copy` cannot truly zero-copy across the network, so it reads a stream into one `Vec` allocation and returns `Bytes`.
- `append_file` and `create_file` check health, resolve disk, then call `open_write_with_retry` with append flag and expected size.
- `walk_dir` serializes `WalkDirOptions` to JSON, sets a stall timeout, optionally disables the total timeout via `skip_total_timeout`, opens a walk stream through `data_transport.open_walk_dir`, and copies stream bytes into the caller-provided writer. It retries only if opening the stream fails with a retryable transport/decoding error; it does not retry after partial bytes have already been written.

Health control flow is layered. `is_online` is a local health-state check, not an active network ping. `enable_health_check` spawns active monitoring only if remote active monitoring is enabled. `monitor_remote_disk_health` starts with a TCP probe, periodically probes again after the recent-success grace window, marks failures through `DiskHealthTracker`, and starts recovery monitoring after a transition. `monitor_remote_disk_recovery` loops until a noop `disk_info` RPC succeeds and `mark_recovery_success` returns the disk to online, or until the cancellation token is cancelled. `close` cancels these monitor tasks.

## State and Persistence Behavior

The file does not persist data locally. It is an RPC facade over remote disk persistence owned by the peer node. Its local state is runtime-only:

- `id: Mutex<Option<Uuid>>` is mutable in-memory disk identity. Setting it changes future `disk_ref()` addressing for UUID-aware RPCs and transports.
- `DiskHealthTracker` stores runtime health state, failure/recovery timestamps, waiting counters, last start/success times, and capacity snapshots.
- `scanning: Arc<AtomicU32>` tracks active scans through `start_scan()` and `ScanGuard`.
- `cancel_token` coordinates shutdown of health/recovery monitor tasks.
- gRPC channels are cached outside this struct by the shared connection map behind `node_service_time_out_client`; this file evicts them with `evict_failed_connection` after timeout/network failures.

Remote persistence is affected by the API calls themselves: metadata writes update xl/file metadata on the remote disk, creates/appends stream object data to the remote disk, rename/delete calls mutate object paths and versions, and `disk_info` reads remote state. Serialization compatibility is important because binary msgpack fields and JSON fallback fields may coexist across mixed versions.

## Dependencies and Integration Points

Key internal dependencies include:

- `crate::disk::*`: the `DiskAPI` trait, disk error/result types, file readers/writers, option structs, volume and disk info types, `DiskHealthTracker`, `RuntimeDriveHealthState`, and timeout/environment helpers.
- `crate::rpc::client`: signed tonic interceptor creation, node-service client creation, and network-like disk error classification.
- `crate::rpc::internode_data_transport`: transport trait plus read/write/walk request shapes used for high-volume streams.
- `rustfs_protos`: node-service protobuf request/client types and cached connection eviction.
- `rustfs_filemeta`: `FileInfo`, `RawFileInfo`, and `ObjectPartInfo` payload models.
- `rustfs_io_metrics` and `metrics`: internode gRPC/TCP metrics, retry counters, timeout counters, byte counters, and failure counters.
- `tokio`, `tonic`, `bytes`, `serde_json`, `rmp-serde`, `tracing`, and `uuid`: async execution, gRPC, payload buffers, serialization, structured logs, and disk IDs.

The adapter integrates with erasure-set code wherever a `DiskAPI` object is expected. It also integrates with the node-service server contract: every protobuf request field and success/error convention here must match the server implementation. The stream methods integrate with the configured internode transport backend, currently tested with a TCP/HTTP capability shape. Runtime health integrates with cluster drive-state reporting through `record_drive_runtime_state` and `DiskHealthTracker`.

## Risks and Edge Cases

- Mixed disk addressing is a compatibility risk. Some methods send `disk_ref()` while others still send `endpoint.to_string()`. Server-side expectations must remain compatible when disk IDs are set.
- `Duration::ZERO` disables total operation timeout in `execute_with_timeout`; methods using it can wait indefinitely unless the underlying client or transport enforces its own deadline.
- `list_volumes`, `read_multiple`, and other collection decoders use `filter_map(...ok())` in places, silently dropping malformed entries rather than returning an error. That can hide partial decode failures.
- `delete_versions` is less uniform than most methods: it creates the client before entering `execute_with_timeout`, manually converts many errors into repeated per-version errors, and converts server error strings with limited structure.
- `walk_dir` intentionally ignores health marking for total/stall failures. This avoids false drive-offline transitions for listing streams, but it means repeated listing transport failures may not influence disk health.
- Retrying `walk_dir` is safe only before bytes are copied. A failure after partial output returns an I/O error and leaves the caller with partial data already written.
- Health probes use TCP for active monitoring and gRPC `disk_info` for recovery. This is stricter on recovery, but initial TCP success alone does not prove disk RPC readiness.
- Background monitor spawning is edge-triggered by health transitions. Repeated transitions could create multiple monitor tasks if tracker semantics change.
- `read_file_zero_copy` reserves `length` capacity. Very large or untrusted lengths can increase memory pressure.
- Serialization compatibility depends on both JSON and msgpack schemas remaining aligned across nodes.

## Test Signals

The in-file tests are broad and focused on adapter reliability:

- Construction/property tests verify endpoint parsing, host names, path extraction, disk location conversion, local/remote flags, disk ID set/get, `disk_ref()` UUID preference, and close cancellation.
- Health tests cover online behavior, missing listeners moving runtime state away from online, first timeout/network errors moving to suspect rather than immediate offline, ignored failure actions preserving online state, business errors not poisoning health, and cached connection eviction on timeout/network-like errors.
- Recovery tests verify that a plain TCP listener is insufficient for recovery; successful recovery requires disk RPC readiness through `disk_info`, and failed probes evict stale channels.
- Transport tests verify that read, create, append, and walk operations use the configured `InternodeDataTransport` with expected endpoint, disk, path, size, body, and stall timeout fields.
- Retry tests cover one retry for retryable open-write errors, no retry for non-retryable write errors, one retry for retryable walk open errors, and no retry after partial walk output.
- Observability tests verify recovery-monitor spans preserve request context and that network-error-triggered recovery monitor logs include both request and recovery span context.

These tests exercise the highest-risk behavior without needing a real remote node by using mock transports, hanging listeners, captured logs, and the global cached connection map.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rpc/remote_disk.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rpc/remote_locker.rs -->
# sources/object-store/rustfs/crates/ecstore/src/rpc/remote_locker.rs

## Purpose

`remote_locker.rs` implements `rustfs_lock::LockClient` for locks hosted by another RustFS node. `RemoteClient` is a thin, signed gRPC adapter around the node-service lock RPCs. It serializes local lock requests to JSON, sends unary protobuf requests to the remote node, converts remote success/error responses back into `LockResponse` and lock-state types, and evicts cached channels when lock RPCs time out or return tonic failures.

The implementation is intentionally not a local lock store. It has no persistent lock table of its own and relies on the remote node service for actual acquisition, release, refresh, force-release, and batch behavior.

## Important APIs, Types, and Functions

- `RemoteClient`: cloneable wrapper containing the remote node base address string.
- `RemoteClient::new` and `RemoteClient::from_url`: constructors from an endpoint string or parsed URL.
- `get_client`: creates or retrieves a signed `NodeServiceClient<InterceptedService<Channel, TonicInterceptor>>` through `node_service_time_out_client` and `gen_tonic_signature_interceptor`.
- `build_ping_request`: creates a flatbuffer-backed `PingRequest` payload used by `is_online`.
- `create_unlock_request`: builds a minimal `LockRequest` from a `LockId` for unlock, refresh, force-unlock, and status-probe paths where the server mainly needs the lock ID/resource.
- `execute_rpc`: wraps acquisition RPCs in a timeout, logs tonic failures/timeouts, evicts cached connections, and maps failures into `LockError`.
- `rpc_timeout`: clamps zero-duration lock timeouts to 1 ms so remote acquisition RPCs cannot accidentally wait forever.
- `rpc_failure_response`, `rpc_timeout_failure_response`, and batch variants: convert transport-layer failures into normal failed `LockResponse` values for acquisition APIs.
- `batch_rpc_timeout`: chooses the maximum acquire timeout from a batch and applies the same zero-timeout clamp.
- `build_lock_info`: uses server-provided `lock_info` JSON when available, otherwise synthesizes a `LockInfo` from the original request.
- `LockClient for RemoteClient`: implements acquire, batch acquire, release, batch release, refresh, force release, status check, stats, close, online check, and local/remote check.

## Control Flow

Single lock acquisition logs the resource, gets a signed client, serializes the `LockRequest` into `GenerallyLockRequest.args`, and calls `client.lock` through `execute_rpc` with `request.acquire_timeout`. Timeout and tonic transport failures are returned as successful Rust `Ok(LockResponse { success: false, ... })` values so the distributed lock layer can treat unreachable remote acquisition as lock acquisition failure rather than a client exception. A successful server response becomes `LockResponse::success` with either decoded or synthesized `LockInfo`; an application-level server rejection becomes `LockResponse::failure`.

Batch acquisition is similar. It returns early for an empty request list, serializes all requests into `BatchGenerallyLockRequest.args`, chooses the maximum request acquire timeout for the RPC, and maps each returned result by index. Missing response entries become per-request failed responses, preserving output length and request ordering.

Release, batch release, refresh, and force release use the minimal unlock request shape and call the corresponding node-service methods directly (`un_lock`, `un_lock_batch`, `refresh`, `force_un_lock`). Unlike acquisition, these paths do not use `execute_rpc`; tonic errors become `Err(LockError::internal(...))`, and server `error_info` is also returned as an error.

`check_status` is an approximation because the node-service API has no direct status query. It tries to acquire an exclusive lock using a minimal request. If that succeeds, it releases it best-effort and returns `None`, meaning the lock was likely free. If acquisition fails, or if communication fails, it returns a generic `LockInfo` with owner `unknown`, exclusive type, acquired status, default metadata, normal priority, and a synthetic expiration time.

`get_stats` returns default stats with `last_updated` set to now because there is no remote stats RPC. `is_online` gets a client and sends a flatbuffer ping request; client creation or ping failure returns false, while any ping success returns true.

## State and Persistence Behavior

`RemoteClient` stores only `addr`. It does not persist locks, cache lock ownership, or maintain local counters. All durable or time-bound lock state lives on the remote lock service. Local behavior that does affect process state includes:

- cached tonic channels managed by the shared connection map behind `node_service_time_out_client`;
- eviction of cached connections through `evict_failed_connection` on acquisition timeout or tonic failure;
- synthesized `LockInfo` timestamps using `SystemTime::now()` when the server does not return lock info or when status is approximated.

The timeout clamp is a state-safety guard: a zero acquire timeout becomes a 1 ms remote RPC timeout instead of an unbounded wait.

## Dependencies and Integration Points

Key dependencies include:

- `rustfs_lock`: `LockClient`, `LockRequest`, `LockResponse`, `LockId`, `LockInfo`, `LockStats`, `LockError`, lock status/type/metadata/priority models, and the result alias.
- `rustfs_protos`: node-service protobufs for single and batch lock requests, ping requests, ping flatbuffer body builder, node-service client, and cached connection eviction.
- `crate::rpc::client`: signed tonic interceptor and shared node-service client factory.
- `tonic`, `tokio::time::timeout`, `bytes`, `flatbuffers`, `serde_json`, `url`, and `tracing`.

This client is used by higher-level distributed locking code through the `LockClient` trait. It must stay wire-compatible with the node-service lock server, including the JSON shape placed in `GenerallyLockRequest.args` and `BatchGenerallyLockRequest.args`. It also participates in shared RPC connection lifecycle through `GLOBAL_CONN_MAP` indirectly, because evicting a failed lock connection removes the cached channel for the node address.

## Risks and Edge Cases

- Acquisition methods turn transport failures into failed lock responses, while release/refresh/force-release methods return `Err`. Callers must understand this asymmetry.
- `release`, `release_locks_batch`, `refresh`, `force_release`, `check_status`, and `is_online` do not use `execute_rpc`, so they do not get the same explicit timeout wrapper or cache eviction behavior on timeout/failure.
- `create_unlock_request` fills owner, type, timeout, TTL, and metadata with defaults because the server is expected to key off `lock_id`. If server behavior starts validating more fields, these minimal requests can break.
- `check_status` is not authoritative and can perturb state briefly by acquiring and releasing a free lock. On communication errors it reports a generic held lock, which is conservative but may hide node reachability failures.
- `build_lock_info` silently falls back to synthesized info if server lock-info JSON is malformed. That keeps acquisition usable but can mask schema drift.
- The special scanner leader lock `.rustfs.sys/leader.lock@latest` downgrades some timeout/failure logs to debug. This reduces noise for expected contention or scanner behavior, but can also hide repeated leader-lock reachability problems unless debug logs are enabled.
- Batch acquisition uses the maximum acquire timeout across requests. One long-timeout request can make the entire batch RPC wait longer than smaller requests would individually.
- The ping health check validates node-service reachability, not remote lock correctness or availability.

## Test Signals

The in-file tests focus on timeout and connection-cache behavior:

- A hanging TCP listener plus a cached lazy tonic channel verifies `acquire_lock` respects the request acquire timeout, returns a failed `LockResponse` with a timeout marker, completes quickly, and evicts the cached connection.
- The same pattern verifies `acquire_locks_batch` respects the derived batch timeout, returns one failed response for one request, and evicts the cached connection.
- A unit test verifies `rpc_timeout(Duration::ZERO)` is clamped to 1 ms and nonzero durations are preserved.

These tests directly cover the highest-risk remote acquisition path. There are no local tests for release, refresh, force-release, status approximation, stats, or ping behavior in this file.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rpc/remote_locker.rs -->
