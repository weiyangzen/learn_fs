# File Research: sources/cow-pools/bcachefs-tools/fs/data/keylist.h

## Purpose
Inline API for initializing, freeing, appending, iterating, and measuring `struct keylist`.

## Main Interfaces and Behavior
- `bch2_keylist_init()` sets both bottom and top pointers to inline storage.
- `bch2_keylist_free()` releases heap storage only when the list was promoted out of inline storage.
- `bch2_keylist_push()` advances `top` by `bkey_next(top)`, and `bch2_keylist_add()` copies a packed key into `top` before pushing.
- `bch2_keylist_empty()`, `bch2_keylist_u64s()`, `bch2_keylist_bytes()`, and `bch2_keylist_front()` expose simple state.
- `for_each_keylist_key()` walks packed keys from `keys` to `top`.
- `keylist_sectors()` sums `k.size` across all stored keys.
- `bch2_verify_keylist_sorted()` is either debug verification or a no-op.

## Risks and Invariants
- Callers must ensure enough capacity, usually via `bch2_keylist_realloc()`, before appending.
