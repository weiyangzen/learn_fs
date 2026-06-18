# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-vout.c

## Purpose
This module registers the JH7110 video-output clock controller for display controller, DSI, MIPI TX DPHY, HDMI, and APB clocks, with runtime PM and top reset handling.

## Important APIs, Types, And Functions
`jh7110_voutclk_data[]` encodes local clocks. `jh7110_vout_top_clks[]` names required top clocks `vout_src` and `vout_top_ahb`. `jh7110_vout_top_rst_init()` deasserts the shared top reset. Runtime PM callbacks gate and ungate top clocks. `jh7110_voutcrg_probe()` registers clocks and reset auxiliary device `rst-vo`.

## Control Flow
Probe allocates private and top-clock state, maps registers, gets top clocks, enables runtime PM using `pm_runtime_resume_and_get()`, deasserts top reset, registers each local clock with local or firmware parent data, adds the OF provider, and registers reset ID 4. Remove drops runtime PM usage and disables PM.

## State And Persistence
State includes display clock registers, runtime PM power state, enabled top clocks, shared reset state, and `jh7110_top_sysclk` metadata.

## Dependencies And Integration Points
It depends on SYS top clocks, PMU/power-domain support, resets, and external firmware parents including `vout_top_axi`, `vout_top_hdmitx0_mclk`, `i2stx0_bclk`, and `hdmitx0_pixelclk`. Consumers are DRM/display, DSI, HDMI, and DPHY drivers.

## Risks
Display pixel clock parent order is mode-sensitive. Missing top clocks or power-domain support prevents probe. Error unwinding handles PM state, but reset deassertion is not reasserted on later failure. HDMI pixel clock is an external dependency not produced locally.

## Test Signals
Runtime suspend/resume, display modes through DC8200, DSI and HDMI output, top reset behavior, and missing-parent probe deferral are important tests.
