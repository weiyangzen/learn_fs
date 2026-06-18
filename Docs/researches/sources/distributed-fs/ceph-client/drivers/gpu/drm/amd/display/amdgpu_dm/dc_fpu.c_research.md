# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/dc_fpu.c

### Purpose
`dc_fpu.c` provides AMD DC wrappers around Linux kernel FPU sections. DCN calculations use floating point in selected paths, so this file tracks per-CPU recursion depth, calls `kernel_fpu_begin/end`, disables preemption while active, and emits trace events.

### Important APIs, Types, And Functions
The file defines per-CPU `fpu_recursion_depth` and implements `dc_assert_fp_enabled`, `dc_is_fp_enabled`, `dc_fpu_begin`, and `dc_fpu_end`.

### Control Flow
`dc_fpu_begin` warns if not in task context, disables preemption, increments the per-CPU depth, starts the kernel FPU section only for the outermost depth, and traces begin. `dc_fpu_end` decrements depth, ends the kernel FPU section when returning to zero, warns on negative depth, traces end, and reenables preemption. Assertion/query helpers read the per-CPU depth.

### State, Persistence, And Dependencies
Runtime state is per-CPU recursion depth and the kernel FPU ownership state. There is no persistence. Dependencies include Linux FPU APIs, preemption control, `ASSERT`, `WARN_ON_ONCE`, and `TRACE_DCN_FPU` from DC tracing.

### Integration Points
Macros in `dc_fpu.h` wrap these functions for DC code that uses floating point. Trace events are defined in `amdgpu_dm_trace.h`. The wrapper allows nested DC floating-point callers without repeated `kernel_fpu_begin`.

### Risks
Unbalanced begin/end calls leave preemption disabled or FPU state active/inactive incorrectly. Calls outside task context warn and may be unsafe. Per-CPU depth requires preemption to remain disabled while active. Negative depth indicates serious caller imbalance.

### Test Signals
Build with `CONFIG_DRM_AMD_DC_FP`, exercise DCN bandwidth/color calculations, enable `dcn_fpu` tracepoints, and run lockdep/preempt debugging to catch unbalanced or invalid-context FPU sections.
