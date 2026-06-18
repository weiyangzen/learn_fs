# sources/distributed-fs/ceph-client/fs/coda/cache.c

## Purpose
`cache.c` implements Coda's small in-kernel permission cache and dentry/inode invalidation helpers used when Venus downcalls indicate cached state is stale.

## Important APIs, Types, And Functions
Public functions are `coda_cache_enter()`, `coda_cache_clear_inode()`, `coda_cache_clear_all()`, `coda_cache_check()`, and `coda_flag_inode_children()`. Global state is `permission_epoch`; per-inode state lives in `struct coda_inode_info` fields protected by `c_lock`.

## Control Flow
Permission checks store the current fsuid, granted mask, and epoch. Later checks hit only if the same fsuid has all requested mask bits and the epoch still matches. Clearing one inode sets a stale epoch; clearing all increments the global epoch. Child invalidation finds an alias dentry for a directory, flags child inodes, shrinks child dentries, and drops the alias.

## State, Persistence, And Dependencies
State is volatile kernel cache only. It depends on current credentials, dentry aliases, RCU dentry traversal, spinlocks, and VFS dcache shrinking.

## Integration Points
`dir.c` permission and revalidation use this cache; Venus downcalls and Coda invalidation paths use child flagging to propagate `C_PURGE`, `C_FLUSH`, or `C_VATTR` effects.

## Risks
Permission caching is fsuid-specific and mask-based; stale invalidation depends on epoch updates and child flag propagation. Dentry traversal must avoid unsafe negative dentry handling and respect locking/RCU rules.

## Test Signals
Test repeated permission hits/misses by uid/mask, global and per-inode invalidation, downcall purge/flush propagation, directory child dentry shrinking, and lockdep/RCU validation.
