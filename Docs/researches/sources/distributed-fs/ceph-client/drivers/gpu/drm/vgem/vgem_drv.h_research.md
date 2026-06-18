<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/vgem_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/vgem_drv.h

## Purpose
`vgem_drv.h` declares VGEM per-file fence state and ioctl helper prototypes shared by the driver and fence implementation.

## Important APIs, Types, and Functions
It defines `struct vgem_file` with `idr fence_idr` and `mutex fence_mutex`, includes UAPI `vgem_drm.h`, and declares `vgem_fence_open()`, `vgem_fence_attach_ioctl()`, `vgem_fence_signal_ioctl()`, and `vgem_fence_close()`.

## Control Flow
`vgem_open()` initializes `struct vgem_file` with `vgem_fence_open()`, ioctls operate on its IDR, and `vgem_postclose()` calls `vgem_fence_close()`.

## State and Persistence Behavior
The per-file IDR persists for an open DRM file and owns references to active dma-fences until signal, timeout, or close.

## Dependencies and Integration Points
The header depends on DRM GEM/cache headers and the VGEM UAPI. It is the contract between `vgem_drv.c`, `vgem_fence.c`, and userspace ioctl structures.

## Risks
ID allocation and lifetime must remain per-file so fence handles cannot cross DRM file boundaries. UAPI structure changes are ABI-sensitive.

## Test Signals
Compile tests and ioctl tests using multiple DRM file descriptors validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/vgem_drv.h -->
