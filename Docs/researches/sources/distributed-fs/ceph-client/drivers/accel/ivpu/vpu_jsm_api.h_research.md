<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/vpu_jsm_api.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/vpu_jsm_api.h

### Purpose
`vpu_jsm_api.h` defines the packed Job Scheduler Module IPC ABI shared between the ivpu kernel driver and VPU firmware. It covers job queues, inline commands, statuses, IPC channels, message types, HWS scheduling structures, trace configuration, metric streamer descriptors, dynamic debug, power messages, and the top-level `struct vpu_jsm_msg`.

### Important APIs, Types, And Functions
The header provides `VPU_JSM_API_VER_*`, engine IDs, JSM status codes, IPC channel IDs, job and job-queue flag enums, priority bands, `struct vpu_job_queue_entry`, `struct vpu_inline_cmd`, `union vpu_jobq_slot`, `struct vpu_job_queue_header`, `struct vpu_job_queue`, HWS log/native-fence log structs, `enum vpu_ipc_msg_type`, payload structs for every request/response, metric group/counter descriptors, `union vpu_ipc_msg_payload`, and `struct vpu_jsm_msg`. There are no functions.

### Control Flow
The header defines message flow rather than executing it. Host sends async commands, general commands, or job queues; firmware sends job done, native fence, command response, metric notification, scheduling log notification, and power acknowledgments. `ivpu_jsm_msg.c` wraps these definitions, and `ivpu_job.c` writes `vpu_job_queue_entry` records consumed by firmware.

### State, Persistence, And Dependencies
All structures are packed to 8-byte alignment for binary compatibility and cacheline-sensitive IPC. Persistent shared state includes job queue header head/tail fields, queue slots, firmware-owned private job flags, metric streamer buffers, log buffers, and message request IDs/results. The API depends on Linux bit macros for some flag definitions and on firmware honoring reserved fields.

### Integration Points
Job submission, doorbell registration, HWS command queue management, engine reset/preempt, context release, heartbeat, PM D0i3/DCT/state dump, trace configuration, dynamic debug, metric streaming, and native fences all depend on this header. The trace layer stringifies `enum vpu_ipc_msg_type`.

### Risks
ABI drift is the main risk. Status ranges drive recovery decisions, especially engine-reset-required statuses. Queue flag semantics affect firmware scheduling and notification behavior. The metric update structure documents host-side hazards when current and next buffers are both nonzero. HWS suspend/resume/reset structures carry context and command queue IDs that must match driver state. Any packing or field-order change must be versioned and coordinated with firmware.

### Test Signals
Run firmware IPC compatibility tests, submit jobs in OS and HWS modes, exercise engine reset/preempt responses, native-fence queues on supported hardware, metric streamer start/update/info/notification, trace get/set/name/capability, dynamic debug control, D0i3 and DCT messages, and negative tests for non-success `result` and engine-reset-required statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/vpu_jsm_api.h -->
