# sources/distributed-fs/ceph-client/fs/cachefiles/cache.c

## Purpose
`cache.c` manages high-level VFS lifecycle for a CacheFiles cache: binding a configured directory, validating the backing filesystem, registering with FS-Cache, enforcing free-space thresholds, and withdrawing the cache cleanly.

## Important APIs, Types, and Functions
The public functions are `cachefiles_add_cache`, `cachefiles_has_space`, and `cachefiles_withdraw_cache`. Important internal helpers are `cachefiles_withdraw_objects`, `cachefiles_withdraw_fscache_volumes`, `cachefiles_withdraw_volumes`, and `cachefiles_sync_cache`.

## Control Flow
`cachefiles_add_cache` acquires an FS-Cache cache cookie, prepares security credentials, resolves the configured root directory, rejects idmapped or read-only mounts and unsupported backing filesystems, computes file/block culling thresholds from `statfs`, creates or opens `cache` and `graveyard` directories, then calls `fscache_add_cache` and marks `CACHEFILES_READY`. `cachefiles_has_space` uses `statfs`, subtracts in-flight `b_writing`, compares remaining files/blocks against stop/cull/run thresholds, toggles `CACHEFILES_CULLING`, and returns `-ENOBUFS` for allocation stops. Withdrawal first unregisters the FS-Cache cache, withdraws active volume cookies, withdraws objects, waits for object cleanup, releases CacheFiles volumes, syncs the backing filesystem, and relinquishes the FS-Cache cookie.

## State and Persistence Behavior
Persistent state is the backing directory tree under the configured root, including live cache and graveyard directories. Runtime state in `struct cachefiles_cache` includes mount/dentry pointers, threshold percentages and absolute thresholds, ready/dead/culling flags, volume/object lists, released counters, and in-flight block-write accounting.

## Dependencies and Integration Points
This file depends on VFS path lookup, statfs, mount and superblock operations, FS-Cache cache registration/withdrawal, CacheFiles directory helpers, security credential override helpers, and tracepoints. It is invoked by daemon `bind`/release flow and by I/O allocation checks.

## Risks and Edge Cases
Backing filesystem capability checks are safety critical: missing `tmpfile`, xattr, statfs, sync, directory, or DIO-compatible blocksize support would corrupt later assumptions. Free-space logic must account for pending writes or CacheFiles can overcommit. Withdrawal must avoid racing object and volume access counts and must not free cache state before on-demand or FS-Cache users have quiesced.

## Test Signals
Test binding on supported and unsupported backing filesystems, read-only and idmapped mounts, low-free-space culling transitions, `statfs` failure injection, bind/unbind under active objects, and sync failure handling. Tracepoints and `cachefilesd` poll/read output expose culling state changes.
