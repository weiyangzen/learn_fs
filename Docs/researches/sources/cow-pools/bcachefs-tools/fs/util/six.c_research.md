# File Research: sources/cow-pools/bcachefs-tools/fs/util/six.c

Purpose: Implementation of sleepable shared/intent/exclusive locks.

Key APIs and behavior:
- Fast path uses an atomic state word for read, intent, write, wait bits, and no-spin flag.
- Optional per-CPU reader mode avoids atomic reader increments.
- Slow path inserts stable RCU wait slots, supports waitlist growth, and wakes eligible waiters.
- Non-reader wakeups choose the oldest matching transaction start time; readers wake as a group.
- Supports trylock, relock by sequence, blocking lock with cycle-detection callback, contended-only path, unlock, downgrade, upgrade, conversion, recursive count increment, wake-all, counts, reader-count adjustment, init, and exit.

Integration:
- Implements `six.h`.
- Uses lockdep, scheduler tracing, RCU, percpu allocation, and optional optimistic spinning.
- Designed for bcachefs tree/transaction locking where intent avoids read-to-write upgrade deadlocks.

Risks and invariants:
- Write lock requires intent ownership.
- Wait slots are RCU-visible and must not move while cycle detectors may scan them.
- `should_sleep_fn` errors can require undoing a lock that was concurrently acquired.
- Per-CPU reader mode relies on memory barriers paired across read and write paths.
