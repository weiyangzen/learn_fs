<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/Makefile

## Purpose
`virtio/Makefile` links the VirtIO GPU DRM driver from core, KMS, GEM, VRAM, display, virtqueue, fence, object, debugfs, plane, ioctl, PRIME, trace, and submit sources.

## Important APIs, Types, and Functions
The key build variable is `virtio-gpu-y`, listing `virtgpu_drv.o`, `virtgpu_kms.o`, `virtgpu_gem.o`, `virtgpu_vram.o`, `virtgpu_display.o`, `virtgpu_vq.o`, `virtgpu_fence.o`, `virtgpu_object.o`, `virtgpu_debugfs.o`, `virtgpu_plane.o`, `virtgpu_ioctl.o`, `virtgpu_prime.o`, `virtgpu_trace_points.o`, and `virtgpu_submit.o`. `obj-$(CONFIG_DRM_VIRTIO_GPU)` links the module.

## Control Flow
Kbuild compiles and links the listed objects when `DRM_VIRTIO_GPU` is enabled.

## State and Persistence Behavior
No runtime state lives here.

## Dependencies and Integration Points
The list includes files outside this research item (`virtgpu_vq.c`, `virtgpu_vram.c`) that provide command transport and VRAM/blob support used by researched files.

## Risks
Omitting transport or trace objects would create missing symbols or absent tracepoints. The object list must remain synchronized with declarations in `virtgpu_drv.h`.

## Test Signals
Allmodconfig, module build, and tracepoint build validation cover this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/Makefile -->
