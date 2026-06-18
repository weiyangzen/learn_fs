# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_panic.c

## Purpose
Adapts i915 GEM framebuffer objects to the DRM panic display infrastructure.

## Important APIs, types, and functions
Exports `i915_display_panic_interface`. Private callbacks are `intel_panic_alloc()`, `intel_panic_setup()`, and `intel_panic_finish()`.

## Control flow
Allocation delegates to `i915_gem_object_alloc_panic()`. Setup retrieves the `intel_framebuffer` from the scanout buffer private pointer, gets its GEM object, and calls `i915_gem_object_panic_setup()` with the framebuffer's panic tiling. Finish delegates to `i915_gem_object_panic_finish()`.

## State and persistence
No local persistent state. Panic mapping/setup state is owned by GEM panic helpers and the `intel_panic` object.

## Dependencies and integration points
Depends on DRM panic, display parent interface, intel framebuffer helpers, and i915 GEM object panic operations.

## Risks
Panic paths run in constrained contexts, so callbacks must stay minimal and avoid normal sleeping/display state assumptions. The scanout buffer private pointer must really be an `intel_framebuffer`.

## Test signals
DRM panic screen tests on i915 scanout buffers, tiled and linear framebuffer panic setup, and build coverage with panic infrastructure enabled.
