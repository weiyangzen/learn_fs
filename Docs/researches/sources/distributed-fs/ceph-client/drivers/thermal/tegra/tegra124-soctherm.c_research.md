# sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra124-soctherm.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra124-soctherm.c` provides Tegra124-specific SOCTHERM tables for the common driver. The source was read as a complete 223-line file.

## Important APIs, Types, and Functions

The file is data-only. It defines Tegra124 thermtrip and thermctl masks, `tegra124_tsensor_config`, CPU/GPU/PLL/MEM group descriptors, eight sensor descriptors, `tegra124_soctherm_fuse`, and exported `tegra124_soctherm`.

## Control Flow

When `soctherm.c` matches `nvidia,tegra124-soctherm`, the common probe consumes these tables to compute fuse calibration, configure sensors, set pdiv/hotspot values, register thermal zones by binding ID, and program hardware trips.

## State and Persistence Behavior

All owned state is static descriptor data. Runtime state lives in the common driver, and hardware register state is reconstructed from this data at probe/resume.

## Dependencies and Integration Points

The file uses `dt-bindings/thermal/tegra124-soctherm.h` IDs and the SOCTHERM shared header. Its fuse descriptor references `FUSE_TSENSOR_COMMON` and spare realignment register `0x1fc` as described by `soctherm-fuse.c`.

## Risks and Edge Cases

The pre-Tegra210 fuse common-register layout and spare realignment field are fragile. Per-sensor alpha/beta coefficients differ across otherwise similar CPU/mem sensors, so table edits can produce local sensor bias. Group IDs are shared with Tegra132/210 descriptors, making binding compatibility important.

## Test Signals

Build with `CONFIG_ARCH_TEGRA_124_SOC`, boot on Tegra124, confirm four groups and eight sensors, compare ambient temperatures by group, inspect debugfs pdiv/hotspot/thermtrip values, and verify thermtrip thresholds use 1000 mC grain.
