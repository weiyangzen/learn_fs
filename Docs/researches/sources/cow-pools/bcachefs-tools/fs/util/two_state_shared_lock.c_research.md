# File Research: sources/cow-pools/bcachefs-tools/fs/util/two_state_shared_lock.c

Purpose: Blocking slow path for the two-state shared lock.

Key APIs and behavior:
- `__bch2_two_state_lock()` waits until `bch2_two_state_trylock(lock, s)` succeeds.
- Uses `__wait_event()` on the lock wait queue.

Integration:
- Implements the out-of-line path declared in `two_state_shared_lock.h`.

Risks and invariants:
- Wakeups rely on unlock waking all waiters when the shared count reaches zero.
