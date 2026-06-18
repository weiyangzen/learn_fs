# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_colorop.c

## Purpose
`drm_colorop.c` implements DRM plane color pipeline objects. A colorop represents one color operation; colorops are chained through `NEXT` and selected by atomic userspace using the plane color pipeline capability.

## Important APIs, Types, And Functions
Base and cleanup APIs include `drm_plane_colorop_init()`, `drm_colorop_cleanup()`, `drm_colorop_destroy()`, and `drm_colorop_pipeline_destroy()`. Constructors include `drm_plane_colorop_curve_1d_init()`, `drm_plane_colorop_curve_1d_lut_init()`, `drm_plane_colorop_ctm_3x4_init()`, `drm_plane_colorop_mult_init()`, and `drm_plane_colorop_3dlut_init()`. State/name helpers include `drm_atomic_helper_colorop_duplicate_state()`, `drm_colorop_atomic_destroy_state()`, `drm_colorop_reset()`, name getters, and `drm_colorop_set_next_property()`.

## Control Flow
Each constructor creates a `DRM_MODE_OBJECT_COLOROP`, links it to `mode_config.colorop_list`, attaches common `TYPE`, optional `BYPASS`, and `NEXT` properties, then adds type-specific properties such as curve type, LUT size/interpolation/data blob, CTM data, or multiplier range. State duplication copies current state and refs `DATA`; destruction drops that blob. Reset defaults bypass to true and applies default curve type. Pipeline destroy walks the global list and calls each colorop's destroy function.

## State And Persistence
Runtime state includes the global colorop list/count, each colorop mode object, properties, plane association, type metadata, next pointer, and `drm_colorop_state` with optional blob references. It is in-memory atomic modeset state only.

## Dependencies And Integration Points
It integrates with DRM mode objects, property APIs, planes, atomic color pipeline uAPI, and driver-provided colorop function tables. It complements older plane color management by exposing explicit operation pipelines.

## Risks And Edge Cases
Constructor failure can leave partially initialized objects unless callers clean up. Cleanup assumes list membership and decrements the global count. Reset can leave NULL state on allocation failure. Pipeline destroy assumes valid `funcs->destroy`. `NEXT` is immutable for userspace but set by the core construction helper, so it should be established during initialization.

## Test Signals
Test constructors and defaults, invalid transfer-function masks, partial failure cleanup, state blob refcounts, reset defaults, `NEXT` chain setup, global list/count maintenance, and rejection of old plane color properties when color pipelines are active.
