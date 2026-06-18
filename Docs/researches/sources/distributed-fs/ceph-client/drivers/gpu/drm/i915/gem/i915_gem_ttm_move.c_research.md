# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm_move.c

## Purpose
This file implements i915's TTM buffer-object move and copy operations. It prepares objects for migration, chooses GPU blit or CPU memcpy fallback, handles failure interception, updates GEM cache/domain state after moves, and exposes selftest failure controls.

## Important APIs, Types, and Functions
Public/internal APIs are `i915_ttm_move_notify`, `i915_ttm_adjust_domains_after_move`, `i915_ttm_adjust_gem_after_move`, `i915_ttm_move`, and `i915_gem_obj_copy_ttm`. Selftest hooks are `i915_ttm_migrate_set_failure_modes` and `i915_ttm_migrate_set_ban_memcpy`. Important internal types are `struct i915_ttm_memcpy_arg` and `struct i915_ttm_memcpy_work`.

## Control Flow
Move notification unbinds active GPU mappings asynchronously and drops GEM pages before TTM changes resources. Accelerated moves use the GT migrate context to clear or copy between SG tables with PAT/cache attributes and LMEM binding classification. If GPU migration is scheduled, the code may arm a custom DMA fence callback that signals success cheaply or queues work to perform memcpy on GPU error. If no GPU path is available or interception fails, synchronous memcpy is used when both source and destination are CPU mappable; otherwise the object enters unknown state and GTs are wedged.

`i915_ttm_move` handles NULL resources with multihop through system memory, purges DONTNEED objects instead of moving them, populates TT pages when required, gathers destination SG tables, attaches migration fences to TTM cleanup, caches IO SG tables for IOMEM destinations, adjusts domains/cache/region, and updates LRUs. `i915_gem_obj_copy_ttm` copies between two locked TTM GEM objects and adds the resulting fence to both reservation objects.

## State and Persistence Behavior
Move state affects TTM resources, `obj->mm.region`, `mem_flags`, cache coherency, read/write domains, `obj->ttm.cached_io_rsgt`, page iterators, migration fences, `unknown_state`, and reservation fences. Async memcpy work owns object and SG references until its fence signals.

## Dependencies and Integration Points
It depends on TTM move cleanup, i915 deps/reservation collection, GT migrate blitter, engine PM, refcounted SG tables, TTM kmap iterators, runtime platform cache rules, GEM unbind/page helpers, and selftest infrastructure.

## Risks
Fallback logic is complex: failing GPU migration to non-mappable memory without memcpy support wedges GTs and marks the object unknown. Reservation fence ordering must protect source and destination. Cached IO SG tables must be refreshed after moves. CCS-aux objects cannot use memcpy. Multihop and purged-object paths must preserve TTM invariants.

## Test Signals
Selftests that force GPU failure, work allocation failure, and memcpy ban are critical. Additional signals include LMEM-to-system and system-to-LMEM migration, eviction moves, copy fences on reservations, CCS object migration, small-BAR non-mappable failures, and data integrity after suspend/move stress.
