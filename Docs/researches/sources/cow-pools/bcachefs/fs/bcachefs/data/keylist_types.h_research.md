# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/keylist_types.h

## Role

`keylist_types.h` defines `struct keylist`.

## Structure

`struct keylist` stores:
- `keys` / `keys_p`: start of packed key storage, typed either as `struct bkey_i *` or `u64 *`
- `top` / `top_p`: current append cursor, typed the same way

## Design

The union layout lets callers treat the storage as packed bkeys or as raw u64s for size/capacity arithmetic.
