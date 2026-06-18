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
