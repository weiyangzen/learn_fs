# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt36672e.c

Purpose: DRM MIPI-DSI panel driver for Novatek NT36672E panels, centered on a 1080x2408 60 Hz FHD+ configuration with vendor page-switch command programming.

Important APIs, types, and functions: `struct panel_desc` carries fixed mode, physical dimensions, DSI flags, format, lanes, panel name, and an init-sequence callback. `struct nt36672e_panel` keeps `drm_panel`, `mipi_dsi_device`, reset GPIO, three regulator supplies, and descriptor. Key functions include `nt36672e_1080x2408_60hz_init()`, `nt36672e_power_on()`, `nt36672e_power_off()`, `nt36672e_on()`, `nt36672e_off()`, panel prepare/unprepare, get-modes, probe, and remove.

Control flow: probe allocates panel state, validates match data, fills supplies from `vddi`, `avdd`, and `avee` with load hints, gets reset GPIO, configures DSI lanes/format/mode flags, binds OF backlight, marks `prepare_prev_first`, adds the panel, then attaches. Prepare enables all regulators, performs the documented out/in/out reset pulse, sends the descriptor init sequence in low-power mode, exits sleep, turns the display on, and waits. Unprepare sends display-off and sleep-mode with low-power cleared, then disables regulators and drives reset low.

State and persistence: no persistent state. Runtime state is descriptor data and current DSI mode flags. Error accumulation uses `mipi_dsi_multi_context`; prepare rolls power off if `nt36672e_on()` fails.

Dependencies and integration points: DRM panel, MIPI DSI multi-context helpers, regulator bulk, GPIO, OF, and panel backlight. Compatible string is `novatek,nt36672e`.

Risks and test signals: the long page-based vendor init sequence has no independent validation in the driver. `nt36672e_panel_unprepare()` ignores the return from `nt36672e_off()` and returns success after best-effort power-off, which can hide DSI failures. Test should cover regulator sequencing, reset polarity, DSI command error injection, 1080x2408 mode export, backlight phandle handling, attach failure cleanup, and suspend/resume.
