## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_accel.c

Purpose: `matroxfb_accel.c` installs and implements accelerated fbdev drawing operations for Matrox framebuffer devices. It configures accelerator pixel format registers and replaces generic cfb operations with hardware-backed copyarea, fillrect, and 1 bpp imageblit paths when text acceleration is enabled.

Important APIs and functions: exported `matrox_cfbX_init()` selects fbops and writes accelerator setup registers (`M_PITCH`, `M_YDSTORG`, `M_OPMODE`, `M_MACCESS`, etc.) based on current bpp. Internal accelerated operations include `matrox_accel_bmove()`, `matrox_accel_bmove_lin()`, `matroxfb_copyarea()`, `matroxfb_cfb4_copyarea()`, `matroxfb_accel_clear()`, `matroxfb_fillrect()`, `matroxfb_cfb4_clear()`, `matroxfb_cfb4_fillrect()`, `matroxfb_1bpp_imageblit()`, and `matroxfb_imageblit()`.

Control flow: mode setting in `matroxfb_base.c` calls `matrox_cfbX_init()` after registers are restored. The function starts with generic cfb fallbacks, computes Matrox access/opmode/pitch for bpp, optionally enables accelerated callbacks, and records accelerator state in `minfo->accel`. fbdev operations then program drawing registers, wait for FIFO/idle, and fall back to software when unsupported (for example odd 4 bpp copy boundaries or non-1bpp imageblit).

State and persistence: persistent software state is `minfo->accel.{m_dwg_rect,m_opmode,m_access,m_pitch}` and bpp-dependent pseudo-palette values in `minfo->cmap`. Hardware state is the drawing engine registers and FIFO/idle state. The optional `MATROXFB_USE_SPINLOCKS` path can serialize accelerator access through `minfo->lock.accel`.

Dependencies and integration points: depends on Matrox MMIO register macros from `matroxfb_base.h`, DAC-family flags such as Millennium II transparency behavior, generic fbdev cfb helpers, and unaligned/MMIO copy helpers. It is called by the base driver after each primary-head mode change.

Risks: accelerator register programming is sensitive to pitch, bpp, interleave, endian opmode, and YDSTORG. Several operations busy-wait with `WaitTillIdle()`. 4 bpp handling mixes accelerated byte-aligned middle spans with direct framebuffer read/modify/write edges. Imageblit comments note that fbdev logo code can pass misleading depth, so non-1bpp is intentionally software.

Test signals: run fbcon text scrolling, rectangle fills, area copies, and monochrome glyph rendering at 4/8/15/16/24/32 bpp with acceleration on/off. Verify no corruption when panning changes YDSTORG, with odd 4 bpp coordinates, and on big-endian platforms. Watch for hangs in FIFO/idle loops during stress scrolling.
