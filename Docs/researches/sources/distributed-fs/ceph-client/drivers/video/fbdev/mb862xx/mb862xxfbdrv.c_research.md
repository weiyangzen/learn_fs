# sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xxfbdrv.c

## Purpose
Implements the main Fujitsu MB862xx framebuffer driver for platform/OpenFirmware Lime-style devices and PCI CoralP/Carmine GDCs. It manages resource mapping, chip initialization, fbdev setup, display timing programming, palette operations, panning, blanking, layer-1 capture/overlay ioctls, interrupts, and device removal.

## Important APIs, Types, and Functions
- Timing helpers `h_total()`, `v_total()`, `hsp()`, `vsp()`, and `d_pitch()` compute register values from fbdev var state.
- `mb862xxfb_setcolreg()`, `mb862xxfb_check_var()`, `mb862xxfb_set_par()`, `mb862xxfb_pan()`, `mb862xxfb_blank()`, and `mb862xxfb_ioctl()` implement fbdev operations.
- `mb862xxfb_init_fbinfo()` initializes fixed/variable fbdev state, detects bootloader display configuration, reserves capture buffers, and initializes capture registers.
- `dispregs_show()` exposes selected display/draw/geo register dumps through sysfs.
- `mb862xx_intr()` acknowledges interrupts differently for Carmine and non-Carmine devices.
- `mb862xx_gdc_init()` initializes Lime host-bus devices.
- `coralp_init()`, `init_dram_ctrl()`, and `carmine_init()` initialize PCI variants.
- `of_platform_mb862xx_probe/remove()` and `mb862xx_pci_probe/remove()` handle bus-specific lifecycles.
- `mb862xxfb_init()` and `mb862xxfb_exit()` register the enabled platform and/or PCI drivers.

## Control Flow
Probe allocates `fb_info` with `mb862xxfb_par`, maps framebuffer and MMIO resources, initializes chip-specific register base pointers and clocks, requests IRQ, initializes fb state, allocates color map, programs initial mode, registers the framebuffer, creates the `dispregs` sysfs file, and enables interrupts. `set_par()` optionally installs acceleration for CoralP, disables display, sets clock divider, layer format/dimensions/timings, disables cursors, then re-enables display. Ioctls manipulate layer-1 capture scaling, mirroring, enable state, and capture state. Remove disables display/interrupts, removes sysfs, unregisters fbdev, unmaps resources, releases IRQ/regions, and frees the framebuffer object.

## State and Persistence
`struct mb862xxfb_par` owns all runtime state: resource mapping, chip type, register windows, IRQ, mode defaults, I2C adapter, capture buffer offsets, layer config, and pseudo palette. Hardware state includes display controller timings, palette registers, capture registers, interrupt masks, DRAM controller programming, and clock/reset registers. `pre_init` preserves bootloader display setup when detected or configured.

## Dependencies and Integration Points
Depends on Linux fbdev, PCI, platform/OF, aperture removal, IRQ, MMIO, and optional I2C support. Integrates with `mb862xx_reg.h`, `mb862xxfb.h`, optional acceleration, optional Lime/PCI configs, and user space through fbdev ioctls and sysfs.

## Risks
`mb862xxfb_check_var()` uses `d_pitch(&fbi->var)` while modifying `var`, so validation may use stale state instead of the candidate mode. `mb862xxfb_ioctl()` treats `arg` directly as `int *` for enable commands instead of copying from user, which is unsafe for fb ioctl ABI. `mb862xx_pci_probe()` does not call `mb862xx_i2c_exit()` on all CoralP failure paths after `coralp_init()`. Capture buffer reservation assumes enough mapped VRAM. Some probe errors return the initial `-ENODEV` in platform paths rather than the exact failure.

## Test Signals
Test platform and PCI probe/remove, bootloader-preinitialized and driver-initialized modes, 8/16/32bpp check/set_par paths, palette writes, panning registers, blank/unblank, sysfs register dump, IRQ ack for Carmine and CoralP/Lime, layer-1 ioctl get/set/enable/capture, acceleration on CoralP, and cleanup after mid-probe failures.
