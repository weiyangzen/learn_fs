# Group Research: group_1807_virtiofsd_sources_virtualization_virtiofsd_gitlab_ci_yml_sources_vi_56a26ebb7e2f

Scope: subset A from `Docs/research_subset_a.md`, covering the listed `sources/virtualization/virtiofsd` files. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/.gitlab-ci.yml -->
# File Research: sources/virtualization/virtiofsd/.gitlab-ci.yml

## Scope

GitLab CI configuration for virtiofsd. It defines merge-request and main-branch workflows for linting, formatting, static musl builds/tests, documentation generation, release artifact publication, and GitLab Pages documentation publishing.

## Behavior

- Uses `rust:alpine` as the base image.
- Runs `clippy` with `-Dwarnings`, explicitly allowing `clippy::manual-c-str-literals` because the crate uses Rust 2018.
- Runs `cargo fmt --check`.
- Builds and tests with static musl target `x86_64-unknown-linux-musl`, linking `libseccomp` and `libcap-ng` statically.
- Generates private-item docs with `cargo doc --no-deps --all-features --document-private-items`.
- Publishes optimized static `virtiofsd` binaries only on `main@virtio-fs/virtiofsd`.
- Publishes documentation artifacts through GitLab Pages with redirects to `virtiofsd` docs.

## Dependencies And Risks

- Alpine packages include `musl-dev`, `libcap-ng-static`, and `libseccomp-static`.
- Release and pages jobs are branch-restricted to avoid publishing artifacts from merge requests.
- The static build environment is part of the project’s portability and distribution contract.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/.gitlab-ci.yml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/50-virtiofsd.json -->
# File Research: sources/virtualization/virtiofsd/50-virtiofsd.json

## Scope

QEMU/vhost-user backend metadata file describing the virtiofsd executable.

## Contents

- Declares description `virtiofsd vhost-user-fs`.
- Declares backend type `fs`.
- Points QEMU tooling to `/usr/libexec/virtiofsd`.
- Advertises `migrate-precopy` and `separate-options`.

## Role

This file is packaging/runtime integration metadata, not executable logic. It aligns with `main.rs --print-capabilities`, which prints the same capability feature names.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/50-virtiofsd.json -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/Cargo.toml -->
# File Research: sources/virtualization/virtiofsd/Cargo.toml

## Scope

Rust package manifest for the virtiofsd crate and binary.

## Package And Features

- Package name `virtiofsd`, version `1.13.3`, Rust edition 2018.
- License is `Apache-2.0 AND BSD-3-Clause`.
- Default feature is `seccomp`.
- `seccomp` exposes optional `libseccomp-sys`.
- `xen` feature switches vhost/vm-memory dependencies to Xen support and explicitly disables normal QEMU/KVM support.
- The `virtiofsd` binary requires `seccomp`.

## Dependencies

Key dependencies include `vhost-user-backend`, `vhost`, `virtio-queue`, `virtio-bindings`, `vm-memory`, `vmm-sys-util`, `capng`, `libc`, `clap`, `serde`, `postcard`, `futures`, `syslog`, and `env_logger`.

## Build Behavior

Release builds enable LTO. `.gitlab-ci.yml` is excluded from the published crate.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/Cargo.toml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/rustfmt.toml -->
# File Research: sources/virtualization/virtiofsd/rustfmt.toml

## Scope

Rust formatting configuration.

## Settings

- `imports_granularity = "Module"` groups imports at module granularity.
- `edition = "2018"` matches the crate manifest.

## Role

Supports the CI `cargo fmt --check` job and keeps import formatting stable across contributors.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/rustfmt.toml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/descriptor_utils.rs -->
# File Research: sources/virtualization/virtiofsd/src/descriptor_utils.rs

## Scope

Utilities that expose virtqueue descriptor chains as high-level `Read` and `Write` streams over guest memory. This is the bridge between vhost-user virtio queue buffers and Rust/FUSE request handling.

## APIs Covered

- `Error` and `Result` for descriptor memory, overflow, split, and I/O failures.
- Internal `DescriptorChainConsumer` over `VecDeque<VolatileSlice>`.
- `Reader` for device-readable descriptors.
- `Writer` for device-writable descriptors.
- `DescriptorType` test helper enum.

## Behavior

- `Reader::new()` collects readable descriptors until the first writable descriptor, resolving guest addresses into volatile memory slices.
- `Writer::new()` collects writable descriptors.
- Both constructors check combined descriptor lengths for `usize` overflow.
- `read_obj()` and `write_obj()` move `ByteValued` protocol structs across descriptor memory.
- `write_to_file_at()` and `read_from_file_at()` use volatile vectored I/O for zero-copy file transfer.
- `split_at()` divides a reader/writer at byte offsets, preserving descriptor boundaries or splitting a volatile slice.
- `Writer` marks guest-memory dirty bitmap ranges after writes.

## Tests And Invariants

Tests cover simple read/write chains, incompatible descriptor types, shared readable/writable chains, object values split byte-by-byte across descriptors, EOF behavior, split edge cases, out-of-bounds split errors, and short full-buffer reads/writes. The main invariant is that descriptor consumption only advances after the closure succeeds.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/descriptor_utils.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/file_traits.rs -->
# File Research: sources/virtualization/virtiofsd/src/file_traits.rs

## Scope

Traits for file sizing and volatile vectored I/O against `std::fs::File`.

## APIs Covered

- `FileSetLen`, implemented by `File`, wraps `set_len()` / `ftruncate`-style behavior.
- `FileReadWriteAtVolatile<B>` defines `read_vectored_at_volatile()` and `write_vectored_at_volatile()`.
- Blanket reference implementation delegates through `&T`.
- `volatile_impl!(File)` implements volatile vectored I/O for `File`.

## Behavior

- Converts `VolatileSlice` arrays into `libc::iovec` arrays.
- Uses `oslib::readv_at()` / `oslib::writev_at()` with optional per-call flags.
- Maintains pointer guards while syscalls operate, preserving guest-memory pointer validity.
- Marks dirty bitmap ranges for bytes read into guest memory.

## Risks And Invariants

- Offset conversion uses `try_into().unwrap()`, so callers must pass offsets representable as syscall offsets.
- Correct dirty bitmap marking matters for migration/shared memory tracking.
- Safety relies on `VolatileSlice` bounds and pointer guards staying alive for the syscall duration.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/file_traits.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/filesystem.rs -->
# File Research: sources/virtualization/virtiofsd/src/filesystem.rs

## Scope

Transport-facing filesystem trait and shared request/response types. This file defines the contract between the FUSE/vhost-user server and concrete filesystem implementations such as passthrough.

## APIs Covered

- `Entry`, `DirEntry`, `GetxattrReply`, `ListxattrReply`.
- `ZeroCopyReader` and `ZeroCopyWriter`.
- Request context: `Context`, `Extensions`, `SecContext`.
- `DirectoryIterator`.
- Main `FileSystem` trait with FUSE operations.
- `SerializableFileSystem` migration trait.

## Behavior

- `Entry` converts to `fuse::EntryOut`, preserving inode, generation, attributes, and cache timeouts.
- `Context` maps FUSE header UID/GID/PID into guest-aware IDs.
- `FileSystem` defines lookup-count semantics and default behavior for most FUSE operations.
- Most unimplemented operations return `ENOSYS`, matching FUSE permanent-disable or success semantics where documented.
- `open()` and `opendir()` default to no handle and empty open options.
- `statfs()` defaults to libfuse-like minimal values.
- Read/write use zero-copy reader/writer traits rather than fixed intermediate buffers.
- `SerializableFileSystem` splits migration into optional preparation, serialization, and destination-side application.

## Invariants

Implementers must maintain inode lookup counts, handle valid kernel caching timeouts, honor open flags, xattr size semantics, directory offsets, writeback-cache caveats, and migration cancellation expectations.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/filesystem.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/fuse.rs -->
# File Research: sources/virtualization/virtiofsd/src/fuse.rs

## Scope

FUSE protocol ABI definitions for virtiofsd. It defines constants, flags, opcodes, request structs, response structs, notification structs, and extension records matching FUSE kernel protocol version 7.38.

## APIs Covered

- Protocol version constants: `KERNEL_VERSION`, `KERNEL_MINOR_VERSION`, `MIN_KERNEL_MINOR_VERSION`.
- FUSE root inode `ROOT_ID`.
- Bitflags: `SetattrValid`, `OpenOptions`, `FsOptions`, `IoctlFlags`, `SetxattrFlags`, `SetupmappingFlags`, notification flags.
- ABI structs: `Attr`, `Kstatfs`, `FileLock`, `EntryOut`, request input/output structs for lookup, getattr, setattr, open, read, write, xattr, init, ioctl, poll, fallocate, lseek, copy-file-range, DAX mappings, syncfs, and extensions.
- `Opcode` enum generated by `enum_value!`.
- `ExtType`, `Secctx`, `SecctxHeader`, and `SuppGroups`.

## Behavior

- `Attr::try_from_stat64()` and `try_with_flags()` convert host `stat64` into guest-visible FUSE attributes through UID/GID mapping closures.
- `Kstatfs` converts from `statvfs64`.
- All protocol structs are `#[repr(C)]`, POD-like, and marked `ByteValued` for descriptor serialization.
- Capability flags cover writeback cache, killpriv v2, POSIX ACLs, security context, supplementary groups, submounts, DAX, and idmapped mounts.

## Risks And Invariants

- Layout must remain ABI-compatible with Linux FUSE.
- `OpenOptions::STREAM` maps to `FOPEN_CACHE_DIR` in this file, which looks intentional only if mirroring existing upstream behavior; otherwise it is a subtle flag-risk.
- Version/capability negotiation elsewhere depends on these bit values being exact.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/fuse.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/idmap.rs -->
# File Research: sources/virtualization/virtiofsd/src/idmap.rs

## Scope

Command-line parsing and formatting for namespace UID/GID map ranges.

## APIs Covered

- `IdMapError`: invalid delimiter, incomplete map, invalid integer.
- `UidMap` and `GidMap` with `FromStr` and `Display`.
- Internal `parse_idmap()`.
- `IdMapSetUpPipeMessage` for setup synchronization.

## Behavior

- Accepts delimiter-wrapped forms such as `:0:100000:65536:`.
- The delimiter is taken from the final character and must be non-alphanumeric.
- Requires an initial matching delimiter and exactly three numeric fields.
- Displays maps back in colon-delimited form.

## Risks

Parsing is deliberately delimiter-flexible but strict about delimiter consistency and field count. These values feed namespace setup in the daemon CLI path.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/idmap.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/lib.rs -->
# File Research: sources/virtualization/virtiofsd/src/lib.rs

## Scope

Crate root for virtiofsd library modules and crate-wide protocol error type.

## Modules

Exports descriptor utilities, file traits, filesystem trait, FUSE ABI, ID maps, limits, macros, OS wrappers, passthrough filesystem, directory reading, sandbox, server, soft ID map, utilities, vhost-user backend, and optional seccomp support.

## Error Type

`Error` covers FUSE message decode/encode/flush failures, missing parameters/extensions, invalid C strings, invalid header length, and xattr size mismatch.

## Role

This file forms the library boundary used by `main.rs` and internal modules. Its error type is focused on protocol message handling rather than filesystem operation errors.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/lib.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/limits.rs -->
# File Research: sources/virtualization/virtiofsd/src/limits.rs

## Scope

Open-file limit management for the daemon.

## APIs Covered

- Internal `get_max_nofile()` reads `/proc/sys/fs/nr_open`.
- Internal `get_nofile_limits()` wraps `getrlimit(RLIMIT_NOFILE)`.
- Internal `setup_rlimit_nofile_to()` wraps `setrlimit`.
- Public `setup_rlimit_nofile()` chooses and applies the limit.

## Behavior

- Default target is `1_000_000`, capped by `/proc/sys/fs/nr_open`.
- User value `0` leaves the current soft limit unchanged.
- If current soft limit is already at least the default, no change is made.
- Explicit user-supplied values above `nr_open` fail.
- If automatic default raising fails, it tries to fall back to the hard limit and warns.

## Role

Used by `main.rs` before computing guest FD quotas. Correct behavior is important because virtiofsd can hold many inode/file descriptors.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/limits.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/macros.rs -->
# File Research: sources/virtualization/virtiofsd/src/macros.rs

## Scope

Small macro helper for enum-to-integer protocol values.

## API

- `enum_value!` defines a `#[repr(T)]` enum and implements `TryFrom<T>` by matching each declared variant’s numeric value.

## Role

Used by `fuse.rs` to define `Opcode` with exact FUSE request numbers while getting fallible conversion from raw wire opcode values.

## Invariants

Unknown integer values convert to `Err(())`, allowing protocol parsing to reject unsupported opcodes.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/macros.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/main.rs -->
# File Research: sources/virtualization/virtiofsd/src/main.rs

## Scope

Daemon entrypoint and command-line runtime setup for virtiofsd.

## APIs And Configuration

- Defines `Opt` with clap options for shared directory, socket/fd, socket group, thread pool, xattrs, POSIX ACLs, xattr maps, sandbox, readonly, seccomp, submount announcement, inode file-handle mode, cache policy, mmap/direct I/O/writeback, compatibility flags, logging, rlimits, namespace ID maps, soft ID translation, noatime handling, and migration behavior.
- Parses seccomp action, vhost-user tag, inode file-handle modes, legacy `-o` options, and capability modification strings.
- `run_generic_fs()` builds and runs `VhostUserDaemon`.

## Behavior

- `--print-capabilities` emits JSON with `migrate-precopy` and `separate-options`.
- Validates shared directory existence and migration option compatibility.
- Computes cache timeout and readdirplus policy from cache options.
- Creates or adopts a vhost-user listener, writes a socket pid file, applies socket permissions/group, and raises `RLIMIT_NOFILE`.
- Computes guest FD quota after reserving internal FDs for memory slots and worker threads.
- Enters configured sandbox before building passthrough config.
- Enables seccomp before starting worker threads.
- Drops Linux capabilities when running as root, with `DAC_READ_SEARCH` required for file-handle inode mode.
- Chooses read-only or normal passthrough filesystem and starts the vhost-user backend.

## Risks And Invariants

- Many options are compatibility-sensitive with older QEMU/legacy virtiofsd syntax.
- Seccomp must be installed before thread-pool creation.
- Sandbox entry changes process view of paths and descriptors, so config captures required proc/mountinfo FDs.
- Migration mode flags are rejected when semantically incompatible.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/main.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/oslib.rs -->
# File Research: sources/virtualization/virtiofsd/src/oslib.rs

## Scope

Linux OS/syscall wrapper layer used by sandboxing, passthrough path handling, migration, and file I/O.

## APIs Covered

- `OsFacts` probes `openat2` support.
- Safe-ish wrappers for `mount`, `umount2`, `fchdir`, `fchmod`, `fchmodat`, `umask`, `openat`, `open_tree`, `move_mount`, and constrained `openat2`.
- `ScopedUmask` restores the previous umask on drop.
- File-handle bindings: `CFileHandle`, `name_to_handle_at`, `open_by_handle_at`.
- `WritevFlags`, `ReadvFlags`, `writev_at`, `readv_at`.
- `PipeReader`, `PipeWriter`, `pipe`.
- Per-thread effective credential syscalls: `seteffuid`, `seteffgid`, `setsupgroup`, `dropsupgroups`.

## Behavior

- `do_open_relative_to()` uses `RESOLVE_IN_ROOT | RESOLVE_NO_MAGICLINKS` plus caller flags to restrict path traversal relative to a directory FD.
- `CFileHandle` converts from serialized file handles and limits handle byte size to 128.
- `preadv2`/`pwritev2` wrappers expose newer RWF flags including noappend, atomic, and dontcache where libc provides them.
- Credential helpers call syscalls directly to avoid libc’s process-wide credential synchronization.

## Risks

Correct safety depends on valid C strings, FDs, iovec pointers, and syscall availability. These wrappers sit on the security boundary for path traversal, sandbox setup, and guest-credential impersonation.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/oslib.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/credentials.rs -->
# File Research: sources/virtualization/virtiofsd/src/passthrough/credentials.rs

## Scope

RAII helpers for temporarily applying guest credentials and temporarily dropping effective capabilities during passthrough filesystem operations.

## APIs Covered

- `UnixCredentials` stores target host UID, GID, supplementary groups, and whether to keep a capability workaround.
- `UnixCredentialsGuard` restores credentials and supplementary groups on drop.
- `ScopedCaps` drops one effective capability on creation and restores it on drop.
- `drop_effective_cap()` public helper.

## Behavior

- `UnixCredentials::set()` changes supplementary groups first, then effective GID, then effective UID.
- Root UID/GID targets are not changed, preserving legacy behavior.
- If supplementary-group extension is not available, it can temporarily add `DAC_OVERRIDE` after UID switch as a kernel compatibility workaround.
- Guard drop restores UID, GID, and drops supplementary groups, logging failures.
- `ScopedCaps` uses capng to drop an effective capability and later restore it; restore failures panic.

## Risks

Credential switching is per-thread by direct syscall wrappers. Ordering is important: changing UID before GID could lose privilege to change GID.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/credentials.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/device_state/deserialization.rs -->
# File Research: sources/virtualization/virtiofsd/src/passthrough/device_state/deserialization.rs

## Scope

Destination-side migration restore logic for passthrough filesystem state.

## APIs Covered

- `TryFrom<Vec<u8>> for serialized::PassthroughFs` via `postcard`.
- `serialized::PassthroughFsV1::apply()` and `apply_with_mount_paths()`.
- `serialized::PassthroughFsV2::apply()`.
- `serialized::NegotiatedOpts::apply()`.
- Inode deserialization helpers for root, path, full path, invalid, and file-handle locations.
- Handle deserialization for reopened inode-backed handles.

## Behavior

- Applies source-negotiated writeback, submount, POSIX ACL, and supplementary group settings, failing if destination configuration cannot support source-enabled features.
- Clears inode store and reconstructs root first when mount-path data is needed for file-handle reopen.
- Repeatedly processes serialized inodes, deferring path entries whose parent inode is not restored yet.
- Restores root from destination config but uses source refcount and optional file-handle identity check.
- Path locations are opened relative to parent inodes with `O_PATH | O_NOFOLLOW | O_CLOEXEC`.
- File-handle locations require source mount ID resolution through V2 mount path metadata.
- Invalid or failed inodes either abort migration or are installed as guest-error placeholders based on `migration_on_error`.
- Reopens handles by opening their associated inode with sanitized preserved flags.

## Risks And Invariants

- Detects unresolved inode dependency cycles.
- Optional file-handle checks protect against path races and inode reuse.
- Destination must not enable source-disabled negotiated behavior without renegotiation; it explicitly applies source state.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/device_state/deserialization.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/device_state/mod.rs -->
# File Research: sources/virtualization/virtiofsd/src/passthrough/device_state/mod.rs

## Scope

Top-level migration-state module for `PassthroughFs`.

## Structure

- Declares submodules: `deserialization`, `preserialization`, `serialization`, and `serialized`.
- Implements `SerializableFileSystem` for `PassthroughFs`.

## Behavior

- `prepare_serialization()` clears old migration info, enables migration-info tracking, then prepares inode locations using either proc-path reconstruction plus tree-walk fallback or file-handle construction.
- Runs an implicit path check after preserialization to catch races where paths became stale while being recorded.
- `serialize()` disables tracking, optionally confirms paths at switch-over, converts state to serialized V2, clears migration info, and writes bytes to the state pipe.
- `deserialize_and_apply()` reads all bytes from the state pipe and applies either V1 or V2 serialized state.

## Risks

Migration is explicitly best-effort during preparation but strict during final serialization when configured to confirm paths. Cancellation is cooperatively checked by constructors.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/device_state/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/device_state/preserialization/file_handles.rs -->
# File Research: sources/virtualization/virtiofsd/src/passthrough/device_state/preserialization/file_handles.rs

## Scope

Preserialization constructor for migration mode that represents inodes by Linux file handles.

## APIs Covered

- `FileHandle` wrapper around `SerializableFileHandle`.
- `Constructor` for collecting file handles for all tracked inodes.
- Conversion from `FileHandle` to shared `InodeLocation`.
- Display implementation for diagnostics.

## Behavior

- Iterates the inode store unless cancellation is requested.
- Skips inodes that already have up-to-date migration info.
- For file-backed inodes, generates a file handle from the FD.
- For handle-backed inodes, reuses the existing handle.
- Invalid inodes report their prior migration error.
- Stores `InodeMigrationInfo` with optional verification handle depending on config.

## Design Notes

The pass is best-effort: failures are logged per inode, and missing migration info can later serialize as invalid, letting the destination decide based on `migration_on_error`.

## Invariants

File-handle locations contain no strong inode references, so their reference-walk helper is a no-op.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/device_state/preserialization/file_handles.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/device_state/preserialization/find_paths.rs -->
# File Research: sources/virtualization/virtiofsd/src/passthrough/device_state/preserialization/find_paths.rs

## Scope

Preserialization fallback constructor that reconstructs inode locations as parent-inode plus filename paths by walking the shared directory tree.

## APIs Covered

- `InodePath` holds a strong parent inode reference and UTF-8 filename.
- `Constructor` walks the filesystem and fills inode migration info.
- `InodePath::check_presence()` validates that a recorded path still identifies the expected inode.
- Display support renders path-like diagnostic output.

## Behavior

- Starts from the FUSE root inode if mounted.
- Uses an explicit directory stack rather than recursive calls.
- Opens directories and iterates entries with `ReadDir::new_no_seek()`.
- Ignores `.` and `..`.
- Opens entries with path-resolution policy through `PassthroughFs::open_relative_to()`.
- Matches discovered entries against the inode store using file handle or inode IDs.
- For matched inodes, records `InodeMigrationInfo::Path`.
- For unmatched directories, creates temporary inode-store entries so deeper tracked children can be represented by parent paths.
- Cancels promptly when the shared cancellation flag is set.

## Validation

`check_presence()` compares device IDs and, when possible, file handles without mount IDs; otherwise it falls back to inode ID comparison. This catches stale paths and inode replacement during migration.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/device_state/preserialization/find_paths.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/device_state/preserialization/mod.rs -->
# File Research: sources/virtualization/virtiofsd/src/passthrough/device_state/preserialization/mod.rs

## Scope

Shared preserialization data model for passthrough migration preparation.

## APIs Covered

- Submodules: `file_handles`, `find_paths`, `proc_paths`.
- `InodeMigrationInfo`: prepared inode location plus optional verification file handle.
- `InodeLocation`: root node, path, or file handle.
- `HandleMigrationInfo`: currently `OpenInode { flags }`.

## Behavior

- `InodeMigrationInfo::new()` chooses location type from `MigrationMode`.
- `new_internal()` optionally attaches a verification `SerializableFileHandle` when `migration_verify_handles` is enabled.
- `new_root()` records root-node migration info without path data.
- `for_each_strong_reference()` exposes strong parent references embedded in path locations so lifetime/refcount handling can be balanced.
- `has_path()` identifies migration info that must be invalidated or updated on rename/unlink.
- `check_path_presence()` delegates validation to path-backed locations.
- `HandleMigrationInfo::new()` strips `O_CREAT`, `O_EXCL`, and `O_TRUNC` from preserved open flags before migration.

## Invariants

Root location is destination-configured, path locations carry parent references, and file-handle locations do not. Handle reopen flags must not recreate, exclusively create, or truncate files after migration.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/device_state/preserialization/mod.rs -->