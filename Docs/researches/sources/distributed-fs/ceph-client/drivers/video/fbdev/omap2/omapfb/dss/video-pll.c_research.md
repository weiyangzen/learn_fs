# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/video-pll.c

## Purpose
`video-pll.c` implements DRA7 video PLL instances on top of the generic DSS PLL framework. It maps PLL and clock-control resources, obtains input clocks, controls SCP and PLL power bits, registers PLLs named `video0`/`video1`, and unregisters them.

## Important APIs, types, and functions
The public APIs are `dss_video_pll_init` and `dss_video_pll_uninit`. The private `struct dss_video_pll` wraps `struct dss_pll`, device pointer, and `clkctrl_base`. Important helpers are `dss_dpll_enable_scp_clk`, `dss_dpll_disable_scp_clk`, `dss_dpll_power_enable`, `dss_dpll_power_disable`, `dss_video_pll_enable`, and `dss_video_pll_disable`. Hardware limits live in `dss_dra7_video_pll_hw`.

## Control Flow
Init maps `"pll1"`/`"pll2"` and matching clock-control resources, gets `"video1_clk"`/`"video2_clk"`, allocates state, fills `struct dss_pll` fields, and registers it. Enable runtime-resumes DSS, enables DSS PLL routing, enables SCP clock, waits for reset done, powers the PLL on with a fixed delay, and returns. Disable powers off, disables SCP clock, clears DSS routing, and runtime-suspends DSS.

## State and Persistence
Runtime state is devm-managed `struct dss_video_pll` plus the generic PLL registry entry. Hardware state persists in PLL control and clock-control registers while active. Cached clock configuration is managed by `pll.c`.

## Dependencies and Integration Points
It depends on DRA7 DSS resources, clocks, optional regulator passed by caller, generic PLL type-A programming, DSS runtime PM, and DSS PLL control routing.

## Risks
Only two IDs are supported by fixed arrays and no explicit bounds check protects bad `id`. DRA7 PLL power status is not trusted, so enable uses a fixed sleep. Error after SCP enable must unwind runtime and DSS control correctly. Resource names must match DT/platform data exactly.

## Test Signals
Test both video PLL IDs, missing resource/clock paths, invalid id handling, reset timeout, enable/disable balance, type-A config programming through `dss_pll_set_config`, regulator involvement, and DSS runtime PM reference balance.
