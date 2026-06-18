# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_plane_regs.h

## Purpose
`i9xx_plane_regs.h` defines MMIO register addresses and bitfield helpers for legacy i9xx primary/display plane registers, including VLV/CHV address variants and CHV pipe B primary-plane window registers.

## Important APIs, Types, and Functions
The header defines register macros such as `DSPCNTR()`, `DSPADDR()`, `DSPLINOFF()`, `DSPSTRIDE()`, `DSPPOS()`, `DSPSIZE()`, `DSPSURF()`, `DSPTILEOFF()`, `DSPOFFSET()`, `DSPSURFLIVE()`, `DSPGAMC()`, `PRIMPOS()`, `PRIMSIZE()`, and `PRIMCNSTALPHA()`. Bitfields include plane enable, pipe gamma/CSC, pixel format encodings, pipe select, color key, line double, alpha, rotation, trickle-feed disable, tiling, async flip, CHV mirror, offsets, sizes, surface address mask, and constant alpha.

## Control Flow and State
The header has no runtime control flow. Its macros are used by C code to calculate platform/plane-specific MMIO addresses and to pack or extract register fields. State is hardware register state represented symbolically.

## Dependencies and Integration Points
It includes `intel_display_reg_defs.h` for `_MMIO_PIPE2`, `_MMIO_TRANS2`, `REG_BIT`, `REG_GENMASK`, and `REG_FIELD_PREP`. `i9xx_plane.c` is the primary consumer, but other low-level display code can use these definitions for readout, capture, and programming.

## Risks and Test Signals
Incorrect addresses or bit encodings directly corrupt plane programming. Overloaded bit positions across generations, such as rotation versus alpha-transparency or pipe CSC versus pipe select, require careful platform gating by users. Test signals include register read/write traces during modeset, IGT plane programming tests, async flip coverage, CHV pipe B reflection/window tests, and hardware state readout matching expected `DSPCNTR`/surface fields.
