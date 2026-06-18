# sources/distributed-fs/ceph-client/drivers/thermal/tegra/soctherm.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/soctherm.h` is the shared contract between the common Tegra SOCTHERM driver, its fuse-calibration helper, and per-SoC descriptor files. The source was read as a complete 162-line file.

## Important APIs, Types, and Functions

The header defines register offsets and masks for thermal control, sensor temperature readbacks, pdiv/hotspot programming, and fuse offsets. It declares `struct tegra_tsensor_group`, `struct tegra_tsensor_configuration`, `struct tegra_tsensor`, `struct tsensor_group_thermtrips`, `struct tegra_soctherm_fuse`, `struct tsensor_shared_calib`, and `struct tegra_soctherm_soc`. It also declares `tegra_calc_shared_calib()` and `tegra_calc_tsensor_calib()` and conditionally declares `tegra114_soctherm`, `tegra124_soctherm`, `tegra132_soctherm`, and `tegra210_soctherm`.

## Control Flow

There is no executable flow. At build time it gives descriptor files a common structure layout and lets `soctherm.c` consume the descriptors uniformly. At runtime the objects described here drive sensor enabling, temperature register selection, pdiv/hotspot setup, trip programming, and fuse conversion.

## State and Persistence Behavior

The header defines state layout, not storage. Per-SoC files instantiate mostly `const` tables; the common driver stores pointers to those tables and mutable arrays such as `thermtrips`.

## Dependencies and Integration Points

It integrates with Tegra DT binding IDs, Tegra fuse register offsets, the common SOCTHERM MMIO programming model, and Kconfig-controlled SoC object inclusion. `soctherm-fuse.c` relies on the `SENSOR_CONFIG2_*` bit layout declared here.

## Risks and Edge Cases

Changing structure fields, masks, or register offsets affects multiple SoCs. Sensor group IDs must stay aligned across Tegra114 and Tegra124 binding constants, and the common driver asserts that equivalence. Threshold masks and `bptt` values must match hardware bit widths or trip programming/debugfs decoding will be wrong.

## Test Signals

Compile coverage across all supported Tegra SoC symbols is the first signal. Runtime signal comes from successful probe and plausible temperatures for every descriptor that includes this header.
