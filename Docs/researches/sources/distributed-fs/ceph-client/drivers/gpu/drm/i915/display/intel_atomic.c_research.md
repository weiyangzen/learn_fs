# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_atomic.c

## Purpose

`intel_atomic.c` implements shared i915 display atomic state helpers for digital connector properties, connector atomic checks, connector and CRTC state duplication/destruction, CRTC color blob lifetime, Intel atomic-state allocation/free/clear, and typed accessors for Intel connector and CRTC state.

## Important APIs, Types, And Functions

Connector property hooks are `intel_digital_connector_atomic_get_property()` and `intel_digital_connector_atomic_set_property()` for force-audio and broadcast-RGB properties. `intel_digital_connector_atomic_check()` runs HDCP atomic checks and requests a modeset when fastset-handled connector properties change. State helpers include `intel_digital_connector_duplicate_state()`, `intel_connector_needs_modeset()`, `intel_any_crtc_needs_modeset()`, `intel_atomic_get_digital_connector_state()`, `intel_crtc_duplicate_state()`, `intel_crtc_destroy_state()`, `intel_crtc_free_hw_state()`, `intel_atomic_state_alloc()`, `intel_atomic_state_free()`, `intel_atomic_state_clear()`, and `intel_atomic_get_crtc_state()`.

## Control Flow

DRM atomic property get/set callbacks translate generic connector state into `struct intel_digital_connector_state` and handle only known display properties. Connector atomic check compares old and new connector state for audio, RGB range, colorspace, aspect ratio, content type, scaling mode, privacy-screen software state, and HDR metadata changes; if any differ, it marks the associated CRTC state `mode_changed`. CRTC duplication kmemdups the old Intel CRTC state, invokes DRM helper duplication, increments references on color blobs and DP tunnel references, then clears transient flags and commit-only pointers so the new state starts clean. Destruction releases DRM helper state, color blobs, DP tunnel refs, and memory.

Intel atomic state allocation wraps `drm_atomic_state_init()` around `struct intel_atomic_state`. Clear releases default DRM state, clears Intel global state, intentionally preserves `state->internal`, resets top-level booleans, and cleans inherited DP tunnel atomic state. Typed getters wrap DRM atomic getters and cast to Intel state types.

## State And Persistence Behavior

The file manages lifetime and copying of persistent state snapshots rather than hardware registers. It preserves refcounted blobs (`degamma_lut`, `gamma_lut`, `ctm`, pre/post CSC LUTs) and DP tunnel references across duplicated states. It explicitly resets transient fields such as watermark update flags, FIFO change flags, async flip flags, DSB pointers, LUT preload flags, plane update bitmasks, and DSB usage so stale commit actions do not leak into later atomic checks.

## Dependencies And Integration Points

Dependencies include DRM atomic core/helpers, HDR metadata comparison, DP tunnel references, Intel display properties, HDCP, PSR, global state, CDCLK-related state via included headers, and universal plane state. These helpers are used by connector function tables, CRTC function tables, atomic check/commit code, and internal sanitize transactions.

## Risks And Edge Cases

Forgetting to refcount a new blob or pointer field in `intel_crtc_duplicate_state()` can cause use-after-free; forgetting to clear a transient field can cause spurious hardware programming. Connector atomic check marks mode changes for properties handled by fastset, which is conservative but can increase modesets. `intel_atomic_state_clear()` intentionally preserves `internal`, so callers must set it deliberately and not expect a full reset. Unknown property access returns `-EINVAL` after debug logging.

## Test Signals

Relevant tests include atomic property get/set for force audio and broadcast RGB, HDR metadata changes, connector scaling/colorspace/content-type changes, HDCP state checks, CRTC state duplication/destruction leak tests, DP tunnel reference lifetime, repeated atomic clear/reuse, async flip state reset, DSB pointer WARN coverage, and KASAN/KMEMLEAK under IGT atomic modeset stress.
