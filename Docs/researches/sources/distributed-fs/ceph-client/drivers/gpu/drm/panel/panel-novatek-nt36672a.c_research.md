# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt36672a.c

Purpose: descriptor-driven DRM MIPI-DSI driver for Novatek NT36672A-based Tianma FHD+ video panels, with comments noting use in some Xiaomi/Poco F1 variants and possible extension to related NT37762A panels.

Important APIs, types, and functions: `struct nt36672a_panel_desc` carries the display mode, physical size, DSI configuration, and split on/off command arrays. `struct nt36672a_panel` stores the `drm_panel`, DSI link, descriptor, regulator bulk data, and reset GPIO. Core functions are `nt36672a_panel_probe()`, `nt36672a_panel_add()`, `nt36672a_panel_prepare()`, `nt36672a_panel_unprepare()`, `nt36672a_panel_power_on()`, `nt36672a_panel_power_off()`, `nt36672a_send_cmds()`, and `nt36672a_panel_get_modes()`.

Control flow: probe allocates panel state, fetches OF match data, copies descriptor DSI mode flags/format/lanes into the DSI device, registers state with `mipi_dsi_set_drvdata()`, calls add, then attaches to the host. Add configures three regulators (`vddio`, `vddpos`, `vddneg`) with load hints, gets reset GPIO, binds an OF backlight, and adds the DRM panel. Prepare enables regulators, applies a long reset sequence, sends first init commands, exits sleep, enables display, sends trailing commands, then waits. Unprepare sends panel off commands, forces display-off and sleep-mode even after prior command errors, waits DCS-specified delays, then powers off.

State and persistence: state is fully volatile. The descriptor and regulator arrays define all panel behavior; no cached mode changes or persisted settings exist.

Dependencies and integration points: DRM panel, MIPI DSI, regulator bulk, GPIO, OF match data, and DRM panel backlight. The sole compatible is `tianma,fhd-video`.

Risks and test signals: reset delays are intentionally inflated to avoid white-screen failures, so timing changes are risky. Command arrays use fixed two-byte DCS buffers; extending to wider commands requires changing `struct nt36672a_panel_cmd`. Probe cleanup detaches/removes on attach failure, but regulator rollback on prepare command failure only resets GPIO, relying on later unprepare. Test probe deferral, regulator failures, DSI attach/detach, mode timing at 1080x2246, backlight acquisition, and suspend/resume with repeated prepare/unprepare cycles.
