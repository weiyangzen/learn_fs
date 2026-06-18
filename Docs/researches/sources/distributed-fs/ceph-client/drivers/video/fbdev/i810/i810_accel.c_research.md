
# sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_accel.c

Purpose: implements accelerated fbdev drawing for the Intel i810/i815 framebuffer. It wraps the i810 instruction ring and exposes `i810fb_fillrect`, `i810fb_copyarea`, `i810fb_imageblit`, `i810fb_sync`, `i810fb_load_front`, and `i810fb_init_ringbuffer` to the main driver.

Important APIs and functions: `wait_for_space()` polls the ring head against `par->cur_tail`, marks `LOCKUP`, and downgrades pixmap alignment on timeout. `wait_for_engine_idle()` flushes ring space then waits on `INSTDONE`. `begin_iring()`, `PUT_RING`, and `end_iring()` are the core command submission path. `source_copy_blit()`, `color_blit()`, and `mono_src_copy_imm_blit()` emit BLT packets for copies, fills, and 1bpp text/image expansion. `i810fb_iring_enable()` toggles the ring enable bit after `flush_cache()`.

Control flow: fb_ops callbacks validate acceleration is enabled, no lockup occurred, and depth is not 32bpp (`par->depth == 4`) before using hardware. Otherwise they fall back to `cfb_*`. Copy direction is adjusted for overlapping regions. Image blits only accelerate 1bpp glyph data and compute padded DWORD payload size before embedding bitmap data in the ring. Panning updates `DPLYBASE` directly when acceleration is disabled or via a parser/front-buffer command when active.

State and persistence: persistent state is in `struct i810fb_par`: `cur_tail`, `iring`, `fb`, `pitch`, `depth`, `blit_bpp`, `dev_flags`, and mapped MMIO. Lockups persist by setting `LOCKUP`, preventing future acceleration until mode/device reinitialization.

Dependencies and integration: depends on `i810_regs.h`, `i810.h`, `i810_main.h`, fbdev software helpers, MMIO accessors, and x86 `flush_cache()` when available. `i810_main.c` wires these functions into `fb_ops` and initializes AGP-backed ring memory.

Risks: polling has fixed retry counts and no scheduling delay; hardware stalls can burn CPU and permanently disable acceleration. Address arithmetic uses `fix.smem_start` physical offsets and assumes validated geometry. Ring space accounting must remain consistent with packet sizes. `mono_src_copy_imm_blit()` casts image data to `u32 *`, so caller padding/alignment assumptions matter.

Test signals: exercise fill/copy/image paths with acceleration on/off, 8/16/24/32 bpp, overlapping copy directions, y-pan, lockup fallback, and `fb_sync()`. Hardware or emulator tests should verify ring head/tail programming and that software fallback still renders after forced timeout.
