# sources/distributed-fs/ceph-client/drivers/clk/meson/clk-pll.c

## Purpose
`clk-pll.c` implements shared Meson PLL common-clock operations. It models PLL DCO rates as `parent * (m + frac/frac_max) / n`, supports table-driven or range-driven settings, handles lock polling, initialization sequences, enable/disable, PCIe-specific enable retry, and mutable/read-only ops.

## Important APIs, Types, And Functions
Exports are `meson_clk_pll_ops`, `meson_clk_pll_ro_ops`, and `meson_clk_pcie_pll_ops`. Key helpers include `__pll_params_to_rate()`, `__pll_params_with_frac()`, `meson_clk_get_pll_settings()`, `meson_clk_pll_determine_rate()`, `meson_clk_pll_wait_lock()`, `meson_clk_pll_is_enabled()`, `meson_clk_pll_init()`, `meson_clk_pll_enable()`, `meson_clk_pll_disable()`, and `meson_clk_pll_set_rate()`.

## Control Flow
Rate determination searches either a multiplier range or a parameter table. It chooses the best integer M/N pair, then optionally improves the result with a fractional field. Initialization obtains a regmap, optionally skips reinitializing a bootloader-enabled PLL when `CLK_MESON_PLL_NOINIT_ENABLED` is set, otherwise asserts reset, writes init registers, and deasserts reset. Enable asserts reset if available, enables the PLL, releases reset, optionally follows newer self-adaption current and lock-detect sequences, then polls lock. Set-rate disables an enabled PLL, writes N/M/fractional settings, re-enables it, and attempts to restore the old rate if relock fails.

## State, Persistence, And Dependencies
Persistent state is entirely in PLL control registers described by `struct meson_clk_pll_data`: enable, M, N, fractional, lock, reset, optional current/lock-detect fields, init sequences, range/table data, fractional max, and flags. Dependencies include `clk-regmap.h`, `clk-pll.h`, `parm.h`, regmap multi-write, Linux delay helpers, 64-bit math helpers, and common clock callbacks.

## Integration Points
SoC clock-controller files use this helper for system, GP, HIFI, HDMI, PCIe, and other PLLs. The PCIe ops intentionally reuse init/enable sequencing for a fixed precise 100 MHz reference clock and omit `set_rate`. Downstream dividers and muxes rely on accurate PLL recalc and set-rate propagation through `CLK_SET_RATE_PARENT`.

## Risks And Edge Cases
PLL lock polling waits up to about 100 ms and returns `-ETIMEDOUT`; enable maps that to `-EIO`. The set-rate failure path recursively calls `meson_clk_pll_set_rate()` to restore the old rate, and the source comment notes this could be unsafe if the old rate also cannot lock. Fractional calculations use round-up or round-closest flags and clamp to `frac_max - 1`, so exactness depends on descriptor fields. A zero hardware N returns rate zero to avoid division by zero. Init sequences can perturb bootloader-programmed PLLs unless the no-init-enabled flag is correctly applied.

## Test Signals
High-value tests include recalc for integer and fractional PLLs, table and range selection, round-down versus round-closest behavior, zero-N handling, enable/disable bit sequences, lock timeout behavior, PCIe retry behavior, no-init-enabled boot handoff, and set-rate failure recovery. Hardware boot tests should monitor PLL lock status and downstream clock stability.
