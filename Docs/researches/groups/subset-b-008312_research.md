# subset-b-008312 research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/device.rs -->
# sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/device.rs

## Purpose
Defines `CryDevice`, the `cryfs_rustfs::object_based_api::Device` adapter for a CryFS filesystem backed by a `ConcurrentFsBlobStore`. It owns the root blob id, atime policy, async-drop blobstore guard, and a shared last-access timestamp used by idle unmount logic.

## Important APIs, types, and functions
- `CryDevice::load_filesystem` wraps an existing blobstore and root id; `create_new_filesystem` creates and flushes a root directory blob before exposing the device.
- `sanity_check` opens the root dir and enumerates entries to validate the loaded filesystem.
- Private path loaders `load_blob`, `load_blob_from_relative_path`, and `load_two_blobs` traverse directory entries and handle shared-prefix loading for rename.
- The `Device` impl exposes associated node/dir/file/symlink/open-file adapters, updates `last_access_time` in `on_operation`, returns `rootdir`, performs `rename`, and computes `statfs`.
- `check_entry_overwrite_allowed` enforces file/dir overwrite compatibility and rejects overwriting non-empty directories.

## Control flow
Root access constructs a root `NodeInfo` without loading the root until a directory operation needs it. Path traversal repeatedly locks the current directory blob, resolves an entry id, drops the previous blob when owned, and loads the next blob. Rename first rejects moving a path into its own descendant and root rename cases, then splits source/destination parents. Same-parent rename delegates to `DirBlob::rename_entry_by_name`; cross-parent rename loads both parents, clones the source entry, loads the child blob, removes the source entry, adds/overwrites the destination, and updates the child parent pointer.

## State and persistence behavior
Persistent state is entirely in fsblobstore blobs: directory entries, blob type, parent pointers, and block counts. `create_new_filesystem` persists the root directory. Rename mutates directory blobs and, for cross-directory moves, the child blob's parent pointer. `statfs` reads used/free block estimates from the blobstore. `last_access_time` is runtime-only atomic state for idle unmount.

## Dependencies and integration points
This file integrates `cryfs_blobstore`, `cryfs_fsblobstore`, `cryfs_blockstore::RemoveResult`, `cryfs_rustfs` device traits and error types, `AsyncDropGuard`/`AsyncDropArc`, `maybe_owned`, `AtomicInstant`, and path utilities. It is the entry point consumed by `cryfs-runner::make_device` and the RustFS/FUSE backend.

## Risks and edge cases
Cross-parent rename has explicit TODOs for race windows and exception safety: source entry removal can succeed before destination add or parent-pointer update fails. Error mapping sometimes collapses storage failures to `UnknownError` or EIO-like custom errors. Overwrite checks depend on parent entry type being honest; corrupted type/blob mismatches are surfaced as filesystem corruption only when loading the overwritten directory.

## Test signals
No local tests are in this file. Indirect signals should come from filesystem operation tests that cover root load, statfs, same-parent rename, cross-parent rename, overwrite type rules, non-empty directory overwrite rejection, and idle-unmount access timestamp updates.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/device.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/dir.rs -->
# sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/dir.rs

## Purpose
Implements `CryDir`, the directory adapter used by RustFS to look up, list, create, remove, rename, move, and fsync CryFS directory entries stored in `DirBlob`s.

## Important APIs, types, and functions
- `CryDir::new` binds a shared blobstore guard to shared `NodeInfo`.
- Helpers create flushed child blobs (`create_dir_blob`, `create_file_blob`, `create_symlink_blob`) before adding parent entries.
- `lookup_child`, `rename_child`, `move_child_to`, `entries`, `create_child_dir`, `remove_child_dir`, `create_child_symlink`, `remove_child_file_or_symlink`, `create_and_open_file`, and `fsync` implement the `Dir` trait.
- `blob_as_dir`/`blob_as_dir_mut` convert entry-type expectations into `CorruptedFilesystem` errors.

## Control flow
Lookup loads the directory blob, reads a matching entry under lock, then constructs child `NodeInfo` that keeps the parent blob alive. Creation loads the parent and creates the child blob concurrently; if parent insertion fails, it removes the just-created blob. Removal first validates type and emptiness when needed, removes the parent entry, flushes the parent to avoid dangling entries, then removes the child blob. `move_child_to` loads source and destination parents, optionally checks ancestor cycles, removes the old entry, adds or overwrites the new entry, updates the moved blob's parent pointer, then updates source/destination parent mtimes.

## State and persistence behavior
Directory entries carry names, blob ids, entry type, mode, uid/gid, atime, mtime, and ctime. This code intentionally orders persistence: newly created blobs are flushed immediately before parent references are created, and removed parent entries are flushed before deleting the target blob. Directory data fsync flushes the directory blob; full fsync also flushes parent metadata.

## Dependencies and integration points
Depends on `ConcurrentFsBlobStore`, `DirBlob`, `FsBlob`, fsblobstore entry errors, `cryfs_rustfs::object_based_api::Dir`, path components, async-drop utilities, and `check_entry_overwrite_allowed` from `device.rs`. It creates `CryNode`, `CryOpenFile`, and `CrySymlink` adapters for child results.

## Risks and edge cases
Several operations release and reacquire locks, and comments call out race conditions in removal and move paths. Move has incomplete rollback if destination insertion or parent-pointer update fails after source removal. Create paths map some insertion failures to `UnknownError` after cleanup. `create_and_open_file` currently ignores open flags, and symlink attrs compute size from the link name rather than the target.

## Test signals
No in-file tests. Expected integration tests should assert POSIX-like directory behavior: duplicate create, lookup miss, rmdir non-empty, unlink-vs-rmdir type errors, flush ordering on failures, rename overwrite rules, cross-directory moves, timestamp updates, and optional ancestor cycle rejection.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/dir.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/file.rs -->
# sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/file.rs

## Purpose
Defines `CryFile`, the lightweight closed-file adapter that can be converted into a `CryOpenFile` for read/write operations.

## Important APIs, types, and functions
- `CryFile::new` stores a borrowed blobstore guard and shared `NodeInfo`.
- The `File` trait impl exposes `into_open`, returning `CryOpenFile`.
- `Debug` prints `node_info`; `AsyncDrop` drops the `NodeInfo` guard.

## Control flow
The adapter does not load or validate file contents itself. `into_open` consumes the async-drop guard with `unsafe_into_inner_dont_drop`, clones the shared blobstore arc, transfers the `NodeInfo` guard, and constructs an open-file adapter. Open flags are accepted but currently ignored.

## State and persistence behavior
`CryFile` owns no persistent state. It keeps the parent/entry metadata reachable through `NodeInfo`; persistence work is delegated to `CryOpenFile` and `NodeInfo`.

## Dependencies and integration points
Integrates the RustFS `File` trait with `CryOpenFile`, `CryDevice`, `NodeInfo`, `ConcurrentFsBlobStore`, and CryFS async-drop ownership.

## Risks and edge cases
Ignoring `OpenInFlags` means access mode, append, truncate, and similar semantics are not enforced here. The TODO notes potential missed sharing of cached metadata between `CryFile` and `CryOpenFile`.

## Test signals
Coverage should verify that opening a looked-up file yields a usable `CryOpenFile`, that dropped file handles release metadata guards, and that open flags are either implemented elsewhere or intentionally unsupported.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/mod.rs -->
# sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/mod.rs

## Purpose
Declares the filesystem module layout and exposes the public filesystem entry type.

## Important APIs, types, and functions
- Private modules: `device`, `dir`, `file`, `node`, `node_info`, `open_file`, and `symlink`.
- Public export: `pub use device::CryDevice`.

## Control flow
There is no runtime control flow. The file is a module boundary that hides implementation adapters while keeping `CryDevice` available to external crates.

## State and persistence behavior
No state is stored here. Persistence is handled by the submodules, especially `device.rs`, `dir.rs`, `node_info.rs`, and `open_file.rs`.

## Dependencies and integration points
This module is consumed by `cryfs-filesystem/src/lib.rs` and by `cryfs-runner`, which imports `cryfs_filesystem::filesystem::CryDevice`.

## Risks and edge cases
Because only `CryDevice` is exported, downstream code cannot directly name internal adapter types except through associated types. That is a deliberate encapsulation boundary but can complicate integration tests that want to inspect internals.

## Test signals
Compile-time tests and downstream crate builds are the primary signal: if module visibility or exports regress, `cryfs-runner` and RustFS integrations fail to compile.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/node.rs -->
# sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/node.rs

## Purpose
Implements `CryNode`, the generic RustFS node adapter that dispatches a CryFS blob-backed node into directory, file, or symlink adapters and exposes shared attribute operations.

## Important APIs, types, and functions
- `CryNode::new` wraps a `NodeInfo` into `AsyncDropArc`; `new_internal` accepts an already shared `NodeInfo`.
- `load_blob` delegates to `NodeInfo`.
- The `Node` trait impl provides `as_dir`, `as_symlink`, `as_file`, `getattr`, `setattr`, and test-only `fsync`.
- `AsyncDrop` releases `node_info` and the blobstore guard.

## Control flow
Type conversion is based on `NodeInfo::node_type`, avoiding blob loads on the happy path. If the type matches, the node clones the blobstore and `NodeInfo` into the specialized adapter; if it does not match, it returns RustFS type errors. Attribute operations are forwarded directly to `NodeInfo`.

## State and persistence behavior
`CryNode` keeps shared runtime references to the blobstore and node metadata. It does not mutate persistence except through forwarded `setattr` and test-only `fsync`, which can flush the blob and parent metadata.

## Dependencies and integration points
Connects `CryDir`, `CryFile`, `CrySymlink`, `NodeInfo`, `ConcurrentFsBlobStore`, `BlobType`, and the RustFS `Node` trait. RustFS inode caching can reuse this node, so `NodeInfo` is intentionally arc-shared.

## Risks and edge cases
`as_file` maps symlink-as-file to `UnknownError` with a TODO, which may produce poor POSIX error fidelity. The test-only `fsync` duplicates logic from directory/open-file fsync. Incorrect `NodeInfo` entry type can delay corruption detection until the specialized adapter loads and casts the blob.

## Test signals
Useful signals include type-dispatch tests for dir/file/symlink nodes, getattr/setattr forwarding, symlink-as-file error behavior, and inode-cache reuse of shared `NodeInfo`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/node.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/node_info.rs -->
# sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/node_info.rs

## Purpose
Centralizes metadata for root and non-root nodes: blob identity, parent directory handle, name, blob type, atime policy, optional ancestor chain, attribute reads/writes, timestamp updates, truncation, and metadata flushing.

## Important APIs, types, and functions
- `NodeInfoImpl` distinguishes `IsRootDir` from `IsNotRootDir`.
- Constructors `new_rootdir` and `new_non_root_dir` set up metadata ownership.
- Accessors include `blob_id`, `parent_blob`, `node_type`, `atime_update_behavior`, and optional ancestor helpers.
- `load_blob`, `flush_if_cached`, `getattr`, `setattr`, `truncate_file`, timestamp update helpers, and `flush_metadata` perform most metadata operations.
- `dir_entry_to_node_attrs` maps fsblobstore `DirEntry` metadata to RustFS `NodeAttrs`.

## Control flow
Root getattr fabricates attrs from current uid/gid and current time. Non-root getattr loads lstat size from the child blob and entry metadata from the parent directory. `setattr` truncates first when size is provided, then updates parent entry mode/uid/gid/atime/mtime and refreshes mtime after truncation. Read/write/list operations use concurrent wrappers to update parent timestamps and run data operations in parallel.

## State and persistence behavior
Non-root metadata persists in the parent directory entry, while file length and symlink target size are read from the child blob. Truncation mutates the file blob. Timestamp helpers mutate parent directory entries. Root metadata is currently synthetic and not persisted. `flush_metadata` flushes the parent directory blob when available.

## Dependencies and integration points
Uses `ConcurrentFsBlobStore`, `ConcurrentFsBlob`, `FsBlob`, `DirBlob`, `FileBlob`, `DirEntry`, mode/uid/gid types, RustFS `NodeAttrs`, `AtimeUpdateBehavior`, tokio join, and async-drop macros. It is shared by every node, directory, file, symlink, and open-file adapter.

## Risks and edge cases
Root attrs are synthetic and may change across calls. `setattr` asserts `ctime.is_none`, so a caller passing ctime panics rather than receiving `FsError`. Truncation before parent attr mutation can leave partial effects if later metadata update fails. Parent directory casts use `expect` in places, so internal invariant violations can panic. Timestamp updates for root are no-ops.

## Test signals
Coverage should verify getattr/setattr mapping, truncate side effects and mtime updates, root behavior, atime policy adaptation, metadata flushes, missing parent entries, corrupted child blob types, and optional ancestor chain construction.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/node_info.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/open_file.rs -->
# sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/open_file.rs

## Purpose
Implements `CryOpenFile`, the RustFS open-file adapter for reading, writing, flushing, fsyncing, and changing attributes on file blobs.

## Important APIs, types, and functions
- `CryOpenFile::new` owns blobstore and shared `NodeInfo` guards.
- `load_blob` and `as_file_mut` load/cast the underlying blob.
- `_read`, `_write`, and `flush_file_contents` perform file-data operations.
- The `OpenFile` trait impl provides `getattr`, `setattr`, `read`, `write`, `flush`, and `fsync`.

## Control flow
Reads allocate a `Data` buffer of requested size, call `try_read`, and shrink to bytes actually read. Non-zero reads run concurrently with parent atime updates. Writes call `FileBlob::write`; non-empty writes run concurrently with parent mtime updates. `flush` currently delegates to full `fsync(false)` for parity with the former C++ behavior. `fsync(true)` flushes file contents only; `fsync(false)` flushes file contents and parent metadata in parallel.

## State and persistence behavior
File contents and size persist in the file blob. Access and modification times persist in the parent directory entry through `NodeInfo`. Full fsync persists both content and metadata; datasync mode skips parent metadata.

## Dependencies and integration points
Depends on `cryfs_utils::data::Data`, `ConcurrentFsBlobStore`, `FileBlob`, `FsBlob`, RustFS `OpenFile`, and shared `NodeInfo`. It is created from `CryFile::into_open` and `CryDir::create_and_open_file`.

## Risks and edge cases
Large reads allocate the full requested size before knowing available data. `data.len() > 0` and `size > 0` control timestamp behavior, so zero-length IO intentionally avoids timestamp updates. `flush` doing fsync may be more expensive than expected. Casting failures are logged and sometimes remapped to `UnknownError`, losing corruption detail.

## Test signals
Expected signals include read/write round trips, short reads, zero-length IO timestamp behavior, fsync datasync vs full behavior, flush-on-close behavior, truncate through setattr, and corrupted file blob type handling.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/open_file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/symlink.rs -->
# sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/symlink.rs

## Purpose
Implements `CrySymlink`, the RustFS symlink adapter for converting back to a node and reading a symlink target from a `SymlinkBlob`.

## Important APIs, types, and functions
- `CrySymlink::new` stores a borrowed blobstore guard and shared `NodeInfo`.
- `load_blob` loads the symlink blob by id.
- `blob_as_symlink_mut` validates the blob type and maps mismatches to `CorruptedFilesystem`.
- The `Symlink` trait impl provides `into_node` and `target`.

## Control flow
`target` updates parent access timestamp according to policy while it loads the symlink blob, locks it, casts it to `SymlinkBlob`, and awaits `target()`. Unparseable target data becomes a corruption error.

## State and persistence behavior
The symlink target is persisted inside the symlink blob. Atime is persisted in the parent directory entry when policy permits. `CrySymlink` itself holds only runtime guards.

## Dependencies and integration points
Uses `ConcurrentFsBlobStore`, `FsBlob`, `SymlinkBlob`, RustFS `Symlink`, `CryNode`, and `NodeInfo` timestamp helpers.

## Risks and edge cases
The adapter reloads the blob for every target read and does not cache target text. Target errors are treated as corrupted filesystem. Like the file and directory adapters, correctness depends on parent entry type matching the actual blob type.

## Test signals
Coverage should assert symlink target round trips, atime updates on target reads, conversion back into `CryNode`, and corrupted type/target error handling.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/symlink.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/src/lib.rs -->
# sources/security-integrity/cryfs/crates/cryfs-filesystem/src/lib.rs

## Purpose
Defines the public root of the `cryfs-filesystem` crate and exposes the filesystem module.

## Important APIs, types, and functions
- Applies `#![forbid(unsafe_code)]`.
- Allows private rustdoc intra-doc links temporarily.
- Public module: `pub mod filesystem`.
- Calls `cryfs_version::assert_cargo_version_equals_git_version!()`.

## Control flow
There is no runtime control flow. The version macro expands at compile time and checks Cargo/git version consistency.

## State and persistence behavior
No runtime or persistent state is stored here.

## Dependencies and integration points
Integrates the crate with `cryfs-version` compile-time version policy and exposes `filesystem::CryDevice` through the nested module.

## Risks and edge cases
The TODO indicates the public API is not settled. Tight compile-time version checking can break builds if Cargo package version and git tags diverge.

## Test signals
The main signal is successful compilation under `forbid(unsafe_code)` and successful expansion of the version assertion macro.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/Cargo.toml -->
# sources/security-integrity/cryfs/crates/cryfs-runner/Cargo.toml

## Purpose
Cargo manifest for the `cryfs-runner` crate, which assembles mounting, daemonization, IPC, filesystem construction, and integration-test helper binary dependencies.

## Important APIs, types, and functions
- Package metadata inherits workspace authors, edition, rust-version, license, repository, readme, and version.
- Runtime dependencies include `cryfs-filesystem`, `cryfs-config`, `cryfs-rustfs` with `fuser`, blobstore/blockstore crates, CLI utilities, `interprocess`, `postcard`, `tokio`, `tokio-util`, `serde`, `libc`, `nix`, and `command-fds`.
- Dev dependencies add `nix` process/signal features and `tempfile`.
- Defines `cryfs-runner-test-background` binary at `src/bin/cryfs_runner_test_background.rs`.

## Control flow
The manifest controls feature wiring and test binary availability rather than runtime flow. The helper binary is always buildable for integration tests because `required-features = []`.

## State and persistence behavior
No direct state. Dependency choices determine runtime persistence through block/blob/filesystem crates and daemon IPC serialization with postcard.

## Dependencies and integration points
This crate is the junction between the filesystem crate, RustFS/FUSE backend, config/local-state handling, blockstore integrity callbacks, IPC pipes, and logging configuration.

## Risks and edge cases
`cryfs-rustfs` disables default features and enables `fuser`, so backend behavior depends on that feature set. `command-fds` relies on pre-exec fd mapping until a future stdlib fd API exists. Serialization compatibility depends on serde/postcard versions across parent and daemon binaries.

## Test signals
`cargo test -p cryfs-runner` should build the helper binary and integration tests. Dependency feature regressions usually surface as compile errors or missing `CARGO_BIN_EXE_cryfs-runner-test-background`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/src/background_process.rs -->
# sources/security-integrity/cryfs/crates/cryfs-runner/src/background_process.rs

## Purpose
Implements parent-side background daemon control and daemon-side RPC serving for bootstrap, status, and mount requests.

## Important APIs, types, and functions
- `BackgroundProcess::daemonize` starts the daemon, sends bootstrap logging config, and performs a status check.
- `mount_filesystem` sends a `MountRequest` and maps serialized mount errors back to `CliError`.
- RPC schema: `BootstrapConfig`, `Request::{Bootstrap, StatusCheckRequest, MountRequest}`, and `Response::{BootstrapAck, StatusCheckResponse, MountResponse}`.
- `background_main` creates the tokio runtime; `background_async_main` enforces bootstrap-first protocol and serves requests.
- `handle_bootstrap` is a testable receive/install/ack helper; `close_stdout_stderr` redirects fd 0/1/2 to `/dev/null`.

## Control flow
The parent starts IPC, sends `Bootstrap`, waits up to 10 seconds for `BootstrapAck`, then sends `StatusCheckRequest`. The daemon requires `Bootstrap` as the first typed request, initializes logging through the callback, and only then acks. On mount, the daemon calls the runner; success callback sends `MountResponse(Ok(()))` immediately after mount succeeds and then detaches stdio while the mount loop continues until unmount.

## State and persistence behavior
State is in the live `RpcClient`/`RpcServer` pipes and serialized `MountArgs`. No disk state is created here except whatever logging destination the bootstrap config selects. Mounting persists through lower block/blob/filesystem layers.

## Dependencies and integration points
Uses `clap-logflag`, `cryfs_cli_utils::CliError`, serde, `anyhow`, runner mount logic, and the IPC spawn/rpc layer. `Mounter::run_in_background` wraps this type.

## Risks and edge cases
Unexpected response variants panic. Once a mount succeeds, the parent receives success before the filesystem later unmounts, so later mount errors may only be logged. Duplicate bootstrap is acked but ignored. If bootstrap logging fails, no ack is sent by design; parent sees a timeout/EOF-style startup failure.

## Test signals
In-file tests cover postcard serialization of logging config, bootstrap round trip over real pipes, no ack when logging install fails, and rejection of non-bootstrap first requests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/src/background_process.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/src/bin/cryfs_runner_test_background.rs -->
# sources/security-integrity/cryfs/crates/cryfs-runner/src/bin/cryfs_runner_test_background.rs

## Purpose
Test-only helper daemon spawned by `start_background_process_with_exe` integration tests. It rebuilds an `RpcServer` from inherited fds 3 and 4 and executes behavior selected by `CRYFS_TEST_BEHAVIOR`.

## Important APIs, types, and functions
- Local `Request { request: i32 }` and `Response { response: i32 }` match integration tests.
- `rpc_server_from_inherited_fds` reconstructs the typed server.
- Behaviors include `echo`, `panic_after_request`, `panic_before_request`, `exit_after_request`, `exit_before_request`, `write_to_fd_then_idle`, and `sentinel_loop`.

## Control flow
Normal `echo` loops receiving requests and responding with `request + 1` until EOF. Panic/exit modes simulate daemon failures before or after receiving a request. FD-isolation mode attempts to write to a provided fd, writes its PID, calls `setsid`, and idles. Sentinel mode drops RPC, writes PID, calls `setsid`, and repeatedly updates a sentinel file.

## State and persistence behavior
The helper writes temporary PID and sentinel files for tests. It does not mount filesystems or persist CryFS data.

## Dependencies and integration points
Used by runner integration tests through `CARGO_BIN_EXE_cryfs-runner-test-background`. It exercises inherited fd reconstruction, EOF behavior, `setsid`, and daemon cleanup logic.

## Risks and edge cases
Environment variable usage in tests must be isolated because process env is global. Infinite idle loops require external cleanup guards in tests. The helper intentionally bypasses the production build-id handshake.

## Test signals
Integration tests use this binary to verify echo round trips, EOF on daemon death, detached survival after parent exit, and absence of leaked parent fds.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/src/bin/cryfs_runner_test_background.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/src/ipc/mod.rs -->
# sources/security-integrity/cryfs/crates/cryfs-runner/src/ipc/mod.rs

## Purpose
Defines the internal IPC module composition and re-exports the types/functions needed by runner and integration tests.

## Important APIs, types, and functions
- Private modules: `pipe`, `rpc`, `spawn`.
- Public re-exports: `RpcClient`, `RpcConnection`, `RpcServer`, `rpc_server_from_inherited_fds`, `send_handshake`, `start_background_process`, and `start_background_process_with_exe`.

## Control flow
No runtime logic. It is a namespace boundary that keeps low-level pipe details private while exposing typed RPC and spawn entry points.

## State and persistence behavior
No state is stored here.

## Dependencies and integration points
Used by `background_process.rs`, `lib.rs`, the test helper binary, and runner integration tests.

## Risks and edge cases
Re-exporting hidden test APIs from `lib.rs` means changes here can break integration tests. Keeping `pipe` private helps prevent callers from bypassing spawn/handshake invariants.

## Test signals
Compile-time linkage of daemon tests and background process code is the relevant signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/src/ipc/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/src/ipc/pipe.rs -->
# sources/security-integrity/cryfs/crates/cryfs-runner/src/ipc/pipe.rs

## Purpose
Provides length-prefixed, postcard-encoded unnamed-pipe IPC primitives with CLOEXEC setup, bounded message size, raw handshake support, and timeout reads.

## Important APIs, types, and functions
- `pipe<T>` creates a typed `Sender<T>`/`Receiver<T>` pair and sets `FD_CLOEXEC` on both ends.
- `Sender::send`, `send_raw`, and `write_length_prefixed` serialize or send raw bytes with a 1 MiB cap.
- `Receiver::recv`, `recv_timeout`, and `recv_raw_timeout` read length-prefixed payloads, optionally with nonblocking timeout.
- `read_exact_with_timeout` uses `poll` to avoid busy-waiting.

## Control flow
Pipe creation panics if a tokio runtime is already active, enforcing single-threaded creation to reduce fork/CLOEXEC races on platforms without atomic `pipe2(O_CLOEXEC)`. Sending writes a little-endian u32 length and payload. Timeout receive sets nonblocking mode, reads the length and payload before a deadline, and reports EOF, timeout, oversize, poll, or decode errors.

## State and persistence behavior
Only OS pipe descriptors and transient serialized bytes are managed. `into_owned_fd` and `from_owned_fd` transfer fd ownership across spawn boundaries.

## Dependencies and integration points
Depends on `interprocess` unnamed pipes, `postcard`, serde, `nix::poll`, `libc` fcntl, and tokio runtime detection. `rpc.rs` builds typed request/response channels on top of it; `spawn.rs` maps descriptors into daemon children.

## Risks and edge cases
CLOEXEC is set after pipe creation, so a narrow race remains if another thread forks before fcntl; the runtime guard is a usage invariant, not a kernel guarantee. Timeout conversion caps poll waits at `u16::MAX` ms per poll. Typed and raw receive share the same wire framing, so ordering must be respected by handshake code.

## Test signals
In-file tests cover CLOEXEC flags, dropped endpoints, blocking receive, timeout receive, zero/short/large/multiple messages, partial length/payload EOF, raw payload round trips, max-size rejection, little-endian framing, and typed-vs-raw byte behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/src/ipc/pipe.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/src/ipc/rpc.rs -->
# sources/security-integrity/cryfs/crates/cryfs-runner/src/ipc/rpc.rs

## Purpose
Builds typed request/response RPC abstractions over two unidirectional `pipe.rs` channels.

## Important APIs, types, and functions
- `RpcConnection::new_pipe` creates request and response pipes.
- `into_client_and_child_fds` keeps parent-side client ends and returns child fd ownership for spawn mapping.
- Test-only `into_server_and_client` splits an in-process server/client pair.
- `RpcServer::from_raw_fds`, `next_request`, `send_response`, and `send_raw_handshake`.
- `RpcClient::send_request`, `recv_response`, and raw handshake receive.

## Control flow
Connection setup creates two typed pipes. Parent/child spawn conversion assigns request sender plus response receiver to the client and request receiver plus response sender to the child. The daemon reconstructs `RpcServer` from fds 3 and 4. Raw handshakes bypass postcard but still use pipe framing and must happen before typed RPC.

## State and persistence behavior
State is owned pipe endpoints. There is no disk persistence.

## Dependencies and integration points
Uses `Sender`/`Receiver` from `pipe.rs`, serde bounds, `OwnedFd`/`RawFd`, and `anyhow`. It is the core transport for background daemon bootstrap and mount RPC.

## Risks and edge cases
`RpcServer::from_raw_fds` is unsafe because fd numbers must be valid, owned pipe ends and must not be reconstructed twice. Schema mismatches between parent and daemon are mitigated by spawn's build-id handshake before typed deserialization.

## Test signals
The unit test verifies a request/response round trip over a local connection. Broader daemon tests validate fd mapping, EOF, and handshakes.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/src/ipc/rpc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/src/ipc/spawn.rs -->
# sources/security-integrity/cryfs/crates/cryfs-runner/src/ipc/spawn.rs

## Purpose
Spawns the background daemon via fork+exec, maps RPC fds into conventional child slots, validates daemon identity with a build-id handshake, and reconstructs daemon-side RPC from inherited fds.

## Important APIs, types, and functions
- Constants define child fds 3/4, hidden `--daemon`, and 10-second handshake timeout.
- `daemon_exe_path` uses `/proc/self/exe` on Linux and `current_exe` elsewhere.
- `start_background_process` starts the production daemon and validates handshake.
- `start_background_process_with_exe` starts a test helper without the build-id handshake.
- `start_background_process_inner` performs fd mapping through `command-fds`.
- `validate_handshake_and_build_client`, `send_handshake`, and `rpc_server_from_inherited_fds` enforce identity and fd sanity.

## Control flow
Production spawn rejects running under an active tokio runtime, resolves the executable, creates RPC pipes, maps child request-recv and response-send fds to 3/4, spawns, then waits for a raw daemon-to-parent build-id handshake before returning the typed client. Daemon-side startup first validates fds are pipes and later sends its build id. Test helper spawn uses the same fd mapping but skips the production handshake.

## State and persistence behavior
State is process identity, environment, argv, and inherited pipe descriptors. No persistent disk state is written here.

## Dependencies and integration points
Uses `command-fds`, Unix `CommandExt::arg0`, `libc::fstat`, `RpcConnection`, `RpcClient`, `RpcServer`, `crate::build_id`, and serde. Production entry is called by `BackgroundProcess::daemonize`; daemon entry is called by `run_as_background_daemon`.

## Risks and edge cases
The pre-exec fd mapping path inherits known fork-after-multithread hazards; the runtime guard reduces risk. Non-Linux `current_exe` can re-resolve a replaced binary, so the build-id handshake covers but cannot pin the exact inode. `start_background_process_with_exe` deliberately skips handshake for tests and must not be used as production identity validation.

## Test signals
Unit tests accept matching build ids and reject mismatched, non-UTF8, EOF-before-handshake, and hung-without-handshake cases. Integration tests cover fd isolation and daemon survival after parent exit.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/src/ipc/spawn.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/src/lib.rs -->
# sources/security-integrity/cryfs/crates/cryfs-runner/src/lib.rs

## Purpose
Public root of the `cryfs-runner` crate, exporting mounting APIs, hidden integration-test IPC APIs, daemon entry point, build identity, and tokio runtime initialization.

## Important APIs, types, and functions
- Re-exports `AtimeUpdateBehavior`, `Mounter`, `CreateOrLoad`, `FuseOption`, `MountArgs`, and `make_device`.
- Hidden exports expose `RpcClient`, `RpcServer`, spawn helpers, and inherited-fd reconstruction for integration tests.
- `BUILD_ID` and `build_id` derive a compile-time `VersionInfo`.
- `run_as_background_daemon` reconstructs server fds, calls `setsid`, sends handshake, and enters background main.
- `init_tokio` builds the multi-threaded runtime.

## Control flow
Production CLI dispatches to `run_as_background_daemon` for the hidden daemon flag. The daemon validates inherited fds, creates a new session, sends build-id bytes to the parent, then hands the server to `background_process::background_main`, which initializes tokio.

## State and persistence behavior
No filesystem persistence is performed here. Runtime state includes inherited fds, process session, build id, and the tokio runtime. Version assertion is compile-time.

## Dependencies and integration points
Connects `background_process`, `ipc`, `mounter`, `runner`, `unmount_trigger`, `cryfs-version`, `libc::setsid`, and `cryfs_cli_utils`-initialized CLI dispatch.

## Risks and edge cases
`setsid` failure is fatal because daemon detachment depends on it. Startup errors exit with distinct codes. Hidden IPC exports are not stable API but are visible to tests. `init_tokio` unwraps runtime construction.

## Test signals
Integration tests indirectly validate `setsid`, fd reconstruction, build-id handshake compatibility, and hidden IPC exports. Compile-time version assertions also guard package/git consistency.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/src/mounter.rs -->
# sources/security-integrity/cryfs/crates/cryfs-runner/src/mounter.rs

## Purpose
Provides a small strategy enum for running mounts in foreground or through a background daemon.

## Important APIs, types, and functions
- `Mounter::{MountInForeground, MountInBackgroud}` selects execution mode.
- `run_in_foreground` creates foreground mode.
- `run_in_background` daemonizes and bootstraps logging through `BackgroundProcess`.
- `mount_filesystem` delegates to foreground runner or background RPC.

## Control flow
Foreground mode awaits `runner::mount_filesystem`, which blocks until unmount. Background mode sends mount args over RPC, returns after successful mount response, then calls the success callback locally.

## State and persistence behavior
Foreground holds no daemon state. Background stores a `BackgroundProcess` RPC client. Persistence is delegated to runner/filesystem layers.

## Dependencies and integration points
Integrates CLI logging config, `MountArgs`, `BackgroundProcess`, and `runner::mount_filesystem`. It is the high-level API used by the CLI to choose daemon mode.

## Risks and edge cases
The enum variant name contains a typo (`MountInBackgroud`), which is harmless but public within the crate. In background mode, the callback is invoked after RPC mount success, not after the daemon eventually unmounts.

## Test signals
Signals should cover foreground blocking semantics, background early-return semantics, daemon bootstrap failure propagation, and callback ordering.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/src/mounter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/src/runner.rs -->
# sources/security-integrity/cryfs/crates/cryfs-runner/src/runner.rs

## Purpose
Assembles blockstore, blobstore, CryFS device, unmount triggers, and RustFS/FUSE backend into the actual mount lifecycle.

## Important APIs, types, and functions
- `Backend` aliases the fuser RustFS backend.
- `CreateOrLoad`, `MountArgs`, and `FuseOption` are serialized mount configuration types.
- `mount_filesystem` sets integrity behavior, blockstore stack, unmount trigger, device, and backend mount.
- `FilesystemRunner` implements `BlockstoreCallback`.
- `make_device` parses root blob id, creates or loads `CryDevice`, and runs `sanity_check`.

## Control flow
`mount_filesystem` derives missing-block integrity policy, installs an integrity-violation callback that triggers unmount, then runs `setup_blockstore_stack` with a callback. The callback builds `BlobStoreOnBlocks`, creates/loads and validates a `CryDevice`, optionally starts idle-unmount polling, converts atime and FUSE ACL options into RustFS config, mounts the backend, and waits for unmount. After return, trigger reason determines whether success, idle unmount success, or integrity violation error is reported.

## State and persistence behavior
Persistent state includes on-disk blocks under the vault dir, local-state locking/integrity metadata, blobstore content, root directory blob, and filesystem mutations performed through the mounted device. Runtime state includes `UnmountTrigger`, last access timestamp, mount options, and client id.

## Dependencies and integration points
Uses `OnDiskBlockStore`, `LockingBlockStore`, `BlobStoreOnBlocks`, `CryConfig`, `LocalStateDir`, `CryDevice`, `cryfs_rustfs` backend/config/session ACL, CLI error mapping, and `UnmountTrigger`.

## Risks and edge cases
`make_device` drops the blobstore on invalid root blob id and drops the device after failed sanity check. `logical_block_size` conversion in lower device statfs can unwrap if oversized. ACL mapping collapses allow-other/root into a single fuser `SessionACL`. Integrity violations asynchronously trigger unmount, so error reporting depends on trigger reason surviving until mount returns.

## Test signals
There is a TODO for tests. Expected coverage includes create vs load, invalid root id, failed sanity check cleanup, mount option mapping, allow-other/root precedence, idle unmount, integrity violation unmount, and missing-block policy behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/src/runner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/src/unmount_trigger.rs -->
# sources/security-integrity/cryfs/crates/cryfs-runner/src/unmount_trigger.rs

## Purpose
Defines a clonable cancellation trigger used to stop the mounted filesystem because of idle timeout or integrity violation.

## Important APIs, types, and functions
- `TriggerReason::{UnmountIdle, IntegrityViolation}` records why cancellation happened.
- `UnmountTrigger::new`, `trigger_after_idle_timeout`, `trigger_now`, `waiter`, and `trigger_reason`.
- Internally uses `tokio_util::sync::CancellationToken` and `Arc<Mutex<Option<TriggerReason>>>`.

## Control flow
Idle timeout spawns a tokio task that polls `last_filesystem_access_time.elapsed()` once per second. If the threshold is exceeded, it calls `trigger_now`. `trigger_now` stores the reason under mutex before cancelling the token, ensuring mount shutdown code can read the reason after cancellation.

## State and persistence behavior
All state is runtime-only: cancellation token, trigger reason, and access timestamp reference. No disk persistence.

## Dependencies and integration points
Used by `runner.rs` to pass a waiter into `Backend::mount` and to convert post-unmount reason into success or `CliErrorKind::IntegrityViolation`.

## Risks and edge cases
The idle polling task runs until it triggers; there is no explicit cancellation if mount ends for another reason. `Mutex` poisoning would panic on unwrap. Time is based on `AtomicInstant` relaxed loads and wall-clock-ish elapsed behavior.

## Test signals
The file has a TODO for tests. Needed tests include trigger reason ordering, idle timeout firing after access gap, no early idle fire after access update, and integrity violation reason propagation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/src/unmount_trigger.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/tests/daemon_child_lifecycle.rs -->
# sources/security-integrity/cryfs/crates/cryfs-runner/tests/daemon_child_lifecycle.rs

## Purpose
Integration tests for daemon child lifecycle behavior when the helper daemon echoes, panics, or exits before/after requests.

## Important APIs, types, and functions
- Defines matching `Request`/`Response` structs.
- `helper_exe` locates `cryfs-runner-test-background`.
- `spawn_daemon` passes `CRYFS_TEST_BEHAVIOR` and calls `start_background_process_with_exe`.
- Tests cover echo, panic after request, panic before request, exit after request, and exit before request.

## Control flow
Each test spawns a clean helper process through the same fork+exec/fd mapping path. Echo sends one request and expects incremented response. Failure modes either send a request then read or read immediately; each expects `recv_response` to fail with `Sender closed the pipe`.

## State and persistence behavior
No persistent state except helper process lifetime. Environment variables configure behavior for the spawned child.

## Dependencies and integration points
Exercises `cryfs_runner::start_background_process_with_exe`, `RpcClient`, postcard serialization, inherited fds, EOF propagation, and the helper binary.

## Risks and edge cases
The test intentionally avoids in-process fork of libtest threads, addressing previous fd-inheritance flakes. It depends on exact error string from pipe EOF handling.

## Test signals
Signals are successful request/response for echo and EOF errors for daemon panic/exit before or after a request.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/tests/daemon_child_lifecycle.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/tests/daemon_roundtrip.rs -->
# sources/security-integrity/cryfs/crates/cryfs-runner/tests/daemon_roundtrip.rs

## Purpose
End-to-end integration test for repeated RPC request/response exchanges with the fork+exec helper daemon.

## Important APIs, types, and functions
- Defines local `Request` and `Response` payloads.
- Uses `CARGO_BIN_EXE_cryfs-runner-test-background` and `start_background_process_with_exe`.
- Single test `roundtrip_many_requests`.

## Control flow
The test starts the helper in `echo` mode, sends ten sequential requests, waits up to five seconds for each response, and asserts each response increments the request value. Dropping the client at the end should close pipes and let the helper exit cleanly.

## State and persistence behavior
No disk persistence. State is the live daemon process and pipe streams.

## Dependencies and integration points
Exercises spawn, fd mapping, typed RPC, postcard encoding, and EOF-on-client-drop behavior at process boundary.

## Risks and edge cases
Payload sizes are simple `i32`; large payload behavior is covered by pipe unit tests instead. The test does not explicitly wait/reap the helper; it relies on helper EOF handling after client drop.

## Test signals
Ten successful sequential responses and no hang on client drop indicate the daemon loop and pipe framing remain healthy.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/tests/daemon_roundtrip.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/tests/daemon_survives_parent_exit.rs -->
# sources/security-integrity/cryfs/crates/cryfs-runner/tests/daemon_survives_parent_exit.rs

## Purpose
Regression test proving a spawned daemon survives after the parent CLI-like process exits and has moved into a separate session with `setsid`.

## Important APIs, types, and functions
- Uses `fork`, `waitpid`, `getsid`, and signal cleanup through `nix`.
- `DaemonGuard` kills the daemon with SIGTERM/SIGKILL on drop.
- The helper runs `sentinel_loop`, writing PID and updating a sentinel file.

## Control flow
The test forks a sub-process that starts the helper daemon and exits immediately. The parent reaps that sub-process, waits for the daemon PID file, installs cleanup guard, compares daemon session id to test session id, waits for the sentinel file, and verifies its contents change after the parent exited.

## State and persistence behavior
Temporary PID and sentinel files are created under a temp directory. The daemon writes a tick counter every 50 ms until killed.

## Dependencies and integration points
Validates `start_background_process_with_exe` plus helper-side `setsid` behavior used to model production daemon detachment.

## Risks and edge cases
The test uses global environment variables, marked safe by being a single-test integration binary. It polls for parseable PID content to avoid races with partial file creation. Cleanup must handle init-parented detached processes.

## Test signals
Signals are clean sub-process exit, parseable daemon PID, distinct session ids, sentinel creation, and sentinel content changes within deadlines.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/tests/daemon_survives_parent_exit.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/tests/spawn_fd_isolation.rs -->
# sources/security-integrity/cryfs/crates/cryfs-runner/tests/spawn_fd_isolation.rs

## Purpose
Regression test ensuring unrelated parent file descriptors do not leak into the daemon across fork+exec.

## Important APIs, types, and functions
- Creates a sentinel pipe and sets `FD_CLOEXEC` on both ends.
- Passes the sentinel writer fd number through `CRYFS_TEST_LEAK_FD`.
- Spawns helper behavior `write_to_fd_then_idle`.
- `DaemonGuard` kills and reaps the direct child daemon.

## Control flow
After spawning the helper, the parent drops its sentinel writer. The helper attempts to write to the fd number before publishing its PID. The parent waits for the PID, gives the helper time to run, then performs a nonblocking read on the sentinel receiver. EOF is expected; data or WouldBlock means a writer leaked into the daemon.

## State and persistence behavior
Temporary PID file only. The sentinel pipe is transient OS state.

## Dependencies and integration points
Exercises `start_background_process_with_exe`, `FD_CLOEXEC`, fd mapping, helper daemon behavior, `interprocess` pipes, and libc fcntl/waitpid/kill.

## Risks and edge cases
The sentinel pipe is intentionally marked CLOEXEC to isolate spawn behavior. The helper idles forever, so cleanup guard correctness is required. Timing includes a short sleep after PID publication to allow the write attempt.

## Test signals
EOF on the sentinel receiver is the core signal. Any bytes or open-writer WouldBlock failure indicates fd leakage.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-runner/tests/spawn_fd_isolation.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-version/Cargo.toml -->
# sources/security-integrity/cryfs/crates/cryfs-version/Cargo.toml

## Purpose
Cargo manifest for the `cryfs-version` crate, which provides semantic version types, git metadata integration, and compile-time version consistency macros.

## Important APIs, types, and functions
- Package metadata inherits workspace settings and version.
- Dependencies: `git2version`, `konst`, serde derive, and `derive_more`.
- Build dependency enables `git2version` build support.
- Dev dependencies include `predicates`, `serde_json`, and local `tempproject`.

## Control flow
The manifest enables build-script generated git metadata and compile-time const parsing/comparison support through `konst`.

## State and persistence behavior
No direct runtime state. Build output from `git2version` becomes compile-time metadata for the crate.

## Dependencies and integration points
Consumed by other CryFS crates through version macros. Dev dependencies support macro/build integration and serialization tests.

## Risks and edge cases
The crate's own version comes from workspace version; mismatches with git tags can fail dependent crate builds through assertions. `git2version` behavior determines availability and exact shape of git metadata.

## Test signals
`cargo test -p cryfs-version` should validate parsing, serde, display, ownership conversions, and version macro behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-version/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-version/build.rs -->
# sources/security-integrity/cryfs/crates/cryfs-version/build.rs

## Purpose
Build script that initializes `git2version` proxy build metadata for the version crate.

## Important APIs, types, and functions
- `main` calls `git2version::init_proxy_build!()`.

## Control flow
At build time, the macro emits or configures environment/proxy metadata used by `git2version::init_proxy_lib!()` in the library.

## State and persistence behavior
The script contributes compile-time build metadata rather than runtime state. It may cause Cargo rebuild behavior through generated environment/output controlled by `git2version`.

## Dependencies and integration points
Requires the build-dependency `git2version` with its `build` feature. Library macros rely on the metadata initialized here.

## Risks and edge cases
If git metadata is unavailable or the build script does not run as expected, downstream version info may lack git details or version assertions may behave differently.

## Test signals
Build success and version macro tests are the primary signal; there are no direct unit tests for the build script.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-version/build.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-version/src/lib.rs -->
# sources/security-integrity/cryfs/crates/cryfs-version/src/lib.rs

## Purpose
Public API root for CryFS version management: exports `Version`, `VersionInfo`, git metadata setup, and macros for package version and Cargo/git consistency.

## Important APIs, types, and functions
- Crate attributes forbid unsafe code and deny missing docs.
- `git2version::init_proxy_lib!()` imports generated git metadata.
- Exports `Version` and `VersionInfo`.
- `package_version!` returns const `VersionInfo` after asserting Cargo/git consistency.
- `cargo_version!` builds a const `Version<&'static str>` from `CARGO_PKG_VERSION_*`.
- `assert_cargo_version_equals_git_version!` creates a module-level const assertion.

## Control flow
Macros expand in the caller's crate context for Cargo package version, while `GITINFO` comes from the version crate's generated metadata. `package_version!` first invokes the assertion macro, then constructs `VersionInfo::new(cargo_version!(), GITINFO)`.

## State and persistence behavior
All state is compile-time constants and generated git metadata. No runtime persistence.

## Dependencies and integration points
Used by `cryfs-filesystem` and `cryfs-runner` to enforce version consistency and expose build identity. Depends on `version.rs`, `version_info.rs`, and `git2version`.

## Risks and edge cases
Macros use `env!`, so malformed Cargo version env vars cause compile-time panic. Git tag parsing and consistency are const-time; mismatches break builds. The docs state package version includes git metadata, but this depends on `GITINFO` availability.

## Test signals
Downstream crates compiling with `assert_cargo_version_equals_git_version!` and any macro-specific tests in the crate validate expansion and consistency behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-version/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-version/src/version.rs -->
# sources/security-integrity/cryfs/crates/cryfs-version/src/version.rs

## Purpose
Defines a generic semantic `Version<P>` type with parsing, const parsing, display/debug formatting, ordering, serde, and borrowed/owned prerelease conversions.

## Important APIs, types, and functions
- `Version<P>` stores `major`, `minor`, `patch`, and optional `prerelease`.
- `Display`/`Debug` emit `major.minor.patch[-prerelease]`.
- `PartialEq`, `Eq`, `Ord`, and `PartialOrd` compare major/minor/patch first, then prerelease, with prerelease less than stable.
- `Version<&str>::parse`, `parse_const`, `eq_const`, `to_owned`, and `into_owned`.
- `Version<String>::to_borrowed`.
- `ParseVersionError` wraps invalid numeric parse errors with the original string.

## Control flow
Parsing splits once on `-`, then up to two `.` separators, defaulting missing minor or patch to zero. Runtime parsing uses standard `str::parse`; const parsing uses `konst::string` and `u32::from_str_radix`. Comparison exits early on numeric differences and then compares prerelease strings lexicographically or stable/prerelease presence.

## State and persistence behavior
The type is value-only and serde-serializable. It persists as JSON fields when serialized and as display strings when formatted.

## Dependencies and integration points
Used by `VersionInfo`, crate macros, and downstream build identifiers. Depends on serde, `derive_more` for error display, `konst` for const parsing, and standard borrow/comparison traits.

## Risks and edge cases
Parsing is permissive for shortened versions and does not validate full SemVer prerelease grammar beyond numeric components. `split_once('-')` treats everything after the first dash as prerelease. Lexicographic prerelease ordering is simpler than full SemVer identifier ordering. `parse_const` returns only `ParseIntError`, losing original string context.

## Test signals
In-file tests cover runtime and const parsing, display/debug, equality/order across borrowed and owned forms, shortened-version equivalence, prerelease ordering, serde JSON round trips/format, and ownership conversions.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-version/src/version.rs -->
