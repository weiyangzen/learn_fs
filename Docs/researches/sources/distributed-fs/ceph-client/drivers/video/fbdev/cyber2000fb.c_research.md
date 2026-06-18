# sources/distributed-fs/ceph-client/drivers/video/fbdev/cyber2000fb.c

## Purpose
`cyber2000fb.c` is the PCI fbdev driver for Integraphics CyberPro 2000/2010/5000 adapters. It owns PCI setup, MMIO mapping, VGA/CyberPro register programming, acceleration, color maps, modes, panning, blanking, optional DDC/I2C buses, and resume/remove.

## APIs And Control Flow
`struct cfb_info` embeds `fb_info` and stores register bases, chip ID, clock data, palette cache, memory-control registers, RAMDAC state, pseudo palette, locks, and optional I2C adapters. fb_ops include `cyber2000fb_check_var()`, `cyber2000fb_set_par()`, `cyber2000fb_setcolreg()`, `cyber2000fb_blank()`, `cyber2000fb_pan_display()`, `cyber2000fb_fillrect()`, `cyber2000fb_copyarea()`, and `cyber2000fb_sync()`. Probe removes conflicting apertures, enables PCI, maps BAR0, wakes linear MMIO, reads clocks, initializes hardware, derives VRAM size, selects a mode, registers optional I2C, and registers fbdev.

## State, Dependencies, Integration, Risks
Mode state is encoded in CRTC, PLL, RAMDAC, accelerator, start-address, and cached palette registers. The driver integrates PCI, aperture helpers, fbdev CFB fallback blitters, I2C bit-banging, and `cyber2000fb.h`. Exported `cyber2000fb_enable_extregs()`/`disable_extregs()` let companion modules access extended registers. Risks include `BUG_ON()` if invalid modes reach `set_par()`, acceleration timeout/reset behavior, shared register-bank locking, and partial multi-card support. Tests should cover probe unwind, bpp variants, ypan bounds, DPMS, resume, DDC/I2C, and copy overlap directions.
