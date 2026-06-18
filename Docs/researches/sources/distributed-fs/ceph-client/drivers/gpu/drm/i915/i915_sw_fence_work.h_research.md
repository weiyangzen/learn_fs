<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence_work.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence_work.h

## Purpose
Declares the dma-fence work abstraction that combines a software-fence chain with executable work and a public dma fence.

## Important APIs, types, and functions
- `struct dma_fence_work_ops` provides name, work callback, and optional release callback.
- `struct dma_fence_work` embeds `struct dma_fence`, spinlock, `struct i915_sw_fence`, one dma-fence callback, work item, and ops pointer.
- `DMA_FENCE_WORK_IMM` requests immediate execution when safe.
- APIs: `dma_fence_work_init()`, `dma_fence_work_chain()`, `dma_fence_work_commit()`, and `dma_fence_work_commit_imm()`.

## Control flow
The inline commit helpers complete the software-fence chain. `commit_imm()` first sets the immediate flag only when the chain still has at most its initial pending count, then commits.

## State and persistence
The embedded dma fence is the externally observed persistent completion state. The software fence tracks internal prerequisites until commit/completion.

## Dependencies and integration points
Depends on dma-fence, spinlocks, workqueues, and `i915_sw_fence.h`. Included by modules that want fence-signaled asynchronous work without open-coding the chaining pattern.

## Risks
`commit_imm()` has strict publication requirements described in the comment. Reusing one embedded callback means the abstraction supports the intended simple chaining pattern rather than arbitrary many callbacks stored in the struct.

## Test signals
Build coverage, immediate execution tests, queued work completion, chained dependency errors, and dma-fence release lifetime validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence_work.h -->
