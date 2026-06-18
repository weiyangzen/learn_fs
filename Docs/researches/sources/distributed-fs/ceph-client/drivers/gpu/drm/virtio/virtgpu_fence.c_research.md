<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_fence.c

## Purpose
`virtgpu_fence.c` implements the VirtIO GPU dma-fence timeline used for control-queue commands and optional per-ring context fences.

## Important APIs, Types, and Functions
Public APIs are `virtio_gpu_fence_alloc()`, `virtio_gpu_fence_emit()`, and `virtio_gpu_fence_event_process()`. Internal dma-fence ops provide driver/timeline names and a defensive `signaled` callback warning if a fence leaks before emission.

## Control Flow
Fence allocation partially initializes a dma-fence with context `base_fence_ctx + ring_idx` and seqno 0. Emission under the fence driver spinlock assigns the next fence ID/seqno, takes a reference, links it into the pending list, traces emission, and adds fence fields to the virtio command header. Completion processing records last fence ID, finds the matching pending fence, signals older fences in the same context, sends any reserved DRM fence events, removes signaled fences from the list, and drops references.

## State and Persistence Behavior
`virtio_gpu_fence_driver` persists in `virtio_gpu_device` with current/last fence IDs, timeline context, pending fence list, and spinlock. Individual fences persist until host completion signals them or cleanup drops them.

## Dependencies and Integration Points
The file depends on dma-fence tracepoints, DRM event sending, virtio GPU command header flags, and locking state initialized in `virtgpu_kms.c`. Submit, object creation, transfers, plane flushes, and vq code allocate/emit fences.

## Risks
Fences must not be exposed before `virtio_gpu_fence_emit()` sets a nonzero seqno. Completion only signals strictly older fences in the same context plus the matched fence, so context/ring correctness is critical. Lost host completions leave fences pending. DRM event ownership is tied to fence completion under spinlock.

## Test Signals
Tests should cover monotonic fence IDs, per-ring contexts, out-of-order completions, event delivery, debugfs last/current fence values, leaked pre-emit fence warnings, and command headers with/without ring info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_fence.c -->
