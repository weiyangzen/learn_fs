# sources/distributed-fs/ceph-client/drivers/video/fbdev/wmt_ge_rops.c

Purpose: WonderMedia Graphics Engine raster-operation acceleration provider. It exports fbdev-compatible fillrect, copyarea, and sync helpers that program a global GE MMIO block for solid fills and screen-to-screen copies.

Important APIs, types, and functions: exported symbols are `wmt_ge_fillrect`, `wmt_ge_copyarea`, and `wmt_ge_sync`. Internal helpers include `pixel_to_pat`, `wmt_ge_rops_probe`, and `wmt_ge_rops_remove`. Register offsets define command, depth, rop, source/destination geometry, pattern color, enable, interrupt, and status registers.

Control flow: a platform driver matching `wm,prizm-ge-rops` maps one MMIO resource into the file-global `regbase`, enables the engine, and refuses a second engine. Fill operations resolve true/direct-color values through the pseudo-palette, expand them to a hardware pattern, synchronize previous work, program destination geometry and rop code (`0xf0` copy or `0x5a` XOR), then fire the command. Copy operations synchronize, program source and destination rectangles, set rop `0xcc`, and fire. Sync busy-waits for the status busy bit to clear with a fixed loop limit.

State and persistence: the only driver state is global `regbase`, plus the GE hardware registers. There is no per-client state, no command queue, and no persistence beyond MMIO state. The accelerated operations depend on caller-provided `fb_info`.

Dependencies and integration points: depends on platform bus, OF, fbdev structures, eventless MMIO polling, and consumers such as `wm8505fb.c`. The header provides software fallbacks when disabled.

Risks: single global engine support means multiple devices are not handled. There is no explicit locking around GE register programming; concurrent fb operations could interleave unless higher layers serialize them. `wmt_ge_sync` is a CPU busy wait and returns `-EBUSY` without recovery. Unsupported pixel depths silently pattern as zero after a warn-once. Remove just clears `regbase`, relying on devm for unmap and not disabling the engine.

Test signals: build with `CONFIG_FB_WMT_GE_ROPS`; probe a `wm,prizm-ge-rops` DT node before framebuffer use; run fbcon scroll/fill/copy workloads, XOR rect tests, unsupported depth checks, concurrent drawing stress, and `fb_sync` timeout injection if possible.
