<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sched_job_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sched_job_types.h

Purpose: defines scheduler job data structures and snapshots.

Important types: `struct xe_job_ptrs` stores each batch address, head offset, preallocated LRC fence, and chain fence. `struct xe_sched_job` embeds `drm_sched_job`, references queue/fence, stores refcount, LRC seqno, per-job user fence, timestamp sample, flags for TLB flush/forced reset/migration flush, and a flexible `ptrs[]`. `struct xe_sched_job_snapshot` records batch addresses for diagnostics.

State and risks: flexible array sizing must match slab selection in `xe_sched_job.c`. Tests should cover maximum queue width, migration two-batch jobs, and snapshot uncanonicalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sched_job_types.h -->
