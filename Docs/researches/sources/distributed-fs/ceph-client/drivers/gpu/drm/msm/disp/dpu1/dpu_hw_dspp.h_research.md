# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_dspp.h

## Purpose
Declares DSPP color-processing structures and ops for PCC and GC.

## Important APIs, Types, and Functions
`struct dpu_hw_pcc_coeff` and `struct dpu_hw_pcc_cfg` model per-channel PCC coefficients. Constants `DPU_GAMMA_LUT_SIZE`, `PGC_TBL_LEN`, and `PGC_8B_ROUND` define gamma LUT sizing and flags. `struct dpu_hw_gc_lut` carries three 512-entry LUT channels plus flags. `struct dpu_hw_dspp_ops` exposes `setup_pcc` and `setup_gc`. `struct dpu_hw_dspp` stores generic block, register map, DSPP index, catalog cap, and ops. `dpu_hw_dspp_init` creates the wrapper.

## Control Flow and State
The header defines only caller-provided configuration and allocated wrapper state. Passing NULL configs to ops disables the corresponding feature in the implementation.

## Dependencies and Integration Points
DSPP catalog entries decide whether ops are assigned. CTL DSPP flush APIs and DRM color-management paths are the main consumers.

## Risks and Test Signals
The main API risks are LUT size assumptions and callers using unassigned ops on catalog entries without the sub-block. Tests should validate PCC coefficient writes, GC LUT length and round flag, disabled feature handling, and CTL flush pairing.
