# sources/distributed-fs/ceph-client/drivers/video/fbdev/neofb.c

## Purpose

`neofb.c` is a PCI fbdev driver for NeoMagic MagicGraph chips from NM2070 through NM2380. It provides VGA-compatible mode programming, LCD/CRT routing, panel stretching/centering, framebuffer and MMIO mapping, colormap management, panning, blanking/DPMS, VGA state save/restore, and hardware acceleration for Neo2200-class chips. The source was read as a complete 2227-line file.

## Important APIs, Types, and Functions

The driver uses `struct neofb_par`, `Neo2200`, `biosMode`, and `NEO_BC*` constants from `include/video/neomagic.h`. User-facing fbdev operations are collected in `neofb_ops`: `neofb_open`, `neofb_release`, `neofb_check_var`, `neofb_set_par`, `neofb_setcolreg`, `neofb_pan_display`, `neofb_blank`, `neofb_sync`, `neofb_fillrect`, `neofb_copyarea`, and `neofb_imageblit`. Mode support is driven by `neoFindMode()` BIOS-mode tables and `neoCalcVCLK()` PLL search. VGA register generation/restoration is handled by `vgaHWInit()`, `vgaHWProtect()`, `vgaHWRestore()`, `neoUnlock()`, and `neoLock()`. Neo2200 acceleration is implemented by `neo2200_accel_init()`, `neo2200_sync()`, `neo2200_fillrect()`, `neo2200_copyarea()`, and `neo2200_imageblit()`. Probe/remove are `neofb_probe()` and `neofb_remove()`, registered through `neofb_driver` and the `neofb_devices` PCI ID table.

## Control Flow

Module/init command-line parsing sets `internal`, `external`, `libretto`, `nostretch`, `nopciburst`, and `mode_option`, then registers the PCI driver unless global modesetting is disabled. Probe removes conflicting apertures, enables the PCI device, allocates `fb_info`, maps MMIO, reads NeoMagic display/panel registers, derives VRAM/clock/cursor capabilities, maps framebuffer memory, chooses an initial mode, allocates a cmap, and registers the framebuffer. `neofb_check_var()` validates dot clock, panel dimensions, supported LCD mode sizes, color layout, and available VRAM. `neofb_set_par()` unlocks NeoMagic extended registers, blanks the display, computes VGA and extended register values, configures LCD/CRT routing, stretching and centering, computes VCLK3, restores VGA state, programs palettes and NeoMagic extension registers, re-locks, updates line length, and initializes Neo2200 acceleration when available. Runtime fbdev calls pan by writing CRTC start address registers plus extended address bits, blank by combining VGA sequencer, LCD, and DPMS bits, and accelerate fill/copy/imageblit for Neo2200+ while falling back to `cfb_*` for unsupported chips or image formats. Remove unregisters the framebuffer, unmaps video/MMIO, frees the mode database and cmap, and releases the `fb_info`.

## State and Persistence Behavior

Per-device state lives in `struct neofb_par`: saved VGA state/refcount, panel size, LCD/CRT routing, stretching/centering registers, PLL parameters, PCI burst flag, `neo2200` MMIO pointer, pseudo palette, and write-combining cookie. The driver saves VGA mode/fonts on first open and restores them on last release. It does not persist data across unloads; persistent effects are limited to hardware registers and framebuffer contents while the device is active. `PanelDispCntlRegRead` is used to preserve Fn-key or firmware display routing changes across blank/unblank cycles.

## Dependencies and Integration Points

The driver integrates with PCI, aperture conflict removal, fbdev core APIs, generic VGA helpers, architecture I/O port access, write-combined framebuffer mapping, and optional Toshiba SMM backlight hooks under `CONFIG_TOSHIBA`. It relies on `vesa_modes`, `fb_find_mode`, and the NeoMagic hardware header for register layout and blitter constants. Acceleration depends on MMIO layout for NM2200/NM2230/NM2360/NM2380.

## Risks and Edge Cases

The code programs legacy VGA I/O ports and NeoMagic extension registers directly, so it is sensitive to primary-display assumptions, firmware state, and concurrent firmware hotkeys. `neo2200_sync()` spins without a timeout, which can hang if the blitter never clears busy. `neofb_check_var()` silently reduces virtual or visible resolution to fit VRAM rather than always rejecting, which can surprise callers. Hardware acceleration has known 24-bpp mono image constraints and falls back for narrow images. Some features are explicitly unfinished, including 32-bpp support and hardware cursor support. Panel detection supports only 640x480, 800x600/480, and 1024x768 panels unless disabled.

## Test Signals

Important coverage includes PCI probe/remove for every listed NeoMagic ID, mode validation for LCD-only and CRT-only paths, Libretto 800x480 mode selection, blank/unblank and DPMS register behavior, first-open/last-release VGA restore, panning after X or console use, accelerated fill/copy/imageblit on NM2200+ with software fallback comparison, and suspend-like hotkey display-route changes across blank/unblank.
