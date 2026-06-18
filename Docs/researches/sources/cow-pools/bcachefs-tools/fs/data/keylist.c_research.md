# File Research: sources/cow-pools/bcachefs-tools/fs/data/keylist.c

## Purpose
Implements dynamic storage and front removal for `struct keylist`, a compact list of packed `bkey_i` values.

## Main Interfaces and Behavior
- `bch2_keylist_realloc()` grows backing storage by rounded power-of-two u64 count. It uses inline storage until the requested size exceeds inline capacity, then `krealloc()`s heap storage and copies existing inline keys on first promotion.
- `bch2_keylist_pop_front()` removes the first key by shrinking `top_p` and memmoving subsequent packed keys down.
- In debug builds, `bch2_verify_keylist_sorted()` asserts that adjacent keys are strictly ordered by position.

## Risks and Invariants
- `keys_p` points either to caller-provided inline storage or heap storage; free/realloc logic depends on comparing against the inline pointer.
- Packed key iteration uses each key's `k.u64s`; corrupt lengths would break traversal.
