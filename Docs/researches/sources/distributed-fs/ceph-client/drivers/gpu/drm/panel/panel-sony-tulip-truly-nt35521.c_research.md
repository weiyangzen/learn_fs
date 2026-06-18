# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sony-tulip-truly-nt35521.c

## Purpose
This DRM MIPI DSI panel driver supports the Sony Tulip Truly NT35521 panel. It provides a fixed 720x1280 mode, lengthy vendor initialization sequence, DSI brightness backlight, and a separate GPIO-controlled backlight enable line.

## Important APIs, Types, And Functions
`struct truly_nt35521` stores the DRM panel, DSI device, two regulators (`positive5`, `negative5`), reset GPIO, and backlight-enable GPIO. `nt35521_switch_page()` wraps the page unlock/select command. `truly_nt35521_on()` emits the multi-page vendor command sequence, exits sleep, waits, turns display on, and writes control display. `truly_nt35521_off()` turns display off and enters sleep.

Panel ops are prepare, unprepare, enable, disable, and get_modes. Backlight ops use `mipi_dsi_dcs_set_display_brightness()` and `mipi_dsi_dcs_get_display_brightness()`.

## Control Flow
Probe allocates the panel, gets positive/negative regulators, reset and backlight GPIOs, configures four-lane RGB888 video burst DSI with HSE, no EOT, and non-continuous clock, creates a managed raw backlight, adds the panel, and attaches to the DSI host. Prepare enables regulators, performs the reset sequence, then sends the large vendor init. On failure it logs and asserts reset but does not explicitly disable regulators in the failure branch. Enable drives the backlight GPIO high; disable drives it low. Unprepare sends off/sleep, asserts reset, and disables regulators.

## State And Persistence
There is no persistent storage. Brightness state is held by the backlight core and mirrored to the panel over DCS. The panel is reinitialized from scratch on prepare. DSI mode flags are switched into LPM for initialization and cleared in off.

## Dependencies And Integration Points
The driver uses DRM panel, MIPI DSI multi-context helpers, regulator bulk APIs, GPIO, managed backlight registration, and OF match binding. It is registered as a MIPI DSI driver under compatible `sony,tulip-truly-nt35521`.

## Risks
The vendor command sequence is long and opaque; small changes are high risk. The reset helper sets reset high twice before low, which likely reflects active-low hardware but should be checked against bindings and board schematics. Prepare failure after regulators are enabled leaves cleanup mostly to later paths unless the caller unprepares. Brightness get returns only the low 8 bits.

## Test Signals
Validation should cover DSI attach, regulator enable/disable, reset polarity, GPIO backlight enable, DCS brightness set/get, fixed mode reporting, and repeated prepare/enable/disable/unprepare. A panel-init failure injection or host error path is useful to inspect regulator cleanup behavior.
