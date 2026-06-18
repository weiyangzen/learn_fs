
# sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_main.h

Purpose: shared interface header for the i810 fbdev implementation. It declares cross-file timing, acceleration, ring-buffer, front-buffer, and optional I2C/DDC helpers used by `i810_main.c`.

Important APIs: timing hooks are `round_off_xres()`, `round_off_yres()`, `i810_get_watermark()`, `i810fb_encode_registers()`, and `i810fb_fill_var_timings()`, supplied by either `i810_dvt.c` or `i810_gtf.c`. Acceleration hooks are `i810fb_fillrect()`, `i810fb_copyarea()`, `i810fb_imageblit()`, `i810fb_sync()`, `i810fb_init_ringbuffer()`, and `i810fb_load_front()`. Optional I2C hooks are real declarations under `CONFIG_FB_I810_I2C` and inline stubs otherwise.

Control flow and integration: the header defines the compile-time timing lane via `IS_DVT`: DVT when `CONFIG_FB_I810_GTF` is off, GTF otherwise. It also provides `flush_cache()` as an x86 `wbinvd` inline for ring enabling and a no-op elsewhere.

State and persistence: this header owns no runtime state, but it shapes which implementation files satisfy symbols and how missing I2C support behaves. The I2C stub returns failure (`1`), causing main initialization to continue without EDID.

Dependencies: expects `struct fb_var_screeninfo` from fbdev and `struct i810fb_par` from `i810.h` to be visible before use by including C files.

Risks: because DVT/GTF provide the same symbol names, build configuration must include exactly one suitable implementation. `flush_cache()` uses a heavy whole-cache writeback/invalidate on x86; any future call sites should remain rare and hardware-specific.

Test signals: compile both `CONFIG_FB_I810_GTF` and non-GTF builds, with and without `CONFIG_FB_I810_I2C`, and ensure all declared symbols resolve and mode initialization follows the intended path.
