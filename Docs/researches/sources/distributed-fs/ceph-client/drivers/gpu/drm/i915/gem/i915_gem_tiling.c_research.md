# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_tiling.c

## Purpose
This file implements legacy GEM tiling and swizzle ABI support for X/Y tiled objects and fence-register requirements. Modern tiling layouts are intentionally left to userspace, but old fence and bit17 swizzle behavior still requires kernel tracking.

## Important APIs, Types, and Functions
Public helpers are `i915_gem_fence_size`, `i915_gem_fence_alignment`, `i915_gem_object_needs_bit17_swizzle`, `i915_gem_object_set_tiling`, `i915_gem_set_tiling_ioctl`, and `i915_gem_get_tiling_ioctl`. Internal helpers validate tiling/stride and unbind GGTT VMAs whose current placement cannot satisfy new fence constraints.

## Control Flow
Fence size/alignment depends on graphics generation: gen4+ aligns to fence pages and rounds by tile height, while older generations require power-of-two fence regions. `i915_gem_object_set_tiling` rejects framebuffers, locks the object, unbinds incompatible GGTT VMAs, handles swizzled-page pinning quirks by moving objects between shrinkable and unshrinkable states, updates VMA fence size/alignment and dirty fence flags, writes `tiling_and_stride`, allocates or frees bit17 metadata, unlocks, and releases GTT mmap state.

The set ioctl validates handle/proxy/tiling constraints, reports swizzle ABI values with bit17 hidden, falls back to untiled on unknown swizzle, applies the tiling change, then returns the actual stored tiling/stride. The get ioctl uses an RCU handle lookup to read tiling and returns logical and physical swizzle modes.

## State and Persistence Behavior
Persistent object state includes `tiling_and_stride`, per-VMA fence constraints, dirty fence flags, `bit_17` swizzle bitmap, tiling-quirk flags, shrink-list membership, and released GTT mmap offsets.

## Dependencies and Integration Points
It integrates with GGTT VMA lists, fence registers, GEM mmap, shrinker pinning, display framebuffer checks, platform swizzle fields in GGTT, and UAPI structs in `i915_drm.h`.

## Risks
Tiling changes can corrupt active scanout, so framebuffer objects are rejected twice. Swizzle ABI compatibility hides bit17 from old userspace. Unknown swizzling disables tiling. VMA unbind error recovery must restore list membership. Pinning swizzled pages reduces reclaimability.

## Test Signals
Set/get tiling ioctl tests, stride validation across generations, fence alignment tests, swizzle reporting compatibility, framebuffer rejection, VMA unbind/rebind behavior, and gen3/gen4 bit17 swizzle tests are key signals.
