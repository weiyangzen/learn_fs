<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_object.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_object.c

## Purpose
`virtgpu_object.c` implements VirtIO GPU GEM object allocation, host resource ID allocation/freeing, shmem memory-entry construction, resource creation commands, detach waiting, and object cleanup/free callbacks.

## Important APIs, Types, and Functions
Key functions are `virtio_gpu_resource_id_get()`, `virtio_gpu_cleanup_object()`, `virtio_gpu_create_object()`, `virtio_gpu_object_create()`, `virtio_gpu_detach_object_fenced()`, and `virtio_gpu_is_shmem()`. It defines shmem GEM object funcs including free/open/close/export/pin/vmap/mmap operations.

## Control Flow
Resource IDs come either from a monotonic atomic workaround for old virglrenderer or from an IDA. Object creation rounds size to pages, creates a shmem GEM object, allocates a resource ID, builds virtio memory entries from the shmem sg table using DMA addresses or physical addresses depending on DMA quirk, optionally locks a one-object reservation for fenced creation, emits blob/3D/2D resource create and attach commands, and returns the object. Free emits unref for created host resources and defers actual cleanup to completion; otherwise it directly frees shmem/VRAM/private object state. Fenced detach emits detach, notifies, waits for the fence, and drops it.

## State and Persistence Behavior
`virtio_gpu_object` stores persistent host resource ID, attachment/created/blob/dumb flags, UUID state, and optional imported sg table. Resource IDs persist until cleanup. Host resource lifetime is asynchronous and tied to command completion.

## Dependencies and Integration Points
The file depends on DRM GEM shmem helpers, DMA mapping/scatterlist APIs, module parameter `virglhack`, VirtIO command emitters, VRAM helpers, PRIME export, GEM open/close context attach, and fence infrastructure.

## Risks
The virgl workaround intentionally leaks/reuses no IDs and can eventually wrap. `virtio_gpu_object_create()` does not free `ents` after successful command submission because ownership is expected to transfer to vq command buffers; that ownership must remain true. Fenced detach waits uninterruptibly. Error paths must release resource IDs and GEM objects exactly once.

## Test Signals
Tests should cover resource ID allocation with/without workaround, DMA-quirk and normal sg entry building, blob/virgl/2D creation, creation failure injection, object unref completion cleanup, detach waits, shmem versus VRAM cleanup, and mmap/vmap/export behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_object.c -->
