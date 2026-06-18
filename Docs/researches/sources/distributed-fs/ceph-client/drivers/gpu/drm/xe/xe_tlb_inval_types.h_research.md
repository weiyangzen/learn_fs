<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval_types.h

## Purpose

`xe_tlb_inval_types.h` defines backend operations, frontend state, invalidation fences, and invalidation batches.

## Important APIs, Types, and Functions

`struct xe_tlb_inval_ops` defines backend callbacks for all, GGTT, PPGTT/range, initialized, flush, and timeout delay. `struct xe_tlb_inval` stores backend private pointer, Xe device, ops, seqno state, locks, pending fence list, delayed timeout work, workqueues, and fence lock. `struct xe_tlb_inval_fence` wraps dma-fence with TLB client, list link, seqno, and invalidation time. `struct xe_tlb_inval_batch` stores one fence per possible GT across all tiles.

## Control Flow

The frontend uses ops to submit hardware/firmware invalidations and uses these state fields to track completion by seqno. Batch objects collect per-GT fences for tile-mask invalidations.

## State and Persistence Behavior

`xe_tlb_inval` persists per GT. Fences are transient per invalidation. Batches are caller-owned stack or embedded objects reset after wait.

## Dependencies and Integration Points

The header depends on workqueue and dma-fence types plus Xe device constants for maximum tile/GT count. Backends such as GuC must implement the ops contract.

## Risks and Test Signals

Backend ops must return `-ECANCELED` for mid-reset and provide correct timeout delays. Tests should validate backend/frontend contracts, pending list protection, and batch size coverage for maximum topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval_types.h -->
