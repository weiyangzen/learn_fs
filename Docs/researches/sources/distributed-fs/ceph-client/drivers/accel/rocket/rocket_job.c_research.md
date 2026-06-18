# sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_job.c

Purpose: implements Rocket job submission, DRM scheduler integration, hardware programming, interrupt completion, timeout reset, and per-file scheduler entity setup.

Important APIs and types: exports `rocket_ioctl_submit`, `rocket_job_init`, `rocket_job_fini`, `rocket_job_open`, `rocket_job_close`, and `rocket_job_is_idle`. Internal helpers manage `rocket_job`, `rocket_task`, custom completion fences, object reservation dependencies, and register programming.

Control flow: submit copies an array of UAPI jobs and task descriptors, looks up input/output BOs, takes an IOMMU domain ref, arms a DRM scheduler job, imports implicit dependencies, reserves output fences, and pushes to the sched entity. Scheduler `run_job` creates a hardware fence, resumes the selected core, attaches the job's IOMMU domain to the core group, stores `in_flight_job`, and writes PC/CNA/CORE registers with the current task's command buffer. IRQ handling masks/clears interrupts; the threaded handler either submits the next task in the same job or detaches IOMMU, signals the fence, autosuspends, and clears in-flight state. Timeout stops the scheduler, balances PM, detaches IOMMU, resets hardware, and restarts scheduling.

State and persistence: per-core scheduler, reset workqueue, fence context/seqno, in-flight job, and PM/IOMMU attachment are persistent. Per-job state owns BO refs, fences, task arrays, domain refs, and task progress.

Dependencies and integration: uses DRM scheduler, dma-fence, GEM reservation locks, IOMMU group attach/detach, PM runtime, Rocket register macros, IRQs, and UAPI structs.

Risks and test signals: high-risk paths include ignored errors in multi-job submit loop, PM/IOMMU cleanup when `pm_runtime_get_sync` or attach fails, reset while a job is in flight, output fence publication, scheduler entity core list allocation, and IRQ status error bits. Test multi-task jobs, multi-core scheduling, timeout reset, implicit sync, invalid user pointers, empty jobs, and remove during active scheduler work.
