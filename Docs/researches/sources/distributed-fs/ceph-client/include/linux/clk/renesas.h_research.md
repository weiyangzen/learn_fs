# sources/distributed-fs/ceph-client/include/linux/clk/renesas.h

Purpose: This header gathers Renesas CPG/MSTP/MSSR integration hooks and RZ/V2H PLL parameter-search structures for Renesas clock drivers.

Important APIs/types/functions: It declares `cpg_mstp_add_clk_domain`, optional `cpg_mstp_attach_dev`/`detach_dev`, optional `cpg_mssr_attach_dev`/`detach_dev`, `rzg2l_cpg_dsi_div_set_divider`, enum targets `PLL5_TARGET_DPI` and `PLL5_TARGET_DSI`, PLL limit/parameter structures `struct rzv2h_pll_limits`, `struct rzv2h_pll_pars`, and `struct rzv2h_pll_div_pars`, macro `RZV2H_CPG_PLL_DSI_LIMITS`, and helpers `rzv2h_get_pll_pars` and `rzv2h_get_pll_divs_pars`. Disabled configs provide `NULL`, no-op, or `false` fallbacks.

Control flow: CPG drivers add clock power domains and attach/detach devices through PM-domain callbacks when corresponding drivers are built. RZ/G2L DSI code can update PLL5 divider state. RZ/V2H code supplies frequency targets in millihertz and receives best PLL/divider parameters constrained by the limits structures.

State and persistence behavior: Runtime state is in Renesas CPG registers, PM domains, and calculated PLL parameter structs. The header includes parameter-cache fields such as best frequencies and signed error values but stores nothing globally itself.

Dependencies and integration points: It includes `<linux/clk-provider.h>`, `<linux/types.h>`, and `<linux/units.h>`. It integrates CPG clock providers, generic PM domains, display DSI/DPI consumers, and Renesas SoC-specific PLL search implementations.

Risks: Config-dependent `NULL` attach hooks must be handled by PM-domain users. Millihertz units in PLL helpers are easy to confuse with hertz. Wrong limits or divider tables can select unstable PLL settings. DSI/DPI target confusion can break display clocking.

Test signals: Renesas boot and PM-domain attach logs, display clock-rate validation, PLL parameter unit tests, DSI/DPI mode-setting tests, and suspend/resume coverage are meaningful signals.
