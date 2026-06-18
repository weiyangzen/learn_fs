<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_debugfs_params.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_debugfs_params.h

### Purpose
`i915_debugfs_params.h` declares the helper that creates debugfs parameter files for an i915 device.

### Important APIs, Types, And Functions
It declares `struct dentry *i915_debugfs_params(struct drm_i915_private *i915)`.

### Control Flow
Debugfs registration code calls the function and receives the created directory dentry or an error dentry.

### State, Persistence, And Dependencies
The header holds no state and forward-declares `struct dentry` and `struct drm_i915_private`.

### Integration Points
It connects `i915_debugfs.c` with the parameter-file implementation.

### Risks
Callers should treat the return as debugfs best-effort infrastructure and not as required device functionality.

### Test Signals
Build coverage and debugfs registration tests cover this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_debugfs_params.h -->
