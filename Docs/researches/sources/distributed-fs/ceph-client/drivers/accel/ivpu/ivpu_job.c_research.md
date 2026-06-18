<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_job.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_job.c

### Purpose
`ivpu_job.c` implements Intel VPU job submission, command queue lifecycle, doorbell registration, DMA fence completion, job timeout integration, and context abort recovery. It is the main bridge between DRM ioctls, GEM buffer objects, firmware job queues, and JSM job-done notifications.

### Important APIs, Types, And Functions
The ioctl entry points are `ivpu_submit_ioctl()`, `ivpu_cmdq_submit_ioctl()`, `ivpu_cmdq_create_ioctl()`, and `ivpu_cmdq_destroy_ioctl()`. Internal queue management is handled by `ivpu_cmdq_create()`, `ivpu_cmdq_register()`, `ivpu_cmdq_unregister()`, `ivpu_cmdq_push_job()`, and `ivpu_cmdq_release_all_locked()`. Job tracking uses `struct ivpu_job`, a private `struct ivpu_fence` wrapper around `dma_fence`, `ivpu_job_create()`, `ivpu_job_submit()`, `ivpu_job_signal_and_destroy()`, `ivpu_jobs_abort_all()`, and `ivpu_cmdq_abort_all_jobs()`. Recovery entry points are `ivpu_job_handle_engine_error()`, `ivpu_context_abort_locked()`, `ivpu_context_abort_work_fn()`, and `reset_engine_and_mark_faulty_contexts()`.

### Control Flow
Legacy submission validates engine, priority, buffer count, command offset alignment, context existence, and MMU fault state before calling `ivpu_submit()` with `cmdq_id` 0. Managed-command-queue submission validates capability and explicit command queue IDs, then uses the same `ivpu_submit()` path. `ivpu_submit()` copies user BO handles, enters the DRM device, creates a job and fence, looks up and binds each GEM object, adds the job fence to BO reservations, takes `pm->reset_lock` for read, then calls `ivpu_job_submit()`. Submission runtime-resumes the device, locks submitted jobs and the file context, lazily acquires or creates a command queue, registers it with firmware, prepares preemption buffers, allocates a job ID in `submitted_jobs_xa`, writes a `vpu_job_queue_entry`, rings the doorbell, starts timeout detection, and leaves the job live until IPC completion.

### State, Persistence, And Dependencies
Persistent per-open state lives in `file_priv->cmdq_xa`, command queue BOs, queue doorbell IDs, queue priority, and optional per-queue preemption buffers. Device-wide in-flight state lives in `vdev->submitted_jobs_xa`, `submitted_jobs_lock`, `busy_start_ts`, `busy_time`, `faults_detected`, and the IPC consumer registered on `VPU_IPC_CHAN_JOB_RET`. Dependencies include DRM file/GEM/reservation APIs, `ivpu_bo` allocation/binding, `ivpu_jsm_msg` doorbell/HWS/reset calls, `ivpu_mmu` context event suppression, runtime PM helpers, firmware boot API structures, and VPU hardware doorbell writes.

### Integration Points
The file integrates with UAPI structs from `ivpu_accel.h`, job queue ABI from `vpu_jsm_api.h`, firmware scheduling mode from `vdev->fw->sched_mode`, IPC completion callbacks through `ivpu_ipc_consumer_add()`, and PM timeout/recovery logic in `ivpu_pm.c`. Hardware scheduling mode creates/destroys command queues and sets context scheduling properties through JSM; OS scheduling mode registers a doorbell directly and releases contexts with `VPU_JSM_MSG_SSID_RELEASE`.

### Risks
The critical risks are concurrency and lifetime ordering. Job submission touches `file_priv->lock`, `submitted_jobs_lock`, runtime PM, BO reservations, and reset locking; lock-order regressions can deadlock. Doorbell IDs are global xarray entries with per-user limits, so unregister/reset paths must keep `db_count` and `db_xa` consistent. Error paths after BO lookup can leave referenced GEM objects until job destruction, making `ivpu_job_destroy()` coverage important. The managed command queue API must reject legacy queue destruction and submissions after `has_mmu_faults`. Preemption buffer handling is split between user-supplied and kernel-created buffers; mappable user buffers are intentionally rejected.

### Test Signals
High-signal tests include successful legacy submit and command-queue submit, queue create/destroy with priority and turbo flags, queue-full `-EBUSY`, invalid BO handle and invalid offset failures, submission during reset, MMU fault followed by context abort, engine-reset-required job status in HWS mode, timeout-driven recovery, user-supplied preemption buffer validation, `npu_busy_time_us` changes while jobs are active, and fence signaling plus BO `job_status` propagation on success, error, and abort.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_job.c -->
