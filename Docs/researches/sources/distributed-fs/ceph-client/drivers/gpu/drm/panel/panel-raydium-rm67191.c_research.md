# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raydium-rm67191.c

Purpose: DRM MIPI-DSI driver for Raydium RM67191 1080x1920 panels, with a long vendor manufacturer command set and an internal DCS backlight.

Important APIs, types, and functions: `struct cmd_set_entry` stores command/parameter pairs. `struct rad_panel` stores DRM panel, DSI, optional reset GPIO, backlight, regulator bulk data, supply count, and `prepared`. Important functions include `rad_panel_probe()`, `rad_init_regulators()`, `rad_panel_prepare()`, `rad_panel_enable()`, `rad_panel_disable()`, `rad_panel_unprepare()`, `rad_panel_push_cmd_list()`, `color_format_from_dsi_format()`, and backlight ops.

Control flow: probe allocates panel state, configures RGB888 video flags, optionally reads `video-mode`, requires `dsi-lanes`, registers reset GPIO and raw backlight, gets `v3p3` and `v1p8` supplies, adds the panel, then attaches. Prepare enables regulators and toggles reset, then marks `prepared`. Enable switches to LPM, sends manufacturer commands, returns to user command set, soft-resets, sets DSI mode, tearing, tear scanline, pixel format, exits sleep, turns display on, and enables backlight. Disable disables backlight, sends display-off and sleep-mode. Unprepare toggles reset specially to keep touch active, disables regulators, and clears `prepared`.

State and persistence: no durable state. `prepared` gates backlight get/set. DSI mode flags are changed during enable and backlight operations.

Dependencies and integration points: DRM panel, MIPI DSI DCS/generic writes, regulator bulk, GPIO, backlight, OF properties `video-mode` and `dsi-lanes`, and media bus formats. Compatible string is `raydium,rm67191`.

Risks and test signals: `dsi-lanes` is mandatory and can block probe. Backlight functions clear LPM but do not restore it, unlike other drivers. The reset release during unprepare is designed for touch-controller access and must be board-validated. Test all `video-mode` values, lane property errors, brightness before/after prepare, regulator rollback, touch behavior after display off, and mode/bus-format reporting.
