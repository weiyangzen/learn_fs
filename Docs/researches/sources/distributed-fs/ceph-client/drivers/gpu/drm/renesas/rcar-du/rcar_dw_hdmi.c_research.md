# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_dw_hdmi.c

## Purpose

`rcar_dw_hdmi.c` is the Renesas R-Car Gen3 wrapper around the Synopsys DesignWare HDMI bridge. It supplies R-Car PHY programming tables and a mode clock limit to the common `dw_hdmi` driver.

## Important APIs, Types, and Functions

`struct rcar_hdmi_phy_params` maps maximum pixel clocks to three PHY register values. `rcar_hdmi_mode_valid()` rejects modes above 297 MHz. `rcar_hdmi_phy_configure()` selects the first table entry whose `mpixelclock` covers the requested clock and writes PHY I2C registers through `dw_hdmi_phy_i2c_write()`. Probe/remove call `dw_hdmi_probe()` and `dw_hdmi_remove()` with `rcar_dw_hdmi_plat_data`.

## Control Flow

Platform probe creates the common DW-HDMI device and stores it as driver data. During mode validation the bridge rejects unsupported high clocks. During PHY setup the wrapper picks table parameters and programs PLL operation, current/GMP, and divider registers. Remove tears down the common bridge.

## State and Persistence Behavior

Persistent state is owned by the common DW-HDMI object. This wrapper keeps only constant platform data and PHY tables. PHY register state persists in hardware until the common HDMI driver reprograms or powers down the block.

## Dependencies and Integration Points

It depends on `drm/bridge/dw_hdmi.h`, DRM mode validation, module/platform driver APIs, and the DT compatible `renesas,rcar-gen3-hdmi`. It integrates with DU encoder/bridge chains through the generic DW-HDMI bridge.

## Risks and Edge Cases

- PHY table coverage ends at 297 MHz; modes above that are rejected.
- The table uses upper-bound matching, so boundary values must match hardware characterization.
- No runtime PM or clock/reset handling is in this wrapper; those responsibilities are either unnecessary for this integration or owned elsewhere.

## Test Signals

Probe/remove under DT, EDID mode validation around 297 MHz, HDMI modes across all table thresholds, and PHY I2C write traces are the useful signals.
