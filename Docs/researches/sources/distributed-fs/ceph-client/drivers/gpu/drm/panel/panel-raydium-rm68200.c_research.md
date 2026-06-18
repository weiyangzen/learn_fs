# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raydium-rm68200.c

Purpose: DRM MIPI-DSI panel driver for Raydium RM68200 720x1280 panels with manufacturer command-page initialization.

Important APIs, types, and functions: `struct rm68200` contains device, DRM panel, reset GPIO, and power regulator. DCS helpers `rm68200_dcs_write_buf()` and `rm68200_dcs_write_cmd()` wrap writes with ratelimited errors. Macros `dcs_write_seq` and `dcs_write_cmd_seq` encode normal and per-address command writes. Main functions are `rm68200_probe()`, `rm68200_prepare()`, `rm68200_unprepare()`, `rm68200_init_sequence()`, and `rm68200_get_modes()`.

Control flow: probe allocates the DSI panel, gets optional reset GPIO and `power` regulator, configures two-lane RGB888 DSI video burst LPM non-continuous clock, binds OF backlight, adds panel, and attaches. Prepare enables power, toggles reset if present, sends a multi-page manufacturer sequence, exits sleep, waits, turns display on, and waits. Unprepare sends display-off and sleep-mode with warnings on failure, waits, asserts reset if present, and disables power. Get-modes exports the single 720x1280 timing.

State and persistence: no persistent state. Initialization is replayed on each prepare. The helper write errors are logged but `rm68200_init_sequence()` itself does not accumulate or return failures.

Dependencies and integration points: DRM panel, MIPI DSI, regulator, optional GPIO, OF backlight, and fixed panel mode. Compatible string is `raydium,rm68200`.

Risks and test signals: command write failures during the manufacturer init sequence are not propagated, so prepare can continue to sleep-exit/display-on after failed setup. Optional reset and regulator sequencing are board-sensitive. Test DSI error handling, power failure rollback, 720x1280 mode export, backlight phandle, attach failure cleanup, and suspend/resume under command-failure injection.
