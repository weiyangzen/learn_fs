# sources/distributed-fs/ceph-client/drivers/clk/mvebu/clk-corediv.c

Purpose: MVEBU core-divider clock provider, currently focused on NAND/core divider clocks for Armada 370/375/380 and mv98dx3236.

Important APIs/functions: custom `clk_corediv_*` ops implement enable/disable/is_enabled, recalc, determine, and set_rate. `mvebu_corediv_clk_init` registers per-SoC divider clocks; `CLK_OF_DECLARE` wrappers bind specific compatibles.

Control flow: init maps the divider register block, allocates `clk_corediv` and clock arrays, reads parent name and output names, registers clocks with SoC-specific ops. Set-rate writes divider ratio, sets reload-force, triggers ratio reload, waits, then clears request bits.

State and persistence: each `clk_corediv` stores register base, descriptor, SoC descriptor, and lock. Hardware registers hold divider and enable state.

Dependencies and integration: CCF, OF early init, MMIO, udelay, and MVEBU SoC compatibles.

Risks: only `spin_lock_init(&corediv->lock)` initializes the first element if more descriptors are added. `recalc_rate` divides by raw divider without zero guard. Determine-rate clamps to 4,5,6,8 only.

Test signals: NAND clock rate set/get, enable bit behavior on SoCs with enable ops, zero-divider fault tests, and compatible-specific register offsets.
