<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vgpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vgpu.h

## Purpose
Declares i915 vGPU detection, capability, registration, and GGTT ballooning APIs.

## Important APIs, types, and functions
- Forward declares `struct drm_i915_private` and `struct i915_ggtt`.
- Exports `intel_vgpu_detect()`, `intel_vgpu_active()`, `intel_vgpu_register()`, capability query helpers, `intel_vgt_balloon()`, and `intel_vgt_deballoon()`.

## Control flow
No implementation control flow exists in the header. It exposes the vGPU contract to initialization, GGTT setup, and capability users.

## State and persistence
No state is defined here; state lives in `drm_i915_private->vgpu` and implementation balloon nodes.

## Dependencies and integration points
Included by driver probe, GGTT initialization, and code paths that adapt behavior for GVT-g guests.

## Risks
Capability helpers are meaningful only after `intel_vgpu_detect()` has run. Balloon/deballoon must be paired around GGTT lifetime.

## Test signals
Build coverage, guest/bare-metal initialization tests, and GGTT balloon/deballoon integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vgpu.h -->
