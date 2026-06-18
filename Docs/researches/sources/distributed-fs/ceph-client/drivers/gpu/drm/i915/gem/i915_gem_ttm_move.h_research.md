# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm_move.h

## Purpose
This header declares i915 TTM migration, copy, and post-move state adjustment helpers.

## Important APIs, Types, and Functions
It declares `i915_ttm_move_notify`, selftest-only failure hooks, `i915_gem_obj_copy_ttm`, `i915_ttm_move`, `i915_ttm_adjust_domains_after_move`, and `i915_ttm_adjust_gem_after_move`. It forward-declares TTM BO, operation context, place, resource, TT, GEM object, and refcounted SG types.

## Control Flow
No executable flow exists except `I915_SELFTEST_DECLARE` conditional exposure. The declared functions are called by the TTM device callbacks, PM backup/restore, and migration/copy code.

## State and Persistence Behavior
The header itself stores no state. Its APIs mutate object bindings, page SG tables, domains, memory-region state, migration fences, and TTM resources.

## Dependencies and Integration Points
It depends on `i915_selftest.h` for conditional declarations and is included by TTM core and TTM PM implementation files.

## Risks
Callers must ensure objects are locked and TTM resources are populated where required by `i915_gem_obj_copy_ttm`; otherwise the implementation returns errors or warns.

## Test Signals
Build coverage plus TTM migration selftests and PM backup/restore copy tests validate this interface.
