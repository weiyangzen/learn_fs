# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-asv.h

## Purpose

`exynos-asv.h` defines private data structures and helpers for Exynos Adaptive Supply Voltage support shared by ChipID, generic ASV, and SoC-specific ASV table code.

## Important APIs, Types, and Functions

`struct asv_limit_entry`, `struct exynos_asv_table`, `struct exynos_asv_subsys`, and `struct exynos_asv` model ASV limits, table dimensions, per-subsystem metadata, and global ASV selection state. Inline helpers read table entries, OPP voltages, and OPP frequencies. `exynos_asv_init()` is declared for ChipID integration.

## Control Flow

No runtime control flow exists in the header. C files fill the structures, then generic code calls inline helpers while updating OPP tables.

## State and Persistence Behavior

The header describes in-memory ASV state only. Table buffers are referenced through pointers owned by implementation code.

## Dependencies and Integration Points

It depends on `struct regmap` forward declaration and kernel integer types. It is a private interface between `exynos-asv.c`, `exynos-chipid.c`, and SoC-specific ASV implementations.

## Risks and Edge Cases

Inline table indexing has no bounds checks. Callers must ensure `num_rows`, `num_cols`, group indexes, and table buffers are valid. The fixed `subsys[2]` array limits current ASV modeling to two CPU subsystems.

## Test Signals

Compile with each ASV implementation. Unit-review table dimensions against all helper accesses and run KASAN boot tests on supported SoCs.
