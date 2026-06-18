# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeonfb.h

## Purpose

`radeonfb.h` is the private interface for the Radeon fbdev driver family. It defines chip families, feature and errata flags, monitor/DDC/connector enums, PLL/panel/mode register state structures, the central `struct radeonfb_info`, MMIO/PLL/BIOS access macros, inline utility functions, engine helper macros, and cross-file function prototypes. It is the contract shared by `radeon_base.c`, `radeon_monitor.c`, `radeon_i2c.c`, `radeon_pm.c`, acceleration code, and optional backlight code.

## Important APIs, Types, And Functions

`enum radeon_family` identifies supported Radeon generations from original Radeon through RV/R/R/RS families up to R420/RS480. `IS_RV100_VARIANT()` and `IS_R300_VARIANT()` group family behavior. `enum radeon_chip_flags` defines driver-data bits for mobility, IGP, CRTC2, and family masking. `enum radeon_errata` describes PLL dummy read, PLL delay, and R300 clock-gating quirks. `enum radeon_montype`, `enum ddc_type`, and `enum conn_type` define monitor, DDC port, and connector vocabulary.

`struct pll_info` stores clock bounds and reference/system/memory clocks. `struct radeon_regs` is the large register snapshot and programmed-mode record, covering common registers, surface registers, CRTC1/CRTC2, flat-panel/LVDS/TMDS, PLLs, computed PLL values, and palette validity. `struct panel_info` stores native flat-panel timing, sync polarity, power delay, and BIOS PLL dividers. Optional `struct radeon_i2c_chan` wraps a bit-banged I2C adapter. `enum radeon_pm_mode` declares no PM, D2, and D3-cold/off resume capability. `struct radeonfb_info` ties all runtime state together.

The macros `INREG*`, `OUTREG*`, `OUTREGP`, `INPLL`, `OUTPLL`, `OUTPLLP`, and `BIOS_IN*` are central to all implementation files. Inline helpers include `round_div()`, `var_to_depth()`, and `radeon_get_dstbpp()`. The header declares exported functions for I2C, PM, monitor probing, acceleration, blanking/mode writing, and backlight.

## Control Flow

This header has no runtime control flow by itself, but it shapes every code path. `radeon_base.c` allocates `struct radeonfb_info` as fbdev private data and progressively fills fields during PCI probe. Monitor probing writes monitor and panel fields; mode setting writes `state`, pitch, bpp, depth, palette, and timer fields; PM reads and writes `save_regs`, `dynclk`, `pm_mode`, `reinit_func`, `asleep`, and `lock_blank`; I2C code fills `i2c[4]` when configured. The access macros assume each function has a local variable named `rinfo`, so callers are constrained to that naming convention.

## State And Persistence

The header defines all important in-memory persistence for the driver. `struct radeonfb_info` retains hardware mappings, PCI device pointer, optional OF node, BIOS mapping pointer, framebuffer aperture layout, chip identity, VRAM characteristics, current and initial register snapshots, monitor/EDID state, panel timing, PLL information, write-combining cookie, PM mode, and delayed LVDS timer state. None of this is persistent across module unload; it is reconstructed on probe. `struct radeon_regs` is the main persistence unit used across mode switches and resume.

## Dependencies And Integration Points

Dependencies include Linux module/kernel/scheduler/delay/PCI/fb headers, optional I2C headers, architecture I/O, SPARC prom when enabled, and `<video/radeon.h>`. All companion files include this header. External consumers are limited because the header is local to the driver directory, but its function prototypes bind the Radeon fbdev submodules together and allow `radeon_base.c` to assemble `fb_ops` from acceleration and PM helpers.

## Risks

The register and PLL macros are convenience-oriented and depend on a local `rinfo` symbol, which makes misuse easy during refactoring. PLL access comments explicitly state that locking was intentionally removed and relies on fbdev/console serialization rather than internal locking; any new caller from IRQ or concurrent context would be dangerous. `BIOS_IN*` macros assume `rinfo->bios_seg` is valid and do not bounds-check offsets. `struct radeon_regs` includes fields not always saved or programmed by every path, so additions require careful synchronization with save/restore and PM code. `save_regs[100]` is opaque and should ideally be replaced with named fields before broad changes.

## Test Signals

Header-level validation is mostly compile and integration coverage: build with and without `CONFIG_FB_RADEON_I2C`, `CONFIG_FB_RADEON_PM`, `CONFIG_FB_RADEON_BACKLIGHT`, PPC, SPARC, and big-endian options; ensure every prototype has exactly one matching implementation under the relevant config; run sparse or Coccinelle checks for invalid `__iomem` access; and verify all MMIO/PLL macro users have a local `rinfo`. Runtime signals include successful mode set, blank, I2C, PM, and acceleration paths because they all depend on this shared contract.
