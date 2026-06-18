# sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra210-soctherm.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra210-soctherm.c` supplies Tegra210 SOCTHERM descriptor data, including wider threshold fields and a mutable thermtrips table. The source was read as a complete 232-line file.

## Important APIs, Types, and Functions

The file defines Tegra210 thermtrip masks with 9-bit thresholds, `tegra210_tsensor_config`, CPU/GPU/PLL/MEM group descriptors, `tegra210_tsensors[]`, `tegra210_soctherm_fuse`, `tegra210_tsensor_thermtrips[]`, and exported `tegra210_soctherm`.

## Control Flow

The common SOCTHERM driver uses this descriptor for `nvidia,tegra210-soctherm`. Probe uses the Tegra210 fuse layout, computes calibration, initializes eight raw sensors, registers four thermal groups, parses DT thermtrips into the provided thermtrips array, and programs 500 mC-grain thresholds using `bptt = 9`.

## State and Persistence Behavior

Most state is static descriptor data. `tegra210_tsensor_thermtrips[]` is mutable so `soctherm_thermtrips_parse()` can store DT-provided group shutdown temperatures. Hardware register state is not persistent and is recreated on probe/resume.

## Dependencies and Integration Points

It uses Tegra124 thermal binding IDs for group numbering, Tegra fuse layout constants, shared SOCTHERM structures, and `CONFIG_ARCH_TEGRA_210_SOC`. It integrates with the common driver's thermtrip parser through `.thermtrips`.

## Risks and Edge Cases

Tegra210 has different thermtrip bit positions, 9-bit threshold fields, and 500 mC grain. Using older masks would corrupt shutdown thresholds. The initial thermtrips table uses sentinel IDs equal to `TEGRA124_SOCTHERM_SENSOR_NUM`; parser behavior depends on replacing entries with valid IDs.

## Test Signals

Boot tests should confirm thermtrips parsed from DT, debugfs threshold decoding at 500 mC granularity, plausible calibrated temperatures, hot-trip throttling, and correct behavior with and without `nvidia,thermtrips`.
