# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_release.c

Purpose: This file manages QXL release objects, which are host-completed command payloads represented as DMA fences and backed by suballocated pinned release BOs.

Important APIs, types, and functions: `qxl_alloc_release_reserved()`, `qxl_alloc_surface_release_reserved()`, `qxl_release_list_add()`, `qxl_release_reserve_list()`, `qxl_release_backoff_reserve_list()`, `qxl_release_fence_buffer_objects()`, `qxl_release_map()/unmap()`, `qxl_release_from_id_locked()`, and `qxl_release_free()`.

Control flow: Release allocation creates an IDR entry and sequence number, increments release count, suballocates a fixed-size slot from a current release BO by type, adds the BO to the release list, writes the release ID into the mapped payload, and returns it reserved for command construction. Reservation uses `drm_exec` to lock all involved BOs and validates them, including lazy QXL surface ID creation. Fencing initializes a DMA fence and attaches it to all BO reservations. Free removes the release from IDR, deallocates deferred surface IDs, frees BO refs, signals/drops the fence if initialized, or directly frees the release otherwise.

State and persistence: Persistent state includes `release_idr`, `release_seqno`, `release_count`, per-type `current_release_bo[]` and offsets, per-release BO lists, DMA fence state, and optional `surface_release_id`. Release payloads live in pinned VRAM BOs until host completion.

Dependencies and integration points: Used by command, display, draw, image, ioctl, and surface paths. Depends on DRM exec, DMA fences, TTM reservations, QXL BO mapping, command release-ring completion, and surface ID deallocation.

Risks: Release BO suballocation and destroy-surface command pairing are delicate; destroy releases can share the create release BO at offset `+64`. If a pushed command never returns, fences and release IDs can leak until cleanup. `qxl_fence_wait()` notifies OOM while waiting, coupling fence waits to host pressure behavior.

Test signals: Draw/cursor/surface release completion, chained release-ring IDs, fence wait and timeout behavior, allocation rollover across release BO pages, surface create/destroy release pairing, and forced host OOM notification.
