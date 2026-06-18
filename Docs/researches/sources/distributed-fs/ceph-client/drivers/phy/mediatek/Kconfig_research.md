<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/Kconfig

Purpose: Defines Kconfig options for MediaTek PHY drivers in this directory, including PCIe, XFI T-PHY, T-PHY, UFS, XS-PHY, HDMI, MIPI CSI v0.5, MIPI DSI, and DisplayPort PHY support.

Important APIs and types: This file has no C APIs. It declares `CONFIG_PHY_MTK_PCIE`, `CONFIG_PHY_MTK_XFI_TPHY`, `CONFIG_PHY_MTK_TPHY`, `CONFIG_PHY_MTK_UFS`, `CONFIG_PHY_MTK_XSPHY`, `CONFIG_PHY_MTK_HDMI`, `CONFIG_PHY_MTK_MIPI_CSI_0_5`, `CONFIG_PHY_MTK_MIPI_DSI`, and `CONFIG_PHY_MTK_DP`.

Control flow: Kconfig controls compile inclusion. Most entries depend on `ARCH_MEDIATEK || COMPILE_TEST` and OF, select `GENERIC_PHY`, and add further dependencies such as `COMMON_CLK`, `REGULATOR`, `HAS_IOMEM`, or `OF_ADDRESS`.

State and persistence: There is no runtime state. Persistent effect is build configuration and module availability.

Dependencies and integration points: Integrates with the kernel configuration system and the local Makefile. Help text documents module names for CSI and feature scope for multiprotocol PHYs.

Risks: Missing dependencies can cause compile failures when drivers include clock, regulator, nvmem, or IO APIs. Overly broad `COMPILE_TEST` exposure is useful but can surface architecture-neutral warnings.

Test signals: `allmodconfig`/`allyesconfig` compile tests, per-option module builds, dependency resolution in menuconfig, and Makefile object inclusion matching each symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/Kconfig -->
