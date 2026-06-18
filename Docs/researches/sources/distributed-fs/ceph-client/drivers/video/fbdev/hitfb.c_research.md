<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/hitfb.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/hitfb.c

Purpose: implements a platform fbdev driver for the Hitachi HD64461 LCD controller on SuperH systems, including basic hardware blit acceleration and PM.

Important APIs, types, and functions: `hitfb_readw()`/`hitfb_writew()` access HD64461 register offsets. Acceleration helpers wait for `ACCSTATUS`, start the engine, set destination, and program bitblt direction/masks. `hitfb_fillrect()` uses hardware fill for `ROP_COPY`, otherwise falls back to `cfb_fillrect()`. `hitfb_copyarea()` uses hardware bitblt. `hitfb_pan_display()` writes LCD base address. `hitfb_blank()` toggles LCD/display stop bits. `hitfb_setcolreg()` updates hardware palette for 8 bpp or pseudo-palette for 16 bpp. `hitfb_check_var()` clamps mode to fixed x/y, supported bpp, and available memory. `hitfb_set_par()` programs line length and bpp in LCD registers. Probe derives initial geometry from controller registers, allocates fbdev, and registers; suspend/resume blank and toggle clock/standby bits.

Control flow: module init registers a platform driver and synthetic platform device. Probe reads hardware current mode, fills fbdev structures, allocates cmap, and registers. Runtime draw callbacks wait for hardware accelerator completion before programming operations. Suspend blanks display and enters LCD clock stop; resume clears stop bits, waits, and unblanks.

State and persistence: `hitfb_var` and `hitfb_fix` are static templates populated from hardware at probe. Pseudo-palette storage is allocated as `info->par`. Hardware state is in fixed HD64461 registers and framebuffer memory at a fixed offset.

Dependencies and integration points: depends on SuperH machvec, HD64461 register definitions, CPU DAC header, fbdev cfb helpers, and platform scaffolding. It maps screen memory by casting the fixed physical offset rather than using a normal ioremap in this source.

Risks: acceleration wait loops have no timeout. Suspend/resume ignore the `struct device *` and operate global hardware. Probe uses fixed 512 KiB memory and fixed register offsets. `hitfb_resume()` reads/clears `SLCKE_OST` in a local variable, sleeps, then rereads and clears `SLCKE_IST`; only the latter is written, which may be intentional but is subtle.

Test signals: probe against 8 bpp and 16 bpp initial register states, check_var clamping of virtual height, palette programming, pan step for both bpp values, fill/copy accelerator operations and sync wait, blank/unblank bit transitions, and suspend/resume display recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/hitfb.c -->
