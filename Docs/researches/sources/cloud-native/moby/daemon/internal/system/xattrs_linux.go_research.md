# sources/cloud-native/moby/daemon/internal/system/xattrs_linux.go

## Purpose
Wraps Linux extended attribute operations with daemon-specific error context and no-follow semantics.

## Important APIs, Types, And Functions
`XattrError` stores operation, attribute, path, and underlying error, implements `Error`, `Unwrap`, and `Timeout`. `Lgetxattr` reads an xattr without following symlinks, starting with a 128-byte buffer and resizing on `ERANGE`. Missing attributes (`ENODATA`) return nil data and nil error. `Lsetxattr` writes an xattr and wraps failures.

## Control Flow
`Lgetxattr` retries size discovery using a zero-sized buffer when the initial buffer is too small, then performs the real read. All other syscall errors are wrapped.

## State And Persistence
`Lsetxattr` mutates xattrs on filesystem objects. `Lgetxattr` is read-only.

## Dependencies And Integration Points
Linux-only helper around `golang.org/x/sys/unix`. Used by layer/archive code that preserves xattrs and needs distinguishable path/attribute errors.

## Risks And Test Signals
Race between size discovery and second read can still produce `ERANGE` if the xattr changes concurrently; the loop handles initial ERANGE but not repeated growth after allocation. No tests are listed in this subset.
