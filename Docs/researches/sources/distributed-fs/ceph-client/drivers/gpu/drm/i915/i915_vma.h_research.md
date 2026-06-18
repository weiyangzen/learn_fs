# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vma.h

Purpose: declares the public/internal VMA API used by GEM, execbuf, GGTT display paths, eviction, and VM teardown code.

Important APIs/functions: exposes VMA lookup/creation, pin/unpin, bind/unbind, async unbind, active tracking, mmap revoke, TLB invalidation, GGTT iomap, fence pinning, scanout markers, shrinkability helpers, current-resource access, module init/exit, and selftest-only page helpers. Inline helpers provide flag tests (`i915_vma_is_ggtt`, `i915_vma_is_bound`, `i915_vma_is_pinned`), effective offset/size with guard subtraction, object-backed refcount wrappers, view comparison, pin count updates, GGTT offset narrowing, and iteration over object GGTT VMAs.

Control flow: callers include this header to move from high-level object operations into VMA lifecycle operations. The inline pin/unpin and flag helpers are intentionally tiny and assume callers satisfy locking documented by exported functions and `assert_vma_held`.

State and persistence: no storage beyond inline access to `struct i915_vma`; it defines flag interpretation and lock expectations. Effective state remains in the VMA object and object reservation lock.

Dependencies and integration: includes GEM object, GTT, active, request, GGTT fencing, and resource headers. It links VMA code to display through `intel_display_vma_interface`, to execbuf through `_i915_vma_move_to_active`, and to eviction through unbind APIs.

Risks: many helpers assume allocated `drm_mm_node`, GGTT-only state, or nonzero pin counts and use `GEM_BUG_ON` rather than recoverable errors. Misusing raw `__i915_vma_pin/unpin` or `i915_vma_get_current_resource()` without a bound VMA can break lifetime rules.

Test signals: compile-time coverage comes from many i915 translation units, selftest declarations, lockdep through `assert_vma_held`, and runtime GEM assertions when helpers are called in invalid states.
