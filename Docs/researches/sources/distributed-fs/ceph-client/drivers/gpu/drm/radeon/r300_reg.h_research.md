# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r300_reg.h

## Purpose
`r300_reg.h` is the primary R300 3D register dictionary. It defines memory-controller latency registers, vertex array processing, viewport and vertex program upload state, rasterization and interpolator routing, scissor/clip rectangles, texture units and formats, fragment program instruction encoding, fog/alpha/blend/color buffer state, z/stencil/HyperZ state, vertex program instruction encoding, packet3 draw constants, and a small set of R500-era aliases used by shared validation code. Its comments record reverse-engineered behavior and uncertainty.

## Important APIs, Types, And Macros
The file is macro-only. Important groups include `R300_VAP_*` for primitive control, vertex formats, input routes, vertex shader upload, and PVS control; `R300_GB_*` for geometry backend, tile config, multisample positions, FIFO sizing, fog/depth selection, and AA; `R300_TX_*` for texture enable, filter, size, format, pitch, offset, chroma key, and border color; `R300_PFS_*` and `R300_FPI*` for fragment program node, texture instruction, ALU source, destination, operand, and opcode fields; `R300_RS_*` for raster interpolator and route registers; `R300_RE_*` for point/line/polygon/fog/cull/scissor/clip state; `R300_RB3D_*` for blending, color masks, color offsets/pitches, and AA resolve; and `R300_ZB_*` for z/stencil, z-cache, HyperZ, zmask/hiz offsets, zpass, and depth XY offset.

The helper `R300_EASY_TX_FORMAT()` assembles texture format swizzles. The packet section defines primitive type/walk bits and packet constants such as `R300_PACKET3_3D_LOAD_VBPNTR`, `R300_PACKET3_INDX_BUFFER`, and `R300_CP_CMD_BITBLT_MULTI`.

## Control Flow And State
No code executes in this header. Its definitions drive command construction and validation elsewhere. In this subset, `r300_packet0_check()` depends on texture offset, size, filter, format, color pitch, depth pitch, z format, HyperZ, CMASK-related, AA resolve, and zpass definitions. `r300_ring_start()` and `r420_pipes_init()` use GB tile, pipe, multisample, cache, and destination pipe constants. State represented here is GPU pipeline state: vertex inputs, shader programs, texture images, render targets, depth buffers, interpolation, and caches.

## Dependencies And Integration Points
This header is included by R300/R420-era driver sources and complements `r300d.h`, `r420d.h`, `radeon_reg.h`, and safe-register bitmap headers. It integrates with Mesa/userspace command generation because many constants describe the exact command stream ABI accepted by the kernel. It also feeds `r100_cs_track` validation by letting kernel code interpret cpp, pitch, compression, coordinate type, tiling, and z/CB enable state.

## Risks
Many comments say "GUESS", "Dangerous", or describe reverse-engineered behavior. That means edits can produce hardware lockups even when the code compiles. Texture format, compression, pitch, and tiling constants are directly tied to bounds checks in `r300_packet0_check()`. HyperZ, zmask, hiz, CMASK, and fast-fill constants are security-sensitive because unauthorized access is rejected by ownership checks. Shader instruction encodings and PVS control registers can hang GPUs if invalid program bounds or unknown fields are emitted.

## Test Signals
Compile coverage is necessary but weak. Stronger signals are 3D rendering tests covering vertex arrays, immediate draws, programmable vertex and fragment shaders, all texture formats allowed by the validator, NPOT/pitched textures, depth/stencil, blending, scissor/cliprects, AA resolve, and HyperZ/CMASK authorization failures. Hardware hang absence and consistent piglit/Mesa behavior across R300, R420, and R500-family variants are the practical regression checks.
