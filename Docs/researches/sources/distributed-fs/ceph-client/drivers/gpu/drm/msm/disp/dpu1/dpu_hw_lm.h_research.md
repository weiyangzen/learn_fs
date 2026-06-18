# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_lm.h

## Purpose
Declares the layer mixer abstraction used by DPU display code to configure mixer output, stage blending, border color, and MISR collection.

## Important APIs, types, and functions
- `struct dpu_hw_mixer_cfg` carries output dimensions, right-mixer flag, and flags.
- `struct dpu_hw_lm_ops` defines mixer operations: output setup, blend config, alpha output, v12+ blend-stage routing, border color, MISR setup, and MISR collection.
- `struct dpu_hw_mixer` embeds the opaque hardware block, register map, catalog pointers, ops, and cached display config.
- `to_dpu_hw_mixer()` converts a generic `dpu_hw_blk` to the mixer container.
- `dpu_hw_lm_init()` is the constructor.

## Control flow
This header has no runtime control flow. It defines function-pointer contracts that callers use only after clocks are enabled, with implementation-selected ops based on hardware version.

## State and persistence
The header defines in-memory wrapper state, not hardware persistence. Hardware state is programmed through the ops and remains in MMIO registers.

## Dependencies and integration points
It includes MDSS common definitions and utility register map definitions. It is consumed by KMS/resource-manager code and CRTC/encoder plane staging code that needs an abstract mixer independent of register generation.

## Risks
Ops are optional by generation; callers must check function pointers for v12-only blend-stage APIs. Header changes affect multiple DPU blocks because mixer objects are central to plane composition.

## Test signals
Build coverage catches signature mismatches. Runtime validation comes from successful CRTC commits with correct z-order, alpha blending, split display, and MISR debug reads.
