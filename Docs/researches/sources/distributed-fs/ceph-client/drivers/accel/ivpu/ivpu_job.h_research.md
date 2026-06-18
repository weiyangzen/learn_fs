<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_job.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_job.h

### Purpose
`ivpu_job.h` declares the job and command queue state shared by the ivpu driver and exposes job submission, command queue, completion, abort, and recovery entry points.

### Important APIs, Types, And Functions
`struct ivpu_cmdq` holds the firmware-visible `vpu_job_queue`, queue BO, optional preemption BOs, queue and doorbell IDs, priority, entry count, and legacy flag. `struct ivpu_job` records the submitting device/context, completion fence, command buffer VPU address, command queue/job/engine IDs, final status, preemption buffers, and flexible array of referenced BOs. Public functions include the four DRM ioctl handlers, `ivpu_context_abort_locked()`, queue reset/release helpers, job-done consumer init/fini, `ivpu_job_handle_engine_error()`, `ivpu_context_abort_work_fn()`, and `ivpu_jobs_abort_all()`.

### Control Flow
The header has no executable flow, but it defines the data contract used by submit ioctls, IPC callbacks, reset handling, and file cleanup. Callers must hold `file_priv->lock` for several command queue operations as documented by implementation lockdep assertions.

### State, Persistence, And Dependencies
State is per open-file context and per submitted job. The header depends on `ivpu_gem.h` for BO types and uses kernel `dma_fence`, DRM device/file declarations, and workqueue declarations through included or transitive headers.

### Integration Points
Consumers include `ivpu_job.c`, driver open/close paths, PM reset paths, IPC setup, sysfs busy accounting, and MMU fault handling. The queue/job fields mirror firmware ABI structures from `vpu_jsm_api.h`.

### Risks
Changes to `struct ivpu_job` or `struct ivpu_cmdq` can affect flexible-array allocation, cleanup ownership, and command queue registration assumptions. Any caller that bypasses the locking convention can race with queue destruction, context abort, or job completion.

### Test Signals
Compile tests should catch declaration drift. Runtime signals are clean open/close cleanup, successful command queue reuse, no BO/fence leaks after aborted jobs, and lockdep-clean submit/abort/reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_job.h -->
