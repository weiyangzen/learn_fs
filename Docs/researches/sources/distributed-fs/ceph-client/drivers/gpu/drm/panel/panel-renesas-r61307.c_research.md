# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-renesas-r61307.c

Purpose: DRM MIPI-DSI driver for Renesas R61307-based 768x1024 panels, matched to HIT and KOE TX13D100VM0EAA-compatible panels.

Important APIs, types, and functions: `struct renesas_r61307` stores DRM panel, DSI device, `vcc` and `iovcc` regulators, optional reset GPIO, and configuration booleans for contrast/inversion plus gamma index. `gamma_setting` contains selectable gamma tables. Main functions are `renesas_r61307_probe()`, `renesas_r61307_prepare()`, `renesas_r61307_enable()`, `renesas_r61307_disable()`, `renesas_r61307_unprepare()`, and get-modes.

Control flow: probe allocates state, gets regulators and optional reset GPIO, reads optional device properties `renesas,column-inversion`, `renesas,contrast`, and `renesas,gamma`, configures four-lane RGB888 video sync-pulse non-continuous LPM DSI, binds OF backlight, adds panel, and attaches with devm. Prepare enables `vcc`, then `iovcc`, waits between rails, and resets. Enable exits sleep, sets address mode and pixel format, disables manufacturer command protection, optionally programs contrast/gamma/inversion, re-enables protection, then turns display on. Disable sends display-off and sleep. Unprepare waits, asserts reset, then disables `iovcc` and `vcc`.

State and persistence: no durable state. Probe-time device properties persist in memory as booleans and gamma index, controlling enable-time command choices.

Dependencies and integration points: DRM panel, MIPI DSI multi-context writes, regulator framework, GPIO, generic device properties, OF backlight, and fixed-mode helper. Compatible strings are `hit,tx13d100vm0eaa` and `koe,tx13d100vm0eaa`.

Risks and test signals: `renesas,gamma` is not bounds-checked before indexing `gamma_setting`, so invalid DT values can read past the table. If `iovcc` enable fails, `vcc` is left enabled. Test property validation, regulator failure rollback, gamma variants, inversion/contrast branches, mode export, and suspend/resume.
