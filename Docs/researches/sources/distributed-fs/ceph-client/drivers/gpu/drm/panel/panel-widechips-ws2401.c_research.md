# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-widechips-ws2401.c

## Purpose
This file drives a WideChips WS2401-controlled Samsung LMS380KF01 480x800 DPI RGB panel over SPI/MIPI DBI. It handles panel power, DBI initialization, optional internal backlight, and DRM panel mode exposure.

## Important APIs, Types, and Functions
The state container is `struct ws2401`, embedding `mipi_dbi`, `drm_panel`, reset GPIO, two regulators, dimensions, and an `internal_bl` flag. Main functions are `ws2401_power_on`, `ws2401_power_off`, panel prepare/enable/disable/unprepare, `ws2401_get_modes`, `ws2401_set_brightness`, `ws2401_read_mtp_id`, probe, and remove.

## Control Flow
Probe allocates a DPI panel, gets `vci` and `vccio`, configures reset, initializes DBI over SPI, assigns readable ID commands, briefly powers the panel to read MTP ID, powers it off, then uses an external DT backlight if present or registers an internal platform backlight. Prepare enables rails, toggles reset, sends repeated sleep-out plus password, resolution, address mode, pixel format, SMPS, power, VCOM, source, panel, MIE, and gamma commands. Enable sends display-on; disable sends display-off; unprepare disables the internal backlight if used, enters sleep, and powers off.

## State and Persistence Behavior
The driver persists SPI DBI bus state, panel registration, reset/regulator handles, and optional backlight selection. The panel itself retains register programming while powered. Internal backlight brightness is controlled by DCS-like DBI commands and not mirrored in private state.

## Dependencies and Integration Points
It integrates with DRM panel, `drm_mipi_dbi`, SPI, regulator/GPIO, media bus format reporting, external `drm_panel_of_backlight`, and Linux backlight. It exposes RGB888 bus format and pixel-drive bus flags to the display pipeline.

## Risks
The driver ignores return values from most DBI commands during power-on, so partial initialization may look successful. Internal backlight requires leaving level-2 command access open; external backlight closes it. Probe intentionally powers the panel for ID reads, which can interact with board sequencing. The implementation is tailored to LMS380KF01 despite a reusable controller name.

## Test Signals
Validate SPI DBI transfers, MTP ID reads, power cycling, display-on/off, RGB bus timing and flags, external versus internal backlight paths, gamma/register initialization on real hardware, and blanking behavior through backlight sysfs.
