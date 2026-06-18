# sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/megacores_pll.c

Purpose: calculates and programs Unisoc MIPI D-PHY PLL and timing registers for the SPRD DSI host.

Important APIs and types: `dphy_pll_config()` reads the attached DSI device `hs_rate`, computes PLL fields with `dphy_calc_pll_param()`, and writes test-interface registers via regmap. `dphy_timing_config()` computes LP/HS request, prepare, zero, trail, exit, and clock-post timings from PLL frequency and writes lane timing registers. `struct dphy_pll` fields are declared in `sprd_dsi.h`.

Control flow: DSI enable calls `dphy_pll_config()` and `dphy_timing_config()` from `sprd_dphy_init()`. PLL calculation scales the requested frequency into the valid VCO band by selecting an output divider, chooses VCO band/filter settings, computes integer and fractional N/K values, then writes a fixed list of PHY test registers.

State and persistence: computed PLL fields persist in `ctx->pll` for the life of the DSI context and for timing calculations. Hardware registers persist until DPHY reset/fini.

Dependencies and integration: depends on `regmap` access provided by the DSI PHY test interface, `do_div()`, MIPI DSI `hs_rate`, and register definitions implicit in the PHY.

Risks: valid VCO range is hard-coded for the sharkle PHY; other SoCs may need different bands/refclk. Arithmetic uses integer scaling and can underflow after subtracting constants in timing formulas if parameters are unexpected. `dphy_pll_config()` ignores any error return from individual `regmap_write()` calls inside `dphy_set_pll_reg()`.

Test signals: panel modes at low/high lane rates, PLL lock after configuration, timing register readback, and invalid `hs_rate` error paths.
