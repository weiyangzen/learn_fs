
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/pior507d.c

## Purpose
Implements PIOR output-resource control for NV507D-era display core channels. PIORs drive external encoders such as external TMDS or TV encoders.

## Important APIs, types, and functions
- `pior507d_ctrl()` merges caller-provided control bits with hsync/vsync polarity and pixel depth from `struct nv50_head_atom`.
- `pior507d_get_caps()` marks `outp->caps.dp_interlace = true`.
- `const struct nv50_outp_func pior507d` exposes `.ctrl` and `.get_caps`.

## Control flow
When an output resource is assigned or reprogrammed, the core output path calls `.ctrl`. If a head atom is supplied, polarity and depth are encoded into `ctrl`; then `PIOR_SET_CONTROL(or)` is emitted on the core push channel. Capability discovery simply reports DP interlace support without probing hardware.

## State and persistence
The file does not keep software state. It changes PIOR control register state in the display core channel, and sets capability bits on the `nouveau_encoder` object during output initialization.

## Dependencies and integration points
Uses `core.h`, `nvif/push507c.h`, `cl507d.h`, and `cl837d.h`. It is selected by the NV50 display output table and relies on `nv50_head_atom` ownership/depth fields being precomputed by atomic modeset code.

## Risks
The function combines NV507D and NV837D field definitions for pixel depth; field compatibility is assumed. Always enabling DP interlace support may overstate capability if a future PIOR path has stricter limits.

## Test signals
Modeset tests through PIOR-backed encoders should verify polarity, depth, and owner/protocol programming. Compile-time class macro compatibility is also important.
