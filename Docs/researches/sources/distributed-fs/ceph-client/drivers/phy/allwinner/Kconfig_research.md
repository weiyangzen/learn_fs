# sources/distributed-fs/ceph-client/drivers/phy/allwinner/Kconfig

Purpose: Allwinner-specific PHY driver configuration menu for USB2, USB3, and MIPI D-PHY blocks.

Important APIs, types, and functions: declarative symbols are `PHY_SUN4I_USB`, `PHY_SUN6I_MIPI_DPHY`, `PHY_SUN9I_USB`, and `PHY_SUN50I_USB3`. They select core dependencies such as `GENERIC_PHY`, `USB_COMMON`, `GENERIC_PHY_MIPI_DPHY`, and `REGMAP_MMIO`.

Control flow: Kconfig exposes tristate options gated by `ARCH_SUNXI || COMPILE_TEST`, `HAS_IOMEM`, `RESET_CONTROLLER`, `USB_SUPPORT`, `EXTCON`, `POWER_SUPPLY`, `COMMON_CLK`, and `OF` as appropriate. The selected symbols drive object inclusion in the Allwinner Makefile.

State and persistence: only kernel configuration state in `.config`; no runtime behavior.

Dependencies and integration: integrates Allwinner SoC PHY drivers with generic PHY framework, USB common helpers, extcon/power-supply infrastructure for OTG detection, reset controller, regmap MMIO, and MIPI D-PHY helpers.

Risks: `PHY_SUN4I_USB` has broad dependencies because the driver supports OTG extcon and VBUS power-supply notification; missing any dependency breaks compile. MIPI D-PHY selection must include `GENERIC_PHY_MIPI_DPHY` or timing validation helpers are unavailable. Test signals include SUNXI defconfig coverage, compile-test builds, and module naming (`sun6i_mipi_dphy`).
