# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/two_state_shared_lock.h

## Summary
Defines a compact lock with two shared states where holders in the same state can coexist, but opposite states conflict.

## Main Contents
- `two_state_lock_t` with signed atomic counter and waitqueue.
- `two_state_lock_init()`.
- `bch2_two_state_trylock()`.
- `bch2_two_state_lock()`.
- `bch2_two_state_unlock()`.

## Important Behavior
State `s` maps to `+1` or `-1`. A positive counter means one or more holders of one state; a negative counter means holders of the other state. Trylock fails if the current sign conflicts with the requested state. Unlock subtracts the state’s sign and wakes all waiters when the counter reaches zero.

## Risks
The lock does not track owners, recursion, or fairness. Mispaired unlock state values corrupt the signed counter and can admit incompatible holders.
