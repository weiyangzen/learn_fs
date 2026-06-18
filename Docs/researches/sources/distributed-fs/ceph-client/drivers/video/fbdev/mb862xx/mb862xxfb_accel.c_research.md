# sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xxfb_accel.c

## Purpose
Provides 2D acceleration hooks for MB862xx framebuffer operations: rectangle fill, copyarea, and imageblit through the GDC geometry FIFO.

## Important APIs, Types, and Functions
- `mb862xxfb_write_fifo()` writes command words to the geometry FIFO, polling free count from `GDC_REG_FIFO_COUNT`.
- `mb86290fb_copyarea()` emits BLT copy commands, selecting direction based on source/destination overlap.
- `mb86290fb_imageblit1()`, `mb86290fb_imageblit8()`, and `mb86290fb_imageblit16()` build FIFO command arrays for 1bpp, 8bpp, and 16bpp images.
- `mb86290fb_imageblit()` clips image blits to virtual resolution, allocates DMA-capable command memory, and falls back to cfb on unsupported depths or allocation failure.
- `mb86290fb_fillrect()` clips fills, chooses XOR or COPY ROP, and emits draw-rect commands.
- `mb862xxfb_init_accel()` installs accelerated fbops for non-32bpp modes and cfb helpers for 32bpp.

## Control Flow
The main driver calls `mb862xxfb_init_accel()` during `set_par()` for CoralP devices. The function sets display/engine registers and replaces fbops. Subsequent fbdev drawing operations build command arrays and feed them to the hardware FIFO. Unsupported image depths and allocation failures fall back to generic cfb implementations.

## State and Persistence
The file updates `fb_ops` function pointers, `info->flags`, `info->fix.accel`, and GDC draw/display registers. `mb862xxfb_write_fifo()` uses a static `free` counter shared by all calls and instances.

## Dependencies and Integration Points
Depends on `mb862xxfb.h`, `mb862xx_reg.h`, and `mb862xxfb_accel.h` command/register constants. Integrates with fbdev drawing callbacks and the main driver's mode setup path.

## Risks
The static FIFO free counter is global rather than per device, problematic for multiple adapters or after hardware reset. `mb86290fb_imageblit16()` copies `step` bytes rather than `step << 2` bytes, which is suspicious because command buffers are u32 words. 8bpp blitting reads pixel pairs and may overread odd widths after clipping. No explicit engine idle synchronization is done before changing mode or unloading.

## Test Signals
Use fbcon and framebuffer drawing tests across 8, 16, and 32bpp. Verify 32bpp uses cfb helpers, non-32bpp sets hardware acceleration flags, copyarea handles overlapping directions, imageblit clips at virtual bounds, and FIFO polling does not hang.
