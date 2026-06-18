# File Research: sources/block-storage/kvdo/vdo/block-allocator.c

## Purpose

Implements a per-physical-zone block allocator for VDO slabs, including slab prioritization, allocation, load/drain/resume flows, slab scrubbing integration, metadata VIO pool ownership, and allocator statistics.

## Main Responsibilities

- Constructs and frees `struct block_allocator`.
- Registers read-only notification listeners.
- Owns:
  - slab summary zone,
  - priority table of allocatable slabs,
  - slab scrubber,
  - metadata VIO pool,
  - optional kcopyd eraser,
  - dirty slab journal list.
- Queues slabs for allocation or scrubbing.
- Allocates physical blocks from the current open slab.
- Releases unused provisional block references.
- Loads/rebuilds allocator-owned slabs and slab journals.
- Prepares slabs for allocation after load.
- Drains allocator I/O in ordered phases.
- Resumes allocator state in reverse drain order.
- Releases recovery-journal tail block locks held by dirty slab journals.
- Exposes allocator, slab journal, and refcount statistics.

## Key Allocation Behavior

Slabs are prioritized by approximate free block count. Full slabs get priority 0. Never-opened slabs get a reserved lower priority than high-free previously opened slabs, so VDO tends to reuse already-written physical space before opening fresh slabs, which is useful on thin-provisioned backing storage.

`vdo_allocate_block()` first tries the current `open_slab`. If it is exhausted, the slab is reprioritized, the highest-priority slab is dequeued/opened, and allocation is retried. Allocated blocks receive provisional references that must later be confirmed or released.

## Important Functions

- `vdo_make_block_allocator()` allocates the allocator and its components.
- `vdo_free_block_allocator()` tears down eraser, scrubber, VIO pool, priority table, and allocator memory.
- `vdo_register_slab_with_allocator()` records ownership.
- `vdo_queue_slab()` validates free count and routes slabs to scrubber or priority table.
- `vdo_adjust_free_block_count()` updates allocated-block count and reprioritizes non-open slabs.
- `vdo_allocate_block()` allocates from slabs.
- `vdo_release_block_reference()` decrements unused provisional references.
- `vdo_load_block_allocator()` starts per-zone allocator loading.
- `vdo_prepare_block_allocator_to_allocate()` loads/queues/scrubs slabs so allocation can begin.
- `vdo_register_new_slabs_for_allocator()` attaches grown slabs to the allocator.
- `vdo_drain_block_allocator()` starts phased drain.
- `vdo_resume_block_allocator()` starts reverse phased resume.
- `vdo_release_tail_block_locks()` asks dirty slab journals to release recovery-journal locks.
- `vdo_acquire_block_allocator_vio()` and `vdo_return_block_allocator_vio()` wrap the allocator’s VIO pool.
- `vdo_scrub_all_unrecovered_slabs_in_zone()` kicks scrub work.
- `vdo_dump_block_allocator()` logs allocator/slab state.

## Load, Drain, and Resume

Loading uses allocator admin state. For rebuild load, slab journals are erased with `dm_kcopyd_zero()` before finishing load. For recovery load, control passes to recovery journal replay into slab journals. Normal load applies a slab action to all slabs.

Draining runs these phases:
1. Stop slab scrubber.
2. Apply drain action to slabs.
3. Drain slab summary zone.
4. Assert VIO pool idle and finish drain.

Resume runs those phases in reverse:
1. Resume slab summary.
2. Apply resume action to slabs.
3. Resume slab scrubber.
4. Finish resume.

## Dependencies and Interactions

- Uses `admin-state.c` for allocator-local operation state.
- Uses `action-manager.c` as zone action callbacks from slab depot operations.
- Integrates with slabs, slab journals, refcounts, slab summaries, recovery journal, VIO pools, read-only notifier, and `dm-kcopyd`.

## Notable Edge Cases

- Invalid slab free-block counts force read-only mode.
- Unrecovered slabs are registered for scrubbing rather than allocation.
- Dirty slab journals are ordered by recovery-journal lock recency.
- kcopyd client destruction is requeued after callbacks to avoid same-stack deadlock.
- `vdo_release_block_reference()` ignores `VDO_ZERO_BLOCK`.
