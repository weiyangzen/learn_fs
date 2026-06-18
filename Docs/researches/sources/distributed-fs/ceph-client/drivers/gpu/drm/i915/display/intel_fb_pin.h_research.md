<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb_pin.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb_pin.h

## Purpose
This header declares framebuffer pinning and unpinning helpers for display scanout.

## Important APIs, Types, and Functions
It declares `intel_fb_pin_to_ggtt()`, `intel_fb_unpin_vma()`, `intel_plane_pin_fb()`, `intel_plane_unpin_fb()`, and `intel_fb_get_map()`. Parameters expose framebuffer, GTT view, alignment, physical alignment, VT-d guard, fence use, flags, and plane state.

## Control Flow
There is no local flow. The lifecycle implied by the API is pin framebuffer for a new plane state, program scanout using returned state, then unpin the old plane state's framebuffer when no longer used.

## State and Persistence Behavior
No state is stored here. Implementations mutate plane-state VMA pointers and flags and manage VMA references.

## Dependencies and Integration Points
The header forward declares DRM framebuffer, i915 VMA/GTT view, Intel plane state, and `iosys_map`. It is used by plane atomic commit and display memory mapping code.

## Risks
Callers must pair pin and unpin calls and pass the same flags to `intel_fb_unpin_vma()`. Incorrect alignment or guard arguments can create hardware-visible scanout faults.

## Test Signals
Compile coverage, atomic plane pin/unpin tests, framebuffer map access through `intel_fb_get_map()`, and leak detection for pin failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb_pin.h -->
