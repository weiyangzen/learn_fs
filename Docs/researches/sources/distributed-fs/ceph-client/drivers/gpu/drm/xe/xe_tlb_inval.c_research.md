<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval.c

## Purpose

`xe_tlb_inval.c` implements the frontend for Xe TLB invalidation. It assigns sequence numbers, tracks pending invalidation fences, handles completion/timeout/reset, and submits all/GGTT/range invalidations to a backend such as GuC.

## Important APIs, Types, and Functions

`xe_gt_tlb_inval_init_early()` initializes per-GT invalidation state and wires the GuC backend. `xe_tlb_inval_all()`, `xe_tlb_inval_ggtt()`, `xe_tlb_inval_range()`, and `xe_tlb_inval_vm()` issue invalidations. `xe_tlb_inval_done_handler()` processes backend completion seqnos. `xe_tlb_inval_fence_init()` initializes stack or heap fences. `xe_tlb_inval_idle()`, `xe_tlb_inval_batch_wait()`, and `xe_tlb_inval_range_tilemask_submit()` support batching across tiles/GTs.

## Control Flow

Issuing takes `seqno_lock`, prepares a fence with the current seqno, queues it on `pending_fences`, schedules timeout work if needed, calls the backend op, signals the fence immediately on backend error, and advances seqno modulo `TLB_INVALIDATION_SEQNO_MAX`. Completion updates `seqno_recv`, signals pending fences in order, and updates/cancels timeout work. Timeout flushes the backend, marks expired fences `-ETIME`, and reschedules if pending fences remain. Reset signals all pending fences and advances received seqno to cover outstanding requests.

## State and Persistence Behavior

`struct xe_tlb_inval` persists per GT and stores backend private data, ops, seqno, received seqno, locks, pending fence list, delayed timeout work, job workqueue, and timeout workqueue. Each fence holds a runtime PM reference until signaled.

## Dependencies and Integration Points

The file depends on DRM managed cleanup, dma-fence, runtime PM, GuC TLB invalidation backend, GT stats/users, Xe tracepoints, forcewake/MMIO includes, and VM/SVM invalidation callers.

## Risks and Test Signals

Risks include seqno wrap ordering, timeout races with completion, stack versus heap fence lifetime, backend `-ECANCELED` handling, and reset during early backend init. Tests should cover seqno wrap, invalid completion seqno, timeout signaling, backend error signaling, GGTT synchronous wait, multi-tile range submit, reset with pending fences, and lockdep under reclaim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval.c -->
