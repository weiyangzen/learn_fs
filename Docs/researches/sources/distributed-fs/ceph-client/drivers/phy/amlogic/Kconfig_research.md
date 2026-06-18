# sources/distributed-fs/ceph-client/drivers/phy/amlogic/Kconfig

Purpose: Amlogic/Meson PHY driver configuration menu covering HDMI TX, USB2, USB3/PCIe combo, PCIe, and MIPI D-PHY analog/digital PHYs.

Important APIs, types, and functions: symbols are `PHY_MESON8_HDMI_TX`, `PHY_MESON8B_USB2`, `PHY_MESON_GXL_USB2`, `PHY_MESON_G12A_MIPI_DPHY_ANALOG`, `PHY_MESON_G12A_USB2`, `PHY_MESON_G12A_USB3_PCIE`, `PHY_MESON_AXG_PCIE`, `PHY_MESON_AXG_MIPI_PCIE_ANALOG`, and `PHY_MESON_AXG_MIPI_DPHY`.

Control flow: Kconfig gates most drivers on `OF && (ARCH_MESON || COMPILE_TEST)` and defaults many to `ARCH_MESON`. Symbols select needed infrastructure such as `GENERIC_PHY`, `REGMAP_MMIO`, `MFD_SYSCON`, `USB_COMMON`, and `GENERIC_PHY_MIPI_DPHY`. The paired Makefile maps enabled symbols to C objects.

State and persistence: configuration only; no runtime state.

Dependencies and integration: integrates Amlogic PHY drivers with generic PHY core, USB support, regmap MMIO, MFD syscon, and MIPI D-PHY helpers.

Risks: defaulting several symbols to `ARCH_MESON` increases build coverage but can pull drivers into platform configs unexpectedly. Analog and digital MIPI pieces require matching consumer/controller expectations. Test signals include Meson defconfigs, compile-test builds, dependency resolution for `REGMAP_MMIO`/`MFD_SYSCON`, and module/object generation.
