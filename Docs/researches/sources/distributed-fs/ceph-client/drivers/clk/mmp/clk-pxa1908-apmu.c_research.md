# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-pxa1908-apmu.c

Purpose: platform driver for the PXA1908 APMU clock block, including PLL1 branch gates, SDH mix clocks, USB/SDH gates, and creation of an auxiliary power controller device.

Important APIs/functions: `pxa1908_apmu_probe` maps MMIO, creates an auxiliary `"power"` device, initializes a 17-clock provider, and calls `pxa1908_axi_periph_clk_init`. That helper registers general PLL1 gates, three SDH mix clocks, and APMU gates.

Control flow: probe sets up power-controller integration before registering clocks. Each SDH controller has its own mix clock using parent choices `pll1_416` and `pll1_624`; gates use `CLK_SET_RATE_UNGATE` so rates can change while gated.

State and persistence: hardware registers hold clock state; the auxiliary device links the same platform device to the power-domain side.

Dependencies and integration: CCF, auxiliary bus, platform driver, PXA1908 bindings, and shared MMP mix/gate helpers.

Risks: reusing a single global `sdh_mix_config` while mutating its register address is safe only because `mmp_clk_register_mix` copies config fields. Missing remove cleanup leaves provider lifetime tied to device lifetime. Power auxiliary creation failure aborts clock registration.

Test signals: APMU bind, auxiliary power device appearance, SDH0-2 rate changes, USB clock enable, and PLL1 gate visibility in `clk_summary`.
