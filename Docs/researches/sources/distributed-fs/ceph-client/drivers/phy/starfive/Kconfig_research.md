# sources/distributed-fs/ceph-client/drivers/phy/starfive/Kconfig

Purpose: Kconfig entries for StarFive JH7110 D-PHY RX, D-PHY TX, PCIe/USB3 PHY, and USB2 PHY drivers.

Important APIs, types, and functions: under `ARCH_STARFIVE || COMPILE_TEST`, declares `PHY_STARFIVE_JH7110_DPHY_RX`, `PHY_STARFIVE_JH7110_DPHY_TX`, `PHY_STARFIVE_JH7110_PCIE`, and `PHY_STARFIVE_JH7110_USB`. D-PHY entries depend on MMIO and select `GENERIC_PHY` plus `GENERIC_PHY_MIPI_DPHY`; PCIe and USB select `GENERIC_PHY`, and USB depends on `USB_SUPPORT`.

Control flow: build-time selection only.

State and persistence: none.

Dependencies and integration points: MIPI CSI/DSI, PCIe/USB3, and Cadence USB controller PHY consumers on JH7110.

Risks: PCIe/USB drivers use clocks/syscon but Kconfig only expresses MMIO/USB support; compile-test should catch missing implicit dependencies.

Test signals: StarFive defconfig, allmodconfig, MIPI D-PHY framework availability, and consumer controller probe tests.
