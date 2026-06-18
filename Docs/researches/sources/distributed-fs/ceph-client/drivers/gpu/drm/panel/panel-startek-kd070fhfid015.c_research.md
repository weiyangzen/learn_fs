# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-startek-kd070fhfid015.c

## Purpose
This driver supports the Startek KD070FHFID015 1200x1920 MIPI DSI panel. It sequences two regulators, reset and power-enable GPIOs, emits a short DCS/vendor init sequence, reports a fixed mode, and registers a DSI DCS backlight.

## Important APIs, Types, And Functions
`struct stk_panel` owns the fixed mode pointer, backlight, DRM panel base, enable/reset GPIOs, DSI device, and two supplies (`iovcc`, `power`). `stk_panel_init()` performs soft reset, sleep-out, interface register programming, brightness/control-display/pixel-format setup, and column/page address programming. `stk_panel_on()` sends display-on, while `stk_panel_off()` sends display-off and sleep-in.

Panel ops are prepare, unprepare, and get_modes. Backlight ops `dsi_dcs_bl_get_brightness()` and `dsi_dcs_bl_update_status()` temporarily clear and restore `MIPI_DSI_MODE_LPM` around DCS brightness commands.

## Control Flow
Probe configures DSI for four RGB888 lanes in video LPM mode, allocates state, adds the panel resources through `stk_panel_add()`, and attaches to the DSI host. Add fetches regulators/GPIOs, creates managed backlight, initializes the DRM panel, and adds it. Prepare asserts reset and enable low, enables IOVCC, waits, enables power, waits, drives enable/reset high, initializes the panel, and turns it on. Failure disables already-enabled regulators and restores GPIOs. Unprepare sends off/sleep, disables regulators, drives reset low, and drives enable high.

## State And Persistence
Runtime state is limited to hardware handles and the fixed mode pointer. Backlight brightness is maintained by the backlight core and panel DCS registers. No persistent storage exists.

## Dependencies And Integration Points
The driver integrates with DRM panel, MIPI DSI multi-context DCS helpers, regulators, GPIOs, backlight core, OF match, and module MIPI DSI registration. Its compatible is `startek,kd070fhfid015`.

## Risks
GPIO polarity is subtle: unprepare drives `enable_gpio` high after disabling supplies, while prepare initially drives it low and later high. If a board inverts this line differently, power sequencing can fail. Backlight operations mutate `dsi->mode_flags`; concurrent panel state changes would need host tolerance. There is no separate enable/disable panel op, so prepare includes display-on.

## Test Signals
Check regulator order, GPIO polarity, DSI attach, fixed 1200x1920 mode, brightness get/set, and failure rollback from each prepare stage. Hardware testing should include repeated full modesets and suspend/resume-like cycles.
