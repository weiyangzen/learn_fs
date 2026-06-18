<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_debugfs_params.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_debugfs_params.c

### Purpose
`i915_debugfs_params.c` creates debugfs files for i915 module/runtime parameters and implements typed read/write handlers for integer, unsigned integer, boolean, unsigned long, and string parameters.

### Important APIs, Types, And Functions
The exported function is `i915_debugfs_params()`. Internal handlers include `i915_param_int_show/open/write()`, `i915_param_uint_show/open/write()`, `i915_param_charp_show/open/write()`, typed `file_operations` for read-write and read-only modes, `notify_guc()`, typed create helpers, and `_i915_param_create_file()`.

### Control Flow
`i915_debugfs_params()` creates an `i915_params` directory under the DRM debugfs root, then iterates `I915_PARAMS_FOR_EACH()` and creates one file per parameter with the mode declared in parameter metadata. Reads print the current value. Writes parse integers or booleans for int/uint parameters; string writes replace the old string with `strndup_user()`. Writing the unsigned `reset` parameter additionally updates GuC global policies on GTs using GuC submission and rolls back the value on failure.

### State, Persistence, And Dependencies
Files point directly at fields in `struct i915_params`, using unsafe debugfs file creation for numeric values. String writes allocate new memory and free the previous pointer. Dependencies include Linux debugfs, seq_file, i915 params metadata, GT iteration, GuC policy update, and container macros to recover `drm_i915_private` from a parameter pointer.

### Integration Points
`i915_debugfs_register()` calls this during debugfs setup. Developers and tests use the files to inspect and, for writable params, alter driver parameter state at runtime.

### Risks
`debugfs_create_file_unsafe()` assumes the i915 device and params outlive the debugfs entries. Writable parameters can affect live driver behavior, and only `reset` has a special GuC synchronization path here. String writes accept up to `PAGE_SIZE` and replace pointers without additional semantic validation.

### Test Signals
Tests should verify directory/file creation for all parameter types and modes, int/uint boolean parsing, read-only mode refusing writes, string replacement and free behavior, reset writes with GuC policy success/failure rollback, and device teardown while debugfs files exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_debugfs_params.c -->
