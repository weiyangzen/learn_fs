<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_prime.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_prime.c

## Purpose
`virtgpu_prime.c` implements PRIME/dma-buf export and import for VirtIO GPU, including virtio-dma-buf UUID support, VRAM map hooks, dynamic import attachments, imported-object resource creation, and invalidation handling.

## Important APIs, Types, and Functions
Public functions are `virtio_gpu_resource_assign_uuid()`, `virtgpu_gem_prime_export()`, `virtgpu_dma_buf_import_sgt()`, `virtgpu_gem_prime_import()`, and `virtgpu_gem_prime_import_sg_table()`. Important internals include `virtgpu_virtio_get_uuid()`, dma-buf map/unmap ops, `virtgpu_dma_buf_unmap()`, `virtgpu_dma_buf_free_obj()`, `virtgpu_dma_buf_init_obj()`, and `virtgpu_dma_buf_move_notify()`.

## Control Flow
Export assigns a resource UUID for non-blob objects when supported, rejects UUID for non-cross-device blobs, then exports with `virtio_dma_buf_export()` and takes DRM/GEM refs. UUID queries wait until async assignment leaves initializing state. Import returns the original GEM object for same-device virtio dma-bufs, falls back to generic PRIME import without blob support, or creates a private imported object with the exported reservation object, dynamically attaches the dma-buf, pins/maps it, converts its sg table into virtio memory entries, creates a shareable guest blob resource, and unpins. Move notifications detach/unmap existing imported mappings.

## State and Persistence Behavior
Exported objects track `uuid_state` and `uuid`. Imported objects store the dma-buf reservation object, attachment, sg table, host resource ID, and guest-blob state. Imported mappings persist until invalidation/free or object cleanup.

## Dependencies and Integration Points
The file depends on DRM PRIME/dma-buf helpers, `virtio_dma_buf`, DMA reservation locking, VRAM map helpers, object create/detach commands, response waitqueue, and resource UUID command support.

## Risks
`virtgpu_gem_prime_import()` leaks the allocated object/attachment reference on `virtgpu_dma_buf_init_obj()` failure by returning `ERR_PTR(ret)` without local cleanup after init failure already calls free only for some paths; this should be reviewed. UUID wait can block indefinitely if host never responds. Dynamic import invalidation must hold the dma-resv lock as asserted. Cross-device sharing requires correct blob flags.

## Test Signals
Tests should cover same-device import, generic fallback without blob support, cross-device blob export, UUID success/failure/timeouts, imported dma-buf invalidation, VRAM export map/unmap, attachment cleanup failure injection, and dma-buf reservation locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_prime.c -->
