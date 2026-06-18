# File Research: sources/cow-pools/bcachefs-tools/fs/util/seqmutex.h

Purpose: Minimal mutex wrapper with a sequence counter for drop-and-relock validation.

Key APIs and behavior:
- `struct seqmutex` contains `struct mutex lock` and `u32 seq`.
- `seqmutex_lock()` takes the mutex and increments the sequence.
- `seqmutex_unlock()` releases and returns the sequence value.
- `seqmutex_relock()` only succeeds if the sequence is unchanged before and after `mutex_trylock()`.

Integration:
- Header-only helper, depends on `<linux/mutex.h>`.

Risks and invariants:
- `seqmutex_init()` initializes only the mutex, not explicitly the sequence; callers need zeroed storage or manual initialization.
- Sequence wrap is possible but likely acceptable for intended validation use.
