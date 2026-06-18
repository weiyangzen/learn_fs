# File Research: sources/cow-pools/bcachefs-tools/fs/data/keylist_types.h

## Purpose
Defines `struct keylist`, a packed bkey list represented as u64 pointers and bkey pointers over the same memory.

## Main Interfaces
- `keys/keys_p` union points to the first stored key/u64.
- `top/top_p` union points one past the final stored key/u64.

## Notes
The union layout makes byte/u64 sizing and packed `bkey_i` traversal cheap without separate metadata.
