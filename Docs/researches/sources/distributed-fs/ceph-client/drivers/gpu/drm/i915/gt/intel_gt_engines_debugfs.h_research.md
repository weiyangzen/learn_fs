# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_engines_debugfs.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_engines_debugfs.h

### Purpose
`intel_gt_engines_debugfs.h` declares per-GT engine debugfs registration.

### Important APIs, Types, And Functions
It forward-declares `struct intel_gt` and `struct dentry`, and declares `intel_gt_engines_debugfs_register()`.

### Control Flow
GT debugfs code includes this header and delegates engine file creation to the implementation.

### State, Persistence, And Dependencies
The header stores no state.

### Integration Points
Connects core GT debugfs registration with engine-specific diagnostics.

### Risks
No direct runtime risk beyond registration ordering.

### Test Signals
Build coverage and presence of the `engines` debugfs file under each `gtN` directory.
