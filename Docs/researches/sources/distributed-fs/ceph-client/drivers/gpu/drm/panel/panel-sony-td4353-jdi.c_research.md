# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sony-td4353-jdi.c

## Purpose
This driver supports Sony Xperia XZ2/XZ2 Compact JDI TD4353-based MIPI DSI panels. It exposes one fixed 1080x2160 60 Hz mode and sequences panel and touch reset GPIOs together with three regulators.

## Important APIs, Types, And Functions
`struct sony_td4353_jdi` stores the DRM panel, DSI device, three supplies (`vddio`, `vsp`, `vsn`), panel reset GPIO, touch reset GPIO, and a type selector. `sony_td4353_jdi_on()` programs DCS address/window/TE/pixel-format/partial-row commands, exits sleep, starts memory write, and turns the display on. `sony_td4353_jdi_off()` turns display off, disables TE, and enters sleep. `sony_td4353_assert_reset_gpios()` drives both reset lines.

Panel functions are prepare, unprepare, and get_modes. Probe handles regulator/GPIO acquisition, DSI setup, backlight binding, `prepare_prev_first`, panel add, and DSI attach.

## Control Flow
Probe allocates the panel from OF match data, configures regulators and reset GPIOs, sets DSI to four RGB888 lanes with non-continuous clock, binds a backlight, adds the panel, and attaches to the DSI host. Prepare enables regulators, waits 100 ms, asserts both reset GPIOs, then runs the panel-on DCS sequence. If panel-on fails, it deasserts reset and disables regulators. Unprepare sends off/sleep commands, deasserts both resets, and disables regulators.

## State And Persistence
The only variant state is `type`; currently only `TYPE_TAMA_60HZ` is implemented. There is no persistent storage. The panel is fully initialized on each prepare. The driver mutates `dsi->mode_flags` to enter low-power mode during on and clears it during off.

## Dependencies And Integration Points
It uses DRM panel, MIPI DSI multi-context DCS helpers, regulator bulk APIs, GPIO descriptors, OF match data, and OF backlight. The compatible is `sony,td4353-jdi-tama`.

## Risks
Touch reset is coupled to panel reset, so sequencing errors can affect the touch controller. The mode selection enum has expansion comments but only one implemented path; unknown types return `-EINVAL` in get_modes. Width/height and timing are hard-coded. The on/off paths modify DSI mode flags and assume host tolerance for LPM transitions.

## Test Signals
Tests should confirm all three regulators, both reset GPIOs, DSI attach, backlight binding, fixed 1080x2160 mode, and clean rollback on panel-on failure. Hardware tests need display-on, display-off, and touch-controller survival across prepare/unprepare cycles.
