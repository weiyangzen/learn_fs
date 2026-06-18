# sources/distributed-fs/ceph-client/drivers/video/fbdev/cirrusfb.c

## Purpose

This file implements the legacy accelerated fbdev driver for Cirrus Logic VGA chipsets on PCI and Amiga Zorro boards. It supports multiple board families, including SD64, Piccolo, Picasso, Spectrum, Picasso IV, Alpine/GD543x, GD5480, and Laguna/GD546x variants. The complete 2954-line source was read.

## Important APIs, Types, and Functions

The main private type is `struct cirrusfb_info`, which stores register bases, optional Laguna MMIO, board type, special-function-register shadow, mode flags, blanking state, pseudo-palette, and an unmap callback. The driver exposes `struct fb_ops cirrusfb_ops` with open/release, I/O-memory read/write/mmap helpers, `cirrusfb_check_var()`, `cirrusfb_set_par()`, `cirrusfb_setcolreg()`, `cirrusfb_pan_display()`, `cirrusfb_blank()`, accelerated fill/copy/imageblit, and `cirrusfb_sync()`.

Important internal helpers include `init_vgachip()`, `cirrusfb_set_par_foo()`, `cirrusfb_check_pixclock()`, `cirrusfb_check_mclk()`, `bestclock()`, `switch_monitor()`, `WGen()`, `RGen()`, `AttrOn()`, `WHDR()`, `WSFR()`, `WClut()`, `cirrusfb_WaitBLT()`, `cirrusfb_BitBLT()`, and `cirrusfb_RectFill()`. Bus integration is via `cirrusfb_pci_driver` and `cirrusfb_zorro_driver`.

## Control Flow

Module/init setup honors `fb_modesetting_disabled("cirrusfb")`, parses `video=cirrusfb:` options when built in, and registers PCI and/or Zorro drivers according to configuration. PCI probe removes conflicting apertures, enables the device, allocates `fb_info`, classifies board type from the PCI ID table, maps display memory and optional Laguna MMIO, probes video RAM size, reserves legacy VGA ports when available, then calls `cirrusfb_register()`. Zorro probe locates register and RAM resources from board-specific `zorrocl` descriptors, handles split/optional Picasso IV RAM, maps Zorro II direct or Zorro III ioremap addresses, initializes SR1F where required, then registers the framebuffer.

Registration fills `fb_info` and `fix` fields, allocates a 256-entry cmap, finds the initial mode with `fb_find_mode()`, validates it, and calls `register_framebuffer()`. Mode setting runs through `cirrusfb_check_var()` and then `cirrusfb_set_par()`, which intentionally writes the hardware mode twice. The mode write path computes CRTC timings, clock numerator/denominator/divider, multiplexing/double-VCLK state, board-specific sequencer and hidden-DAC settings, line pitch, screen-start extension bits, Laguna format/threshold registers, and finally enables display sequencing. Pan display converts x/y offsets into the Cirrus split start-address registers. Acceleration paths clip requested rectangles, fall back to generic `cfb_*` helpers when disabled or unsupported, and otherwise program the Cirrus blitter registers.

## State and Persistence Behavior

Driver state is held in `fb_info`, `cirrusfb_info`, `opencount`, module parameters `noaccel` and `mode_option`, and bus drvdata. Hardware-visible state includes VGA sequencer, graphics, CRTC, attribute, DAC, hidden DAC, special function, and Laguna MMIO registers, plus framebuffer memory. Zorro monitor switching uses the `SFR` shadow and a static `IsOn` flag in `switch_monitor()`. No file-backed persistence exists, but module parameters and boot command-line options affect initial state.

## Dependencies and Integration Points

The file depends on fbdev core APIs, generic I/O-memory fbops macros, VGA/Cirrus register definitions, PCI, aperture conflict removal, Zorro, Amiga hardware helpers, and optional debug dumps. It integrates with `/dev/fb*`, fbcon, module autoloading through PCI/Zorro tables, boot video options, and generic `cfb_fillrect()`, `cfb_copyarea()`, and `cfb_imageblit()` fallback routines.

## Risks and Edge Cases

This is register-heavy legacy hardware code with many board-specific assumptions. Risks include unsupported 32 bpp despite some internal 32 bpp blitter paths, truncated offsets in `check_var()` when virtual dimensions equal visible dimensions, wait loops that spin indefinitely if the blitter never clears busy bits, and a global `opencount`/Zorro monitor switch state that is not per-device. The PCI path sets `regbase` to `NULL` for VGA-style register access and maps `laguna_mmio`; `cirrusfb_pci_unmap()` checks `if (cinfo->laguna_mmio == NULL) iounmap(cinfo->laguna_mmio)`, which appears inverted and risks leaking non-NULL mappings while calling `iounmap(NULL)` on the NULL case. Acceleration clips a copied `modded` rectangle but passes original coordinates/sizes to the blitter, so clipped requests near edges require careful review. Several comments mark incomplete Picasso IV and 24 bpp acceleration behavior.

## Test Signals

Useful tests include PCI probe/remove for each supported PCI ID, Zorro probe/remove with contiguous and non-contiguous RAM, boot parameter parsing for `mode:` and `noaccel`, fbcon rendering at 1/8/16/24 bpp, pan/blank/setcolreg ioctls, mode rejection for oversized virtual screens and vertical totals, blitter fill/copy/image paths with generic fallback, forced busy blitter timeouts under instrumentation, aperture conflict handling, and suspend-like blank/unblank cycles. Build coverage should include PCI-only, Zorro-only, both enabled, and non-module built-in configurations.
