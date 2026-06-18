# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nvidia.c

## Purpose

`nvidia.c` is the main PCI/fbdev driver for legacy NVIDIA graphics adapters. It handles module parameters, PCI probe/remove, framebuffer/MMIO mapping, chipset/architecture selection, fbdev operation registration, initial mode selection, mode validation and programming, colormap and hardware cursor support, panning, blanking, suspend/resume, acceleration selection, and optional backlight initialization. The source was read as a complete 1599-line file.

## Important APIs, Types, and Functions

The driver registers `nvidiafb_driver` with a broad NVIDIA display-class PCI ID table. Key fbdev operations are `nvidiafb_open`, `nvidiafb_release`, `nvidiafb_check_var`, `nvidiafb_set_par`, `nvidiafb_setcolreg`, `nvidiafb_pan_display`, `nvidiafb_blank`, `nvidiafb_cursor`, `nvidiafb_sync`, and accelerated fill/copy/imageblit hooks. Important setup helpers are `nvidia_get_chipset()`, `nvidia_get_arch()`, `nvidia_set_fbinfo()`, `nvidia_init_vga()`, `nvidia_calc_regs()`, `nvidia_save_vga()`, `nvidia_write_regs()`, `nvidia_screen_off()`, `nvidia_panel_tweak()`, CLUT helpers, and cursor-image loading. Power management is implemented by `nvidiafb_suspend_late()` and `nvidiafb_resume()`.

## Control Flow

Initialization parses boot/module options, rejects global modesetting-disabled configurations, and registers the PCI driver. Probe enables PCI I/O/memory, maps BAR0 MMIO, determines chipset/architecture, removes conflicting apertures, allocates `fb_info` and pixmap memory, requests PCI regions, stores module option state into `struct nvidia_par`, calls `NVCommonSetup()`, computes framebuffer usable/scratch/cursor regions, maps framebuffer write-combined, enables write-combining unless `nomtrr`, initializes `fb_info`, validates the initial mode, saves VGA state, registers the framebuffer, optionally initializes backlight, and logs the device. Mode set (`nvidiafb_set_par`) locks/unlocks registers, initializes VGA defaults, computes register state, blanks the screen, writes registers, sets start address, installs acceleration or software fbops, resets cursor state, and unblanks. Remove tears down backlight, unregisters fbdev, removes write-combining, unmaps memory, frees EDID mode data, deletes I2C buses, releases PCI regions, frees pixmap memory, and releases `fb_info`.

## State and Persistence Behavior

Per-device state is `struct nvidia_par` plus fbdev `info` state. `SavedReg` is captured at probe/suspend, `initial_state` is captured on first open and restored on last release, and `ModeReg` is regenerated for each mode. `open_count` gates VGA save/restore. `pm_state` tracks suspend state. Framebuffer contents persist in VRAM while mapped; hardware registers persist until mode changes, suspend/resume, release restore, or remove. Module parameters persist globally for all probed devices.

## Dependencies and Integration Points

The file depends on PCI, aperture removal, fbdev helpers, console locking, backlight, write-combining, optional BootX text update, and all NVIDIA local modules (`nv_setup`, `nv_hw`, `nv_accel`, `nv_i2c`, `nv_of`, `nv_backlight`). It exposes a standard fbdev device to userspace and console layers and competes with DRM/native drivers for the same aperture.

## Risks and Edge Cases

Probe error paths must unwind partially initialized I2C, mode databases, MMIO mappings, PCI regions, and pixmap memory in the correct order. `nvidia_bl_exit()` is called unconditionally on remove even if backlight registration was skipped by parameter or hardware; this relies on safe handling of a NULL/no device. Mode validation mutates requested bpp/resolution and may cap flat-panel modes to panel size. Hardware cursor is disabled by default and limited to 32x32. Acceleration can be disabled by parameter or dynamically after lockup. The broad PCI ID table requires accurate architecture detection to avoid programming unsupported chips.

## Test Signals

Build and boot with representative NV04/NV10/NV20/NV30/NV40 IDs, test probe failure unwinds by injecting mapping/region/cmap failures, validate mode setting at 8/16/32 bpp and flat-panel bounds, exercise panning, colormap, blanking, open/release VGA restore, suspend/resume, backlight parameter on/off, `noaccel`, `hwcur`, `nomtrr`, and remove/reprobe cycles.
