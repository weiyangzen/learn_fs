# sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-axg-mipi-dphy.c

Purpose: Implements the digital MIPI DSI D-PHY block for Amlogic Meson AXG. It bridges the generic PHY MIPI-DPHY interface to AXG DSI control registers and coordinates with a separate analog PHY instance.

Important APIs and types: `struct phy_meson_axg_mipi_dphy_priv` stores the MMIO regmap, `pclk`, reset, analog PHY, and last `phy_configure_opts_mipi_dphy`. `phy_meson_axg_mipi_dphy_configure()` validates MIPI timing with `phy_mipi_dphy_config_validate()`, forwards the same options to the analog PHY, and caches them. The `phy_ops` implement `.init`, `.exit`, `.configure`, `.power_on`, and `.power_off`.

Control flow: probe maps the DSI PHY register window, creates an 8-bit/32-bit regmap, gets `pclk`, reset `phy`, and named `analog`, then enables the clock and deasserts reset before registering a simple OF PHY provider. Init initializes the analog PHY and resets the digital block. Power-on powers the analog side first, enables DSI clocking, calculates byte-clock timing from `hs_clk_rate`, programs clock/HS/LP/init/wakeup/watchdog timing registers, powers the selected number of data lanes, and syncs `txclkesc`. Power-off powers down all lanes, asserts soft reset, then powers off analog.

State and persistence: The driver persists only runtime configuration in `priv->config`; hardware state lives in DSI registers and the companion analog PHY. There is no suspend/resume or NVM state. Dependencies include `clk`, reset controller, generic PHY, regmap MMIO, and the MIPI-DPHY timing helpers.

Integration points: It is matched by `amlogic,axg-mipi-dphy` and is consumed by DSI/display drivers through the generic PHY framework. The named `analog` PHY links it to the AXG MIPI/PCIe analog provider.

Risks and test signals: Timing conversion depends on a valid nonzero `hs_clk_rate` and integer rounding of picosecond periods. Probe enables `pclk` without a remove-time disable path because it relies on devm lifetime and permanent PHY availability. Test with 1-4 lane DSI modes, invalid MIPI timing, analog PHY probe deferral, power-cycle ordering, and scope-visible LP/HS timing after mode changes.
