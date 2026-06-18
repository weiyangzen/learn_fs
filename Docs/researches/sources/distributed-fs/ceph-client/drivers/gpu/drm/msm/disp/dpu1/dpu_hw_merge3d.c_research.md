# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_merge3d.c

## Purpose
Implements the small hardware wrapper for DPU merge_3d blocks, which combine left/right or stereo streams according to a 3D blend mode.

## Important APIs, types, and functions
- `dpu_hw_merge_3d_init()` allocates and initializes a `struct dpu_hw_merge_3d`.
- `dpu_hw_merge_3d_setup_3d_mode()` writes `MERGE_3D_MODE` and, for disable, `MERGE_3D_MUX`.
- `_setup_merge_3d_ops()` installs the single setup callback.

## Control flow
Initialization is devres-backed, binds the register base to `addr + cfg->base`, stores catalog `id` and caps, and installs ops. Runtime setup clears both mode and mux for `BLEND_3D_NONE`; otherwise it enables bit 0 and encodes `(mode_3d - 1)` starting at bit 1.

## State and persistence
Wrapper state is limited to MMIO base, block index, catalog pointer, and ops. Hardware mode persists in merge_3d registers until changed, power-cycled, or reset.

## Dependencies and integration points
Depends on catalog data, MDSS blend-mode enum, and DPU MMIO helpers. Pingpong and encoder/resource-manager paths associate merge_3d blocks with pingpong/output composition for dual-pipe or 3D modes.

## Risks
The function assumes `mode_3d` is a valid enum value; out-of-range values would be encoded directly. The block uses `DPU_DBG_MASK_PINGPONG`, so debug filtering groups it with pingpong rather than a distinct merge mask.

## Test signals
Validation is visual and register-based: correct dual-pipe merge behavior, no stale mux state after disabling 3D, and debugfs/snapshot reads showing expected `MERGE_3D_MODE` and `MERGE_3D_MUX` values.
