# File Research: sources/cow-pools/bcachefs-tools/fs/util/six.h

Purpose: Public interface and data structures for SIX locks.

Key APIs and behavior:
- Documents read, intent, and write semantics, sequence relock, reentrancy counters, and cycle-detection waiters.
- Defines `enum six_lock_type`, `struct six_lock_waiter`, wait-slot/fifo types, and `struct six_lock`.
- Provides init macro, trylock/relock/unlock wrappers for each lock type, and generic type-based APIs.
- Declares conversion, downgrade, upgrade, wake-all, counts, and reader-count adjustment helpers.

Integration:
- Implemented by `six.c`.
- Includes `fifo.h` and `util.h`.
- Exposes lockdep fields under debug lock allocation.

Risks and invariants:
- Waiter `trans_start_time` is used for fairness and cycle-detection cursoring.
- Inline FIFO starts with eight waiters and grows under wait lock.
- Reentrancy is not automatic; upper layers must track held locks and call increment APIs correctly.
