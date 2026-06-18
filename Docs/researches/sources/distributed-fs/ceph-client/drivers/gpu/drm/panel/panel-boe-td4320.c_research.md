# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-td4320.c

Purpose: MIPI DSI video-mode panel driver for BOE TD4320 1080x2340 panels, generated from vendor DSI data.

Important APIs/types/functions: `struct boe_td4320`, static supply table, reset/on/off helpers, prepare/unprepare, fixed display mode, panel funcs, probe/remove, and OF match.

Control flow: Probe obtains constant supplies `iovcc`, `vsn`, and `vsp`, reset GPIO, configures four-lane RGB888 video burst DSI with non-continuous clock, sets `prepare_prev_first`, attaches OF backlight, registers panel, and attaches DSI. Prepare enables supplies, resets, sends vendor generic/DCS command sequence including brightness/control-display/sleep-out/display-on, and cleans up on failure. Unprepare sends display-off/sleep-in and powers down.

State and persistence: State stores panel, DSI, supply array, and reset GPIO. Brightness is initialized by command sequence but external backlight is managed through OF panel backlight.

Dependencies and integration: Uses DRM MIPI DSI multi-context helpers, regulator bulk const API, GPIO, DRM fixed mode helper, panel backlight, and OF.

Risks: Generated command sequences are opaque and panel-specific. `boe_td4320_off` returns an error but unprepare only logs it and continues power-down. DSI LPM flag is toggled inside on/off and may interact with host state.

Test signals: Probe with `boe,td4320`, supply/reset sequencing, DSI command failure cleanup, fixed mode helper output, backlight phandle attachment, and remove detach handling.
