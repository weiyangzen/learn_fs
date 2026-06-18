<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/quota.h -->
# sources/distributed-fs/ceph-client/fs/gfs2/quota.h

## Purpose
`quota.h` declares the clustered quota API used by GFS2 allocation, inode, xattr, directory, superblock, and mount code.

## Important APIs, types, and functions
It defines sentinel uid/gid values `NO_UID_QUOTA_CHANGE` and `NO_GID_QUOTA_CHANGE`. It declares qadata lifetime functions, hold/unhold, lock/unlock, check/change, sync/refresh, init/cleanup, quotad, statfs wake, quotactl ops, qd shrinker setup/teardown, global qd LRU, and quota hash initialization. The inline `gfs2_quota_lock_check` combines common allocation behavior: assume unlimited allocation, bypass quotas when off or caller has `CAP_SYS_RESOURCE`, lock quota qds, skip enforcement in account-only mode, otherwise run `gfs2_quota_check` and unlock on failure.

## Control Flow
Allocation callers typically call `gfs2_quota_lock_check` before reserving or allocating blocks, then call `gfs2_quota_change` inside the transaction and `gfs2_quota_unlock` afterward. More complex ownership-change or metadata paths can call hold/lock/check/change/unlock directly.

## State and Persistence
No state is defined here except external declarations. The API controls state maintained by `quota.c`: inode qadata, qd cache/LRU/hash, quota glock LVBs, per-node quota_change slots, and shared quota records.

## Dependencies and Integration Points
The header depends on `list_lru.h` and GFS2 core structs. It is consumed by mount/module initialization, allocation and free paths, inode operations, file writes, xattr changes, directory operations, sysfs-triggered sync, and superblock read-only transitions.

## Risks
Callers must pair lock/hold APIs correctly and must call `gfs2_quota_unlock` to drop glocks and potentially sync local deltas. Bypassing the inline for privileged or quota-off cases is valid, but bypassing `gfs2_quota_change` after allocation/free is not. `GFS2_QUOTA_ACCOUNT` records usage but intentionally skips enforcement.

## Test Signals
Compile coverage of all quota clients, allocation failure due to hard limits, account-only mode, privileged allocation bypass, owner change with old/new ids, cleanup of qadata references, and lockdep coverage of quota lock/unlock pairing are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/quota.h -->
