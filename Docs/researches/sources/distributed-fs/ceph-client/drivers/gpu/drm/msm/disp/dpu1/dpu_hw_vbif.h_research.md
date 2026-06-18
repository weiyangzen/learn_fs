# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_vbif.h

## Purpose
Declares the VBIF wrapper and operation table for configuring DPU memory-interface behavior.

## Important APIs, types, and functions
- `struct dpu_hw_vbif_ops` exposes limit config, halt control, QoS remap, memory type, error clearing, and write-gather callbacks.
- `struct dpu_hw_vbif` stores the register map, catalog caps, and ops.
- `dpu_hw_vbif_init()` constructs the wrapper.

## Control flow
No runtime control flow is present in the header. All operations assume clocks and register mappings are valid.

## State and persistence
The header defines wrapper state only. Persistent behavior is in VBIF registers programmed by the implementation.

## Dependencies and integration points
Includes DPU catalog, MDSS common types, and utility register map. KMS owns the single VBIF wrapper, while plane/VBIF policy code uses it for QoS and transaction limit programming.

## Risks
The ops table includes optional `set_qos_remap`; callers must check it on catalogs without remap support. Shared memory-interface programming has high blast radius if XIN IDs or limits are wrong.

## Test signals
Build coverage and runtime bandwidth stress are primary signals. Debugfs/snapshot VBIF register dumps and error clear outputs validate operation.
