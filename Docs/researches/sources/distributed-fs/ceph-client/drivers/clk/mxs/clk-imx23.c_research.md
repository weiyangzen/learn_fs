# sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-imx23.c

Purpose: Provides the i.MX23 clock tree as an early OF one-cell provider for `"fsl,imx23-clkctrl"`. It registers fixed clocks, PLL/reference clocks, muxes, integer and fractional dividers, gates, and initial always-on clocks.

Important APIs, types, and functions: `mx23_clocks_init()` is the `CLK_OF_DECLARE()` entry. `clk_misc_init()` programs WFI clock gating, clears SAIF/SSP bypasses, enables SAIF fractional divider mode, and programs the IO fractional reference to 288 MHz. The `enum imx23_clk` indexes the `clks[]` provider array. Helper calls include `mxs_clk_fixed()`, `mxs_clk_pll()`, `mxs_clk_ref()`, `mxs_clk_mux()`, `mxs_clk_div()`, `mxs_clk_frac()`, `mxs_clk_gate()`, and fixed-factor registration.

Control flow: Init maps the DIGCTL node and the CLKCTRL node, applies misc clock programming, registers every clock in enum order, checks for `IS_ERR()`, publishes `clk_data` through `of_clk_add_provider()`, and prepares/enables core clocks `cpu`, `hbus`, `xbus`, `emi`, and `uart`.

State and persistence: `clkctrl` and `digctrl` are static MMIO bases. The registered clock tree persists globally. Hardware registers hold mux, divider, PLL, and gate state; early init also mutates power/performance defaults.

Dependencies and integration points: Depends on the `"fsl,imx23-digctl"` node, MXS helper files, DT clock indexes matching `enum imx23_clk`, and CCF one-cell lookup. Consumers such as SSP, SAIF, LCDIF, GPMI, USB, and UART rely on these names and indexes.

Risks: Missing DIGCTL mapping only warns but later USB gate registration uses `DIGCTRL`, so NULL mapping can become unsafe. The init returns on the first registration error, potentially leaving a partially registered clock tree without provider registration. Register offsets and busy bits are hard-coded and must match the SoC reference manual.

Test signals: Boot should show no i.MX23 registration errors. `clk_summary` should expose all enum clocks and show the init-on clocks prepared. SSP parent should be `ref_io` rather than `ref_xtal`, SAIF should use fractional mode, and USB gate should resolve through DIGCTL.
