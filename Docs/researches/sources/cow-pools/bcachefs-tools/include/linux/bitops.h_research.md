# File Research: sources/cow-pools/bcachefs-tools/include/linux/bitops.h

Purpose: userspace implementation of Linux bit operations and bit arithmetic helpers.

Key contents:
- Defines bit sizing macros, `BIT_MASK`, `BIT_WORD`, and `BITS_TO_*`.
- Implements atomic and non-atomic set/clear/test/test-and-set/test-and-clear operations.
- Provides acquire/release variants used for lock-style bit operations.
- Defines set-bit iteration macros.
- Implements hweight/popcount helpers, rotate helpers, find-last/find-first-set helpers, `ffz()`, and `rounddown_pow_of_two()`.

Important interactions:
- Included by bitmap and many kernel-shim headers.
- Uses compiler builtins and `__atomic` operations for userspace atomicity.
