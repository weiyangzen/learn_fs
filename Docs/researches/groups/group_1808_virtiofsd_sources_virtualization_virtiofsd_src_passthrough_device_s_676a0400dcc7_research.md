# Group Research: group_1808_virtiofsd_sources_virtualization_virtiofsd_src_passthrough_device_s_676a0400dcc7

Scope checked against `Docs/research_subset_a.md`: `sources/virtualization/virtiofsd` is included. All listed files were read completely. Line counts matched the prompt: 6,933 total Rust lines.

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/device_state/preserialization/proc_paths.rs -->
# File Research: sources/virtualization/virtiofsd/src/passthrough/device_state/preserialization/proc_paths.rs

This file implements path discovery through `/proc/self/fd` for passthrough filesystem migration. It is part of preserialization: it fills or repairs `InodeMigrationInfo` so serialized state can describe how the destination should find inodes.

Key structures:
- `Walker`: shared implementation for all modes; holds `&PassthroughFs`, a `Mode`, and an optional cancellation flag.
- `Constructor`: best-effort preserialization path builder for `--migration-mode=find-paths`.
- `ConfirmPaths`: explicit `--migration-confirm-paths` checker; returns hard errors to block migration.
- `ImplicitPathCheck`: lax post-preserialization double-check; logs warnings instead of failing migration.
- `WrappedError`: separates `Fallback` errors, where exhaustive path search might work, from `Unrecoverable` errors.

Main flow:
- `Walker::run()` obtains the root node and the shared directory path from the root inode's `/proc/self/fd` symlink, then iterates `fs.inodes`.
- Cancellation is honored between inode visits through an `AtomicBool`.
- `should_update_inode()` decides whether to create migration info, leave existing info alone, or clear and refresh bad path info.
- `set_path_migration_info_from_proc_self_fd()` reads an inode's absolute `/proc/self/fd` path, derives a path relative to the shared directory, walks each component through `fs.do_lookup()`, and attaches `InodeMigrationInfo` along the path.

Important behavior:
- Root absence is allowed only when the inode store is empty; otherwise it is treated as unrecoverable.
- Deleted `/proc/self/fd` targets with positive link count and paths outside the shared root with multiple links trigger fallback, because a hard link inside the shared directory may still exist.
- `InodePathError::NoFd` is unrecoverable; most other `FdPathError`s are fallback candidates.
- Non-UTF-8 relative paths are unrecoverable because serialized path locations use `String`.
- If component traversal succeeds but does not end at the intended inode, the caller is advised to fall back.

Interactions:
- Uses `InodeData::get_path()`, `statx()` link counts, `relative_path()`, `StrongInodeReference`, and `PassthroughFs::do_lookup()`.
- Feeds `device_state::serialization.rs` by ensuring `InodeData.migration_info` is present where possible.
- Used again by `passthrough/mod.rs` after path-invalidating operations to rediscover moved or hard-linked inodes.

Edge cases and risks:
- Path discovery is inherently race-prone; the surrounding migration code mitigates this with confirm and implicit check phases.
- `/proc/self/fd` may report deleted, anonymous, or outside-root paths, so fallback classification is central to correctness.
- The relative path helper is byte-prefix based; callers depend on root identity and later lookup verification to avoid accepting wrong sibling paths.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/device_state/preserialization/proc_paths.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/device_state/serialization.rs -->
# File Research: sources/virtualization/virtiofsd/src/passthrough/device_state/serialization.rs

This file converts prepared `PassthroughFs` runtime state into serde/postcard serializable structs defined in `serialized.rs`.

Main responsibilities:
- `TryFrom<serialized::PassthroughFs> for Vec<u8>` serializes the structured state with `postcard::to_stdvec()`.
- `From<&PassthroughFs> for serialized::PassthroughFsV2` builds the full migration payload.
- `From<&PassthroughFs> for serialized::NegotiatedOpts` captures options negotiated during FUSE `INIT`.
- `InodeData::as_serialized()` converts one inode, requiring migration info.
- `InodeMigrationInfo::as_serialized()` maps preserialization locations to wire locations.
- `From<(Handle, &HandleData)> for serialized::Handle` serializes open file handles.

Inode serialization:
- Iterates every inode in `fs.inodes`.
- If an inode cannot be serialized, logs a warning and emits a `serialized::Inode` with `InodeLocation::Invalid`, preserving inode ID and refcount.
- Requires `migration_info`; missing info becomes "Failed to reconstruct inode location".
- Asserts that only `fuse::ROOT_ID` uses `RootNode` migration info.
- If `migration_verify_handles` is enabled, requires a prepared file handle and stores it for destination-side verification.

Handle serialization:
- Serializes handle ID, inode ID, and `HandleMigrationInfo`.
- Currently the only handle source is `OpenInode { flags }`.
- Invalid handles from prior failed migration are still serialized so a later destination can retry opening them.

Mount path handling:
- `MountPathsBuilder` is active only for `MigrationMode::FileHandles`.
- It maps source mount IDs, found in serialized file handles, to paths relative to the shared directory.
- If a mount root is outside the shared directory, it serializes `"."` so the destination can use the shared root.
- Mount path collection failures are warning-only; missing mount paths mean affected file-handle inodes cannot migrate.

Interactions:
- Depends on preserialization modules for `InodeMigrationInfo` and `HandleMigrationInfo`.
- Depends on `MountFds` for mount roots and `relative_path()` for shared-directory-relative paths.
- Produces `serialized::PassthroughFs::V2`, which `device_state/mod.rs` writes to the migration state pipe.

Edge cases and risks:
- This layer intentionally avoids new I/O for verification handles; missing prepared handles are internal errors.
- `mount_paths` is best effort; failure does not abort serialization but can make file-handle migration incomplete.
- Path locations require UTF-8 because the wire format stores filenames as `String`.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/device_state/serialization.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/device_state/serialized.rs -->
# File Research: sources/virtualization/virtiofsd/src/passthrough/device_state/serialized.rs

This file defines the migration wire-format structs and enums for passthrough filesystem state. It intentionally contains data shapes only; conversion to bytes happens in `serialization.rs`, and restoration happens in `deserialization.rs`.

Wire format:
- `PassthroughFs`: versioned top-level enum with `V1` and `V2`.
- `PassthroughFsV1`: inodes, next inode ID, open handles, next handle ID, and negotiated FUSE options.
- `PassthroughFsV2`: wraps `V1` and adds `mount_paths` for file-handle migration.
- `NegotiatedOpts`: remembers `writeback`, `announce_submounts`, `posix_acl`, and supplementary group extension negotiation.

Inode representation:
- `Inode`: stores FUSE inode ID, refcount, `InodeLocation`, and optional verification `SerializableFileHandle`.
- `InodeLocation::RootNode`: destination finds root independently.
- `InodeLocation::Path { parent, filename }`: destination opens a filename relative to another serialized inode.
- `InodeLocation::FullPath { filename }`: destination opens a path relative to shared root without a parent strong reference.
- `InodeLocation::FileHandle { handle }`: destination opens by file handle using V2 mount-path translation.
- `InodeLocation::Invalid`: destination must apply `migration_on_error` policy or preserve guest-visible failure state.

Handle representation:
- `Handle`: handle ID, owning inode ID, and `HandleSource`.
- `HandleSource::OpenInode { flags }`: reopen the inode using original `openat(2)` flags.

Important compatibility detail:
- The top-level enum allows incompatible future changes by adding variants while retaining support for older streams.
- V2 is backward-compatible by embedding V1 and adding mount-path metadata needed only for file handles.

Interactions:
- Uses `SerializableFileHandle` from `file_handle.rs`.
- Type aliases align wire inode IDs and handle IDs with `inode_store::Inode` and `passthrough::Handle`.
- Consumed by both serializer and deserializer.

Edge cases and risks:
- Filename fields are UTF-8 `String`s, so non-UTF-8 host paths cannot be represented in path-based migration.
- V1 cannot carry mount path translations, so file-handle migration is meaningfully V2-only.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/device_state/serialized.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/file_handle.rs -->
# File Research: sources/virtualization/virtiofsd/src/passthrough/file_handle.rs

This file wraps Linux file-handle APIs used to identify and reopen inodes without holding an `O_PATH` fd for every inode.

Core types:
- `FileHandle`: mount ID plus `oslib::CFileHandle`.
- `OpenableFileHandle`: a `FileHandle` paired with an `Arc<MountFd>` suitable for `open_by_handle_at()`.
- `SerializableFileHandle`: serde form containing mount ID, handle type, and handle bytes.
- `FileOrHandle`: stores an inode as a `GuestFile`, an openable file handle, or an invalid migration error.

File-handle creation:
- `from_name_at_fail_hard()` calls `name_to_handle_at()` and always returns either a handle or an error.
- `from_name_at()` returns `Ok(None)` for unsupported filesystems (`EOPNOTSUPP`) or oversized handles (`EOVERFLOW`), allowing fallback to `O_PATH` FDs.
- `from_fd_fail_hard()` and `from_fd()` use `AT_EMPTY_PATH` to address an already-open fd.

Opening:
- `FileHandle::to_openable()` asks `MountFds` for a mount FD matching the handle's mount ID.
- `OpenableFileHandle::open()` calls `open_by_handle_at()` with caller-provided flags.
- `SerializableFileHandle::to_openable()` converts serialized bytes back to `CFileHandle` and intentionally uses the destination `MountFd`'s local mount ID, not the serialized source mount ID.

Verification helpers:
- `require_equal()` compares mount ID and handle payload.
- `require_equal_without_mount_id()` compares type and payload only; this is important during migration because source and destination mount IDs differ.
- `Display` prints mount ID, handle type, and hex bytes for diagnostics.

Interactions:
- Used by `inode_store.rs` as a store key when inodes are represented by handles.
- Used by `passthrough/mod.rs` when `inode_file_handles` or file-handle migration is enabled.
- Used by serialized migration state for inode verification and file-handle locations.

Edge cases and risks:
- File handles are filesystem-dependent; unsupported or oversized handles must be handled without breaking normal operation in `Prefer` mode.
- Opening serialized handles depends on correct source-mount-ID to destination-mount-FD translation.
- `FileOrHandle::Invalid` preserves migration errors so guest operations can fail deterministically and later migrations can forward the invalid state.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/file_handle.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/guest_fd_limit.rs -->
# File Research: sources/virtualization/virtiofsd/src/passthrough/guest_fd_limit.rs

This file implements a small semaphore for limiting file descriptors allocated on behalf of the guest.

Core types:
- `GuestFdSemaphore`: tracks the initial limit, remaining available slots, and whether exhaustion has already been logged.
- `GuestFile`: wraps a `File` and releases one semaphore slot on drop.

Behavior:
- `GuestFdSemaphore::new(limit)` initializes available slots to the configured limit.
- `allocate()` atomically subtracts one slot with `fetch_update()` and returns a `GuestFile`.
- If no slots remain, it logs one error suggesting `--rlimit-nofile` adjustment and returns `ENFILE`.
- `GuestFile::drop()` calls `release()`, which atomically increments available slots.
- `GuestFile` implements `AsRawFd` and exposes `get_file()` for wrapped file access.

Interactions:
- `PassthroughFs` wraps guest-visible inode and handle FDs in `GuestFile`.
- `HandleDataFile` and `FileOrHandle::File` rely on this wrapper for automatic slot release.

Edge cases and risks:
- Relaxed atomics are sufficient because this semaphore guards counts, not memory visibility of file contents.
- Overflow on release panics, which would indicate an internal accounting bug.
- Returning `ENFILE` is chosen because these errors often go directly back to the guest.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/guest_fd_limit.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/inode_store.rs -->
# File Research: sources/virtualization/virtiofsd/src/passthrough/inode_store.rs

This file owns passthrough inode identity, lookup deduplication, FUSE refcounting, and safe lifetime handling for migration metadata.

Core data model:
- `Inode = u64`: FUSE inode ID.
- `InodeIds`: host inode tuple: `st_ino`, `st_dev`, and mount ID.
- `InodeData`: FUSE inode ID, `FileOrHandle`, atomic refcount, host IDs, mode, and optional migration info.
- `InodeStoreInner`: maps by FUSE ID, by host IDs, and by file handle.
- `InodeStore`: `Arc<RwLock<InodeStoreInner>>` public wrapper.
- `StrongInodeReference`: counted strong reference that increments/decrements `InodeData.refcount`.

Inode file access:
- `InodeData::get_file()` returns an `InodeFile::Ref` for stored `GuestFile`, opens an `OpenableFileHandle`, or reports invalid migration state.
- `open_file()` reopens stored `O_PATH` FDs through `/proc/self/fd` or opens by handle with requested flags.
- Non-regular and non-directory inodes are protected from unsafe non-`O_PATH` opens via `is_safe_inode()`.
- `get_path()` reads `/proc/self/fd` and rejects non-root nodes reported as `/`, treating them as outside the shared root.
- `identify()` prefers path diagnostics and falls back to inode metadata.

Store behavior:
- `insert_new()` populates all identity maps and asserts FUSE ID uniqueness.
- `remove()` removes all identity entries and drops migration-info strong refs with `drop_unlocked()`.
- `clear_migration_info()` preserves root migration info but clears all other inode migration data safely.
- `claim_inode()` prefers file-handle identity, then falls back to host IDs only for entries backed by a live FD. This avoids inode-number reuse when only a file handle is stored.
- `get_or_insert()` deduplicates existing inodes or inserts a new one with refcount 1.
- `new_inode()` inserts without deduplication, used for known FUSE IDs such as root or deserialized state.

Strong reference behavior:
- `StrongInodeReference::new()` and `new_with_data()` increment the refcount only if it is nonzero.
- `new_no_increment()` is unsafe and requires the caller to have already accounted for the refcount.
- `leak()` transfers the refcount to the guest, which must later send `FORGET`.
- `Drop` decrements refcount and removes the inode when it reaches zero.
- `drop_unlocked()` is the safe path when the inode store is already mutably locked.

Interactions:
- Used by nearly every operation in `passthrough/mod.rs`.
- Migration info may contain `StrongInodeReference`, creating cycles that `InodeStore::drop()` explicitly clears.
- Used by `proc_paths.rs` and serialization to traverse and preserve inode relationships.

Edge cases and risks:
- Lock ordering matters: dropping `StrongInodeReference` while holding the store lock can deadlock unless `drop_unlocked()` is used.
- Refcounts intentionally saturate on over-forget to avoid integer underflow from misbehaving guests.
- The iterator does not hold the lock across calls and can see newly added inodes with higher IDs.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/inode_store.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/mod.rs -->
# File Research: sources/virtualization/virtiofsd/src/passthrough/mod.rs

This is the main passthrough filesystem implementation. It defines configuration, runtime state, helper logic, and the `FileSystem` implementation that forwards FUSE operations to the host filesystem.

Major public modules:
- Re-exports and submodules include credentials, device migration state, file handles, inode store, mount FD management, read-only wrapper, stat helpers, utility helpers, and xattr mapping.

Configuration:
- `CachePolicy`: `Never`, `Metadata`, `Auto`, `Always`.
- `InodeFileHandlesMode`: `Never`, `Prefer`, `Mandatory`.
- `MigrationOnError`: `Abort` or `GuestError`.
- `MigrationMode`: `FindPaths` or `FileHandles`.
- `Config`: timeouts, cache/writeback, root directory, proc fds, submounts, file-handle mode, xattr and security-label behavior, ACLs, migration behavior, ID maps, and guest FD limit.

Runtime state:
- `PassthroughFs` holds `InodeStore`, open handle map, guest FD semaphore, optional `MountFds`, `/proc/self/fd`, original cwd, negotiated option flags, OS facts, migration tracking flag, config, and UID/GID maps.
- `HandleData` tracks open handle ownership, wrapped file or invalid migration error, and handle migration info.
- `ScopedWorkingDirectory` temporarily switches cwd to `/proc/self/fd` for path-based syscalls against O_PATH descriptors.

Initialization:
- `PassthroughFs::new()` opens proc fds or consumes sandbox-provided ones, initializes `MountFds` when needed, builds soft ID maps, detects remapped `security.capability`, validates file-handle support, and clears umask.
- `init()` resets prior state, opens root, negotiates FUSE options, records negotiated state, and validates required capabilities for ACLs and security labels.
- `open_root_node()` creates the root `InodeData`, gives it root migration info when possible, and assigns libfuse-like refcount 2.

Lookup and open behavior:
- `open_relative_to()` uses `openat2` when available and falls back to `openat`.
- `try_lookup_implementation()` opens a child as `O_PATH`, stats it, optionally creates a file handle, and claims an existing inode by handle or IDs.
- `do_lookup()` creates new inode entries, marks submounts, attaches migration info if migration tracking is active, and leaks one strong reference to the guest.
- `open_inode()` handles writeback read/write upgrade, writeback append clearing, optional `O_DIRECT` filtering, and then reopens by proc path or file handle.
- `do_open()` cleans flags, optionally drops `FSETID`, opens the inode, clears capabilities on truncate, stores a handle, and chooses FUSE open cache options.

Mutation and migration consistency:
- `before_invalidating_path()` looks up an inode before unlink/overwrite-style operations.
- `after_invalidating_path()` clears path-based migration info after the syscall and tries to rediscover the inode through `/proc/self/fd`.
- `update_inode_migration_info()` refreshes path migration info after successful rename.
- These hooks appear around `unlink`, `rmdir`, `mkdir`, `rename`, `mknod`, `link`, and `symlink`.

Filesystem operations:
- Implements statfs, lookup, forget, batch_forget, opendir/releasedir, readdir, open/release, create, unlink/rmdir, read/write, getattr/setattr, rename, mknod, link, symlink, readlink, flush, fsync/fsyncdir, access, xattr operations, fallocate, lseek, copyfilerange, and syncfs.
- Readdir serializes kernel directory offset access with a write lock around `lseek64`/`getdents64`.
- Reads and writes use zero-copy helpers and offset-based syscalls so file offsets are not shared.
- Write paths clear remapped file capabilities and handle append semantics with `RWF_APPEND` only for non-delayed writes.

Xattr and privilege behavior:
- Blocks POSIX ACL xattrs unless ACL support is negotiated.
- Applies `XattrMap` on client names and server xattr lists.
- Clears remapped `security.capability` on writes, truncates, chown, and relevant xattr paths.
- Clears SGID explicitly for POSIX ACL setxattr when requested by `SETXATTR_ACL_KILL_SGID`.
- `unix_credentials_guard()` maps guest credentials to host credentials and handles supplementary groups when negotiated.

Tests:
- Two unit tests cover SGID clearing decision for non-UTF-8 xattr names and `system.posix_acl_access`.

Edge cases and risks:
- This file is syscall-heavy and depends on correct `O_PATH`, `/proc/self/fd`, and `openat2`/`openat` behavior.
- File-handle mode has early validation and per-filesystem error suppression, but support can vary by underlying filesystem.
- Writeback caching intentionally trades consistency for performance when users assert exclusive directory access.
- Migration consistency relies on best-effort rediscovery after path invalidation and on preserialization/confirmation phases.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/mount_fd.rs -->
# File Research: sources/virtualization/virtiofsd/src/passthrough/mount_fd.rs

This file manages open mount file descriptors used with `open_by_handle_at()` and file-handle migration.

Core types:
- `MountFd`: one open FD on a mount, its local mount ID, and a weak pointer back to the mount-FD map.
- `MountFds`: shared map from mount ID to weak `MountFd`, plus `/proc/self/mountinfo`, optional prefix stripping, and per-mount error suppression.
- `MPRError`: mount-point-related error with optional mount ID/root context and a `silent` flag.

Mount FD creation:
- `MountFd::new()` opens a path relative to a directory with `O_RDONLY`, stats it to get the local mount ID, and optionally inserts or reuses an entry in `MountFds`.
- `MountFds::get()` first tries to upgrade an existing weak entry.
- If missing, it finds the mount root from mountinfo, opens it with `O_PATH`, verifies the mount ID with `statx()`, ensures the mount point is regular file or directory, reopens it read-only, and stores it.

Mount root lookup:
- `get_mount_root()` rewinds and reads `/proc/self/mountinfo`.
- It searches for the requested mount ID and extracts the mount path column.
- If `mountprefix` is set, it strips that prefix, returning `/` for the shared root mount or mounts outside the prefix.

Error handling:
- `MPRError::Display` adds filesystem mount ID and/or mount root context when known.
- `error_for_nolookup()` marks repeated mount-ID errors as silent.
- `error_for()` augments non-silent errors with mount root lookup where safe.

Lifecycle:
- `MountFd::drop()` removes its weak map entry only when the entry's strong count is zero, avoiding races with concurrent replacement.
- The weak-map design means the cache does not keep mount FDs alive without active users.

Interactions:
- `file_handle.rs` uses `MountFds::get()` to make file handles openable.
- `serialization.rs` uses `get_mount_root()` to serialize source mount IDs to shared-directory-relative paths.
- `passthrough/mod.rs` creates `MountFds` when file handles or file-handle migration are enabled.

Edge cases and risks:
- Mountinfo parsing is intentionally simple and column-oriented; unusual escaped mount paths are worth auditing if path fidelity matters.
- Mount points that are not regular files or directories are rejected because they cannot be safely reopened read-only.
- Mount IDs are local to a host, so serialized file handles must be translated through paths on migration.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/mount_fd.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/read_only.rs -->
# File Research: sources/virtualization/virtiofsd/src/passthrough/read_only.rs

This file implements a read-only wrapper around `PassthroughFs` while preserving the same `FileSystem` and `SerializableFileSystem` interfaces.

Core type:
- `PassthroughFsRo(PassthroughFs)`: owns an inner passthrough filesystem and restricts mutating operations.

Open filtering:
- `rofs_open()` allows `O_PATH` opens directly because `O_PATH` ignores most access flags.
- Non-`O_RDONLY` access modes return `EROFS`.
- `O_EXCL` returns `EROFS`.
- `O_TMPFILE` and `O_TRUNC` return `EINVAL`.
- `O_CREAT` is stripped and the underlying open is attempted; if the path does not exist, the wrapper returns `EROFS`.

Delegation helpers:
- `ops_allow!` generates methods that forward directly to the inner filesystem.
- `ops_forbid!` generates methods that always return `EROFS`.

Allowed operations:
- Init/destroy, lookup/forget, getattr, readlink/read, flush, fsync, release, statfs, get/list xattr, readdir, fsyncdir, releasedir, lseek, and syncfs are allowed.

Forbidden operations:
- setattr, symlink, mknod, mkdir, unlink, rmdir, rename, link, write, fallocate, setxattr, removexattr, and copyfilerange return `EROFS`.

Special operations:
- `open()` and `opendir()` apply `rofs_open()` before delegating.
- `create()` never creates; it performs lookup and open on an existing file, returning `EROFS` if lookup reports not found.
- `access()` rejects `W_OK` with `EROFS` and delegates all other checks.
- Serialization methods delegate directly, so read-only instances still support migration.

Edge cases and risks:
- The wrapper intentionally returns `EROFS` earlier than Linux might in some cases, for example when a writable filesystem would have returned `EEXIST`.
- Read-only mode still allows fsync/syncfs and metadata reads.
- Xattr reads are allowed, but all xattr writes/removals are blocked.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/read_only.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/stat.rs -->
# File Research: sources/virtualization/virtiofsd/src/passthrough/stat.rs

This file provides the passthrough stat wrapper used throughout the filesystem. It normalizes Linux `statx()` output into `libc::stat64` plus a mount ID.

Core types:
- `MountId = u64`.
- `StatExt`: `st: libc::stat64` and `mnt_id: MountId`.
- `SafeStatXAccess`: internal trait for accessing only valid `statx` fields based on `stx_mask`.

Main behavior:
- `SafeStatXAccess::stat64()` converts valid `STATX_BASIC_STATS` fields into a zero-initialized `libc::stat64`.
- `SafeStatXAccess::mount_id()` returns `stx_mnt_id` only when `STATX_MNT_ID` is present.
- `get_mount_id()` falls back to `name_to_handle_at()` mount ID when kernel `statx()` lacks mount ID support.
- `do_statx()` invokes `libc::syscall(libc::SYS_statx)` directly instead of relying on a libc wrapper.
- `statx()` defaults path to an empty C string, uses `AT_EMPTY_PATH | AT_SYMLINK_NOFOLLOW`, requests basic stats and mount ID, and returns `ENOSYS` if basic stats are missing.

Interactions:
- Used by lookup, getattr, file-handle validation, mount FD creation, migration path link counts, and xattr/permission helpers.
- `MountId` is a core part of inode identity in `inode_store.rs`.

Edge cases and risks:
- On kernels before `STATX_MNT_ID`, mount ID falls back to file-handle support and then to `0`.
- A mount ID of `0` weakens submount identification and file-handle diagnostics.
- Direct syscall use improves portability across libc versions but remains Linux-specific.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/stat.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/stat/file_status.rs -->
# File Research: sources/virtualization/virtiofsd/src/passthrough/stat/file_status.rs

This file abstracts platform differences for the `statx` structure and constants used by `stat.rs`.

Behavior:
- On GNU libc targets, re-exports `libc::statx` as `statx_st` and `libc::{STATX_BASIC_STATS, STATX_MNT_ID}`.
- On non-GNU targets, defines a local C-compatible `statx_st_timestamp`.
- On non-GNU targets, defines a local C-compatible `statx_st` containing the fields needed by `stat.rs`, including `stx_mnt_id`.
- On non-GNU targets, defines `STATX_BASIC_STATS = 0x07ff` and `STATX_MNT_ID = 0x1000`.

Purpose:
- Lets `stat.rs` call the `statx` syscall and inspect results even when the libc crate does not expose a `statx` wrapper for the target environment.
- Specifically addresses musl environments, where the struct exists conceptually but libc crate support differs.

Interactions:
- Only consumed by `passthrough/stat.rs`.

Edge cases and risks:
- The local non-GNU struct must match the Linux kernel ABI layout for the fields used.
- Any future `stat.rs` access to additional `statx` fields would require updating this compatibility struct.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/stat/file_status.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/util.rs -->
# File Research: sources/virtualization/virtiofsd/src/passthrough/util.rs

This file contains small passthrough helpers for fd opening, fd path discovery, errno construction, and shared-root-relative path handling.

Open helpers:
- `openat()` wraps `libc::openat()` with `CString` conversion and returns `File`.
- `openat_verbose()` adds path context to errors and is intended for internal setup, not guest-returned errors.
- `reopen_fd_through_proc()` opens `/proc/self/fd/{fd}` with adjusted flags, clearing `O_NOFOLLOW` because the proc entry is a symlink.
- `is_safe_inode()` returns true only for regular files and directories.

Errno helpers:
- `ebadf()`, `einval()`, and `erofs()` construct common raw OS errors.

FD path discovery:
- `FdPathError` distinguishes readlink failure, too-long symlink, invalid C string, non-file proc link targets, and deleted targets.
- `get_path_by_fd()` reads the `/proc/self/fd/{fd}` symlink, rejects targets whose pre-slash segment contains `:`, and rejects targets ending in `" (deleted)"`.
- `printable_fd()` returns a path through proc when possible or a `{fd:N}` placeholder.

Relative path handling:
- `relative_path(path, prefix)` strips a byte prefix from a C string path, removes leading slashes from the remainder, and returns the remaining `CStr`.

Interactions:
- Used by `passthrough/mod.rs` for opening and reopening files.
- Used by `inode_store.rs` and `proc_paths.rs` for migration path discovery.
- Used by `mount_fd.rs` and `serialization.rs` through `openat()` and `relative_path()`.

Edge cases and risks:
- `get_path_by_fd()` treats anonymous or special proc targets as non-file paths and treats deleted paths as invalid for migration.
- `relative_path()` is a byte-prefix operation rather than a component-aware path check; callers that need strict directory containment should verify the resolved inode path through subsequent lookup.
- `openat_verbose()` can clobber raw errno context, which is why the file warns not to use it for errors returned directly to the guest.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/util.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/xattrmap.rs -->
# File Research: sources/virtualization/virtiofsd/src/passthrough/xattrmap.rs

This file implements extended-attribute name translation between the guest client and host server.

Rule model:
- `Scope`: client, server, or both.
- `Type`: `Prefix`, `Okay`, `Bad`, `Unsupported`, and `Map`.
- `Rule`: scope, type, client-side key prefix, and server-side prepend prefix.
- `XattrMap`: ordered list of expanded rules; first matching rule wins.

Error model:
- `ErrorKind` covers invalid scope/type, invalid delimiter, incomplete rule, `map` rule violations, empty input, and unterminated mappings.
- `Error` wraps `ErrorKind` plus optional 1-based rule number.

Parsing:
- Rules are delimiter-based and may use different delimiters per rule.
- Full form: delimiter, type, scope, key, prepend, delimiter-separated.
- `map` shorthand parses key and prepend, expands to multiple ordinary rules, and must be final.
- Empty input is rejected.
- Whitespace between ordinary rules is skipped.

Mapping behavior:
- `map_client_xattr()` finds a client rule and returns `AppliedRule::Pass`, `Deny`, or `Unsupported`.
- `Prefix` prepends the configured server prefix to a client xattr name.
- `Okay` passes the client name unchanged.
- `Bad` maps to guest `EPERM` at the caller.
- `Unsupported` maps to guest `ENOTSUP` at the caller.
- `map_server_xattrlist()` processes NUL-separated host xattr names, hiding `Bad` and `Unsupported` names, passing `Okay`, and stripping `Prefix` prepends.
- If all server names are filtered, it returns a single NUL byte.

Tests:
- Cover single and multiple rule parsing, whitespace-separated rules, incomplete rules, map-rule violations, map expansion, invalid type/scope, no rules, different delimiters, ok/bad/unsupported behavior, prefix prepend, and server prefix stripping.

Interactions:
- `passthrough/mod.rs` uses this map in `map_client_xattrname()` and `map_server_xattrlist()`.
- The read-only wrapper allows read/list xattr operations to use the same mapping while denying mutation.

Edge cases and risks:
- `CString::new(...).unwrap()` assumes parsed rule fields contain no interior NULs.
- The `InvalidType.expected` string omits `unsupported` even though `unsupported` is accepted.
- The `map` final-rule check happens before trailing whitespace is skipped, so a final `map` rule followed only by whitespace appears likely to be rejected.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/passthrough/xattrmap.rs -->