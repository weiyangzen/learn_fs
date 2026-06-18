# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey_cmp.h

This header implements hot packed-key comparison helpers.

Key contents:
- `__bkey_cmp_bits()` compares the packed key bitstream across the configured number of key bits.
- On x86-64, it uses inline assembly to compare descending packed words efficiently.
- The generic path masks off header bits, advances through words with `next_word()`, and returns `cmp_int()` of the first differing word.
- `__bch2_bkey_cmp_packed_format_checked_inlined()` compares two packed keys in the same btree format and debug-checks equivalence against unpacked `bpos` comparison.
- `bch2_bkey_cmp_packed_inlined()` handles mixed packed/unpacked inputs by unpacking the packed side when necessary, otherwise directly comparing `bpos`.

Role:
- This is a performance-critical comparator for bset auxiliary tree lookup and btree-node iteration ordering.
