# sources/distributed-fs/glusterfs/xlators/features/locks/src/reservelk.c

## Purpose
`reservelk.c` implements reserve locks for the locks translator. Reserve locks are exact-range reservations that can block later POSIX lock calls until the matching reservation is unlocked. `posix.c` calls this file from `pl_lk` for `F_RESLK_*` commands and before ordinary `F_SETLK/F_SETLKW` requests.

## Important APIs, Types, And Functions
The public functions are `reservelks_equal`, `pl_verify_reservelk`, `grant_blocked_reserve_locks`, `grant_blocked_lock_calls`, `pl_reserve_unlock`, and `pl_reserve_setlk`. Internal helpers include `__reservelk_grantable`, `__same_owner_reservelk`, `__matching_reservelk`, `__reservelk_conflict`, `_pl_verify_reservelk`, `__lock_reservelk`, `find_matching_reservelk`, and `__reserve_unlock_lock`.

## Control Flow
Reservation equality is exact: start and end offsets must match. Setting a reserve lock checks `pl_inode->reservelk_list`; if an equal reservation exists, nonblocking callers get `-EAGAIN`, while blocking callers are linked to `pl_inode->blocked_reservelks`. Otherwise the lock is inserted into `reservelk_list`.

Ordinary POSIX locks call `pl_verify_reservelk`. If a matching reservation exists with the same owner, the reserve lock is consumed and destroyed so the POSIX lock can continue. If the owner differs, the POSIX lock is added to `pl_inode->blocked_calls` and the caller is held. Unlocking a reserve lock removes the exact matching reservation, grants newly possible reserve locks, then retries blocked ordinary lock calls through `pl_setlk`.

## State And Persistence Behavior
All state is in `pl_inode_t` lists protected by `pl_inode->mutex`: active reservations, blocked reservations, and blocked lock calls. There is no disk persistence. Waiting callers hold their original `posix_lock_t` and frame until grant or failure.

## Dependencies And Integration Points
This file depends on list primitives, `posix_lock_t`, lock owner comparison, `__delete_lock`, `__destroy_lock`, `pl_setlk`, tracing, fd-number conversion, refkeeper updates, and GlusterFS unwind macros. It is tightly integrated with `pl_lk` in `posix.c`.

## Risks And Edge Cases
The exact-boundary matching model is narrow; overlapping but non-identical reservations do not conflict. `__matching_reservelk` returns the list iterator after traversal, so callers rely on list macros producing `NULL`-like behavior only through loop control assumptions. The helper `__grant_blocked_lock_calls` splices from `blocked_reservelks` even though it is named for blocked ordinary calls; if this is not intentional, blocked POSIX calls may not drain as expected. Frame lifetime is delicate because blocked locks are unwound outside the inode mutex.

## Test Signals
Useful tests should exercise exact same-range reserve locks, same-owner conversion into POSIX locks, different-owner blocking, nonblocking `EAGAIN`, unlock granting order, and interaction with later `pl_setlk` conflicts.
