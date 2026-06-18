# sources/distributed-fs/ceph-client/drivers/video/fbdev/fm2fb.c

## Purpose
`fm2fb.c` supports BSC FrameMaster II and Rainbow II Zorro framebuffers: simple fixed-timing 32bpp truecolor Amiga cards.

## APIs And Control Flow
The driver defines fixed PAL/NTSC `fb_var_screeninfo`, `fb_fix_screeninfo`, `fm2fb_blank()`, `fm2fb_setcolreg()`, `fm2fb_probe()`, option parsing, and Zorro registration. Probe requests the Zorro device, allocates fb_info and cmap, maps the 2MB aperture, initializes the control register, draws EBU color bars, selects a mode, and registers fbdev.

## State, Dependencies, Integration, Risks
Global state is the control register pointer and selected mode. It depends on Zorro bus, Amiga I/O mapping, and fbdev default IOMEM ops. Risks include color-bar writes through a physical-address-derived pointer rather than `screen_base`, no remove path, and unblank always setting non-interlace. Tests should cover Zorro unwind, PAL/NTSC parsing, blank register values, pseudo palette writes, and mapping behavior.
