# sources/distributed-fs/ceph-client/drivers/clk/mvebu/kirkwood.c

Purpose: Implements early common-clock support for Marvell Kirkwood-family core clocks, including `marvell,kirkwood-core-clock`, `marvell,mv88f6180-core-clock`, and `marvell,mv98dx1135-core-clock`. It decodes sample-at-reset registers to expose CPU, TCLK, L2, and DDR clocks, then optionally registers SoC clock gates and the Kirkwood power-save mux.

Important APIs, types, and functions: `kirkwood_get_tclk_freq()`, `kirkwood_get_cpu_freq()`, `kirkwood_get_clk_ratio()`, `mv88f6180_get_cpu_freq()`, `mv88f6180_get_clk_ratio()`, and `mv98dx1135_get_tclk_freq()` fill `struct coreclk_soc_desc` callbacks consumed by `mvebu_coreclk_setup()`. `kirkwood_gating_desc` supplies gate names and bit positions to `mvebu_clk_gating_setup()`. Local `struct clk_muxing_soc_desc` and `struct clk_muxing_ctrl` describe and own mux clocks; `clk_muxing_get_src()` maps OF clock specifier argument 0 to the mux shift.

Control flow: `CLK_OF_DECLARE()` invokes `kirkwood_clk_init()` during early OF clock init. The init selects the right `coreclk_soc_desc` from the compatible string, calls the common MVEbu core clock helper, finds the separate `"marvell,kirkwood-gating-clock"` node, registers gates, registers muxes with `clk_register_mux()`, and installs an OF provider for mux lookup.

State and persistence: Runtime state is MMIO-backed clock state plus allocated mux control storage. Core-clock frequencies are derived from immutable boot strap bits. Muxes and gates persist through CCF registrations; allocation is not devm-managed because this is early init.

Dependencies and integration points: Depends on `drivers/clk/mvebu/common.h` helpers, Linux CCF, OF early clock declaration, `of_iomap()`, `readl()`, and the shared `ctrl_gating_lock`. Device tree must provide the correct core-clock and gating-clock compatibles and use the mux shift as the clock specifier.

Risks: Unsupported strap encodings return zero multipliers or rates, which can propagate invalid clock rates. The mux provider uses the same flags value for mux registration and mux flags, so descriptor flags must stay valid for both roles. Error paths warn and return but may leave some clocks registered if later mux registration fails. The gating node lookup is global by compatible, so malformed DT with multiple matching nodes can bind an unexpected one.

Test signals: Boot logs should show no `WARN_ON()` from mapping/allocation or mux registration. `/sys/kernel/debug/clk/clk_summary` should expose `cpuclk`, `l2clk`, `ddrclk`, Kirkwood gates, and `powersave`; rates should match strap combinations in the comments. DT clock consumers using the gating node should be able to resolve the mux by shift 11.
