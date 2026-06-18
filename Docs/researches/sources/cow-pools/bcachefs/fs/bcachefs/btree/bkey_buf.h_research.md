# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey_buf.h

This header defines a small reusable buffer for assembling, copying, and unpacking bkeys.

Key contents:
- `struct bkey_buf` contains a `struct bkey_i *k` plus a 12-u64 inline stack buffer.
- `bch2_bkey_buf_init()` points `k` at the inline buffer and initializes the key.
- `bch2_bkey_buf_realloc_noprof()` switches from inline storage to a 2048-byte heap allocation when requested u64 count exceeds the inline capacity.
- `bch2_bkey_buf_reassemble_noprof()` copies a split const key/value into inline/heap `bkey_i` storage.
- `bch2_bkey_buf_copy_noprof()` copies a full inline bkey.
- `bch2_bkey_buf_unpack_noprof()` unpacks a packed key from a btree node into the buffer.
- `bch2_bkey_buf_exit()` frees heap storage if used.

Role:
- Used in traversal/repair/cache paths that need a stable `bkey_i` copy while iterators, journal overlays, or cache lookups may move independently.
