# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_base.c

## Purpose

`radeon_base.c` is the central fbdev PCI driver for pre-KMS ATI Radeon adapters. It binds supported PCI IDs, maps MMIO and framebuffer apertures, discovers firmware/monitor/PLL state, registers the `fb_info`, implements core fbdev callbacks, and coordinates mode programming, blanking, palette updates, sysfs EDID exposure, acceleration setup, power-management initialization, and teardown. The file is the owner of the `pci_driver` named `radeonfb` and is the integration point that calls into the companion Radeon files for I2C/DDC, monitor probing, acceleration, backlight, and PM.

## Important APIs, Types, And Functions

The PCI ID table uses `CHIP_DEF()` to encode Radeon family and capability flags in `driver_data`; probe decodes these into `rinfo->family`, `has_CRTC2`, `is_mobility`, and `is_IGP`. Global module parameters and boot options include `mode_option`, `monitor_layout`, `noaccel`, `nomodeset`, `ignore_edid`, `mirror`, `default_dynclk`, `nomtrr`, `panel_yres`, `force_dfp`, `force_measure_pll`, `force_sleep`, and `ignore_devlist`.

Register access helpers exported to the driver family include `_radeon_msleep()`, `_OUTREGP()`, `__INPLL()`, `__OUTPLL()`, `__OUTPLLP()`, `_radeon_fifo_wait()`, `radeon_engine_flush()`, and `_radeon_engine_idle()`. These hide MMIO/PLL errata details and provide bounded polling with timeout diagnostics. Firmware helpers include `radeon_map_ROM()`, `radeon_unmap_ROM()`, x86 `radeon_find_mem_vbios()`, OF `radeon_read_xtal_OF()`, `radeon_probe_pll_params()`, and `radeon_get_pllinfo()`.

The fbdev operations are collected in `radeonfb_ops`: `fb_check_var`, `fb_set_par`, `fb_setcolreg`, `fb_setcmap`, `fb_pan_display`, `fb_blank`, `fb_ioctl`, `fb_sync`, accelerated fill/copy/imageblit, default mmap, and default I/O read/write. Mode-state routines are `radeon_save_state()`, `radeon_calc_pll_regs()`, `radeon_write_pll_regs()`, `radeon_write_mode()`, and `radeonfb_set_par()`. Lifecycle routines are `radeonfb_pci_register()`, `radeonfb_pci_unregister()`, `radeonfb_init()`, and `radeonfb_exit()`.

## Control Flow

Module initialization first honors `fb_modesetting_disabled("radeonfb")`, parses boot options when built in, and registers the PCI driver. Probe enables the PCI device, allocates `fb_info` with private `struct radeonfb_info`, initializes locks/timers, decodes chip identity, removes conflicting aperture users, requests BAR 0 and BAR 2, maps MMIO, applies PPC memory-map fixups, identifies VRAM size/type, maps a bounded write-combining framebuffer window, locates BIOS/legacy/OF data, derives PLL information, optionally creates four bit-banged I2C busses, fills `fb_info`, probes monitors, builds the mode database, exposes EDID sysfs files, saves initial registers, initializes PM, registers with fbdev, adds a WC mapping, optionally initializes backlight, and unmaps temporary BIOS ROM.

Mode setting flows through `radeonfb_check_var()` and `radeonfb_set_par()`. `check_var` delegates timing selection to `radeon_match_mode()`, normalizes color depth, computes virtual pitch alignment, validates mapped VRAM capacity, and corrects offsets. `set_par` computes CRTC timings, sync polarity, pitch, PLL values, flat-panel scaler/stretch registers, LVDS/TMDS control, endian surface swappers, and then writes the mode if the adapter is awake. `radeon_write_mode()` blanks unless asked for registers-only restoration, clears common overlay/capture/I2C interrupt registers, writes surface/CRTC/DAC/flat-panel registers, updates PLLs, unblanks, and restores VCLK source.

Blanking uses `radeon_screen_blank()` to disable CRTC sync/display bits and then handle DFP/LCD output-specific sequencing. LCD blank/unblank uses `lvds_timer` for delayed LVDS power transitions and tracks `pending_lvds_gen_cntl`. Panning programs `CRTC_OFFSET`. Palette updates select the primary palette, handle 8/15/16/24/32 bpp mappings, and maintain both hardware palette entries and the first 16-entry pseudo-palette.

## State And Persistence

Persistent runtime state is in `struct radeonfb_info` from `radeonfb.h`: mapped resource bases, BIOS pointer, chip family/flags, VRAM sizing, monitor and EDID pointers, panel info, PLL info, current and initial `struct radeon_regs`, palette caches, WC cookie, PM flags, and LVDS timer state. `rinfo->state` represents the last programmed mode for resume; `rinfo->init_state` snapshots the firmware/entry state for restoration-like behavior and LVDS sequencing. The driver also publishes EDID blobs as binary sysfs attributes tied to the PCI device. State is not persisted across boot; all hardware state is rediscovered on probe and reconstructed on resume.

## Dependencies And Integration Points

This file depends on the Linux PCI, fbdev, sysfs, aperture, MMIO, MTRR/write-combining, timer, and module parameter APIs. It uses Radeon register definitions from `<video/radeon.h>`, chip IDs from `ati_ids.h`, EDID helpers from `../edid.h`, and architecture hooks for PPC/SPARC OF and PPC BootX text. It calls `radeon_create_i2c_busses()`, `radeon_probe_screens()`, `radeon_check_modes()`, `radeonfb_pm_init()`, `radeonfb_pm_exit()`, acceleration functions from `radeon_accel.c`, and optional backlight helpers.

## Risks

The file performs extensive raw MMIO and PLL programming with family-specific errata; ordering and delays are hardware-sensitive. `radeon_probe_pll_params()` disables local interrupts while measuring vertical timing and can fail if display state is odd. BIOS parsing assumes legacy offsets and validates only lightly. `radeonfb_check_var()` adjusts offsets with `v.xres_virtual - v.xres - 1`, which requires care when virtual and visible sizes match. The cleanup path after `register_framebuffer()` failure jumps to `err_unmap_fb` but does not call `radeonfb_pm_exit()`, even though PM was initialized just before `pci_set_drvdata()`. EDID sysfs creation failures are non-fatal, so user-space may miss diagnostics. Runtime globals such as `mirror` and module-wide options affect all adapters rather than being per-device.

## Test Signals

Useful validation signals include PCI bind/unbind on supported Radeon IDs, failure-injection across region request, MMIO map, framebuffer map, cmap allocation, I2C creation, and framebuffer registration paths; boot with `noaccel`, `nomodeset`, `ignore_edid`, `monitor_layout`, `mode_option`, `nomtrr`, and dynamic-clock options; `fbset` mode validation and panning; `FBIO_RADEON_GET_MIRROR`/`SET_MIRROR` on mobility chips; sysfs `edid1`/`edid2` reads; suspend/resume preservation of `rinfo->state`; and visual checks for LVDS/DFP blank/unblank timing.
