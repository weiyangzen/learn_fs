# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_ccs_mode.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_ccs_mode.c

### Purpose
`intel_gt_ccs_mode.c` computes the DG2 fixed CCS load-balancing mode value from the GT's available CCS slices.

### Important APIs, Types, And Functions
The exported function is `intel_gt_apply_ccs_mode()`. It uses `CCS_MASK(gt)`, `gt->ccs.cslices`, `I915_MAX_CCS`, `XEHP_CCS_MODE_CSLICE()`, and `XEHP_CCS_MODE_CSLICE_MASK`.

### Control Flow
Non-DG2 platforms return zero. DG2 picks the first available CCS engine, then iterates compute slices. Enabled slices are mapped to that first CCS engine; unavailable slices are marked with the reserved/unavailable mask.

### State, Persistence, And Dependencies
The function reads GT platform data and the `ccs.cslices` mask but writes no persistent state. The returned mode is consumed by register programming elsewhere. Dependencies are platform macros and GT register definitions.

### Integration Points
Engine and workaround setup paths use the computed value when programming `XEHP_CCS_MODE`/related CCS mode state on DG2.

### Risks
The function assumes `CCS_MASK(gt)` is nonzero on DG2 before `__ffs()` is used. Incorrect `cslices` discovery can route work to unavailable CCS slices or over-constrain load balancing.

### Test Signals
Test DG2 configurations with one, multiple, and sparse CCS slices; non-DG2 zero behavior; and register programming that consumes the returned mode.
