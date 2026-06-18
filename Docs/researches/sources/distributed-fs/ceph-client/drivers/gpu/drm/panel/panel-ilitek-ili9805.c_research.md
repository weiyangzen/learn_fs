# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9805.c

## Purpose

This MIPI DSI DRM panel driver supports Ilitek ILI9805 controller panels, with descriptors for Giantplus GPM1790A0 and Tianma TM041XDHG01. It uses descriptor-provided command arrays and fixed display modes.

## Important APIs, Types, And Functions

`struct ili9805_instr` represents one DCS write buffer plus an optional delay. `struct ili9805_desc` stores the panel name, init array, fixed mode, and physical dimensions. `struct ili9805` owns the DRM panel, DSI device, descriptor, `dvdd`/`avdd` regulators, and reset GPIO.

`ili9805_power_on()` enables regulators and toggles reset. `ili9805_activate()` iterates descriptor commands with `mipi_dsi_dcs_write_buffer()`, exits sleep, waits, and turns display on. `ili9805_deactivate()` sends display-off and sleep-in. `ili9805_prepare()` and `ili9805_unprepare()` compose power and DCS activation/deactivation. Probe configures two-lane RGB888 DSI video and attaches the panel.

## Control Flow

Probe allocates the panel, stores descriptor match data, configures DSI flags including HSE, sync pulse, non-continuous clock, LPM, and no-EOT, obtains regulators and reset GPIO, gets a DT backlight, adds the panel, and attaches DSI. Prepare enables `avdd`, then `dvdd`, releases reset, waits 120 ms, sends the descriptor init table, exits sleep, and turns display on. Unprepare sends display-off/sleep-in and then disables power.

## State And Persistence

There is no persistent state. Panel behavior is determined by static descriptor arrays selected from OF match data. Runtime state is the DSI attachment, regulators, reset GPIO, and optional DT backlight.

## Dependencies And Integration Points

The driver integrates with DRM panel, MIPI DSI, GPIO, regulators, and OF match data. It requires supplies `dvdd` and `avdd`, a `reset` GPIO, a backlight binding when needed, and compatibles `giantplus,gpm1790a0` or `tianma,tm041xdhg01`.

## Risks

The descriptor width/height fields are not copied into the `drm_display_mode`; `ili9805_get_modes()` uses `mode->width_mm` and `mode->height_mm`, which are unset in the provided timing structures. The code logs DSI failures in activation/deactivation but `ili9805_unprepare()` ignores a deactivate failure before powering off. Command arrays are opaque and panel-specific. The two compatibles share DSI bus configuration even though they have different vertical resolutions.

## Test Signals

Check DSI attach, correct fixed 480x480 or 480x768 mode selection, physical size reporting, backlight binding, reset and regulator sequencing, command-array writes with delays, visible output after sleep-out/display-on, and suspend/resume behavior when DCS sleep commands fail.
