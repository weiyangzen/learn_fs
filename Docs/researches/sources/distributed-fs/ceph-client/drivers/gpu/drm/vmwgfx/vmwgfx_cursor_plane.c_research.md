# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cursor_plane.c

## Purpose
This file implements the vmwgfx DRM cursor plane. It bridges DRM atomic cursor state to VMware SVGA cursor mechanisms: legacy alpha-cursor FIFO commands backed by snooped legacy surfaces, guest-backed cursor updates from buffer objects, and the newer cursor MOB register path when `SVGA_CAP2_CURSOR_MOB` is available. It also owns cursor image snooping for old non-atomic userspace and the `DRM_VMW_CURSOR_BYPASS` ioctl hotspot override.

## Important APIs, types, and functions
- `vmw_send_define_cursor_cmd()` reserves FIFO command space and emits `SVGA_CMD_DEFINE_ALPHA_CURSOR` with an image payload. Reservation failure is deliberately swallowed because the FIFO reservation cannot be held while KMS atomic resource preparation waits.
- `vmw_cursor_update_type()` selects `VMW_CURSOR_UPDATE_LEGACY`, `VMW_CURSOR_UPDATE_MOB`, `VMW_CURSOR_UPDATE_GB_ONLY`, or `VMW_CURSOR_UPDATE_NONE` from the current user object, snooper state, `has_mob`, and `SVGA_CAP2_CURSOR_MOB`.
- `vmw_cursor_update_mob()` writes a `SVGAGBCursorHeader` plus ARGB image into a pinned cursor MOB, then writes `SVGA_REG_CURSOR_MOBID`.
- `vmw_cursor_mob_get()`, `vmw_cursor_mob_put()`, `vmw_cursor_mob_map()`, and `vmw_cursor_mob_unmap()` allocate, cache, pin, map, unmap, and destroy cursor MOB buffer objects. The plane keeps a small three-entry cache.
- `vmw_cursor_update_position()` programs cursor visibility and position through extra registers, FIFO cursor-bypass registers, or legacy cursor registers while holding `dev_priv->cursor_lock`.
- `vmw_kms_cursor_snoop()` copies a constrained surface DMA upload into `vmw_surface.snooper.image` and increments the snooper image id so legacy cursor updates can detect changes.
- `vmw_cursor_plane_prepare_fb()`, `vmw_cursor_plane_cleanup_fb()`, `vmw_cursor_plane_atomic_check()`, and `vmw_cursor_plane_atomic_update()` are the DRM plane helper lifecycle hooks.
- `vmw_kms_cursor_bypass_ioctl()` updates legacy hotspot offsets on one CRTC or all CRTCs under `mode_config.mutex`.
- `vmw_cursor_snooper_create()` allocates a 64x64 ARGB snooper buffer for legacy, non-atomic, scanout cursor surfaces.

## Control flow
The atomic cursor path starts in `vmw_cursor_plane_atomic_check()`, which delegates generic plane validation to `drm_atomic_helper_check_plane_state()`. Disabling the cursor exits early. Legacy snooped cursors are restricted to exactly 64x64 ARGB surfaces with a valid snooper image. `vmw_cursor_plane_prepare_fb()` then replaces the plane state's `vmw_user_object`, references the framebuffer backing surface or BO, selects an update type, validates and pins BOs for guest-backed paths, maps the image, detects unchanged buffers, and prepares/maps a cursor MOB when a real update is needed. On commit, `vmw_cursor_plane_atomic_update()` hides the cursor for null user objects, otherwise emits the selected image update, then computes global cursor coordinates from CRTC position plus display-unit GUI offsets and hotspot offsets before programming hardware position.

The legacy snoop path is separate. `vmw_cursor_snooper_create()` installs a snooper only for old non-atomic userspace creating a 64x64 ARGB scanout surface. Later execbuf validation calls `vmw_kms_cursor_snoop()` for surface DMA commands. The snooper accepts only face 0, mip 0, a single copy box starting at zero, page-aligned guest offsets, depth 1, and dimensions within 64x64. It maps the source BO, copies either a contiguous full cursor or per-row partial cursor data, increments `snooper.id`, and unmaps/unreserves the BO. `vmw_cursor_plane_update_legacy()` only sends a new define-cursor command when that id changes.

## State and persistence behavior
Persistent device state is minimal but timing-sensitive. Cursor visibility and coordinates live in SVGA registers or FIFO cursor fields. Legacy cursor image state is tracked in `vmw_surface.snooper.image` and `snooper.id`. Plane state tracks the current `vmw_user_object`, `cursor.update_type`, legacy hotspot/id, and a transient cursor MOB pointer. The plane object caches up to three MOBs across commits to reduce allocation churn; excess or undersized MOBs are unpinned and unreferenced. BO mapping state is cached through `vmw_bo_map_and_cache*()` and must be explicitly unmapped in cleanup.

## Dependencies and integration points
The file depends on DRM atomic helpers, `struct drm_plane`, vmwgfx KMS plane state, `vmw_user_object` conversion helpers, TTM BO reservation/pinning/mapping, vmwgfx FIFO command helpers, SVGA register definitions, dirty tracking, and `vmw_surface` metadata. It is called from KMS plane setup/teardown and from execbuf DMA validation for cursor snooping. It consumes capability bits initialized by `vmwgfx_drv.c` and shared state/types declared in `vmwgfx_cursor_plane.h` and `vmwgfx_drv.h`.

## Risks and edge cases
- Several resource preparation failures are collapsed to `-ENOMEM` or ignored. In particular `vmw_cursor_mob_get()` and `vmw_cursor_mob_map()` return values are not propagated from `prepare_fb()`, so MOB update failure can degrade into later no-op or stale cursor behavior.
- `vmw_cursor_update_mob()` assumes successful BO mappings and copies `crtc_w * crtc_h * 4` bytes; the preceding prepare/check paths must enforce size and mapping validity.
- The snooper supports only a narrow DMA shape and logs errors for partial offsets, multiple boxes, non-zero source/destination offsets, or larger dimensions. Legacy users outside that pattern will not update cursor images.
- `vmw_cursor_buffer_changed()` contains a currently unreachable memcmp branch because the function returns immediately when BO pointers differ. Dirty tracking is the active same-BO change detector.
- Cursor register programming is protected by `cursor_lock`, but image/MOB state is managed through atomic plane lifetime and BO reservations; regressions in cleanup ordering can leak pinned BOs or leave mappings behind.

## Test signals
Useful validation includes atomic cursor enable/disable, movement, hotspot changes, same-image commits, dirty BO updates, CRTC offset changes, legacy non-atomic 64x64 cursor surface updates through DMA, fallback behavior without `SVGA_CAP2_CURSOR_MOB`, and suspend/unload cleanup with no pinned cursor MOB leaks. Runtime signals include `drm_warn` for invalid legacy dimensions, `DRM_ERROR` from snooper rejection paths, absence of TTM reservation failures, and correct cursor visibility across multi-monitor display-unit offsets.
