# sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_gem.c

Purpose: implements Rocket BO allocation, IOMMU mapping, cache ownership ioctls, and GEM object destruction.

Important APIs and types: exports `rocket_gem_create_object`, `rocket_ioctl_create_bo`, `rocket_ioctl_prep_bo`, and `rocket_ioctl_fini_bo`. Uses `rocket_gem_object` from `rocket_gem.h` and shmem GEM helpers.

Control flow: create BO allocates a shmem GEM object, attaches per-file state/domain, creates a GEM handle, obtains the SG table, allocates an IOVA range from the per-file `drm_mm`, maps the SG table into the per-file IOMMU domain with read/write permissions, and returns mmap offset plus NPU DMA address. Free unmaps IOMMU, removes the MM node, drops the domain ref, and frees shmem. Prep waits for write fences then syncs the SG table for CPU; fini syncs for device.

State and persistence: each BO stores driver private pointer, IOMMU domain ref, MM node, mapped size, and offset. Mapping persists for the GEM handle lifetime.

Dependencies and integration: uses DRM shmem GEM, DMA reservation fences, IOMMU mapping, per-file `drm_mm`, and Rocket UAPI structs.

Risks and test signals: test map failures after handle creation, partial IOMMU mappings, size alignment, cache sync before/after CPU access, BO free with outstanding page pins, and reserved-field validation.
