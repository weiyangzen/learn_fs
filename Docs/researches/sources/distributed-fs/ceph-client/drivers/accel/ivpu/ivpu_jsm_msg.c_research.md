<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_jsm_msg.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_jsm_msg.c

### Purpose
`ivpu_jsm_msg.c` is the typed firmware IPC wrapper layer for Job Scheduler Module commands. It builds `struct vpu_jsm_msg` requests, sends them on the correct IPC channel, waits for expected response message types, decodes selected response payloads, and maps serious failures into PM recovery when required.

### Important APIs, Types, And Functions
`ivpu_jsm_msg_type_to_str()` provides trace/debug names for every JSM message enum. Doorbell and context APIs are `ivpu_jsm_register_db()`, `ivpu_jsm_unregister_db()`, `ivpu_jsm_context_release()`, and `ivpu_jsm_hws_register_db()`. Engine APIs are `ivpu_jsm_get_heartbeat()`, `ivpu_jsm_reset_engine()`, `ivpu_jsm_preempt_engine()`, and `ivpu_jsm_hws_resume_engine()`. HWS command queue APIs include create, destroy, priority-band setup, context scheduling properties, and scheduling log setup. Telemetry/debug/power APIs include trace capability/config, dynamic debug control, metric streamer start/stop/update/info, D0i3 entry, DCT enable/disable, and state dump.

### Control Flow
Each function initializes a request with a fixed `type`, fills only the relevant union payload, then calls `ivpu_ipc_send_receive()`, `ivpu_ipc_send_receive_internal()`, or `ivpu_ipc_send_and_wait()` with the expected response type and timeout from `vdev->timeout`. Some functions validate `engine == VPU_ENGINE_COMPUTE`. Metric update validates returned `bytes_written` against the buffer size, and metric info rejects zero sample size. Engine reset increments `pm->engine_reset_counter`; reset or HWS resume failures trigger `ivpu_pm_trigger_recovery()`.

### State, Persistence, And Dependencies
This file stores no long-lived state itself. It modifies firmware state: doorbell registrations, command queue registrations, scheduling properties, trace configuration, metric streams, power DCT state, D0i3 save state, and engine reset state. Dependencies are `ivpu_ipc`, `ivpu_pm`, hardware idle polling, `vpu_jsm_api.h`, and device timeout settings.

### Integration Points
Job submission uses doorbell/HWS queue calls; PM uses heartbeat, D0i3, DCT, and state dump calls; debugfs/fw log paths can use trace and dynamic debug calls; metric-streamer ioctls use the metric APIs; context abort uses context release and HWS resume/reset calls. The tracepoint code depends on `ivpu_jsm_msg_type_to_str()`.

### Risks
The functions encode a firmware ABI. Wrong response type, channel, timeout, or payload union member can produce hangs or silent firmware misconfiguration. Some warnings are ratelimited, so repeated transient firmware failures may be easy to miss. D0i3 and DCT calls use internal IPC paths and must be coordinated with runtime PM state. Metric update has explicit overflow checking, but callers must still serialize buffer ownership.

### Test Signals
Useful signals include firmware boot with successful priority-band setup, doorbell register/unregister cycles in OS and HWS modes, heartbeat progress during long jobs, engine reset and resume after injected faults, trace config round trips, dynamic-debug commands, metric streamer start/update/stop with nonzero sample sizes, D0i3 entry on suspend, and DCT enable/disable acknowledgments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_jsm_msg.c -->
