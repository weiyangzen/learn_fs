
# sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/fbdev.c

Purpose: fbdev-facing PCI driver for STG4000/Kyro/PowerVR3 graphics. It owns PCI probing, framebuffer registration, mode database, fb_ops, color pseudo-palette, private overlay ioctls, write-combining, and calls lower-level STG4000 helper files for hardware programming.

Important APIs and types: static `kyro_fix`/`kyro_var` provide defaults. `kyro_modedb[]` lists supported VESA-like modes. `device_info_t` holds the mapped register base and overlay allocation offsets/strides; `deviceInfo` is global. fb_ops include check-var, set-par, setcolreg, ioctl, and default IO memory ops. Private ioctl commands come from `<video/kyro.h>`.

Control flow: probe removes conflicting apertures, enables PCI, requests BARs, allocates fb_info, maps MMIO and framebuffer, enables write-combining unless disabled, sets panning/wrapping steps, calls `SetCoreClockPLL()`, selects a mode via `fb_find_mode()`, allocates cmap, programs mode with `kyrofb_set_par()`, clears framebuffer memory, registers fbdev, and stores drvdata. Set-par derives Kyro timing fields from fb_var, calls `kyro_dev_video_mode_set()`, updates line length and visual. Mode set stops VTG/RAMDAC, disables VGA, initializes RAMDAC, sets VTG, resets overlay, and restarts output. Ioctls create overlay, set viewport, or return overlay offsets/strides.

State and persistence: per-fb `struct kyrofb_info` stores timing and pseudo-palette. Global `deviceInfo` stores register pointer and overlay allocation state, so this driver effectively assumes one card. Module/boot options control mode, panning, wrapping, and MTRR/write-combining.

Dependencies and integration: uses PCI managed region helpers, fbdev core, aperture arbitration, architecture WC API, user copy helpers, and the STG4000 interface. It depends on `<video/kyro.h>` for `struct kyrofb_info` and ioctl payloads.

Risks: global `deviceInfo` is not multi-device safe. `deviceInfo.ulNextFreeVidMem` uses `xres*yres*bits_per_pixel` without dividing bpp by 8, overestimating primary memory and affecting overlay placement. Probe failure path returns `-EINVAL` for many resource failures, obscuring root cause. `SetCoreClockPLL()` return is ignored. No remove-time devm unmap is needed, but framebuffer release order must stay compatible with registered fbdev state.

Test signals: probe/remove, mode database selection and fallback, 16/32 bpp checks, line length, panning/wrap options, overlay ioctl create/view/stride/offset paths, multi-card static-state analysis, and failure injection for mapping/register_framebuffer.
