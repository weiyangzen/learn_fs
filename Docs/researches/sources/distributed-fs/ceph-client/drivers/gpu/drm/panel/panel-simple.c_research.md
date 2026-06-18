# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-simple.c

## Purpose
Provides the generic DRM "simple panel" driver for panels that need only a power rail, optional enable GPIO, optional backlight, optional DDC, and static mode/timing metadata. Most of the file is a large descriptor registry mapping OF compatibles to `panel_desc` or `panel_desc_dsi` data for DPI, LVDS, and a small set of DSI panels.

## Important APIs, types, and functions
- `struct panel_desc` describes fixed `drm_display_mode` entries or bounded `display_timing` entries, bpc, physical size, delays, media bus format, bus flags, and connector type.
- `struct panel_desc_dsi` wraps `panel_desc` with DSI mode flags, pixel format, and lane count.
- `struct panel_simple` stores the DRM panel, descriptor, power regulator, optional DDC adapter, enable GPIO, cached EDID, override mode, orientation, and last unprepare timestamp.
- Mode helpers include `panel_simple_get_timings_modes()`, `panel_simple_get_display_modes()`, `panel_simple_get_non_edid_modes()`, `panel_simple_get_modes()`, and `panel_simple_get_timings()`.
- Power helpers include `panel_simple_suspend()`, `panel_simple_resume()`, `panel_simple_prepare()`, `panel_simple_unprepare()`, `panel_simple_enable()`, and `panel_simple_disable()`.
- Probe helpers include `panel_dpi_probe()`, `panel_simple_parse_panel_timing_node()`, `panel_simple_override_nondefault_lvds_datamapping()`, `panel_simple_get_desc()`, and `panel_simple_probe()`.
- Registration is split between `panel_simple_platform_driver` and, when enabled, `panel_simple_dsi_driver`, both installed from `panel_simple_init()`.

## Control flow
For platform devices, OF match data normally supplies a descriptor; the special `panel-dpi` compatible builds one from the `panel-timing` node. For DSI devices, match data supplies a `panel_desc_dsi`, and the DSI probe later copies flags/format/lanes to the MIPI DSI device before attach. Common probe validates connector type and bus fields, allocates the DRM panel, gets the `power` regulator and optional `enable` GPIO, reads panel orientation, optionally resolves `ddc-i2c-bus`, accepts a DT timing override only when it fits descriptor timing bounds, optionally overrides LVDS data mapping, enables runtime PM with autosuspend, resolves backlight, and adds the panel.

Prepare and unprepare are runtime-PM wrappers. Runtime resume waits for any required minimum unprepare interval, enables the regulator, asserts the enable GPIO, and waits the descriptor prepare delay. Runtime suspend deasserts enable, disables power, records `unprepared_time`, and frees cached EDID. Enable/disable only wait descriptor delays for valid frame appearance/disappearance. Mode enumeration reads EDID through DDC while temporarily runtime-resuming the panel, then adds static or override modes and applies display info and orientation.

## State and persistence
Persistent software state includes descriptor pointer, optional cached EDID, override mode from DT, orientation, and `unprepared_time` used to enforce power-off minimums across prepare cycles. Hardware state is limited to the power regulator and enable GPIO because this driver intentionally avoids panel-specific command sequences. The descriptor tables are compile-time static and encode the supported panel database.

## Dependencies and integration points
The driver depends on DRM panel, EDID, OF, MIPI DSI, runtime PM, regulators, GPIO, I2C/DDC, videomode/display timing, LVDS data-mapping helpers, and media bus format definitions. It integrates with many board device trees via the large platform `of_device_id` table, with DSI panels through `dsi_of_match`, and with display controllers through `drm_panel` mode, timing, bus format, bus flag, backlight, orientation, and connector-type APIs.

## Risks
Descriptor correctness is the main risk: wrong timing, bus flags, bus format, bpc, connector type, or delays can cause blank panels or subtle signal integrity problems. The common driver warns for likely LVDS/DPI/DSI descriptor mistakes but still falls back in some cases for compatibility. EDID reads require powering the panel briefly and rely on runtime PM balance. Shutdown contains explicit disable/unprepare calls as compatibility glue for older modeset drivers and warns not to copy that pattern. DSI error cleanup in `panel_simple_dsi_probe()` removes the panel but relies on common remove paths for other resources.

## Test signals
Test signals include successful probe for representative platform, `panel-dpi`, LVDS with `data-mapping`, DDC/EDID, and DSI descriptors; correct runtime PM prepare/unprepare balance; expected modes from EDID plus static descriptors; accepted and rejected DT timing overrides; correct orientation reporting; backlight discovery; and clean module init/exit registration of both platform and DSI drivers.
