# sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/fbdev.c

## Purpose
`fbdev.c` is the Linux fbdev-facing RIVA/TNT/GeForce framebuffer driver. It binds supported NVIDIA PCI devices, maps MMIO and framebuffer apertures, discovers EDID, initializes the shared RIVA hardware abstraction, registers `struct fb_info`, and implements fbdev operations for mode setting, palette programming, panning, blanking, acceleration, cursor, open/release state save and restore, and module parameters.

## Important APIs, types, and functions
- `rivafb_pci_tbl`, `rivafb_driver`, `rivafb_probe()`, `rivafb_remove()`, `rivafb_init()`, and `rivafb_exit()` form the PCI/module lifecycle.
- `riva_fb_ops` wires fbdev callbacks: `rivafb_open`, `rivafb_release`, `rivafb_check_var`, `rivafb_set_par`, `rivafb_setcolreg`, `rivafb_pan_display`, `rivafb_blank`, accelerated `fillrect`/`copyarea`/`imageblit`, hardware cursor, sync, mmap, and I/O helpers.
- `riva_load_video_mode()` converts `fb_var_screeninfo` timings to VGA CRTC fields plus `RIVA_HW_STATE`, then calls `CalcStateExt()` and `riva_load_state()`.
- `riva_save_state()` and `riva_load_state()` bridge VGA register arrays in `struct riva_regs` with extended state callbacks from `riva_hw.c`.
- `riva_get_EDID_OF()`, `riva_get_EDID_i2c()`, `riva_get_edidinfo()`, and `riva_update_default_var()` derive monitor modes from firmware or DDC.
- Optional backlight support registers a raw backlight device and writes PMC/PCRTC backlight registers.

## Control flow
Probe removes conflicting apertures, allocates `fb_info` plus `struct riva_par`, enables PCI, claims BARs, maps control registers, computes architecture from PCI IDs, sets PRAMIN/PCRTC pointers, calls `riva_common_setup()`, measures VRAM and dclk, maps framebuffer memory write-combined, reads EDID, normalizes initial fb info, registers the framebuffer, and optionally initializes backlight. Mode changes flow through `rivafb_check_var()` for depth/timing validation and virtual-size clamping, then `rivafb_set_par()` unlocks VGA/RIVA registers, calls `riva_load_video_mode()`, resets acceleration and cursor state, and updates `fix` fields.

## State and persistence behavior
Persistent runtime state lives in `struct riva_par`: initial/current VGA plus extended RIVA state, X86 VGA save state, palette caches, EDID pointer, selected CRTC/flat-panel flags, write-combining cookie, cursor reset, and open reference count. Hardware state is saved on first open and restored on last release; remove tears down I2C, backlight, mappings, PCI regions, and allocations. Module parameters (`noaccel`, `flatpanel`, `forceCRTC`, `nomtrr`, `strictmode`, boot mode option, backlight) alter global driver behavior.

## Dependencies and integration points
This file depends on fbdev core, PCI, aperture conflict removal, Open Firmware EDID, optional I2C DDC via `rivafb-i2c.c`, optional PowerMac/backlight hooks, VGA save/restore on X86, and the RIVA hardware abstraction in `riva_hw.c`/`riva_hw.h`. Acceleration writes FIFO method registers defined in `riva_hw.h`; mode calculations rely on `CalcStateExt()`.

## Risks and test signals
Risk areas include legacy direct MMIO/VGA programming, unchecked hardware FIFO waits, mode validation shortcuts when monitor specs are incomplete, hardware cursor endian/packing paths, cleanup on partial probe failures, and known text-mode restore/doublescan issues. Test signals are successful PCI probe/unbind, fbcon display, EDID-derived mode selection, `fbset` mode changes across 8/16/32 bpp, pan/blank behavior, accelerated console scroll/fill/image paths, cursor visibility, suspend-like open/release restore on X86, and I2C/backlight operation when configured.
