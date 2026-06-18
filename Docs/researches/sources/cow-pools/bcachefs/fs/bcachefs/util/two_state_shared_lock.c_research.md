# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/two_state_shared_lock.c

## Summary
Provides the blocking slow path for the two-state shared lock.

## Main Responsibilities
- Implements `__bch2_two_state_lock()`.
- Waits until `bch2_two_state_trylock()` succeeds for the requested state.

## Important Behavior
The wait uses the lock’s waitqueue and retries the inline atomic trylock predicate.

## Risks
All substantive state handling lives in the header. Wakeup correctness depends on unlock waking all waiters when the aggregate counter returns to zero.
