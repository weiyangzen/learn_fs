<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_dw_hdmi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_dw_hdmi.h

## Purpose

`sun8i_dw_hdmi.h` defines the Allwinner-specific DW-HDMI wrapper, PHY register map, PHY/clock variant structures, and cross-file APIs connecting the DW-HDMI component with the HDMI PHY and PHY clock provider.

## Important APIs, Types, And Definitions

The header names HDMI PHY debug, REXT, read-enable, unscramble, analog, PLL, status, and CEC registers with bitfields. `struct sun8i_hdmi_phy_variant` selects PHY clock availability, second PLL, DW-HDMI PHY tables or ops, and init callback. `struct sun8i_hdmi_phy` stores clocks, regmap, reset, calibration, and variant. `struct sun8i_dw_hdmi_quirks` stores mode validation and infoframe behavior. `struct sun8i_dw_hdmi` stores controller runtime state. APIs include `sun8i_hdmi_phy_get/init/deinit/set_ops()` and `sun8i_phy_clk_create()`.

## Control Flow

No standalone flow runs here. The DW-HDMI component calls PHY APIs declared here; the PHY driver and clock provider use the register macros and structures to initialize hardware and expose clock ops.

## State And Persistence Behavior

The structures persist for platform device lifetimes. `rcal` stores calibration read from PHY analog status. `phy->clk_phy` may be created dynamically during PHY init and then used by mode programming.

## Dependencies And Integration Points

It includes DW-HDMI bridge declarations, DRM encoder, clocks, regmap, regulator, and reset APIs. It is the shared contract among `sun8i_dw_hdmi.c`, `sun8i_hdmi_phy.c`, and `sun8i_hdmi_phy_clk.c`.

## Risks And Test Signals

Risks include register macro mistakes, variant table mismatches, and lifecycle assumptions around optional PHY clock creation. Test by building all three files together and running HDMI modes across A83T/H3/R40/A64/H6 variants, including PHY init/deinit and clock parent/divider paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_dw_hdmi.h -->
