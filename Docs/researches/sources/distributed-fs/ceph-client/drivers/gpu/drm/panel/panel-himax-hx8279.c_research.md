<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx8279.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx8279.c

### Purpose

`panel-himax-hx8279.c` is a descriptor-driven DRM/MIPI-DSI driver for panels built around the Himax HX8279 display controller. It supports single-DSI and dual-DSI wiring, validates controller configuration data before writing potentially persistent/OTP-like registers, programs MIPI timing, GOA mux/config/timing, analog and digital gamma, voltage settings, advanced engineer-page controls, and exposes fixed modes for supported Aoly and Startek panels.

### Important APIs, types, and functions

`struct hx8279` stores the DRM panel, up to two DSI devices, `vdd`/`iovcc` regulator bulk entries, enable/reset GPIOs, descriptor, cached `last_page`, and skip flags derived from validation. Descriptor types include `struct hx8279_panel_mode`, `struct hx8279_goa_mux`, `struct hx8279_analog_gamma`, `struct hx8279_digital_gamma`, and `struct hx8279_panel_desc`. Register macros define page selection and fields for pages 0 through 12.

Programming helpers are `hx8279_set_page()`, `hx8279_set_module_config()`, `hx8279_set_gmux()`, `hx8279_set_analog_gamma()`, `hx8279_set_goa_timing()`, `hx8279_set_goa_cfg()`, `hx8279_set_mipi_cfg()`, `hx8279_set_adv_cfg()`, and `hx8279_set_digital_gamma()`. Validation helpers are `hx8279_init_vregs()`, `hx8279_check_gmux_config()`, `hx8279_check_goa_config()`, `hx8279_check_dig_gamma()`, and `hx8279_check_params()`. DRM callbacks are `hx8279_prepare()`, `hx8279_enable()`, `hx8279_disable()`, `hx8279_unprepare()`, and `hx8279_get_modes()`.

### Control flow

Probe allocates the panel, obtains and voltage-checks `vdd` and `iovcc`, reads match data, validates descriptor values, gets optional enable and required reset GPIOs, optionally discovers a secondary DSI host from graph port 1, registers a managed DSI device for the right side, binds backlight, adds the DRM panel, configures every present DSI device with descriptor lane count, RGB888 format, non-continuous clock and LPM, adds video sync-pulse flags for video modes, and attaches both devices. `prepare()` enables regulators, asserts enable and reset with short delays, sets LPM on both DSI devices, calls `hx8279_on()` to program pages 5, 1, 2, 3, 0, 6, and 7-12, exits sleep, and waits 130 ms. `enable()` sends display-on; `disable()` sends display-off; `unprepare()` enters sleep, waits, clears LPM, resets/powers off, and disables regulators.

### State and persistence behavior

`last_page` avoids redundant page-select writes during one programming pass and persists until the device is reinitialized. Skip flags are computed at probe to avoid programming absent voltage, GOA, MIPI timing, or GOA timing blocks. The descriptor data is immutable static match data. Hardware register programming is volatile in normal operation but the comments warn some fields may be OTP in some driver ICs, motivating validation. Dual-DSI state stores both device pointers, but command programming is issued through the primary DSI device.

### Dependencies

The driver depends on Linux bitfield helpers, OF graph helpers for secondary DSI discovery, regulator and GPIO APIs, DRM panel/mode/connector helpers, MIPI DSI generic and DCS multi-context helpers, and device match data. It uses managed DSI attachment and managed registration for the secondary DSI endpoint.

### Integration points

Supported compatibles are `aoly,sl101pm1794fog-v15` and `startek,kd070fhfid078`. Their descriptors provide modes, voltages, GOA muxes, timing values, MIPI timing, engineer controls, and optional analog/digital gamma tables. Board DTS supplies `vdd`, `iovcc`, reset, optional enable, optional backlight, and optional second DSI graph connection. Connectors receive descriptor modes, bpc, and physical dimensions.

### Risks

The descriptor validation is essential but contains fragile logic: bounds compare values against bit masks rather than decoded maxima in several places, and the GOA timing validity counters are non-obvious. `hx8279_set_goa_timing()` writes `goa_odd_timing` for both odd and even register loops, which looks suspicious when `goa_even_timing` differs. `hx8279_set_digital_gamma()` reuses loop variable `i` in nested loops, so the intended two-pass positive/negative programming may not execute as written. Command programming only uses `dsi[0]`, so dual-DSI panels rely on mirrored controller behavior or host-side routing. Display-on/off helpers ignore accumulated DSI errors and return zero.

### Test signals

Run build coverage, probe both compatibles, validation failure tests for voltages/GOA/gamma descriptors, single- and dual-DSI attach paths, regulator voltage support checks, command traces verifying page order and gamma programming, sleep/display transitions, repeated suspend/resume, mode enumeration, backlight binding, and hardware image checks for GOA/gamma correctness. Static review should specifically cover the even-timing and digital-gamma loop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx8279.c -->
