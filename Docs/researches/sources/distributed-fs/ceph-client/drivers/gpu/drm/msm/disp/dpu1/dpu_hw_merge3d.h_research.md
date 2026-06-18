# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_merge3d.h

## Purpose
Declares the merge_3d hardware object and operation used to configure 3D merge mode for DPU output composition.

## Important APIs, types, and functions
- `struct dpu_hw_merge_3d_ops` exposes `setup_3d_mode()`.
- `struct dpu_hw_merge_3d` stores the base block, register map, block index, catalog caps, and ops.
- `to_dpu_hw_merge_3d()` converts from generic hardware block to the merge_3d wrapper.
- `dpu_hw_merge_3d_init()` constructs the block.

## Control flow
No runtime control flow exists in the header. Callers use the function pointer after clocks are enabled.

## State and persistence
The header defines wrapper state only; merge mode persists in hardware registers programmed by the implementation.

## Dependencies and integration points
Includes catalog, MDSS, and utility headers. It is integrated by the resource manager and pingpong/encoder output paths that need a merge block near the final output pipeline.

## Risks
The API is intentionally narrow. Any future merge feature, mux selection, or validation would require expanding the ops while preserving existing users.

## Test signals
Build coverage validates the constructor and ops signature. Runtime testing is covered by merge_3d programming in dual-pipe or 3D-output modes.
