# Research: subset-b-000236

Grouped research for Nydus storage remote helpers, storage utilities/tests, BATS infrastructure, upgrade persistence, and selected `nydus-utils` modules.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/remote/message.rs -->
# sources/cloud-native/nydus/storage/src/remote/message.rs

Purpose: defines the fixed-size wire protocol types used by the storage remote blob manager over Unix sockets. It contains request codes, message headers, validation traits, and packed request/reply payloads for `Noop`, `GetBlob`, and `FetchRange`.

Important APIs/types/functions: `MAX_MSG_SIZE` caps payload size at 4 KiB and `MAX_ATTACHED_FD_ENTRIES` documents fd-passing capacity. `Req` constrains request enums to numeric, comparable, thread-safe command codes. `RequestCode` maps `Noop = 0`, `GetBlob = 1`, `FetchRange = 2`, and `MaxCommand = 3`; `Req::is_valid` accepts only values below `MaxCommand`. `MsgValidator` provides a syntax-validation hook. `HeaderFlag` defines protocol version, reply, need-reply, all valid bits, and reserved bits. `MsgHeader` is `repr(C, packed)` and `ByteValued` so it can be copied directly to and from socket buffers; accessors manage tag, code, version, reply flags, need-reply flags, and payload size. Payload structs are `GetBlobRequest`, `GetBlobReply`, `FetchRangeRequest`, `FetchRangeReply`, plus `FetchRangeResult`.

Control flow: clients and servers construct `MsgHeader::new`, which forces protocol version 1 while preserving supported reply flags. Receivers call `MsgHeader::is_valid` before dispatch; it rejects invalid command codes, tag zero, payloads larger than `MAX_MSG_SIZE`, non-version-1 headers, and reserved flag bits. Payload validation is per message: `GetBlobRequest` requires a NUL byte somewhere in the fixed 256-byte id field, and `GetBlobReply` requires either a nonzero token or nonzero result. `FetchRangeRequest` and `FetchRangeReply` currently inherit the always-true default validator.

State and persistence: the file has no durable state. Message tags correlate requests and replies, and `GetBlobReply.token` appears to encode generation plus a per-connection token generated elsewhere. All structs are by-value POD-style protocol records.

Dependencies and integration points: uses `vm_memory::ByteValued` for safe byte-slice casting in the remote connection layer. It is consumed by `storage/src/remote/server.rs` and the unlisted client/connection modules. The protocol depends on host endianness and Rust enum layout being stable enough for Nydus peers because the packed structs carry raw numeric fields.

Risks: `GetBlobRequest::new` uses `buf.copy_from_slice(id.as_bytes())` against a 256-byte array, which would panic for any id shorter than 256 bytes despite the debug assertion saying `< 256`; callers may avoid it, but the constructor is unsafe as written. `MsgHeader::get_code` transmutes arbitrary `u32` into `RequestCode`; validation checks afterward reduce risk, but invalid enum values are still created. Packed structs require careful field access to avoid unaligned references; the code generally uses copied field expressions. Empty/default headers are invalid because tag zero is rejected. `FetchRange` payloads lack semantic validation for zero token/count or overflow ranges.

Test signals: unit tests cover request-code validity, invalid transmuted codes, header flag/version/size/tag operations, clone/debug/partial-eq behavior, and `MAX_MSG_SIZE` boundary behavior. Payload validation and constructor behavior are lightly covered or not covered.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/remote/message.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/remote/mod.rs -->
# sources/cloud-native/nydus/storage/src/remote/mod.rs

Purpose: declares the remote blob manager module boundary for storage and re-exports the public client/server entry points.

Important APIs/types/functions: `pub use self::client::RemoteBlobMgr` exposes the remote blob manager client, and `pub use self::server::Server` exposes the server type. Internal submodules are `client`, `connection`, `message`, and `server`.

Control flow: there is no executable control flow in this file. It is a namespace and visibility shim that lets callers import `crate::remote::RemoteBlobMgr` and `crate::remote::Server` while keeping connection/message internals private to the module tree.

State and persistence: none.

Dependencies and integration points: ties together the unlisted `client` and `connection` modules with the researched `message.rs` and `server.rs`. Storage users depend on this file for the public remote API surface.

Risks: because `message` and `connection` are private, protocol extension must happen inside this module. Re-exporting only two types keeps API narrow but can hide lower-level testing hooks from external integration tests.

Test signals: no direct tests. It is indirectly compiled by remote server/client tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/remote/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/remote/server.rs -->
# sources/cloud-native/nydus/storage/src/remote/server.rs

Purpose: implements a Unix-domain-socket remote blob manager server that accepts clients, dispatches remote protocol messages, and tracks active client connections.

Important APIs/types/functions: `ClientConnection` wraps a locked `Endpoint`, shutdown flag, numeric id, shared `ServerState`, per-client token counter, and cloned `UnixStream` used for shutdown. `ClientConnection::handle_message` reads a header and dispatches to `handle_noop`, `handle_get_blob`, or `handle_fetch_range`. `ServerState` stores `active_workers` and a `HashMap<u64, Arc<ClientConnection>>`. `Server` owns the socket path, listener, next connection id, shutdown flag, and shared state. Public server APIs are `new`, `start`, `stop`, `close_connection`, `handle_event`, `handle_incoming_connection`, and `AsRawFd`.

Control flow: `Server::new` creates a `Listener` bound to the socket. `Server::start` makes the listener blocking and spawns an accept thread. Each accepted socket gets a monotonic id starting at 1024, is inserted into `ServerState.clients`, and is handled by another thread that loops on `client.handle_message()` until error. The synchronous `handle_incoming_connection` and `handle_event` path provides an event-loop style alternative: accept one connection and then service a known client id. `stop` sets the exit flag, wakes a blocking accept by connecting a `RemoteBlobMgr`, shuts down all clients, and clears the client map.

State and persistence: all state is in-memory and process-local. Connection ids are u64 internally but constrained to u32 for external `id()` and event handling. `active_workers` counts accept and client threads. The per-client token counter starts at 1 and contributes to `GetBlobReply.token` combined with request generation. No blob handles or fetched data are persisted here.

Dependencies and integration points: depends on `crate::remote::connection::{Endpoint, Listener}` for socket IO and fd transport, `crate::remote::client::RemoteBlobMgr` to wake accept during shutdown, and protocol records from `message.rs`. Uses `vm_memory::ByteValued` for payload byte loading. Logging macros and project IO-error macros (`eio!`, `einval!`, `enoent!`, `eother!`) are assumed from crate scope.

Risks: `handle_get_blob` and `handle_fetch_range` contain TODO behavior: `GetBlob` always replies with `ENOSYS` and a generated token/base 0, while `FetchRange` echoes count with success result and token 0. This means the server skeleton is not a real blob manager yet. The accept loop breaks if one client cannot be initialized. `stop` unwraps `RemoteBlobMgr::new`, so invalid wakeup setup could panic. Worker count uses `Ordering::Acquire` for increment in one place, which is unusual for atomic increments. The client handler loops forever unless `handle_message` returns an error; clean client disconnect is treated as warning/error path. Id exhaustion rejects new connections after `u32::MAX`.

Test signals: ignored tests exercise server start/stop, worker counts, client connect/start/ping, shutdown cleanup, and reconnect after server restart. They are integration-like and ignored, so normal CI may only compile this path without exercising runtime behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/remote/server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/test.rs -->
# sources/cloud-native/nydus/storage/src/test.rs

Purpose: supplies mock storage backend and chunk metadata types for storage unit tests.

Important APIs/types/functions: `MockBackend` holds shared `BackendMetrics` and implements both `BlobReader` and `BlobBackend`. `BlobReader::try_read` fills the destination buffer with deterministic byte values equal to the byte index modulo 256. `BlobBackend::get_reader` returns a new `Arc<MockBackend>` sharing metrics. `MockChunkInfo` is a cloneable/default chunk metadata holder. It implements `BlobChunkInfo` and `BlobV5ChunkInfo`, using `impl_getter!` to expose offsets, sizes, index, flags, and blob index.

Control flow: tests can instantiate `MockBackend` and receive successful reads without external storage. Chunk tests can set fields on `MockChunkInfo` and pass it through trait-object APIs; methods compute booleans from `BlobChunkFlags` and return zero CRC when the `HAS_CRC32` flag is absent.

State and persistence: no persistence. `MockBackend.metrics` is shared through `Arc`; read contents are generated on demand. `MockChunkInfo` is plain in-memory metadata.

Dependencies and integration points: integrates with `crate::backend::{BlobBackend, BlobReader}`, `crate::device::{BlobChunkInfo, BlobChunkFlags}`, v5 chunk metadata via `BlobV5ChunkInfo`, `nydus_utils::digest::RafsDigest`, and `nydus_utils::metrics::BackendMetrics`. It is intended for crate-internal tests because all types are `pub(crate)`.

Risks: `try_read` ignores offset and `blob_size` returns 0 even though reads can return data, so tests using it do not validate real object sizing or offset semantics. `is_encrypted` always returns false. CRC and batch/compression behavior are flag-only, so data integrity behavior must be tested elsewhere.

Test signals: this is test support rather than a test module. It strengthens other tests by avoiding network/backend dependencies but can mask offset, size, and encryption bugs if used too broadly.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/utils.rs -->
# sources/cloud-native/nydus/storage/src/utils.rs

Purpose: provides low-level storage helpers for vectored IO, memory-slice copying, platform-specific file copy, fd path lookup, memory cursoring over FUSE buffers, readahead, aligned uninitialized allocation, and hash/CRC verification.

Important APIs/types/functions: `readv` wraps `nix::sys::uio::preadv` and retries interrupted reads. `copyv` copies from a slice of byte buffers into `FileVolatileSlice` destinations and returns bytes copied plus final destination cursor. `copy_file_range` uses Linux `copy_file_range` or a portable pread/pwrite loop. `get_path_from_file` resolves fd paths through `/proc/self/fd` on Linux or `F_GETPATH` on macOS. `MemSliceCursor` tracks `index` and `offset` across `FileVolatileSlice` arrays, with `move_cursor`, `consume`, and `inner_slice`. `readahead` issues Linux `libc::readahead` or macOS `F_RDADVISE` in 128 KiB windows after 4 KiB alignment. `alloc_buf` returns page-aligned, unzeroed storage. `check_hash` and `check_crc` verify against `RafsDigest` and iSCSI CRC32.

Control flow: callers typically validate read/copy ranges, then call `copyv` or cursor `consume` to write into FUSE memory slices. `copyv` iterates source buffers and nested destination slices, advancing destination indices as slices fill and returning `StorageError::MemOverflow` when destination capacity is exhausted. `MemSliceCursor::consume` produces mutable IO slices directly over volatile memory using raw pointer arithmetic, advancing its cursor as slices are consumed. File copying loops until the requested byte count is copied and treats zero-byte progress as IO error.

State and persistence: `MemSliceCursor` maintains transient cursor state over caller-owned memory. `copy_file_range` persists bytes into destination files. Readahead changes kernel page-cache state but no durable data. `alloc_buf` deliberately leaves memory uninitialized, so callers must write before reading.

Dependencies and integration points: depends on `fuse_backend_rs::file_buf::FileVolatileSlice`, `vm_memory::bytes::Bytes`, `nix`, `libc`, and `nydus_utils::{crc32,digest,round_down_4k}`. Used by storage backends and blob/device read paths that need efficient vectored memory movement.

Risks: `copyv` validates `offset` only against the first source buffer, then resets `src_offset` for later buffers; this matches its documented "first buffer offset" behavior but is easy to misuse. It may partially write before returning `MemOverflow`, as covered by tests. `MemSliceCursor::consume` creates `IoSliceMut` from raw pointers and relies on valid `FileVolatileSlice` lifetimes and bounds. `alloc_buf` is uninitialized and page-aligned via unsafe allocation. Linux `copy_file_range` can have filesystem-specific semantics, and the fallback does not handle partial writes beyond treating zero as error.

Test signals: tests cover copy edge cases, partial overflow behavior, cursor movement and consume semantics, page-aligned allocation, hash/CRC checks, file copy success and EOF errors, and fd path lookup including invalid fd. Platform-specific tests are guarded where appropriate.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/tests/qps_pauser_integration.rs -->
# sources/cloud-native/nydus/storage/tests/qps_pauser_integration.rs

Purpose: integration tests for storage backend QPS limiting and pausing behavior under concurrent and time-dependent scenarios.

Important APIs/types/functions: imports `nydus_storage::backend::qps::QpsLimiter` and `nydus_storage::backend::pauser::Pauser`. QPS tests cover `new`, `acquire`, `try_acquire`, and `acquire_tokens`. Pauser tests cover `new`, `set_pause`, `wait`, and `clear_pause`.

Control flow: QPS tests spawn worker threads or loops that acquire tokens under sustained load, consume the initial burst bucket, mix single-token and multi-token requests, and verify the boolean "was limited" indication. Pauser tests set a pause before spawning request threads, assert they remain blocked briefly, then wait for expiration; another test clears a long pause and asserts prompt unblocking.

State and persistence: no persistence. Shared state is in `Arc<QpsLimiter>`, `Arc<AtomicUsize>`, and `Arc<AtomicBool>`. Timing and token bucket state are in-memory.

Dependencies and integration points: validates the behavior expected by backend request paths and retry/fallback logic that need to throttle source/backend access. Uses std threading, atomics, `Duration`, and `Instant`.

Risks: time-based assertions are inherently sensitive to loaded CI machines. The sustained throughput test uses generous bounds but still assumes scheduler behavior over two seconds. `all_started` in the pauser test is stored but not meaningfully asserted. The "mixed token" test verifies accounting but not elapsed rate bounds.

Test signals: these are direct integration tests and provide useful coverage for concurrency and operator pause/resume behavior. They complement unit tests by checking real thread contention and elapsed time behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/tests/qps_pauser_integration.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/tests/bats/Makefile -->
# sources/cloud-native/nydus/tests/bats/Makefile

Purpose: defines a BATS-based CI target for end-to-end container/image tests.

Important APIs/types/functions: includes `/usr/lib/os-release` or `/etc/os-release`, then defines target `ci`. The target runs `install_bats.sh` and executes six BATS suites with TAP formatting: Docker image build, nydusd compile, nydus snapshotter compile, container run with RAFS, container run with zran, and RAFS plus Linux compile.

Control flow: `make ci` first ensures BATS is installed, then invokes each `.bats` file sequentially. Any failing shell command stops make.

State and persistence: the Makefile itself persists no state, but the invoked tests build images/binaries and may affect local Docker/containerd/system state.

Dependencies and integration points: integrates with BATS, Docker/container runtimes, nydusd, nydus-snapshotter, and host OS release files. The included OS release variables may be used by invoked BATS scripts or inherited make context.

Risks: assumes Linux-like OS release paths. Sequential BATS invocations can leave partial environment if a later test fails. Requires elevated/container runtime environment not available in many developer shells.

Test signals: this is a top-level CI entry point for smoke and integration behavior beyond Rust unit tests. It is valuable for packaging/runtime validation rather than library-level correctness.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/tests/bats/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/tests/bats/common_tests.sh -->
# sources/cloud-native/nydus/tests/bats/common_tests.sh

Purpose: common shell helpers for the BATS integration suites, primarily deriving toolchain versions, generating a Rust+Go Dockerfile, starting nydus snapshotter, and configuring containerd for Nydus.

Important APIs/types/functions: `parse_toml` extracts a quoted key from TOML text with sed. `get_rust_toolcahin` reads `rust-toolchain.toml` or legacy `rust-toolchain` (function name contains a typo). `get_go_work_version` reads the `go` directive from `go.work`. Global variables set `repo_base_dir`, `rust_toolchain`, `go_work_version`, `compile_image`, and `nydus_snapshotter_repo`. `generate_rust_golang_dockerfile` writes a Dockerfile installing Rust, build packages, rustfmt/clippy, and Go. `run_nydus_snapshotter` writes a temporary nydus-erofs config, clears containerd/nydus cache directories, and launches `containerd-nydus-grpc`. `config_containerd_for_nydus` writes `/etc/containerd/config.toml`, restarts containerd, and sleeps.

Control flow: BATS files source this script, then call helpers to build an environment and configure runtime services. Dockerfile generation is a heredoc. Snapshotter startup runs in background with stdout/stderr redirected to a per-test log. Containerd configuration overwrites or creates the daemon config and restarts the service.

State and persistence: writes Dockerfiles, `/tmp/nydus-erofs-config.json`, `/etc/containerd/config.toml`, snapshotter logs, and deletes `/var/lib/containerd/io.containerd.snapshotter.v1.nydus` plus `/var/lib/nydus/cache`. It changes system containerd state.

Dependencies and integration points: depends on sed, grep, awk, wget, Docker build context, Go downloads, rustup, containerd, systemctl, `containerd-nydus-grpc`, and `/usr/local/bin/nydusd`. Ties Rust and Go workspace versions into the test image.

Risks: TOML parsing is ad hoc and only handles simple quoted `key = "value"` lines. Heredoc paths are unquoted, so spaces in paths would break. It overwrites containerd config and restarts the service, making it unsuitable outside isolated CI. Network download of Go and apt packages affects reproducibility. `git`/network assumptions appear in other BATS helpers.

Test signals: not a test by itself, but it is central to BATS integration repeatability. It exposes environmental assumptions that can explain CI-only failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/tests/bats/common_tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/tests/bats/install_bats.sh -->
# sources/cloud-native/nydus/tests/bats/install_bats.sh

Purpose: installs BATS from source when it is not already present.

Important APIs/types/functions: shell script with `set -e`; runs `which bats && exit`, defines `BATS_REPO=https://github.com/bats-core/bats-core.git` and `LOCAL_DIR=/tmp/bats`, clones the repository, runs `./install.sh /usr`, and removes the temporary directory.

Control flow: if `bats` exists on PATH the script exits successfully. Otherwise it recreates `/tmp/bats`, clones bats-core, installs into `/usr`, returns to the previous directory, and cleans up.

State and persistence: modifies `/usr` by installing BATS and deletes `/tmp/bats`. It has no project-local state.

Dependencies and integration points: used by `tests/bats/Makefile` before running BATS suites. Requires network access, git, shell, and permissions to install under `/usr`.

Risks: `git clone ... || true` can hide clone failures; the subsequent `cd bats-core` will fail under `set -e`, but the original failure reason may be obscured. Unquoted variables are safe for current constants but fragile. Installing to `/usr` requires root privileges and mutates the host.

Test signals: supports integration tests but is not tested itself. Failures here prevent the BATS CI target from running.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/tests/bats/install_bats.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/tests/texture/stargz/estargz_sample.json -->
# sources/cloud-native/nydus/tests/texture/stargz/estargz_sample.json

Purpose: fixture metadata describing a small eStargz/stargz file layout for tests.

Important APIs/types/functions: JSON object with `version: 1` and `entries`. Entries cover a directory `bin/`, regular files `bin/busybox`, `lib/ld-musl-x86_64.so.1`, `.prefetch.landmark`, and hardlink `bin/busybox2`. Regular files include size, modtime, mode, offset, `NumLink`, `digest`, and `chunkDigest`.

Control flow: none; tests parse it as data.

State and persistence: static test fixture only.

Dependencies and integration points: likely consumed by stargz/eStargz conversion or metadata tests to verify TOC parsing, hardlink handling, offsets, and prefetch landmark behavior. Digest strings use OCI-style `sha256:<hex>` format.

Risks: fixture accuracy matters because offsets and digests encode assumptions about a paired compressed sample. If the sample blob changes without updating this JSON, tests may fail or validate stale behavior. The JSON includes a trailing two-space ending after the final brace, which parsers tolerate.

Test signals: provides coverage for directory, regular file, hardlink, digest, chunk digest, and prefetch landmark entries in stargz tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/tests/texture/stargz/estargz_sample.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/upgrade/Cargo.toml -->
# sources/cloud-native/nydus/upgrade/Cargo.toml

Purpose: package manifest for the `nydus-upgrade` crate, which supports Nydus daemon online upgrade state persistence.

Important APIs/types/functions: package metadata names the crate `nydus-upgrade` version `0.2.0`, edition 2021, Apache-2.0 license. Dependencies are `sendfd`, `dbs-snapshot`, `thiserror`, `versionize_derive`, and `versionize`.

Control flow: none; Cargo uses the manifest to resolve and build the crate.

State and persistence: declares persistence-related dependencies but stores no runtime state.

Dependencies and integration points: `sendfd` supports fd transfer over Unix sockets; `dbs-snapshot` and `versionize` support versioned state snapshots; `thiserror` implements typed errors. The crate integrates with the rest of Nydus as an upgrade helper library.

Risks: dependency versions are pinned to broad minor versions. Snapshot compatibility depends on the exact behavior of `dbs-snapshot`/`versionize`, so manifest changes can affect upgrade compatibility.

Test signals: no tests in the manifest. Crate tests live in `src/backend/*` and `src/persist.rs`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/upgrade/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/upgrade/src/backend/mod.rs -->
# sources/cloud-native/nydus/upgrade/src/backend/mod.rs

Purpose: defines the storage-backend abstraction for saving/restoring daemon device fds and serialized state during online upgrade.

Important APIs/types/functions: module exports `unix_domain_socket`. `StorageBackendErr` enumerates `CreateUnixStream`, `SendFd`, `RecvFd`, and `NoEnoughFds`. `Result<T>` aliases the backend error result. `StorageBackend` requires `Send + Sync` and defines `save(&mut self, fds, data) -> Result<usize>` plus `restore(&mut self) -> Result<(Vec<RawFd>, Vec<u8>)>`.

Control flow: concrete backends implement the trait to persist raw fds plus byte state. The included test backend copies fds and state into memory and returns clones on restore.

State and persistence: the trait describes persistence but owns no state itself. Implementations decide whether state is in memory, socket-mediated, or elsewhere.

Dependencies and integration points: uses `std::os::fd::RawFd` and `thiserror`. The Unix-domain-socket implementation in the child module is the primary concrete integration. Higher-level upgrade code can depend on trait objects.

Risks: raw fd ownership semantics are not explicit in the trait; implementors and callers must agree whether returned fds are borrowed, duplicated, or ownership-transferred. `NoEnoughFds` grammar is minor but part of error display.

Test signals: unit test validates trait-object save/restore round trip with a simple in-memory backend and fixed fd/data arrays.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/upgrade/src/backend/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/upgrade/src/backend/unix_domain_socket.rs -->
# sources/cloud-native/nydus/upgrade/src/backend/unix_domain_socket.rs

Purpose: implements `StorageBackend` by transferring state bytes and file descriptors over a Unix domain socket.

Important APIs/types/functions: `UdsStorageBackend` stores `socket_path: PathBuf`. `new` constructs it. `MAX_STATE_DATA_LENGTH` is 32 KiB. `save` connects to the socket and calls `send_with_fd(data, fds)`. `restore` connects, allocates a fixed 32 KiB byte buffer and 16-fd array, then calls `recv_with_fd`.

Control flow: `save` rejects an empty fd slice before connecting, then returns the number of bytes sent. `restore` reads one message with fds, truncates the fd vector to the returned fd count, and returns fds with the data buffer.

State and persistence: no local durable state; persistence is delegated to the peer listening on `socket_path`. Fds are passed through SCM_RIGHTS via the `sendfd` crate. State data is transient bytes.

Dependencies and integration points: depends on `sendfd::{SendWithFd, RecvWithFd}` and `std::os::unix::net::UnixStream`. Implements the backend trait from `upgrade/src/backend/mod.rs`.

Risks: `restore` checks `if fds.is_empty()` before truncating, but the preallocated fd vector has length 16, so a zero-fd receive will not be rejected; it should likely check `fds_cnt`. It also returns the full 32 KiB data buffer rather than truncating to the actual byte count returned by `recv_with_fd`, so callers may see trailing zeroes as state. `save` requires at least one fd, which may preclude data-only upgrade state. Fixed fd capacity of 16 and data capacity of 32 KiB are hard limits.

Test signals: tests cover constructor path storage, empty-fd save error, invalid socket save connect error, and invalid socket restore connect error. There is no loopback socket test validating successful fd/data transfer or received-length truncation.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/upgrade/src/backend/unix_domain_socket.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/upgrade/src/lib.rs -->
# sources/cloud-native/nydus/upgrade/src/lib.rs

Purpose: crate root for `nydus-upgrade`.

Important APIs/types/functions: exposes `pub mod backend` and `pub mod persist`.

Control flow: none.

State and persistence: none directly. It makes backend fd transfer and snapshot persistence modules available to downstream crates.

Dependencies and integration points: Cargo builds this as the library root. Public module exposure defines the crate API.

Risks: minimal. All public API is delegated to submodules, so compatibility is controlled there.

Test signals: no direct tests; submodules contain unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/upgrade/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/upgrade/src/persist.rs -->
# sources/cloud-native/nydus/upgrade/src/persist.rs

Purpose: provides a `Snapshotter` trait for saving and restoring versioned Rust structs using `dbs-snapshot` and `versionize`.

Important APIs/types/functions: `Versions = Vec<HashMap<TypeId, u16>>` maps each snapshot version to per-type version numbers. `Snapshotter` extends `Versionize + Sized + Debug` and requires `get_versions`. Default methods build a `VersionMap`, create a latest-version `Snapshot`, serialize `self` into `Vec<u8>` with `save`, and deserialize from a mutable `Vec<u8>` with `restore`.

Control flow: `new_version_map` iterates over version maps; the first map applies to version 1, later maps call `version_map.new_version()` before setting type versions. `save` constructs a snapshot and serializes into a fresh buffer. `restore` calls `Snapshot::load` over the full input buffer and maps snapshot errors to `std::io::Error::other`.

State and persistence: persists versionized object graphs into byte buffers. No files or sockets are used directly; callers decide where bytes are stored, possibly via `StorageBackend`.

Dependencies and integration points: integrates with `dbs_snapshot::Snapshot` and `versionize::{VersionMap, Versionize}`. Designed for daemon online upgrade structures that need backward/forward version handling.

Risks: correctness depends on each implementor providing a complete `get_versions` map and proper `#[version]` annotations/defaults. `restore` consumes from a slice over the provided vector but does not shrink or clear it. Error messages include debug formatting but no structured error type. TypeId-based version maps are process/build specific and must align with versionize expectations.

Test signals: tests define simple versionized structs and cover single/multiple versions, snapshot creation, save/restore round trips with normal/empty/large values, and invalid/empty restore buffers.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/upgrade/src/persist.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/Cargo.toml -->
# sources/cloud-native/nydus/utils/Cargo.toml

Purpose: package manifest for `nydus-utils`, the shared utility crate used across Nydus.

Important APIs/types/functions: package version `0.5.1`, dual license `Apache-2.0 OR BSD-3-Clause`, edition 2021. Core dependencies include `arc-swap`, `thiserror`, `blake3`, `httpdate`, `lazy_static`, `libc`, `log`, `lz4-sys`, `lz4`, `serde`, `serde_json`, `sha2`, `tokio`, `zstd`, `nix`, `crc`, and local `nydus-api`. Optional `openssl` backs `encryption`; optional `libz-sys` backs `zran`. Target-specific flate2/libz choices use stock zlib on ppc64 and linux/aarch64, zlib-ng elsewhere. Dev dependencies include `vmm-sys-util`, `tar`, `futures`, and Tokio test features.

Control flow: Cargo feature resolution controls whether `compress::zlib_random` and `crypt` build. Target cfg selects zlib implementation.

State and persistence: none directly.

Dependencies and integration points: this manifest determines shared primitive availability for digesting, compression, logging, metrics, async helpers, and encryption across Nydus crates. Docs.rs builds all features for selected targets.

Risks: feature-gated modules can be under-tested in default builds. Vendored OpenSSL increases build time/complexity but improves portability. Target-specific zlib choices signal prior linking issues and should be maintained carefully.

Test signals: dev dependencies support unit and fixture tests throughout `utils/src`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/async_helper.rs -->
# sources/cloud-native/nydus/utils/src/async_helper.rs

Purpose: provides a thread-local Tokio current-thread runtime for synchronous code that needs to execute async operations.

Important APIs/types/functions: `CURRENT_THREAD_RT` is a `thread_local!` `Runtime` built with `Builder::new_current_thread().enable_all()`. `with_runtime<F, R>(f)` passes the runtime reference to a callback.

Control flow: first use on each thread constructs a current-thread runtime or panics with a clear message. Callers run async work through the callback, usually `rt.block_on(...)`.

State and persistence: runtime state is thread-local and lives for the lifetime of the thread. No persistence.

Dependencies and integration points: depends on Tokio runtime builder. Used by synchronous Nydus code paths that need timers, IO, or async primitives without owning a global multi-thread runtime.

Risks: nested Tokio runtime/blocking interactions can panic or deadlock if called from incompatible async contexts. One runtime per thread may increase resource usage in thread-heavy paths. Panic on runtime construction failure is acceptable for utility initialization but not recoverable.

Test signals: unit test calls `with_runtime` twice and verifies simple `block_on` results.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/async_helper.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/compact.rs -->
# sources/cloud-native/nydus/utils/src/compact.rs

Purpose: wraps platform-specific device number encoding/decoding so Linux and macOS callers can use common helpers.

Important APIs/types/functions: `makedev(major, minor)`, `major_dev(dev)`, and `minor_dev(dev)`. Linux delegates to `nix::sys::stat`; macOS uses bit operations compatible with xnu device encoding.

Control flow: compile-time cfg selects Linux or macOS implementations.

State and persistence: none.

Dependencies and integration points: depends on `nix::sys::stat::dev_t`. Used where filesystem metadata/device ids must be constructed or decoded portably.

Risks: macOS bit expressions rely on operator precedence; the current expression `major & 0xff << 24` should be read carefully because shift precedence can be surprising. Linux tests do not validate macOS behavior. Large values are masked by platform encodings.

Test signals: Linux-only tests cover round-tripping normal and large major/minor values and direct nix compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/compact.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/compress/lz4_standard.rs -->
# sources/cloud-native/nydus/utils/src/compress/lz4_standard.rs

Purpose: low-level LZ4 block compression/decompression wrappers over `lz4_sys`.

Important APIs/types/functions: `lz4_compress(src) -> Result<Vec<u8>>` calls `LZ4_compressBound` and `LZ4_compress_default`. `lz4_decompress(src, dst) -> Result<usize>` validates destination size and calls `LZ4_decompress_safe`.

Control flow: compression rejects inputs too large for LZ4's i32 API or invalid compression bounds, allocates a destination buffer with capacity equal to the bound, calls the C API, sets vector length to returned compressed size, and returns it. Decompression rejects destination buffers at or above `i32::MAX`, validates the requested size with `LZ4_compressBound`, calls safe decompression, and maps negative return to IO error.

State and persistence: no state; all buffers are caller/local memory.

Dependencies and integration points: used by `compress/mod.rs` for `Algorithm::Lz4Block`. Depends on `libc::c_char`, `lz4_sys`, and crate error macros.

Risks: uses unsafe FFI and `Vec::set_len`; correctness depends on LZ4 respecting the supplied capacity. The test allocates a `u32::MAX`-sized vector to trigger errors, which may be too memory-heavy for some environments. No streaming LZ4 support here.

Test signals: boundary error test checks oversized compression/decompression input handling. Round-trip tests for LZ4 live in `compress/mod.rs`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/compress/lz4_standard.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/compress/mod.rs -->
# sources/cloud-native/nydus/utils/src/compress/mod.rs

Purpose: central compression abstraction for Nydus utilities, supporting no compression, LZ4 block, gzip, zstd, streaming gzip/zstd decoders, gzip compressed-size estimation, and feature-gated zran random access.

Important APIs/types/functions: `Algorithm::{None,Lz4Block,GZip,Zstd}` with display, string parsing, numeric conversion, and `is_none`. `compress(src, algorithm)` returns a `Cow<[u8]>` plus boolean indicating whether compression was kept. `decompress(src, dst, algorithm)` reverses block compression. `Decoder<R>` wraps `Read` implementations for no compression, gzip `MultiGzDecoder`, and zstd stream decoder; LZ4 block is explicitly unsupported for streaming. `ZlibDecoder<R>` wraps gzip/zlib multi-member decoding. `compute_compressed_gzip_size` estimates how many compressed bytes may be needed to inflate a gzip member. `zstd_compress` uses zstd default compression level.

Control flow: `compress` short-circuits empty and `None` data, compresses via algorithm-specific path, then discards compressed output if it does not meet `COMPRESSION_MINIMUM_RATIO` (currently 100%, meaning compressed size must be strictly smaller). `decompress` requires exact size match for `None`, delegates to LZ4 FFI, reads exact gzip output into destination, or calls zstd bulk decompression. `Decoder::new` selects stream decoder and panics for LZ4 block.

State and persistence: no durable state. Stream decoders hold reader/decompressor state while reading.

Dependencies and integration points: depends on `flate2`, `zstd`, internal `lz4_standard`, and optional `zlib_random`. Used across RAFS/blob paths for chunk compression and image conversion. Fixture tests read from `tests/texture/zran`.

Risks: `Algorithm::from_str` error text mentions only none/lz4 despite gzip/zstd support. `Decoder::new` panics for LZ4 instead of returning an error, so callers must branch first. `decompress` for gzip uses `read_exact`, requiring callers to know exact uncompressed size. Compression-ratio arithmetic uses integer division and could lose precision for small buffers. Some tests rely on fixture files and may not run in minimal package contexts.

Test signals: extensive unit tests cover gzip/none/zstd/lz4 round trips across sizes, one/two/16/4095/4096/4097-byte cases, stream decoders over fixture gzip files, algorithm parsing/display/numeric conversion, invalid strings, and consistency.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/compress/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/compress/zlib_random.rs -->
# sources/cloud-native/nydus/utils/src/compress/zlib_random.rs

Purpose: feature-gated zran support for generating and using random-access context information over gzip/zlib streams, especially OCI tarball streams.

Important APIs/types/functions: constants define dictionary/window and context limits: `ZRAN_DICT_WIN_SIZE`, `ZRAN_MAX_CI_ENTRIES`, `ZRAN_READER_BUF_SIZE`. `ZranChunkInfo` maps uncompressed chunk ranges to compression-context slices. `ZranContext` stores compressed/uncompressed offsets/lengths, pending bit state, previous byte, and dictionary. `ZranDecoder::uncompress` decodes a random-access slice using a context. `ZranGenerator<R>` wraps `ZranReader<R>` and emits context entries/chunk info via `begin_read` and `end_read`. `ZranReader<R>` tracks compressed input size/hash and exposes initial-data seeding. `ZranStream` wraps raw `z_stream` with custom alloc/free, reset, dictionary, prime bits, and pointer setters.

Control flow: `ZranReaderState::read` feeds compressed input to zlib in `Z_BLOCK` mode, records block-boundary context and dictionaries, handles gzip member boundaries by reset, and returns decompressed bytes to callers such as `tar::Archive`. `ZranGenerator::begin_read` decides whether to reuse or create a compression-info entry based on compressed/uncompressed growth, stream switches, and gaps. `end_read` updates the selected context sizes and returns a `ZranChunkInfo`. `ZranDecoder::uncompress` resets to raw inflate mode, primes pending bits, installs dictionary, inflates the requested context, and has special handling for gzip multi-member transitions/trailers.

State and persistence: contexts and chunk info are persistent metadata that can be stored by callers to later fetch compressed byte ranges and decompress only desired uncompressed chunks. Reader state tracks zlib stream position, dictionaries, SHA256 of compressed bytes read, and total input size.

Dependencies and integration points: depends on `libz_sys`, `sha2`, `tar` in tests, and unsafe C ABI calls including `inflateGetDictionary`. Enabled by the `zran` feature from `utils/Cargo.toml`. Integrates with stargz/zran image handling where random access to compressed tar content is needed.

Risks: this is unsafe, pointer-heavy code around zlib internals; correctness depends on exact `z_stream` pointer/avail accounting. `begin_read` accepts tunables but does not enforce documented relationships between min/max sizes. `ZranDecoder::uncompress` has complex multi-member gzip handling and strict input length checks. Custom zalloc/zfree must match layout precisely. Several methods lock `Mutex` and unwrap, so poisoning panics. Feature-gated code may receive less routine build coverage.

Test signals: tests parse single-stream, first-stream, two-stream, and zero-file gzip tar fixtures; generate compression info; decode bgzip and multi-stream contexts; and verify reader initial-data accounting. These are strong fixture tests for expected stream patterns, but not exhaustive fuzz/property tests for malformed streams.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/compress/zlib_random.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/config.rs -->
# sources/cloud-native/nydus/utils/src/config.rs

Purpose: global scoped configuration store for runtime string settings such as registry auth, proxy URL, and Dragonfly scheduler endpoint.

Important APIs/types/functions: `CONFIG_MAP` is `ArcSwap<HashMap<String, String>>`. `Keys` enumerates `RegistryAuth`, `ProxyURL`, and `DragonflySchedulerEndpoint`, with conversions to/from strings. Public functions include `set`, `set_if_empty`, `get_changed`, `get`, `remove`, `clear`, `contains_key`, `keys`, `len`, `is_empty`, and `get_all`.

Control flow: keys are stored as `"id:key"` strings. Writers clone the current map, mutate the clone, and atomically store a new `Arc<HashMap<...>>`. Readers load the current map snapshot and clone values as needed. `set_if_empty` reads the current value and only writes a non-empty replacement if the current value is empty. `get_all(Some(id))` strips the `id:` prefix and returns only entries for that id; `None` clones the whole map.

State and persistence: all configuration is process-global and in-memory. There is no persistence across process restart.

Dependencies and integration points: uses `arc-swap` for lock-free read-mostly access and `lazy_static`. Likely used by backend/auth/proxy code to update live configuration for mounted instances.

Risks: concurrent writers can lose updates because each write clones from a snapshot and replaces the entire map without compare-and-swap retry. `set_if_empty` is not atomic relative to other writers. Empty string values are indistinguishable from missing values for `get`, though `contains_key` can distinguish them. Plain `"id:key"` concatenation can collide if ids contain chosen key suffix patterns, though current filtering uses exact prefix.

Test signals: many tests cover set/get, missing keys, change detection, removal, clearing, key listing, length, update, special characters, large values, filtered `get_all`, `set_if_empty`, and key conversion. Tests serialize access with a global lock; the "concurrent" test joins threads sequentially and does not expose lost-update races.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/crc32.rs -->
# sources/cloud-native/nydus/utils/src/crc32.rs

Purpose: CRC32 checksum helper using the iSCSI polynomial for buffers, readers, digesters, and raw fd ranges.

Important APIs/types/functions: `Algorithm::{None,Crc32Iscsi}` with display, default, and numeric conversions. `Crc32` wraps `crc::Crc<u32, Table<16>>`. Methods are `new`, `from_buf`, `from_reader`, `digester`, and `from_raw_fd`.

Control flow: `Crc32::new` selects `CRC_32_ISCSI`, with `Algorithm::None` currently falling back to the same implementation. `from_reader` streams through a 1 MiB buffer until EOF. `from_raw_fd` uses `nix::sys::uio::pread` from a starting offset for a requested size, retrying interrupted reads and stopping on EOF or requested byte count.

State and persistence: no persistent state. Digesters hold incremental checksum state.

Dependencies and integration points: depends on `crc`, `nix::sys::uio`, and project `last_error!` macro. Storage utilities use it for `check_crc`; other chunk verification paths can use it over memory, readers, or file descriptors.

Risks: `Algorithm::None` behaving as CRC32 may surprise callers expecting disabled checksum behavior. `from_raw_fd` silently returns checksum of fewer bytes if EOF occurs before `size`; callers must compare file size separately if short reads are invalid. Raw fd API does not own or close the fd.

Test signals: tests cover display/default/conversions, known checksum for `"123456789"`, empty buffers, large reader input, incremental digester, Linux memfd raw-fd checksum with offset and zero-size reads.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/crc32.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/crypt.rs -->
# sources/cloud-native/nydus/utils/src/crypt.rs

Purpose: feature-gated encryption utilities for Nydus data and metadata, supporting AES-128-XTS, AES-256-XTS, and AES-256-GCM through OpenSSL.

Important APIs/types/functions: constants define data unit, IV, key, tag, and padding sizes. `Algorithm` exposes cipher creation, encryption-enabled checks, AEAD checks, tag size, and key length. `Cipher` wraps OpenSSL cipher handles and supports `encrypt`, `decrypt`, `encrypt_aead`, `decrypt_aead`, `encrypted_size`, `tag_size`, `tweak_key_for_xts`, random key/IV generation, and internal `cipher`. `CipherContext` stores key, IV, convergent-encryption flag, and algorithm, with `new`, `generate_cipher_meta`, and `get_cipher_meta`. Top-level helpers `encrypt_with_context` and `decrypt_with_context` conditionally apply encryption based on a boolean.

Control flow: XTS encryption pads data shorter than 16 bytes to an 18-byte buffer containing a 16-byte CMS-like padded block plus a two-byte magic suffix, then decrypt trims only when this magic padding is present. AES-GCM is only available through AEAD-specific methods and returns/accepts a separate tag. `CipherContext::new` validates key length and rejects identical XTS key halves. Convergent metadata encryption can derive key material from data and substitutes default keys for symmetric halves. Random key generation uses OpenSSL RNG then tweaks XTS keys to avoid identical halves.

State and persistence: `CipherContext` stores key and IV in memory. Ciphertext/tag output may be persisted by callers. No key zeroization is visible.

Dependencies and integration points: depends on optional `openssl` feature, `std::sync::Arc`, and crate error macros. Used by encrypted blob/bootstrap metadata paths when `nydus-utils/encryption` is enabled.

Risks: `CipherContext::new` indexes `key[0..key_length >> 1]`; for `Algorithm::None` with zero-length key this is safe, but zero-length encryption context semantics should be reviewed. Internal `alloc_buf` does not handle allocation failure explicitly and creates a vector from possibly null pointer; unlike storage's allocator, it does not call `handle_alloc_error`. XTS padding returns 18 bytes for very small plaintext while `encrypted_size` reports 16 for plaintext smaller than 16, so callers relying on `encrypted_size` may under-allocate. AES-GCM uses 12-byte tags but tests pass 16-byte IVs; nonce policy must be enforced by callers. Error text for `decrypt_aead` says "failed to encrypt data".

Test signals: tests cover XTS encrypt/decrypt determinism, IV/data sensitivity, small and >16-byte data, AES-GCM encrypt/decrypt/tag behavior, key tweaking, algorithm attributes/parsing/conversions, context validation, optional encryption bypass, and convergent key generation.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/crypt.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/digest.rs -->
# sources/cloud-native/nydus/utils/src/digest.rs

Purpose: digest primitives for RAFS/Nydus content hashing with Blake3 and SHA256.

Important APIs/types/functions: `RAFS_DIGEST_LENGTH = 32`, `DigestData = [u8; 32]`, `Algorithm::{Blake3,Sha256}` with display, parsing, and numeric conversions. `DigestHasher` trait abstracts update/finalize. `RafsDigestHasher` wraps boxed `blake3::Hasher` or `Sha256`. `RafsDigest` is a 32-byte `repr(C)` digest with `from_buf`, `from_reader`, `from_string`, `hasher`, `Display`, `AsRef<[u8]>`, and conversions from digest data and into `String`.

Control flow: buffer and reader hashing select the requested algorithm and stream bytes until EOF. `from_string` parses a hex string in two-byte chunks into digest bytes. Display formats each byte as two lowercase hex digits. `From<&DigestData> for &RafsDigest` performs an unsafe reference cast for zero-copy digest interpretation.

State and persistence: digest values are plain 32-byte records commonly persisted in metadata. Incremental hashers hold transient state.

Dependencies and integration points: depends on `blake3`, `sha2`, and project error macros. Used by storage chunk metadata, hash verification, and image formats.

Risks: `from_string` unwraps UTF-8 and hex parsing and does not validate length; malformed or short/long strings can panic or partially fill data. The unsafe reference conversion relies on `repr(C)` single-field layout alignment compatibility. Display uses enum debug names (`Blake3`, `Sha256`) while parsing expects lowercase (`blake3`, `sha256`), so string forms are not symmetrical for algorithms.

Test signals: tests cover known Blake3/SHA256 vectors, incremental hashing, algorithm parsing/conversions/display, reader hashing, hex string conversion, `AsRef`, and data conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/digest.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/exec.rs -->
# sources/cloud-native/nydus/utils/src/exec.rs

Purpose: small shell-command execution helper with optional stdin and captured output.

Important APIs/types/functions: `exec(cmd: &str, output: bool, input: &[u8]) -> Result<String>` runs `sh -c cmd` with `RUST_BACKTRACE=1`, optional piped stdin, and either captured or inherited stdout/stderr.

Control flow: the function configures a child process, writes input if provided, waits for completion, returns captured stdout when `output` is true, and maps non-zero exits to `eother!("exit with non-zero status")`. Captured stdout must be valid UTF-8.

State and persistence: no internal state. External commands can modify arbitrary system state depending on `cmd`.

Dependencies and integration points: used by utility callers needing shell integration. Depends on std process APIs and project logging/error macros.

Risks: command string is executed through the shell, so callers must avoid passing unsanitized user input. Non-zero stderr is discarded from error messages when captured. Captured stdout requiring UTF-8 limits binary commands. `output=false` inherits process output, which can noisy-log tests or daemons.

Test signals: tests cover captured echo, inherited echo, stdin piping through `cat`, and non-zero exit errors for both output modes.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/exec.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/filemap.rs -->
# sources/cloud-native/nydus/utils/src/filemap.rs

Purpose: safe-ish wrapper for memory mapping file regions and reading/writing typed data from mapped bytes.

Important APIs/types/functions: `FileMapState` stores base/end pointers, size, and owned fd. `new(file, offset, size, writable)` maps with `mmap(MAP_NORESERVE | MAP_SHARED)` and takes ownership of the fd. Accessors include `size`, `get_ref<T>`, `get_mut<T>`, `get_slice<T>`, `get_slice_mut<T>`, `validate_range`, unsafe `offset`, and `sync_data`. `clone_file(fd)` duplicates a raw fd into a `File`.

Control flow: `new` maps the requested file region and converts the `File` into a raw fd only after mmap success. Drop unmaps and closes the fd. Range accessors compute start/end pointers with wrapping arithmetic and reject ranges outside `[base,end)`. Slice accessors check multiplication and address overflow and use dangling pointers for zero-length slices. `sync_data` temporarily reconstructs a `File` from the owned fd, calls `sync_data`, then forgets it to avoid closing.

State and persistence: owns an mmap and fd. Writes through mutable accessors can persist to the mapped file; `sync_data` flushes file data.

Dependencies and integration points: depends on `libc`, `nix::unistd::close`, Unix fd traits, and project error macros. Used by bootstrap/image metadata readers needing typed access to mapped files.

Risks: typed reference methods do not check alignment for `T`, so unaligned offsets can cause undefined behavior. `get_mut` can produce mutable references even if the mapping was created read-only; writing through them would fault or violate aliasing expectations. `MAP_NORESERVE`/`MAP_SHARED` are platform-specific to Unix/Linux assumptions. The `Send`/`Sync` impl assumes read-only data, but writable mappings can be created. `mmap` with size zero is not specially handled.

Test signals: tests map a RAFS bootstrap fixture and validate magic/range errors, default drop, mmap error on writable mapping of read-only file, slice overflow/out-of-range checks, and zero-length slice handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/filemap.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/inode_bitmap.rs -->
# sources/cloud-native/nydus/utils/src/inode_bitmap.rs

Purpose: concurrent bitmap for tracking inode numbers and exporting compact inode ranges.

Important APIs/types/functions: `InodeBitmap` wraps `RwLock<BTreeMap<u64, AtomicU64>>`, where map key is `ino >> 6` and bit mask is `1 << (ino & 0x3f)`. Public methods are `new`, `set`, `is_set`, `clear`, `clear_all`, `bitmap_to_array`, and `bitmap_to_array_and_clear`. `Display`/`Debug` serialize as JSON containing `"inode_range"`.

Control flow: `set` first tries a read lock and atomic OR on an existing bucket; if missing, it drops the read lock, takes a write lock, inserts an `AtomicU64`, and ORs the bit. `clear` atomic-ANDs the inverted mask for existing buckets. `bitmap_to_vec` scans sorted buckets and set bits with `trailing_zeros`, merging adjacent inode values into either singleton `[n]` or range `[start,end]`. `bitmap_to_array_and_clear` uses `fetch_and(0)` as it scans.

State and persistence: in-memory bitmap only. JSON/range output can be persisted by callers.

Dependencies and integration points: depends on serde_json for display and std atomics/locks. Useful for dirty inode tracking or reporting changed inode ranges.

Risks: inode 0 is commented as invalid but can still be set and exported; tests set it indirectly in the 0..100000 loop. Atomic operations are relaxed, which is fine for bitmap counters when protected by map structure locks but gives no ordering for external data. Empty buckets remain after clear, so long-lived instances can retain map entries. `bitmap_to_array_and_clear` may race with concurrent `set`, potentially clearing bits set during scan.

Test signals: tests cover setting, clearing, range merging, clear_all, array-and-clear, display/debug JSON, nonexistent clear/is_set, idempotent set, empty behavior, and range formatting helper.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/inode_bitmap.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/lib.rs -->
# sources/cloud-native/nydus/utils/src/lib.rs

Purpose: crate root for `nydus-utils`, exporting utility modules and defining common numeric rounding, delay, and lazy-drop helpers.

Important APIs/types/functions: macro imports for `log`, `serde`, `lazy_static`, and `nydus_api`. Re-exports `exec::*`, `InodeBitmap`, `reader::*`, and `types::*`. Public modules include async, compact, compress, config, crc32, digest, exec, filemap, inode_bitmap, logger, metrics, mpmc, reader, singleflight, trace, types, verity, and feature-gated `crypt`. Helper functions are `div_round_up`, `round_up`, `round_up_usize`, `try_round_up_4k`, `round_down_4k`, and `round_down`. `DelayType` and `Delayer` implement fixed/exponential sleeps. `lazy_drop` defers dropping an object on a spawned thread after 600 seconds.

Control flow: rounding helpers require power-of-two divisors via debug assertions and use `div_ceil` or bit masking. `try_round_up_4k` uses checked addition and fallible conversion to avoid overflow. `Delayer::delay` sleeps fixed duration or `2^attempts * time`, then increments attempts. `lazy_drop` moves a value into a background thread, sleeps ten minutes, then drops it.

State and persistence: no persistent state. `Delayer` tracks attempt count. `lazy_drop` extends object lifetime asynchronously.

Dependencies and integration points: root export surface for many Nydus crates. Rounding helpers are used by storage/readahead/alignment code. `lazy_drop` can help release large objects outside latency-sensitive paths.

Risks: `round_up`/`round_up_usize` can overflow in release builds because only debug assertions guard divisor properties and no checked arithmetic is used. `Delayer::BackOff` can overflow shift or duration multiplication for high attempts. `lazy_drop` spawns an untracked thread per call and requires `unsafe impl Send` wrapper instead of bounding `T: Send`; moving non-Send values across threads is unsound.

Test signals: tests cover 4 KiB rounding overflow/conversion behavior, usize rounding, generic round up/down/div helpers, and delayer attempt increments with zero-duration sleeps.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/logger.rs -->
# sources/cloud-native/nydus/utils/src/logger.rs

Purpose: bounded in-memory error/event holder that exports recent critical messages as JSON.

Important APIs/types/functions: `ErrorHolderError::{TooLarge,Serde}`, `Result<T>`, and `ErrorHolder`. `ErrorHolder` tracks `max_errors`, `total_errors`, `max_size`, `total_size`, and a `Mutex<VecDeque<String>>`. `new(max_errors, max_size)` constructs it. `push(&mut self, error)` timestamps an error with HTTP-date format and appends it while evicting old entries to satisfy count/size limits. `export(&self)` serializes the holder to JSON.

Control flow: `push` formats the incoming error with current time, then loops evicting from the front while adding the new message would exceed byte or count limits. If the new message is too large even after evicting all entries, it returns `TooLarge`. `export` locks the queue and serializes `self`; serde sees the mutex field through its `Serialize` support.

State and persistence: in-memory circular buffer only. Exported JSON can be persisted or exposed by diagnostics.

Dependencies and integration points: depends on `httpdate`, `serde`, `serde_json`, `Mutex`, and `VecDeque`. Useful for diagnostics endpoints or status reports where logs must be bounded.

Risks: `push` requires `&mut self` despite also using a mutex, limiting shared concurrent use unless wrapped externally. Size accounting uses `String::len` bytes and includes timestamp prefix. If `max_errors` or `max_size` is zero, most pushes will return `TooLarge`. Serialization while holding the lock could block pushers if external synchronization is added.

Test signals: overflow test pushes repeated errors to verify max count/size are respected and that an oversized message returns `TooLarge`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/logger.rs -->
