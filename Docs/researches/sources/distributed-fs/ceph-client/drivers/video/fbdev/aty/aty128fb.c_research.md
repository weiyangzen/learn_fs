# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/aty128fb.c

## Purpose
`aty128fb.c` is the fbdev PCI driver for ATI Rage128 and Rage128 Pro adapters. It maps framebuffer and MMIO BARs, obtains PLL/memory timing information, programs CRTC/PLL/DDA FIFO registers for fbdev modes, supports palette and pseudo-palette updates, optional acceleration engine initialization, M3 LCD/CRT mirroring and backlight, panning, blanking, and PCI power management.

## Important APIs, types, and functions
Important private structures include `struct aty128fb_par`, `struct aty128_crtc`, `struct aty128_pll`, `struct aty128_ddafifo`, `struct aty128_constants`, and `struct aty128_meminfo`. Device matching is in `aty128_pci_tbl`; driver registration is through `aty128fb_driver`.

The fbdev entry points are `aty128fb_check_var()`, `aty128fb_set_par()`, `aty128fb_setcolreg()`, `aty128fb_pan_display()`, `aty128fb_blank()`, `aty128fb_ioctl()`, and `aty128fb_sync()`. Hardware helpers include MMIO/PLL accessors, `register_test()`, FIFO/idle wait functions, `aty128_reset_engine()`, `aty128_init_engine()`, `aty128_map_ROM()`, `aty128_get_pllinfo()`, `aty128_timings()`, `aty128_var_to_crtc()`, `aty128_var_to_pll()`, `aty128_ddafifo()`, and CRTC/PLL/FIFO programming functions.

## Control flow
Module init checks `fb_modesetting_disabled("aty128fb")`, parses boot options when built in, and registers the PCI driver. Probe removes conflicting apertures, enables the PCI device, reserves framebuffer and MMIO BARs, allocates `fb_info`, maps MMIO and VRAM, reads VRAM size, verifies register writes, maps the BIOS or searches legacy x86 ROM space, extracts PLL info when available, fills timing defaults, stores drvdata, and calls `aty128_init()`.

`aty128_init()` identifies the chip, selects a default mode from platform options or mac modes, validates it with `aty128fb_check_var()`, configures DAC and bus-master state, allocates the colormap, initializes the acceleration engine, registers the framebuffer, and optionally registers backlight support. Mode validation decodes `fb_var_screeninfo` into CRTC, PLL, and FIFO register values, checking non-interlaced mode, x alignment, VRAM size, PLL limits, and memory FIFO range. `set_par()` clears interfering blocks, disables video, programs CRTC/PLL/FIFO, applies endian aperture settings, re-enables video, updates `fix`, handles M3 output enables, and initializes acceleration if requested.

## State and persistence behavior
Runtime state persists in `struct aty128fb_par`: register base, VRAM size, chip generation, memory timings, cached CRTC/PLL/FIFO values, palette components, pseudo palette, output routing, suspend flags, FIFO accounting, MTRR/write-combining cookie, and PCI device pointer. Hardware state is stored in Rage128 registers and restored on resume by re-running mode setup, panning, and colormap programming. Framebuffer contents persist in mapped VRAM while the device remains powered.

## Dependencies and integration points
The driver integrates with PCI, aperture conflict removal, fbdev, architecture I/O mapping, optional PowerMac mode/backlight/AGP hooks, optional BootX text update, backlight core, MTRR/write-combining helpers, and Rage128 register definitions from `<video/aty128.h>`.

## Risks and edge cases
The FIFO wait loops reset the engine after long busy polling but have no bounded failure return. BIOS parsing accepts fallback guessed timings when ROM lookup fails. Probe cleanup must balance multiple BAR reservations and mappings. The driver disables bus mastering and I2C paths during mode set, which can affect expectations if future code adds DDC. `aty128fb_setcolreg()` has special 565 handling with cached red/green/blue arrays; palette regressions are easy at 15/16 bpp. M3 LCD/CRT power sequencing and PM paths are platform-specific and guarded by global suspend/blank flags.

## Test signals
Build and bind against Rage128 PCI IDs, verify BAR reservations and register test, boot with and without BIOS PLL data, run fb modes at 8/15/16/24/32 bpp, test panning x alignment and 24 bpp offset handling, verify palette and pseudo-palette colors, exercise blank states and M3 mirror ioctls, test suspend/resume on PowerMac and non-PowerMac PCI paths, validate backlight registration on supported M3 systems, and run fb_sync after accelerated text operations if acceleration is enabled.
