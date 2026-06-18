## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-mantix-mlaf057we51.c

Purpose: This driver supports Mantix MLAF057WE51-X and YS YS57PSS36BH5GQ 720x1440 MIPI-DSI panels. It manages three power rails, reset and touch-reset GPIOs, a short vendor initialization sequence, fixed mode selection by compatible, and external backlight binding.

Important APIs, types, and functions: `struct mantix` stores the panel, device, reset GPIO, `mantix,tp-rstn` GPIO, `avdd`, `avee`, `vddi` regulators, and selected default mode. `mantix_init_sequence()` sends vendor generic commands (`OTP_STOP_RELOAD_MIPI`, `INT_CANCEL`, `SPI_FINISH`, VCOM). `mantix_prepare()` enables `vddi`, `avdd`, and `avee` with datasheet delays, then releases touch and panel reset. `mantix_enable()` sends init sequence, exits sleep, and turns display on. `mantix_disable()` turns display off and enters sleep. `mantix_unprepare()` disables rails in reverse-ish order and asserts touch reset and panel reset. `mantix_get_modes()` duplicates the compatible-selected mode and sets RGB888 bus format.

Control flow: OF match data selects between two timing structures. Probe requests GPIOs/regulators/backlight, fixes DSI to four lanes RGB888 video burst sync-pulse LPM, adds the panel, and attaches. Runtime prepare performs only power/reset sequencing; enable performs DSI programming and display-on. Disable and unprepare split DSI sleep from power-down.

State and persistence: The selected mode pointer and resource handles are the only software state. Panel register state is written on each enable. The touch reset GPIO is controlled together with panel reset, implying a board-level dependency between display and touch controller reset state.

Dependencies and integration points: Dependencies include MIPI-DSI multi-context helpers, DRM panel/mode APIs, media bus format, GPIO/regulator/backlight APIs, and OF match data. It exposes compatible strings for both Mantix and YS panels and logs panel readiness after DSI attach.

Risks: Error handling in `mantix_prepare()` does not disable already-enabled regulators if enabling a later rail fails, so failed `avdd`/`avee` paths can leak power. The vendor init sequence is short but undocumented. Touch reset is a non-standard panel GPIO name and may couple unrelated device state to panel lifecycle. The compatible-specific modes are very similar but differ in vertical porch/clock; wrong match data can produce subtle refresh issues.

Test signals: Verify both compatibles select the correct mode, DSI attach succeeds, bus format is RGB888, external backlight binds, power rails are enabled/disabled in expected order, touch and panel reset signals are correct, and enable/disable cycles produce no accumulated DSI errors. Error injection should focus on regulator enable cleanup.
