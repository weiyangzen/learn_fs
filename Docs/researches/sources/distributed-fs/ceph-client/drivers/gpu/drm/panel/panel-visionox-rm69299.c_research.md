# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-visionox-rm69299.c

## Purpose
This file is a DRM MIPI-DSI panel driver for Visionox RM69299-based AMOLED panels. It supports two compatible variants with different fixed modes, initialization command tables, and optional backlight limits.

## Important APIs, Types, and Functions
The main state is `struct visionox_rm69299`, backed by `struct visionox_rm69299_panel_desc` for variant mode/init data. Key functions are `visionox_rm69299_power_on`, `visionox_rm69299_power_off`, `visionox_rm69299_prepare`, `visionox_rm69299_unprepare`, `visionox_rm69299_get_modes`, brightness get/update callbacks, `visionox_rm69299_probe`, and `visionox_rm69299_remove`.

## Control Flow
Probe allocates a `drm_panel`, reads OF match data, gets `vdda` and `vdd3p3` regulators plus a reset GPIO, optionally registers a raw backlight, adds the panel, configures four-lane RGB888 DSI video mode, and attaches to the host. Prepare enables regulators, runs the reset timing, switches to low-power DSI mode, writes the selected init table as two-byte DCS packets, exits sleep, waits, and turns the display on. Unprepare disables low-power mode, sends display-off and sleep commands, then powers down.

## State and Persistence Behavior
Persistent driver state is devm-managed: panel object, regulator array, reset GPIO, DSI pointer, selected descriptor, and optional backlight. Runtime state is mostly external hardware state: regulator enables, reset line level, DSI mode flags, panel sleep/display state, and DCS brightness.

## Dependencies and Integration Points
It integrates with DRM panel helpers, MIPI DSI multi-command helpers, device-tree match data, regulator and GPIO frameworks, and the Linux backlight class. The mode is exposed through connector probing and the module binds through `module_mipi_dsi_driver`.

## Risks
The init tables are opaque vendor sequences, so mode or timing changes can silently break bring-up. Brightness callbacks temporarily clear `MIPI_DSI_MODE_LPM`; failures before restoring the flag can leave later transfers in the wrong mode. Power-on and DCS delays are panel-specific and sensitive to shortening. The 1080p descriptor has no backlight bounds, so no backlight is created for that variant.

## Test Signals
Useful signals are DSI attach/probe on both compatibles, panel prepare/unprepare cycles, suspend/resume, display mode enumeration, brightness read/write through sysfs, regulator/reset scope traces, and display-on/off timing checks against the DCS 120 ms waits.
