<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval.h

## Purpose

`xe_tlb_inval.h` declares the TLB invalidation frontend API and the inline fence wait helper.

## Important APIs, Types, and Functions

It exposes init, reset, all/GGTT/VM/range invalidation, fence initialization, completion handler, idle query, tile-mask range submit, batch wait, and `xe_tlb_inval_fence_wait()`.

## Control Flow

Backends call the done handler when firmware/hardware completes a seqno. VM/SVM and migration paths initialize fences, issue invalidations, and wait or batch-wait as needed.

## State and Persistence Behavior

The API operates on persistent `struct xe_tlb_inval` and transient `struct xe_tlb_inval_fence` or batch objects.

## Dependencies and Integration Points

It includes TLB invalidation types and forward-declares GT/GuC/VM. It is used by GT init, VM binds/unbinds, SVM notifier handling, and TLB invalidation jobs.

## Risks and Test Signals

Callers must initialize fences before issuing and must wait/drop according to stack/heap ownership. Tests should validate each public issue path and batch error behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval.h -->
