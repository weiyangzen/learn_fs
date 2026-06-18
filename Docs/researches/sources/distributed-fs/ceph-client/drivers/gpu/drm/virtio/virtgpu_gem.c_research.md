<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_gem.c

## Purpose
`virtgpu_gem.c` implements GEM object creation for dumb and resource objects, context attach/detach on GEM open/close, and helper arrays for batches of GEM objects used by command submission and delayed cleanup.

## Important APIs, Types, and Functions
Important functions are `virtio_gpu_mode_dumb_create()`, `virtio_gpu_gem_object_open()`, `virtio_gpu_gem_object_close()`, `virtio_gpu_array_alloc()`, `virtio_gpu_array_from_handles()`, `virtio_gpu_array_add_obj()`, `virtio_gpu_array_lock_resv()`, `virtio_gpu_array_unlock_resv()`, `virtio_gpu_array_add_fence()`, `virtio_gpu_array_put_free()`, and delayed free work helpers.

## Control Flow
Dumb create accepts only 32 bpp, computes pitch/size, selects a 2D host format, optionally uses shareable guest blob resources when blob support exists without virgl, creates the object, and returns handle/pitch. GEM open creates a virgl context if needed and attaches the resource to the file context. Close detaches from the context. Object arrays are allocated from handles, lock all reservation objects with ww locking when needed, reserve fence slots, add fences, and drop references either immediately or through a workqueue.

## State and Persistence Behavior
GEM handles own references to `virtio_gpu_object` instances. Per-file virgl contexts track attached resources on host side. Object arrays are transient command payload/lifetime containers and may be held until vq completion before references are dropped.

## Dependencies and Integration Points
The file depends on DRM GEM handle lookup, dma-resv locking, VirtIO GPU object creation, context attach/detach commands, and notify paths. Submit, ioctl transfer, plane, object, and vq code use object arrays.

## Risks
On GEM create handle failure, the code calls `drm_gem_object_release()` instead of the full object free path; this is a pattern worth reviewing for resource-ID cleanup in error cases. Reservation locking failures must unlock and drop refs. Delayed free work must be flushed before device teardown. Context attach can fail only by allocation here; host command completion is asynchronous.

## Test Signals
Tests should cover dumb create validation, blob-backed dumb resources, GEM open/close with virgl contexts, object array duplicate/missing handles, reservation deadlock avoidance, fence insertion, and delayed free flushing during remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_gem.c -->
