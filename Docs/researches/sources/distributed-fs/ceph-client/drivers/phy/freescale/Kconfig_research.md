# sources/distributed-fs/ceph-client/drivers/phy/freescale/Kconfig

## Purpose
Declares Freescale/NXP PHY options, including `PHY_MIXEL_MIPI_DPHY` and `PHY_FSL_IMX8M_PCIE`.

## APIs and dependencies
Most i.MX entries are gated by `(ARCH_MXC && ARM64) || COMPILE_TEST`. `PHY_MIXEL_MIPI_DPHY` depends on `OF && HAS_IOMEM` and selects `GENERIC_PHY`, `GENERIC_PHY_MIPI_DPHY`, and `REGMAP_MMIO`. `PHY_FSL_IMX8M_PCIE` depends on `OF && HAS_IOMEM` and selects `GENERIC_PHY`.

## Control flow and state
Enabled symbols drive object inclusion through the Freescale Makefile. Kconfig has no runtime state.

## Integration, risks, and test signals
The file integrates i.MX and Layerscape PHY drivers with Generic PHY, MIPI D-PHY helpers, and regmap-mmio. The Mixel combo path also needs i.MX firmware IPC at runtime, which is not obvious from this entry. Test built-in and module configs for the two symbols under target and compile-test builds.
