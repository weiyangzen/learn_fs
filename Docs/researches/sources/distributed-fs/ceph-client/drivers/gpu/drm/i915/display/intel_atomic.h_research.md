# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_atomic.h

## Purpose

`intel_atomic.h` declares shared i915 atomic display helper APIs for connector property handling, connector/CRTC state access, modeset detection, and Intel atomic-state lifetime management. It is the common header included by encoder, connector, CRTC, watermark, and modeset code needing typed Intel wrappers around DRM atomic state.

## Important APIs, Types, And Functions

The header forward declares DRM and Intel atomic, connector, CRTC, and property types. It declares digital connector hooks `intel_digital_connector_atomic_get_property()`, `intel_digital_connector_atomic_set_property()`, `intel_digital_connector_atomic_check()`, and `intel_digital_connector_duplicate_state()`. It declares modeset/state accessors `intel_connector_needs_modeset()`, `intel_any_crtc_needs_modeset()`, `intel_atomic_get_digital_connector_state()`, and `intel_atomic_get_crtc_state()`. It declares CRTC and atomic state lifetime helpers `intel_crtc_duplicate_state()`, `intel_crtc_destroy_state()`, `intel_crtc_free_hw_state()`, `intel_atomic_state_alloc()`, `intel_atomic_state_free()`, and `intel_atomic_state_clear()`.

## Control Flow

The header has no runtime control flow. DRM object function tables and Intel display code call the declared helpers during atomic property operations, state duplication/destruction, atomic check, internal sanitize transactions, and state cleanup.

## State And Persistence Behavior

No state is stored in the header. The implementation manages connector state fields, CRTC state snapshots, color blob references, DP tunnel references, and Intel atomic state global-object arrays. The declarations define the ownership boundary for those operations.

## Dependencies And Integration Points

The header depends on `<linux/types.h>` and forward declarations, keeping dependencies low for many display files. It integrates with DRM atomic core while exposing Intel-specific typed state (`struct intel_atomic_state`, `struct intel_crtc_state`, and `struct intel_digital_connector_state`).

## Risks And Edge Cases

The header returns raw DRM state pointers for duplicate/allocation functions and Intel typed pointers for accessors, so call sites must use the right conversion and error handling. Any new Intel state field requiring reference management must be handled in the C implementation without changing this API. Broad inclusion means signature changes have a large compile-time blast radius.

## Test Signals

Build coverage across display objects, connector property tests, atomic state allocation/clear/free tests, CRTC duplicate/destroy lifetime checks, and static analysis for `ERR_PTR` handling on typed getters are useful validation signals.
