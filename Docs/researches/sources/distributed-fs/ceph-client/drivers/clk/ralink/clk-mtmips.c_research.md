# sources/distributed-fs/ceph-client/drivers/clk/ralink/clk-mtmips.c

Purpose: This shared MTMIPS/Ralink driver provides early clock providers and reset controller support for RT2880, RT3050/3052, RT3352, RT3883, RT5350, MT7620, MT7628, and MT7688 style system-controller blocks.

Important APIs, types, and functions: It defines data-driven `mtmips_clk_data` tables containing base, fixed, factor, and peripheral clocks. Rate callbacks decode SoC-specific system registers, including `rt2880_cpu_recalc_rate()`, `rt305x_cpu_recalc_rate()`, `rt3352_cpu_recalc_rate()`, `rt3883_bus_recalc_rate()`, `rt5350_xtal_recalc_rate()`, `mt7620_pll_recalc_rate()`, `mt7620_cpu_recalc_rate()`, and `mt76x8_cpu_recalc_rate()`. Main paths are `mtmips_clk_init()` and `mtmips_clk_probe()`.

Control flow: `CLK_OF_DECLARE_DRIVER()` runs `mtmips_clk_init()` early for each sysc compatible. It selects the matching `mtmips_clk_data`, optionally adjusts MT7620 CPU bus fractional dividers for USB behavior, registers base/fixed/factor/peripheral clocks, and publishes a onecell provider. Separately, an `arch_initcall()` platform driver registers reset-controller operations for the same compatibles.

State and persistence: Clock rates are computed from syscon registers and fixed tables. Peripheral clocks are critical pass-through clocks. Reset state is controlled by `SYSC_REG_RESET_CTRL`; reset ID 0 is rejected. No persistent software state survives boot.

Dependencies and integration: Depends on syscon/regmap, CCF, reset-controller, OF compatibles, and legacy Ralink DT clock names such as device-address-derived peripheral clocks. Consumers often use named clocks rather than numeric bindings.

Risks: The driver intentionally uses `BUG()` for impossible strap values in several rate callbacks, making bad emulation or corrupted register state fatal. There is a spelling inconsistency in `pherip` names but it is internal. MT7620 register writes during init alter bus fractional dividers globally.

Test signals: Boot representative SoCs or QEMU/device-tree tests, compare reported rates to datasheets, verify USB on MT7620 after divider adjustment, confirm reset phandles reject ID 0, and check no duplicate provider registration warnings.
