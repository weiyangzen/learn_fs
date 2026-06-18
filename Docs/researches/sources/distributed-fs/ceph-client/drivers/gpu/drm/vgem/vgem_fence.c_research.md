<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/vgem_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/vgem_fence.c

## Purpose
`vgem_fence.c` implements synthetic dma-fence creation, attachment to GEM reservation objects, signaling, timeout, and per-file cleanup for VGEM.

## Important APIs, Types, and Functions
Key type: `struct vgem_fence`, embedding `dma_fence`, spinlock, and timer. Public functions are `vgem_fence_open()`, `vgem_fence_attach_ioctl()`, `vgem_fence_signal_ioctl()`, and `vgem_fence_close()`. Internal helpers include `vgem_fence_create()`, `vgem_fence_timeout()`, and `vgem_fence_release()`.

## Control Flow
Attach ioctl validates flags/padding, looks up the GEM handle, creates a fence with a 10-second timer, checks reservation-object conflicts for read/write usage, reserves and adds the fence under the reservation lock, stores it in the file IDR, and returns an ID. Signal ioctl validates flags, removes the fence from IDR with `idr_replace(..., NULL, id)`, returns `-ENOENT` for missing IDs, returns `-ETIMEDOUT` if the timer already signaled it, signals the fence, and drops the reference. Close iterates all remaining IDR entries, signals and puts each, then destroys IDR/mutex.

## State and Persistence Behavior
Fences persist in dma-resv objects and the per-file IDR until signaled, timed out, or closed. The timeout timer guarantees eventual signaling to avoid indefinite hangs.

## Dependencies and Integration Points
The file integrates Linux dma-fence, dma-resv, DRM GEM handle lookup, and VGEM UAPI flags. Consumers see fences through dma-buf reservation objects.

## Risks
Attach checks reservation signaled state before taking the reservation lock, so races with other users need careful dma-resv semantics review. Timed-out fences remain removable by signal ioctl but report `-ETIMEDOUT`. IDR replacement leaves NULL entries, and all callers must handle `ERR_PTR` results from `idr_replace()`.

## Test Signals
Tests should cover read/read sharing, read/write conflicts, invalid flags/pad, missing handles, timeout behavior, signal-after-timeout, double signal, close cleanup, and dma-buf consumers waiting on attached fences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/vgem_fence.c -->
