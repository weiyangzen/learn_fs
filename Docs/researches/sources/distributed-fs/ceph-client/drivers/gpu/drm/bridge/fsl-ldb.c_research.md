# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/fsl-ldb.c

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/fsl-ldb.c

## Purpose

This driver implements Freescale/NXP LDB LVDS bridge support for i.MX6SX, i.MX8MP, and i.MX93-style syscon-controlled LVDS blocks. It connects one or two LVDS channels to a panel bridge and programs data width, bit mapping, split mode, clocking, and analog LVDS control.

## Important APIs, Types, And Functions

`struct fsl_ldb` stores bridge, panel bridge, LDB clock, syscon regmap, device data, channel enable flags, and termination option. Core functions are `fsl_ldb_probe/remove()`, `fsl_ldb_atomic_enable/disable()`, `fsl_ldb_atomic_get_input_bus_fmts()`, `fsl_ldb_mode_valid()`, and `fsl_ldb_link_frequency()`.

## Control Flow

Probe selects device data from OF, gets the `ldb` clock and parent syscon regmap, inspects ports 1/2 to determine enabled channels and panel node, creates a panel bridge, validates dual-link pixel order, and adds the bridge. Atomic enable reads negotiated LVDS output bus format, retrieves adjusted mode from connector/CRTC state, sets LDB clock to pixel clock times 7 or 3.5 for dual-link, enables the clock, writes LDB control bits, and for newer blocks writes LVDS analog control with optional termination before enabling channels. Disable clears LVDS and LDB control registers and disables the clock.

## State And Persistence Behavior

Channel availability and termination are probe-time state; clock rate and registers are programmed per enable. No persistent storage exists.

## Dependencies And Integration Points

It depends on syscon regmap, common clock framework, OF graph, panel bridge helpers, DRM bridge atomic negotiation, media bus LVDS formats, and `drm_of_lvds_get_dual_link_pixel_order()`.

## Risks And Test Signals

Risks include unsupported even-odd dual-link order, falling back to SPWG24 when downstream format is absent, exact clock-rate mismatch warnings, and SoC-specific LVDS enable polarity differences. Test signals are accepted single/dual-link modes, correct LVDS bus format, clock programming at 7x or 3.5x pixel rate, and visible panel output.
