# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-visionox-vtdr6130.c

## Purpose
This is a DRM panel driver for the Visionox VTDR6130 AMOLED DSI panel. It provides a fixed 1080x2400 144 Hz mode, vendor DCS initialization, regulator/reset sequencing, and raw backlight control.

## Important APIs, Types, and Functions
`struct visionox_vtdr6130` stores the DRM panel, DSI device, reset GPIO, and three supplies. Core functions are `visionox_vtdr6130_reset`, `visionox_vtdr6130_on`, `visionox_vtdr6130_off`, prepare/unprepare, mode enumeration, `visionox_vtdr6130_bl_update_status`, and DSI probe/remove.

## Control Flow
Probe allocates the panel, gets `vddio`, `vci`, and `vdd`, obtains reset, sets four-lane RGB888 DSI video mode with no EOT and non-continuous clock, registers a 4095-step raw backlight, adds the panel, and attaches. Prepare enables all supplies, runs reset, sends tear-on, display control, brightness, page/keyed vendor tables, exits sleep, waits 120 ms, and turns the panel on. Unprepare sends display-off and sleep, asserts reset, and disables regulators.

## State and Persistence Behavior
The file keeps only device lifetime state. Hardware state persists across prepare until unprepare: regulator rails, reset state, DSI mode flags, panel command pages, sleep/display state, and current DCS brightness value.

## Dependencies and Integration Points
It uses DRM panel and MIPI DSI helpers, Linux regulator and GPIO consumers, OF matching for `visionox,vtdr6130`, and the backlight core. Connector physical size is populated from the fixed mode.

## Risks
The on-sequence contains many undocumented command pages and magic values. The backlight update callback does not force low-power mode like the prepare path, so host requirements for DCS brightness transfers matter. Failure during `visionox_vtdr6130_off` is not propagated. Timing is tuned for the panel and may not tolerate aggressive PM.

## Test Signals
Important tests include probe/attach, repeated prepare/unprepare, mode probe at 144 Hz, brightness writes across the 0-4095 range, suspend/resume with regulator sequencing, and oscilloscope or host logs for reset and DSI command timing.
