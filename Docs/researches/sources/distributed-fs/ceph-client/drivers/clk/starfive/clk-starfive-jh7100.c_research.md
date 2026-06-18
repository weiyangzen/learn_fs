# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7100.c

## Purpose
This built-in driver registers the main StarFive JH7100 clock generator, including root muxes, PLL fixed-factor outputs, CPU/bus clocks, DDR, video, audio source, GMAC, USB, security, and peripheral clocks.

## Important APIs, Types, And Functions
`jh7100_clk_data[]` is the main clock topology table. `jh7100_clk_get()` customizes provider lookup so IDs below `JH7100_CLK_PLL0_OUT` return register-backed clocks while PLL output IDs return the fixed-factor `priv->pll[]` clocks. `clk_starfive_jh7100_probe()` performs allocation, register mapping, fixed-factor PLL registration, table iteration, and OF provider registration.

## Control Flow
Probe creates three fixed-factor PLL outputs from `osc_sys` or `pll2_refclk`, then registers all register-backed clocks before the first PLL ID. Parent resolution handles local clocks, PLL outputs, and firmware names for `osc_sys`, `osc_aud`, `gmac_rmii_ref`, and `gmac_gr_mii_rxclk`.

## State And Persistence
Clock state persists in one register per clock index under the shared JH71x0 register format. PLLs are modeled as fixed factors instead of programmable PLLs in this driver. Several CPU, DDR, and interconnect clocks are marked `CLK_IS_CRITICAL` to prevent accidental disable.

## Dependencies And Integration Points
It depends on `dt-bindings/clock/starfive-jh7100.h`, the shared JH71x0 core, and board-provided external clocks. Consumers use the onecell provider exposed by compatible `starfive,jh7100-clkgen`.

## Risks
The loop only registers clocks below `JH7100_CLK_PLL0_OUT`; binding ID ordering is therefore a hard contract. Fixed-factor PLL modeling assumes boot firmware configured PLLs as expected. GMAC mux/inverter paths are parent-order sensitive.

## Test Signals
Boot on JH7100 should show all critical roots enabled. Useful tests include CPU/bus rate summaries, DDR stability, SDIO, USB, GMAC RGMII/RMII modes, display/video, and audio-source consumers.
