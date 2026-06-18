<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_plane.c

## Purpose
`virtgpu_plane.c` implements VirtIO GPU primary and cursor plane behavior, including format translation, atomic validation, damage-based uploads, scanout commands, cursor commands, imported dma-buf preparation, fences, and DRM panic scanout support.

## Important APIs, Types, and Functions
Public APIs are `virtio_gpu_translate_format()` and `virtio_gpu_plane_init()`. Important callbacks/helpers include plane state duplicate, `virtio_gpu_plane_atomic_check()`, dumb BO update helpers, resource flush helpers, `virtio_gpu_primary_plane_update()`, imported object prepare/cleanup, `virtio_gpu_plane_prepare_fb()`, `virtio_gpu_plane_cleanup_fb()`, `virtio_gpu_cursor_plane_update()`, `virtio_drm_get_scanout_buffer()`, and `virtio_panic_flush()`.

## Control Flow
Plane init allocates a managed universal plane with primary or cursor formats and helper funcs, enabling damage clips for primary planes. Atomic check disallows scaling and marks full update when framebuffer changes. Prepare_fb prepares GEM, allocates fences for dumb/imported/blob paths, and attaches imported dmabuf memory if needed. Primary update handles nofb scanout clearing, merges damage, uploads dumb BO damage to host, updates scanout when FB/source or CRTC modeset changed, and flushes the damaged rectangle. Cursor update uploads new dumb cursor contents synchronously, then sends update or move cursor command. Cleanup releases fences and unpins imported buffers.

## State and Persistence Behavior
Plane state embeds an optional VirtIO fence for the pending flush/upload. `virtio_gpu_output` stores cursor command state and `needs_modeset`. Host scanout state persists until another set_scanout or disable command. Imported buffers are pinned while in plane state.

## Dependencies and Integration Points
The file depends on DRM atomic/damage/GEM helpers, virtio-dma-buf import, DRM panic helpers, VirtIO GPU command helpers, PRIME import support, and object/fence arrays.

## Risks
`virtio_gpu_resource_flush()` ignores return from `virtio_gpu_array_lock_resv()`, which can lead to command emission without a locked reservation on failure. Imported-object attach/unpin lifetime is subtle with dma-buf dynamic attachments. Panic paths use atomic allocation/transport helpers and must remain minimal. Cursor upload waits synchronously and may stall atomic commits.

## Test Signals
KMS tests should cover damage clips, full update on FB change, dumb and blob scanout, cursor update/move/hotspot, imported dma-buf scanout and invalidation, panic screen flush, reservation-lock failure injection, and no-scaling validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_plane.c -->
