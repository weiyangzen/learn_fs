# sources/distributed-fs/ceph-client/drivers/firmware/sysfb.c

Generic system framebuffer device creator. It turns firmware-populated `sysfb_primary_display.screen` data into a platform device for either `simple-framebuffer` or a legacy framebuffer driver. The code runs as a `device_initcall()` after PCI enough for EFI quirks and parent-device detection.

Public APIs are `sysfb_disable()` and `sysfb_handles_screen_info()`. `sysfb_disable()` serializes against init with `disable_lock`, unregisters the platform device when the caller is global or matches the detected parent, and permanently suppresses registration. `sysfb_handles_screen_info()` reports whether `screen_info_video_type()` sees a supported video type.

`sysfb_init()` applies screen-info fixups, honors the global disabled flag, applies EFI quirks, resolves an optional PCI parent via `screen_info_pci_dev()`, then asks `sysfb_parse_mode()` whether the mode can become `simple-framebuffer`. If simplefb creation fails or is unsupported, it selects a legacy platform-device name from the video type, attaches the full `sysfb_display_info` as platform data, applies EFI fwnode data, and registers the device.

State is minimal: static `pd` records the registered platform device, while `disabled` gates future registration. Firmware framebuffer metadata remains in global `screen_info`; this file does not own video memory. Dependencies include PCI, platform devices, `screen_info`, `sysfb` helpers, and simplefb platform data.

Risks include parent reference handling: `sysfb_parent_dev()` returns a referenced PCI device, and `sysfb_init()` unconditionally calls `put_device(parent)` on the common exit path, so null-parent paths rely on `put_device(NULL)` being harmless. Registration uses device id 0 by design, which requires other firmware parsers to avoid conflicts. Test signals include boot logs for simplefb versus legacy fallback, `sysfb_disable()` from native DRM drivers, PCI memory-disabled parent rejection, EFI quirk behavior, and absence of duplicate platform framebuffer devices.
