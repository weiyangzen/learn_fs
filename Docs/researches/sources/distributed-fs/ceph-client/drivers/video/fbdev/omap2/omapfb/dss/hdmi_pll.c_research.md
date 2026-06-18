# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi_pll.c

## Purpose
`hdmi_pll.c` implements HDMI-specific PLL setup on top of the generic DSS PLL helpers. It computes HDMI TMDS-derived PLL parameters, maps the PLLCTRL register block, registers the PLL with the DSS PLL registry, and controls HDMI wrapper PLL power.

## Important APIs, types, and functions
Public APIs are `hdmi_pll_dump`, `hdmi_pll_compute`, `hdmi_pll_init`, and `hdmi_pll_uninit`. The PLL ops are `hdmi_pll_enable`, `hdmi_pll_disable`, and `dss_pll_write_config_type_b` through `dsi_pll_ops`. Hardware descriptions are `dss_omap4_hdmi_pll_hw` and `dss_omap5_hdmi_pll_hw`.

## Control Flow
`hdmi_pll_compute` reads `sys_clk`, computes target bit clock as TMDS times ten, selects `n` to keep Fint below hardware max, chooses `m2` to keep DCO above the minimum, computes integer and fractional M, derives `clkout`, and stores sigma-delta and clock info. Init maps `"pll"`, gets `"sys_clk"`, chooses OMAP4 or OMAP5/DRA7 hardware limits, and registers the PLL. Enable turns on DSS HDMI PLL control and wrapper PLL power; disable powers it off and clears DSS control.

## State and Persistence
Per-instance state is `struct hdmi_pll_data`, containing mapped base, wrapper pointer, and embedded `struct dss_pll`. Generic PLL state caches the last `dss_pll_clock_info`. Hardware state persists in PLLCTRL registers and wrapper power control while enabled.

## Dependencies and Integration Points
The file depends on clock APIs, DSS feature/version detection, wrapper power helpers from `hdmi_wp.c`, generic PLL code in `pll.c`, and HDMI display power-on flows in `hdmi5.c` or the OMAP4 counterpart.

## Risks
Clock math assumes the requested TMDS target is reachable and does not search alternatives; bad parent clock rates or extreme pixel clocks can produce out-of-range PLL parameters. Enable/disable errors from wrapper power transitions are timeout-based. The ops variable name `dsi_pll_ops` is misleading but functional.

## Test Signals
Validate computed N/M/MF/M2/SD for common HDMI pixel clocks, PLL lock across OMAP4 and OMAP5/DRA7, failure paths for missing resources/clocks, power on/off sequencing, register dumps, and video output stability across mode changes.
