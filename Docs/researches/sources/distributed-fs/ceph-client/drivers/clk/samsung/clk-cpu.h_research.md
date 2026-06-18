# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-cpu.h

## Purpose

`clk-cpu.h` is the public header for Samsung Exynos CPU-clock support. It defines CPU-clock feature flags, register-layout identifiers, and the divider configuration structure used by `clk-cpu.c` and SoC-specific clock tables.

## Important APIs and types

- `CLK_CPU_HAS_DIV1` means the CPU clock block has a second divider configuration/status register.
- `CLK_CPU_NEEDS_DEBUG_ALT_DIV` means debug-related clocks need safe divider values while the alternate parent is selected.
- `enum exynos_cpuclk_layout` identifies `CPUCLK_LAYOUT_E4210`, `CPUCLK_LAYOUT_E5433`, `CPUCLK_LAYOUT_E850_CL0`, and `CPUCLK_LAYOUT_E850_CL1`.
- `struct exynos_cpuclk_cfg_data` maps a primary parent rate in KHz to `div0` and `div1` register values.

## Control flow and integration

The header has no runtime control flow. Platform clock drivers embed arrays of `exynos_cpuclk_cfg_data` in `struct samsung_cpu_clock` descriptors. `clk-cpu.c` copies those arrays at registration, selects callbacks based on `reg_layout`, and checks the flags to decide whether to program DIV1 and debug-safe alternate dividers.

## State and persistence behavior

The header defines data contracts only. Platform tables are commonly `__initconst`, while `clk-cpu.c` copies them into persistent allocations so CPU rate transitions continue after init memory is freed.

## Dependencies

The flag macros use `BIT()`, so inclusion context must provide Linux bit macros. The definitions are coupled to `clk-cpu.c` and to the `samsung_cpu_clock` contract in `clk.h`.

## Risks and edge cases

- `prate` is KHz, while notifier rates are Hz; table values must exactly match `new_rate / 1000`.
- `div0` and `div1` are packed hardware values interpreted by layout-specific code.
- Adding a new enum value requires adding a matching `exynos_clkcpu_chips[]` entry in `clk-cpu.c`.
- Platform tables require a zero-rate sentinel.

## Test signals

Compile coverage catches missing enum references but not bad divider values. Hardware CPU frequency transition tests validate tables using this header. Static review should check KHz units, zero sentinels, complete OPP coverage, and correct flags for DIV1/debug-divider hardware.
