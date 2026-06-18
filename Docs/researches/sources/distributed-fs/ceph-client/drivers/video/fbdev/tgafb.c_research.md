# sources/distributed-fs/ceph-client/drivers/video/fbdev/tgafb.c

## Purpose
`tgafb.c` is the framebuffer driver for DEC 21030 TGA/SFB+ graphics devices on PCI and TurboChannel buses. It handles 8-plane, 24-plane, and 24-plus-Z variants, programs TGA timing/PLL/RAMDAC state, and implements custom accelerated image, fill, and copy operations.

## Important APIs, Types, and Functions
Private state is `struct tga_par` from `include/video/tgafb.h`, holding mapped memory, type/revision, current timing, bpp, sync-on-green, blank state, and pseudo palette. Important functions are `tgafb_check_var()`, `tgafb_set_par()`, `tgafb_set_pll()`, `tgafb_setcolreg()`, `tgafb_blank()`, `tgafb_mono_imageblit()`, `tgafb_clut_imageblit()`, `tgafb_fillrect()`, `tgafb_copyarea()`, `tgafb_init_fix()`, `tgafb_pan_display()`, `tgafb_register()`, and `tgafb_unregister()`. Bus wrappers are `tgafb_pci_register()` and `tgafb_tc_register()`.

## Control Flow
PCI probe removes conflicting apertures and calls common registration; TC probe calls the same path with TC resource handling. `tgafb_register()` enables PCI if needed, allocates `fb_info`, requests/maps the device memory resource, reads the TGA type from ROM/register space, derives framebuffer and register offsets, selects PCI or TC default modes, initializes `fix`, finds a mode, allocates cmap, calls `tgafb_set_par()`, and registers fbdev. `tgafb_set_par()` validates and stores timing, disables video, programs DEEP/rasterop/mode/base registers, computes and writes the ICS1562 PLL, initializes BT485/BT459/BT463 RAMDAC state depending on bus and depth, initializes palette/window type table, then enables video.

## State and Persistence
Runtime state lives in `fb_info` and `tga_par`: mapped device memory, framebuffer/register base pointers, card type, revision, timing registers, PLL frequency, bpp, blank flag, and palette. Hardware state includes TGA registers, PLL shift/programming bits, BT RAMDAC palettes/masks/window types, cursor-valid bits, and framebuffer contents. It does not persist across driver lifetime.

## Dependencies and Integration Points
The driver depends on PCI, optional TurboChannel, aperture handoff, `video/tgafb.h`, raw MMIO access, fbdev mode/cmap/modelist helpers, and optional VT default color tables. It integrates with `video=tgafb:mode:...`, PCI ID `DEC_TGA`, and TC IDs `PMAGD-AA`/`PMAGD`.

## Risks and Edge Cases
Several hardware waits spin until command status or retrace changes, with no timeout. Type-derived offsets index preset arrays and assume recognized hardware type. 32bpp copy falls back in general cases because pixelshift behavior is unclear. Acceleration code has many alignment, clipping, and endian assumptions. `tgafb_init()` only registers the TC driver if PCI registration returns success, so mixed build behavior deserves attention. Error cleanup must release mapped resources and cmap.

## Test Signals
Test PCI and TC binding, all TGA type variants, 8bpp-only and 32bpp-only validation, sync-on-green modes, PLL programming across common clocks, BT485/BT459/BT463 palette writes, blank/unblank and DPMS states, mono and CLUT imageblit, aligned and unaligned fill/copy, full-line scroll acceleration, pan reset behavior, and unregister cleanup.
