# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_services.c

### Purpose
`amdgpu_dm_services.c` provides small service hooks used by DC/DM code for elapsed-time calculation, performance trace emission, and SMU trace stubs.

### Important APIs, Types, And Functions
The file defines `dm_get_elapse_time_in_ns`, `dm_perf_trace_timestamp`, `dm_trace_smu_enter`, and `dm_trace_smu_exit`.

### Control Flow
Elapsed time returns the difference between current and last timestamps. Performance tracing forwards current read/write counters and last-entry pointers from `ctx->perf_trace` to `trace_amdgpu_dc_performance`, which also updates the last counters. SMU enter/exit trace hooks are currently empty.

### State, Persistence, And Dependencies
State is limited to caller-provided timestamps and `dc_context->perf_trace` counters. There is no persistence. It depends on `amdgpu_dm_trace.h` tracepoints and DC context service expectations.

### Integration Points
DC code can call these service hooks for instrumentation without depending directly on Linux tracepoint implementation details. The empty SMU hooks reserve integration points for future SMU tracing.

### Risks
`dm_perf_trace_timestamp` assumes `ctx->perf_trace` is valid. Timestamp subtraction has no wrap handling beyond unsigned arithmetic. Empty SMU hooks may hide expected tracing if callers assume they emit events.

### Test Signals
Enable AMDGPU DM tracepoints and verify performance counter deltas during register-heavy modesets; build with service users enabled.
