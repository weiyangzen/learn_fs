# sources/distributed-fs/openafs/src/WINNT/afsd/cm_scache.c

## Purpose
`cm_scache.c` implements the Windows cache manager's stat-cache lifecycle and synchronization core. It owns allocation/recycling of `cm_scache_t` objects, FID hash lookup, LRU management, callback/status invalidation, fetch/store synchronization, status merging, refcounting, validation, shutdown, and diagnostics.

## Important APIs and functions
- Global state: `cm_scacheLock`, `cm_allFileLocks`, `cm_freeFileLocks`, `cm_lockRefreshCycle`, `cm_fakeSCache`, and the free waiter list.
- `cm_RootSCachep()` obtains status/callback on the root scache before returning it.
- `cm_AdjustScacheLRU()`, `cm_RemoveSCacheFromHashTable()`, and `cm_RecycleSCache()` manage hash/LRU membership and object reset.
- `cm_GetNewSCache()` recycles an unused LRU entry or allocates from the preallocated scache arena.
- `cm_SetFid()` and `cm_FidCmp()` are the canonical FID construction/comparison helpers.
- `cm_InitSCache()`, `cm_ShutdownSCache()`, and `cm_SuspendSCache()` initialize locks/lists, release callbacks/resources, and handle suspend callback expiry.
- `cm_FindSCache()` and `cm_GetSCache()` provide held scache lookup/create paths, including freelance-root handling.
- `cm_SyncOp()` and `cm_SyncOpDone()` serialize status, data, callback, access-rights, lock, async-store, and bulk-read operations against a scache and optional buffer.
- `cm_MergeStatus()` merges `AFSFetchStatus` and `AFSVolSync` results into an scache, updates ACL/access caches, invalidates stale buffers, updates volume online state, and notifies the redirector.
- `cm_DiscardSCache()`, refcount helpers, `cm_FindFileType()`, `cm_ValidateSCache()`, and `cm_DumpSCache()` support invalidation, lifecycle safety, and diagnostics.

## Control flow
Lookup starts with a hash-table scan under `cm_scacheLock`. On miss, `cm_GetSCache()` obtains a new/recycled scache, resolves the cell and volume, rechecks the hash under write lock to avoid duplicate insertion, initializes RO/dotdot/parent state, inserts into the hash table, and returns a held reference. Freelance root and mountpoint entries bypass normal server status and synthesize local metadata.

Recycling walks the LRU tail, temporarily drops the global lock to inspect dirty or redirector-held buffers, tries the scache write lock, verifies LRU position did not change, removes hash membership, clears callbacks, ACLs, DNLC entries, mountpoint state, file locks, B+ directory state, flags, and FID fields, and optionally notifies the redirector of callback expiry.

`cm_SyncOp()` is the main concurrency gate. It requires the scache write lock, tests requested sync flags against current scache and buffer flags, obtains callbacks and access rights when requested, and sleeps via a per-scache waiter queue if the operation conflicts. On success it marks scache flags and buffer I/O queues. `cm_SyncOpDone()` clears those marks, removes buffer queue entries, releases held buffers, and wakes waiters.

`cm_MergeStatus()` validates status, handles server-side error status, rejects stale non-RO data versions unless forced, updates file metadata and ACL caches, removes stale unreferenced clean buffers from hash tables, maintains `bufDataVersionLow`, sends redirector data-version invalidations when needed, marks fetch-status complete, and marks the backing volume online.

## State and persistence behavior
Stat-cache state is in-memory only, backed by the mapped `cm_data` arena and hash/LRU lists. Each scache stores FID, status fields, data-version ranges, callback server/expiry, access cache links, file-lock counters, buffer I/O queues, redirector buffer queues, wait queues, and B+ directory state. No scache state is persisted by this file, but it preserves dirty buffer state by avoiding recycle when dirty buffers exist and by not discarding dirty data on status invalidation.

## Dependencies and integration points
This file is central to the afsd subsystem. It depends on volume/cell lookup, callback management, DNLC, ACL cache, buffer cache, redirector invalidation, freelance root support, B+ directory trees, server refs, request flags, OpenAFS fetch-status structures, and OSI locks/queues. Its public functions are used by fetch/store, directory, SMB, redirector, callback, and daemon paths.

## Risks and edge cases
- Lock ordering is complex: the code intentionally drops global locks around per-object locks, redirector invalidation, volume lookup, buffer checks, and callback operations. Regressions can deadlock.
- `cm_SyncOp()` can sleep with interactions between scache locks and buffer mutexes; missed `cm_SyncOpDone()` calls leave waiters dependent on the error wakeup path.
- Recycle decisions are race-sensitive and rely on LRU neighbor snapshots plus refcount/buffer checks.
- `cm_MergeStatus()` assumes valid `reqp` in redirector-invalidation checks; callers should not pass NULL if redirector support is active.
- Data-version arithmetic uses wrap-aware `dv_diff()` and active-RPC counts; incorrect flags can invalidate too much or too little cached data.
- Several diagnostic paths use fixed-size `sprintf` buffers with rich state strings.

## Test signals
High-value tests include duplicate lookup races, LRU recycle with dirty/redirector buffers, callback discard, redirector invalidation on data-version change, concurrent fetch/store/read/write conflicts, waiter wake ordering, `NOWAIT` behavior, stale data-version merges on RW versus RO files, ACL cache updates on access errors, directory B+ reset, suspend/shutdown callback release, and validation of hash/LRU/DNLC invariants.
