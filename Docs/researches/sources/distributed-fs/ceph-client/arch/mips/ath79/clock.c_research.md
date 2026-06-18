## sources/distributed-fs/ceph-client/arch/mips/ath79/clock.c

Purpose: implements ATH79 clock provider setup for AR71xx, AR724x/AR913x, AR933x, AR934x, QCA953x, QCA955x, and QCA956x-compatible PLL blocks. It registers CPU, DDR, AHB, reference, and MDIO clocks for device tree consumers and MIPS timer setup.

Important APIs and functions: `ath79_clocks_init_dt()` is registered through multiple `CLK_OF_DECLARE()` compatible strings. Helpers `ath79_set_clk()` and `ath79_set_ff_clk()` create fixed-rate/fixed-factor clocks and clkdev aliases. SoC-specific functions decode PLL registers, including `ar71xx_clocks_init()`, `ar724x_clocks_init()`, `ar933x_clocks_init()`, `ar934x_clocks_init()`, `qca953x_clocks_init()`, `qca955x_clocks_init()`, and `qca956x_clocks_init()`. `ar934x_get_pll_freq()` handles fractional PLL math with 64-bit division.

Control flow: DT clock initialization optionally accepts an external ref clock from phandle index 0, maps PLL registers, selects decoder by compatible string, creates CPU/DDR/AHB clocks, defaults MDIO to ref if not explicitly set, then registers a onecell OF provider. Some families read bootstrap bits through `ath79_reset_rr()` to choose 25 or 40 MHz reference clocks. QCA956x also enables the MIPS SI timer interrupt workaround before clocks are finalized.

State and persistence: static `clks[]` and `clk_data` hold registered clock pointers. Hardware PLL registers are read, not generally written, except QCA956x misc interrupt enable through reset registers.

Dependencies and integration: depends on Linux common clock framework, OF clock/address APIs, dt-bindings clock IDs, ATH79 reset helpers, and AR71xx register definitions. `setup.c` calls `of_clk_init()` and later obtains the CPU clock.

Risks: PLL formulas are family-specific and easy to regress. Some functions do not check `ioremap()` failures for secondary SRIF maps. A missing compatible leaves clocks unset with little direct error handling. Divide fields of zero must be interpreted carefully by family.

Test signals: boot should log a plausible CPU clock in `plat_time_init()`. DT consumers should resolve `cpu`, `ddr`, `ahb`, `ref`, and `mdio` clocks. Timer rate, UART baud, Ethernet MDIO, and PCI behavior are practical validation points.
