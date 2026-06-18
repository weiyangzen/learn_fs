
# sources/distributed-fs/ceph-client/drivers/video/fbdev/leo.c

Purpose: Open Firmware platform framebuffer driver for Sun LEO/SX graphics on SBUS-style systems. It maps the LEO register/framebuffer windows, initializes window IDs and draw engine state, exposes fbdev color/blank/pan operations, and delegates SBUS mmap/ioctl handling.

Important APIs and types: hardware structs model cursor, LX kernel command register, LC/LD register banks, SS1 misc, and `struct leo_par` caches mapped register pointers, CLUT data, extent, flags, and IO-space id. fb_ops are built with `FB_DEFAULT_SBUS_OPS(leo)`, plus `leo_setcolreg()`, `leo_blank()`, and `leo_pan_display()`. Private helpers include `leo_wait()`, `leo_switch_from_graph()`, `leo_wid_put()`, `leo_init_wids()`, `leo_init_hw()`, and `leo_unmap_regs()`.

Control flow: probe allocates fb_info, reads OF geometry through `sbusfb_fill_var()`, maps LC/LD/LX/cursor/framebuffer regions at fixed offsets, initializes WIDs, programs hardware to a cfb-compatible state, unblanks, allocates cmap, initializes fixed info, registers framebuffer, and stores drvdata. `leo_pan_display()` is mainly a hook to recover from graphics mode; it rejects nonzero offsets/modes. `leo_setcolreg()` updates cached CLUT data, writes all 256 CLUT entries through LX command registers, then triggers update bits. Blanking toggles `LEO_KRN_CSR_ENABLE`.

State and persistence: `leo_par` persists mapped windows, the 256-entry CLUT cache, current extent, blank flag, and OF IO flags. Hardware WID/CLUT/cursor state is initialized at probe and may be reasserted when panning back from graphics mode.

Dependencies and integration: uses OF platform matching name `SUNW,leo`, `sbuslib` helpers for var filling, mmap, and ioctl, SBUS read/write accessors, fbdev core, and `<asm/fbio.h>` constants. `leo_mmap_map[]` exposes multiple hardware regions to userspace according to Sun fb mappings.

Risks: register polling waits up to 0.3 seconds under spinlock in color/WID paths, which can create latency. Color updates rewrite the whole CLUT for every entry change. Fixed offsets and mappings assume exact LEO hardware layout. `leo_switch_from_graph()` performs substantial engine programming during pan. Only no-offset panning is supported.

Test signals: OF probe with expected resources, mmap offset translation, FBIO ioctl helper behavior, color map updates, blank/unblank, pan with zero and nonzero offsets, graphics-to-console recovery, WID initialization, and cleanup after partial mapping failures.
