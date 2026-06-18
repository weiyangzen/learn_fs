<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_backlight.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_backlight.c

## Purpose
This module exposes PicoLCD backlight brightness through the Linux backlight class and translates brightness/power changes into `REPORT_BRIGHTNESS` HID output reports.

## Important APIs, types, and functions
`picolcd_blops` provides `.update_status = picolcd_set_brightness` and `.get_brightness = picolcd_get_brightness`. `picolcd_init_backlight` validates the brightness report shape, registers a `BACKLIGHT_RAW` device, sets default brightness 0xff, and sends it to hardware. `picolcd_exit_backlight`, `picolcd_resume_backlight`, and `picolcd_suspend_backlight` handle teardown and power management restore.

## Control flow
Probe passes the brightness output report from core into `picolcd_init_backlight`. Runtime updates come from the backlight class into `picolcd_set_brightness`, which caches `lcd_brightness` and `lcd_power`, sets the single report field to either the brightness value or zero when powered off, and submits a SET_REPORT under `data->lock` if the device has not failed.

## State and persistence behavior
Backlight state is held in `picolcd_data.lcd_brightness`, `lcd_power`, and `backlight`. It is restored on resume/reset by replaying the cached brightness. No state is persisted beyond the attached device lifetime.

## Dependencies and integration points
The module depends on HID output reports, the backlight subsystem, and the shared PicoLCD lock/status fields. Framebuffer code may attach the backlight to `fb_info` when `CONFIG_FB_BACKLIGHT` is enabled.

## Risks and test signals
Risks include invalid report descriptors, null `data->backlight` during cleanup, and races with device removal. Tests should vary brightness and blanking, suspend/resume, reset-resume, removal after registration, and Kconfig combinations with framebuffer support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_backlight.c -->
