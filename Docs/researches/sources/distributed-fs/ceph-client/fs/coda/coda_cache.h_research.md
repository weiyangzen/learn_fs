# sources/distributed-fs/ceph-client/fs/coda/coda_cache.h

## Purpose
`coda_cache.h` declares Coda permission-cache and invalidation helper functions shared between directory, downcall, and attribute paths.

## Important APIs, Types, And Functions
It declares `coda_cache_enter()`, `coda_cache_clear_inode()`, `coda_cache_clear_all()`, `coda_cache_check()`, and `coda_flag_inode_children()`.

## Control Flow
The header has no executable flow. Callers use the cache APIs around Venus access checks and use child flagging when a directory subtree needs purge, flush, or attribute invalidation.

## State, Persistence, And Dependencies
State is implemented in `cache.c`; this header only exposes the contract. It depends on VFS `struct inode` and `struct super_block` declarations through included users.

## Integration Points
`dir.c` uses the permission cache in `coda_permission()` and invalidation helpers in dentry/inode revalidation. Venus downcall code uses these declarations to invalidate kernel cache state.

## Risks
The API does not encode locking in types, so callers must rely on implementation semantics. Misuse can leave stale permissions or dentries visible.

## Test Signals
Build coverage and permission/invalidation integration tests validate that declarations remain aligned with `cache.c`.
