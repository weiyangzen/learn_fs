# File Research: sources/cow-pools/bcachefs-tools/include/linux/bitmap.h

Purpose: userspace bitmap helper implementation compatible with common Linux bitmap APIs.

Key contents:
- Defines `DECLARE_BITMAP`, first/last word masks, and small-constant optimization helper.
- Implements bitmap weight, and, andnot, complement, zero, or, equality, empty tests, and allocation.
- Implements next-bit and next-zero-bit scanning, plus `find_next_andnot_bit()`.
- Defines `find_first_bit()` and `find_first_zero_bit()` aliases.

Important interactions:
- Depends on `bits.h`, `bitops.h`, `kernel.h`, and libc allocation/string routines.
- Used throughout bcachefs code for masks, device sets, flags, and allocation maps.
