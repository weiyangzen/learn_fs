<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/Kconfig

## Purpose
`vgem/Kconfig` declares the virtual GEM provider driver used for software-renderer and buffer-sharing workflows without physical graphics hardware.

## Important APIs, Types, and Functions
The symbol is `DRM_VGEM`, a tristate depending on `DRM` and `MMU` and selecting `DRM_GEM_SHMEM_HELPER`.

## Control Flow
When enabled, the adjacent Makefile builds the `vgem` module. Userspace can then open a render node backed by shmem GEM objects and synthetic fences.

## State and Persistence Behavior
No runtime state is stored here; build configuration persists in the kernel/module image.

## Dependencies and Integration Points
The selected shmem helper matches VGEM's coherent GEM backing. The option integrates with Mesa/software rendering and dma-buf sharing tests.

## Risks
Without `MMU` or DRM shmem helper support the driver cannot provide expected mmap/dma-buf behavior. Build coverage must keep the dependency list current.

## Test Signals
Kconfig build tests for built-in/module/disabled states and IGT VGEM tests validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vgem/Kconfig -->
