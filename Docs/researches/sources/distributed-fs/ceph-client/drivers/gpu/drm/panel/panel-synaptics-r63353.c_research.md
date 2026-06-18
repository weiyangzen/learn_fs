# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-synaptics-r63353.c

## Purpose
This MIPI DSI driver supports panels using the Synaptics R63353 controller, currently described by the Sharp LS068B3SX02 descriptor. It powers two regulators, controls reset, emits a descriptor-defined init command list, and reports a fixed RGB888 DSI mode.

## Important APIs, Types, And Functions
`struct r63353_instr` and `R63353_INSTR()` encode initialization commands. `struct r63353_desc` stores the panel name, init list, mode, and dimensions. `struct r63353_panel` contains the DRM panel, DSI device, reset GPIO, `dvdd` and `avdd`, and descriptor pointer.

Core helpers are `r63353_panel_power_on()`, `r63353_panel_power_off()`, `r63353_panel_activate()`, and `r63353_panel_deactivate()`. DRM ops are prepare, unprepare, and get_modes. Shutdown calls `drm_panel_unprepare()` to put the panel down on system shutdown.

## Control Flow
Probe allocates the panel, stores match descriptor, configures the DSI device for two RGB888 lanes with video, HSE, LPM, sync pulse, no EOT, and non-continuous clock, acquires `dvdd`, `avdd`, and reset GPIO, marks `prepare_prev_first`, binds optional backlight, adds the panel, and attaches to DSI. Prepare enables `avdd`, waits, enables `dvdd`, waits 300-350 ms, deasserts reset, soft-resets the controller, enters sleep, writes the descriptor init commands, waits 120 ms, exits sleep, then turns display on. Unprepare sends display-off/sleep and powers off.

## State And Persistence
State is descriptor-driven and held in memory only. There is no persistent storage. The init list is immutable. Hardware is reinitialized on each prepare.

## Dependencies And Integration Points
The driver uses DRM panel, MIPI DSI multi-context helpers, regulators, GPIOs, OF match data, media bus format reporting, OF backlight, and DSI shutdown handling.

## Risks
The init sequence contains brightness/control-display/display-on commands before sleep-out, so ordering is panel-specific. `r63353_panel_power_on()` uses a long regulator stabilization wait; shortening it may break real hardware. `r63353_panel_activate()` enters sleep after soft reset before writing init commands, which should not be generalized without datasheet evidence. The descriptor pointer is typed non-const in state despite pointing to static data.

## Test Signals
Check regulator sequencing and long delay, reset polarity, DSI attach, fixed mode dimensions, RGB888 bus format, backlight binding, shutdown unprepare, and error rollback when activation fails.
