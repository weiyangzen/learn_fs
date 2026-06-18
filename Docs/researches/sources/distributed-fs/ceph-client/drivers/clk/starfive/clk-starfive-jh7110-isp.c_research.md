# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-isp.c

## Purpose
This module registers the JH7110 ISP clock controller for VIN/MIPI/ISP wrapper clocks and coordinates required top-domain clocks, resets, and runtime PM.

## Important APIs, Types, And Functions
`jh7110_ispclk_data[]` describes local clocks. `jh7110_isp_top_clks[]` names required top SYS clocks `isp_top_core` and `isp_top_axi`. `jh7110_isp_top_rst_init()` obtains shared reset controls and deasserts them. Runtime PM callbacks disable and enable the top clocks. `jh7110_ispcrg_probe()` performs all registration and reset setup.

## Control Flow
Probe allocates clock and top-clock state, maps registers, gets top clocks, enables runtime PM and powers the domain, deasserts shared top resets, registers local clocks with local or firmware parents, adds the OF provider, and registers reset auxiliary device `rst-isp`. Error handling unwinds runtime PM.

## State And Persistence
State includes hardware clock registers, runtime PM state, prepared/enabled top clocks, reset deassertion state, and driver-private top-clock metadata stored with `dev_set_drvdata()`.

## Dependencies And Integration Points
It depends on JH7110 SYS and PMU/power-domain support. Parent firmware names include `isp_top_core`, `isp_top_axi`, `noc_bus_isp_axi`, and `dvp_clk`. It uses shared JH71x0 operations and the JH7110 reset auxiliary-device helper.

## Risks
`pm_runtime_get_sync()` failure returns without disabling runtime PM, which can leave PM enabled on probe failure. Parent-clock and power-domain availability are mandatory. Pixel-path muxes and inversion depend on correct external DVP/MIPI wiring.

## Test Signals
Probe under active power domain, runtime suspend/resume, reset deassertion, VIN/MIPI capture, ISP wrapper clocks, and error-injection around missing top clocks or resets are important validation points.
