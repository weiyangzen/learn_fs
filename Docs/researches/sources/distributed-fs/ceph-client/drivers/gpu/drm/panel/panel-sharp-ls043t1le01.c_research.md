# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sharp-ls043t1le01.c

## Purpose
Implements a Sharp LS043T1LE01 qHD panel using a Novatek NT35565-style MIPI DSI controller. The driver manages one `avdd` regulator, reset GPIO, panel init/on/off DCS commands, fixed 540x960 mode reporting, and optional OF backlight integration.

## Important APIs, types, and functions
- `struct sharp_nt_panel` stores the DRM panel, DSI device, regulator, and reset GPIO.
- `sharp_nt_panel_init()` exits sleep, waits 120 ms, selects Novatek two-lane operation, and sets both MCU and RGB interfaces to 24 bpp.
- `sharp_nt_panel_on()` sends DCS display on in LPM.
- `sharp_nt_panel_off()` clears LPM and sends display off plus enter sleep.
- `sharp_nt_panel_prepare()` enables power, toggles reset, initializes the panel, and turns it on.
- `sharp_nt_panel_probe()` configures two-lane RGB888 video mode with sync pulse, HSE, non-continuous clock, and no EOT packet.

## Control flow
Probe allocates the context with `devm_kzalloc()`, sets DSI drvdata, records the DSI device, adds the DRM panel through `sharp_nt_panel_add()`, then attaches to the DSI host. Add obtains the `avdd` regulator, gets reset GPIO, initializes the DRM panel manually with `drm_panel_init()`, sets `prepare_prev_first`, resolves backlight, and adds the panel. Prepare enables the regulator, waits, performs a high-low-high reset pulse, runs init, then display-on. Unprepare sends off/sleep commands, disables the regulator, and drives reset low if present.

## State and persistence
State is limited to the DSI device, regulator, reset line, and DRM panel flags. Panel controller state includes two-lane mode, pixel format, sleep/display state, and any backlight state managed externally. The DSI mode flags are modified in init/on/off to choose LPM or high-speed command behavior.

## Dependencies and integration points
The file uses DRM panel, MIPI DSI helpers, regulator and GPIO frameworks, OF matching for `sharp,ls043t1le01-qhd`, and optional backlight lookup. It integrates as a normal `mipi_dsi_driver`.

## Risks
The reset GPIO is requested as mandatory but errors are converted into a NULL reset GPIO after logging, which may allow probe on hardware that will not reliably reset. Off commands return errors and abort unprepare before regulator disable, so a DSI failure can leave power on. The mode has no explicit physical mode type flags in the static struct; get_modes duplicates and publishes it without marking preferred.

## Test signals
Useful tests include DSI attach, correct two-lane host configuration, reset waveform, successful sleep-out and display-on, one 540x960 mode with 54x95 mm dimensions, backlight lookup behavior, and regulator disable on unprepare.
