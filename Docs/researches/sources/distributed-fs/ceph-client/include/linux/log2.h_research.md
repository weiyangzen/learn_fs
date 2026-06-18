<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/log2.h -->
# sources/distributed-fs/ceph-client/include/linux/log2.h

## Purpose
This header provides integer base-2 logarithm, power-of-two rounding, bit-width, and related helpers for kernel code. It supports both compile-time constant folding and runtime builtins.

## Important APIs, Types, and Functions
Functions/macros include `__ilog2_u32`, `__ilog2_u64`, `is_power_of_2`, `__roundup_pow_of_two`, `__rounddown_pow_of_two`, `const_ilog2`, `ilog2`, `roundup_pow_of_two`, `rounddown_pow_of_two`, `__order_base_2`, `order_base_2`, `__bits_per`, `bits_per`, and `max_pow_of_two_factor`.

## Control Flow
Constant macros use compile-time conditional expressions to produce folded results. Runtime helpers use bit operations such as leading-zero count and shifts. Rounding helpers convert a value to the next or previous power of two.

## State and Persistence Behavior
There is no state. Results are pure functions of integer inputs.

## Dependencies and Integration Points
It depends on `linux/types.h` and `linux/bitops.h`. Callers include allocators, block code, bitmaps, hash tables, and protocol sizing logic.

## Risks and Test Signals
Risks include undefined or special behavior for zero, overflow when rounding large values, signed/unsigned surprises, and misuse where exact powers are required. Test signals are compile-time assertions, boundary tests around 0/1/max values, and sanitizer coverage for shifts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/log2.h -->
