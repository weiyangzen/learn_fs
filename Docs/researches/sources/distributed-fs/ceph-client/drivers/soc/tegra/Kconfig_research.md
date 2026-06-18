# sources/distributed-fs/ceph-client/drivers/soc/tegra/Kconfig

## Purpose

This Kconfig file defines NVIDIA Tegra SoC family support symbols and common SoC driver options for fuse, flow controller, PMC, voltage couplers, and CBB error handling.

## Important APIs, Types, and Functions

Architecture options cover 32-bit `ARCH_TEGRA_2x_SOC`, `3x`, `114`, `124` and ARM64 `132`, `210`, `186`, `194`, `234`, `238`, `241`, and `264`. Common symbols include `SOC_TEGRA_FUSE`, `SOC_TEGRA_FLOWCTRL`, `SOC_TEGRA_PMC`, `SOC_TEGRA20_VOLTAGE_COUPLER`, `SOC_TEGRA30_VOLTAGE_COUPLER`, and `SOC_TEGRA_CBB`.

## Control Flow

Under `ARCH_TEGRA`, users select SoC families by architecture. Each family selects required pinctrl, timer, errata, mailbox, PMC, flowctrl, and regulator support as appropriate. `SOC_TEGRA_CBB` is enabled by default for Tegra194 or Tegra234 families and builds the Control Backbone error-reporting drivers.

## State and Persistence Behavior

The file has no runtime state. It controls compile-time platform feature inclusion.

## Dependencies and Integration Points

It integrates Tegra SoC drivers with ARM/ARM64 architecture menus, pinctrl, mailbox, timers, PM domains, OPP, regmap, generic pinconf, IRQ domains, and SoC bus support.

## Risks and Edge Cases

Selections encode hardware assumptions; missing `select` entries can cause boot-time subsystem failures, while over-selection increases build footprint. Several ARM64 CBB-capable newer SoCs use the Tegra234 CBB implementation despite the symbol name. Big-endian exclusion is explicit for several ARM64 SoCs.

## Test Signals

Run old 32-bit Tegra and modern ARM64 defconfigs, randconfig with `ARCH_TEGRA`, and module/built-in CBB builds. Verify selected dependencies match object files in Makefiles.
