<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_fb.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_fb.c

## Purpose
This module exposes the PicoLCD 256x64 monochrome display as a Linux fbdev framebuffer. It translates packed or 8-bit grayscale framebuffer memory into the display controller's tile format and sends only changed tiles through LCD command/data HID reports.

## Important APIs, types, and functions
Constants define a 256x64 display and 2048-byte 1bpp device bitmap. `picolcd_fb_send_tile` emits one tile using `REPORT_LCD_CMD_DATA` and `REPORT_LCD_DATA`. `picolcd_fb_update_tile` translates framebuffer pixels into the PicoLCD vertical-byte tile layout and detects changes. `picolcd_fb_update` scans all 4 chips x 8 tiles and throttles against `HID_OUTPUT_FIFO_SIZE` with `hid_hw_wait`. Fbdev operations are in `picolcdfb_ops`; deferred I/O is provided by `picolcd_fb_deferred_io`. `picolcd_init_framebuffer` allocates/registers fb_info and sysfs `fb_update_rate`; `picolcd_exit_framebuffer` disconnects and unregisters it.

## Control flow
Initialization allocates one fb_info block containing deferred I/O metadata, pseudo palette, `picolcd_fb_data`, and vbitmap storage, then vmallocs the user framebuffer. It resets the LCD controller, creates update-rate sysfs, initializes deferred I/O, and registers the framebuffer. Damage callbacks schedule immediate deferred work. The update path locks the framebuffer, resets the display if not ready, translates changed tiles, sends changed or forced tiles, waits when the HID output FIFO may fill, and clears the force flag on success.

`picolcd_fb_reset` sends LCD mapping commands to all four chips, optionally clears cached/device framebuffer memory, marks `force`, and schedules the first output once ready. `picolcd_set_par` supports switching between 1bpp and 8bpp by translating existing content.

## State and persistence behavior
Framebuffer state is runtime memory only: `bitmap` is the userspace-visible buffer, `vbitmap` is the last sent device-format image, `force` triggers full refresh, `ready` tracks initial reset, and `update_rate` controls deferred I/O delay. Display contents can be restored after reset/resume from `bitmap`.

## Dependencies and integration points
The module integrates with fbdev, deferred I/O, optional backlight/LCD devices, HID output reports, and the shared PicoLCD `data->lock` and failed status. It is called from core probe, reset, raw power-management restore, and remove.

## Risks and test signals
Risks include deferred work racing with disconnect, tile translation errors across 1bpp/8bpp modes, HID FIFO flooding, and invalid report descriptors. The code mitigates teardown by nulling `fbdata->picolcd` under lock and flushing deferred work before unregister. Tests should draw patterns covering every chip/tile, switch bpp, tune `fb_update_rate`, reset/resume with retained contents, and disconnect during active framebuffer writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_fb.c -->
