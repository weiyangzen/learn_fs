# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-divider.c

Implements Tegra fractional divider clocks and a special memory-controller divider helper.

`tegra_clk_frac_div_ops` recalculates, determines, sets, and restores divider rates. Recalc reads the divider field, optionally bypasses UART division when `PERIPH_CLK_UART_DIV_ENB` is clear, then computes `parent * frac_base / (div + frac_base)`. Set-rate calculates the encoded divisor with `div_frac_get()`, updates the field under an optional spinlock, toggles UART divider enable, and sets fixed PLL output override when requested. `tegra_clk_register_divider()` allocates and registers a `tegra_clk_frac_div`. `tegra_clk_register_mc()` registers a critical read-only divider-table clock for MC.

Divider state persists in MMIO fields; optional UART enable and fixed override bits are coupled to divider programming. Restore context reprograms the current rate after suspend. The code depends on CCF divider math helpers, Tegra-specific flags from `clk.h`, MMIO access, and optional shared spinlocks. Peripheral clock wrappers embed this divider implementation.

Fractional rounding and UART bypass semantics are the main risks. `determine_rate` relies on `best_parent_rate` already being populated by CCF. Test signals include serial baud stability, `clk_round_rate()` accuracy for fractional dividers, context restore after suspend, and MC divider remaining critical/read-only.
