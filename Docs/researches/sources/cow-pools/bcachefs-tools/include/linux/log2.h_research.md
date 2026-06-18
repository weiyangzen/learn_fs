# File Research: sources/cow-pools/bcachefs-tools/include/linux/log2.h

This header implements base-2 integer helpers. It provides `__ilog2_u32()`, `__ilog2_u64()`, `is_power_of_2()`, `roundup_pow_of_two()`, `rounddown_pow_of_two()`, `order_base_2()`, `bits_per()`, and `get_order()`.

The macros are constant-expression-capable where possible, using a long ternary chain for `const_ilog2()`. Runtime paths rely on `fls()`/`fls64()`. Several results are undefined for zero inputs, matching kernel semantics.
