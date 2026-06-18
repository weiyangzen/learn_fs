# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reflink.h

Header for reflink bkey operations, indirect extent helpers, remap, and reflink GC.

Key contents:
- Declares validate/text/merge/trigger functions for `reflink_p`.
- Defines `bch2_bkey_ops_reflink_p` with validation, text, merge, trigger, and 16-byte minimum value.
- Declares validate/text/trigger functions for `reflink_v` and defines `bch2_bkey_ops_reflink_v`, including pointer swabbing.
- Declares validate/text/trigger functions for `indirect_inline_data` and defines its bkey ops.
- Provides `bkey_is_indirect()`, `bkey_refcount_c()`, and `bkey_refcount()` helpers for refcount-bearing indirect keys.
- Declares `bch2_lookup_indirect_extent()`, `bch2_remap_range()`, `bch2_gc_reflink_start()`, and `bch2_gc_reflink_done()`.

Important invariants:
- Only `KEY_TYPE_reflink_v` and `KEY_TYPE_indirect_inline_data` expose refcount pointers through the helper functions.
- Reflink pointer and value bkey ops are kept separate because pointer keys live in extents while value keys live in the reflink btree.
