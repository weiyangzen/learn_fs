# sources/cloud-native/containerd/internal/fsview/overlay_linux_test.go

## Purpose
Tests Linux-specific overlay behavior, especially xattr-based opaque directories and symlink resolution across layers.

## Important APIs, Types, And Functions
Tests create real directories, files, symlinks, and `user.overlay.opaque` xattrs, then call `FSMounts` over overlay lowerdir options and read/stat paths.

## Control Flow
Cases validate upper precedence, relative and absolute symlink targets, chained symlinks, cross-layer symlink target replacement, and file-over-directory replacement under opaque parents.

## State And Persistence
Uses temporary directories and Linux xattrs. No persistent state after test cleanup.

## Dependencies And Integration Points
Uses `golang.org/x/sys/unix` for xattrs, `io/fs`, `os`, `path/filepath`, and containerd mount/fsview APIs.

## Risks
Linux filesystem must support user xattrs. Tests do not directly cover trusted overlay xattrs, which may require elevated privileges.

## Test Signals
Strong signal for the hard parts of overlay path resolution and opaque-directory semantics.
