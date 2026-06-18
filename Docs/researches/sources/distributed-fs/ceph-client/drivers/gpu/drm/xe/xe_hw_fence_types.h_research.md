# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_fence_types.h

Purpose: defines state for hardware fence IRQ handling, fence contexts, and individual hardware fences.

Important types: `struct xe_hw_fence_irq` with spinlock, irq_work, pending list, and enabled flag; `struct xe_hw_fence_ctx` with GT, IRQ pointer, dma-fence context, next seqno, and name; `struct xe_hw_fence` with embedded dma fence, device pointer, name, seqno map, and pending-list link.

Control flow/state: contexts issue monotonically increasing seqnos; fences compare their seqno against a memory-mapped hardware-written value; IRQ handler scans `pending`.

Dependencies/integration: depends on Linux dma-fence, iosys-map, irq_work, list, and spinlock; forward-declares Xe device and GT.

Risks/test signals: lock lifetime is important because it is passed to `dma_fence_init`; `xe_hw_fence_irq_finish` synchronizes RCU for safe lock release. Tests should inspect pending-list cleanup and seqno wrap behavior.
