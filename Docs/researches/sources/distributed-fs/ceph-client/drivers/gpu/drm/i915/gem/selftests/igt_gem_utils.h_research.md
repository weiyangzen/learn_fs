# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/igt_gem_utils.h

## Purpose
Declares shared GEM selftest helpers for request allocation, GPU dword-store batch creation, and unlocked VMA active tracking.

## APIs And Control Flow
Declares `igt_request_alloc()`, `igt_emit_store_dw()`, `igt_gpu_fill_dw()`, and inline `igt_vma_move_to_active_unlocked()`. The inline helper locks a VMA, calls `i915_vma_move_to_active()`, unlocks, and returns the result.

## State, Dependencies, Integration, Risks, And Tests
The header stores no state and depends on `i915_vma.h` plus forward-declared i915/intel types. It is included by context, dma-buf, huge-page, and other GEM tests. Risk is using the unlocked wrapper where lock ordering is inappropriate. Build coverage and caller runtime failures provide test signals.
