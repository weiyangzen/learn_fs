# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/g2d-hw.c

Purpose: low-level MMIO helper layer for Samsung G2D BitBLT hardware. It writes source/destination geometry, base addresses, color modes, ROP, flip, scaling, command, start, reset, and interrupt-clear registers.

Important APIs: `g2d_reset()`, `g2d_set_src_size()`, `g2d_set_src_addr()`, `g2d_set_dst_size()`, `g2d_set_dst_addr()`, `g2d_set_rop4()`, `g2d_set_flip()`, `g2d_set_v41_stretch()`, `g2d_set_cmd()`, `g2d_start()`, and `g2d_clear_int()`.

Control flow: `device_run()` in `g2d.c` enables the clock gate, resets hardware, programs source and destination frames plus DMA addresses, applies current controls, optionally configures stretch scaling, writes command bits, and calls `g2d_start()`. The ISR calls `g2d_clear_int()` after completion.

State and persistence: the helpers only project `struct g2d_frame` and `struct g2d_dev` state into volatile registers. Hardware state is reset per mem2mem job.

Dependencies and integration: includes `g2d.h` for device/frame structures and `g2d-regs.h` for register offsets and constants. Uses `readl/writel` only; locking and clock management are handled by `g2d.c`.

Risks: `g2d_set_v41_stretch()` divides by destination crop dimensions, so prior selection validation must prevent zero width/height. Register fields mask dimensions to 12 or 16 bits, relying on upper-layer clamping to `MAX_WIDTH/MAX_HEIGHT`. Revision-specific behavior differs for cache clear and scaling command bits.

Test signals: mem2mem copy, invert, H/V flip, stretch on v3 and v4 hardware, IRQ completion, and register programming tests that compare frame offsets/strides/right-bottom coordinates against requested crop/compose rectangles.
