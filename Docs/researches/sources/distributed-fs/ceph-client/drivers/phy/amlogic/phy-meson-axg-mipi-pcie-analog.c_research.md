# sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-axg-mipi-pcie-analog.c

Purpose: Provides the shared AXG analog PHY controls used by MIPI DSI and PCIe-related analog circuitry through the HHI syscon register block.

Important APIs and types: `struct phy_axg_mipi_pcie_analog_priv` stores the HHI regmap, current MIPI-DPHY configuration, and booleans for configured, enabled, and powered state. Helper routines split bandgap control from DSI lane analog setup: `phy_bandgap_enable()`, `phy_bandgap_disable()`, `phy_dsi_analog_enable()`, and `phy_dsi_analog_disable()`.

Control flow: probe obtains the parent syscon regmap, creates one simple PHY, and registers `of_phy_simple_xlate`. Configure validates and caches MIPI-DPHY options; if the analog block is already powered it disables any active DSI analog setup, waits briefly, and re-enables with the new lane mask. Power-on enables bandgap and, when configured, enables the DSI analog lanes. Power-off disables bandgap and tears down DSI analog state.

State and persistence: The driver keeps only software booleans and a cached config. HHI registers hold the actual analog programming. There is no locking, so callers are expected to serialize generic PHY operations.

Dependencies and integration: It depends on parent-node `syscon`, regmap update/write helpers, and generic PHY MIPI config validation. It integrates with `phy-meson-axg-mipi-dphy.c` as the named `analog` PHY and may also be relevant to PCIe PHY setup on AXG.

Risks and test signals: Lane mask construction assumes validated lane counts from 1 to 4, but invalid cached lane values would disable all lanes. Reconfiguration while powered is explicitly handled, but concurrent configure/power calls would be unsafe. Test DSI lane-count changes, power-on before configure, configure after power-on, syscon probe deferral, and cleanup of HHI_MIPI_CNTL registers on power-off.
