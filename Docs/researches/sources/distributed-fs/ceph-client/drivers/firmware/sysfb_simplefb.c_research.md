# sources/distributed-fs/ceph-client/drivers/firmware/sysfb_simplefb.c

Simple-framebuffer helper for `sysfb.c`. It validates firmware `screen_info`, translates recognized VESA/EFI packed RGB modes into `simplefb_platform_data`, computes an accessible framebuffer memory resource, and registers a `simple-framebuffer` platform device.

`sysfb_parse_mode()` accepts only `VIDEO_TYPE_VLFB` and `VIDEO_TYPE_EFI`, rejects transparent formats, and matches bits-per-pixel plus RGB bitfield sizes/offsets against `SIMPLEFB_FORMATS`. On success it fills format, width, height, and stride. `sysfb_create_simplefb()` builds a 64-bit base when `VIDEO_CAPABILITY_64BIT_BASE` is set, rejects inaccessible/truncated bases, uses `height * stride` rather than the full advertised VRAM, verifies it fits in firmware-reported VRAM, page-aligns the mapping length, creates the `BOOTFB` memory resource, attaches EFI fwnode data, platform data, and registers the device.

State is not persistent beyond the platform device and its resource/platform data. Dependencies include `screen_info`, simplefb format definitions, platform-device resource APIs, page alignment, and `sysfb_set_efifb_fwnode()`.

Risks include integer overflow if `height * stride` exceeds 32 bits before assignment to `u32 length`, although firmware modes are typically bounded. The `res.end <= res.start` guard catches some wrap cases after page alignment. Test signals include known EFI/VESA formats, 64-bit framebuffer base handling, advertised-VRAM-too-small rejection, resource bounds in `/proc/iomem`, and simpledrm/simplefb binding behavior.
