# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-math-compat.c

Read completely: 275 lines.

This provides compiler/runtime 64-bit division and modulo helper symbols for 32-bit Linux platforms.

Key responsibilities:
- Implements unsigned and signed 64-bit divide/modulo helpers when `BITS_PER_LONG == 32`.
- Exports `__udivdi3`, `__divdi3`, `__umoddi3`, `__moddi3`, `__udivmoddi4`, and `__divmoddi4`.
- Provides ARM EABI wrappers `__aeabi_uldivmod` and `__aeabi_ldivmod` on 32-bit ARM.

Important implementation details:
- The unsigned division algorithm is based on Hacker's Delight double-word division and avoids Linux `div64_u64()` because older kernels could return incorrect results.
- 32-bit divisor cases use `do_div()` directly or a grade-school two-half quotient path.
- 64-bit divisor cases normalize the divisor, estimate the quotient, and correct it if needed.
- Signed helpers operate by dividing absolute values and restoring quotient/remainder signs.
- ARM EABI helpers marshal quotient and remainder into `r0-r3` as required by the ABI.

Dependencies and interactions:
- Only compiled on 32-bit long platforms.
- Satisfies compiler-emitted helper references from other OpenZFS/SPL code using 64-bit arithmetic.

Reliability notes:
- This is low-level arithmetic infrastructure; divide-by-zero behavior is not explicitly guarded and follows helper/CPU expectations.
