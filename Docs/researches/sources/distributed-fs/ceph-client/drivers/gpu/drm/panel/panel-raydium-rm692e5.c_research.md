# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raydium-rm692e5.c

Purpose: generated DRM MIPI-DSI driver for RM692E5-equipped AMOLED panels, specifically `fairphone,fp5-rm692e5-boe`, using DSC and a 1224x2700 90 Hz mode.

Important APIs, types, and functions: `struct rm692e5_panel` stores DRM panel, DSI device, `drm_dsc_config`, three regulators, and reset GPIO. Core functions are `rm692e5_probe()`, `rm692e5_prepare()`, `rm692e5_disable()`, `rm692e5_unprepare()`, `rm692e5_on()`, `rm692e5_get_modes()`, and DCS large-brightness backlight ops.

Control flow: probe sets supplies `vddio`, `dvdd`, and `vci`, gets reset GPIO, configures four-lane RGB888 DSI with no-EOT and non-continuous clock, sets `prepare_prev_first`, creates a raw 4095-level DCS backlight, adds the panel, assigns `dsi->dsc`, fills DSC 1.1 parameters, and attaches. Prepare enables regulators, toggles reset, sends vendor generic command pages, exits sleep/display-on, packs and sends DSC PPS, enables DSC compression, waits, switches to a command page to select 90 Hz, and returns accumulated errors. Disable leaves LPM, switches page 0, sends display-off and sleep-mode. Unprepare asserts reset and disables regulators.

State and persistence: no durable state. `ctx->dsc` is the key runtime configuration shared with the DSI host. Backlight get/set toggles LPM around DCS brightness transactions.

Dependencies and integration points: DRM panel, MIPI DSI, DRM DSC helpers, regulator bulk, GPIO, backlight, and OF match `fairphone,fp5-rm692e5-boe`.

Risks and test signals: the comment notes a TODO for `slice_per_pkt = 2`, so DSC host interoperability is a risk. The mode is 90 Hz and prepare explicitly selects 90 Hz with `0xbd = 0x05`. Test DSC PPS/compression, refresh-rate command, brightness read/write, regulator rollback on accumulated errors, attach failure, and suspend/resume.
