# sources/distributed-fs/ceph-client/fs/coda/dir.c

## Purpose
`dir.c` implements Coda directory VFS operations, permission checks, lookup/create/remove/rename/link/symlink/mkdir/rmdir operations, directory reading, and dentry/inode revalidation.

## Important APIs, Types, And Functions
Key functions include `coda_lookup()`, `coda_permission()`, `coda_create()`, `coda_mkdir()`, `coda_link()`, `coda_symlink()`, `coda_unlink()`, `coda_rmdir()`, `coda_rename()`, `coda_readdir()`, `coda_dentry_revalidate()`, `coda_dentry_delete()`, and `coda_revalidate_inode()`. It exports `coda_dentry_operations`, `coda_dir_inode_operations`, and `coda_dir_operations`.

## Control Flow
Directory mutations call corresponding Venus operations, then update local dentries, link counts, and directory mtime. Lookup handles the root `.CONTROL` pseudo-entry specially, otherwise asks Venus and materializes an inode. Permission checks use the kernel permission cache before `venus_access()`. Readdir first delegates to the container file's `iterate_dir()`; if that reports `-ENOTDIR`, it parses Venus directory records manually. Revalidation consumes Coda flags and refetches attributes from Venus.

## State, Persistence, And Dependencies
Directory state is split between local VFS dentries/inodes and authoritative Venus/server state. Coda invalidation flags (`C_VATTR`, `C_PURGE`, `C_FLUSH`) drive cache refresh. Dependencies include Venus upcalls, cnode creation, permission cache, dcache shrink/revalidation, and VFS link-count helpers.

## Integration Points
This is the main bridge from VFS directory operations to the Venus cache manager. It shares open/release/fsync with `file.c`, cnode materialization with `cnode.c`, and invalidation with `cache.c`.

## Risks
Risks include stale dentries after downcalls, manual Venus dirent parsing, link-count heuristics for volume mount points, unsupported rename flags, `.CONTROL` protection, and revalidation returning success for busy purged dentries until references drop.

## Test Signals
Test lookup, negative lookup, `.CONTROL`, create/mkdir/link/symlink/unlink/rmdir/rename, permission-cache hits and misses, readdir via host directory and Venus records, downcall purge/flush behavior, and RCU lookup fallback.
