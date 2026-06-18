# sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-pll.c

## Purpose
Implements simple Berlin2 system PLL rate reporting. It reads feedback, reference, and VCO divider fields and exposes the result as a CCF clock.

## Important APIs, Types, And Functions
Private `struct berlin2_pll` stores `clk_hw`, base, and a copied `berlin2_pll_map`. `berlin2_pll_recalc_rate` implements the rate formula, and `berlin2_pll_register` allocates/registers a PLL clock.

## Control Flow
Registration copies the map, attaches one parent, and calls `clk_hw_register`. Recalc reads `SPLL_CTRL0` for feedback and reference divisors, reads `SPLL_CTRL1` for the VCO divider select, maps that selector through `map->vcodiv`, multiplies by `map->mult`, and divides by refdiv and vcodiv.

## State And Persistence
Per-clock software state is static after registration. Hardware registers persist PLL configuration. The driver only reports rates; it does not enable, disable, or reprogram PLL settings.

## Dependencies And Integration Points
Used by `bg2.c` and `bg2q.c` with maps from `berlin2-pll.h`. Integrates with common clock framework parent/rate propagation.

## Risks And Edge Cases
Zero refdiv or vcodiv values are warned and treated as one to avoid divide-by-zero, which can hide bad hardware state. Failed registration leaks the allocated PLL object. No locking is used because this driver only reads PLL registers.

## Test Signals
Known register images should produce expected rates, zero divisor warnings should not crash, and BG2/BG2Q maps should select the correct shifts and VCO divider tables.
