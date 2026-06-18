# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_stolen_mgr.c

Purpose: Implements a TTM resource manager for stolen memory by extending the VRAM manager, detecting stolen-memory size/base for integrated and discrete platforms, and providing CPU/GPU offset and TTM bus mapping helpers.

Important APIs/types/functions: Internal `struct xe_ttm_stolen_mgr` embeds `struct xe_ttm_vram_mgr` and stores `io_base`, `stolen_base`, and optional WC mapping. Public functions are `xe_ttm_stolen_mgr_init`, `xe_ttm_stolen_io_mem_reserve`, `xe_ttm_stolen_cpu_access_needs_ggtt`, `xe_ttm_stolen_io_offset`, and `xe_ttm_stolen_gpu_offset`. Detection helpers include `get_wopcm_size`, `detect_bar2_dgfx`, `detect_bar2_integrated`, and `detect_stolen`.

Control flow: Initialization allocates the stolen manager with DRM-managed memory, skips SR-IOV VFs, selects a detection path for DGFX, newer integrated platforms, or legacy x86 stolen memory, then initializes the embedded VRAM manager with `XE_PL_STOLEN`. If direct CPU access is available, it maps `io_base` with `devm_ioremap_wc`. CPU bus reservation chooses between BAR2-style direct offsets and legacy GGTT-mediated stolen access.

State and persistence behavior: The manager persists as a TTM memory type manager for `XE_PL_STOLEN`. It tracks immutable base addresses and an optional CPU mapping. Allocation accounting is inherited from `xe_ttm_vram_mgr`. `xe_ttm_stolen_io_mem_reserve` mutates the passed TTM resource bus fields (`offset`, `addr`, `is_iomem`, `caching`) for CPU mapping.

Dependencies and integration points: Uses PCI BAR resources, MMIO registers (`DSMBASE`, `GGC`, `STOLEN_RESERVED`, `GSCPSMI_BASE`), WOPCM sizing, platform checks, SR-IOV checks, workarounds, Xe BO/GGTT helpers, resource cursors, and `__xe_ttm_vram_mgr_init`. Legacy x86 path relies on external `intel_graphics_stolen_res`.

Risks: Platform register interpretation is sensitive: wrong stolen base/size can overlap WOPCM, GSC PSMI reserved regions, or normal VRAM. Legacy platforms requiring GGTT CPU access need BOs with `XE_BO_FLAG_GGTT`; otherwise CPU mapping fails. `to_stolen_mgr(ttm_manager_type(...))` assumes the manager exists for offset helpers. Direct BAR mapping is intentionally disabled when CPU access must go through GGTT.

Test signals: Boot on DGFX, Xe2 integrated, pre-1270 integrated x86, and SR-IOV VF configurations; validate reported stolen size, WOPCM carveout, debug logs, BO allocation in `XE_PL_STOLEN`, CPU mmap paths, and GPU offsets. Fault paths should cover missing WOPCM size, invalid GMS/GGMS, no `io_base`, and missing GGTT flag.
