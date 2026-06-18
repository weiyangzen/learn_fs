<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/gxfb_core.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/gxfb_core.c

Purpose: implements the PCI fbdev core for AMD/National Geode GX video devices with virtual PCI BARs for framebuffer, graphics processor, display controller, and video/flat-panel registers.

Important APIs, types, and functions: mode databases `gx_modedb` and OLPC `gx_dcon_modedb` feed `get_modedb()`. `gxfb_check_var()` validates geometry, bpp, memory capacity, and color fields. `gxfb_set_par()` computes visual and pitch, then calls `gx_set_mode()`. `gxfb_setcolreg()` updates the pseudo-palette or calls `gx_set_hw_palette_reg()`. `gxfb_map_video_memory()` maps BAR3 video processor, BAR2 display controller, BAR1 graphics processor, and BAR0 framebuffer, then programs `DC_GLIU0_MEM_OFFSET`. `gxfb_suspend()`/`gxfb_resume()` wrap `gx_powerdown()`/`gx_powerup()` under `console_lock()`. `gxfb_probe()` selects CRT versus flat-panel output by reading `MSR_GX_GLD_MSR_CONFIG`, finds a mode, clears VRAM, sets hardware, configures VT switching, and registers fbdev.

Control flow: init optionally parses `gxfb` boot options, checks `fb_modesetting_disabled()`, and registers a PCI driver. Probe allocates `fb_info`, maps all BARs, derives output type, chooses the normal or DCON mode table, programs a selected mode, then registers the framebuffer. PM callbacks save/restore hardware through `suspend_gx.c`; fbdev callbacks route to mode, palette, and blank helpers in `video_gx.c`.

State and persistence: `struct gxfb_par` stores mappings, output state, and suspend snapshots. The `vram` module parameter can override `gx_frame_buffer_size()`. `vt_switch` is persisted via `pm_set_vt_switch()`. The pseudo-palette is embedded after private data in the framebuffer allocation.

Dependencies and integration points: depends on PCI, fbdev, console suspend coordination, aperture removal, OLPC DCON detection, x86 MSR access, CS5535 definitions, and `gxfb.h` operations. It assumes firmware supplies a virtual PCI header with a fixed BAR layout and a 16 MiB framebuffer unless overridden.

Risks: mapping failure paths in `gxfb_map_video_memory()` do not unwind prior requested BARs before returning to the caller, though the probe error path later handles fields that were stored. `gxfb_resume()` returns after a failed `gx_powerup()` without unlocking `console_lock()`, which is a potential deadlock path in this version. Timing validation is still a FIXME. The code assumes BIOS/firmware virtual PCI setup and may misbehave on nonconforming platforms.

Test signals: probe/remove on emulated BAR failure permutations, suspend/resume while framebuffer is active, OLPC DCON mode selection, mode validation across 8/16/32 bpp, palette writes in pseudo and truecolor, and DPMS blank modes. Locking tests should cover the `gx_powerup()` failure path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/gxfb_core.c -->
