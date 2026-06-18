# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-shx3.c

Purpose: provides SH-X3 clock-framework registration for the legacy SuperH clock tree. It defines the external input clock, a fixed PLL clock, DIV4-derived clocks, MSTP gate clocks, and `clkdev` lookup aliases used by SH-X3 platform devices.

Important APIs, types, and functions: `arch_clk_init()` is the exported init entry point. `pll_recalc()` models PLL1 as `parent * 72`. Static `struct clk`, `struct sh_clk_ops`, `struct clk_div4_table`, `struct clk_div_mult_table`, and `struct clk_lookup` instances describe hardware clocks. The file uses `SH_CLK_DIV4`, `SH_CLK_MSTP32`, `CLKDEV_CON_ID`, and `CLKDEV_ICK_ID`.

Control flow: `arch_clk_init()` registers `extal_clk` and `pll_clk`, installs the lookup table, then registers DIV4 clocks and MSTP gate clocks if prior registration succeeded. Device drivers later acquire these clocks by connection id or by `(dev_id, con_id)` pairs such as `fck` for `sh-sci.*` and `sh-tmu.*`.

State and persistence: state is static kernel clock metadata plus MMIO-backed gate/divider state in `FRQMR1`, `MSTPCR0`, and `MSTPCR1`. The default EXTAL rate is `16666666` Hz and can be overridden by platform code through `clk_set_rate()`. Clocks marked `CLK_ENABLE_ON_INIT` stay enabled from boot.

Dependencies and integration points: depends on the SuperH clock core in `<asm/clock.h>`, frequency register definitions in `<asm/freq.h>`, `clkdev`, and MMIO helpers. It integrates with SH-X3 setup files that instantiate `sh-sci`, `sh-tmu`, H8, CSM, FE, HUDI, and DMAC devices.

Risks: register addresses and bit masks are hard-coded for SH-X3; wrong SoC selection can gate required clocks or expose invalid aliases. `ret |= clk_register()` collapses individual error codes and continues registering all root clocks. Some MSTP clocks have `NULL` parents, so consumers rely on gate control without rate derivation.

Test signals: boot log should show no clock registration failures; serial and TMU devices should probe and obtain `fck`; clock debugfs/sysfs, if enabled, should show expected rates derived from EXTAL and PLL; suspend/resume or module stop tests should verify MSTP gates do not disable essential clocks.
