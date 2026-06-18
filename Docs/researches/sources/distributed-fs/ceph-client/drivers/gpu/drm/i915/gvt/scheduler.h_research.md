<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/scheduler.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/scheduler.h

### Purpose
`scheduler.h` defines the GVT-g workload scheduler and per-workload data contracts used by virtual submission code. It exposes the queueing, setup, reset, cleanup, scheduler init, and workload creation APIs implemented in `scheduler.c`.

### Important APIs, Types, And Functions
The main types are `struct intel_gvt_workload_scheduler`, `struct shadow_indirect_ctx`, `struct shadow_per_ctx`, `struct intel_shadow_wa_ctx`, `struct intel_vgpu_workload`, and `struct intel_vgpu_shadow_bb`. It declares `intel_vgpu_queue_workload()`, `intel_gvt_init_workload_scheduler()`, `intel_gvt_clean_workload_scheduler()`, `intel_gvt_wait_vgpu_idle()`, `intel_vgpu_setup_submission()`, `intel_vgpu_reset_submission()`, `intel_vgpu_clean_submission()`, `intel_vgpu_select_submission_ops()`, `intel_vgpu_create_workload()`, `intel_vgpu_destroy_workload()`, and `intel_vgpu_clean_workloads()`.

### Control Flow
The header does not implement logic, but its structures encode the runtime flow: workloads move through per-engine `workload_q_head()` lists, can be shadowed, dispatched, completed through submission hooks, and tracked as current work by `intel_gvt_workload_scheduler`.

### State, Persistence, And Dependencies
Scheduler state includes current/next vGPU selection, current workload per engine, engine MMIO owners, wait queues, worker threads, and policy ops. Workload state includes request pointers, shadow MM refs, shadow ring buffer storage, guest ring register snapshots, ELSP descriptor fields, pending events, shadow batch buffers, WA context state, and OA registers. The header depends on i915 engine types and GVT execlist/interrupt definitions.

### Integration Points
GVT submission models include this header to build workloads from guest execlist descriptors. Scheduler policy code uses `sched_data` and `sched_ops`, while vGPU lifecycle code uses setup/reset/cleanup declarations.

### Risks
Most fields are shared across scheduler threads, context status notifiers, and reset paths, so lock ownership from the implementation is part of the API contract even though it is not visible in this header. The usercopy slab range for workload allocation depends on the position and size of `rb_tail`, so layout changes must be reviewed carefully.

### Test Signals
Compile-time coverage should catch struct dependency drift. Runtime tests should exercise queueing and cleanup across all engines, workload destruction after partial setup, and submission ops switching with active and inactive vGPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/scheduler.h -->
