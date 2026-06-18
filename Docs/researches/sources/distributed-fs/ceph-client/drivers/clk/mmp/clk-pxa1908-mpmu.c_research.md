# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-pxa1908-mpmu.c

Purpose: platform driver for the PXA1908 MPMU root clock provider, defining fixed PLL roots, fixed-factor PLL1 derivatives, and the UART fractional PLL.

Important APIs/functions: `pxa1908_mpmu_probe` maps the MPMU register block, creates a 39-clock onecell provider, and calls `pxa1908_pll_init`.

Control flow: registration creates fixed rates for clk32, vctcxo, and multiple PLL1 outputs; then it registers a tree of fixed factors such as `pll1_d2`, `pll1_d4`, `pll1_d96`, `pll1_32`, `pll1_208`, and `pll1_117`; finally it registers `uart_pll` from the MPMU UART PLL register.

State and persistence: fixed clocks are software constants; `uart_pll` is MMIO-backed by `clk-frac.c`. Device-managed resources are tied to the platform device.

Dependencies and integration: Linux units macros, PXA1908 DT bindings, platform CCF provider, and parent names consumed by APBC/APBCP/APMU drivers.

Risks: fixed PLL rates assume boot firmware configured expected frequencies. The UART fractional table exposes only one 14.745 MHz entry, limiting rate flexibility. Provider ID count must remain consistent with bindings.

Test signals: probe ordering before APB/APMU consumers, parent name resolution, UART baud-rate accuracy, and `clk_summary` root/factor hierarchy.
