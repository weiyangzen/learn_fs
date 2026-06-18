# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_gem.c

## Purpose

`armada_gem.c` implements Armada GEM buffer allocation, backing, CPU mapping, dumb buffers, private GEM ioctls, pwrite updates, mmap for shmem-backed objects, PRIME export/import, and scanout mapping of imported buffers. It supports page-backed small objects, contiguous linear graphics-memory objects, shmem objects, and imported dma-bufs.

## Important APIs, Types, And Functions

Exported APIs include `armada_gem_free_object()`, `armada_gem_linear_back()`, `armada_gem_map_object()`, `armada_gem_alloc_private_object()`, `armada_gem_dumb_create()`, `armada_gem_create_ioctl()`, `armada_gem_mmap_ioctl()`, `armada_gem_pwrite_ioctl()`, `armada_gem_prime_export()`, `armada_gem_prime_import()`, and `armada_gem_map_import()`. The file defines `armada_gem_vm_ops`, object funcs, and custom dma-buf ops for PRIME export.

## Control Flow

Private objects are initialized without shmem; normal GEM create ioctl initializes shmem-backed GEM. Dumb create computes aligned pitch/size, allocates a private object, backs it with `armada_gem_linear_back()`, creates a handle, and drops the allocation reference. Linear backing uses small page allocations for <=8192-byte CPU-only objects, otherwise allocates from the master `drm_mm`, clears the WC mapping, and records physical/device addresses. Mapping ioremaps linear objects. Pwrite validates user memory, looks up a kernel-mapped object, bounds-checks offset/size, copies data, and calls an optional update callback, used by cursor updates. PRIME export maps shmem/page/linear objects into sg tables; import attaches a dma-buf lazily and `armada_gem_map_import()` later maps it for scanout, requiring one sufficiently large DMA segment.

## State And Persistence Behavior

`struct armada_gem_object` stores address, physical address, device address, mapped flag, linear drm_mm node, small backing page, imported sg table, and optional update callback. Linear allocator state persists in `priv->linear` under `linear_lock`. Imported attachments persist until object free, where mapped attachments are unmapped and PRIME state destroyed.

## Dependencies And Integration Points

The file depends on dma-buf, DMA mapping, shmem, DRM PRIME/GEM helpers, Armada custom uAPI structs, private driver state, and GEM header definitions. It integrates with framebuffer creation, fbdev allocation, cursor upload/update, dumb-buffer ABI, and PRIME sharing.

## Risks And Edge Cases

`armada_gem_pwrite_ioctl()` returns `-EINVAL` without dropping the GEM reference if `!dobj->addr`, which is a leak risk in that path. Imported dmabufs with multiple sg entries or short DMA length are rejected but the failure path leaves `dobj->sgt` set after `armada_gem_map_import()` errors, so callers/free paths must handle it carefully. Linear objects use physical addresses and WC ioremap rather than DMA coherent allocation by design. PRIME mmap is disabled. Small page-backed objects are CPU accessible but not marked mapped for scanout.

## Test Signals

Tests should cover dumb create/pitch/handle lifecycle, private GEM create/mmap/pwrite, cursor pwrite update callback, linear allocator exhaustion/free, small cursor object allocation, fbdev mapping, PRIME export/import self-import and foreign import, scattered import rejection, object free leak checks, mmap fault insertion for linear objects, and refcount/error-path testing around pwrite and import failures.
