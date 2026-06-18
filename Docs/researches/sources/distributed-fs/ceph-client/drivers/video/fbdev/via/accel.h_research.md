# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/accel.h

## Purpose
`accel.h` defines VIA framebuffer acceleration constants, MMIO register offsets, command bits, status masks, memory reservation sizes, and public acceleration helper prototypes.

## Important APIs, Types, And Data
Important definitions include `FB_ACCEL_VIA_UNICHROME`, VGA MMIO base offsets, cursor and virtual queue sizes, 2D engine register offsets for legacy and M1 layouts, GEMODE bpp encodings, GECMD command bits, source/destination mode bits, clipping/pattern/mono flags, status masks for H2/H5/M1 engines, `MAXLOOP`, and bitblt operation IDs. It declares `viafb_setup_engine()`, `viafb_reset_engine()`, `viafb_show_hw_cursor()`, and `viafb_wait_engine_idle()`.

## Control Flow
The header has no control flow. Its constants are consumed by `accel.c` to program registers and by other VIA fbdev files to advertise acceleration and manage cursor state.

## State And Persistence
No runtime state is stored here. The constants define persistent ABI-like assumptions inside the driver about MMIO layout, command encodings, and reserved framebuffer memory sizes.

## Dependencies And Integration Points
It is included through `global.h` and therefore becomes part of most VIA fbdev compilation units. It integrates `accel.c` with chip detection and main fbdev setup code via shared prototypes and constants.

## Risks
Incorrect register offsets or masks can hang the 2D engine or corrupt framebuffer memory. The fixed `CURSOR_SIZE` and `VQ_SIZE` constants affect framebuffer memory layout. Because several chip families reuse names with different register layouts, callers must pair the constants with the right engine type.

## Test Signals
Signals include clean compilation across all VIA objects, correct register writes visible in MMIO traces, successful cursor and VQ allocation sizes, and acceleration tests on chips using both legacy and M1 register maps.
