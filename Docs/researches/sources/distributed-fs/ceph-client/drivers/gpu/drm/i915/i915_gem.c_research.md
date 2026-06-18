# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem.c

## Purpose
`i915_gem.c` implements core i915 GEM lifecycle and several legacy GEM UAPI operations: aperture reporting, object unbinding, pread/pwrite, software-finish cache flushes, runtime suspend cleanup, GGTT pinning, madvise/shrinker list transitions, workqueue draining, GEM hardware initialization/removal/release, and per-file GEM open.

## Important APIs, Types, and Functions
Important exported functions include `i915_gem_get_aperture_ioctl()`, `i915_gem_object_unbind()`, `i915_gem_pread_ioctl()`, `i915_gem_pwrite_ioctl()`, `i915_gem_sw_finish_ioctl()`, `i915_gem_runtime_suspend()`, `i915_gem_object_ggtt_pin_ww()`, `i915_gem_object_ggtt_pin()`, `i915_gem_madvise_ioctl()`, `i915_gem_drain_freed_objects()`, `i915_gem_drain_workqueue()`, `i915_gem_init()`, `i915_gem_driver_register()`, `i915_gem_driver_unregister()`, `i915_gem_driver_remove()`, `i915_gem_driver_release()`, `i915_gem_init_early()`, `i915_gem_cleanup_early()`, and `i915_gem_open()`.

## Control Flow
Pread/pwrite first reject unsupported gen12+ non-Tigerlake platforms, validate userspace pointers, look up GEM handles, bounds-check object ranges, and honor object-specific `ops->pread/pwrite` hooks. Generic pread waits for object idleness, tries shmem page reads with cache flush handling, and falls back to GGTT reads if needed. Generic pwrite waits for all activity, attempts fast GGTT writes for non-struct-page or clflush-needing objects, then falls back to shmem writes on page faults or ENOSPC. GGTT access uses `i915_gem_gtt_prepare()` to set GTT domain, opportunistically pin an untiled mappable VMA, or allocate a temporary one-page mappable GGTT node and insert object pages page-by-page.

`i915_gem_object_unbind()` walks an object's VMA list under object lock, gets runtime PM first to avoid shrinker/ACPI deadlocks, optionally tests only, tries async unbind, active unbind, VM trylock unbind, or normal VMA unbind, and uses an RCU barrier retry when VM refs could be in deferred release. GGTT pinning creates/reuses VMA instances, checks mappable aperture size and nonblocking heuristics, discards misplaced active/pinned VMAs by removing them from the object tree and retrying, unbinds idle misplaced VMAs, pins with `PIN_GLOBAL`, revokes unnecessary fences, and waits for bind completion.

Initialization verifies cache-level enum assumptions, adjusts vGPU page-size capabilities, fetches uC firmware and WOPCM data per GT, programs private PAT for gen8+, initializes GGTT, applies clock gating/workarounds before context state capture, initializes each GT, and registers UABI engines. On `-EIO`, it can wedge GTs and keep KMS minimally alive by re-enabling GGTT and clock gating. Removal suspends late GEM, removes GTs, clears UABI engines, drains work; release frees GTs/uC firmware and verifies context list cleanup.

## State and Persistence Behavior
GEM state lives in `i915->mm`, object VMA lists, shrink/purge lists, userfault lists, GGTT nodes, fence registers, runtime PM lists, contexts, and file-private state. `madvise` persists object purgeability unless already purged, moves objects between shrink and purge lists, and can truncate backing storage. Runtime suspend releases GTT mmap/userfault mappings and marks unpinned fence registers dirty because hardware fence state is lost across powerdown. `i915_gem_open()` allocates per-file state, client accounting, context xarrays, VM xarray, default engine selection, and hang timestamp.

## Dependencies and Integration Points
This file integrates GEM objects and regions, GGTT, VMA bind/unbind, TTM workqueues, DMA reservation waits, runtime PM, frontbuffer invalidation/flush, cache coherency/clflush, display fences, vGPU capability reporting, uC firmware, WOPCM, GT init, clock-gating workarounds, DRM UAPI handles, and i915 fd private/client accounting.

## Risks
Legacy pread/pwrite paths mix usercopy, cache maintenance, runtime PM, tiled-object restrictions, and temporary GGTT mappings; page fault fallback behavior is subtle. Object unbind can race with VMA destruction, VM release, shrinkers, and active requests, so lock ordering and runtime wakerefs are critical. GGTT pinning heuristics intentionally return ENOSPC in nonblocking cases to avoid aperture ping-pong; callers need fallbacks. `-EIO` initialization recovery keeps the driver partially alive and must not leave later teardown assuming full init. Workqueue drain loops rely on RCU barriers and bounded recursive passes.

## Test Signals
IGT GEM pread/pwrite/sw_finish/get_aperture/madvise tests, usercopy fault injection, tiled versus untiled object coverage, runtime PM suspend with GTT mmap faults, GGTT pin/unpin tests under aperture pressure, vGPU huge-GTT capability tests, GT init failure injection including `-EIO`, shrinker/purge behavior, lockdep for object/VM locks, and context/file open-close leak checks.
