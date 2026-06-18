# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_dma.h

## Purpose

`nv_dma.h` is a register/tag definition header for NVIDIA 2D DMA objects used by `nv_accel.c`. It names command offsets, depth encodings, bitfield positions, and data array limits for surface, ROP, pattern, clipping, line, blit, rectangle, color expansion, and stretch blit methods. The source was read as a complete 188-line file.

## Important APIs, Types, and Functions

There are no functions or types. Important macro groups include `SURFACE_*`, `ROP_SET`, `PATTERN_*`, `CLIP_*`, `LINE_*`, `BLIT_*`, `RECT_*`, `RECT_EXPAND_ONE_COLOR_*`, `RECT_EXPAND_TWO_COLOR_*`, and `STRETCH_BLIT_*`. Macros such as `SURFACE_PITCH_SRC 15:0` are intended for the bitfield helpers in `nv_type.h` (`SetBF`, `SetBitField`, etc.), while offset macros are sent through `NVDmaStart()`.

## Control Flow

No executable control flow exists. The header supplies symbolic constants consumed when acceleration code emits DMA method headers and payload words.

## State and Persistence Behavior

The file owns no state. Its constants describe hardware command-buffer layout; changing them changes how driver state is serialized into the GPU FIFO.

## Dependencies and Integration Points

It is included by `nv_accel.c` and `nvidia.c`, together with `nv_local.h` DMA macros. The constants must match the PRAMIN object setup performed in `NVLoadStateExt()` and the FIFO command stream expectations of supported NVIDIA architectures.

## Risks and Edge Cases

Macro values are hardware ABI. Incorrect offsets, duplicated/ambiguous definitions such as repeated `STRETCH_BLIT_CLIP_POINT`, or wrong data limits can corrupt FIFO commands or hang acceleration. Because the file has no type checking, callers must provide correct word counts to `NVDmaStart()`.

## Test Signals

Acceleration smoke tests are the real validation: fillrect, copyarea, mono imageblit, clipping, ROP, and pitch/offset behavior across bpp modes. Build coverage should also catch malformed macro use after edits.
