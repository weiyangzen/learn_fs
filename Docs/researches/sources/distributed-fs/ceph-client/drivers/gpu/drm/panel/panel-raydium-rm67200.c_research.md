# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raydium-rm67200.c

Purpose: descriptor-driven DRM MIPI-DSI driver for Raydium RM67200-equipped panels, currently the Wanchanglong W552793BAA 1080x1920 panel.

Important APIs, types, and functions: `struct raydium_rm67200_panel_info` contains the fixed mode, regulator list, regulator count, and setup callback. `struct raydium_rm67200` stores DRM panel, panel info, DSI, reset GPIO, and supplies. Key functions are `raydium_rm67200_probe()`, `raydium_rm67200_prepare()`, `raydium_rm67200_disable()`, `raydium_rm67200_unprepare()`, `raydium_rm67200_get_modes()`, and the long `w552793baa_setup()` sequence.

Control flow: probe allocates panel state, gets match data, obtains the descriptor’s supplies (`vdd`, `iovcc`, `vsp`, `vsn`), optionally gets reset GPIO, configures four-lane RGB888 DSI video burst LPM, marks `prepare_prev_first`, binds OF backlight, adds the panel, and attaches. Prepare enables supplies, resets, waits, runs the panel setup command sequence through generic writes, exits sleep, turns display on, and waits. Disable sends display-off and sleep-mode. Unprepare asserts reset, disables supplies, and waits.

State and persistence: no persistent state. Runtime behavior is entirely descriptor-driven, so additional RM67200 variants can be added by new `panel_info` records.

Dependencies and integration points: DRM panel, MIPI DSI multi-context generic writes, regulator bulk const API, optional GPIO, OF backlight, fixed-mode helper, and device property match data. Compatible string is `wanchanglong,w552793baa`.

Risks and test signals: `raydium_rm67200_prepare()` ignores `mctx.accum_err` and returns 0 even if setup or DCS commands fail, so DSI error propagation is weak. Optional reset handling is partly guarded in reset but unprepare unconditionally calls `gpiod_set_value_cansleep(ctx->reset_gpio, 1)`, which must be checked for NULL safety expectations. Test command-error injection, optional reset absent, regulator sequencing, backlight binding, fixed mode, and suspend/resume.
