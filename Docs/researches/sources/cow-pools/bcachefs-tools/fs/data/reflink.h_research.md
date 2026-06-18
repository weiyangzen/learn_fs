# File Research: sources/cow-pools/bcachefs-tools/fs/data/reflink.h

## Role

Declares reflink key operations and helpers for indirect extent management.

## Bkey Operation Bundles

- `bch2_bkey_ops_reflink_p` provides validation, text printing, merge hook, trigger, fsck check/repair hook, and a minimum value size of 16 bytes.
- `bch2_bkey_ops_reflink_v` provides validation, text printing, pointer byte-swapping, extent trigger integration, pointer repair through `bch2_check_fix_ptrs`, and a minimum value size of 8 bytes.
- `bch2_bkey_ops_indirect_inline_data` provides validation, text printing, trigger, and a minimum value size of 8 bytes.

## Helper Semantics

`bkey_is_indirect()` identifies `reflink_v` and `indirect_inline_data`. `bkey_refcount_c()` and `bkey_refcount()` return a const or mutable refcount pointer for those indirect types and `NULL` otherwise.

## Exported Operations

The header exports indirect lookup, direct-to-indirect conversion, range remapping, and GC start/done helpers:

- `bch2_lookup_indirect_extent()`
- `bch2_make_extent_indirect()`
- `bch2_remap_range()`
- `bch2_gc_reflink_start()`
- `bch2_gc_reflink_done()`
