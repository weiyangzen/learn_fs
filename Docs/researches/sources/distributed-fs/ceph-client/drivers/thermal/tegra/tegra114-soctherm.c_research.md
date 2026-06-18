# sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra114-soctherm.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra114-soctherm.c` supplies Tegra114-specific SOCTHERM descriptor data for the common driver. The source was read as a complete 209-line file.

## Important APIs, Types, and Functions

There are no functions. The file defines Tegra114 thermtrip/threshold masks, `tegra114_tsensor_config`, four `tegra_tsensor_group` objects for CPU/GPU/PLL/MEM, the `tegra114_tsensors[]` sensor table, `tegra114_soctherm_fuse`, and the exported `const struct tegra_soctherm_soc tegra114_soctherm`.

## Control Flow

The common `soctherm.c` probe selects `tegra114_soctherm` for compatible `nvidia,tegra114-soctherm`. It then iterates these tables to calculate calibration, enable raw sensors, register group zones, program pdiv/hotspot offsets, decode temperature registers, and configure thermtrip/throttle thresholds.

## State and Persistence Behavior

The file owns static const descriptor state only. Runtime state is allocated by `soctherm.c`; hardware persistence is limited to register programming based on these constants.

## Dependencies and Integration Points

It depends on Tegra114 thermal DT binding IDs and the shared structures in `soctherm.h`. It integrates with `CONFIG_ARCH_TEGRA_114_SOC` through the Makefile/header and common OF match table.

## Risks and Edge Cases

Descriptor errors directly affect thermal safety. Fuse offsets, correction coefficients, pdiv values, hotspot differences, and threshold masks must match Tegra114 silicon. The file uses 8-bit threshold grain behavior (`TEGRA114_BPTT = 8`, `thresh_grain = 1000`), unlike Tegra210, so copying masks between SoCs would be hazardous.

## Test Signals

Probe on Tegra114 hardware should show four thermal zones and eight raw sensors. Temperature plausibility, debugfs register decoding, thermtrip programming for each group, and calibration comparison with vendor BSP values are primary validation signals.
