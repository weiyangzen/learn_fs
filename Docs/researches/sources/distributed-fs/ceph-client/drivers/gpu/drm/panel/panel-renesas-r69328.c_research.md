# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-renesas-r69328.c

Purpose: DRM MIPI-DSI driver for Renesas R69328-based JDI DX12D100VM0EAA-compatible 720x1280 panels.

Important APIs, types, and functions: `struct renesas_r69328` holds the DRM panel, DSI device, `vdd` and `vddio` regulators, and optional reset GPIO. Main functions are `renesas_r69328_probe()`, `renesas_r69328_prepare()`, `renesas_r69328_enable()`, `renesas_r69328_disable()`, `renesas_r69328_unprepare()`, `renesas_r69328_reset()`, and `renesas_r69328_get_modes()`.

Control flow: probe allocates the panel, gets `vdd` and `vddio`, gets optional reset GPIO, configures four-lane RGB888 video sync-pulse non-continuous LPM DSI, binds OF backlight, adds the panel, and attaches using devm. Prepare enables `vdd`, waits, enables `vddio`, waits, then toggles reset. Enable sets address mode and 24-bit pixel format, exits sleep, disables manufacturer access protection, writes power and three gamma tables, re-enables protection, turns display on, and waits. Disable sends display-off, waits, and enters sleep. Unprepare asserts reset, waits, then disables `vddio` and `vdd`.

State and persistence: no persistent state and no configurable runtime state beyond acquired resources and fixed mode.

Dependencies and integration points: DRM panel, MIPI DSI multi-context helpers, regulators, optional GPIO, OF backlight, and fixed-mode helper. Compatible string is `jdi,dx12d100vm0eaa`.

Risks and test signals: if enabling `vddio` fails after `vdd` is enabled, the code returns without disabling `vdd`. Vendor power/gamma tables are hard-coded. Test regulator failure rollback, optional reset absence, DSI command error propagation through `ctx.accum_err`, 720x1280 mode export, backlight phandle, attach failure cleanup, and suspend/resume timing.
