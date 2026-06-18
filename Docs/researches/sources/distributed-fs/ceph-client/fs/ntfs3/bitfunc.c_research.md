# sources/distributed-fs/ceph-client/fs/ntfs3/bitfunc.c

## Purpose
Provides low-level bit-range predicates for little-endian NTFS bitmaps: test whether all bits in a range are clear or set.

## Important APIs, Types, And Functions
`are_bits_clear()` returns true when `[bit, bit + nbits)` contains only zero bits. `are_bits_set()` returns true when the same range contains only one bits. `fill_mask[]` and `zero_mask[]` handle partial leading/trailing byte masks.

## Control Flow
Both functions handle an unaligned leading byte, advance to a `size_t`-aligned address, scan full machine words, scan full trailing bytes, then check a final partial byte. The set variant compares against all-ones values; the clear variant checks for any nonzero word/byte.

## State And Persistence
No state is stored. These predicates inspect bitmap memory that represents persistent allocation state when called by bitmap code.

## Dependencies And Integration Points
Used by `bitmap.c` to validate free/used ranges read from `$Bitmap` buffers. Depends on `MINUS_ONE_T` and NTFS3 type definitions.

## Risks And Edge Cases
Correctness depends on unaligned memory access being acceptable for the target architecture or compiler handling; the code aligns before word loads after a possible initial byte. Zero-length ranges return true. Endianness is safe because the functions inspect byte-level bit layout expected by NTFS little-endian bitmap helpers.

## Test Signals
Test zero-length, sub-byte, byte-aligned, unaligned, word-aligned, cross-word, all-clear, all-set, and mixed ranges under KUnit or equivalent, including big-endian builds.
