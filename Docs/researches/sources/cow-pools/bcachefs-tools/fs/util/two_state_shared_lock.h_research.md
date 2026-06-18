# File Research: sources/cow-pools/bcachefs-tools/fs/util/two_state_shared_lock.h

Purpose: Lock where two opposing states are each shared internally but mutually exclusive.

Key APIs and behavior:
- `two_state_lock_t` stores a signed atomic count and wait queue.
- Positive count represents one state; negative count represents the other.
- `bch2_two_state_trylock()` atomically increments or decrements only if the opposite state is absent.
- `bch2_two_state_unlock()` subtracts the state count and wakes all when zero.
- `bch2_two_state_lock()` uses trylock then blocking slow path.

Integration:
- Slow path implemented in `two_state_shared_lock.c`.
- Uses `EBUG_ON` from `util.h`.

Risks and invariants:
- Caller-provided state `s` is interpreted as boolean.
- Overflow of the signed atomic count is not guarded.
