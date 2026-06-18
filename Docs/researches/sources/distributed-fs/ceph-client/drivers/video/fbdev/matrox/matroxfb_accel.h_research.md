## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_accel.h

Purpose: `matroxfb_accel.h` declares the Matrox acceleration initializer used by the base mode-setting path.

Important APIs: `matrox_cfbX_init(struct matrox_fb_info *minfo)` configures accelerator registers and fbops for the current framebuffer var. It is implemented in `matroxfb_accel.c`.

Control flow: no executable flow in the header. The base driver includes it and calls the function after mode programming so copy/fill/image operations match the new bpp and pitch.

State and persistence: no state is owned here. The declared function mutates `minfo->fbops`, `minfo->accel`, and hardware drawing registers.

Dependencies and integration points: includes `matroxfb_base.h` for `struct matrox_fb_info`. It is part of the core `CONFIG_FB_MATROX` object set, so the declaration should always resolve when the base driver is built.

Risks: if callers invoke the initializer before `fbcon.var`, `curr.ydstorg`, MMIO mappings, and capability flags are valid, it can program wrong accelerator state. The header offers no additional type abstraction, so it assumes internal Matrox driver ordering discipline.

Test signals: build core Matrox configs and exercise mode switches that call `matrox_cfbX_init()`. Runtime behavior should show correct fbops selection when `FB_ACCELF_TEXT` is toggled and safe fallback to cfb helpers when acceleration is disabled.
