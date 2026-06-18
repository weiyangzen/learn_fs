# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/waveshare-dsi.c

Purpose: implements a Waveshare DSI-to-DPI bridge as an I2C-controlled DRM bridge with an internal raw backlight device. It creates and attaches a MIPI DSI device to the upstream DSI host, wraps the downstream panel as a panel bridge, and writes simple control registers for bridge and backlight enable/brightness.

Important APIs/types/functions: `struct ws_bridge` holds the DRM bridge, next bridge, backlight, device, and I2C regmap. `ws_bridge_attach_dsi()` finds the DSI host from graph port 0, registers a `mipi_dsi_device`, sets video HSE/video/non-continuous clock flags and RGB888 format, reads data-lane count from endpoint with fallback to two lanes, and attaches the DSI device. `ws_bridge_probe()` allocates state, initializes regmap, finds the downstream panel at graph port 1, creates a panel bridge, registers a raw backlight, writes initial control registers `0xc0`, `0xc2`, and `0xac`, registers the DRM bridge, then attaches DSI. Bridge hooks attach the next bridge, enable by writing `0xad=1` and enabling backlight, and disable by disabling backlight then writing `0xad=0`. Backlight update writes inverted brightness to `0xab` and commits with `0xaa=1`.

Control flow: probe must find both DSI host and panel through the OF graph. Runtime bridge enable/disable only toggles the bridge output and backlight; there are no mode validation, bus format, HPD, or EDID callbacks.

State and persistence: state is the regmap-backed bridge registers and kernel backlight brightness. Register settings are not cached by regmap and no runtime PM is used, so suspend/resume persistence depends on parent I2C device behavior and panel/bridge sequencing.

Dependencies and integration points: depends on I2C/regmap, DRM bridge and panel bridge helpers, MIPI DSI, OF graph, and backlight core. Compatible string is `waveshare,dsi2dpi`.

Risks: register semantics are magic constants with no local definitions. I2C write errors in enable/disable/backlight update are ignored. DSI lane fallback preserves old DT behavior but can hide invalid descriptions. No remove callback is needed because devm is used, but the attached DSI device and bridge state depend on devm cleanup order.

Test signals: DSI host probe deferral, panel bridge creation, lane count 1..4 and fallback path, backlight brightness inversion, enable/disable I2C writes on scope or register trace, and suspend/resume if the chip loses register state.
