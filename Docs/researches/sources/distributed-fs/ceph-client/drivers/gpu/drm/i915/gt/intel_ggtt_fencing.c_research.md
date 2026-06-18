# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ggtt_fencing.c

## Purpose
This file manages i915 GGTT fence registers, which are hardware detiler windows for tiled objects, not DMA/execution fences. It also detects and initializes memory swizzling behavior and preserves/fixes bit-17 swizzled object pages on older platforms.

## Important APIs, Types, and Functions
Public functions include `i915_vma_pin_fence()`, `i915_vma_revoke_fence()`, `i915_reserve_fence()`, `i915_unreserve_fence()`, `intel_ggtt_restore_fences()`, `intel_ggtt_init_fences()`, `intel_ggtt_fini_fences()`, `intel_gt_init_swizzling()`, `i915_gem_object_do_bit_17_swizzle()`, and `i915_gem_object_save_bit_17_swizzle()`.

Register writers are split by generation: `i830_write_fence_reg()`, `i915_write_fence_reg()`, and `i965_write_fence_reg()`, selected by `fence_write()`. `fence_update()` binds or clears a fence register for a VMA, waits for prior active users, revokes CPU mmaps when stealing a fence, and writes hardware if runtime PM says the device is active. `fence_find()` implements the LRU/active-fence selection policy.

## Control Flow
`intel_ggtt_init_fences()` detects bit-6 swizzling, determines the platform/vGPU fence count, allocates `i915_fence_reg` entries, initializes active trackers, and writes initial hardware state. A tiled VMA requiring CPU GTT detiling calls `i915_vma_pin_fence()`, which takes the GGTT mutex, finds or reuses a fence, increments its pin count, and updates hardware. Untiled access can revoke an existing fence. Reserved fences can be removed from the normal LRU for vGPU and later returned.

Swizzling detection runs once during fence init and programs i915 swizzle state. Bit-17 save/restore records page physical-address bit 17 before unpin and swaps 64-byte chunks after repin if the bit changes.

## State and Persistence Behavior
Persistent state is in `ggtt->fence_regs`, `ggtt->fence_list`, `ggtt->num_fences`, per-fence VMA/start/size/tiling/stride/dirty/pin-count fields, and `ggtt->bit_6_swizzle_x/y`. Per-object `obj->bit_17` persists the physical swizzle record across unpin/repin. Hardware fence registers are restored after resume/reset and may be skipped on runtime suspend when clearing only.

## Dependencies and Integration Points
The code integrates with GEM VMA binding and mmap revocation, frontbuffer/display fence users, vGPU fence reservation, runtime PM, uncore MMIO, MCHBAR/register swizzle detection, object page pinning, and GGTT resume/reset flows.

## Risks
Fence registers are scarce and visible to display, CPU GTT mappings, and old GPU blits. Stealing an active or pinned fence can corrupt tiled access, so waits and mmap revocation are mandatory. Generation-specific register layouts differ substantially. Swizzle detection mistakes can make tiled buffers appear corrupted to userspace. Skipping hardware clears when the device is not truly suspended can leave overlapping fence windows.

## Test Signals
Signals include tiled GEM mmap correctness, display scanout/FBC stability with tiled buffers, vGPU fence reservation behavior, suspend/resume fence restoration, bit-17 swizzle selftests on old platforms, no frontbuffer corruption after fence stealing, and lockdep-clean use of GGTT mutex/runtime PM.
