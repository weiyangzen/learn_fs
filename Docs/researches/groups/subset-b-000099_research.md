# subset-b-000099 research

This grouped report covers the requested Rust overlay implementation, syscall wrappers, whiteout/xattr helpers, and focused integration tests for `sources/cloud-native/fuse-overlayfs`. Each section is wrapped with the required source-path markers for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/overlay.rs -->
# sources/cloud-native/fuse-overlayfs/src/overlay.rs

## Purpose
`overlay.rs` is the core Rust overlay filesystem implementation. It owns the long-lived `OverlayFs` state and implements `fuser::Filesystem` callbacks for lookup, metadata, directory traversal, copy-up, whiteout-aware mutation, hardlinks, xattrs, passthrough I/O, sync, allocation, seek, copy ranges, and selected filesystem ioctls.

## Important APIs, Types, And Functions
`OverlayFs` stores mount configuration, the locked `OverlayInner`, open file/directory handle maps, FUSE passthrough backing-id maps, and a `Notifier` for cache invalidation. `OverlayInner` stores ordered layers, inode table, node arena, root node, workdir fd, inode passthrough mode, overflow ids, whiteout/copy-up counters, and mknod capability. Important helpers include `reply_open_maybe_passthrough`, `do_rm`, `prepare_create_parent`, `stat_and_register_child`, `rpl_stat_with_path`, `load_dir_impl`, `do_lookup_file`, `do_lazy_lookup`, `build_dir_entries`, `get_node_up`, `hide_node`, `create_and_register_child`, and stat override parsers. The `Filesystem` impl provides the operational API surface: `init`, `lookup`, `forget`, `getattr`, `setattr`, `readlink`, `mknod`, `mkdir`, `unlink`, `rmdir`, `symlink`, `rename`, `link`, `open`, `read`, `write`, `release`, `statfs`, xattr handlers, `create`, directory handlers, `fsync`, `fsyncdir`, `fallocate`, `lseek`, `copy_file_range`, and `ioctl`.

## Control Flow
Mount initialization negotiates FUSE capabilities, preferring passthrough when available and compatible with fsync behavior, otherwise enabling writeback cache when configured. Lookup first attempts a read-locked cache hit against the arena and inode table; misses take the write lock, lazily scan layers, honor whiteouts/opaque directories, register FUSE inode numbers, and return mapped attributes. Directory loading walks layers from upper/top to lower, merges unseen children, records whiteouts, and stops at opaque directories. Write-like operations resolve the node, copy it up through `copyup::copyup` when it lives on a lower layer, then operate on upper-layer fd/path objects resolved through `openat2` containment helpers.

## State And Persistence
Persistent state is written to the upper layer and workdir: copied-up files/dirs, whiteouts, hidden renamed-away entries, user/trusted overlay xattrs, POSIX ACLs, stat override xattrs, and created filesystem objects. In-memory state includes the node arena, inode/hardlink registrations, lookup counts, loaded/unloaded directory caches, open fh/dh maps, passthrough backing reference counts, and hidden node metadata. `wd_counter` provides workdir temporary names. UID/GID views are mapped through configured id mappings and overflow ids; persisted ids are mapped back through `map_uid`/`map_gid`.

## Dependencies And Integration Points
This file integrates `OverlayConfig`, `OvlLayer`/datasources, `copyup`, `whiteout`, `xattr`, `mapping`, `node`, and `sys::*` wrappers. Externally it depends on `fuser`, libc syscalls, `parking_lot::RwLock`, `rustc_hash::FxHashMap`, and Linux overlay semantics. Test integration comes from shell suites that mount `fuse-overlayfs`, package managers, `renameat2`, mmap/gcc, xattr tools, and special-file commands.

## Risks
The highest-risk areas are lock ordering across `inner`, open handle maps, and passthrough backing maps; path containment for multi-component operations; FUSE lookup-count and inode-table lifetime correctness for hardlinks; whiteout cleanup when replacing or recreating entries; lower-layer directory rename restrictions; stat override parsing and xattr namespace remapping; passthrough incompatibilities with writeback/volatile modes; and platform-specific syscall behavior such as `renameat2`, `openat2`, mknod, xattrs, and `copy_file_range`. The `read` path caps reply buffers and uses thread-local storage; changes must preserve offset-based I/O and not leak stale bytes.

## Test Signals
Unit tests at the end cover stat override parsing and device parsing. Integration coverage is broad in this subset: copy-up tests validate content/xattrs/timestamps/directories; directory tests validate merges, opaque dirs, nlink, whiteout filtering, and lower priority; hardlink tests cover lower-layer hardlinks, unlink/relink, rename, and copy-up; rename tests exercise `RENAME_NOREPLACE` and `RENAME_EXCHANGE`; readonly and special-file tests cover EROFS, id mapping, volatile mode, mknod/FIFO/socket/fallocate/statfs/setattr; passthrough and mmap tests validate inode stability and same-inode cross-layer behavior; Fedora and Alpine scripts exercise real container/package-manager workflows.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/overlay.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/sys/dir.rs -->
# sources/cloud-native/fuse-overlayfs/src/sys/dir.rs

## Purpose
`sys/dir.rs` wraps libc `DIR*` iteration behind a small Rust API used by overlay directory merging and cleanup paths.

## Important APIs, Types, And Functions
`RawDirEntry` carries entry name bytes, inode number, and `d_type`. `DirStream` owns a `*mut libc::DIR`. `DirStream::from_fd` consumes an `OwnedFd` with `fdopendir`; `DirStream::from_raw_fd` duplicates a borrowed fd first; `next_entry` wraps `readdir`; `Drop` closes the stream with `closedir`. An unsafe `Send` impl is justified by exclusive `&mut self` iteration.

## Control Flow
Callers open a directory fd, construct a `DirStream`, loop on `next_entry`, and use returned raw names/types for merge or deletion decisions. End of directory returns `None`; syscall failure during `readdir` is not separately surfaced.

## State And Persistence
The only state is the owned DIR pointer and the fd consumed by `fdopendir`. No persistent data is written. `from_raw_fd` avoids stealing caller ownership by duping the fd.

## Dependencies And Integration Points
`overlay.rs` uses `DirStream` for loading layer directories and emptying upper directories before rename-over-dir. Datasource implementations can also expose it through `opendir`. It depends on libc and the project `FsError`/`FsResult` error wrapper.

## Risks
`readdir` errors are indistinguishable from end-of-directory. `d_type` can be `DT_UNKNOWN`, so callers must stat when type matters. The unsafe `Send` contract relies on higher-level locking or exclusive ownership; sharing a `DirStream` concurrently would be invalid.

## Test Signals
Unit tests create temporary directories and verify normal listing includes `.`/`..` and files/subdirs, and an empty directory only lists `.`/`..`.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/sys/dir.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/sys/fs.rs -->
# sources/cloud-native/fuse-overlayfs/src/sys/fs.rs

## Purpose
`sys/fs.rs` centralizes unsafe filesystem-related libc calls behind checked `FsResult` wrappers. It is the low-level syscall substrate for metadata, creation, deletion, linking, renaming, allocation, truncation, and path resolution.

## Important APIs, Types, And Functions
Wrappers include `fstat`, `fstatat`, `fstatvfs`, `statfs`, `statvfs`, `statx`, `fchown`, `fchownat`, `fchmod`, `fchmodat`, `futimens`, `utimensat`, `mkdirat`, `mknodat`, `unlinkat`, `linkat`, `symlinkat`, `readlinkat`, `renameat`, `renameat2`, `fallocate`, `truncate`, and `realpath`. Test-only `zeroed_stat` helps stat override parser tests.

## Control Flow
Each function prepares C-compatible arguments, zero-initializes output structs where needed, invokes one libc syscall or Linux syscall, checks negative return values, and maps `errno` to `FsError::last()`.

## State And Persistence
State changes are exactly the underlying filesystem operations: metadata ownership/mode/time updates, object creation/removal/linking, renames, preallocation, truncation, and resolved path allocation/freeing in `realpath`.

## Dependencies And Integration Points
`overlay.rs`, `whiteout.rs`, copy-up logic, datasources, and tests call these wrappers to keep unsafe code outside higher-level overlay logic. It depends on libc, `CStr`, raw fds, and project error types.

## Risks
Callers must pass valid fds and containment-safe paths; these wrappers deliberately do not prevent symlink traversal by themselves. `renameat2` is Linux-specific and may fail on older kernels or unsupported filesystems. `readlinkat` uses a fixed `PATH_MAX` buffer. `realpath` follows symlinks and should only be used for trusted inputs.

## Test Signals
Unit tests exercise `fstat`, `fstatat`, `mkdirat`/`unlinkat`, `symlinkat`/`readlinkat`, `fchmod`, `fstatvfs`, and `renameat`. Integration tests exercise the rest through FUSE operations such as mknod, chmod/chown, rename, fallocate, truncate, statfs, and whiteout deletion.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/sys/fs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/sys/handle.rs -->
# sources/cloud-native/fuse-overlayfs/src/sys/handle.rs

## Purpose
`sys/handle.rs` exposes Linux `name_to_handle_at` and hashes returned file handles for stable inode generation in xino/NFS-filehandle mode.

## Important APIs, Types, And Functions
`FileHandle` stores `handle_bytes` and the variable-length handle payload. `name_to_handle_at` allocates a fixed 128-byte raw kernel handle buffer, invokes `SYS_name_to_handle_at`, and returns the used handle bytes. `fnv1a_hash` implements the C-compatible 64-bit FNV-1a hash over handle bytes.

## Control Flow
The caller passes a directory fd, raw path bytes, and flags. The wrapper converts path bytes to a C string, runs the syscall, then truncates the internal fixed buffer to the kernel-reported handle length. Higher-level code hashes that byte vector when a datasource can supply stable handles.

## State And Persistence
No persistent state is written. The file handle is an in-memory representation of kernel-provided filesystem identity.

## Dependencies And Integration Points
Layer datasource code uses this for `get_nfs_filehandle`; `overlay.rs` consumes those values in `get_st_ino_with_path` when `nfs_filehandles` is enabled. It depends on Linux syscall availability and `FsError`.

## Risks
Not all filesystems support file handles. The fixed 128-byte maximum can reject larger handles if encountered. Hash collisions are possible, though FNV-1a is used to match the existing C behavior. Path conversion rejects interior NUL bytes.

## Test Signals
There are no direct tests in this file. `test-passthrough.sh` indirectly validates stable inode behavior with `xino=auto`, same-inode layers, and double-FUSE cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/sys/handle.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/sys/io.rs -->
# sources/cloud-native/fuse-overlayfs/src/sys/io.rs

## Purpose
`sys/io.rs` wraps low-level fd I/O syscalls used by FUSE read/write paths, sync operations, truncation, sparse/extent operations, file cloning, copy ranges, and filesystem ioctls.

## Important APIs, Types, And Functions
The module exports `pread`, `pwrite`, `read`, `write`, `sendfile`, `copy_file_range`, `fsync`, `fdatasync`, `ftruncate`, `lseek`, `ficlone`, and `ioctl_long`.

## Control Flow
Each wrapper invokes one libc syscall using raw fd and Rust-managed buffers or integer parameters, then returns either the byte count/result or `FsError::last()`.

## State And Persistence
Persistent effects are file content writes, file length changes, sync-to-storage requests, copied extents, cloned extents, and ioctl-set filesystem flags/version values. The module itself keeps no state.

## Dependencies And Integration Points
`overlay.rs` uses `pread`/`pwrite` for FUSE `read`/`write`, sync wrappers for `fsync`/`fsyncdir`, `ftruncate` for setattr/truncate, `lseek` for FUSE lseek, `copy_file_range` for server-side copies, and `ioctl_long` for `FS_IOC_*FLAGS`/`VERSION`. Copy-up code can use `ficlone`/`sendfile` paths elsewhere in the crate.

## Risks
Partial reads/writes/copies must be handled by callers. `copy_file_range`, `sendfile`, and `FICLONE` are filesystem/kernel dependent. `ioctl_long` assumes c_long-sized in/out values and is not a generic ioctl abstraction. Offset casts must remain within kernel-supported ranges.

## Test Signals
Unit tests cover pread/pwrite round trips, fsync, ftruncate, lseek, best-effort copy_file_range, and read/write. Integration tests cover FUSE I/O, fallocate, sparse and mmap workflows, and setattr truncation.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/sys/io.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/sys/mod.rs -->
# sources/cloud-native/fuse-overlayfs/src/sys/mod.rs

## Purpose
`sys/mod.rs` is the module index for the crate's unsafe/syscall boundary.

## Important APIs, Types, And Functions
It publicly exports `dir`, `fs`, `handle`, `io`, `openat2`, `process`, `statx`, and `xattr`.

## Control Flow
There is no runtime control flow. The file defines the module tree consumed by higher-level overlay, datasource, copy-up, and mount code.

## State And Persistence
No state or persistence is defined here.

## Dependencies And Integration Points
All higher-level modules import syscall wrappers through this namespace. The organization supports the crate-level comment in `overlay.rs` that unsafe code lives in `src/sys`.

## Risks
Changing module visibility or names will break imports throughout the crate. Adding unsafe code outside this boundary would weaken the architectural contract.

## Test Signals
No direct tests. Successful compilation and the tests for individual submodules validate the module wiring.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/sys/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/sys/openat2.rs -->
# sources/cloud-native/fuse-overlayfs/src/sys/openat2.rs

## Purpose
`sys/openat2.rs` provides contained file opening with Linux `openat2(2)` and `RESOLVE_IN_ROOT`, plus helpers for safely resolving parent directories before path-based filesystem operations.

## Important APIs, Types, And Functions
`SafeFd` wraps an `OwnedFd` that can only be produced by `safe_openat`. `safe_openat` masks valid flags, sets mode only for creation, and invokes `SYS_openat2` with `RESOLVE_IN_ROOT`. `open_trusted` uses plain `open` for mount-time trusted paths. `open_parent_safe` and `open_parent_safe_cstr` split multi-component paths into safely opened parent fds and basenames. `proc_fd_path` builds `/proc/self/fd/<fd>/<basename>` byte paths. `file_exists_at` checks existence with `faccessat`, falling back to `fstatat` on `EINVAL`.

## Control Flow
Higher-level operations use `safe_openat` for user-influenced overlay-relative paths. For syscalls that accept only a parent fd plus basename, callers first run `open_parent_safe_cstr`, then pass the returned raw parent fd and basename to `mknodat`, `renameat`, `unlinkat`, and related wrappers. Trusted setup code bypasses openat2 through `open_trusted`.

## State And Persistence
The module owns fd lifetimes through `OwnedFd`/`SafeFd` but writes no persistent state directly. It affects persistence indirectly by ensuring subsequent operations target paths contained under a layer root.

## Dependencies And Integration Points
`overlay.rs` uses `safe_parent` for setattr, create, mknod, mkdir, symlink, rename, link, hide, fsyncdir, and xattr path construction. `whiteout.rs` uses it for whiteout creation/deletion and opaque sentinels. Datasources use it for safe layer access.

## Risks
`openat2` is Linux-specific and requires kernel support; failure propagates without a compatibility fallback for untrusted paths. `proc_fd_path` relies on `/proc/self/fd` availability. `open_parent_safe` treats an empty parent before a slash poorly if given malformed paths; callers should provide normalized relative paths. `file_exists_at` reads errno via libc internals and is Linux/glibc-specific.

## Test Signals
No direct unit tests in this file. Coverage is indirect through nearly every integration test that creates, renames, deletes, copies up, or whiteouts nested paths without escaping layer roots.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/sys/openat2.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/sys/process.rs -->
# sources/cloud-native/fuse-overlayfs/src/sys/process.rs

## Purpose
`sys/process.rs` contains process-level libc wrappers for daemonization and effective-UID discovery.

## Important APIs, Types, And Functions
`daemonize` forks, exits the parent, creates a new session, redirects stdin/stdout/stderr to `/dev/null`, closes the extra fd, and changes directory to `/`. `geteuid` returns the current effective UID.

## Control Flow
Mount setup can call `daemonize` before worker threads exist. On fork, the parent exits successfully while the child detaches. Any fork, setsid, or dup2 failure logs and exits with status 1.

## State And Persistence
This changes process identity/lifecycle state, stdio fds, session membership, and cwd. It writes no filesystem state except opening `/dev/null`.

## Dependencies And Integration Points
The CLI/mount layer uses this module when running in background mode and for privilege decisions. It depends on libc and `log::error`.

## Risks
`daemonize` exits the process on failure and should only run before multi-threading. It does not do a double fork, write pidfiles, or report child startup success to the parent. Redirecting stdio can hide later diagnostics unless logging is configured elsewhere.

## Test Signals
No direct tests. Container-driven mount tests indirectly require foreground/background process behavior in normal fuse-overlayfs invocation paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/sys/process.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/sys/statx.rs -->
# sources/cloud-native/fuse-overlayfs/src/sys/statx.rs

## Purpose
`sys/statx.rs` converts Linux `statx` results into traditional `libc::stat` and re-exports statx mask constants used by datasource and overlay metadata paths.

## Important APIs, Types, And Functions
`statx_to_stat` maps device, inode, mode, nlink, uid/gid, rdev, size, block size/count, and atime/mtime/ctime fields. Constants include `STATX_TYPE`, `STATX_MODE`, `STATX_INO`, and `STATX_BASIC_STATS`.

## Control Flow
Callers perform `statx`, then call `statx_to_stat` when they need the legacy `stat` shape expected by overlay attribute logic.

## State And Persistence
The module is pure conversion logic with no state and no writes.

## Dependencies And Integration Points
`overlay.rs` requests these masks when statting layer entries and converts stats to `fuser::FileAttr`. Datasource implementations likely bridge `statx` to `stat` with this helper.

## Risks
Field conversions are architecture-sensitive, especially device ids, nanosecond timestamps, and signedness/width of libc stat fields. Birth time and extended statx fields are intentionally not propagated.

## Test Signals
No direct tests in this file. Integration tests validate metadata presentation for mode, uid/gid, nlink, device rdev, timestamps, and file sizes through `stat`.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/sys/statx.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/sys/xattr.rs -->
# sources/cloud-native/fuse-overlayfs/src/sys/xattr.rs

## Purpose
`sys/xattr.rs` provides checked wrappers around Linux extended-attribute libc calls for fd-based and symlink-preserving path-based xattr operations.

## Important APIs, Types, And Functions
Exports are `fgetxattr`, `lgetxattr`, `fsetxattr`, `lsetxattr`, `llistxattr`, `flistxattr`, and `lremovexattr`.

## Control Flow
Each wrapper converts names and paths to C strings where required, passes Rust buffers to libc, checks negative results, and returns either byte counts, unit, or `FsError`.

## State And Persistence
Persistent effects are xattr writes and removals on files, directories, symlinks, whiteout/opaque markers, ACL metadata, stat override metadata, and user-visible attributes.

## Dependencies And Integration Points
`overlay.rs` uses these wrappers for xattr FUSE operations, ACL inheritance, stat override read/write, and path-based lset/lremove via `/proc/self/fd`. `whiteout.rs` uses `fsetxattr` for opaque directories. `xattr.rs` decides which names are allowed or encoded before these syscalls are called.

## Risks
Path-based wrappers preserve symlinks (`l*`) but do not themselves provide root containment; callers must use safe fd/proc paths. Fixed caller buffers can produce `ERANGE`. Name/path conversion rejects interior NUL bytes. Namespace permissions differ for `trusted.*`, `security.*`, and rootless/container modes.

## Test Signals
No direct unit tests here. `src/xattr.rs` tests cover name policy, while `test-copyup.sh`, `test-dir-ops.sh`, `test-readonly.sh`, `fedora-installs.sh`, and special-file tests exercise xattr preservation, opaque markers, large xattrs, ACL/stat override behavior, and user xattr visibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/sys/xattr.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/whiteout.rs -->
# sources/cloud-native/fuse-overlayfs/src/whiteout.rs

## Purpose
`whiteout.rs` implements overlay whiteout and opaque-directory operations for both privileged kernel-overlay style and unprivileged fallback style.

## Important APIs, Types, And Functions
`is_directory_opaque` detects opacity via `trusted.overlay.opaque`, `user.overlay.opaque`, `user.fuseoverlayfs.opaque`, or `.wh..wh..opq`. `set_fd_opaque` writes an opaque xattr and creates the sentinel file. `delete_whiteout` removes existing char-device and `.wh.<name>` whiteouts. `create_whiteout` creates a char device `(0,0)` when allowed, otherwise falls back to a regular `.wh.<name>` file. Static `CAN_MKNOD` disables future mknod attempts after permission/support failures.

## Control Flow
Directory merge code calls `is_directory_opaque` to stop lower-layer lookup. Creation and rename paths call `delete_whiteout` when recreating a name. Removal and lower-layer rename paths call `create_whiteout` to hide lower entries. New directories under copied-up lower parents call `set_fd_opaque` so old lower contents do not reappear.

## State And Persistence
Persistent state is encoded as xattrs, `.wh..wh..opq` sentinel files, char-device `(0,0)` whiteouts, or `.wh.<name>` files in the upper layer. In-memory state is limited to `CAN_MKNOD`, which records process-wide fallback from mknod to `.wh.` files.

## Dependencies And Integration Points
The module depends on datasource xattr/file-existence APIs, `sys::fs`, `sys::xattr`, `sys::openat2`, and constants from `xattr.rs`. It is tightly integrated with `overlay.rs` directory loading, deletion, mkdir, create, link, and rename behavior.

## Risks
Privilege and filesystem differences mean mknod and trusted xattrs can fail; fallback logic must remain correct. Whiteout deletion must avoid removing non-whiteout real files. Opaque detection order affects multi-layer merge semantics. Sentinel creation through `safe_openat` requires openat2 support. `CAN_MKNOD` is global, so one EPERM/ENOTSUP switches the process to fallback whiteouts for later operations.

## Test Signals
`test-dir-ops.sh` covers opaque xattrs, `.wh..wh..opq`, char-device or `.wh.` whiteouts, rmdir whiteouts, mkdir over whiteouts, and readdir filtering. `test-rename.sh` validates whiteout creation for renamed lower files. `fedora-installs.sh` includes regressions for multi-layer whiteouts and opaque sentinels.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/whiteout.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/xattr.rs -->
# sources/cloud-native/fuse-overlayfs/src/xattr.rs

## Purpose
`xattr.rs` defines overlay xattr namespaces and policy for hiding internal attributes, encoding otherwise-hidden attributes in container stat-override mode, and filtering listxattr results.

## Important APIs, Types, And Functions
Constants define internal prefixes and names: `user.fuseoverlayfs.*`, `user.overlay.*`, `trusted.overlay.*`, `user.containers.override_`, `security.`, and `.wh..wh..opq`. `can_access_xattr` decides whether a user-facing name is visible. `is_encoded_xattr_name`, `decode_xattr_name`, `encode_xattr_name`, and `filter_xattr_list` transform names according to `StatOverrideMode`.

## Control Flow
FUSE xattr operations call `encode_xattr_name` before get/set/remove and `filter_xattr_list` after listing raw layer xattrs. In containers mode, inaccessible internal names may be stored under the `user.containers.override_` prefix and decoded when listed.

## State And Persistence
The module is stateless policy logic. Persistent effects happen when encoded names are passed to `sys::xattr` from overlay operations.

## Dependencies And Integration Points
`overlay.rs` uses it in FUSE xattr callbacks. `whiteout.rs` uses constants for opaque xattrs and sentinels. The datasource stat override mode determines whether privileged/internal names can be encoded instead of rejected.

## Risks
Incorrect filtering can expose overlay internals or hide legitimate user attributes. The 255-byte xattr-name limit is enforced only for encoded names. Invalid UTF-8 names in list buffers are silently skipped. Containers mode hides `security.*`, which affects SELinux-like labels.

## Test Signals
Unit tests cover access policy, decode behavior, encode behavior, and filtering of null-separated list buffers. Integration tests cover user xattrs, large xattrs, opaque markers, and stat override behavior through FUSE.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/xattr.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/alpine.sh -->
# sources/cloud-native/fuse-overlayfs/tests/alpine.sh

## Purpose
`tests/alpine.sh` builds the project Alpine container image and runs the unlink test inside it, validating behavior in an Alpine/musl container environment.

## Important APIs, Types, And Functions
The script selects `docker` or `podman`, builds `../Containerfile.alpine` as `fuse-overlayfs:alpine`, then runs the image privileged with `/unlink.sh` mounted from the test directory and `EXPECT_UMOUNT_STATUS=1`.

## Control Flow
It changes to the test directory, enables shell tracing/errors, detects a container runtime, builds the image from the repository root context, and runs the test entrypoint in `/tmp`.

## State And Persistence
Persistent host state is limited to the local container image tag and any runtime build cache. The container run is `--rm`; test filesystem state is inside the container except the mounted unlink script.

## Dependencies And Integration Points
Depends on Docker or Podman, privileged container execution, `Containerfile.alpine`, and `tests/unlink.sh`. It validates packaging/runtime compatibility rather than a narrow Rust function.

## Risks
Requires privileged container support and network/package availability during image build. Runtime choice changes behavior between Docker and Podman. Failures can be environmental rather than code regressions.

## Test Signals
Pass means the Alpine image builds and the unlink/umount scenario completes with the expected status. It indirectly exercises mount, unlink, and cleanup behavior in a distribution-specific environment.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/alpine.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/fedora-installs.sh -->
# sources/cloud-native/fuse-overlayfs/tests/fedora-installs.sh

## Purpose
`tests/fedora-installs.sh` is a broad real-world integration regression script that runs Fedora package-manager workloads and many historical overlayfs edge cases against fuse-overlayfs.

## Important APIs, Types, And Functions
The script detects Docker/Podman and Python, mounts fuse-overlayfs with escaped colons, `sync=0`, `threaded=1`, `suid`, `dev`, `fast_ino_check`, readonly lower-only mode, and multiple lowerdirs. It compiles `suid-test.c`, runs Fedora `dnf` installs into the merged root, checks xattrs with `setfattr/getfattr`, creates Unix sockets, uses tar, creates whiteouts/opaque sentinels, validates symlink and timestamp behavior, checks name length limits, and tests open-deleted-file access through `/proc/<pid>/fd`.

## Control Flow
The script stages lower/upper/workdir/merged directories, performs a Fedora install into a writable overlay, remounts upper as a lower layer, runs suid behavior checks, installs larger packages, removes package-managed trees, verifies readonly errors, then runs a sequence of named GitHub issue regressions around whiteouts, opaque dirs, symlinks, directory nlink, timestamps, long names, linked deleted files, rename/whiteout cleanup, recreated directories, special files, and copy/rename directory cases.

## State And Persistence
It creates and destroys multiple overlay directory trees, a static `suid-test` binary, package-manager install roots, xattrs, sockets, special files, and container runtime state. It intentionally moves `upper:2` to `lower` to simulate committed layer reuse.

## Dependencies And Integration Points
Depends on fuse-overlayfs in PATH, Fedora container image, container runtime, GCC, Python, xattr tools, tar, mknod, attr, package network access, and sufficient privileges for `suid`/`dev` cases. It exercises almost every major integration point in `overlay.rs`, whiteout handling, xattr handling, and syscall wrappers.

## Risks
This is environment-heavy and can fail because of Fedora image/package changes, network failures, privilege restrictions, long runtime, or missing host tools. It also contains a suspicious check after the issue 143 setup that tests `merged/dir1/dir2/foo` even though that path is not created in that scenario, so that assertion may be legacy/no-op-like rather than targeted.

## Test Signals
Strong pass signal for package-manager compatibility, copy-up durability, suid bit handling, directory nlink, xattr propagation, readonly EROFS behavior, multi-layer whiteouts, opaque sentinels, symlink metadata, max filename reservation for `.wh.`, open deleted file lifetime, and historical regressions for issues 136, 138, 143, 151, 279, 306, 337, and 444.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/fedora-installs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/suid-test.c -->
# sources/cloud-native/fuse-overlayfs/tests/suid-test.c

## Purpose
`tests/suid-test.c` is a small helper used by Fedora integration tests to distinguish preserved setuid bits from setuid bits cleared by writes after chmod.

## Important APIs, Types, And Functions
`main` unlinks `suid` and `nosuid`, creates each with `open(O_WRONLY | O_CREAT | O_EXCL)`, writes data, calls `fchown(fd, 0, 0)`, applies `fchmod(fd, S_ISUID | 0755)`, and for `nosuid` performs an extra write after chmod before closing.

## Control Flow
The first file is chmodded setuid and closed without further writes. The second is chmodded setuid and then written again, which should trigger kernel privilege-bit clearing semantics.

## State And Persistence
It creates two files in the current working directory of the mounted overlay. Their resulting modes are checked by `fedora-installs.sh` in the upper layer.

## Dependencies And Integration Points
Depends on libc/POSIX file APIs and sufficient privilege or mount behavior to allow chown/chmod. It integrates with overlay write handling, especially code that preserves setuid/setgid for writeback-cache writepage but not normal user writes.

## Risks
Return values are not checked, so failures can lead to misleading downstream mode checks. It assumes running as root or with permissions that make `fchown(0,0)` and setuid chmod meaningful.

## Test Signals
`fedora-installs.sh` expects `upper/suid` to retain setuid and `upper/nosuid` not to retain it, validating correct privilege-bit behavior around writes.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/suid-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-copyup.sh -->
# sources/cloud-native/fuse-overlayfs/tests/test-copyup.sh

## Purpose
`tests/test-copyup.sh` validates copy-up behavior for regular files, metadata, symlinks, xattrs, directories, open-for-write, truncate, nested paths, and repeated copy-ups.

## Important APIs, Types, And Functions
The script uses `fuse-overlayfs`, `dd`, `md5sum`, `chmod`, `touch`, symlink commands, `setfattr/getfattr`, Python file I/O, `truncate`, and shell loops. Cleanup unmounts and removes a temporary test directory.

## Control Flow
Each test creates fresh lower/upper/workdir/merged directories, mounts a writable overlay, triggers copy-up by write/chmod/create/truncate/open, validates merged and upper-layer effects, unmounts, and resets. Scenarios cover content preservation for a 400 KiB file, permission/timestamp copy-up, symlink target behavior, xattr preservation before and after copy-up, directory and nested directory copy-up, write-open copy-up, truncation, and twenty sequential copy-ups.

## State And Persistence
Persistent state is test-local lower, upper, workdir, merged content. The key persisted artifact under validation is the upper-layer copy created from lower-layer input.

## Dependencies And Integration Points
Exercises `OverlayInner::get_node_up`, `copyup::copyup`, `open`, `setattr`, `create`, `xattr` wrappers, directory creation, and path-safe upper-layer operations. Requires xattr tools and Python.

## Risks
Some metadata tests only assert existence rather than exact preserved mode/timestamp, so regressions could slip through. `md5sum` checks only the original prefix after append. Environment must support FUSE and user xattrs.

## Test Signals
Pass indicates copy-up preserves data and user xattrs, keeps symlinks usable, creates upper nested directory structure, supports open-for-write and truncate copy-up paths, and handles multiple files without cross-contamination.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-copyup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-dir-ops.sh -->
# sources/cloud-native/fuse-overlayfs/tests/test-dir-ops.sh

## Purpose
`tests/test-dir-ops.sh` validates directory merge semantics, opaque directories, whiteout filtering, nlink computation, removal/recreation, nested operations, readdir correctness, and lower-layer priority.

## Important APIs, Types, And Functions
The script repeatedly mounts `fuse-overlayfs` over fresh test trees and uses mkdir, rm/rmdir, mknod/touch whiteouts, setfattr opaque markers, stat, grep, and ls counts.

## Control Flow
Fifteen isolated scenarios cover two-layer and three-layer merges, upper-over-lower shadowing, xattr and sentinel opaque directories, computed nlink and `static_nlink`, rmdir of lower content producing whiteouts, mkdir over deleted lower dirs, nested mkdir/rm, readdir updates after delete/add, whiteout filtering, rejecting non-empty rmdir, and multi-lower priority where the first lowerdir wins.

## State And Persistence
Creates temporary lower/upper/workdir/merged directories and persists whiteouts, opaque xattrs/sentinels, created dirs/files, and upper changes until each scenario cleanup.

## Dependencies And Integration Points
Directly exercises `load_dir_impl`, `do_lookup_file`, `reload_dir`, `build_dir_entries`, `do_rm`, `mkdir`, whiteout helpers, and nlink logic in `rpl_stat_with_path`. Requires FUSE, xattr tools, and optionally mknod.

## Risks
Directory listing counts depend on `ls` behavior and locale minimally. Char-device whiteout paths are conditional. The test focuses on visible behavior and does not inspect internal inode-table state.

## Test Signals
Pass is a strong signal for overlay directory layering semantics, opaque stop conditions, deletion hiding lower entries, correct readdir contents, nlink updates, and correct lowerdir ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-dir-ops.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-hardlinks.sh -->
# sources/cloud-native/fuse-overlayfs/tests/test-hardlinks.sh

## Purpose
`tests/test-hardlinks.sh` validates hardlink creation, shared data, link counts, unlink survival, cross-directory links, rename interaction, relinking, and lower-layer hardlink copy-up cycles.

## Important APIs, Types, And Functions
The script uses `ln`, `rm`, `mv`, `stat`, `chown`, and `grep` across fresh fuse-overlayfs mounts.

## Control Flow
It creates writable overlays and runs nine scenarios: basic hardlink creation, data sharing through links, removing one link, linking to a lower-layer file, multiple hardlinks, rename with hardlinks, cross-directory hardlinks, relink after delete, and a containers/storage-like flow where lower-layer hardlinked binaries are chowned, one link is removed, and links are recreated in both orders.

## State And Persistence
State lives in temporary lower/upper/workdir/merged trees. The critical persistent state is upper-layer copied-up hardlink topology and inode/link count consistency.

## Dependencies And Integration Points
Exercises `link`, `unlink`/`do_rm`, `rename`, copy-up, inode table registration, nlink calculation, and inode invalidation after unlinking one hardlink while survivors remain.

## Risks
Some link-count assertions use `-ge`, so they tolerate over-counting. The test does not inspect upper-layer inode equality after every copy-up, mostly merged view/content behavior.

## Test Signals
Pass indicates hardlinked overlay entries share data, survive unlink/rename/relink operations, and lower-layer hardlinks remain usable through chown/unlink/link cycles that previously caused container storage failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-hardlinks.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-mmap.sh -->
# sources/cloud-native/fuse-overlayfs/tests/test-mmap.sh

## Purpose
`tests/test-mmap.sh` validates that mmap-heavy dynamic linking/compilation works when lower layers can contain files with identical inode numbers on different backing filesystems.

## Important APIs, Types, And Functions
The script creates ext2 images with `truncate` and `mke2fs`, mounts them via `fuse2fs`, copies compiler shared-library dependencies split across the two filesystems, mounts fuse-overlayfs lower-only, and runs `gcc` with `LD_LIBRARY_PATH=mnt/`.

## Control Flow
It prepares two ext2-backed FUSE mounts, alternates copied `cc1` dependencies between them, overlays `ext2:ext1`, compiles a trivial C program against libraries resolved from the overlay, and cleans up all mounts/images.

## State And Persistence
Temporary ext2 image files, fuse2fs mounts, overlay mount, copied libraries, and compiled `a.out` are created and removed. No repository state is changed.

## Dependencies And Integration Points
Depends on `mke2fs`, `fuse2fs`, GCC, `ldd`, FUSE, and shared-library availability. It integrates with inode mapping, read/mmap behavior, and lower-only overlay mode.

## Risks
Highly environment-sensitive: missing fuse2fs, mke2fs, GCC, or library paths will fail the test. It assumes copied dependencies are enough for a trivial compile. Cleanup prints `FAILED` on trapped exits, which can be noisy if unmounts fail.

## Test Signals
Pass indicates same-number backing inodes across layers do not break mmap/dynamic-link workloads through the overlay.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-mmap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-passthrough.sh -->
# sources/cloud-native/fuse-overlayfs/tests/test-passthrough.sh

## Purpose
`tests/test-passthrough.sh` validates inode passthrough, readdir `d_ino` consistency, xino stability, and behavior when layers are on the same filesystem, different filesystems, or nested FUSE mounts.

## Important APIs, Types, And Functions
It defines `fail` and `test_d_ino`, uses `stat`, `ls -li`, ext2 images, `mke2fs`, `fuse2fs`, and repeated fuse-overlayfs mounts with `lowerdir`, `xino=auto`, and `xino=off`.

## Control Flow
First it overlays same-filesystem lower/upper trees and asserts merged inode numbers match direct access and `ls` d_ino values. Then it creates two ext2 filesystems where first files intentionally share `st_ino`, verifies merged inode uniqueness, checks non-stable behavior across mounts with different filesystems, verifies `xino=auto` produces stable inode numbers across remounts, and confirms double-FUSE layers disable xino/export-like stability expectations.

## State And Persistence
Temporary lower/upper/mnt trees, ext2 image files, fuse2fs mounts, and nested overlay mounts are created and removed. Inode values are sampled and compared across remounts.

## Dependencies And Integration Points
Exercises `OverlayFs::new` same-device detection, inode table mapping, `get_st_ino_with_path`, NFS/filehandle/xino behavior, readdirplus/direntry inode reporting, and FUSE export capability negotiation. Depends on `fuse2fs`, `mke2fs`, FUSE, and stat/ls formats.

## Risks
The test assumes ext2 first-file inode equality; it fails with an explicit message if that setup assumption breaks. Some non-stability cases are informational and do not require difference. Host FUSE capability differences can affect double-FUSE expectations.

## Test Signals
Pass gives strong evidence that inode passthrough is correct on same-device layers, duplicate lower inode numbers are disambiguated across devices, and `xino=auto` gives stable remount-visible inodes when supported.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-passthrough.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-readonly.sh -->
# sources/cloud-native/fuse-overlayfs/tests/test-readonly.sh

## Purpose
`tests/test-readonly.sh` validates lower-only readonly overlays and selected mount options for id mapping, squash modes, symlinks, special files, and volatile/fsync behavior.

## Important APIs, Types, And Functions
The script uses `fuse-overlayfs`, shell write operations expected to fail, `stat`, `chown`, symlink commands, `mkfifo`, optional `mknod`, and `sync`.

## Control Flow
Eight scenarios mount lower-only or writable overlays: readonly writes must fail while reads work; multiple lower layers merge; `squash_to_root` and `squash_to_uid/gid` alter visible ownership; `uidmapping`/`gidmapping` maps host ids; symlinks and special files are visible in readonly mode; volatile mode allows writes and tolerates sync behavior.

## State And Persistence
Temporary lower/upper/workdir/merged directories are created per scenario. Readonly scenarios should not persist upper changes because no upperdir exists; writable option tests create normal upper/workdir state.

## Dependencies And Integration Points
Exercises `upper_layer`/EROFS paths, metadata mapping in `rpl_stat_with_path`, symlink readlink, special-file type mapping, and fsync-disabled volatile behavior. Requires FUSE and optionally mknod privilege.

## Risks
Write-failure checks grep human-readable "read-only" messages, which can vary by locale/tool. Mapping tests require permission to chown prepared lower files. Volatile test accepts sync failure, so it only validates data remains readable before unmount.

## Test Signals
Pass indicates lower-only mounts reject mutation with readonly errors, multiple lowerdir merge works without upperdir, id/squash mapping affects visible stats, and symlink/special-file metadata remains intact.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-readonly.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-rename.sh -->
# sources/cloud-native/fuse-overlayfs/tests/test-rename.sh

## Purpose
`tests/test-rename.sh` validates rename behavior including lower-layer copy-up/whiteout, overwrite, cross-directory moves, recreate-after-rename, and Linux `renameat2` flags.

## Important APIs, Types, And Functions
The script compiles a helper C program that invokes `SYS_renameat2` with `RENAME_NOREPLACE` or `RENAME_EXCHANGE`. It also uses `mv`, `grep`, `stat`, and whiteout inspection.

## Control Flow
Ten scenarios cover upper-layer basic rename, renaming lower files with whiteout creation, renaming lower directories, overwrite of existing files, `RENAME_NOREPLACE` failure/success, `RENAME_EXCHANGE` for files and directories, renaming over lower-layer destination, cross-directory file moves, and recreating a lower name after it was moved.

## State And Persistence
Each scenario creates temporary lower/upper/workdir/merged state. Persistent upper effects include copied-up renamed files/directories, whiteouts at old names, replaced destination files, exchanged directory entries, and recreated names.

## Dependencies And Integration Points
Directly exercises `OverlayFs::rename`, `get_node_up`, `empty_upper_dir`, `whiteout::create_whiteout/delete_whiteout`, `renameat2` wrapper, inode table updates, parent cache invalidation, and directory reload behavior. Requires GCC and kernel/filesystem support for `renameat2` flags.

## Risks
If `renameat2` is unsupported, helper-driven tests fail as environmental failures. Directory lower-layer rename semantics are subtle; implementation currently rejects some lower/merged directory renames with `EXDEV`, so test expectations are important to keep aligned with actual supported behavior. Whiteout validation allows either char-device or `.wh.` format.

## Test Signals
Pass indicates rename paths maintain visible content, enforce no-replace, atomically exchange entries, generate whiteouts for lower source names, and keep directory/parent caches coherent after moves.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-rename.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-special-files.sh -->
# sources/cloud-native/fuse-overlayfs/tests/test-special-files.sh

## Purpose
`tests/test-special-files.sh` validates special-file creation and preservation plus fallocate, statfs, chmod, chown, truncate, timestamp updates, and directory metadata updates.

## Important APIs, Types, And Functions
The script checks host `mknod` capability, then uses `mknod`, `mkfifo`, Python Unix sockets, `fallocate`, `stat`, `chmod`, `chown`, `truncate`, `touch`, and standard fuse-overlayfs mounts.

## Control Flow
Fourteen scenarios cover creating char/block devices when permitted, FIFO creation, Unix socket bind, fallocate size growth, statfs output, chmod/chown/truncate of lower files through copy-up, timestamp updates on files and dirs, preserving lower-layer devices and FIFOs, and chmod/chown on directories.

## State And Persistence
Temporary overlay trees hold created devices, FIFOs, sockets, files, and metadata changes. Tests inspect merged view and sometimes lower/upper behavior indirectly.

## Dependencies And Integration Points
Exercises `mknod`, `create`, `fallocate`, `statfs`, `setattr`, type conversion in `mode_to_filetype`, device rdev preservation, copy-up for metadata operations, and raw syscall wrappers in `sys/fs.rs`/`sys/io.rs`. Requires FUSE, Python, and optional device-node privilege.

## Risks
Device-node tests are skipped when host privileges are insufficient. Some filesystems may not support fallocate as expected. Chown tests require privilege to set arbitrary owners. Socket test depends on Python and Unix-domain socket support.

## Test Signals
Pass indicates overlay operations preserve and create special file types correctly, report filesystem stats, and apply metadata/size/time changes through FUSE-visible paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-special-files.sh -->
