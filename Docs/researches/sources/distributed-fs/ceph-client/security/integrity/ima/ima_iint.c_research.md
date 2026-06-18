<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_iint.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_iint.c

## Purpose
Manages the per-inode IMA integrity cache stored through the inode LSM security blob.

## Important APIs, Types, And Functions
- `ima_iint_find()` returns an existing cache only when `S_IMA` is set.
- `ima_inode_get()` allocates and attaches a new `ima_iint_cache`.
- `ima_inode_free_rcu()` frees cache data during inode security RCU cleanup.
- `ima_iintcache_init()` creates the slab cache.

## Control Flow
Callers holding the inode lock request an iint with `ima_inode_get()`. If none exists, the code allocates from `ima_iint_cache`, initializes flags/statuses/hash/version, annotates the mutex lock class by filesystem stack depth, sets `S_IMA`, and stores the pointer in the inode security blob. Freeing occurs later through the LSM inode-free RCU hook.

## State And Persistence
The cache is volatile per-inode state. It persists while the inode exists and stores collected hash data, version/change-cookie data, measurement flags, appraisal statuses, and atomic invalidation flags.

## Dependencies And Integration Points
Depends on LSM blob sizing from `ima_blob_sizes`, slab allocation, lockdep, filesystem stack depth, and the `S_IMA` inode flag. `ima_main.c`, `ima_api.c`, and `ima_appraise.c` all rely on this cache.

## Risks And Edge Cases
Allocation failure causes IMA operations to fail or skip enforcement depending on caller context. Lockdep class assignment must account for overlay/stacked filesystems to avoid false positives. RCU cleanup assumes the security blob still contains the pointer slot.

## Test Signals
Runtime signals include successful measurement/appraisal caching, no leaks on inode eviction, stable behavior on overlayfs, and lockdep remaining quiet for nested IMA operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_iint.c -->
