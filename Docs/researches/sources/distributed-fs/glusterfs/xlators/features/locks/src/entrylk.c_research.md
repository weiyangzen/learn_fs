# sources/distributed-fs/glusterfs/xlators/features/locks/src/entrylk.c

## Purpose

`entrylk.c` implements Gluster entry locks: locks on names inside a directory, including a `NULL` basename that represents the whole directory. It handles granted and blocked entry locks per domain, starvation avoidance, stale-lock revocation, contention upcalls, client cleanup, and the `entrylk`/`fentrylk` xlator entry points.

## Important APIs, types, and functions

- `new_entrylk_lock()` creates a `pl_entry_lock_t` from a frame, basename, type, domain, and optional connection id.
- `names_conflict()`, `names_equal()`, `__same_entrylk_owner()`, and `__conflicting_entrylks()` define entry lock compatibility. A `NULL` basename conflicts with every name; same `(client, lk_owner)` is allowed to conflict.
- `__entrylk_prune_stale()` revokes stale or overly blocked entry locks using `clrlk_clear_entrylk()`.
- `entrylk_contention_notify_check()` and `entrylk_contention_notify()` throttle and emit `GF_UPCALL_ENTRYLK_CONTENTION` notifications.
- `__lock_entrylk()` grants or blocks a request and includes starvation prevention by respecting already-blocked conflicting locks unless the owner already has a lock.
- `__unlock_entrylk()` removes the matching granted lock.
- `grant_blocked_entry_locks()` and `__grant_blocked_entry_locks()` retry blocked entry locks and unwind newly granted frames.
- `pl_common_entrylk()` is the common entry point for both path-based `pl_entrylk()` and fd-based `pl_fentrylk()`.
- `pl_entrylk_client_cleanup()` releases all entry locks associated with a disconnected client context.
- `get_entrylk_count()` and `__get_entrylk_count()` count granted plus blocked entry locks.

## Control flow

`pl_entrylk()` and `pl_fentrylk()` both call `pl_common_entrylk()` with either `loc->inode` or `fd->inode`. The common path extracts `"connection-id"` from xdata, gets the `pl_inode_t`, gets or creates the domain, traces the request, allocates a request lock, and takes an early inode ref to keep `pinode` alive across concurrent disconnect cleanup.

For `ENTRYLK_LOCK` and `ENTRYLK_LOCK_NB`, the code locks the client context and inode, calls `__lock_entrylk()`, records successful or blocking lock ownership in `ctx->entrylk_lockers`, and either unwinds immediately or leaves the frame saved on a blocked lock. For `ENTRYLK_UNLOCK`, it removes the matching lock, drops client-list membership and references, releases the extra inode ref, then tries to grant blocked locks.

`__lock_entrylk()` first rejects conflicts with granted locks. If no granted conflict exists, it still blocks behind conflicting already-blocked locks to avoid starvation, except when the same owner already has a lock and needs nested progress. Granted locks receive an additional ref and are added to `dom->entrylk_list`; blocked locks are queued on `dom->blocked_entrylks`.

Client cleanup walks `ctx->entrylk_lockers`, separates granted locks from blocked-only locks, unwinds blocked frames with `EAGAIN`, grants newly unblocked waiters, unreferences lock objects, and releases inode refs.

## State and persistence behavior

Entry lock state is in-memory only and lives in `pl_dom_list_t` lists: `entrylk_list` for granted locks and `blocked_entrylks` for blocked requests. Each lock also has `client_list` membership in the owning `pl_ctx_t`, refcounting, optional `connection_id`, timing fields, and `contention_time`. `pinode->inode` is held while granted or blocking state needs to survive client cleanup races. Stale-lock revocation does not persist state; it clears in-memory locks through the clear-lock path and logs counts.

## Dependencies and integration points

The file depends on `locks.h` structures, `common.h` domain/tracing/owner helpers, `clear.h` clear-lock APIs, Gluster list/logging/upcall utilities, client contexts from `pl_ctx_get()`, and xlator stack unwind APIs. It emits `GF_UPCALL_ENTRYLK_CONTENTION` through `this->notify`. It uses `pl_does_monkey_want_stuck_lock()` for optional test/fault behavior configured in private state.

## Risks and edge cases

- `__blocked_entrylk_conflict()` returns the requested `lock` instead of the conflicting blocked lock; callers only test non-NULL, so behavior is fine but the API is misleading.
- Correctness relies on lock objects being on up to three lists (`domain_list`, `blocked_locks`, `client_list`) with refcounts matching each state transition.
- `NULL` basename means whole-directory lock, so trace and log paths must tolerate null strings.
- Client cleanup handles races where a lock is both granted and still on a granted-list handoff via `blocked_locks`; this is subtle and easy to break.
- Starvation prevention intentionally blocks otherwise grantable locks, which can surprise tests that only model granted-lock conflicts.

## Test signals

Tests should cover exact-name locks, whole-directory `NULL` locks, same-owner nested locks, nonblocking conflict returning `EAGAIN`, blocking conflict later granted on unlock, cleanup of granted and blocked locks during disconnect, contention upcall throttling, stale revocation by age and max-blocked threshold, and `check_entrylk_on_basename()` behavior across domains.
