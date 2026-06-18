# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_debugfs.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_debugfs.h

### Purpose
`intel_gt_debugfs.h` provides helper macros and registration types for per-GT debugfs files.

### Important APIs, Types, And Functions
It defines `DEFINE_INTEL_GT_DEBUGFS_ATTRIBUTE()`, `DEFINE_INTEL_GT_DEBUGFS_ATTRIBUTE_WITH_SIZE()`, `struct intel_gt_debugfs_file`, and declarations for GT debugfs registration and reset show/store helpers.

### Control Flow
The macros generate `single_open` file operations that pass `inode->i_private` to a show callback. Registration code consumes arrays of `intel_gt_debugfs_file` entries and optional evaluation callbacks.

### State, Persistence, And Dependencies
The header stores no state. It depends on Linux file operations and forward-declared GT structures.

### Integration Points
GT, engine, PM, SSEU, and UC debugfs modules use these helpers to keep per-GT file creation consistent.

### Risks
Generated file operations are read-only unless a custom fops table supplies writes. Callback data must remain valid for the debugfs file lifetime.

### Test Signals
Compile coverage of generated fops and runtime file open/read behavior for each registered GT debugfs module are the main signals.
