# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_placement.h

Purpose: defines TTM placement domains, placement flags, and the structures drivers pass to choose valid memory locations for BOs.

Important APIs/types/functions: memory domains include `TTM_PL_SYSTEM`, `TTM_PL_TT`, `TTM_PL_VRAM`, and driver-private start `TTM_PL_PRIV`. Flags request contiguous allocation, top-down search, temporary placement during eviction, desired placement, and fallback placement. `struct ttm_place` stores PFN range, memory type, and flags. `struct ttm_placement` stores an array of preferred places.

Control flow: BO validation and eviction walk candidate placements, allocate a compatible resource in the requested manager, and may fall back or use temporary placements based on flags.

State and persistence: placement structures are caller-provided policy; selected placement becomes BO `ttm_resource` state.

Dependencies and integration: depends on fixed-width Linux types. Used by TTM BO validation, resource allocation, eviction, and driver placement tables.

Risks and test signals: wrong PFN limits or fallback ordering can evict excessively or allocate inaccessible memory. Test VRAM/system/TT placement, top-down and contiguous constraints, eviction fallback, and driver private memory types.
