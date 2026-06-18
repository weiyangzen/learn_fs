# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-osd-osd101t2587-53ts.c

Purpose: small DRM MIPI-DSI video panel driver for the OSD Displays OSD101T2587-53TS 10.1-inch 1920x1200 panel.

Important APIs, types, and functions: `struct osd101t2587_panel` holds a DRM panel, DSI device, `power` regulator, and default mode pointer. Key functions are `osd101t2587_panel_probe()`, `osd101t2587_panel_add()`, `osd101t2587_panel_prepare()`, `osd101t2587_panel_enable()`, `osd101t2587_panel_disable()`, `osd101t2587_panel_unprepare()`, and `osd101t2587_panel_get_modes()`.

Control flow: probe matches the OF node to retrieve mode data, configures four-lane RGB888 DSI video burst/sync-pulse/no-EOT flags, allocates panel state, stores the default mode, adds the panel, and attaches to the DSI host. Prepare enables the regulator. Enable calls `mipi_dsi_turn_on_peripheral()`. Disable calls `mipi_dsi_shutdown_peripheral()`. Unprepare disables the regulator. Get-modes duplicates the fixed WUXGA timing and sets physical dimensions to 217 mm by 136 mm.

State and persistence: no persistent state and minimal runtime state. The mode pointer is set once from OF match data.

Dependencies and integration points: DRM panel, MIPI DSI peripheral helpers, regulator framework, OF match table, and optional OF backlight. Compatible string is `osddisplays,osd101t2587-53ts`.

Risks and test signals: the driver has no reset GPIO or custom command sequence, relying on generic peripheral on/off behavior. It does not set explicit mode type preferred in `get_modes()`. Attach failure removes the panel but no DSI detach path is needed because attach failed. Test regulator enable/disable, generic DSI peripheral commands on the target host, WUXGA timing, backlight phandle handling, and repeated enable/disable cycles.
