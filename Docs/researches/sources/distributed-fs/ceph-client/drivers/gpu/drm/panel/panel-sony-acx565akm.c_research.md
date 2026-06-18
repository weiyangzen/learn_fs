# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sony-acx565akm.c

## Purpose
This SPI/DPI DRM panel driver supports the Sony ACX565AKM family and related MIPI DBI-like panels historically used on Nokia/OMAP hardware. It detects panel ID over SPI, controls sleep/display state, exposes a DRM fixed mode, registers an internal backlight device when supported, and exposes CABC controls through sysfs.

## Important APIs, Types, And Functions
`struct acx565akm_panel` tracks the DRM panel, SPI device, reset GPIO, backlight, mutex, detected name/model/revision, feature flags, enabled flag, CABC mode, and hardware guard timing. SPI transfers are centralized in `acx565akm_transfer()` with helpers `acx565akm_cmd()`, `acx565akm_write()`, and `acx565akm_read()`.

Important behavior is in `acx565akm_detect()`, `acx565akm_power_on()`, `acx565akm_power_off()`, `acx565akm_set_sleep_mode()`, `acx565akm_set_display_state()`, backlight ops, and `cabc_mode` sysfs handlers. Panel ops are `enable`, `disable`, and `get_modes`; this older driver does not split power into prepare/unprepare.

## Control Flow
Probe allocates the panel, sets `SPI_MODE_3`, gets reset GPIO default high, detects display status and ID, derives feature flags, initializes backlight/CABC when supported, and adds the panel. Detection may leave reset asserted low if the bootloader did not already enable the panel. Enable locks the mutex, performs reset/sleep-out/display-on/CABC/backlight programming, and records `enabled`. Disable locks the mutex, sends display-off and sleep-in, waits for required frame/reset delays, asserts reset, and clears `enabled`.

## State And Persistence
Mutable state includes `enabled`, `cabc_mode`, hardware guard jiffies, and detected panel identity. CABC mode persists only in memory and is applied when the panel is enabled. Backlight brightness is read from and written to panel registers. The mutex serializes panel register access from DRM, backlight, and sysfs paths.

## Dependencies And Integration Points
The file integrates with DRM panel, SPI, GPIO, backlight core, sysfs attributes, MIPI DCS command definitions, mutexes, jiffies, and scheduler sleep for guard timing. OF and SPI ID tables bind compatible `sony,acx565akm`.

## Risks
The file contains TODOs noting untested backlight modernization and prepare/unprepare separation. SPI transfer helpers do not propagate errors to most callers. The CABC sysfs parser has a duplicated `return -EINVAL;` line after the invalid-mode check, harmless but visibly stale. Power sequencing uses FIXME delay comments and legacy assumptions. Since display ID controls feature flags, failed or noisy reads can prevent probe.

## Test Signals
Hardware validation should cover ID detection for each supported ID, bootloader-enabled and disabled startup states, CABC sysfs reads/writes, brightness get/update, sleep guard timing, and repeated enable/disable. Static review should watch for ignored SPI errors and legacy backlight behavior.
