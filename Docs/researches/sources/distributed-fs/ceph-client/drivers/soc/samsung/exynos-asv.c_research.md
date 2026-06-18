# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-asv.c

## Purpose

`exynos-asv.c` applies Exynos Adaptive Supply Voltage data to CPU OPP tables. It selects SoC-specific ASV probing, computes adjusted voltages, updates OPP entries, and refreshes energy-model chip-binning data.

## Important APIs, Types, and Functions

`exynos_asv_init()` is called from the ChipID driver after regmap setup. It allocates `struct exynos_asv`, reads product ID, selects `exynos5422_asv_init()` for Exynos5800/5422-class ID, reads optional `samsung,asv-bin`, initializes subsystem back-pointers, and updates OPPs. `exynos_asv_update_cpu_opps()` adjusts per-frequency voltages. `exynos_asv_update_opps()` avoids duplicate work for CPUs sharing an OPP table.

## Control Flow

ChipID probe calls ASV init. If the SoC is unsupported, the function returns success with no changes. Supported SoCs wait for CPU0 OPP availability, run the SoC-specific probe to fill tables/group selection, then iterate possible CPUs and adjust each unique OPP table.

## State and Persistence Behavior

ASV state is devm-managed under the ChipID device. Updated OPP voltages persist in kernel OPP tables for runtime consumers; no nonvolatile storage is changed.

## Dependencies and Integration Points

It depends on ChipID regmap, Exynos ASV tables, CPU device nodes, OPP core, and energy model. CPUfreq and thermal scheduling observe the adjusted OPP/EM data.

## Risks and Edge Cases

Unsupported SoCs intentionally no-op. Missing OPPs are logged and skipped, so partial voltage adjustment is possible. `get_cpu_device(0)` is not null-checked before OPP count. A typo in an error message says "udate". ASV table dimensions and group indexes must be valid or inline table access can go out of bounds.

## Test Signals

Boot supported and unsupported Exynos SoCs, test OPP probe deferral, missing OPP rows, DT-provided ASV bin, updated OPP voltages, EM refresh, and shared OPP table deduplication.
