<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_drv.h

## Purpose
`virtgpu_drv.h` is the central internal header for VirtIO GPU. It defines object, fence, queue, output, framebuffer, plane-state, device, file-private, capset, and command interfaces shared across KMS, GEM, ioctl, PRIME, object, fence, submit, vq, and VRAM code.

## Important APIs, Types, and Functions
Key definitions include driver version/name constants, state constants, `MAX_CAPSET_ID`, `MAX_RINGS`, `struct virtio_gpu_object_params`, `struct virtio_gpu_object`, `struct virtio_gpu_object_array`, `struct virtio_gpu_fence_driver`, `struct virtio_gpu_fence`, `struct virtio_gpu_vbuffer`, `struct virtio_gpu_output`, `struct virtio_gpu_framebuffer`, `struct virtio_gpu_plane_state`, `struct virtio_gpu_queue`, `struct virtio_gpu_device`, and `struct virtio_gpu_fpriv`. It declares all cross-file APIs for init, ioctls, GEM arrays, virtqueue commands, modeset, planes, fences, objects, PRIME, debugfs, VRAM, and submit.

## Control Flow
The header does not execute flow, but it defines the call graph: `virtgpu_drv.c` probes and calls KMS init; ioctl and plane paths create objects and command buffers; vq functions emit commands and complete fences; PRIME and VRAM paths manage dma-buf sharing and host-visible memory; submit path parses userspace execbuffers.

## State and Persistence Behavior
`struct virtio_gpu_device` is the persistent per-device state: virtio device, DRM device, scanouts, queues, fence timeline, ID allocators, response waitqueue, feature flags, host-visible memory manager, work items, capset cache, and locks. `struct virtio_gpu_fpriv` persists per DRM file for virgl context state, ring configuration, and debug name. `struct virtio_gpu_object` persists with GEM objects and tracks host resource ID, blob type, UUID state, and attachment.

## Dependencies and Integration Points
The header depends on Linux virtio GPU protocol definitions, DRM core/GEM/shmem/ioctl/fourcc/framebuffer/probe helpers, and UAPI `virtgpu_drm.h`. It bridges all source files in the driver and unresearched transport/VRAM files.

## Risks
This is a high-coupling ABI-like internal contract; field lifetime and locking comments must stay accurate. Object kind checks rely on `obj->funcs` pointer identity. Fixed scanout/ring/capset limits must match protocol. Functions declared here often transfer ownership of object arrays, fences, or command buffers to vq completion paths.

## Test Signals
Whole-driver build coverage, sparse/lockdep, object lifetime tests, multi-context/ring submit tests, PRIME import/export, KMS, and debugfs tests validate this header's contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_drv.h -->
