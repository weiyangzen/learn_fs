# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos5422-asv.c

## Purpose

`exynos5422-asv.c` implements Adaptive Supply Voltage setup for Exynos5422 CPU clusters. It chooses ASV voltage tables from chip-id fuse fields, derives an ASV group from IDS/HPM or special-speed-grade bits, applies per-cluster voltage offsets, and exposes an OPP voltage callback to the shared Exynos ASV core.

## Important APIs, Types, and Functions

The large `asv_arm_table` and `asv_kfc_table` arrays encode frequency-to-voltage rows for the Cortex-A15 ARM cluster and Cortex-A7 KFC cluster. Constants such as `ASV_GROUPS_NUM`, `ASV_ARM_DVFS_NUM`, and bin2 row counts bound table dimensions. `__asv_limits[]` maps IDS/HPM thresholds to ASV groups. `exynos5422_asv_get_group()` reads `EXYNOS_CHIPID_REG_PKG_ID` and `EXYNOS_CHIPID_REG_AUX_INFO`. `exynos5422_asv_offset_voltage_setup()` configures high/low offsets. `exynos5422_asv_opp_get_voltage()` is the exported per-OPP adjustment callback. `exynos5422_asv_init()` is exported with `EXPORT_SYMBOL_GPL`.

## Control Flow

Initialization reads package id, decides whether bin2 mode is forced by DT (`of_bin == 2`) or parsed from package fuses, parses whether special speed-grade math is used, computes `asv->group`, table selector, and offsets, then binds subsystem metadata. ARM gets `cpu_dt_compat = "arm,cortex-a15"` and KFC gets `"arm,cortex-a7"`. Bin2 selects shorter bin2 tables and table index 3; otherwise package table values 2 or 3 select alternate tables, and all other values use table 0. Later, the ASV core calls `opp_get_voltage`, which bounds the OPP level, fetches the voltage column for the selected group, and applies high or low offset based on the OPP's original voltage relative to a 1,000,000 uV base.

## State and Persistence Behavior

All runtime state is stored in the caller-provided `struct exynos_asv`: selected group/table, `use_sg`, per-subsystem base and offsets, table pointers, row/column counts, and callback pointer. The driver does not persist data; it interprets SoC fuse state and updates OPP voltages during boot.

## Dependencies and Integration Points

It depends on the Samsung chip-id regmap, `exynos-asv.h` shared structures, Exynos5422 fuse bit definitions from `exynos5422-asv.h`, and the OPP/ASV framework that applies updated CPU OPP voltages. It integrates with DT CPU compatible strings rather than directly touching cpufreq.

## Risks and Edge Cases

The first KFC table uses frequency values in Hz-like units while later tables use MHz-style values; this is presumably intentional but easy to misread. Table dimensions are hard-coded, so any row-count mismatch can corrupt OPP lookup. If fuse reads fail, the current code does not check regmap return values. ASV group calculation stops when either IDS or HPM crosses a threshold; boundary behavior must match vendor calibration. Offset application uses the original OPP voltage compared with a fixed base, so unexpected DT voltages can select the wrong offset side.

## Test Signals

Boot should log and apply valid OPP voltages for both A15 and A7 clusters across normal, bin2, and special-speed-grade parts. Tests should compare generated OPP voltages against vendor tables for representative `pkg_id`/`aux_info` values, verify `of_bin = 2` overrides fuse parsing, and run cpufreq stress plus thermal throttling on Exynos5422 boards.
