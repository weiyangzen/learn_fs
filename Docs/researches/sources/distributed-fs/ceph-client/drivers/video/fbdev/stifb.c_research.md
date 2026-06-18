# sources/distributed-fs/ceph-client/drivers/video/fbdev/stifb.c

## Purpose
`stifb.c` is the PA-RISC framebuffer driver for HP STI/NGLE graphics devices. It binds to STI ROM-discovered devices, maps the framebuffer and NGLE register space, exposes a fixed-mode fbdev interface, programs device-specific RAMDAC/attribute/overlay state, and provides limited hardware acceleration for rectangle fill and copy.

## Important APIs, Types, and Functions
The main private state is `struct stifb_info`, which links `fb_info`, the STI ROM handle, NGLE card id, device-specific config, ROM data, and a 16-entry pseudo palette. Important setup and hardware helpers include `stifb_init_fb()`, `stifb_init_display()`, `SETUP_FB()`, `SETUP_HW()`, `SETUP_HCRX()`, `SETUP_RAMDAC()`, `CRX24_SETUP_RAMDAC()`, `ngleSetupAttrPlanes()`, `ngleResetAttrPlanes()`, `ngleClearOverlayPlanes()`, `hyperResetPlanes()`, and `hyperUndoITE()`. fbdev callbacks are `stifb_check_var()`, `stifb_setcolreg()`, `stifb_blank()`, `stifb_fillrect()`, `stifb_copyarea()`, and generic IOMEM mmap/read/write/imageblit helpers. Module entry points are `stifb_init()`, `stifb_cleanup()`, and `stifb_setup()`.

## Control Flow
`stifb_init()` parses `stifb=` options, locates the default STI ROM first, then initializes each available STI ROM through `stifb_init_fb()`. Probe validates supported NGLE ids, rejects Visualize EG double-buffer modes, chooses bpp from hardware and `bpp:` preferences, derives visible resolution from STI, maps framebuffer memory, allocates a 256-entry cmap, initializes display planes and blanking, reserves framebuffer/MMIO resources, and registers the framebuffer. Runtime mode changes are intentionally narrow: `stifb_check_var()` only accepts the current resolution and bpp. Colormap updates switch hardware into image colormap access, write the entry, and either trigger HCRX LUT load or restore normal register state. Fill/copy callbacks program NGLE bitmap-op registers and fall back to `cfb_fillrect()` for unsupported cases.

## State and Persistence
Driver state is runtime-only and stored in `fb_info`, `struct stifb_info`, resource reservations, mapped STI regions, the fbdev cmap, and the pseudo palette. Hardware-visible state includes NGLE setup registers, RAMDAC contents, overlay planes, attribute planes, framebuffer contents, HCRX Hyperbowl/LUT state, blanking bits, and selected bpp. Nothing is persisted across unload or reboot. Global init-only state includes `stifb_bpp_pref[]` and `stifb_disabled`.

## Dependencies and Integration Points
The driver depends on PA-RISC STI core discovery (`video/sticore.h`), STI ROM region descriptors, GSC register accessors, fbdev IOMEM helpers, HP-UX grfioctl compatibility headers, kernel resource reservation, and generic cfb drawing. It integrates with fb boot options, STI primary graphics ordering, and the platform firmware's current display mode rather than EDID or dynamic mode setting.

## Risks and Edge Cases
Most risk is in undocumented hardware programming sequences and fixed register constants. `SETUP_HW()` waits on device status with no timeout. Some clear-image helpers are stubs, double-buffer devices are rejected, Tomcat dual-head support is incomplete, and HCRX bpp behavior depends on ROM/device-specific config. Resource cleanup is manual and ordered; failed initialization must unwind mapped memory, cmap, and reserved regions correctly. Since mode changes are refused, userspace expecting dynamic modes will fail.

## Test Signals
Useful signals are boot tests on each supported NGLE family, `stifb=off` and `stifb=bpp:` parsing, 8-bit and HCRX 32-bit color display, palette changes, fbcon scroll exercising fill/copy acceleration, blank/unblank for each card family, mmap/read/write sanity, unload cleanup, and unsupported/double-buffer hardware rejection.
