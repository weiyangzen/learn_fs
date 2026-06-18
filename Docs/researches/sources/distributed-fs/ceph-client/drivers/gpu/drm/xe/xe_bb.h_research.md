# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bb.h

## Purpose

`xe_bb.h` declares the public batch-buffer helper API for allocation, initialization, scheduler job creation, migration job creation, and cleanup.

## Important APIs, Types, and Functions

- `xe_bb_new(struct xe_gt *gt, u32 dwords, bool usm)`.
- `xe_bb_alloc(struct xe_gt *gt)`.
- `xe_bb_init(struct xe_bb *bb, struct xe_sa_manager *bb_pool, u32 dwords)`.
- `xe_bb_create_job(struct xe_exec_queue *q, struct xe_bb *bb)`.
- `xe_bb_create_migration_job(struct xe_exec_queue *q, struct xe_bb *bb, u64 batch_ofs, u32 second_idx)`.
- `xe_bb_free(struct xe_bb *bb, struct dma_fence *fence)`.

## Control Flow

There is no executable code in the header. Consumers include it to use the implementation in `xe_bb.c`.

## State and Persistence Behavior

The header exposes operations on `struct xe_bb` from `xe_bb_types.h`; ownership and deferred-free semantics are implemented in `xe_bb.c`.

## Dependencies and Integration Points

It includes `xe_bb_types.h` and forward-declares scheduler, execution queue, GT, suballocator, and fence types. It integrates with migration, command submission, and driver-generated batch construction.

## Risks and Edge Cases

- API users must respect ownership: every successful allocation/init needs a matching `xe_bb_free`.
- Migration job users must pass a valid second batch index and migration queue.
- The header does not document all sizing constraints; implementation comments and asserts provide details.

## Test Signals

Compile coverage catches signature drift. Runtime signals come from migration tests and any driver-generated batch users completing jobs without GPU faults or suballocator reuse issues.
