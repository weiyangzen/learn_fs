# sources/distributed-fs/ceph-client/arch/s390/lib/find.c

## Purpose
Implements s390 MSB0-numbered bit scanning helpers for bitmaps where hardware and architecture conventions number bit 0 at the most significant bit of a word.

## Important APIs, Types, And Functions
Exports `find_first_bit_inv()` and `find_next_bit_inv()`. Both return the first set bit according to inverted/MSB0 numbering and return `size` when no bit is found within bounds.

## Control Flow And State
`find_first_bit_inv()` scans full words until a nonzero word appears, handles a partial tail by masking unused low-order bits, then uses `__fls(tmp) ^ (BITS_PER_LONG - 1)` to convert MSB-position to logical bit index. `find_next_bit_inv()` starts at an offset, masks bits before the offset in the first word, scans middle words, handles a partial final word, and applies the same index conversion.

## Dependencies And Integration
Depends on Linux bitops and export infrastructure. It supports s390 code paths that interact with hardware bitmaps or facility masks with MSB0 numbering.

## Risks And Test Signals
Risks include off-by-one errors for partial words, incorrect masks at nonzero offsets, and returning past `size`. Signals include bitmap unit tests, facility-mask users, and architecture code exercising `test_bit_inv()`/find helpers across boundary sizes.
