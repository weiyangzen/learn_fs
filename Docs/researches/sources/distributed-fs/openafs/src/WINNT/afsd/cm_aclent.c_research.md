# sources/distributed-fs/openafs/src/WINNT/afsd/cm_aclent.c

## Purpose
`cm_aclent.c` implements the Windows cache-manager ACL entry cache. It stores per-user random access rights for scache objects, expires entries according to token/TGT lifetime, maintains an LRU queue over a fixed memory-mapped entry array, invalidates redirector objects/volumes when credentials change, and validates internal pointer integrity.

## Important APIs And State
The global lock is `cm_aclLock`. Main functions are `cm_InitACLCache`, `cm_FindACLCache`, `cm_AddACLCache`, `cm_FreeAllACLEnts`, `cm_InvalidateACLUser`, `cm_ResetACLCache`, `cm_ValidateACLCache`, `cm_ShutdownACLCache`, `cm_TGTLifeTime`, and internal `GetFreeACLEnt`/`CleanupACLEnt`. Entries are `cm_aclent_t` records from `cm_aclent.h` linked both in a global LRU queue and in each scache's `randomACLp` list.

## Control Flow
Initialization creates the lock once and, for a new cache file, zeroes the ACL memory region, stamps every entry with `CM_ACLENT_MAGIC`, and links all entries into the LRU queue. Reopening an existing cache clears user pointers and token lifetimes. `cm_AddACLCache` computes the user's token lifetime for the scache cell, updates an existing user entry or evicts the LRU tail, links the entry into the scache list, holds the user, stores rights and lifetime, and moves it to the LRU head. `cm_FindACLCache` scans the scache list under scache write lock and `cm_aclLock`; expired entries are cleaned and moved to the LRU tail, while hits return rights and move to the LRU head.

Invalidation can target all entries for one scache, one user on one scache, or all scaches/volumes for a user and optional cell. `cm_ResetACLCache` scans the scache hash table, invalidates matching user entries, clears EACCES cache entries, and asks the redirector to invalidate objects and volumes with `AFS_INVALIDATE_CREDS`. Validation walks the LRU queue forward and backward, checking pointer ranges, magic values, and loops.

## Dependencies And Integration
The file depends on global `cm_data` memory layout, scache/user/cell/volume structures, OpenAFS locks and queues, token/user cell state, callback checks, redirector invalidation (`RDR_InvalidateObject`, `RDR_InvalidateVolume`), and EACCES cache clearing. It is integrated with status fetches that populate `CallerAccess` and with token-change paths in user/ioctl code.

## Risks And Test Signals
Correctness depends on strict lock ordering between scache locks and `cm_aclLock`; `GetFreeACLEnt` temporarily drops and reacquires the ACL lock to lock an evicted entry's scache. Stale pointer validation assumes the memory-map region ordering of acl/scache/dnlc base addresses. Expiration depends on user token lifetime and can force server refetch after token renewal/loss. Test signals include cold and reopened cache initialization, LRU hit/miss/eviction order, expired entry cleanup, user reference hold/release balance, invalidate-one-user behavior with redirector callback, reset by cell and global reset, validation failures for corrupted queues, and token-renewal-driven ACL invalidation.
