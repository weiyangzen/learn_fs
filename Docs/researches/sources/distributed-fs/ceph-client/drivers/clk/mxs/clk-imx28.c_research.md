# sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-imx28.c

Purpose: Provides the i.MX28 clock tree as an early OF one-cell provider for `"fsl,imx28-clkctrl"`. It extends the i.MX23 pattern with multiple PLLs, four SSP channels, Ethernet/PTP, FlexCAN, dual USB PHY gates, and SAIF clock-mux selection support.

Important APIs, types, and functions: `mx28_clocks_init()` is the early init entry. `mxs_saif_clkmux_select()` is an exported SoC helper that programs the SAIF input clock mux in DIGCTL. `clk_misc_init()` sets WFI behavior, fixes a bad ENET divider default, clears SAIF and SSP bypasses, enables SAIF fractional mode, clears ENET sleep, and sets IO fractional references. `enum imx28_clk` defines one-cell indexes.

Control flow: Init maps `"fsl,imx28-digctl"` and CLKCTRL, applies misc programming, registers fixed, PLL, reference, mux, divider, fractional, fixed-factor, and gate clocks, validates no `IS_ERR()` entries, adds the provider, registers the `enet_out` clkdev alias, and enables `cpu`, `hbus`, `xbus`, `emi`, and `uart`.

State and persistence: Static `clkctrl` and `digctrl` hold MMIO bases. Clock state is persisted in hardware registers and CCF registrations. `mxs_saif_clkmux_select()` can later mutate DIGCTL mux state.

Dependencies and integration points: Depends on MXS common helpers, DT indexes matching `enum imx28_clk`, and the DIGCTL node. Ethernet users can use the `enet_out` clkdev registration. SAIF users depend on the exported clkmux selector.

Risks: The helper accepts only mux values 0..3 but has no locking around the DIGCTL write pair. Missing DIGCTL mapping warns but later USB/SAIF accesses depend on it. The ENET divider quirk and IO fractional defaults are policy decisions that can affect board-specific expectations.

Test signals: Boot with i.MX28 DT should register all clocks without errors. Validate SSP0-3 can derive from ref_io0/ref_io1, SAIF clocks use fractional divisors, `enet_out` exists as a clkdev lookup, and `mxs_saif_clkmux_select()` returns `-EINVAL` for values above 3.
