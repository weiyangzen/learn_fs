<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/writable/writable.go -->
# sources/distributed-fs/ipfs-kubo/fuse/writable/writable.go

## Purpose

This file implements the shared writable FUSE adapter for MFS-backed mounts. `/mfs` and local `/ipns` directories use it to expose MFS directories, files, and UnixFS symlinks as POSIX-like writable filesystems.

## Important APIs, Types, and Functions

`Config` controls metadata persistence, DAG access, repo statfs path, and block-size hints. `NewDir` validates the DAG and normalizes block size. `Dir` implements getattr/statfs/setattr/lookup/readdir/mkdir/unlink/rmdir/rename/create/xattr/symlink. `FileInode` implements getattr/open/setattr/xattr. `FileHandle` serializes read/write/flush/release/fsync around an MFS descriptor. `Symlink` implements readlink/getattr/setattr. `roFileHandle` provides snapshot reads via DagReader. `SymlinkTarget` detects UnixFS symlink nodes represented as MFS files.

## Control Flow, State, and Integration

Directory operations delegate to boxo MFS, then flush where needed. `Rename` unlinks before add and is explicitly non-atomic. `Create` adds an empty UnixFS file, opens an MFS descriptor, and fills attrs to avoid kernel zero caching. Read-only opens bypass MFS's descriptor lock by creating a DagReader from the current DAG node; write opens use MFS descriptors and handle `O_TRUNC` and `O_APPEND`. Flush, release, and fsync invalidate go-fuse kernel caches. Metadata writes persist UnixFS optional mode/mtime when configured.

## Dependencies, Risks, and Test Signals

Dependencies include go-fuse, boxo MFS, UnixFS DAG helpers, Kubo mount constants, and IPLD DAG services. Risks include non-atomic rename data loss on mid-operation failure, deadlocks if read-only opens use MFS locks, stale kernel caches after writes, sparse write semantics, symlink metadata limitations, StoreMode dropping high permission bits, and statfs path errors. The shared writable suite plus writable unit tests cover these risks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/writable/writable.go -->
