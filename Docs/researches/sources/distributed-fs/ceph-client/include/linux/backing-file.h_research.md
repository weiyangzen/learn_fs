# sources/distributed-fs/ceph-client/include/linux/backing-file.h

## Purpose
Declares common helpers for stackable filesystems that operate on real backing files while preserving the user file context and credentials.

## Important APIs, types, and functions
- `struct backing_file_ctx` carries the credentials used for backing access plus optional `accessed()` and `end_write()` callbacks.
- Open helpers: `backing_file_open()` and `backing_tmpfile_open()`.
- I/O helpers: `backing_file_read_iter()`, `backing_file_write_iter()`, `backing_file_splice_read()`, and `backing_file_splice_write()`.
- Mapping helper: `backing_file_mmap()`.

## Control flow and state
A stackable filesystem opens a backing file or tmpfile with explicit credentials, then routes read/write/splice/mmap operations through these helpers. The context callbacks let the caller mirror access-time or write-completion side effects back into the upper file/inode.

## State and persistence behavior
This header defines no storage itself. Persistent effects are delegated to the opened backing file and filesystem. Credential state is explicit and must be chosen by the stackable filesystem rather than inherited accidentally from the current task.

## Dependencies and integration points
Depends on `file.h`, `uio.h`, and `fs.h`. Integrated by overlay/stackable filesystem implementations and VFS iterator/splice/mmap paths.

## Risks
Credential confusion is the main risk: using the wrong `cred` can bypass or over-restrict access. Callback ordering must match actual I/O completion. The helper prototypes expose flags and iterators directly, so callers must respect VFS iterator ownership and partial-I/O semantics.

## Test signals
Tests should cover read/write/splice/mmap through stackable files with overridden credentials, partial I/O, permission-denied paths, atime updates, and delayed write completion callbacks.
