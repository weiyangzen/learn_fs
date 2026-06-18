# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_ccs_mode.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_ccs_mode.h

### Purpose
`intel_gt_ccs_mode.h` declares the CCS mode helper for compute-slice load-balancing register setup.

### Important APIs, Types, And Functions
It forward-declares `struct intel_gt` and declares `intel_gt_apply_ccs_mode()`.

### Control Flow
Consumers include the header when they need to compute a register value from `struct intel_gt` CCS topology.

### State, Persistence, And Dependencies
The header stores no state and only depends on a GT forward declaration.

### Integration Points
Used by platform/workaround or engine setup code that programs DG2 CCS mode registers.

### Risks
The narrow API hides platform assumptions in the implementation; callers must only use the returned value with the matching hardware register semantics.

### Test Signals
Compile coverage and DG2 CCS register programming validation are sufficient.
