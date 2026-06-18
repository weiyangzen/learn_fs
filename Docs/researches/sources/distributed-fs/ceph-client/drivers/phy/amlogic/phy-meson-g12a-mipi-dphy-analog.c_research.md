# sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-g12a-mipi-dphy-analog.c

Purpose: Controls the G12A MIPI DSI analog D-PHY registers in the parent HHI syscon block. It supplies analog lane enables and bias/reference programming for a separate digital DSI PHY user.

Important APIs and types: `struct phy_g12a_mipi_dphy_analog_priv` stores the PHY, HHI regmap, and cached `phy_configure_opts_mipi_dphy`. `phy_g12a_mipi_dphy_analog_configure()` validates and stores MIPI options. Power callbacks write three HHI MIPI control registers.

Control flow: probe gets the parent HHI syscon regmap, creates a simple PHY, and registers it as an OF provider for `amlogic,g12a-mipi-dphy-analog`. Power-on writes reference, bandgap, and differential TX constants, then builds the enabled-channel mask from the configured lane count. Power-off clears all three HHI registers.

State and persistence: Only the cached MIPI config persists in software. Hardware state is direct register programming and is not restored by a PM callback.

Dependencies and integration: It uses regmap syscon access, generic PHY, MIPI-DPHY validation, and `dt-bindings/phy/phy.h`. It integrates as an analog provider for G12A-family MIPI DSI display paths.

Risks and test signals: Unlike the AXG analog driver, this file does not track whether configure ran before power-on; an uninitialized lane count would produce only the clock-lane default path. Test with display pipeline configure-before-power ordering, 1-4 lane panels, power-off register clearing, invalid lane counts, and parent syscon probe errors.
