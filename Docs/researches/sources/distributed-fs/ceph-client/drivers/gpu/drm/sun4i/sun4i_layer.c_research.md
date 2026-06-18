<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_layer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_layer.c

## Purpose

`sun4i_layer.c` implements DRM plane objects for the older DE1 backend pipeline. It owns plane state allocation, format/modifier advertisement, atomic update/disable behavior, and the initialization of primary/overlay layers backed by `sun4i_backend` and optionally `sun4i_frontend`.

## Important APIs, Types, And Functions

The public API is `sun4i_layers_init()`. Important helpers are `sun4i_backend_layer_reset()`, duplicate/destroy state callbacks, `sun4i_backend_layer_atomic_update()`, `sun4i_backend_layer_atomic_disable()`, `sun4i_layer_format_mod_supported()`, and `sun4i_layer_init_one()`. Supported format lists differ depending on whether a frontend is available, and modifiers include linear plus Allwinner tiled when the frontend can be used.

## Control Flow

`sun4i_layers_init()` allocates a sentinel-terminated plane array and creates `SUN4I_BACKEND_NUM_LAYERS` planes, with layer 0 primary and the rest overlays. Atomic update clears previous backend layer programming, then either routes through the frontend for formats requiring conversion/scaling to XRGB8888 or programs backend format/buffer directly. It always updates coordinates, zpos, and layer enable. Atomic disable disables the backend layer and, if old state used the frontend, marks `backend->frontend_teardown` under `frontend_lock`.

## State And Persistence Behavior

Per-plane persistent state is `struct sun4i_layer`; per-atomic state is `struct sun4i_layer_state`, especially `uses_frontend`. Hardware state persists through backend/frontend register programming until the next atomic update or disable. The frontend teardown flag coordinates deferred cleanup with vblank-side backend behavior.

## Dependencies And Integration Points

It depends on DRM plane/atomic/blend helpers, `sun4i_backend`, `sun4i_frontend`, and `sunxi_engine` layer initialization. The CRTC obtains these planes through the engine ops during display pipeline setup.

## Risks And Test Signals

Risks include mismatched `uses_frontend` transitions, frontend teardown races, format/modifier advertisement inconsistent with backend/frontend support, zpos bounds tied to hardware layer count, and cleanup when partial plane init fails. Test with atomic plane enable/disable, frontend-required tiled/YUV formats, overlay z-order changes, alpha/zpos properties, and repeated format switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_layer.c -->
