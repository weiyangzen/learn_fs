# File Research: sources/cow-pools/bcachefs-tools/fs/btree/bkey_cmp.h

## Purpose
Defines hot inline packed-bkey comparison routines.

## Main Contents
- `__bkey_cmp_bits()`:
  - x86-64 inline assembly implementation for packed key bit comparison.
  - generic C fallback for non-x86-64.
- `__bch2_bkey_cmp_packed_format_checked_inlined()`: compares two packed keys using the btree’s packed format.
- `bch2_bkey_cmp_packed_inlined()`: handles packed-vs-packed hot path and mixed packed/unpacked cold path.

## Notable Details
- The x86-64 path walks high-order packed words and returns `-1/0/1`.
- Debug assertions compare packed comparison results against unpacked `bpos_cmp()` results.
- Mixed packed/unpacked comparison declares the temporary `struct bkey` only in the cold branch to avoid stack auto-init cost on the hot path.

## Risks / Review Notes
- The assembly is performance-driven and architecture-specific.
- Correctness depends on `high_word()`, endian definitions, and `b->nr_key_bits` matching `bkey_format_key_bits()`.
