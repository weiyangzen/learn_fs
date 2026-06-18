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
