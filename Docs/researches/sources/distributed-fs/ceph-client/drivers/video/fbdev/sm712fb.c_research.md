# sources/distributed-fs/ceph-client/drivers/video/fbdev/sm712fb.c

## Purpose
`sm712fb.c` is a PCI fbdev driver for Silicon Motion SM710, SM712, and SM720 display chips. It maps the device framebuffer/MMIO BAR, probes VRAM size, chooses a fixed mode from command-line VESA IDs or platform defaults, writes large static VGA register tables to program timings, exposes truecolor/pseudocolor fbdev operations, implements custom read/write paths for endian conversion, and provides basic PCI suspend/resume.

## Important APIs, types, and functions
- State types and defaults: `struct smtcfb_screen_info`, `struct smtcfb_info`, `smtcfb_var`, `smtcfb_fix`, `struct vesa_mode`, `vesa_mode_table[]`, and the large `vgamode[]` register table.
- Setup and color: `sm7xx_vga_setup()`, `sm712_setpalette()`, `chan_to_field()`, `smtc_setcolreg()`, and `smtc_blank()`.
- I/O and mode programming: `smtcfb_read()`, `smtcfb_write()`, `sm7xx_set_timing()`, `smtc_set_timing()`, `smtcfb_setmode()`, `smtc_check_var()`, and `smtc_set_par()`.
- Resource/lifecycle helpers: `smtc_map_smem()`, `smtc_unmap_smem()`, `sm7xx_init_hw()`, `sm7xx_vram_probe()`, `sm7xx_resolution_probe()`, `smtcfb_pci_probe()`, and `smtcfb_pci_remove()`.
- PM and module registration: `smtcfb_pci_suspend()`, `smtcfb_pci_resume()`, `SIMPLE_DEV_PM_OPS`, `smtcfb_driver`, `sm712fb_init()`, and `sm712fb_exit()`.

## Control flow
Module init rejects disabled modesetting, parses `video=sm712fb:` options, maps recognized VESA strings like `0x317` into `smtc_scr_info`, and registers the PCI driver. Probe removes conflicting firmware framebuffer apertures, enables the PCI function, requests BAR 0, allocates `fb_info` plus `smtcfb_info`, initializes fbops/fix/var/palette, wakes the chip, probes revision and VRAM, maps SM710/712 or SM720 memory layouts, sets chip-specific clocks and PCI-burst registers, selects resolution, maps screen memory, clears VRAM, and registers the framebuffer. `set_par` calls `smtcfb_setmode()`, which adjusts line length and RGB bitfields for 8/16/24/32 bpp, stores width/height/hz, and calls `sm7xx_set_timing()`. The timing writer searches `vgamode[]` for an exact width/height/bpp/60Hz match and writes sequencer, graphics, attribute, CRTC, and video-processor registers.

## State and persistence behavior
Per-device state in `struct smtcfb_info` stores PCI device, fb pointer, chip id/revision, mapped linear framebuffer and register windows, selected dimensions, and a 17-entry pseudo-palette. Global `smtc_regbaseaddress` backs the register helpers from `sm712.h`. `smtc_scr_info` stores boot-option-selected resolution/depth globally. Suspend writes sequencer registers to put memory in self-refresh and disables function blocks, then marks fbdev suspended under `console_lock()`. Resume reinitializes hardware clocks/registers by chip family, re-applies mode programming with `smtcfb_setmode()`, and clears fbdev suspend. Framebuffer contents are not explicitly saved by the driver.

## Dependencies and integration points
The driver depends on PCI, aperture removal, fbdev core, generic IOMEM drawing/mmap helpers, console locking, usercopy, and the local `sm712.h` register helper/mode layout. It supports PCI IDs `0x126f:0x710`, `0x126f:0x712`, and `0x126f:0x720`. The accepted user-facing mode input is VESA BIOS-style IDs in `vesa_mode_table[]`, not arbitrary fb mode strings. On MIPS, default height changes to 1024x600 for Loongson netbook panels.

## Risks
Mode support is static: if `check_var` accepts a resolution/depth with no matching `vgamode[]` entry, `sm7xx_set_timing()` silently writes only the common trailing registers after no table match. SM710/712 VRAM probing assumes 4 MiB and notes that 2 MiB SM712 systems may crash. `smtc_regbaseaddress` is global, making multi-device use unsafe. The SM720 screen-base offset adjustment in unmap subtracts from `screen_base`, which must still correspond to the mapped base. Custom read/write loops operate in 32-bit chunks even for unaligned byte counts and rely on over-read-safe vmalloc/IOMEM access behavior. Suspend does not save VRAM contents.

## Test signals
Tests should cover each supported PCI ID, 8/16/24/32 bpp modes from VESA IDs, default PC and MIPS netbook resolutions, static table lookup for every accepted resolution, palette writes in 8 bpp and pseudo-palette writes in truecolor modes, big-endian read/write and 32 bpp address shifting, framebuffer mmap/read/write correctness for odd byte counts, DPMS blank states, suspend/resume preserving a visible mode, and cleanup after failed map/register paths.
