<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/lxfb_core.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/lxfb_core.c

Purpose: implements the PCI fbdev core for AMD Geode LX video devices. It owns module parameters, mode database selection, fbdev callbacks, PCI BAR mapping, output selection, registration, and PM entry points.

Important APIs, types, and functions: `geode_modedb` contains a broad fixed mode list up to 1920x1440; `olpc_dcon_modedb` supplies the 1200x900 OLPC panel mode. `lxfb_check_var()` rejects missing pixclock, unsupported geometry, unsupported bpp, and insufficient VRAM, then assigns color bitfields. `lxfb_set_par()` selects visual/pitch and calls `lx_set_mode()`. `lxfb_setcolreg()` handles pseudo-palette or hardware palette updates. `lxfb_map_video_memory()` requests BAR0 framebuffer, BAR1 GP, BAR2 display controller, BAR3 VP, maps them, and programs the GLIU memory offset with DC unlock/lock. `lxfb_suspend()` and `lxfb_resume()` call `lx_powerdown()`/`lx_powerup()` under `console_lock()`.

Control flow: init parses `lxfb` options for `noclear`, `nopanel`, `nocrt`, or a mode string, then registers a PCI driver. Probe removes conflicting apertures, allocates fbdev state, maps resources, computes `par->output`, selects OLPC or generic mode database, sets and optionally clears the framebuffer, configures hardware mode, configures VT switching, and registers fbdev.

State and persistence: private state is `struct lxfb_par`; module parameters persist initial VRAM override, no-clear policy, output disable flags, and VT switch behavior. The framebuffer allocation embeds the pseudo-palette after private data. Suspend state is saved/restored in `lxfb_ops.c`.

Dependencies and integration points: depends on PCI, fbdev, aperture conflict handling, console locking, OLPC DCON detection, and LX operation functions. Hardware expectations include BAR layout matching the Geode LX PCI video function and accessible CS5535/LX MSRs.

Risks: `lxfb_map_video_memory()` returns after request/map failures without local unwind, so probe cleanup must infer partial state; requested PCI regions with failed mapping may be retained until the error path. `lxfb_resume()` has the same early-return-without-console-unlock risk as `gxfb_resume()` if `lx_powerup()` fails. Timing validation is limited to nonzero pixclock and maximum geometry. No explicit check rejects disabling both panel and CRT.

Test signals: boot/module option parsing, probe/remove with each BAR failure injected, no-clear behavior, output combinations including `nopanel,nocrt`, OLPC DCON mode selection, color depth validation, suspend/resume including forced `lx_powerup()` failure, and DPMS blank tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/lxfb_core.c -->
