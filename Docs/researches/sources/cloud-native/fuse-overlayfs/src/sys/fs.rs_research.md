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
