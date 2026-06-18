# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/fuse-tegra30.c

## Purpose

`fuse-tegra30.c` provides the shared direct-MMIO fuse backend for Tegra30 and newer SoCs, plus the SoC descriptor tables for Tegra30, Tegra114, Tegra124/132, Tegra210, Tegra186, Tegra194, Tegra234, and Tegra241. It declares NVMEM cells, lookup aliases, keepout ranges, fuse aperture sizes, spare offsets, speedo hooks, SoC sysfs attribute groups, and suspend clock policy.

## Important APIs, Types, and Functions

The main read callbacks are `tegra30_fuse_read_early()` and `tegra30_fuse_read()`. Early init uses `tegra30_fuse_init()` and `tegra30_fuse_add_randomness()`. Public SoC descriptors include `tegra30_fuse_soc`, `tegra114_fuse_soc`, `tegra124_fuse_soc`, `tegra210_fuse_soc`, `tegra186_fuse_soc`, `tegra194_fuse_soc`, `tegra234_fuse_soc`, and `tegra241_fuse_soc`, gated by architecture config.

NVMEM cell arrays expose thermal sensor calibration, XUSB pad calibration, SATA calibration, GPU calibration/configuration, and selected GPU PDI fields depending on SoC. Lookup arrays map those cells to platform device IDs and connection IDs such as padctl calibration, thermal sensor CPU/GPU/MEM channels, SATA calibration, and GPU calibration. Keepout arrays hide reserved fuse ranges from generic NVMEM reads on newer SoCs.

## Control Flow

For Tegra30+ SoCs, early init installs both early and runtime direct-MMIO read callbacks, initializes revision, runs an optional speedo hook, and adds manufacturing/random identity words to kernel randomness. Runtime reads enable runtime PM, read `FUSE_BEGIN + offset`, and release runtime PM.

The common fuse driver selects the SoC descriptor by compatible string or ACPI chip ID. That descriptor drives NVMEM size, spare bit location, cell table, lookup aliases, keepout table, sysfs attributes, speedo init, and whether the fuse clock must stay enabled during system suspend.

## State and Persistence Behavior

This file is mostly static immutable SoC metadata. Runtime state lives in the common `struct tegra_fuse`. eFuse contents are read-only OTP. `tegra30_fuse_init()` updates global SKU/process/speed data through `tegra_init_revision()` and SoC-specific speedo init functions. NVMEM keepouts persist as provider policy for reserved regions.

## Dependencies and Integration Points

The file depends on Linux NVMEM provider/consumer data structures, runtime PM, Tegra public fuse APIs, and speedo implementations. Consumer integration is explicit: thermal, XUSB padctl, SATA, and GPU drivers can request named cells without embedding fuse offsets.

## Risks and Edge Cases

Direct runtime reads return zero when runtime PM resume fails, hiding errors from consumers. Keepout correctness is security- and stability-sensitive on newer SoCs: missing a reserved range could expose or read protected fuse fields; overly broad keepouts can break consumers. Cell offsets differ subtly between Tegra114, Tegra124, and Tegra210 thermal layouts. Tegra241 uses a very large aperture and a broad keepout from 0x0c to 0x1600c, so boundary testing matters.

## Test Signals

Validate NVMEM provider size and keepout enforcement on every descriptor, lookup resolution for each named consumer, direct reads under runtime PM, early randomness paths, speedo hook invocation, suspend behavior for Tegra124 `clk_suspend_on`, and DT/ACPI matching for Tegra186+ systems. Thermal, XUSB, SATA, and GPU probe success are practical integration signals.
