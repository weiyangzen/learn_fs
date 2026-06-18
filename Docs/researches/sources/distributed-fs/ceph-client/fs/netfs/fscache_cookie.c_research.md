<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/fscache_cookie.c -->
# sources/distributed-fs/ceph-client/fs/netfs/fscache_cookie.c

## Purpose
Implements FS-Cache data-object cookie lifetime management. A cookie represents one cached netfs object inside a volume; this file handles allocation, key hashing, duplicate detection, asynchronous lookup/create/invalidate/withdraw/relinquish transitions, LRU discard, procfs inspection, and exported cookie reference/access APIs.

## Important APIs, Types, And Functions
Key exports are `__fscache_acquire_cookie()`, `__fscache_use_cookie()`, `__fscache_unuse_cookie()`, `__fscache_relinquish_cookie()`, `__fscache_invalidate()`, `fscache_begin_cookie_access()`, `fscache_end_cookie_access()`, `fscache_withdraw_cookie()`, `fscache_get_cookie()`, and `fscache_put_cookie()`. Internal anchors include `fscache_cookie_hash[]`, `fscache_cookies`, `fscache_cookie_lru`, `fscache_cookie_state_machine()`, `fscache_perform_lookup()`, `fscache_perform_invalidation()`, and `fscache_unhash_cookie()`. The state enum is defined externally, but this file drives states such as `QUIESCENT`, `LOOKING_UP`, `CREATING`, `ACTIVE`, `INVALIDATING`, `LRU_DISCARDING`, `WITHDRAWING`, `RELINQUISHING`, `FAILED`, and `DROPPED`.

## Control Flow
Acquire validates key/aux lengths, allocates a slab cookie, hashes it under a bucket lock, and pins the parent volume. First use increments `n_active`; a quiescent cookie begins volume access, pins cookie access, marks `IS_CACHING`, and queues work for lookup. The worker serializes lookup, prepare-to-write, invalidation, LRU discard, withdrawal, and relinquish. `__fscache_unuse_cookie()` updates aux/size when requested, decrements active use, and moves inactive cached cookies onto the LRU. The timer/workqueue later sets `DO_LRU_DISCARD` and withdraws only if there are no active users/accesses. Invalidation sets `NO_DATA_TO_READ`, updates coherency data and size, and queues the worker if active; lookup-time invalidation is deferred with `DO_INVALIDATE`.

## State And Persistence
Persistent cache identity is `(volume, key_hash, key bytes)` with aux data and object size stored on the cookie. In-memory state is guarded by `cookie->lock`, bucket locks, refcounts, `n_active`, `n_accesses`, and flag bits. Cache backend persistence is reached through `cookie->volume->cache->ops` for `lookup_cookie()`, `prepare_to_write()`, `invalidate_cookie()`, and `withdraw_cookie()`.

## Dependencies And Integration Points
Depends on `internal.h`, tracepoints, FS-Cache cache/volume operations, the shared `fscache_wq`, procfs seq support, timers, and hlist bucket locks. Netfs clients call public wrappers from `<linux/fscache.h>`; cache backends call exported state helpers such as lookup-negative, resume-after-invalidation, and caching-failed.

## Risks
High-risk areas are collision waiting, access gate ordering, LRU races with new use, invalidation while lookup/create is in flight, and ensuring `n_accesses` reaches zero before withdrawal. `fscache_free_cookie()` warns rather than freeing a hashed cookie, so missing unhash paths leak. State transitions rely on barriers around `cookie->state` and flag/counter ordering.

## Test Signals
Exercise duplicate-key acquisition, acquire/relinquish with racing reacquire, use/unuse LRU expiry, invalidation during lookup and active IO, backend lookup failure, cache withdrawal while IO is pinned, and procfs cookie listing. Tracepoints and FS-Cache stats should reflect acquire, LRU, invalidation, relinquish, and failure paths.
