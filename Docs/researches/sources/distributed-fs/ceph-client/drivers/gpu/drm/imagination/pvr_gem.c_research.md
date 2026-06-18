# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_gem.c

## Purpose
Implements PowerVR GEM buffer object creation, flag validation, CPU mapping policy, dma-buf export restrictions, userspace mmap restrictions, handle conversion, zeroing, and DMA-address lookup over shmem GEM backing storage.

## Important APIs, types, and functions
- `pvr_gem_object_create()` creates and zeroes PowerVR GEM objects with validated flags.
- `pvr_gem_create_object()` is the DRM object factory.
- `pvr_gem_object_into_handle()` and `pvr_gem_object_from_handle()` bridge PowerVR objects and DRM file handles.
- `pvr_gem_object_vmap()` and `pvr_gem_object_vunmap()` wrap shmem vmap/vunmap with cache synchronization for CPU-cached objects.
- `pvr_gem_get_dma_addr()` resolves a byte offset to a DMA address in the scatter-gather table.
- Object funcs customize free, export, mmap, pin, sg-table, vmap, and vunmap behavior.

## Control flow
Creation rejects zero-size or invalid flags, forces CPU cached mode on DMA-coherent devices, creates a shmem object, sets write-combine mapping policy when not CPU cached, stores immutable PowerVR flags, obtains/pins the sg table, synchronizes it for device access, and zeroes the full rounded object size through vmap. Export rejects PM/FW-protected objects with `-EPERM`. Mmap rejects objects without `DRM_PVR_BO_ALLOW_CPU_USERSPACE_ACCESS`.

CPU vmap locks the reservation object, maps through shmem, and if the object is CPU cached and already has an sg table, syncs for CPU. Vunmap syncs cached sg tables back for device before unmapping. DMA address lookup walks mapped DMA SG entries accumulating lengths until the requested offset falls within an entry.

## State and persistence
Persistent object state is `struct pvr_gem_object.flags` plus the shmem GEM base, page backing, sg table, vmap pointer, reservation object, and mmap offset. Flags are treated as immutable after creation and drive future CPU/device mapping behavior. BO contents are zeroed at creation.

## Dependencies and integration points
Depends on DRM GEM shmem helpers, PRIME export, dma-buf, DMA mapping APIs, device DMA coherency properties, and PVR VM/FW object code. Firmware objects are built on this GEM layer with implicit PM/FW protection.

## Risks
Cache coherency depends on correct flag selection and DMA syncs. `pvr_gem_get_dma_addr()` warns but proceeds if `sgt` is missing, which would dereference invalid state if callers violate backing assumptions. PM/FW protection is enforced for export and mmap, but all ioctl paths must also validate kernel-only flags.

## Test signals
Validate flag rejection, PM/FW protected export/mmap denial, userspace-access mmap success, DMA-coherent CPU cached override, zeroed allocation contents, vmap/vunmap cache sync paths, handle ownership transfer, and DMA address lookup across multi-entry sg tables.
