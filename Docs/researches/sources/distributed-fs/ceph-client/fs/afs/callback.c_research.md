# sources/distributed-fs/ceph-client/fs/afs/callback.c

## Purpose
`callback.c` handles AFS callback invalidation: mmap invalidation work, server-wide callback state reset, volume-level callback breaks, vnode-level callback breaks, and grouping callback break requests by volume.

## Important APIs, types, and functions
Public functions are `afs_invalidate_mmap_work()`, `afs_init_callback_state()`, `__afs_break_callback()`, `afs_break_callback()`, and `afs_break_callbacks()`. Internal helpers include `afs_volume_init_callback()`, `afs_lookup_volume_rcu()`, `afs_break_volume_callback()`, `afs_break_one_callback()`, and `afs_break_some_callbacks()`.

## Control flow
Server callback reset iterates volumes served by that server, clears expiry promises, and invalidates open mmaps. Individual callback breaks look up the relevant volume under RCU/seqlock protection, identify volume-wide breaks by zero vnode/unique, otherwise find matching inodes by fid and clear promises under vnode callback locks. File mmaps are unmapped asynchronously so future faults revalidate.

## State and persistence
Runtime state includes vnode callback promises, callback break counters, volume callback break counters, mmap tracking lists, server-volume expiry fields, and permit caches. No durable state exists; remote callbacks drive cache coherency.

## Dependencies and integration points
It integrates with `cmservice.c` callback RPC delivery, AFS inode lookup, volume/server lists, lock wait wakeups, pagecache/mmap invalidation, RCU, seqlocks, and workqueues.

## Risks and test signals
Risks include races with new inodes, RCU volume lookup retries, missed mmap invalidations, volume-wide breaks with missing volumes, and lock-state wakeups. Test signals include CB.CallBack for vnode and volume breaks, InitCallBackState, mmap invalidation under mapped files, deleted-file callbacks, lock callback wakeups, and concurrent volume tree mutations.
