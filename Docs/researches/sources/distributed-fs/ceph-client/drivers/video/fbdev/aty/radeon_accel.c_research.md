# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_accel.c

## Purpose

`radeon_accel.c` implements Radeon fbdev 2D acceleration setup and drawing primitives for `radeonfb`, separate from the Mach64 driver but located in the same `aty` fbdev directory. It initializes and resets the Radeon 2D engine, provides accelerated fill and copy operations, synchronizes with the engine, and falls back to software image blitting.

## Important APIs, Types, and Functions

Public functions are `radeonfb_fillrect()`, `radeonfb_copyarea()`, `radeonfb_imageblit()`, `radeonfb_sync()`, `radeonfb_engine_reset()`, and `radeonfb_engine_init()`. Internal helpers are `radeon_fixup_offset()`, `radeonfb_prim_fillrect()`, and `radeonfb_prim_copyarea()`. The code uses Radeon register macros such as `INREG`, `OUTREG`, `OUTREGP`, `INPLL`, `OUTPLL`, `radeon_fifo_wait()`, `radeon_engine_idle()`, `radeon_engine_flush()`, and `radeon_get_dstbpp()`.

## Control Flow

Every accelerated fill/copy first checks `info->state` and falls back if `FBINFO_HWACCEL_DISABLED` is set. `radeon_fixup_offset()` rereads `MC_FB_LOCATION` and updates default, destination, and source pitch/offset registers if firmware or X changed the card's framebuffer base behind the driver's cached state. Fill validates and clips the rectangle to virtual resolution, writes `DP_GUI_MASTER_CNTL`, brush color, write mask, direction, flush/idleness controls, and destination rectangle registers. Copy similarly validates and clips source and destination bounds, adjusts starting coordinates and direction for overlaps, configures source-memory blit state, flushes, and writes source/destination/size registers.

`radeonfb_imageblit()` waits for engine idle and delegates to `cfb_imageblit()` rather than accelerating image upload. `radeonfb_sync()` idles the engine. `radeonfb_engine_reset()` flushes the engine, forces memory clocks on, applies RBBM soft resets with R300-specific differences, resets host data path, restores clock/reset registers, and handles cache mode quirks. `radeonfb_engine_init()` disables 3D, resets the engine, configures destination cache mode, rereads framebuffer location, writes pitch/offsets, sets endian mode, default scissor, GUI master control, line/brush/source/write-mask defaults, and idles the engine.

## State and Persistence Behavior

Long-lived state is in `struct radeonfb_info`: `fb_local_base`, `pitch`, `depth`, `dp_gui_master_cntl`, `pseudo_palette`, family flags, and MMIO/PLL access context. Hardware register programming persists until the next engine reset, mode set, X handoff, suspend/resume, or driver unload. There is no disk-backed state.

## Dependencies and Integration Points

The file integrates with `radeonfb` via `radeonfb.h` and the fbdev operation table defined elsewhere. It depends on Radeon register definitions from `<video/radeon.h>`, fbdev software helpers, and chip-family helpers `IS_R300_VARIANT()`. It is designed to tolerate firmware/X server changes by checking framebuffer base before each accelerated operation.

## Risks and Edge Cases

The offset fixup is a workaround for potentially dangerous stale engine offsets; if it fails or is skipped, acceleration can write to the wrong memory. Fill and copy clip to virtual resolution, but arithmetic should still be checked for overflow on unusual modes. Image blit is software-only after idling, so glyph performance is lower but safer. Reset paths differ for R300 variants and older chips; wrong family detection can leave blocks reset or cache behavior wrong. The code relies on busy-wait FIFO/idle macros and direct MMIO ordering.

## Test Signals

Test accelerated fill/copy on 8/16/24/32-bpp modes, clipping at each edge, overlapping copies in all directions, disabled acceleration fallback, `FBINFO_STATE_RUNNING` gating, software image blit after accelerated operations, engine sync, engine init after mode set, and simulated `MC_FB_LOCATION` changes before fill/copy. Hardware tests should cover R300 and non-R300 families and big-endian builds.
