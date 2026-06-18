# sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-imx8qm-lvds-phy.c

## Purpose
Mixel LVDS PHY provider for i.MX8QM display links. It exposes two LVDS PHY channels, validates LVDS configuration, sets reference clock rate, coordinates master/slave dual-channel operation, controls channel enable bits, and handles runtime PM power-down/up.

## Important APIs, types, and functions
- `struct mixel_lvds_phy_priv` stores the syscon regmap, reference clock, mutex, and two channel objects.
- `struct mixel_lvds_phy` stores per-channel `phy_configure_opts_lvds`, ID, and generic PHY.
- `mixel_lvds_phy_validate()` enforces `PHY_MODE_LVDS`, 7/10 bits per lane, 3/4 lanes, 25-165 MHz differential clock, and matching master/slave configuration.
- `mixel_lvds_phy_configure()` sets the PHY reference clock to the requested differential clock rate.
- `mixel_lvds_phy_power_on()` programs divider mode from link format, enables one or both channels, and polls `LOCK`.
- Runtime PM callbacks set/clear the `PD` bit and restore initialization fields.

## Control flow
Probe gets the parent syscon regmap and ref clock, enables runtime PM, writes the POR value, creates two PHYs, and registers a custom xlate with one channel index argument. Consumers validate and configure before power-on. Slave channels are passive: the master powers on/off both channels when the companion is marked slave. Power-on holds the lock while setting mode/channel bits and polling PLL lock.

## State and persistence
State is cached per-channel LVDS configuration and MMIO register state. The mutex protects shared regmap access and cached configuration. Runtime PM may power the block down between active uses; no persistent storage is used.

## Dependencies and integration points
Uses generic PHY LVDS configure/validate operations, clk, syscon/regmap, platform device, and runtime PM. Integrates with display bridge/encoder consumers that configure LVDS physical parameters through `phy_configure_opts_lvds`.

## Risks and test signals
Risks include relying on master configuration being cached before slave validation, clock disable on lock failure while still holding shared state, and probe error paths requiring runtime PM disable. Test master-only and dual-channel master/slave display modes, invalid LVDS opts, runtime suspend/resume, and PLL-lock timeout handling.
