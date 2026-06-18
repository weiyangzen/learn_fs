# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_engines_debugfs.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_engines_debugfs.c

### Purpose
`intel_gt_engines_debugfs.c` exposes a per-GT debugfs `engines` file that dumps state for each initialized engine.

### Important APIs, Types, And Functions
The public registration function is `intel_gt_engines_debugfs_register()`. Internally, `engines_show()` iterates `for_each_engine()` and calls `intel_engine_dump()`.

### Control Flow
Registration adds the `engines` file under a GT debugfs root. Opening the file creates a seq_file; reading it prints every engine's debug dump with the engine name as a label.

### State, Persistence, And Dependencies
The file owns no persistent state. It reads `gt->engine[]` and engine-private state through `intel_engine_dump()`. Dependencies include DRM printers, GT debugfs helpers, engine dump support, and seq_file.

### Integration Points
Registered from GT debugfs setup and used by developers/support tooling to inspect engine state during hangs or scheduling problems.

### Risks
Dump content can race with active engine state and must rely on engine dump routines for locking/consistency. The file exposes only initialized engines.

### Test Signals
Reading debugfs on systems with different engine classes, during idle and active workloads, and after engine reset provides useful coverage.
