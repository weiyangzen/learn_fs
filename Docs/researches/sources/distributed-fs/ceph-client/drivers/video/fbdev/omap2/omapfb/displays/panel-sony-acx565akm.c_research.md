# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-sony-acx565akm.c

## Purpose

`panel-sony-acx565akm.c` is a SPI-controlled SDI panel driver for Sony ACX565AKM-compatible MIPI command panels used through the legacy OMAP DSS/fbdev display model. The complete 857-line source was read. It detects the LCD model over SPI, registers an `omap_dss_device`, proxies SDI connect/enable/timing operations to the upstream DSS output, and exposes backlight/CABC controls for panels that support them.

## Important APIs, Types, and Functions

The core state is `struct panel_drv_data`: embedded `omap_dss_device`, upstream `in` device, reset GPIO, SDI datapair count, current `omap_video_timings`, panel identity fields, brightness/CABC capability flags, sleep guard timing, SPI device, mutex, and `backlight_device`. SPI helpers are `acx565akm_transfer()`, `acx565akm_cmd()`, `acx565akm_write()`, and `acx565akm_read()`. Panel control is split across `panel_enabled()`, `panel_detect()`, `set_sleep_mode()`, `set_display_state()`, `acx565akm_panel_power_on()`, and `acx565akm_panel_power_off()`. Backlight integration uses `acx565akm_bl_ops`, `acx565akm_set_brightness()`, and CABC sysfs attributes `cabc_mode` and `cabc_available_modes`. DSS entry points are in `acx565akm_ops`.

## Control Flow

Probe requires a DT node, sets SPI mode 3, allocates driver data, finds the first endpoint source via `omapdss_of_find_source_for_first_ep()`, requests optional reset GPIO, waits after reset, reads display status and display ID, registers a backlight, creates CABC sysfs files when supported, initializes default 800x480 timings, and registers the display. Enable checks that the display is connected and inactive, then under `ddata->mutex` programs SDI timings/datapairs, enables the upstream SDI output, waits for panel timing requirements, deasserts reset according to the historical GPIO polarity quirk, exits sleep, turns display on, restores CABC, and updates brightness. Disable reverses display-on and sleep state, waits for two frames, asserts reset, and disables upstream SDI.

## State and Persistence Behavior

All state is volatile kernel driver state. `enabled`, `cabc_mode`, detected model/revision, brightness properties, and sleep guard jiffies persist only while the SPI device is bound. Hardware-visible state is held in panel registers and is restored during enable; CABC sysfs stores the requested CABC mode even when the panel is disabled and applies it on the next power-on. There is no file-backed persistence.

## Dependencies and Integration Points

The driver depends on SPI, GPIO descriptors, backlight core, OF endpoint lookup, and `video/omapfb_dss.h`. It integrates with DSS as an SDI sink through `in->ops.sdi`, with fb/backlight through `backlight_device_register()`, and with sysfs through the backlight device kobject.

## Risks and Edge Cases

SPI transfers use 9-bit command/data framing and special 10-bit dummy handling for multi-byte reads, so controller support and endianness are critical. `acx565akm_transfer()` logs SPI failures but returns void, so many command failures are not propagated. The reset GPIO polarity comment documents compatibility with incorrect older DTS polarity. Remove unconditionally removes the CABC sysfs group even though it is created only when `has_cabc`, which is normally harmless but worth checking on sysfs changes. Sleep in/out timing relies on jiffies guards and fixed delays.

## Test Signals

Useful signals include DT probe with compatible `omapdss,sony,acx565akm`, SPI read of display ID/status, enable/disable cycling with SDI source connected, backlight brightness get/set, CABC sysfs read/write including unsupported modes, suspend/resume through DSS display disable/enable, and negative tests for missing endpoint, missing reset GPIO, unsupported SPI transfers, and unknown display ID.
