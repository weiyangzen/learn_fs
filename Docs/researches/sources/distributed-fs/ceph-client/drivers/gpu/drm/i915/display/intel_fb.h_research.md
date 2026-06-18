<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb.h

## Purpose
This header exposes Intel framebuffer modifier, tiling, CCS, GTT-view, DPT, validation, and creation APIs used by display plane and framebuffer code.

## Important APIs, Types, and Functions
It defines plane capability bits for CCS render compression, render compression with clear color, media compression, X/Y/Yf/4 tiling, and 64K physical placement. Declarations cover modifier predicates, CCS plane mapping, modifier-list generation, format overrides, semiplanar YUV checks, surface linearity, tile sizing, plane subsampling, offset alignment, DPT use, fence use, rotation support, view size helpers, framebuffer info filling, view selection, VT-d guard computation, GTT computation, x/y offset conversion, framebuffer initialization/allocation/creation, user framebuffer creation, modifier-to-tiling conversion, and BO lookup.

## Control Flow
There is no implementation flow. The API is used during ADDFB validation, plane atomic checks, GTT pinning, scanout programming, and framebuffer destruction.

## State and Persistence Behavior
The header does not define the full framebuffer structs, but it exposes operations that mutate persistent `struct intel_framebuffer` and `struct intel_plane_state` view state. Capability bits are stable contracts between plane initialization and modifier filtering.

## Dependencies and Integration Points
It depends on Linux bits/types and forward declarations of DRM and Intel display structures. It integrates with plane initialization, DRM framebuffer creation, BO pinning, DPT, frontbuffer, and modifier advertisement.

## Risks
Mismatched declarations and implementation changes can break userspace-visible framebuffer behavior. Capability-bit changes must be coordinated with `intel_modifiers[]` in `intel_fb.c` and per-plane capabilities. Callers must pass valid framebuffer/plane state and respect that some helpers return derived offsets in-place.

## Test Signals
Compile coverage across plane and framebuffer code, modifier advertisement tests per plane, ADDFB validation tests, and scanout tests using helper-computed views.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb.h -->
