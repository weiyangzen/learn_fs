# sources/distributed-fs/ceph-client/drivers/video/fbdev/dnfb.c

## Purpose
`dnfb.c` is a fixed-mode Apollo monochrome framebuffer driver exposing a 1280x1024 1bpp display.

## APIs And Control Flow
The driver defines Apollo register addresses and ROP/control bits, fixed `dnfb_var` and `dnfb_fix`, `dnfb_blank()`, custom `dnfb_copyarea()`, and `dnfb_probe()`. Probe allocates `fb_info`, installs ops, sets the fixed memory address as `screen_base`, allocates a 2-entry cmap, registers fbdev, then initializes hardware registers. Init only proceeds on `MACH_IS_APOLLO` and creates a platform device.

## State, Dependencies, Integration, Risks
State is fixed hardware register state and fbdev's cmap/var/fix data; there is no remove path. Dependencies are m68k Apollo/Amiga hardware headers, platform devices, and fbdev CFB helpers. The copyarea mask/direction logic is the main risk, especially for overlapping and unaligned copies. Tests should cover blank/unblank, forward/backward copy, odd x offsets, one-word and multi-word copies, and non-Apollo init rejection.
