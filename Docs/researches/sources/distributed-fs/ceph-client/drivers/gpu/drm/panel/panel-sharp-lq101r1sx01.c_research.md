# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sharp-lq101r1sx01.c

## Purpose
Implements the Sharp LQ101R1SX01 dual-link MIPI DSI panel. It registers a DRM panel only for the primary DSI link, uses the second link for split output, programs panel registers through generic DSI writes, and exposes a 2560x1600 mode.

## Important APIs, types, and functions
- `struct sharp_panel` stores primary and secondary DSI devices, regulator supply, and active mode.
- `sharp_panel_write()` sends a 16-bit register offset plus value over generic DSI to link1, followed by a DCS NOP and a short delay.
- `sharp_panel_read()` is a debug/helper read path marked `__maybe_unused`.
- `sharp_setup_symmetrical_split()` sets DCS column/page windows so left and right links cover half the horizontal resolution.
- `sharp_panel_prepare()` powers the panel, exits sleep, programs left-right split mode and command mode, sets RGB888 pixel format, configures the split, turns display on, and waits six frames.
- `sharp_panel_probe()` attaches both DSI endpoints but only creates the panel object when probing the DSI-LINK1 endpoint that references `link2`.

## Control flow
Each DSI endpoint probes with four RGB888 lanes and LPM. The primary link locates the secondary DSI peripheral through the `link2` phandle. When found, the driver allocates and registers a panel, obtains the `power` regulator and optional OF backlight, stores both links, and attaches the primary. The secondary probe may simply attach without a panel if it has no `link2`. Prepare enables power, waits for panel readiness, exits sleep on link1, enables left-right and command modes through vendor registers, sets pixel format, programs link1 and link2 address windows, turns display on, and waits frame-derived time. Unprepare waits four frames, sends display-off and sleep-in on link1, waits 120 ms, and disables power.

## State and persistence
State includes the secondary DSI device reference obtained with `of_find_mipi_dsi_device_by_node()`, released in `sharp_panel_del()`. Hardware state includes split mode, command mode, DCS address windows, pixel format, and display/sleep state. The panel mode pointer is static. Backlight state is external through `drm_panel_of_backlight()`.

## Dependencies and integration points
The driver depends on DRM panel APIs, MIPI DSI DCS/generic helpers, OF phandle lookup, regulators, and optional backlight. It binds `sharp,lq101r1sx01` and integrates with host drivers that expose two coordinated DSI peripherals.

## Risks
Only left-right split is supported; even-odd split would need host/panel coordination not present here. `sharp_wait_frames()` uses integer frame math and warns if asked for more frames than refresh. Register writes go only over link1, so hardware must propagate global settings appropriately. If probe order makes `link2` unavailable, the primary returns `-EPROBE_DEFER`.

## Test signals
Important signals are successful primary/secondary probe ordering, no leaked secondary device reference on failure/remove, correct 2560x1600 mode, both panel halves displaying their expected columns, clean power-on/off timing, and stable external backlight behavior.
