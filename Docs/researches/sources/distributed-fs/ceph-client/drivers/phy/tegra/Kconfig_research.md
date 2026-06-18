# sources/distributed-fs/ceph-client/drivers/phy/tegra/Kconfig

Purpose: Kconfig entries for NVIDIA Tegra XUSB pad controller and Tegra194/Tegra234 P2U PHY driver.

Important APIs, types, and functions: `PHY_TEGRA_XUSB` depends on `ARCH_TEGRA && USB_SUPPORT`, selects USB common/connector/PHY helpers, and builds the XUSB pad controller. `PHY_TEGRA194_P2U` depends on Tegra or compile-test and selects `GENERIC_PHY`.

Control flow: build-time selection only.

State and persistence: none.

Dependencies and integration points: XUSB pad controller supports multiple Tegra SoC files; P2U supports PIPE-to-UPHY blocks for PCIe on Tegra194 and Tegra234.

Risks: XUSB is not compile-test enabled outside Tegra, while P2U is. Consumers require correct SoC object selection in the Makefile.

Test signals: Tegra defconfig builds, compile-test for P2U, and module alias checks for Tegra194/Tegra234 compatibles.
