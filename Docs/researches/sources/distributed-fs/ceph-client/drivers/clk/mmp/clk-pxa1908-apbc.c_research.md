# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-pxa1908-apbc.c

Purpose: platform driver for the PXA1908 APBC clock block, exposing APB peripheral muxes and gates.

Important APIs/functions: `pxa1908_apbc_probe` maps the APBC resource, initializes a 19-clock onecell provider, and calls `pxa1908_apb_periph_clk_init`. The helper registers shared PWM gates, SWJTAG through `mmp_clk_register_apbc`, muxes for UART/SSP, and APBC gate table entries.

Control flow: on bind, all clocks are registered from static tables. UART parents are `pll1_117` or `uart_pll`; SSP parents are PLL1 divided roots. PWM clocks share intermediate APB gates.

State and persistence: platform-device managed memory and MMIO mappings; actual enable/mux state is hardware-backed.

Dependencies and integration: PXA1908 DT clock IDs, shared MMP helper functions, and platform driver matching `marvell,pxa1908-apbc`.

Risks: some gate table entries have no locks while sharing registers, so concurrent CCF operations may race if consumers manipulate related APBC clocks. `APBC_NR_CLKS` must stay aligned with binding IDs. No remove path unregisters the provider.

Test signals: module/platform bind, UART0/1 console and SSP function, PWM shared-gate behavior, SWJTAG clock lookup, and `clk_summary` ID count.
