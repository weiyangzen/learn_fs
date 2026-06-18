# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/six.c

## Summary
Implements bcachefs “six” locks: sleepable shared/intent/exclusive locks with optional percpu reader accounting, sequence numbers, reentrancy counters, lockdep integration, wait-list exposure for deadlock cycle detection, and optional optimistic spinning.

## Main Responsibilities
- Provides trylock, blocking lock, relock, unlock, conversion, downgrade, reentrant increment, reader-count adjustment, count reporting, wakeup, init, and teardown operations.
- Encodes read/intent/write ownership and waiter bits in `lock->state`.
- Supports percpu read mode to reduce reader-side atomic contention.
- Maintains an RCU-swappable stable-index waiter array so lockless cycle detectors can traverse waiters without entries moving.
- Wakes read waiters in batches and intent/write waiters by oldest transaction start time.
- Integrates with lockdep/lockstat and saves owner backtraces under debug builds.

## Key APIs
- `six_trylock_ip()`, `six_lock_ip_waiter()`, `six_relock_ip()`, `six_unlock_ip()`.
- `six_lock_downgrade()`, `six_lock_tryupgrade()`, `six_trylock_convert()`.
- `six_lock_increment()`, `six_lock_readers_add()`.
- `six_lock_wakeup_all()`, `six_lock_counts()`.
- `__six_lock_init()`, `six_lock_exit()`.

## Important Behavior
Read locks conflict with write locks, intent locks conflict with other intent locks, and write locks require the current task to already own intent. Write unlock increments the lock sequence so callers can drop and later relock only if protected state did not change.

The slow path installs a `six_lock_waiter` before sleeping, then runs an optional `should_sleep_fn` callback. This lets bcachefs’ upper layers detect lock dependency cycles and abort/restart transactions.

Percpu read mode temporarily increments the current CPU reader slot and uses barriers to race safely with write acquisition. Failed percpu trylocks may return a negative wakeup code so conflicting waiters are not stranded.

## Risks
Correctness depends on tight memory ordering between wait-slot removal, `lock_acquired`, percpu reader counts, and state bits. Waiter objects live on blocked task stacks, so wakeup and abort paths must not dereference them after publishing acquisition or removal. Reentrant counters are only partial support; upper layers must track ownership correctly.
