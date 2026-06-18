# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_ttm_buffer.c

Purpose: Implements vmwgfx's TTM backend: placements, DMA mapping, GMR/MOB binding, population, movement, notifications, and pinned populated BO creation.

Important APIs/types: `vmw_vram_placement`, `vmw_sys_placement`, `vmw_tt_size`, `vmw_piter_start()`, `vmw_bo_sg_table()`, `vmw_bo_driver`, and `vmw_bo_create_and_populate()`.

Control flow: TT creation selects SG or normal TTM based on external buffers and DMA mode. Populate allocates pages or derives DMA addresses from imported SG. Map builds/maps SG tables for DMA. Bind maps pages and binds them to GMR or MOB ids; unbind reverses bindings and may unmap. Move binds new TT-backed memory, notifies resources/queries, performs null TT moves when possible, or memcpy moves otherwise.

State/persistence: `vmw_ttm_tt` tracks dev_priv, SG/vsgt state, MOB, mapped/bound flags, memory type, and GMR id. BO resource placement and pinning drive validation.

Dependencies/integration: Linux DMA API, DRM TTM pool/placement/move helpers, vmwgfx GMR/MOB code, BO/query notifications, and PRIME imports.

Risks/test signals: DMA synchronization assumptions, SG/MOB leak paths, bind failure state, move rollback notifications, PRIME import/export, map-mode matrix, eviction, and DMA debug.
