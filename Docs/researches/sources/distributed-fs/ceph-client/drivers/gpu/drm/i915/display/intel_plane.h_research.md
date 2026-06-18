# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_plane.h

## Purpose
`intel_plane.h` declares the common Intel display plane API exported by `intel_plane.c` to the rest of the i915 display stack. It keeps consumers insulated from the implementation details of Intel plane state lifetime, atomic checking, update dispatch, framebuffer helper installation, and format/async capability filtering.

## Important APIs And Types
The header forward-declares DRM and Intel display types instead of including large internal headers. This makes it a low-dependency interface for `struct intel_plane`, `struct intel_plane_state`, `struct intel_crtc_state`, `struct intel_atomic_state`, `struct intel_dsb`, and related DRM objects.

The declarations group into lifecycle (`intel_plane_alloc`, `intel_plane_free`, `intel_plane_destroy`, `intel_plane_duplicate_state`, `intel_plane_destroy_state`), state copying (`intel_plane_copy_uapi_to_hw_state`, `intel_plane_copy_hw_state`), rate/accounting (`intel_adjusted_rate`, `intel_plane_pixel_rate`, `intel_plane_data_rate`), commit dispatch (`intel_plane_update_noarm`, `intel_plane_update_arm`, `intel_plane_disable_arm`, `intel_plane_async_flip`, CRTC arm/noarm helpers), validation (`intel_plane_atomic_check`, `intel_plane_atomic_check_with_state`, clipping and source coordinate checks), and utilities (`intel_crtc_get_plane`, `intel_plane_set_invisible`, `intel_plane_needs_physical`, `intel_plane_helper_add`, `intel_plane_add_affected`, async format/modifier support).

## Control Flow And Integration
Generation-specific plane files call these declarations to participate in common atomic validation and commit sequencing. Atomic modeset code calls `intel_plane_atomic_check()` and the CRTC plane update helpers; plane initialization code calls allocation/helper-install functions; platform plane check hooks call clipping/source coordinate/rate helpers.

Because only prototypes are present, the header does not own state mutations itself. Its role is contract definition: callers must pass Intel atomic/CRTC/plane state objects that are already in the DRM atomic transaction and must respect lock and refcount assumptions enforced in `intel_plane.c`.

## State, Dependencies, Risks, And Test Signals
The header has no persistent data and no direct MMIO behavior. Its main dependency is ABI consistency between declarations and `intel_plane.c`. Misdeclared argument types would usually fail at build time, but semantic mismatches are still possible: for example, callers must understand that `intel_plane_copy_uapi_to_hw_state()` grabs framebuffer references and that `intel_plane_set_invisible()` mutates CRTC aggregate masks.

Test signals are mostly compile/link coverage plus exercising external users of the API: plane init, atomic check, update arm/noarm, async flip, and cleanup paths.
