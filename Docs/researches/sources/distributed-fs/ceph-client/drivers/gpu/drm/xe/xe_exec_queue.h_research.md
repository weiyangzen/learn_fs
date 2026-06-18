<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec_queue.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec_queue.h

## Purpose
`xe_exec_queue.h` declares the execution queue API and inline helpers used by submission, VM bind, scheduler, fdinfo, and backend code.

## Important APIs, types, and functions
The header exports creation helpers, fini/destroy/name assignment, refcount helpers, lookup, parallel and PXP predicates, multi-queue predicates and primary lookup, LR/idle/kill queries, create/destroy/property ioctls, max priority query, last-fence helpers, TLB invalidation fence helpers, run-tick update, HWSP rebase, and LRC accessors. `for_each_tlb_inval()` iterates primary/media TLB invalidation slots.

## Control flow and integration points
Inline control flow covers kref get/put, width-based parallel detection, PXP type detection, and multi-queue primary/secondary classification. The API is consumed by exec ioctl, VM bind, backend schedulers, fdinfo, suspend/resume, and SR-IOV migration fixups.

## State and persistence behavior
No state is owned by the header. It exposes operations over persistent `struct xe_exec_queue` state: refs, LRCs, VM/file ownership, last fences, TLB invalidation fences, and backend entities.

## Dependencies, risks, and test signals
Dependencies include exec queue and VM types plus DRM file/device declarations. Risks are stale inline predicates relative to `xe_exec_queue_types.h`, improper refcount use, and callers using unlocked last-fence functions outside destroy paths. Test signals include build coverage, kref lifetime stress, queue ioctl tests, VM bind fence tests, and suspend/resume rebase paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec_queue.h -->
