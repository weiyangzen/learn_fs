# subset-b-008277 Research

Grouped research for the SFTP protocol implementation files under `sources/object-store/rustfs/crates/protocols/src/sftp/`. Each section preserves its source path and is bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/driver.rs -->
# sources/object-store/rustfs/crates/protocols/src/sftp/driver.rs

## Purpose
`driver.rs` defines `SftpDriver`, the per-session `russh_sftp::server::Handler` that translates SFTPv3 packets into S3-like `StorageBackend` operations. It centralizes session-scoped state: authenticated `SessionContext`, read-only mode, handle table, multipart part sizing, per-handle read-cache configuration, backend deadlines, and the `SessionDiag` activity stamp used by watchdogs. It also owns the `Drop` cleanup path for live multipart uploads, making it the core safety boundary between an SSH channel lifetime and backend object state.

## Important APIs, Types, and Functions
`SftpDriver::new` wires storage, credentials, limits, read-cache accounting, and diagnostics into a fresh empty handle table. Helper APIs include `access_key`, `secret_key`, `enforce_server_readonly`, `with_handle_ref`, `allocate_handle`, `run_backend`, `run_backend_with_err`, and `authorize`. `run_backend` wraps every backend future in `RUSTFS_SFTP_BACKEND_OP_TIMEOUT_SECS` and maps backend errors through `s3_error_to_sftp`; `run_backend_with_err` keeps typed backend errors visible for callers that need to distinguish not-found. `authorize` delegates to `authorize_operation` and preserves the distinction between policy denial (`PermissionDenied`) and IAM unavailability or timeout (`Failure`).

The `Handler` implementation covers SFTPv3 packet dispatch: version negotiation (`init`), path resolution (`realpath`), metadata (`stat`, `lstat`, `fstat`), directory operations (`opendir`, `readdir`), file open/read/write/close, mutation operations (`remove`, `mkdir`, `rmdir`, `rename`), no-op metadata writes (`setstat`, `fsetstat`), and unsupported symlink/readlink/extended requests. Several bodies delegate to sibling modules such as `read.rs`, `write.rs`, `dir.rs`, and `attrs.rs`.

## Control Flow
Handler methods stamp `session_diag` on entry and exit for liveness accounting. `open` rejects append, read-write combined opens, and malformed `EXCL`/`TRUNC` flags before dispatching to `open_read` or `open_write`. `read` delegates to `read_inner` and suppresses error-level logging for normal `Eof`. `write` removes a handle from the map before awaiting write dispatch so a mutable state machine can cross awaits; if the state already owns an upload id, it inserts a tombstone first so cancellation leaves `Drop` enough data to abort. `close` removes the handle, then commits buffered writes with `PutObject`, completes multipart streams, or aborts failed streams as appropriate. `rename` HEADs the source, uses single-shot `CopyObject` for <=5 GiB, falls back to multipart copy for larger objects, and finally deletes the source.

## State and Persistence Behavior
The handle table is the session-local source of truth. Read handles cache object attributes and read cache state. Write handles hold a `WritePhase` state machine and may carry multipart upload ids that represent persistent backend resources. Tombstones are deliberately inserted before awaits in cancellation-sensitive close/write paths. `Drop` drains remaining handles, finds `Streaming` or `Failed` uploads whose cached `abort_authorized` flag permits cleanup, and spawns bounded fire-and-forget `AbortMultipartUpload` tasks under a global permit pool sized from available parallelism. If abort authorization is denied, permits are exhausted, the runtime shuts down, or abort times out, cleanup falls back to bucket lifecycle rules.

## Dependencies and Integration Points
This module depends on `StorageBackend`, IAM authorization, `SessionContext`, `MaskedAccessKey`, SFTP protocol types, `s3s` multipart/copy DTOs, `uuid` handle ids, `tokio` timeouts/semaphores, and tracing. It integrates tightly with `state.rs` for handle phases, `paths.rs` for safe path parsing, `errors.rs` for status mapping, `read_cache.rs` through `new_read_cache`, and watchdog/lifecycle code through `SessionDiag`.

## Risks and Test Signals
Key risks are cancellation during multipart operations, timeout behavior that can orphan upload ids, non-atomic rename semantics, stale cached abort authorization after policy changes, read-only enforcement drift, and handle table exhaustion returning generic `Failure`. Tests cover SFTPv3 version advertisement, activity stamping, fstat behavior, realpath sanitization and traversal collapse, no-backend realpath, read-only setstat/fsetstat rejection, directory-empty error propagation, and authorization status separation. Multipart write details are mostly tested in sibling write modules, so regressions at cross-module boundaries should be checked with end-to-end SFTP transfer tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/driver.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/errors.rs -->
# sources/object-store/rustfs/crates/protocols/src/sftp/errors.rs

## Purpose
`errors.rs` defines the SFTP error wrapper and all common conversions from RustFS/S3/IAM failures into SFTPv3 status codes. The file deliberately keeps wire responses minimal while logging backend detail server-side.

## Important APIs, Types, and Functions
`SftpError(StatusCode)` converts into both `StatusCode` and `russh_sftp::server::StatusReply`. `ok_status(id)` builds successful `Status` replies for mutating SFTP operations. `s3_error_to_sftp(op, err)` maps typed backend errors to `NoSuchFile`, `PermissionDenied`, or generic `Failure` and emits a structured warn log. `auth_err` and `auth_err_unreachable` encode authorization denial and IAM unavailability respectively. `is_not_found_error` supports control flow such as create-exclude and stat fallback checks; `is_no_such_upload_error` lets abort retry paths treat already-gone multipart uploads as benign.

Internally, `BackendErrorKind` and `classify_backend_error` avoid substring parsing. `S3Error` is classified by `S3ErrorCode` variants and known string codes such as `NoSuchKey`, `NoSuchBucket`, `NotFound`, `403`, and `NoSuchUpload`. Under `cfg(test)`, `DummyError` is classified the same way to keep unit tests aligned with production behavior.

## Control Flow
Callers pass backend errors into `s3_error_to_sftp`; the helper classifies, logs the original display string, and returns an `SftpError` with the selected status. Authorization helpers are direct constructors, except `auth_err_unreachable` also logs operation and target context. Predicate helpers share the same classification path, which prevents the driver from accepting or suppressing an error category that would map differently on the wire.

## State and Persistence Behavior
This file holds no mutable state or persistence. Its main state-like behavior is semantic consistency: the same typed classifier is reused for response mapping and for branching decisions in driver code.

## Dependencies and Integration Points
The module depends on constants for S3/HTTP error-code aliases, `russh_sftp` protocol reply types, `s3s::S3Error`, and tracing. It is used throughout read, write, directory, driver, and watchdog cleanup paths whenever backend, IAM, or multipart abort errors must be translated.

## Risks and Test Signals
The principal risk is misclassification. Mapping by display text would be unsafe because arbitrary messages can contain `AccessDenied` or `NoSuchKey`; the tests explicitly pin code-based classification and ensure unknown display strings remain `Failure`. Tests also verify `ok_status`, not-found predicates, permission mapping, and `NoSuchUpload` behavior for both S3 and dummy errors.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/errors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/fallback_watchdog.rs -->
# sources/object-store/rustfs/crates/protocols/src/sftp/fallback_watchdog.rs

## Purpose
`fallback_watchdog.rs` provides the non-Linux liveness backstop for SFTP sessions. Because non-Linux targets do not have the Linux `/proc/net/tcp[6]` CLOSE_WAIT probe used by `wedge_watchdog.rs`, this watchdog relies only on silence at the SFTP handler layer.

## Important APIs, Types, and Functions
The single public-in-module API is `spawn_for_session(session_diag, cancel_token)`. It starts a Tokio task that periodically reads `SessionDiag.last_activity_ms`, computes `silence_secs`, and cancels the shared session token when `fallback_threshold_reached` returns true. Helpers are pure or near-pure: `silence_secs` compares wall-clock milliseconds to the atomic activity stamp, and `fallback_threshold_reached` checks `WEDGE_FALLBACK_KILL_SILENCE_SECS`.

## Control Flow
The task creates an interval using `WEDGE_WATCHDOG_TICK_SECS`, sets missed ticks to delay, and skips the first immediate tick so it never makes a cancellation decision before a full interval has elapsed. Each tick races against `cancel_token.cancelled()`. A clean session end or listener-wide shutdown cancels the token and the task exits. If silence reaches the fallback threshold, the task logs a warn event with session id, peer, silence, and reason `fallback_silence`, then cancels the same token and exits.

## State and Persistence Behavior
The watchdog owns no persistent data. It holds an `Arc<SessionDiag>` and a `CancellationToken` clone. The only state it reads is the relaxed atomic last-activity timestamp updated by authentication, subsystem dispatch, and every SFTP handler. Cancellation drops the session future, which in turn drops the `SftpDriver` and releases handle/read-cache/multipart state.

## Dependencies and Integration Points
It depends on `constants::limits`, `lifecycle::SessionDiag`, `tokio_util::CancellationToken`, and Tokio timers. `server.rs` spawns it only under `cfg(not(target_os = "linux"))` after SSH handshake completion.

## Risks and Test Signals
The tradeoff is coarse detection: without TCP state, a very long backend operation that does not stamp activity could be canceled once the fallback silence threshold is reached. The high threshold is intended to avoid killing healthy idle sessions. Tests pin threshold boundaries, cancellation behavior with paused Tokio time, clean early cancellation releasing the `SessionDiag` `Arc`, and monotonic silence calculations from stale stamps.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/fallback_watchdog.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/lifecycle.rs -->
# sources/object-store/rustfs/crates/protocols/src/sftp/lifecycle.rs

## Purpose
`lifecycle.rs` holds the per-session diagnostic record, the weak registry of live sessions, and the Linux TCP-state probe used by the SFTP wedge watchdog. It is infrastructure for detecting sessions that are silent at the SFTP layer while the kernel socket has entered a close-related state.

## Important APIs, Types, and Functions
`SessionDiag` stores a generated `session_id`, local and peer socket addresses, `accepted_at`, and relaxed atomic `last_activity_ms`. `SessionDiag::new` initializes those fields and `stamp` refreshes the activity timestamp. `SessionRegistry` is a `Mutex<Vec<Weak<SessionDiag>>>`; `new_session_registry` creates it for `SftpServer`.

`TcpState` abstracts Linux procfs state bytes into `Established`, `CloseWait`, or `Other(u8)`. `probe_tcp_state(local, peer)` reads `/proc/net/tcp` and `/proc/net/tcp6`, then calls `lookup_tcp_state` for tuple matching. `render_proc_net_tcp_addr` encodes IPv4 and IPv6 `SocketAddr`s into procfs little-endian hex address formats, including IPv4-mapped IPv6 handling.

## Control Flow
The accept loop creates one `SessionDiag` per TCP connection, pushes a weak reference into the registry, and shares strong references with `SshSessionHandler`, `SftpDriver`, and the watchdog. Handlers call `stamp` at authentication/subsystem boundaries and SFTP operation entry/exit. On Linux, the watchdog calls `probe_tcp_state`, which tries the IPv4 procfs table first, then the IPv6 table. Lookup skips the header, matches exact local and remote columns, parses the state byte in base 16, and returns the normalized `TcpState`.

## State and Persistence Behavior
All lifecycle state is in memory. The registry uses weak references so it does not extend session lifetimes; stale entries can be retained until consumers walk and prune them. `last_activity_ms` uses relaxed atomics because the value is a best-effort liveness timestamp rather than a synchronization primitive.

## Dependencies and Integration Points
The file uses `std::net`, `std::sync`, procfs reads, and formatting helpers. `server.rs` owns the registry and session construction. `wedge_watchdog.rs` consumes `probe_tcp_state`; `fallback_watchdog.rs` consumes only the activity stamp.

## Risks and Test Signals
Risks include procfs format drift, byte-order mistakes, stale weak refs, and false negatives when procfs is unavailable or the socket row has disappeared. Tests cover IPv4, IPv4-mapped IPv6, native IPv6 rendering, unsupported native IPv6 for the IPv4 table, close-wait and established lookup, no-match behavior, and `Other` state parsing.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/lifecycle.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/mod.rs -->
# sources/object-store/rustfs/crates/protocols/src/sftp/mod.rs

## Purpose
`mod.rs` is the SFTP module facade. It documents the protocol architecture, declares submodules, applies platform-specific watchdog selection, and re-exports the public entry points used by the rest of RustFS.

## Important APIs, Types, and Functions
The public exports are `SftpConfig`, `SftpInitError`, `SftpDriver`, `SftpError`, and `SftpServer`. Public submodules are `config` and `server`; implementation modules include `attrs`, `constants`, `dir`, `driver`, `errors`, `lifecycle`, `paths`, `read`, `read_cache`, `state`, and `write`. `fallback_watchdog` is compiled on non-Linux targets, while `wedge_watchdog` is compiled on Linux.

## Control Flow
There is no runtime control flow beyond module loading, but the module declaration controls which implementation is available at compile time. The docs describe how `SftpServer` accepts SSH connections, `server.rs` authenticates and dispatches the SFTP subsystem, and `driver.rs` maps SFTP operations to backend S3 calls.

## State and Persistence Behavior
The module itself owns no state. Its documentation records important stateful subsystems: per-session watchdog diagnostics and process-wide read-cache accounting. It also documents the environment-driven configuration surface for enablement, address, host keys, reloads, idle timeout, part size, read-only mode, banner, handle cap, backend timeout, and read-cache limits.

## Dependencies and Integration Points
The facade ties the SFTP feature into RustFS through `SftpServer` and `SftpConfig`. It also documents platform behavior: Unix host key mode checks, Windows ACL reliance, and unsupported platforms. The compile-time test ensures `Protocol::Sftp`, `SftpConfig`, and `SftpInitError` remain available.

## Risks and Test Signals
Risks are mostly architectural drift: adding modules without updating exports/docs, changing public names, or accidentally compiling both watchdogs. The module-level test is a simple compile-time signal that core public symbols and protocol variant still exist, but it does not validate runtime behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/paths.rs -->
# sources/object-store/rustfs/crates/protocols/src/sftp/paths.rs

## Purpose
`paths.rs` contains pure path manipulation and sanitization helpers used by the SFTP driver. It is the boundary that turns client-supplied SFTP paths into bucket/key pairs while blocking traversal surprises, reserved internal directory markers, and control-byte log injection.

## Important APIs, Types, and Functions
`ensure_absolute` prefixes empty or relative paths with `/`. `last_path_component` extracts a final component after trimming trailing slashes. `relative_filename` derives a single listing entry name from a full key and a prefix. `parse_s3_path` canonicalizes an input path with `rustfs_utils::path::clean`, splits it with `path_to_bucket_object`, rejects embedded NUL/CR/LF and `GLOBAL_DIR_SUFFIX`, and returns `(bucket, Option<key>)`. `sanitise_control_bytes` replaces C0 controls other than tab with `?` for safe longname/log rendering.

## Control Flow
`parse_s3_path` first rejects raw dangerous controls, then normalizes the path to absolute form and cleans dot segments. Defensively, cleaned `.`/`..`/`../...` collapses to root. The cleaned path is split into bucket and object; an empty object becomes `None`. Reserved `__XLDIR__` marker occurrences in the object are rejected with `BadMessage` so clients cannot address backend directory-marker internals.

## State and Persistence Behavior
The module is stateless. Its behavioral persistence is namespace consistency: every driver operation that calls `parse_s3_path` sees the same root, bucket, object, and rejection rules.

## Dependencies and Integration Points
It depends on `rustfs_utils::path`, SFTP `StatusCode`, and `SftpError`. `driver.rs`, `read.rs`, `dir.rs`, and write paths rely on it before authorization or backend access. `sanitise_control_bytes` is used in tracing instrumentation and SFTP name formatting.

## Risks and Test Signals
Risks include accidental exposure of internal directory marker keys, accepting CR/LF into logs or SFTP longnames, and path-cleaning behavior changes upstream. Tests cover root/bucket/key parsing, trailing slash collapse, control rejection, marker rejection, traversal collapse, helper edge cases, unicode preservation in sanitization, and a proptest asserting accepted outputs do not contain control bytes or uncollapsed `..` key segments.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/paths.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/read.rs -->
# sources/object-store/rustfs/crates/protocols/src/sftp/read.rs

## Purpose
`read.rs` implements read-side SFTP behavior for `SftpDriver`: opening objects for read, serving `SSH_FXP_READ`, draining backend range bodies, and populating the per-handle read-ahead cache.

## Important APIs, Types, and Functions
`open_read(id, filename)` parses a path, requires bucket plus object key, authorizes `GetObject`, HEADs the object, builds SFTP attrs including user metadata, creates a `ReadCache`, and allocates a `HandleState::File`. `read_inner(id, handle, offset, len)` is the body of the handler-level `read`. `fetch_object_range` calls `StorageBackend::get_object_range`, then drains the returned stream into a `Vec<u8>` with a timeout around each `body.next()`. `try_populate_read_cache` performs a soft global memory-limit check before replacing the handle cache.

## Control Flow
`read_inner` rejects zero-length reads before range math to avoid inclusive-end underflow. It caps client length to `MAX_READ_LEN`, validates the handle is a file handle, and returns `Eof` without backend access when `offset >= size`. It probes the handle cache without awaiting; a hit returns immediately and may be a short read at a cache-window edge. On miss, it re-authorizes `GetObject`, chooses a fetch length at least as large as the requested length and normally as large as `read_cache_window`, drains backend bytes, returns EOF if empty, slices the requested response from the fetched window, and then offers the full window to the cache.

## State and Persistence Behavior
Read handles persist object size and attrs from open time; subsequent reads do not re-HEAD, so concurrent object replacement is not reflected during the handle lifetime. `ReadCache` state is per handle, while `read_cache_in_use` is process-wide. Cache population is best-effort and soft-capped: concurrent sessions can exceed the limit briefly, but individual populate calls skip storage when projected capacity is above `read_cache_total_mem_limit`. With `READ_CACHE_DISABLED`, no cache memory is retained.

## Dependencies and Integration Points
The module depends on attrs conversion helpers, constants, `SftpDriver`, error mapping, path parsing, `HandleState`, `StorageBackend`, IAM `S3Action::GetObject`, `futures_util::StreamExt`, and SFTP data/handle types. It is called from `driver.rs` `open` and `read`, and uses `read_cache.rs` indirectly through handle state.

## Risks and Test Signals
Risks include stale size metadata, short reads on cache boundary surprising clients, body-stream stalls after a successful range call, soft memory limit overshoot, and repeated authorization cost on every cache miss. Tests cover zero-length rejection, EOF before backend calls, normal reads, silent EOF logging, error-level logging on backend failures, stalled body timeout, sequential cache hits, crossing cache windows, partial edge hits, and fully disabled cache behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/read.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/read_cache.rs -->
# sources/object-store/rustfs/crates/protocols/src/sftp/read_cache.rs

## Purpose
`read_cache.rs` defines the per-handle in-memory read-ahead cache used by SFTP file handles. It reduces backend range calls for clients that read objects sequentially in small SFTP chunks.

## Important APIs, Types, and Functions
`ReadCache` stores a `Vec<u8>`, the `window_offset` for that buffer, and an `Arc<AtomicU64>` shared process-wide memory accumulator. `ReadCache::new` creates an empty cache. `get(offset, len)` returns a slice when the requested offset falls inside the cached window; it truncates at the window end and returns `None` for misses or zero length. `populate(offset, bytes)` replaces the buffer and updates the shared accumulator by subtracting old capacity and adding new capacity. `capacity` reports current buffer capacity. `Drop` subtracts any live capacity from the accumulator.

## Control Flow
The driver checks memory limits before calling `populate`. Once populated, reads are simple range checks against `[window_offset, window_offset + buf.len())`. When a cache hit starts near the end of the window, only the in-window portion is returned; the next SFTP read is expected to request the remainder and trigger a new backend range call.

## State and Persistence Behavior
Cache state lives only for the lifetime of an open file handle. It is dropped on `CLOSE` or session teardown. Accounting uses `Vec::capacity`, not length, so memory reservation rather than logical payload size is tracked. The atomic uses relaxed ordering because the counter is an approximate resource guard rather than a synchronization mechanism.

## Dependencies and Integration Points
The module uses only standard `Arc`, `AtomicU64`, and `Ordering`. `state.rs` embeds `ReadCache` in `HandleState::File`; `driver.rs` creates caches from the shared server accumulator; `read.rs` queries and populates them.

## Risks and Test Signals
Risks include accumulator drift if populate/drop paths are changed, capacity-based accounting being larger than byte length, and partial-hit short reads. Tests cover empty misses, hits at start/middle/end, misses before and after the window, partial edge hits, replacing windows, capacity reporting, drop draining the accumulator, and zero-length gets.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/read_cache.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/server.rs -->
# sources/object-store/rustfs/crates/protocols/src/sftp/server.rs

## Purpose
`server.rs` is the SSH server entry point for the SFTP subsystem. It owns SSH cryptographic preferences, host-key configuration and hot reload, TCP accept/session orchestration, password authentication against IAM, channel gating, and creation of per-session `SftpDriver` instances.

## Important APIs, Types, and Functions
`SftpServer<S>` stores validated `SftpConfig`, a hot-reloadable `SshConfigHolder`, the cloneable `StorageBackend`, a weak `SessionRegistry`, and the process-wide read-cache accumulator. `SftpServer::new`, `config`, and `start` are the public lifecycle APIs. `build_preferred` and `build_ssh_config` construct a password-only SSH config with AEAD ciphers, modern KEX including strict-KEX markers, non-SHA1 host key algorithms, no compression, keepalives, idle timeout, and packet/channel sizing constants. `SshConfigHolder` wraps current config and an order-independent host-key fingerprint; `spawn_host_key_reload_loop` periodically reloads keys when enabled.

Session functions include `handle_accept`, `run_session`, and `drain_sessions`. `SshSessionHandler` implements `russh::server::Handler` for auth, channel bookkeeping, subsystem dispatch, and explicit rejection of non-SFTP SSH features.

## Control Flow
`start` binds the configured address, starts optional host-key reload, and enters a prioritized accept loop. Finished session tasks are synchronously drained with `try_join_next`; `tokio::select!` biases accept before shutdown. Each accepted stream gets a `SessionDiag`, registry weak ref, child cancellation token, cloned storage, and resolved per-session limits. Linux also duplicates the socket for the wedge watchdog. `run_session` wraps SSH handshake/auth setup in `HANDSHAKE_DEADLINE_SECS`, spawns the platform watchdog after handshake, then awaits either the running SSH session or cancellation. Shutdown cancels the parent token and drains sessions up to `SHUTDOWN_DRAIN_TIMEOUT_SECS`.

Authentication rejects `none` and public key methods, checks access key existence and active status through `rustfs_iam`, compares the supplied secret with `subtle::ConstantTimeEq`, and stores a `SessionContext` on success. `subsystem_request` accepts only the configured SFTP subsystem name, requires an authenticated context and known channel, sends channel success, builds `SftpDriver`, and awaits `russh_sftp::server::run`.

## State and Persistence Behavior
Host-key state is held in an `RwLock<Arc<russh::server::Config>>`; reload only swaps configs when the fingerprint changes, so existing sessions keep their current config and new sessions see new keys. Per-session state includes channel map, optional session context, `SessionDiag`, and resolved limits. Read-cache memory is accumulated process-wide across all drivers. Persistent backend state is delegated to the driver; server shutdown eventually drops drivers, triggering multipart cleanup.

## Dependencies and Integration Points
Dependencies include `russh`, `russh_sftp`, `rustfs_iam`, SFTP config/constants, lifecycle/watchdog modules, `StorageBackend`, session types, Tokio listener/broadcast/join sets, `CancellationToken`, and tracing. `mod.rs` re-exports `SftpServer`; embedding code constructs and starts it with host keys and storage.

## Risks and Test Signals
Risks include handshake tasks pinned by slow peers, hot reload accepting invalid empty key sets, default russh auth/channel behavior changing, shutdown delays from wedged sessions, and channel map leaks if close paths drift. The code mitigates these with handshake deadlines, explicit method/channel rejections, watchdog cancellation, and drain timeouts. Tests cover crypto preferences, strict-KEX/ext-info markers, no SHA1 RSA, password-only auth config, zero auth rejection delay, keepalive/idle config, host-key reload replacement/no-op/failure retention, and order-independent key fingerprints.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/state.rs -->
# sources/object-store/rustfs/crates/protocols/src/sftp/state.rs

## Purpose
`state.rs` defines the in-memory state machines used by SFTP driver operations. It deliberately contains type definitions rather than operation logic, keeping read, write, directory, and driver handlers focused on behavior.

## Important APIs, Types, and Functions
`HandleState` is the main enum stored in `SftpDriver.handles`. `File` handles store bucket, key, size, cached attrs, and `ReadCache`. `Dir` handles store a `DirCursor`. `Write` handles store bucket, key, reported attrs, raw open attrs, and `WritePhase`.

`WritePhase` models upload lifecycle: `Buffering { part_buffer }`, `Streaming { upload_id, abort_authorized, part_buffer, uploaded_parts, next_part_number }`, and `Failed { upload_id, abort_authorized }`. `CompletedPart` carries part number and ETag for complete multipart upload. `MultipartUpload` pairs upload id and cached abort authorization. `DirCursor` distinguishes root listing from bucket/prefix listing; `ListingContinuation` tracks `Initial`, `Next(token)`, and `Done`.

## Control Flow
Operation modules drive these states. Read opens create `File`, readdir advances `DirCursor`, and writes begin in `Buffering`, transition to `Streaming` after multipart creation, move parts into `uploaded_parts`, and enter `Failed` on upload-part errors. Close completes or aborts based on the phase. Directory listing uses `Initial` before the first `ListObjectsV2`, `Next` between pages, and `Done` to suppress further backend calls.

## State and Persistence Behavior
All state is per-session and lives in the handle table. The persistent implication is strongest for `Streaming` and `Failed`, whose `upload_id` refers to backend multipart resources. `abort_authorized` is cached at create-multipart time so both `close` and synchronous `Drop` can decide whether abort is allowed without re-entering async IAM.

## Dependencies and Integration Points
The file depends on `ReadCache`, SFTP `FileAttributes`, and `s3s::dto::ETag`. It is used by `driver.rs`, `read.rs`, `write.rs`, `dir.rs`, and tests. Constants tests here pin important S3 multipart limits imported from `constants::limits`.

## Risks and Test Signals
Risks include invalid phase transitions, stale cached abort authorization, forgetting to carry uploaded part order, and directory cursor cancellation safety. The local test pins multipart constants against S3 limits. Broader behavioral validation lives in modules that mutate this state.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/state.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/test_support.rs -->
# sources/object-store/rustfs/crates/protocols/src/sftp/test_support.rs

## Purpose
`test_support.rs` provides shared `#[cfg(test)]` construction helpers for SFTP module tests. It lets tests instantiate `SftpDriver` and handle states around `DummyBackend` without real IAM or S3 services.

## Important APIs, Types, and Functions
`TEST_PART_SIZE` fixes a 5 MiB multipart part size for tests. `file_handle` builds a `HandleState::File` with a fresh independent read-cache accumulator. `write_handle` builds a `HandleState::Write` for a specified `WritePhase`. Driver builders include `build_driver`, `build_readonly_driver`, `build_driver_with_read_cache`, and `build_driver_with_timeout`; all construct `SftpDriver<DummyBackend>` with a test `SessionContext`, loopback `SessionDiag`, and either default or supplied limits. `capture_tracing_at` installs a temporary tracing subscriber that writes to `CapturingWriter` so tests can assert on emitted log levels and messages.

## Control Flow
The helpers are synchronous except `capture_tracing_at`, which registers a subscriber, rebuilds tracing callsite interest caches, awaits a supplied future, and returns both the future output and captured UTF-8 log text. Driver construction consistently uses `test_session(Protocol::Sftp)` and loopback addresses.

## State and Persistence Behavior
No production state is persisted. Test drivers receive fresh handle maps and fresh read-cache counters. `file_handle` deliberately uses an independent accumulator, so tests that need driver-level cache accounting must use the builder and real `open_read`/read paths instead.

## Dependencies and Integration Points
The module depends on SFTP constants, `SftpDriver`, `SessionDiag`, `ReadCache`, state types, `DummyBackend`, test session helpers, `russh_sftp::FileAttributes`, `tracing`, and `tracing_subscriber`. It is imported by per-file tests in attrs, dir, driver, errors, paths, read, and write modules.

## Risks and Test Signals
The main risk is tests diverging from production defaults. Builders intentionally source default handles, timeout, and read-cache limits from constants, reducing drift. The tracing helper addresses callsite cache behavior that can otherwise make parallel log assertions flaky.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/test_support.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/wedge_watchdog.rs -->
# sources/object-store/rustfs/crates/protocols/src/sftp/wedge_watchdog.rs

## Purpose
`wedge_watchdog.rs` is the Linux per-session liveness watchdog. It detects SFTP sessions silent at the handler layer while the kernel reports the TCP connection in `CLOSE_WAIT`, then cancels the session and shuts down a duplicated socket to unblock russh internals.

## Important APIs, Types, and Functions
`dup_socket(stream)` safely duplicates the accepted `TcpStream` file descriptor through `AsFd` and wraps it in `socket2::Socket`. `spawn_for_session(session_diag, socket, cancel_token)` starts the watchdog task. `WedgeReason` records cancellation reasons: confirmed close-wait, confirmed probe failure, or fallback silence. `Decision` and `evaluate(silence_secs, probe, wedge_suspected)` isolate the core state machine. `silence_secs` reads the `SessionDiag` activity stamp.

## Control Flow
The task ticks every `WEDGE_WATCHDOG_TICK_SECS`, skips the immediate first tick, and on each later tick computes silence plus `probe_tcp_state(local, peer)`. If silence is below the fast threshold, it is quiet. If silence is above the fast threshold and the probe is `CloseWait` or unavailable, the first tick marks suspicion and a second consecutive signal cancels. `Established` and other known TCP states clear suspicion. Silence above `WEDGE_FALLBACK_KILL_SILENCE_SECS` cancels regardless of probe result. On task exit, the duplicated socket is shut down with `Shutdown::Both` so blocked reads/writes in the original session can observe EOF or error.

## State and Persistence Behavior
The watchdog keeps only `wedge_suspected` between ticks. It reads session diagnostics but does not own handle state. Cancelling the token causes `run_session` to drop the running SSH/SFTP session, which drops `SftpDriver` and triggers read-cache and multipart cleanup.

## Dependencies and Integration Points
The file depends on liveness constants, `lifecycle::probe_tcp_state` and `TcpState`, `socket2`, Linux fd traits, Tokio timers, and `CancellationToken`. `server.rs` duplicates sockets and spawns this watchdog only under `cfg(target_os = "linux")`.

## Risks and Test Signals
Risks include false positives if probe failures are treated too aggressively, failure to unblock russh without socket shutdown, and noisy cancellation for healthy idle sessions. The two-tick confirmation and TCP-state filtering reduce false positives. Tests cover quiet paths below threshold, established and transient close states, first/second close-wait ticks, probe-failure confirmation, reason selection based on the cancelling tick, fallback silence, and `WedgeReason` string values.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/wedge_watchdog.rs -->
