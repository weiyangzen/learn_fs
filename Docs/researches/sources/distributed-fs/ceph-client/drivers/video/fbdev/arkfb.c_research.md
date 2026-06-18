# sources/distributed-fs/ceph-client/drivers/video/fbdev/arkfb.c

## Purpose
`arkfb.c` is a PCI framebuffer driver for ARK 2000PV VGA hardware with an ICS5342 RAMDAC. It maps the linear framebuffer, programs VGA/SVGA timing and ARK extended registers, controls the RAMDAC pixel mode and PLL, implements fbdev mode setting, and provides optimized 4bpp image/fill paths.

## Important APIs, Types, and Functions
`struct arkfb_info` stores memory clock metadata, write-combining cookie, RAMDAC object, saved VGA state, open mutex/refcount, and pseudo-palette. Supported fb formats are described by `arkfb_formats`; timing register mappings are described by `ark_timing_regs` and associated `vga_regset` arrays.

The RAMDAC abstraction uses `struct dac_ops` and `struct dac_info`, with ICS5342 implementation in `ics5342_set_mode()`, `ics5342_set_freq()`, `ics5342_release()`, and `ics5342_init()`. Driver fbops include `arkfb_open`, `arkfb_release`, `arkfb_check_var`, `arkfb_set_par`, `arkfb_setcolreg`, `arkfb_blank`, `arkfb_pan_display`, `arkfb_fillrect`, `arkfb_imageblit`, and cfb copyarea helpers. PCI lifecycle is handled by `ark_pci_probe`, `ark_pci_remove`, `ark_pci_suspend`, and `ark_pci_resume`.

## Control Flow
Module init rejects operation if modesetting is disabled, accepts a boot/module `mode_option`, and registers a PCI driver for device `0xEDD8:0xA099`. Probe removes conflicting aperture users, ignores secondary VGA devices, allocates `fb_info`, enables the PCI device, requests regions, initializes the ICS5342 DAC, maps BAR0 write-combining, derives a VGA I/O base, detects memory size from sequencer register 0x10, finds the startup mode, allocates a 256-entry colormap, registers the framebuffer, stores driver data, and adds write-combining via `arch_phys_wc_add()`.

Open saves VGA mode/fonts/cmap on the first open; release restores VGA state and resets the DAC when the last opener exits. Mode setting unlocks CRT registers, blanks the display, resets VGA register groups, enables ARK linear framebuffer/full memory access, programs the FIFO threshold and offset, selects a mode-specific sequencer/CRT/DAC path, computes and writes the pixel clock, programs SVGA timings, clears visible memory, and unblanks the device.

## State and Persistence
Runtime state resides in `struct arkfb_info` plus hardware registers. The saved VGA state persists only while the framebuffer is open and is restored on last release. The framebuffer memory mapping and write-combining cookie persist until remove. Module parameters `mode_option` and `threshold` influence default mode and FIFO threshold for the module lifetime.

## Dependencies and Integration Points
The driver depends on PCI, fbdev core, aperture conflict removal, VGA/SVGA helper APIs from `linux/svga.h` and `video/vga.h`, cfb drawing helpers, console locking for suspend/resume, architecture write-combining helpers, and VGA primary-device detection. It integrates with users through fbdev, with system firmware/console state through VGA save/restore, and with PCI resource management.

## Risks and Edge Cases
The code deliberately ignores secondary VGA devices because it has no VGA arbitration support. Memory size is read from an ARK sequencer register with a FIXME; wrong firmware state could produce an incorrect size. Several optimized 4bpp paths assume 8-pixel alignment and fall back only when the wrapper detects unsupported cases. `pci_disable_device()` is commented out in error/remove paths, which is a legacy choice but can leave enable state to PCI core/system policy. Suspend/resume only reprograms hardware when `ref_count` is nonzero, so closed framebuffers may resume without a refreshed mode until reopened. RAMDAC mode/frequency failures in `arkfb_set_par()` may leave previous clocking active while other registers change.

## Test Signals
Validation should include probe on primary and secondary VGA placements, aperture conflict removal with VGA/DRM firmware drivers, default and user-specified modes, text mode, 4bpp packed/interleaved, 8/16/24/32bpp modes, DAC PLL boundary frequencies, palette programming, blank/unblank/powerdown, ypan, first-open save and last-close restore, suspend/resume with open and closed fb, and FIFO threshold variations.
