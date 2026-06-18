# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/fuse-tegra.c

## Purpose

`fuse-tegra.c` is the common Tegra fuse platform driver and early boot initializer. It owns the global `struct tegra_fuse`, exports global SKU data as `tegra_sku_info`, provides an NVMEM provider for SoC eFuses, registers NVMEM cell lookups for consumers, exposes basic SoC revision attributes, and registers a `soc_device` on ARM64. It bridges the early pre-driver mapping used by boot code into the normal platform-device lifetime.

## Important APIs, Types, and Functions

The file exports `tegra_sku_info` and `tegra_fuse_readl()`. Early init helpers are `tegra_fuse_read_spare()`, `tegra_fuse_read_early()`, and `tegra_init_fuse()`. Runtime driver entry points are `tegra_fuse_probe()`, `tegra_fuse_runtime_resume()`, `tegra_fuse_runtime_suspend()`, `tegra_fuse_suspend()`, and `tegra_fuse_resume()`.

`tegra_fuse_match` maps `nvidia,tegra*-efuse` compatible strings to `struct tegra_fuse_soc` descriptors supplied by SoC-specific files. `tegra_fuse_read()` is the NVMEM `reg_read` callback and dispatches every 32-bit word through `fuse->read`. `tegra_soc_device_register()` builds a `soc_device_attribute` from chip ID, platform, revision, and the SoC-specific sysfs attribute group.

## Control Flow

Early boot calls `tegra_init_fuse()` via `early_initcall`. It first initializes APBMISC, locates the FUSE node, or falls back to hardcoded legacy Tegra ARM addresses. It maps CAR registers if available to force-enable the fuse clock before the clock framework exists, maps the FUSE region, selects the `tegra_fuse_soc`, calls its `init()` hook, prints SKU/revision/process data, and adds NVMEM cell lookup aliases.

The platform driver later probes `tegra-fuse`. Probe saves the early mapping for cleanup, remaps the platform resource through devm, handles ACPI-only SoC selection for Tegra194/234/241, gets the optional fuse clock, enables runtime PM, runs any SoC-specific `probe()` hook, registers a read-only NVMEM device named `fuse`, gets and pulses the optional reset, and unmaps the old early mapping.

Runtime reads through `tegra_fuse_readl()` defer until the platform device, clock pointer, and SoC read callback are ready. PM hooks enable/disable the fuse clock, except SoCs marked `clk_suspend_on` keep the clock active across system suspend for RAM re-repair or cluster switching requirements.

## State and Persistence Behavior

The global `fuse` pointer persists across early and normal init. Early state includes a temporary MMIO mapping and SoC descriptor. Runtime state adds `dev`, `phys`, `clk`, `rst`, `nvmem`, duplicated lookup table, and optional SoC-private fields such as Tegra20 APBDMA. The source fuses are one-time-programmed hardware state; this driver is read-only and does not persist data to files.

`tegra_sku_info` persists as a global cached summary of eFuse and APBMISC-derived SoC identity. Consumers such as speed binning, regulators, and SoC bus use that cache after early init.

## Dependencies and Integration Points

The file integrates with OF, ACPI, platform bus, clocks, resets, runtime PM, NVMEM provider/consumer lookup APIs, sysfs SoC bus, APBMISC helpers, and SoC-specific fuse implementations in the same directory. Device-tree consumers reach individual calibration cells by lookup entries installed here or by NVMEM cells from the SoC descriptors.

## Risks and Edge Cases

The singleton `fuse` is shared by early boot, normal probe, exported readers, and ACPI fallback paths. Callers before probe must be prepared for `-EPROBE_DEFER`. The early mapping is replaced during probe and must remain valid until `iounmap(base)` at the end; the devm restore action protects the pointer if probe fails. ACPI SoC selection depends on APBMISC chip ID and supports only explicitly compiled SoCs.

`tegra_fuse_read()` assumes NVMEM byte counts are word-aligned because the NVMEM config uses word size and stride 4. Misaligned future callers would silently truncate `bytes / 4`. Lookup duplication uses `kmemdup_array`; the code does not explicitly remove lookups, relying on process lifetime for this built-in driver.

## Test Signals

Useful validation includes boot on each supported Tegra compatible, legacy Tegra20/30 DT fallback, ACPI boot on Tegra194/234/241, successful `nvmem` registration, consumer lookup resolution for thermal/XUSB/SATA/GPU cells, correct `/sys/devices/soc0` family/revision fields, runtime PM clock transitions, reset pulse success, and exported `tegra_fuse_readl()` returning `-EPROBE_DEFER` before probe but data after probe.
