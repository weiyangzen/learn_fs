# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/nocow_locking.c

## Role

`nocow_locking.c` implements bucket-level synchronization for no-COW updates versus copy/move operations. It prevents in-place updates and relocation from racing on the same physical bucket.

## Lock Model

Each bucket lock table entry contains several tracked `dev:bucket` slots. The atomic lock value sign distinguishes modes:
- positive: update locks
- negative: copy locks

Opposite signs conflict. Same-sign users can share the lock, subject to overflow checks.

## Main Functions

- `bch2_bucket_nocow_is_locked()`: checks whether a bucket has any active nocow lock.
- `__bch2_bucket_nocow_trylock()`: low-level slot lookup/allocation and mode-compatible lock acquisition.
- `__bch2_bucket_nocow_unlock()`: decrements lock count and wakes waiters when zero.
- `bch2_bkey_nocow_trylock()`: tries to lock all pointer buckets for a key, rolling back partial success.
- `bch2_bkey_nocow_lock()`: blocking ordered acquisition for all pointer buckets.
- `bch2_bkey_nocow_unlock()`: unlocks buckets for pointers previously locked.
- `bch2_nocow_locks_to_text()`: diagnostic dump.
- `bch2_fs_nocow_locking_init_early()` / `exit()`: initialize spinlocks and assert no locks remain.

## Deadlock Avoidance

Blocking acquisition first builds a list of bucket table entries, prefetches them, sorts by lock-bucket address, and takes locks in that order. If a hash bucket is full, it drops earlier locks, waits for the bucket to become empty, and retries all.

## Invariants

- The `cas[]` array is parallel to extent pointers and records exactly which device references were acquired; it is authoritative for unlock.
- Unlock asserts that remaining lock count, if nonzero, keeps the same sign.
- Exit asserts no nocow locks remain.
