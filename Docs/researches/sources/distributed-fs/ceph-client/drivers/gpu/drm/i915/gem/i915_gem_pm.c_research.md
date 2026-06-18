# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_pm.c

## Purpose
This file coordinates GEM object state across suspend, hibernation freeze, and resume. Its main responsibility is preserving local-memory contents using TTM backup/restore and making CPU/GPU cache-domain state safe for platform power transitions.

## Important APIs, Types, and Functions
Public lifecycle hooks are `i915_gem_suspend`, `i915_gem_backup_suspend`, `i915_gem_suspend_late`, `i915_gem_freeze`, `i915_gem_freeze_late`, and `i915_gem_resume`. Local helpers `lmem_suspend`, `lmem_restore`, and `lmem_recover` iterate local memory regions and call the TTM PM APIs.

## Control Flow
Suspend first disables the userfault auto wakeref, waits for pending RCU callbacks, flushes driver workqueues, asks each GT to prepare suspend, and drains freed GEM objects. Backup suspend then performs staged LMEM handling: evict unpinned objects with GPU allowed, suspend GTs, evict/backup newly unpinned and pinned non-early objects, and finally memcpy-backup remaining pinned objects after migrate contexts are no longer used. Any failure frees partial backups.

Late suspend walks shrink and purge lists under `obj_lock`, marks objects as CPU-written for hibernation, and flushes CPU caches with `wbinvd_on_all_cpus` if non-coherent CPU-visible data may exist. Resume restores early backups, resumes GTs, then restores GPU-assisted backups; GT resume failures wedge affected GTs.

## State and Persistence Behavior
The file does not own object data itself but changes persistence guarantees for LMEM objects through `obj->ttm.backup`, TTM placement, shrink/purge list domain state, runtime PM userfault wakerefs, and GT suspend/resume state. Hibernation paths force objects toward CPU domain so the image contains coherent backing data.

## Dependencies and Integration Points
It depends on `i915_gem_ttm_pm` for LMEM backup/restore, GT PM and request retirement, runtime PM wakeref helpers, shrinker reclaim, freed-object draining, and architecture cache flush support.

## Risks
Incorrect staging can lose LMEM contents, especially pinned objects and CCS aux state. Missing global cache flushes can write stale data into hibernation images. Resume ordering matters because the kernel context image is disposable but user object contents are not. On non-x86, the fallback only warns for missing `wbinvd`.

## Test Signals
Suspend/resume and hibernate cycles on integrated and DGFX platforms, LMEM object checksum validation before/after power transitions, wedged-GT resume fault injection, framebuffer preservation, early-PM object tests, and shrink-list domain assertions are important signals.
