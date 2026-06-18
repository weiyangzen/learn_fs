# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos-arm64.c

## Purpose

`clk-exynos-arm64.c` provides shared CMU registration, initialization, runtime PM setup, and suspend/resume helpers for newer arm64 Samsung/Exynos-style clock drivers. SoC-specific files supply `struct samsung_cmu_info` tables; this file handles common register initialization policy, bus-clock enablement, CCF provider registration, dynamic root clock gating, and register save/restore.

## Important APIs, types, and functions

- `struct exynos_arm64_cmu_data` stores per-device PM state: CMU register dumps, optional sysreg dumps, suspend override registers, bus clock, parent clocks, and Samsung provider context.
- `is_gate_reg()`, `is_pll_conx_reg()`, and `is_pll_con1_reg()` classify register offsets.
- `exynos_arm64_init_clocks()` maps a CMU, optionally enables global automatic clock gating, sets PLL manual bits, and forces gate registers to manual mode when auto mode is inactive.
- `exynos_arm64_enable_bus_clk()` obtains and enables the CMU's named parent/bus clock using either a device or OF node.
- `exynos_arm64_cmu_prepare_pm()` allocates save buffers and obtains parent clocks for suspend/resume sequencing.
- `exynos_arm64_register_cmu()` is the simple CMU registration path.
- `exynos_arm64_register_cmu_pm()` is the PM-aware platform registration path.
- `exynos_arm64_cmu_suspend()` and `exynos_arm64_cmu_resume()` save/restore CMU and sysreg registers and manage parent/bus clocks.

## Control flow

The simple path calls `exynos_arm64_enable_bus_clk()`, logs but ignores failure, initializes clock registers through `exynos_arm64_init_clocks()`, and registers clocks with `samsung_cmu_register_one()`.

The PM path obtains match data, allocates `exynos_arm64_cmu_data`, prepares save state, enables the bus clock, optionally initializes registers, maps the MMIO resource, initializes the Samsung provider, marks runtime PM active, registers clocks and the OF provider, enables dynamic root clock gating, and drops the runtime PM usage count.

Suspend saves CMU and sysreg registers, enables all parent clocks from the DT node, writes any suspend override register values, disables those parent clocks, and disables the bus clock. Resume enables the bus clock and parent clocks, restores CMU registers, restores sysreg registers when present, then disables parent clocks.

## State and persistence behavior

PM-capable registration persists `exynos_arm64_cmu_data` as driver data. Register-save buffers are allocated with `samsung_clk_alloc_reg_dump()` and kept for device lifetime after successful probe. The bus clock and parent clocks are retained. Hardware state initialization depends on `cmu->auto_clock_gate`, `samsung_is_auto_capable(np)`, `cmu->option_offset`, and `cmu->manual_plls`.

## Dependencies

The file depends on Samsung clock provider internals from `clk.h`, OF address/resource mapping, CCF clock APIs, platform devices, runtime PM, and optional sysreg/dynamic-root-gating helpers. SoC `samsung_cmu_info` tables must provide accurate register lists, optional sysreg/suspend lists, clock names, and auto/manual gating flags.

## Risks and edge cases

- `exynos_arm64_init_clocks()` panics if `of_iomap()` fails.
- Gate and PLL classification is based on fixed offset ranges, so incompatible future CMU layouts need changes.
- Bus-clock enable failures are nonfatal and can defer failures until register access.
- Suspend disables the CMU bus clock; wake paths must account for that policy.
- Late error handling in `exynos_arm64_register_cmu_pm()` after runtime PM enablement is sparse and should be revisited if called helpers start returning failures.

## Test signals

Validation should boot SoCs using both simple and PM-capable paths, inspect register initialization for auto/manual gating policy, verify `clk_summary` before and after suspend, and test runtime/system suspend/resume for CMUs with sysreg-backed dynamic root gating and parent clocks in DT.
