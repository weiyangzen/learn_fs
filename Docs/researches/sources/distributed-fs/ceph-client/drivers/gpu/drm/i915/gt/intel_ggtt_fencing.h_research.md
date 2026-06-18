# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ggtt_fencing.h

## Purpose
This header defines the software representation and public operations for GGTT fence registers and legacy swizzling support.

## Important APIs, Types, and Functions
`struct i915_fence_reg` records the list node, owning GGTT, current VMA, pin count, active tracker, register ID, dirty bit, start, size, tiling mode, and stride. The header exports fence reservation, unreservation, restoration, init/fini, VMA fence pin/revoke functionality through companion declarations, plus bit-17 swizzle save/restore helpers and `intel_gt_init_swizzling()`.

## Control Flow
The header contains declarations only. GGTT initialization calls `intel_ggtt_init_fences()`, tiled CPU/GTT access calls VMA pin/revoke helpers, resume/reset calls `intel_ggtt_restore_fences()`, and object backing-store migration paths call bit-17 swizzle helpers.

## State and Persistence Behavior
State is stored in `struct i915_fence_reg` instances allocated by `intel_ggtt_init_fences()` and in GEM object bitmaps for bit-17 tracking. The constant `I965_FENCE_PAGE` documents the page granularity used by newer fence registers.

## Dependencies and Integration Points
It depends on `i915_active` for active tracking and forward-declares GEM object, VMA, GGTT, GT, and scatterlist types. Consumers include GEM mmap/fence code, GGTT init/resume, display/frontbuffer users, and vGPU.

## Risks
Consumers must understand that these are detiling registers, not execution fences. Misusing `pin_count` or bypassing active tracking can cause tiled memory corruption. Any struct field semantic change must match `intel_ggtt_fencing.c`.

## Test Signals
Build coverage, tiled mmap/display correctness, fence init/fini leak checks, and vGPU fence reservation tests validate this interface.
