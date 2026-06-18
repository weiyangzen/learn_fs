# File Research: sources/cow-pools/bcachefs-tools/include/linux/math.h

This header supplies kernel math macros and declarations. It includes power-of-two rounding (`round_up`, `round_down`), arbitrary rounding (`roundup`, `rounddown`), division rounding helpers, `mult_frac()`, `sector_div`, reciprocal scaling, and integer power/sqrt declarations.

It defines `abs()` using nested compile-time type selection to preserve signed type behavior. It also bridges 64-bit square root handling depending on word size.
