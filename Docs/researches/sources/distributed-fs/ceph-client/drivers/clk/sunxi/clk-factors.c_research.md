# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-factors.c

## Purpose
`clk-factors.c` is the legacy adjustable factor-based clock implementation used before sunxi-ng. It registers composite clocks with optional mux and gate around a custom factor-rate component.

## Important APIs, Types, And Functions
Important functions are `clk_factors_recalc_rate()`, `clk_factors_determine_rate()`, `clk_factors_set_rate()`, `__sunxi_factors_register()`, public `sunxi_factors_register()`, `sunxi_factors_register_critical()`, and `sunxi_factors_unregister()`.

## Control Flow
Rate recalculation decodes N/K/M/P fields and either calls a custom recalc hook or applies `(parent * (n + n_start) * (k + 1) >> p) / (m + 1)`. Rate determination tries all parents and calls the SoC getter. Set-rate computes factors, updates fields under an optional lock, writes the register, and delays for PLL stabilization. Registration builds a composite with optional mux/gate and an OF provider.

## State And Persistence
State includes allocated `clk_factors`, optional mux/gate structures, and hardware factor fields. No disk persistence exists; unregister frees allocated pieces but notes composite internals may leak.

## Dependencies And Integration Points
It depends on CCF, OF, MMIO, allocation helpers, and legacy factor-data callbacks. It integrates with `clk-mod0.c` and other legacy sunxi clock providers.

## Risks
The generic formula depends on callback-specific raw field conventions. The register mask macros assume nonzero widths. The register function currently passes `CLK_IS_CRITICAL` to composites regardless of the `flags` argument, which is a behavioral detail to preserve or fix deliberately.

## Test Signals
Test with legacy MOD0/MMC/MBUS clocks, PLL factor clocks, parent-rate propagation, and clk-summary recalculated rates.
