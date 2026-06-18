# File Research: sources/cow-pools/bcachefs-tools/fs/data/nocow_locking.c

## Purpose
Implements hashed bucket locks used to coordinate no-COW copy/update access to buckets referenced by extent pointers.

## Main Interfaces and Behavior
- Locks are stored in hashed `nocow_lock_bucket` entries. Each slot records a bucket id and signed atomic count.
- Positive counts represent update locks; negative counts represent copy locks. Opposite signs conflict, same signs can nest/share.
- `bch2_bucket_nocow_is_locked()` checks whether a bucket has any active slot count.
- `__bch2_bucket_nocow_unlock()` subtracts the matching signed count, asserts sign consistency, and wakes waiters when a slot reaches zero.
- `__bch2_bucket_nocow_trylock()` finds or allocates a slot under spinlock, rejects opposite-sign contention, detects overflow/sign changes, and reports bucket-full or contended errors.
- `bch2_bkey_nocow_unlock()` unlocks all pointer buckets for which the parallel `cas[]` device-ref array indicates a lock was taken.
- `bch2_bkey_nocow_trylock()` attempts to lock all pointer buckets and unwinds already-taken locks on failure.
- `bch2_bkey_nocow_lock()` first tries the fast path; on failure it builds a bucket list, sorts by lock-bucket address to avoid deadlocks, waits on contention, and retries all locks when a hash bucket is full.
- `bch2_nocow_locks_to_text()` renders active locks and coalesces empty entries.
- Filesystem init/exit initialize spinlocks and assert all locks are released at exit.

## Dependencies and Coupling
Uses extent pointer iteration, device bucket helpers, closures waitlists, darray utilities, and timing stats.

## Risks and Invariants
- The `cas[]` array is authoritative for which device refs/locks exist; code avoids re-deriving devices from `c->devs[]` because device removal may clear entries while refs remain.
- Sorting by hash-bucket address is the deadlock-avoidance mechanism for multi-bucket locks.
