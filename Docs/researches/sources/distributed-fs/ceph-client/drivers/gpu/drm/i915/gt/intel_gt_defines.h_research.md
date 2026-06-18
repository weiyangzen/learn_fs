# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_defines.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_defines.h

### Purpose
`intel_gt_defines.h` centralizes simple GT-wide constants.

### Important APIs, Types, And Functions
It defines `I915_MAX_GT` as `2`, setting the array bound for GT instances in this tree.

### Control Flow
There is no runtime control flow. The constant constrains iteration and storage in code that supports a root GT plus one extra tile/media GT.

### State, Persistence, And Dependencies
The header stores no state and has no dependencies beyond include guards.

### Integration Points
Used by GT arrays, `for_each_gt()`, and platform code that enumerates extra GT definitions.

### Risks
If future platforms expose more GTs than this constant allows, probe and iteration would silently lack capacity until the constant and associated arrays are updated.

### Test Signals
Compile-time array sizing and multi-GT probe tests on platforms with root plus media/tile GTs validate the current bound.
