# sources/distributed-fs/ceph-client/drivers/dma-buf/dma-fence-array.c

Purpose: implements a dma-fence container that represents a set of fences and signals either when all member fences signal or, optionally, when any member signals.

Important APIs/types/functions: exports `dma_fence_array_ops`, `dma_fence_array_alloc()`, `dma_fence_array_init()`, `dma_fence_array_create()`, `dma_fence_match_context()`, `dma_fence_array_first()`, and `dma_fence_array_next()`. Internal callbacks track pending fence count and error propagation.

Control flow: init initializes the base fence with array ops, an irq_work item, the pending counter, and the supplied fence array. `enable_signaling()` registers a callback on each contained fence and takes extra references on the array so callbacks cannot outlive the container. Each member callback records the first nonzero error, decrements `num_pending`, and queues irq_work when the array is complete. The irq_work clears the pending-error sentinel, signals the base fence, and drops the held reference. The signaled op either checks `num_pending` after software signaling is enabled or scans member signaled state before callbacks are armed.

State and persistence behavior: the array owns the supplied `struct dma_fence **fences` array and drops each member fence plus the array allocation in release. `base.error` temporarily carries `PENDING_ERROR` until real error propagation or completion.

Dependencies and integration points: depends on dma-fence core, irq_work, lockdep class separation, and fence-array public helpers used by reservation singleton export, fence unwrap/merge, and sync-file composition.

Risks and test signals: array containers must not contain other containers; the code warns and expects callers to flatten first to avoid recursion and stack overflow. Callback registration races are handled, but error propagation depends on members setting `f->error` before signaling. Test signals include all-vs-any completion semantics, first-error propagation, no premature free with outstanding callbacks, deadline forwarding to all members, and correct iteration through `first/next`.
