# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sharp-lq079l1sx01.c

## Purpose
Implements a dual-link MIPI DSI DRM panel driver for the Sharp LQ079L1SX01 panel. It drives both left and right DSI hosts, powers four regulators, performs a simple DCS bring-up sequence on both links, and exposes a fixed 1536x2048 mode.

## Important APIs, types, and functions
- `struct sharp_panel` stores the DRM panel, two DSI devices, reset GPIO, regulator bulk pointer, and display mode pointer.
- `sharp_supplies[]` names the `avdd`, `vddio`, `vsp`, and `vsn` supplies.
- `mipi_dsi_dual_dcs_write_seq_multi()` is used to send the same DCS command to both DSI links.
- `sharp_panel_probe()` discovers the secondary DSI host via OF graph port 1 and registers a second DSI peripheral with name `sharp-link1`.
- `sharp_panel_prepare()` powers supplies, resets the panel, exits sleep on both links, sets brightness/power/control display registers, and turns display on.
- `sharp_panel_unprepare()` sends display-off and sleep-in to both links, asserts reset, and disables regulators.

## Control flow
Probe allocates the panel on the primary DSI device, gets all supplies and optional reset GPIO, locates the second DSI host through the graph, registers the secondary MIPI DSI device, resolves an OF backlight, adds the panel, configures both links as four-lane RGB888 video/LPM endpoints, and attaches each link with devm attach. Prepare enables regulators, waits 24 ms, toggles reset if present, waits 32 ms, then sends sleep-out, brightness, power save, control display, and display-on commands to both DSI devices. Unprepare sends display-off/sleep-in to both, waits, asserts reset, and disables all supplies.

## State and persistence
The driver tracks two DSI endpoints and shared power/reset state. Panel command state is mirrored to both links. Brightness is initialized to `0xff` in prepare, while ongoing backlight control is delegated to an external OF backlight instead of custom callbacks. Device-managed DSI attach and secondary device registration own most resource lifetime.

## Dependencies and integration points
It depends on DRM panel helpers, MIPI DSI dual-write helpers, OF graph discovery, regulator bulk APIs, GPIO, backlight lookup, and compatible `sharp,lq079l1sx01`. Integration requires a board device tree with two DSI hosts wired as expected.

## Risks
The secondary DSI host is mandatory; probe defers or fails without graph port 1. The prepare function does not return `dsi_ctx.accum_err`, so DSI command failures during bring-up are not propagated. Both links use identical mode flags, which must match host capabilities. Reset GPIO is optional, but actual hardware may require it for reliable startup.

## Test signals
Test by checking both DSI links attach, one 1536x2048 preferred mode appears, regulators enable/disable as a group, both panel halves wake and sleep together, the OF backlight controls brightness after initial setup, and no secondary-host probe deferral remains.
