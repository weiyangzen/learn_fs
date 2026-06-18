# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_mman.c

## Purpose
Validates GEM mmap behavior across GGTT, WC/WB/UC, and fixed mmap offsets. It covers partial tiled GGTT views, mmap offset exhaustion, LMEM mmap fault migration, userspace access helpers, GPU execution from mmap-written batches, and PTE revocation.

## APIs And Control Flow
Core helpers include `tiled_offset()`, `check_partial_mapping(s)()`, `igt_partial_tiling()`, `igt_smoke_tiling()`, `igt_mmap_offset_exhaustion()`, `__igt_mmap()`, `igt_mmap_migrate()`, `__igt_mmap_access()`, `__igt_mmap_gpu()`, and `__igt_mmap_revoke()`. Tests map partial views, manually compute swizzled tiled offsets, trim the VMA offset manager to force exhaustion, map objects into `current->mm`, fault non-visible LMEM through fixed mmap, and verify present/absent PTEs before and after unbind or page release.

## State, Dependencies, Integration, Risks, And Tests
State includes GEM objects, memory-region visible ranges, VMA offset nodes, process VMAs/PTEs, GGTT fences, TTM buddy visible-size state, and active requests. Dependencies include `igt_mmap`, memory-region/TTM migration APIs, GGTT iomap, page-table walkers, and reset helpers. Risks are global offset-manager/visible-size mutation, platform-specific swizzle math, fault migration failure injection, and kthread `current->mm` handling. Signals include partial-view misalignment, wrong poison values, unexpected allocation success, bad migration/fault results, PTE check failures, and GPU batch timeouts.
