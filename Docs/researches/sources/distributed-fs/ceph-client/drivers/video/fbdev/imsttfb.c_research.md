
# sources/distributed-fs/ceph-client/drivers/video/fbdev/imsttfb.c

Purpose: PCI framebuffer driver for IMS TwinTurbo cards with IBM 624 or TI TVP3030 RAMDACs. It programs scan timing, RAMDAC PLL/pixel format, palette, panning, blanking, simple 2D acceleration, debug ioctls, and PCI resource lifecycle.

Important APIs and types: `struct imstt_regvals` stores timing and PLL values; `struct imstt_par` stores mapped device-controller registers, RAMDAC colormap registers, RAMDAC type, and pseudo palette. Mode helpers compute or select register values for IBM/TVP RAMDACs, then `set_imstt_regvals()` writes timing, refresh, stride, endian/byte-swap, and pixel format registers. fb_ops include check-var, set-par, setcolreg, pan, blank, fillrect, copyarea, imageblit fallback, ioctl, mmap/read/write defaults.

Control flow: probe removes conflicting apertures, allocates fb_info, reserves PCI BAR0, determines RAMDAC type from PCI id and Open Firmware name, maps framebuffer/MMIO/cmap windows, and calls `init_imstt()`. Initialization sizes VRAM, clears it, initializes RAMDAC registers, selects a default or PowerMac NVRAM mode, validates supported timing, sets fixed info, programs mode, allocates cmap, and registers fbdev. Mode setting validates bpp/resolution/virtual size, computes register values, selects RGB555/565, writes RAMDAC and controller registers, and updates pixclock.

State and persistence: persistent state includes hardware mappings, selected RAMDAC type, cached mode register values, pseudo palette, and fbdev cmap. Boot options can set inverse/font and PowerMac vmode/cmode in non-module builds.

Dependencies and integration: uses PCI, Open Firmware node lookup, fbdev core, PowerMac NVRAM/macmodes when configured, `aperture_remove_conflicting_pci_devices`, I/O accessors, and user copy helpers for private ioctls.

Risks: private ioctls expose raw register access to userspace and need privilege/context review. Busy-wait loops on BLT status have no timeout. `setclkMHz()` loops until exact integer MHz match for supported hard-coded modes. Probe error unwinding must match mappings. Endianness correction is hardware-specific and easy to regress on non-PowerPC.

Test signals: probe both TT128 and TT3D paths, IBM-vs-TVP register init, supported modes at 8/16/24/32 bpp, panning bounds, blank/unblank, accelerated fill/copy including overlap, ioctl bounds checks, PowerMac NVRAM defaults, and failure injection for each ioremap/register step.
