<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_lcd.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_lcd.c

## Purpose
This module exposes PicoLCD contrast through the Linux LCD class and translates contrast changes into the one-byte `REPORT_CONTRAST` HID output report.

## Important APIs, types, and functions
`picolcd_lcdops` implements `.get_contrast` and `.set_contrast`. `picolcd_init_lcd` validates the contrast output report, registers an `lcd_device`, sets max contrast 0xff, caches default contrast 0xe5, and sends it to hardware. `picolcd_exit_lcd` unregisters the LCD class device. `picolcd_resume_lcd` replays cached contrast after reset/resume.

## Control flow
Core probe passes the contrast report into `picolcd_init_lcd`. Runtime LCD class updates call `picolcd_set_contrast`, which masks the requested value to 8 bits, writes the report field under `data->lock`, and submits SET_REPORT if the device is not marked failed.

## State and persistence behavior
Only the cached `data->lcd_contrast` and `data->lcd` pointer are maintained. Contrast is restored from memory after reset/resume, but not persisted across unplug.

## Dependencies and integration points
It depends on HID reports and the LCD subsystem. Framebuffer code may attach this LCD device to fb_info for fb blanking/notification integration.

## Risks and test signals
Risks are report shape mismatch, null teardown, and removal races during class callbacks. Tests should validate contrast sysfs/class controls, default contrast setup, resume/reset restore, and builds with/without framebuffer and backlight modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_lcd.c -->
