# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/atyfb_base.c

## Purpose

`atyfb_base.c` is the core Linux fbdev driver for ATI Mach64 adapters. It owns the `atyfb` PCI/Atari lifecycle, framebuffer registration, fbdev operations, chip identification, mode validation, CRTC programming, PLL/DAC dispatch, palette programming, panning, vblank waits, suspend/resume, optional LCD/backlight handling, and cleanup. The file is the integration point for the Mach64-specific helper files: acceleration is provided by `mach64_accel.c`, CT-family PLL support by `mach64_ct.c`, GX-family DAC/clock support by `mach64_gx.c`, and hardware cursor support by `mach64_cursor.c`.

## Important APIs, Types, and Functions

The exported fbdev surface is `atyfb_ops`: `atyfb_open()`, `atyfb_release()`, `atyfb_check_var()`, `atyfb_set_par()`, `atyfb_setcolreg()`, `atyfb_pan_display()`, `atyfb_blank()`, `atyfb_ioctl()`, accelerated drawing callbacks, mmap, and sync. `struct atyfb_par` from `atyfb.h` is the central per-device state, holding MMIO bases, selected DAC/PLL ops, CRTC/PLL snapshots, chip features, memory clock limits, acceleration flags, vblank state, IRQ state, PCI resources, saved mode, and optional LCD fields.

Important internal functions include `correct_chipset()` for PCI id and revision matching, `aty_get_crtc()` and `aty_set_crtc()` for hardware register snapshots/programming, `aty_var_to_crtc()` and `aty_crtc_to_var()` for fbdev timing conversion, `atyfb_get_pixclock()` for LCD-aware pixel-clock selection, `aty_init()` for full device initialization, `atyfb_setup_generic()` and `atyfb_setup_sparc()` for PCI resource mapping, `atyfb_pci_probe()` and `atyfb_pci_remove()` for PCI driver binding, `atyfb_blank()` for display power state, and `atyfb_reboot_notify()` for DMI-specific hardware restore on reboot.

## Control Flow

Probe removes conflicting apertures, enables the PCI device, reserves the framebuffer BAR, allocates `fb_info`, maps MMIO and framebuffer apertures, verifies the chipset, optionally reads BIOS/LCD timing data, then calls `aty_init()`. Initialization selects GX or CT DAC/PLL operations, derives clock limits and memory type, saves the incoming CRTC/PLL state, determines real VRAM size, configures MMIO aperture length and write-combining, chooses an initial mode from platform defaults, module parameters, BIOS LCD timings, or `default_var`, validates it through `atyfb_check_var()`, optionally initializes the hardware cursor, allocates the colormap, registers the framebuffer, and registers a backlight device for supported mobile chips.

Mode changes flow through `atyfb_check_var()` and `atyfb_set_par()`. The check path converts fbdev geometry into Mach64 CRTC fields and asks the selected PLL ops to validate the requested pixel clock. The set path repeats the conversion, programs CRTC, DAC, PLL, memory-control bits, DAC mask, line length, visual type, and acceleration engine state. LCD-enabled paths rewrite timing and stretching registers so smaller modes can be scaled or replicated on the panel.

Panning updates `info->var` offsets, recomputes `CRTC_OFF_PITCH`, and either defers the register write to the next vblank interrupt or writes immediately. `FBIO_WAITFORVSYNC` enables vblank IRQs and waits on `par->vblank.wait`. Suspend blanks, resets/parks the engine, optionally powers down PowerMac LCD hardware, marks `par->asleep`, and resumes by restoring memory/PLL state, resetting the mode, and unblanking.

## State and Persistence Behavior

Driver state is volatile and per-device. `par->saved_crtc`, `par->saved_pll`, and `par->mem_cntl` preserve the firmware/boot mode so remove, failed init, reboot notification, and some suspend/resume paths can restore hardware. Module parameters (`noaccel`, `nomtrr`, `vram`, `pll`, `mclk`, `xclk`, `comp_sync`, `mode`, `backlight`, and PowerMac `vmode`/`cmode`) influence initialization but are not persisted by the driver.

Hardware state is persistent only in registers: CRTC timing, PLL programming, memory refresh, DAC palette, LCD power, and acceleration registers. User-visible persistent effects are limited to current framebuffer mode and optional backlight state while the driver is loaded. The driver does not store configuration on disk.

## Dependencies and Integration Points

The file depends on fbdev core, PCI, aperture arbitration, MMIO/ioremap helpers, interrupts/wait queues, console locking, backlight core, DMI reboot notifiers, PowerMac/Atari/Sparc platform hooks, and `<video/mach64.h>` register definitions. It integrates with helper ops through `struct aty_dac_ops`, `struct aty_pll_ops`, and acceleration/cursor functions declared in `atyfb.h`.

## Risks and Edge Cases

The code programs old hardware directly and relies on many chipset-specific magic constants. LCD scaling code is complex and can reject modes larger than the panel unless CRT is enabled. `atyfb_ops` is a static global and `atyfb_set_par()` mutates its `fb_sync` pointer based on one device's acceleration state, which is risky if multiple adapters with different settings are present. Several resource-failure paths rely on staged cleanup and should be fault-injected. Vblank IRQ enable/disable races are controlled with `irq_flags` and `int_lock`, but delayed pan state depends on interrupts being delivered. BIOS parsing uses legacy x86 memory mappings and fixed offsets, so malformed ROM data is a risk.

## Test Signals

Useful coverage includes build tests across PCI, Sparc, PowerMac, Atari, CT, GX, LCD, backlight, and cursor configurations; probe/remove with auxiliary and in-BAR register apertures; mode validation for 8/15/16/24/32 bpp, double-scan/interlace, LCD panel scaling, and VRAM limits; acceleration enabled/disabled transitions; panning with and without `FB_ACTIVATE_VBL`; `FBIO_WAITFORVSYNC` timeout and IRQ delivery; suspend/resume and reboot notifier restore; palette programming in pseudocolor and directcolor modes; and fault injection for ioremap, memory-region, colormap, IRQ, and framebuffer registration failures.
