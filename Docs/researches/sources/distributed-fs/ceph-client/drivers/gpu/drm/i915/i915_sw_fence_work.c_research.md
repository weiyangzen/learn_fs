<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence_work.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence_work.c

## Purpose
Adapts an i915 software-fence dependency chain into a dma-fence-backed work item.

## Important APIs, types, and functions
- `dma_fence_work_init()` initializes the embedded dma fence, software fence chain, work item, and ops.
- `dma_fence_work_chain()` adds a dma-fence dependency to the chain.
- Internal `fence_notify()` schedules or directly executes work when the chain completes.
- Internal `fence_work()`, `fence_complete()`, and dma fence ops handle execution, release callback, signaling, and object lifetime.

## Control flow
Callers initialize the object, chain dependencies, then commit the software fence from the header helper. When the chain completes, errors are copied to the dma fence. If no error exists, the code takes a dma-fence reference and either runs the work immediately when `DMA_FENCE_WORK_IMM` is set or queues it to `system_dfl_wq`. Work execution calls owner `ops->work()`, releases owner resources if requested, signals the dma fence, and drops the temporary reference.

## State and persistence
`struct dma_fence_work` owns a dma fence, software chain, one embedded dma-fence callback for chaining, a work item, ops pointer, and spinlock. The dma fence remains visible to external waiters until signaled and released.

## Dependencies and integration points
Depends on `i915_sw_fence`, Linux workqueues, dma-fence, and owner-provided work/release ops. Used where i915 needs asynchronous work with a standard dma-fence completion object.

## Risks
Immediate execution is only safe before publication and when no other thread can add waits. Error paths must still signal the dma fence. The release callback runs before fence signaling in `fence_complete()`, so owner lifetime rules must account for any waiter-visible state.

## Test signals
Fenced work unit tests or consumers, dependency-chain tests, immediate-vs-queued execution tests, dma-fence wait/signaling checks, and error propagation from chained fences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence_work.c -->
