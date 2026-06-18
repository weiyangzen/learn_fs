# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-dsi-j721e.c

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-dsi-j721e.c

## Purpose

This file implements the TI J721E wrapper operations for the generic Cadence DSI core. The wrapper selects and enables the SoC-specific DPI path feeding the Cadence DSI block.

## Important APIs, Types, And Functions

`cdns_dsi_j721e_init()` maps the second platform resource into `dsi->j721e_regs`. `cdns_dsi_j721e_enable()` writes `DSI_WRAP_DPI_0_EN` to the wrapper DPI control register. `cdns_dsi_j721e_disable()` clears that register. `dsi_ti_j721e_ops` exports those functions as `struct cdns_dsi_platform_ops`.

## Control Flow

The core driver obtains these ops from OF match data for `"ti,j721e-dsi"`. During probe, the wrapper maps its extra MMIO resource. During atomic pre-enable, before Cadence link/PHY programming, the wrapper enables DPI0. During post-disable, after the Cadence stream has been stopped, it resets the wrapper DPI control to defaults.

## State And Persistence Behavior

The only persistent runtime state is the extra MMIO pointer stored in `struct cdns_dsi`. Hardware state is a single wrapper register bit, restored to zero on disable. No clocks, resets, or allocations are owned here.

## Dependencies And Integration Points

This wrapper depends on the generic Cadence DSI core and platform resource index 1. It is selected only when `CONFIG_DRM_CDNS_DSI_J721E` is enabled and integrated through the core OF table.

## Risks And Test Signals

The hard-coded routing supports only the J721E configuration where DSS0 DPI2 feeds DSI DPI0. Wrong DT resource ordering or unsupported routing would produce a blank panel despite the Cadence core succeeding. Test with a J721E DSI panel should show wrapper enable before link start and clean disable on modeset teardown.
