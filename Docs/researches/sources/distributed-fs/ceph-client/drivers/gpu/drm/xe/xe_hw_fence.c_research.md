# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_fence.c

Purpose: implements Xe hardware completion fences as `dma_fence` objects backed by a seqno memory location and signaled from engine IRQ work.

Important functions: module slab init/exit, `xe_hw_fence_irq_init`, `xe_hw_fence_irq_finish`, `xe_hw_fence_irq_run`, `xe_hw_fence_ctx_init`, `xe_hw_fence_alloc`, `xe_hw_fence_free`, `xe_hw_fence_init`, and dma-fence ops for driver/timeline names, signaling, signaled check, and release.

Control flow: module init creates a cache. A fence context allocates a dma-fence context and initial seqno. Fence init stores device, name, seqno map, initializes list link, and calls `dma_fence_init` with the IRQ spinlock. Enabling signaling takes a fence ref and appends it to `irq->pending`; IRQ work scans pending fences under lock and drops refs for signaled fences. Engine IRQs call `xe_hw_fence_irq_run`.

State/persistence: `xe_hw_fence_irq` owns the pending list and lock per engine class. Each fence stores its seqno map and list node. Release uses RCU and the slab cache. `XE_FENCE_INITIAL_SEQNO` intentionally starts near wrap to expose wrapping issues early.

Dependencies/integration: integrates Linux dma-fence, irq_work, RCU, Xe map reads, engine IRQ dispatch, tracepoints, GT/device state, and hardware seqno writes from jobs.

Risks/test signals: pending list refs must balance when signaling or finishing. Signaled logic treats fence error as completion and compares hardware seqno with dma-fence seqno. Test IRQ signaling, software-completed fences that need immediate work kick, finish with pending fences, RCU slab destruction, early seqno wrap, and fence error signaling.
