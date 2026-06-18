# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-summit.c

## Purpose
This compact MIPI DSI panel driver models Apple Summit as a non-desktop display with a fixed 60x2008 mode and a raw DCS brightness backlight. It primarily provides mode enumeration and brightness control rather than explicit power sequencing.

## Important APIs, Types, And Functions
`struct summit_data` stores the DSI device, backlight, and DRM panel. `summit_set_brightness()` sends `mipi_dsi_dcs_set_display_brightness()` with the current backlight level. `summit_get_modes()` marks the connector non-desktop and delegates mode creation to `drm_connector_helper_get_modes_fixed()`. Suspend/resume PM uses `summit_suspend()` and `summit_set_brightness()`.

## Control Flow
Probe allocates the panel, stores DSI driver data, reads `max-brightness` from firmware properties, registers a raw backlight using that maximum, adds the panel, and attaches to the DSI host. Remove detaches and removes the panel. There are no explicit prepare/enable/disable/unprepare ops; brightness is used by backlight and PM callbacks.

## State And Persistence
State is limited to the DSI pointer, backlight object, and panel. Brightness is managed by backlight core and sent to the panel on update/resume. No persistent state is written.

## Dependencies And Integration Points
The file depends on DRM panel/mode/helper APIs, MIPI DSI DCS brightness, backlight core, generic device properties, non-desktop connector property support, and simple dev PM ops. It binds `apple,summit`.

## Risks
The mode is unusual (`hdisplay = 60`, `vdisplay = 2008`) and intentionally non-desktop, so generic desktop assumptions should not be applied. Missing `max-brightness` fails probe. There is no regulator/GPIO sequencing, so hardware must be powered by other platform components. DSI mode flags are not configured in this driver, relying on host/default setup or firmware assumptions.

## Test Signals
Validation should confirm property parsing, backlight registration with expected max brightness, non-desktop connector flag/property, fixed mode reporting, DSI attach/detach, suspend brightness zeroing, and resume brightness restoration.
