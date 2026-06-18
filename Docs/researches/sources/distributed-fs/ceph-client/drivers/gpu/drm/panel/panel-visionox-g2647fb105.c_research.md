# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-visionox-g2647fb105.c

## Purpose
This MIPI DSI driver supports the Visionox G2647FB105 AMOLED panel. It provides a fixed 1080x2340 mode, sequences four regulators and reset, sends a short vendor initialization sequence, and registers a high-range DCS backlight.

## Important APIs, Types, And Functions
`struct visionox_g2647fb105` holds the DRM panel, DSI device, reset GPIO, and managed regulator bulk array. The regulator list is `vdd3p3`, `vddio`, `vsn`, and `vsp`. `visionox_g2647fb105_reset()` toggles reset. `visionox_g2647fb105_on()` writes vendor pages/registers, enables TE, sets brightness to zero, exits sleep, waits 100 ms, and turns display on. `visionox_g2647fb105_off()` sends display-off and sleep-in.

Panel ops are prepare, unprepare, and get_modes. Backlight update uses `mipi_dsi_dcs_set_display_brightness_large()` with a 2047 maximum.

## Control Flow
Probe allocates state, gets constant regulator bulk data, gets reset GPIO default high, configures four-lane RGB888 DSI in burst/non-continuous/LPM mode, initializes the DRM panel, creates a managed raw backlight, adds the panel, and attaches with `devm_mipi_dsi_attach()`. Prepare enables all regulators, resets, and runs the on sequence. Unprepare runs off, asserts reset high, and disables regulators. Backlight update temporarily clears LPM, writes large brightness, then restores LPM.

## State And Persistence
No persistent state is stored. Brightness is managed by backlight core; the init sequence sets brightness to zero before display-on, while later updates apply user brightness. Regulator handles are managed through a bulk pointer allocated by the devm helper.

## Dependencies And Integration Points
It depends on DRM panel, MIPI DSI multi-context helpers, regulator bulk const API, GPIO, managed backlight registration, DCS large brightness helper, and managed DSI attach. Compatible is `visionox,g2647fb105`.

## Risks
Prepare failure after regulators are enabled does not explicitly disable them if `visionox_g2647fb105_on()` fails. Backlight updates mutate DSI LPM flags, which can race conceptually with panel lifecycle unless higher layers serialize calls. The file sets `prepare_prev_first` before and after `drm_panel_init()`, with the first assignment occurring before panel init and therefore not useful. Vendor command meanings are mostly opaque.

## Test Signals
Validate regulator cleanup paths, reset polarity, DSI attach, fixed mode dimensions, TE enable, brightness range and large-brightness command, and repeated prepare/unprepare. A host-command failure test is useful for regulator leak detection.
