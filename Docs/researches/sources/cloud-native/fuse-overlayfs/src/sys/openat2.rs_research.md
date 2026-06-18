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
