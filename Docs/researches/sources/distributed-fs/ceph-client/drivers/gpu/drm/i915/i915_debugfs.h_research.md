<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_debugfs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_debugfs.h

### Purpose
`i915_debugfs.h` declares i915 debugfs registration and GEM-object description helpers, with no-op stubs when debugfs is disabled.

### Important APIs, Types, And Functions
It declares `i915_debugfs_register()` and `i915_debugfs_describe_obj()` under `CONFIG_DEBUG_FS`; otherwise it provides inline empty versions. It forward-declares `struct drm_i915_private`, `struct drm_i915_gem_object`, `struct drm_connector`, and `struct seq_file`.

### Control Flow
Driver init code can call `i915_debugfs_register()` unconditionally because the header compiles it out when debugfs is disabled. Debug output users can similarly call `i915_debugfs_describe_obj()` without local config guards.

### State, Persistence, And Dependencies
The header has no persistent state. It depends on `CONFIG_DEBUG_FS` to choose declarations versus stubs.

### Integration Points
It is used by i915 driver registration and by display BO support that wants to describe GEM objects.

### Risks
When debugfs is disabled, callers get no output or registration side effects. Code must not rely on debugfs helpers for functional behavior.

### Test Signals
Builds with `CONFIG_DEBUG_FS=y` and disabled debugfs validate both branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_debugfs.h -->
