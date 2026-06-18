# sources/distributed-fs/ceph-client/drivers/phy/st/Kconfig

Purpose: Kconfig entries for STMicroelectronics PHY drivers in this subtree.

Important APIs, types, and functions: declares `PHY_MIPHY28LP`, `PHY_ST_SPEAR1310_MIPHY`, `PHY_ST_SPEAR1340_MIPHY`, `PHY_STIH407_USB`, `PHY_STM32_COMBOPHY`, and `PHY_STM32_USBPHYC`. Entries select `GENERIC_PHY`; STM32 USBPHYC also depends on `COMMON_CLK`; STiH407 USB depends on reset controller.

Control flow: build-time selection only.

State and persistence: no runtime state.

Dependencies and integration points: covers STiH407 MiPHY/picoPHY, SPEAr PCIe/SATA PHYs, STM32MP25 ComboPHY, and STM32 USBPHYC. Help text documents the controller/protocol relationships.

Risks: `PHY_MIPHY28LP` depends only on `ARCH_STI` and is not compile-test exposed, so broad build coverage is lower. Several drivers use syscon/regmap but do not all express `MFD_SYSCON` dependencies explicitly in this file.

Test signals: ST platform defconfigs, allmodconfig/compile-test where available, and dependency checking for reset, clock, and syscon APIs.
