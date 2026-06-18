# sources/distributed-fs/ceph-client/drivers/clk/clk-loongson1.c

Purpose: early OF clock driver for Loongson-1 LS1B and LS1C SoCs. It registers PLL, CPU, DC, AHB, and APB clocks with SoC-specific divider layouts.

Important APIs, types, and functions: `ls1x_clk_pll_data` describes fixed/integer/fractional PLL fields. `ls1x_clk_div_data` describes divider fields, bypass bits, optional divider tables, and lock. `ls1x_clk` binds a register offset and data block to `clk_hw`. Macro-generated `LS1X_CLK_PLL` and `LS1X_CLK_DIV` instances define the LS1B/LS1C clock trees. `ls1x_clk_init()` maps registers and registers onecell clocks.

Control flow: OF init maps the controller, iterates the onecell array, assigns register pointers to non-APB custom clocks, registers each clock, then adds the onecell provider. Divider set-rate locks, bypasses the clock according to bypass polarity, updates divider bits, restores normal path, and unlocks.

State and persistence: state is clock controller MMIO and static clock objects. A global spinlock protects divider register changes. The fixed APB clocks are static fixed-factor children.

Dependencies and integration points: depends on Loongson DT clock IDs, OF early registration, common clock divider helpers, MMIO, and spinlocks.

Risks and test signals: `ls1x_pll_rate_part()` uses `GENMASK(shift + width, shift)`, which may include one extra bit compared with typical width handling. Error cleanup unregisters clocks while iterating backward but sparse arrays need care. Test signals are LS1B/LS1C rate recalc from boot registers, divider set-rate bypass behavior, onecell IDs, and APB fixed-factor propagation.
