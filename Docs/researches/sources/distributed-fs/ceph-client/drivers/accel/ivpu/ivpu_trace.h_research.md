<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_trace.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_trace.h

### Purpose
`ivpu_trace.h` defines ftrace tracepoints for ivpu power-management events, job lifecycle events, and JSM message activity.

### Important APIs, Types, And Functions
Trace events are `pm`, `job`, and `jsm` under `TRACE_SYSTEM vpu`. `pm` records a string event. `job` records event, context ID, engine ID, and job ID. `jsm` records event, message type string, status, request ID, and firmware result.

### Control Flow
The header expands through Linux tracepoint macros. Call sites such as `trace_pm()`, `trace_job()`, and `trace_jsm()` become enabled/disabled tracepoint calls depending on ftrace configuration.

### State, Persistence, And Dependencies
Tracepoints do not persist driver state but expose runtime events to tracing buffers. Dependencies include `ivpu_drv.h`, `ivpu_job.h`, `vpu_jsm_api.h`, `ivpu_jsm_msg.h`, and `ivpu_ipc.h`. `TRACE_INCLUDE_PATH` is set to `.` and the file includes `trace/define_trace.h`.

### Integration Points
PM code traces suspend/resume transitions; job code traces job create/submit/done; IPC/JSM code can trace firmware messages. `ivpu_trace_points.c` instantiates the tracepoints.

### Risks
Tracepoint payloads dereference `job->file_priv` and JSM message pointers at call time, so callers must pass live objects. String fields point to static or caller-provided strings; unstable lifetime would corrupt trace output.

### Test Signals
Build with tracing enabled, inspect `/sys/kernel/tracing/events/vpu/*`, enable events while submitting jobs and suspending/resuming, and verify JSM types stringify correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_trace.h -->
