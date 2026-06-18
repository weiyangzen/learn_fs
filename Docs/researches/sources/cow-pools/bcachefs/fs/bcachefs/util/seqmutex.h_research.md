# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/seqmutex.h

This header defines a small mutex plus sequence counter utility.

Structure:
- `struct seqmutex`:
  - `struct mutex lock`
  - `u32 seq`

API:
- `seqmutex_init()` initializes the mutex.
- `seqmutex_trylock()` attempts to lock without incrementing sequence.
- `seqmutex_lock()` locks and increments `seq`.
- `seqmutex_unlock()` unlocks and returns the sequence observed while locked.
- `seqmutex_relock()` tries to reacquire only if `seq` still matches the supplied value.

Important behavior:
- `seqmutex_relock()` double-checks sequence before and after `mutex_trylock()`.
- A caller can unlock, perform work, and later relock only if no intervening full lock acquisition changed the sequence.

Research notes:
- This is a compact optimistic-relock helper for code that needs to drop a mutex and detect intervening mutation.
