# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm_pm.h

## Purpose
This header declares the TTM local-memory backup, recovery, restore, and object-backup cleanup APIs used by GEM PM code.

## Important APIs, Types, and Functions
It defines `I915_TTM_BACKUP_ALLOW_GPU` and `I915_TTM_BACKUP_PINNED`, and declares `i915_ttm_backup_region`, `i915_ttm_recover_region`, `i915_ttm_restore_region`, and internal `i915_ttm_backup_free`.

## Control Flow
There is no executable flow. The flags control whether backup/restore may use GPU blits and whether pinned objects should receive explicit backup objects.

## State and Persistence Behavior
The header stores no state. The declared implementation manages `obj->ttm.backup` references and TTM region placement across PM phases.

## Dependencies and Integration Points
It forward-declares memory-region and GEM object types and is included by GEM PM, TTM object destruction, and TTM PM implementation code.

## Risks
Using the wrong flag combination in a PM phase can either attempt GPU access too early/late or skip pinned objects that cannot be evicted. Cleanup must be called during object destruction to avoid leaking backup objects.

## Test Signals
Compile coverage, LMEM suspend/resume tests, backup cleanup on object destruction, and recovery after failed suspend validate the contract.
