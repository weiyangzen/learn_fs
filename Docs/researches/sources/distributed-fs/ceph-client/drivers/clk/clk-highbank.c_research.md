# sources/distributed-fs/ceph-client/drivers/clk/clk-highbank.c

Purpose: early OF clock driver for Calxeda Highbank PLL, CPU bus/peripheral, and eMMC peripheral clocks.

Important APIs, types, and functions: `struct hb_clk` stores a clock hw and register pointer. `clk_pll_ops` implements prepare/unprepare, enable/disable, recalc, determine, and set-rate for Highbank PLLs. `a9periphclk_ops`, `a9bclk_ops`, and `periclk_ops` implement derived clock rates and peripheral divider setting. `hb_clk_init()` is the shared OF registration helper.

Control flow: `CLK_OF_DECLARE` callbacks invoke `hb_clk_init()` with the right ops. The helper reads the per-node `reg` offset, finds the `"calxeda,hb-sregs"` system register node, maps registers, initializes parent/name data, registers the clock, and adds a simple OF provider. PLL set-rate calculates dividers, may enter bypass/reset to relock when `divf` changes, waits for lock bits, then restores external enable.

State and persistence: all state is MMIO PLL/divider registers plus allocated `hb_clk` instances. PLL prepare and set-rate busy-wait until lock bits are asserted. There is no devres cleanup for these early registered clocks.

Dependencies and integration points: depends on OF clock declarations, MMIO accessors, common clock divider math, and Highbank system-register DT layout.

Risks and test signals: lock waits have no timeout and can hang if hardware never locks. `BUG_ON(!hb_clk->reg)` is fatal for missing sysreg mapping. Set-rate only accepts even peripheral dividers. Test signals are boot-time clock registration, PLL rate recalc after bootloader setup, set-rate relock behavior, and eMMC divider programming.
