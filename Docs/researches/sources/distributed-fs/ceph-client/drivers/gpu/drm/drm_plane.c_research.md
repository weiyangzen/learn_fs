# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_plane.c

## Purpose

`drm_plane.c` is the DRM core implementation for KMS plane objects. It registers universal planes, exposes plane resources and state through legacy ioctls, handles legacy setplane/cursor/page-flip operations, validates format/modifier support, and attaches standard plane properties such as `IN_FORMATS`, damage clips, scaling filters, size hints, hotspots, and color pipelines.

## Important APIs, Types, and Functions

- `__drm_universal_plane_init()`, `drm_universal_plane_init()`, `__drmm_universal_plane_alloc()`, and `__drm_universal_plane_alloc()` create and register plane objects.
- `create_in_format_blob()` builds the `drm_format_modifier_blob` for `IN_FORMATS` and `IN_FORMATS_ASYNC`.
- `drm_plane_cleanup()`, `drm_plane_register_all()`, and `drm_plane_unregister_all()` manage plane lifecycle and driver callbacks.
- `drm_mode_getplane_res()` and `drm_mode_getplane()` implement legacy resource query ioctls with lease and capability filtering.
- `drm_plane_has_format()` and `drm_any_plane_has_format()` validate format/modifier support.
- `drm_mode_setplane()`, `setplane_internal()`, `__setplane_internal()`, and `__setplane_atomic()` implement legacy plane updates for non-atomic and atomic drivers.
- `drm_mode_cursor_ioctl()` and `drm_mode_cursor2_ioctl()` implement legacy cursor updates, using universal cursor planes when available.
- `drm_mode_page_flip_ioctl()` implements legacy page flip and page flip target behavior.
- Property helpers include `drm_plane_enable_fb_damage_clips()`, damage clip accessors, `drm_plane_create_scaling_filter_property()`, `drm_plane_add_size_hints_property()`, and `drm_plane_create_color_pipeline_property()`.

## Control Flow

Plane initialization validates total plane and format-count limits, checks atomic state callback requirements, registers a mode object, initializes the modeset lock, allocates and copies format/modifier arrays, creates a name, links the plane into `mode_config.plane_list`, assigns an index, attaches immutable type and atomic properties, optionally creates cursor hotspot properties, and attaches format/modifier blobs. Managed allocation variants add DRM-managed cleanup actions; unmanaged allocation leaves freeing to the driver destroy hook.

Legacy `SETPLANE` lookup resolves plane, framebuffer, and CRTC IDs, then takes all modeset locks. Non-atomic updates call driver `update_plane` or `disable_plane` and update `plane->crtc`, `plane->fb`, and framebuffer references. Atomic drivers still route through plane funcs but use atomic-aware hooks. Common validation checks CRTC compatibility, framebuffer format/modifier support, coordinate overflow, and source bounds.

Cursor ioctls lock the CRTC and cursor plane. If a universal cursor plane exists, buffer-object updates wrap the GEM handle in an internal ARGB8888 framebuffer, optionally update hotspot state, and call the setplane path. Without a universal plane, the code calls legacy CRTC cursor callbacks. Page flips validate flags, target vblank semantics, async support, lease access, old framebuffer presence, new framebuffer source compatibility, and format stability. Optional events are reserved before invoking driver page-flip callbacks and canceled on failure.

## State and Persistence

Each plane stores its mode object, lock, name, index, possible CRTCs, type, format arrays, modifier arrays, property pointers, current state or legacy `fb/crtc`, and old framebuffer during transitions. Properties are persistent DRM objects attached to the plane. Blob properties store immutable format/modifier tables, damage clip arrays, and size hints.

## Dependencies and Integration Points

The file depends on DRM mode object/property infrastructure, framebuffer lifetime, CRTC/plane locks, leases, atomic and legacy modeset callbacks, vblank/event handling, userspace copy helpers, and driver-provided `drm_plane_funcs`. It is central to both old KMS ioctls and modern atomic property exposure.

## Risks and Edge Cases

- Plane indices are limited to 32-bit masks and format blobs currently encode formats in a 64-bit bitset.
- Mixing planes with and without zpos is warned as invalid.
- Legacy and atomic paths share some callbacks; comments note redundant validation for async/cursor tricks until all drivers call atomic checks.
- Cursor hotspot exposure is filtered for virtualized drivers unless userspace declares support.
- Page flip target handling must balance vblank references on all failure paths.
- `drm_plane_cleanup()` assumes plane list membership and zeros the structure, so callers must not use it afterward.
- Damage clips are hints; drivers must still tolerate full updates or inaccurate userspace damage.

## Test Signals

Tests should cover plane initialization failure unwinding, modifier blob contents, capability-filtered plane enumeration, lease filtering, format/modifier validation, setplane enable/disable reference counts, cursor BO and move paths with hotspots, page flip target absolute/relative validation, event reservation/cancel paths, damage clip accessors, scaling filter property validation, cursor-only size hints, and color pipeline enum creation.
