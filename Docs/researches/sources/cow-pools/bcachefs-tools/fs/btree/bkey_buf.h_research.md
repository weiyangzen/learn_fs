# File Research: sources/cow-pools/bcachefs-tools/fs/btree/bkey_buf.h

## Purpose
Provides a small reusable buffer abstraction for temporary bkeys, with inline stack storage and heap fallback.

## Main Contents
- `struct bkey_buf`:
  - `struct bkey_i *k`
  - `u64 onstack[12]`
- Helpers:
  - `bch2_bkey_buf_realloc_noprof()`
  - `bch2_bkey_buf_reassemble_noprof()`
  - `bch2_bkey_buf_copy_noprof()`
  - `bch2_bkey_buf_unpack_noprof()`
  - `bch2_bkey_buf_init()`
  - `bch2_bkey_buf_exit()`

## Behavior
- Starts with `k` pointing at `onstack`.
- If requested key size exceeds the inline array, allocates a fixed 2048-byte heap buffer with `GFP_KERNEL|__GFP_NOFAIL`.
- Reassemble/copy/unpack helpers ensure storage exists, then copy or unpack the key.
- Public macro wrappers route through `alloc_hooks()`.

## Risks / Review Notes
- Reallocation uses a fixed 2048-byte allocation, not `u64s * sizeof(u64)`. This assumes bkeys fit that allocation size in the relevant contexts.
- Allocation is no-fail once heap fallback is needed.
