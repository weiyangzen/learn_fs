# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/microchip-lvds.c

## Purpose

This platform driver exposes the Microchip SAM9X75 LVDS controller as a DRM bridge to an LVDS panel. It maps the LVDS controller registers, enables the pixel clock and runtime PM, programs the serializer for JEIDA 24-bit LVDS with high DE polarity, and attaches the downstream panel bridge.

## Important APIs, Types, And Functions

`struct mchp_lvds` contains the device, MMIO base, pixel clock, panel pointer, DRM bridge, and panel bridge. Register helpers are `lvds_readl()` and `lvds_writel()`. `lvds_serialiser_on()` unlocks write protection, waits for configuration status to clear, writes `LVDSC_CFGR`, and enables serialization with `LVDSC_CR_SER_EN`.

Bridge callbacks are `mchp_lvds_attach()`, `mchp_lvds_enable()`, and `mchp_lvds_disable()`.

## Control Flow

Probe requires OF, allocates the bridge, maps MMIO, gets `pclk`, finds the panel from output port 1, gets the panel bridge via `devm_drm_of_get_bridge()`, sets connector type LVDS, enables runtime PM, and registers the bridge. Enable prepares/enables `pclk`, resumes runtime PM, and turns on the serializer. Disable drops runtime PM and disables the clock.

## State And Persistence

The driver has no per-mode state and no suspend/resume-specific storage. LVDS controller configuration persists in MMIO registers while the hardware remains powered. Runtime PM and clock state control register access and serializer operation.

## Dependencies And Integration Points

Dependencies include platform MMIO resources, clocks, PM runtime, OF graph, DRM bridge/panel helpers, and low-level register access. It integrates as a simple bridge between a display controller and an LVDS panel.

## Risks And Edge Cases

`mchp_lvds_enable()` returns void and does not unwind `clk_prepare_enable()` if `pm_runtime_get_sync()` fails. The serializer configuration is hardcoded to JEIDA, 24-bit, high DE, and unbalanced DC, with no bus-format negotiation. `lvds_serialiser_on()` times out with only an error log. There is no remove callback to explicitly remove the bridge, relying on platform/device lifetime behavior.

## Test Signals

Test build/probe for `microchip,sam9x75-lvds`, missing MMIO/clock/panel resources, runtime PM failures, serializer status timeout, enable/disable cycles, panel bridge attachment, and visual validation for JEIDA 24-bit LVDS timing/polarity.
