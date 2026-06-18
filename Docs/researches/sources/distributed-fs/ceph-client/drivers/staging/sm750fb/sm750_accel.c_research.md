## sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750_accel.c

Purpose: this file implements SM750 2D drawing engine operations used by accelerated framebuffer callbacks: rectangle fill, screen-to-screen copy, and monochrome image blit.

Important functions: low-level helpers `write_dpr()`, `read_dpr()`, and `write_dp_port()` access drawing-engine registers and the data port. `sm750_hw_de_init()` initializes masks, stretch format, clipping, color compare, and transparency. `sm750_hw_set2dformat()` programs the pixel format. `sm750_hw_fillrect()`, `sm750_hw_copyarea()`, and `sm750_hw_imageblit()` program the engine for fbdev acceleration. `de_get_transparency()` preserves selected transparency bits during host writes.

Control flow: each operation waits for engine readiness through `accel->de_wait()`, writes base addresses, pitches converted from bytes to pixels, window width, source/destination coordinates, dimensions, colors, ROP values, and command bits, then starts the operation by setting `DE_CONTROL_STATUS`. Copy operations compute direction for overlapping same-surface blits and adjust coordinates for bottom-to-top or right-to-left transfers. Image blits use host-write mode and stream packed monochrome data through the data port line by line.

State and persistence: the drawing engine state persists in DPR registers. `struct lynx_accel` carries MMIO base pointers and wait function pointers set during probe/hardware init. There is no local locking; `sm750.c` protects accelerated fbops with `sm750_dev->slock`.

Dependencies and integration points: used through `struct lynx_accel` hooks assigned in `lynxfb_pci_probe()`. Register offsets and bit definitions come from `sm750_accel.h`. The wait implementation is chip-specific and supplied by `sm750_hw.c` for SM750 versus SM750LE.

Risks: `sm750_hw_imageblit()` casts potentially unaligned source bytes to `unsigned int *`, which can fault or behave poorly on strict-alignment architectures. The `remain[4]` buffer is not zero-initialized before copying trailing bytes, so padding bytes written to the data port may contain stack data. Engine busy waits can spin for a large count. Division by `Bpp` assumes nonzero validated bpp. Copy direction only considers some overlap geometry and maps vertical and horizontal reverse directions to the same control bit, relying on hardware interpretation.

Test signals: accelerated console scrolling, `fbtest` rectangle/copy/mono glyph paths, overlapping copy cases in all directions, 8/16/32 bpp modes, forced engine-busy timeout behavior, and strict-alignment builds are important. Comparing accelerated output with software cfb fallbacks can catch pitch, ROP, and endian issues.
