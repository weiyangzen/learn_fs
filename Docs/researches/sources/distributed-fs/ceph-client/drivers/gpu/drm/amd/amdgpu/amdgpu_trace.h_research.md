## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_trace.h

Purpose: defines Linux tracepoints for major AMDGPU events: register reads/writes, interrupt vectors, BO creation/move/list status, command submission and scheduling, VM mapping/update/flush operations, PASID allocation/free, isolation changes, cleaner shader fences, IB pipe sync, and reset register dumps.

Important APIs and events: `TRACE_EVENT(amdgpu_device_rreg/wreg)` records device ID, register, and value. `amdgpu_iv` records interrupt vector metadata. `amdgpu_bo_create`, `amdgpu_bo_list_set`, `amdgpu_cs_bo_status`, and `amdgpu_bo_move` cover memory objects. `amdgpu_cs`, `amdgpu_cs_ioctl`, and `amdgpu_sched_run_job` record submissions and scheduler jobs. VM events include BO map/unmap, mapping/update/CS derived events, PTE updates, set/copy PTEs, and VM flush. PASID events share an event class. Other tracepoints cover isolation pointer transitions, cleaner shader sequence, pipe sync fence dependencies, and reset register dumps.

Control flow: tracepoint macros define per-event prototypes, argument capture, fast assignment, and print formats. `AMDGPU_JOB_GET_TIMELINE_NAME` derives scheduler fence timeline names for job events. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` make the header consumable by `define_trace.h`.

State and persistence: tracepoints do not own state; they snapshot runtime objects into trace buffers when enabled. Dynamic arrays are used for PTE destination dumps.

Dependencies and integration points: depends on Linux tracepoint infrastructure, AMDGPU object/job/VM/ring definitions, DMA fences, and scheduler objects. Called from register access, interrupt handling, CS ioctl/scheduler paths, VM code, BO management, PASID allocator, reset dump code, and IB scheduling.

Risks: tracepoint field access assumes objects are alive for the call duration; enabling verbose events like PTE updates can produce large trace output. Format strings and field widths are ABI-ish for tracing tooling. `AMDGPU_JOB_GET_TIMELINE_NAME` dereferences nested scheduler fence ops and assumes a valid job fence.

Test signals: kernel tracepoint compilation, `trace-cmd`/ftrace enabling for each event, command submission traces, VM update traces with dynamic arrays, and register access traces from `amdgpu_reg_access.c`.
