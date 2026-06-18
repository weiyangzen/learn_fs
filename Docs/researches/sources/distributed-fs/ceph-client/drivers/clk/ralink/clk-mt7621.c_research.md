# sources/distributed-fs/ceph-client/drivers/clk/ralink/clk-mt7621.c

Purpose: This driver provides MT7621 clock and reset support. It has an early clock provider for boot-critical `xtal`, `cpu`, and `bus`, then a platform-driver phase that registers fixed clocks, gated peripheral clocks, a full onecell provider, and a reset controller.

Important APIs, types, and functions: Key types are `mt7621_clk_priv`, `mt7621_clk`, `mt7621_fixed_clk`, `mt7621_gate`, and `mt7621_rst`. Rate callbacks include `mt7621_xtal_recalc_rate()`, `mt7621_cpu_recalc_rate()`, and `mt7621_bus_recalc_rate()`. Registration functions include `mt7621_register_early_clocks()`, `mt7621_register_fixed_clocks()`, `mt7621_register_gates()`, `mt7621_reset_init()`, and `mt7621_clk_probe()`.

Control flow: `CLK_OF_DECLARE_DRIVER()` registers early clocks for `mediatek,mt7621-sysc`, leaving later clock IDs as `-EPROBE_DEFER`. `arch_initcall()` registers the platform driver, whose probe reuses early clock handles, registers fixed-rate clocks and gates, adds the managed provider, and registers reset ops.

State and persistence: `sysc` and `memc` regmaps expose SoC registers. CPU rate is derived from clock selection, current divider/fraction fields, and MEMC CPU PLL fields. Gate state is controlled by `SYSC_REG_CLKCFG1`. Reset state is `SYSC_REG_RESET_CTRL`. The static `mt7621_clk_early` array bridges early and platform phases.

Dependencies and integration: Depends on syscon/regmap, CCF, reset-controller, DT bindings for MT7621 clock/reset IDs, and the `ralink,memctl` phandle. Consumers reference onecell clock IDs and reset IDs in DT.

Risks: `mt7621_cpu_recalc_rate()` divides by `ffiv`; invalid hardware values could fault. All peripheral gates are marked `CLK_IS_CRITICAL` to preserve legacy drivers, which can hide unused-clock issues. Early and late providers must agree on clock array ordering.

Test signals: Boot MT7621, confirm early console/timer clocks before platform probe, inspect onecell clock IDs after `arch_initcall`, test reset controller phandles except disallowed system reset, and verify CPU/bus rates against hardware strap values.
