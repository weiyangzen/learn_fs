# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-sofef00.c

## Purpose
Provides a DRM MIPI DSI panel driver for Samsung SOFEF00 DDIC panels, including the AMS628NW01 compatible. It handles three power rails, reset sequencing, a small vendor setup sequence, a fixed 1080x2280 mode, display enable/disable operations, and DCS large-brightness backlight control.

## Important APIs, types, and functions
- `struct sofef00_panel` contains the DRM panel, DSI device, regulator bulk pointer, and reset GPIO.
- `sofef00_supplies[]` defines required `vddio`, `vci`, and `poc` regulators.
- `sofef00_panel_on()` exits sleep, enables TE, writes vendor register `0xb6`, enables display control and disables power save.
- `sofef00_enable()`, `sofef00_disable()`, `sofef00_panel_prepare()`, and `sofef00_panel_unprepare()` implement the DRM lifecycle.
- `sofef00_panel_bl_update_status()` writes 16-bit brightness with `mipi_dsi_dcs_set_display_brightness_large()`.
- `sofef00_panel_probe()` creates the panel/backlight, configures the DSI endpoint, and attaches it to the host.

## Control flow
Probe obtains regulators and reset GPIO, configures four RGB888 DSI lanes with burst, non-continuous clock, and LPM, creates a platform backlight with range 0..1023, registers the panel, and attaches. Prepare enables all supplies, performs the reset pulse sequence, and executes panel-on setup. Enable only sends DCS display on. Disable sends display off and sleep-in through `sofef00_panel_off()`. Unprepare disables the regulator bulk without an extra reset toggle.

## State and persistence
Panel state lives in the hardware command registers and in DRM panel prepared/enabled flags. Backlight brightness persists in the DCS brightness register while the panel remains powered. Regulator and reset state is not otherwise cached. The driver mutates `dsi->mode_flags` for backlight writes by clearing and restoring LPM, and `sofef00_panel_on()` leaves LPM set for initialization.

## Dependencies and integration points
The driver uses DRM panel helpers, MIPI DSI multi-context helpers, regulator bulk APIs, GPIO descriptors, backlight registration, and OF matching for `samsung,sofef00` and `samsung,sofef00-ams628nw01`. It is a `mipi_dsi_driver` consumed by DSI host drivers and bridge/display pipelines.

## Risks
The legacy compatible aliases the same panel behavior, so board files using it must really match the AMS628NW01-style timings and commands. `sofef00_disable()` ignores the return from `sofef00_panel_off()`, hiding DSI command errors. Power-down does not assert reset, which may be intentional but leaves panel state dependent on regulator behavior. Brightness updates assume the panel accepts high-speed DCS writes after temporary LPM clearing.

## Test signals
Validation should check regulator order and reset pulse timing, DSI attach success, one 1080x2280 preferred mode, TE/display-control setup, display on/off transitions, brightness writes across 0..1023, suspend/resume behavior, and absence of detach errors on remove.
