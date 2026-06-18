# File Research: sources/cow-pools/bcachefs-tools/include/linux/math64.h

This header provides 64-bit division and multiplication helpers. `do_div()` divides a 64-bit lvalue by a 32-bit base and returns the remainder. It defines unsigned/signed 64-bit division with remainder, full 64-by-64 division, and 64-bit by 32-bit convenience functions.

It also provides `mul_u32_u32()` and `mul_u64_u64_shr()`. The latter uses `unsigned __int128` when available through config, otherwise manually composes the 128-bit product from 32-bit limbs and shifts.
