# sources/distributed-fs/ceph-client/drivers/clk/clk-tps68470.c

Purpose: platform CCF driver for the TPS68470 PMIC clock output used by camera sensor stacks. It exposes a single PLL-derived clock with three supported output rates: 19.2 MHz, 20 MHz, and 24 MHz.

Important APIs/types/functions: `struct tps68470_clkdata` holds the clock hardware, parent PMIC regmap, and cached rate. `clk_freqs[]` maps supported rates to XTALDIV/PLLDIV/POSTDIV/BUCKDIV/BOOSTDIV register values. CCF ops are `tps68470_clk_is_prepared`, `tps68470_clk_prepare`, `tps68470_clk_unprepare`, `tps68470_clk_recalc_rate`, `tps68470_clk_determine_rate`, and `tps68470_clk_set_rate`. Probe registers both a generic clkdev name and platform-data consumer aliases.

Control flow: probe obtains the parent MFD regmap, initializes the clock with `CLK_SET_RATE_GATE`, programs the default 19.2 MHz rate, registers the hardware clock, registers clkdev aliases, and optionally registers aliases for ACPI/platform-data consumers. determine_rate chooses the nearest supported table entry; set_rate requires exact support and writes boost/buck/PLL/divider/drive/source registers; prepare enables outputs A and B, enables the PLL, and waits 4-5 ms; unprepare disables PLL and tri-states outputs.

State and persistence: PMIC registers persist PLL configuration, output enable/tri-state, dividers, and drive strength. Software caches only the selected rate. Init uses `subsys_initcall()` so built-in ordering precedes camera sensor drivers.

Dependencies and integration: depends on the TPS68470 MFD regmap, platform data consumer list, CCF, clkdev, and ACPI/platform-device ordering. It integrates with camera sensors that request named clock aliases.

Risks: regmap write/update return values are ignored in prepare/unprepare/set_rate, so I/O failures are silent. Parent crystal is assumed to match the hard-coded 20 MHz-derived table. determine_rate rounds to a supported rate but set_rate rejects non-exact requests. PLL lock bit is not trusted; fixed sleep is used. Consumer alias registration loops overwrite `ret` and return only the final alias result.

Test signals: probe ordering with ACPI camera devices, exact supported set_rate values, rejected unsupported rates, clkdev alias lookup, prepare/unprepare register sequencing, and recalc after set_rate. No direct tests are present.
