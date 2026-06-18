# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm_pm.c

## Purpose
This file backs up and restores TTM-backed local-memory objects across suspend/resume. It either evicts evictable LMEM objects to system memory or creates system-memory backup GEM objects for pinned contents.

## Important APIs, Types, and Functions
Public APIs are `i915_ttm_backup_free`, `i915_ttm_recover_region`, `i915_ttm_backup_region`, and `i915_ttm_restore_region`. `struct i915_gem_ttm_pm_apply` extends region iteration state with `allow_gpu` and `backup_pinned` flags. Internal callbacks are `i915_ttm_backup`, `i915_ttm_recover`, and `i915_ttm_restore`.

## Control Flow
Backup is applied to every object in a memory region using `i915_gem_process_region`. If an object is not IOMEM-backed or already has a backup, it is skipped. If GPU-assisted eviction is allowed and the object is evictable, TTM validates it into system placement. If pinned backup is enabled, not PM-volatile, and not deferred to a later PM stage, a shmem-region backup object is created, optionally with CCS aux allocation, locked, populated, and filled by `i915_gem_obj_copy_ttm`; the backup object is stored on `obj->ttm.backup`.

Recover frees partial backups after suspend failure. Restore locks backup objects, validates swapped-out backups back to system placement, populates them, copies data back into the original object with or without GPU acceleration depending on stage flags, clears the backup pointer, unlocks, and drops the backup reference.

## State and Persistence Behavior
Persistence is represented by `obj->ttm.backup`, a referenced system-memory GEM object holding a copy of LMEM contents. Flags `I915_TTM_BACKUP_ALLOW_GPU` and `I915_TTM_BACKUP_PINNED` define which objects and copy engines are used in a PM phase. PM-volatile objects are intentionally not backed up.

## Dependencies and Integration Points
It integrates with GEM region iteration, TTM placement validation, TTM population/waiting, shmem memory region allocation, TTM copy/move helpers, CCS aux handling, and the staged PM flow in `i915_gem_pm.c`.

## Risks
Pinned framebuffer objects with CCS need aux backup or resume can corrupt display. Backup allocation or copy failures abort suspend and require recovery. Restore is phased: non-early backups wait until GPU use is allowed. Lock ordering depends on region iteration ww contexts.

## Test Signals
Suspend/resume data integrity for LMEM objects, pinned framebuffer preservation, CCS aux backup tests, PM-volatile skip tests, GPU-allowed vs memcpy-only phases, and fault injection for backup allocation/copy failure are relevant.
