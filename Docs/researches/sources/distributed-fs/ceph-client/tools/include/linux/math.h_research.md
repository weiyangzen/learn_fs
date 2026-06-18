<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/math.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/math.h

## Purpose
This header provides simple integer rounding and division helper macros for tools code.

## APIs And Flow
It defines `__round_mask()`, `round_up()`, `round_down()`, `DIV_ROUND_UP()`, and `roundup()`. The macros use typed temporaries or typed masks so argument evaluation and bit width are controlled.

## State, Dependencies, Risks, Tests
There is no state and no includes. Integration points are allocation sizing, buffer alignment, and page or record boundary calculations. Risks include divisor zero, non-power-of-two use with bitmask-based `round_up` and `round_down`, overflow in `(n + d - 1)`, and side effects in arguments not protected by every macro. Tests should cover powers of two, non-powers where supported, boundary values, type widths, and expressions with side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/math.h -->
