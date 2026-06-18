# sources/distributed-fs/ceph-client/drivers/video/fbdev/tridentfb.c

## Purpose
`tridentfb.c` is a PCI fbdev driver for Trident TGUI, 3DImage, Blade, BladeXP, and CyberBlade graphics chips. It programs VGA and Trident extended registers, supports flat-panel centering/stretching, DDC probing, panning, DPMS blanking, palette handling, and chip-family-specific 2D acceleration.

## Important APIs, Types, and Functions
`struct tridentfb_par` stores MMIO base, chip id, flat-panel flag, pseudo palette, acceleration function pointers, engine state, and DDC adapter data. Important helper groups include chip classifiers (`is_oldclock()`, `is_blade()`, `is_xp()`, `is3Dchip()`, `iscyber()`), DDC bit-bang callbacks, acceleration implementations for Blade, XP, Image, and TGUI families, VGA/MMIO helpers, `get_nativex()`, `set_lwidth()`, `screen_stretch()`, `screen_center()`, `set_screen_start()`, `set_vclk()`, `get_memsize()`, `tridentfb_check_var()`, `tridentfb_set_par()`, `tridentfb_setcolreg()`, `tridentfb_blank()`, `trident_pci_probe()`, and `trident_pci_remove()`.

## Control Flow
Probe removes conflicting apertures, enables PCI with devres, allocates fbdev state, refines `TGUI9660` revisions to specific chip ids, installs chip-family acceleration callbacks, requests/maps MMIO BAR1, enables MMIO, detects framebuffer size from registers or module options, requests/maps framebuffer BAR0, detects flat-panel/native width, configures fbdev flags and pixmap, creates a DDC bus and optionally selects an EDID best mode, falls back to `640x480-8@60`, allocates cmap, and registers fbdev. Mode set computes VGA timings, enables extended register access, handles panel center/stretch, writes CRTC/graphics/attribute/clock registers, configures bpp and pitch, initializes acceleration, and updates visual/cmap length.

## State and Persistence
Runtime state includes mapped MMIO/framebuffer, selected chip id, DDC adapter, pixmap buffer, pseudo palette, fbdev cmap, global module options, and selected acceleration callbacks. Hardware state includes Trident extended registers, VGA CRTC/SEQ/GFX/ATTR registers, PLL, DPMS registers, flat-panel stretch/center bits, graphics engine state, framebuffer contents, and DAC palette. No state is persisted.

## Dependencies and Integration Points
Dependencies include PCI, aperture helpers, fbdev mode/EDID/cmap APIs, `video/vga.h`, `video/trident.h`, I2C bit-banging, and cfb fallback drawing. It integrates with module/boot options for mode, bpp, acceleration, memory size adjustment, flat panel/CRT selection, native width, centering, and stretching.

## Risks and Edge Cases
Acceleration wait loops are mostly busy waits; XP has a software timeout/reset but other engines may spin. The file mutates global `tridentfb_fix`, so multi-device behavior can inherit the most recent chip's acceleration id. Some error paths do not release requested memory regions explicitly. `crt` option parsing sets `fp = 0` rather than `crt = 1`. Panel handling depends on register heuristics and user overrides. Mode validation rewrites 24 bpp to 32 bpp and adjusts virtual width for acceleration pitch constraints.

## Test Signals
Test each supported chip family, TGUI9660 revision remapping, DDC success/failure, EDID and fallback mode selection, 8/16/32 bpp validation, panning offsets, flat-panel center/stretch, memory-size overrides, noaccel fallback, accelerated fill/copy/imageblit, DPMS states, palette/pseudo-palette programming, and probe/remove resource cleanup.
