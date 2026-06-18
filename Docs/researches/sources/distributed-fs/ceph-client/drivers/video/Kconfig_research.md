# sources/distributed-fs/ceph-client/drivers/video/Kconfig

## Purpose
This Kconfig file defines the `Graphics support` menu and wires legacy video, framebuffer, console, backlight, logo, EDID, aperture, HDMI, and helper options into the kernel configuration tree.

## Important APIs, types, and functions
It is declarative Kconfig rather than C code. Important symbols include `APERTURE_HELPERS`, `SCREEN_INFO`, `STI_CORE`, `VIDEO`, `HAVE_FB_ATMEL`, `VGASTATE`, `VIDEOMODE_HELPERS`, `HDMI`, and `FIRMWARE_EDID`. It sources submenus for auxdisplay, AGP, VGA, GPU, DRM, framebuffer devices, backlight devices, console, logo, and GPU tracing.

## Control flow
Configuration visibility is gated primarily by `HAS_IOMEM` and `VT`. If I/O memory is available, the file exposes GPU/DRM/fbdev/backlight and low-level video helpers. Firmware EDID is exposed outside `HAS_IOMEM` but depends on EFI generic stub or x86. Console and logo submenus are included only when their owning subsystems are configured.

## State and persistence
The file contributes build-time state only. Selected symbols persist in `.config` and drive object inclusion through Makefiles and preprocessor conditionals.

## Dependencies and integration points
It is the parent for many graphics subsystems. `APERTURE_HELPERS` maps to `drivers/video/aperture.c`; `VIDEO` maps to video command-line helpers; `VIDEOMODE_HELPERS` selects display timing conversions; `source "drivers/video/backlight/Kconfig"` integrates the backlight/LCD driver menu.

## Risks and test signals
Risks are dependency mistakes that expose drivers on unsupported platforms or hide required helpers from DRM/fbdev users. Test signals include `allyesconfig`, `allmodconfig`, architecture-specific builds without `HAS_IOMEM`, x86/EFI firmware EDID combinations, and randconfig coverage for sourced submenu reachability.
