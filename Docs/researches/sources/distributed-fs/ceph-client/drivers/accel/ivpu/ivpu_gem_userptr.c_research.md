## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_gem_userptr.c

### Purpose
`ivpu_gem_userptr.c` implements the UAPI path that turns page-aligned userspace memory into an ivpu BO by long-term pinning pages, exporting them as a dma-buf, and importing that dma-buf through the normal GEM path.

### Important APIs, Types, And Functions
The exported ioctl is `ivpu_bo_create_from_userptr_ioctl()`. Internal pieces include custom dma-buf ops for map/unmap/release, `ivpu_create_userptr_dmabuf()` to pin pages and build an sg_table, and `ivpu_bo_create_from_userptr()` to import the dma-buf and assign ivpu flags.

### Control Flow
The ioctl validates flags, nonzero pointer/size, page alignment, and `access_ok()`. Creation pins pages with `FOLL_LONGTERM` and `FOLL_WRITE` unless read-only, creates an sg_table over all pages, exports it as a dma-buf, imports it via `ivpu_gem_prime_import()`, creates a GEM handle, and returns the VPU address. Release unpins pages and frees the sg_table when the dma-buf is destroyed.

### State, Persistence, And Dependencies
Persistent state includes long-term pinned user pages, a dma-buf carrying the sg_table, the imported GEM object, VPU VA allocation, and eventual MMU mapping. Dependencies include GUP, dma-buf, sg tables, DRM GEM, ivpu PRIME import, and UAPI userptr flags.

### Integration Points
This provides `DRM_IVPU_BO_CREATE_FROM_USERPTR`, allowing userspace to submit existing memory to the NPU through the same BO/MMU path as shmem and imported dma-buf objects.

### Risks
Long-term pins can affect memory migration and must be released on every error path. Read-only flags control whether `FOLL_WRITE` is used and whether later MMU mappings are read-only. Only aligned full-page ranges are supported. The exported dma-buf uses `DMA_ATTR_SKIP_CPU_SYNC`, so cache coherency assumptions must match ivpu snooping/cache mode.

### Test Signals
Test invalid flags, null/unaligned/inaccessible ranges, partial GUP failure, sg allocation/export/import failure unwind, read-only versus writable pin flags, handle creation failure, context close/free releasing pins, and actual NPU access to userptr BOs.
