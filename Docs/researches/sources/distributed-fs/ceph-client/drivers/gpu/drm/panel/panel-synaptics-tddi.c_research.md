# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-synaptics-tddi.c

## Purpose
This driver supports Synaptics TDDI DSI panels, currently `syna,td4101-panel` and `syna,td4300-panel`. It uses firmware-provided panel timings, descriptor-provided lane counts and enable/disable delays, regulator/reset/backlight GPIO sequencing, and a managed backlight device.

## Important APIs, Types, And Functions
`struct tddi_panel_data` stores lanes and panel-specific sleep/display delays. `struct tddi_ctx` stores the DRM panel, DSI device, parsed DRM mode, backlight device, descriptor data, regulator array, reset GPIO, and optional backlight GPIO. `tddi_update_status()` writes DCS brightness only when `ctx->panel.enabled` is true.

Panel functions are `tddi_prepare()`, `tddi_unprepare()`, `tddi_enable()`, `tddi_disable()`, and `tddi_get_modes()`. Probe uses `of_get_drm_panel_display_mode()` rather than hard-coded mode constants.

## Control Flow
Probe allocates the panel, gets constant regulator bulk data for `vio`, `vsn`, and `vsp`, gets optional backlight and reset GPIOs, parses the fixed mode from device tree, registers a platform backlight, configures DSI lanes/format/video flags from descriptor data, sets `prepare_prev_first`, adds the panel, and attaches with `devm_mipi_dsi_attach()`. Prepare enables regulators, toggles reset low-high-low, and drives the backlight GPIO low. Enable sends power-save/control-display commands, exits sleep, waits descriptor delay, synchronizes brightness, turns display on, and waits display-on delay. Disable performs display-off and sleep-in with descriptor delays. Unprepare drives backlight GPIO high, reset high, and disables regulators.

## State And Persistence
The parsed display mode and descriptor timing data persist for device lifetime. Brightness lives in the backlight core and is sent at enable/update time. There is no nonvolatile state.

## Dependencies And Integration Points
The driver integrates with DRM panel and probe helper fixed-mode support, MIPI DSI multi-context helpers, regulator bulk const APIs, GPIO, backlight core, OF display timing parsing, and managed DSI attach.

## Risks
Reset and backlight GPIOs are optional but used unconditionally via `gpiod_set_value_cansleep()`, which is safe for NULL descriptors but requires correct polarity in bindings. Brightness updates are skipped while the panel is disabled; callers must rely on enable to sync stored brightness. Mode correctness depends entirely on device-tree timings.

## Test Signals
Validate both compatibles for lane count and delays, device-tree timing parsing, regulator/GPIO handling when optional GPIOs are absent, brightness sync on enable, and repeated enable/disable with DSI host error injection.
