<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sched_job.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sched_job.c

Purpose: implements Xe scheduler job allocation, fence setup, runtime PM accounting, job push, error propagation, start/completion checks, user-fence metadata, snapshots, and dependency registration.

Important APIs and control flow: module init creates separate slabs for single and parallel/migration jobs. `xe_sched_job_create()` allocates a job, references the exec queue, initializes DRM scheduler job state, preallocates LRC seqno fences and chain fences, copies batch addresses, increments queue job count, and takes runtime PM. `xe_sched_job_arm()` asserts VM locking, determines whether TLB flush is needed, initializes LRC fences, chains parallel fences, stores the final fence, and arms DRM scheduler state. `xe_sched_job_push()` pushes to the DRM scheduler entity with a temporary ref. `xe_sched_job_set_error()` sets errors under fence locks and runs fence IRQ work.

State and dependencies: `struct xe_sched_job` owns refs to queue and fences, per-width `ptrs`, optional user fence data, ring-op flags, and DRM scheduler base. Dependencies include DRM scheduler, DMA fences/chains, LRC seqno fences, VM locking/TLB state, PM runtime, tracing, and exec queue lifecycle.

Risks and test signals: fence chain setup is sensitive to queue width and migration jobs use width 2 even if queue width differs. Tests should cover allocation failure cleanup, parallel fence chains, migration job slab choice, VM TLB invalidation flagging, error propagation to chain-contained fences, and runtime PM ref balance on destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sched_job.c -->
