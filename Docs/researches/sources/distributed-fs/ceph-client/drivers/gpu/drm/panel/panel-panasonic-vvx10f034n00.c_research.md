# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-panasonic-vvx10f034n00.c

Purpose: DRM MIPI-DSI panel driver for Panasonic VVX10F034N00 / Novatek NT1397-based WUXGA 1920x1200 video-mode panels.

Important APIs, types, and functions: `struct wuxga_nt_panel` stores DRM panel, DSI device, `power` regulator, `earliest_wake`, and mode pointer. Main functions are `wuxga_nt_panel_probe()`, `wuxga_nt_panel_add()`, `wuxga_nt_panel_prepare()`, `wuxga_nt_panel_disable()`, `wuxga_nt_panel_unprepare()`, `wuxga_nt_panel_get_modes()`, and helper `wuxga_nt_panel_on()`.

Control flow: probe configures four-lane RGB888 DSI video mode with HSE, non-continuous clock, and LPM, allocates panel state, gets power/backlight, adds the panel, and attaches. Prepare enforces the panel’s minimum 500 ms off-time using `earliest_wake`, enables the regulator, waits 250 ms for command readiness, then calls `mipi_dsi_turn_on_peripheral()`. Disable shuts down the DSI peripheral. Unprepare disables power and records the next permitted wake time. Get-modes duplicates the fixed WUXGA timing and sets dimensions.

State and persistence: no durable state, but `earliest_wake` is important volatile timing state that survives between unprepare and the next prepare within the device lifetime.

Dependencies and integration points: DRM panel, MIPI DSI peripheral helpers, regulator, ktime, OF backlight, and OF match `panasonic,vvx10f034n00`.

Risks and test signals: the lack of reset pin makes off-time enforcement critical; tests should verify immediate re-enable waits correctly. The mode pointer field is set but `get_modes()` uses the static mode directly. Test DSI host support for turn-on/shutdown peripheral commands, regulator failures, wake-delay math, suspend/resume, and WUXGA mode export.
