<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/math.h -->
# sources/distributed-fs/ceph-client/include/linux/math.h

## Purpose
This header provides common integer math helpers for kernel code: rounding, division with rounding, fractional structures, overflow-avoiding multiply/divide, absolute values, reciprocal scaling, and integer powers/square roots.

## Important APIs, types, and functions
Macros include `round_up`, `round_down`, `DIV_ROUND_UP_POW2`, `DIV_ROUND_UP`, `DIV_ROUND_DOWN_ULL`, `DIV_ROUND_UP_ULL`, `roundup`, `rounddown`, `DIV_ROUND_CLOSEST`, `DIV_ROUND_CLOSEST_ULL`, `mult_frac`, `sector_div`, `abs`, and `abs_diff`. It declares fixed-size fraction structs such as `struct u32_fract`, defines `reciprocal_scale()`, and declares `int_pow`, `int_sqrt`, and `int_sqrt64`.

## Control flow
Most helpers are compile-time macros or inline arithmetic. `round_up/down` assume power-of-two alignment; `roundup/down` handle arbitrary multiples. `mult_frac()` splits quotient and remainder to reduce overflow in `x * n / d`; `reciprocal_scale()` maps a 32-bit value into a right-open interval using a 64-bit product.

## State and persistence
There is no state. All helpers operate on arguments.

## Dependencies and integration points
It depends on Linux types, architecture `do_div`, and UAPI kernel math macros. It is broadly included by drivers, filesystems, block code, and memory management.

## Risks and test signals
Risks include divide-by-zero, overflow in rounded additions, using power-of-two helpers with non-power-of-two divisors, side-effecting macro arguments, and `abs()` on signed minimum values. Test boundary values, 32-bit builds, unsigned and signed types, sector-sized divisions, and compiler type checking in `abs_diff()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/math.h -->
