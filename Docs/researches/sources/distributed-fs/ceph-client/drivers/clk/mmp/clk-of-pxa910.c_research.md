# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-of-pxa910.c

Purpose: early OF clock controller for PXA910, registering MPMU roots/factors, APBC and APBCP peripheral clocks, APMU clocks, and reset cells.

Important APIs/functions: `pxa910_clk_init` is the `CLK_OF_DECLARE` entry. `pxa910_pll_init`, `pxa910_apb_periph_clk_init`, `pxa910_axi_periph_clk_init`, and `pxa910_clk_reset_init` provide staged registration.

Control flow: init maps MPMU/APMU/APBC/APBCP resources, initializes a 200-entry onecell provider, registers fixed root and factor clocks plus UART fractional PLL, registers APBC and APBCP muxes/gates, registers APMU mux/div/gates for DFC/USB/SDH/display/camera, and creates reset cells from APBC plus APBCP gate arrays.

State and persistence: hardware MMIO holds clock/reset state. Allocated unit and reset cells are permanent after early init.

Dependencies and integration: uses PXA910 DT clock bindings, the shared MMP clock helpers, and reset-controller registration.

Risks: the APBCP reset loop indexes `apbc_gate_clks` and `apbc_base` instead of `apbcp_gate_clks` and `apbcp_base`, which looks like a real reset mapping bug. Failure paths correctly unmap resources before provider registration but not after partial clock registration.

Test signals: PXA910 boot with APBCP UART2/TWSI1 reset phandles, serial and SDH clocks, USB gates, and static validation of reset-cell register addresses.
