# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt36523.c

Purpose: DRM MIPI-DSI panel driver for Novatek NT36523-based panels used by Lenovo J606F and Xiaomi Elish BOE/CSOT variants. It supports both single-DSI and dual-DSI topologies and hides variant differences behind `struct panel_desc`.

Important APIs, types, and functions: `struct panel_info` stores the `drm_panel`, up to two `mipi_dsi_device` links, reset GPIO, `vddio`, orientation, and optional DCS backlight. `struct panel_desc` provides timings, DSI lanes/format/mode flags, device info for the second DSI, and the variant init callback. Main functions are `nt36523_probe()`, `nt36523_prepare()`, `nt36523_disable()`, `nt36523_unprepare()`, `nt36523_get_modes()`, and the variant command sequences `elish_boe_init_sequence()`, `elish_csot_init_sequence()`, and `j606f_boe_init_sequence()`.

Control flow: probe allocates the panel, gets `vddio` and reset GPIO, loads match data, optionally follows OF graph port 1 to register the secondary DSI device, reads panel orientation, sets `prepare_prev_first`, wires backlight, adds the panel, configures all DSI links, and attaches them. Prepare enables `vddio`, toggles reset, then runs the descriptor init sequence. Disable sends display-off and sleep-mode to each active DSI link; unprepare asserts reset and disables power.

State and persistence: no disk state. Runtime state is descriptor selection, DSI link array, orientation, and backlight object. The DCS brightness handlers temporarily clear `MIPI_DSI_MODE_LPM` and restore it after large-brightness transactions.

Dependencies and integration points: integrates with DRM panel, MIPI DSI, OF graph, regulator, GPIO, orientation, and backlight frameworks. Compatible strings are `lenovo,j606f-boe-nt36523w`, `xiaomi,elish-boe-nt36523`, and `xiaomi,elish-csot-nt36523`.

Risks and test signals: dual-DSI probe depends on valid graph wiring and secondary host availability. The magic vendor command sequences and reset timings are fragile. Attach failure after `drm_panel_add()` removes no panel in this function, so host attach paths deserve probe/remove stress testing. Test with DT binding validation, dual-DSI probe deferral, mode enumeration, suspend/resume, DCS backlight read/write, and panel orientation reporting.
