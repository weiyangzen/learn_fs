# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sharp-ls060t1sx01.c

## Purpose
Implements a Sharp LS060T1SX01 1080p MIPI DSI video-mode panel. It manages four named regulators with strict sequencing, reset GPIO, a short panel-on/off DCS sequence, fixed 1080x1920 mode reporting, and external backlight integration.

## Important APIs, types, and functions
- `struct sharp_ls060` stores DRM panel, DSI device, `vddi`, `vddh`, `avdd`, `avee` regulators, and reset GPIO.
- `sharp_ls060_reset()` performs a low-high-low reset pulse with 10 ms gaps.
- `sharp_ls060_on()` enables LPM, writes a vendor register `0xbb`, starts memory write, exits sleep, waits, turns display on, and waits again.
- `sharp_ls060_off()` clears LPM, sends display off, waits a few milliseconds, enters sleep, and waits 121 ms.
- `sharp_ls060_prepare()` enables regulators in order with delays and unwinds them on errors.
- `sharp_ls060_probe()` configures four-lane RGB888 DSI video burst with no EOT and non-continuous clock.

## Control flow
Probe allocates the panel, gets all four regulators and reset GPIO, sets DSI drvdata and link parameters, resolves an OF backlight, adds the panel, and attaches to the DSI host. Prepare enables `vddi`, then `avdd`, delays, enables `avee`, delays, enables `vddh`, delays, resets the panel, then sends the on sequence. If any later stage fails, it disables already-enabled rails in reverse-ish order and asserts reset. Unprepare sends off/sleep commands, disables `vddh`, waits, disables `avee` and `avdd`, asserts reset, then disables `vddi`.

## State and persistence
Persistent state is mostly physical: regulator enable state, reset GPIO level, DSI controller mode flags, and panel sleep/display state. Brightness is external through `drm_panel_of_backlight()`. The fixed mode and dimensions are static.

## Dependencies and integration points
The driver depends on DRM panel APIs, MIPI DSI, regulator framework, GPIO, OF backlight, and compatible `sharp,ls060t1sx01`. It integrates into DSI host pipelines as a video-mode DSI panel.

## Risks
Power sequencing is rail-order sensitive; incorrect device tree supplies or delays can damage bring-up reliability. `sharp_ls060_off()` has no return value and ignores accumulated DSI errors, so unprepare always continues. The on sequence writes `MIPI_DCS_WRITE_MEMORY_START` before sleep-out, which is panel-specific and should not be generalized. Reset polarity must match the GPIO descriptor.

## Test signals
Check successful rail acquisition, ordered rail transitions with delays, reset pulse timing, DSI attach, one preferred 1080x1920 mode with 75x132 mm dimensions, visible sleep-out/display-on, working external backlight, and clean regulator unwind on forced command or attach failures.
