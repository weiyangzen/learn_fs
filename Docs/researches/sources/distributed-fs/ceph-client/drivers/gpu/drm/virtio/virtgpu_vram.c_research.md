# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_vram.c

## Purpose

`virtgpu_vram.c` implements virtio-gpu GEM objects backed by host-visible blob VRAM. It creates private GEM objects, issues blob resource commands, maps them into the host-visible aperture, supports userspace mmap through PFN remapping, and exports DMA-BUF mappings for mappable and UUID-addressable resources.

## Important APIs, types, and functions

The object functions table `virtio_gpu_vram_funcs` wires GEM open/close, `virtio_gpu_vram_free()`, `virtio_gpu_vram_mmap()`, and PRIME export. `virtio_gpu_vram_create()` allocates `struct virtio_gpu_object_vram`, initializes GEM size and mmap offset, obtains a resource id, creates a blob resource, and optionally calls `virtio_gpu_vram_map()`. DMA-BUF helpers are `virtio_gpu_vram_map_dma_buf()` and `virtio_gpu_vram_unmap_dma_buf()`. `virtio_gpu_is_vram()` distinguishes this object class.

## Control flow and state

Creation aligns size, initializes a fake GEM mmap offset, creates a virtio blob resource, and if `VIRTGPU_BLOB_FLAG_USE_MAPPABLE` is set inserts a node in `vgdev->host_visible_mm`. The map command stores an aperture-relative offset and asynchronously updates `vram->map_state`/`map_info` through `virtgpu_vq.c`. mmap waits until the map leaves `STATE_INITIALIZING`, validates object flags and requested range, sets mixed-map/non-expand VMA flags, adjusts page protection based on virtio cache mode, and remaps the aperture PFN range.

Freeing checks whether the object was created, conditionally unmaps allocated host-visible aperture space, unrefs the host resource, and notifies the virtqueue. DMA-BUF export returns a real one-entry sg table for mappable resources and a stub sg table for non-mappable blob resources when a virtio peer can import by UUID.

## Dependencies and integration

The file depends on DRM GEM/VMA helpers, `drm_mm` host-visible allocation state, virtio blob commands from `virtgpu_vq.c`, DMA resource mapping, and UUID export capability for non-mappable sharing. It is a bridge between DRM userspace mmap, DMA-BUF import/export, and virtio host-visible memory.

## Risks and test signals

Risks include leaked `drm_mm` nodes on command failure, blocking waits if map completion never arrives, cache-mode mismatch, PFN overflow checks, and stub sg tables that only work for UUID-capable virtio devices. Test signals include blob creation with and without mappable flags, mmap range validation, PRIME export/import, and unmap/unref ordering during object teardown.
