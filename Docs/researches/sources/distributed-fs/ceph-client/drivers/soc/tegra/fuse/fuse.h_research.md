# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/fuse.h

## Purpose

`fuse.h` is the private header for the Tegra fuse/APBMISC implementation. It defines the common fuse device model, SoC descriptor contract, early/runtime read hooks, NVMEM metadata hooks, Tegra20 APBDMA state, and declarations shared by fuse core, speedo files, APBMISC, and SoC-specific fuse descriptors.

## Important APIs, Types, and Functions

`struct tegra_fuse_info` describes the fuse read callback, NVMEM size, and spare-bit base. `struct tegra_fuse_soc` is the per-SoC operations and metadata table: `init`, `speedo_init`, optional `probe`, `info`, NVMEM lookup/cell/keepout arrays, SoC sysfs attributes, and `clk_suspend_on`. `struct tegra_fuse` stores runtime device state, MMIO base and physical address, clock/reset handles, early and runtime read callbacks, SoC descriptor, Tegra20 APBDMA resources, NVMEM device, and duplicated lookup table.

The header declares APBMISC initialization and revision helpers, early fuse read helpers, SoC attribute groups, speedo init functions, and all SoC descriptor symbols guarded by architecture config.

## Control Flow

No executable logic is present. The header defines the call boundary: common code selects a `tegra_fuse_soc`, calls `init()` during early boot, later calls optional `probe()` during platform probe, and uses `info->read` or `fuse->read` to serve NVMEM and exported reads. Speedo init functions receive a mutable `struct tegra_sku_info`.

## State and Persistence Behavior

The structures describe volatile kernel state around immutable eFuse OTP data. `struct tegra_fuse` persists for the boot lifetime. The APBDMA members persist only for Tegra20 runtime reads. NVMEM cells and keepouts are static metadata used to expose or hide fuse regions.

## Dependencies and Integration Points

The header depends on DMAengine and NVMEM type declarations and integrates with public Tegra SoC headers for `struct tegra_sku_info` and enum/config constants. It is included by fuse core, Tegra20/Tegra30 fuse backends, speedo implementations, and APBMISC code.

## Risks and Edge Cases

Because this is a private cross-file contract, changing fields in `struct tegra_fuse_soc` or `struct tegra_fuse` requires auditing all SoC descriptors and the common probe path. Read callbacks return `u32`, so backend errors cannot be represented directly and commonly collapse to zero. Architecture guards must match the symbols referenced from `tegra_fuse_match`; missing guards cause link failures or unsupported SoCs at boot.

## Test Signals

Build all relevant `CONFIG_ARCH_TEGRA_*` combinations, especially mixed ARM/ARM64 and ACPI-capable configurations. Validate all descriptors link, NVMEM cells compile with the current provider API, and SoC speedo init declarations match their implementations.
