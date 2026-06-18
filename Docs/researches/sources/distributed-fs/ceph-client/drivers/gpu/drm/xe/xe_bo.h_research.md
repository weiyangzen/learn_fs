# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo.h

## Purpose
This header defines the public Xe BO contract: memory placement flags, page constants, purgeable states, creation/pinning/migration/mapping APIs, address helpers, shrinker interfaces, and inline accounting helpers used by VM, exec, PM, display, and memory-management code.

## Important APIs, Types, and Functions
Key definitions include `XE_BO_FLAG_*`, memory type aliases `XE_PL_SYSTEM`, `XE_PL_TT`, `XE_PL_VRAM0/1`, `XE_PL_STOLEN`, `enum xe_madv_purgeable_state`, conversion helpers `ttm_to_xe_bo` and `gem_to_xe_bo`, and lifecycle APIs such as `xe_bo_create_user`, `xe_bo_pin`, `xe_bo_validate`, `xe_bo_migrate`, `xe_bo_evict`, `xe_bo_vmap`, `xe_bo_put`, `xe_bo_put_async`, and `xe_bo_shrink`.

## Control Flow
The header itself has no standalone flow, but its inlines enforce required object-lock context for purgeable and memory-type checks. `xe_bo_willneed_get_locked`, `xe_bo_willneed_put_locked`, and VMA count helpers couple VM mappings and dma-buf exports to purgeable state transitions. Deferred put helpers avoid final object destruction in reclaim-tainted or atomic contexts by queuing final reference drops.

## State and Persistence Behavior
Flags declared here determine persistent BO behavior: user vs kernel, valid placements, GGTT mapping, pinned/late restore/no restore, deferred backing, CPU cache requirements, fixed placement, page-table backing, CCS/compression needs, and test-only/internal alignment bits. The purgeable state enum is terminal once `PURGED` is reached.

## Dependencies and Integration Points
It exposes TTM, DRM GEM, GGTT, VM, validation, VRAM, and scatter-gather types to the wider Xe driver. Callers include VM bind, exec, PM eviction, display dumb buffers, dma-buf code, SR-IOV CCS, pagefault handling, and debug/testing modules.

## Risks
Flag combinations are dense and some ranges must remain contiguous, especially VRAM flags. Inlines assume the caller holds the correct `dma_resv` lock; misuse can corrupt purgeable counters or observe stale placement. Header defaults and fallbacks must remain synchronized with `xe_bo.c` and uAPI validation.

## Test Signals
Build coverage catches signature drift. Runtime signals include GEM create placement tests, purgeable madvise/VMA accounting tests, async put paths from interrupt/reclaim-like contexts, migration/pin validation, and address helper checks for system, stolen, and VRAM BOs.
