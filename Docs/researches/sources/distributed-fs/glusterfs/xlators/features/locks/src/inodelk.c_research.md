# sources/distributed-fs/glusterfs/xlators/features/locks/src/inodelk.c

## Purpose

`inodelk.c` implements Gluster inode locks: domain-scoped byte-range locks on an inode used by internal/distributed operations rather than ordinary POSIX fcntl locking. It handles conflict detection, blocking, starvation avoidance, stale-lock revocation, contention upcalls, synchronization with inode removal, client cleanup, and the `inodelk`/`finodelk` xlator entry points.

## Important APIs, types, and functions

- `new_inode_lock()` creates `pl_inode_lock_t` requests from a `gf_flock`, frame/client identity, domain, and optional connection id.
- `inodelk_overlap()`, `inodelk_type_conflict()`, `same_inodelk_owner()`, `inodelk_conflict()`, and `inodelks_equal()` define compatibility and unlock matching.
- `__inodelk_prune_stale()` revokes stale or over-blocked locks through `clrlk_clear_inodelk()`.
- `inodelk_contention_notify_check()` and `inodelk_contention_notify()` throttle and send `GF_UPCALL_INODELK_CONTENTION`.
- `__lock_inodelk()` checks removal gating via `pl_inode_remove_inodelk()`, granted-lock conflicts, blocked-lock starvation, and finally inserts into granted or blocked lists.
- `__inode_unlock_lock()` removes an exactly matching same-owner granted inodelk.
- `__grant_blocked_inode_locks()`, `grant_blocked_inode_locks()`, and `unwind_granted_inodes()` retry blocked locks and unwind saved frames.
- `pl_inode_setlk()` is the core set/unlock routine for inodelks.
- `pl_common_inodelk()` validates input, performs special domain conversion for metadata ranges, allocates the request, dispatches `F_SETLK`/`F_SETLKW`, and unwinds.
- `pl_inodelk_client_cleanup()` releases all inodelks associated with a client context.
- `get_inodelk_count()` and `__get_inodelk_count()` count granted and blocked locks, optionally by domain.

## Control flow

`pl_inodelk()` and `pl_finodelk()` pass path-based or fd-based inodes into `pl_common_inodelk()`. The common path validates the frame/inode/flock, rejects negative ranges, maps the special metadata range to a `:metadata` domain when needed, traces the request, obtains the client context and `pl_inode_t`, creates the domain, and allocates a request lock.

Only `F_SETLK` and `F_SETLKW` are supported; `F_GETLK` returns `ENOTSUP`. `F_SETLKW` sets `can_block`. `pl_inode_setlk()` takes an early inode ref, optionally prunes stale locks or performs monkey unlock behavior, prepares contention notification state, and locks the client context plus inode. Non-unlock requests go through `__lock_inodelk()` and are either granted, blocked, or failed. Unlock requests require exact same range and owner, remove the granted lock, wake remove waiters, and then grant blocked inodelks after dropping the mutex.

Blocked-grant flow splices the domain's blocked list to a local list under lock, retries each request through `__lock_inodelk()`, and puts requests that are no longer `-EAGAIN` on a granted handoff list. `unwind_granted_inodes()` performs stack unwinds outside the initial grant loop and then unreferences the lock objects under the inode mutex.

## State and persistence behavior

Inodelk state is in-memory per `pl_dom_list_t`: `inodelk_list` for granted locks and `blocked_inodelks` for blocked locks. Each lock also records range, type, owner, client, pid, domain, user flock, saved frame, connection id, client-list membership, refcount, timing fields, contention timestamp, and retry status. The file does not persist lock state; it integrates with clear-lock code for revocation and with `pl_inode_remove_*` state from `common.c` to gate regular-operation locks while remove operations are active.

The special range `(l_start == LLONG_MAX - 1 && l_len == 0)` changes the lock domain to `volume:metadata`, keeping metadata locks distinct without changing the range representation.

## Dependencies and integration points

The file uses Gluster core types, list/logging/upcall utilities, `clear.h`, `common.h`, and `locks.h`. It works with `pl_ctx_t` client cleanup lists, `pl_inode_remove_inodelk()` and `pl_inode_remove_wake()` from `common.c`, and `this->notify()` for contention upcalls. It shares tracing with byte-range locks via `pl_trace_in/out/block()` and `pl_print_inodelk()`.

## Risks and edge cases

- Inodelk unlock requires exact range equality, unlike POSIX byte-range partial unlock semantics; callers must know this contract.
- `pl_inode_setlk()` has intricate refcount decisions around blocking, nonblocking failure, unlock, and client-list insertion.
- Removal gating depends on client pid conventions: negative pid internal locks bypass synchronization.
- Starvation avoidance can block otherwise grantable locks when a conflicting blocked lock exists, except for owners already holding locks.
- Domain string conversion allocates a new `:metadata` string for special ranges; leaks or double-frees would affect uncommon metadata-lock paths.
- The local `res1` variable in `pl_common_inodelk()` is freed but never assigned in the observed code, suggesting leftover interface churn.

## Test signals

Tests should exercise read/read sharing, write conflicts, same-owner overlap, exact unlock matching, nonblocking and blocking conflict results, grant-after-unlock, blocked-lock starvation ordering, special metadata domain conversion, remove-operation gating and wakeups, client cleanup of granted and blocked locks, stale revocation thresholds, max-blocked revocation, contention upcall throttling, and unsupported `F_GETLK`.
