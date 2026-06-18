## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_gem.c

### Purpose
`ivpu_gem.c` implements ivpu GEM/shmem buffer objects, VPU virtual-address allocation, DMA/IOMMU mapping, MMU binding/unbinding, PRIME import, BO creation/info/wait ioctls, and BO diagnostics.

### Important APIs, Types, And Functions
Core APIs include `ivpu_bo_bind()`, `ivpu_bo_unbind_all_bos_from_context()`, `ivpu_gem_create_object()`, `ivpu_gem_prime_import()`, `ivpu_bo_create()`, `ivpu_bo_create_runtime()`, `ivpu_bo_create_global()`, `ivpu_bo_free()`, `ivpu_bo_create_ioctl()`, `ivpu_bo_info_ioctl()`, `ivpu_bo_wait_ioctl()`, `ivpu_bo_list()`, and `ivpu_bo_list_print()`. The GEM object funcs implement free/open/status plus shmem pin/vmap/mmap helpers.

### Control Flow
Allocation validates cache flags, creates a shmem GEM object, marks WC mapping when requested, and adds it to `vdev->bo_list`. GEM open allocates a VPU VA in the file context using user, shave, or DMA range based on flags. Bind obtains an sg_table from shmem or dma-buf import, maps it into the ivpu MMU context at `bo->vpu_addr`, and records `mmu_mapped`. Free removes the BO from the list, unmaps MMU and DMA/sg resources under reservation lock, and releases shmem. Runtime/global helpers allocate device-internal BOs, bind them immediately, and vmap mappable buffers. Wait ioctl waits on the reservation object and returns command-buffer job status.

### State, Persistence, And Dependencies
BO state is split across DRM GEM/shmem fields, `struct ivpu_bo`, `drm_mm_node` VPU VA allocation, sg_table/DMA mappings, MMU page tables, and the global BO list. Dependencies include DRM shmem/GEM/PRIME, dma-buf, dma-resv, ivpu MMU context, hardware address ranges, and UAPI BO flags.

### Integration Points
Firmware, IPC, jobs, command queues, user allocations, PRIME import, debugfs BO listing, and MMU context cleanup all use this BO layer.

### Risks
Unbind order is delicate: MMU unmap, address range removal, DMA unmap, sg free, and imported attachment unmap differ by BO origin. BOs can belong to only one context; re-opening in another context returns `-EALREADY`. Imported objects are not re-exportable in `ivpu_drv.c`. Missing reservation locking can race map/free. User-visible flags select security-sensitive address ranges.

### Test Signals
Test BO creation with all valid/invalid flags, mmap/vmap paths, context close unbinds, PRIME import and no re-export, bind failures, wait timeout and completion status, runtime/global BO allocation, list output, and fault/unwind paths under MMU map or DMA map failure.
