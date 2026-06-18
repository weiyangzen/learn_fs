# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-utils.c

## Purpose
This file provides a small shared helper, `div_frac_get()`, for computing Tegra divider register values from a requested child rate, parent rate, divider field width, fractional width, and Tegra divider flags. It is used by Tegra clock implementations that need consistent integer/fractional divider math.

## Important APIs, Types, And Functions
The only function is `int div_frac_get(unsigned long rate, unsigned parent_rate, u8 width, u8 frac_width, u8 flags)`. The local `div_mask(w)` macro computes the maximum register value for a divider field of width `w`. The function understands `TEGRA_DIVIDER_INT` and `TEGRA_DIVIDER_ROUND_UP` from `clk.h`.

## Control Flow
If `rate` is zero, the function returns zero. Otherwise it starts with `parent_rate`, scales by `1 << frac_width` for fractional dividers, optionally adds `rate - 1` to implement round-up division, divides by requested rate with `do_div()`, rescales integer-divider results into fractional units, clamps results below one unit to zero, subtracts one unit because Tegra dividers encode `divider - 1`, then clamps the encoded value to the bitfield mask.

## State And Persistence Behavior
The helper is pure computation. It has no static mutable state, performs no allocation, and touches no hardware. Its only persistence effect is the returned encoded divider value that callers later write into clock registers.

## Dependencies And Integration Points
The file depends on `<asm/div64.h>` for `do_div()` and on Tegra divider flag definitions in `clk.h`. It integrates with Tegra divider, peripheral, and mux/div clock registration code elsewhere in the Tegra clock driver set. Because it returns an encoded register field rather than a human divider, callers must pair it with the same flag/field semantics used by their hardware register definitions.

## Risks
`div_mask(w)` uses `1 << w`, so callers must provide widths that fit the integer expression and match hardware field sizes. A zero requested rate returns an encoded zero rather than an error, so callers must validate invalid rate requests if zero should be rejected. The function clamps over-large dividers to the maximum field value, which avoids overflow but can hide that a requested rate is below hardware capability unless the caller separately checks achieved rate.

## Test Signals
Test cases should cover zero rate, integer and fractional dividers, round-up versus truncating behavior, values below the minimum divider, values above the maximum field encoding, and known parent/rate pairs from Tegra peripheral clock tables. Cross-checking `recalc_rate` after programming a divider is the best integration signal.
