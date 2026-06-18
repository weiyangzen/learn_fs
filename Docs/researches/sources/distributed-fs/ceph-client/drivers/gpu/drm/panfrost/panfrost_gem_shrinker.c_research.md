# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_gem_shrinker.c

## Purpose
This file registers a memory shrinker for purgeable Panfrost shmem GEM objects.

## Important APIs, Types, and Functions
The public functions are `panfrost_gem_shrinker_init` and `panfrost_gem_shrinker_cleanup`. Internal callbacks are `panfrost_gem_shrinker_count`, `panfrost_gem_shrinker_scan`, and `panfrost_gem_purge`.

## Control Flow
The count callback try-locks the device shrinker lock and sums pages for purgeable objects on `pfdev->shrinker_list`. The scan callback iterates the same list until the scan budget is met, purging objects that are still purgeable and successfully locked. Purge refuses BOs in GPU use, locks mappings and reservation, tears down GPU mappings, calls `drm_gem_shmem_purge_locked`, and removes purged entries from the list.

## State and Persistence Behavior
It mutates `pfdev->shrinker`, `pfdev->shrinker_list`, BO mapping activity, shmem GEM pages/madv state, and heap/GPU mapping residency indirectly through teardown. It never blocks indefinitely because it uses trylocks in reclaim context.

## Dependencies and Integration Points
It integrates with Linux shrinker infrastructure, DRM shmem GEM purge helpers, Panfrost GEM mappings, MMU teardown, dma-resv locking, and the MADVISE ioctl that places objects on the shrinker list.

## Risks
Reclaim context lock ordering is delicate. Objects with active GPU use must not be purged. Mapping teardown before shmem purge is required to prevent GPU access to freed pages. Trylock failures reduce reclaim effectiveness under contention.

## Test Signals
Use memory pressure with MADV_DONTNEED BOs, jobs holding purgeable BO references, repeated MADV_WILLNEED/DONTNEED transitions, lock contention, and post-purge fault/access behavior to validate the shrinker.
