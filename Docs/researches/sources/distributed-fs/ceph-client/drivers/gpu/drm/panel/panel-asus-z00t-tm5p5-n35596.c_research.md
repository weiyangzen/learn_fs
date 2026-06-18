# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-asus-z00t-tm5p5-n35596.c

Purpose: MIPI DSI DRM panel driver for the ASUS Z00T TM5P5 NT35596 1080x1920 video-mode panel.

Important APIs/types/functions: `struct tm5p5_nt35596`, reset/on/off helpers, prepare/unprepare, fixed mode, panel funcs, DCS backlight ops, DSI probe/remove, and OF match table.

Control flow: Probe gets `vdd`/`vddio` regulators, reset GPIO, configures four-lane RGB888 video burst DSI with low-power commands, creates a DCS backlight, registers the panel, and attaches to the DSI host. Prepare enables regulators, toggles reset, and sends a long vendor command sequence ending in sleep-out/display-on. Unprepare sends display-off/sleep-in commands, drops reset, and disables regulators. Backlight ops temporarily leave LPM to set/get DCS brightness.

State and persistence: Driver state holds panel, DSI device, two regulators, and reset GPIO. Brightness lives in panel DCS registers and backlight core state.

Dependencies and integration: Depends on DRM MIPI DSI, GPIO, regulators, backlight class, OF, and DRM panel mode helpers.

Risks: Command sequence failures accumulate through `mipi_dsi_multi_context`; prepare must clean up power on any error. Backlight get returns low 8 bits despite DCS 16-bit storage. DSI mode flag toggling around brightness is stateful.

Test signals: DSI attach/probe on matching DT, regulator/reset sequencing, prepare failure cleanup, display mode timing, DCS brightness set/get, and remove detach error logging.
