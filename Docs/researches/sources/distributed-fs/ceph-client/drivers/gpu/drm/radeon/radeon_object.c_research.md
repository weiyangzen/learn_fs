<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_object.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_object.c

## Purpose

`radeon_object.c` implements Radeon GEM/TTM buffer-object management. It creates and destroys BOs, maps/unmaps them for the kernel, handles references, pins/unpins BOs into VRAM/GTT, initializes/finalizes TTM memory management, validates command-submission BO lists, manages legacy surface registers for tiled CPU mappings, responds to BO moves and CPU faults, evicts VRAM, force-deletes leaked objects, and attaches Radeon fences to DMA reservations.

## Important APIs, Types, and Functions

- `radeon_ttm_bo_destroy()` and `radeon_ttm_bo_is_radeon_bo()`: Radeon TTM object destructor and type predicate.
- `radeon_ttm_placement_from_domain()`: converts Radeon GEM domains and flags into TTM placement arrays, including visible-VRAM constraints for CPU-accessible BOs and invisible-VRAM preference for no-CPU-access BOs.
- `radeon_bo_create()`: aligns size, chooses TTM BO type, initializes GEM object, applies architecture/chipset cacheability restrictions, initializes placement, and calls `ttm_bo_init_validate()`.
- `radeon_bo_kmap()` / `radeon_bo_kunmap()`: wait for kernel usage, map/unmap BO pages through TTM, cache `bo->kptr`, and update tiling surface state.
- `radeon_bo_ref()` / `radeon_bo_unref()`: GEM reference wrappers.
- `radeon_bo_pin_restricted()`, `radeon_bo_pin()`, and `radeon_bo_unpin()`: validate BO placement, disallow userptr pinning, account pinned VRAM/GART sizes, and return GPU offsets.
- `radeon_bo_evict_vram()`, `radeon_bo_force_delete()`, `radeon_bo_init()`, and `radeon_bo_fini()`: memory-manager lifecycle and emergency cleanup.
- `radeon_bo_list_validate()`: reserve all BOs for command submission, migrate them to preferred/allowed domains within a bytes-moved threshold, handle UVD segment constraints, and record GPU offsets/tiling flags.
- `radeon_bo_get_surface_reg()`, `radeon_bo_clear_surface_reg()`, `radeon_bo_set_tiling_flags()`, `radeon_bo_get_tiling_flags()`, and `radeon_bo_check_tiling()`: manage legacy surface registers needed for tiled BO mappings.
- `radeon_bo_move_notify()` and `radeon_bo_fault_reserve_notify()`: TTM callbacks for move invalidation and CPU fault migration into visible VRAM/GTT.
- `radeon_bo_fence()`: reserves one DMA fence slot and records shared/exclusive Radeon fences on the BO reservation object.

## Control Flow

BO creation initializes the wrapper, embeds the GEM object, strips unsupported cache flags based on bus, ASIC, architecture, and PAT/WC support, computes initial placement from requested domains, takes the memory-clock read lock, and asks TTM to allocate/validate the BO. Destruction removes the BO from the GEM object list under `gem.mutex`, clears any surface register, warns on leftover VM mappings, destroys PRIME import state if present, releases the GEM object, and frees the wrapper.

Pinning requires the caller to hold reservation. Userptr BOs cannot be pinned. Already-pinned BOs just increment TTM pin count and return current GPU address. First pin validates the BO into the requested domain and optional max offset, constraining CPU-accessible VRAM pins to visible VRAM when needed, then pins and updates aggregate pin accounting.

Command submission validation first uses `drm_exec` to reserve every BO. It then iterates the list, skips pinned BOs, chooses preferred placement but avoids excessive relocations after a dynamic VRAM-usage threshold, validates with TTM, retries with allowed domains on non-signal failures, applies UVD segment restrictions when needed, and records GPU offset and tiling flags for relocation emission.

Surface-register management is demand-driven for BOs with `RADEON_TILING_SURFACE`. It reuses existing surface registers, finds free entries, or steals one from an unpinned BO by unmapping that BO's CPU virtual mapping. BO moves and force-drop paths clear surface state and invalidate VM mappings.

CPU faults on invisible VRAM try to migrate the BO into visible VRAM; if that fails with `-ENOMEM`, the path falls back to GTT. Pinned invisible BOs fault with SIGBUS because they cannot be moved.

## State and Persistence Behavior

Persistent BO state includes GEM/TTM object state, placement arrays, flags, initial domain, tiling flags/pitch, surface register index, kernel mapping pointer, VM mapping list, PRIME import attachment, reservation fences, and pin counts. Device-level state includes GEM object list, aggregate VRAM/GART pinned sizes, TTM managers, VRAM WC/MTRR reservations, surface-register ownership, and atomic bytes-moved counters.

## Dependencies and Integration Points

This file depends on DRM GEM, DRM PRIME, DMA reservation/fence APIs, TTM resource managers and BO validation, architecture WC/MTRR helpers, Radeon TTM backend, Radeon tracing, VM invalidation, UVD placement constraints, command submission BO lists, and legacy surface-register hardware callbacks. It is a core dependency for framebuffer scanout, command submission, cursor BOs, IB pools, user GEM objects, and PRIME sharing.

## Risks and Edge Cases

- `radeon_bo_create()` leaks the allocated wrapper if `ttm_bo_init_validate()` fails before the TTM destructor owns it; ownership should be checked against the TTM API version in this tree.
- BO reservation discipline is critical. Several functions assert or assume the BO reservation is held; callers that skip reservation can race placement/tiling/pin state.
- Surface-register stealing unmaps another BO's virtual mappings and relies on unpinned selection; bugs can disturb CPU mappings unexpectedly.
- Pin accounting must exactly match first pin and final unpin or memory pressure reporting becomes wrong.
- Userptr, PRIME-shared, and no-CPU-access flags impose placement restrictions that can be violated by future call paths.
- Fault migration from invisible VRAM can fail with SIGBUS for pinned BOs, which is correct but user-visible.

## Test Signals

Test BO creation across VRAM/GTT/CPU domains, cache flag variants, PRIME imports, userptr rejection on pin, kmap/kunmap, pin/unpin accounting, visible-VRAM constraints, command submission validation under memory pressure, bytes-moved threshold behavior, UVD segment placement, tiling flag validation for Evergreen+, surface-register allocation/steal/clear, CPU faults on invisible VRAM, VRAM eviction, forced object delete diagnostics, and fence attachment under OOM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_object.c -->
