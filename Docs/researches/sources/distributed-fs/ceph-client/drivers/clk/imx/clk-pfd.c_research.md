# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pfd.c

## Purpose
Implements legacy i.MX PFD clocks, where a PLL output is multiplied by 18 and divided by a six-bit fractional divider stored in a packed PFD register.

## Important APIs, Types, And Functions
`struct clk_pfd` stores `clk_hw`, register, and PFD index. Operations include `clk_pfd_enable()`, `clk_pfd_disable()`, `clk_pfd_recalc_rate()`, `clk_pfd_determine_rate()`, `clk_pfd_set_rate()`, and `clk_pfd_is_enabled()`. Public factory `imx_clk_hw_pfd()` is exported.

## Control Flow
Enable/disable write to hardware SET/CLR alias registers for the gate bit. Rate calculation reads the per-index fraction and computes `parent * 18 / frac`. Determine/set round the requested rate to a fraction clamped to 12..35, then update the packed field using CLR and SET aliases.

## State And Persistence Behavior
State is fully in the PFD hardware register. The allocated clock object is not devm-managed and is returned to callers for normal clock framework lifetime handling.

## Dependencies And Integration Points
Used by SoC clock drivers such as i.MXRT1050 and older i.MX6-style trees. Depends on common clock framework, MMIO alias semantics, and helper allocation macros from `clk.h`.

## Risks
No explicit locking protects shared packed PFD registers, so concurrent updates would rely on higher-level serialization. Fraction zero would divide by zero if hardware contains an invalid value. Valid range clamping can produce a different rate than requested.

## Test Signals
Verify PFD rates in `clk_summary`, assigned-clock rate rounding, gate enable/disable state, and peripherals sourced from PLL2/PLL3 PFD outputs.
