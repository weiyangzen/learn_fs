# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cursor_plane.h

## Purpose
This header declares the vmwgfx cursor plane contract shared by KMS setup, atomic plane helpers, legacy cursor snooping, and cursor-specific plane state. It exposes the cursor plane's supported DRM format and the state needed to decide which SVGA cursor update path to use.

## Important APIs, types, and definitions
- `vmw_plane_to_vcp()` converts a `struct drm_plane` embedded object to `struct vmw_cursor_plane`.
- `vmw_cursor_plane_formats[]` advertises `DRM_FORMAT_ARGB8888`, matching the alpha cursor image format used by the C file.
- `enum vmw_cursor_update_type` names the four update modes: none, legacy snooped surface, guest-backed define-cursor command, and cursor MOB.
- `struct vmw_cursor_plane_state` augments common vmwgfx plane state with update type, change flags, a cursor MOB pointer, and legacy hotspot/id tracking.
- `struct vmw_cursor_plane` embeds `struct drm_plane` and keeps a three-entry cursor MOB reuse cache.
- Public functions include snooper creation, cursor plane destroy, atomic check/update, prepare/cleanup framebuffer hooks, and the snooping callback declaration.

## Control flow and integration
The KMS plane implementation includes this header to wire DRM plane callbacks to `vmw_cursor_plane_atomic_check()`, `vmw_cursor_plane_prepare_fb()`, `vmw_cursor_plane_atomic_update()`, `vmw_cursor_plane_cleanup_fb()`, and `vmw_cursor_plane_destroy()`. Surface creation code can call `vmw_cursor_snooper_create()` when a legacy cursor-sized surface is created. Execbuf/KMS code uses the snooping callback to keep legacy cursor image memory synchronized with surface DMA uploads.

## State and persistence behavior
The header defines the persistent cursor plane state that is cloned through DRM atomic state objects. `cursor.mob` is a referenced/pinned BO while active or cached by the plane after cleanup. `legacy.id` records the last snooped surface image id submitted to the device. `legacy.hotspot_x/y` stores driver-private hotspot offsets supplied through the cursor-bypass ioctl, separate from the DRM plane state's standard hotspot fields.

## Dependencies
It depends on SVGA3D command definitions, DRM file/format/plane declarations, and Linux integer types. It forward declares vmwgfx objects to avoid pulling in the full private driver header except where implementations need it.

## Risks and edge cases
- The header declares `vmw_cursor_cmd_dma_snoop()`, while the implementation and `vmwgfx_drv.h` expose `vmw_kms_cursor_snoop()`. If no other compatibility symbol exists, this stale declaration is misleading and should be checked before future users include it.
- `changed` and `surface_changed` fields are declared in `struct vmw_cursor_plane_state` but are not used in the inspected implementation, so new code should confirm whether they are legacy leftovers or planned state.
- The MOB cache size is fixed at three; changes to display topology or concurrent cursor plane assumptions should verify that this remains sufficient.

## Test signals
Compile-time coverage should catch prototype drift for callbacks actually wired by KMS. Runtime cursor tests should confirm that ARGB8888 framebuffers are accepted, non-ARGB cursor buffers are rejected elsewhere, and copied atomic state preserves `legacy` hotspot/id and MOB ownership correctly.
