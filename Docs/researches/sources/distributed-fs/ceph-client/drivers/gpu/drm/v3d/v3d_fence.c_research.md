<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_fence.c

Purpose: Creates V3D dma_fence objects and supplies fence driver/timeline names.

Important APIs/types/functions: `v3d_fence_create()` allocates `struct v3d_fence`, assigns device, queue, monotonically increasing queue seqno, and calls `dma_fence_init()` with queue lock/context. `v3d_fence_ops` implements `get_driver_name` and `get_timeline_name`.

Control flow: Submit paths create IRQ fences per hardware queue; IRQ handling signals them when work completes.

State and persistence: Fence state is per allocation: seqno, queue, device pointer, and embedded `dma_fence`. Queue state holds `emit_seqno` and `fence_context`.

Dependencies and integration points: Integrates Linux dma-fence and V3D queue state. Timeline names are used by debugging/synchronization tooling.

Risks and test signals: The CPU/cache-clean queues are not named in `get_timeline_name()` and may return NULL if used directly. Tests should validate seqno monotonicity, fence signaling, timeline names for all submitted queues, and cleanup on allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_fence.c -->
