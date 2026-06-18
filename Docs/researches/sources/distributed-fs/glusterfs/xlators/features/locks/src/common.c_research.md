# sources/distributed-fs/glusterfs/xlators/features/locks/src/common.c

## Purpose

`common.c` implements the shared mechanics behind the locks translator: per-inode lock state creation, byte-range POSIX lock insertion/merging, blocked-lock granting, lock tracing, mandatory-lock enforcement lookup, client/request local cleanup, and coordination between inode-removal operations and inodelks. It is the core state machine for fcntl-style locks and a utility layer consumed by `entrylk.c`, `inodelk.c`, and the rest of the posix-locks xlator.

## Important APIs, types, and functions

- `get_domain()` returns or creates a `pl_dom_list_t` within a `pl_inode_t`; domains partition entrylk and inodelk lists by volume/domain name.
- `pl_inode_get()` attaches a `pl_inode_t` to an inode context, initializes all lock lists, mutex/condition state, GFID, and mandatory-lock flags, and optionally fetches mandatory-lock xattr state.
- `new_posix_lock()`, `__delete_lock()`, `__destroy_lock()`, `posix_lock_to_flock()`, `locks_overlap()`, and `same_owner()` are the basic byte-range lock lifecycle and comparison helpers.
- `pl_setlk()` is the main byte-range set/unlock path. It checks client connectivity, handles pre-lock unlocks for blocking upgrades/downgrades, grants or blocks the request, queues when metalock is active, then wakes blocked locks and blocked I/O.
- `pl_getlk()` returns the first conflicting granted byte-range lock, or rewrites the request to `F_UNLCK` when none exists.
- `grant_blocked_locks()` and `__grant_blocked_locks()` scan blocked byte-range locks, re-check grantability, merge granted locks into `ext_list`, and unwind the saved frames outside the inode mutex.
- `pl_lock_preempt()` forcefully removes conflicting byte-range locks and blocked I/O for a requesting owner, unwinding displaced operations with `EBUSY`.
- `pl_is_mandatory_locking_enabled()`, `pl_fetch_mlock_info_from_disk()`, and `pl_update_refkeeper()` bridge in-memory lock state to mandatory-lock policy and inode lifetime management.
- `pl_inode_remove_prepare()`, `pl_inode_remove_complete()`, `pl_inode_remove_cbk()`, `pl_inode_remove_unlocked()`, and `pl_inode_remove_inodelk()` coordinate unlink/rmdir/rename-style removal with outstanding inodelks.

## Control flow

The byte-range lock path begins with `new_posix_lock()` copying the requested `gf_flock`, client, fd, lk-owner, and flags into a heap object. `pl_setlk()` then takes `pl_inode->mutex`, rejects disconnected clients for blocking non-unlock requests, optionally sends a synthetic pre-lock unlock when a blocking lock conflicts, and calls `__is_lock_grantable()`. Grantable locks are inserted through `__insert_and_merge()`, which recursively merges same-owner same-type ranges or subtracts same-owner different-type/unlock ranges. Non-grantable blocking requests are marked `blocked`, left on `ext_list`, and unwound only when later granted. Nonblocking conflicts return would-block.

Blocked lock handling is split deliberately: while holding `pl_inode->mutex`, `__grant_blocked_locks()` moves candidate blocked locks to a temporary list and reinserts grantable ones; after unlocking, `grant_blocked_locks()` unwinds saved call frames. This avoids stack unwinds and callbacks while holding the inode lock. `pl_send_prelock_unlock()` follows the same pattern after injecting an `F_UNLCK` lock.

The remove coordination path resolves an inode from a `loc_t`, records `pl_inode->inode`, checks all inodelk domains for owners from other clients, and either marks the inode locked for removal or queues a stub in `pl_inode->waiting`. Completion decrements `remove_running`, clears `is_locked` when appropriate, grants blocked inodelks, sends contention notifications, and releases inode refs.

## State and persistence behavior

The durable state is mostly external to this file: lock state is in memory on `pl_inode_t` and domain lists; mandatory-lock enforcement can be recovered from disk via `GF_ENFORCE_MANDATORY_LOCK` xattr. `pl_inode_get()` sets `check_mlock_info` so the xattr is fetched lazily when mandatory locking is active and a `pl_local_t` with fd/loc is available. `refkeeper` holds an inode ref while byte-range locks exist, preventing pruning. Lists on `pl_inode_t` include `ext_list` for byte-range locks, `dom_list` for per-domain entry/inode locks, `rw_list` for blocked I/O, `metalk_list` and `queued_locks` for metalock behavior, and `waiting` for removal stubs.

Timing fields (`blkd_time`, `granted_time`) are assigned at insertion for dump/debug behavior. The code relies on list membership to encode lock state: granted byte-range locks have `blocked == 0` on `ext_list`; blocked byte-range locks have `blocked == 1` on the same list.

## Dependencies and integration points

This file depends on Gluster core objects (`xlator_t`, `inode_t`, `fd_t`, `call_frame_t`, `loc_t`, `dict_t`, `client_t`), list helpers, memory accounting, inode context APIs, logging/tracing APIs, syncop xattr APIs, and lk-owner helpers. It calls into other lock modules via declarations such as `do_blocked_rw()`, `pl_metalock_is_active()`, `__pl_queue_lock()`, `__grant_blocked_inode_locks()`, `unwind_granted_inodes()`, and contention notification helpers. `PL_STACK_UNWIND_AND_FREE` from `common.h` is used to unwind lock calls while cleaning `pl_local_t`.

## Risks and edge cases

- Lock splitting and merging in `__insert_and_merge()` assumes `subtract_locks()` receives contained ranges; unexpected geometry asserts and logs an error.
- The file stores fd identity as a cast integer (`fd_to_fdnum()`), so correctness depends on not treating it as a durable descriptor value.
- `pl_setlk()` unlocks `pl_inode->mutex` early in the disconnected-client branch, making lock/unlock structure fragile if future edits add cleanup before `out`.
- Mandatory-lock xattr fetch is synchronous and uses negative `op_ret` as errno-like data; incorrect syncop return handling would affect enforcement decisions.
- Remove coordination keeps `pl_inode->mutex` locked across a `-1` return from `pl_inode_remove_prepare()` by contract, so callers must always complete via `pl_inode_remove_complete()`.
- Recursive lock merging is concise but difficult to audit for all overlapping same-owner transitions, especially with `F_UNLCK` cleanup.

## Test signals

Useful tests include same-owner range merge/split/unlock cases, conflicting owner read/write matrices, blocking `F_SETLKW` grant after unlock, metalock queue behavior, disconnected-client blocking lock rejection, mandatory-lock xattr recovery with fd and loc paths, inode refkeeper transitions when lock lists become empty/non-empty, and remove-vs-inodelk sequencing where removal waits on external owners but same-client/internal locks proceed.
