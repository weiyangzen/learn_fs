# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_gmrid_manager.c

## Purpose
`vmwgfx_gmrid_manager.c` implements a TTM resource manager for vmwgfx GMR and MOB id spaces. It allocates numeric ids using `ida`, tracks page consumption, applies soft graphics-memory limits, and installs/removes the manager for TTM placement types.

## Important APIs, Types, and Functions
- `struct vmwgfx_gmrid_man` embeds `ttm_resource_manager` and stores a spinlock, `ida`, max id count, max page budget, used pages, and placement type.
- `vmw_gmrid_man_get_node()` allocates a TTM resource, assigns a GMR/MOB id, increments used pages, and expands soft limits when possible.
- `vmw_gmrid_man_put_node()` frees the id, decrements used pages, finalizes the TTM resource, and frees memory.
- `vmw_gmrid_man_debug()` reports usage to DRM printers.
- `vmw_gmrid_man_init()` and `vmw_gmrid_man_fini()` register and unregister the manager with the vmwgfx TTM device.

## Control Flow
Initialization selects limits from `dev_priv` based on `VMW_PL_GMR` or `VMW_PL_MOB`, initializes the resource manager and ida, registers it with TTM, and marks it used. Allocation initializes a resource from the requested TTM place, allocates an id up to the configured maximum, then updates page accounting under the manager lock. If usage exceeds the current soft page budget, the manager warns the guest/host and attempts to double the budget up to half of RAM; if it cannot cover current usage, allocation fails with `-ENOSPC` and fully unwinds. Finalization marks the manager unused, evicts all resources, cleans up TTM state, unregisters it, destroys the ida, and frees the manager.

## State and Persistence Behavior
Persistent runtime state is the id allocator and page counters for the registered TTM placement. Allocated TTM resources store the id in `res->start`, which later becomes the hardware GMR/MOB id used by relocation and binding. No disk persistence exists.

## Dependencies and Integration Points
This file depends on Linux `ida`, TTM resource-manager APIs, vmwgfx device limits, `totalram_pages()`, DRM warning/printer helpers, and `vmw_host_printf()` for guest-visible warnings. BO placement into `VMW_PL_GMR` and `VMW_PL_MOB` depends on this manager.

## Risks
Accounting must remain balanced across all allocation failures and frees. The soft-limit expansion policy allows graphics memory growth up to half of RAM, so memory pressure behavior is intentionally permissive but potentially surprising. Locking only protects accounting, while id allocation happens outside the spinlock. Finalization assumes eviction drains all resources before cleanup.

## Test Signals
Cover GMR and MOB initialization, id exhaustion, page-budget overflow with successful expansion, page-budget overflow with `-ENOSPC`, balanced `used_gmr_pages` after eviction, debug output, and module unload/reset paths that call `vmw_gmrid_man_fini()`.
