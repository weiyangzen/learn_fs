# sources/distributed-fs/ceph-client/drivers/clk/clk-sparx5.c

Purpose: built-in platform CCF driver for Microchip Sparx5 DPLL clocks. It exposes nine PLL outputs named by binding order and supports exact integer or fractional divisor programming.

Important APIs/types/functions: `struct s5_clk_data` owns MMIO base and an array of `struct s5_hw_clk`; `struct s5_pll_conf` captures divider and fractional rotation fields. Key helpers are `s5_calc_freq()`, `s5_search_fractional()`, `s5_calc_params()`, `s5_pll_enable()`, `s5_pll_disable()`, `s5_pll_set_rate()`, `s5_pll_recalc_rate()`, `s5_pll_determine_rate()`, and `s5_clk_hw_get()`. `s5_pll_ops` is the shared CCF operation table.

Control flow: `s5_clk_probe()` maps one MMIO resource, creates one `clk_hw` per binding clock, points each at a 4-byte register slot, and registers an OF provider. Runtime determine_rate searches for a divider/fractional rotation configuration matching the requested rate against the best parent rate. set_rate requires the effective computed rate to exactly equal the requested rate, preserves the enable bit, writes divider and optional fractional fields, and returns `-EOPNOTSUPP` when only an approximate match exists. recalc returns zero when disabled.

State and persistence: all hardware state is in one register per clock. No software cache is retained. The enable bit is preserved across set_rate. The driver is built-in via `builtin_platform_driver()`, so it is expected to be available early and is not unloadable as a module.

Dependencies and integration: depends on MMIO, platform driver, CCF, bitfield helpers, `dt-bindings/clock/microchip,sparx5.h`, and compatible `microchip,sparx5-dpll`. Consumers use a single phandle index into `N_CLOCKS`.

Risks: `s5_calc_params()` can leave the selected configuration underinitialized when the rounded and truncated divider are equal but the fractional search is not exact, because only the alternate path assigns in that case. Fractional search stores `best` only after an improvement, so impossible searches would be fragile. set_rate rejects approximate rates even though determine_rate can return the nearest rate. No register locking is used. recalc divides by the encoded divider and assumes it is nonzero.

Test signals: verify all nine IDs and names, exact integer rates, exact fractional rates, unsupported approximate rates, enable/disable bit behavior, disabled recalc, and invalid phandle index. No direct tests are present.
