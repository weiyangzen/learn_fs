# sources/distributed-fs/ceph-client/drivers/clk/spear/clk-vco-pll.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk-vco-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spear/clk-vco-pll.c

Purpose: implements paired SPEAr VCO and PLL clocks. The VCO programs mode/M/N feedback parameters, while the child PLL programs output divider P and forces rate changes through the VCO parent.

Important APIs and control flow: `pll_calc_rate()` calculates VCO and optional PLL rates from a `pll_rate_tbl`. `clk_pll_round_rate_index()` scans the shared table while updating the requested VCO parent rate for a requested PLL rate. PLL ops recalc by reading P, determine rate through the shared table, and set only P. VCO ops recalc by reading mode and feedback/divider fields, determine rate from table rows, and set mode/M/N fields. `clk_register_vco_pll()` allocates `clk_vco` and `clk_pll`, optionally registers a VCO gate, registers VCO and PLL clocks, returns the VCO clock, and returns the PLL/gate clocks through output parameters.

State and persistence behavior: hardware state is in mode and frequency registers plus optional enable bit. Software state is allocated `struct clk_vco` shared by the child `struct clk_pll`. No devm ownership is used; partial failure unregisters the VCO if PLL registration fails but does not fully unwind an optional VCO gate.

Dependencies and integration points: depends on CCF, raw MMIO, optional shared spinlocks, SPEAr `pll_rate_tbl`, and platform clock files passing matching mode/config registers. SPEAr1310/1340 use it for PLL1-PLL4 and then derive CPU, bus, VCO-divided, and peripheral synthesizer parents.

Risks and test signals: risks include a likely error path in `clk_pll_set_rate()` passing NULL for `prate` to `clk_pll_round_rate_index()`, which logs and returns before `i` is meaningfully selected; lack of lock-status wait despite lock bit definitions; table ordering requirements; arithmetic truncation to 10 kHz; optional gate leak on later failure; and NULL/ERR_PTR inconsistency. Test signals include PLL and VCO rates matching table rows, PLL child set-rate updating P as intended, VCO set-rate updating mode/M/N, CPU/AHB/APB rates after boot, and failure-path behavior under invalid registration arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk-vco-pll.c -->
