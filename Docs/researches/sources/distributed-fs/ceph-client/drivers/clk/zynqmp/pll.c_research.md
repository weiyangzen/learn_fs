# sources/distributed-fs/ceph-client/drivers/clk/zynqmp/pll.c

Purpose: implements ZynqMP PLL clocks controlled through PM firmware, including integer and fractional modes.

Important APIs/types/functions: `struct zynqmp_pll`, `enum pll_mode`, `zynqmp_clk_register_pll()`, `zynqmp_pll_get_mode()`, `zynqmp_pll_set_mode()`, `zynqmp_pll_determine_rate()`, `zynqmp_pll_recalc_rate()`, `zynqmp_pll_set_rate()`, and enable/disable/is_enabled callbacks.

Control flow: CCF rate selection keeps the VCO in the 1.5 GHz to 3.0 GHz range and clamps feedback divider values to 25..125. Recalc reads divider and optional fractional data. Set-rate chooses fractional mode when the requested rate cannot be represented by an integer feedback divider, writes divider and fractional data, and then enable handles any required PLL mode refresh.

State and persistence: PLL mode, divider, enable state, and fractional data live in firmware/hardware. `set_pll_mode` is a local latch used so enable is not skipped immediately after a fractional-mode IOCTL.

Dependencies and integration points: called from `clkc.c` for `TYPE_PLL` topology nodes. Depends on ZynqMP PM APIs for clock state, divider, fractional mode, and fractional data.

Risks: `zynqmp_pm_get_pll_frac_data()` and `zynqmp_pm_set_pll_frac_data()` return values are not checked. Rate arithmetic uses `long` intermediates and can be sensitive to large rates. A firmware `-EUSERS` set-divider result warns for shared PLL ownership but still continues fractional data handling.

Test signals: integer and fractional PLL rate programming, VCO boundary requests, shared-user firmware errors, enable after mode switch, and clock summaries comparing expected versus actual rates.
