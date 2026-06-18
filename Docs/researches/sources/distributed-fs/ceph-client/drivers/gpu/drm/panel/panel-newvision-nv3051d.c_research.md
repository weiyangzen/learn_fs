## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-newvision-nv3051d.c

Purpose: This driver supports NewVision NV3051D-based MIPI-DSI handheld panels for Anbernic/Powkiddy devices. It provides a long vendor DCS initialization sequence, per-compatible mode lists and DSI mode flags, regulator/reset handling, external backlight binding, and shutdown/remove power-down support.

Important APIs, types, and functions: `struct nv3051d_panel_info` stores display modes, physical size, bus flags, and DSI mode flags. `struct panel_nv3051d` stores panel, reset GPIO, panel info, and `vdd` regulator. `panel_nv3051d_init_sequence()` writes multiple command pages for power, gamma, gate mapping, and interface settings. `panel_nv3051d_prepare()` enables `vdd`, toggles reset, runs init, exits sleep, waits 200 ms, and turns display on. `panel_nv3051d_unprepare()` sends display-off, sleep-in, asserts reset, and disables `vdd`. `panel_nv3051d_get_modes()` exposes all modes from the panel info, marking the mode preferred only when there is one mode. Shutdown calls unprepare and disable.

Control flow: Probe selects panel info by compatible, requests optional reset and `vdd`, sets DSI to four lanes RGB888 and info-specific flags, binds backlight, adds the panel, and attaches to DSI. Prepare performs power/reset/init/display-on. Remove first calls the shutdown helper before detaching and removing the panel.

State and persistence: Per-compatible panel info is persistent software state. Hardware state is fully programmed during prepare and lost on power-off. Multiple refresh-rate modes are supported for RG351V/RG353P variants, while RK2023 has one timing. Bus flags advertise DE low and negative-edge pixel drive.

Dependencies and integration points: The driver depends on DRM MIPI-DSI helpers, regulator/GPIO APIs, OF match data, external backlight lookup, and media bus flag definitions. It integrates with compatibles `anbernic,rg351v-panel`, `anbernic,rg353p-panel`, and `powkiddy,rk2023-panel`.

Risks: `panel_nv3051d_init_sequence()` uses `mipi_dsi_multi_context` but always returns 0, so accumulated DSI init errors are not propagated to prepare. The shutdown helper calls unprepare before disable even though no disable hook exists, and unprepare already sends display-off. The long vendor command table is undocumented and revision-sensitive. Error cleanup after init/sleep/display failures disables `vdd` but does not assert reset except in the unprepare path.

Test signals: Validate each compatible selects the correct mode list and DSI flags, all modes are reported with correct physical size and bus flags, DSI attach works, backlight binds, reset/power sequencing is correct, init command failures are visible in logs, and shutdown/remove leave the panel asleep and regulator disabled. Hardware tests should check 60/100/120 Hz modes where available.
