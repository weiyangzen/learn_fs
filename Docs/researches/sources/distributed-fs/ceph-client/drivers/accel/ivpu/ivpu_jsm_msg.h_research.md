<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_jsm_msg.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_jsm_msg.h

### Purpose
`ivpu_jsm_msg.h` declares the ivpu firmware JSM wrapper API used by jobs, PM, tracing, metric streaming, and debug paths.

### Important APIs, Types, And Functions
The header exports message-type stringification and wrappers for doorbells, heartbeat, engine reset/preempt, dynamic debug, trace capability/config, context release, D0i3 entry, HWS command queue lifecycle, scheduling logs/properties, priority bands, metric streamer operations, DCT, and state dumps.

### Control Flow
There is no runtime flow in the header. It defines a synchronous command/response contract: most functions return `0` or a negative errno after sending one JSM request.

### State, Persistence, And Dependencies
The header includes `vpu_jsm_api.h`, so it is tied to firmware ABI definitions and `struct vpu_jsm_msg`. It forward-uses `struct ivpu_device` through included driver headers.

### Integration Points
This is the shared boundary between higher-level driver code and firmware IPC. It is included by job, PM, sysfs/debug, trace, metric streamer, and IPC code.

### Risks
Prototype changes ripple through many subsystems and can break firmware ABI call sites. Because functions expose raw firmware fields like context IDs, command queue IDs, masks, and VPU addresses, callers must validate user input before invoking them.

### Test Signals
Compile coverage across ivpu modules is the first signal. Runtime tests should exercise all exported wrapper families at least once: submit, reset, suspend/resume, trace config, metric streamer, DCT, and state dump.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_jsm_msg.h -->
