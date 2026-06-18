# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/keylist.h

## Role

`keylist.h` provides inline operations and declarations for packed bkey lists.

## Main Helpers

- `bch2_keylist_init()` / `bch2_keylist_free()`
- `bch2_keylist_push()` / `bch2_keylist_add()`
- `bch2_keylist_empty()`
- `bch2_keylist_u64s()` / `bch2_keylist_bytes()`
- `bch2_keylist_front()`
- `for_each_keylist_key()`
- `keylist_sectors()`

## Use

Keylists are useful where code must accumulate multiple btree keys contiguously without per-key allocation overhead. They rely on the standard `bkey_next()` packed-key traversal convention.
