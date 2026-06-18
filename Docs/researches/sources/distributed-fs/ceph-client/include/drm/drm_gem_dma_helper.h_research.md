# sources/distributed-fs/ceph-client/include/drm/drm_gem_dma_helper.h

Purpose: Defines the DMA-backed GEM object subtype and helper APIs/macros for simple drivers that allocate contiguous or DMA-address-contiguous scanout buffers.

Important APIs, types, and functions: Defines `struct drm_gem_dma_object`, `to_drm_gem_dma_obj()`, create/free/print/sg-table/vmap/mmap helpers, `drm_gem_dma_vm_ops`, object-func wrapper inlines for free/print/get_sg_table/vmap/mmap, dumb-create helpers, PRIME import helpers, driver-op macros `DRM_GEM_DMA_DRIVER_OPS*`, no-MMU `drm_gem_dma_get_unmapped_area()`, and `DEFINE_DRM_GEM_DMA_FOPS()`.

Control flow: Drivers create DMA GEM objects for dumb buffers or internal framebuffers. The object stores CPU virtual address, DMA address, optional imported sg table, and non-coherent flag. Object funcs wrap the DMA helpers for free, mmap, vmap, and PRIME export. Driver op macros install default dumb-create and PRIME import behavior, with variants that ensure imported buffers are virtually mapped. File-op macros install DRM open/release/ioctl/poll/read/mmap behavior plus no-MMU get-unmapped-area support.

State and persistence: State is per GEM DMA object: base GEM object, DMA address, sg table, CPU virtual address, and coherency flag. It persists until the GEM refcount reaches zero and the DMA allocation/import attachment is freed.

Dependencies and integration points: Depends on DRM file/ioctl/GEM infrastructure, DMA allocation/mapping, PRIME dma-buf imports, sg tables, VM operations, dumb-buffer IOCTLs, and no-MMU mapping support. It integrates with framebuffer DMA helpers and fbdev DMA helpers.

Risks and test signals: Risks include assuming physical contiguity for multi-entry sg imports, cache maintenance omissions for non-coherent buffers, mmap attributes mismatching allocation attributes, imported-buffer vmap availability, no-MMU mapping errors, and dumb-buffer size overflow. Test native allocation, imported sg tables, vmap-required imports, mmap from userspace, PRIME export/import, non-coherent CPU writes, no-MMU builds, and dumb framebuffer creation.
