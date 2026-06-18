# sources/distributed-fs/ceph-client/include/soc/tegra/fuse.h

## Purpose

`fuse.h` exposes Tegra chip identity, platform/revision, SKU, fuse, strap, RAM-code, and SoC registration interfaces.

## Important APIs, Types, and Functions

It defines chip constants from `TEGRA20` through `TEGRA264` and fuse offsets for SKU and calibration data. `enum tegra_revision` names silicon revisions; `enum tegra_platform` names silicon, FPGA, simulation, VDK, VSP, and related platforms. `struct tegra_sku_info` stores SKU ID, process/speedo/IDDQ values, revision, and platform.

Enabled builds export global `tegra_sku_info` and functions such as `tegra_read_straps()`, `tegra_read_ram_code()`, `tegra_fuse_readl()`, `tegra_read_chipid()`, `tegra_get_chip_id()`, `tegra_get_platform()`, `tegra_is_silicon()`, and `tegra194_miscreg_mask_serror()`. Disabled builds return zeros, `false`, or `-ENODEV`. `tegra_soc_device_register()` is also declared.

## Control Flow

Consumers read immutable fuse/strap registers during probe or platform setup, then choose clocks, OPPs, calibration, errata, or SKU-specific behavior from those values.

## State and Persistence

Fuse hardware is immutable. `tegra_sku_info` is a global cached view of identity and characterization data.

## Dependencies and Integration Points

The header depends on Linux types and integrates with SoC registration, OPP/clock setup, calibration users, thermal, memory/display code, and platform errata handling.

## Risks

Risks include reading SKU state before initialization, treating disabled-build zeros as real silicon values, and checking chip ID without platform/revision context.

## Test Signals

Test fuse reads on supported SoCs, disabled-config stubs, SKU table selection, platform/revision branching, SoC device registration, and calibration consumers.
