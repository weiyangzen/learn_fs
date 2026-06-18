# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/keylist.c

## Role

`keylist.c` implements dynamic storage support for `struct keylist`, a compact append-only list of packed `bkey_i` records.

## Main Functions

- `bch2_keylist_realloc()`: grows the keylist backing store by rounded power-of-two u64 capacity, preserving inline keys when transitioning to heap allocation.
- `bch2_keylist_pop_front()`: removes the first key by shrinking `top_p` and memmoving the remaining packed keys down.
- `bch2_verify_keylist_sorted()`: debug-only sorted-order verifier.

## Invariants

- `keys_p` may point to caller-provided inline storage or heap storage.
- `top_p` always points just past the last packed key.
- The debug sorted check requires strictly increasing key positions.
