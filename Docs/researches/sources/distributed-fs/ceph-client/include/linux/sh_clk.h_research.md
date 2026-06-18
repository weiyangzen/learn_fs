# sources/distributed-fs/ceph-client/include/linux/sh_clk.h

## Purpose

`sh_clk.h` defines the legacy SuperH clock framework structures, operations, registration helpers, and initializer macros for module-stop clocks, divider clocks, reparentable clocks, and FSIDIV clocks.

## Important APIs, Types, And Functions

Core types are `struct clk_mapping`, `struct sh_clk_ops`, `struct clk`, `struct clk_div_mult_table`, and `struct clk_div_table`. `struct clk` tracks list membership, parent and children, selectable parent table fields, operations, usecount, rate, flags, enable/status registers, enable bit, mapped register, divider mask, arch-private flags, private data, mapping, and CPU frequency table data.

APIs include `followparent_recalc()`, `recalculate_root_clocks()`, `propagate_rate()`, `clk_reparent()`, `clk_register()`, `clk_unregister()`, `clk_enable_init_clocks()`, `clk_rate_table_build()`, `clk_rate_table_round()`, `clk_rate_table_find()`, `clk_rate_div_range_round()`, `clk_rate_mult_range_round()`, `sh_clk_mstp_register()`, deprecated `sh_clk_mstp32_register()`, `sh_clk_div4_register()`, `sh_clk_div4_enable_register()`, `sh_clk_div4_reparent_register()`, `sh_clk_div6_register()`, `sh_clk_div6_reparent_register()`, and `sh_clk_fsidiv_register()`.

Initializer macros include `SH_CLK_MSTP*`, `SH_CLK_DIV4`, `SH_CLK_DIV6_EXT`, `SH_CLK_DIV6`, `SH_CLK_FSIDIV`, and clock lookup helpers `CLKDEV_CON_ID`, `CLKDEV_DEV_ID`, and `CLKDEV_ICK_ID`.

## Control Flow

Board or SoC code statically declares clock arrays using the macros, registers them, and the framework enables initial clocks, recalculates root rates, propagates rate changes to children, handles parent changes, and applies register-level enable/disable or divider updates through `sh_clk_ops`.

## State And Persistence

Clock state persists in `struct clk` instances and hardware registers. `usecount`, `rate`, parent links, child lists, and mapping refcounts are in-memory state; enable bits, status bits, and divider fields are hardware state. Initializer flags such as `CLK_ENABLE_ON_INIT`, access-size flags, and `CLK_MASK_DIV_ON_DISABLE` control persistent behavior after registration.

## Dependencies And Integration Points

Dependencies include list handling, seq files, cpufreq tables, krefs, common clock consumer APIs, and MMIO. Integration points are SuperH CPG/MSTP clock drivers, cpufreq, clkdev lookup, peripheral power gating, and board setup code.

## Risks And Test Signals

Risks are wrong MMIO access width, incorrect divider masks, stale parent/child rate propagation, register mapping lifetime bugs, and usecount imbalance. Test signals include clock enable/disable tests, cpufreq table rate selection, parent reparenting, peripheral probe requiring MSTP clocks, debug clock tree dumps, and suspend/resume of clock-gated devices.
