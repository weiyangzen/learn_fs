<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval_job.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval_job.h

## Purpose

`xe_tlb_inval_job.h` declares the dependency-scheduled TLB invalidation job API.

## Important APIs, Types, and Functions

It exposes job creation, page reclaim list attachment, dependency preallocation, job push, and reference get/put operations.

## Control Flow

VM/migration code creates a job for a range, optionally embeds PRL data, preallocates dependency storage when needed, pushes the job behind a dependency fence, and drops references after use.

## State and Persistence Behavior

The opaque `xe_tlb_inval_job` object owns references described in the implementation until `xe_tlb_inval_job_put()` destroys it.

## Dependencies and Integration Points

It forward-declares dma-fence, dependency scheduler, exec queue, migrate, PRL, TLB invalidation, and VM types. It is consumed by VM bind/unbind and migration/reclaim paths.

## Risks and Test Signals

The create/push/get/put ownership contract is subtle. Tests should verify callers release creation references and that push returns a fence with a valid caller reference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval_job.h -->
