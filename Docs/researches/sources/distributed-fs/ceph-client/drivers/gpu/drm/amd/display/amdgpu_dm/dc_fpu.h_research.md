# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/dc_fpu.h

### Purpose
`dc_fpu.h` declares DC FPU wrapper functions and provides macros that enforce the intended call pattern for floating-point sections in AMD display code.

### Important APIs, Types, And Functions
It declares `dc_assert_fp_enabled`, `dc_is_fp_enabled`, `dc_fpu_begin`, and `dc_fpu_end`. Public macros are `DC_FP_START`, `DC_FP_END`, and `DC_RUN_WITH_PREEMPTION_ENABLED`.

### Control Flow
Normal compilation maps `DC_FP_START/END` to begin/end calls with function and line metadata. When `CONFIG_DRM_AMD_DC_FP` is enabled, `DC_RUN_WITH_PREEMPTION_ENABLED` temporarily exits an active FPU section around code that needs preemption enabled, then reenters it. For `_LINUX_FPU_COMPILATION_UNIT`, direct macro use is blocked with `BUILD_BUG()` to keep low-level FPU implementation code from recursively using its own wrappers.

### State, Persistence, And Dependencies
The header stores no state. It depends on the implementation's per-CPU recursion tracking and on `CONFIG_DRM_AMD_DC_FP` build configuration. No persistence exists.

### Integration Points
Used throughout DCN code around floating-point calculations and by code that needs to query/assert FPU protection. It is paired with `dc_fpu.c` and `amdgpu_dm_trace.h` FPU trace events.

### Risks
Incorrect macro use can break preemption/FPU balance. `DC_RUN_WITH_PREEMPTION_ENABLED` only preserves an existing FPU section when configured for DC FP, so callers must understand behavior in non-FP builds.

### Test Signals
Compile FP and non-FP configurations, verify `_LINUX_FPU_COMPILATION_UNIT` guard behavior, and exercise nested `DC_FP_START/END` plus `DC_RUN_WITH_PREEMPTION_ENABLED` call sites.
