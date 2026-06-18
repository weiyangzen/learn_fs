# sources/distributed-fs/ceph-client/drivers/phy/hisilicon/Kconfig

## Purpose
Kconfig menu entries for HiSilicon PHY drivers covering HI6220/HI3660/HI3670 USB, HI3670 PCIe, STB COMBPHY, INNO USB2, and HIX5HD2 SATA PHY support.

## Important APIs, types, and functions
This file defines build symbols, not C APIs. Symbols are `PHY_HI6220_USB`, `PHY_HI3660_USB`, `PHY_HI3670_USB`, `PHY_HI3670_PCIE`, `PHY_HISTB_COMBPHY`, `PHY_HISI_INNO_USB2`, and `PHY_HIX5HD2_SATA`.

## Control flow
Kconfig selection gates whether corresponding objects are built. Most entries are `tristate`, select `GENERIC_PHY`, and several select `MFD_SYSCON` because drivers use syscon/regmap phandles.

## State and persistence
The selected config symbols persist in the kernel `.config` and control build inclusion. No runtime state exists.

## Dependencies and integration points
Integrates with architecture symbols such as `ARCH_HISI`, `ARM64`, `ARCH_HIX5HD2`, `OF`, `HAS_IOMEM`, and `COMPILE_TEST`. Downstream Makefile maps symbols to object files.

## Risks and test signals
Risks are missing dependencies for drivers using clk/reset/regmap APIs or too-restrictive architecture guards. Test with `allmodconfig`, `COMPILE_TEST`, and target defconfigs to ensure symbol visibility and build coverage.
