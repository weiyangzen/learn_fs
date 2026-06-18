<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval_job.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval_job.c

## Purpose

`xe_tlb_inval_job.c` wraps TLB invalidation in a dependency-scheduled job so invalidations can be ordered behind migration or bind work and represented by scheduler fences.

## Important APIs, Types, and Functions

`struct xe_tlb_inval_job` embeds `xe_dep_job`, TLB client, exec queue, VM, page reclaim list, refcount, invalidation fence, range, GT type, and armed flag. Public APIs create jobs, add page reclaim lists, preallocate dependency storage, push jobs, and manage references.

## Control Flow

Create allocates the job and heap invalidation fence, initializes scheduler job state, and takes queue/VM/runtime PM references. Push optionally swaps a preallocated stub dependency for a real unsignaled fence, arms the invalidation fence, locks migration job submission, pushes the scheduler job, records the scheduler finished fence as the queue's last TLB invalidation fence, and returns that finished fence. The run callback optionally builds a page reclaim list BO and issues range invalidation. Destruction frees PRL references, fence, scheduler job, queue/VM refs, and PM ref.

## State and Persistence Behavior

Jobs are reference-counted and live until scheduler completion and caller references are dropped. Page reclaim entries are copied into the job and retained until destroy. The invalidation fence is owned by the job until armed, then by dma-fence references.

## Dependencies and Integration Points

The file integrates dependency scheduler, DRM scheduler jobs, Xe exec queues, migration locking, page reclaim, TLB invalidation frontend, VM lifetime, runtime PM, and queue last-fence tracking.

## Risks and Test Signals

Risks include requiring `xe_tlb_inval_job_alloc_dep()` before pushing with an unsignaled fence in reclaim paths, PRL fallback to PPC flush when PRL BO creation fails, and lifetime split between scheduler finished fence and internal invalidation fence. Tests should cover dependency preallocation, signaled/unsignaled dependencies, PRL attach, destroy before arm, destroy after arm, and queue last-fence update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval_job.c -->
